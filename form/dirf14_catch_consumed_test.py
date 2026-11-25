"""DIR-F14 — repeated Catch re-reports a consumed error.

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) on a real Program, plus
one hook-level decision witness:

- Pending vs consumed are distinct frame state: Catch moves
  the frame error into caught_error + caught_history and
  EMPTIES frame["error"]; status becomes "caught".
- A second (and third) Catch with no new failure reports
  "Catch (no error)", consumes nothing, and preserves the
  caught history exactly.
- A new post-Catch failure is a new pending root cause —
  including a failure whose error string is IDENTICAL to the
  consumed one (Delete the same absent key again): it is
  reported by the next Catch, never swallowed.
- Two different failures caught in sequence: caught_history
  preserves BOTH in order; caught_error holds the latest
  (the step-8 contract is unchanged).
- Failed-Commit evidence survives: commit_illegal stays in
  extra_errors across Catches and never becomes pending.
- Nested frames: inner Catch x2 never touches the outer
  frame; outer Catch with no outer failure reports no error.
- Chain path: Try > Delete > Catch > Catch > Commit in one
  seed reports the error once, then no error, then commits.
- Hook-level DECISION (packet P6/W3): a failure noted while
  status == "failed" dedupes (same outcome, two layers);
  a note arriving after Catch is a new failure signal and
  becomes the new root cause — no identity suppression.
- Regressions: no-error Catch creates no caught fields;
  Catch with no frame still refuses catch_illegal; Commit
  from "caught" and Revert after Catch behave as in step 8.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program).
"""
from __future__ import annotations

import glob
import os
import shutil

RESULTS: list = []


def _rec(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "state")
    if not os.path.isdir(base):
        return
    errors = []
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}.json",
                f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json",
                f"confirm_current_{owner}.json"):
        for f in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(f)
            except OSError as e:
                errors.append(f"{f}: {e}")
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        try:
            shutil.rmtree(d)
        except OSError as e:
            errors.append(f"{d}: {e}")
    if errors:
        raise RuntimeError(f"cleanup failed for {owner}: {errors}")


def _prog(owner: str):
    _cleanup(owner)
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=owner)
    attach(p)
    return p


def _run(p, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(p, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:",
                                 "Chain atoms=", "-- "))]


def _frame(p):
    return p.core_ii.tx[-1]


def _w1_repeated_catch() -> None:
    p = _prog("F14Rep")
    st = p.core_ii
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: absent")
    r = _run(p, "94[Catch]")
    f = _frame(p)
    _rec("W1 first Catch reports the error and CONSUMES it: "
         "pending emptied, archive holds it",
         _msgs(r) == ["Catch delete_missing:absent"]
         and f.get("status") == "caught"
         and f.get("error") == ""
         and f.get("caught_error") == "delete_missing:absent"
         and f.get("caught_history") == ["delete_missing:absent"],
         str(f))
    r = _run(p, "94[Catch]")
    f = _frame(p)
    _rec("W1 second Catch: 'Catch (no error)', nothing consumed, "
         "history preserved exactly",
         _msgs(r) == ["Catch (no error)"]
         and f.get("status") == "caught"
         and f.get("error") == ""
         and f.get("caught_error") == "delete_missing:absent"
         and f.get("caught_history") == ["delete_missing:absent"],
         f"{_msgs(r)} / {f}")
    r = _run(p, "94[Catch]")
    _rec("W1 third Catch: still 'Catch (no error)', history "
         "does not grow on empty Catches",
         _msgs(r) == ["Catch (no error)"]
         and _frame(p).get("caught_history")
         == ["delete_missing:absent"],
         f"{_msgs(r)} / {_frame(p)}")
    r = _run(p, "95[Commit]")
    _rec("W1 caught frame still commits (step-8 eligibility)",
         r.get("ok") is True
         and _frame(p).get("status") == "committed",
         f"{r.get('ok')} / {_frame(p)}")
    _cleanup("F14Rep")


