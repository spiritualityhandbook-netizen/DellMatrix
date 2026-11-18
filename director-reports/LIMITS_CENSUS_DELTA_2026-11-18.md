# LIMITS CENSUS — CURRENT-MAIN DELTA CLASSIFICATION (2026-11-18)

Companion to `LIMITS_CENSUS_2026-11-13.md`, landed on main by this PR per
Director disposition 6980308495 (PR #427). The census itself is a PINNED
2026-11-13 baseline (185 limits: 70 HINDERS / 88 GUARDS / 12 ELASTIC /
15 UNKNOWN) and is preserved byte-identical (source blob
c4509c57080586e198ee4fc73448049b25c2fa16). Its counts are NOT re-measured
November 18 truth.

This delta classifies ONLY the limits actually rechecked against current
main (a92e8e3b) with firsthand evidence. Every other census row stands
exactly as pinned: NOT RECHECKED.

## Rechecked rows

- **R26 (DuoBeta ledger detail cut to 120 chars, two enforcements — census line 97) — CLOSED / MERGED.** Repaired
  and merged as PR #483 (merge c93e358b, 2026-11-18); merged-main proof
  29/29; Keeper CODE credit 6977388157; CODE +1 settled. The census row's
  defect no longer exists on main.
- **Q-LC.1 (undo/redo) — CLOSED / IMPLEMENTED to documented scope.** Merged
  as PR #481 (merge d17c6b4, 2026-11-18); CODE +1 settled (Keeper credit
  6975649030); plan record merged as PR #434 (a92e8e3b). Scope is the
  documented undo/redo repair, not arbitrary cross-room undo (Director
  6980308495).
- **R17 (phantom default-8 composition bound) — IN FLIGHT.** Defect
  confirmed and repaired through three correction rounds on PR #485
  (current head e26e27cc); Director contract 6978656808 (unspecified nested
  nonterminal refuses as bound_unspecified; bounded fail-closed scan).
  CI terminal ALL SUCCESS at e26e27cc; x3 campaign + Keeper CODE CONFIRM +
  Director final outstanding. NOT merged; no credit.
- **R23 (outcome-ledger fixed input bounds) — DEFECT VERIFIED LIVE
  2026-11-18.** Constants confirmed on current main in Uni's G1 challenge
  CH-05 (PR #486): outcome_ledger.py _MAX_INPUT=200, _MAX_ERROR=300,
  _MAX_MESSAGE=200, _MAX_STATE_NOTE=300, search clamp 100. Spec accepted
  as GP-E02. Not yet repaired.
- **R24 (translate fixed cuts) — DEFECT VERIFIED LIVE 2026-11-18.**
  Confirmed in G1 challenge CH-04 (PR #486): translate.py [:60]/[:240]/[:80]
  cuts and siblings present on current main. Spec accepted as GP-E01.
  Not yet repaired.
- **R25 (extra shorthand operand) — CONTRACT RULED.** GP-E04 (PR #486):
  extra shorthand token refuses as CONDITION_EXTRA_OPERAND plus correction
  scope; the defective test pin is challenged in that circuit (CH-15).
  Not yet repaired.
- **R19 (cycle visibility / router-translate pre-clamps / flow 99) — NOT
  RECHECKED in this delta.** It is the next R-order circuit after R17 per
  the PR #427 repair order; no current-main verification is claimed here.
- **R5 (history truncation family) — NOT RECHECKED in this delta.**
  Reproduction is owed as GP-E05 evidence (CH-16, PR #486); no
  current-main claim is made here.
- **FI-012 binding (Director 6980308495):** no destructive fixed
  200-PENDING Nursery storage ceiling is to be implemented; Ace's ELASTIC
  INTAKE rule is the binding end-state. A five-result topic display is a
  presentation window with full counts/paging, not a persistent cap. The
  historical proposed cap remains in the audit record, named superseded
  for destructive retention only.

## What this landing is not

Records only. No product code changed. No scoreboard denominator, PLAN or
CODE credit changes. PR #427 closes as SUPERSEDED BY LANDED RECORD once
this PR merges under section 32; it is not merged itself and earns no
credit.
