# DELLMATRIX — ORIGINAL 72-ITEM DEVELOPMENT INVENTORY

Source date: November 3, 2026
Original audit baseline: 4df2246
Authority: ACE > DIRECTOR > UNI
Purpose: Transfer all 72 original objectives into Uni's accessible development records.
Transmitted: by the Director via Ace, 2026-11-04 (Director Addendum — Historical Objectives Reconciliation). Stored verbatim as received.

Classification: P0 = critical; P1 = significant; P2 = lower priority. C = confirmed issue or remaining boundary; E = enhancement requiring verification; I = investigation.

RULE: This is the original inventory. Do not assume an item remains incomplete. Reconcile every item against current main, Director rulings, and later merged repairs. Preserve original IDs.

---

## A. Open rulings and outstanding boundaries (01–09)

**01. Finalize Studio browser acceptance on the current integrated revision**
P0 / C
Source: PR #258; director-reports/DIRECTOR_REPORT_STUDIO_BROWSER_ACCEPTANCE.md
Acceptance: Inspect the final integrated revision; demonstrate 16/16 genuine browser acceptance, preserve the artifact, and state the exact certified boundary.

**02. Reconcile merged Core I gate with the Director INDEX and archival status**
P0 / C
Source: director-reports/INDEX.md
Acceptance: Verify PR #259 and update its historical disposition without changing the established runtime evidence.

**03. Independently reproduce unresolved DAF-09 session-escape process cleanup**
P0 / C
Source: form/regress.py
Acceptance: Independently test Linux process-tree escape, termination, and identity-safe signaling. Preserve the unresolved 19/22 discrepancy unless actually explained.

**04. Close or precisely retain identical-label/unit-ID ambiguity in Growth lenses**
P1 / C
Source: form/dell_matrix/view_rooms.py
Acceptance: Test two distinct units with identical labels; demonstrate independent identity and truthful stages, or document the remaining limitation.

**05. Repair Dell 37 REPL failure visibility without changing Nurture semantics**
P1 / C
Source: form/repl.py
Acceptance: A real REPL invocation must visibly report Dell 37 failure, including chained execution and restart cases where applicable.

**06. Review English Intent.args as a separate end-to-end contract**
P1 / C
Source: form/mandell/translate.py
Acceptance: Trace English argument extraction through parsing and execution. Distinguish Intent.args from SeedAtom.args; classify actual losses.

**07. Dispose of remaining per-scope admission and registry certification requests**
P1 / C
Source: director-reports/DIRECTOR_REPORT_STEP14_ADMISSION.md
Acceptance: Resolve A2/A3 and 100-Dell classification requests within proven scopes. Preserve existing DAF-09 and whole-program certification restrictions.

**08. Preserve CI-only #233 and long-lived certification artifacts accurately**
P1 / C
Source: director-reports/responses/DIRECTOR_RULING_DIR-CERT-2026-11-02.md
Acceptance: Keep PR #233 under its existing DO NOT MERGE ruling. Preserve durable evidence, provenance, and artifact-expiration information.

**09. Harden the existing Director–Uni next-best circuit handoff**
P1 / E
Source: director-reports/workflow/WORKFLOW.md
Acceptance: Maintain deterministic work selection, dependency ordering, stale-head handling, and the established review-ready circuit limits.

---

## B. Mandell grammar and execution (10–27)

**10. Stress the existing Seed grammar and error precedence**
P1 / I
Source: form/mandell/seed.py
Acceptance: Test nested delimiters, escaped Unicode, malformed terms, chainlinks, and ManifestSet. Rejected input must not mutate business state.

**11. Reconcile English create and other direct REPL handlers with canonical Mandell behavior**
P1 / I
Source: form/repl.py
Acceptance: Compare equivalent English/REPL and typed Mandell requests. Prove actual semantic differences before changing routing.

**12. Deepen reachability for already-supported English actions only**
P2 / E
Source: form/mandell/semantic_router.py
Acceptance: Measure English coverage against executable operations. Unsupported requests must return UNKNOWN rather than fabricated behavior.

