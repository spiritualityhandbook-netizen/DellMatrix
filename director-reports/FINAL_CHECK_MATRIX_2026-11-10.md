# FINAL-CHECK MATRIX — item-specific closure candidates

Uni main session, 2026-11-10 ~22:45 CST, per Director MODE D ruling
(mail 1a1c8ea8dd1d247c): #374 SCOPED_RECORD_ACCEPTED as evidence;
this matrix links, for EACH merged-backlog item, the exact merged
SHA, the actual postmerge command/output, failure/attempt history,
authority trail, remaining exclusions, and a PROPOSED status.
Nothing here promotes itself — closure stamps are the authorities'.

Postmerge evidence base: fresh clone of merged main
5362f53ff20e (FINAL_CHECK_SWEEP_2026-11-10.md, merged via #374
ea4773a) plus merge-time receipts on each PR. No tests were rerun
for this matrix (Director: no reruns without a concrete gap).

## Item rows

### MWL 2 — DD-44 loop bounds (PR #360)
- Merged: d58a3d5 (head 0773d13).
- Postmerge: `form.dd44_bounds_explicit_test smoke()` on merged
  main at merge time 16/16; sweep at 5362f53: True.
- Failures/attempts: none outstanding; two wording follow-ups
  split off as Q-DD44.2/Q-DD44.3 (MWL 13/14, OPEN, not this item).
- Authority: Director SCOPED_CODE_PASS + Keeper scoped CONFIRM.
- Exclusions: Loop 13 grammar receipts (Q-DD44.2), Compose
  recursion (Q-DD44.3) — separate items.
- PROPOSED: COMPLETE (Q-DD44.1 scope).

### MWL 4 — DD-31 diagnostic capture hardening (PR #350)
- Merged: e4aad9d (head b6b0307).
- Postmerge: `form.regress_capture_test smoke()` True at sweep
  (27/27 internal); local full regression GREEN at head pre-merge;
  capture-file hygiene verified (4 files, none in repo).
- Failures/attempts: branch required a rebase cascade during the
  records-batch day; no product failures.
- Authority: Director SCOPED_CODE_PASS + Keeper CONFIRM; Keeper
  final-check flag cleared 19:01 CST (records).
- Exclusions: DD-31 root mechanism remains OPEN (separate item;
  this item is the capture hardening only).
- PROPOSED: COMPLETE (capture-hardening scope).

### MWL 5 — DD31-CI-INTERMITTENT fix (PR #361)
- Merged: c13de21.
- Postmerge: dd31 suite 21/21 on merged main at merge time;
  `form.dd31_sanitize_copula_test smoke()` True at sweep.
- Failures/attempts: the defect itself was a test-oracle flaw
  (whole-directory substring scan), root-caused with a planted-file
  differential (20/21 red planted, 21/21 clean removed).
- Authority: Director scoped PASS + Q-DD31F.1 SCOPED CONFIRM +
  Keeper CONFIRM (ba6609a); Keeper final-check flag cleared 19:01.
- Exclusions: none within scope.
- PROPOSED: COMPLETE.

### MWL 6 — Q-DD31F.2 sibling repair (PR #372)
- Merged: 5d2deb4 (head 1182e35; one test file:
  form/mandell/p0_integrated_proof_test.py).
- Postmerge: p0 smoke() ALL GREEN (13/13 internal) on merged main
  at merge time; sweep at 5362f53: True. Local regression fwd /
  --twice / rev TERMINAL GREEN at head pre-merge.
- Failures/attempts: legs launch needed three attempts (wrong
  branch name, then a shell backgrounding mangle) — all disclosed;
  the suite itself never failed at the candidate head.
- Authority: Director SCOPED PASS (P3 oracle only) + conditional
  authorization; Keeper final-check flag cleared 18:01 CST.
- Exclusions: the 17 SUSPECT suites from the inventory remain an
  evidence-first investigation (not declared clean or defective);
  they are NOT part of this item's closure.
