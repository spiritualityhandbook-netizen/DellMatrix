# DIRECTOR REPORT — STEP 8: TRANSACTIONS (B15/B16/B17)

Status: SUBMITTED 2026-11-01 — circuit closed (frozen
candidate, CI, merge and fresh-clone recorded in Evidence).
This report is evidence submitted, never a certificate.

## Findings addressed
- B15 failed-frame: an atom failure inside a Try frame must
  mark that frame failed; a clean Commit after a failed
  atom must not be accepted as if nothing failed.
- B16 Catch: Catch must capture the frame's own error (the
  first root cause), never a stale pre-Try/global error or
  a later commit_illegal; a Catch with no frame error must
  say so explicitly and consume nothing.
- B17 Commit: ACCEPT with wording — Commit is mark/accept
  over a checkpoint field set, with no atomic staged-
  isolation, ACID, or external-effect rollback claims.

## Before (failing-first probe, reproduced 2026-11-01 on
## unmodified ecca0b9 by hidden_files/step8_probe.py,
## public seed path, synthetic owner)
- P1 Delete-in-Tx: frame stays "open", error ""; Commit
  then ACCEPTED clean (ok=True, "Commit tx0 accepted").
- P2 Assert-in-Tx: frame failed assert_fail; Commit
  refused; Catch captures "commit_illegal" — root cause
  overwritten.
- P3 pre-Try Delete ghost, then Try+Catch: captures the
  stale pre-Try "delete_missing:ghost".
- P4 Catch with no frame error: captures the same stale
  ghost and marks the frame "caught".
- P5 chain seed Try > Delete-miss > Commit in ONE seed:
  Commit "accepted" inside the chain despite the Delete
  failure.
- P6 nested Try>Try>Patch-miss: NEITHER inner nor outer
  frame marked failed.

## After (candidate e78ada4)
All six probe lines flip: failed atoms mark the innermost
active frame; Commit on a failed frame is refused with
the root cause preserved (the refusal lands in
extra_errors, not over the root cause); Catch captures
the frame's own first error; a no-error Catch reports
"Catch (no error)", status and error unchanged; nested
frames mark the innermost frame only.

## Mechanism (one canonical hook)
- spectrum_ops.note_atom_failure(st, err): innermost
  ACTIVE frame only. First failure sets status="failed"
  and error=err; later failures on an already-failed
  frame append to extra_errors only (idempotent re-notes
  deduped). A failure after a Catch is a new root cause
  for the reopened frame; the caught error stays in
  caught_error. _fail_open_tx delegates to this hook —
  one authority, no second marker.
- Call sites: core_ii_exec tail (every Core II outcome,
  incl. commit_illegal and query/scope/Join/spectrum
  failures; skipped receipts and ok=True predicates never
  reach the hook) and chain_exec execute_range +
  _run_control head (leaf atoms and pre-execution
  TOAM/reference/conflict failures in-chain).
- Catch (Dell 94) reads frame state only; st.last_error
  remains a global diagnostic with no authority over
  Catch. Catch records caught_error.
- Commit (Dell 95): acceptance set unchanged
  (open/caught); failed -> commit_illegal. Dell cards
  93/94/95 rewritten to the B17 wording: checkpoint field
  set stated, live mutations stated, no atomic isolation
  / ACID / external-effect rollback claimed.

## Evidence
- Suite STEP8_TRANSACTIONS 22/22 (regress entry 214).
- Mutants (defect-restoring, all killed): M1 core-tail
  hook removed 21/22; M1b chain call sites removed
  21/22; M2 sticky Catch 18/21; M3 root-cause overwrite
  16/21; M4 no-error Catch marks caught 20/21; M5 Commit
  accepts failed 16/21. (M2–M5 measured on the 21-check
  suite before the direct-path check was added.)
- Neighborhoods: spectrum 48/48 (exhibits amended to the
  step-8 contracts), core_ii_smoke 36/36, control 38/38,
  step7 28/28, step6 34/34, AF5 21/21, coreii a/b green;
  proof cards regenerated (d1_proof_cards 6/6).
- Regress x3 on candidate e78ada4 (tree b1692ad): fwd
  214/214, --twice 214/214 both passes, --order rev
  214/214 — all GREEN (logs hidden_files/step8_logs/
  reg1_fwd.log, reg2_twice.log, reg3_rev.log).
- Exact-head CI on e78ada4 verified COMPLETE SUCCESS in
  a separate step before merge: package run 41295294688
  SUCCESS completed 09:57:35Z; smoke run 41295294699
  SUCCESS completed 10:14:20Z. (This verification run
  waited on smoke IN_PROGRESS from 09:57Z to completion;
  the merge waited for it.)
- PR #188 merged as 1607f33 (2026-11-01T10:14:32Z);
  merge tree b1692ad == candidate tree; parents ecca0b9
  + e78ada4.
- Fresh-clone regress at merge 1607f33: 214/214 GREEN
  (log hidden_files/step8_logs/freshclone_regress.log).

## Limitations
- The hook marks the innermost ACTIVE frame only; a
  failure with no active frame changes no frame state
  (st.last_error remains the diagnostic record).
- extra_errors is per-frame evidence, bounded by the
  frame's lifetime and AF5 terminal-frame pruning; it is
  not a durable log.
- B17 is wording + honesty only: no snapshot, isolation,
  or rollback semantics were added or claimed. Step 11
  still carries the remaining public-contract wording.

## Anticipated probes
- Try > failing atom > Catch > failing atom > Commit:
  expected — second failure is the new root cause of the
  reopened frame, caught_error retains the first, Commit
  refused.
- The same failing Core II atom executed directly and
  in-chain: expected — identical frame marking (hook is
  shared; chain re-notes are idempotent, no duplicate
  extra_errors).
- Catch as the first atom inside Try with no prior
  failure: expected — "Catch (no error)", frame stays
  open, nothing consumed, a following Commit accepts.
- A skipped (skipped=True) atom inside Try: expected —
  no frame failure (lawful skip is not a failure, per
  step 7's receipt law).
- Commit_illegal raised inside a nested frame: expected
  — lands in extra_errors of the innermost frame, root
  cause unchanged.

## Questions for the Director
Q1. After a Catch, this implementation treats a NEW
failure as a new root cause for the reopened frame
(caught_error preserves the first). The alternative —
keeping the first error as root cause forever — would
misreport post-Catch failures. Uni recommends certifying
the reopened-frame reading; it unblocks no other step,
but a contrary ruling would change one hook branch.
Q2. B17's remaining wording lives in step 11. Uni
recommends step 8's ruling be bounded to the frame/Catch/
Commit mechanism + the 93/94/95 card wording as
submitted, leaving cross-surface wording consistency to
step 11 as ordered.

## Requested ruling
Bounded re-ruling on B15, B16 and B17 within the scope
above: canonical failed-frame marking, frame-owned Catch
with root-cause preservation and explicit no-error
reporting, and Commit mark/accept wording with the
checkpoint scope stated.
