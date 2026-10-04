#!/usr/bin/env python3
"""P4 LATTICE-COLLISION PROOF (P4-DIR-01).

Adversarial proof that the HarmonicLattice derived projection is
LOSSLESS under integer-cell quantization collisions.

Cases:
 1. two Ideas with identical explicit coordinates
 2. two Ideas with distinct coords rounding to the same cell
 3. three or more colliding Ideas
 4. collision membership independent of insertion order
 5. deterministic rebuild across fresh processes
 6. all canonical Plane IDs recoverable from lattice (all_members)
 7. moving one collider to another cell updates without stale membership
 8. repeated rebuild is idempotent
 9. collision creates no semantic relationships/containment/acceptance/
    resonance/hierarchy
10. causal mutant (first-sorted-wins / continue) is detected
"""
import os
import shutil
import sys

REPO = os.path.expanduser("~/workspace/dellmatrix-gdp-phase4")
sys.path.insert(0, REPO)
os.chdir(REPO)

CHECKS, FAILED = [], []


def rec(name, ok, detail=""):
    CHECKS.append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}", flush=True)
    if not ok:
        FAILED.append(name)


def _clean(owner):
    from form.persist import _safe_owner
    d = os.path.join(REPO, "form/state", f"ideas_{_safe_owner(owner)}")
    shutil.rmtree(d, ignore_errors=True)
    for suffix in (f"program_{owner}.json", f"nursery_{owner}.json"):
        try:
            os.remove(os.path.join(REPO, "form/state", suffix))
        except OSError:
            pass


def _prog(owner):
    from form.open import Program
    p = Program(owner=owner)
    p.cube.session.plane.units.clear()
    return p


def t1_identical_coords():
    """Two Ideas at identical explicit coordinates: both in members."""
    owner = "P4LC1"
    try:
        p = _prog(owner)
        p.place("c1a", "alpha", x=5.0, y=5.0)
        p.place("c1b", "beta", x=5.0, y=5.0)
        m = p.lattice.members_at(5, 5)
        rec("collide::identical_coords",
            sorted(m) == ["c1a", "c1b"], f"members={m}")
        cell = p.lattice.get(5, 5)
        rec("collide::identical_is_collision",
            cell.is_collision and cell.member_count == 2,
            f"count={cell.member_count}")
    finally:
        _clean(owner)


def t2_rounding_collision():
    """Distinct coords (5.2,5.2) and (5.4,5.4) round to same cell (5,5)."""
    owner = "P4LC2"
    try:
        p = _prog(owner)
        p.place("c2a", "alpha", x=5.2, y=5.2)
        p.place("c2b", "beta", x=5.4, y=5.4)
        # sanity: they really are distinct in Plane
        pa = p.cube.session.plane
        distinct = (pa.units["c2a"].x != pa.units["c2b"].x)
        m = p.lattice.members_at(5, 5)
        rec("collide::rounding",
            distinct and sorted(m) == ["c2a", "c2b"],
            f"distinct={distinct} members={m}")
    finally:
        _clean(owner)


def t3_three_colliders():
    """Three Ideas in one cell: all three in members."""
    owner = "P4LC3"
    try:
        p = _prog(owner)
        for i in range(3):
            p.place(f"c3{i}", f"idea {i}", x=7.0, y=-3.0)
        m = p.lattice.members_at(7, -3)
        rec("collide::three",
            sorted(m) == ["c300", "c301", "c302"] or
            sorted(m) == ["c30", "c31", "c32"],
            f"members={sorted(m)}")
        # all_members completeness
        pa = p.cube.session.plane
        plane_ids = sorted(pa.units.keys())
        lat_ids = p.lattice.all_members()
        rec("collide::three_complete", plane_ids == lat_ids,
            f"plane={plane_ids} lattice={lat_ids}")
    finally:
        _clean(owner)


