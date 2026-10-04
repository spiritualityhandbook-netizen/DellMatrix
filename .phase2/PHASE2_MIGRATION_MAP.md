# PHASE2_MIGRATION_MAP (final)

| Existing structure | Classification | Fate in Phase 2 |
|---|---|---|
| Canonical Phase-1 Idea | CANONICAL | Node authority. Zero relationship fields (verified). Graph attaches; Idea untouched except additive observer hook. |
| `form.dell_matrix.lineage` module | CANONICAL | Plane-unit derivation authority. Phase 2 creates NO second lineage validator. LINEAGE != CONTAINMENT (not mapped). |
| Plane.Unit.parents / origin / lineage_version | HISTORICAL_ONLY | Plane-unit derivation ancestry. Never read by the graph. No auto-migration (laundered semantics — C1). |
| Nursery Proposal.parents / affinity | HISTORICAL_ONLY | Quarantine-local affinity-trigger record. Never becomes graph edges. |
| RingedGrowth parent lineage | HISTORICAL_ONLY | Proposal trigger record (same substance as Proposal.parents). |
| Nursery revision links (supersedes_id etc.) | SPECIALIZED | Revision semantics, explicitly distinct from derivation (existing good precedent, mirrored). |
| Sandbox membership | SPECIALIZED | Flat plane-unit view-grouping, owned by Plane, unchanged. Not canonical Idea containment (C2). |
| GraphView / ViewEdge | DERIVED | View-only projection, never persisted, never canonical. Proximity edges quarantined (C6). |
| Plane.neighbors / relation_middle | UNRELATED | Spatial derivations. Never graph edges. |
| HarmonicLattice | UNRELATED | Coordinate substrate. No edges. |
| ResonanceState / affinity scores | UNRELATED | Scores, not relationship truth (pre-mortem vector #8). |
| correction_graph | DERIVED | Precedent pattern (explicit type, derived-only, no second authority). Followed, not reused (nodes are outcomes). |
| knowledge_lineage | DERIVED | Clean derived projection. Pattern reused. |
| CoreIIState.causes / deps | COMPATIBILITY_VIEW | Kept as-is; not merged into graph dependencies (C3). |
| confirm_proposal (nursery→plane) | SPECIALIZED | Existing "promotion" keeps its meaning; disambiguated from Phase-2 promote (C4). |
| Program lifecycle | UNRELATED | Program state machine, not graph state. |
| Checkpoint persistence (3-member journaled transaction) | CANONICAL | Generalized coherently to 4 members (program+nursery+ideas+graph) BEFORE the graph relies on it. |
| RootPath (historical) | N/A | No historical format exists. New semantics authored per archaeology (flow/traversal definition), honestly documented as new. |
| Mandell/Flow relationship mechanisms | UNRELATED | No edge-bearing relationship constructs found in Mandell/Flow (query deps classified above). |

**No MIGRATED entries:** nothing auto-migrates into the canonical graph. The graph starts empty; every relationship is explicitly declared with provenance. This is the honest answer to "No silent reinterpretation."