**13. Audit the 17 registered typed-signature error and coercion contracts**
P1 / I
Source: form/mandell/signatures.py
Acceptance: Test required, unknown, invalid, and conflicting roles across typed, legacy, and chained execution. Do not expand signature count without authorization.

**14. Strengthen Core I single/chain/intercept/live refusal parity**
P1 / E
Source: form/mandell/executor.py
Acceptance: Test mixed valid Core II and refused Core I operations through the real REPL, preserving valid neighboring operations and mutation boundaries.

**15. Challenge Core II unsupported-role control-head short circuits**
P1 / E
Source: form/mandell/chain_exec.py
Acceptance: Invalid typed control heads must not execute their bodies. Preserve first-error provenance and accurate receipts.

**16. Reconcile legacy flow executor with canonical chain ownership**
P2 / I
Source: form/mandell/flow_executor.py
Acceptance: Identify real callers, compare behavior, and avoid creating a second authoritative executor.

**17. Remove or relabel literal Show placeholder output where surfaced**
P2 / I
Source: form/mandell/executor_leaf.py
Acceptance: Probe bare 09[Show]; distinguish a reserved rendering marker from a genuinely rendered result.

**18. Audit message-only Dell descriptions for truthful operations**
P2 / I
Source: form/mandell/DELL_PROOF_CARDS.md
Acceptance: Verify 17[Shadow], 43[Fallback], and comparable operators against actual effects. Correct misleading claims without inventing behavior.

**19. Preserve first-failure provenance through mixed chain receipts**
P1 / E
Source: form/mandell/chain_exec.py
Acceptance: Failed, successful, and skipped atoms must retain the original failure and accurate partial-result accounting.

**20. Challenge Branch/Parallel/Sequence/Join reported guarantees**
P1 / I
Source: form/mandell/chain_exec.py
Acceptance: Confirm execution order, failure propagation, and Join verdicts. Do not claim true concurrency if execution is sequential.

**21. Stress Until/While/ForEach bounds and nested control inheritance**
P1 / I
Source: form/mandell/chain_exec.py
Acceptance: Verify iteration limits, early failure, zero iterations, nested skip handling, and persistence.

**22. Reverify Try/Catch error consumption and same-frame reuse**
P1 / E
Source: form/mandell/spectrum_ops.py
Acceptance: Catch consumes one pending error once. Repeated Catch must not resurrect an old error; historical evidence remains available.

**23. Challenge Commit/Revert exact state and side-effect boundaries**
P1 / I
Source: form/mandell/spectrum_ops.py
Acceptance: Verify rollback, post-commit behavior, and injected failures. Do not claim atomic staging beyond actual implementation.

**24. Stress Diff/Set missing-vs-None and baseline handling**
P1 / E
Source: form/mandell/spectrum_ops.py
Acceptance: Distinguish absent keys from stored null values, retain deterministic baselines, and report changed keys accurately.

**25. Protect Define/Alias/Compose against failed-run persistence**
P1 / E
Source: form/mandell/spectrum_ops.py
Acceptance: A failed definition must not publish a usable name. Successful definitions must survive save/reload.

**26. Stress per-member ManifestSet and typed chainlink transport**
P1 / E
Source: form/mandell/seed.py
Acceptance: A failing ManifestSet member must not automatically invalidate independent valid members. Verify exact per-atom arguments and receipts.

**27. Recheck Guard/Assert failure propagation across control frames**
P2 / E
Source: form/mandell/chain_exec.py
Acceptance: Distinguish ordinary atom failures from Guard/Assert behavior and reflect both correctly in frame verdicts and continuation.

---

## C. Persistence, recovery, and ownership (28–36)

**28. Audit Program/Nursery pair-atomic save and fresh-process load**
P0 / E
Source: form/persist_rest.py
Acceptance: Inject crashes between staged writes and renames. Verify that recovery exposes coherent generations, not an invalid hybrid.

