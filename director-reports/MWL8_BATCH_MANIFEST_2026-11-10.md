# MWL 8 — Governance Records Publication Batch: Unit Definition, Exhaustive Manifest, Closure Criterion

Published by Uni at the Director's order (mail 1a1c9225c1bae60f,
2026-11-10 23:43 CST) to cure the FINAL_CHECK_MATRIX's "(see PRs)"
placeholder. MWL 8 remains HELD for item-specific completion until an
authority rules against this manifest.

## The one unit

MWL 8 is exactly the set of fifteen records-only pull requests merged
to main on 2026-11-10 that published the day's governance record:
WORKFLOW v1 and its adoption records, the authority-certification
protocol, the six-dispositions record, the Director review queue, the
Master Work List itself, the final-check sweep, and their INDEX,
register, and state-file companions. No product code is in the unit;
no other PR belongs to it.

## Exhaustive manifest (merge SHAs verified against GitHub 2026-11-10)

| PR | Merge SHA | Content |
|---|---|---|
| #351 | 4b1761d22 | records batch 1 |
| #352 | 4b04f2f67 | records batch 2 |
| #353 | a7f59c946 | authority-certification protocol build |
| #354 | 8bf09b5a7 | WORKFLOW v1 fast-lane refinement records |
| #355 | f8295f328 | records batch 5 |
| #356 | 554af2760 | records batch 6 |
| #362 | 95c740964 | records |
| #363 | 88c1c5ef7 | WORKFLOW v1 adoption |
| #364 | 318736014 | records |
| #365 | 444a76062 | records (SHA missing from the matrix; supplied here) |
| #366 | 92dadd33b | records |
| #368 | 3651a5b6f | Director Review Queue publication |
| #371 | da73ff9b5 | Ace's six dispositions record |
| #373 | a2d67d259 | Director Review Queue refresh |
| #374 | ea4773a58 | final-check sweep (SCOPED_RECORD_ACCEPTED, mail 1a1c8ea8dd1d247c) |

## Verification performed

- Every merge SHA above read from `gh pr view` (state MERGED) on
  2026-11-10; each is an ancestor of latest main b1f73caf2d8c.
- The unit's published files are present and current on main
  (INDEX.md, DIRECTOR_REVIEW_QUEUE.md, MASTER_WORK_LIST.md,
  WORKFLOW_V1_FINAL_2026-11-10.md), verified in the final-check
  sweep (PR #374) and the matrix (PR #375).
- All fifteen merges ran under the SS32 hard gate at their steps
  (terminal exact-head checks; the #359-class incident and its
  repair are recorded separately and are not part of this unit's
  claim).

## Explicit closure criterion

MWL 8 is COMPLETE when an authority rules that: (1) the unit
definition above is the correct bounded identity for the batch;
(2) every manifest row's merge SHA matches GitHub's record; and
(3) the unit's files remain present and un-superseded on main at
the ruling's head. Until that ruling, MWL 8 stays MERGED_UNVERIFIED
and takes no completion credit.

## CLOSURE RECEIPT (Uni, 2026-11-11)

Director CONDITIONAL SCOPED_RECORD_PASS (mail 1a1c9549bfb1581c,
2026-11-11 00:38 CST). Verification executed by Uni main session
against GitHub and latest main 8f789cefc60224ca558e540d7f8efc96b0fd6a3b:

- All 15 PRs: state MERGED, mergeCommit OID matching the manifest
  table exactly (scripted gh check, 15/15 MATCH).
- All 15 merge commits are ancestors of latest main (git
  merge-base --is-ancestor, 15/15).
- Product code in diffs: ZERO files under form/ or gui/ across all
  15 PRs (records-only confirmed).
- Publication files present and unsuperseded on main: INDEX.md,
  DIRECTOR_REVIEW_QUEUE.md, MASTER_WORK_LIST.md,
  WORKFLOW_V1_FINAL_2026-11-10.md, this manifest,
  FINAL_CHECK_MATRIX_2026-11-10.md.

Result: MWL 8 COMPLETE (records-only scope) under the conditional
pass; no product/runtime claim. Criterion of the manifest met.
