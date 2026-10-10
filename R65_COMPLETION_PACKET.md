# R6.5 COMPLETION PACKET — Separation Enforcement (AMEND-3)

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C)
**AMEND Directive:** GDP_PHASE_6_R65_COMPLETE_REAL_SEPARATION_CIRCUIT (MODE=C)
**AMEND-2 Directive:** GDP_R65_FINISH_EXISTING_EXECUTABLE_PROOF (MODE=C)
**AMEND-3 Directive:** GDP_R65_FINISH_NONVACUOUS_EXISTING_CONTROLS (MODE=C)
**Authorization:** GDP_R65_AUTHORIZATION_RECONCILIATION (2026-10-09 16:17 CDT)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Exact Identity

- **Branch:** `gdp-phase6-r65-separation`
- **Head:** `86dd64d6d057ebb1b0712f145c6619e2215f5a91`
- **Tree:** `4b25f9ad7e602dd6ec69cd2b0a2d014f50346d14`
- **Base:** `0ceb3113beb8ce93e6bca422b9bddad12984feac` (R6.4 MERGED)
- **Base tree:** `7ab8c67b1a4ba742fb971d7039ac5b3755366cd5`

## Objective → Owner → Evidence Map (AMEND)

| # | Objective | Owner (R6.1–R6.4) | Evidence |
|---|-----------|-------------------|----------|
| 6.5.1 | PERSONA ≠ PERMISSION | `agent_coordinator.py` (R6.4) | Behavioral: matched requests before/after persona change; `r65 behavioral: denied with persona A/B`; canonical state unchanged |
| 6.5.2 | BIMO = descriptive, not authority | `personas.py` (presentation) + `acceptance_policy.py` (R6.1) | `effective_capabilities` labeled presentation-only; `r65 bimo: labels are not grant handles`; `r65 bimo: real grant succeeds` |
| 6.5.3 | PERSPECTIVE ≠ TRUTH | `perspective_views.py` + coordinator snapshot (R6.4) | `r65 skeleton: view mutation does not touch canonical`; `views preserve canonical content` |
| 6.5.4 | Behavior ≠ authority | `agent_authority.py` (R6.2) + coordinator (R6.4) | `r65 skeleton: unauthorized confirm denies`; `r65 sovereignty: agent cannot mint authority` |
| 6.5.5 | Human sovereignty | `acceptance_policy.py` (R6.1) via grant issuance | Every protected op requires host-issued grant; `r65 sovereignty: host-issued grant succeeds`; `r65 skeleton: revocation before execution denies` |

## AMEND Findings (All Addressed)

| Director Finding | Resolution |
|------------------|------------|
| Sovereignty gate disconnected | **Removed.** No dormant helper. Sovereignty via grant-issuance boundary. |
| Invented credentials accepted | **Removed.** No token format. Only host-issued grants. |
| BIMO computes labels, not authority | **Relabeled.** Presentation-only; proven labels ≠ grants. |
| Persona assertion proves nothing | **Removed.** Replaced with behavioral proofs. |
| Evidence incomplete | **Completed.** Fresh-process tests, old-grant rejection, reissue success, real sensitivity. |
| Delta-20 replaced categories | **Restored.** All 20 established categories mapped. |

## Findings

**No defects found in R6.1–R6.4.** The separation boundaries were
architecturally present; R6.5 proves them behaviorally and removes
unsupported parallel mechanisms.
   `_assert_persona_authority_separation`.
3. No sovereignty gate for bulk operations → added `_check_sovereignty`.

## Sensitivities (Real)

- Weaken `AcceptancePolicy.check` (specific decision) →
  `r65 sensitivity: weakened check diverges` passes (unauthorized now
  succeeds), proving the check is load-bearing. Restored in `finally`.
- The sensitivity patches the real production method, not a fabricated
  dispatch replacement. Observable divergence required.

## Research

See `R65_RESEARCH_DELTA20.md`:
- Capability-based security: ADAPT
- Object-capability model: ADAPT
- View-model separation (CQRS): ADAPT
- Human-in-the-loop: ADAPT
- Unix setuid/sudo: REJECT

## Delta-20

All 20 established categories mapped with bounded status and evidence.
See `R65_RESEARCH_DELTA20.md` for the full mapping.

## Verification (AMEND-3)

- `python3 -m form.regress --twice`: **111/111 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **111/111 GREEN**
- R6.5 separation: **52/52**
- Exact-head CI: [pending push]

## Costs

- 1 presentation utility (`effective_capabilities`, labeled non-enforcing)
- 1 new test file (34 checks) + 1 fixed child script
- 5 documentation files
- Zero changes to R6.1–R6.4 runtime behavior (additive only; AMEND removed
  the two non-production helpers)

## Limits

- Single-host enforcement (per R6.4; no distributed).
- Human sovereignty enforced via trusted-host grant issuance (no separate
  token mechanism).
- Does not cover UI/UX, distributed systems, or Phase-7.
- Scanning: EVALUATION_UNAVAILABLE (Copilot quota 402), unchanged.
- Performance: no measured baseline; changes are O(1)/O(n) on bounded
  inputs, no hot paths modified.

## Authorization

- **Implementation:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C),
  2026-10-09 15:10 CDT.
- **Reconciliation:** GDP_R65_AUTHORIZATION_RECONCILIATION, 2026-10-09 16:17 CDT.
- **Record:** `R65_AUTHORIZATION.md`; ledger § "R6.5 AUTHORIZATION".

---

**END OF R6.5 COMPLETION PACKET (CANDIDATE)**
