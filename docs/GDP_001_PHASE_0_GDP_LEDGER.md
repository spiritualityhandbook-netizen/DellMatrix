# DELLMATRIX_GDP_LEDGER.md — Grand Development Ledger

**Program:** DELLMATRIX GRAND DEVELOPMENT PLAN · **Version:** GDP-V1
**Authority:** OVERSEER > DIRECTOR > UNI / ADAPTIVE SUSX100 > SPECIALISTS > REPOSITORY
**Status model per objective:** NOT_STARTED | IN_PROGRESS | IMPLEMENTED | AUDIT_FAILED | REPAIRING | CERTIFIED | BLOCKED | UNKNOWN

**Phase-0 baseline (frozen):** BASE_SHA `1c90cecf9e5bbbf6bda055f3157ecada299f6840` · BASE_TREE `83f184b3718b64f3370b61617c8019aa1085c9cb`
**Baseline meaning:** main immediately after PR #69 merge (MPC-011 §0: Dell87 occupied refusal + /cmd hardening + Dell37 reconciliation + CA-01 corrections). Exact-head CI green (3.10, 3.11, smoke); security EVALUATION_UNAVAILABLE_QUOTA.

**Ledger law:** do not remove completed objectives. Record evidence/SHA/tests/dependencies/discoveries/future-phase findings per objective. Phase 0 objectives are verbatim from GDP-001. Phases 1–7 requirements/objectives are DERIVED DRAFT (from the mission verbs and MPC-012/012-R census) — subject to Director review at each phase gate.

---

## PHASE 0 — INTEGRITY & SEMANTIC FOUNDATION [CERTIFIED] [MERGED] [CLOSED]

**Merge:** PR #70 merged 2026-10-03T21:00:12Z as `827e4f8bacb0e2eb1438183ecb3cab722c39f7fd`
(parents: `1c90cecf9e5bbbf6bda055f3157ecada299f6840`, `7319b5e7c4d38d4be72a0af3c8c20d36fdb1eea9`).
**Requirements:** 0.1 CERTIFIED, 0.2 CERTIFIED, 0.3 CERTIFIED, 0.4 CERTIFIED, 0.5 CERTIFIED.
**Objectives:** 25/25 CERTIFIED.
**Post-merge:** fresh-main regress 83/83 GREEN; persistence 55/55; exact-head CI green.
**R1/R2/R3 findings preserved** as engineering history (see SWAT report).

**Phase-0 permanent contracts (inherited by Phases 1–7):**
PERSISTENCE MUST FAIL CLOSED. SEALED HISTORY IMMUTABLE. LIVE MUST NOT ALIAS
SEALED. NO HYBRID MULTI-FILE STATE. UNKNOWN RECOVERY != VALID STATE.
ATOM TRUTH != CHAIN POLICY. UNEXECUTED != SUCCESS. TEST PASS != CAPABILITY.
VACUOUS TEST != EVIDENCE. CLAIM <= PROVEN BEHAVIOR. RESERVED FAILS HONESTLY.
MATH REQUIRES ADMISSION. NO COMPETING AUTHORITY.

**Integration branch:** `gdp-phase0-work` (from baseline 1c90cec). R1–R5 specialist branches merged; R2 MUST_FIX applied. Integrated regress running.

### R0.1 Persistence integrity
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 0.1.1 | Repair Dell28 rollback/autosave generation corruption (sealed generation must not become mutable via nursery alias) | IMPLEMENTED | MPC-012-R verified bug; fix = copy-on-rollback + re-point |
| 0.1.2 | Prove save/load/checkpoint/rollback across fresh OS-process boundaries | IMPLEMENTED | p0_integrated_proof_test (registered): every step in fresh OS processes; 13/13 ALL GREEN. Gate R1: eager rollback convergence proven. Gate R2 Finding 1: journaled two-file transaction (prepare/stage/commit/cleanup/verify); recovery in every load; 8 crash-injection points proven (old-complete or target-complete, never hybrid). Gate R3: fail-closed recovery (no exception suppression; fingerprint-verified old/target pairs; 16 adversarial tests); 55/55 persistence battery |
| 0.1.3 | Establish generation immutability/sealing invariants; explicit non-aliased ownership of committed vs mutable state | IMPLEMENTED | Generation sealing: manifest sha256 per member; _load_impl re-points staged nursery to live file; NurseryConflictError on stale save; sealed members never written post-commit (byte-identity verified) |
| 0.1.4 | Test interruption/failure/corruption behavior; no partial operation becomes accepted truth | IMPLEMENTED | Failure probes in 19/19 battery: SIGKILL, os._exit, missing/corrupt member, corrupt manifest, concurrency conflict, serialization failure; no partial op becomes accepted truth |
| 0.1.5 | Create the persistence contract required by all later Idea/history/provenance/AI phases | IMPLEMENTED | docs/PERSISTENCE_CONTRACT.md created; perf: save 0.027s/load 0.004s/commit 0.134s/rollback 0.001s (200-unit case in contract) |
**Requirement complete only when:** persistent state can be trusted as architectural foundation.

