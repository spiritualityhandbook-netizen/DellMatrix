"""Director order step 8 — transactions (B15/B16/B17).

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) on a real Program:

- B15: EVERY executed atom failure marks the innermost active
  transaction frame failed via the one canonical outcome hook
  (spectrum_ops.note_atom_failure) — spectrum (Delete/Patch),
  other Core II (Scope), composition-adjacent and leaf (Create
  TOAM) failures included, on BOTH the single-atom path and
  the one-seed chain path. A failed frame cannot commit as
  clean (commit_illegal). False predicates used as data
  (Select no-match) and lawful skips (FlowOver) are NOT
  failures and never fail a frame.
- B16: error ownership belongs to the frame. A new Try has
  clean frame error state: Catch never captures a
  pre-transaction sticky error. Catch consumes the frame's
  own error (caught_error recorded); the first root cause is
  preserved — a second failure lands in extra_errors, and a
  failed Commit attempt's commit_illegal is additional
  evidence only. Catch with no frame error reports
  "Catch (no error)" explicitly and consumes nothing. A
  failure AFTER a Catch is a new root cause.
- B17: Commit is live mark/accept — mutations inside a Try
  are visible before Commit; there is no atomic staged
  isolation. Revert restores exactly the checkpoint field
  set (store/groups shown); fields outside the set (traces)
  are not rolled back. AF5 bounds retained: terminal frames
  pruned to TERMINAL_TX_KEEP, ids monotonic.
- Nested isolation: an inner failure fails ONLY the inner
  frame; inner Catch/Commit leave the outer frame open and
  committable.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program via
form.open.Program, public executor).
"""
from __future__ import annotations

import glob
import os
import shutil
import sys

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
                f"confirm_current_{owner}.json",
                f"exchange_journal_{owner}.json"):
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


def _program(owner: str):
    _cleanup(owner)
    from form.open import Program
    prog = Program(owner=owner)
    from form.mandell.core_ii_exec import attach
    attach(prog)
    return prog


def _run(prog, seed):
    from form.mandell.executor import execute_seed
    return execute_seed(prog, seed)


def _msgs(r):
    return [m for m in r.get("messages", [])
            if not m.startswith(("Mandell:", "English:",
                                 "Chain atoms=", "-- "))]


