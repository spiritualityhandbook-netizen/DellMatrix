# PHASE2_CONFLICT_MAP (final)

## C1. Proposal.parents (affinity) → Unit.parents (derivation) laundering
- **What:** Nursery Proposal.parents means "affinity-triggered this proposal"; on confirmation it becomes Plane.Unit.parents meaning "derivation ancestry". Two semantics, one field name, silent merge.
- **Resolution:** BOTH classified HISTORICAL_ONLY. The canonical graph NEVER reads either field. No auto-migration (would import laundered semantics). The pre-existing laundering point is out of Phase-2 scope; documented, not extended.

## C2. Sandbox (flat plane-unit containment) vs canonical Idea containment
- **What:** Sandbox is the only existing true containment — flat, one-box-per-unit, on plane units, persisted via program member.
- **Resolution:** DIFFERENT DOMAINS. Sandbox = SPECIALIZED view-grouping for plane units (owned by Plane, unchanged). Canonical containment = fractal parent/child for canonical IDEAS (owned by SemanticGraph). Never merged; never cross-queried. GraphView's "sandbox" edge kind is a view-level encoding, documented as non-canonical (Phase-2 law 2.3.2 governs the canonical graph).

## C3. CoreIIState "deps" (label strings) vs DEPENDS_ON (ID-grounded edges)
- **What:** Mandell query ops 78/79 persist free-text (a,b) "deps" pairs via the program member. Phase 2 needs ID-grounded DEPENDS_ON edges for propagation.
- **Resolution:** CoreIIState deps = COMPATIBILITY_VIEW (kept as-is, query-session bags, no production consumer). Phase-2 DEPENDS_ON edges are the ONLY dependency authority for propagation. Terminology disambiguated in docs. No silent merge.

## C4. "Promotion" term collision
- **What:** Existing "promotion/confirmation" = nursery quarantine → plane live. Phase-2 "promotion" (2.2) = nested Idea → top-level.
- **Resolution:** Disambiguated in Phase-2 docs. Phase-2 uses "promote" ONLY for nested→top-level; existing flow keeps "confirm". Acceptance criteria use the Phase-2 meaning.

## C5. Restore-mode validation skip (pre-existing injection vector)
- **What:** lineage.assign_lineage(restore=True) skips cycle/missing validation; blank_cube/persist_rest restore paths use it. A corrupted program file can inject cyclic/dangling parentage.
- **Resolution:** The GRAPH load path NEVER skips validation (no restore flag; whole-graph fail-closed validation always). The pre-existing plane vector is documented as out-of-scope for Phase 2 (not extended, not fixed here).

## C6. GraphView "vesica" proximity edges
- **What:** View-only edges derived from spatial proximity.
- **Resolution:** Quarantined to the view layer permanently. SPATIAL NEARNESS != SEMANTIC RELATIONSHIP. The canonical graph has no proximity-derived edges.
