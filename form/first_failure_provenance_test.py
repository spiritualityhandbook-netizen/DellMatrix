#!/usr/bin/env python3
"""72-19 — first-failure provenance through mixed chain
receipts: the FINAL COMPOSITION PROOF the register retained
as outstanding (Steps 7/8 proved per-frame provenance; this
suite composes the frames).

Acceptance (original inventory): "Failed, successful, and
skipped atoms must retain the original failure and accurate
partial-result accounting."

The provenance division of labor, grounded in chain_exec.py
and pinned here so any change is a conscious contract
change:

- atom_results (the receipt surface): occurrence-complete
  and execution-ordered across every composition — leaf
  sequences, Branch arms (unchosen = skipped receipts),
  Sequence/Parallel bodies, Until/While iterations,
  ForEach members (annotated), nested frames, refused
  control heads, and Join verdicts. The FIRST failing
  occurrence is always the true first failure, with its
  error verbatim. A Join whose incoming body failed records
  its own downstream 'join_fail' verdict AFTER the body
  failure — it never displaces it.
- result.error (the chain summary): the last leaf failure
  in execution order (execute_chain names it last_error),
  with first-preserving guards: a refused control head and
  a Join failure fill it only when no earlier failure
  stands; a loop bound_reached is the frame's terminal
  verdict and closes the chain error. Where the two
  surfaces diverge (C8b), both are pinned.
- The outcome hook (spectrum_ops.note_atom_failure, when a
  transaction is open): the tx frame's error is the FIRST
  root cause; later failures accumulate in extra_errors.
  C9 pins cross-surface agreement: receipt first failure ==
  tx root cause.

Existing coverage (NOT duplicated): step8_transactions_test
(tx-frame internals, Catch), eoc_i_test (per-node evidence),
control_runtime_test (frame mechanics), dirf14 (Catch
consumption).

Labels: PUBLIC_ENTRY_PATH throughout (execute_seed).
Hygiene: uuid-unique owners; exact-pattern cleanup;
cleanup failures reported, never swallowed.
"""
from __future__ import annotations

import os
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


def _fresh(tag):
    from form.open import open_program
    return open_program(f"T7219{tag}{RUN}")


def _fails(out):
    return [(r.get("dell"), r.get("error"), r.get("member"))
            for r in (out.get("atom_results") or [])
            if not r.get("ok", True) and not r.get("skipped")]


def _first(out):
    f = _fails(out)
    return f[0] if f else None


def _cleanup(tag):
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    owner = f"T7219{tag}{RUN}"
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


