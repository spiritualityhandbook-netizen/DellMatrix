# DIRECTOR REPORT — 72-28 (SM-35): Program/Nursery Pair-Atomic Crash Proof

**Item:** Master Register 72-28 — Program/Nursery pair-atomicity
under crash was unproven as one closed contract (the checkpoint
seal's crash evidence existed as fragments; the ordinary save
path's pair behavior was an unexamined assumption). Executed in
SUSX100,000 Cycles 21–25, 2026-11-05.
**Branch:** `uni/72-28-pair-atomic-proof`. **Code head:**
`b893931` on main `ed4ac00`. This report is prepared locally at
that head and rides in the PR when a review slot clears.
**Status:** SUBMITTED for Director review. Uni label on merge:
MERGED_VERIFIED_BY_UNI (not a certification). **This is a
proof circuit (Part A): no product code changed. Part B — any
repair of the ordinary save path — is NOT built and requires
a Director ruling (see Questions).**

## The gap

Two different pair paths write the canonical program and
nursery files, and they must not be collapsed:

- **Ordinary saves** have NO pair transaction. `Program.save`
  writes only the program file (owner lock, TD-1-R2);
  `Nursery.save` writes only the nursery file (no owner lock,
  per-instance signature check). `atomic_write`'s own contract
  disclaims cross-file transactions: each file is written as
  one complete generation, the PAIR is not.
- **The checkpoint seal** is the only pair-atomic mechanism:
  an intent journal plus a byte-preserved pair taken before
  the first durable write, a pointer swap as the commit
  boundary, and `load()` convergence (old pair / target pair /
  fail-closed). Its crash behavior had never been run as ONE
  closed proof across the staged-write crash points with a
  fresh-process load verdict.

## Falsification first (pristine code)

A cross-process probe (`mr28_probe.py`, genuine child OS
processes, unique owner per case, verdicts read from a
fresh-process `persist_rest.load()` view) ran at main
`ed4ac00` before any suite was built. Run 1 failed on a
probe-harness assumption only (slugified proposal IDs;
recorded, not evidence). Runs 2 and 3 returned IDENTICAL
verdicts:

- **H1-A** (nursery save lands, crash before program save):
  HYBRID — new proposal + old program exposed; load rewrote
  NO files.
- **H1-B** (program save lands, crash before nursery save):
  HYBRID — new unit + old nursery exposed; load rewrote NO
  files.
- **CP1** (checkpoint, crash at nursery stage): OLD_ONLY, no
  load rewrite. **CP2** (crash at program stage): OLD_ONLY,
  load restored the preserved pair byte-exactly. **CP3**
  (crash at pointer swap): OLD_ONLY, load restored the
  preserved pair. **CP4** (crash after commit): NEW_PAIR.
  **CP0** (clean commit control): NEW_PAIR.

**H1 CONFIRMED in both orders:** an interrupted ordinary
pair save leaves a hybrid live pair that a fresh load
exposes as-is. The checkpoint path was NEVER hybrid at any
crash point. SWAT choice: proportionate falsification
(proof-only over existing seams); full SWAT is required
before any repair. Recorded in the grounding paper.

## What was built

- `form/sm35_pair_atomic_test.py` (NEW, 45 checks): the
  probe restructured as a self-contained suite (children
  invoked as `python3 -m form.sm35_pair_atomic_test
  <mode>`). H1-A/H1-B assert the HYBRID outcome + no-rewrite
  as a **bounded statement** (per-file atomicity only is the
  current ordinary-path contract — named as such, not
  silently blessed); CP1 asserts OLD_ONLY with no rewrite;
  CP2/CP3 assert OLD_ONLY with preserved-pair restore;
  CP4/CP0 assert NEW_PAIR. Every case also asserts child
  setup, the crash observation (rc=42 at the real stage
  boundary), a successful fresh-process load, and old-pair
  presence.
- Registered in `form/regress.py` (canonical count
  237 -> **238**, uniqueness verified via
  `intended_entries()`).
- README suite count updated 237 -> 238 in the same commit.

## Evidence

- **Probe:** two identical cross-process runs at `ed4ac00`
  (H1 confirmed; CP0–CP4 as above). Evidence label:
  CROSS_PROCESS.
- **Targeted suite:** 45/45 GREEN at `b893931`; **fresh
  clone at `b893931`: 45/45 GREEN**; post-mutant-revert run
  45/45 GREEN.
- **Mutants (3, real work committed first, inverse-edit
  reverts, git diff 0 lines after each):** M1
  `persist_rest.load`'s `recover_checkpoint_intent` call
  dropped — KILLED at CP3 (verdict HYBRID). M2 seal's
  program save skipped — KILLED at CP4 (verdict HYBRID).
  M3 ordinary save also saving the nursery (pair save) —
  KILLED at H1-B (verdict NEW_PAIR), proving the H1
  bounded-statement checks are not vacuous.
- **Finding inside M1 (disclosed, not hidden):** under M1,
  CP2 still converged OLD_ONLY — `form/open.py:255` is a
  SECOND legitimate `recover_checkpoint_intent` call site
  covering CP2's divergence but NOT CP3's. The
  `persist_rest.load` call site is load-bearing for CP3;
  CP2 has defense in depth.
- **Full regression x3 (sequential, main-session chain,
  terminal logs read in full):** fwd **238/238 GREEN**
  (rc=0, 2026-11-05T12:00:19Z); `--twice` **238/238 GREEN**
  (rc=0, 12:19:41Z); `--order rev` **238/238 GREEN** (rc=0,
  12:29:10Z), all at `b893931`, with sm35 45/45 inside each
  leg.
- Test realism: CROSS_PROCESS (genuine child OS processes;
  product `crash_*` seams are literal `os._exit(42)` at real
  stage boundaries; the H1 crash is the probe child's own
  exit between the two real ordinary saves — disclosed).
  Below REAL_USER_PATH.

## Boundaries

- Part A proves the CHECKPOINT path's pair-atomic contract
  and bounds the ORDINARY path's contract as per-file only.
  It does not repair the ordinary path, and the hybrid
  exposure is asserted as current documented behavior
  pending a ruling — the same exposure the Q1 audit's T3
  writer class describes (Q1 Amendment D adopts C-B:
  coherence claimed only against journaled transactions;
  C-A, a pair-save funnel, is separate future work
  requiring human authorization).
- No Q1-scope code was touched; Q1 repair remains STOPPED.
- Graph (`graph_<owner>.json`) and per-Idea persistence are
  outside this circuit's pair definition, per the Q1 scope
  split.

## Anticipated probes

- "Is H1 a defect or a design contract?" It is an
  absence-by-design per `atomic_write`'s own contract — but
  until this circuit, no load/API wording marked the pair
  as NOT GUARANTEED (the Q1 plan now carries that marking
  as a binding acceptance criterion). Whether the behavior
  itself should change is the Part B ruling requested
  below, not a conclusion this proof asserts.
- "Does CP2's second call site make M1 a weak kill?" M1 is
  killed by CP3 exactly; the CP2 coverage is disclosed
  above rather than averaged away.

## Questions for the Director

- **Q1 (Part B):** rule one of — (a) authorize a bounded
  ordinary-path repair circuit (pair-save funnel; overlaps
  Q1's deferred C-A), (b) accept per-file-only as the
  ordinary path's standing contract with the NOT-GUARANTEED
  marking as the complete remedy, or (c) defer Part B until
  the Q1 implementation circuit is authorized and decide
  both there.
- **Q2:** is the CP2 defense-in-depth (two legitimate
  `recover_checkpoint_intent` call sites) acceptable as-is,
  or should convergence ownership be consolidated to the
  single `persist_rest.load` site in a future circuit?

---

## Addendum 1 — Evidence supplement, reconciliation, merge timing, defect status (2026-11-05)

Supplied under the Director's exact-head review (2026-11-05
09:32 CST, Gmail 1a1ac56ce97780e7): INSUFFICIENT_EVIDENCE for
independent ALL_AI_CONFIRMATION_PASS; retrievable evidence,
pinned runner, independent receipt, and b893931<->2fefcdc
reconciliation demanded.

- **Evidence bundle:** director-reports/evidence/72-28-pair-atomic/
  — original raw logs (probe x3, suite, post-revert, mutant
  kills x3, fresh clone, regress x3 + chain), the probe source
  (verbatim from 132f39b), labeled mutant RECONSTRUCTION diffs,
  MANIFEST.sha256, and verify_72_28.sh (fresh clone; pinned
  head asserted before manifest verification; suite at
  b893931 and 2fefcdc; probe at 2fefcdc; byte identity of the
  suite and both product files across b893931/2fefcdc/a585a6d;
  three mutant re-executions at 2fefcdc asserting the original
  CP3/CP4/H1-B signatures). The verify-72-28 GitHub Actions
  workflow executes the script at the exact pushed supplement
  head as the independent receipt.
- **Reconciliation:** b893931 -> 2fefcdc changed NO code under
  test (documentation + a merge of main + removal of a
  swept-in working paper; byte identity asserted by the
  script, step 5). Executions at b893931 are executions of
  the merged code.
- **Bounded wording (accepted corrections):** H1 demonstrates
  the crash between two separate ordinary saves — a bounded
  ordering, not all crash schedules. "Never hybrid" is
  bounded to the CP0-CP4 seams and tested assumptions.
- **Merge timing (recorded plainly):** the review's "Hold PR
  #298" was sent 09:32 CST while Form smoke was in progress;
  the main session merged #298 at ~09:37 CST on terminal-green
  CI under the hard gate, BEFORE the email was processed
  (09:49, via heartbeat) — the same timing pattern as PR #296.
  PR #298 therefore stands as MERGED_VERIFIED_BY_UNI only;
  no confirmation is claimed or inferred from the merge.
- **Defect status (Mode A assessment, 2026-11-05, Ace-relayed):**
  the demonstrated everyday-save defect remains OPEN; this
  proof circuit's closure does not close it. Part B is
  DEFERRED into the Q1 transaction design (PR #294 Amendment
  E); CP2's two recovery call sites remain unchanged pending
  a separately scoped review. No Part B or Q1 implementation
  is authorized by anything in this supplement.

### Addendum 1 receipt — independent CI execution (2026-11-05)

The verify-72-28 GitHub Actions workflow executed
verify_72_28.sh at supplement head 83d18ca0 on a GitHub-hosted
runner (run 42062153339, conclusion SUCCESS; runner
runnervmwuk1x, Python 3.14.4): manifest verified, suite
45/45 at b893931 and at 2fefcdc, probe exit 0, byte identity
across b893931/2fefcdc/a585a6d, and all three mutant
re-executions killed at the original CP3/CP4/H1-B
signatures — ALL STEPS PASS. Full log:
evidence/72-28-pair-atomic/verify_72_28_ci_run.log. The job
re-executes at the final supplement head on this receipts
push; that run is the receipt for the final head. This is
independent execution evidence for the Director's scoped
confirmation decision; it is not itself a confirmation.
