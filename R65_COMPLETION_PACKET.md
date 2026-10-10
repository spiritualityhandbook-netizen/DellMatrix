# R6.5 COMPLETION PACKET — Separation Enforcement (AMEND-5)

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C)
**AMEND Directive:** GDP_PHASE_6_R65_COMPLETE_REAL_SEPARATION_CIRCUIT (MODE=C)
**AMEND-2 Directive:** GDP_R65_FINISH_EXISTING_EXECUTABLE_PROOF (MODE=C)
**AMEND-3 Directive:** GDP_R65_FINISH_NONVACUOUS_EXISTING_CONTROLS (MODE=C)
**AMEND-4 Directive:** GDP_R65_COMPLETE_ASSERTIONS_WITH_CANONICAL_EVIDENCE (MODE=C)
**AMEND-5 Directive:** GDP_R65_CLOSE_REPORT_TO_CODE_DISAGREEMENT (MODE=C)
**Authorization:** GDP_R65_AUTHORIZATION_RECONCILIATION (2026-10-09 16:17 CDT)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Exact Identity

- **Branch:** `gdp-phase6-r65-separation`
- **Head:** `05c683b974c6c1bdba0962b22b70bfe63695d4ed`
- **Tree:** `6c839e13a53fc37372a648b85aaa4076bac8c290`
- **Base:** `0ceb3113beb8ce93e6bca422b9bddad12984feac` (R6.4 MERGED)
- **Base tree:** `7ab8c67b1a4ba742fb971d7039ac5b3755366cd5`

## Objective → Owner → Evidence Map

| # | Objective | Owner (R6.1–R6.4) | Evidence |
|---|-----------|-------------------|----------|
| 6.5.1 | PERSONA ≠ PERMISSION | `agent_coordinator.py` (R6.4) | Behavioral: matched requests before/after persona change; canonical state unchanged |
| 6.5.2 | BIMO = descriptive, not authority | `personas.py` (presentation) + `acceptance_policy.py` (R6.1) | `effective_capabilities` labeled presentation-only; labels ≠ grants proven |
| 6.5.3 | PERSPECTIVE ≠ TRUTH | `perspective_views.py` + coordinator snapshot (R6.4) | View mutation does not touch canonical; exact pid keys used |
| 6.5.4 | Behavior ≠ authority | `agent_authority.py` (R6.2) + coordinator (R6.4) | Unauthorized confirm denies; agent cannot mint authority |
| 6.5.5 | Human sovereignty | `acceptance_policy.py` (R6.1) via grant issuance | Every protected op requires host-issued grant |

## Sensitivity (Real, Executed)

Three independently prepared equivalent PENDING fixtures (unique owners).

**Before EACH attempt:**
- Assert `prop.status == "pending"` (exact, not heuristic)
- Assert `pid not in program.cube.session.plane.units` (exact absence)

**Normal/Restored denial:**
- Must deny for authority reasons
- After denial: assert `status=="pending"` AND `pid not in plane.units` again

**Weakened success:**
- After weakened `AcceptancePolicy.check`: assert `status=="confirmed"`
- Assert exact unit presence via `plane.units[pid]`
- Assert exact content match

**Isolation:** Every case uses a unique UUID owner. Cleanup via canonical
state paths in `finally`.

## Audit Preservation (Executed)

- Capture the SPECIFIC committed audit record (request_id="r65-restart-confirm",
  result="committed") before save.
- Require nonempty expectations — empty cannot satisfy the proof.
- Do NOT swallow capture errors.
- Both children compare: request_id, subject, target, AND result.
- Negative controls: empty expectations fail; changed result fails.

## Restart (Real, Two Children)

**Child 1 (mutating probe):** Fresh OS process. Denies old grant on same
target. Reissues and confirms. Saves state.

**Child 2 (verification-only):** Separate OS process. No issuance or mutation.
Loads and compares: exact Idea, committed proposal, audit evidence.

Both require `returncode==0` and structured assertions.

## Delta-20

All 20 established categories mapped. See `R65_RESEARCH_DELTA20.md`.

**Note:** Research records ADAPT/REJECT dispositions. Primary-source
citation verification was limited; do not overstate as completed
primary-source research.

## Verification

- `python3 form/mandell/r65_separation_test.py`: **72/72**
- `python3 -m form.regress --twice`: **111/111 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **111/111 GREEN**
- Exact-head CI: [pending push]

## Costs

- 1 presentation utility (`effective_capabilities`, labeled non-enforcing)
- 1 test file (72 checks) + 2 child scripts
- Documentation files
- Zero changes to R6.1–R6.4 runtime behavior (additive only)

## Limits

- Single-host enforcement (per R6.4; no distributed).
- Human sovereignty enforced via trusted-host grant issuance.
- Does not cover UI/UX, distributed systems, or Phase-7.
- Scanning: EVALUATION_UNAVAILABLE (Copilot quota 402), unchanged.
- Performance: no measured baseline; changes are O(1)/O(n) on bounded inputs.

## Authorization

- **Implementation:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C),
  2026-10-09 15:10 CDT.
- **Reconciliation:** GDP_R65_AUTHORIZATION_RECONCILIATION, 2026-10-09 16:17 CDT.
- **AMEND-5:** GDP_R65_CLOSE_REPORT_TO_CODE_DISAGREEMENT (MODE=C).
- **Record:** `R65_AUTHORIZATION.md`; ledger § "R6.5 AUTHORIZATION".

---

**END OF R6.5 COMPLETION PACKET (CANDIDATE)**