def _w2_new_failure_after_catch() -> None:
    p = _prog("F14New")
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: firstmiss")
    _run(p, "94[Catch]")
    _run(p, "86[Delete] :: secondmiss")
    f = _frame(p)
    _rec("W2 new post-Catch failure is the new pending root; "
         "prior caught evidence untouched",
         f.get("status") == "failed"
         and f.get("error") == "delete_missing:secondmiss"
         and f.get("caught_error") == "delete_missing:firstmiss"
         and f.get("caught_history") == ["delete_missing:firstmiss"],
         str(f))
    r = _run(p, "94[Catch]")
    f = _frame(p)
    _rec("W2 second Catch reports the NEW error; history holds "
         "BOTH caught errors in order, caught_error is latest",
         _msgs(r) == ["Catch delete_missing:secondmiss"]
         and f.get("error") == ""
         and f.get("caught_error") == "delete_missing:secondmiss"
         and f.get("caught_history") == ["delete_missing:firstmiss",
                                         "delete_missing:secondmiss"],
         f"{_msgs(r)} / {f}")
    _run(p, "96[Revert]")
    _rec("W2 Revert after Catches still works (frame reverted)",
         _frame(p).get("status") == "reverted", str(_frame(p)))
    _cleanup("F14New")


def _w2b_same_error_string_new_failure() -> None:
    p = _prog("F14Same")
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: samekey")
    _run(p, "94[Catch]")
    r = _run(p, "86[Delete] :: samekey")
    f = _frame(p)
    _rec("W2b Delete of the SAME absent key after Catch is a "
         "NEW failure (ok=False, frame re-failed, error pending) "
         "— never swallowed as a duplicate of the consumed one",
         r.get("ok") is False
         and f.get("status") == "failed"
         and f.get("error") == "delete_missing:samekey",
         f"{r.get('ok')} / {f}")
    r = _run(p, "94[Catch]")
    _rec("W2b the new identical failure is reported by Catch "
         "and appended to history as a second catch",
         _msgs(r) == ["Catch delete_missing:samekey"]
         and _frame(p).get("caught_history")
         == ["delete_missing:samekey", "delete_missing:samekey"],
         f"{_msgs(r)} / {_frame(p)}")
    _cleanup("F14Same")


def _w3_hook_decision() -> None:
    p = _prog("F14Hook")
    st = p.core_ii
    from form.mandell.spectrum_ops import note_atom_failure
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: hookmiss")
    note_atom_failure(st, "delete_missing:hookmiss")
    f = _frame(p)
    _rec("W3 duplicate note while status=failed dedupes "
         "(same outcome reaching the hook from two layers)",
         f.get("status") == "failed"
         and f.get("error") == "delete_missing:hookmiss"
         and "delete_missing:hookmiss"
         not in f.get("extra_errors", []),
         str(f))
    _run(p, "94[Catch]")
    note_atom_failure(st, "delete_missing:hookmiss")
    f = _frame(p)
    _rec("W3 DECISION: a note arriving AFTER Catch is a new "
         "failure signal — it becomes the new pending root "
         "cause (no identity suppression in the hook)",
         f.get("status") == "failed"
         and f.get("error") == "delete_missing:hookmiss"
         and f.get("caught_error") == "delete_missing:hookmiss",
         str(f))
    _cleanup("F14Hook")


def _w4_nested() -> None:
    p = _prog("F14Nest")
    _run(p, "93[Try]")
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: innermiss")
    r = _run(p, "94[Catch]")
    _rec("W4 inner Catch reports the inner error",
         _msgs(r) == ["Catch delete_missing:innermiss"],
         str(_msgs(r)))
    r = _run(p, "94[Catch]")
    _rec("W4 inner second Catch: no error (consumed once)",
         _msgs(r) == ["Catch (no error)"], str(_msgs(r)))
    outer = p.core_ii.tx[-2]
    _rec("W4 outer frame untouched by inner Catches: still "
         "open, no pending error, no caught fields",
         outer.get("status") == "open"
         and outer.get("error") == ""
         and "caught_error" not in outer,
         str(outer))
    r = _run(p, "95[Commit]")
    _rec("W4 inner caught frame commits", r.get("ok") is True,
         f"{r.get('ok')} / {_msgs(r)}")
    r = _run(p, "94[Catch]")
    _rec("W4 outer Catch with no outer failure: no error",
         _msgs(r) == ["Catch (no error)"], str(_msgs(r)))
    r = _run(p, "95[Commit]")
    _rec("W4 outer frame commits from open",
         r.get("ok") is True, f"{r.get('ok')} / {_msgs(r)}")
    _cleanup("F14Nest")


