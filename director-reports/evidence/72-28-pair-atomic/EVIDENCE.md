# 72-28 (SM-35) — EVIDENCE BUNDLE

Supplied under the Director's 72-28 exact-head review
(2026-11-05 09:32 CST, Gmail id 1a1ac56ce97780e7,
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_28.md):
INSUFFICIENT_EVIDENCE for independent ALL_AI_CONFIRMATION_PASS.
This bundle makes every claimed execution retrievable at exact
SHAs and supplies the pinned runner + independent CI receipt
the review required.

## Tested SHAs (all full, verified against git)

| Role | SHA |
|---|---|
| Executed code head (suite + probe + mutants + regress) | b8939310b3fb0dc9049cb98a33cd1e28d0d26ebb |
| Report commit | 66fa1bb268db53defa7fc8a51ed49dd955765f7c |
| R5-archive commit (probe briefly committed here) | 132f39b9a7a2ed66512413a630283df602395315 |
| Final PR #298 head | 2fefcdceea1c28251c53ca90028772ebb5713a1e |
| PR #298 merge on main | a585a6ddba9fb2128a3cc927bd4bf826c1a83fb8 |

## Reconciliation b893931 <-> 2fefcdc (demanded by the review)

The branch delta b893931 -> 132f39b is documentation only:
the Director report, the INDEX row, README 237->238, and the
72-49 R5 email archive. 2fefcdc is a merge of main 5962d85 into
the branch (INDEX union; the swept-in mr28_probe.py working
paper removed — it is NOT on main). The suite and both product
files under test are BYTE-IDENTICAL at b893931, 2fefcdc and
a585a6d (verify_72_28.sh step 5 asserts this; suite SHA-256
4c39cbc430e4a5165d301e09c1b6cbc9f07280aae869f866bf61a5fb85a26717).
No execution needs re-attribution: the code that ran at
b893931 is the code that merged.

## Original raw logs (Uni executions, retained from the build)

All produced at code head b893931 unless noted; SHA-256 in
MANIFEST.sha256.

- probe_run2.log / probe_run3.log — the pristine-code crash
  probe, the two identical confirming runs (H1-A/H1-B HYBRID;
  CP1-CP3 OLD_ONLY; CP4/CP0 NEW_PAIR). probe_run1.log — an
  earlier grounding run retained for completeness: the crash
  seams were not yet calibrated (CRASH_NOT_OBSERVED verdicts,
  CP0 COMMIT_FAILED); it is NOT one of the confirming runs.
- mr28_probe.py — the probe source, extracted verbatim from
  commit 132f39b (its only committed form).
- suite_run1.log — suite 45/45 at b893931.
- suite_post_revert.log — suite 45/45 after mutant reverts.
- mutant_m1.log / mutant_m2.log / mutant_m3.log — ORIGINAL
  kill logs. Signatures: M1 CP3 OLD_ONLY assertion; M2 CP4
  NEW_PAIR assertion; M3 H1-B HYBRID assertion.
- fresh_clone.log — fresh clone at b893931, suite 45/45.
- regress_leg1/2/3.log + regress_chain.log — regress x3 at
  b893931, 238/238 each (main session, sequential).

## Mutant distinction (preserved)

The original sessions edited product files in place; no diff
files were saved then. mutant_m{1,2,3}_recon.diff are
RECONSTRUCTIONS, regenerated deterministically from the
report's recorded mutation definitions at b893931.
verify_72_28.sh step 6 re-executes all three kills at 2fefcdc
as LABELED supplement executions and asserts the original
signatures (CP3 / CP4 / H1-B). Nothing here relabels a
reconstruction as an original.

## Bounded wording (corrections accepted from the review)

- H1 demonstrates the crash BETWEEN two separate ordinary
  saves — a bounded ordering, NOT all possible crash
  schedules.
- "Checkpoint never hybrid" is bounded to the enumerated
  CP0-CP4 seams and the suite's tested assumptions.
- The defect statement stands as demonstrated: an interrupted
  ordinary pair save can leave a hybrid live pair that a
  fresh load exposes.

## Defect status

Per the Director's Mode A assessment (2026-11-05, relayed by
Ace; responses/DIRECTOR_MODE_A_ASSESSMENT_2026-11-05_72_28.md):
the demonstrated everyday-save defect remains **OPEN**.
Closing the 72-28 proof circuit does not close the product
defect. Part B is DEFERRED into the Q1 transaction design
(PR #294, Amendment E); no Part B or Q1 implementation is
authorized. CP2's two recovery call sites remain unchanged
pending a separately scoped review.

## Independent verification

    bash verify_72_28.sh <SUPPLEMENT_SHA>

Fresh clone; asserts the pinned head before manifest
verification; suite at b893931 and 2fefcdc; probe at 2fefcdc;
byte identity across b893931/2fefcdc/a585a6d; three mutant
re-executions at 2fefcdc. The verify-72-28 GitHub Actions
workflow runs the same command at the exact pushed supplement
head — that run is the independent receipt.
