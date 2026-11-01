"""Director order step 9 — Diff circuit (B13/B14).

Contracts proven here, through the public seed path
(form.mandell.executor.execute_seed) on a real Program,
plus the direct execute_core_ii entry and save/load:

- B13: with no baseline captured in this session, Diff
  REFUSES baseline_missing (ok=False) and claims NO
  change-set: last_diff baseline="missing",
  available=False, changed=None (never []), before=None.
  Reading Diff never captures a baseline — a fresh
  program Diffed twice is refused twice, identically.
- B14: ONE baseline lifecycle for every store writer.
  Set (55) captures the shared baseline through
  spectrum_ops._note_mutation (pre=_ckpt(st) after
  refusal checks, immediately before the mutation) —
  legacy and typed-roles paths alike — so a Set write
  is visible to Diff with no other writer involved.
  Spectrum writers (84-88) keep the same rule:
  "immediate" = the pre-state of the most recent
  mutation, whoever wrote it. A REFUSED Set captures
  nothing and mutates nothing.
- Reading Diff is read-only and never resets the
  baseline: repeated reads return the identical result,
  and a later mutation — not a read — is what moves the
  baseline. An empty change-set (changed=[]) is only
  ever reported against a real captured baseline.
- Transactions: while a frame is active Diff reads the
  frame checkpoint (baseline=transaction) and a Set
  inside the frame is staged like every other writer;
  after Revert the standalone baseline captured before
  the in-transaction Set governs again; after Commit
  the pre-mutation capture of the last in-transaction
  writer governs.
- Persistence: the baseline is session-only (never in
  CORE_II_DURABLE). A save/load-restored state keeps
  its store but reports baseline_missing until its
  next mutation captures a fresh baseline.

Labels: INTEGRATION / PUBLIC_ENTRY (real Program via
form.open.Program, public executor; one direct
execute_core_ii leg; one save/load leg).
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
    owner = "Step9Diff"
    p = _program(owner)
    st = p.core_ii

    # -- B13: fresh Diff refuses, claims no change-set
    r = _run(p, "89[Diff]")
    _rec("B13 fresh Diff refuses baseline_missing with no "
         "empty-change-set claim",
         r.get("ok") is False
         and r.get("error") == "baseline_missing"
         and _msgs(r) == ["Diff baseline_missing "
                          "(no baseline captured)"]
         and st.last_diff.get("baseline") == "missing"
         and st.last_diff.get("available") is False
         and st.last_diff.get("changed") is None
         and st.last_diff.get("before") is None
         and st.last_diff.get("after") == {},
         str(st.last_diff))
    # -- B13: the read itself captures nothing; a second
    #    read is refused identically
    r = _run(p, "89[Diff]")
    _rec("B13 reading Diff creates no baseline: second "
         "fresh Diff refuses identically",
         r.get("ok") is False
         and r.get("error") == "baseline_missing"
         and getattr(st, "diff_baseline", None) is None,
         str(st.last_diff))

    # -- B14: Set as the ONLY writer is visible
    _run(p, "55[Set] :: a=1")
    r = _run(p, "89[Diff]")
    _rec("B14 Set-only write is visible to Diff "
         "(baseline=immediate, before/after exact)",
         r.get("ok") is True
         and _msgs(r) == ["Diff changed=['a'] "
                          "baseline=immediate"]
         and st.last_diff.get("before") == {}
         and st.last_diff.get("after") == {"a": "1"},
         str(st.last_diff))
    # -- No reset from reading: repeated read identical,
    #    baseline and store untouched by the read
    baseline_before = st.diff_baseline
    store_before = dict(st.store)
    snaps_before = len(st.snapshots)
    r = _run(p, "89[Diff]")
    _rec("B14 repeated Diff reads are identical and "
         "read-only (no baseline reset, no store or "
         "snapshot mutation)",
         r.get("ok") is True
         and _msgs(r) == ["Diff changed=['a'] "
                          "baseline=immediate"]
         and st.diff_baseline == baseline_before
         and st.store == store_before
         and len(st.snapshots) == snaps_before,
         str(st.last_diff))

    # -- Multiple mutations: immediate = most recent
    #    mutation's pre-state, across writer kinds
    _run(p, "55[Set] :: b=2")
    r = _run(p, "89[Diff]")
    _rec("B14 second Set moves the baseline: Diff "
         "reports only the most recent mutation",
         _msgs(r) == ["Diff changed=['b'] "
                      "baseline=immediate"]
         and st.last_diff.get("before") == {"a": "1"}
         and st.last_diff.get("after") == {"a": "1", "b": "2"},
         str(st.last_diff))
    _run(p, "88[Patch] :: a=9")
    r = _run(p, "89[Diff]")
    _rec("B14 spectrum writer after Set shares the same "
         "baseline: Patch is the reported change",
         _msgs(r) == ["Diff changed=['a'] "
                      "baseline=immediate"]
         and st.last_diff.get("before", {}).get("a") == "1"
         and st.last_diff.get("after", {}).get("a") == "9",
         str(st.last_diff))
    _run(p, "85[Move] :: b>c")
    r = _run(p, "89[Diff]")
    _rec("B14 Move after Patch: both sides of the move "
         "are the change-set against the shared baseline",
         r.get("ok") is True
         and sorted(st.last_diff.get("changed") or []) == ["b", "c"]
         and st.last_diff.get("baseline") == "immediate",
         str(st.last_diff))

    # -- A TRUE empty change-set requires a real baseline:
    #    re-Set the same value, Diff honestly reports []
    _run(p, "55[Set] :: a=9")
    r = _run(p, "89[Diff]")
    _rec("B13 changed=[] is reported only against a real "
         "captured baseline (same-value Set)",
         r.get("ok") is True
         and st.last_diff.get("changed") == []
         and st.last_diff.get("baseline") == "immediate",
         str(st.last_diff))

    # -- B14 typed-roles Set path
    owner2 = "Step9DiffTyped"
    p2 = _program(owner2)
    st2 = p2.core_ii
    _run(p2, '55[Set](key="tk", value="tv")')
    r = _run(p2, "89[Diff]")
    _rec("B14 typed-roles Set captures the baseline too",
         r.get("ok") is True
         and st2.last_diff.get("changed") == ["tk"]
         and st2.last_diff.get("baseline") == "immediate"
         and st2.store.get("tk") == "tv",
         str(st2.last_diff))
    _cleanup(owner2)

    # -- Sentinel: a REFUSED Set captures no baseline
    owner3 = "Step9DiffRefused"
    p3 = _program(owner3)
    st3 = p3.core_ii
    st3.store["a"] = "1"
    st3.store["a=b"] = "NB"
    r = _run(p3, "55[Set] :: a=b=NEW")
    refused = (r.get("ok") is False
               and r.get("error") == "ambiguous_set"
               and st3.store == {"a": "1", "a=b": "NB"}
               and getattr(st3, "diff_baseline", None) is None)
    r = _run(p3, "89[Diff]")
    _rec("B14 refused (ambiguous) Set mutates nothing and "
         "captures no baseline; Diff still missing after it",
         refused and r.get("ok") is False
         and r.get("error") == "baseline_missing",
         str(st3.store))
    _cleanup(owner3)

    # -- Transactions: frame checkpoint governs; Set is
    #    staged; Revert restores the standalone baseline
    owner4 = "Step9DiffTx"
    p4 = _program(owner4)
    st4 = p4.core_ii
    _run(p4, "55[Set] :: base=1")
    _run(p4, "93[Try]")
    _run(p4, "55[Set] :: txk=tv")
    staged = list(st4.tx[-1].get("staged_changes") or [])
    r = _run(p4, "89[Diff]")
    _rec("B14 Set inside a transaction is staged through "
         "the shared authority and Diff reads the frame "
         "checkpoint (baseline=transaction)",
         staged == [{"op": "set", "lab": "txk=tv"}]
         and _msgs(r) == ["Diff changed=['txk'] "
                          "baseline=transaction"],
         str((staged, _msgs(r))))
    _run(p4, "96[Revert]")
    r = _run(p4, "89[Diff]")
    _rec("B14 after Revert the store is restored and the "
         "standalone baseline captured before the "
         "in-transaction Set governs (true empty diff)",
         st4.store == {"base": "1"}
         and r.get("ok") is True
         and st4.last_diff.get("baseline") == "immediate"
         and st4.last_diff.get("changed") == [],
         str(st4.last_diff))
    # -- Commit: the last in-transaction writer's capture
    _run(p4, "93[Try]")
    _run(p4, "88[Patch] :: base=2")
    _run(p4, "95[Commit]")
    r = _run(p4, "89[Diff]")
    _rec("B14 after Commit, Diff reads the pre-mutation "
         "capture of the last in-transaction writer",
         r.get("ok") is True
         and st4.last_diff.get("baseline") == "immediate"
         and st4.last_diff.get("changed") == ["base"]
         and st4.last_diff.get("before", {}).get("base") == "1"
         and st4.last_diff.get("after", {}).get("base") == "2",
         str(st4.last_diff))
    _cleanup(owner4)

    # -- Save/load: store survives, baseline does not
    owner5 = "Step9DiffPersist"
    p5 = _program(owner5)
    _run(p5, "55[Set] :: s=1")
    from form.persist import load, save
    path = save(p5)
    q = load(owner5, path)
    r = _run(q, "89[Diff]")
    missing_after_load = (r.get("ok") is False
                          and r.get("error") == "baseline_missing"
                          and q.core_ii.store.get("s") == "1")
    _run(q, "55[Set] :: s=2")
    r = _run(q, "89[Diff]")
    _rec("B13/B14 save/load: restored store intact but "
         "baseline is session-only (baseline_missing), "
         "and the first post-load Set captures a fresh "
         "baseline",
         missing_after_load
         and r.get("ok") is True
         and q.core_ii.last_diff.get("changed") == ["s"]
         and q.core_ii.last_diff.get("before", {}).get("s") == "1"
         and q.core_ii.last_diff.get("after", {}).get("s") == "2",
         str(q.core_ii.last_diff))
    _cleanup(owner5)

    # -- Direct execute_core_ii path (no chain layer)
    owner6 = "Step9DiffDirect"
    p6 = _program(owner6)
    st6 = p6.core_ii
    from form.mandell.core_ii_exec import execute_core_ii
    out = execute_core_ii(p6, 89, "Diff", "", [])
    direct_missing = (out.get("ok") is False
                      and out.get("error") == "baseline_missing")
    execute_core_ii(p6, 55, "Set", "dk=dv", [])
    out = execute_core_ii(p6, 89, "Diff", "", [])
    _rec("B13/B14 direct execute_core_ii path agrees: "
         "missing first, Set visible after",
         direct_missing and out.get("ok") is True
         and st6.last_diff.get("changed") == ["dk"],
         str(st6.last_diff))
    _cleanup(owner6)

    # -- Chain path: Set then Diff in ONE seed; and a
    #    missing-baseline Diff atom receipt in a chain
    owner7 = "Step9DiffChain"
    p7 = _program(owner7)
    st7 = p7.core_ii
    r = _run(p7, "55[Set] :: c=1 > 89[Diff]")
    chain_ok = (r.get("ok") is True
                and st7.last_diff.get("changed") == ["c"])
    r = _run(_program(owner7), "89[Diff] > 90[Trace]")
    receipts = [a for a in r.get("atom_results", [])
                if a.get("dell") == 89]
    _rec("B13/B14 chain path: in-chain Set feeds in-chain "
         "Diff; a missing-baseline Diff atom reports "
         "baseline_missing as its receipt",
         chain_ok and receipts
         and receipts[0].get("ok") is False
         and receipts[0].get("error") == "baseline_missing",
         str(receipts))
    _cleanup(owner7)

    # -- Wording: the cards carry the new contract
    from form.mandell.dell_cards import DEEP_NOTES
    _rec("B13/B14 card wording: Diff card states the "
         "shared lifecycle and the baseline_missing "
         "refusal; Set card states baseline capture",
         "baseline_missing" in DEEP_NOTES[89]
         and "_note_mutation" in DEEP_NOTES[89]
         and "session-only" in DEEP_NOTES[89]
         and "_note_mutation" in DEEP_NOTES[55],
         DEEP_NOTES[89][:80])

    _cleanup(owner)
    total = len(RESULTS)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"FAIL {name} :: {detail}")
    print(f"STEP9_DIFF: {passed}/{total}")
    return passed == total


def smoke() -> bool:
    return main()


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
