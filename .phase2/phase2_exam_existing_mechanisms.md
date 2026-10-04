# PHASE 2 EXAMINATION — EXISTING MECHANISM MAP

**Scope:** relationship / lineage / graph-like mechanisms in the current codebase.
**Worktree:** `~/workspace/dellmatrix-gdp-phase1` @ `gdp-phase2-work` (38819e4), READ-ONLY examination.
**Date:** 2026-10-03.
**Convention:** FACT = read directly from code (file:line cited). INFERENCE = judgment, labeled as such.

---

## M1. `form.dell_matrix.lineage` — the lineage authority (FACT: single authority module)

- **File:** `form/dell_matrix/lineage.py` (full module, 118 lines)
- **Docstring claim:** "Single lineage authority: parents, origin, version, inspect." (line 2)
- **What it stores:** NOTHING itself. Pure functions operating on a caller's unit dict:
  - `normalize_parents` (line 8): dedupe + strip → `List[str]`
  - `child_version` (line 16): `1 + max(parent lineage_versions)`
  - `_ancestors` (line 32): cycle-guarded BFS traversal; detects cycles and missing parents
  - `assign_lineage` (line 51): validates `self_parent`, `lineage_cycle`, `missing_parent`; returns `{ok, parents, origin, lineage_version, missing}`. `restore=True` SKIPS cycle/missing validation (line 63).
  - `inspect_lineage` (line 101): returns `{parents, children, ancestors, origin, lineage_version, cycle, missing_parents}` — children computed by reverse scan.
- **Writers:** none directly; called by `Plane.place` (plane.py:118), `confirm_proposal` (confirm_lineage.py:37), `knowledge_lineage.lineage_record` (read path).
- **Semantics claimed:** DERIVATION ANCESTRY ("where this unit came from": placed / confirmed / merge / split). NOT containment — nothing in the module speaks of nesting.
- **Persistence:** none of its own; results are stored on Unit fields (see M2) and persist through them.
- **Checkpoint/rollback:** participates indirectly via Unit persistence in the program member.
- **Authority-collision risk:** LOW as a module — it is already the single authority for derivation lineage. Phase 2 must NOT create a second lineage validator. The open question is only whether derivation ancestry maps to containment (per Phase-2 law, LINEAGE != CONTAINMENT unless explicitly mapped).

---

## M2. `Plane.Unit.parents` — derivation ancestry on plane units

- **File:** `form/dell_matrix/plane.py:48-62` (dataclass `Unit`; `parents: List[str]` at line 60, plus `origin: str` at 61, `lineage_version: int` at 62)
- **Data model:** `parents` = list of unit-ID strings (write-once at placement). `origin` ∈ {"placed", "confirmed", "merge", "split", ...} (free string). `lineage_version` = 1 + max(parent versions).
- **Writers** (all go through `Plane.place` → `assign_lineage`; plane.py:96-134):
  - `blank_cube.place_idea` (blank_cube.py:34) — passthrough for all `program.place` calls
  - `confirm_lineage.confirm_proposal` (confirm_lineage.py:51-54) — nursery promotion, `origin="confirmed"`, parents carried from proposal
  - `live_identity.merge_live` (live_identity.py:67-74) — `parents=parent_ids`, `origin="merge"`, with snapshot verification that parents weren't mutated mid-operation
  - `live_identity.split_live` (live_identity.py:101-102) — `parents=[source.id]`, `origin="split"`
  - Restore paths: `blank_cube.py:61` and `persist_rest.py:316` — both call `place(..., restore=True)`, which SKIPS lineage validation (lineage.py:63)
  - `open.py:971` `place` → `cube.place_idea` → same chain (public runtime surface)
