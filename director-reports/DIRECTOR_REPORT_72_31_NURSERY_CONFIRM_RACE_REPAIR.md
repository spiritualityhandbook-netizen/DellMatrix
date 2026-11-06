# DIRECTOR REPORT — 72-31 REPAIR (corrected candidate): Nursery confirmation race + compensation pointer-identity

Circuit: 72-31 (SM-31) — §6.6 persistence batch, Sleep Protocol v2.
Authorization: Director Mode A directive of 2026-11-06 (Ace relay;
archived responses/DIRECTOR_MODE_A_DIRECTIVE_2026-11-06_72_31_GO.md),
as corrected by the Director's CORRECTION_REQUIRED rulings of
2026-11-06 — round 1 (archived
responses/DIRECTOR_MODE_A_RULING_2026-11-06_72_31_CORRECTION_REQUIRED.md),
round 2 (archived
responses/DIRECTOR_MODE_A_RULING_2026-11-06_72_31_CORRECTION2.md;
Q-31R.2 answered there: FIX, bounded to 72-31), and round 3
(archived
responses/DIRECTOR_MODE_A_RULING_2026-11-06_72_31_CORRECTION3.md).
Work through a MERGE-READY PR; merge only on the Director's
exact-head ruling relayed through Ace. Assessment issues direction
and no merge authorization. Timers paused; email watermark frozen
at 2026-11-06 06:26 CST throughout.
Base: main 77c1b0fc68b328a3ae770993837e68e3a6242e3e (PR #313 merge).
Branch: uni/72-31-nursery-confirm-race.
Candidate history: original repair head 3c905e3caaf1da855146ec940a93577df6a48011
(CORRECTION_REQUIRED round 1 — superseded); round-1 corrected code
SHA 756916ce6b5eed86de2f21ce5664847307eb4c04 (commits b1939e7
production, 756916c suite, on top of 3c905e3); records head 616449f
(CORRECTION_REQUIRED round 2 — superseded); round-2 code head
79c3c46de6780f0406830dda88bf07bad20f7c39 (commits f534a3f
production, 79c3c46 suite; Director-verified, then
CORRECTION_REQUIRED round 3, classification only — superseded);
round-3 FINAL code SHA 506823e26ad8b0a96cb34ed1b8a6f3388dbfd238
(commits b8f31c4 production, 506823e suite). The final PR head adds
records only — the product-code diff between the final code SHA
506823e and the PR head is empty.
CI execution identity: the PR workflows execute the pull-request
merge ref of the final PR head (the #306 lesson: that ref, not the
branch head, is what CI runs); the concrete run IDs at the final
head are listed in the delivery packet and on the PR's checks.

## Original defects (confirmed, failing-first, at 3c905e3's base)

Scoping first: the Nursery layer itself is NOT in the everyday-save/Q1
boundary — `Program.confirm_proposal` commits through the checkpoint
transaction. The Nursery-level probe was clean. Defects are at Program
level, in the interleaved/concurrent commit window only; every
sequential control held.

- **D-A DOUBLE-OK.** Barrier-synchronized cross-process workers both
  reported `ok=True` confirming the same proposal (probe: 4/5 runs;
  suite D2: both attempts).
- **D-B LOST WINNER.** One worker ok, the other refused — yet
  canonical reload showed the proposal still PENDING with no unit
  (probe2: 2/3; probe3: 1/5). Deterministic mechanism (suite D1): the
  refused loser's compensation restored baseline bytes captured
  BEFORE the winner committed.
- Repair at 3c905e3 (commit dbfe2c1, `form/dell_matrix/confirm_lineage.py`):
  the confirm commit section is serialized under the owner-state
  lock (D-A), and compensation re-validates the committed generation
  before restoring baseline bytes (D-B). Test-double repair (3c905e3):
  r3's two monkeypatched `commit_checkpoint` fakes updated to the real
  signature after the repair's generation-pinned commit call exposed
  them (clean-copy differential: main r3 19/19, branch 18/19).

## Director's correction — two further defects, both reproduced by Uni

1. **D1U — unreadable pointer at the compensation recheck loses the
   winner (production).** The Director injected OSError on the third
   `_read_pointer` call routed through `confirm_proposal ->
   current_generation_id` (the loser's recheck). Uni reproduced it
   exactly (probe hidden_files/72-31_d1u_probe.py): winner ok, loser
   nursery_conflict, reload pending / unit=False / label_count=0.
   Root cause: `current_generation_id` is a best-effort accessor that
   collapses EVERY failure to None; the recheck read None as
   "generation not advanced" and restored stale baseline bytes over
   the winner's committed generation.
2. **D2 vacuity (test).** The Director forced worker 2 to exit 17
   after the barrier, before confirming; both D2 checks passed with
   the missing worker parsed as `{"ok": None, "reason": "no-output"}`.
   Uni reproduced it exactly (probe hidden_files/72-31_d2_vacuity_probe.py):
   return codes [0, 17], both checks PASS. Exit codes were collected
   but never asserted; a missing receipt never disturbed the count.

## Correction (commits b1939e7 + 756916c)

Production (`form/mandell/checkpoint_generation.py`,
`form/dell_matrix/confirm_lineage.py`):

- New tri-state reader `committed_generation_state(owner)`:
  `("verified", generation_id)` when CURRENT reads cleanly;
  `("absent", None)` only when the pointer file does not exist
  (proven absence — `CheckpointNotEstablished`); `("unreadable",
  error)` for every other failure. `current_generation_id` is
  unchanged for its best-effort epoch-context consumers.
- Baseline capture uses the tri-state reader; an unreadable pointer
  at baseline FAILS the capture (compensation unverifiable; the
  existing fail-closed path leaves the intent journal for recovery)
  instead of recording an ambiguous None.
- The compensation recheck restores baseline bytes ONLY on verified
  identity (same generation as baseline) or proven absence on both
  sides. A different verified generation = advanced (skip restore,
  converged — the original D-B rule). Pointer vanished or unreadable
  = UNCERTAIN: no restore, the intent journal is NOT cleared, and
  the affected instance is marked recovery-required
  (`compensation_unverified_generation_unreadable`, fenced from
  saving) — recovery evidence preserved on uncertainty.

Suite (`form/nursery_confirm_race_test.py`, 21 -> 42 checks):

- **D1U** — the Director's injection, retargeted at the same semantic
  point through the corrected call path (identity-routed pointer
  reads made by confirm_proposal after the interleaved winner
  completes = exactly the loser's recheck): winner ok, loser
  nursery_conflict, winner survives per a FRESH-PROCESS reload, the
  loser instance carries the unreadable recovery mark, and the
  journal disposition is clean.
- **D1B** — baseline-read failure (first identity-routed read of the
  loser's attempt raises): loser refused, winner survives
  (fresh-process reload), the loser's intent journal is still on
  disk naming its proposal (fresh-process disposition read BEFORE
  any load can consume it), and the owner lock is released — a
  fresh instance confirms a new proposal immediately after.
- **L1** — legacy absence: an owner with no established checkpoint
  (proven absence asserted via `_read_pointer` raising
  `CheckpointNotEstablished`) confirms its first proposal cleanly.
- **D2 strengthened** to named predicates per attempt: both workers
  ready before release; both exit zero; both leave valid receipts;
  exactly one ok and the other the documented `nursery_conflict`
  refusal; winner preserved per fresh-process reload.
- **D2M** — sabotage rejection pinned: a worker exiting 17 after the
  barrier and a worker whose confirm raised must each make the
  predicate set reject the run.

## Evidence (corrected candidate, code SHA 756916c)

- Failing-first: the strengthened suite against the UNREPAIRED
  production code scores **39/42**, failing exactly
  `D1U.winner_survives_unreadable_recheck` (reload pending/False/0),
  `D1U.recovery_evidence_preserved` (no mark), and
  `D1B.journal_preserved_as_evidence` (journal cleared). All
  controls pass. (The suite is runnable at both heads; L1 asserts
  absence through the pre-existing `_read_pointer` contract.)
- After repair: **42/42 PASS**, standalone and through the harness
  `smoke()` door.
- Mutants: (a) conflation mutant — the recheck's uncertainty branch
  neutralized so an unreadable pointer falls through to the restore
  path: **40/42**, failing exactly the two D1U defect checks; killed,
  reverted by inverse edit, tree verified clean. (b) The original
  re-validation-off mutant receipt from the 06:21 CST step stands
  for the D-B profile at dbfe2c1 (code identity of that branch
  unchanged by the correction). (c) D2's missing-worker and
  raised-exception mutants are killed by construction: D2M asserts
  their rejection in-suite.
- Neighbours: dcc_xviii 89/89 · dcc_xvi_atomicity 101/101 ·
  checkpoint_generation_stress 15/15 · graph_journal_crash 12/12.
- Fresh clone (clean clone from GitHub, checkout at the corrected
  SHA 756916c, 2026-11-06): suite **42/42 PASS**.
- Full regression x3 (sequential, isolated owner state), SEPARATED
  BY CANDIDATE as ordered: at the ORIGINAL head 3c905e3, run3
  TERMINAL GREEN **244/244** on all three legs (fwd / fwd-twice /
  rev) — that SHA's own evidence; it does not cure the correction,
  whose fault paths the then-current 21-check suite and the
  standard regression do not exercise. At the CORRECTED code SHA
  756916c: run4 was killed mid-leg-2 by a runtime restart (leg 1
  GREEN 244/244; leg 2 partial = NO RESULT; disclosed, not
  counted); the deciding run5 is TERMINAL GREEN **244/244** on all
  three legs (fwd / fwd-twice / rev, LEG_RC=0 x3, CHAIN_DONE),
  with the strengthened suite showing 42/42 inside the regression.

## Correction round 2 — baseline refusal + pointer-shape classification

Ruling (Mode A, 2026-11-06 ~09:40 CST; archived
responses/DIRECTOR_MODE_A_RULING_2026-11-06_72_31_CORRECTION2.md):
Q-31R.1 CORRECTION_REQUIRED at records head 616449f, on two probes
the Director reran at the exact head. Q-31R.2 answered in the same
ruling: **FIX, bounded to 72-31**; broader save-path changes retain
their separate gate.

1. **Lone worker, unreadable baseline, healthy checkpoint: the
   confirm COMMITTED and succeeded.** `commit_checkpoint` ran once;
   reload showed the proposal confirmed with one unit. Required:
   explicit refusal with ZERO commit calls. Root cause: baseline
   capture failure only set `_baseline_ok=False`; the flow
   proceeded to commit anyway. Uni's D1B case had masked it — its
   stale loser was refused independently by the nursery guard, so
   the suite was green while the lone-worker path was broken (a
   test whose subject is refused for an independent reason proves
   nothing about the path under test).
2. **CURRENT as a directory or a dangling symlink classified
   `("absent", None)`.** Absence was inferred from `isfile`-style
   existence probing; a present-but-unreadable pointer shape must
   be `unreadable`, never absent.

Repair (commits f534a3f production + 79c3c46 suite; code head
79c3c46de6780f0406830dda88bf07bad20f7c39):

- New `BaselineUnverifiableError(RuntimeError)` in
  `form/dell_matrix/confirm_lineage.py`, raised as the first
  statement inside the commit try — before any `commit_checkpoint`
  call — when baseline capture failed. The existing handler reverts
  in-memory staging, preserves the intent journal, releases the
  lock, and returns `{ok: False, reason: "baseline_unverifiable"}`.
- `committed_generation_state` gates absence on `os.path.lexists`:
  a path that exists in any shape is never classified absent from
  an existence probe (superseded by round 3's error-preserving
  lookup; see below).
- New suite cases (42 -> 51 checks): **D1S** — the lone-worker
  refusal: exact refusal reason, zero commit calls (counting
  wrapper), fresh-process reload shows the proposal pending with
  no unit, the intent journal preserved naming the pid, the owner
  lock released (a fresh instance's retry of the SAME proposal
  succeeds). **D1P** — pointer-shape classification: missing ->
  absent (control), directory -> unreadable, dangling symlink ->
  unreadable.
- Failing-first at 616449f: **44/51**, failing exactly the five
  D1S outcome checks and the two D1P classification checks — the
  Director's probes verbatim.
- Mutants killed exactly: refusal removed -> 46/51 (D1S only);
  classification reverted -> 49/51 (D1P only). Both reverted by
  inverse edit, tree verified clean.
- Neighbours: confirm_crash_matrix 21/21.
- The Director verified the round-2 head himself (2026-11-06
  ~09:58 CST): reproduced 51/51; refusal, journal, retry,
  directory and dangling-symlink cases all confirmed.
- T3 at 79c3c46 (run6, sequential, isolated state): TERMINAL GREEN
  **244/244** on all three legs (fwd / fwd-twice / rev). Legs 1-2
  completed in the original chain; leg 3 was killed mid-suite by
  a runtime restart (2026-11-06 ~10:13 CST; partial log preserved)
  and rerun to TERMINAL GREEN — disclosed here, not hidden in the
  count.

## Correction round 3 — absence requires positive proof (EACCES)

Ruling (Mode A, 2026-11-06 ~09:58 CST; archived
responses/DIRECTOR_MODE_A_RULING_2026-11-06_72_31_CORRECTION3.md):
CORRECTION_REQUIRED at 79c3c46. The `lexists` gate itself hides
lookup ERRORS: with a real CURRENT file whose parent directory
loses search permission, `os.lstat` raises PermissionError
(EACCES, as a non-root user) yet `committed_generation_state`
returned `("absent", None)`. Classification defect only; the
Director observed no lost confirmation in his run.

Repair (commits b8f31c4 production + 506823e suite; FINAL code SHA
506823e26ad8b0a96cb34ed1b8a6f3388dbfd238):

- `committed_generation_state` now opens with an error-preserving
  `os.lstat` on the pointer path: `FileNotFoundError` -> absent
  (the ONLY absence proof); any other lookup exception ->
  unreadable; then `_read_pointer` success -> verified, any read
  failure after the entry was observed -> unreadable.
- New suite cases (51 -> 57 checks): **D1PE** — the real-filesystem
  EACCES case. This VM's suite runs as root (uid 0), where EACCES
  cannot occur, so the case copies `form/` to a world-traversable
  /tmp tree and runs the classification as user `nobody`
  (`setpriv --reuid=nobody --regid=nogroup --clear-groups`): the
  worker proves PermissionError (errno 13) on a direct `os.lstat`
  of the pointer, then asserts the classification is unreadable.
  **D1SE** — the same EACCES fault carried through a lone-worker
  confirm (an `os.lstat` wrapper raising PermissionError only for
  the owner's pointer path; faithful at both code versions because
  `lexists` internally calls `os.lstat` and swallows the OSError):
  refusal `baseline_unverifiable`, zero commit calls, proposal
  pending on fresh-process reload. Missing-file, directory,
  dangling-link and successful-retry controls retained.
- Failing-first at 79c3c46: **53/57**, failing exactly
  `D1PE.classified` and the three D1SE checks. The lexists mutant
  (round-3 repair reverted to the `lexists` gate) is killed with
  the identical 53/57 profile; reverted by inverse edit.
- Neighbours: confirm_crash_matrix 21/21 ·
  checkpoint_generation_stress 15/15 · graph_journal_crash 12/12.
- Fresh clone (clean clone from GitHub, checkout at the final
  code SHA 506823e, HEAD verified, tree clean): suite **57/57
  PASS**.
- T3 at 506823e (run7, sequential, isolated state): TERMINAL
  GREEN **244/244** on all three legs (fwd / fwd-twice / rev,
  LEG_RC=0 x3, CHAIN_DONE), with the 57-check suite inside the
  regression.

Round-2/3 lesson, generalized: a helper that collapses distinct
outcomes into one value (best-effort None, `lexists` False,
`isfile` False) must never feed an identity or absence decision.
Absence requires positive proof (FileNotFoundError from an
error-preserving lookup); every other outcome is uncertainty,
and uncertainty fails closed.

## Scoreboard correction + register reconciliation (Director-ordered)

- **OCI tool bug (Uni's, owned).** `oci.py` matched register status
  cells with startswith checks that markdown-bold cells
  (`**OPEN**`, `**BLOCKED**`) miss, then scored the misses with a
  non-rubric default of 25 — +45/+25 = 70 phantom points. The
  Director's arithmetic is correct: the register as delivered
  yields 3,770/7,200 = **52.4%**, not the reported 53.3%. The
  script is fixed (emphasis stripped before matching; an
  unrecognized status is now a hard error) and verified against
  both registers: main **52.4%** (16/49/3/3/1) and the PR #308
  register **52.6%** (16/48/4/3/1 — likewise not the reported
  53.6%).
- **Register rows reconciled in this PR** (bounded; statuses change
  only where delivered evidence + a Director ruling already closed
  the item): 72-31 gains this repair note (stays PARTIAL — Q-31R.1
  outstanding at the final head; Q-31R.2 answered FIX bounded); **72-64 -> COMPLETED** (its whole content
  was the README/docs refresh: PR #301, Director bounded PASS
  2026-11-05, merged 3a29e35; the README already points at the
  canonical LIST — the row's 'refresh counts' action was obsolete);
  72-17's remaining action replaced (the one-probe investigation
  it requested is complete and its repair Director-confirmed
  bounded 2026-11-06 00:41 CST; status token unchanged); 72-28's
  remaining replaced (the hybrid it asked to evidence is
  demonstrated; what remains is the C-A repair on its F2 path);
  72-30's remaining replaced (the Q1 audit it requested is
  complete; what remains is the gated C-B repair). The register
  footer line calling 72-64's drift open is corrected with it.
  Post-reconciliation counts: 17 COMPLETED / 49 PARTIAL /
  3 INVESTIGATION / 2 OPEN / 1 BLOCKED -> OCI **53.6%**, strict
  17/72 — reported separately from the as-delivered 52.4% so the
  tool correction and the row reconciliation never blend.
- **Defect dial reconciled by ID** (the retired '7 tracked /
  5 fixed / 3 gated' summed to eight listed entries against a
  seven denominator and is withdrawn as irreconcilable):
  FIXED — DD-01 Class E counts (PR #309), DD-02 Class D zombie
  args (PR #310), DD-03 Studio __RENDER__ (PR #311), DD-04 72-29
  checkpoint family, 3 classes (PR #312), DD-05 72-32 graph-journal
  family, 3 classes (PR #313). GATED — DD-06 everyday-save hybrid
  pair (C-A circuit), DD-07 Q1 family W1/W2/W3 (PR #294 hold),
  DD-08 72-16 semantic divergence (R-2 review authorized).
  IN VERIFICATION — DD-09 72-31 confirm-race family (D-A/D-B/D1U
  plus the round-2 baseline-refusal and round-2/3
  pointer-classification classes, this PR). Reconciled dial: 9 families — 5 fixed (9 classes),
  3 gated (5 classes), 1 in verification. No repaired-defect
  percentage is claimed.

## Queue after this circuit (per the ruling)

72-36 nested Core II version validation (moved ahead of 72-35;
bounded repair authorized after 72-31: reject unsupported explicit
versions — 999 / true / "1" / null / -1 reproduced on main —
before binding, preserving legacy missing-block files) -> 72-35
atomic-write failure boundaries. 72-28 advances on its separate
C-A/F2 path; C-B stays independently scoped; R-2 stays
mapping-only; #307 requires Ace's tap; #233/#294 fenced; #308
held as the census record. Whole-program certification withheld.

## Anticipated probes

- *Why not fix current_generation_id itself?* It has best-effort
  consumers (DCC epoch context) whose contract is 'never raise,
  context only'. The defect was using a best-effort accessor for
  an identity decision; the repair gives identity decisions their
  own strict reader instead of changing the shared helper's
  contract under unrelated callers.
- *Does the uncertain branch leak the lock?* The lock release is
  in the handler's common tail (`_release_commit_lock()` runs on
  every path through the except block); D1B proves it operationally
  — a fresh instance confirms immediately after the baseline
  failure.
- *Journal 'preserved' vs 'clean' — D1B keeps it, D1U doesn't.*
  Different dispositions, both verified from a fresh process:
  D1B's loser was the only in-flight attempt when it failed, so
  its intent journal remains as recovery evidence; in D1U the
  winner's successful commit legitimately cleared the shared
  per-owner journal before the loser's recheck failed, so the
  correct disposition is absence (no stale intent misrepresenting
  durable state) plus the loser's instance-level recovery mark.
- *Could the tri-state reader misclassify a torn pointer read as
  'absent'?* No: after round 3, absence is returned only when the
  error-preserving `os.lstat` on the pointer path raises
  FileNotFoundError. Lookup errors (EACCES included), directory or
  dangling-symlink shapes, corrupt JSON, wrong version, owner
  mismatch and read OS errors all land in 'unreadable'.

## Questions for the Director

- **Q-31R.1** — Exact-head ruling on this PR (through Ace, per the
  directive): confirm the bounded repair at the final head (code
  SHA 506823e: D-A/D-B at 3c905e3, tri-state compensation at
  756916c, baseline refusal at 79c3c46, error-preserving pointer
  classification at 506823e; 57-check race proof; T3 TERMINAL
  GREEN 244/244 x3 at both corrected heads) so the merge may
  proceed under your ruling — or state the correction required.
- **Q-31R.2** — ANSWERED by the Director (round-2 ruling,
  2026-11-06 ~09:40 CST): **FIX, bounded to 72-31.** Broader
  save-path changes retain their separate gate. Recorded; no
  further answer required.
