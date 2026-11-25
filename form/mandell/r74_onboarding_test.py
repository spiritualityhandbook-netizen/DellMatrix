"""R7.4 (GDP draft 7.1.4) — disclosure onboarding / teach rhythm proofs.

Adopted decisions (Ace, 2026-10-20): D1 fourth disclosure level
``first-run`` below beginner, presentational only, never a dispatch
gate; D2 teach rhythm Show -> Explain -> Try -> Verify over a short
path (create, grow/confirm, look, save/load), reusing the demo owner
for Show and the proven scoped-session pattern for Try.

Covers: the level-filtering differential; new owners starting at
first-run; the full rhythm on the real REPL public path with
completion + graduation persisted; the scoped gate (out-of-scope and
say-prefixed lines rejected before dispatch); Verify honesty (a Try
that changes nothing does not verify); early-exit honesty (leave and
EOF); demo-owner isolation; the legacy rule (absent section never
demotes); the strict section schema (explicit null / bool version /
forged completion / foreign owner fail closed, evidence preserved);
stage-then-save failure recovery; and one-scoped-environment mutual
exclusion with the workshop gate.

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


def _repl(commands: list, owner: str, do_load: bool = False, timeout: int = 120):
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


def _ob_section(owner: str) -> dict:
    return _state(owner).get("onboarding_sessions") or {}


def _ob_records(owner: str) -> dict:
    return _ob_section(owner).get("sessions") or {}


def _unit_labels(owner: str) -> list:
    plane = _state(owner).get("plane") or {}
    units = plane.get("units") or {}
    return [u.get("label") for u in units.values() if isinstance(u, dict)]


# =====================================================================
# 1. LEVEL DIFFERENTIAL (registry unit proofs)
# =====================================================================

def part_registry_differential():
    from form.dell_matrix.actions_registry import (
        actions_for_mode, actions_flat, normalize_mode)
    fr = actions_for_mode("first-run")
    check("first-run surface is exactly the First run group",
          [g["group"] for g in fr] == ["First run"],
          f"{[g['group'] for g in fr]}")
    b = actions_for_mode("beginner")
    check("beginner surface includes First run + beginner groups",
          "First run" in [g["group"] for g in b]
          and len(b) > len(fr))
    counts = [len(actions_flat(m)) for m in
              ("first-run", "beginner", "builder", "depth")]
    check("surfaces strictly widen first-run < beginner < builder <= depth",
          counts[0] < counts[1] < counts[2] <= counts[3], f"{counts}")
    check("first-run surface differs from beginner (bypass would fail)",
          actions_flat("first-run") != actions_flat("beginner"))
    check("normalize_mode accepts first-run",
          normalize_mode("first-run") == "first-run")
    check("normalize_mode fallback unchanged",
          normalize_mode("nonsense") == "builder")


# =====================================================================
# 2. NEW OWNER STARTS AT FIRST-RUN (real REPL)
# =====================================================================

def part_new_owner():
    owner = unique_owner("r74new")
    rc, out, _ = _repl(["quit"], owner)
    check("new owner render shows mode=first-run", "mode=first-run" in out)
    rc, out, _ = _repl(["save", "quit"], owner)
    section = _ob_section(owner)
    check("new owner save persists begun=True, no sessions",
          section.get("begun") is True and _ob_records(owner) == {},
          f"{section.get('begun')}")
    check("new owner persisted ux mode is first-run",
          (_state(owner).get("ux") or {}).get("mode") == "first-run")


# =====================================================================
# 3. FULL FLOW (real REPL): rhythm, completion, graduation, reload
# =====================================================================

def part_full_flow():
    owner = unique_owner("r74flow")
    rc, out, _ = _repl(
        ["onboard",
         "create an idea called Seedling detail: first goals: learn",
         "grow ideas 1",
         "look",
         "save",
         "quit"], owner)
    check("scoped prompt shown", "onboard> " in out)
    for mv in ("Move 1 of 4", "Move 2 of 4", "Move 3 of 4", "Move 4 of 4"):
        check(f"{mv} presented", mv in out)
    for mv in ("Create an idea", "Grow, then confirm", "Look around",
               "Save and load"):
        check(f"verified message: {mv}", f"Verified: {mv}" in out)
    check("completion announced", "Onboarding complete" in out)
    check("graduation announced", "first-run → beginner" in out)
    recs = _ob_records(owner)
    check("exactly one onboarding record", len(recs) == 1, f"{len(recs)}")
    if recs:
        rec = next(iter(recs.values()))
        check("record completed and closed",
              rec["completed"] is True and bool(rec["closed"]))
        kinds = [s["kind"] for s in rec["steps"]]
        expected = []
        for m in ("create", "grow_confirm", "look", "save_load"):
            expected += [f"show:{m}", f"explain:{m}", f"try:{m}",
                         f"verify:{m}"]
        it = iter(kinds)
        check("step trail is show/explain/try/verify per move, in order",
              all(any(k == e for k in it) for e in expected)
              and kinds[-1] == "complete", f"{kinds}")
        check("verify results recorded as verified",
              all(s["result"] == "verified" for s in rec["steps"]
                  if s["kind"].startswith("verify:")))
    check("section begun True", _ob_section(owner).get("begun") is True)
    check("persisted ux mode graduated to beginner",
          (_state(owner).get("ux") or {}).get("mode") == "beginner")
    # Reload: completion is durable; re-entry refused with the fact.
    rc, out, _ = _repl(["onboard", "quit"], owner, do_load=True)
    check("reload: onboard reports already complete",
          "Onboarding already complete" in out)
    check("reload: mode stays beginner", "mode=beginner" in out)


# =====================================================================
# 4. SCOPE GATE (real REPL): out-of-scope rejected before dispatch
# =====================================================================

def part_scope_gate():
    owner = unique_owner("r74gate")
    rc, out, _ = _repl(
        ["onboard", "cube", "say cube", "leave", "quit"], owner)
    check("out-of-scope command rejected",
          "that is not this move's try" in out)
    check("say-prefixed line cannot smuggle dispatch",
          out.count("that is not this move's try") >= 2)
    check("no cube form change leaked into state",
          "Form → cube" not in out)
    recs = _ob_records(owner)
    check("one record from leave", len(recs) == 1, f"{len(recs)}")
    if recs:
        rec = next(iter(recs.values()))
        results = [s["result"] for s in rec["steps"]]
        check("rejections recorded as OUT_OF_SCOPE",
              results.count("rejected: OUT_OF_SCOPE") == 2, f"{results}")
        check("early leave record not completed",
              rec["completed"] is False)


# =====================================================================
# 5. VERIFY HONESTY (real REPL): a Try that changes nothing fails
# =====================================================================

def part_verify_honesty():
    owner = unique_owner("r74honest")
    rc, out, _ = _repl(
        ["onboard",
         "create an idea called Honest detail: x goals: y",
         "confirm all",          # nothing pending: must NOT verify
         "grow ideas 1",         # now it verifies
         "look",
         "save",
         "quit"], owner)
    check("no-change confirm does not verify",
          "Not verified: that did not change your state yet" in out)
    check("flow still completes after honest retry",
          "Onboarding complete" in out)
    recs = _ob_records(owner)
    if recs:
        rec = next(iter(recs.values()))
        grow_steps = [s["result"] for s in rec["steps"]
                      if s["kind"] == "verify:grow_confirm"]
        check("verify trail shows failure then success",
              grow_steps == ["not verified", "verified"], f"{grow_steps}")


# =====================================================================
# 6. EARLY EXIT HONESTY (real REPL): leave persists incomplete; EOF
#    persists nothing
# =====================================================================

def part_early_exit():
    owner = unique_owner("r74early")
    rc, out, _ = _repl(["onboard", "leave", "quit"], owner)
    check("early leave says not complete",
          "Not complete — your level stays first-run" in out)
    recs = _ob_records(owner)
    check("early leave record exists, not completed",
          len(recs) == 1
          and next(iter(recs.values()))["completed"] is False)
    rc, out, _ = _repl(["status", "quit"], owner, do_load=True)
    check("level remains first-run on reload", "mode=first-run" in out)

    owner2 = unique_owner("r74eof")
    rc, out, _ = _repl(["save", "onboard"], owner2)  # EOF inside session
    check("EOF states session NOT saved",
          "Onboarding session NOT saved (EOF)" in out)
    check("EOF persisted no onboarding record",
          _ob_records(owner2) == {})


# =====================================================================
# 7. DEMO ISOLATION: Show writes only demo state; the owner's state
#    changes only through their own Try steps
# =====================================================================

def part_demo_isolation():
    owner = unique_owner("r74iso")
    rc, out, _ = _repl(
        ["onboard",
         "create an idea called Mine detail: own goals: own",
         "grow ideas 1", "look", "save", "quit"], owner)
    labels = _unit_labels(owner)
    check("owner state has their own created idea", "Mine" in labels,
          f"{labels}")
    check("demo idea NOT in owner state",
          "Onboarding Demo" not in labels, f"{labels}")
    demo_labels = _unit_labels(f"DEMO_TUTORIAL_{owner}")
    check("demo idea IS in demo state",
          "Onboarding Demo" in demo_labels, f"{demo_labels}")


# =====================================================================
# 8. LEGACY RULE (integration): absent section never demotes
# =====================================================================

def part_legacy():
    import copy
    from form.persist import _path
    from form.persist_rest import load, save
    # Build a state file with NO onboarding section (pre-feature shape)
    # from a disposable owner's real saved state.
    donor = unique_owner("r74donor")
    _repl(["save", "quit"], donor)
    data = _state(donor)
    data.pop("onboarding_sessions", None)
    data["ux"]["mode"] = "builder"
    legacy = unique_owner("r74legacy")
    data["owner"] = legacy
    with open(_path(legacy), "w") as f:
        json.dump(data, f)
    p = load(legacy, activate=False)
    check("legacy owner keeps restored mode (no demotion)",
          p.ux_mode == "builder", f"{p.ux_mode}")
    check("legacy owner not marked begun/completed",
          p.onboarding_begun is False and p.onboarding_completed is False)
    save(p)
    p2 = load(legacy, activate=False)
    check("legacy owner still not demoted after re-save",
          p2.ux_mode == "builder", f"{p2.ux_mode}")
    check("re-save writes begun=False section",
          _ob_section(legacy).get("begun") is False)


# =====================================================================
# 9. STRICT SCHEMA (unit): fail-closed evidence rules + level rule
# =====================================================================

def part_schema():
    from form.dell_matrix.onboarding_session import (
        validate_section, serialize_section, OnboardingSession,
        apply_restored_level, _MISSING)

    s, m, meta = validate_section(_MISSING, "o1")
    check("absent section is legacy",
          s == {} and m is None and meta["present"] is False)
    s, m, meta = validate_section(None, "o1")
    check("explicit null is malformed + section_malformed",
          isinstance(m, dict) and "_section" in m
          and meta["section_malformed"] is True)
    s, m, meta = validate_section(
        {"version": True, "begun": False, "sessions": {}}, "o1")
    check("bool version malformed", meta["section_malformed"] is True)
    s, m, meta = validate_section({"version": 1, "sessions": {}}, "o1")
    check("missing begun malformed", meta["section_malformed"] is True)

    rec = OnboardingSession.open("o1").closed_copy(completed=True)
    s, m, meta = validate_section(
        {"version": 1, "begun": True,
         "sessions": {rec["session_id"]: rec}}, "o1")
    check("valid completed record restores",
          len(s) == 1 and m is None and meta["begun"] is True)

    forged = dict(rec, completed="yes")
    s, m, meta = validate_section(
        {"version": 1, "begun": True,
         "sessions": {rec["session_id"]: forged}}, "o1")
    check("forged completion (string) is malformed, proves nothing",
          s == {} and rec["session_id"] in (m or {}))

    foreign = dict(rec, owner="someoneelse")
    s, m, meta = validate_section(
        {"version": 1, "begun": True,
         "sessions": {rec["session_id"]: foreign}}, "o1")
    check("foreign-owner record malformed", s == {}
          and rec["session_id"] in (m or {}))

    # Same-key accumulation: preserved evidence + a new failure coexist.
    prior = [{"raw": {"why": "earlier"}, "error": "earlier failure"}]
    bad = dict(rec, closed=None)
    s, m, meta = validate_section(
        {"version": 1, "begun": True,
         "sessions": {rec["session_id"]: bad},
         "malformed": {rec["session_id"]: prior}}, "o1")
    entries = (m or {}).get(rec["session_id"])
    check("same-key malformed accumulates",
          isinstance(entries, list) and len(entries) == 2, f"{entries}")

    # Serializer: an active record is preserved as malformed, never saved.
    active = OnboardingSession.open("o1").to_dict()
    out = serialize_section({active["session_id"]: active}, None, "o1",
                            begun=True)
    check("active record not serialized as valid",
          active["session_id"] not in out["sessions"]
          and active["session_id"] in out.get("malformed", {}))
    check("serializer writes strict begun bool",
          out["begun"] is True
          and serialize_section({}, None, "o1", begun="yes")["begun"]
          is False)

    # Level rule (apply_restored_level) against the state machine.
    class _P:
        ux_mode = "builder"
    p = _P(); apply_restored_level(p, {}, {"present": False})
    check("level: absent section leaves mode", p.ux_mode == "builder")
    p = _P(); apply_restored_level(
        p, {}, {"present": True, "section_malformed": True})
    check("level: section-malformed fails closed to first-run",
          p.ux_mode == "first-run")
    p = _P(); p.ux_mode = "depth"
    apply_restored_level(p, {}, {"present": True, "begun": True,
                                 "section_malformed": False})
    check("level: begun without completion -> first-run",
          p.ux_mode == "first-run")
    p = _P(); p.ux_mode = "first-run"
    apply_restored_level(p, {rec["session_id"]: rec},
                         {"present": True, "begun": True,
                          "section_malformed": False})
    check("level: completed graduates first-run -> beginner",
          p.ux_mode == "beginner")
    p = _P(); p.ux_mode = "depth"
    apply_restored_level(p, {rec["session_id"]: rec},
                         {"present": True, "begun": True,
                          "section_malformed": False})
    check("level: completed keeps a manually-raised mode",
          p.ux_mode == "depth")


# =====================================================================
# 10. SAVE FAILURE (in-process handler): stage-then-save recovery
# =====================================================================

def part_save_failure():
    from form.open import open_program
    from form.dell_matrix.onboarding_session import OnboardingSession
    from form.repl import _handle_onboarding_line
    owner = unique_owner("r74blocked")
    p = open_program(owner)
    p.ux_mode = "first-run"
    p.onboarding_begun = True
    sess = OnboardingSession.open(p.owner)
    sess.record("enter", "onboarding entered")
    # Genuinely recovery-required instance via the production attribute
    # (the save guard itself is NOT mocked; persist_rest.save raises).
    p._recovery_required = {"reason": "probe"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p2, sess2 = _handle_onboarding_line(p, "leave", sess)
    out = buf.getvalue()
    check("blocked leave reports SAVE_FAILED", "SAVE_FAILED" in out, out)
    check("blocked leave retains session", sess2 is not None)
    check("blocked leave stages nothing",
          (getattr(p, "onboarding_sessions", None) or {}) == {})
    # Clear the block through the production attribute; retry succeeds
    # with exactly one closed record.
    p._recovery_required = None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        p3, sess3 = _handle_onboarding_line(p, "leave", sess)
    out = buf.getvalue()
    check("retry leave succeeds", "Onboarding session saved" in out, out)
    check("retry exits session", sess3 is None)
    check("exactly one record after retry",
          len(getattr(p, "onboarding_sessions", None) or {}) == 1)


# =====================================================================
# 11. ONE SCOPED ENVIRONMENT: onboarding cannot start inside a
#     workshop session (the workshop gate owns the lines)
# =====================================================================

def part_one_environment():
    owner = unique_owner("r74oneenv")
    rc, out, _ = _repl(
        ["workshop matrix", "onboard", "leave", "quit"], owner)
    check("onboard inside workshop rejected by workshop gate",
          "Out of scope for the matrix workshop" in out)
    check("onboarding session never opened (no scoped prompt)",
          "onboard> " not in out)
    check("no onboarding session recorded",
          _ob_records(owner) == {})


def _run_all() -> int:
    part_registry_differential()
    part_new_owner()
    part_full_flow()
    part_scope_gate()
    part_verify_honesty()
    part_early_exit()
    part_demo_isolation()
    part_legacy()
    part_schema()
    part_save_failure()
    part_one_environment()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== R7.4 onboarding: {passed}/{len(CHECKS)} ===")
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