**29. Stress checkpoint sealing, rollback, and directory-sync failure**
P1 / E
Source: form/mandell/checkpoint_generation.py
Acceptance: Verify sealed hashes across rollback, restart, failed fsync, missing generations, and retry.

**30. Challenge Exchange journaled import/recovery and receipt disposal**
P0 / E
Source: form/dell_matrix/exchange.py
Acceptance: Inject failures into journal writing, cleanup, compensation, saving, and loading. Partial state must never be reported as fully durable.

**31. Check Nursery optimistic concurrency and duplicate confirmation**
P1 / E
Source: form/dell_matrix/nursery.py
Acceptance: Concurrent stale instances must not silently lose accepted updates. Repeated confirm/reject actions must remain deterministic.

**32. Validate semantic-graph journals against derived Program effects**
P1 / E
Source: form/mandell/semantic_graph.py
Acceptance: Inject crashes between graph and derived-state writes. Invalid journals must remain preserved and fail closed.

**33. Verify supersession crash and acceptance lineage across restart**
P1 / E
Source: form/mandell/supersession.py
Acceptance: A predecessor remains authoritative until its valid successor commits. Recovery must restore coherent revision history.

**34. Test owner namespace collision and foreign-state rejection**
P1 / E
Source: form/persist.py
Acceptance: Normalized owner-name collisions and cross-owner restore attempts must not expose or overwrite another owner's state.

**35. Recheck atomic-write orphan-temp and rollback cleanup bounds**
P2 / E
Source: form/dell_matrix/atomic_write.py
Acceptance: Inject failures at write, fsync, and replacement boundaries. Temporary artifacts must never be mistaken for canonical data.

**36. Roundtrip every existing persistent envelope under corrupt/unknown versions**
P1 / I
Source: form/persist_core_ii.py
Acceptance: Supported versions roundtrip correctly. Malformed or unknown versions refuse without partial activation.

---

## D. Canonical Ideas, knowledge, intelligence, and DuoBeta (37–54)

**37. Plan and verify the existing Plane-to-Idea bridge (Track D)**
P1 / E
Source: form/mandell/idea.py
Acceptance: Trace Plane units into canonical Idea identity, properties, provenance, and persistence using the minimum required integration.

**38. Reconcile Idea and semantic-graph node identity throughout lifecycle**
P1 / I
Source: form/mandell/semantic_graph.py
Acceptance: Verify no unintended duplicate or orphan identities across rename, creation, save/reload, supersession, and graph references.

**39. Prove nested Idea parent/child relationships and promotion invariants**
P2 / I
Source: form/mandell/idea.py
Acceptance: Verify real parent-child links, preserved child identity and lifecycle, promotion, and correct upward references without a second containment authority.

**40. Enforce active/faded/superseded participation across all consumers**
P1 / E
Source: form/dell_matrix/canonical_lifecycle.py
Acceptance: Inactive or superseded ideas do not participate in ordinary resonance. Explicit historical queries remain possible.

**41. Reconcile GrowthForce label identity with stable Plane unit IDs**
P1 / C
Source: form/dell_matrix/forces.py
Acceptance: Preserve idea_full compatibility and distinguish identical-label units without transferring a sibling's Growth stage.

**42. Stress knowledge selection, scope, lineage and dependencies**
P1 / E
Source: form/mandell/knowledge_selector.py
Acceptance: Selection must exclude knowledge that is out of scope, inactive, unresolved, or invalid through cyclic dependencies.

**43. Trace cause/depend/provenance explanations to real graph evidence**
P2 / E
Source: form/mandell/knowledge_influence.py
Acceptance: Every why_used and why_not_used explanation must reference resolvable evidence, without unsupported causal claims.

**44. Test resonance/harmony-to-Nursery proposals at the human gate**
P2 / I
Source: form/dell_matrix/resonance.py
Acceptance: Generated candidates remain pending until human approval. Rejected candidates cannot alter accepted ideas.

