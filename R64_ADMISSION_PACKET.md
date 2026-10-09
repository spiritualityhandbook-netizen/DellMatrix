# ADMISSION PACKET — R6.4 MULTI-INTELLIGENCE SHARED-STATE CIRCUIT
## (AMEND corrections applied)

**To:** Director · **From:** Uni Ω · **Date:** 2026-10-08
**Directive:** GDP_PHASE_6_R64_CLOSE_IDENTITY_EVIDENCE_AND_PERSISTENCE (MODE=C)
**Status:** CANDIDATE — NOT CERTIFIED — DO NOT MERGE. Awaiting Director admission review.

---

## 1. Identity

- **PR:** #83
- **HEAD:** `4e4f98894d6a77c7ead9565590d3bda0f4763586`
- **TREE:** `77dcb367262e7cdd99d4873e281c67ec379e4cea`
- **BASE:** `84a59137fe75d4ad5206642f8ba8a42183fdcef2` (R6.3 merge)
- **Branch:** `gdp-phase6-r64-multi-intelligence`
- **Prior candidate:** `d7eb47d` (AMEND findings; superseded)
- **Branch:** `gdp-phase6-r64-multi-intelligence`

## 2. Scope coverage (6.4.1–6.4.5 + AMEND findings)

| Objective | Implementation | Proofs |
|-----------|---------------|--------|
| 6.4.1 agent identity/BIMO binding | `agent_coordinator.py`: AgentIdentity, host-bound registration; persona/BIMO descriptive only | 9 checks |
| 6.4.2 shared-state protocol | `agent_coordinator.py`: HostCoordinator, strict RequestEnvelope, detached snapshots, serialized dispatch, namespaced idempotency | 18 checks + AMEND |
| 6.4.3 audit trail | `agent_coordinator.py`: capture_agent_action; value-based secret screening; `agent_audit` payload; malformed preserved | 7 checks + AMEND |
| 6.4.4 IntrinsicAgent recovery | `intrinsic_agent.py`: for_agent isolation, strict versioned validation; auto-sync hook in serialize() | 16 checks + AMEND |
| 6.4.5 public-path proofs | `r64_multi_intelligence_test.py` (98 checks), `r64_child.py`, `r64_reference_model.py` | 23 + 25 AMEND checks |

**Total: 98/98 checks pass.**

### AMEND findings → fixes (all 8)

1. **Retry identity:** receipts namespaced by (owner, subject, request_id); canonical descriptor compared. B cannot receive A's receipt.
2. **Mutable receipts:** deep-copy on store and return; caller mutation isolated.
3. **Secret logging:** value-based screening via `protected_values`/`contains_protected`; boundary rejection; canary test.
4. **Malformed state:** strict int/float (no bool/coercion/NaN/Inf); absent≠null; full-payload validation; over-bound rejected.
5. **Audit failure:** `audit_ok` flag in outcome; committed+flagged, never silent.
6. **Queue leakage:** queued entries removed on retry/conflict; bound+5 retries prove no growth.
7. **Auto-sync:** `sync_all_agents_to_program` in `serialize()`; observe→save→reload without manual sync.
8. **Model:** binds identity; revocation/rollback production-compared; model-only checks removed.

## 3. Results

- `python3 -m form.mandell.r64_multi_intelligence_test`: **98/98**
- `python3 -m form.regress --twice`: **110/110 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **110/110 GREEN**
- Exact-head CI: Python package (3.10, 3.11) SUCCESS; Form smoke SUCCESS.
  Code scanning AI findings: FAILURE — classified from logs as GitHub
  Copilot monthly quota exhausted (402); EVALUATION_UNAVAILABLE, not a
  code defect.

## 4. Architecture decisions (directive §2)

- **One trusted HostCoordinator** per program/owner; protected writes serialized.
- **Reuse:** AcceptancePolicy (permission), R6.1 `agent_confirm` (writer),
  R6.2 docking (inference, no permission), R6.3 `check_save_allowed` +
  rollback epochs, persistence payload, outcome-ledger pattern.
- **BIMO/personas descriptive only:** never mint/inherit/combine authority.
- **Agents get:** bounded detached snapshots + narrow `AgentRequestSurface`
  (snapshot + request_confirm). Never mutable Program/Nursery, policy
  controllers, or credentials.

## 5. Shared-state protocol (§3)

Typed `RequestEnvelope`: request_id, operation, target, expected
content/state evidence, correlation. Identity from host binding, never
payload. Validated before dispatch; authority/freshness/recovery/epoch
revalidated AT EXECUTION. Queued ≠ authorized.

- Exact retry → same receipt, no duplicate.
- Reused request_id + different content → reject.
- Interrupted/unknown → "unknown", never "completed".
- Concurrent/reentrant dispatch → explicit rejection.

## 6. IntrinsicAgent (§4)

- Traced all `intrinsic_agent.AGENT` uses: **zero production callers**.
- `for_agent(program, subject)`: isolated by (owner, subject).
- Versioned (`AGENT_LOCAL_VERSION=1`), validated persistence via
  program payload; malformed → `AgentLocalLoadError` (fail closed);
  absence → fresh default.
- Restores observations only; never permissions/grant handles.
- Payloads bounded (cells 1024, labels 256, history 32).
- Movement distinct from knowledge acceptance (tested).
- Module-global `AGENT` preserved for compatibility.

## 7. Audit and failure contract (§5)

- Records: bound subject, request correlation, operation, affected
  objects, result, provenance. **Never grant handles/credentials**
  (defensive scrub + content assertions).
- Statuses: attempted, denied, committed, failed, incomplete_recovery.
- Receipt ≠ durable evidence (documented).
- Audit persistence failure → visible (returns None), never falsely
  reverses committed ops.

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

Full reconciliation in `R64_DELTA20.md`. Summary:
- **PROVEN (executed):** 1, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 19, 20
- **BOUNDED:** 2, 3, 6, 12, 18
- **Gaps:** none outstanding; all 20 tracked with explicit limits.

## 10. Research decisions

- **ADAPT** Erlang message-passing: typed envelopes through serialized
  coordinator (not shared mutable objects).
- **REJECT** Python queues as transaction-safety: safety comes from
  serialized dispatch + writer checks, not the queue primitive.
- **ADOPT** existing owners: personas.py (descriptive slots),
  agent_authority.py (subject-bound endpoints), outcome_ledger.py
  (durable evidence pattern).

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
- Certification bounded to the multi-intelligence circuit.

## 13. Files changed

- `form/dell_matrix/agent_coordinator.py` (new, 27KB)
- `form/dell_matrix/intrinsic_agent.py` (agent-local isolation + persistence)
- `form/open.py` (Program fields: agent_local_states, agent_audit_records/seq)
- `form/persist.py` (serialize agent_local, agent_audit)
- `form/persist_rest.py` (restore agent_local, agent_audit; DURABLE_KEYS)
- `form/regress.py` (register R6.4 smoke)
- `form/mandell/r64_multi_intelligence_test.py` (new, 73 checks)
- `form/mandell/r64_child.py` (new, cross-process)
- `form/mandell/r64_reference_model.py` (new, independent model)
- `docs/README_EVIDENCE_MAP.md` (R6.3 MERGED/CLOSED; R6.4 candidate)
- `R64_RECONCILIATION.md`, `R64_DELTA20.md` (new)

---

**STOPPING POINT:** One complete R6.4 admission candidate for Director review.
No merge. No R6.5 implementation.
