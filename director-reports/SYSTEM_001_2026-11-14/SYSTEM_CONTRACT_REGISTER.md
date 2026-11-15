> **Deliverable 3 of SYSTEM-001 (DIR-DM-SYSTEM-001) — master contract register; statuses carry their evidence; merged is not certified.**

# SYSTEM-001 — LANE 2: MASTER CONTRACT REGISTER

**Circuit:** SYSTEM-001 (Director directive DIR-DM-SYSTEM-001, 2026-11-14).
**Lane:** 2 — contracts. **Prepared by:** Uni, contract lane.
**Sources:** THE_GRAND_PLAN_UNIFIED_2026-11-14.md (Parts I–V);
`docs/DELLMATRIX_EQUATION_LEDGER.md` (clone `sys001_clone` @ `62bdcbc`);
THL-SM-01 return; code spot-checks in `sys001_clone` (read-only).
**Status law:** VERIFIED_EXISTING / IMPLEMENTED_UNVERIFIED / PARTIAL /
PROPOSED / CONTRADICTED / UNKNOWN / HISTORICAL_ONLY. Merged ≠ certified;
implemented ≠ verified. Every status carries its evidence. Gap classes:
FUNCTIONAL / MATHEMATICAL / DOCUMENTARY / DESIGN-DECISION.
**Count:** 44 contracts — 11 boundaries + Tree five layers + cross-cutting.

---

## BOUNDARY 1 — English → LatinMandell → Dells

### SYS-C01 — English intent → Mandell composite (composer path)
- **OWNER:** H1 The Spine (english_composer) · **INPUT:** English intent text · **OUTPUT:** composite Mandell chain (joins emitted only as ` > `) · **PRECONDITION:** intent parses to a CompositeIntent · **EFFECT:** none until executed (SYS-C02/C05) · **AUTHORITY:** composer is a translator, not an executor of record · **FAILURE:** unparseable intent refused at parse; no silent rerouting · **PERSISTENCE:** none (stateless translation) · **CONSUMERS:** DCC-IV REPL branch, chain surfaces · **TEST:** english_composer_test; FL-G31-02 trace (composer emits only ` > ` joins, english_composer.py:170, :201-211)
- **STATUS: IMPLEMENTED_UNVERIFIED** — works on the residual REPL path; scoped trace evidence only, no end-to-end certification. Gap: FUNCTIONAL.

