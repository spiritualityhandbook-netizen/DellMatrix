#!/usr/bin/env python3
"""72-27 — Guard/Assert frame propagation adjudication
(evidence circuit).

Acceptance (register): "Deterministic frame/error
behavior when guards fail inside control compositions."

Guard (92) and Assert (91) evaluate their label as a
condition (control_runtime.eval_condition); a failed
Assert records last_assert=FAIL and fails assert_fail; a
blocked Guard records last_guard=BLOCK and fails
guard_block (the labels "block"/"deny" force BLOCK);
both fail any open transaction frame. Prior suites pin
the two Dells standalone (registry spectrum) and the
transaction Catch discipline (Step 8). This suite
adjudicates how their failures PROPAGATE through the
control compositions, at the public entry path:

- Bare in a chain: an honest failure receipt; the chain
  error is the Dell's own; the NEXT atom still runs —
  Guard/Assert failures are captured verdicts, not
  chain halts (the same continue-on-failure contract
  pinned for every atom in 72-19/72-20).
- Inside a Sequence: the frame settles 'fail', the
  Join judges the executed failure (join_fail), and
  later Sequence members still run. A passing Guard
  settles 'ok' end to end.
- Inside a Branch: a failing Assert in the taken arm
  fails the branch frame and the Join; an Assert in
  the UNCHOSEN arm is skipped and never evaluated
  (last_assert untouched), branch and Join 'ok'.
- Nested Sequences: the failure propagates exactly
  one Join per level (inner join_fail -> outer
  join_fail), frames settle 'fail' at both levels,
  and the outer Sequence's later member still runs.
- Inside a While body: the Guard failure is one
  executed failure in that iteration — the body's
  remaining member still runs in the same iteration,
  the loop ends on its condition, the frame settles
  'fail', the Join judges join_fail.
- Inside Try/Catch: Catch executes (its receipt is
  ok — it consumes the transaction frame's error),
  while the chain error remains the Guard's own
  (the standing last-leaf summary contract, 72-19).

Labels: PUBLIC_ENTRY_PATH throughout (execute_seed).
Hygiene: uuid-unique owners; exact-pattern cleanup;
cleanup failures reported, never swallowed.
"""
from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []
RUN = uuid.uuid4().hex[:8]


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _prog(tag):
    from form.open import Program
    from form.mandell.core_ii_exec import attach
    p = Program(owner=f"T7227{tag}{RUN}")
    attach(p)
    return p


def _run(p, chain):
    from form.mandell.executor import execute_seed
    return execute_seed(p, chain)


def _recs(out, dell=None):
    rs = out.get("atom_results", [])
    if dell is not None:
        rs = [r for r in rs if r.get("dell") == dell]
    return [(r.get("ok"), r.get("error") or None,
             bool(r.get("skipped"))) for r in rs]


def _settled(p, kind):
    fs = [f for f in p.core_ii.frames if f.get("kind") == kind]
    return fs[-1].get("status") if fs else None


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7227{tag}{RUN}"
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")


TAGS = []


