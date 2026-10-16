"""R7.3 General Workshop Contract proofs.

Covers the workshop contract: enter -> scoped command set + scoped
prompt -> leave, with in-scope commands routed through the SAME public
dispatcher, out-of-scope commands rejected before dispatch, bounded
session evidence persisted through the canonical save under the strict
shared schema, and honest EOF/quit behavior.

All fixtures use disposable-copy isolation (unique owners).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _repl(commands: list, owner: str, do_load: bool = False, timeout: int = 60):
    """Run the real REPL with piped commands. Returns (rc, stdout, stderr)."""
    cwd = os.path.abspath(".")
    args = [sys.executable, "-m", "form.repl", "--owner", owner]
    if do_load:
        args.append("--load")
    inp = "\n".join(commands) + "\n"
    result = subprocess.run(
        args, cwd=cwd, env={**os.environ, "PYTHONPATH": cwd},
        input=inp, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def _state(owner: str) -> dict:
    from form.persist import _path
    with open(_path(owner)) as f:
        return json.load(f)


def _ws_records(owner: str) -> dict:
    section = _state(owner).get("workshop_sessions") or {}
    return section.get("sessions") or {}


# =====================================================================
# 1. SCOPE ROUTING (real REPL)
# =====================================================================

def part_scope_routing():
    owner = unique_owner("r73scope")
    rc, out, _ = _repl(
        ["workshop matrix", "cube", "confirm", "leave"], owner)
    check("enter shows scoped prompt", "workshop:matrix> " in out)
    check("in-scope command dispatches", "Form → cube" in out)
    check("out-of-scope rejected", "Out of scope for the matrix workshop" in out)
    recs = _ws_records(owner)
    check("one closed record persisted", len(recs) == 1, f"{len(recs)}")
    if recs:
        rec = next(iter(recs.values()))
        kinds = [(c["kind"], c["result"]) for c in rec["commands"]]
        check("record trail: enter/cube/confirm/leave",
              ("enter", "workshop entered") in kinds
              and ("cube", "dispatched") in kinds
              and ("confirm", "rejected: OUT_OF_SCOPE") in kinds
              and ("leave", "leave recorded") in kinds, f"{kinds}")
        check("record is for matrix, closed",
              rec["workshop"] == "matrix" and bool(rec["closed"]))

    # say-prefix and staged reissue cannot bypass the gate.
    owner2 = unique_owner("r73bypass")
    rc, out, _ = _repl(
        ["create an idea called bypassprobe", "reissue", "workshop matrix",
         "say confirm bypassprobe", "reissue confirm", "leave"], owner2)
    check("say-prefix blocked inside workshop",
          "Out of scope for the matrix workshop" in out)
    check("reissue confirm blocked inside",
          "Reissuing now" not in out)


# =====================================================================
# 2. ALL SEVEN WORKSHOPS + SEMANTICS DIFFER INSIDE (draft 7.1.2/7.1.3)
# =====================================================================

def part_all_workshops():
    cases = {
        "matrix": "cube",
        "perspective": "look",
        "mandel": "patterns",
        "persona": "personas",
        "bimo": "bimo",
        "psalms": "lattice",
        "forces": "forces",
    }
    for wid, in_scope in cases.items():
        owner = unique_owner(f"r73{wid}")
        rc, out, _ = _repl(
            [f"workshop {wid}", in_scope, "confirm", "leave"], owner)
        check(f"{wid}: scoped prompt", f"workshop:{wid}> " in out)
        check(f"{wid}: in-scope not rejected",
              "Out of scope" not in out.split(in_scope)[0][-200:]
              and out.count("Out of scope") == 1, out[-300:])
        check(f"{wid}: out-of-scope rejected once",
              out.count("Out of scope") == 1)
        recs = _ws_records(owner)
        check(f"{wid}: session persisted", len(recs) == 1
              and next(iter(recs.values()))["workshop"] == wid)


def part_semantics_differ():
    # Outside: create dispatches. Inside matrix: same line is rejected
    # and no idea is created (draft 7.1.3 — commands differ inside).
    owner_out = unique_owner("r73diffout")
    _repl(["create an idea called differential", "save"], owner_out)
    n_out = len((_state(owner_out).get("plane") or {}).get("units") or {})
    owner_in = unique_owner("r73diffin")
    _repl(["workshop matrix", "create an idea called differential",
           "leave"], owner_in)
    n_in = len((_state(owner_in).get("plane") or {}).get("units") or {})
    check("create dispatches outside (units grow)", n_out >= 2, f"{n_out}")
    check("create rejected inside (units unchanged)", n_in == 1, f"{n_in}")


# =====================================================================
# 3. LEAVE / EOF / QUIT HONESTY + MODE NOT RESTORED
# =====================================================================

def part_leave_honesty():
    owner = unique_owner("r73eof")
    rc, out, _ = _repl(["workshop forces", "force tick"], owner)
    check("EOF states NOT saved", "Workshop session NOT saved (EOF)" in out)
    check("EOF persists no record",
          not os.path.exists(f"form/state/program_{owner}.json")
          or _ws_records(owner) == {})

    owner = unique_owner("r73quit")
    rc, out, _ = _repl(["workshop forces", "force tick", "quit"], owner)
    check("quit states NOT saved", "Workshop session NOT saved (quit)" in out)

    owner = unique_owner("r73reload")
    _repl(["workshop forces", "force tick", "leave"], owner)
    rc, out, _ = _repl([], owner, do_load=True)
    check("reload: mode not restored (you> prompt)",
          "workshop:forces> " not in out)
    check("reload: closed record present", len(_ws_records(owner)) == 1)
    st = _state(owner)
    check("reload: persisted active flag cleared",
          (st.get("ux") or {}).get("active_workshop") is None)


# =====================================================================
# 4. SAVE FAILURE + RETRY (genuine blocked instance, no guard mock)
# =====================================================================

def part_save_failure():
    from form.open import open_program
    from form.dell_matrix.workshop_session import WorkshopSession
    from form.repl import _handle_workshop_line
    owner = unique_owner("r73blocked")
    p = open_program(owner)
    p.enter_workshop("matrix")
    sess = WorkshopSession.open(p.owner, "matrix")
    sess.record("enter", "workshop entered")
    # Genuinely recovery-required instance via the production attribute
    # (the save guard itself is NOT mocked; persist_rest.save raises).
    p._recovery_required = {"reason": "probe"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p2, sess2 = _handle_workshop_line(p, "leave", sess)
    out = buf.getvalue()
    check("blocked leave reports SAVE_FAILED", "SAVE_FAILED" in out, out)
    check("blocked leave retains session", sess2 is not None)
    check("blocked leave stages nothing",
          (getattr(p, "workshop_sessions", None) or {}) == {})
    check("blocked leave restores active flag",
          p.active_workshop == "matrix")
    # Clear the block through the production attribute; retry succeeds
    # with exactly one closed record.
    p._recovery_required = None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p3, sess3 = _handle_workshop_line(p, "leave", sess)
    out = buf.getvalue()
    check("retry leave succeeds", "Workshop session saved" in out, out)
    check("retry exits session", sess3 is None)
    check("exactly one record after retry",
          len(getattr(p, "workshop_sessions", None) or {}) == 1)
    check("flag cleared after retry", p.active_workshop is None)


# =====================================================================
# 5. BOUNDS (enforced during recording + retention at serialization)
# =====================================================================

def part_bounds():
    from form.dell_matrix.workshop_session import (
        WorkshopSession, serialize_section)
    s = WorkshopSession.open("o1", "matrix")
    for i in range(55):
        s.record(f"c{i}", "dispatched")
    check("55 records bounded to 50", len(s.commands) == 50)
    check("oldest evicted", s.commands[0]["kind"] == "c5",
          s.commands[0]["kind"])
    sessions = {}
    for i in range(11):
        rec = WorkshopSession.open("o1", "matrix")
        rec.record("enter", "workshop entered")
        d = rec.closed_copy()
        d["started"] = f"2026-01-{i + 1:02d}T00:00:00Z"
        sessions[d["session_id"]] = d
    out = serialize_section(sessions, None, "o1")
    check("11 sessions retained to 10", len(out["sessions"]) == 10)


# =====================================================================
# 6. PROTECTION (real grant handle, real REPL, persisted evidence)
# =====================================================================

def part_protection():
    from form.open import open_program
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa
    owner = unique_owner("r73prot")
    p = open_program(owner)
    pr = p.nursery.add("S1", words="r73 protection fixture idea")
    pid = pr.id
    coord = ac.new_coordinator(p)
    coord.register_agent("ta", persona_slots={"pilot": "manny"})
    sa = coord.surface_for("ta")
    grant = aa.issue_root_grant(p, issuer="t", subject="ta",
                                target=pid, content_pid=pid)
    handle = grant["grant_id"]
    p.save()
    rc, out, _ = _repl(
        ["workshop matrix", f"cube {handle}", "leave"], owner)
    check("protected line rejected", "Rejected: PROTECTED_MATERIAL" in out)
    check("handle absent from REPL output", handle not in out)
    from form.persist import _path
    with open(_path(owner), "rb") as f:
        blob = f.read().decode("utf-8", "replace")
    check("handle absent from persisted evidence", handle not in blob)
    recs = _ws_records(owner)
    if recs:
        kinds = [(c["kind"], c["result"]) for c in
                 next(iter(recs.values()))["commands"]]
        check("protected attempt recorded with safe code only",
              ("protected", "rejected: PROTECTED_MATERIAL") in kinds,
              f"{kinds}")


# =====================================================================
# 7. PERSISTENCE SCHEMA (strict, sentinel, accumulation, serializer)
# =====================================================================

def part_schema():
    from form.dell_matrix.workshop_session import (
        validate_section, serialize_section, WorkshopSession, _MISSING)
    s, m = validate_section(_MISSING, "o1")
    check("absent section is legacy", s == {} and m is None)
    s, m = validate_section(None, "o1")
    check("explicit null is malformed", isinstance(m, dict)
          and "_section" in m)
    s, m = validate_section({"version": True, "sessions": {}}, "o1")
    check("bool version malformed", isinstance(m, dict) and "_section" in m)
    rec = WorkshopSession.open("o1", "matrix").closed_copy()
    s, m = validate_section(
        {"version": 1, "sessions": {rec["session_id"]: rec}}, "o1")
    check("valid closed record restores", len(s) == 1 and m is None)
    foreign = dict(rec, owner="someoneelse")
    s, m = validate_section(
        {"version": 1, "sessions": {rec["session_id"]: foreign}}, "o1")
    check("foreign-owner record malformed", s == {}
          and rec["session_id"] in (m or {}))
    alien = dict(rec, workshop="notaworkshop",
                 session_id="alien1")
    s, m = validate_section(
        {"version": 1, "sessions": {"alien1": alien}}, "o1")
    check("unknown-workshop record malformed", s == {} and "alien1" in (m or {}))
    # Same-key accumulation: preserved evidence + a new failure coexist.
    prior = [{"raw": {"why": "earlier"}, "error": "earlier failure"}]
    bad = dict(rec, closed=None)
    s, m = validate_section(
        {"version": 1, "sessions": {rec["session_id"]: bad},
         "malformed": {rec["session_id"]: prior}}, "o1")
    entries = (m or {}).get(rec["session_id"])
    check("same-key malformed accumulates",
          isinstance(entries, list) and len(entries) == 2, f"{entries}")
    # Serializer: an active record is preserved as malformed, never saved.
    active = WorkshopSession.open("o1", "matrix").to_dict()
    out = serialize_section({active["session_id"]: active}, None, "o1")
    check("active record not serialized as valid",
          active["session_id"] not in out["sessions"]
          and active["session_id"] in out.get("malformed", {}))


# =====================================================================
# 8. ONE SCOPED ENVIRONMENT + STUDIO NON-REGRESSION
# =====================================================================

def part_one_environment():
    owner = unique_owner("r73one")
    rc, out, _ = _repl(
        ["workshop matrix", "workshop forces", "perspective studio",
         "cube", "leave", "perspective studio", "leave"], owner)
    check("second workshop entry blocked inside",
          "Already in a scoped workshop session" in out)
    check("studio entry blocked inside workshop",
          out.count("Out of scope for the matrix workshop") >= 1)
    check("still in matrix after blocked attempts",
          out.rindex("workshop:matrix> ") > out.index("Already in a scoped"))
    check("studio enterable after leaving workshop",
          "Perspective Studio — scoped composition workshop." in out
          and "studio> " in out)


def _run_all() -> int:
    part_scope_routing()
    part_all_workshops()
    part_semantics_differ()
    part_leave_honesty()
    part_save_failure()
    part_bounds()
    part_protection()
    part_schema()
    part_one_environment()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== R7.3 workshop contract: {passed}/{len(CHECKS)} ===")
    return 0 if passed == len(CHECKS) else 1


def smoke() -> bool:
    """Regression-harness entry (form.regress calls module:smoke)."""
    global CHECKS
    CHECKS = []
    return _run_all() == 0


def main() -> int:
    return _run_all()


if __name__ == "__main__":
    sys.exit(main())