def main() -> bool:
    owner = "Step8Tx"
    p = _program(owner)
    st = p.core_ii

    # -- B15: spectrum failure fails the frame; no clean commit
    _run(p, "93[Try]")
    r = _run(p, "86[Delete] :: nosuchkey")
    _rec("B15 Delete failure marks frame failed with root cause",
         r.get("ok") is False
         and st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "delete_missing:nosuchkey",
         str(st.tx[-1]))
    r = _run(p, "95[Commit]")
    _rec("B15 failed frame cannot commit as clean; commit_illegal "
         "is extra evidence, root cause preserved",
         r.get("ok") is False and r.get("error") == "commit_illegal"
         and st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "delete_missing:nosuchkey"
         and "commit_illegal" in st.tx[-1].get("extra_errors", []),
         str(st.tx[-1]))
    # -- B16: Catch consumes the frame error; commit then legal
    r = _run(p, "94[Catch]")
    _rec("B16 Catch consumes frame error (caught_error recorded)",
         _msgs(r) == ["Catch delete_missing:nosuchkey"]
         and st.tx[-1].get("status") == "caught"
         and st.tx[-1].get("caught_error") == "delete_missing:nosuchkey",
         str(_msgs(r)))
    r = _run(p, "95[Commit]")
    _rec("B16 caught frame may commit (mark/accept)",
         r.get("ok") is True
         and st.tx[-1].get("status") == "committed",
         str(_msgs(r)))

    # -- B16: first root cause wins across two failures
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: firstmiss")
    _run(p, "88[Patch] :: secondmiss=v")
    _rec("B16 first root cause preserved; second failure is "
         "extra evidence only",
         st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "delete_missing:firstmiss"
         and st.tx[-1].get("extra_errors") == ["patch_miss:secondmiss"],
         str(st.tx[-1]))
    _run(p, "96[Revert]")

    # -- B16: failure after Catch is a NEW root cause
    _run(p, "93[Try]")
    _run(p, "86[Delete] :: oldmiss")
    _run(p, "94[Catch]")
    _run(p, "88[Patch] :: newmiss=v")
    _rec("B16 failure after Catch re-fails frame with the new "
         "root cause; caught_error keeps the consumed one",
         st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "patch_miss:newmiss"
         and st.tx[-1].get("caught_error") == "delete_missing:oldmiss",
         str(st.tx[-1]))
    _run(p, "96[Revert]")

    # -- B15: non-spectrum Core II failure (Scope) fails frame
    _run(p, "93[Try]")
    r = _run(p, "53[Scope] :: Nowhere")
    _rec("B15 Scope refusal (non-spectrum Core II) fails frame",
         r.get("ok") is False
         and st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "scope_unknown:Nowhere",
         str(st.tx[-1]))
    _run(p, "96[Revert]")

    # -- B16: Catch with no error reports explicitly, consumes nothing
    _run(p, "93[Try]")
    r = _run(p, "94[Catch]")
    _rec("B16 Catch with no frame error: 'Catch (no error)', "
         "frame stays open, nothing consumed",
         _msgs(r) == ["Catch (no error)"]
         and st.tx[-1].get("status") == "open"
         and st.tx[-1].get("error") == ""
         and "caught_error" not in st.tx[-1],
         str(_msgs(r)))
    r = _run(p, "95[Commit]")
    _rec("B16 no-error frame still commits from open",
         r.get("ok") is True
         and st.tx[-1].get("status") == "committed",
         str(_msgs(r)))

    # -- B16: stale pre-Try error is never captured
    _run(p, "86[Delete] :: ghost")
    _run(p, "93[Try]")
    r = _run(p, "94[Catch]")
    _rec("B16 pre-Try sticky error not captured by Catch in a "
         "fresh frame (clean error state)",
         _msgs(r) == ["Catch (no error)"]
         and st.tx[-1].get("error") == ""
         and st.last_error == "delete_missing:ghost",
         str(_msgs(r)))
    _run(p, "96[Revert]")

    # -- B15 chain path: one seed, Delete fails, Commit refused
    r = _run(p, "93[Try] > 86[Delete] :: chainmiss > 95[Commit]")
    commit_receipts = [a for a in r.get("atom_results", [])
                       if a.get("dell") == 95]
    _rec("B15 chain path: Delete failure in one seed fails the "
         "frame and the in-chain Commit is commit_illegal, "
         "frame NOT committed",
         commit_receipts and commit_receipts[0].get("ok") is False
         and commit_receipts[0].get("error") == "commit_illegal"
         and st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "delete_missing:chainmiss",
         str(st.tx[-1]))
    _run(p, "96[Revert]")

    # -- B15 leaf path: Create TOAM failure inside a chain Try
    r = _run(p, '93[Try] > 08[Create](skin="SPHERE") > 95[Commit]')
    _rec("B15 leaf failure (Create TOAM MISSING_REQUIRED) in a "
         "chain fails the frame; in-chain Commit refused",
         st.tx[-1].get("status") == "failed"
         and "MISSING_REQUIRED" in str(st.tx[-1].get("error")),
         str(st.tx[-1]))
    _run(p, "96[Revert]")

    # -- B15 non-failures: data predicate + lawful skip
    _run(p, "93[Try]")
    r = _run(p, "51[Select] :: zzz_no_such_thing")
    _rec("B15 Select no-match is data (ok=True), frame stays open",
         r.get("ok") is True
         and st.tx[-1].get("status") == "open",
         str(st.tx[-1]))
    r = _run(p, "93[Try] > 51[Select] :: plane >>> 86[Delete] :: neverran > 61[Join] > 95[Commit]")
    _rec("B15 FlowOver-skipped atom never ran and does NOT fail "
         "the frame; Commit accepted",
         st.tx[-1].get("status") == "committed",
         str(st.tx[-1]))

    # -- Nested isolation
    _run(p, "93[Try]")
    _run(p, "55[Set] :: outerkey=outer")
    _run(p, "93[Try]")
    _run(p, "88[Patch] :: inner_miss=v")
    _rec("B15 nested: inner failure fails ONLY the inner frame",
         st.tx[-1].get("status") == "failed"
         and st.tx[-1].get("error") == "patch_miss:inner_miss"
         and st.tx[-2].get("status") == "open"
         and st.tx[-2].get("error") == "",
         str(st.tx))
    _run(p, "94[Catch]")
    r = _run(p, "95[Commit]")
    inner_ok = r.get("ok") is True and st.tx[-1].get("status") == "committed"
    r = _run(p, "95[Commit]")
    _rec("B16 nested: inner Catch+Commit succeed; outer still "
         "open and commits clean with its own write intact",
         inner_ok and r.get("ok") is True
         and st.tx[-1].get("status") == "committed"
         and st.store.get("outerkey") == "outer",
         str(st.tx[-1]))

    # -- B17: live mutations, Revert scope = checkpoint fields
    _run(p, "55[Set] :: keepme=1")
    traces_before = len(st.traces)
    _run(p, "93[Try]")
    _run(p, "84[Copy] :: keepme")
    live = st.store.get("copy_keepme") == "1"
    _run(p, "55[Set] :: keepme=2")
    _run(p, "82[Group] :: txgroup")
    r = _run(p, "96[Revert]")
    _rec("B17 mutations are LIVE before Commit (no staged "
         "isolation); Revert restores checkpoint fields "
         "(store, groups) exactly",
         live and r.get("ok") is True
         and st.store.get("keepme") == "1"
         and "copy_keepme" not in st.store
         and "txgroup" not in st.groups,
         str(st.store))
    _rec("B17 fields outside the checkpoint set are NOT "
         "rolled back (traces keep growing)",
         len(st.traces) > traces_before,
         f"traces {traces_before} -> {len(st.traces)}")

    # -- B17 wording: cards state mark/accept + covered fields
    from form.mandell.dell_cards import DEEP_NOTES
    _rec("B17 Commit card: mark/accept, no atomic isolation, "
         "no ACID wording",
         "mark/accept" in DEEP_NOTES[95]
         and "NO atomic staged" in DEEP_NOTES[95]
         and "NO whole-program ACID" in DEEP_NOTES[95],
         DEEP_NOTES[95][:80])
    _rec("B17 Try card lists the checkpoint field set",
         all(f in DEEP_NOTES[93] for f in
             ("scope", "selected", "store", "groups", "defs",
              "aliases", "compositions", "weights", "context",
              "route", "refs", "causes", "deps", "last_assert",
              "last_guard")),
         DEEP_NOTES[93][:80])

    # -- AF5 bounds retained under the new frame fields
    base_ids = len(st.tx)
    for _ in range(20):
        _run(p, "93[Try]")
        _run(p, "95[Commit]")
    terminal = [f for f in st.tx if f.get("status") in
                ("committed", "reverted")]
    ids = [int(f["id"][2:]) for f in st.tx]
    _rec("AF5 terminal frames pruned to keep=16 and ids stay "
         "monotonic after step 8 fields",
         len(terminal) <= 16 and ids == sorted(ids)
         and len(st.tx) < base_ids + 40,
         f"terminal={len(terminal)} tx={len(st.tx)}")

    # -- B15 direct Core II path (no chain layer): execute_core_ii
    #    is a public entry other consumers call directly; its
    #    tail hook must fail the frame on its own.
    owner2 = "Step8TxDirect"
    p2 = _program(owner2)
    st2 = p2.core_ii
    from form.mandell.core_ii_exec import execute_core_ii
    execute_core_ii(p2, 93, "Try", "op", [])
    out = execute_core_ii(p2, 86, "Delete", "directmiss", [])
    direct_failed = (out.get("ok") is False
                     and st2.tx[-1].get("status") == "failed"
                     and st2.tx[-1].get("error")
                     == "delete_missing:directmiss")
    out = execute_core_ii(p2, 95, "Commit", "", [])
    _rec("B15 direct execute_core_ii path: Delete failure fails "
         "the frame and Commit is refused without the chain layer",
         direct_failed and out.get("ok") is False
         and out.get("error") == "commit_illegal"
         and st2.tx[-1].get("status") == "failed",
         str(st2.tx[-1] if st2.tx else None))
    _cleanup(owner2)

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"STEP8_TRANSACTIONS: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
