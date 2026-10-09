# ADMISSION PACKET — R6.4 MULTI-INTELLIGENCE SHARED-STATE CIRCUIT

**To:** Director · **From:** Uni Ω · **Date:** 2026-10-08
**Directive:** GDP_PHASE_6_R64_MULTI_INTELLIGENCE_SHARED_STATE_CIRCUIT (MODE=C)
**Status:** CANDIDATE — NOT CERTIFIED — DO NOT MERGE. Awaiting Director admission review.

---

## 1. Identity

- **PR:** #83
- **HEAD:** `db647a252d95387f7634a0e4d84fe5b4e6c424ca`
- **TREE:** `e87da1e607f4583375de6021257660024f8d017f`
- **BASE:** `84a59137fe75d4ad5206642f8ba8a42183fdcef2` (R6.3 merge)
- **Branch:** `gdp-phase6-r64-multi-intelligence`

## 2. Scope coverage (6.4.1–6.4.5)

| Objective | Implementation | Proofs |
|-----------|---------------|--------|
| 6.4.1 agent identity/BIMO binding | `agent_coordinator.py`: AgentIdentity, host-bound registration; persona/BIMO descriptive only | 9 checks: host binding, unregistered rejection, envelope identity-field rejection, narrow surface |
| 6.4.2 shared-state protocol | `agent_coordinator.py`: HostCoordinator, RequestEnvelope, detached snapshots, serialized dispatch, idempotency | 18 checks: snapshots, A-confirms, B-denied, retry idempotent, reuse rejects, content/revoke/rollback/recovery denies, queue bounds, reentrancy |
| 6.4.3 audit trail | `agent_coordinator.py`: capture_agent_action; program payload `agent_audit` | 7 checks: subject/correlation/operation/affected, no grant leakage, stable IDs, persistence |
| 6.4.4 IntrinsicAgent recovery | `intrinsic_agent.py`: for_agent isolation, versioned to_dict/from_dict; payload `agent_local` | 16 checks: isolation, roundtrip, malformed fails closed, absence default, reload restores, no permissions, cross-owner |
| 6.4.5 public-path proofs | `r64_multi_intelligence_test.py`, `r64_child.py`, `r64_reference_model.py` | 23 checks: cross-process, reference model (7), sensitivity (4) |

**Total: 73/73 checks pass.**

## 3. Results

- `python3 -m form.mandell.r64_multi_intelligence_test`: **73/73**
- `python3 -m form.regress --twice`: **110/110 GREEN** (both passes)
- `python3 -m form.regress --order rev`: **110/110 GREEN**
- Exact-head CI: pending (PR #83 workflows)

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
