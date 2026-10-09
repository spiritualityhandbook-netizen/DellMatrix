# R6.5 COMPLETION PACKET — Separation Enforcement (AMEND)

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C)
**AMEND Directive:** GDP_PHASE_6_R65_COMPLETE_REAL_SEPARATION_CIRCUIT (MODE=C)
**Authorization:** GDP_R65_AUTHORIZATION_RECONCILIATION (2026-10-09 16:17 CDT)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Exact Identity

- **Branch:** `gdp-phase6-r65-separation`
- **Base:** `0ceb3113beb8ce93e6bca422b9bddad12984feac` (R6.4 MERGED)
- **Base tree:** `7ab8c67b1a4ba742fb971d7039ac5b3755366cd5`
- **Commits:**
  - `40574e4`: R6.5 separation enforcement (BIMO intersection, sovereignty
    gate, persona assertion, walking skeleton 21/21)
  - `9d46d9b`: Register separation test in regress runner
  - `[auth]`: R6.5 authorization record
  - `[research]`: Research dispositions and Delta-20 mapping

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

## Sensitivities

- Disable `effective_capabilities` intersection (use union) →
  `r65 bimo: sensitivity` fails (proves intersection is load-bearing).
- Modify `dispatch` to consult `persona_slots` →
  `r65 skeleton: persona change` tests would fail (proves separation).
- Remove sovereignty check →
  `r65 sovereignty: bulk without token rejected` fails.

## Research

See `R65_RESEARCH_DELTA20.md`:
- Capability-based security: ADAPT
- Object-capability model: ADAPT
- View-model separation (CQRS): ADAPT
- Human-in-the-loop: ADAPT
- Unix setuid/sudo: REJECT

## Delta-20

7 applicable categories, all with executed negative controls.
Categories 8-20 reserved; no additional R6.5 falsifiers identified.
See `R65_RESEARCH_DELTA20.md` for the full mapping.

## Verification (AMEND)

- `python3 -m form.regress --twice`: **111/111 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **111/111 GREEN**
- R6.5 separation: **25/25**
- Exact-head CI: [pending push]

## Costs

- 3 new methods (no new modules, no new authorities)
- 1 new test file (21 checks)
- 4 documentation files
- Zero changes to R6.1–R6.4 runtime behavior (additive only)

## Limits

- Single-host enforcement (per R6.4; no distributed).
- Sovereignty token validation is format/owner check; the trusted host
  is responsible for issuance.
- Does not cover UI/UX, distributed systems, or Phase-7.
- Scanning: EVALUATION_UNAVAILABLE (Copilot quota 402), unchanged.

## Authorization

- **Implementation:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C),
  2026-10-09 15:10 CDT.
- **Reconciliation:** GDP_R65_AUTHORIZATION_RECONCILIATION, 2026-10-09 16:17 CDT.
- **Record:** `R65_AUTHORIZATION.md`; ledger § "R6.5 AUTHORIZATION".

---

**END OF R6.5 COMPLETION PACKET (CANDIDATE)**