### R0.2 Mandell semantic authority
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 0.2.1 | Reconcile the authoritative active Dell registry; resolve registry uncertainty relevant to runtime authority | IMPLEMENTED | MPC-012: per-Dell authority uneven; dead leaf branches 27,28,34,35,40,44,47 |
| 0.2.2 | Reconcile ENGLISH → ENGLISH BRAIN → MANDELL → DELL → EXECUTOR for supported semantics | IMPLEMENTED | 27/27 semantic honesty suite; raw-seed public path documented (bypasses English Brain); english_brain.understand() zero production callers documented; HANDLED shadowing documented |
| 0.2.3 | Reconcile Flow operators and composition semantics; preserve Free-Origin, Flow-Priority, No-Orphans, Typed-Sockets, Cross-Layer-Routing, Symmetry, Fractal-Nesting where authoritative | IMPLEMENTED | Flow laws classified: Free-Origin/Symmetry/Fractal-Nesting STATED_ONLY; Flow-Priority/No-Orphans/Typed-Sockets/Cross-Layer-Routing PARTIAL; operator_bridge typed-arg drop fixed (single lowering authority) |
| 0.2.4 | Enforce semantic honesty: unsupported/ambiguous/contradictory/unauthorized must not silently become valid operations | IMPLEMENTED | Reserved refusal: leaf ok=False zero-mutation (8b8bfb9) extended to 51-99/37 direct-leaf (ARGUS 2a); chain skip recorded honestly (ARGUS 2b); gibberish refused; 27/27 honesty |
| 0.2.5 | Produce authoritative LANGUAGE_COMPLETION_MATRIX per active Dell: REGISTERED, PARSEABLE, TRANSLATABLE, EXECUTABLE, PUBLICLY_REACHABLE, TESTED, SEMANTICALLY_CONSISTENT, PERSISTENT where applicable | IMPLEMENTED | docs/LANGUAGE_COMPLETION_MATRIX.md: 100 active + 49 reserved rows x 8 dims; ORACLE 10/10 random sample verified vs code; 19 Dell test gaps disclosed (Core-II 90-99) |

### R0.3 Execution integrity
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 0.3.1 | Find and eliminate competing semantic authorities for the same operation | IMPLEMENTED | Eliminated in-scope: Dell 21/22 leaf divergence (single front-door authority), operator_bridge arg-drop (single lowering authority), receipt naming (adapter). DEFERRED to Phase 3 per ledger §7 R4-A2–A5: vesica_strength vs sacred_geometry.vesica(), resonance.py vs _affinity, _harmonic vs pair-verita vs sacred-verita (NULL audit verified deferral documented) |
| 0.3.2 | Reconcile legitimate dispatch paths; equivalent operations must not differ by entry interface | IMPLEMENTED | 80/80 multi-path suite (raw/English/Flow/API). Gate R1 Decision 1: unified atom truth (ok=False/skipped/reason); chain continues per policy, aggregate honest (ok=False/partial/any_skipped); PRISM C2 multi-atom guard; eoc/cac/ros tests updated to new semantics |
| 0.3.3 | Require atomic mutation where operation semantics demand it | IMPLEMENTED | Atomicity: merge/split partial reported via PARTIAL markers. Gate R1 Decision 2: rollback eagerly converges live files. Gate R2 Finding 1: pair-atomic via journaled transaction; no hybrid program/nursery observable. Gate R3: fail-closed (RollbackRecoveryError on unrecoverable; fingerprints verified); 55/55 persistence battery |
| 0.3.4 | Standardize honest execution Outcome/receipt info: requested/resolved operation, authority, success/failure, reason, before/after, affected objects, provenance | IMPLEMENTED | Receipt/Outcome standardized. Gate R1: chain atom records carry ok=False/skipped=True/reason; chain result exposes partial/any_skipped; raw receipt threads atom_results/partial; Outcome partial_completion honest |
| 0.3.5 | Prove execution integrity through raw Dell, English, Flow, direct API/runtime, public interface where supported | IMPLEMENTED | 44/44 through raw Dell, English, Flow, direct API; integrated proof cross-process; 82/82 regress fwd+rev |

