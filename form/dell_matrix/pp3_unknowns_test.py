"""Post-plan PP3 / D5 — unknowns as first-class state.

Ace's direction: the matrix must handle unknown variables and
information — to discover what nobody knows yet, the not-knowing
itself has to be recorded somewhere it can be worked on. Before
PP3, an unparseable seed, a skipped atom, or a docked judge's
"unverifiable" verdict evaporated into a result message.

This suite pins the register (form/dell_matrix/unknowns.py) and
its three capture paths on the real mechanisms:

- the register itself: record, dedup by (subject, question)
  while OPEN (recurrence increments `seen` — it is evidence),
  persistence through save/load, and the discovery gate — an
  unknown closes ONLY with evidence (the answer for RESOLVED,
  the reason for UNKNOWABLE) from a named resolver; a settled
  question re-encountered opens a FRESH entry;
- executor capture: an unparseable seed and a FlowThru-skipped
  atom land as OPEN unknowns (sources executor:parse /
  executor:skip), deduped on repeat, and clean executions
  record nothing;
- docked flag capture: a judge's flag on a field entry records
  an OPEN unknown naming the entry (source dock:flag:<subject>);
- the public REPL surface (REAL_USER_PATH): `unknowns` lists,
  `unknowns resolve <id> <answer>` closes with evidence;
- the section contract: strict validation (an OPEN entry may
  not carry a resolution), malformed records preserved as
  evidence, the 200-entry bound evicts the oldest.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402
from form.dell_matrix import unknowns as unk  # noqa: E402

RESULTS = []


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:200]))


def _cleanup(owner):
    base = os.path.join(os.path.dirname(__file__), "..", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_{owner}.journal.json",
                f"checkpoint_{owner}.journal.json",
                f"gen_{owner}_*", f"current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except FileNotFoundError:
                pass
    for d in glob.glob(os.path.join(base, f"ideas_{owner}*")):
        if os.path.isdir(d):
            shutil.rmtree(d)


def _check_register():
    from form.persist import load as pload
    owner = "PP3Reg"
    _cleanup(owner)
    try:
        p = Program(owner)
        r = p.record_unknown("widget torque",
                             "What torque does the widget need?",
                             source="pp3test")
        e = r.get("entry") or {}
        _rec("record opens an unknown",
             r.get("ok") and r.get("created")
             and e.get("status") == "OPEN" and e.get("seen") == 1,
             f"r={r}")
        r2 = p.record_unknown("widget torque",
                              "What torque does the widget need?",
                              source="pp3test")
        _rec("repeat encounter dedups and increments seen",
             r2.get("ok") and r2.get("created") is False
             and r2["entry"]["entry_id"] == e["entry_id"]
             and r2["entry"]["seen"] == 2,
             f"r2={r2}")
        bad = p.resolve_unknown(e["entry_id"], "   ",
                                resolver="pp3test")
        after = [x for x in p.list_unknowns()
                 if x["entry_id"] == e["entry_id"]][0]
        _rec("closing without evidence is refused, entry stays OPEN",
             bad.get("ok") is False
             and bad.get("reason") == "resolution_required"
             and after["status"] == "OPEN",
             f"bad={bad}")
        ok = p.resolve_unknown(e["entry_id"],
                               "42 Nm per the workshop manual",
                               resolver="pp3test:ace")
        _rec("resolve with evidence closes RESOLVED",
             ok.get("ok") and ok["entry"]["status"] == "RESOLVED"
             and ok["entry"]["resolver"] == "pp3test:ace"
             and bool(ok["entry"]["closed"]),
             f"ok={ok}")
        again = p.resolve_unknown(e["entry_id"], "another answer",
                                  resolver="pp3test")
        _rec("a closed unknown cannot be closed again",
             again.get("ok") is False
             and again.get("reason") == "already_closed",
             f"again={again}")
        r3 = p.record_unknown("widget torque",
                              "What torque does the widget need?",
                              source="pp3test")
        _rec("re-encountering a settled question opens a fresh entry",
             r3.get("created") is True
             and r3["entry"]["entry_id"] != e["entry_id"],
             f"r3={r3}")
        un = p.mark_unknown_unknowable(
            r3["entry"]["entry_id"],
            "The widget was a one-off; no manual exists.",
            resolver="pp3test:ace")
        _rec("mark unknowable with a reason closes UNKNOWABLE",
             un.get("ok") and un["entry"]["status"] == "UNKNOWABLE",
             f"un={un}")
        p2 = pload(owner, activate=False)
        by_id = {x["entry_id"]: x for x in p2.list_unknowns()}
        _rec("register persists through save and reload",
             by_id.get(e["entry_id"], {}).get("status") == "RESOLVED"
             and by_id.get(r3["entry"]["entry_id"], {}).get("status")
             == "UNKNOWABLE",
             f"reloaded={list(by_id.values())}")
    finally:
        _cleanup(owner)


def _check_section_contract():
    owner = "PP3Contract"
    good = unk.new_entry(owner, "subj", "question?", "pp3test")
    bad = dict(good)
    bad["entry_id"] = "a" * 32
    bad["resolution"] = "answered while open"
    raw = {"version": 1, "entries": {good["entry_id"]: good,
                                     bad["entry_id"]: bad}}
    valid, malformed = unk.validate_section(raw, owner)
    _rec("malformed records are preserved, not silently dropped",
         good["entry_id"] in valid
         and bad["entry_id"] not in valid
         and malformed is not None
         and bad["entry_id"] in malformed,
         f"valid={list(valid)} malformed={malformed}")
    ok, _why = unk.validate(good, owner)
    tampered = dict(good)
    tampered["status"] = "HALF_KNOWN"
    ok2, _ = unk.validate(tampered, owner)
    _rec("validation enforces the closed shape and status set",
         ok and not ok2, f"good={ok} tampered={ok2}")
    many = {}
    for i in range(201):
        e = unk.new_entry(owner, f"subject {i}", "question?", "pp3")
        e["opened"] = (f"2026-10-28T{i // 3600:02d}:"
                       f"{(i // 60) % 60:02d}:{i % 60:02d}Z")
        e["entry_id"] = f"{i:032x}"
        many[e["entry_id"]] = e
    sec = unk.serialize_section(many, None, owner)
    kept = sec.get("entries") or {}
    _rec("register bound keeps the newest 200, oldest evicted",
         len(kept) == 200 and f"{0:032x}" not in kept,
         f"kept={len(kept)}")


def _check_executor_capture():
    from form.mandell.executor import execute_seed
    owner = "PP3Exec"
    _cleanup(owner)
    try:
        p = Program(owner)
        res = execute_seed(p, "??? not a seed ???")
        parses = [e for e in p.list_unknowns("OPEN")
                  if e["source"] == "executor:parse"]
        _rec("unparseable seed is recorded as an unknown",
             res.get("ok") is False and len(parses) == 1
             and "could not be parsed" in parses[0]["question"],
             f"res_ok={res.get('ok')} parses={parses}")
        res = execute_seed(p, "86[Old] >> 10[Keep]")
        skips = [e for e in p.list_unknowns("OPEN")
                 if e["source"] == "executor:skip"]
        _rec("a skipped atom is recorded with its honest reason",
             res.get("any_skipped") is True and len(skips) == 1
             and "Dell 10 did not execute" in skips[0]["question"]
             and "FlowThru" in skips[0]["question"],
             f"skips={skips}")
        execute_seed(p, "86[Old] >> 10[Keep]")
        skips = [e for e in p.list_unknowns("OPEN")
                 if e["source"] == "executor:skip"]
        _rec("the same skip dedups on repeat (seen grows)",
             len(skips) == 1 and skips[0]["seen"] == 2,
             f"skips={skips}")
        before = len(p.list_unknowns())
        res = execute_seed(p, "10[Keep]")
        _rec("a clean execution records no unknown",
             res.get("ok") is True
             and len(p.list_unknowns()) == before,
             f"ok={res.get('ok')} before={before} "
             f"after={len(p.list_unknowns())}")
    finally:
        _cleanup(owner)


class _FlagJudge:
    """Scripted semantic judge (the P5 pattern): answers a flag
    verb with one valid flag proposal."""

    def generate(self, prompt, timeout_s=30, max_chars=8000):
        ids = re.findall(r'"(?:uid|pid)":\s*"([^"]+)"', prompt)
        return json.dumps({
            "label": "Flag: unverifiable",
            "words": "Claim cannot be verified.",
            "detail": "", "goals": [],
            "reason": "Nothing in the field supports this claim.",
            "parents": ids[:1]})


def _check_flag_capture():
    from form.dell_matrix import inference_dock as idock
    from form.dell_matrix.agent_coordinator import new_coordinator
    owner = "PP3Flag"
    _cleanup(owner)
    try:
        p = Program(owner)
        pr = p.nursery.add("MoonCheeseCore", words="MoonCheeseCore",
                           detail="The Moon has a core of aged cheese.")
        ctx = p.make_review_context(pr.id, reviewer="human:ace")
        r = p.confirm_proposal(pr.id, _producer="pp3test",
                               _review_context=ctx)
        assert r.get("ok"), r
        uid = None
        for u_id, u in p.cube.session.plane.units.items():
            if u.label == "MoonCheeseCore":
                uid = u_id
        assert uid, "unit not placed"
        s = idock.DockedSession(
            p, "agent-x", owner, "judge", _FlagJudge(),
            "judge:calibration", 30, 8000, 8000, task="propose")
        coord = new_coordinator(p)
        coord.register_agent("agent-x")
        object.__setattr__(s, "_coordinator", coord)
        out = s.flag(uid, concern="Verify the composition claim")
        flags = [e for e in p.list_unknowns("OPEN")
                 if e["source"] == "dock:flag:agent-x"]
        _rec("a docked flag records an OPEN unknown naming the entry",
             out.get("ok") is True and len(flags) == 1
             and flags[0]["subject"] == f"entry {uid}"
             and flags[0]["question"]
             == "Verify the composition claim",
             f"out={out.get('ok')} flags={flags}")
        s.undock()
    finally:
        _cleanup(owner)


def _check_repl_surface():
    owner = "PP3Repl"
    _cleanup(owner)
    root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "form.repl", "--owner", owner],
            input="86[Old] >> 10[Keep]\n10[Keep]\nunknowns\n",
            capture_output=True, text=True, cwd=root, timeout=300)
        m = re.search(r"id ([0-9a-f]{32})", proc.stdout)
        _rec("REPL lists the captured unknown with its id",
             m is not None and "executor:skip" in proc.stdout
             and "1 open" in proc.stdout,
             f"rc={proc.returncode} tail={proc.stdout[-300:]}")
        if m:
            eid = m.group(1)
            proc2 = subprocess.run(
                [sys.executable, "-m", "form.repl", "--owner", owner,
                 "--load"],
                input=f"unknowns resolve {eid} "
                      "Old was already gone; the skip was honest\n"
                      "unknowns all\n",
                capture_output=True, text=True, cwd=root, timeout=300)
            _rec("REPL resolve closes it with evidence (later process)",
                 "→ RESOLVED" in proc2.stdout
                 and "the skip was honest" in proc2.stdout,
                 f"tail={proc2.stdout[-300:]}")
    finally:
        _cleanup(owner)


def main():
    _check_register()
    _check_section_contract()
    _check_executor_capture()
    _check_flag_capture()
    _check_repl_surface()
    ok = sum(1 for _, c, _ in RESULTS if c)
    for name, cond, detail in RESULTS:
        print(f"{'PASS' if cond else 'FAIL'} {name}"
              + (f" :: {detail}" if not cond else ""))
    print(f"PP3_UNKNOWNS: {ok}/{len(RESULTS)}")
    return ok == len(RESULTS)


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
