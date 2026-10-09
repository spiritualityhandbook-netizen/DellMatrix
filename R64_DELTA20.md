# R6.4 Delta-20 — AMEND-4 Reconciliation

**Directive:** GDP_PHASE_6_R64_FINISH_OUTPUT_COLLISION_AND_ERROR_CONTRACT (MODE=C)
**Date:** 2026-10-09
**Status:** All twenty re-examined against the Director's AMEND-4 findings.
Affected evidence-integrity, security, failure-reporting, and public-path
claims reopened below. Full twenty-category mapping retained.

## Director AMEND-4 findings → dispositions

Director independently reproduced on `b97b625` (controlled-dependency
probes, not a full independent regression):
- Snapshot redaction preserves canonical content: confirmed holding.
- Writer-failure receipts withhold secrets: confirmed holding.

Still failing → fixed:

| # | Finding | Disposition |
|---|---------|-------------|
| D1 | Mixed-key collision: {protected_key: A, "[REDACTED_KEY:1]": B} loses A's evidence | FIXED: full reservation of surviving clean keys before allocation. Proven. |
| D2 | Snapshot exception reflects canary-bearing protection failure via str(e) | FIXED: fixed non-reflecting message, chaining suppressed. Proven. |

## Delta-20 (AMEND-4 re-examination)

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
AMEND-4 found: mixed-key collision losing evidence; snapshot exception
reflecting canary-bearing protection failures. Fixed: full reservation
of surviving clean keys before allocation (deterministic, collision-free);
fixed non-reflecting error messages with suppressed chaining for all
protection failures. Proven: 14 new controls including both collision
orders, multiple reserves, nested dicts, entry/snapshot/output canary
exceptions, and sensitivity (buggy allocator loses evidence; fixed
preserves).

### 10. Credential/subject escape — PROVEN (re-verified)
See §9. Coverage stated: canonical grant-handle format + session values
+ configured credentials + decoded forms, now applied to the complete
outward boundary (including snapshots and dictionary keys). No
unknown-secret guarantee (explicit).

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
168 checks; sensitivity probes on the load-bearing boundaries
(envelope retention, secret screening, output guard, key allocator,
error wrapper, writer classification); no unconditional passes.

### 16. Misleading display — PROVEN (re-examined and reopened, now re-closed)
AMEND-4 found: exception messages reflecting internal protection
failures (OWASP: use generic outward errors, not reflected internals).
Fixed: all protection failure messages use fixed non-reflecting text;
exception chaining suppressed where it would reveal the original.
Packet identity: reviewed head/tree separated from historical
code-freeze identities; Director-reproduced controls identified
exactly.

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
