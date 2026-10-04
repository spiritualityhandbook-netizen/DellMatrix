"""Graph + harmony integration (GDP-001 Phase 3, R3.6).

The smallest graph-backed consumer of the Phase-2 canonical semantic graph,
plus the plane-unit -> idea token adapter shared by the harmony wiring in
RingedGrowth.

GRAPH CONSUMER (ends the Phase-3 3.5.5 deferral):
  Phase-2's SemanticGraph (form/mandell/semantic_graph.py) is the ONE
  authority for canonical idea relationships. This module consumes it
  read-only through its EXISTING read queries only:

    - SemanticGraph.association_neighbors(idea_id)
        -> List[(neighbor_id, RelationshipType)]

  No new edge authority, no new relationship types, no graph mutation.
  Canonical Phase-1 Idea IDs are used throughout (identity lives in the
  Idea; graph position never defines identity).

  Defined neutral value: every function here returns 0.0 when the graph
  records no association for the given IDs. 0.0 means "the graph has no
  association evidence here" — it is never fabricated, and it is never
  presented as proof of semantic disconnectedness (absence of a recorded
  edge is not evidence of no relationship).

HARMONY ADAPTER:
  unit_idea_view(unit) exposes a plane unit through the idea token
  interface read by form.dell_matrix.harmony.harmony_score (title +
  get_active_properties). It mirrors the adapter inside
  Program.harmony_of (form/open.py) intentionally — same token sources
  (label -> title; words/detail/goals -> properties) — so harmony values
  computed in growth agree with the public path. It is a view, not a
  second harmony authority: the score itself always comes from
  harmony_score.

Real consumers:
  - RingedGrowth.run (form/dell_matrix/ringed_growth.py): computes
    graph_coherence for each proposal pair when a graph is attached,
    persists it on the Nursery proposal, and reports it.
  - form/mandell/p3_r36_graph_harmony_proof.py: proves the consumer
    reads real graph structure (bypass-must-fail).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


# ---------------------------------------------------------------------------
# Plane-unit -> idea token adapter
# ---------------------------------------------------------------------------

class _UnitIdeaView:
    """Adapter: exposes a plane unit through the idea token interface.

    Token sources (identical to Program.harmony_of's adapter):
      title                <- unit.label
      properties           <- unit.words, unit.detail, unit.goals (joined)

    Lifecycle is resolved canonically at the ID level via
    canonical_lifecycle (owner-aware boundary), not via dynamic Unit
    attributes. This adapter carries tokens only.
    """

    def __init__(self, unit: Any):
        self.title = getattr(unit, "label", "") or ""
        self._unit = unit

    def get_active_properties(self) -> Dict[str, str]:
        u = self._unit
        props: Dict[str, str] = {}
        for name in ("words", "detail"):
            v = getattr(u, name, "")
            if v:
                props[name] = v
        goals = getattr(u, "goals", None) or []
        if goals:
            props["goals"] = " ".join(str(g) for g in goals)
        return props


def unit_idea_view(unit: Any) -> _UnitIdeaView:
    """Wrap a plane unit so harmony_score can tokenize it honestly."""
    return _UnitIdeaView(unit)


# ---------------------------------------------------------------------------
# Graph-backed consumer (read-only; existing queries only)
# ---------------------------------------------------------------------------

def graph_neighbor_ids(graph: Any, idea_id: str) -> List[str]:
    """Canonical association neighbors of one idea, sorted, deduplicated.

    Uses ONLY SemanticGraph.association_neighbors (existing read query).
    Containment edges are excluded by that query's own semantics
    (CONTAINS is structural, not association — Phase-2 law 2.3.2), so the
    result is the pure association neighborhood. Unknown IDs yield []
    (the query returns [] for IDs with no index entries) — defined
    neutral, never fabricated.
    """
    seen = set()
    for neighbor_id, _rel_type in graph.association_neighbors(idea_id):
        seen.add(neighbor_id)
    return sorted(seen)


def graph_coherence(graph: Any, idea_ids: Iterable[str]) -> float:
    """Graph-backed coherence of an idea set, in [0, 1].

    Fraction of unordered pairs in the set that share an ACTIVE
    association edge (either direction; association_neighbors already
    presents both edge directions). Computed from real graph structure
    via graph_neighbor_ids -> association_neighbors — the single
    existing read query used here.

    Defined neutral value: 0.0 when the graph records no association
    among the IDs (including fewer than two distinct IDs, unknown IDs,
    or a graph with no edges for them). 0.0 = "no graph evidence of
    association", never a fabricated score and never proof of
    disconnectedness.

    Determinism: pure function of (graph current state, idea_ids).
    """
    ids = [i for i in dict.fromkeys(idea_ids) if i]  # dedupe, keep order
    n = len(ids)
    if n < 2:
        return 0.0
    neighbor_sets = {iid: set(graph_neighbor_ids(graph, iid)) for iid in ids}
    linked = 0
    for a in range(n):
        for b in range(a + 1, n):
            # Edge a-b exists iff either endpoint lists the other as an
            # association neighbor (association_neighbors covers both
            # edge directions, so one check per endpoint suffices).
            if ids[b] in neighbor_sets[ids[a]] or ids[a] in neighbor_sets[ids[b]]:
                linked += 1
    total = n * (n - 1) // 2
    return linked / total
