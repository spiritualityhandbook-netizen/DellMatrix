# WORKFLOW ROLE SEEDS — EVIDENCE ADDENDUM (2026-11-10)

Answers the Director's three missing-evidence items on PR #367
(12:40 CST mail 1a1c6c2b3e28e0d4: SCOPED_PASS on accounting only;
INSUFFICIENT_EVIDENCE for runtime certification and authority
isolation). All tests run at PR head dc01e4f (branch worktree;
product code = main's code at that head) in the WFROLES1 field
unless a controlled owner is named. Raw results retained in the
goal workspace (evidence_roles_result.json, diff_probes_result.json,
catch_probes_result.json).

## 1. Controlled precondition tests — 94[Catch] and 89[Diff]

**94[Catch] — precondition PROVEN: an open Try room in the session.**
- A: Catch as first atom, cold field → REFUSED `catch_illegal`.
- B: Catch after a failing atom in the same chain (no Try) → REFUSED.
- C: Catch in a new chain after a prior chain failed (same session)
  → REFUSED. (A live failure alone is NOT the precondition; this
  falsifies Uni's earlier DERIVED guess, which is withdrawn.)
- D: Catch inside a Try room after a failing atom → EXECUTED_OK.
- P1: UNI_FAILURE_PATH alone → its Catch REFUSED (`catch_illegal`).
- P2: UNI master first (it opens Try rooms), then UNI_FAILURE_PATH
  in the same process → Catch EXECUTED_OK.
- P3: a bare `93[Try]` in one chain makes Catch legal in a separate
  later chain → rooms persist across chains until closed.
This fully explains the run-1/run-2 classification flip: run 2's
process executed the masters first, leaving Try rooms open; run 1's
classification process ran the failure-path seeds cold.

**89[Diff] — precondition NOT established; negative results complete.**
Standalone Diff refused `baseline_missing` under every controlled
condition tried: brand-new field; after an in-process Checkpoint;
after save + reload of a checkpointed field; on the mature WFROLES1
field; with the Keeper master's exact label text; as a later chain
atom after Compare. The single EXECUTED_OK observation (inside the
full Keeper master during verification run 2) did NOT reproduce when
the same master was re-run on the same field under a different
process history. Diff is therefore recorded RUN_CONDITIONAL,
PRECONDITION UNKNOWN — no mechanism is claimed.

## 2. Relabeling (done in this PR)

REAL → **EXECUTED_OK** throughout the classification JSON and
legend; the three state-dependent atoms (89[Diff] in
KEEPER_FASTLANE_FULL; 94[Catch] in both failure-path seeds) carry
`run_conditional: true`.

## 3. Authority-isolation snapshots (before/after, all 31 seeds run)

- Files changed by a full 31-seed execution: ONLY WFROLES1 state
  files. **Non-WFROLES1 files changed: none ([])** — every other
  owner's state is byte-identical before/after (SHA-256 compared).
- Compositions: [] before → [] after. Aliases: [] before → [] after.
  No composition or alias was created by any seed, including the
  seeds containing Compose/Alias/Commit/Merge atoms.
- Nursery: pending proposals 55 → 92 across the run (the seeds' own
  proposal-generating atoms add PENDING proposals inside their own
  field; the landing count was 31, grown by each re-execution).
  **Confirmed proposals: 0 before → 0 after.** Nothing was promoted,
  confirmed, or merged by any run; Ace's sovereign confirm was never
  exercised or bypassed.

## What this does and does not establish

Established: Catch's exact precondition (controlled, falsified
alternatives published); Diff's honest unknown; cross-owner
isolation and the zero-confirmation invariant across full runs.
Not established: Diff's precondition; any claim that the 31 seeds
form an accepted catalog (they remain PENDING proposals under
Ace's confirm); runtime certification, which remains the
Director's act on this evidence.
