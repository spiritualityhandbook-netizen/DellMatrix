# R6.4 Delta-20 — AMEND-3 Reconciliation

**Directive:** GDP_PHASE_6_R64_CLOSE_ALL_OUTWARD_SECRET_PATHS (MODE=C)
**Date:** 2026-10-09
**Status:** All twenty re-examined against the Director's AMEND-3 findings.
Affected security, provenance, public-path, failure, and contradiction
claims reopened below. No PROVEN label rests on helper presence alone.

## Director AMEND-3 findings → dispositions

Director independently reproduced on `c555079` (controlled-dependency
probes, not a full independent regression):
- Request detachment: confirmed holding.
- Canonical incomplete-compensation reporting: confirmed holding.
- Null rejection: confirmed holding.
- Synchronization-error propagation: confirmed holding.

Still failing → fixed:

| # | Finding | Disposition |
|---|---------|-------------|
| C1 | Protected handle in proposal words reaches snapshot() unchanged | FIXED: snapshot_for sanitizes; canonical content untouched. Proven. |
| C2 | Grant handle as audit/provenance key survives sanitizer | FIXED: keys sanitized with deterministic collision-free safe representations. Proven. |
| C3 | Sanitization failure returns handle with sanitize_failed=True | FIXED: all fallbacks removed; minimal fixed-schema receipts. Proven. |

## Delta-20 (AMEND-3 re-examination)

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
AMEND-3 found: snapshots bypassed screening; sanitizer ignored dict
keys; sanitization failure released the original. Fixed: one complete
outward boundary (snapshots, receipts, audit, keys+values, identifiers,
provenance, errors); deterministic collision-free key representations;
minimal fixed-schema receipts on protection failure (no
`sanitize_failed` fallbacks). Proven: 19 new controls including
snapshot canaries (canonical unchanged), key collision tests,
protection failure at entry/after-enqueue/during-output, writer
exceptions with handles, all outcome paths, zero-canary durable audit,
and sensitivity (disabled guard leaks; restored guard sanitizes).

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
154 checks; sensitivity probes on the load-bearing boundaries
(envelope retention, secret screening, output guard, writer
classification); no unconditional passes.

### 16. Misleading display — PROVEN (re-examined and reopened, now re-closed)
AMEND-3 found: `sanitize_failed=True` flags that released the original
payload — a warning flag does not close the boundary (OWASP: logging
failures must not leak information). Fixed: all such fallbacks
removed; minimal fixed-schema receipts preserve classification with
zero uncontrolled content. Packet identity corrected: reviewed
head/tree separated from historical code-freeze identities; no blanket
"confirmed by Director" claims — the packet now identifies exactly
which controls the Director independently reproduced.

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
