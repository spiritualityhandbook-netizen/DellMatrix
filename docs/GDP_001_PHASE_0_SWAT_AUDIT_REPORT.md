# GDP-001 Phase 0 — SWAT Audit Report (§17)

**Branch:** `gdp-phase0-work` · **Method:** four independent read-only auditors
(NULL, PRISM, ORACLE, ARGUS) · **Date:** 2026-10-03

All auditors ran against pre-repair heads and re-verified against repair
commits. No auditor wrote to the working tree. Every MUST_FIX below was
repaired, re-tested, and re-audited before this report was frozen.

---

## NULL — adversarial documentation/code consistency audit

### MUST_FIX (all repaired)

1. **GDP ledger 0.3.1 falsely implied vesica/resonance duplicates were
   eliminated.** The duplicates were deferred to Phase 3 (R4-A2–A5), not
   eliminated. Corrected: the ledger now says "DEFERRED to Phase 3 per
   ledger §7 R4-A2–A5".
2. **LANGUAGE_COMPLETION_MATRIX stale after the reserved-Dell fix**
   (integration commit `8b8bfb9`). Corrected and recommitted.
3. **Perspective runtime checks not registered in regress.** Registered;
   suite went 81 → 82.

### SAFE_FUTURE_PHASE (deferred, no gate impact)

- Message framing predicate duplication (×3), partial predicate
  duplication (×3), receipt naming adapter/fallback, duplicate 21/22
  delegation block (×2), two unused imports. All safe future cleanup.

---

## PRISM — adversarial semantic/execution audit

### MUST_FIX (all repaired)

1. **Matrix summary count typo** (Core-I consistency 34/13/4). Corrected.
2. **Multi-atom primary 21/22 silently dropped later atoms.** The front-door
   intercept consumed the whole seed for a single-atom 21/22 merge/split.
   Fixed: intercept guarded with `len(s.atoms) == 1`; multi-atom seeds
   reach `chain_exec` while each atom still uses the same merge/split
   authority.
3. **Matrix stale references** to the reserved-Dell gap and the "dead"
   21/22 leaf. Corrected.
4. **Perspective checks absent from regress.** Corrected (same as NULL-3).

### Noted (not defects)

- RUNTIME_TRUTH_INVARIANTS "MUST" wording exceeds current conformance for
  dead/unwired consumers (`spatial_audio`, `world_predict`) — Phase 7.
- The admission contract closes disclosure/honesty, not mandatory
  derivation. Do not claim it "closes the derivation gap."
- Matrix TESTED counts rest on name-pattern evidence; not exact execution
  proof.

---

## ORACLE — independent verification audit

Re-ran all six specialist suites at HEAD `c9c0170` in throwaway copies:

| Suite | Claimed | Re-run |
|---|---|---|
| `p0r1_persist_test` | 19/19 | **19/19 PASS** |
| `r2_registry_reconciliation_test` | 315/315 | **315/315 GREEN** |
| `r2_semantic_honesty_test` | 27/27 | **27/27 GREEN** |
| `p0r3_execution_integrity_test` | 44/44 | **44/44 PASS** |
| `equation_ledger_invariants_test` | 14/14 | **14/14** |
| `perspective_runtime_truth_checks` | 26/26 | **26/26** |

Headline fixes empirically confirmed with independent probes (not the
suites): Dell28 rollback/autosave (sealed member byte-identical,
fingerprint validates), reserved Dell 151 refusal through the public
front door (`ok=False`, zero mutation; pre-fix code confirmed to have
answered `ok=True` + placed the idea), `see_whole` REAL count=8 on an
8-unit program. Matrix 10/10 random sample verified against code.

### Findings

