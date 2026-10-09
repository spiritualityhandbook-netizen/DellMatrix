# R6.4 Delta-20 — AMEND Reconciliation

**Directive:** GDP_PHASE_6_R64_CLOSE_IDENTITY_EVIDENCE_AND_PERSISTENCE (MODE=C)
**Date:** 2026-10-08
**Status:** All twenty re-examined against the Director's AMEND findings.
Contradicted PROVEN labels reopened below; every item maps to executed
evidence or explicit noncoverage.

## Director findings → dispositions

| # | Finding | Disposition |
|---|---------|-------------|
| F1 | Retry identity isolation (B got A's receipt) | FIXED: receipts namespaced by (owner, subject, request_id); descriptor compared. Proof: cross-subject retry denied. |
| F2 | Mutable cached evidence | FIXED: deep-copy on store and return. Proof: mutation isolation checks. |
| F3 | Secret logging (canary under innocent key) | FIXED: value-based screening via protected_values/contains_protected; boundary rejection. Proof: canary rejected, audit clean. |
| F4 | Malformed behavioral state (null/bool/float/NaN/tail) | FIXED: strict validation; absent≠null; full-payload validation; NaN/Inf rejected. Proof: 12 malformation cases. |
| F5 | Invisible audit failure | FIXED: audit_ok flag in outcome; committed+flagged, not silent. Proof: injected failure test. |
| F6 | Queue leakage on cached retry | FIXED: queued entries removed on retry/conflict paths. Proof: queue-bound retries, no growth. |
| F7 | Manual sync required; model shares omission | FIXED: canonical auto-sync hook in serialize(); model binds identity. Proof: observe→save→reload without manual sync. |
| F8 | Model-only checks | FIXED: revocation/rollback now production-compared. Model-only checks removed. |

## Delta-20 (reopened)

### 1. Missing workflow — PROVEN (executed)
98 checks cover all findings; smoke() registered in regress.

### 2. Contradictory records — BOUNDED
Reconciliation doc updated; admission packet identity corrected (see §20).

### 3. Semantic drift — BOUNDED
"Historical receipt" now a defined term (not new authorization/execution).

### 4. Duplicate authority — PROVEN
Coordinator still delegates all permission to AcceptancePolicy/writer.
Sensitivity probe (weakened writer subject check) confirms the writer decides.

### 5. Identity/permission conflation — PROVEN (re-verified)
F1 was an identity/attribution defect, not a permission grant — B got
ok=True but no second write occurred. Fixed via namespacing. Persona≠permission
re-tested.

### 6. Unmediated execution layer — BOUNDED (unchanged)
Threat model excludes malicious in-process Python (directive §2).

### 7. Persistence inconsistency — PROVEN (re-verified)
F4/F7 fixed. Auto-sync hook; strict validation; malformed audit preserved
(agent_audit_malformed), not silently emptied.

### 8. Lost history — PROVEN (unchanged)
Committed history survives revocation/restart/rollback.

### 9. False provenance — PROVEN (re-verified)
F3 fixed: value-based screening; canary test proves no leakage.

### 10. Credential/subject escape — PROVEN (re-verified)
F3 fixed. Coverage stated: canonical grant-handle format + session values
+ env credentials. No unknown-secret guarantee (explicit).

### 11. Human-authority bypass — PROVEN (unchanged)
No mint/widen/revoke on agent surfaces.

### 12. Offline dependency — BOUNDED (unchanged)

### 13. Measured performance regression — PROVEN (unchanged)
Coordinator median 194ms vs baseline 220ms; no regression.

### 14. Public-path theater — PROVEN (re-verified)
All AMEND proofs through production paths; no mocks.

### 15. Vacuous/count/statistical claims — PROVEN (re-verified)
98 checks; sensitivity probes; no unconditional passes.

### 16. Misleading display — PROVEN (re-verified)
F5 fixed: audit_ok flag; historical label; incomplete_recovery distinct
from denial.

### 17. Recovery/replay failure — PROVEN (re-verified)
F8 (incomplete compensation) now preserved as incomplete_recovery.

### 18. Unnecessary architecture — BOUNDED (unchanged)
Reuses protected_values, agent_confirm, check_save_allowed, persist.

### 19. Research-to-code mismatch — BOUNDED
Dataclass frozen=True does NOT freeze nested dicts — now explicitly
documented; detachment via deep copy. Python JSON nonfinite — now
explicitly rejected. ADAPT with eyes open.

### 20. Independent-model disagreement — PROVEN (re-verified)
Model binds (owner, subject, request_id); revocation and rollback now
production-compared (2 agreement checks); model-only checks removed.

## CI scanning classification

**Code scanning AI findings: FAILURE — classified from actual logs.**
Cause: `SessionModelError: You have exceeded your monthly quota`
(statusCode 402, errorCode "quota"). This is a GitHub Copilot service
quota exhaustion, not a code defect. Recorded as EVALUATION_UNAVAILABLE
per standing rule (never PASS, never assumed).

Python package (3.10, 3.11) and Form smoke: SUCCESS on candidate head.

## Retained limits

- No distributed consensus, concurrent-writer safety, or malicious
  in-process Python protection.
- No crash-safe exactly-once; receipt retention bounded at 500
  (in-memory, per-process).
- Secret screening covers recognized formats/values only.
- Coordinator queue is per-process; durable queue is future work.
