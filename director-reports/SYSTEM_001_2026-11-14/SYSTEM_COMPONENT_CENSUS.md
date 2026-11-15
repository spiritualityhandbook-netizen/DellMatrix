> **Deliverable 2 of SYSTEM-001 (DIR-DM-SYSTEM-001) — runtime component census at pin 62bdcbc.**

# SYSTEM-001 — LANE 1: RUNTIME COMPONENT CENSUS

**Directive:** DIR-DM-SYSTEM-001, initial circuit SYSTEM-001 (whole-system census + contract map).
**Lane:** 1 — runtime components of the `form/` tree.
**Pin (verified by `git rev-parse HEAD` in the clone):** `62bdcbcbb53396b87d5884e4fecbd6f8ac8ab239`, clone `~/workspace/sys001_clone`, read-only throughout.
**Method:** directory/AST scan of all 487 `form/**/*.py`; docstring extraction; AST import-frequency count; targeted grep for state paths, write mechanisms, `def main` / `__main__` entrypoints, and per-module references. Machine-readable fragment: `LANE1_GRAPH.json` (86 nodes, 27 edges — grep/AST-derived, best-effort).
**Caveats (load-bearing):** (1) AST import counting **undercounts** consumers — this codebase also loads modules via `importlib.import_module(...)` string references, subprocess child scripts, and the `form.regress` manifest (292 `form.` references in `form/regress.py` alone); a module with zero AST importers is therefore an orphan *candidate*, never a proven orphan. (2) Test coverage below is by test-file naming/import association, not by running anything — this lane executed no tests. (3) Task figure says 253 test files; a name scan finds 253 `*test*`-named files and 274 test/proof-like files (the difference is `*_proof` scripts in `form/mandell/`). Both numbers are recorded; neither was forced.

## Counts

| Scope | .py total | non-test |
|---|---|---|
| `form/` (top level) | 117 | 22 |
| `form/mandell/` (+ `diagnostics/`) | 254 | 102 |
| `form/dell_matrix/` | 101 | 95 |
| `form/duobeta/` | 3 | 3 |
| `form/llm/` | 3 | 3 |
| `form/avatar/` | 4 | 4 |
| `form/worldwide/` | 2 | 2 |
| `form/ancient/` | 2 | 2 |
| `form/matrices/` | 0 | 0 (README only) |
| **Total** | **487** | **213 non-test-like / 274 test-and-proof-like** |

