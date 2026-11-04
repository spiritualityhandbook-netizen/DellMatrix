# DIRECTOR REPORT — TD-1-R1: Conflict and Corruption Guard

Circuit: TD-1-R1 (Mode C, Director directive 2026-11-04, Mode D
review of TD-1). Scope: close the two source-review findings that
deferred TD-1 certification — F1 corrupt-state overwrite path,
F2 concurrent-binding race. No containment, no TD-2.
Base: main 0bbefec (PR #281). Candidate branch:
uni/td1-r1-conflict-corruption-guard.

## What changed

`form/mandell/unit_binding.py`, `form/persist_rest.py`, one new
suite, one registration line. Nothing else.

F1 — refuse unreadable state before minting. Bind now reads the
canonical state file exactly once at entry
(`_read_persisted_state`): absent / ok / unreadable. An
existing-but-unreadable file raises
`BindingRefused(state_unreadable)` before any mint; the bind
never proceeds toward a save over it, and the corrupt bytes are
left exactly as found (suite-verified by hash).

F2 — fingerprint compare-and-swap, two layers:

1. Baseline: `persist_rest.load` (live path only) and
   `persist_rest.save` stamp the instance with the SHA-256 of
   the state version it derives from / just wrote
   (`_td_state_fingerprint`). Bind refuses a stamped instance
   whose canonical file has since moved or vanished:
   `BindingRefused(conflict)`, detail naming the persisted
   pointer (when readable) and the in-memory pointer.
2. Commit gate: immediately before the pointer is committed,
   bind re-reads the state file and compares fingerprints with
   the entry read. Any change — including absent->present and
   present->absent transitions — raises
   `BindingFailed(reason="concurrent_save")` with the minted
   shell reported as a census-visible orphan; the pointer is
   never set on the losing instance and the winning writer's
   persisted state is untouched. Whole-file granularity is
   deliberate: a bind's save rewrites the entire program state,
   so any intervening save invalidates the binder.

Reconciliation: where the in-memory pointer and the canonical
persisted pointer disagree, the persisted record is canonical —
bind refuses with a conflict naming both, rather than trusting
memory into an `already_bound` answer.

Disclosed residual (no overclaim): between the commit-gate
re-read and the atomic rename inside `persist_rest.save` itself,
a racing save can still land undetected; the guard detects every
interleaving that completes before the gate and narrows the
undetectable window to that rename. An OS-level lock file would
close it fully; it was not added — the directive authorizes "a
concurrency guard OR an atomic version check", and this is the
version check, with its window stated. If the Director prefers
the lock as well, that is a small R2.

## Evidence

- Failing-first: on pristine code the new suite aborts at
  "F1 corrupt state refuses the bind" — the bind proceeded (and
  its save would have overwritten the corrupt file). F2's race
  was reproduced deterministically by injecting writer A's
  complete bind inside writer B's mint (the idea-persist seam).
- Suite `form/track_d_td1_r1_test.py`: **10/10 GREEN** (registered;
  canonical count 233). Covers corrupt refusal + byte
  preservation + no mint; overlapping-writer gate failure;
  winner survival; loser shell census-visible as an orphan;
  memory/persisted split refusal naming both ids; vanished-file
  fail-closed with no silent resurrection; honest sequential
  binds unbroken; zero SemanticGraph writes (file hashes).
- TD-1 suite: **24/24 GREEN** unchanged.
- Mutants (defect-restoring, each killed by exactly its target
  check): unreadable-guard removed → F1 fails; commit-gate CAS
  removed → F2 fails; baseline check removed → vanished-file
  check fails. All reverted by inverse edit; tree clean.
- Full regression x3 sequential: **233/233 GREEN in all legs**
  (fwd, twice pass1+pass2, rev). Process note: the first chain's
  rev leg was killed by a VM replacement; per standing law the
  partial leg counted as NO RESULT and was re-run in full —
  terminal GREEN. Logs preserved.
- Exact-head CI and fresh-clone verification: reported in the
  closure addendum on this PR (identifiers from terminal output).

Test realism: INTEGRATION (real Program/persist paths on a
throwaway owner through the public Program wrapper; the writer
interleave is injected at the mint seam — a deterministic
reproduction of the overlapping-writer window, not two racing OS
processes; labeled as such).

## Anticipated probes

1. Two OS processes binding simultaneously — not tested; the
   claim is the CAS contract above with its disclosed rename
   window, not process-level mutual exclusion.
2. The stamp lives on the Program object (`_td_state_fingerprint`)
   and is refreshed by the canonical load/save only; a program
   restored through checkpoint/generation paths carries no stamp
   and is guarded by the commit-gate CAS alone (baseline-less).
   Stated, not hidden.
3. `persist_rest.save`'s stamp write is best-effort: a stamp
   read failure sets the stamp to None (baseline-less), never
   fails the save; the gate CAS still applies.
4. Census/H1/rollback semantics from TD-1 are unchanged; TD-1's
   Q1 (the `_on_information_change` boundary) remains as
   submitted there.

## Questions for the Director

1. Does the fingerprint CAS (with the disclosed rename window)
   satisfy the F2 guarantee for TD-1 certification, or is an
   OS-level lock required?
2. TD-1 certification: with F1/F2 closed as above, will the
   Director certify TD-1, and does TD-2 authorization follow or
   remain separately gated?
