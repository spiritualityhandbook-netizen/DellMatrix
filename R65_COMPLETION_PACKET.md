# R6.5 COMPLETION PACKET — Separation Enforcement

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C)
**Authorization:** GDP_R65_AUTHORIZATION_RECONCILIATION (2026-10-09 16:17 CDT)
**Date:** 2026-10-09
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Exact Identity

- **Branch:** `gdp-phase6-r65-separation`
- **Base:** `0ceb3113beb8ce93e6bca422b9bddad12984fe4ac` (R6.4 MERGED)
- **Base tree:** `7ab8c67b1a4ba742fb971d7039ac5b3755366cd5`
- **Commits:**
  - `40574e4`: R6.5 separation enforcement (BIMO intersection, sovereignty
    gate, persona assertion, walking skeleton 21/21)
  - `9d46d9b`: Register separation test in regress runner
  - `[auth]`: R6.5 authorization record
  - `[research]`: Research dispositions and Delta-20 mapping

## Objective → Owner → Evidence Map

| # | Objective | Owner (R6.1–R6.4) | Evidence |
|---|-----------|-------------------|----------|
| 6.5.1 | PERSONA ≠ PERMISSION | `agent_coordinator.py` (R6.4) | `r65 skeleton: persona change does not grant authority`; `persona change does not bypass denial`; `_assert_persona_authority_separation` |
| 6.5.2 | BIMO = enforced capability | `personas.py` + `acceptance_policy.py` (R6.1) | `BIMOBody.effective_capabilities` (intersection); `r65 bimo: effective = intersection`; sensitivity (union would be wrong) |
| 6.5.3 | PERSPECTIVE ≠ TRUTH | `perspective_views.py` + coordinator snapshot (R6.4) | `r65 skeleton: view mutation does not touch canonical`; `views preserve canonical content` |
| 6.5.4 | Behavior ≠ authority | `agent_authority.py` (R6.2) + coordinator (R6.4) | `r65 skeleton: unauthorized confirm denies` (no grant = deny) |
| 6.5.5 | Human sovereignty | `acceptance_policy.py` (R6.1) | `HostCoordinator._check_sovereignty`; `r65 sovereignty: bulk without token rejected`; `r65 skeleton: revocation before execution denies` |

## Findings

**No defects found in R6.1–R6.4.** The separation boundaries were
architecturally present; R6.5 adds explicit runtime enforcement and
proofs.

**Gaps closed:**
1. BIMO `fuse()` returned descriptive abilities with no enforced
   capability computation → added `effective_capabilities` (intersection).
2. No explicit runtime assertion of PERSONA ≠ PERMISSION → added
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

## Verification

- `python3 -m form.regress --twice`: **111/111 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **111/111 GREEN**
- R6.5 separation: **21/21**
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
