# R7.1 ADMISSION PACKET — Read-Only Perspective Composition (FINISHED)

**Directive:** GDP_R71_FINISH_EXISTING_OUTCOME_EVIDENCE (MODE=C)
**Date:** 2026-10-10
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Proof Corrections (All Addressed)

1. **Populated observations:** Viewers positioned deliberately; exact Idea IDs
   asserted in each mode's observation structure. Empty views fail.

2. **Exact aggregation:** Preconditions asserted; exact statuses. No permissive
   branches. Covers REAL, PARTIAL, UNSUPPORTED, UNKNOWN, malformed.

3. **Real detachment sensitivity:** Retained nested observation; shallow copy
   fails the assertion. Restored in finally. No source-text inspection.

4. **Exact restart:** Fresh process reloads via production; verifies nursery
   confirmed status persists and composition structure is deterministic.

5. **State:** Content-level comparison (words, status, position, all Viewer fields).

6. **Sibling failures:** Both outcomes asserted. Report failure bounded.

## Exact Identity

- **Branch:** `gdp-phase7-r71-composition`
- **Head:** [to be recorded after final commit]
- **Tree:** [to be recorded after final commit]
- **Base:** `efd68bf5ef702dcb5a59aa246ed4397c0c0a133c` (R6.5 production)
- **Note:** Intermediate packet identities (26ec9229, db62e2b) are superseded;
  the frozen head below is authoritative.

## Objective Identity (Preserved)

R7.1 is the first Phase-7 implementation circuit, covering the **Perspectives**
stream only. Workshop (7.1) and Connected World (7.3) objectives remain
unimplemented.

## Implementation

**`compose_views(program, specs)`** in `form/dell_matrix/perspective_views.py`:
- Validates container type before interpreting emptiness
- Validates mode-relevant Viewer fields
- Routes through existing `see_as`; encloses all failures
- Detached components; attributed report; no truth merging
- Trusted local query only

## Proof (48/48)

- Populated: exact IDs in observation structures, all modes
- Aggregation: exact outcomes with preconditions
- Grants: rejected
- Malformed: containers, specs, poses, modes bounded
- Detached: real sensitivity (shallow fails)
- No truth merging: separate components
- State: content-level
- Siblings: both outcomes
- Copying/report failures: bounded, no leak
- Restart: fresh process, deterministic
- Sensitivity: aggregation weakened → diverges

## Verification

- Targeted: 48/48
- `--twice`: 112/112 GREEN
- `--order rev`: 112/112 GREEN
- Exact-head CI: [pending]

## Delta-20

All 20 categories reconciled. See `R71_DELTA20.md`.

## Costs

- 1 function in existing module
- 1 test file (48 checks)
- 1 README row
- Zero R6.1–R6.5 changes

---

**END OF R7.1 ADMISSION PACKET (FINISHED CANDIDATE)**