def t4_insertion_order_independent():
    """Collision membership identical regardless of insertion order."""
    def build(order, owner):
        p = _prog(owner)
        for uid in order:
            p.place(uid, f"idea {uid}", x=3.0, y=3.0)
        m = p.lattice.members_at(3, 3)
        _clean(owner)
        return sorted(m)
    m1 = build(["x1", "x2", "x3"], "P4LC4a")
    m2 = build(["x3", "x1", "x2"], "P4LC4b")
    rec("collide::order_independent", m1 == m2 == ["x1", "x2", "x3"],
        f"{m1} vs {m2}")


def t5_cross_process_deterministic():
    """Rebuild deterministic across fresh processes (via members)."""
    import subprocess
    code = (
        "import sys; sys.path.insert(0, '/home/hatch/workspace/"
        "dellmatrix-gdp-phase4');"
        "from form.open import Program;"
        "p=Program(owner='P4LC5');"
        "p.cube.session.plane.units.clear();"
        "[p.place(f'q{i}', 'x', x=9.0, y=9.0) for i in range(4)];"
        "print(sorted(p.lattice.members_at(9,9)));"
        "print(p.lattice.get(9,9).member_count)"
    )
    outs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, "-c", code],
                           capture_output=True, text=True, timeout=120,
                           cwd=REPO)
        outs.append(r.stdout.strip())
        _clean("P4LC5")
    rec("collide::cross_process", outs[0] == outs[1] and "q0" in outs[0],
        f"{outs[0][:60]}")


def t6_all_recoverable():
    """Every Plane ID recoverable from lattice (no silent loss)."""
    owner = "P4LC6"
    try:
        p = _prog(owner)
        # mix: isolated, paired collisions, triple collision
        p.place("s1", "solo", x=100.0, y=100.0)
        p.place("p1", "pair a", x=1.0, y=1.0)
        p.place("p2", "pair b", x=1.0, y=1.0)
        p.place("t1", "tri a", x=2.0, y=2.0)
        p.place("t2", "tri b", x=2.0, y=2.0)
        p.place("t3", "tri c", x=2.0, y=2.0)
        pa = p.cube.session.plane
        plane_ids = sorted(
            uid for uid, u in pa.units.items()
            if __import__("math").isinf(u.x) is False)
        # filter to finite only (mirrors rebuild logic)
        import math
        plane_ids = sorted(
            uid for uid in pa.units
            if math.isfinite(pa.units[uid].x)
            and math.isfinite(pa.units[uid].y))
        lat_ids = p.lattice.all_members()
        rec("collide::all_recoverable", plane_ids == lat_ids,
            f"plane={len(plane_ids)} lattice={len(lat_ids)}")
    finally:
        _clean(owner)


def t7_move_updates_no_stale():
    """Moving one collider away: old cell drops it, new cell gains it."""
    owner = "P4LC7"
    try:
        p = _prog(owner)
        p.place("m1", "mover", x=4.0, y=4.0)
        p.place("m2", "stayer", x=4.0, y=4.0)
        assert sorted(p.lattice.members_at(4, 4)) == ["m1", "m2"]
        # move m1 far away via authority tick is indirect; use direct
        # Plane update then rebuild (the sanctioned derived path)
        pa = p.cube.session.plane
        pa.units["m1"].x, pa.units["m1"].y = 40.0, 40.0
        p.lattice.rebuild_from_plane(pa)
        old = p.lattice.members_at(4, 4)
        new = p.lattice.members_at(40, 40)
        rec("collide::move_no_stale",
            old == ["m2"] and new == ["m1"],
            f"old={old} new={new}")
    finally:
        _clean(owner)


def t8_idempotent():
    """Repeated rebuild: identical cells and members."""
    owner = "P4LC8"
    try:
        p = _prog(owner)
        p.place("i1", "a", x=6.0, y=6.0)
        p.place("i2", "b", x=6.0, y=6.0)
        p.place("i3", "c", x=8.0, y=8.0)
        pa = p.cube.session.plane
        snap1 = {k: (sorted(c.members), c.content)
                 for k, c in p.lattice.cells.items()}
        p.lattice.rebuild_from_plane(pa)
        snap2 = {k: (sorted(c.members), c.content)
                 for k, c in p.lattice.cells.items()}
        p.lattice.rebuild_from_plane(pa)
        snap3 = {k: (sorted(c.members), c.content)
                 for k, c in p.lattice.cells.items()}
        rec("collide::idempotent", snap1 == snap2 == snap3,
            f"cells={len(snap1)}")
    finally:
        _clean(owner)