- **Post-placement mutation:** NONE EXISTS (FACT: grep for `.parents =` / `.parents.append` finds only test assertions). Parents are immutable after placement — there is NO reparenting API today.
- **Readers:**
  - `Plane.inspect_lineage` (plane.py:135) → `lineage.inspect_lineage`
  - `knowledge_lineage.lineage_record` (knowledge_lineage.py:52)
  - `Plane.render` (plane.py:269) — display only
  - REPL `lineage` command (repl.py:2063-2077) — display only
  - `persist.py:118` — serialization
- **Semantics claimed:** derivation ancestry. Children are computed by reverse scan (lineage.py:106), not stored.
- **Persistence:** YES — `form/persist.py:106-122` serializes each unit including `parents`, `origin`, `lineage_version` into `program_<owner>.json` → checkpoint member `"program"` (checkpoint_generation.py:69). Restore via `persist_rest.py:311-320`.
- **Checkpoint/rollback:** YES, via the program member (whole-file atomic; rollback restores the sealed program file including plane units).
- **Authority-collision risk:** MEDIUM-HIGH. This is the closest thing to a parentage authority. Two specific hazards: (a) on nursery confirmation, `Proposal.parents` (affinity-trigger semantics, M3) flows into `Unit.parents` (derivation semantics) — a semantic laundering point; (b) restore-mode skips cycle/missing validation, so a corrupted program file can inject cyclic or dangling parentage that the live validators would have rejected — Phase-2 cycle invariants must cover the restore path.

---

## M3. `Nursery.Proposal.parents` — affinity-trigger proposal parentage

- **File:** `form/dell_matrix/nursery.py:100-121` (`parents: List[str]` at line 108)
- **Data model:** plain `List[str]` — NO validation at `add()` (nursery.py:132-159 just does `parents or []`). Plus `affinity: float` (line 109), `reason: str` (line 110), and DCC-XVI revision links: `lifecycle_state`, `supersedes_id`, `superseded_by_id`, `revision_root_id`, `revision_number` (lines 114-119).
- **Writers:**
  - `RingedGrowth.run` (ringed_growth.py:305: `parents=[a, b]` for Solstice new; :332: `parents=[primary]` for Equinox/Standstill evolved; :241: `parents=[]` for body-restore proposals) — parents are the plane unit IDs whose token/spatial affinity triggered the proposal
  - `supersession.py:368-375` — creates successor with `parents=[]` explicitly; comment at lines 313-316: "The successor is created as a derivation root (parents=[]): revision ancestry is NOT derivation ancestry."
  - `Nursery.add` direct callers
- **Readers:**
  - `confirm_proposal` (confirm_lineage.py:37,51) — carries proposal parents into plane placement (become M2 Unit.parents)
  - `proposal_valid.proposal_parents` / `proposal_valid_for_plane` (proposal_valid.py:8-31) — confirmability gate: ALL parent IDs must be live plane units
  - REPL `lineage` command (repl.py:2066-2069)
- **Semantics claimed:** "which live ideas triggered this proposal" (affinity lineage). NOT containment, NOT derivation in the Unit.parents sense — yet it BECOMES Unit.parents on confirmation.
- **Persistence:** YES — `to_dict()` (asdict) into `nursery_<owner>.json` → checkpoint member `"nursery"`. Fail-closed load (`NurseryLoadError`).
- **Checkpoint/rollback:** YES, via the nursery member (own atomic file; part of the journaled 3-member transaction).
- **Authority-collision risk:** HIGH. This is the #1 collision risk: two different parent-semantics (affinity-trigger vs derivation) share one field name and one flows into the other at confirmation. Phase 2 must explicitly classify: does proposal parentage map to graph edges, derivation ancestry, or stay a quarantine-local record?

---

## M4. `Plane.box` / `Sandbox` — the existing containment mechanism

