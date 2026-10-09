# ADMISSION PACKET — R6.4 MULTI-INTELLIGENCE SHARED-STATE CIRCUIT
## (AMEND-2 corrections applied)

**To:** Director · **From:** Uni Ω · **Date:** 2026-10-09
**Directive:** GDP_PHASE_6_R64_FINISH_EXISTING_BOUNDARIES (MODE=C)
**Status:** CANDIDATE — NOT CERTIFIED — DO NOT MERGE. Awaiting Director admission review.

---

## 1. Identity

- **PR:** #83
- **HEAD:** `0f61be07413331787b90fbd4c2f4ed3402489407`
- **TREE:** `95713a986175ca9a285a89073d661108b347a547`
- **BASE:** `84a59137fe75d4ad5206642f8ba8a42183fdcef2` (R6.3 merge)
- **Branch:** `gdp-phase6-r64-multi-intelligence`
- **Prior candidates:** `d7eb47d` (AMEND findings; superseded),
  `06f6953` (AMEND-2 findings; superseded)

## 2. Scope coverage (6.4.1–6.4.5 + AMEND + AMEND-2 findings)

| Objective | Implementation | Proofs |
|-----------|---------------|--------|
| 6.4.1 agent identity/BIMO binding | `agent_coordinator.py`: AgentIdentity, host-bound registration; persona/BIMO descriptive only | 9 checks |
| 6.4.2 shared-state protocol | `agent_coordinator.py`: HostCoordinator, strict RequestEnvelope, detached snapshots, serialized dispatch, namespaced idempotency, RETAINED validated snapshot | 18 + AMEND + AMEND-2 checks |
| 6.4.3 audit trail | `agent_coordinator.py`: capture_agent_action; complete secret screening; sanitized receipts/audit; `agent_audit` payload with preserved malformed evidence | 7 + AMEND + AMEND-2 checks |
| 6.4.4 IntrinsicAgent recovery | `intrinsic_agent.py`: for_agent isolation, strict versioned validation, sentinel absence, fail-honest sync | 16 + AMEND + AMEND-2 checks |
| 6.4.5 public-path proofs | `r64_multi_intelligence_test.py` (135 checks), `r64_child.py`, `r64_reference_model.py` | 23 + 25 AMEND + 37 AMEND-2 checks |

**Total: 135/135 checks pass.**

### AMEND findings → fixes (8/8, confirmed by Director)

1. **Retry identity:** receipts namespaced by (owner, subject, request_id); canonical descriptor compared. B cannot receive A's receipt. ✅
2. **Mutable receipts:** deep-copy on store and return; caller mutation isolated. ✅
3. **Secret logging:** value-based screening; boundary rejection; canary test. ✅
4. **Malformed state:** strict validation; absent≠null; full-payload; over-bound rejected. ✅
5. **Audit failure:** `audit_ok` flag; committed+flagged, never silent. ✅
6. **Queue leakage:** entries removed on retry/conflict; bound+5 retries prove no growth. ✅
7. **Auto-sync:** hook in `serialize()`; observe→save→reload without manual sync. ✅
8. **Model:** binds identity; revocation/rollback production-compared. ✅

### AMEND-2 findings → fixes (6/6)

1. **Retain validated request:** `enqueue` constructs and stores a NEW
   envelope from the validator's detached values; the caller's original
   (mutable nested mappings) is never stored. Descriptor derived from the
   retained snapshot. Proven: post-enqueue mutation of the original
   cannot change execution, attribution, screening, or evidence
   (structural `is not` check + behavioral mutation test). Conflicting
   reuse denies WITHOUT overwriting the established historical receipt;
   exact retry after conflict still returns the original.
2. **Complete secret protection:** the COMPLETE envelope is screened —
   request_id, target, operation, all keys and values (decoded-form
   check catches `\uXXXX`). Complete outward receipts and audit records
   sanitized (subject, request_id, affected, errors). Protection import
   or screening failure REJECTS explicitly (no silent `except: return`).
   Proven: canaries in request_id, nested keys, target, and post-enqueue
   mutation all rejected/never reach audit; protection-failure raises;
   sensitivity (screening disabled → canary passes) proves the guard is
   active; clean-input positive control works with no redaction artifacts.
