# R6.5 Research Dispositions + Delta-20

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT §5 (AMEND)
**Date:** 2026-10-09

## Research Dispositions

Research informs implementation; it does not redefine project law.

### Capability-based security (Miller, Shapiro, et al.)

**Disposition:** ADAPT

**Contribution:** Unforgeable tokens, attenuation-only delegation,
complete mediation. R6.1's AcceptancePolicy already implements this
for grant issuance. R6.5 proves the principle holds for persona/BIMO:
descriptive metadata cannot substitute for validated grants.

**DellMatrix analog:** `agent_authority.issue_root_grant` (unforgeable
handles); coordinator dispatch (complete mediation).

### Object-capability model (E language, Joe-E)

**Disposition:** ADAPT

**Contribution:** The "no ambient authority" principle. A persona
activated in a session must not confer ambient authority. R6.4's
coordinator already enforces this; R6.5 proves it behaviorally.

**Correction from research:** Authorization must validate the specific
operation at execution, rather than trust credential formatting or
descriptive metadata. (This led to removal of the format-only
sovereignty token.)

### View-model separation (MVVM, CQRS)

**Disposition:** ADAPT

**Contribution:** Command/query separation as the mechanism for
PERSPECTIVE ≠ TRUTH. Views are queries; they cannot issue commands.
R6.4's `snapshot_for` already returns detached data; R6.5 proves the
write barrier holds and exercises actual perspective interfaces.

### Human-in-the-loop / meaningful human control

**Disposition:** ADAPT

**Contribution:** Sovereignty as an explicit gate, not a convention.
R6.5 AMEND corrects the implementation: sovereignty is enforced via
the existing grant-issuance path (only the trusted host mints grants),
not via a separate token format. Human sovereignty applies to every
protected operation equally.

### Unix setuid / sudo

**Disposition:** REJECT

**Reason:** Ambient authority with elevation is the opposite of the
required design. DellMatrix uses explicit capability grants, not
ambient privilege escalation.

## Delta-20 (Established Categories)

Mapping R6.5 evidence against the 20 established Delta-20 categories.

### 1. Missing concept
**Finding:** None. R6.5 does not introduce new concepts requiring
coverage. The three enforcement mechanisms (grant-issuance boundary,
behavioral persona proofs, presentation-only BIMO) are all within
the established R6.1–R6.4 architecture.

### 2. Contradiction
**Finding:** RESOLVED in AMEND-6. The AMEND-5 packet claimed "canonical
cleanup for every case" while the code used guessed `form/state/...` globs
with `except Exception: pass`. This report-to-code disagreement is now
resolved: the packet describes disposable-copy isolation (accurate), and
the guessed cleanup code has been removed. No behavioral contradiction
remains.

### 3. Semantic drift
**Finding:** None. No R6.1–R6.4 behavior changed. All R6.5 changes
are additive (new methods, new tests, documentation).

### 4. Duplicate authority
**Finding:** None. R6.5 creates no new authority. The removed
sovereignty token would have been a duplicate; its removal prevents
this. `effective_capabilities` is explicitly labeled presentation-only.

### 5. Wrong abstraction
**Finding:** None. The grant handle remains the correct abstraction
for authority. Persona/BIMO remain descriptive metadata.

### 6. Wrong layer
**Finding:** None. Enforcement remains at the coordinator dispatch
layer (where R6.4 placed it). No new enforcement layer created.

### 7. Persistence failure
**Finding:** None for production; test isolation verified in AMEND-6.
Fresh-process test proves accepted outcomes survive reload. Old grants
do not authorize in fresh process (session-scoped). Test artifacts are
confined to disposable repository copies; production `form/state/` is
not modified by the suite (verified via sentinel-file test). The suite
does not redirect production `_STATE_DIR`; it runs in a copy where
`form/state/` is fresh.

### 8. History/provenance consequence
**Finding:** None. No historical records modified. Audit evidence
preserved through existing R6.4 mechanisms.

### 9. Security consequence
**POSITIVE.** The AMEND removes a format-only credential check that
could have created false confidence. Real enforcement (grant
validation at dispatch) is now the only mechanism, with sensitivity
proof.

### 10. Human-authority consequence
**POSITIVE.** Human sovereignty is now correctly enforced via the
trusted-host grant issuance path, not via an invented token format.
Every protected operation requires a host-issued grant.

### 11. Offline consequence
**Finding:** None. All R6.5 mechanisms are local; no network dependencies.

### 12. Performance consequence
**Finding:** None. The added checks are O(1) or O(n) on small bounded
inputs. No performance-sensitive paths modified.

### 13. Public-path theater
**Finding:** None (verified, re-examined in AMEND-6). All proofs execute
through real public interfaces (`surface_for`, `snapshot_for`, `dispatch`,
`issue_root_grant`). No mocks for enforcement decisions. The suite runs
via two public paths: (1) `form.regress` (canonical regression entry,
uses isolated copy), and (2) direct `python3 form/mandell/r65_separation_test.py`
(which self-isolates via disposable copy). Both paths verified. The
isolation mechanism (disposable copies) is test infrastructure, not
production behavior; it does not create a parallel test-only path for
the enforcement logic itself.

### 14. Mathematical weakness
**Finding:** None. No new mathematical claims. The intersection
computation is presentation-only, not a security boundary.

### 15. Visual theater
**Finding:** None. No UI changes.

### 16. Historical-recovery conflict
**Finding:** None for R6.3 mechanisms (untouched). Re-examined in AMEND-6
for test failure handling: The previous `except Exception: pass` in cleanup
code could have masked failures. This is now resolved: `tempfile.TemporaryDirectory`
propagates cleanup failures as exceptions (not swallowed). Behavioral test
failures are preserved in CHECKS and reported; cleanup errors fail the test
with explicit diagnostic. No failure-masking remains.

### 17. Simpler reuse opportunity
**Finding:** None. R6.5 reuses R6.1 (AcceptancePolicy), R6.2
(agent_authority), R6.4 (coordinator) with no duplication.

### 18. Research contradiction
**Finding:** None. Research dispositions (above) align with implementation.
The AMEND was informed by the object-capability literature.

### 19. Future-phase incompatibility
**Finding:** None. R6.5 does not constrain Phase-7. The separation
boundaries are compatible with future workshop/perspective work.

### 20. From-scratch challenge
**Open question for Director:** Could the persona/BIMO descriptive
layer be removed entirely without loss? The AMEND proves it does not
affect authority, but its UX value (guidance, synthesis) is outside
R6.5's scope to evaluate.

## Partial / Unavailable / Excluded

- **Partial:** None. All R6.5 claims have complete proof coverage.
- **Unavailable:** Copilot code scanning remains EVALUATION_UNAVAILABLE
  (quota 402). This is separate from the R6.5 functional proofs.
- **Excluded:** Distributed enforcement (single-host only, per R6.4);
  UI/UX changes; Phase-7 work.