- **File:** `form/dell_matrix/plane.py:78-83` (`Sandbox`: `id`, `member_ids: List[str]`); `Plane.box` (176-188), `Plane.unbox` (190-198); `Unit.sandboxed: bool` (56), `Unit.sandbox_id: Optional[str]` (57)
- **Data model:** flat membership. A unit is in at most one sandbox (`sandbox_id` is a single optional string). No nesting of sandboxes. No cycle protection needed (flat), none present.
- **Writers:** `Plane.box`, `Plane.unbox`, `Plane.remove` (auto-unbox at line 142).
- **Readers:** `Plane.enhance_scope` (213-221: sandboxed units scope to box members), `Plane.render` (box display), `GraphView.build_view` (graph_view.py:118: emits `ViewEdge(source=uid, target=sandbox_id, kind="sandbox")`).
- **Semantics claimed:** membership grouping ("box"). This IS containment-like — the only existing one.
- **Persistence:** YES — `persist.py:124` (`sandboxes = {sid: list(sb.member_ids)...}`) + per-unit `sandboxed`/`sandbox_id` (persist.py:114-115) → program member → checkpoint.
- **Authority-collision risk:** HIGH. Phase 2 introduces canonical containment for Ideas; the Sandbox is an existing containment semantic on plane units. MUST be explicitly classified: does Sandbox become canonical containment, a specialized view-grouping, or legacy? Note the GraphView already encodes sandbox membership as a generic edge kind `"sandbox"` — exactly what Phase-2 law 2.3.2 forbids ("Containment SHALL NOT be represented as a generic association").

---

## M5. `GraphView` / `ViewEdge` — existing typed-edge graph projection

- **File:** `form/dell_matrix/graph_view.py:36-44` (`ViewEdge`: `source: str, target: str, kind: str`); `build_view` at line 91
- **Data model:** `GraphView` (line 47): perspective, zoom, `nodes: List[ViewNode]`, `edges: List[ViewEdge]`, sandboxes, floor. Edge kinds emitted: `"enhance"` (from `enhance_scope`, line 116), `"sandbox"` (line 118), `"vesica"` (lines 122-134, derived from spatial proximity via `verita_between_nodes(..., max_dist=3.5, min_verita=0.2)` with an all-pairs fallback).
- **Writers:** `build_view(plane, scores)` only — pure derivation, no stored edges.
- **Readers:** ASCII renderer, `to_dict()` ("DellMatrixGraphView" version 2) — UI contract consumers.
- **Semantics claimed:** view projection, explicitly "UI contract" (line 2). Not truth.
- **Persistence:** NONE. Built on demand, never written to disk, not in checkpoint.
- **Authority-collision risk:** MEDIUM. It is the only existing edge-typed graph structure, so it will be tempting to treat as precedent. Two hazards: (a) `"vesica"` edges are proximity-derived — Phase-2 law "SPATIAL NEARNESS != SEMANTIC RELATIONSHIP" must keep this quarantined to the view layer; (b) `"sandbox"` edges encode containment as a generic edge kind — prohibited by Phase-2 law 2.3.2. Classification: DERIVED view, never canonical.

---

## M6. `Plane.neighbors` / `Plane.relation_middle` — derived spatial relations

- **File:** `form/dell_matrix/plane.py:223-234` (`neighbors`: euclidean distance ≤ radius → List[str]); `:236-240` (`relation_middle`: returns synthetic `{"middle": "relation(A⊗B)", "distance": ...}` dict, "Flower/Vesica — shared middle from two centers")
- **Data model:** computed on call; nothing stored.
- **Semantics claimed:** spatial proximity (neighbors); poetic/geometric midpoint (relation_middle). Neither claims semantic relationship.
- **Persistence:** none. Checkpoint: n/a.
- **Authority-collision risk:** LOW. Pure derivations. Must stay out of the semantic graph per Phase-2 law.

---

## M7. `RingedGrowth` affinity — computed pair scores

