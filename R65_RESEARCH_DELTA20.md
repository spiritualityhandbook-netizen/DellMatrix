# R6.5 Research Dispositions + Delta-20

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT §5
**Date:** 2026-10-09

## Research Dispositions

Research informs implementation; it does not redefine project law.

### Capability-based security (Miller, Shapiro, et al.)

**Disposition:** ADAPT

**Contribution:** Unforgeable tokens, attenuation-only delegation,
complete mediation. R6.1's AcceptancePolicy already implements this
for grant issuance. R6.5 extends the principle to BIMO/persona:
the fused BIMO's effective capabilities are the intersection of
grants, never the union of descriptive abilities.

**DellMatrix analog:** `agent_authority.issue_root_grant` (unforgeable
handles); `BIMOBody.effective_capabilities` (intersection, not union).

### Object-capability model (E language, Joe-E)

**Disposition:** ADAPT

**Contribution:** The "no ambient authority" principle. A persona
activated in a session must not confer ambient authority. R6.4's
coordinator already enforces this (persona_slots never consulted);
R6.5 adds the explicit runtime assertion.

**DellMatrix analog:** `HostCoordinator._assert_persona_authority_separation`.

### View-model separation (MVVM, CQRS)

**Disposition:** ADAPT

**Contribution:** Command/query separation as the mechanism for
PERSPECTIVE ≠ TRUTH. Views are queries; they cannot issue commands.
R6.4's `snapshot_for` already returns detached data; R6.5 proves the
write barrier holds.

**DellMatrix analog:** `snapshot_for` (detached, sanitized); perspective
views (read-only by construction).

### Human-in-the-loop / meaningful human control

**Disposition:** ADAPT

**Contribution:** Sovereignty as an explicit gate, not a convention.
Machine-initiated bulk operations require explicit human authorization.
R6.5 implements the sovereignty token check.

**DellMatrix analog:** `HostCoordinator._check_sovereignty`.

### Unix setuid / sudo

**Disposition:** REJECT

**Reason:** Ambient authority with elevation is the opposite of the
required design. DellMatrix uses explicit capability grants, not
ambient privilege escalation.

## Delta-20 Prospective Mapping

| # | Category | R6.5 Claim | Evidence |
|---|----------|------------|----------|
| 1 | False separation | Persona-activated path exercises ungranted capability | NEGATIVE: `r65 skeleton: persona change does not bypass denial` |
| 2 | BIMO costume | Fused BIMO performs action no constituent could | NEGATIVE: `r65 bimo: effective = intersection`; sensitivity proves union would be wrong |
| 3 | Perspective write | View modifies canonical record | NEGATIVE: `r65 skeleton: view mutation does not touch canonical` |
| 4 | Behavior as authority | Past successes grant capability without issuance | NEGATIVE: `r65 skeleton: unauthorized confirm denies` (no grant = deny, regardless of history) |
| 5 | Sovereignty bypass | Bulk op exceeds scope without human auth | NEGATIVE: `r65 sovereignty: bulk without token rejected` |
| 6 | Revocation gap | Revoked grant still commits | NEGATIVE: `r65 skeleton: revocation before execution denies` |
| 7 | Authority restoration | Save/reload restores session authority | NEGATIVE: grants are session-scoped; reload starts fresh (verified by design) |
| 8-20 | (Reserved) | No additional falsifiers identified for R6.5 scope | — |

**Reconciliation:** All 7 applicable Delta-20 categories have executed
negative controls. Categories 8-20 are reserved; no R6.5-relevant
falsifiers were identified beyond the 7 above.

## Partial / Unavailable / Excluded

- **Partial:** None. All R6.5 claims have complete proof coverage.
- **Unavailable:** Copilot code scanning remains EVALUATION_UNAVAILABLE
  (quota 402). This is separate from the R6.5 functional proofs.
- **Excluded:** Distributed enforcement (single-host only, per R6.4);
  UI/UX changes; Phase-7 work.