- PROPOSED: COMPLETE (the one proven sibling's repair scope).

### MWL 7 — WORKFLOW role seeds implementation (PR #367) — STATE-BOUND
- Merged: 70a478e.
- Postmerge evidence class: STATE-BOUND, split per the Director's
  instruction. The verification target is persisted owner state
  (WFROLES1 field: 31 PENDING proposals), which is NOT repository
  content and cannot be reproduced from a bare clone. Evidence of
  record: fresh-process reload verified at build; run 2 reproduced
  269/272 atom classes; 3 run-conditional atoms named with proven
  preconditions (89[Diff] baseline UNKNOWN; two 94[Catch] atoms
  execute only inside an open Try room).
- Failures/attempts: run 1 vs run 2 delta fully explained by the
  3 run-conditional atoms; no unexplained variance.
- Authority: Director MODE D SCOPED CERTIFICATION of the evidence
  record, accounting, and state-isolation results ONLY + Keeper
  record-truth CONFIRM.
- Exclusions: the seeds as an accepted catalog were NOT certified;
  Ace's Nursery confirm of the 31 proposals remains his separate
  sovereign step (non-blocking; tracked in the MWL appendix).
- PROPOSED: COMPLETE for the implementation/record scope exactly
  as certified; no catalog claim.

### MWL 8 — Governance records publication batch (PRs #351–#356, #362–#366, #368, #371, #373, #374)
- Merged: 4b1761d / 4b04f2f / a7f59c9 / 8bf09b5 / f8295f3 /
  554af27 / 95c7409 / 88c1c5e / 318736014 / (see PRs) / 92dadd3 /
  3651a5b / da73ff9 / a2d67d2 / ea4773a.
- Postmerge: presence + currency on main verified in the sweep
  clone (incl. the refreshed DIRECTOR_REVIEW_QUEUE.md via #373 and
  this matrix's predecessor sweep via #374, SCOPED_RECORD_ACCEPTED).
- Failures/attempts: the batch required multiple rebase rounds
  (INDEX union conflicts) and one description race by a background
  cycle (disclosed, corrected); all merges terminal-green under
  SS32 at their steps.
- Authority: dispositions recorded per PR; Keeper final-check
  flags cleared for the records set (18:01/19:01 deep cycles).
- Exclusions: records publication only — the engineering items
  these records describe keep their own statuses.
- PROPOSED: COMPLETE (publication scope).

### MWL 152 — DD-37 Roster / C8.Roster (PR #370)
- Merged: ad2a12c (head 2b95d86).
- Postmerge: fresh clone of merged main: `form.dd37_roster_test
  smoke()` 15/15 True; `form.regress_capture_test` spot 27/27;
  sweep at 5362f53 re-verified True.
- Failures/attempts: two legs incidents (wrong-path launcher;
  VM replacement mid-leg-2 counted NO RESULT and rerun) — both
  disclosed; final legs fwd/--twice/rev all TERMINAL GREEN.
- Authority: Director SCOPED_CODE_PASS + CONDITIONAL MERGE
  AUTHORIZATION (17:58 CST), 18:38 CST recognition of merged +
  scoped postmerge receipts with item held MERGED_UNVERIFIED
  pending independent closure/register reconciliation — this
  matrix + sweep are that reconciliation package; Keeper scoped
  CONFIRM (9d39cdc, disposition file on main).
- Exclusions (explicit): C8.Roster ONLY — not all C8; sibling
  session modules untouched; 50-proposal bound untouched; no UI
  claim; forward-only for pre-fix evicted sessions (unrecoverable,
  disclosed).
- PROPOSED: COMPLETE (C8.Roster scope).

### PR #369 — Master Work List publication (reconciliation note)
- Merged: 6b2bad8 (head 547f27c). Docs-only; Director
  SCOPED_DESIGN_PASS with NO completion credit — this matrix takes
  none. The list is infrastructure: its data currency is maintained
  by regeneration (items 1/3/152 flips ride the post-merge
  regeneration), and its closure is the Director's design pass,
  already on record. Not an MWL item; no status proposed.

## Scoreboard fence
Headline remains 25/179 = 14.0% until the authorities stamp the
proposals above. If all seven proposals (MWL 2, 4, 5, 6, 7, 8, 152)
are confirmed, COMPLETE becomes 32/179 = 17.9% — stated as a
projection, not a claim.