Status classes used: **ACTIVE** (consumers + entrypoint or central role evidenced) · **ACTIVE_UNVERIFIED** (present and referenced, but this lane found no direct coverage/behavior evidence) · **HISTORICAL_ONLY** (build-time, retired, or legacy by its own docstring) · **ORPHAN_CANDIDATE** (zero consumers found by AST+grep scan; see caveat 1) · **TEST_ONLY** (exists only as test/proof harness — the 274 test/proof files as a class; individually listed only in the graph's absence, see §9).

---

## 1. Top-level `form/*.py` — the program shell (22 non-test modules)

The top level is the operating shell: front door, REPL, persistence, regression authority, and build-time LatinMandell tooling.

| Module | Purpose / capability | Canonical data owned | Entrypoints | Persistence | Consumers (evidence) | Tests | Class |
|---|---|---|---|---|---|---|---|
| `form/__main__.py` | `python -m form → open the program` (its docstring) | none | `python -m form` | — | interpreter | via regress (`form.open` entry) | ACTIVE |
| `form/open.py` | "One program — Form front door with Avatar + Ringed Growth Nursery + HarmonicLattice." Hosts `class Program` (:103), `open_program()` (:2194), `main()` (:2247), `smoke()` (:2222) | **Program live state** — the in-memory canonical session every other subsystem hangs off | `main()`, `open_program(owner)`, `Program` | delegates to `form.persist`/`persist_rest` | **347 files import `form.open`** (AST count — the most-imported module in the tree; mostly tests + `persist_rest` + `repl`) | nearly the whole suite; regress LIST head entry is `form.open` | ACTIVE |
| `form/repl.py` | "REPL — Mandell Origin. English, seeds, lattice, polyglot, LatinMandell depth." `main()` :4927; handlers incl. `_handle_latinmandell`, `_handle_studio_line`, `_dispatch_public_line`, learn/why/group/containment handlers | none — derived (drives Program) | `python -m form.repl`; interactive REPL (English lines, Mandell seeds, commands) | via Program/persist | imported by tests (e.g. `repl_seed_error_visibility_test.py`) | `form/repl_seed_error_visibility_test.py`; dcc/p-series suites exercise it via subprocess | ACTIVE |
| `form/persist.py` | "Persist v7 — matrix + avatar + nursery + lattice + history + LatinMandell customs + idea detail/goals." Defines `_STATE_DIR` (:36, `form/state`, created at import), `VERSION = 7`, `_path(owner)` → `program_{owner}.json`, `serialize()` | **The v7 program document schema + the `form/state` directory authority** — every other persistence module imports `_STATE_DIR`/`_safe_owner` from here | `serialize(program)`; re-exports save/load via `__getattr__` to `persist_rest` | see `persist_rest` | **194 AST importers** | `form/persist_full_roundtrip_test.py`, `sm35_pair_atomic_test.py`, checkpoint/recovery suites | ACTIVE |
| `form/persist_rest.py` | Save/load/checkpoint implementation bound from persist.py: `save()` :120, `checkpoint()` :166, `load()` :314, `_write_program_file()` :101, binding-loss refusal (`_refuse_if_binding_loss`), `durable()`, `smoke()`, `main()` :1058 | The write/read mechanism for the v7 document | `save/load/checkpoint/list_checkpoints` | **Writes `form/state/program_{owner}.json`; checkpoints `program_{owner}_cp_{stamp}.json`**; write path goes through the atomic-write primitive + owner lock (imports evidence) | 42 AST importers (`form.persist` module) | as persist.py | ACTIVE |
| `form/persist_core_ii.py` | "Core II durable persist helpers. v7 document stays version 7." `CORE_II_DURABLE` field set (scope/selected/store/groups/defs/aliases/compositions/weights/context/route/refs/causes/deps/last_assert/last_guard) | The Core II durable field contract inside the v7 document | helpers only | inside `program_{owner}.json` | persist.py imports it | `form/core_ii_version_validation_test.py`, `form/mandell/core_ii_persist_test.py` | ACTIVE |
| `form/owner_state_lock.py` | "Owner-state lock — the single concurrency authority for" owner state (docstring) | The owner write lock | lock context/API | lock files under `form/state` (owner-scoped) | checkpoint/persist writers (grep) | `form/owner_namespace_collision_test.py` | ACTIVE |
| `form/regress.py` | "Canonical regression authority (one list, one runner)." Each entry runs in its own process inside ONE private temp copy of the tree (fresh `form/state`) | none — derived | `python -m form.regress [--order rev \| --twice \| --passk ENTRY K]` | temp copy only; never writes the checkout | CI + all lanes | self-verifying manifest (LIST + every `*_test.py` coverage rule) | ACTIVE |
| `form/accept.py` | "One-click offline acceptance path." | none | `__main__` script (:73) | UNKNOWN | grep: no significant importers found | `form/foundation_acceptance_test.py` (topical) | ACTIVE_UNVERIFIED |
| `form/grow.py` | "Turn self-grow on." | none (switch) | script entry | — | UNKNOWN | `form/growth_persistence_test.py` (topical) | ACTIVE_UNVERIFIED |
| `form/give_blank.py` | "Give a blank Dell Matrix to someone." (`blank_cube.py` is the in-matrix counterpart) | none | script entry | writes `form/state/START_{owner}.txt` (:44-45) | none found | none found | ACTIVE_UNVERIFIED |
| `form/greek.py` | "Greek operators — the Mandell floor made public (C1 corrected)." | none — derived | public functions | — | UNKNOWN | `form/greek_test.py` | ACTIVE_UNVERIFIED |
| `form/idea_create.py` | "Parse and validate idea create lines: label + detail + goals. Strong-idea law." | none — derived | parse/validate API | — | referenced in executor/leaf comments; used by create paths | seed/idea suites | ACTIVE |
| `form/invariants.py` | "SUS invariants — runnable hard checks." | none | runnable checks | — | **none found** | none found | ORPHAN_CANDIDATE |
| `form/lifecycle.py` | "TPP-I: Temporal Presence Projection I (NBD-Ω-048)" | UNKNOWN — not isolated in this scan | UNKNOWN | UNKNOWN | UNKNOWN | lifecycle-named suites exist (`resonance_lifecycle_gate_test.py` is topical, not proven coverage) | ACTIVE_UNVERIFIED |
| `form/seed_strong_ideas.py` | "Plant strong foundation ideas (detail + goals) into a profile session." | none (plants via Program) | script entry | via Program/persist | **none found** | none found | ORPHAN_CANDIDATE |
| `form/utc_time.py` | "The one UTC timestamp helper (P3 / TD-7)." | none — derived | helper API | — | dell_matrix session modules (grep) | UNKNOWN | ACTIVE |
| `form/lm1_import.py` / `form/lm1_harvest.py` / `form/lm2_census_build.py` | LM-1 external import (Wikipedia roots) / harvest-only table builder / LM-2 census export — all self-described **build-time only** | LM table build artifacts | build scripts | `form/mandell/lm_table_v1.json` + `.collisions.json` (lm1_harvest :23-24, :68) | their own tests | `form/lm1_import_test.py`, `lm1_harvest_test.py`, `lm2_splitter_test.py` (LM-2) | HISTORICAL_ONLY (build-time; the built table is live data, the builders are not runtime) |

## 2. `form/mandell/` — the language core (102 non-test modules)

Docstring of the package: "Mandell — language core. Most foundational layer." This is the largest subsystem: seed language, registry, executors, Core I/II, semantic graph, knowledge lifecycle, LatinMandell, and the persistence/recovery machinery for ideas and checkpoints. Only significant modules are itemized; the remaining ~60 non-test modules are smaller NBD/circuit components (bounded_orbit, correction_graph, nbd_engine, patterns, phrases, polyglot, spectrum/query ops, etc.) — present, mostly ACTIVE_UNVERIFIED as a class, and enumerated in the AST scan underlying the graph fragment.

| Module | Purpose | Canonical data owned | Entrypoints | Persistence | Consumers | Tests | Class |
|---|---|---|---|---|---|---|---|
| `registry.py` | "True Dell registry — numbered operators + manors." `get_dell/lookup/namespace_of/active_core_count/execution_standing` | **The Dell registry itself** (Dells 00–99 + 100-series per address_space) | API | none (in-code data) | executor, semantic_router, dell_cards; r2 reconciliation suite | `r2_registry_reconciliation_test.py`, d1_registry_* suites | ACTIVE |
| `seed.py` | "Mandell seed language — parse, validate, explain. Atoms: 08[Create] or 151[Harmonic]." | none — derived | parse/validate/explain API | — | 27 AST importers | `form/seed_grammar_stress_test.py`, phrase suites | ACTIVE |
| `executor.py` | "Mandell seed executor — front door." | none — derived | execute API | — | **128 AST importers** (second only to form.open among mandell modules) | executor/dcc suites extensively | ACTIVE |
| `executor_leaf.py` | "Mandell seed executor — dense Dell coverage." | none — derived | leaf handlers | — | referenced by executor path + tests (`dd14_loop_body_test.py`, `dirf13_loop_count_test.py` name it the owner of `_parse_count`); AST scan undercounts it | d1_* per-Dell suites | ACTIVE |
| `chain_exec.py` | "Multi-atom Mandell execution with control frames and flow contracts." | in-memory control frames | chain API | — | control_runtime/flow consumers | dcc suites, `g31_contract_test.py` | ACTIVE |
| `flow_executor.py` | "DCC-IV: Composed Mandell program execution via verified flow operators." Owns `FLOW_CLASSIFICATION` (the seven fail-closed refusals) | none — derived | composed execution API | — | english_composer, repl DCC-IV branch | `flow_executor_test.py`, `r2_semantic_honesty_test.py` | ACTIVE |
| `control_runtime.py` | "Deterministic Core II control predicates and frames. No eval. No threads." Holds `FLOW_CONTRACT` + the G31 `FLOW_PROFILES` annotation | The flow vocabulary contract (annotation layer) | predicates/frames API | — | chain_exec, flow tests | `control_runtime_test.py`, `g31_contract_test.py` | ACTIVE |
| `core_ii.py` / `core_ii_exec.py` | Core II definition ("Dells 51-99 instruction architecture") / "Core II runtime 51-99. Formalized executable state." | Core II executable state (in-memory) | exec API; `core_ii_smoke.py` standalone smoke | serialized via `persist_core_ii` into the v7 document | 63 AST importers of core_ii_exec | `core_ii_persist_test.py`, `core_ii_smoke.py`, dcc suites | ACTIVE |
| `core_i_ops.py` / `core_i_recovery.py` | Core I arms wrapping the leaf / "Core I 27/28 program checkpoints. Distinct from Core II 93-96 transactions." Recovery owns rollback/confirm/checkpoint/supersede **journals** | **Core I checkpoint + journal authority** | recovery APIs | `form/state/rollback_{owner}.journal.json`, `confirm_…`, `checkpoint_…`, `supersede_…`, `*.staging` (module grep) | 91 AST importers of core_i_recovery | checkpoint_generation_stress, dirf12, confirm suites | ACTIVE |
| `checkpoint_generation.py` | "DCC-XVIII: Coherent checkpoint generations + cross-file recovery." `commit_checkpoint/load_checkpoint/committed_generation_state` | **Checkpoint generations**: pointer + manifests + sealed members, current+previous retention | API | `form/state/current_{owner}.json`, `gen_{owner}_{id}.json`, `{kind}_{owner}.g_{id}.json` | 35 AST importers | `form/checkpoint_generation_stress_test.py`, graph_journal_crash | ACTIVE |
| `semantic_graph.py` | "GDP-001 Phase 2 — Canonical Semantic Graph authority." RelationshipEntry/journal validation, propagation | **The canonical semantic graph + its journal** | `SemanticGraph` API | graph file + journal under `form/state` (`graph_path`/`graph_journal_path` in module), atomic write | 44 AST importers | p2_graph, p3_r36, graph_journal_crash suites | ACTIVE |
| `semantic_router.py` | "Typed Mandell -> Dell semantic routing boundary (DCC-II)." | none — derived | routing API | — | 53 AST importers | semantic_route suites | ACTIVE |
| `idea.py` | "Canonical Idea — GDP-001 Phase 1, Requirement 1.1." Idea/LifecycleState/Provenance/PropertyVersion/IdeaChangeEvent | **The canonical Idea type** (identity, lifecycle, provenance) | data API | — | 34 AST importers | p1 idea circuit suites | ACTIVE |
| `idea_persist.py` / `idea_checkpoint.py` | Idea persistence (Req. 1.1.5) / checkpoint integration (MF-5) | per-owner idea records / idea checkpoints | helpers | `form/state/ideas_{owner}` and `ideas_{owner}.json`; `ideas_rehydrate_{owner}.pending` | 38 AST importers of idea_persist | snapshot/idea suites | ACTIVE |
| `supersession.py` | "DCC-XVI: Versioned knowledge supersession + revision lifecycle (Supersession V1)." | supersession lifecycle state (in Program) | API | journals via core_i_recovery | 35 AST importers | `supersession_lineage_restart_test.py`, `form/lineage_*` | ACTIVE |
| `knowledge_selector.py` / `knowledge_lineage.py` / `knowledge_influence.py` | Deterministic contextual selector (Relevance V2) / evidence lineage (Lineage V1) / "KIE-I read-only explanation layer" | none — derived (selection); lineage records; none (explanation is read-only by design) | APIs | UNKNOWN for lineage | selector: kie_i suite; influence: **no importers found** | `kie_i_test.py` | selector ACTIVE; lineage ACTIVE_UNVERIFIED; **influence ORPHAN_CANDIDATE** |
| `translate.py` / `bridge.py` / `polyglot.py` | "45[Translate] — English → Mandell" / bidirectional bridge / natural languages → same Dell layer | none — derived | translate API | — | 69 AST importers of translate | `form/translate_*_test.py`, polyglot suites | ACTIVE (bridge/polyglot ACTIVE_UNVERIFIED) |
| `english_composer.py` / `english_brain.py` | English multi-step → Mandell program → DCC-IV execution (`execute_composite`) / natural-English understanding | none — derived | composer API | — | composer: dcc/flow path; brain: UNKNOWN | `english_composer_test.py` | composer ACTIVE; brain ACTIVE_UNVERIFIED |
| `latinmandell.py` (+ `lm_table.py`, `morpheme.py`) | "LatinMandell — core morphological depth layer." LM-4 toll-booth reading runs in the repl path (prior verified work) | the LM table **data** (`lm_table_v1.json`, built by the §1 build tools); curated definitions govern per doctrine | decomposition/composition API | reads the JSON table | latinmandell: repl + lm suites; **lm_table loader: no direct importers found in scan** | `form/lm4_tollbooth_test.py`, `lm2_splitter_test.py`, `lm3_composer_test.py` | latinmandell ACTIVE; **lm_table ORPHAN_CANDIDATE** (may load via latinmandell internals — scan-inconclusive) |
| `floor.py` | "Floor — immutable. More foundational than Dell Matrix." | **The Floor** (foundational constants) | `FLOOR`, `assert_floor_intact`, `floor_status` | — | 38 AST importers | floor/foundation suites | ACTIVE |
| `circuit_ledger.py` | "Canonical Circuit Ledger — ONE current state authority for DellMatrix." (docstring claim) | claims a ledger authority — **conflict note:** overlaps persist/checkpoint authorities; no production importer found, only test importlib use (`p3_wiring_test.py`, `cdpc_i_test.py`) | ledger API | UNKNOWN | tests only (grep) | cdpc/fcnd suites | ACTIVE_UNVERIFIED — authority overlap flagged for Lane-contract work |
| `unit_binding.py` / `unit_containment.py` | TD-1 Plane Unit → canonical Idea binding / TD-2 containment operations | binding records / containment state (on Plane units) | APIs | via Program | repl containment handlers | `form/track_d_td1*/td2` suites | ACTIVE |
| `dell_cards.py` | "D1 proof cards — a survey of every Dell in the registry." | none — derived | `build_card` API | builds against an owner state dir and cleans it (`_cleanup`) | registry consumers | d1_proof_cards suite | ACTIVE_UNVERIFIED |
| `language.py` | "Mandell language authority: persist, evidence, plan, parser adapter." | claims a persist role — path not isolated in this scan: UNKNOWN | API | UNKNOWN | UNKNOWN | language_efficiency suite (topical) | ACTIVE_UNVERIFIED |
| `duobeta_learn.py` | "DBEL-I: DuoBeta Evidence Learning (NBD-Ω-007)." | learning records — UNKNOWN location | API | UNKNOWN | duobeta_cross_session suite (topical) | `duobeta_cross_session_test.py` | ACTIVE_UNVERIFIED |

## 3. `form/dell_matrix/` — the matrix runtime (95 non-test modules)

Package docstring is empty; the subsystem is the snap host + Plane + spatial/geometry + Nursery/growth + Studio surfaces + boards. Itemized: the significant ~30; the remaining ~65 are feature modules (personas, workshops, sessions, enhance/evolve 150-loops, inspire/needs/self-model, fourier/linear-algebra/logistic cores, view rooms, etc.) — mostly ACTIVE_UNVERIFIED as a class, several __main__-only (see §8).

| Module | Purpose | Canonical data owned | Entrypoints | Persistence | Consumers | Tests | Class |
|---|---|---|---|---|---|---|---|
| `core.py` | "Dell Matrix snap host — required set post-preform open." `DellMatrix` | host composition (in-memory) | `DellMatrix` | via Program | 338 package-level AST imports of `form.dell_matrix`; core imported across open/repl | `core_test.py`, p3_wiring | ACTIVE |
| `plane.py` | "Dell Matrix Plane — L3 surface." Perspective (incl. FLOWER), Skin, Unit, Sandbox, Plane; `smoke()`, `main()` | **Plane state**: units, perspectives, sandboxes (live) | API + `__main__` | serialized inside the v7 program document | 57 AST importers | cn_ii_nav, confirm_placement, TD suites | ACTIVE |
| `spatial_authority.py` | "Canonical Spatial Authority (GDP-001 Phase 4, Living Spatial Matrix)." Forces: mass/wells/separation/spring/center/weather | **Canonical positions/forces authority** | `SpatialAuthority` API | UNKNOWN (carried in Program/Plane serialization) | plane/growth consumers (grep) | saoc_ii suite (topical) | ACTIVE |
| `harmonic_lattice.py` | "H / V / F Harmonic Lattice + shared perception forms." Cell store (h,v,f) + note readings; `to_core/to_cube/to_sphere/to_flower` switch the *reading*; `plant_flower` inserts 2D Flower centers | none — **derived** coordinate store + perception forms (not a sphere model — THL-SM-01 verified) | `HarmonicLattice` API; `__main__` | serialized via persist (`_serialize_lattice`) | open.py front door, lattice consumers | p4_lattice_* proofs | ACTIVE |
| `sacred_geometry.py` | "Sacred geometry + structural pattern layer — form/ only." flower_centers/seed/fruit, vesica, verita_between_nodes, Rule-90/complex-orbit/Sierpinski generators | none — derived (pure functions) | API; `geometry_status`; `smoke()`; `__main__` | — | graph_view (ViewEdge vesica), plane FLOWER perspective, repl flower/vesica/verita commands | equation_ledger_invariants, fcnd suites | ACTIVE |
| `nursery.py` | "Nursery / Void / Op-Box." `Nursery`, `Proposal`, per-owner paths | **Nursery pending-proposal pool** | API | **`form/state/nursery.json`; `nursery_{owner}.json`** via atomic_write; `_STATE_DIR` created at import | **107 AST importers** | nursery_confirm_race, proposal suites | ACTIVE |
| `ringed_growth.py` | "Ringed Growth — sole public growth path. Body pulse first. Goals bias affinity." Owns `_harmonic()`/`_affinity()` (ledger EQ-RES-001/002, ACTIVE_UNVALIDATED) | growth state (in Program) | API; `__main__` | via Program/persist | open.py, growth suites | `form/growth_persistence_test.py`, water/forcefield suites | ACTIVE |
| `resonance.py` | "ResonanceAct L3." `harmonize_pair` — logs "vesica", computes no geometry (ledger EQ-RES-003 DISCONNECTED) | resonance state (in-memory) | API; `__main__` | UNKNOWN | resonance_command suite | `form/mandell/resonance_command_test.py` | ACTIVE_UNVERIFIED |
| `harmony.py` / `graph_harmony.py` | coherence degree of idea sets / graph+harmony integration (R3.6) | none — derived metrics | APIs | — | p3_r36 proof | p3_r36 suite | ACTIVE_UNVERIFIED |
| `atomic_write.py` | "Persistence V2: crash-safe JSON file replacement (DCC-XVII)." | none — **the** write primitive | write function | (mechanism) | 29 AST importers + persist_rest, nursery, checkpoint_generation, semantic_graph, core_i_recovery, idea_persist, exchange, confirm_lineage | `form/atomic_write_boundaries_test.py` | ACTIVE |
| `visual.py` | "Visual control panel — offline HTML UI. Shared actions · entities · pages · vision." + `assets/` (css/js/12 HTML pages) | none — derived | `main()` :728; `__main__` | writes HTML output | actions_registry consumers | gui_api, r72_studio suites | ACTIVE |
| `live_visual.py` / `live_host.py` / `perspective_studio.py` | live two-way visual bridge (localhost) / persistent live HTML host (`main(argv)`) / R7.2 presentation adapter | none — derived | servers + `__main__` | — | live_visual: vision/repl consumers; **live_host: no importers found** | visual_ux suites (topical) | live_visual ACTIVE_UNVERIFIED; **live_host ORPHAN_CANDIDATE**; perspective_studio ACTIVE_UNVERIFIED |
| `profile_board.py` / `schema_board.py` / `simulate_board.py` | C7.Profile (Dell 49 speedometer) / C7.Schema (Dell 39 read-only) / C13 Simulate (Dell 31 dry-run) boards | none — derived (boards read state) | APIs; `__main__` | **read** `form/state/*{owner}*` (profile/simulate) | Program/open surfaces | `form/c7profile_test.py`, `c7schema_test.py`, `c13_simulate_test.py` | ACTIVE |
| `forces.py` | "Nature Forces — ported from src/forces/nature_forces.js." Seven-force family | force state (in-memory) — **persistence asymmetric** (prior verified census: gravity wells + evolution level saved; other forces' intensity not) | API; `__main__` | partial via Program/persist | ringed_growth/spatial consumers | `form/forcefield_gravity_evolution_test.py`, water_persistence | ACTIVE_UNVERIFIED |
| `lineage.py` (+ `lineage_bind.py`) | "Single lineage authority: parents, origin, version, inspect." / bind = "Retired compatibility shim" (its own docstring) | **lineage records** | APIs | via Program | confirm/proposal paths | lineage_authority suites | lineage ACTIVE; **lineage_bind HISTORICAL_ONLY** |
| `spatial_audio.py` | "Spatial audio cues — offline-first." position→pan/gain/band/ear cues | none — derived | API; `__main__` | — | **zero references outside itself (grep, this pin)** | none found | **ORPHAN_CANDIDATE (strongest in tree)** |
| `ambient_gate.py` / `auto_growth.py` | folder-adapter ingest (inbox/screen/mic/clipboard) / "Auto Growth — the automated Nursery producer (WO-5.1)" | inbox folders / producer state | APIs; `__main__` (ambient) | `form/state/inbox/ screen/ mic/ clipboard/`; auto_growth `_STATE` (env `DELLMATRIX_STATE` override) | UNKNOWN | gs4_sandbox (topical) | ACTIVE_UNVERIFIED |
| `exchange.py` | "Exchange v1 (master plan P9) — seed packets with receipts." | exchange receipts | API | via atomic_write (paths in module) | step5/step5b suites | `form/step5*_test.py` | ACTIVE_UNVERIFIED |
| `acceptance_policy.py`, `agent_authority.py`, `agent_coordinator.py`, `rollback_authority.py`, `sandbox_gate.py`, `internet_gate.py`, `enhance_gate.py` | governance/gate family: human confirmation policy; R6.1 agent-authority dispatch; R6.4 multi-agent coordinator; R6.3 authority rollback (imports `form.persist._STATE_DIR/_path`); global sandbox isolation; network gate; enhance gate | policy/gate state (in-memory); rollback reads persist paths | APIs; several `__main__` | rollback: reads `form/state` member files | r6 suites, step3 security | `form/step3_security_test.py`, sm32, r61/r64 suites | ACTIVE_UNVERIFIED as a class (individually unproven by this lane) |

## 4. `form/duobeta/` (3 modules)

| Module | Purpose | Owns | Entrypoints | Persistence | Consumers | Tests | Class |
|---|---|---|---|---|---|---|---|
| `growth.py` | "DuoBeta — living growth / self-understanding (Voynich structural)." | DuoBeta growth state | API | UNKNOWN | selfgrow, open | `form/duobeta_live_test.py`, duobeta_cross_session | ACTIVE_UNVERIFIED |
| `selfgrow.py` | "SelfGrow L3 — program evolves using Mandell seeds against live foundation." | **SelfGrow state file** | API | **`selfgrow_state.json`** (`STATE_PATH` from module `_DATA`; direct `open(...,"w")` write :185 — **not** the atomic primitive) | `form/grow.py` switch (topical) | duobeta_live (topical) | ACTIVE_UNVERIFIED |

## 5. `form/llm/` (3 modules)

| Module | Purpose | Owns | Entrypoints | Persistence | Consumers | Tests | Class |
|---|---|---|---|---|---|---|---|
| `bridge.py` | "Universal LLM bridge — cloud + local open-source (Ollama)." The dock seam for Psalm/Gemini-class AIs | none — derived (transport) | bridge API | — | dock/inference consumers (grep) | dock suites (topical) | ACTIVE |
| `cli.py` | "LLM bridge CLI for sister terminal." `main()` :19 | none | CLI `main()` | — | **none found** | none found | ORPHAN_CANDIDATE |

## 6. `form/avatar/` (4 modules)

| Module | Purpose | Owns | Entrypoints | Persistence | Consumers | Tests | Class |
|---|---|---|---|---|---|---|---|
| `body.py` / `face.py` | "Avatar body FSM. Law: Body first. Thinks second." / "Face state + expression cycles" | Avatar body/face state (serialized in the v7 document via persist `_serialize_avatar`) | APIs | inside `program_{owner}.json` | open.py front door | avatar coverage UNKNOWN by name | ACTIVE_UNVERIFIED |
| `kaomoji.py` | "Kaomoji packs for expression." | none — data | data/functions | — | **none found in scan** | none found | ORPHAN_CANDIDATE |

## 7. `form/worldwide/`, `form/ancient/`, `form/matrices/`

| Module | Purpose | Owns | Entrypoints | Persistence | Consumers | Tests | Class |
|---|---|---|---|---|---|---|---|
| `worldwide/WORLDWIDE_IDEAS.py` + `__init__.py` | "Worldwide idea catalog — source list for planting into Worldwide and DEV." | none — source data | plant helpers | planted via Program | UNKNOWN | none found | ACTIVE_UNVERIFIED |
| `ancient/stonehenge_seed.py` | "Stonehenge → Dell Matrix structural seed" (package: "not decipherment claims") | none — seed data | `__main__` :222 | — | none found | none found | HISTORICAL_ONLY |
| `matrices/` | README.md only — **no Python modules exist at this pin** | none | none | — | — | — | HISTORICAL_ONLY (empty shell; the matrices function lives in `dell_matrix/matrices_hub.py` + `mandell` spectrum ops) |

## 8. (a) PUBLIC-ENTRYPOINT INVENTORY — every way in

Verified from code (`__main__` guards, `main()` defs, regress manifest), not from docs:

1. **`python -m form`** → `form/__main__.py` → `form.open.main()` — the program front door (Program + Avatar + Nursery + HarmonicLattice).
2. **`python -m form.repl`** → `form/repl.py main()` — the REPL: English lines, Mandell seeds, LatinMandell toll-booth, lattice/studio/group/containment/learn/why commands.
3. **`python -m form.regress`** → the canonical regression runner (also the CI entry).
4. **`python -m form.accept`** / `form/accept.py` script — one-click offline acceptance.
5. **`form/llm/cli.py main()`** — LLM bridge CLI (sister terminal) — orphan-candidate entrypoint.
6. **Studio / visual surfaces (in-process, not separate servers by default):** `form/dell_matrix/visual.py main()` (offline HTML control panel + `assets/pages/*.html` ×12), `live_visual.py` (localhost two-way bridge), `live_host.py main(argv)` (persistent HTML host), `perspective_studio.py`, and the REPL's studio lines (`_handle_studio_line` in repl.py). No standalone web-server package (no flask/http.server module) was found in `form/` — UNKNOWN whether Studio ships outside this tree.
7. **Per-module `__main__` smokes:** ~50 `dell_matrix` modules and many `mandell` modules carry `if __name__ == "__main__"` smoke/demo entries (plane, sacred_geometry, harmonic_lattice, forces, resonance, boards, gates…) — developer entrypoints, each running that module's `smoke()`/demo.
8. **Build-time tools:** `form/lm1_import.py`, `lm1_harvest.py`, `lm2_census_build.py` (LatinMandell table builds); `form/give_blank.py`; `form/seed_strong_ideas.py`; `form/grow.py`.
9. **Cross-process child scripts** (invoked by parents via subprocess, not by users): `form/mandell/r61_child.py`, `r62_child.py`, `r64_child.py`, `r65_fresh_probe.py`, `r65_verify_probe.py`, `form/track_d_td1_r2_child.py`, and the p-series proof scripts driven by regress.

## 9. (b) PERSISTENCE-OWNER INVENTORY — every durable writer

All durable state roots at **`form/state/`** (`form/persist.py:36` `_STATE_DIR`, created at import; a fresh clone has no `form/state` until first run — regress always runs in a temp copy with a fresh one). Writers:

| # | Owner (writer) | What | Path(s) | Mechanism |
|---|---|---|---|---|
| 1 | `form/persist_rest.py` (`save`) | the v7 program document (matrix+avatar+nursery+lattice+history+LM customs+idea detail/goals+Core II fields) | `form/state/program_{owner}.json` | atomic-write primitive + owner lock + binding-loss refusal |
| 2 | `form/persist_rest.py` (`checkpoint`) | program checkpoints | `form/state/program_{owner}_cp_{stamp}.json` | as above |
| 3 | `form/mandell/checkpoint_generation.py` | checkpoint generations (pointer/manifest/sealed members, current+previous retained) | `current_{owner}.json`, `gen_{owner}_{id}.json`, `{kind}_{owner}.g_{id}.json` | sealed members + pointer commit (module) |
| 4 | `form/mandell/core_i_recovery.py` | Core I rollback/confirm/checkpoint/supersede journals + staging | `rollback_{owner}.journal.json`, `confirm_…`, `checkpoint_…`, `supersede_…`, `*.staging` | journal files (module) |
| 5 | `form/mandell/semantic_graph.py` | canonical semantic graph + journal | `form/state` graph file + journal (`graph_path`/`graph_journal_path`) | atomic write |
| 6 | `form/mandell/idea_persist.py` | per-owner idea records | `form/state/ideas_{owner}` (module-computed) | atomic write (import evidence) |
| 7 | `form/mandell/idea_checkpoint.py` | idea checkpoints + rehydrate pending marker | `ideas_{owner}.json`, `ideas_rehydrate_{owner}.pending` | atomic write (import evidence) |
| 8 | `form/dell_matrix/nursery.py` | nursery proposal pool | `form/state/nursery.json`, `nursery_{owner}.json` | atomic_write (direct import) |
| 9 | `form/dell_matrix/ambient_gate.py` | ambient ingest drops | `form/state/inbox/`, `screen/`, `mic/`, `clipboard/` | direct file drops (folder adapters) |
| 10 | `form/dell_matrix/auto_growth.py` | auto-growth producer state | module `_STATE` under `form/state` (env override `DELLMATRIX_STATE`) | UNKNOWN |
| 11 | `form/duobeta/selfgrow.py` | SelfGrow state | `selfgrow_state.json` (module `_DATA`) | **direct `open("w")` — not the atomic primitive** (:185) |
| 12 | `form/give_blank.py` | blank-matrix starter marker | `form/state/START_{owner}.txt` | direct write |
| 13 | `form/lm1_harvest.py` (build-time) | LM-1 table + collision log | `form/mandell/lm_table_v1.json`, `lm_table_v1.collisions.json` | build-time write |
| 14 | `form/dell_matrix/exchange.py` | seed-packet receipts | paths in module | atomic_write (import evidence) |
| 15 | `form/owner_state_lock.py` | owner write locks (not data) | lock files in `form/state` | lock primitive |

**Single-mechanism note:** exactly one crash-safe write primitive exists (`dell_matrix/atomic_write.py`, DCC-XVII) and the major writers use it; the exceptions found are #9 (folder drops, by design), #11 (direct write), #12 (marker text). The everyday-save pair risk from prior main-line findings (program pair written as separate files) is consistent with owners #1+#8 being distinct files — recorded here as structure, not re-tested by this lane.

## 10. (c) STATUS SUMMARY + ORPHAN CANDIDATES

Graph fragment: 86 significant nodes — **ACTIVE 41 · ACTIVE_UNVERIFIED 30 · HISTORICAL_ONLY 6 · ORPHAN_CANDIDATE 9** (the 274 test/proof files are TEST_ONLY as a class and are not itemized as nodes). Group-level: `mandell` and the top-level shell are the ACTIVE core; `dell_matrix` is ACTIVE at its center (core/plane/nursery/geometry/lattice/boards) with a wide ACTIVE_UNVERIFIED feature belt; `duobeta`, `avatar`, `worldwide` are small and mostly ACTIVE_UNVERIFIED; `llm` splits ACTIVE bridge / orphan-candidate CLI; `ancient` and `matrices` are HISTORICAL_ONLY.

**Top orphan candidates** (zero consumers under AST+grep at this pin; caveat 1 applies — importlib/subprocess/regress references can hide a consumer):

1. **`form/dell_matrix/spatial_audio.py`** — zero references anywhere outside itself; no test found. (Independently matches the Grand Plan's X11 orphan exhibit.)
2. **`form/llm/cli.py`** — CLI entrypoint, no importers, no tests found.
3. **`form/avatar/kaomoji.py`** — expression data pack, no importers found.
4. **`form/invariants.py`** — "runnable hard checks" nobody imports.
5. **`form/seed_strong_ideas.py`** — planting tool, no importers (may be run manually as a script).
6. **`form/mandell/knowledge_influence.py`** — KIE-I explanation layer; read-only by design, but no consumer found.
7. **`form/mandell/lm_table.py`** — LM table loader; scan-inconclusive (latinmandell may reach the table by path rather than by importing this loader).
8. **`form/dell_matrix/live_host.py`** — persistent HTML host with `main(argv)`; no importers found (may be launched as a script).
9. Script-class (likely intentional, listed for completeness): `form/dell_matrix/{allwhere, dynamic_view_switch, neuroevo, organ_atlas, procedural_assets, visual_terminal, function/page/program/sync/visual *_loop}.py` and `form/mandell/{address_space, correction_graph, nature_english, manifest_resolver, live_identity, p1_idea_circuit, p2_perf_baseline, p2_susx100, p4_acceptance_circuit, english_brain_150_loop}.py` — all carry `__main__` or proof/circuit roles and zero AST importers; several are certainly regress/subprocess-driven. Each needs a consumer-trace before any orphan ruling (Completeness Law: PARTICIPATING or STOOD DOWN WITH A RECEIPT — this census supplies the candidate list, not the verdict).

## 11. Legacy directories (one line each)

- **`preform/`** — HISTORICAL_ONLY: the pre-Form JS/MD era (PSALM preform docs, `mandell_kernel.js`, `boot.js`, forces/core in JS); superseded by `form/`, retained as evidence.
- **`src/`** — HISTORICAL_ONLY: legacy JS sources (visual/forces/snapins ancestors of several `dell_matrix` ports whose docstrings cite `src/...` origins); no runtime role at this pin.

## 12. What this lane did NOT determine (UNKNOWN, for the contract lanes)

- Per-module test *pass* state (nothing was executed).
- Whether `mandell/language.py`'s claimed persist role duplicates `form/persist.py` (authority-overlap candidate, with `circuit_ledger.py`'s "ONE current state authority" claim as a second candidate overlap — both flagged, neither resolved here).
- SpatialAuthority's and resonance's exact serialization paths inside the v7 document.
- Studio's shipping form outside this tree (no server package found in `form/`).
- Exact consumer lists for the ~65 un-itemized `dell_matrix` feature modules and ~60 un-itemized `mandell` circuit modules (AST data exists in the working scan; the graph fragment carries the significant subset).

*End of Lane 1 census. Companion: `LANE1_GRAPH.json` (86 nodes / 27 edges, grep/AST-derived).*
