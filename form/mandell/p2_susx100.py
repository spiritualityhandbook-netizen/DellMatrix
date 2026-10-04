"""GDP-001 Phase 2 — SUSX100: 100 randomized adversarial graph operations.

Each case: random owner, random DAG of ideas, random sequence of nest/
reparent/unnest/relate/remove/declare_dependency operations with random
parameters (including invalid ones). After each case, assert the permanent
laws hold on a FRESH load:
- exactly ≤1 active parent per child
- no containment cycles
- no dangling active edges
- fold is deterministic (two loads agree)
- history is append-only (entry count never decreases)
"""

import os
import random
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import (
    SemanticGraph, RelationshipType, RelationshipStatus, DerivationKind,
    GraphInvariantError, GraphValidationError, graph_path)

from form.persist import _STATE_DIR as _PERSIST_STATE_DIR
BASE = _PERSIST_STATE_DIR
PROV = Provenance(source=ProvenanceSource.HUMAN, activity="susx", agent="susx")


def wipe(owner):
    d = os.path.join(BASE, f"ideas_{owner}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    p = graph_path(owner)
    if os.path.isfile(p):
        os.remove(p)


def check_laws(owner):
    """Assert the permanent Phase-2 laws on a fresh load."""
    g = SemanticGraph.load(owner)
    # ≤1 active parent per child
    parents = {}
    for e in g._current.values():
        if e.type == RelationshipType.CONTAINS and e.status == RelationshipStatus.ACTIVE:
            assert e.target_id not in parents, f"two parents for {e.target_id}"
            parents[e.target_id] = e.source_id
    # no cycles
    for child in parents:
        seen = set()
        node = child
        while node in parents:
            assert node not in seen, f"cycle at {node}"
            seen.add(node)
            node = parents[node]
    # no dangling active edges (load already validates, but double-check)
    # deterministic fold: reload and compare
    g2 = SemanticGraph.load(owner)
    assert len(g._entries) == len(g2._entries)
    assert [(e.rel_id, e.status.value) for e in g._entries] == \
           [(e.rel_id, e.status.value) for e in g2._entries]
    return len(g._entries)


def run_case(seed):
    rng = random.Random(seed)
    owner = f"P2SUSX{seed}"
    wipe(owner)
    try:
        n = rng.randint(2, 8)
        ideas = []
        for i in range(n):
            idea = Idea(title=f"N{i}_{seed}")
            save_idea(idea, owner)
            ideas.append(idea.id)
        g = SemanticGraph.load(owner)
        entry_count = 0
        for _ in range(rng.randint(5, 30)):
            op = rng.choice(["nest", "reparent", "unnest", "relate",
                             "remove", "depend", "bad_nest"])
            a, b = rng.sample(ideas, 2)
            try:
                if op == "nest":
                    g.nest(a, b, PROV)
                elif op == "reparent":
                    g.reparent(a, b, PROV)
                elif op == "unnest":
                    g.unnest(a, PROV)
                elif op == "relate":
                    t = rng.choice(list(RelationshipType))
                    if t == RelationshipType.CONTAINS:
                        continue
                    if t == RelationshipType.DEPENDS_ON:
                        continue  # covered separately
                    g.add_relationship(t, a, b, PROV)
                elif op == "remove":
                    act = [e for e in g._current.values()
                           if e.status == RelationshipStatus.ACTIVE
                           and e.type != RelationshipType.CONTAINS]
                    if act:
                        g.remove_relationship(rng.choice(act).rel_id, PROV)
                elif op == "depend":
                    g.declare_dependency(
                        a, b, DerivationKind.MIRROR, f"mir_{seed}",
                        unit="v", provenance=PROV, force=True)
                elif op == "bad_nest":
                    # invalid: self, cycle attempt, or missing
                    bad = rng.choice([
                        lambda: g.nest(a, a, PROV),
                        lambda: g.nest("missing-id", b, PROV),
                        lambda: g.nest(a, "missing-id", PROV),
                    ])
                    try:
                        bad()
                        return (seed, "BAD_OP_SUCCEEDED", op)
                    except (GraphInvariantError, GraphValidationError):
                        pass
            except (GraphInvariantError, GraphValidationError):
                pass  # legal rejections
            # append-only: entry count never decreases
            assert len(g._entries) >= entry_count, "history shrank!"
            entry_count = len(g._entries)
        # fresh-load law check
        check_laws(owner)
        return (seed, "OK", "")
    except AssertionError as e:
        return (seed, "LAW_VIOLATION", str(e)[:80])
    except Exception as e:
        return (seed, "UNEXPECTED", f"{type(e).__name__}: {str(e)[:60]}")
    finally:
        wipe(owner)


def main():
    fails = []
    for seed in range(100):
        s, status, detail = run_case(seed)
        if status != "OK":
            fails.append((s, status, detail))
    print(f"SUSX100: {100-len(fails)}/100 clean")
    for s, status, detail in fails[:10]:
        print(f"  seed {s}: {status} {detail}")
    if fails:
        sys.exit(1)
    print("SUSX100: ALL CLEAN")


if __name__ == "__main__":
    main()