### R0.4 Mathematical authority
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 0.4.1 | Integrate MPC-012-R equation recovery into authoritative DELLMATRIX_EQUATION_LEDGER | IMPLEMENTED | docs/DELLMATRIX_EQUATION_LEDGER.md: 28 DellMatrix + 6 external-ref entries recovered from MPC-012-R; 14/14 invariant checks (incl. 200-case randomized duplicate-consistency) |
| 0.4.2 | Classify every recovered equation: ACTIVE_VALIDATED, ACTIVE_UNVALIDATED, DISCONNECTED, EXPERIMENTAL, HISTORICAL, DUPLICATE, CONTRADICTORY, MATHEMATICALLY_UNJUSTIFIED, RECOVERY_CANDIDATE, UNKNOWN | IMPLEMENTED | 6 VAL / 8 UNVAL / 3 UNJUST / 2 CONTRA / 1 DUP / 9 HIST / 2 DISC aspects / 3 UNK = 32 distinct (ORACLE F2: counts corrected to listed IDs) |
| 0.4.3 | Preserve mathematical lineage: RootPath, Harmonic Cube, Verita, Flower geometry, gravity, resonance, harmony, known/unknown/growth, others | IMPLEMENTED | Lineage preserved: RootPath/Harmonic-Cube math carried as UNKNOWN (honest, not fabricated); Verita/Flower/gravity/resonance/harmony sections in ledger |
| 0.4.4 | Remove/reconcile duplicate mathematical authority; no two formulas silently define the same quantity | IMPLEMENTED | Duplicate EQ-VER-001→EQ-GEO-001 reconciled (single authority); Phase-3 dupes (vesica/resonance/verita pairs) documented deferrals R4-A2..A5, not silent |
| 0.4.5 | Create MATHEMATICAL_ADMISSION_CONTRACT: defined variables/domain/outputs/invariants/basis/interpretation/tests/limitations; no pseudomathematics | IMPLEMENTED | docs/MATHEMATICAL_ADMISSION_CONTRACT.md created: variables/domain/outputs/invariants/basis/interpretation/tests/limitations; heuristics must be labelled |

### R0.5 Runtime truth
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 0.5.1 | Repair severe Perspective misinformation (perspective_views blind "whole" reporting 0 nodes) | IMPLEMENTED | MPC-012 Agent C: SEVERE theater |
| 0.5.2 | Audit computed-but-never-consumed mechanisms relevant to Phase 0 | IMPLEMENTED | Computed-but-never-consumed audited: english_brain.understand() zero callers; spatial_audio/world_predict discards fixed (ARGUS 5); UNKNOWN cells in matrix where unverified |
| 0.5.3 | Audit persisted-but-never-used state relevant to Phase 0 | IMPLEMENTED | Persisted-but-never-used audited: outcome_ledger-in-program-member documented; legacy adapters PARTIAL; no orphaned durable writes on Phase-0 paths |
| 0.5.4 | Require public/runtime surfaces to distinguish REAL / PARTIAL / UNAVAILABLE / UNKNOWN / UNSUPPORTED | IMPLEMENTED | All perspective views + spatial_audio.cues_for_program + world_predict.predict_unseen carry epistemic_status/data_source: REAL/PARTIAL/UNAVAILABLE/UNKNOWN/UNSUPPORTED |
| 0.5.5 | Establish RUNTIME_TRUTH_INVARIANTS for all subsequent phases | IMPLEMENTED | docs/RUNTIME_TRUTH_INVARIANTS.md created; 26/26 runtime-truth checks registered in regress |

---