- **F1 (was MUST_FIX, resolved during audit):** Matrix §3/§4 described the
  reserved-dell leaf bug as still present; already fixed by `8b8bfb9`.
  Residual stale phrase in §4 item 5 → SAFE_FUTURE_PHASE (repaired in the
  post-audit commit: item 5 now reads "the leaf else-branch it reaches is
  now honest").
- **F2 (SAFE_FUTURE_PHASE, repaired):** Equation ledger §11 had two
  off-by-one counts (ACTIVE_UNVALIDATED 9 vs 8 IDs; HISTORICAL 10 vs 9
  IDs) and the "Total 28" headline. Corrected to listed IDs: 32 distinct
  DellMatrix equations.
- **F3 (NOT_A_DEFECT):** Matrix rows 21/22 "Dead leaf" wording; the leaf
  now delegates — wording imprecision only (rows updated post-audit).
- **F4 (RESOLVED):** Perspective LIST wiring note superseded.

**Net conclusion:** every claimed number and headline fix is real and
reproducible. Nothing found that should block the phase gate on
code-integrity grounds.

---

## ARGUS — adversarial penetration audit

Read-only; all runtime probes in `/tmp` against throwaway objects.

### MUST_FIX (all repaired, re-verified)

1. **2a — Leaf 51–99/37 dishonest on direct calls.** The `8b8bfb9` guard
   covered only `None`/`>99`; primaries 51–99 and 37 through
   `executor_leaf.execute_seed` directly still answered `ok=True`
   "runtime thin" + `place_idea` mutation — the exact defect class the
   fix claimed to eliminate. **Repair:** the leaf's final else now
   refuses `primary > 50` and `primary == 37` (`ok=False`, zero
   mutation). 37's production authority is `core_i_ops`; the leaf has
   no 37 arm. Verified: 60/37/151 → `ok=False`, delta 0; 34 (explicit
   arm) still executes.
2. **2b-chain — Reserved atoms recorded as ok-clean.** `chain_exec`
   recorded skipped reserved atoms as `{"dell": 151, "ok": True,
   "error": ""}`. **Repair:** atoms recorded as `{"dell": 151,
   "ok": True, "skipped": True, "error": "reserved/not-active"}`; the
   skip-and-continue semantic is preserved (the Director-open
   skip-vs-refuse decision concerns overall chain `ok`, not the atom
   record). Verified end-to-end.
3. **3.3b — Raw-path Outcome false negative on partials.**
   `_RawReceipt` had no `atom_results`/`partial` fields, so
   `build_outcome` always recorded `atom_results=[]`,
   `partial_completion=False` on the raw path — the primary public
   execution path. **Repair:** fields added and populated from the
   execution result (chain `atom_results`; `partial` mirrored from
   `RouteReceipt.partial` semantics). Verified: partial chain → Outcome
   carries atom results and `partial_completion=True`.
4. **5-consumers (×2) — Confident zero over blind state.**
   `spatial_audio.cues_for_program` returned `{"ok": True, "count": 0}`
   and `world_predict.predict_unseen` returned `{"ok": True,
   "seen_count": 0}` on blind programs with no epistemic status — the
   exact R5 defect class. **Repair:** both propagate `_probe_nodes`
   status. Verified: blind → `UNKNOWN`; real program → `REAL`.

### SAFE_FUTURE_PHASE

- 3.2: receipt names `execute_seed`, `core_i_ops` actually ran (6
  correspondence dells) — name the terminal executor or document the
  delegation.
- 3.2-inc: chain drops Core-I typed args on leaf re-entry (sibling of
  the 0.3.2 fix).
- 3.3: raw-path refusal receipt gaps (`resolved_operation=None`,
  failed/blocked vocabulary split).
- P1.1: raw `Nursery.load(member)+save` corrupts the member — no
  production caller; latent API hazard only.

### NOT_A_DEFECT (holds)

Dell28 true-shape rollback, rollback variants, reserved router/flow/
bridge paths, negative primaries, receipt forgery resistance, Nursery
concurrency (lost-update refused), Perspective views on all program
shapes, Dell87 refusal, /cmd hardening. TOCTOU silent lost update:
structural, contrived-only timing — not a gate blocker. R5 registration
"finding": withdrawn, stale worker observation.

**Gate verdict:** no `UNKNOWN_REQUIRES_DIRECTOR` — every probe produced
a determinate, reproduced result. The five MUST_FIX items were
line-class repairs; all applied and re-verified.

---

## Post-audit state

All MUST_FIX findings across all four auditors are repaired. Full
regress: **83/83 GREEN (order=fwd)** and **83/83 GREEN (order=rev)** on
the post-repair head, including the newly registered
`p0_integrated_proof_test` (13/13 cross-process). The audit reports
themselves are delivered evidence in this repository under `docs/`.

---

## Gate R1 reconciliation (2026-10-03) — Director decisions implemented

### Decision 1: unified reserved/skipped atom truth

**Changed semantics:** a reserved/unexecuted chain atom is now
`ok=False, skipped=True, reason=<explicit>` (was `ok=True, skipped=True`).
ATOM EXECUTION RESULT != CHAIN CONTINUATION POLICY: the chain continues
past skipped atoms per its composition policy, but the aggregate is
honest (`ok=False`, `partial=True` when mixed, `any_skipped=True`).
FlowThru (`>>`) blocks after skipped atoms, consistent with the existing
`flow_thru_block` precedent (already `ok=False`).

**Tests:** 36 new assertions in `p0r3_execution_integrity_test`
(`t_director_d1_reserved_atom_truth`) covering all 12 required
scenarios: single/first/middle/final/multiple/surrounding/all-supported/
all-reserved/nested-sequence/raw-receipt/public-receipt/consumer.
80/80 execution suite green. Three pre-existing tests (`eoc_i`,
`cac_i`, `ros_i`) asserted the overruled semantics and were updated.

**SWAT re-verification:**
- ARGUS: adversarial probes confirm no path (direct chain, observer,
  Outcome ledger) lets a consumer infer `ok=True` for a skipped atom;
  chain-level `ok` is `False` whenever skips are present. ALL HOLDS.
- ORACLE: all 12 scenarios empirically verified; atom records carry
  explicit reasons; aggregate flags correct.
- PRISM: `partial` semantics consistent across chain result,
  `_RawReceipt`, and Outcome (`partial_completion`); `RouteReceipt.partial`
  uses the same `any/not-all` logic.
- NULL: no parallel mechanisms — existing `_run_atom`/`execute_range`
  paths modified; `partial`/`any_skipped` are additive result keys.

### Decision 2: eager rollback convergence

**Changed semantics:** `core_i_recovery.rollback` now eagerly writes the
validated target generation's state to the live program and nursery
files (atomic, independent copies) before returning. A fresh
`persist_rest.load(owner)` observes the rolled-back state with no
subsequent save. Sealed members are never written (Dell28 invariant
preserved). Failures before the first live write (validation,
serialization, nursery-conflict pre-flight) leave live files
byte-identical — zero partial mutation.

**Tests:** 12 new proofs in `p0r1_persist_test`
(`t_d2_eager_rollback_convergence`) covering all 7 required scenarios,
several in fresh OS processes: live-immediate, sealed-byte-identical,
fresh-process-no-save, save-reload, mutate-save-reload, multi-cycle,
and three injected-failure zero-mutation proofs. 31/31 persistence
battery green.

**SWAT re-verification:**
- ARGUS: nursery never points at sealed members post-rollback; sealed
  members byte-identical after aggressive mutation; concurrent live-
  nursery modification refused with zero program mutation. ALL HOLDS.
- ORACLE: all 7 scenarios empirically verified, including cross-process.
- PRISM: rollback path consistent across `core_i_recovery`,
  `checkpoint_generation`, `persist_rest`, and `nursery` — single
  authority, no divergent restore paths.
- NULL: `_eager_converge_live` reuses `persist_rest.save` and
  `nursery.save`; no duplicated persistence logic.

**Delta reconsideration:** no new material issues. The two semantic
changes are minimal, focused, and do not introduce new failure classes.
The eager-rollback write window (between the two atomic file writes) is
documented; each file remains internally consistent.

---

## GATE R2 RE-AUDIT (2026-10-03)

Director issued FINAL_GATE_R2 with two material findings. All auditors
re-ran against the R2 repair.

### NULL R2

- **No duplicate persistence transaction mechanisms.** `transactional_ops.py`
  is in-memory apply/undo (Verse-inspired), not file-pair persistence.
  The rollback journal (`core_i_recovery`) is the single authority for
  program/nursery pair-atomicity. No unnecessary state machinery found.

### PRISM R2

- **One persistence authority verified** across rollback, load, journal
  recovery, checkpoint generations, and live state. `persist_rest` owns
  live files; `checkpoint_generation` owns sealed members; `core_i_recovery`
  owns rollback with journal; `recover_rollback_transaction` runs inside
  every load. No competing authority.

### ORACLE R2

- **Transaction behavior independently reproduced.** 8 injection points
  verified in fresh OS processes: pre-commit failures -> old pair;
  post-staging failures -> target pair via recovery. Never hybrid.
- **Repaired delegation test proven fallible.** The new `dup21_leaf_delegates`
  assertion returns True on current code and False on simulated divergent
  code (place_idea without delegation). The old `or True` assertion
  returned True on both, proving vacuity.

### ARGUS R2

- **Journal crash boundaries:** injected at prepare/stage/commit/cleanup/
  verify; recovery yields old-complete or target-complete. Never hybrid.
- **Recovery idempotence:** second recovery is no-op (None).
- **Stale journal:** 'prepared' phase with no staging -> rolled_back, journal
  discarded.
- **Unknown phase:** raises RuntimeError, refuses to guess.
- **Partial rename:** staged journal + one rename -> recovery completes second.
- **Repeated recovery:** clean state -> None.

### Test-honesty sweep R2

- **Vacuous assertion removed:** `"_front_door" in src and "live_identity"
  not in src or True` (unconditionally True) replaced with arm-scoped
  delegation check.
- **Sweep result:** no other `or True`/`and False` in Phase-0 tests. One
  `rec(..., True)` is perf measurement-only (labeled). Exception handlers
  are cleanup-only. No mock-only integration claims. No dead PASS-forcing
  branches.

### MUST_FIX R2 (all repaired)

1. **Rollback pair-atomicity gap.** Two separate atomic writes did not
   guarantee the live pair was transactionally atomic. **Repair:**
   journaled two-file transaction (prepare/stage/commit/cleanup/verify)
   with recovery in every load.
2. **Vacuous test assertion.** Replaced with fallible single-authority proof.
