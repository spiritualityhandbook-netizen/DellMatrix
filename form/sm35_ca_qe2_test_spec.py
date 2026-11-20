"""SM-35 C-A / Q-E2 failing-first spec (MWL #46, GATED — scoping only).

WHY A *_test_spec.py FILE (not a *_test.py): form/regress.py's
intended_entries() = LIST + every discovered form/**/*_test.py;
an unregistered failing suite in the registry path turns CI
smoke RED as an omitted/red entry (failure class proven on
PR #503, smoke run 44758805458). Both checks below FAIL on
current main by design. CODE-STAGE STEP ZERO (recorded in the
Part I plan): IF AND WHEN C-A is separately scoped and
authorized, merge these two cases into form/sm35_pair_atomic_
test.py's run_all (they reuse its _one_case machinery verbatim)
and delete this spec file. C-A is NOT authorized by Part I;
MWL #46 stays GATED; this spec is scoping evidence only.

Director C-A scoping (PR #294, comment 7040542941): the Q-E2
guarantee the checkpoint path already proves (SM-35 A1-A5/B1-B5,
GREEN) does NOT currently extend to the ORDINARY save path:
Program.save -> persist.save writes program + nursery files in
sequence with no pair journal, and persist.load performs no
pair-consistency recovery. The two cases below reuse the SM-35
child crash seams on the ordinary path (modes h1a/h1b) and ask
the Q-E2 question of a fresh-process view:

  CA-QE2-A / CA-QE2-B — after an ordinary save is interrupted
  between the two file writes, a fresh load must expose
  OLD_ONLY or NEW_PAIR — never a HYBRID of the new program
  generation with the old nursery generation (or vice versa).

EXPECTED TODAY: FAIL, verdict=HYBRID for both cases (measured
2026-11-20 on main af2519b6 via the in-suite form of these same
checks: SM35 51/53 with exactly these two red). The C-A fix
class, if ever authorized, is a pair journal + recovery in the
save/load authority — the same shape C-B designs for the
exchange path (see director-reports/
Q1_CB_TRANSACTION_DESIGN_2026-11-20.md).

Machinery note: _one_case is imported from the parent suite;
its internal sub-checks (setup / crash rc=42 / fresh view) print
in the parent's format and raise on their own failure, which
this spec records as a case failure. Children are genuine OS
processes running the parent suite file (CROSS_PROCESS tier,
same as the parent suite).

Standalone:  python3 form/sm35_ca_qe2_test_spec.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.sm35_pair_atomic_test import _one_case  # noqa: E402

RESULTS = []


def rec(name, ok, detail=""):
    RESULTS.append(bool(ok))
    line = f"[{'PASS' if ok else 'FAIL'}] {name}"
    if detail and not ok:
        line += f" — {detail}"[:300]
    print(line)


def main() -> bool:
    for case_id, owner, mode in (("CA-QE2-A", "SM35CA1", "h1a"),
                                 ("CA-QE2-B", "SM35CA2", "h1b")):
        name = (f"{case_id}: Q-E2 — fresh load exposes OLD_ONLY or "
                f"NEW_PAIR after interrupted ordinary save (never "
                f"HYBRID)")
        try:
            verdict, _view, _rewrote = _one_case(case_id, owner, mode)
            rec(name, verdict in ("OLD_ONLY", "NEW_PAIR"),
                f"verdict={verdict}")
        except AssertionError as exc:
            rec(name, False, f"parent machinery sub-check failed: {exc}")
        except Exception as exc:  # noqa: BLE001
            rec(name, False, f"machinery error: {exc!r}")
    print(f"SM35 CA-QE2 SPEC: {sum(RESULTS)}/{len(RESULTS)} "
          f"checks passed")
    return all(RESULTS)


def smoke() -> bool:
    try:
        return main()
    except Exception as exc:  # noqa: BLE001
        print(f"SM35 CA-QE2 SPEC SMOKE FAILED: {exc!r}")
        return False


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