3. **Real writer contract:** incomplete compensation classified by the
   canonical fields (`reason="acceptance_policy_denied"`,
   `compensation="incomplete"`, `compensation_failures`,
   `compensation_removed`, `evidence_retained`) — no invented reason
   names. Proven through the REAL public writer with failure injected
   after actual placement (wrapped `place`: revoke grant + break
   cleanup). Returns `incomplete_recovery` with sanitized structured
   details. Audit failures aggregated across the lifecycle (enqueue,
   dispatch, retry, conflict, failure, incomplete); a failed
   attempted-event survives a successful final capture. In-memory vs
   persisted evidence distinguished in the receipt audit block.
4. **Honest behavioral save:** broad suppression REMOVED from both
   `sync_all_agents_to_program` and `serialize`. All live snapshots
   staged and validated BEFORE stored state changes; a sync failure
   propagates and no durable write occurs (previous bytes preserved;
   live observations retained in memory). Proven through ordinary save.
   Sentinels for genuine absence; explicit null section/subject rejected
   in loader AND `for_agent`. Outer `agent_local_version` strictly
   validated (null/str/bool/mismatch reject). Nested history validated
   without `str()` normalization (dict/tuple/NaN items reject); valid
   scalars accepted. Declared retention (to_dict) separate from input
   validation (from_dict).
5. **Damaged audit evidence:** the COMPLETE original malformed record is
   preserved in `agent_audit_malformed` through the existing
   `agent_audit` payload section (no parallel store). Serialize writes
   it back; loader restores it. Proven: malformed load → save → reload
   keeps the complete originals; valid records survive.
6. **Evidence closure:** 37 new public-path checks with sensitivity
   controls; packet/PR/evidence-map/ledger reconciled; Delta-20
   re-examined with affected claims reopened.

## 3. Results

- `python3 -m form.mandell.r64_multi_intelligence_test`: **135/135**
- `python3 -m form.regress --twice`: **110/110 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **110/110 GREEN**
- Exact-head CI: (to be verified on final HEAD)
  - Previous candidate: Python package (3.10, 3.11) SUCCESS; Form smoke SUCCESS.
  - Code scanning AI findings: FAILURE — classified from actual logs as
    GitHub Copilot monthly quota exhausted (402 SessionModelError);
    EVALUATION_UNAVAILABLE, not a code defect, not a PASS.

## 4. Architecture decisions (directive §2)

- **One trusted HostCoordinator** per program/owner; protected writes serialized.
- **Reuse:** AcceptancePolicy (permission), R6.1 `agent_confirm` (writer),
  R6.2 docking (inference, no permission), R6.3 `check_save_allowed` +
  rollback epochs, persistence payload, outcome-ledger pattern,
  `inference_dock.protected_values` / `contains_protected_decoded`
  (secret screening — no new secret interpreter).
- **BIMO/personas descriptive only:** never mint/inherit/combine authority.
- **Agents get:** bounded detached snapshots + narrow `AgentRequestSurface`
  (snapshot + request_confirm). Never mutable Program/Nursery, policy
  controllers, or credentials.

## 5. Shared-state protocol (§3)

Typed `RequestEnvelope`: request_id, operation, target, expected
content/state evidence, correlation. Identity from host binding, never
payload. The VALIDATED snapshot is retained at enqueue; authority/
freshness/recovery/epoch revalidated AT EXECUTION. Queued ≠ authorized.

- Exact retry → same receipt (historical), no duplicate.
- Reused request_id + different descriptor → reject; established history
  preserved (not overwritten).
- Post-enqueue caller mutation → cannot reach execution/evidence.
- Interrupted/unknown → "unknown", never "completed".
- Concurrent/reentrant dispatch → explicit rejection.

## 6. IntrinsicAgent (§4)

- Traced all `intrinsic_agent.AGENT` uses: **zero production callers**.
- `for_agent(program, subject)`: isolated by (owner, subject); sentinel
  distinguishes genuine absence (fresh default) from explicit null
  (AgentLocalLoadError).
- Versioned (`AGENT_LOCAL_VERSION=1` outer + inner), strictly validated;
  malformed → fail closed; absence → fresh default.
- Sync is fail-honest: staged/validated before stored-state mutation;
  failure propagates before any durable write.
