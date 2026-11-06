#!/usr/bin/env python3
"""72-31 — Nursery optimistic concurrency + duplicate confirmation
(= SM-31): two live stale instances racing confirm.

Existing coverage (NOT duplicated): foundation_acceptance's
lost_update_explicit pins a stale confirm refused after an
intervening nursery ADD, and the 72-31 scoping probe
(hidden_files/72-31_probe.py) pins the Nursery level. This suite
pins the register's missing evidence at the PROGRAM level:

  Controls (must hold):
  - N* Nursery level (isolated temp file): two stale instances;
    first confirm succeeds; stale second refused with
    NurseryConflictError, in-memory status rolled back; fresh
    reload confirmed exactly once; duplicate confirm on one
    instance is a clean no-op; stale ADD refused, no lost update.
  - P* Program level, sequential stale (both instances loaded
    from the SAME generation before either confirms): first
    confirm ok; stale second refused explicitly
    (nursery_conflict), loser's in-memory proposal stays pending
    with no placed unit; canonical reload (Nursery.load +
    persist_rest.load) shows confirmed + the Idea exactly once;
    a further confirm on the reloaded instance is refused.

  Defects (fail at the unrepaired head):
  - D1 interleaved commit (deterministic): the loser's commit is
    intercepted so the winner's confirm completes first, then
    the loser's commit proceeds and is refused — but the loser's
    failure compensation restores the BASELINE BYTES captured
    before the winner committed, silently overwriting the
    winner's confirmed Nursery + Program state. Reload then
    shows pending / no unit: a reported-success confirmation is
    lost. The winner's committed state must survive the loser's
    refused attempt.
  - D2 true concurrent cross-process race (barrier-synchronised
    workers, both loaded + authorised before either confirms):
    combined contract — exactly one worker reports ok AND the
    canonical reload shows confirmed + the Idea exactly once.
    At the unrepaired head every probed run violated it
    (8/8: double-ok, or ok+conflict with the winner lost).

Labels: CROSS_PROCESS for D2 (fresh OS processes against the real
Program authority); the rest INTEGRATION / REAL_PROGRAM.
State hygiene: uuid-unique owners; cleanup failures are reported
in the final check, never swallowed.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _clean(owner):
    for p in glob.glob(os.path.join(REPO, "form", "state", f"*{owner}*")):
        try:
            os.remove(p) if os.path.isfile(p) else shutil.rmtree(p)
        except Exception as e:  # noqa: BLE001
            _CLEANUP_ERRORS.append(f"{p}:{type(e).__name__}")


def _owner(tag):
    return f"T7231{tag}" + uuid.uuid4().hex[:8]


def _reload(owner, pid):
    from form.dell_matrix.nursery import Nursery, owner_nursery_path
    from form import persist_rest
    n = Nursery.load(owner_nursery_path(owner))
    status = n.proposals[pid].status if pid in n.proposals else "ABSENT"
    p = persist_rest.load(owner, activate=False)
    units = p.cube.session.plane.units
    return {"status": status, "unit": pid in units,
            "label_count": sum(1 for u in units.values()
                               if u.label == "Race Idea")}


def _confirm(p, pid):
    try:
        r = p.confirm_proposal(
            pid, _producer="test",
            _review_context=p.make_review_context(pid, "test"))
        return {"ok": r.get("ok") is True, "reason": r.get("reason"),
                "raw": r}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"raised:{type(e).__name__}",
                "raw": {}}


# ---------------------------------------------------------------- N
def case_nursery():
    from form.dell_matrix.nursery import Nursery, NurseryConflictError
    tmp = tempfile.mkdtemp(prefix="n31_")
    path = os.path.join(tmp, "nursery_test.json")
    try:
        s = Nursery.load(path)
        pid = s.add("Race Idea", words="alpha beta").id
        a, b = Nursery.load(path), Nursery.load(path)
        check("N.both_see_pending",
              a.proposals[pid].status == "pending"
              and b.proposals[pid].status == "pending")
        ra = a.confirm(pid)
        check("N.first_confirm_ok",
              ra is not None and ra.status == "confirmed")
        try:
            b.confirm(pid)
            bout = "no-raise"
        except NurseryConflictError:
            bout = "conflict"
        except Exception as e:  # noqa: BLE001
            bout = f"other:{type(e).__name__}"
        check("N.stale_confirm_refused", bout == "conflict", bout)
        check("N.stale_inmemory_rolled_back",
              b.proposals[pid].status == "pending")
        c = Nursery.load(path)
        check("N.reload_confirmed_once",
              c.proposals[pid].status == "confirmed"
              and c.summary()["confirmed"] == 1
              and c.summary()["total"] == 1)
        check("N.dup_confirm_noop", c.confirm(pid) is None)
        d, e = Nursery.load(path), Nursery.load(path)
        d.add("Second Idea", words="gamma")
        try:
            e.add("Third Idea", words="delta")
            eout = "no-raise"
        except NurseryConflictError:
            eout = "conflict"
        except Exception as ex:  # noqa: BLE001
            eout = f"other:{type(ex).__name__}"
        labels = sorted(p.label for p in Nursery.load(path).proposals.values())
        check("N.stale_add_refused_no_lost_update",
              eout == "conflict" and labels == ["Race Idea", "Second Idea"],
              f"{eout} {labels}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- P
def case_program_sequential():
    from form.open import open_program
    owner = _owner("SEQ")
    _clean(owner)
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        a, b = open_program(owner), open_program(owner)
        check("P.both_see_pending",
              a.nursery.proposals[pid].status == "pending"
              and b.nursery.proposals[pid].status == "pending"
              and pid not in a.cube.session.plane.units
              and pid not in b.cube.session.plane.units)
        ra = _confirm(a, pid)
        check("P.first_confirm_ok", ra["ok"], str(ra["raw"])[:200])
        rb = _confirm(b, pid)
        check("P.stale_confirm_refused_conflict",
              not rb["ok"] and rb["reason"] == "nursery_conflict",
              str(rb["raw"])[:200])
        check("P.loser_inmemory_pending_no_unit",
              b.nursery.proposals[pid].status == "pending"
              and pid not in b.cube.session.plane.units)
        rel = _reload(owner, pid)
        check("P.reload_confirmed_exactly_once",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
        c = open_program(owner)
        rdup = _confirm(c, pid)
        check("P.reload_dup_confirm_refused", not rdup["ok"],
              str(rdup["raw"])[:200])
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D1
def case_interleaved_commit():
    from form.open import open_program
    import form.mandell.checkpoint_generation as cg
    owner = _owner("INT")
    _clean(owner)
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        loser, winner = open_program(owner), open_program(owner)
        orig_commit = cg.commit_checkpoint
        state = {"fired": False, "winner": None}

        def intercept(program, *a, **kw):
            if not state["fired"]:
                state["fired"] = True
                # Winner's confirm completes ENTIRELY (its own commit
                # goes through the original function) before the
                # loser's commit proceeds.
                state["winner"] = _confirm(winner, pid)
            return orig_commit(program, *a, **kw)

        cg.commit_checkpoint = intercept
        try:
            rl = _confirm(loser, pid)
        finally:
            cg.commit_checkpoint = orig_commit
        check("D1.winner_confirm_ok",
              bool(state["winner"] and state["winner"]["ok"]),
              str(state["winner"]))
        check("D1.loser_refused", not rl["ok"], str(rl["raw"])[:200])
        rel = _reload(owner, pid)
        check("D1.winner_state_survives_loser_refusal",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, str(rel))
    finally:
        _clean(owner)


# ---------------------------------------------------------------- D2
_WORKER = r"""
import json, os, sys, time
sys.path.insert(0, %(REPO)r)
owner, pid, barrier, ready, outp = sys.argv[1:6]
from form.open import open_program
p = open_program(owner)
ctx = p.make_review_context(pid, "test")
open(ready, "w").write("ready")
deadline = time.time() + 60
while not os.path.exists(barrier):
    if time.time() > deadline: sys.exit(3)
    time.sleep(0.02)