## PHASE 1 — THE IDEA [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: CREATE, UNDERSTAND, REMEMBER, SUPERSEDE, FADE.
### R1.1 Idea lifecycle + non-destructive history
| 1.1.1 | Per-Unit revision store (append-only); detail/goals writes create revisions, never overwrite | NOT_STARTED |
| 1.1.2 | State machine: ACTIVE/FADED/SUPERSEDED/ARCHIVED with enforced transitions | NOT_STARTED |
| 1.1.3 | `history <idea>` / `trace_revision` public paths over Unit revisions | NOT_STARTED |
| 1.1.4 | Persistence of revisions per-owner, atomic | NOT_STARTED |
| 1.1.5 | Destructive-write path eliminated; regression proves prior revisions survive | NOT_STARTED |
### R1.2 Idea state enforcement
| 1.2.1 | Fade excludes/reduces influence in selector/growth/router per published policy | NOT_STARTED |
| 1.2.2 | Supersession of Unit content with preserved predecessor | NOT_STARTED |
| 1.2.3 | Archived/restored states with identity preservation | NOT_STARTED |
| 1.2.4 | Two-path query pattern (active vs history) | NOT_STARTED |
| 1.2.5 | State badges on public surfaces bound to real state | NOT_STARTED |
### R1.3 Provenance attribution
| 1.3.1 | Proposal fields: proposer, decider, proposed_at, decided_at, evidence refs | NOT_STARTED |
| 1.3.2 | Outcome `_knowledge_snapshot` carries parents/origin/lineage_version | NOT_STARTED |
| 1.3.3 | `inspect <proposal>` shows WHY/SOURCE/DECIDER | NOT_STARTED |
| 1.3.4 | Back-compat: optional fields, no migration breakage | NOT_STARTED |
| 1.3.5 | No silent WHY on any new proposal/outcome | NOT_STARTED |
### R1.4 Idea persistence + identity
| 1.4.1 | UID identity guarantees across save/load/migration | NOT_STARTED |
| 1.4.2 | Per-owner atomic persistence of ideas + revisions + state | NOT_STARTED |
| 1.4.3 | Cross-process identity stability proofs | NOT_STARTED |
| 1.4.4 | Deduplication semantics preserved and proven | NOT_STARTED |
| 1.4.5 | Persistence contract compliance (from Phase 0) | NOT_STARTED |
### R1.5 Idea public paths
| 1.5.1 | Create/understand/inspect flows honest end-to-end | NOT_STARTED |
| 1.5.2 | English → Mandell → Dell paths for idea operations | NOT_STARTED |
| 1.5.3 | Failure behavior honest (no silent partial creation) | NOT_STARTED |
| 1.5.4 | Public-path proofs for each operation | NOT_STARTED |
| 1.5.5 | Documentation matches runtime truth | NOT_STARTED |

---

## PHASE 2 — FRACTAL SEMANTIC GRAPH [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: FRACTAL, RELATE.
### R2.1 Fractal containment model
| 2.1.1 | Containment: ideas as containers of ideas; children/members on Unit | NOT_STARTED |
| 2.1.2 | Containment vs lineage separation (parents = derivation, containers = nesting) | NOT_STARTED |
| 2.1.3 | Nest/unnest operations with provenance | NOT_STARTED |
| 2.1.4 | Containment persisted per-owner | NOT_STARTED |
| 2.1.5 | No silent re-parenting | NOT_STARTED |
### R2.2 Graph relationships
| 2.2.1 | First-class relationship edges (resonates-with, derived-from, contains) | NOT_STARTED |
| 2.2.2 | Graph queryable independently of hierarchy | NOT_STARTED |
| 2.2.3 | Edges carry provenance + evidence | NOT_STARTED |
| 2.2.4 | Graph persisted per-owner | NOT_STARTED |
| 2.2.5 | Hierarchy ≠ complete relationship model (law enforced in code) | NOT_STARTED |
### R2.3 Promotion
| 2.3.1 | Nested → top-level promotion preserving identity | NOT_STARTED |
| 2.3.2 | Promotion preserves containment origin, history, evidence, provenance, Nursery origin | NOT_STARTED |
| 2.3.3 | Demotion (top-level → nested) symmetric | NOT_STARTED |
| 2.3.4 | Promotion via human acceptance only | NOT_STARTED |
| 2.3.5 | Full §35 promotion scenario passes end-to-end | NOT_STARTED |
### R2.4 Multi-representation coherence
| 2.4.1 | One underlying state; semantic/Mandell/graph/spatial/resonance/visual representations | NOT_STARTED |
| 2.4.2 | Representations derived, never competing truths | NOT_STARTED |
| 2.4.3 | Representation registry with derivation proofs | NOT_STARTED |
| 2.4.4 | Perspective reads representations, never authors truth | NOT_STARTED |
| 2.4.5 | Inconsistency between representations is a defect, surfaced | NOT_STARTED |
### R2.5 Graph traversal + query
| 2.5.1 | Traversal operations with bounded depth | NOT_STARTED |
| 2.5.2 | Query language/path for relationships | NOT_STARTED |
| 2.5.3 | Performance: indexed, no full-graph scans for local queries | NOT_STARTED |
| 2.5.4 | Public-path proofs | NOT_STARTED |
| 2.5.5 | Integration with Phase-1 history/provenance | NOT_STARTED |

