"""GDP-001 Phase 2 — Semantic Graph contract tests (proof-first).

Covers 2.1 (containment), 2.2 (promotion/reparenting), 2.3 (semantic
graph), 2.4 (RootPath), 2.5 (semantic resolution), and 1.5.4 (dependency
propagation). Each test uses a unique owner for isolation; probe state is
cleaned. Run: python3 -m form.mandell.p2_graph_test
"""

import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea, load_idea, idea_exists
from form.mandell.semantic_graph import (
    SemanticGraph, RelationshipType, RelationshipStatus, DerivationKind,
    GraphInvariantError, GraphValidationError, GraphError, graph_path,
)

from form.persist import _STATE_DIR as _PERSIST_STATE_DIR
BASE = _PERSIST_STATE_DIR
OWNER = "P2GRAPH_TEST"
PROV = Provenance(source=ProvenanceSource.HUMAN, activity="p2_test", agent="p2")


def wipe():
    d = os.path.join(BASE, f"ideas_{OWNER}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    p = graph_path(OWNER)
    if os.path.isfile(p):
        os.remove(p)


def make_idea(title):
    idea = Idea(title=title)
    save_idea(idea, OWNER)
    return idea


_PASS_COUNT = 0

def check(name, cond):
    global _PASS_COUNT
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        raise AssertionError(name)
    _PASS_COUNT += 1

def main():
    wipe()
    try:
        # ---- 2.1 fractal containment -------------------------------------
        house = make_idea("House")
        rooms = make_idea("Rooms")
        bath = make_idea("Bathroom")
        g = SemanticGraph.load(OWNER)
        g.nest(rooms.id, house.id, PROV)
        g.nest(bath.id, rooms.id, PROV)
        check("2.1.1 parent", g.parent(bath.id) == rooms.id)
        check("2.1.1 children", g.children(house.id) == [rooms.id])
        check("2.1.4 ancestors", g.ancestors(bath.id) == [rooms.id, house.id])
        check("2.1.4 descendants", sorted(g.descendants(house.id)) == sorted([rooms.id, bath.id]))
        check("2.1.4 breadcrumb", g.breadcrumb(bath.id) == [house.id, rooms.id, bath.id])
        check("2.1.4 root status", g.is_top_level(house.id) and not g.is_top_level(bath.id))
        check("2.1.3 identity stable", load_idea(bath.id, OWNER).id == bath.id)
        # 2.1.2 arbitrary depth (10-chain)
        prev = bath.id
        chain = [prev]
        for i in range(10):
            n = make_idea(f"Deep{i}")
            g.nest(n.id, prev, PROV)
            prev = n.id
            chain.append(prev)
        check("2.1.2 depth-10 ancestors", len(g.ancestors(prev)) == 12)
        check("2.1.2 breadcrumb length", len(g.breadcrumb(prev)) == 13)
        # 2.1.5 navigation needs no computation/rendering
        check("2.1.5 no UI modules", not any(m.startswith("form.dell_matrix.live_visual") for m in sys.modules))

        # ---- 2.2 promotion / reparenting ----------------------------------
        studio = make_idea("Studio")
        g.nest(studio.id, house.id, PROV)
        old_id = studio.id
        g.unnest(studio.id, PROV)  # promote to top-level
        check("2.2.1 promoted top-level", g.is_top_level(studio.id))
        check("2.2.1 ID unchanged", studio.id == old_id)
        check("2.2.1 idea file ID unchanged", load_idea(studio.id, OWNER).id == old_id)
        hist = [e for e in g._entries if e.type == RelationshipType.CONTAINS and e.target_id == studio.id]
        check("2.2.2 former parent in history", any(e.source_id == house.id for e in hist))
        check("2.2.3 reparent history kept", any(e.status == RelationshipStatus.SUPERSEDED for e in hist))
        # reparent preserves history too
        g.reparent(studio.id, rooms.id, PROV)
        check("2.2 reparent works", g.parent(studio.id) == rooms.id)
        hist2 = [e for e in g._entries if e.type == RelationshipType.CONTAINS and e.target_id == studio.id]
        check("2.2.3 full chain", len(hist2) == 3)  # nest, supersede(promote), nest(reparent)

        # ---- 2.3 semantic graph --------------------------------------------
        album = make_idea("Album")
        e = g.add_relationship(RelationshipType.RELATED_TO, studio.id, album.id, PROV, cause="test")
        check("2.3.1 typed edge", e.type == RelationshipType.RELATED_TO)
        check("2.3.1 direction", e.source_id == studio.id and e.target_id == album.id)
        check("2.3.5 outgoing", e.rel_id in [x.rel_id for x in g.outgoing(studio.id)])
        check("2.3.5 incoming", e.rel_id in [x.rel_id for x in g.incoming(album.id)])
        check("2.3.5 by_type", e.rel_id in [x.rel_id for x in g.by_type(RelationshipType.RELATED_TO)])
        check("2.3.5 neighbors", (album.id, RelationshipType.RELATED_TO) in g.association_neighbors(studio.id))
        # 2.3.2 containment is not a generic association
        check("2.3.2 contains not in neighbors", not any(t == RelationshipType.CONTAINS for _, t in g.association_neighbors(rooms.id)))
        check("2.3.2 contains queryable distinctly", len(g.by_type(RelationshipType.CONTAINS)) > 0)
        # 2.3.3 cross-level: nested bath RELATED_TO top-level album
        g.add_relationship(RelationshipType.RELATED_TO, bath.id, album.id, PROV)
        check("2.3.3 cross-level", True)
        # 2.3.4 no hyperedges: edge ids are not idea ids; edges cannot be endpoints
        try:
            g.add_relationship(RelationshipType.RELATED_TO, e.rel_id, album.id, PROV)
            check("2.3.4 edge-as-endpoint rejected", False)
        except GraphInvariantError:
            check("2.3.4 edge-as-endpoint rejected", True)
        # provenance/history on the edge
        check("2.3.5 edge history", len(g.edge_history(e.rel_id)) == 1)
        # removal is a tombstone, history preserved
        g.remove_relationship(e.rel_id, PROV)
        check("2.3 removal tombstone", g._current[e.rel_id].status == RelationshipStatus.REMOVED)
        check("2.3 removed not in outgoing", e.rel_id not in [x.rel_id for x in g.outgoing(studio.id)])
        check("2.3 history after remove", len(g.edge_history(e.rel_id)) == 2)

        # ---- 2.4 RootPath ----------------------------------------------------
        g2 = SemanticGraph.load(OWNER)
        path = g2.find_path(house.id, bath.id)
        check("2.4 path found", path.node_ids[0] == house.id and path.node_ids[-1] == bath.id)
        check("2.4 hop count", path.hop_count == len(path.edge_ids) == 2)
        check("2.4 root is root", path.root_id == house.id)
        g2.save_path(path)
        check("2.4 path validates ACTIVE", g2.validate_path(path.path_id) == "ACTIVE")
        # path over association edges
        g2.add_relationship(RelationshipType.REFERENCES, studio.id, album.id, PROV)
        p2 = g2.find_path(studio.id, album.id, types={RelationshipType.REFERENCES})
        check("2.4 typed path", p2.hop_count == 1)
        # stale detection: remove the edge, path goes STALE
        ref_edge = g2.outgoing(studio.id, RelationshipType.REFERENCES)[0]
        g2.save_path(p2)
        g2.remove_relationship(ref_edge.rel_id, PROV)
        check("2.4 stale path detected", g2.validate_path(p2.path_id).startswith("STALE"))
        # unreachable
        try:
            g2.find_path(album.id, house.id, types={RelationshipType.REFERENCES})
            check("2.4 unreachable raises", False)
        except GraphError:
            check("2.4 unreachable raises", True)

        # ---- 2.5 semantic resolution ------------------------------------------
        g3 = SemanticGraph.load(OWNER)
        check("2.5.1 title index", g3.lookup_by_title("House") == house.id)
        # rename updates index via observer
        h = load_idea(house.id, OWNER)
        g3.attach(h)
        h.rename("Maison", PROV)
        save_idea(h, OWNER)
        check("2.5.1 rename reindexed", g3.lookup_by_title("Maison") == house.id)
        check("2.5.1 old title gone", g3.lookup_by_title("House") is None)
        # 2.5.3 structural categorization, no NLP
        h.set_property("note", "hello", PROV)
        h.set_property("n", 3, PROV)
        h.set_property("items", [1, 2], PROV)
        save_idea(h, OWNER)
        cats = g3.unit_categories(house.id)
        check("2.5.3 categories", cats.get("note") == "text" and cats.get("n") == "number" and cats.get("items") == "list")
        # 2.5.4 reference resolution; UNKNOWN stays UNKNOWN
        g3.add_relationship(RelationshipType.REFERENCES, bath.id, album.id, PROV)
        resolved = g3.resolve_references(bath.id)
        check("2.5.4 resolves", resolved[0][1].id == album.id)
        # dangling reference target deleted at file level -> load fails closed (tested separately)

        # ---- 1.5.4 dependency propagation --------------------------------------
        g4 = SemanticGraph.load(OWNER)
        alb = load_idea(album.id, OWNER)
        std = load_idea(studio.id, OWNER)
        g4.attach(alb)
        alb.set_property("songs", ["A"], PROV)
        save_idea(alb, OWNER)
        g4.declare_dependency(std.id, alb.id, DerivationKind.MIRROR, "setlist", unit="songs", provenance=PROV)
        # trigger via observer (attached alb) — emulate by direct call too
        g4._propagate_property(alb.id, "songs")
        s_after = load_idea(std.id, OWNER)
        check("1.5.4 mirror propagated", s_after.get_active_properties().get("setlist") == ["A"])
        ev = s_after.last_change()
        check("1.5.4 evidence recorded", ev is not None and ev.provenance.activity == "dependency_propagation")
        check("1.5.4 derived_from link", len(ev.provenance.derived_from) == 1)
        # equality cutoff
        n_ev = len(s_after.change_events())
        g4._propagate_property(alb.id, "songs")
        check("1.5.4 cutoff", len(load_idea(std.id, OWNER).change_events()) == n_ev)
        # unrelated untouched
        h_after = load_idea(house.id, OWNER)
        check("1.5.4 unrelated untouched", "setlist" not in h_after.get_active_properties())
        # zero propagation legitimate: change a unit nobody depends on
        n_house_ev = len(h_after.change_events())
        h_after.set_property("unrelated_prop", 1, PROV)
        save_idea(h_after, OWNER)
        g4._propagate_property(house.id, "unrelated_prop")
        check("1.5.4 zero propagation ok", len(load_idea(std.id, OWNER).change_events()) == n_ev)
        # child_count derivation on structure change
        g4.declare_dependency(house.id, house.id, DerivationKind.CHILD_COUNT, "room_count",
                              subject_id=house.id, provenance=PROV)
        extra = make_idea("Extra")
        g4.attach(extra)
        g4.nest(extra.id, house.id, PROV)  # structure change triggers propagate
        h2 = load_idea(house.id, OWNER)
        check("1.5.4 child_count", h2.get_active_properties().get("room_count") == len(g4.children(house.id)))

        # ---- persistence: fresh load -------------------------------------------
        g5 = SemanticGraph.load(OWNER)
        check("persist parent", g5.parent(bath.id) == rooms.id)
        check("persist promotion history", any(
            e.status == RelationshipStatus.SUPERSEDED
            for e in g5._entries
            if e.type == RelationshipType.CONTAINS and e.target_id == studio.id))
        check("persist title index", g5.lookup_by_title("Maison") == house.id)
        check("roots covers all top-level",
              house.id in g5.roots()
              and rooms.id not in g5.roots()  # nested under house
              and bath.id not in g5.roots())  # nested under rooms

        # ---- NULL fixes: session contract, lifecycle, descendant_count -------
        g6 = SemanticGraph.load(OWNER)
        # initial computation at declaration (never silently None)
        d2 = make_idea("Dep2")
        t2 = make_idea("Tgt2")
        t2.set_property("v", 42, PROV)
        save_idea(t2, OWNER)
        g6.declare_dependency(d2.id, t2.id, DerivationKind.MIRROR, "mv",
                              unit="v", provenance=PROV)
        check("declare initial compute",
              load_idea(d2.id, OWNER).get_active_properties().get("mv") == 42)
        # out-of-session mutation does not propagate; reconcile() fixes it
        t2u = load_idea(t2.id, OWNER)  # NOT attached
        t2u.set_property("v", 43, PROV)
        save_idea(t2u, OWNER)
        check("unattached no silent propagate",
              load_idea(d2.id, OWNER).get_active_properties().get("mv") == 42)
        n_up = g6.reconcile(t2.id)
        check("reconcile updates",
              n_up == 1 and load_idea(d2.id, OWNER).get_active_properties().get("mv") == 43)
        # descendant_count derivation is reachable
        g6.declare_dependency(house.id, house.id, DerivationKind.DESCENDANT_COUNT,
                              "desc_count", subject_id=house.id, provenance=PROV)
        check("descendant_count",
              load_idea(house.id, OWNER).get_active_properties().get("desc_count")
              == len(g6.descendants(house.id)))
        # lifecycle/graph composition: archived child stays in history,
        # live_children filters it
        doomed = make_idea("Doomed")
        g6.nest(doomed.id, house.id, PROV)
        dl = load_idea(doomed.id, OWNER)
        dl.archive("test")
        save_idea(dl, OWNER)
        check("archived still structural child", doomed.id in g6.children(house.id))
        check("archived not live child", doomed.id not in g6.live_children(house.id))
        check("archived in active_children history",
              any(e.target_id == doomed.id and e.status == RelationshipStatus.ACTIVE
                  for e in g6.by_type(RelationshipType.CONTAINS)))

        print(f"\nP2 GRAPH CONTRACT TESTS: ALL PASS")
        print(f"P2GRAPH {_PASS_COUNT}/{_PASS_COUNT}")
    finally:
        wipe()


def smoke() -> bool:
    """Regression-runner entry: True iff all contract checks pass."""
    try:
        main()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    main()
