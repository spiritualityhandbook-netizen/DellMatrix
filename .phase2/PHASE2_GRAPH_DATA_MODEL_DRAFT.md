# PHASE2 CANONICAL GRAPH DATA MODEL (DRAFT — pending existing-mechanism examination)

## Node
- Node = canonical Phase-1 Idea ID (UUID string). Node DATA lives in the Idea (Phase-1 authority, untouched).
- Graph position NEVER defines Idea identity. Identity never derived from position.

## Edge (identified object — research A3, adopted)
```
Relationship = {
  rel_id: UUID,            # edge identity (fiat, LPG-style)
  type: CONTAINS | RELATED_TO | DEPENDS_ON | REFERENCES | DERIVED_FROM,  # closed vocabulary, exactly one, directed
  source_id: Idea UUID,
  target_id: Idea UUID,
  props: {                 # type-specific, minimal
     # DEPENDS_ON: {unit: property_name, derivation: mirror|child_count|descendant_count}
  },
  status: ACTIVE | SUPERSEDED | REMOVED,   # terminal REMOVED = tombstone (research C3)
  seq: int,                # monotonic, ordering token (research C4)
  recorded_at: float,      # transaction time, system-written (research C2)
  provenance: Provenance,  # Phase-1 Provenance extended with derived_from / cause
  cause: str,              # why this entry exists (create/reparent/promote/remove/restore...)
}
```

## Persisted form: append-only log (research C2, adapted — single timeline)
- ONE persisted list per owner: all relationship entries, immutable, append-only.
- Current graph = deterministic fold: for each rel_id, the max-seq entry; ACTIVE ones form the current graph.
- NO valid-time/valid-from bitemporal second clock: conscious simplification, single transaction timeline. (Documented; revisit only if a real valid-time need appears.)
- In-memory derived indexes (by_id, by_source, by_target, by_type, active_children, active_parent) rebuilt from log on every load — NEVER persisted, never trusted.

## Containment (research B1/B2/B4)
- CONTAINS edge type with type-level invariants: ≤1 ACTIVE CONTAINS per child (target); no self-containment; no cycles (O(depth) ancestor walk pre-insert); both endpoints exist.
- Reparent = append SUPERSEDED (old) + ACTIVE (new) in one mutation. Promotion = SUPERSEDED old, no new edge (top-level). Idea record untouched → identity structurally preserved (research B3).
- Breadcrumbs/path derived on read, O(depth). Never stored.

## Association
- RELATED_TO / REFERENCES / DERIVED_FROM: many allowed, no single-parent invariant. Direction semantics documented per type.

## Derived values + propagation (1.5.4/2.5.5 — research D2/D4)
- DEPENDS_ON edge declares (target idea, unit property) + derivation kind (closed: mirror | child_count | descendant_count).
- Derived value stored AS A REGULAR IDEA PROPERTY via set_property with derivation provenance → participates in Phase-1 versioning/history/events for free. NO new event authority; NO new versioning.
- Propagation entry: graph.on_information_change(idea_id, property_name) → BFS over DEPENDS_ON edges on (idea, unit) → topological recompute → EQUALITY CUTOFF (skip set_property if equal) → evidence = normal IdeaChangeEvent with derivation provenance.
- Zero propagation is legitimate and tested. Dependencies narrow (per unit, not per Idea).

## Observer hook (2.5.1/2.5.2)
- ADDITIVE extension to Idea: add_change_listener(fn). SemanticGraph.attach(idea) subscribes; Idea._on_information_change notifies. In-memory only, re-subscribed on load. (Extension, not a closed-contract change.)

## RootPath (from archaeology decision)
- RootPath = recorded directed traversal: {path_id, root_id, edge_ids (ordered), provenance}. Persisted in graph file `paths` section (distinct structure, NOT edges).
- find_path(source, target, types) computes; hop count = the only cost metric (computationally meaningful). Persisted paths re-validated on use; STALE if an edge was removed. No invented prerequisites.

## 2.5 semantic index
- Title index (title → idea_id), updated via observer. Structural categorization only (JSON type). resolve_reference follows REFERENCES edges → Idea or UNKNOWN.

## Persistence / checkpoint
- Live file: graph_<owner>.json (the log + paths). 4th member kind "graph".
- Generalize the journaled transaction (program+nursery+ideas+graph) BEFORE relying on it. Rollback restores graph file from sealed member; in-memory graph reloads (eager convergence).
- Load: whole-graph validation (schema, endpoints exist, containment acyclic, single-active-parent) — first invalid record fails the load closed.

## Invariants (pre-mutation gate)
self-containment / cycle / missing endpoint / duplicate active CONTAINS / illegal type / illegal transition → reject with evidence. Node delete/archive/fade → explicit graph effects (no silent erase): TBD after examination of lifecycle interplay.