def _w5_chain() -> None:
    p = _prog("F14Chain")
    r = _run(p, "93[Try] > 86[Delete] :: chainmiss > 94[Catch] "
                "> 94[Catch] > 95[Commit]")
    msgs = _msgs(r)
    _rec("W5 chain: error caught ONCE, second in-chain Catch "
         "reports no error, in-chain Commit accepted",
         msgs.count("Catch delete_missing:chainmiss") == 1
         and "Catch (no error)" in msgs
         and any(m.startswith("Commit") and "accepted" in m
                 for m in msgs),
         str(msgs))
    r = _run(p, "93[Try] > 86[Delete] :: chaina > 94[Catch] "
                "> 86[Delete] :: chainb > 94[Catch] > 95[Commit]")
    msgs = _msgs(r)
    f = _frame(p)
    _rec("W5 chain: two different failures each caught once; "
         "history preserves both in order",
         msgs.count("Catch delete_missing:chaina") == 1
         and msgs.count("Catch delete_missing:chainb") == 1
         and f.get("caught_history") == ["delete_missing:chaina",
                                         "delete_missing:chainb"],
         f"{msgs} / {f}")
    _cleanup("F14Chain")


def _w6_failed_commit_evidence() -> None:
    p = _prog("F14Commit")
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: rootmiss")
    r = _run(p, "95[Commit]")
    f = _frame(p)
    _rec("W6 Commit on failed frame refused; commit_illegal is "
         "extra evidence, root cause still pending",
         r.get("ok") is False
         and f.get("status") == "failed"
         and f.get("error") == "delete_missing:rootmiss"
         and "commit_illegal" in f.get("extra_errors", []),
         f"{r.get('ok')} / {f}")
    r = _run(p, "94[Catch]")
    f = _frame(p)
    _rec("W6 Catch consumes ONLY the root cause; commit_illegal "
         "evidence survives in extra_errors, never caught",
         _msgs(r) == ["Catch delete_missing:rootmiss"]
         and "commit_illegal" in f.get("extra_errors", [])
         and f.get("caught_history") == ["delete_missing:rootmiss"],
         f"{_msgs(r)} / {f}")
    r = _run(p, "94[Catch]")
    _rec("W6 second Catch does not catch the commit_illegal "
         "evidence either: no error",
         _msgs(r) == ["Catch (no error)"], str(_msgs(r)))
    r = _run(p, "95[Commit]")
    _rec("W6 frame commits after Catch (eligibility intact)",
         r.get("ok") is True, f"{r.get('ok')} / {_msgs(r)}")
    _cleanup("F14Commit")


def _w7_regressions() -> None:
    p = _prog("F14Reg")
    r = _run(p, "94[Catch]")
    _rec("W7 Catch with no frame still refuses catch_illegal",
         r.get("ok") is False and r.get("error") == "catch_illegal",
         f"{r.get('ok')} / {r.get('error')}")
    _run(p, "93[Try]")
    r = _run(p, "94[Catch]")
    f = _frame(p)
    _rec("W7 no-error Catch consumes nothing and creates NO "
         "caught_error / caught_history fields (step-8 contract)",
         _msgs(r) == ["Catch (no error)"]
         and f.get("status") == "open"
         and "caught_error" not in f
         and "caught_history" not in f,
         f"{_msgs(r)} / {f}")
    _cleanup("F14Reg")


def main() -> bool:
    _w1_repeated_catch()
    _w2_new_failure_after_catch()
    _w2b_same_error_string_new_failure()
    _w3_hook_decision()
    _w4_nested()
    _w5_chain()
    _w6_failed_commit_evidence()
    _w7_regressions()
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"DIRF14_CATCH_CONSUMED: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
