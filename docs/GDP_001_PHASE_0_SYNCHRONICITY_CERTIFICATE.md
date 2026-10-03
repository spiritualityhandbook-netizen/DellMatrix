# GDP-001 Phase 0 — Synchronicity Certificate (§20–21)

**Branch:** `gdp-phase0-work` · **Date:** 2026-10-03
**Claim:** the twelve Phase-0 subsystems below are mutually consistent —
no subsystem's contract contradicts another's, and every cross-subsystem
claim has been tested at the boundary, not just inside its own suite.

---

## 1. Mandell ↔ Registry

`registry.execution_standing()` (ACTIVE / ACTIVE_REFUSAL /
RESERVED_NOT_ACTIVE / UNREGISTERED) agrees with `executor_leaf` behavior:
every ACTIVE dell has an executable path; every RESERVED_NOT_ACTIVE
dell (100–151) refuses with `ok=False` and zero mutation on all three
entry paths (single seed, direct leaf, chain atom). 315/315
reconciliation + 27/27 honesty. **SYNC.**

## 2. Registry ↔ Flow

Flow `parse_program` fail-closes on reserved addresses (`ValueError`);
the chain executor records reserved atoms as skipped-with-reason rather
than ok-clean. No Flow path can smuggle a reserved dell past the
registry's standing. **SYNC.**

## 3. English Brain ↔ Executor

The live English normalization path (`create`/`stamp`/etc.) routes
through the same front door (`observe_seed_execution` →
`executor.execute_seed`) as raw Mandell seeds. `english_brain.understand()`
has zero production callers — documented, not hidden. No English input
reaches an executor the registry does not authorize. **SYNC.**

## 4. Executor ↔ Program

`execute_seed` mutations land on the Program's real units; the
integrated proof (fresh OS processes) shows English create → units
present → save → new-process load → units present. No phantom mutations,
no lost mutations across the process boundary. **SYNC.**

## 5. Program ↔ Persistence

Save/load/checkpoint/rollback round-trip the Program's units, nursery,
and history. Post-rollback, the nursery re-points to the live owner
file (`repoint_to_live`); sealed generation members are byte-identical
after subsequent mutations; manifest fingerprints validate. 19/19
cross-process battery + 13/13 integrated proof. **SYNC.**

## 6. Persistence ↔ Outcome

Outcomes are captured per execution via `observe_seed_execution` and
persisted through the normal save path; rollback restores the
pre-checkpoint Outcome stream position honestly (post-checkpoint
Outcomes are discarded with the rolled-back state — documented, not
silent). No Outcome is recorded for an execution that did not happen;
no executed mutation lacks an Outcome record on the raw path. **SYNC.**

## 7. Outcome ↔ Perspective

Perspective views read the Program's real units (`_probe_nodes` →
`program.cube.session.plane.units`); Outcomes reference the same unit
identities. `see_whole` on the proof's program reported REAL count=2,
matching the two units the Outcome stream recorded as placed. No
divergence between "what happened" (Outcome) and "what is" (Perspective).
**SYNC.**

## 8. Perspective ↔ Security/Authority

Epistemic status is a security property: a blind consumer
(`spatial_audio`, `world_predict`) can no longer present an unverified
zero as fact — both propagate `UNKNOWN`. The Dell87 occupied-destination
refusal and `/cmd` origin hardening (PR #69) are unaffected by
perspective changes (no shared code paths). **SYNC.**

## 9. Security/Authority ↔ Executor

The refusal contract is uniform: reserved/not-active → `ok=False` +
named error + zero mutation, on the single-seed path, the direct-leaf
path, and (as honest skip records) the chain path. The two deliberate
semantic differences are documented Director-open decisions, not
accidents: (a) chain-skip (`ok=True, skipped=True`) vs single-seed
refusal (`ok=False`); (b) rollback converges the live file on next save
rather than eagerly. **SYNC.**

## 10. Executor ↔ Tests

Every executor path asserted in docs is exercised: 44/44 multi-path
integrity (raw/English/Flow/API), 82/82 full regress fwd+rev, exact-head
CI (3.10/3.11/smoke) pending on the PR head. No doc claims an executor
behavior without a test; the 19 Dell test gaps are disclosed in the
matrix, not hidden. **SYNC.**

## 11. Tests ↔ Docs

`LANGUAGE_COMPLETION_MATRIX.md` (ORACLE 10/10 sample-verified),
`PERSISTENCE_CONTRACT.md`, `RUNTIME_TRUTH_INVARIANTS.md`,
`DELLMATRIX_EQUATION_LEDGER.md` (counts corrected to listed IDs),
`MATHEMATICAL_ADMISSION_CONTRACT.md`, the GDP ledger (25/25 rows with
evidence), Delta-20, and this SWAT report are all in-repo and mutually
consistent. No doc contradicts a test result; audit-found staleness was
repaired, not excused. **SYNC.**

## 12. Docs ↔ Mandell (semantic closure)

The equation ledger's 32 classified equations, the registry's 100+49
dells, and the Flow laws' stated/partial classifications form a closed
vocabulary: every Mandell-level claim in the docs resolves to a
registry entry, a ledger equation, or an explicitly UNKNOWN cell. No
orphan claims. **SYNC.**

---

## Certificate

The twelve subsystems are mutually consistent at the Phase-0 gate.
Known deferred items (Phase-3 math duplicates, Flow STATED_ONLY laws,
19 Dell test gaps, SAFE_FUTURE_PHASE cleanups, the two Director-open
semantic decisions) are documented as deferrals/decisions, not hidden
inconsistencies.

**Synchronicity: CERTIFIED** — pending Director review of the two
open semantic decisions (§9a, §9b).
