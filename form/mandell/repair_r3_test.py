"""Director review repair R3 — confirmed-idea grouping.

Independent review (Mode D, 2026-10-27) declined PR #105
(Phase M groups): `group add <id>` refused an ALREADY-CONFIRMED
Nursery idea as "a nursery proposal, not a live idea — confirm
it first". Root cause: the canonical resolver returns the
PROPOSAL record when a confirmed proposal and its plane unit
share one ID (one entity, proposal precedence — by design for
lineage display), and the group handler never mapped back to
the unit. lifecycle.py already documents and applies the
map-back pattern; the group handler now does the same, and
speaks honestly about the other statuses (confirmed-but-
unplaced, rejected, pending).

Proof standard: REAL_USER_PATH — the group commands run in a
separate REPL process against gate-confirmed state.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from form.open import Program  # noqa: E402

RESULTS = []
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:300]))


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


def _repl(owner, lines):
    r = subprocess.run(
        [sys.executable, "-m", "form.repl", "--owner", owner,
         "--load"],
        input="\n".join(lines) + "\n", cwd=ROOT,
        capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr[-600:]
    return r.stdout


def smoke() -> bool:
    owner = "RepairG1"
    _cleanup(owner)
    try:
        p = Program(owner=owner)

        def confirm(label):
            pr = p.nursery.add(label, words=label)
            ctx = p.make_review_context(pr.id, reviewer="human:ace")
            r = p.confirm_proposal(pr.id, _producer="repair_r3",
                                   _review_context=ctx)
            assert r.get("ok"), r
            return pr.id

        pid_by_id = confirm("Confirmed By Id")
        pid_by_label = confirm("Confirmed By Label")
        pending = p.nursery.add("Still Pending Idea",
                                words="pending")
        rejected = p.nursery.add("Rejected Idea", words="rejected")
        p.nursery.reject(rejected.id)
        p.save()

        out = _repl(owner, [
            "group create Field Team",
            f"group add {pid_by_id} to Field Team",
            "group add Confirmed By Label to Field Team",
            f"group add {pending.id} to Field Team",
            f"group add {rejected.id} to Field Team",
            "group show Field Team",
            "save",
        ])
        _rec("confirmed_add_by_id",
             f"Added Confirmed By Id ({pid_by_id})" in out,
             out[-400:])
        _rec("confirmed_add_by_label",
             f"Added Confirmed By Label ({pid_by_label})" in out)
        _rec("pending_still_refused_honestly",
             "not a live idea — confirm it first" in out)
        _rec("rejected_named_honestly",
             "is a rejected proposal" in out)
        _rec("show_lists_two_members",
             "2 member(s)" in out
             and pid_by_id in out and pid_by_label in out)

        out2 = _repl(owner, [
            f"group remove {pid_by_id} from Field Team",
            "group show Field Team",
        ])
        _rec("confirmed_remove_works",
             f"Removed Confirmed By Id ({pid_by_id})" in out2
             and "1 member(s)" in out2, out2[-300:])
    finally:
        _cleanup(owner)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")
    print(f"repair_r3_test {passed}/{len(RESULTS)}")
    return passed == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