def main():
    from form.mandell.executor import execute_seed

    # C1: leaf - leaf - success
    p = _fresh("C1")
    out = execute_seed(
        p, "86[Delete] :: firstmiss > 86[Delete] :: secondmiss "
           "> 55[Set] :: ok=1")
    check("C1.first_is_first",
          _first(out) == (86, "delete_missing:firstmiss", None),
          str(_first(out)))
    check("C1.both_failures_in_order",
          [e for _, e, _ in _fails(out)] == [
              "delete_missing:firstmiss",
              "delete_missing:secondmiss"], str(_fails(out)))
    check("C1.chain_error_is_last_leaf",
          out.get("error") == "delete_missing:secondmiss",
          str(out.get("error")))
    check("C1.accounting",
          out.get("ok") is False and out.get("partial") is True)
    _cleanup("C1")

    # C2: leaf failure, then a succeeding Sequence frame
    p = _fresh("C2")
    out = execute_seed(
        p, "86[Delete] :: firstmiss > 63[Sequence] > 80[TrueArm] "
           "> 61[Join]")
    check("C2.first_retained_before_frame",
          _first(out) == (86, "delete_missing:firstmiss", None))
    check("C2.chain_error", out.get("error")
          == "delete_missing:firstmiss")
    _cleanup("C2")

    # C3: succeeding frame, then a leaf failure
    p = _fresh("C3")
    out = execute_seed(
        p, "63[Sequence] > 80[TrueArm] > 61[Join] "
           "> 86[Delete] :: latemiss")
    check("C3.first_is_the_leaf",
          _first(out) == (86, "delete_missing:latemiss", None))
    check("C3.chain_error", out.get("error")
          == "delete_missing:latemiss")
    _cleanup("C3")

    # C4: Branch taken-arm failure; unchosen arm skipped;
    # Join verdict downstream of the first failure
    p = _fresh("C4")
    out = execute_seed(
        p, "60[true] > 86[Delete] :: branchmiss > 59[Else] "
           "> 80[TrueArm] > 61[Join] > 55[Set] :: after=1")
    check("C4.first_is_branch_failure",
          _first(out) == (86, "delete_missing:branchmiss", None),
          str(_first(out)))
    check("C4.join_fail_is_downstream_not_first",
          [e for _, e, _ in _fails(out)] == [
              "delete_missing:branchmiss", "join_fail"],
          str(_fails(out)))
    check("C4.chain_error_is_body_failure",
          out.get("error") == "delete_missing:branchmiss")
    check("C4.accounting_skips",
          out.get("any_skipped") is True
          and out.get("partial") is True)
    _cleanup("C4")

    # C5: nested Branch-in-Sequence failure, then top failure
    p = _fresh("C5")
    out = execute_seed(
        p, "63[Sequence] > 60[true] > 86[Delete] :: nestmiss "
           "> 61[Join] > 61[Join] > 86[Delete] :: topmiss")
    check("C5.first_is_nested_failure",
          _first(out) == (86, "delete_missing:nestmiss", None),
          str(_first(out)))
    check("C5.failures_in_execution_order",
          [e for _, e, _ in _fails(out)] == [
              "delete_missing:nestmiss", "join_fail", "join_fail",
              "delete_missing:topmiss"], str(_fails(out)))
    check("C5.chain_error_is_last_leaf",
          out.get("error") == "delete_missing:topmiss")
    _cleanup("C5")

    # C6: Until loop, two distinct body failures x2 iterations;
    # bound_reached closes the chain error, receipts keep order
    p = _fresh("C6")
    execute_seed(p, "72[Limit] :: 2")
    out = execute_seed(
        p, "64[false] > 86[Delete] :: missA "
           "> 86[Delete] :: missB > 61[Join]")
    check("C6.first_is_iteration1_first",
          _first(out) == (86, "delete_missing:missA", None),
          str(_first(out)))
    check("C6.iteration_order_preserved",
          [e for _, e, _ in _fails(out)][:4] == [
              "delete_missing:missA", "delete_missing:missB",
              "delete_missing:missA", "delete_missing:missB"],
          str(_fails(out)))
    check("C6.chain_error_is_bound_verdict",
          out.get("error") == "bound_reached", str(out.get("error")))
    _cleanup("C6")

    # C7: ForEach — the failing occurrence carries its member
    p = _fresh("C7")
    out = execute_seed(
        p, "51[Select] > 66[ForEach] > 86[Delete] :: femiss "
           "> 61[Join]")
    f7 = _fails(out)
    check("C7.first_carries_member",
          bool(f7) and f7[0][1] == "delete_missing:femiss"
          and bool(f7[0][2]), str(f7[:1]))
    check("C7.chain_error", out.get("error")
          == "delete_missing:femiss")
    _cleanup("C7")

    # C8a: leaf failure, then a refused control head —
    # the head refusal never overwrites the earlier root cause
    p = _fresh("C8A")
    out = execute_seed(
        p, '86[Delete] :: firstmiss > 63[Sequence](x="1") '
           '> 80[TrueArm] > 61[Join]')
    check("C8a.first_is_leaf",
          _first(out) == (86, "delete_missing:firstmiss", None))
    check("C8a.head_refusal_recorded",
          [e for _, e, _ in _fails(out)][1:]
          == ["UNSUPPORTED_ARGS: x"], str(_fails(out)))
    check("C8a.chain_error_keeps_first",
          out.get("error") == "delete_missing:firstmiss",
          str(out.get("error")))
    check("C8a.body_skipped_not_failed",
          out.get("any_skipped") is True)
    _cleanup("C8A")

    # C8b: refused head first, then a leaf failure — the two
    # surfaces diverge BY DESIGN; pin both
    p = _fresh("C8B")
    out = execute_seed(
        p, '63[Sequence](x="1") > 80[TrueArm] > 61[Join] '
           '> 86[Delete] :: latemiss')
    check("C8b.receipt_first_is_head_refusal",
          _first(out) == (63, "UNSUPPORTED_ARGS: x", None),
          str(_first(out)))
    check("C8b.chain_error_is_last_leaf",
          out.get("error") == "delete_missing:latemiss",
          str(out.get("error")))
    _cleanup("C8B")

    # C9: transaction open + failures inside a Sequence frame:
    # receipt first failure == tx root cause; later failures
    # accumulate in extra_errors in order
    p = _fresh("C9")
    execute_seed(p, "93[Try]")
    out = execute_seed(
        p, "63[Sequence] > 86[Delete] :: txfirst "
           "> 86[Delete] :: txsecond > 61[Join]")
    check("C9.receipt_first",
          _first(out) == (86, "delete_missing:txfirst", None))
    tx = p.core_ii.tx[-1]
    check("C9.tx_root_cause_is_first",
          tx.get("error") == "delete_missing:txfirst",
          str(tx.get("error")))
    check("C9.tx_extra_errors_in_order",
          tx.get("extra_errors") == [
              "delete_missing:txsecond", "join_fail"],
          str(tx.get("extra_errors")))
    check("C9.cross_surface_agreement",
          _first(out)[1] == tx.get("error"))
    _cleanup("C9")

    # C10: body failure + refused Join — the Join refusal
    # never overwrites the body failure on either surface
    p = _fresh("C10")
    out = execute_seed(
        p, '63[Sequence] > 86[Delete] :: bodymiss '
           '> 61[Join](x="1")')
    check("C10.first_is_body",
          _first(out) == (86, "delete_missing:bodymiss", None))
    check("C10.chain_error_keeps_body",
          out.get("error") == "delete_missing:bodymiss",
          str(out.get("error")))
    _cleanup("C10")

    # C11: partial accounting
    p = _fresh("C11A")
    out = execute_seed(
        p, "60[false] > 80[TrueArm] > 61[Join] > 55[Set] :: ok=1")
    check("C11a.lawful_skip_accounting",
          out.get("ok") is True and out.get("partial") is True
          and out.get("any_skipped") is True
          and out.get("error") == "",
          f"ok={out.get('ok')} partial={out.get('partial')}")
    _cleanup("C11A")
    p = _fresh("C11B")
    out = execute_seed(p, "55[Set] :: a=1 > 55[Set] :: b=2")
    check("C11b.clean_chain_accounting",
          out.get("ok") is True and out.get("partial") is False
          and out.get("any_skipped") is False)
    _cleanup("C11B")

    # C12: Parallel — failing member + succeeding sibling,
    # then a top-level failure
    p = _fresh("C12")
    out = execute_seed(
        p, "62[Parallel] > 86[Delete] :: parmiss > 80[TrueArm] "
           "> 61[Join] > 86[Delete] :: aftermiss")
    check("C12.first_is_parallel_member",
          _first(out) == (86, "delete_missing:parmiss", None),
          str(_first(out)))
    check("C12.chain_error_is_last_leaf",
          out.get("error") == "delete_missing:aftermiss")
    _cleanup("C12")

    # C13: While — body failure in the single iteration
    p = _fresh("C13")
    execute_seed(p, "55[Set] :: go=1")
    execute_seed(p, "72[Limit] :: 4")
    out = execute_seed(
        p, "65[store_go] > 86[Delete] :: whilemiss > 86[go] "
           "> 61[Join]")
    check("C13.first_is_while_body",
          _first(out) == (86, "delete_missing:whilemiss", None),
          str(_first(out)))
    check("C13.chain_error",
          out.get("error") == "delete_missing:whilemiss")
    _cleanup("C13")

    check("cleanup.no_errors", not _CLEANUP_ERRORS,
          str(_CLEANUP_ERRORS))
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"first_failure_provenance_test: "
          f"{passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
