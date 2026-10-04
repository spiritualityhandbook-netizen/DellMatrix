# GDP-001 Phase 3 Acceptance Matrix

**Program:** GDP-V1 · **Phase:** 3 — Resonance, Harmony & Information Geometry
**Baseline:** `ebfd68b6234de1bae8e60bed1bc380f30e425b39`
**Authority:** OVERSEER > DIRECTOR > UNI
**Status:** FINAL — archaeology complete, dispositions set; P3R repair amendment 2026-10-04 (see §P3R record)

Each objective: contract, canonical owner, real caller, expected behavior,
failure behavior, proof, disposition.

---

## R3.1 — Affinity/resonance reconciliation

### 3.1.1 `_affinity` exposed as first-class service with contract
- **Contract:** Mathematical admission contract (8 fields). Inputs: two idea IDs + plane. Output: dict with affinity, jaccard, harmonic, distance, shared, goal_boost, body_boost. **Honest bounds (P3R, verified empirically 2026-10-04; the old "affinity ∈ [0,1]" contradicted the body boost and is withdrawn):** affinity ≥ 0.0 always; affinity ≤ 1.0 whenever body_boost == 0.0 (0.40+0.22+0.13+0.13 = 0.88 base, goal_boost ≤ 0.12); affinity ≤ 1.15 theoretical maximum with body_boost active (0.88 + 0.12 + 0.15 — identical co-located in-scope ideas naming missing organs; approached within ~1e-9 of the harmonic epsilon). jaccard, harmonic ∈ [0,1]; distance ≥ 0.0 (99.0 sentinel when a unit is missing); shared, goal_boost, body_boost ≥ 0.0.
- **Canonical owner:** `form/dell_matrix/ringed_growth.py::_affinity` (live authority)
- **Real caller:** `RingedGrowth.run()` (line 260) ← `Program.grow_ideas` ← REPL growth commands
- **Expected behavior:** Deterministic composite: 0.40×harmonic + 0.22×jaccard + 0.13×spatial + 0.13×in_scope + goal_boost + body_boost. **Permutation guarantee (P3R, verified empirically: 0 mismatches / 2974 random ordered pairs):** the full output dict is bitwise identical under argument permutation (`_affinity(plane,a,b) == _affinity(plane,b,a)` field-for-field). The in_scope term formally reads `enhance_scope(a)`, but scope membership is mutual in all reachable plane states, so no asymmetry is observable.
- **Failure behavior:** Missing units → returns the full dict WITHOUT raising (fail-closed, no exception), with distance 99.0 and the token/goal/body terms 0.0. **The old "affinity 0.0" shorthand is falsified and withdrawn:** the spatial floor (0.13/(1+99) = 0.0013) and the in_scope floor (0.13×0.2 = 0.026) still contribute, so affinity is 0.0273 (repr-verified), not 0.0. Fail-closed IN EFFECT: 0.0273 < STANSTILL_AFFINITY (0.10), so the "None" gate fires and no ring proposal results. FADED units (R3.5.2): either unit faded → the full dict with all values 0.0, no exception.
- **Proof:** `p3_r31_affinity_proof.py` — determinism, bounds, failure cases, live-path witness. **P3R (Phase B):** rewritten non-vacuous — content-bearing fixtures, hand-computed expected affinity asserted in comments, bypass-must-fail tests (faded filter disabled → faded pair must leak; `_tension` suppressed → `_harmonic` must change).
- **Disposition:** IMPLEMENT (expose with contract + admission documentation)

### 3.1.2 `resonance.py` rehomed or removed after exposure
- **Contract:** N/A (reconciliation)
- **Canonical owner:** N/A
- **Real caller:** `enhance_gate.py` (pulse/status), `persist.py`/`persist_rest.py` (ResonanceState persistence)
- **Expected behavior:** `resonance.py` (pulse/diffusion) and `_affinity` (pair scoring) are DIFFERENT concepts. Keep both, document the distinction.
- **Failure behavior:** N/A
- **Proof:** Documentation + code comments
- **Disposition:** IMPLEMENT (reconcile, not remove: document that pulse≠affinity)

