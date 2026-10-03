# PHASE2_AUTHORITY_MAP (draft skeleton — fill from examination reports)

## The one canonical question
WHAT IS THE CURRENT CANONICAL IDEA RELATIONSHIP?
→ Answered by: TBD (candidate: one SemanticGraph per owner, own persisted file, 4th checkpoint member)

## Node authority
- Node = canonical Idea identity (Idea.id, UUID). Node DATA lives in the Idea (Phase-1 authority, untouched).
- Graph position NEVER defines Idea identity.

## Edge authority
- Edge = typed directed relationship between two Idea IDs, with its own edge UUID identity.
- Containment: CONTAINS edges, one ACTIVE parent per child, system-invariant-enforced.
- Association: typed edges (types TBD after research), many allowed.
- Inverse traversal: DERIVED index, never independently persisted.

## Non-authorities (must not claim parentage incompatibly)
- Plane.Unit.parents → TBD (see EXISTING_MECHANISM_MAP)
- Nursery Proposal.parents → TBD
- RingedGrowth lineage/affinity → TBD (affinity is NOT relationship truth)
- HarmonicLattice → TBD
- View/perspective projections (graph_view.py etc.) → DERIVED PROJECTIONS only
## RootPath — RECOVERED (2026-10-03, git archaeology, /tmp/phase2_exam_rootpath_history.md)
"RootPath" as a literal term has NO historical authority: it is a Phase-0
ledger neologism (English gloss for "RuPat"). RuPat has two real historical
meanings: (a) RU→PAT 7-stage ingest pipeline (dead code, 0 callers) — NOT a
graph route; (b) RuPat = flow/direction of execution (preform design docs,
never implemented): "Structure = edges; Flow = RuPat; Markers = nodes/centers".
No route/location/prerequisite/cost semantics exist anywhere in history.

DECISION (per directive 2.4: "if historical evidence proves a different
correct definition, document and implement that definition"):
RootPath = a first-class DIRECTED TRAVERSAL over the canonical semantic graph:
identity + root (starting marker node) + ordered edge-traversal sequence +
provenance. It is a RECORDED ROUTE, distinct from: the graph itself
(ROOTPATH != GENERIC GRAPH), plane position (ROOTPATH != PLANE POSITION),
and execution flow (ROOTPATH != FLOW). Prerequisites/actions: NOT invented —
steps carry only what the graph supports. Cost/energy: hop-count/depth ONLY
where computationally meaningful; no game statistics. Director-reviewable.

## Laws (from directive)
CONTAINMENT != ASSOCIATION. LINEAGE != CONTAINMENT unless explicitly mapped.
SPATIAL NEARNESS != SEMANTIC RELATIONSHIP. RESONANCE != GRAPH TRUTH.
PERSPECTIVE != GRAPH TRUTH. Edge must have explicit semantic type.
No relationship merely from coexistence. No duplicate inverse authority.
No orphans. No dangling relationships. No containment cycles.
No silent identity change on reparenting. Promotion changes containment, not identity.
Fractal navigation triggers no semantic computation.
Graph change → traceable processing evidence.
Propagation only on real declared dependencies.
