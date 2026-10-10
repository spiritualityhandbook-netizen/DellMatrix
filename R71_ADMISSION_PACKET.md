# R7.1 ADMISSION PACKET — Read-Only Perspective Composition

**Directive:** GDP_PHASE_7_R71_READ_ONLY_PERSPECTIVE_COMPOSITION (MODE=C)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Exact Identity

- **Branch:** `gdp-phase7-r71-composition`
- **Head:** [to be recorded after final commit]
- **Tree:** [to be recorded after final commit]
- **Base:** `efd68bf5ef702dcb5a59aa246ed4397c0c0a133c` (R6.5 production)

## Objective Identity (Preserved)

R7.1 is the first Phase-7 implementation circuit, covering the **Perspectives**
stream only. Workshop (7.1) and Connected World (7.3) objectives remain
unimplemented. Uninspected Phase-7 objectives marked UNKNOWN (not invented).

## Implementation

**`compose_views(program, specs)`** in `form/dell_matrix/perspective_views.py`:
- Routes each validated (Viewer, mode) spec through existing `see_as`
- Preserves input order; attaches viewer, requested mode, source, epistemic_status
- Returns detached components (deepcopy) + attributed combined report
- No merging of conflicting observations into truth; no summing of counts
- No Viewer mutation; no references into canonical state
- Trusted local query only; no agent/network exposure; no permission mechanism

**Aggregation semantics (explicit):**
- All REAL → REAL
- Readable mixed with legacy/failed → PARTIAL (each status retained)
- No readable → explicitly unverified (reasons preserved, no confident counts)
- Empty input → explicitly empty request (not proof of empty Plane)

**Validation:** Modes in MODES; finite poses; valid facing; spec structure.
Invalid → bounded non-reflecting failures (UNSUPPORTED).

**Grant rejection:** Unexpected kwargs (including grants) → rejected with
explicit list, not silently ignored.

## Proof (29/29)

- Positive: real confirmed Ideas, distinguishable viewers, all modes
- Aggregation: empty, mixed, unverified cases
- Grants: rejected (not ignored)
- Invalid: bad mode, non-Viewer, infinite pose, bad facing, malformed spec
- Detached: output mutation does not touch canonical or Viewer
- No truth merging: components kept separate, reports attributed
- State: Program and Viewer unchanged before/after
- Sensitivity: weakened see_as → divergence; restored → normal

## Verification

- Targeted: 29/29
- `--twice`: 112/112 GREEN
- `--order rev`: 112/112 GREEN
- Exact-head CI: [pending]

## Delta-20

All 20 categories examined. See `R71_DELTA20.md`.
Key: no duplicate authority, no contradiction with PERSPECTIVE≠TRUTH,
public-path verified, no new attack surface.

## Research Preserved

Dispositions and source links in `~/workspace/PHASE_7_R71_WORK_ORDER.md`:
- CQRS (Fowler): ADAPT
- pal-mvvm-foundation: ADAPT
- Vortex/Babylon.js/MDN: ADAPT
- Cosmos DB materialized views: ADAPT
- CAPMAS, MCP/A2A: ADAPT (for 7.1, deferred)

## README

Executed composition example added to capabilities table.

## Costs

- 1 function (`compose_views`, ~150 lines) in existing module
- 1 test file (29 checks)
- 1 README row
- Zero changes to R6.1–R6.5 runtime behavior

## Limits

- Single-host; no networking
- Composition is query-only; no workshop sessions
- Scanning: EVALUATION_UNAVAILABLE (quota 402) if applicable

---

**END OF R7.1 ADMISSION PACKET (CANDIDATE)**
