# R6.4 Delta-20 — AMEND-2 Reconciliation

**Directive:** GDP_PHASE_6_R64_FINISH_EXISTING_BOUNDARIES (MODE=C)
**Date:** 2026-10-09
**Status:** All twenty re-examined against the Director's AMEND-2 findings.
Affected claims reopened below. No PROVEN label rests on helper presence
alone — every claim maps to an executed assertion, with sensitivity
controls where the boundary is load-bearing.

## Director AMEND-2 findings → dispositions

| # | Finding | Disposition |
|---|---------|-------------|
| B1 | Enqueue retains original mutable envelope | FIXED: validated snapshot retained; caller object never stored. Proven structurally (`is not`) + behaviorally (post-enqueue mutation). |
| B2 | Grant handles in request_id enter audit unchanged | FIXED: complete envelope screened; complete audit sanitized. Proven with canaries. |
| B3 | Secret-screen import failure silently disables | FIXED: protection failure rejects explicitly. Proven with injected failure. |
| B4 | Sync failures suppressed twice | FIXED: suppression removed from sync AND serialize; failure propagates before durable write. Proven through ordinary save. |
| B5 | Explicit null becomes fresh state | FIXED: sentinels in loader and for_agent; from_dict rejects null. Proven. |
| B6 | Writer incomplete-compensation becomes ordinary denial | FIXED: canonical fields classified; incomplete_recovery with details. Proven through real writer. |

## Delta-20 (AMEND-2 re-examination)

### 1. Missing workflow — PROVEN (executed)
135 checks cover all AMEND and AMEND-2 findings; smoke() registered in regress.

### 2. Contradictory records — BOUNDED
Admission packet, PR body, evidence map, ledger reconciled together in
this cycle. Identity labels updated to final HEAD.

### 3. Semantic drift — BOUNDED
"Historical receipt" remains a defined term. "Retained snapshot" now
defined: the validator's detached values, stored at enqueue. "Audit
block" defined: in-memory vs persisted evidence distinguished.

### 4. Duplicate authority — PROVEN (re-verified)
Coordinator still delegates all permission to AcceptancePolicy/writer.
Sensitivity probe (weakened writer subject check) confirms the writer decides.
No new authority introduced; protection utilities reused, not reinvented.

### 5. Identity/permission conflation — PROVEN (re-verified)
Retry isolation confirmed by Director. AMEND-2 adds: the retained
envelope (not the caller's) is the request of record; conflicting reuse
preserves established history. Persona≠permission re-tested.

### 6. Unmediated execution layer — BOUNDED (unchanged)
Threat model excludes malicious in-process Python (directive §2).

### 7. Persistence inconsistency — PROVEN (re-examined and reopened, now re-closed)
AMEND-2 found: sync suppression, null-as-absence, unvalidated outer
version, str() normalization. All fixed and proven: fail-honest sync
(staged/validated, failure propagates before write, previous bytes
preserved), sentinels, strict outer version, no str() normalization.
Damaged audit evidence: complete originals preserved through the
payload; malformed load → save → reload keeps evidence (proven).

### 8. Lost history — PROVEN (unchanged)
Committed history survives revocation/restart/rollback.

### 9. False provenance — PROVEN (re-examined and reopened, now re-closed)
AMEND-2 found: request_id unscreened, audit fields unsanitized,
protection failure silent. All fixed: complete envelope screened
(identifiers, target, keys, values, decoded forms); complete audit
sanitized; protection failure rejects explicitly. Proven with canaries
in request_id, nested keys, target, post-enqueue mutation, and errors;
protection-unavailable negative control; clean-input positive control;
sensitivity (disabled screening → canary passes) proves the guard is
active.

### 10. Credential/subject escape — PROVEN (re-verified)
See §9. Coverage stated: canonical grant-handle format + session values
+ configured credentials + decoded forms. No unknown-secret guarantee
(explicit).

### 11. Human-authority bypass — PROVEN (unchanged)
No mint/widen/revoke on agent surfaces.

### 12. Offline dependency — BOUNDED (unchanged)

### 13. Measured performance regression — PROVEN (unchanged)
Coordinator median 194ms vs baseline 220ms; no regression.

### 14. Public-path theater — PROVEN (re-verified)
All AMEND-2 proofs through production paths. Incomplete compensation
proven through the REAL public writer with failure injected after
actual placement (not synthetic receipts). No mocks.

### 15. Vacuous/count/statistical claims — PROVEN (re-verified)
135 checks; sensitivity probes on the load-bearing boundaries
(envelope retention, secret screening, writer classification);
no unconditional passes.

### 16. Misleading display — PROVEN (re-examined and reopened, now re-closed)
AMEND-2 found: invented reason names, lost incomplete details,
invisible aggregated audit failures, conflated in-memory/persisted
evidence. Fixed: canonical writer fields; incomplete_recovery with
sanitized structured details; audit block aggregates lifecycle
failures and distinguishes in-memory from persisted.

### 17. Recovery/replay failure — PROVEN (re-verified)
Incomplete compensation preserved with canonical fields through the
real writer; recovery-required still blocks dispatch.

### 18. Unnecessary architecture — BOUNDED (unchanged)
Reuses protected_values, agent_confirm, check_save_allowed, persist,
atomic_write. No parallel audit store; no new secret interpreter.

### 19. Research-to-code mismatch — BOUNDED
Copy semantics: a validated detached copy is only independent if
RETAINED (Director's research note confirmed — enqueue now stores the
validated snapshot). Dataclass frozen=True still does not freeze
nested dicts (documented). Python JSON nonfinite explicitly rejected.

### 20. Independent-model disagreement — PROVEN (re-verified)
Model binds (owner, subject, request_id); revocation and rollback
production-compared. Model covers decision logic; the AMEND-2
mechanical fixes (retention, screening, classification) are proven by
direct production-path assertions, not modeled.

## CI scanning classification

**Code scanning AI findings: FAILURE — classified from actual logs.**
Cause: `SessionModelError: You have exceeded your monthly quota`
(statusCode 402, errorCode "quota"). This is a GitHub Copilot service
quota exhaustion, not a code defect. Recorded as EVALUATION_UNAVAILABLE
per standing rule (never PASS, never assumed). Supported by the actual
failure log (run 37876097089, 2026-10-09T02:46:16Z).

Python package (3.10, 3.11) and Form smoke: SUCCESS on candidate head.

## Retained limits

- No distributed consensus, concurrent-writer safety, or malicious
  in-process Python protection.
- No crash-safe exactly-once; receipt retention bounded at 500
  (in-memory, per-process).
- Secret screening covers recognized formats/values only.
- Coordinator queue is per-process; durable queue is future work.
- Audit `persisted` is only confirmed by save+reload, never at dispatch.
