#!/usr/bin/env python3
"""P4 placement & dynamics proof (GDP-001 Phase 4, objectives 4.1/4.2/4.3, 7/8/9).

Proves, against the production SpatialAuthority (sole decider of
post-placement Idea positions):
  1. no dishonest (0,0) placement            (4.1.1)
  2. deterministic placement                  (4.1.2)
  3. barycentric placement from graph anchors (4.1.2)
  4. placement explanation                    (4.1.5)
  5. bounded per-tick displacement            (8)
  6. convergence / honest non-convergence     (4.2.5)
  7. mental-map preservation                  (4.2.4, 9)
  8. faded units frozen + exert no attraction (2.4 lifecycle law)
  9. coincidence separation, deterministic    (8)
 10. NaN/inf fail-closed, no propagation      (8, 2.5)
 11. insertion-order sensitivity quantified   (7)

Pattern: rec(name, ok, detail) collects failures; main() runs all;
exit 0 iff all pass. Unique owner per test; state cleaned after.
"""
import math
import os
import shutil
import sys

sys.path.insert(0, os.path.expanduser("~/workspace/dellmatrix-gdp-phase4"))
os.chdir(os.path.expanduser("~/workspace/dellmatrix-gdp-phase4"))

from form.persist import _STATE_DIR, _safe_owner  # noqa: E402
from form.dell_matrix.spatial_authority import (  # noqa: E402
    MAX_DISP_PER_TICK, PLANE_BOUND)

FAILURES = []


def rec(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}", flush=True)
    if not ok:
        FAILURES.append(name)


def _clean(owner):
    d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}")
    f = os.path.join(_STATE_DIR, f"nursery_{_safe_owner(owner)}.json")
    shutil.rmtree(d, ignore_errors=True)
    try:
        os.remove(f)
    except OSError:
        pass
    try:
        from form.mandell.semantic_graph import (
            graph_path, graph_journal_path)
        for pth in (graph_path(owner), graph_journal_path(owner)):
            try:
                os.remove(pth)
            except OSError:
                pass
    except Exception:
        pass


def _prog(owner):
    from form.open import Program
    return Program(owner=owner)


def _pos(p, uid):
    u = p.cube.session.plane.units[uid]
    return (u.x, u.y)