def main():
    # -- A: bare verdicts ----------------------------------------------
    tag = "A"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "92[false] > 55[Set] :: after=1")
    check("A1.guard_block_bare_next_atom_runs",
          _recs(out) == [(False, "guard_block", False),
                         (True, None, False)]
          and out["error"] == "guard_block"
          and st.store.get("after") == "1"
          and st.last_guard == "BLOCK" and out["partial"] is True,
          f"{_recs(out)} err={out['error']!r} lg={st.last_guard!r}")

    tag = "B"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "91[false] > 55[Set] :: after=1")
    check("B1.assert_fail_bare_next_atom_runs",
          _recs(out) == [(False, "assert_fail", False),
                         (True, None, False)]
          and out["error"] == "assert_fail"
          and st.store.get("after") == "1"
          and st.last_assert == "FAIL",
          f"{_recs(out)} err={out['error']!r} la={st.last_assert!r}")

    tag = "C"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: go=1")
    out = _run(p, "92[store_go]")
    check("C1.guard_store_condition_allows",
          out["ok"] is True and st.last_guard == "ALLOW",
          f"ok={out['ok']} lg={st.last_guard!r}")
    out = _run(p, "92[block]")
    check("C2.guard_deny_label_blocks",
          out["ok"] is False and out["error"] == "guard_block"
          and st.last_guard == "BLOCK",
          f"err={out['error']!r} lg={st.last_guard!r}")
    out = _run(p, "91[true]")
    check("C3.assert_pass_records_pass",
          out["ok"] is True and st.last_assert == "PASS",
          f"ok={out['ok']} la={st.last_assert!r}")

    # -- D: Sequence ----------------------------------------------------
    tag = "D"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "63[Sequence] > 92[false] > 55[Set] :: after=1 > 61[Join]")
    check("D1.guard_in_sequence_frame_fail_join_fail",
          _recs(out, 61) == [(False, "join_fail", False)]
          and _settled(p, "sequence") == "fail"
          and out["error"] == "guard_block",
          f"r61={_recs(out, 61)} seq={_settled(p, 'sequence')}")
    check("D2.guard_in_sequence_later_member_runs",
          st.store.get("after") == "1"
          and _recs(out, 92) == [(False, "guard_block", False)],
          f"store={dict(st.store)}")

    tag = "E"; TAGS.append(tag)
    p = _prog(tag)
    out = _run(p, "63[Sequence] > 92[true] > 55[Set] :: after=1 > 61[Join]")
    check("E1.guard_pass_sequence_all_ok",
          out["ok"] is True and _settled(p, "sequence") == "ok"
          and _recs(out, 61) == [(True, None, False)],
          f"ok={out['ok']} seq={_settled(p, 'sequence')}")

    # -- F: Branch -------------------------------------------------------
    tag = "F"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "60[true] > 91[false] > 59[Else] > 55[Set] :: alt=1 > 61[Join]")
    check("F1.assert_taken_arm_branch_fail_join_fail",
          _settled(p, "branch") == "fail"
          and _recs(out, 61) == [(False, "join_fail", False)]
          and out["error"] == "assert_fail" and dict(st.store) == {},
          f"br={_settled(p, 'branch')} r61={_recs(out, 61)}")

    tag = "G"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "60[false] > 91[false] > 59[Else] > 55[Set] :: alt=1 > 61[Join]")
    check("G1.assert_unchosen_arm_skipped_never_evaluated",
          _recs(out, 91) == [(False, None, True)]
          and st.last_assert == "" and out["ok"] is True
          and _settled(p, "branch") == "ok"
          and st.store.get("alt") == "1",
          f"r91={_recs(out, 91)} la={st.last_assert!r}")

    # -- H: nested Sequences ---------------------------------------------
    tag = "H"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    out = _run(p, "63[Sequence] > 63[Sequence] > 91[false] > 61[Join] "
                  "> 55[Set] :: after=1 > 61[Join]")
    check("H1.nested_assert_propagates_one_join_per_level",
          _recs(out, 61) == [(False, "join_fail", False),
                             (False, "join_fail", False)]
          and _settled(p, "sequence") == "fail"
          and out["error"] == "assert_fail",
          f"r61={_recs(out, 61)} seq={_settled(p, 'sequence')}")
    check("H2.nested_outer_later_member_still_runs",
          st.store.get("after") == "1", f"store={dict(st.store)}")

    # -- I: While body ----------------------------------------------------
    tag = "I"; TAGS.append(tag)
    p = _prog(tag)
    st = p.core_ii
    _run(p, "55[Set] :: go=1")
    out = _run(p, "65[store_go] > 92[false] > 86[Delete] :: go > 61[Join]")
    check("I1.guard_in_while_body_one_iteration_frame_fail",
          _recs(out, 92) == [(False, "guard_block", False)]
          and _settled(p, "while") == "fail"
          and _recs(out, 61) == [(False, "join_fail", False)],
          f"r92={_recs(out, 92)} while={_settled(p, 'while')}")
    check("I2.guard_in_while_body_sibling_still_runs",
          dict(st.store) == {}, f"store={dict(st.store)}")

    # -- J: Try/Catch ------------------------------------------------------
    tag = "J"; TAGS.append(tag)
    p = _prog(tag)
    out = _run(p, "93[Try] > 92[false] > 94[Catch]")
    check("J1.guard_in_try_catch_executes_chain_error_stays",
          _recs(out) == [(True, None, False),
                         (False, "guard_block", False),
                         (True, None, False)]
          and out["error"] == "guard_block",
          f"{_recs(out)} err={out['error']!r}")

    for t in TAGS:
        _cleanup(t)
    check("cleanup.no_errors", not _CLEANUP_ERRORS, str(_CLEANUP_ERRORS))

    total = len(RESULTS)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"guard_assert_propagation_test: {passed}/{total} PASS")
    return 0 if passed == total else 1


def smoke():
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