### 3.1.3 Serendipity term (tension/dissimilarity) + affinity evaluation metrics
- **Contract:** The "tension" term already exists inside `_harmonic` (exclusive-token bridge). Expose as explicit serendipity metric.
- **Canonical owner:** `ringed_growth.py::serendipity` (exposed normalized tension; raw form `ringed_growth.py::_tension`)
- **Real caller (P3R reconciliation, code-verified 2026-10-04):** the consumer is `_affinity` via `_harmonic`'s tension term (0.40 weight). Honest precision: `_harmonic` calls `_tension` directly; the named `serendipity()` function is the exposed normalized form t/(1+t) of that same term, currently invoked by the proof (no production call site uses the name yet — the tension *concept* flows `_tension` → `_harmonic` → `_affinity`). The old "Real caller: _affinity" shorthand is refined, not contradicted.
- **Expected behavior:** Serendipity = tension/(1+tension) ∈ [0,1); high when pairs share little but have complementary exclusive tokens. Range verified: 0.0 ≤ s < 1.0 (approaches 1.0 asymptotically, never reaches it); symmetric; serendipity(a,a) == 0.0; empty inputs → 0.0.
- **Failure behavior:** Empty sets → 0.0
- **Proof:** `p3_r31_affinity_proof.py` — serendipity bounds, monotonicity
- **Disposition:** IMPLEMENT (expose tension as named serendipity metric)

### 3.1.4 Seeded RNG for deterministic growth IDs
- **Contract:** Growth IDs must be deterministic given (seed, inputs)
- **Canonical owner:** `form/dell_matrix/nursery.py::_slug` (seeded deterministic ID)
- **Real caller:** `Nursery.add` ← `RingedGrowth.run(seed)`
- **Expected behavior:** Same inputs + same seed → same IDs. The digest is SHA-256 over (seed, text), not `hash()`; the exact-collision fallback suffix (`"_<count>"`) is deterministic given the same add sequence on an equal starting nursery.
- **Failure behavior:** Pre-Phase-3: `hash(text)` is salted per process (PYTHONHASHSEED), so IDs were deterministic only within one process. Post-Phase-3: identical (seed, label, add-sequence) yields identical IDs in every process (cross-process verified in the proof).
- **Proof:** `p3_r31_affinity_proof.py` — determinism test
- **Disposition:** IMPLEMENT (or document if already deterministic)

### 3.1.5 Resonance vs Verita authority reconciled (parallel, not merged)
- **Contract:** N/A (architectural decision)
- **Canonical owner:** N/A
- **Real caller:** N/A
- **Expected behavior:** Resonance (pulse/diffusion + pair affinity) and Verita (solo integrity + pair coherence) remain DISTINCT. No merging. Document the firewall.
- **Failure behavior:** N/A
- **Proof:** Documentation in ledger + code comments
- **Disposition:** IMPLEMENT (document firewall, keep parallel)

---

## R3.2 — Harmony model

### 3.2.1 Define harmony as a DellMatrix semantic (not musical metaphor)
- **Contract:** Harmony = "the degree to which a set of ideas forms a coherent, non-redundant whole" (operational definition)
- **Canonical owner:** NEW `form/dell_matrix/harmony.py`
- **Real caller:** proof (initially); public path `Program.harmony_of` (`form/open.py`); integration consumers in 3.5 per W1 (verified in Phase B)
- **Expected behavior:** `harmony_score(idea_set)` ∈ [0,1]; high when ideas are pairwise coherent but not identical
- **Failure behavior:** Empty set → 0.0; single idea → defined (solo coherence)
- **Proof:** `p3_r32_harmony_proof.py`
- **Disposition:** IMPLEMENT (new module with operational definition)

### 3.2.2 Harmonic naming cleanup (lattice/core/link renamed to what they are)
- **Contract:** N/A (renaming for honesty)
- **Canonical owner:** N/A
- **Real caller:** Various
- **Expected behavior:**
  - `HarmonicLattice` → document as "3D coordinate cell store" (keep name, add honest docstring) OR rename
  - `harmonic_core.py` → document as "pulse constants and key bookkeeping"
  - `harmonic_link.py` → DEAD, remove or mark deprecated
  - `_harmonic` (ringed_growth) → rename to `_coherence_blend` or document as "Jaccard-tension combiner (not musical)"
- **Failure behavior:** N/A
- **Proof:** Code review
- **Disposition:** IMPLEMENT (honest documentation + dead code removal)