try:
    r = p.confirm_proposal(pid, _producer="test", _review_context=ctx)
    res = {"ok": r.get("ok") is True, "reason": r.get("reason")}
except Exception as e:
    res = {"ok": False, "reason": "raised:" + type(e).__name__}
open(outp, "w").write(json.dumps(res))
print(json.dumps(res))
"""


def case_concurrent(attempt):
    from form.open import open_program
    owner = _owner("CON")
    _clean(owner)
    tmp = tempfile.mkdtemp(prefix="n31con_")
    try:
        pid = open_program(owner).nursery.add(
            "Race Idea", words="alpha beta").id
        barrier = os.path.join(tmp, "go")
        procs = []
        for k in range(2):
            procs.append(subprocess.Popen(
                [sys.executable, "-c", _WORKER % {"REPO": REPO},
                 owner, pid, barrier, os.path.join(tmp, f"ready{k}"),
                 os.path.join(tmp, f"out{k}.json")],
                cwd=REPO, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True))
        deadline = time.time() + 60
        while time.time() < deadline and not all(
                os.path.exists(os.path.join(tmp, f"ready{k}"))
                for k in range(2)):
            time.sleep(0.05)
        open(barrier, "w").write("go")
        results = []
        for prc in procs:
            prc.communicate(timeout=120)
            results.append(prc.returncode)
        outs = []
        for k in range(2):
            try:
                outs.append(json.loads(
                    open(os.path.join(tmp, f"out{k}.json")).read()))
            except Exception:  # noqa: BLE001
                outs.append({"ok": None, "reason": "no-output"})
        n_ok = sum(1 for o in outs if o.get("ok") is True)
        rel = _reload(owner, pid)
        check(f"D2.concurrent_exactly_one_ok[{attempt}]", n_ok == 1,
              f"workers={outs}")
        check(f"D2.concurrent_winner_preserved[{attempt}]",
              rel["status"] == "confirmed" and rel["unit"]
              and rel["label_count"] == 1, f"{outs} reload={rel}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _clean(owner)


def main():
    case_nursery()
    case_program_sequential()
    case_interleaved_commit()
    case_concurrent(1)
    case_concurrent(2)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"nursery_confirm_race_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