**45. Preserve epistemic source/status through views and spatial consumers**
P1 / E
Source: form/dell_matrix/perspective_views.py
Acceptance: UNKNOWN must not become zero. Alternative perspectives must preserve the actual source and epistemic status.

**46. Verify dock COMPREHEND/relate_field through existing policy and Nursery**
P1 / E
Source: form/dell_matrix/inference_dock.py
Acceptance: Trace field snapshots through proposals, acceptance gates, and persistence. Model output alone cannot mutate accepted state.

**47. Stress stale field-snapshot and agent reconnect boundaries**
P1 / E
Source: form/dell_matrix/agent_coordinator.py
Acceptance: Validate changes occurring after a snapshot; retries and reconnects must preserve decision authority.

**48. Exercise agent host-bound idempotency, retries and conflicting envelopes**
P1 / E
Source: form/dell_matrix/agent_coordinator.py
Acceptance: Duplicate request identifiers with conflicting payloads must refuse. Prevent duplicate accepted mutations and protected-value disclosure.

**49. Challenge AcceptancePolicy delegation, expiry and revocation chains**
P0 / E
Source: form/dell_matrix/acceptance_policy.py
Acceptance: Revoked approval must invalidate dependent grants across restart and retry. AI models cannot create root human authority.

**50. Prove runtime DirectorSession remains recommendations-only**
P1 / E
Source: form/dell_matrix/director_session.py
Acceptance: Recommendations and directives never directly confirm proposals. Canonical AcceptancePolicy remains authoritative.

**51. Reconcile DuoBeta outcome evidence and learning ledger persistence**
P1 / E
Source: form/mandell/duobeta_learn.py
Acceptance: The Observe → Propose → Gate → Apply → Save/Reload chain produces one bounded durable learning effect.

**52. Test learned-score saturation and opt-out reversibility**
P2 / E
Source: form/mandell/duobeta_learn.py
Acceptance: Turning learning influence OFF restores baseline ranking. Learned scores remain bounded and cannot override hard truth gates.

**53. Harden optional provider errors, prompt/output validation and protected values**
P0 / E
Source: form/dell_matrix/inference_dock.py
Acceptance: Hostile or malformed provider outputs remain untrusted data. Ownership, role, and approval identifiers must not leak through errors.

**54. Keep the selfgrow auxiliary ledger explicitly isolated from canonical state**
P2 / I
Source: form/duobeta/selfgrow.py
Acceptance: Auxiliary learning records cannot override sealed or accepted canonical state. Errors must be explicitly classified.

---

## E. Studio, browsers, and spatial functionality (55–63)

**55. Trigger real-browser acceptance for relevant Form runtime changes**
P1 / E
Source: gui/browser_acceptance.py; PR #258
Acceptance: Browser workflows cover GUI changes and relevant execution/API dependencies, preventing dispatch-only test blind spots.

**56. Add browser refusal, PARTIAL and skipped-atom acceptance paths**
P1 / E
Source: gui/static/app.js
Acceptance: Genuine Chromium execution must display failed, partial, and skipped results truthfully.

**57. Drive existing Growth and Console tabs in browser acceptance**
P1 / E
Source: gui/static/app.js
Acceptance: Verify actual browser input, DOM transitions, state changes, and absence of console exceptions.

**58. Regression-test Studio Host/Origin/token and malformed HTTP boundaries**
P0 / E
Source: gui/server.py
Acceptance: Preserve implicit-port Origin refusal, HTTP 403 with zero mutation, request size limits, and legitimate same-origin requests.

**59. Test Studio state refresh, stale owner state and receipt reconstruction**
P1 / I
Source: gui/server.py
Acceptance: GET/POST responses, subsequent refreshes, and reopened sessions must agree with canonical owner state and show no phantom status.

**60. Prove identical executable semantics across GUI, API, REPL and Python path**
P1 / E
Source: form/gui_api_test.py
Acceptance: The same Seed should yield equivalent semantic results, errors, and state mutations through every supported entry point.

