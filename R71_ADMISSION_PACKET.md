# R7.1 ADMISSION PACKET — Read-Only Perspective Composition (AMEND)

**Directive:** GDP_R71_COMPLETE_REAL_COMPOSITION_AND_FAILURE_PROOFS (MODE=C)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## AMEND Findings (All Addressed)

1. **Container validation:** `None`, `False`, `0`, `""`, `{}` explicitly reject
   (UNSUPPORTED). Only valid empty list/tuple → empty request.

2. **Failure boundary:** Dispatch, validation, detachment (deepcopy), and report
   construction all enclosed. Copying failures bounded (UNAVAILABLE), no exception
   text reflected. Sibling components preserved.

3. **Real confirmed Ideas:** Fixtures use coordinator + grants; assert receipts,
   confirmed status, exact Plane presence.

4. **No unconditional verdicts:** Removed `or True`; swept suite.

5. **Fresh-process restart:** Fixed-script OS process reloads production state,
   recreates identical specs, compares against pre-captured expected. Exit zero
   with structured assertions.

6. **Exact aggregation:** Asserts specific outcomes (all REAL→REAL, mixed→PARTIAL,
   malformed→UNSUPPORTED, etc.), not permissive.

7. **Detachment:** Mutates actual nested observations (vision, report); verifies
   canonical Plane units unchanged and complete Viewer state preserved.

8. **State:** Captures proposal count, Plane count, statuses, unit IDs (not just count).

## Exact Identity

- **Branch:** `gdp-phase7-r71-composition`
- **Head:** [to be recorded after final commit]
- **Tree:** [to be recorded after final commit]
- **Base:** `efd68bf5ef702dcb5a59aa246ed4397c0c0a133c` (R6.5 production)

## Objective Identity (Preserved)

R7.1 is the first Phase-7 implementation circuit, covering the **Perspectives**
stream only. Workshop (7.1) and Connected World (7.3) objectives remain
unimplemented. Uninspected Phase-7 objectives marked UNKNOWN.

## Implementation

**`compose_views(program, specs)`** in `form/dell_matrix/perspective_views.py`:
- Validates container type before interpreting emptiness
- Validates mode-relevant Viewer fields (parts radius, skins)
- Routes each validated spec through existing `see_as`
- Encloses dispatch, detachment, and report construction in failure boundary
- Preserves input order; attaches viewer, mode, source, epistemic_status
- Returns detached components + attributed combined report
- No truth merging; no count summing; no Viewer mutation
- Trusted local query only; no agent/network exposure

**Aggregation semantics (explicit):**
- All REAL → REAL
- Readable mixed with legacy/failed → PARTIAL
- No readable → explicitly unverified (reasons preserved)
- Empty → explicitly empty request
- Malformed → UNSUPPORTED (explicit rejection)

**Grant rejection:** Unexpected kwargs rejected with explicit list.

## Proof (45/45)

- Confirmed Ideas: real coordinator + grant confirms; receipts, status, Plane
- All modes: distinguishable nonempty observations
- Exact aggregation: specific outcomes asserted
- Grants: rejected
- Malformed: containers, specs, poses, modes all bounded
- Detached: nested mutation; canonical untouched
- No truth merging: components separate; counts not summed
- State: meaningful (counts, statuses, IDs)
- Copying failure: bounded, no leak, sibling preserved
- Sensitivity: detachment and aggregation boundaries weakened → diverge; restored
- Restart: fresh OS process, structured assertions, exit zero

## Verification

- Targeted: 45/45
- `--twice`: 112/112 GREEN
- `--order rev`: 112/112 GREEN
- Exact-head CI: [pending]

## Delta-20

All 20 categories re-examined. See `R71_DELTA20.md` (AMEND version).

## Research Preserved

Dispositions and source links in `~/workspace/PHASE_7_R71_WORK_ORDER.md`.

## README

Executed composition example in capabilities table.

## Costs

- 1 function (`compose_views`) in existing module
- 1 test file (45 checks)
- 1 README row
- Zero changes to R6.1–R6.5 runtime behavior

## Limits

- Single-host; no networking
- Composition is query-only; no workshop sessions
- Scanning: EVALUATION_UNAVAILABLE if applicable

---

**END OF R7.1 ADMISSION PACKET (AMEND CANDIDATE)**