### 3.2.3 Harmony computation with contract + tests
- **Contract:** Mathematical admission contract (8 fields)
- **Canonical owner:** NEW `form/dell_matrix/harmony.py::harmony_score`
- **Real caller:** Proof only (initially)
- **Expected behavior:** Defined formula with documented variables, domain, invariants
- **Failure behavior:** Degenerate inputs → defined outputs (0.0 or solo score)
- **Proof:** `p3_r32_harmony_proof.py` — bounds, symmetry, monotonicity, degenerate cases. **P3R permutation record (empirically verified 2026-10-04):** `harmony_score` is NOT bitwise permutation-invariant — pair sums accumulate in input order, so 7456/16252 random permutations differed at the last ulp. Honest guarantee: permutation equality within float tolerance (~1e-15 relative), NOT bitwise. (The harmony.py docstring's "Symmetric: permuting the input order never changes the result" is bitwise-false; flagged for W1/W2 correction — harmony.py is outside W3 ownership.) **P3R bypass requirement (Director's explicit test):** the rewritten proof monkeypatches `exclude_faded` out of `harmony_score`; the proof MUST FAIL (faded ideas must leak back in). Removing the filter and still passing is vacuity.
- **Disposition:** IMPLEMENT

### 3.2.4 Harmony vs resonance separation proven
- **Contract:** N/A (separation proof)
- **Canonical owner:** N/A
- **Real caller:** N/A
- **Expected behavior:** Demonstrate that harmony_score and _affinity measure different things (counterexample: high affinity pair with low set harmony, and vice versa)
- **Failure behavior:** N/A
- **Proof:** `p3_r32_harmony_proof.py` — separation test with concrete counterexample
- **Disposition:** IMPLEMENT