- Restores observations only; never permissions/grant handles.
- Payloads bounded (cells 1024, labels 256, history 32).
- Movement distinct from knowledge acceptance (tested).
- Module-global `AGENT` preserved for compatibility.

## 7. Audit and failure contract (§5)

- Records: bound subject, request correlation, operation, affected
  objects, result, provenance. Complete record sanitized (subject,
  request_id, affected, errors); protection failure → observable
  capture failure, never unsanitized storage.
- Statuses: attempted, denied, committed, failed, incomplete_recovery.
- Audit failures aggregated across the request lifecycle; the receipt
  carries an audit block (`captured_in_memory`, `persisted`,
  `evidence`, `failures`, `ok`) plus top-level `audit_ok`.
- In-memory evidence ≠ persisted evidence (never claimed at dispatch).
- Incomplete compensation: canonical writer fields preserved as
  `incomplete_recovery` with sanitized structured details — never
  ordinary denial, never lost details.
- Damaged audit evidence: complete originals preserved through the
  payload; malformed load → save → reload keeps evidence.

## 8. Walking skeleton (§6)

Two agents (A, B), one owner, production public interfaces:
- A+B isolated snapshots; A content-bound grant; B cannot use it.
- A confirms; retry idempotent; changed-content/revoked deny.
- Persona/docking changes confer no permission.
- Rollback invalidates stale queued requests; recovery-required blocks.
- Fresh reload restores behavior + history, not session authority.
- Cross-owner isolation, malformed state, queue bounds, failure/restart
  all covered. Fixed child scripts + JSON args; real OS-process restart.

## 9. Delta-20 (§7)

Full reconciliation in `R64_DELTA20.md` (re-examined for AMEND-2).
Affected categories reopened: identity, provenance, security,
persistence, public-path, recovery, contradiction. No PROVEN label
rests on helper presence alone — every claim maps to an executed
assertion with sensitivity where the boundary is load-bearing.

## 10. Research decisions

- **ADAPT** Erlang message-passing: typed envelopes through serialized
  coordinator (not shared mutable objects).
- **REJECT** Python queues as transaction-safety: safety comes from
  serialized dispatch + writer checks, not the queue primitive.
- **ADAPT** copy semantics with eyes open: a validated detached copy is
  only independent if RETAINED — enqueue now stores the validated
  snapshot (research note from Director confirmed in code).
- **ADOPT** existing owners: personas.py (descriptive slots),
  agent_authority.py (subject-bound endpoints), outcome_ledger.py
  (durable evidence pattern), inference_dock protection utilities.

## 11. Performance

Matched-storage alternating runs (n=10, operation-only):
- Baseline `agent_confirm`: median 219.68ms
- Coordinator `request_confirm`: median 194.34ms
- Overhead: -25.34ms (noise; **no regression**)

## 12. Honest limits

- No distributed consensus, concurrent-writer safety, or malicious
  in-process Python protection claimed.
- No crash-safe exactly-once execution claimed.
- Coordinator queue/receipts are per-process (in-memory); durable
  queue is future work.
- Secret screening covers recognized formats/values only; no
  unknown-secret guarantee.
- Certification bounded to the multi-intelligence circuit.

## 13. Files changed

- `form/dell_matrix/agent_coordinator.py` (new)
- `form/dell_matrix/intrinsic_agent.py` (agent-local isolation + persistence)
- `form/open.py` (Program fields: agent_local_states, agent_audit_records/seq/malformed)
- `form/persist.py` (serialize agent_local, agent_audit + malformed)
- `form/persist_rest.py` (restore agent_local, agent_audit; DURABLE_KEYS)
- `form/regress.py` (register R6.4 smoke)
- `form/mandell/r64_multi_intelligence_test.py` (135 checks)
- `form/mandell/r64_child.py` (cross-process)
- `form/mandell/r64_reference_model.py` (independent model)
- `docs/README_EVIDENCE_MAP.md` (R6.3 MERGED/CLOSED; R6.4 candidate)
- `R64_RECONCILIATION.md`, `R64_DELTA20.md`

---

**STOPPING POINT:** One complete R6.4 admission candidate for Director review.
No merge. No R6.5 implementation.