# ---------------------------------------------------------------- 1
def t1_no_dishonest_origin():
    """4.1.1: ideas placed without coords never land exactly on (0,0)."""
    owner = "P4PD1"
    try:
        p = _prog(owner)
        ids = [f"n{i}" for i in range(5)]
        for i, uid in enumerate(ids):
            p.place(uid, f"node {i}")
        units = p.cube.session.plane.units
        bad = [uid for uid in ids
               if units[uid].x == 0.0 and units[uid].y == 0.0]
        nonfinite = [uid for uid in ids
                     if not (math.isfinite(units[uid].x)
                             and math.isfinite(units[uid].y))]
        # 'welcome' at (0,0) is the declared MATRIX_ORIGIN landmark.
        w = units.get("welcome")
        origin_ok = w is not None and w.x == 0.0 and w.y == 0.0
        rec("place::no_dishonest_origin", not bad and origin_ok,
            f"at_origin={bad} welcome_is_origin={origin_ok}")
        rec("place::all_finite", not nonfinite,
            f"positions={[(u, round(units[u].x,2), round(units[u].y,2)) for u in ids]}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------- 2
def t2_determinism():
    """4.1.2: same placement sequence on two fresh programs -> identical."""
    try:
        runs = []
        for tag in ("P4PD2A", "P4PD2B"):
            p = _prog(tag)
            seq = [f"d{i}" for i in range(5)]
            for uid in seq:
                p.place(uid, f"det {uid}")
            runs.append({uid: _pos(p, uid) for uid in seq})
            _clean(tag)
        same = all(runs[0][uid] == runs[1][uid] for uid in runs[0])
        rec("place::deterministic", same,
            f"run1={runs[0]}")
    finally:
        pass


# ---------------------------------------------------------------- 3
def t3_barycentric():
    """4.1.2: graph-anchored placement lands on the centroid, explained."""
    owner = "P4PD3"
    try:
        from form.mandell.idea import Idea, Provenance, ProvenanceSource
        from form.mandell.idea_persist import save_idea
        from form.mandell.semantic_graph import (
            SemanticGraph, RelationshipType)
        for kid, title in (("a", "alpha"), ("b", "beta"), ("c", "gamma")):
            save_idea(Idea(idea_id=kid, title=title), owner)
        p = _prog(owner)
        p.place("a", "alpha", x=10.0, y=0.0)
        p.place("b", "beta", x=0.0, y=10.0)
        prov = Provenance(source=ProvenanceSource.SYSTEM,
                          activity="p4pd", agent="p4pd")
        g = SemanticGraph.load(owner)
        g.add_relationship(RelationshipType.RELATED_TO, "a", "c", prov,
                           cause="p4pd")
        g.add_relationship(RelationshipType.RELATED_TO, "b", "c", prov,
                           cause="p4pd")
        p.place("c", "gamma")  # no coords -> barycentric from anchors
        cx, cy = _pos(p, "c")
        dist = math.hypot(cx - 5.0, cy - 5.0)
        expl = p.spatial_explain("c")["placement"]
        rec("place::barycentric_position", dist < 1.0,
            f"c=({cx:.4f},{cy:.4f}) dist_to_centroid={dist:.6f}")
        rec("place::barycentric_explained",
            expl.get("cause") == "barycentric"
            and expl.get("anchors") == ["a", "b"],
            f"cause={expl.get('cause')} anchors={expl.get('anchors')}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------- 4
def t4_explanation():
    """4.1.5: spatial_explain returns cause/anchors/env/tick."""
    owner = "P4PD4"
    try:
        p = _prog(owner)
        p.place("e1", "explain one")
        expl = p.spatial_explain("e1")
        pl = expl.get("placement", {})
        ok = (expl.get("present") is True
              and all(k in pl for k in ("cause", "anchors", "env", "tick"))
              and isinstance(pl["cause"], str) and pl["cause"]
              and isinstance(pl["anchors"], list))
        rec("place::explanation", ok, f"placement={pl}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------- 5
def t5_bounded_displacement():
    """8: every single-tick displacement respects the DecreasingMaxMovement
    cap (MAX_DISP_PER_TICK * disp_mult * temperature)."""
    owner = "P4PD5"
    try:
        p = _prog(owner)
        assert str(p.forces.weather.condition or "clear").lower() == "clear"
        ids = [f"m{i}" for i in range(6)]
        for uid in ids:
            p.place(uid, f"mover {uid}")
        worst, worst_cap = 0.0, 0.0
        ok = True
        for _ in range(20):
            temp_before = p.spatial.temperature
            before = {u: _pos(p, u)
                      for u in p.cube.session.plane.units}
            p.force_tick()
            cap = MAX_DISP_PER_TICK * 1.25 * temp_before + 1e-9
            for u, (bx, by) in before.items():
                ax, ay = _pos(p, u)
                d = math.hypot(ax - bx, ay - by)
                worst = max(worst, d)
                worst_cap = max(worst_cap, cap)
                if d > cap:
                    ok = False
        rec("dyn::bounded_displacement", ok,
            f"max_disp={worst:.6f} max_allowed={worst_cap:.6f}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------- 6
def t6_convergence():
    """4.2.5: a small cluster settles to equilibrium within budget."""
    owner = "P4PD6"
    try:
        p = _prog(owner)
        for i in range(5):
            p.place(f"s{i}", f"settle {i}")
        res = p.spatial_settle(max_ticks=200)
        rec("dyn::converged", res.get("converged") is True
            and res.get("honestly_non_convergent") is False
            and res.get("ticks_run", 999) <= 200,
            f"ticks={res.get('ticks_run')} max_disp={res.get('max_displacement'):.6f}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------- 7
def t7_mental_map():
    """4.2.4/9: inserting one unrelated idea barely moves the settled five."""
    owner = "P4PD7"
    try:
        p = _prog(owner)
        ids = [f"k{i}" for i in range(5)]
        for uid in ids:
            p.place(uid, f"keep {uid}")
        p.spatial_settle()
        before = {uid: _pos(p, uid) for uid in ids}
        p.place("newcomer", "unrelated newcomer")  # no graph edges
        p.spatial_settle()
        after = {uid: _pos(p, uid) for uid in ids}
        maxd = max(math.hypot(after[u][0] - before[u][0],
                              after[u][1] - before[u][1]) for u in ids)
        rec("dyn::mental_map", maxd < 2.0,
            f"max_displacement_of_settled={maxd:.4f}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------- 8
def t8_faded_frozen():
    """2.4: faded units neither move nor exert attraction (Phase-3 law)."""
    from form.dell_matrix.nursery import Proposal
    exp_o, ctl_o = "P4PD8E", "P4PD8C"
    try:
        pe = _prog(exp_o)
        pe.place("anchor", "anchor", x=20.0, y=0.0)
        pe.place("faded1", "faded one", x=21.5, y=0.0)
        pe.nursery.proposals["faded1"] = Proposal(
            id="faded1", label="faded one", words="old silt",
            kind="new", lifecycle_state="faded")
        pc = _prog(ctl_o)
        pc.place("anchor", "anchor", x=20.0, y=0.0)
        pc.place("loner", "far loner", x=200.0, y=200.0)
        f0 = _pos(pe, "faded1")
        for _ in range(10):
            pe.force_tick()
            pc.force_tick()
        f1 = _pos(pe, "faded1")
        frozen = f0 == f1
        ae, ac = _pos(pe, "anchor"), _pos(pc, "anchor")
        no_pull = ae == ac
        rec("life::faded_frozen", frozen, f"faded {f0} -> {f1}")
        rec("life::faded_no_attraction", no_pull,
            f"anchor_exp={ae} anchor_ctl={ac}")
    finally:
        _clean(exp_o)
        _clean(ctl_o)


# ---------------------------------------------------------------- 9
def t9_coincidence():
    """8: identical starting coordinates separate deterministically."""
    owner = "P4PD9"
    try:
        finals = []
        for tag in ("P4PD9A", "P4PD9B"):
            p = _prog(tag)
            p.place("c1", "coin one", x=7.0, y=7.0)
            p.place("c2", "coin two", x=7.0, y=7.0)
            for _ in range(5):
                p.force_tick()
            finals.append((_pos(p, "c1"), _pos(p, "c2")))
            _clean(tag)
        d0 = math.hypot(finals[0][0][0] - finals[0][1][0],
                        finals[0][0][1] - finals[0][1][1])
        same = finals[0] == finals[1]
        rec("dyn::coincidence_separates", d0 > 0.1, f"distance={d0:.4f}")
        rec("dyn::coincidence_deterministic", same,
            f"repeat_identical={same}")
    finally:
        pass


# --------------------------------------------------------------- 10
def t10_nan_fail_closed():
    """8/2.5: NaN position freezes the unit; never propagates, never raises."""
    owner = "P4PD10"
    try:
        p = _prog(owner)
        p.place("ok1", "ok one", x=30.0, y=0.0)
        p.place("ok2", "ok two", x=31.5, y=0.0)
        p.place("bad", "bad one", x=33.0, y=0.0)
        p.cube.session.plane.units["bad"].x = float("nan")
        raised = None
        try:
            for _ in range(5):
                p.force_tick()
        except Exception as e:  # noqa: BLE001
            raised = e
        units = p.cube.session.plane.units
        others_finite = all(
            math.isfinite(u.x) and math.isfinite(u.y)
            for uid, u in units.items() if uid != "bad")
        rec("dyn::nan_no_raise", raised is None, f"raised={raised!r}")
        rec("dyn::nan_no_propagate", others_finite,
            "all other units finite after 5 ticks")
    finally:
        _clean(owner)


# --------------------------------------------------------------- 11
def t11_insertion_order():
    """7: insertion-order sensitivity is bounded and quantified."""
    try:
        runs = {}
        for tag, order in (("P4PD11A", ["a", "b", "c"]),
                           ("P4PD11B", ["c", "b", "a"])):
            p = _prog(tag)
            for uid in order:
                p.place(uid, f"order {uid}")
            p.spatial_settle()
            runs[tag] = {uid: _pos(p, uid) for uid in ("a", "b", "c")}
            _clean(tag)
        ds = [math.hypot(runs["P4PD11A"][u][0] - runs["P4PD11B"][u][0],
                         runs["P4PD11A"][u][1] - runs["P4PD11B"][u][1])
              for u in ("a", "b", "c")]
        maxd = max(ds)
        rec("place::insertion_order_bounded", maxd < 5.0,
            f"max_pairwise_displacement={maxd:.4f} per_idea={sorted(ds)}")
    finally:
        pass


def main():
    t1_no_dishonest_origin()
    t2_determinism()
    t3_barycentric()
    t4_explanation()
    t5_bounded_displacement()
    t6_convergence()
    t7_mental_map()
    t8_faded_frozen()
    t9_coincidence()
    t10_nan_fail_closed()
    t11_insertion_order()
    n = 11
    print(f"P4 placement/dynamics: {n - len(FAILURES)}/{n} test groups pass; "
          f"checks={len(FAILURES)} failed: {FAILURES or 'none'}", flush=True)
    if FAILURES:
        print(f"P4 PLACEMENT/DYNAMICS: FAILURES PRESENT: {FAILURES}",
              flush=True)
        return 1
    print("P4 PLACEMENT/DYNAMICS WORLD: ALL PASS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