- **File:** `form/dell_matrix/ringed_growth.py:124-148` (`_affinity`: harmonic*0.40 + jaccard*0.22 + spatial*0.13 + in_scope*0.13 + goal_boost + body_boost)
- **Data model:** ephemeral dict per pair; only the scalar `affinity` is stored on the resulting Proposal (M3).
- **Semantics claimed:** growth-trigger scoring ("sole public growth path"), NOT relationship truth.
- **Persistence:** only via Proposal.affinity. Checkpoint: via nursery member.
- **Authority-collision risk:** MEDIUM (pre-mortem vector #8: "treating affinity/resonance as graph truth"). Affinity is token-overlap + spatial distance — it must never become a graph edge weight without explicit semantic authorization.

---

## M8. `HarmonicLattice` — coordinate lattice (NOT a relationship store)

- **File:** `form/dell_matrix/harmonic_lattice.py:65-158`
- **Data model:** `cells: Dict[(h,v,f), Cell]` where Cell holds arbitrary `content: Any`, label, tags. `chord_neighbors` (line 95) computes coordinate adjacency — derived, not stored.
- **Semantics claimed:** "One lattice. Cube/core, square/circle... are perception modes — coordinates stay; reading changes." Pure perception/spatial substrate.
- **Persistence:** `form/persist.py:85-99` serializes cells (content coerced to str/int/float/bool/None) — lattice state persists, but no relationships are stored in it.
- **Authority-collision risk:** LOW. No parentage, no edges. (INFERENCE: the main risk is terminological — "lattice" vs "graph" — not architectural.)

---

## M9. `ResonanceState` — per-unit scores (NOT a relationship store)

- **File:** `form/dell_matrix/resonance.py:37-44` (`scores: Dict[str, float]`, `tags: Dict[str, Dict[str, float]]`, `log`, `pulse_count`)
- **Semantics claimed:** computed coherence scores per unit. No pairwise storage.
- **Authority-collision risk:** LOW (same quarantine as affinity: resonance ≠ graph truth).

---

## M10. `correction_graph.correction_edges` — derived outcome graph (precedent)

- **File:** `form/mandell/correction_graph.py:100-170`
- **Data model:** derived list of `{earlier_outcome_id, later_outcome_id, relationship: "CORRECTION_CANDIDATE", shared_knowledge_ids, temporal_evidence, confidence, reason}`. Explicit edge TYPE (`RELATIONSHIP = "CORRECTION_CANDIDATE"`, line 40) with confidence classes (FACT / DERIVED_FACT / PROJECTION / UNKNOWN).
- **Semantics claimed:** explicitly NON-causal projection. Module docstring: "It is not automatically 'the thing that fixed' the earlier failure... No new ledger. No second Outcome authority."
- **Persistence:** NONE — derived on demand from the Outcome ledger. Not in checkpoint.
- **Authority-collision risk:** LOW. This is the codebase's best existing example of the pattern Phase 2 should follow: explicit edge type, derived-only, no second authority. Note its nodes are OUTCOMES, not ideas — no overlap with the idea graph.

---

## M11. `CoreIIState.causes` / `deps` — persisted Mandell query relations

- **File:** `form/mandell/core_ii_exec.py:29-30` (`causes: List[tuple]`, `deps: List[tuple]`)
- **Data model:** lists of `(a, b)` string tuples. Written by Mandell query ops 78/79 (`query_ops.py:160-162` → `_relation`, lines 166-189): parses `"A>B"` labels, rejects self-relations and duplicates, appends to `st.causes` / `st.deps`. Labels are FREE TEXT, not canonical IDs; no endpoint existence validation; only two implicit types ("cause", "depend").
- **Writers:** Mandell query execution only (user-issued `78`/`79` queries).
- **Readers:** `query_reasoning_test`, `core_ii_persist_test` (tests); no production consumer found (FACT: no other non-test references to `.causes`/`.deps` outside query_ops and persist).
- **Semantics claimed:** query-session relation bags ("A causes B", "A depends on B").
- **Persistence:** YES — `form/persist_core_ii.py:83-84` serializes, `:135-136` restores → program file → checkpoint via program member.
- **Authority-collision risk:** MEDIUM. Persisted, typed-ish ("depend") relationships — and "deps" is exactly the term Phase-2 dependency propagation needs. Two hazards: (a) terminology collision; (b) these are label-strings, not ID-grounded edges — if Phase 2 builds dependency edges, these must be classified (COMPATIBILITY_VIEW or DEPRECATED) rather than silently merged.

---

## M12. `knowledge_lineage` — derived lineage projection for selection

- **File:** `form/mandell/knowledge_lineage.py` (full module)
- **Data model:** derived records `{unit_id, origin_kind, origin, parent_ids, root_ids, depth, status, cycle, missing_parents}`; groupings by shared root.
- **Semantics claimed:** "descriptive metadata only — it never boosts relevance rank and never resolves conflicts" (docstring). Explicitly defers to `form.dell_matrix.lineage` as the authority.
- **Persistence:** none. Checkpoint: n/a.
- **Authority-collision risk:** LOW. Clean derived projection; Phase 2 can reuse the pattern.

---

## M13. Nursery revision links — `supersedes_id` / `superseded_by_id` / `revision_root_id`

- **File:** `form/dell_matrix/nursery.py:114-119`; `form/mandell/supersession.py` (notably lines 313-316)
- **Data model:** bidirectional revision links on Proposal; canonical Idea side has `PropertyVersion.supersedes` (idea.py:108) — version-level, NOT idea-level.
- **Semantics claimed:** revision ancestry, EXPLICITLY distinguished from derivation ancestry ("revision ancestry is NOT derivation ancestry", supersession.py:315).
- **Persistence:** yes (nursery member; idea member respectively).
- **Authority-collision risk:** MEDIUM. A second link system with its own semantics. Must be classified as specialized (revision) semantics, not containment or derivation. The existing explicit distinction is good precedent — Phase 2 should mirror this discipline.

---

## M14. `confirm_lineage.confirm_proposal` — the existing "promotion" path

- **File:** `form/dell_matrix/confirm_lineage.py:27-72`
- **What it does:** canonical confirmation authority: SELECT PENDING → VALIDATE/ASSIGN LINEAGE → PLACE on plane → COMMIT `Nursery.confirm` → persist. Carries proposal parents → unit parents, `origin="confirmed"`, inherits goals/detail from parents.
- **Semantics claimed:** quarantine → live promotion. NOT nested → top-level promotion (that operation does not exist yet).
- **Authority-collision risk:** MEDIUM (terminological). Phase-2 "promotion" (2.2) means nested Idea → top-level; the existing "promotion/confirmation" means nursery → plane. The directive's acceptance world uses "promote Music Studio to top-level" — the word must be disambiguated in Phase-2 docs or the two promotions will be confused.

---

## M15. Canonical Phase-1 Idea — clean slate (FACT)

- **File:** `form/mandell/idea.py` (842 lines)
- **Relationship fields:** NONE. Grep for parent/child/relation/edge/link/contain/depend finds only `PropertyVersion.supersedes` (line 108, version-level link) and docstring mentions. No idea-level parentage, containment, or association fields exist.
- **Authority-collision risk:** NONE — this is the clean foundation the canonical graph authority should attach to.

---

## M16. RootPath / RuPat — historical only (FACT: no runtime existence)

- **Code:** ZERO hits in any `.py` file; ZERO hits in git history (693 commits searched, `--grep=rootpath` and filename filters empty).
- **Docs only:** `preform/MANUAL_EXTRACT.md:12,18` ("Attach RuPat / flow"; "Fog = drop from active workspace; may return via RuPat") and `preform/VISUAL_GLYPH_LAYER.md:18,44,58,65,110` (flow diagonals, fog-return path). Equation ledger (`docs/DELLMATRIX_EQUATION_LEDGER.md:380`) classifies: "preform design docs only... No runtime equations found... UNKNOWN as mathematics; preserved as design vocabulary. No-loss law applies: do not erase, do not invent." GDP ledger 0.4.3 records the same.
- **Recovered semantics (INFERENCE from the two doc sources):** RuPat appears to be a *return-path* concept — how a fogged (archived-from-workspace) item may return — attached to flow, not a graph of ideas. It is NOT described as parent/child containment or as a generic relationship graph anywhere in the sources found.
- **Authority-collision risk:** LOW for collision (nothing exists to collide with); the risk is FABRICATION — inventing graph semantics the history does not support. Any RootPath implementation must be documented as new semantics honestly derived from, not "recovered" from, these fragments.

---

## M17. Minor / ephemeral mechanisms (for completeness)

- **`GrowEvent`** (idea_grow.py:92-100): `{cycle, source, target, affinity, action, detail}` — in-memory growth report only. No persistence. Risk: NONE.
- **`first_person.neighbors_cube/sphere`** (first_person.py:31-77): lattice coordinate adjacency. Risk: NONE.
- **`idea_grow.pair_affinity`** (idea_grow.py:68-89): second affinity implementation (simpler than RingedGrowth's). Ephemeral. Risk: LOW (duplicate affinity logic — NULL may flag as duplication, not authority).
- **`open.py:912` `verita_edges`**: view-layer vesica edges. Risk: LOW (view only).
- **`live_identity.merge_live/split_live`**: derivation writers with snapshot-verified parent immutability — good precedent for grounded derivation. Risk: LOW.
- **`lineage_bind.py`**: retired shim (`RETIRED = True`, "Lineage is native on confirm and load"). Risk: NONE.

---

## CHECKPOINT / PERSISTENCE SUMMARY (FACT)

- `_MEMBER_KINDS = ("nursery", "program", "ideas")` (checkpoint_generation.py:69).
- `Unit.parents/origin/lineage_version` → `program_<owner>.json` "plane" section (persist.py:106-122) → program member → checkpoint/rollback: YES.
- `Proposal.parents/affinity/revision links` → `nursery_<owner>.json` (nursery.py:199-247) → nursery member → checkpoint/rollback: YES.
- `CoreIIState.causes/deps` → program file via persist_core_ii.py:83-84 → checkpoint: YES (via program member).
- Canonical Ideas → ideas member → checkpoint: YES (no relationship fields).
- Sandbox membership → program file (persist.py:114-115,124) → checkpoint: YES.
- GraphView edges, neighbors, relation_middle, lattice chord adjacency, resonance scores, correction edges, knowledge_lineage records → NOT persisted (derived).

---

## TOP 3 AUTHORITY-COLLISION RISKS

1. **Proposal.parents → Unit.parents semantic laundering (M3→M2).** Two different parent-semantics share one field name: proposal parents mean "affinity-triggered this proposal" while unit parents mean "derivation ancestry". On confirmation they merge silently. When Phase 2 adds a third semantics (containment parentage), this field becomes a three-way collision. The canonical graph authority must decide the fate of each semantics explicitly — NOT inherit the merged field as graph truth.

2. **Sandbox membership vs canonical containment (M4).** The only existing true containment (flat box membership, persisted, checkpointed) will collide with Phase-2 fractal containment unless explicitly classified. The GraphView already encodes it as a generic `"sandbox"` edge — the exact anti-pattern Phase-2 law 2.3.2 forbids. Decide: canonical containment, specialized grouping, or legacy — before building.

3. **`CoreIIState.causes`/`deps` (M11).** Persisted, typed-ish ("depend") relationships using the exact term Phase 2 needs for dependency propagation — but they are unvalidated free-text label pairs, not ID-grounded edges. If Phase-2 "declared dependencies" and Mandell "deps" coexist unclassified, two dependency authorities exist. Classify as COMPATIBILITY_VIEW or DEPRECATED early; do not merge silently.

**Honorable mention:** restore-mode lineage validation skip (lineage.py:63, persist_rest.py:316, blank_cube.py:61) — a cycle/dangling injection vector through load that Phase-2 cycle invariants must cover, since checkpoint restore is a trust boundary.
