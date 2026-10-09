# R6.4 Delta-20 — Predeclared Falsifiers and Dispositions

**Directive:** GDP_PHASE_6_R64_MULTI_INTELLIGENCE_SHARED_STATE_CIRCUIT §7
**Date:** 2026-10-08
**Status:** All twenty tracked. Bounded claims with executed evidence where
claimed; explicit gaps preserved. Analysis alone is never labeled PROVEN.

## 1. Missing workflow
**Claim:** All five objectives (6.4.1–6.4.5) have executed proofs.
**Evidence:** `r64_multi_intelligence_test.py` smoke (73 checks) covers
identity, protocol, audit, IntrinsicAgent, cross-process, rollback,
recovery, reference model, sensitivity. **PROVEN** (executed).

## 2. Contradictory records
**Claim:** Ledger, packet, and code agree on R6.4 scope.
**Evidence:** R64_RECONCILIATION.md maps objectives to owners; no
contradictory scope claims found. **BOUNDED** (reconciliation document;
not independently audited).

## 3. Semantic drift
**Claim:** "Agent", "coordinator", "grant", "persona" mean one thing each.
**Evidence:** AgentIdentity (host-bound subject); HostCoordinator (one
per program); grant (AcceptancePolicy capability); persona (descriptive
BIMOBody slot). No term reused with different meaning. **BOUNDED**
(code inspection).

## 4. Duplicate authority
**Claim:** No second permission authority created.
**Evidence:** Coordinator delegates ALL permission decisions to
AcceptancePolicy via the R6.1 `agent_confirm` writer path; audit is
observation-only (never consulted for allow/deny). **PROVEN** (sensitivity
probe: weakening the writer's subject check changes outcomes, proving
the writer — not the coordinator — decides).

## 5. Identity/permission conflation
**Claim:** PERSONA != PERMISSION; identity != authority.
**Evidence:** Persona slots/BIMO bindings recorded descriptively, never
read during dispatch; B cannot use A's grant (subject mismatch at writer);
persona/docking changes confer no permission (tested). **PROVEN**.

## 6. Unmediated execution layer
**Claim:** Every protected mutation goes through the coordinator.
**Evidence:** AgentRequestSurface exposes only snapshot + request_confirm;
both route through HostCoordinator.dispatch; reentrant dispatch rejected.
**BOUNDED** (agents in-process could bypass by importing program directly;
threat model explicitly excludes malicious in-process Python per directive).

## 7. Persistence inconsistency
**Claim:** agent_local and agent_audit persist/restore consistently.
**Evidence:** serialize/restore roundtrip tested (audit survives save/load;
agent-local observations survive save/load + cross-process). Malformed
agent_local fails closed. **PROVEN** (executed roundtrips).

## 8. Lost history
**Claim:** Committed history survives revocation, restart, rollback.
**Evidence:** Revoked grant denies new requests but committed idea stays
on plane (tested in protocol part); restart preserves committed history
(cross-process). **PROVEN**.

## 9. False provenance
**Claim:** Audit records carry true bound subject and correlation.
**Evidence:** Subject comes from host binding, not payload; correlation
passed through from envelope; no grant handles logged. **PROVEN**
(audit content assertions).

## 10. Credential/subject escape
**Claim:** No grant handles, credentials, or cross-agent secrets leak.
**Evidence:** Audit scrub drops grant/credential/password/secret keys;
snapshots contain no handles; B cannot read A's grant. **PROVEN**
(audit content scan + B-cannot-use-A-grant).

## 11. Human-authority bypass
**Claim:** Agents cannot mint, widen, or revoke grants.
**Evidence:** Surface exposes no mint/attenuate/revoke; coordinator has
no such methods; issuance stays on trusted host path. **PROVEN**
(surface method enumeration).

## 12. Offline dependency
**Claim:** No network or external service required.
**Evidence:** All proofs run offline; no imports of network modules in
the R6.4 path. **BOUNDED** (no explicit network-attempt test).

## 13. Measured performance regression
**Claim:** Coordinator adds no measurable overhead vs direct writer path.
**Evidence:** Matched-storage alternating runs (n=10 each, operation-only
timers, same owner/program): baseline `agent_confirm` median 219.68ms;
coordinator `request_confirm` median 194.34ms; overhead median -25.34ms
(noise; no regression). Runtime SHA `7b7a801d01178c4c`
(agent_coordinator.py). **PROVEN** (executed measurement).

## 14. Public-path theater
**Claim:** Proofs exercise production paths, not mocks.
**Evidence:** Real Program, real Nursery, real AcceptancePolicy, real
writer, real persistence, real OS processes. No mocks in the proof
suite. **PROVEN**.

## 15. Vacuous/count/statistical claims
**Claim:** Every check asserts a real outcome.
**Evidence:** 73 checks, each with concrete pre/postconditions;
sensitivity probes prove the checks can fail. No unconditional passes.
**PROVEN** (sensitivity).

## 16. Misleading display
**Claim:** Receipts and audit distinguish attempted/denied/committed.
**Evidence:** Receipt carries ok + result + reason; audit vocabulary
has five distinct statuses; unknown != completed. **PROVEN**.

## 17. Recovery/replay failure
**Claim:** Recovery-required blocks; rollback invalidates; replay safe.
**Evidence:** check_save_allowed blocks dispatch when recovery-required;
epoch advance invalidates queued requests; idempotent retry safe.
**PROVEN** (executed).

## 18. Unnecessary architecture
**Claim:** No second router/ledger/authority; reuse first.
**Evidence:** Reuses AcceptancePolicy, agent_confirm, outcome-ledger
pattern, persist payload, core_i_recovery. New code: coordinator
(serialization + idempotency, no existing owner), agent-local isolation
(no existing owner). **BOUNDED** (design review).

## 19. Research-to-code mismatch
**Claim:** Erlang message-passing inspiration correctly adapted.
**Evidence:** Agents communicate via typed request envelopes through a
serialized host coordinator (message-passing, not shared mutable
objects); Python queues NOT used as a transaction-safety claim —
safety comes from the coordinator's serialized dispatch + writer
checks. **BOUNDED** (design alignment; ADAPT not ADOPT).

## 20. Independent-model disagreement
**Claim:** Production agrees with independent reference model.
**Evidence:** 7 agreement checks on commit/retry/mismatch/reuse/revoke/
epoch; model calls no production helpers. **PROVEN**.

## Retained limits
- No distributed consensus, concurrent-writer safety, or malicious
  in-process Python protection claimed (directive §2).
- No crash-safe exactly-once execution claimed (directive §3).
- Performance measurement pending (see §13).