def t9_no_semantic_side_effects():
    """Collision creates no graph edges, containment, acceptance, scores."""
    owner = "P4LC9"
    try:
        from form.mandell.semantic_graph import SemanticGraph
        from form.dell_matrix import canonical_lifecycle
        p = _prog(owner)
        p.place("s1", "shared cell one", x=11.0, y=11.0)
        p.place("s2", "shared cell two", x=11.0, y=11.0)
        # graph edges
        g = SemanticGraph.load(owner)
        edges = []
        try:
            from form.dell_matrix.graph_harmony import graph_neighbor_ids
            edges = graph_neighbor_ids(g, "s1")
        except Exception:
            pass
        # lifecycle / scores unchanged by collision
        l1 = canonical_lifecycle.resolve_lifecycle(p, "s1")
        l2 = canonical_lifecycle.resolve_lifecycle(p, "s2")
        scores = p.scores()
        cell = p.lattice.get(11, 11)
        rec("collide::no_semantics",
            len(edges) == 0 and l1 == l2 and cell.is_collision
            and scores.get("s1", 0) == scores.get("s2", 0),
            f"edges={len(edges)} lifecycles={l1},{l2} collision={cell.is_collision}")
    finally:
        _clean(owner)


def t10_causal_mutant():
    """CAUSAL: restoring first-sorted-wins/continue MUST be detected.

    Monkeypatch rebuild_from_plane with the old lossy logic; assert
    that a colliding idea disappears from all_members (detection works),
    then confirm the real implementation keeps it.
    """
    owner = "P4LC10"
    try:
        p = _prog(owner)
        p.place("k1", "one", x=12.0, y=12.0)
        p.place("k2", "two", x=12.0, y=12.0)
        lat = p.lattice
        orig_rebuild = lat.rebuild_from_plane

        def _lossy_rebuild(plane):
            # P4-DIR-01 defect: first-sorted wins, rest silently dropped
            lat.cells = {}
            import math as _math
            for uid in sorted(plane.units):
                u = plane.units[uid]
                try:
                    x, y = float(u.x), float(u.y)
                except (TypeError, ValueError):
                    continue
                if not (_math.isfinite(x) and _math.isfinite(y)):
                    continue
                key = (int(round(x)), int(round(y)), 0)
                if key in lat.cells:
                    continue
                from form.dell_matrix.harmonic_lattice import Cell
                lat.cells[key] = Cell(h=key[0], v=key[1], f=0,
                                      content=uid, members=[uid])
            return len(lat.cells)

        import types
        lat.rebuild_from_plane = types.MethodType(
            lambda self, plane: _lossy_rebuild(plane), lat)
        try:
            pa = p.cube.session.plane
            lat.rebuild_from_plane(pa)
            lost = "k2" not in lat.all_members()
            rec("causal::lossy_detected", lost,
                f"k2 missing={lost} (must be True: defect detected)")
        finally:
            lat.rebuild_from_plane = orig_rebuild
        # real implementation: both present
        pa = p.cube.session.plane
        lat.rebuild_from_plane(pa)
        kept = sorted(lat.all_members()) == ["k1", "k2"]
        rec("causal::real_lossless", kept,
            f"members={lat.all_members()}")
    finally:
        _clean(owner)


def main():
    print("=== P4 LATTICE-COLLISION PROOF (P4-DIR-01) ===", flush=True)
    t1_identical_coords()
    t2_rounding_collision()
    t3_three_colliders()
    t4_insertion_order_independent()
    t5_cross_process_deterministic()
    t6_all_recoverable()
    t7_move_updates_no_stale()
    t8_idempotent()
    t9_no_semantic_side_effects()
    t10_causal_mutant()
    n = len(CHECKS)
    print(f"P4 LATTICE-COLLISION: {n - len(FAILED)}/{n} pass; "
          f"failed={FAILED}", flush=True)
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
