"""GDP-001 Phase 2 — performance baseline (local-first, Chromebook-class).

Measures at realistic small scale. Not optimized; records evidence.
Owner: P2PERF (isolated; cleaned).
"""

import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import (
    SemanticGraph, RelationshipType, DerivationKind, graph_path)

from form.persist import _STATE_DIR as _PERSIST_STATE_DIR
BASE = _PERSIST_STATE_DIR
OWNER = "P2PERF"
PROV = Provenance(source=ProvenanceSource.HUMAN, activity="perf", agent="p2")


def wipe():
    d = os.path.join(BASE, f"ideas_{OWNER}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    p = graph_path(OWNER)
    if os.path.isfile(p):
        os.remove(p)


def timed(name, fn, n=1):
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    dt = (time.perf_counter() - t0) / n
    print(f"{name}: {dt*1000:.2f} ms/op (n={n})")


def main():
    wipe()
    try:
        N = 500
        ids = []
        t0 = time.perf_counter()
        for i in range(N):
            idea = Idea(title=f"Node{i}")
            save_idea(idea, OWNER)
            ids.append(idea.id)
        print(f"idea creation: {(time.perf_counter()-t0)/N*1000:.2f} ms/op (n={N})")

        g = SemanticGraph.load(OWNER)
        # chain containment: 0>1>2>... (depth N)
        t0 = time.perf_counter()
        for i in range(1, N):
            g.nest(ids[i], ids[i - 1], PROV)
        print(f"nest (with save): {(time.perf_counter()-t0)/(N-1)*1000:.2f} ms/op")

        # associations
        t0 = time.perf_counter()
        for i in range(0, N - 1, 2):
            g.add_relationship(RelationshipType.RELATED_TO, ids[i], ids[i + 1], PROV)
        print(f"relate (with save): {(time.perf_counter()-t0)/(N//2)*1000:.2f} ms/op")

        leaf = ids[-1]
        timed("ancestors (depth 500)", lambda: g.ancestors(leaf))
        timed("descendants (500)", lambda: g.descendants(ids[0]))
        timed("breadcrumb (depth 500)", lambda: g.breadcrumb(leaf))
        timed("children", lambda: g.children(ids[0]))

        # cycle check cost on deep nest attempt (rejected)
        t0 = time.perf_counter()
        try:
            g.nest(ids[0], leaf, PROV)
        except Exception:
            pass
        print(f"cycle-check reject (depth 500): {(time.perf_counter()-t0)*1000:.2f} ms")

        # reparent
        timed("reparent", lambda: (g.reparent(ids[250], ids[10], PROV),
                                  g.reparent(ids[250], ids[249], PROV)))

        # propagation
        dep = ids[100]
        tgt = ids[200]
        ideas_t = __import__("form.mandell.idea_persist", fromlist=["load_idea"])
        t = ideas_t.load_idea(tgt, OWNER)
        t.set_property("v", 1, PROV)
        ideas_t.save_idea(t, OWNER)
        g.declare_dependency(dep, tgt, DerivationKind.MIRROR, "mv", unit="v", provenance=PROV)
        def prop():
            t2 = ideas_t.load_idea(tgt, OWNER)
            t2.set_property("v", t2.get_active_properties()["v"] + 1, PROV)
            ideas_t.save_idea(t2, OWNER)
            g._propagate_property(tgt, "v")
        timed("propagation (mirror, 1 dependent)", prop, n=5)

        # save/load
        timed("graph save", lambda: g.save())
        timed("graph load+validate+fold (1000 edges)", lambda: SemanticGraph.load(OWNER))

        print("\nP2 PERF BASELINE RECORDED")
    finally:
        wipe()


if __name__ == "__main__":
    main()