### SYS-C02 — LatinMandell Toll Booth (LM-4 forced first pass)
- **OWNER:** H8 The Doors / dock pipeline · **INPUT:** outbound dock prompt + field text · **OUTPUT:** prompt with LatinMandell decomposition block appended beside the receipt · **PRECONDITION:** curated definitions govern; imported table is shadow only · **EFFECT:** decomposition disclosed on the receipt; spine diagnostic-only · **AUTHORITY:** LatinMandell is a lens, never a source of truth (shadow doctrine) · **FAILURE:** decomposition failure disclosed, prompt sent undecomposed per Q-LM4.5 — never a silent drop (inference_dock.py:1149-1164) · **PERSISTENCE:** none in the prompt path · **CONSUMERS:** docked Psalm (Gemini) · **TEST:** LM-4 live on main (PR #416, merged b546faf8); dock prompt ceiling 1,000,000 (inference_dock.py:54)
- **STATUS: IMPLEMENTED_UNVERIFIED** — merged and live; merged ≠ certified. Guard placement defect is SYS-C34. Gap: — (contract itself); see SYS-C34.

### SYS-C03 — LatinMandell table, Splitter, Composer (LM-1/2/3)
- **OWNER:** H1 · **INPUT:** English word · **OUTPUT:** morpheme split / composed reading, PARTIAL honestly returned where a quarantined row cannot drive an answer · **PRECONDITION:** table lineage (Wikipedia CC BY-SA 4.0, 2,245 rows) verifies · **EFFECT:** none (reading only) · **AUTHORITY:** curated hand-written definitions govern over the table · **FAILURE:** lineage failure fails closed; unknown morphemes refused honestly · **PERSISTENCE:** table is data at rest · **CONSUMERS:** SYS-C02, gloss presentations · **TEST:** LM-0 census, LM-1 import lineage checks, LM-2/LM-3 honest-composition cases ('biology' full, 'incredible' PARTIAL)
- **STATUS: IMPLEMENTED_UNVERIFIED** — built and merged on the main line; not certified as a set. Gap: FUNCTIONAL (coverage).

### SYS-C04 — Seed text → atom execution honesty
- **OWNER:** H1 (seed.py, chain_exec) · **INPUT:** seed text (parse_seed; tokenizer cited as AF-2 authority, seed.py:172/:207) · **OUTPUT:** per-atom results — an unexecuted atom reports ok=False, skipped=True, with an explicit reason · **PRECONDITION:** Dell numbers resolve against the registry; compound names ride as terms · **EFFECT:** only executed atoms mutate (SYS-C05) · **AUTHORITY:** Core I per-atom UNSUPPORTED_ARGS gate · **FAILURE:** refusal is reported, never upgraded to ok=True by chain continuation · **PERSISTENCE:** via SYS-C08 bindings only · **CONSUMERS:** all chain surfaces, REPL raw-seed path (repl.py:3441) · **TEST:** core_i_arg_gate_test; PR #256/#259 scoped certification (DIR-CERT line)
- **STATUS: VERIFIED_EXISTING (scoped)** — the arg-gate and atom-honesty contract are certified within their tested surfaces; whole-grammar coverage is not claimed. Gap: — within scope.

## BOUNDARY 2 — Dells → canonical state

### SYS-C05 — Dell execution → Core mutation door
- **OWNER:** H1/H7 (chain_exec) · **INPUT:** executed atom + arguments · **OUTPUT:** state write or nothing · **PRECONDITION:** atom executed (SYS-C04) · **EFFECT:** checkpoint-before-write invariant (chain_exec.py:245-254, _ckpt before write); a pure failed atom writes NOTHING · **AUTHORITY:** the executor is the only mutation door on this path · **FAILURE:** failed atom ⇒ no write, failure preserved on the chain result (ok=False survives composition) · **PERSISTENCE:** Core II working state (SYS-C08) · **CONSUMERS:** Program state, Plane, graph · **TEST:** FL-G31-02 mutation-door invariant verification (Director SCOPED PASS)
- **STATUS: IMPLEMENTED_UNVERIFIED** — invariants verified by trace on the chain surfaces; not a whole-surface certification. Gap: FUNCTIONAL.

### SYS-C06 — FLOW execution profiles (G31-CONTRACT-02) ★ exemplar
- **OWNER:** H1 (control_runtime.FLOW_CONTRACT / FLOW_PROFILES) · **INPUT:** a flow line · **OUTPUT:** execution under exactly one profile — Profile A canonical chain (nine operators) or Profile B correspondence composition (`>`/`>>` only) · **PRECONDITION:** operator classified in FLOW_CLASSIFICATION · **EFFECT:** Profile B executes only its two operators on its surfaces · **AUTHORITY:** one vocabulary (control_runtime) for both profiles · **FAILURE:** the seven non-B operators refuse fail-closed at parse with a named FlowRefusal (flow_executor.py:45, :174); the REPL prints the refusal by name and executes nothing (D-6) · **PERSISTENCE:** none beyond SYS-C08 · **CONSUMERS:** flow_executor, english_composer, REPL DCC-IV · **TEST:** g31_contract_test 20/20 (failing-first 12/20 at base); exact-head CI all green; post-merge live REPL refusal proof on merged main
- **STATUS: VERIFIED_EXISTING** — design CONFIRMED (G31-CONTRACT-01), implemented, merged PR #417 (b39c6a0), live-proven post-merge. Authority *credit* for G-31 remains the authorities' separate act; the contract's behavior is verified. Gap: —.

### SYS-C07 — The Dell registry contract (plan ↔ registry)
- **OWNER:** H1 (registry.py + core_ii.py; the Dell Plan is the authority) · **INPUT:** Dell number · **OUTPUT:** the registry's implemented contract for that Dell · **PRECONDITION:** number in 00..99 (100 = None; 100–999 ADDRESS_RESERVED, unnamed in any source) · **EFFECT:** defines what execution may claim · **AUTHORITY:** THE PLAN STANDS — where registry and plan differ, the registry is behind (DELL-PLAN DEBT) · **FAILURE:** unknown Dell refuses by name (the pre-G31 "unknown Dell 150" misreport is the historical counterexample, fixed by SYS-C06) · **PERSISTENCE:** registry is code · **CONSUMERS:** every Dell surface · **TEST:** r2_registry_reconciliation_test; Part II census (this plan)
- **STATUS: PARTIAL** — 31/99 Dells verified clean against the plan; 69 carry debt, thin spec, or a zero foundation factor (Part II). Gap: FUNCTIONAL + DOCUMENTARY.

### SYS-C08 — Program working-state bindings
- **OWNER:** H7 (Core II) · **INPUT:** executed Dell writes · **OUTPUT:** bindings in working state · **PRECONDITION:** SYS-C05 door · **EFFECT:** bindings are working state only — they never mint a generation · **AUTHORITY:** generations are minted ONLY by the checkpoint authority (SYS-C31) — proven at pin 1c5129e (committed_generation_state ('absent', None) before/after failed-bind and DeltaFlow chains) · **FAILURE:** failed bind leaves generation state untouched · **PERSISTENCE:** Core II working state · **CONSUMERS:** chains, composer, REPL · **TEST:** G31-CONTRACT-01 C-2 persistence proof; core_ii_persist_test
- **STATUS: IMPLEMENTED_UNVERIFIED** — the separation is proven at its test points; not certified as a whole surface. Gap: — (separation); FUNCTIONAL (coverage).

## BOUNDARY 3 — Ideas → semantic graph

### SYS-C09 — Idea identity and lifecycle
- **OWNER:** H2/H5 (Program, Nursery, Plane) · **INPUT:** created/confirmed idea · **OUTPUT:** a stable idea identity with lifecycle state (proposed → confirmed → placed; sealed on forget) · **PRECONDITION:** creation through a public entry path · **EFFECT:** identity survives navigation, geometry, and lifecycle changes (the Director's §5.4 requirement — asserted by design, verified only in slices) · **AUTHORITY:** Ace's confirm is the sovereign promotion step · **FAILURE:** unconfirmed proposals never promote silently · **PERSISTENCE:** program state pair (SYS-C30) / checkpoint path (SYS-C31) · **CONSUMERS:** graph, Plane, Studio, Nursery · **TEST:** lifecycle slices across c13/c7 suites; no single end-to-end identity suite
- **STATUS: IMPLEMENTED_UNVERIFIED** — mechanisms exist and are slice-tested; the end-to-end identity guarantee is not yet one proven contract. Gap: FUNCTIONAL.

### SYS-C10 — SemanticGraph containment
- **OWNER:** H2 (form/mandell/semantic_graph.py:464, SemanticGraph) · **INPUT:** nest / promote / reparent operations · **OUTPUT:** containment structure · **PRECONDITION:** REPL-first surfaces; SemanticGraph is the ONLY containment authority (TD-2 design) · **EFFECT:** containment changes without a second store · **AUTHORITY:** TD-2 authorized as containment only — not a binding display, no cross-file atomicity claim · **FAILURE:** operations outside save/bind scope are out of contract · **PERSISTENCE:** canonical save/bind scope · **CONSUMERS:** graph views, growth, Studio · **TEST:** TD-2 candidate frozen at one implementation; **no scoped ruling receipt is linked in the §14 record**
- **STATUS: IMPLEMENTED_UNVERIFIED** — built to its design; its certification is recorded UNKNOWN for want of the receipt. Gap: DOCUMENTARY (missing receipt, not missing mechanism).

### SYS-C11 — Associations and provenance
- **OWNER:** H2/H7 (SemanticGraph edges, confirm_lineage.py) · **INPUT:** association/confirm events · **OUTPUT:** edges + provenance records · **PRECONDITION:** events through public paths · **EFFECT:** lineage is inspectable · **AUTHORITY:** provenance birth-stamp is application metadata, **not cryptographic proof** (disclosed at PR #415) · **FAILURE:** unverifiable sandbox box claims are refused by name on the receipt (growth path) · **PERSISTENCE:** graph + receipts · **CONSUMERS:** Studio, growth, evidence surfaces · **TEST:** confirm_lineage tests; confirm-placement receipts
- **STATUS: PARTIAL** — lineage works; provenance strength is metadata-grade by disclosed design, and no contract yet states what each consumer may infer from it. Gap: DESIGN-DECISION.

## BOUNDARY 4 — Semantic graph → space

### SYS-C12 — Placement (graph → Plane coordinates)
- **OWNER:** H2 (spatial_authority.py:297 SpatialAuthority; place() :324) · **INPUT:** idea id + placement inputs (anchors, graph neighbours) · **OUTPUT:** coordinates in Plane.units — Plane.units is the position STORE, SpatialAuthority OWNS placement · **PRECONDITION:** idea exists in the graph · **EFFECT:** position written to the store; readings derive from it · **AUTHORITY:** SpatialAuthority alone places; no second position writer is authorized · **FAILURE:** load failure is fail-closed (SpatialLoadError :77; forces restore silently by contrast — the restore-parity debt, Part I H4) · **PERSISTENCE:** Plane state · **CONSUMERS:** SYS-C15/16, forces, Studio views · **TEST:** spatial suites; confirm-placement (SYS-C14)
- **STATUS: IMPLEMENTED_UNVERIFIED** — the authority split is real in code; end-to-end placement semantics (which inputs may move an idea, when) are not one verified contract. Gap: FUNCTIONAL.

### SYS-C13 — Movement and forces on the Plane
- **OWNER:** H4 (forces.py; spatial_authority attract/separation/spring :119-226) · **INPUT:** positions + scores · **OUTPUT:** moved positions · **PRECONDITION:** placed ideas · **EFFECT:** force-driven movement · **AUTHORITY:** five actor forces + two witnesses (Weather, Space) per the forces study · **FAILURE:** gravity-as-pull is DISCONNECTED as a mechanism — wells are assigned (EQ-GRV-001), no pull equation consumes mass; the class description claims behavior no equation implements (ledger §5) · **PERSISTENCE:** **asymmetric** — Water and Growth persist intensity, the other forces do not (open proposal-first inventory item) · **CONSUMERS:** Plane views, growth · **TEST:** forces suites; no pull-law test exists because no pull law exists
- **STATUS: PARTIAL** — movement forces compute; the gravity contract is contradicted by its own description, and persistence parity is an open defect class. Gap: MATHEMATICAL + FUNCTIONAL.

### SYS-C14 — Confirm placement choice
- **OWNER:** H5/H2 · **INPUT:** a confirmed mixed-wall proposal · **OUTPUT:** placement — manual: Ace chooses each time, choice on the receipt; automatic: into a SANDBOX first, never directly to a wall · **PRECONDITION:** Ace's personal confirm (sovereign step) · **EFFECT:** idea placed per the recorded choice · **AUTHORITY:** Ace (manual) / sandbox-first rule (automatic) · **FAILURE:** unverifiable box claims refused by name · **PERSISTENCE:** placement + receipt · **CONSUMERS:** Plane, Nursery · **TEST:** confirm_placement_test; PR #415 merged with same-wall inheritance proven live
- **STATUS: IMPLEMENTED_UNVERIFIED** — merged and live-proven; authority credit is the separate pending act. Gap: — (behavior); DOCUMENTARY (credit).

## BOUNDARY 5 — Space → Flower / Tree

### SYS-C15 — Perspective readings of the Plane
- **OWNER:** H9/H2 (plane.py Perspective :47 — PAGE/CIRCLE/FLOWER/SPHERE/CUBE/TABLE; harmonic_lattice perception forms) · **INPUT:** Plane state · **OUTPUT:** a reading (Flower, cube, sphere, table…) · **PRECONDITION:** none (read-only) · **EFFECT:** none — coordinates stay; the reading changes (harmonic_lattice docstring contract) · **AUTHORITY:** readings are derived views, never records · **FAILURE:** an unreadable state fails the reading, never rewrites the state · **PERSISTENCE:** none · **CONSUMERS:** Studio, REPL views, SYS-C22 · **TEST:** plane/graph_view suites
- **STATUS: IMPLEMENTED_UNVERIFIED** — the derived-view discipline is the modules' stated contract and holds in code; cross-perspective consistency is not yet one tested guarantee (Grand Synchronization, step 7). Gap: FUNCTIONAL.

### SYS-C16 — Position → vesica relationship edges
- **OWNER:** H6 (graph_view.py:129 — verita_between_nodes → ViewEdge(kind="vesica"); sacred_geometry EQ-GEO-001/003/004) · **INPUT:** positioned idea pairs + radii (SYS-C20's unadmitted mapping) · **OUTPUT:** vesica edges with strength/lens values · **PRECONDITION:** real positions · **EFFECT:** the geometric relationship layer of the graph view · **AUTHORITY:** EQ-GEO-003/004 are ACTIVE_VALIDATED; EQ-GEO-001's "strength of meeting" reading is ACTIVE_UNVALIDATED · **FAILURE:** **on live content the contract is vacuous** — all real user ideas sit at (0,0), so overlap is computed over stacked positions (ledger §3 header, MPC-012; unified-plan UU-6) · **PERSISTENCE:** derived · **CONSUMERS:** graph views, SYS-C21 · **TEST:** geometry suites validate the math on synthetic positions; no test cures the live-content vacuity
- **STATUS: PARTIAL** — mechanism and core math verified; the semantic output on real content is empty until placement is real. Gap: FUNCTIONAL (placement) + MATHEMATICAL (radius, SYS-C20).

### SYS-C17 — The (111)-slice rule for product Flower comparisons ★ Director's rule
- **OWNER:** H6/H10 · **INPUT:** the FCC reference model (SYS-C18) · **OUTPUT:** the rule: any comparison of the product's Flower against the Tree is made against the **defined (111) slice** (the plane i+j+k=0 layer), never against an unrestricted 3D→2D projection (which superimposes off-plane points) · **PRECONDITION:** SYS-C18's exact definition · **EFFECT:** governs SYS-C22 presentation claims and all future Flower↔Tree evidence · **AUTHORITY:** Director, DIR-DM-SYSTEM-001 §4 · **FAILURE:** a projection-based comparison is invalid evidence under this rule · **PERSISTENCE:** this register · **CONSUMERS:** SYS-C18/22, THL admission fixture · **TEST:** THL-SM-01 cross-check was performed slice-correctly — the projected (111) layer's distance multiset equals flower_centers(rings=2) exactly, explicit symmetry fit found
- **STATUS: PROPOSED** — the rule is newly stated by the Director; the product's existing Flower generation already coincides with the slice (verified), but no product mechanism yet distinguishes slice from projection. Gap: DESIGN-DECISION (adoption into the geometry contracts).

## THE TREE OF HARMONIC LIFE — FIVE LAYERS, FIVE CONTRACTS (Director §4 separation)

### SYS-C18 — Tree L1: exact geometric kernel
- **OWNER:** H6 · **INPUT:** the definition C = {(i,j,k)/√2 : i+j+k even} · **OUTPUT:** coordinates, adjacency (12 NN), distances, shells (Euclidean census; step shells 10k²+2), slices ((111) triangular, (100) square), distance exclusions (s2 = 28, 60 — Legendre three-square), reproducible projections · **PRECONDITION:** none (pure mathematics) · **EFFECT:** none — a reference model, not a runtime mechanism (Q-THL3 fixture registration: data, not mechanism) · **AUTHORITY:** mathematics; admission is a separate ruling (THL-SM-02 Keeper gate, then Director) · **FAILURE:** any claimed property not derivable from the definition is out of contract · **PERSISTENCE:** fixture files (PR #419 evidence; hidden_files/thl_sm_01/) · **CONSUMERS:** SYS-C17/19/21/22 · **TEST:** THL-SM-01 — reproduced exactly + independently re-derived by a second construction; exclusive volume ZERO by exact proof
- **STATUS: PROPOSED** (as a product contract) — the mathematics is independently VERIFIED as research evidence; it is not implemented in the product and not yet admitted. Gap: DESIGN-DECISION (admission) — the math itself has no open gap.

### SYS-C19 — Tree L2: occupancy
- **OWNER:** H6/H2 · **INPUT:** placement facts · **OUTPUT:** per-position occupancy state: populated / empty / reserved / unavailable — **spatial facts, not claims about knowledge** (Director §4) · **PRECONDITION:** SYS-C18 + a placement source (SYS-C12 is Plane-based, not Tree-based) · **EFFECT:** occupancy readings for presentation and derived math · **AUTHORITY:** the occupancy layer reports facts; it asserts nothing semantic · **FAILURE:** unknown occupancy must read as unknown, never as empty · **PERSISTENCE:** none defined · **CONSUMERS:** SYS-C21/22 · **TEST:** none exists
- **STATUS: PROPOSED** — no occupancy layer exists in any form; Plane.units is a 2D position store, not Tree occupancy. Gap: FUNCTIONAL + DESIGN-DECISION.

### SYS-C20 — Tree L3: semantic mapping (idea ↔ location)
- **OWNER:** H6/H2 · **INPUT:** an idea · **OUTPUT:** a geometric location + radius, with provenance, **reversibly** · **PRECONDITION:** an admitted radius rule and an admitted placement rule · **EFFECT:** ideas become addressable in the Tree · **AUTHORITY:** none admitted — the existing score→radius mapping (EQ-GEO-006) is MATHEMATICALLY_UNJUSTIFIED (every constant arbitrary; ledger §3); idea radius is open question Q-F1 / UU-5 · **FAILURE:** today, any radius claim is out of contract · **PERSISTENCE:** none defined · **CONSUMERS:** SYS-C16/19/21 · **TEST:** none possible until admission
- **STATUS: PROPOSED** — blocked on a mathematical admission, not on engineering. Gap: MATHEMATICAL + DESIGN-DECISION.

### SYS-C21 — Tree L4: derived mathematical layer
- **OWNER:** H6/H10 · **INPUT:** SYS-C18/19/20 outputs · **OUTPUT:** overlap measurements, topology, void classification, harmonic readings — **each carrying its validity status** · **PRECONDITION:** the layer below it admitted · **EFFECT:** derived readings only; never records · **AUTHORITY:** per-quantity — 2D overlap core validated (EQ-GEO-003/004); sacred verita (EQ-GEO-002) MATHEMATICALLY_UNJUSTIFIED, replacement is ledger action R4-A3; 3D methods (lens volume, Čech, alpha, power diagram — EXT-GEO-001..004) are RECOVERY_CANDIDATE, not authority; THE CHORD is an Ace-adopted derived reading, never an authority · **FAILURE:** an unvalidated quantity presented without its label is a contract breach (firewall F3: overlap is not truth) · **PERSISTENCE:** none · **CONSUMERS:** SYS-C22, resonance boundary (SYS-C23) · **TEST:** THL-SM-01 covers the regular-arrangement quantities; irregular-field quantities untested (UU-8)
- **STATUS: PARTIAL** — the 2D slice of this layer exists with mixed validity (validated core, unjustified heuristic on top); the 3D layer is candidates only. Gap: MATHEMATICAL.

### SYS-C22 — Tree L5: presentation
- **OWNER:** H9 · **INPUT:** SYS-C15/18/21 readings · **OUTPUT:** 3D Tree view, 2D Flower, cube, diagram, and text views **of the same underlying data** · **PRECONDITION:** SYS-C17 slice rule for every Flower comparison · **EFFECT:** none (witness surface) · **AUTHORITY:** presentation tunes readings only (the Console doctrine); the Tree visual is PLACED in the plan (H9 tab) · **FAILURE:** a view that disagrees with the underlying data is a defect, not an interpretation · **PERSISTENCE:** presets are receipts, not records · **CONSUMERS:** Studio (SYS-C37/39) · **TEST:** sacred_geometry payloads + geometry_ascii exist and are suite-covered; the Tree view itself is unbuilt
- **STATUS: PARTIAL** — Flower/SVG/ASCII presentations exist; the Tree presentation and the same-data guarantee across views are unbuilt/untested. Gap: FUNCTIONAL.

## BOUNDARY 6 — Tree → resonance / harmony

### SYS-C23 — Resonance quantities (the live combiners)
- **OWNER:** H4/H6 (ringed_growth.py _harmonic :81-91, _affinity :123-142) · **INPUT:** two ideas' token sets, distance, scope · **OUTPUT:** harmonic/affinity values in [0,1] driving growth decisions · **PRECONDITION:** tokenized ideas · **EFFECT:** growth affinity (SYS-C26) · **AUTHORITY:** none mathematical — EQ-RES-001/002 are ACTIVE_UNVALIDATED; weights (0.40/0.22/0.13/0.13, 0.2 out-of-scope) are un-derived policy; "harmonic" has no harmonic-series basis (ledger §4) · **FAILURE:** none specified — the combiners always answer, which is itself the risk · **PERSISTENCE:** scores in growth state · **CONSUMERS:** growth, Nursery candidates · **TEST:** growth suites exercise behavior; no test validates the weights
- **STATUS: IMPLEMENTED_UNVERIFIED** — real computation, live in decisions, unvalidated as measurement. Gap: MATHEMATICAL.

### SYS-C24 — Resonance ↔ geometry link (the "vesica" log token)
- **OWNER:** H4 (resonance.py harmonize_pair :115-148) · **INPUT:** idea pair + amount · **OUTPUT:** accumulated scores/tags + a log line reading "vesica {a}⊗{b} → {mid}" · **PRECONDITION:** — · **EFFECT:** tag/score accumulation (the arithmetic is ACTIVE_UNVALIDATED) · **AUTHORITY:** **the name claims geometry the code does not compute** — harmonize_pair computes NO geometry (EQ-RES-003, DISCONNECTED aspect) · **FAILURE:** the contract as named is false; ledger action R4-A4 (rename the token or wire real geometry) is outstanding · **PERSISTENCE:** accumulated scores/tags · **CONSUMERS:** growth paths reading the log/semantics · **TEST:** none distinguishes the claim from the behavior
- **STATUS: CONTRADICTED** — name vs behavior, in-tree, with a ledger action already assigned. Gap: DOCUMENTARY + FUNCTIONAL.

### SYS-C25 — Harmonic readings synchronization (incl. THE CHORD)
- **OWNER:** H6 · **INPUT:** lattice/tree readings (cube, labeling families A/B) · **OUTPUT:** THE CHORD — the triple reading that identifies all 177 Tree centres — synchronized program-wide as a derived reading · **PRECONDITION:** SYS-C18 admission for any Tree use · **EFFECT:** none (derived) · **AUTHORITY:** Ace adopted THE CHORD (2026-11-13) as a derived reading only; harmonic_core is honestly "not an engine"; harmonic projection is a cross-check, never storage or proof (R3 lineage) · **FAILURE:** a harmonic reading presented as authority breaches the adoption terms · **PERSISTENCE:** none · **CONSUMERS:** H9 surfaces, Profile · **TEST:** Tree Harmony Mirrors study (24 labelings, chord identification) — study-grade, no product mechanism
- **STATUS: PROPOSED** — adopted as a reading, implemented nowhere as a synchronized product contract. Gap: FUNCTIONAL + DESIGN-DECISION.

## BOUNDARY 7 — Resonance → Nursery

### SYS-C26 — Evidence-backed candidate generation (growth gates)
- **OWNER:** H5 (brain.py, auto_growth.py; verita.py gates) · **INPUT:** candidate ideas · **OUTPUT:** accept / reject→residue decisions · **PRECONDITION:** candidate reaches a gate · **EFFECT:** accepted candidates flow to the Nursery; rejected leave residue records · **AUTHORITY:** the gates are heuristics — EQ-VER-002 (solo integrity), EQ-VER-003 (pair coherence), EQ-VER-004 (floor license) are all ACTIVE_UNVALIDATED policy constants (ledger §2); the human decision (SYS-C28) is the real authority downstream · **FAILURE:** fog/weak verdicts reject to residue — behavior exists; threshold validity does not · **PERSISTENCE:** residue + gate outcomes · **CONSUMERS:** Nursery · **TEST:** verita smoke (6 assertions, in-module); no validation test for any weight or threshold exists in the repo (ledger §2 evidence)
- **STATUS: IMPLEMENTED_UNVERIFIED** — the circuit runs end-to-end; its measuring instruments are uncalibrated by the ledger's own verdict. Gap: MATHEMATICAL.

### SYS-C27 — Nursery ranking and discovery
- **OWNER:** H5 · **INPUT:** pending proposals · **OUTPUT:** ranked presentation — designed formula S = 0.40·LINK + 0.25·ACE + 0.20·FRESH + 0.15·NOVEL, top-5 per topic, 200 ceiling on PENDING only · **PRECONDITION:** the formula (NURSERY_PROPOSAL_RANKING_FORMULA_2026-11-08) · **EFFECT:** what Ace sees first · **AUTHORITY:** the design document · **FAILURE:** **the designed contract was never built** — the limits census found the ranking unimplemented and the code "elastic by accident" (no formula, no ceiling enforcement as designed) · **PERSISTENCE:** — · **CONSUMERS:** Nursery surfaces · **TEST:** none for the formula (it does not exist in code)
- **STATUS: CONTRADICTED** — a confirmed design with no implementation; the surface behaves otherwise. Gap: FUNCTIONAL.

## BOUNDARY 8 — Nursery → persistence

### SYS-C28 — Proposal lifecycle and atomic acceptance
- **OWNER:** H5/H7 (nursery.py, confirm paths) · **INPUT:** proposal + Ace's confirm · **OUTPUT:** confirmed idea on the Plane; unconfirmed proposals age at 3/7/14-day marks and FADE at 30 days **only while new proposals are arriving** (Ace ruling 2026-11-10) · **PRECONDITION:** Ace's sovereign confirm for promotion · **EFFECT:** promotion is the acceptance event; FORGET = SEALING (Dock doctrine) · **AUTHORITY:** Ace · **FAILURE:** confirm races are tested (nursery_confirm_race_test); the aging/fade rule's implementation status is unverified · **PERSISTENCE:** SYS-C29/30/31 · **CONSUMERS:** Plane, Studio Nursery screen · **TEST:** confirm + race suites; no aging-rule suite identified
- **STATUS: PARTIAL** — acceptance works; the ruled lifecycle (aging/fade) is not evidenced as built. Gap: FUNCTIONAL.

### SYS-C29 — Nursery store integrity
- **OWNER:** H7 (nursery.py) · **INPUT:** proposal words (plan allows 5,000 chars) · **OUTPUT:** stored proposal · **PRECONDITION:** §1 doctrine — declared bounds only, no silent truncation · **EFFECT:** **the store silently cuts words at 240 chars** (nursery.py:212, words=words[:240]) against the 5,000-char allowance (limits census, 2026-11-13) · **AUTHORITY:** the §1 anti-truncation clause outranks the code · **FAILURE:** the failure is silent — the exact behavior the doctrine forbids · **PERSISTENCE:** the truncated text is what persists · **CONSUMERS:** every downstream reader of the proposal · **TEST:** none catches it (the census found it, not a test)
- **STATUS: CONTRADICTED** — code vs doctrine, measured. Gap: FUNCTIONAL.

### SYS-C30 — Everyday save pair (Program state)
- **OWNER:** H7 (Program save path; Q1 owns the repair) · **INPUT:** working state · **OUTPUT:** the saved file pair · **PRECONDITION:** — · **EFFECT:** each file is written safely alone; **interrupting the pair can expose a hybrid new/old state with no warning and no recovery** (crash-test finding) · **AUTHORITY:** the Director adopted LOAD-TIME CONVERGENCE as the C-A acceptance contract; Amendment F2 still required; PR #294 stands on Director hold (never-merge fence) · **FAILURE:** the hybrid exposure IS the failure; today it is undetected at load · **PERSISTENCE:** this contract IS the persistence · **CONSUMERS:** every restart · **TEST:** crash/interruption tests prove the defect; the repair's acceptance test is the adopted convergence contract, unbuilt
- **STATUS: PARTIAL** — defect proven, acceptance contract decided, repair unbuilt and gated. Gap: FUNCTIONAL.

### SYS-C31 — Checkpoint / sealed-generation persistence
- **OWNER:** H7 (form/mandell/checkpoint_generation.py; idea_checkpoint.py) · **INPUT:** checkpoint command · **OUTPUT:** a sealed generation; rollback restores by COPYING the sealed target into independent live state — never by aliasing live state to a sealed member · **PRECONDITION:** checkpoint authority only (SYS-C08) · **EFFECT:** live state converges eagerly on rollback · **AUTHORITY:** TD-1 CERTIFIED WITH NOTED BOUNDARIES within canonical save/bind scope · **FAILURE:** recovery that cannot establish a proven complete old or target pair fails closed — live state is not exposed · **PERSISTENCE:** sealed generations · **CONSUMERS:** Program, growth, all stateful surfaces · **TEST:** checkpoint_generation_stress_test; the checkpoint path passed every crash test in its circuits (contrast SYS-C30)
- **STATUS: VERIFIED_EXISTING (scoped)** — verified within the checkpoint/sealed scope and its noted boundaries; it does not cover the everyday save pair (SYS-C30). Gap: — within scope.

## BOUNDARY 9 — HCN → Dock → Psalm

### SYS-C32 — HCN orchestration
- **OWNER:** H3 (Harvest Core Network, blueprint R3 FROZEN) · **INPUT:** demand signals · **OUTPUT:** orchestrated organ hand-offs — ORGAN = NAME × JOB × HAND-OFF × HEALTH TEST × LEDGER; the DEMAND BEAT · **PRECONDITION:** R3 as frozen (Amendment B); changes only via versioned amendments · **EFFECT:** none today · **AUTHORITY:** the frozen blueprint · **FAILURE:** undefined (no mechanism) · **PERSISTENCE:** organ ledgers, by design only · **CONSUMERS:** Dock, Psalm Matrix, workspace (sequence steps 2–5) · **TEST:** none — **no HCN engine exists in form/** (grep: the only "harvest" code is lm1_harvest, the unrelated LatinMandell table harvest)
- **STATUS: PROPOSED** — a frozen, ruled design with zero implementation; sequence step 2. Gap: FUNCTIONAL.

### SYS-C33 — Dock session contract
- **OWNER:** H8 (dock_session.py) · **INPUT:** session proposals for a docked AI · **OUTPUT:** bounded session state · **PRECONDITION:** a docked Psalm · **EFFECT:** session contents held under explicit bounds · **AUTHORITY:** the dock wall (12 docks max; FORGET = SEALING; SCRAPPED keeps its denial receipt — the Dock study) · **FAILURE:** bounds refuse by message ("session.proposals exceeds _MAX_PROPOSALS", dock_session.py:186/:260/:421) · **PERSISTENCE:** session state · **CONSUMERS:** SYS-C34/35 · **TEST:** dock_wall_test, dock_proposal_b_test
- **STATUS: IMPLEMENTED_UNVERIFIED** — bounds and refusals are real and tested at unit level; the full dock contract (12-dock census, sealing semantics end-to-end) is not one verified surface. Gap: FUNCTIONAL.

### SYS-C34 — Dock prompt assembly and the size guard ⚠ IN PROGRESS
- **OWNER:** H8 (inference_dock.py) · **INPUT:** field state → assembled prompt (ceiling DEFAULT_MAX_PROMPT_CHARS = 1,000,000, :54) · **OUTPUT:** the final outbound prompt, decomposition appended (:1149-1164) · **PRECONDITION:** the size guard should fire before expensive work · **EFFECT:** **the guard sits at the wrong end of the pipeline** — on a giant input the program runs the full expensive LatinMandell decomposition FIRST (the module's own comment prices it: decomposition expands dense prose ~10×, :49) and checks size afterward; measured waste ≈ 23 s and ~100 MB before the guard fires (main-lane investigation) · **AUTHORITY:** §1 efficiency doctrine (declared bounds, no wasted work) · **FAILURE:** oversized content is eventually refused — correctly, but after paying the cost the guard exists to prevent · **PERSISTENCE:** none · **CONSUMERS:** every docked-AI interaction · **TEST:** the investigation's failing-first tests are the main lane's current work
- **STATUS: PARTIAL — IN PROGRESS** (Director-ordered LM-4 resource-guard investigation, main lane: prove the waste with tests, move the guard pre-decomposition, never refuse valid content). Gap: FUNCTIONAL (efficiency).

### SYS-C35 — Psalm role permissions (Gemini command doctrine)
- **OWNER:** H8/H9 (personas.py registry; dock surfaces) · **INPUT:** Ace/Director/Uni direction, through program surfaces only · **OUTPUT:** Psalm output — always **PENDING**, never state · **PRECONDITION:** a docked Psalm · **EFFECT:** proposals only; a Psalm never writes canonical state, never accesses the repository, has no resident mode · **AUTHORITY:** Ace > Director > Uni chain; the doctrine is recorded law · **FAILURE:** out-of-doctrine output stays PENDING and inert · **PERSISTENCE:** proposals via SYS-C28 only · **CONSUMERS:** Nursery, Studio · **TEST:** dock/persona suites; doctrine compliance is process-verified, not suite-verified
- **STATUS: IMPLEMENTED_UNVERIFIED** — the surfaces enforce the shape; no single test certifies the doctrine end-to-end. Gap: FUNCTIONAL.

### SYS-C36 — Psalm Matrix surface
- **OWNER:** H9 · **INPUT:** docked Psalms + field state · **OUTPUT:** the Psalm Matrix screen — the context-linked page set (proposal cards, field views) of Ace's future plan · **PRECONDITION:** SYS-C32/33/35 · **EFFECT:** the human testing surface (gated on a live docked AI + Ace working the Matrix himself) · **AUTHORITY:** plan (Afterplan step 4; Grand Plan SEQ4) · **FAILURE:** undefined · **PERSISTENCE:** none (surface) · **CONSUMERS:** Ace · **TEST:** none
- **STATUS: PROPOSED** — designed in the plan sequence; not built as the unified surface. Gap: FUNCTIONAL + DESIGN-DECISION.

## BOUNDARY 10 — All engines → Studio

### SYS-C37 — Studio read models and public path
- **OWNER:** H9 (Studio — a functional LOCAL-ONLY application) · **INPUT:** engine state via read models · **OUTPUT:** consistent views, errors, navigation, snapshots · **PRECONDITION:** engines expose read models · **EFFECT:** none on state (read path) except through explicit actions · **AUTHORITY:** Studio security is CERTIFIED in scope (PR #255) and browser acceptance CERTIFIED in scope (PR #258); the __RENDER__ defect is OPEN and R-B repair unauthorized · **FAILURE:** two exact-head evidence supplements (#304/#305) are HELD — GitHub ran verify against a merge-preview instead of the frozen head; PR #306's pin-and-assert fix awaits re-review · **PERSISTENCE:** none (surface) · **CONSUMERS:** Ace · **TEST:** studio_security_test, browser-acceptance workflow — certified slices; **complete public-path testing is outstanding** (Director gap table)
- **STATUS: PARTIAL** — certified slices inside an uncertified whole; one open defect fenced. Gap: FUNCTIONAL.

### SYS-C38 — Snapshots and derived-view delivery
- **OWNER:** H9/H10 · **INPUT:** subsystem state · **OUTPUT:** bounded snapshots / projections for surfaces (e.g., the Email Matrix field snapshot: first 200 Nursery + first 200 Plane items, exposed separately) · **PRECONDITION:** snapshot bounds declared · **EFFECT:** none (derived) · **AUTHORITY:** derived views never record (SYS-C15 discipline) · **FAILURE:** the bounded-snapshot repair is authorized but the general contract — every surface snapshot declares its bound and its staleness — is not stated once, anywhere · **PERSISTENCE:** none · **CONSUMERS:** Studio, Feed-like surfaces · **TEST:** per-surface tests only
- **STATUS: PARTIAL** — instances exist and one repair is authorized; the universal snapshot contract does not. Gap: DESIGN-DECISION + FUNCTIONAL.

### SYS-C39 — The Console and windowed workspace
- **OWNER:** H9 · **INPUT:** readings (visual + audio elements) · **OUTPUT:** knob/lever/number-slot control over readings; saveable presets · **PRECONDITION:** SEQ5's navigation research (Ace's standing rule: navigation researched first) · **EFFECT:** tunes readings only — derived layer, never records · **AUTHORITY:** plan (Grand Plan H9 record, 2026-11-14); toehold: visual.py already styles itself a "Visual control panel" · **FAILURE:** undefined · **PERSISTENCE:** presets as receipts · **CONSUMERS:** workspace, FAR-20 (SYS-C22 audio side) · **TEST:** none
- **STATUS: PROPOSED** — placed in the plan with a code toehold; unbuilt. Gap: FUNCTIONAL + RESEARCH (navigation study first, per Batch C C-SEQ5).

## BOUNDARY 11 — Every subsystem → evidence

### SYS-C40 — Regression and exact-head CI evidence
- **OWNER:** H10 (form/regress.py manifest; GitHub workflows) · **INPUT:** a candidate head · **OUTPUT:** per-suite verdicts at that exact head (canonical local run: 286/286 at --order rev on the G31 head; CI: build 3.10/3.11, browser-acceptance, smoke) · **PRECONDITION:** suites registered in the manifest (an unregistered suite is OMITTED — the #417 smoke failure taught this; the manifest is part of the contract) · **EFFECT:** the merge gate's evidence · **AUTHORITY:** hard gate — no terminal green, no merge · **FAILURE:** cross-environment discrepancy is itself a finding (DAF-09: local greens claim nothing toward the withheld session-escape question) · **PERSISTENCE:** CI records, run logs under goal hidden_files · **CONSUMERS:** every circuit, the Director's review · **TEST:** regress_coverage_test guards the manifest
- **STATUS: IMPLEMENTED_UNVERIFIED** — the machinery runs and gates real merges; it is infrastructure, itself verified by use, with one standing withheld discrepancy honestly carried. Gap: — (machinery); the DAF-09 item is a product-evidence gap, not a machinery gap.

### SYS-C41 — Provenance of rulings (authority input fold)
- **OWNER:** H10/H11 (WORKFLOW v1 §35 protocol) · **INPUT:** Director/Keeper mail and GitHub artifacts · **OUTPUT:** distilled ruling records in the state file · **PRECONDITION:** each authority certified ONCE (attestation + channel markers + one mechanically verified artifact) · **EFFECT:** the main session acts on distilled records; mismatches quarantine as unauthenticated · **AUTHORITY:** certification covers sources and inputs, never claims · **FAILURE:** a flagged or interrupted raw read never freezes the pipeline and is never acted on alone (the #413 lesson: independent GitHub verification + Ace's blessing before executing) · **PERSISTENCE:** state file watermarks (DIRECTOR_MAIL_/GROK_MAIL_LAST_PROCESSED) · **CONSUMERS:** all circuits · **TEST:** mechanical verification per fold (sender/subject/watermark sequence; label + diff scope + parent continuity)
- **STATUS: IMPLEMENTED_UNVERIFIED** — operating daily with its failure lesson already bought and encoded; it is a process contract, verified by operation. Gap: —.

### SYS-C42 — Failure-behavior honesty (cross-surface)
- **OWNER:** H10 (all surfaces) · **INPUT:** any refusal, skip, or failure · **OUTPUT:** the failure visible by name, with its reason, on the surface where it happened · **PRECONDITION:** SYS-C04/C06 behaviors · **EFFECT:** no silent vanishing (the pre-G31 refused flow line disappeared and a later error blamed "unknown Dell 150" — the canonical counterexample) · **AUTHORITY:** the honesty contracts (D-6/D-7; ledger firewall F3) · **FAILURE:** a swallowed failure is a defect class (cleanup errors fail tests explicitly, never except-pass) · **PERSISTENCE:** receipts carry refusals · **CONSUMERS:** Ace, the Director, every operator · **TEST:** r2_semantic_honesty_test (27/27 on merged main); g31_contract_test T-5a/b/c
- **STATUS: VERIFIED_EXISTING (scoped)** — verified on the flow/chain surfaces where it was built and live-proven post-merge; universality across all surfaces is the Grand Synchronization's test burden, not yet discharged. Gap: FUNCTIONAL (coverage).

## CROSS-CUTTING CONTRACTS

### SYS-C43 — The Verita name firewall
- **OWNER:** H10 (ledger §10, binding) · **INPUT:** any surface reporting a "verita" value · **OUTPUT:** the value labeled as exactly one of VERITA-SMITH (historical), VERITA-MEET (coherence-of-meet, EQ-GEO-002), VERITA-JUDGE (structural checks, EQ-VER-002/003) · **PRECONDITION:** — · **EFFECT:** prevents cross-borrowing of equations, thresholds, interpretations (F1–F5) · **AUTHORITY:** the ledger firewall; R4-A2 requires namespacing/renaming at least two of the three · **FAILURE:** **today, surfaces do not reliably say which verita they report** — the rename is outstanding and the collision is live (three mechanisms, one word, shared callers in brain/auto_growth) · **PERSISTENCE:** — · **CONSUMERS:** SYS-C16/23/26 and every REPL/report surface · **TEST:** none enforces the labeling
- **STATUS: CONTRADICTED** — a binding rule the current surfaces do not yet obey. Gap: DOCUMENTARY + FUNCTIONAL.

### SYS-C44 — One overlap authority (the duplicate vesica)
- **OWNER:** H6/H10 · **INPUT:** — · **OUTPUT:** the law: no two formulas silently define the same semantic quantity (ledger law) · **PRECONDITION:** — · **EFFECT:** **the vesica strength core is implemented twice live** — sacred_geometry.py:145 (canonical, EQ-GEO-001) and verita.py:31-44 (EQ-VER-001, DUPLICATE), plus a frozen third copy in legacy JS · **AUTHORITY:** ledger R4-A1 assigns the dedup (verita.py must delegate or be removed with callers migrated) — **not performed** · **FAILURE:** two live authorities for one quantity is the failure, ongoing · **PERSISTENCE:** — · **CONSUMERS:** SYS-C16/26 · **TEST:** none asserts the singleness
- **STATUS: CONTRADICTED** — the ledger's own first law, violated in-tree, with the repair already specified and unexecuted. Gap: FUNCTIONAL.

---

## SUMMARY TABLE — ID × STATUS × GAP CLASS

| ID | Contract | Status | Gap class |
|---|---|---|---|
| SYS-C01 | English → Mandell composite | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C02 | LatinMandell Toll Booth (LM-4) | IMPLEMENTED_UNVERIFIED | — |
| SYS-C03 | LM table / Splitter / Composer | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C04 | Seed → atom execution honesty | VERIFIED_EXISTING (scoped) | — |
| SYS-C05 | Dell → Core mutation door | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C06 | FLOW execution profiles | VERIFIED_EXISTING | — |
| SYS-C07 | Dell registry contract | PARTIAL | FUNCTIONAL + DOCUMENTARY |
| SYS-C08 | Working-state bindings | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C09 | Idea identity & lifecycle | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C10 | SemanticGraph containment | IMPLEMENTED_UNVERIFIED | DOCUMENTARY |
| SYS-C11 | Associations & provenance | PARTIAL | DESIGN-DECISION |
| SYS-C12 | Placement (SpatialAuthority) | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C13 | Movement & forces | PARTIAL | MATHEMATICAL + FUNCTIONAL |
| SYS-C14 | Confirm placement choice | IMPLEMENTED_UNVERIFIED | DOCUMENTARY |
| SYS-C15 | Perspective readings | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C16 | Position → vesica edges | PARTIAL | FUNCTIONAL + MATHEMATICAL |
| SYS-C17 | (111)-slice comparison rule | PROPOSED | DESIGN-DECISION |
| SYS-C18 | Tree L1 exact kernel | PROPOSED (math verified as research) | DESIGN-DECISION |
| SYS-C19 | Tree L2 occupancy | PROPOSED | FUNCTIONAL + DESIGN-DECISION |
| SYS-C20 | Tree L3 semantic mapping | PROPOSED | MATHEMATICAL + DESIGN-DECISION |
| SYS-C21 | Tree L4 derived math | PARTIAL | MATHEMATICAL |
| SYS-C22 | Tree L5 presentation | PARTIAL | FUNCTIONAL |
| SYS-C23 | Resonance quantities | IMPLEMENTED_UNVERIFIED | MATHEMATICAL |
| SYS-C24 | Resonance ↔ geometry link | CONTRADICTED | DOCUMENTARY + FUNCTIONAL |
| SYS-C25 | Harmonic readings / THE CHORD | PROPOSED | FUNCTIONAL + DESIGN-DECISION |
| SYS-C26 | Candidate generation gates | IMPLEMENTED_UNVERIFIED | MATHEMATICAL |
| SYS-C27 | Nursery ranking | CONTRADICTED | FUNCTIONAL |
| SYS-C28 | Proposal lifecycle & acceptance | PARTIAL | FUNCTIONAL |
| SYS-C29 | Nursery store integrity | CONTRADICTED | FUNCTIONAL |
| SYS-C30 | Everyday save pair | PARTIAL | FUNCTIONAL |
| SYS-C31 | Checkpoint / sealed generations | VERIFIED_EXISTING (scoped) | — |
| SYS-C32 | HCN orchestration | PROPOSED | FUNCTIONAL |
| SYS-C33 | Dock session | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C34 | Dock prompt guard | PARTIAL — IN PROGRESS | FUNCTIONAL |
| SYS-C35 | Psalm role permissions | IMPLEMENTED_UNVERIFIED | FUNCTIONAL |
| SYS-C36 | Psalm Matrix surface | PROPOSED | FUNCTIONAL + DESIGN-DECISION |
| SYS-C37 | Studio read models | PARTIAL | FUNCTIONAL |
| SYS-C38 | Snapshots / derived views | PARTIAL | DESIGN-DECISION + FUNCTIONAL |
| SYS-C39 | Console / workspace | PROPOSED | FUNCTIONAL + RESEARCH |
| SYS-C40 | Regression & exact-head CI | IMPLEMENTED_UNVERIFIED | — |
| SYS-C41 | Ruling provenance fold | IMPLEMENTED_UNVERIFIED | — |
| SYS-C42 | Failure-behavior honesty | VERIFIED_EXISTING (scoped) | FUNCTIONAL (coverage) |
| SYS-C43 | Verita name firewall | CONTRADICTED | DOCUMENTARY + FUNCTIONAL |
| SYS-C44 | One overlap authority | CONTRADICTED | FUNCTIONAL |

**Counts:** VERIFIED_EXISTING 4 (C04, C06, C31, C42 — three of them scoped) ·
IMPLEMENTED_UNVERIFIED 16 · PARTIAL 11 · PROPOSED 8 · CONTRADICTED 5 ·
UNKNOWN 0 · HISTORICAL_ONLY 0. (The ledger's historical stratum —
EQ-SMI-001..006, EQ-GEO-011/012/015 — is registered in the ledger itself
and intentionally not re-contracted here; VERITA-SMITH appears inside
SYS-C43 as a historical name, not a live contract.)

**Boundaries with NO verified contract:** Boundary 3 (best:
IMPLEMENTED_UNVERIFIED, with SYS-C10's certification receipt missing),
Boundary 5 incl. the Tree layers (best: PARTIAL; the kernel's math is
verified as *research*, which is not a product contract), Boundary 6
(best: IMPLEMENTED_UNVERIFIED, plus one CONTRADICTED), Boundary 9
(best: IMPLEMENTED_UNVERIFIED), Boundary 10 (best: PARTIAL).

*End of Lane 2 register. Companion lanes hold the census, the
dependency graph, and the gap ledger; this register's statuses are
the contract layer they cite.*
