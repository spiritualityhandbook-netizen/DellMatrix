# GDP-001 Phase 3 Acceptance Matrix

**Program:** GDP-V1 · **Phase:** 3 — Resonance, Harmony & Information Geometry
**Baseline:** `ebfd68b6234de1bae8e60bed1bc380f30e425b39`
**Authority:** OVERSEER > DIRECTOR > UNI
**Status:** FINAL — archaeology complete, dispositions set

Each objective: contract, canonical owner, real caller, expected behavior,
failure behavior, proof, disposition.

---

## R3.1 — Affinity/resonance reconciliation

### 3.1.1 `_affinity` exposed as first-class service with contract
- **Contract:** Mathematical admission contract (8 fields). Inputs: two idea IDs + plane. Output: dict with affinity ∈ [0,1], jaccard, harmonic, distance, shared, goal_boost, body_boost.
- **Canonical owner:** `form/dell_matrix/ringed_growth.py::_affinity` (live authority)
- **Real caller:** `RingedGrowth.run()` (line 260) ← `Program.grow_ideas` ← REPL growth commands
- **Expected behavior:** Deterministic composite: 0.40×harmonic + 0.22×jaccard + 0.13×spatial + 0.13×in_scope + goal_boost + body_boost
- **Failure behavior:** Missing units → returns dict with affinity 0.0 (fail-closed, no exception)
- **Proof:** `p3_r31_affinity_proof.py` — determinism, bounds, failure cases, live-path witness
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
- **Canonical owner:** `ringed_growth.py::_harmonic` (tension subterm)
- **Real caller:** `_affinity` (weight 0.40)
- **Expected behavior:** Serendipity = tension/(1+tension) ∈ [0,1]; high when pairs share little but have complementary exclusive tokens
- **Failure behavior:** Empty sets → 0.0
- **Proof:** `p3_r31_affinity_proof.py` — serendipity bounds, monotonicity
- **Disposition:** IMPLEMENT (expose tension as named serendipity metric)

### 3.1.4 Seeded RNG for deterministic growth IDs
- **Contract:** Growth IDs must be deterministic given (seed, inputs)
- **Canonical owner:** TBD (investigate current ID generation)
- **Real caller:** `RingedGrowth.run` / `nursery.add`
- **Expected behavior:** Same inputs + same seed → same IDs
- **Failure behavior:** TBD
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
- **Real caller:** TBD (initially: proof only; integration in 3.5)
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
- **Proof:** `p3_r32_harmony_proof.py` — bounds, symmetry, monotonicity, degenerate cases
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
- **Canonical owner:** TBD
- **Real caller:** TBD
- **Expected behavior:** User can invoke harmony computation through supported interface
- **Failure behavior:** TBD
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
- **Proof:** Code review (grep for uncomputed region display)
- **Disposition:** IMPLEMENT (verify policy holds; document)

---

## R3.5 — Resonance/harmony integration

### 3.5.1 Resonance/harmony feed selection/growth/Nursery through honest contracts
- **Contract:** Selection → Growth handoff must be explicit about what flows (currently IDs only)
- **Canonical owner:** `form/mandell/knowledge_selector.py` (selection), `form/dell_matrix/ringed_growth.py` (growth), `form/dell_matrix/nursery.py` (Nursery)
- **Real caller:** `core_i_ops.py:567` (`grow_using_knowledge_about`)
- **Expected behavior:** Document the handoff contract: selection provides ID set; growth computes affinity independently. OR: wire selection scores into growth (if justified).
- **Failure behavior:** TBD
- **Proof:** `p3_r35_integration_proof.py` — handoff contract test
- **Disposition:** IMPLEMENT (document honest contract; wire scores only if justified)

### 3.5.2 Faded-state exclusion honored in resonance computation
- **Contract:** FADED ideas must be excluded from resonance/affinity computation
- **Canonical owner:** `form/mandell/idea.py::LifecycleState`
- **Real caller:** `_affinity`, `pulse`, `harmony_score`
- **Expected behavior:** Ideas with lifecycle_state=FADED are excluded from pair scoring and diffusion
- **Failure behavior:** All ideas faded → empty result (not error)
- **Proof:** `p3_r35_integration_proof.py` — faded exclusion test
- **Disposition:** IMPLEMENT

### 3.5.3 Outcome/observation of resonance effects
- **Contract:** Resonance effects must be observable via Outcome/observation
- **Canonical owner:** TBD
- **Real caller:** TBD
- **Expected behavior:** When resonance/affinity influences a decision, an Outcome records it
- **Failure behavior:** TBD
- **Proof:** `p3_r35_integration_proof.py`
- **Disposition:** IMPLEMENT (or document if already present)

### 3.5.4 Public-path proofs
- **Contract:** Integration accessible via public path
- **Canonical owner:** TBD
- **Real caller:** TBD
- **Expected behavior:** TBD
- **Failure behavior:** TBD
- **Proof:** `p3_r35_integration_proof.py`
- **Disposition:** IMPLEMENT

### 3.5.5 Integration with Phase-2 graph
- **Contract:** Phase-2 semantic graph should inform or be informed by resonance
- **Canonical owner:** `form/mandell/semantic_graph.py`
- **Real caller:** NONE (currently zero integration)
- **Expected behavior:** TBD (investigate: should graph edges influence affinity? Should affinity create graph edges?)
- **Failure behavior:** TBD
- **Proof:** `p3_r35_integration_proof.py`
- **Disposition:** IMPLEMENT (minimal honest integration) or DEFER with rationale
