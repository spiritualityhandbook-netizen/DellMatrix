#!/usr/bin/env python3
"""Critic P1 / F7 — owner-namespace collision, NURSERY-FIRST order
(the circuit's regression suite; born as the failing-first fixture).

This suite expresses the isolation contract for the one order the
existing owner_namespace_collision_test never exercises: the first
owner writes ONLY nursery state (nursery.add persists immediately)
and never saves a program file before the second owner constructs.
As the prepared fixture it ran EXPECTED RED 4/7 against main
91eaa5a5 — failing exactly F2.second_owner_sees_none_of_first,
F2.private_detail_never_crosses, F3.first_owner_not_locked_out.
The authorized build (nursery owner binding: the nursery file
records its raw owner under a reserved section and the load /
add / save doors enforce it with OwnerCollisionError, extending
the program file's 72-34/DD-12 identity doctrine) turns it 7/7
GREEN; it now stands as the circuit's regression suite.

Authority / evidence trail:

  * Critic Master Critique, PR #530 review 6066727800, finding
    comment 4702349097 (P1): form/persist.py _safe_owner collapses
    distinct raw owners ("Fresh/Owner", "Fresh_Owner") onto one
    safe name, hence one nursery file; nursery.add persists
    immediately while no program file exists, so the second owner's
    fresh Program is constructed holding the first owner's proposal
    INCLUDING private detail; after the second owner saves, the
    first owner is locked out with OwnerCollisionError.
  * Uni verdict 7178450928 on issue #512: CONFIRMED_BEHAVIOR, REAL.
  * Uni first-hand reproduction at main 91eaa5a5 (2026-11-25):
    leak=True, detail_leak=True, first-owner lockout=True
    (hidden_files/critic_fixes_2026-11-25/repro_output.txt).
  * Director authorization 7180713277 on issue #512 (2026-11-25):
    "For 7, authorize a bounded owner-isolation repair covering
    the nursery-first path and preservation of existing owners'
    data."

Mechanism (verified against this tree):

  * form/persist.py:50-51 — _safe_owner maps every character that
    is not alphanumeric / '-' / '_' to '_'; it is many-to-one.
  * form/dell_matrix/nursery.py — owner_nursery_path keys the
    nursery file by the safe name ALONE:
    nursery_<_safe_owner(owner)>.json. Before this circuit the
    nursery file recorded no raw owner anywhere in its payload
    (verified: proposal records carry no owner field), so the
    nursery door had no identity to check even in principle. The
    build adds the OWNER_SECTION_KEY identity record, enforced by
    Nursery.load(path, owner=...) / add() / save().
  * form/dell_matrix/nursery.py (Nursery.add, tail) — add() calls
    self.save(): a proposal is durable the moment it is added.
  * form/open.py — Program.__post_init__ loads the live nursery
    with owner=self.owner, so the nursery identity record is
    enforced at construction exactly as the program file's is.
  * The original identity guard, persist.assert_program_owner_access
    (form/persist.py, called at Program construction), checks ONLY
    the program file program_<safe>.json. In the nursery-first
    order that file does not exist yet, the guard sees no proven
    owner and passes — which is why the nursery door needed its
    own binding. Once the second owner saved a program file, the
    same guard then locked the FIRST owner out.

Why the existing suite is green: owner_namespace_collision_test
build() always calls save(p) for the first owner before the second
owner loads, so the program-file guard fires and isolation holds.
The nursery-first branch is the uncovered seam.

Contract under test (shape-agnostic — a repair may either give
colliding owners disjoint namespaces OR refuse the foreign nursery
loudly at the nursery door; both satisfy isolation, silent
adoption satisfies neither):

- F1 premise: the chosen pair is distinct raw and DOES collide
  under _safe_owner; the control pair does not.
- F2 nursery-first no-adoption: owner A adds a proposal carrying
  private detail and never saves a program; constructing owner B
  must raise, or B's nursery must contain NONE of A's proposals
  (and in particular not the private detail).
- F3 no first-owner lockout: after B's flow completes (construct,
  and save if construction was allowed), A must still construct
  successfully and still hold its own proposal.
- K1 control: two NON-colliding owners stay fully isolated
  through the same nursery-first flow (A adds only; B constructs
  empty; B saves; A still constructs with its proposal intact).

Labels: INTEGRATION in-process.
Hygiene: uuid-unique owners; exact-pattern cleanup (files + the
ideas_<safe> directory); cleanup failures reported as a failing
check, never swallowed.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

from form.persist import _STATE_DIR, _path, _safe_owner, save
from form.dell_matrix.nursery import owner_nursery_path
from form.open import open_program

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]

A = f"CF{RUN}/A"   # raw owner with a separator (nursery-first)
B = f"CF{RUN}_A"   # distinct raw owner, same safe name
P = f"CF{RUN}P"    # non-colliding control pair
Q = f"CF{RUN}Q"
SECRET = "alpha private detail — must never cross owners"


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


def cleanup():
    for f in glob.glob(os.path.join(_STATE_DIR, f"*{RUN}*")):
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.unlink(f)
        except OSError as e:
            _CLEANUP_ERRORS.append(f"{f}: {e}")


def construct_or_none(owner):
    """Return (program, raised) — a loud refusal is a legitimate
    isolation outcome; silent foreign adoption is not."""
    try:
        return open_program(owner), False
    except Exception:
        return None, True


def main():
    cleanup()
    check("F1.collision_premise",
          A != B and _safe_owner(A) == _safe_owner(B)
          and owner_nursery_path(A) == owner_nursery_path(B)
          and _path(P) != _path(Q),
          f"safe={_safe_owner(A)}")

    # --- Nursery-first: A adds ONLY; no program save ----------
    pa = open_program(A)
    prop = pa.nursery.add("alpha private idea", "alpha words",
                          detail=SECRET)
    check("F1.nursery_first_premise",
          os.path.isfile(owner_nursery_path(A))
          and not os.path.isfile(_path(A)),
          "nursery durable, program file absent")

    # --- F2: B must not adopt A's nursery ---------------------
    pb, b_raised = construct_or_none(B)
    leaked = (pb is not None and prop.id in pb.nursery.proposals)
    detail_leaked = bool(
        leaked and pb.nursery.proposals[prop.id].detail == SECRET)
    check("F2.second_owner_sees_none_of_first",
          b_raised or not leaked,
          f"raised={b_raised} leaked={leaked}")
    check("F2.private_detail_never_crosses",
          b_raised or not detail_leaked,
          f"detail_leaked={detail_leaked}")

    # --- F3: B saves (if allowed); A must not be locked out ---
    if pb is not None:
        try:
            save(pb)
        except Exception:
            pass  # a loud save refusal also protects A — F3 judges A
    pa2, a_raised = construct_or_none(A)
    check("F3.first_owner_not_locked_out",
          not a_raised and pa2 is not None and pa2.owner == A
          and prop.id in pa2.nursery.proposals,
          f"a_raised={a_raised}")

    cleanup()

    # --- K1: non-colliding control, same nursery-first flow ---
    pp = open_program(P)
    p_prop = pp.nursery.add("papa idea", "papa words",
                            detail="papa detail")
    pq, q_raised = construct_or_none(Q)
    k1a = not q_raised and pq is not None \
        and p_prop.id not in pq.nursery.proposals
    if pq is not None:
        try:
            save(pq)
        except Exception:
            k1a = False
    pp2, p_raised = construct_or_none(P)
    k1b = not p_raised and pp2 is not None \
        and p_prop.id in pp2.nursery.proposals
    check("K1.noncolliding_nursery_first_isolated", k1a and k1b)

    cleanup()
    check("Z.cleanup_complete", not _CLEANUP_ERRORS,
          "; ".join(_CLEANUP_ERRORS))

    failed = [n for n, ok, _ in RESULTS if not ok]
    print(f"critic_owner_collision_fixture: "
          f"{len(RESULTS) - len(failed)}/{len(RESULTS)} PASS")
    if failed:
        print("FAILURES:", ", ".join(failed))
    return 1 if failed else 0


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
