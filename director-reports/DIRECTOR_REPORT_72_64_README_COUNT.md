# DIRECTOR REPORT — 72-64 README SUITE-COUNT REFRESH

Circuit: Master Objective Register item 72-64 (= SM-62), reconciliation §6 batch 4, smallest falsifiable scope first. Docs-only circuit; no code changed.

## Claim verified (failing-first, at base)

Base: main `8e0784cd15d78d60a148c09942d3a185fec07529` (fresh clone from GitHub, HEAD verified).

- README.md line 568 claimed a regression harness of **230 suites**; line 607 claimed **230 registered suites**.
- Canonical count at that exact head, computed from the harness itself: `form.regress.LIST` = **236**; `intended_entries()` (LIST + discovered suites, deduplicated) = **236**; discovered suites = 203, all already in LIST. The regress terminal totals all SUSX100,000 cycle long (TD-2, TD-2 F1: 236/236 ×3 legs each) corroborate 236 as the executed count.
- The register's earlier figure (235, at its 2026-11-04 baseline) was correct then; TD-2 added one suite since. Historical mentions of 230/235 in `director-reports/` are dated records and are preserved unchanged, per the register's instruction ("preserve historical counts as history").

## Change

README.md only: 230 → 236 in the two present-tense claims (lines 568, 607). A grep for numeric suite-count claims across README.md finds no other stale figure. No other file changed except this report and the INDEX row.

## SWAT choice

Proportionate falsification (Ace's calibration, 2026-11-04): docs-only, no state, no runtime path. Falsification = the count is recomputed from the canonical harness at the exact head, not copied from any prior document; the two edited lines are the only present-tense count claims in README.

## Anticipated probes

1. "Is 236 LIST or intended?" — Both: LIST = 236 and intended (LIST ∪ discovered, deduped) = 236 at this head, so the wording "registered suites" and "harness of N suites" are each accurate.
2. "Will this drift again?" — Yes, whenever a suite registers; that is inherent to a present-tense count in prose. The count is correct at this head and dated by this report's base.

## Questions for the Director

Q1. Should README stop carrying a numeric suite count (e.g. "a regression harness (`form/regress.py`)") to end the recurring drift class (SM-62 closed this once at 230; it drifted twice since), or is the dated numeric claim preferred?

## Disposition

SUBMITTED for Director review. Uni label if merged: MERGED_VERIFIED_BY_UNI, not certified. Nothing else in 72-64's scope ("stale in-use docs") was found stale in README's suite-count claims; broader docs currency remains "varies" as README itself states.
