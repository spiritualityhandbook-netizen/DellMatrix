# SCOREBOARD RECONCILIATION DELTA — 2026-11-17

**Purpose.** PRs #424 (MWL × Unified crosswalk) and #441 (three-row
reconciliation) were built 2026-11-15 on stale bases and are CONFLICTING
against current main; neither stale head is mergeable as-is. This PR
carries both documents onto current main **verbatim as dated exhibits**
and adds this delta, which re-verifies their open questions against the
canonical register at a pinned main SHA under the live-scoreboard truth
contract (Director corrected ruling 6925729360, 2026-11-16: live
progress renders ONLY from `director-reports/master_work_list_items.json`
+ the `master_list.py` generator at a pinned main SHA, with provenance;
belt totals stay separate and are never blended with MWL progress).

**Pin.** main `8e4e821514fbc61627e066cd927a1623be2bc794` (PR #477 merge).
Verified 2026-11-17 by Uni, mechanically, from
`director-reports/master_work_list_items.json` at that SHA.

## CANONICAL REGISTER AT THE PIN (Uni-verified, mechanical count)

| Measure | Count |
|---|---|
| Rows in canonical JSON | 185 |
| Active basis (excl. SANDBOXED) | 182 |
| COMPLETE | **39** |
| PARTIAL | 54 |
| OPEN | 86 |
| GATED | 3 |
| SANDBOXED | 3 |

Headline: **39 of 182 COMPLETE = 21.4%**, matching the checked-in
`MASTER_WORK_LIST.md` render at this SHA.

## WHAT THIS DELTA SETTLES

1. **Crosswalk Exception X-1 — CLOSED.** The crosswalk (2026-11-15)
   found the two source documents' COMPLETE sets identical at 35 and
   could not name the +4 rows behind the 39 figure from those documents
   (X-1). The canonical register at the pin names them: the four
   post-crosswalk COMPLETE entries are **#130** (Diff becomes the one
   comparison authority — Rings 1+2), **#148** (Schema = the nervous
   system — read-only baseline), **#183** (LM-2 THE SPLITTER), and
   **#184** (GS-4 Growth Sandbox Integrity). All four stand COMPLETE in
   the canonical JSON at the pin. The 35 figure is the correct frozen
   2026-11-15 crosswalk count; 39 is the correct current canonical
   count. No contradiction remains.

2. **227 vs 224 — RECONCILED (carried from #441, verdict stands).**
   The 3-row gap is the MWL's own sandboxed block (#180/#181/#182),
   excluded under the MWL's own standing rule; excluding exactly those
   three reproduces every per-section subtotal in the Unified edition's
   recount. At the pin this is consistent with the canonical register:
   185 rows = 182 active + 3 SANDBOXED.

3. **182 − 4 + 49 = 227 — carried from #424, arithmetic stands.**
   182 MWL rows accounted for (175 active, 3 sandboxed, 4 proven
   duplicates #171/#177/#178/#179); 49 Unified additions with no MWL
   source. Active basis 224. Both figures reproduce the Unified
   edition's Part 0 exactly.

## DISPOSITIONS REQUESTED

- **#424 and #441:** close as SUPERSEDED BY this PR once it merges
  (their full content lands here verbatim; zero loss).
- **#421:** this packet is the auditable crosswalk + 3-row evidence its
  CORRECTION_REQUIRED (6921699052) requires on the counting side. Its
  Unified Edition text still must reconcile to the live-source rule
  before any adoption; this delta does not certify #421's register or
  counts.

Records only. No status in any register is changed by this PR; no
PLAN/CODE credit is claimed.

— Uni Ω, 2026-11-17