---

## PHASE 3 — RESONANCE, HARMONY & INFORMATION GEOMETRY [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: RESONATE.
### R3.1 Affinity/resonance reconciliation
| 3.1.1 | `_affinity` exposed as first-class service with contract | NOT_STARTED |
| 3.1.2 | `resonance.py` rehomed or removed after exposure | NOT_STARTED |
| 3.1.3 | Serendipity term (tension/dissimilarity) + affinity evaluation metrics | NOT_STARTED |
| 3.1.4 | Seeded RNG for deterministic growth IDs | NOT_STARTED |
| 3.1.5 | Resonance vs Verita authority reconciled (parallel, not merged) | NOT_STARTED |
### R3.2 Harmony model
| 3.2.1 | Define harmony as a DellMatrix semantic (not musical metaphor) | NOT_STARTED |
| 3.2.2 | Harmonic naming cleanup (lattice/core/link renamed to what they are) | NOT_STARTED |
| 3.2.3 | Harmony computation with contract + tests | NOT_STARTED |
| 3.2.4 | Harmony vs resonance separation proven | NOT_STARTED |
| 3.2.5 | Public-path proofs | NOT_STARTED |
### R3.3 Verita transformation layer (where justified)
| 3.3.1 | Decide: build the transformation layer or park it (Director) | NOT_STARTED |
| 3.3.2 | If built: define state space, variables, normalization, transformation, invariants, inverse | NOT_STARTED |
| 3.3.3 | Prove bijectivity/boundedness from DellMatrix constraints | NOT_STARTED |
| 3.3.4 | Center/boundary conditions from DellMatrix semantics, measurable | NOT_STARTED |
| 3.3.5 | No pseudomathematics (admission contract enforced) | NOT_STARTED |
### R3.4 Information geometry (where justified)
| 3.4.1 | Replace heuristic verita with defined overlap metric; unify duplicate vesica_strength | NOT_STARTED |
| 3.4.2 | Čech nerve as higher-order relationship model (only with proven consumers) | NOT_STARTED |
| 3.4.3 | Power diagrams for weighted ideas (exclusive vs shared volume) | NOT_STARTED |
| 3.4.4 | Alpha filtration for void lifecycle (only with proven consumers) | NOT_STARTED |
| 3.4.5 | Negative-space channels remain declared-future; never display uncomputed regions | NOT_STARTED |
### R3.5 Resonance/harmony integration
| 3.5.1 | Resonance/harmony feed selection/growth/Nursery through honest contracts | NOT_STARTED |
| 3.5.2 | Faded-state exclusion honored in resonance computation | NOT_STARTED |
| 3.5.3 | Outcome/observation of resonance effects | NOT_STARTED |
| 3.5.4 | Public-path proofs | NOT_STARTED |
| 3.5.5 | Integration with Phase-2 graph | NOT_STARTED |

---

## PHASE 4 — LIVING SPATIAL MATRIX [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: BUILD, OBSERVE.
### R4.1 Spatial honesty
| 4.1.1 | Meaningful coordinates assigned (affinity→layout with published legend) OR honest de-spatialization | NOT_STARTED |
| 4.1.2 | Binding test: every visual channel encodes real state or is removed | NOT_STARTED |
| 4.1.3 | Layout determinism proven | NOT_STARTED |
| 4.1.4 | Lattice idea-bridge repaired or removed (no single-cell pileup) | NOT_STARTED |
| 4.1.5 | No-theater re-audit: zero findings | NOT_STARTED |
### R4.2 Gravity/force bounded movement
| 4.2.1 | Force movement bounded; equilibrium defined and reached | NOT_STARTED |
| 4.2.2 | Movement only from real state changes | NOT_STARTED |
| 4.2.3 | Settles rather than constantly wobbles (convergence) | NOT_STARTED |
| 4.2.4 | Force parameters inspectable (legend) | NOT_STARTED |
| 4.2.5 | Public-path proofs | NOT_STARTED |
### R4.3 Weather bounded pressure
| 4.3.1 | Weather → bounded exploration pressure effectors with independent world logic | NOT_STARTED |
| 4.3.2 | Pressure never alters truth (law enforced) | NOT_STARTED |
| 4.3.3 | Oblique correlation (never moralizing mirror) | NOT_STARTED |
| 4.3.4 | Honest labeling: never safe/unsafe unless mechanically true | NOT_STARTED |
| 4.3.5 | Public-path proofs | NOT_STARTED |
### R4.4 Live Matrix Law
| 4.4.1 | Dependency-aware updates: change → affected neighborhood only | NOT_STARTED |
| 4.4.2 | Spatial index (no naive O(n²) at scale) | NOT_STARTED |
| 4.4.3 | Incremental topology maintenance | NOT_STARTED |
| 4.4.4 | No global recompute to simulate "living" | NOT_STARTED |
| 4.4.5 | Performance within baseline envelope | NOT_STARTED |
### R4.5 No-theater visual binding
| 4.5.1 | Feedback budget per game-feel research (medium-high band) | NOT_STARTED |
| 4.5.2 | Simulation/presentation separation (juice never changes outcomes) | NOT_STARTED |
| 4.5.3 | Every visual event traces to computational referent (proven) | NOT_STARTED |
| 4.5.4 | Growth-room stages bound to real GrowthForce or removed | NOT_STARTED |
| 4.5.5 | Re-audit clean | NOT_STARTED |