### 3.2.5 Public-path proofs
- **Contract:** Harmony accessible via public path (REPL or Program method)
- **Canonical owner:** `form/open.py::Program.harmony_of` (thin public wrapper over `harmony_score`)
- **Real caller:** proof; `Program.harmony_of` public API (no REPL command wires it yet — honest: reachable via Program, not via a REPL verb)
- **Expected behavior:** `harmony_of` matches `harmony_score` on Idea objects and plane unit IDs (units resolved against the program's cube plane; faded units excluded via lifecycle passthrough)
- **Failure behavior:** Unknown unit IDs → 0.0 (fail-closed, never raises); None/non-iterable input → 0.0
- **Proof:** `p3_r32_harmony_proof.py` — public-path test
- **Disposition:** IMPLEMENT (minimal public wiring)

---

## R3.3 — Verita transformation layer (where justified)

### 3.3.1 Decide: build the transformation layer or park it (Director)
- **Contract:** N/A (decision)
- **Canonical owner:** Director
- **Real caller:** N/A
- **Expected behavior:** Explicit decision with rationale
- **Failure behavior:** N/A
- **Proof:** Decision record in ledger
- **Disposition:** **PARK** (recommendation: no mathematical derivation exists, no proven consumers, spatial positions are vacuous (all ideas at 0,0). Building would be pseudomathematics.)

### 3.3.2–3.3.5
- **Disposition:** **PARKED** (contingent on 3.3.1; explicit rationale recorded)

---

## R3.4 — Information geometry (where justified)

### 3.4.1 Replace heuristic verita with defined overlap metric; unify duplicate vesica_strength
- **Contract:** Mathematical admission contract (8 fields)
- **Canonical owner:** `form/dell_matrix/sacred_geometry.py::vesica` (EQ-GEO-001, live authority)
- **Real caller:** `verita_between_nodes` ← `open.py:verita_edges` ← English "verita" command; `graph_view.py`
- **Expected behavior:** `verita.vesica_strength` delegates to `sacred_geometry.vesica` (or is removed). One canonical overlap implementation.
- **Failure behavior:** Invalid inputs (negative radii, NaN) → defined behavior
- **Proof:** `p3_r34_geometry_proof.py` — delegation test, identical outputs, invalid input handling
- **Disposition:** IMPLEMENT (unify; R4-A1 finally executed)

### 3.4.2 Čech nerve as higher-order relationship model (only with proven consumers)
- **Contract:** Mathematical admission contract
- **Canonical owner:** NONE
- **Real caller:** NONE (no proven consumers)
- **Expected behavior:** N/A
- **Failure behavior:** N/A
- **Proof:** N/A
- **Disposition:** **DEFER** (explicit: no consumers; would be speculative architecture)

### 3.4.3 Power diagrams for weighted ideas (exclusive vs shared volume)
- **Contract:** Mathematical admission contract
- **Canonical owner:** NONE
- **Real caller:** NONE
- **Expected behavior:** N/A
- **Failure behavior:** N/A
- **Proof:** N/A
- **Disposition:** **DEFER** (explicit: no consumers; spatial positions vacuous)

### 3.4.4 Alpha filtration for void lifecycle (only with proven consumers)
- **Contract:** Mathematical admission contract
- **Canonical owner:** NONE
- **Real caller:** NONE
- **Expected behavior:** N/A
- **Failure behavior:** N/A
- **Proof:** N/A
- **Disposition:** **DEFER** (explicit: no consumers)

### 3.4.5 Negative-space channels remain declared-future; never display uncomputed regions
- **Contract:** N/A (policy)
- **Canonical owner:** N/A
- **Real caller:** N/A
- **Expected behavior:** No UI/code displays uncomputed geometric regions
- **Failure behavior:** N/A
- **Proof:** Code review (grep for uncomputed region display) + `p3_r34_geometry_proof.py` failure-handling phase. **P3R bypass requirement (Director's explicit test):** the rewritten proof forces the geometry call to raise (monkeypatch) and asserts (a) NO fabricated edges are emitted and (b) an explicit unavailable marker is surfaced instead. If the code falls back to returning fabricated edges, the proof MUST FAIL (exit non-zero). The known graph_view.py exception-fallback finding (emits uncomputed kind="vesica" edges) is W2 territory; the proof pins the honest contract against W2's final implementation.
- **Disposition:** IMPLEMENT (verify policy holds; document)

---

## R3.5 — Resonance/harmony integration

### 3.5.1 Resonance/harmony feed selection/growth/Nursery through honest contracts
- **Contract:** Selection → Growth handoff must be explicit about what flows (currently IDs only)
- **Canonical owner:** `form/mandell/knowledge_selector.py` (selection), `form/dell_matrix/ringed_growth.py` (growth), `form/dell_matrix/nursery.py` (Nursery)
- **Real caller:** `core_i_ops.py:567` (`grow_using_knowledge_about`)
- **Expected behavior:** Per Director P3R: IMPLEMENTED via W1 (selection→growth wiring beyond the IDs-only handoff). The prior "document honest contract" posture is superseded. The exact contract is verified against W1's final implementation in the Phase-B proof rewrite.
- **Failure behavior:** Per W1 implementation (concurrent); verified in the Phase-B proof rewrite.
- **Proof:** `p3_r35_integration_proof.py` — handoff contract test (rewritten Phase B, non-vacuous; includes a graph/harmony-consumption bypass-must-fail: bypassing the consumer must fail the proof)
- **Disposition:** IMPLEMENTED (Director decision P3R; W1 implementing)

### 3.5.2 Faded-state exclusion honored in resonance computation
- **Contract:** FADED ideas must be excluded from resonance/affinity computation
- **Canonical owner:** `form/mandell/idea.py::LifecycleState`
- **Real caller:** `_affinity`, `pulse`, `harmony_score`
- **Expected behavior:** Ideas with lifecycle_state=FADED are excluded from pair scoring and diffusion
- **Failure behavior:** All ideas faded → empty result (not error)
- **Proof:** `p3_r35_integration_proof.py` — faded exclusion test. **P3R bypass requirement (Director's explicit test):** disabling/removing the faded filter (monkeypatched `is_faded` → False / `exclude_faded` → identity) MUST make the proof FAIL — faded ideas must leak back into `_affinity`, `pulse`, and `harmony_score`. A proof that stays green with the filter removed is vacuous and rejected.
- **Disposition:** IMPLEMENT

### 3.5.3 Outcome/observation of resonance effects
- **Contract:** Resonance effects must be observable via Outcome/observation
- **Canonical owner:** `form/mandell/execution_observer.py::observe_seed_execution` (EOC-I adapter path)
- **Real caller:** the Mandell seed front door (`form/mandell/executor.py::execute_seed` — the same path the REPL dispatches Mandell seeds through)
- **Expected behavior:** When resonance/affinity influences a decision, an Outcome V1 records it: consumed knowledge provenance (routable IDs), the effect summary in messages ("New proposals:"), and the consumer-computed affinity/parents/reason on the nursery proposals.
- **Failure behavior:** Documented limitation (recorded, not asserted as failure): the Outcome record does not carry per-pair affinity values or gate decisions — those live on nursery proposals and last_nurture, which are not frozen into the outcome. No new Outcome subsystem is built (out of scope per DIVG-I).
- **Proof:** `p3_r35_integration_proof.py`
- **Disposition:** IMPLEMENT (or document if already present)

### 3.5.4 Public-path proofs
- **Contract:** Integration accessible via public path
- **Canonical owner:** `form/mandell/executor.py::execute_seed` (+ `form/mandell/execution_observer.py::observe_seed_execution`)
- **Real caller:** the REPL's Mandell-seed dispatch path (execute_seed is the front door)
- **Expected behavior:** `observe_seed_execution(p, "37[Nurture] :: grow_using_knowledge_about …")` → ok; Outcome V1 observed (`p.last_outcome`); nurture receipt with action == "grow_contextual"
- **Failure behavior:** Isolated owner state: state dirs verified absent before the phase and removed after; any residue fails the phase.
- **Proof:** `p3_r35_integration_proof.py`
- **Disposition:** IMPLEMENT

### 3.5.5 Integration with Phase-2 graph
- **Contract:** Phase-2 semantic graph should inform or be informed by resonance
- **Canonical owner:** `form/mandell/semantic_graph.py`
- **Real caller:** NONE (currently zero integration)
- **Expected behavior:** Per Director P3R: IMPLEMENTED via W1 (Phase-2 graph ↔ resonance integration). The prior "DEFER with rationale" posture is superseded. The exact contract is verified against W1's final implementation in the Phase-B proof rewrite, including a graph/harmony-consumption bypass-must-fail (bypassing the consumer must fail the proof).
- **Failure behavior:** Per W1 implementation (concurrent); verified in the Phase-B proof rewrite.
- **Proof:** `p3_r35_integration_proof.py` (+ W1's `form/mandell/p3_r36_graph_harmony_proof.py`, audited by W3 in Phase B for vacuity)
- **Disposition:** IMPLEMENTED (Director decision P3R; W1 implementing)

---

## P3R Consolidated Repair Record (2026-10-04, Worker 3 — Proofs + Contracts)

Director's findings and their resolution in this matrix:

1. **Vacuous proofs (faded-filter removal still green):** resolved by the bypass-must-fail requirements recorded in 3.1.1, 3.2.3, 3.5.2, and 3.4.5 (proof lines). Phase-B proof rewrites (`p3_r31`/`p3_r32`/`p3_r34`/`p3_r35`) are non-vacuous: content-bearing canonical fixtures, hand-computed expected values asserted in comments, and meta-tests proving that bypassing lifecycle handling, graph/harmony consumption, or geometry failure handling makes the proof FAIL.
2. **Contradictory affinity bounds:** resolved in 3.1.1 — the honest bound is affinity ≤ 1.0 when body_boost == 0.0, ≤ 1.15 theoretical with body_boost active; the old "∈ [0,1]" is withdrawn. (W1 updates the `_affinity` docstring; this matrix matches.)
3. **Missing-unit behavior:** resolved in 3.1.1 — affinity is 0.0273 (repr-verified: 0.13/(1+99) + 0.13×0.2), not 0.0; fail-closed in effect via the STANSTILL_AFFINITY (0.10) "None" gate.
4. **Serendipity caller/range:** resolved in 3.1.3 — range [0,1); consumer is `_affinity` via `_harmonic`'s tension term (0.40 weight); the named `serendipity()` is the exposed normalized form (code-verified: `_harmonic` uses `_tension` directly).
5. **Permutation guarantees:** resolved — `_affinity`'s output dict is bitwise identical under argument permutation (0 mismatches / 2974 random ordered pairs); `harmony_score` is NOT bitwise (last-ulp summation-order differences observed: 7456/16252) — the honest guarantee is equality within float tolerance (~1e-15 relative). Recorded in 3.1.1 and 3.2.3.
6. **Disposition updates per Director:** 3.5.1 and 3.5.5 are IMPLEMENTED via W1 (prior document/DEFER postures superseded); 3.3.1 PARK and 3.4.2–3.4.4 DEFER approved — kept. W1's implementation is verified in the Phase-B proof rewrite, not in this matrix.
7. **All TBDs resolved:** 3.1.4 (owner `nursery._slug`; seeded SHA-256 IDs deterministic across processes), 3.2.1 (real caller: proof + `Program.harmony_of`), 3.2.5 (owner `Program.harmony_of`; unknown IDs → 0.0), 3.5.3 (owner `execution_observer.observe_seed_execution`; Outcome V1 records knowledge provenance + effect summary; documented limitation: no per-pair affinity values in the outcome), 3.5.4 (owner `executor.execute_seed`; isolated owner state), 3.5.5 (expected per W1).

Preserved: Verita PARK (3.3.1), geometry DEFERRALs (3.4.2–3.4.4). No Verita or geometry-deferral record was altered.

---

## Inactive Scratch (excluded from Phase-3 work and evidence)

Per Overseer directive 2026-10-04: leave untouched, record as inactive.

- `~/workspace/dellmatrix-fresh-main15` — untracked DCC-XV cross-process test (DCC-era scratch)
- `~/workspace/dellmatrix-fresh-main6` — modified `core_i_ops.py` (+56/-8) (DCC-era scratch)

Neither is referenced by any active directive. Excluded from Phase-3 evidence.