**61. Improve existing Studio keyboard, focus, and constrained viewport behavior**
P2 / E
Source: gui/static/index.html
Acceptance: Existing controls must work with keyboard navigation and narrow viewports. No unrelated new interface family is authorized.

**62. Reconcile offline visual snapshot with canonical state and clear non-live label**
P2 / E
Source: form/dell_matrix/visual.py
Acceptance: Exported HTML must truthfully identify itself as a snapshot, never falsely suggesting that static visuals execute live commands.

**63. Stress current 2D spatial placement, rendering, and restore invariants**
P2 / I
Source: form/dell_matrix/spatial_authority.py
Acceptance: Validate finite coordinates, reserved origin, collision behavior, and consistent positions after persistence and reload.

---

## F. Documentation, architecture, CI, performance, and workflow (64–72)

**64. Refresh stale in-use docs and README suite-count claims**
P1 / C
Source: README.md
Acceptance: Update obsolete suite counts and claims using verified current-main evidence. Preserve historical counts as history.

**65. Protect Form as source of truth against frozen JS/preform namespace drift**
P2 / E
Source: form/CORE_SCOPE.md
Acceptance: Verify that live Form does not import frozen src/ or preform/ authorities or confuse historical Dell names with live names.

**66. Deepen changed-file lint and Python-version compatibility checks**
P2 / E
Source: .github/workflows/python-package.yml
Acceptance: Introduce selected high-confidence lint and compatibility gates without weakening the existing CI.

**67. Harden GitHub workflow permissions and pin third-party action revisions**
P1 / E
Source: .github/workflows/form-smoke.yml
Acceptance: Apply least-privilege permissions, reviewed action revisions, safe pull-request contexts, and protection of secrets from untrusted code.

**68. Reconcile regression discovery, suite registration, and mutation detection**
P1 / E
Source: form/regress.py
Acceptance: Meaningful suites cannot disappear silently from regression. Failures must identify the actual assertion or oracle.

**69. Create repeatable low-memory and large-state performance baselines**
P2 / E
Source: form/mandell/p2_perf_baseline.py
Acceptance: Measure long Seeds, large Plane/graph states, persistence, and CI under defined memory/CPU budgets. Compare identical workloads.

**70. Incrementally reduce oversized live-module coupling without behavior change**
P2 / E
Source: form/repl.py
Acceptance: Refactor one bounded boundary at a time with characterization tests proving unchanged behavior and canonical callers.

**71. End-to-end protected-value canaries across every outward evidence surface**
P1 / E
Source: form/mandell/redaction.py
Acceptance: Verify secret-like values do not leak through new errors, receipts, logs, or exports. Preserve the documented scope of existing seed echoes.

**72. Automate morning report reconciliation, staleness and next-best recommendations within workflow**
P1 / E
Source: director-reports/workflow/validate_packet.py
Acceptance: Compare the INDEX, PR heads, evidence, outstanding objectives, and Director rulings. Recommend only authorized next circuits; never self-certify.

---

## DIRECTOR INSTRUCTIONS — WHAT UNI MUST DO WITH THESE 72

1. Preserve all 72 IDs and titles in the historical objective register.
2. Compare each item against the current GitHub main branch and subsequent Director decisions.
3. Record COMPLETED, PARTIAL, OPEN, INVESTIGATION, BLOCKED, SUPERSEDED, or DECLINED as warranted by evidence.
4. Link completed objectives to the actual proving PR, test suite, and certification.
5. Add the previously transmitted future-vision objectives as separate entries, deduplicating genuine overlaps.
6. Add unresolved objectives established before or after this inventory that are not among these 72.
7. Produce one consolidated Master Objective Register with dependencies and authorization boundaries.
8. Preserve the existing TD-2 implementation directive and its stop condition.
9. Do not begin SUSX100,000 or implement newly discovered objectives without the applicable authorization.

DELIVERABLE: A complete, historically reconciled master objective register, ready for Director review.

STOP CONDITION: Inventory and reconciliation only. No automatic implementation, no self-certification, and no new sleep-run start.

END OF ORIGINAL 72-ITEM TRANSFER