---

## PHASE 5 — NURSERY, GROWTH & LEARNING [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: GROW, DISCOVER.
### R5.1 Nursery workshop surface
| 5.1.1 | Nursery as real scoped workshop (one workshop contract) | NOT_STARTED |
| 5.1.2 | Proposal cards with full provenance display | NOT_STARTED |
| 5.1.3 | Scored pending view (priority, aging) | NOT_STARTED |
| 5.1.4 | Re-review-if-changed on supersession chains | NOT_STARTED |
| 5.1.5 | Public-path proofs (REPL + visual) | NOT_STARTED |
### R5.2 Growth
| 5.2.1 | RingedGrowth with grammar labels (Compton) | NOT_STARTED |
| 5.2.2 | Seeded deterministic IDs | NOT_STARTED |
| 5.2.3 | Growth honors faded exclusion | NOT_STARTED |
| 5.2.4 | Growth proposes only into Nursery (law preserved) | NOT_STARTED |
| 5.2.5 | Public-path proofs | NOT_STARTED |
### R5.3 DuoBeta learning
| 5.3.1 | DBEL-I lifecycle preserved and proven end-to-end | NOT_STARTED |
| 5.3.2 | Gated evolve loop (preform 31: propose→gate→ledger) where justified | NOT_STARTED |
| 5.3.3 | Learning stays advisory/bounded (AUTONOMY law) | NOT_STARTED |
| 5.3.4 | Pairwise preference model evaluated (future) | NOT_STARTED |
| 5.3.5 | Public-path proofs | NOT_STARTED |
### R5.4 Knowledge lifecycle
| 5.4.1 | 7-stage pipeline proven end-to-end with contracts | NOT_STARTED |
| 5.4.2 | 4-gate eligibility enforced everywhere (no drift) | NOT_STARTED |
| 5.4.3 | `_check_routable` wired to real conflict evidence | NOT_STARTED |
| 5.4.4 | Architect governance gate (sift→confirm→apply) where justified | NOT_STARTED |
| 5.4.5 | Public-path proofs | NOT_STARTED |
### R5.5 Evidence chains
| 5.5.1 | Internet → evidence → eligibility chain built | NOT_STARTED |
| 5.5.2 | Evidence store (outcome-ID gating today; store where justified) | NOT_STARTED |
| 5.5.3 | INTERNET != TRUTH preserved structurally | NOT_STARTED |
| 5.5.4 | Research topics land as nursery proposal evidence | NOT_STARTED |
| 5.5.5 | Public-path proofs | NOT_STARTED |

---

## PHASE 6 — INTELLIGENCE, AUTHORITY & BIMO [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: EQUIP, DIRECT, GOVERN.
### R6.1 BIMO capability enforcement
| 6.1.1 | Capability tokens (unforgeable, attenuation-only) | NOT_STARTED |
| 6.1.2 | Complete mediation on all action paths | NOT_STARTED |
| 6.1.3 | Default-deny; prompts strictly secondary (97% rubber-stamp law) | NOT_STARTED |
| 6.1.4 | Revocation propagates (derivation tree) | NOT_STARTED |
| 6.1.5 | Every attach has learnable enforced consequence (anti-theater) | NOT_STARTED |
### R6.2 AI identity + docking
| 6.2.1 | AI identity object | NOT_STARTED |
| 6.2.2 | Docking interface: identity → persona → BIMO → authorized interface | NOT_STARTED |
| 6.2.3 | form/llm wired as inference layer (keys outside agent reach) | NOT_STARTED |
| 6.2.4 | Thinks async thread (preform 13) where justified | NOT_STARTED |
| 6.2.5 | Public-path proofs | NOT_STARTED |
### R6.3 General confirmation framework
| 6.3.1 | Nursery confirm generalized to destructive operations | NOT_STARTED |
| 6.3.2 | Pipeline confirm queue (preform 24/28) where justified | NOT_STARTED |
| 6.3.3 | AutoGrowth auto-confirm posture resolved (Director) | NOT_STARTED |
| 6.3.4 | Confirmation receipts with provenance | NOT_STARTED |
| 6.3.5 | Public-path proofs | NOT_STARTED |
### R6.4 Multiple intelligences
| 6.4.1 | Agent identity, regions, per-agent BIMO/persona binding | NOT_STARTED |
| 6.4.2 | Shared-state protocol + contention handling | NOT_STARTED |
| 6.4.3 | Audit trail of agent actions (visible + reversible) | NOT_STARTED |
| 6.4.4 | IntrinsicAgent as exploration policy (recovered) | NOT_STARTED |
| 6.4.5 | Public-path proofs | NOT_STARTED |
### R6.5 Separation enforcement
| 6.5.1 | PERSONA != PERMISSION proven continuously | NOT_STARTED |
| 6.5.2 | BIMO = enforced capability (law holds structurally) | NOT_STARTED |
| 6.5.3 | PERSPECTIVE != TRUTH proven continuously | NOT_STARTED |
| 6.5.4 | AI behavior vs AI authority never confused in code | NOT_STARTED |
| 6.5.5 | Human sovereignty proven under multi-intelligence load | NOT_STARTED |

---

## PHASE 7 — WORKSHOPS, PERSPECTIVES & CONNECTED WORLD [NOT_STARTED] (DERIVED DRAFT)

Mission verbs: RESEARCH.
### R7.1 One workshop contract
| 7.1.1 | Formal contract: enter → scoped command set + scoped view → leave; all commands logged; mutations via same dispatcher | NOT_STARTED |
| 7.1.2 | 7 button-menus rebuilt as real scoped environments | NOT_STARTED |
| 7.1.3 | Workshop semantics tested (commands differ inside) | NOT_STARTED |
| 7.1.4 | 4-level disclosure onboarding; 4-step teach rhythm | NOT_STARTED |
| 7.1.5 | Public-path proofs | NOT_STARTED |
### R7.2 Perspective Studio
| 7.2.1 | Perspective as scoped workshop for representation work | NOT_STARTED |
| 7.2.2 | perspective_views deleted or rewired (no misinformation) | NOT_STARTED |
| 7.2.3 | Cloud perspective defined or explicitly deferred | NOT_STARTED |
| 7.2.4 | Layout legend published and inspectable | NOT_STARTED |
| 7.2.5 | Public-path proofs | NOT_STARTED |
### R7.3 BIMO Forge / Persona Workshop
| 7.3.1 | BIMO Forge as real scoped environment (requires Phase 6 enforcement) | NOT_STARTED |
| 7.3.2 | Persona Workshop: behavioral lenses, coaching (MANUELL) | NOT_STARTED |
| 7.3.3 | Knowledge-gated capability (gating by understanding) | NOT_STARTED |
| 7.3.4 | No fake progression (progression = genuine trust/capability) | NOT_STARTED |
| 7.3.5 | Public-path proofs | NOT_STARTED |
### R7.4 Connected world
| 7.4.1 | Internet as evidence environment (from Phase 5.5) surfaced in workshops | NOT_STARTED |
| 7.4.2 | LLM docking (local + cloud) through BIMO enforcement | NOT_STARTED |
| 7.4.3 | Offline completeness proven (connected adds, never required) | NOT_STARTED |
| 7.4.4 | Credential gateway (keys outside agent reach) | NOT_STARTED |
| 7.4.5 | Public-path proofs | NOT_STARTED |
### R7.5 Grand integration
| 7.5.1 | All phases operate as ONE synchronized system | NOT_STARTED |
| 7.5.2 | No subsystem holds competing interpretation | NOT_STARTED |
| 7.5.3 | North Star acceptance scenarios pass end-to-end | NOT_STARTED |
| 7.5.4 | No-theater audit across the whole system | NOT_STARTED |
| 7.5.5 | Grand Integration Audit (program end condition) | NOT_STARTED |

---

## FUTURE-PHASE DISCOVERIES (recorded during Phase 0)

(none yet)

## OBJECTIVE COUNT

8 phases × 5 requirements × 5 objectives = **200 objectives**. Phase 0: 25 (verbatim). Phases 1–7: 175 (derived draft).

---

## PHASE 1 — THE IDEA [IN_PROGRESS]

**Base:** `d282d35160386f3df56c68cc1aba21931d1d45a5` (Phase-0 closure)
**Branch:** `gdp-phase1-work`
**Goal:** Canonical evolving Idea object.

### R1.1 Canonical Idea Object
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 1.1.1 | Persistent identity | IMPLEMENTED | form/mandell/idea.py: Idea.id UUID; t_111 |
| 1.1.2 | Core content | IMPLEMENTED | title/properties/goals/metadata; t_112 |
| 1.1.3 | Temporal/lifecycle metadata | IMPLEMENTED | created_at/modified_at; t_113 |
| 1.1.4 | Ownership/authority | IMPLEMENTED | Provenance source/agent; t_114 |
| 1.1.5 | Persistence | IMPLEMENTED | idea_persist.py; t_115; cross-process |

### R1.2 Idea Lifecycle
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 1.2.1 | Active | IMPLEMENTED | t_121 |
| 1.2.2 | Faded | IMPLEMENTED | t_122; fade_property |
| 1.2.3 | Superseded | IMPLEMENTED | t_123; replacement links |
| 1.2.4 | Proposed/Accepted/Rejected | IMPLEMENTED | t_124; Nursery semantics reused |
| 1.2.5 | Archive/Delete/Restore | IMPLEMENTED | t_125; soft semantics |

### R1.3 Unit-Level History
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 1.3.1 | No destructive overwrite | IMPLEMENTED | t_131; append-only versions |
| 1.3.2 | Property versioning | IMPLEMENTED | PropertyVersion list |
| 1.3.3 | Replacement links | IMPLEMENTED | supersedes/superseded_by; t_123 |
| 1.3.4 | Query/recovery | IMPLEMENTED | t_134 |
| 1.3.5 | Restoration | IMPLEMENTED | restore(); history preserved |

### R1.4 Provenance
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 1.4.1 | Source attribution | IMPLEMENTED | t_141; 5 sources |
| 1.4.2 | Derivation | IMPLEMENTED | derived_from field |
| 1.4.3 | Transformation/process | IMPLEMENTED | activity field |
| 1.4.4 | Provenance persistence | IMPLEMENTED | t_144 |
| 1.4.5 | Explanation | IMPLEMENTED | t_145; explain() |

### R1.5 Live Matrix Processing
| Obj | Objective | Status | Evidence |
|---|---|---|---|
| 1.5.1 | Perspective-independent | IMPLEMENTED | `set_property` (information arrival) drives all state change; zero UI/Perspective dependency in the model; LIVE MATRIX LAW upheld |
| 1.5.2 | Segmentation | IMPLEMENTED | Property-level versioning; ambiguous=UNKNOWN |
| 1.5.3 | Semantic representation update | IMPLEMENTED + SEAM_ONLY | Core: information arrival creates new ACTIVE PropertyVersion and supersedes the old (tested). Downstream notification hook `_on_information_change` is a documented no-op seam for later phases |
| 1.5.4 | Dependency-aware propagation | BELONGS_FUTURE_PHASE | No dependency model exists in Phase 1; dependencies are the explicit subject of Phase 2 (Fractal Semantic Graph). Implementing propagation without a dependency model would be theater, not capability |
| 1.5.5 | Observable change | IMPLEMENTED | `get_active_properties()` reflects arrivals; public circuit proves it |

**R3 reconciliation (2026-10-03, per Director R3 §7):** 1.5.3's core is the
version-supersession that already happens on every `set_property`; only the
downstream hook is a seam. 1.5.4 is explicitly deferred with the semantic
reason above — Director may reclassify. Total honest objective count is
therefore not 25/25; see packet.

**Fixtures:** House (t_house_fixture) + Album (t_album_fixture) PASS.
**Public circuit:** p1_idea_circuit.py PASS.
**Integrated proof:** p1_integrated_proof.py 6/6 PASS.
**Research:** 6 sources (see RESEARCH_LEDGER.md).
**Migration:** See MIGRATION_MATRIX.md.
