#!/usr/bin/env python3
"""P4 Lattice + Environment proof (GDP-001 Phase 4, objectives 4.4 / 4.5,
adversarial §13).

Proves, against the production canonical spatial authority
(form/dell_matrix/spatial_authority.py :: SpatialAuthority):

  1. Lattice is a DERIVED projection (rebuild_from_plane): every live unit
     appears as a cell's content, no stale refs, moves are reflected,
     rebuild is drift-free.
  2. Program.place never mirrors via lattice.put (source inspection); the
     only sanctioned path is rebuild_from_plane.
  3. Weather semantics: exact declared multipliers per condition;
     unknown condition -> clear parameters (fail-safe).
  4. Storm displacement stays within the declared bound.
  5. Fog local emphasis: distant-well radius gate is wired; fog displacement
     <= clear displacement from identical state.
  6. Environmental isolation: 20 ticks across all 4 weather modes change
     ZERO semantic state.
  7. Semantic isolation: real movement does not mutate canonical truth.
  8. Causal mutants: owner bypass, weather write, persistence skip.
  9. Malformed spatial state fails closed.

Pattern: rec(name, ok, detail); main(); exit 0 iff all pass.
Unique owner per test; state files cleaned after each test.
"""

from __future__ import annotations

import inspect
import json
import math
import os
import shutil
import sys

FAILURES: list[str] = []


def rec(name: str, ok: bool, detail: str = "") -> None:
    print(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}", flush=True)
    if not ok:
        FAILURES.append(name)


OWNER_BASE = "P4LE"


def _owner(tag: str) -> str:
    return f"{OWNER_BASE}_{tag}"


def _clean(owner: str) -> None:
    from form.persist import _safe_owner, _STATE_DIR
    d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}")
    shutil.rmtree(d, ignore_errors=True)
    for name in (f"nursery_{owner}.json", f"program_{_safe_owner(owner)}.json"):
        try:
            os.remove(os.path.join(_STATE_DIR, name))
        except OSError:
            pass
    for f in os.listdir(_STATE_DIR) if os.path.isdir(_STATE_DIR) else []:
        if f.startswith(f"program_{_safe_owner(owner)}_cp_"):
            try:
                os.remove(os.path.join(_STATE_DIR, f))
            except OSError:
                pass
    try:
        from form.mandell.semantic_graph import graph_path, graph_journal_path
        for pth in (graph_path(owner), graph_journal_path(owner)):
            try:
                os.remove(pth)
            except OSError:
                pass
    except Exception:
        pass


def _prog(owner: str):
    from form.open import Program
    return Program(owner=owner)


def _units(p):
    return p.cube.session.plane.units


def _pos(p, uid):
    u = _units(p)[uid]
    return (float(u.x), float(u.y))


def _set_scores(p, mapping):
    for k, v in mapping.items():
        p.enhance.state.scores[k] = float(v)


# ---------------------------------------------------------------------------
# 1. Lattice is a derived projection
# ---------------------------------------------------------------------------

def t1_lattice_derived() -> None:
    owner = _owner("t1")
    _clean(owner)
    try:
        p = _prog(owner)
        p.place("a", "alpha river", x=10.0, y=10.0)
        p.place("b", "beta stream", x=50.0, y=20.0)
        p.place("c", "gamma brook", x=90.0, y=30.0)
        unit_ids = set(_units(p))
        contents = {c.content for c in p.lattice.cells.values()}
        rec("lattice::units_covered", unit_ids <= contents,
            f"units={sorted(unit_ids)} covered={sorted(unit_ids & contents)}")
        rec("lattice::no_stale", contents <= unit_ids,
            f"stale={[c for c in contents if c not in unit_ids]}")
        # Move a unit via the authority tick; lattice must reflect it.
        _set_scores(p, {"a": 5.0, "b": 1.0, "c": 0.5})
        x0, y0 = _pos(p, "a")
        rep = p.spatial.tick(p)
        x1, y1 = _pos(p, "a")
        moved = math.hypot(x1 - x0, y1 - y0)
        rec("lattice::tick_moves", moved > 1e-9 and rep["moved"] >= 1,
            f"disp={moved:.4f} moved={rep['moved']}")
        key = (round(x1), round(y1), 0)
        cell = p.lattice.cells.get(key)
        rec("lattice::reflects_move",
            cell is not None and cell.content == "a",
            f"cell@{key}={getattr(cell, 'content', None)}")
        # Rebuild is drift-free by construction.
        before = {k: c.content for k, c in p.lattice.cells.items()}
        n = p.lattice.rebuild_from_plane(p.cube.session.plane)
        after = {k: c.content for k, c in p.lattice.cells.items()}
        rec("lattice::rebuild_deterministic", before == after and n == len(after),
            f"cells={n}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 2. No independent lattice truth
# ---------------------------------------------------------------------------

def t2_no_independent_lattice_truth() -> None:
    from form.open import Program
    src = inspect.getsource(Program.place)
    rec("lattice::no_direct_put", "lattice.put" not in src,
        "Program.place must not mirror via lattice.put")
    rec("lattice::rebuild_path", "rebuild_from_plane" in src,
        "only sanctioned path is rebuild_from_plane")


# ---------------------------------------------------------------------------
# 3. Weather semantics: exact multipliers + fail-safe
# ---------------------------------------------------------------------------

def t3_weather_semantics() -> None:
    from form.dell_matrix.spatial_authority import weather_modulation
    expected = {
        "clear": {"disp_mult": 1.0, "friction": 0.90,
                  "attract_radius_mult": 1.0, "jitter": 0.0},
        "rain": {"disp_mult": 1.25, "friction": 0.95,
                 "attract_radius_mult": 1.0, "jitter": 0.0},
        "fog": {"disp_mult": 0.8, "friction": 0.90,
                "attract_radius_mult": 0.6, "jitter": 0.0},
        "storm": {"disp_mult": 1.0, "friction": 0.90,
                  "attract_radius_mult": 1.0, "jitter": 0.1},
    }
    for cond, exp in expected.items():
        got = weather_modulation(cond)
        rec(f"weather::{cond}_exact", got == exp, f"{got}")
    for bad in ("hurricane", None, "", "   ", "RAINBOW"):
        got = weather_modulation(bad)
        rec(f"weather::unknown_failsafe_{bad!r}", got == expected["clear"],
            f"{bad!r} -> {got}")


# ---------------------------------------------------------------------------
# 4. Storm stays bounded
# ---------------------------------------------------------------------------

def t4_weather_bounded() -> None:
    from form.dell_matrix.spatial_authority import MAX_DISP_PER_TICK, COOLING
    owner = _owner("t4")
    _clean(owner)
    try:
        p = _prog(owner)
        p.place("a", "alpha river", x=20.0, y=20.0)
        p.place("b", "beta stream", x=60.0, y=20.0)
        _set_scores(p, {"a": 8.0, "b": 0.5})
        p.set_weather("storm")
        ok, detail, moved_any = True, "", False
        for i in range(15):
            rep = p.spatial.tick(p)
            temp_during = rep["temperature"] / COOLING
            bound = (MAX_DISP_PER_TICK * 1.0 * temp_during
                     + 0.1 * MAX_DISP_PER_TICK + 1e-9)
            md = rep["max_displacement"]
            if md > bound:
                ok, detail = False, f"tick {i}: {md:.4f} > {bound:.4f}"
                break
            if md > 1e-9:
                moved_any = True
        rec("weather::storm_bounded", ok, detail or "15 ticks within bound")
        rec("weather::storm_moves", moved_any,
            "non-vacuous: storm actually displaces")
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 5. Fog local emphasis
# ---------------------------------------------------------------------------

def t5_fog_local_emphasis() -> None:
    import form.dell_matrix.spatial_authority as sa

    def displacement_under(weather: str) -> float:
        owner = _owner("t5")
        _clean(owner)
        try:
            p = _prog(owner)
            p.place("a", "alpha river", x=-50.0, y=0.0)
            p.place("b", "beta stream", x=50.0, y=0.0)
            _set_scores(p, {"a": 10.0, "b": 0.5})
            p.set_weather(weather)
            x0, y0 = _pos(p, "b")
            p.spatial.tick(p)
            x1, y1 = _pos(p, "b")
            return math.hypot(x1 - x0, y1 - y0)
        finally:
            _clean(owner)

    d_clear = displacement_under("clear")
    d_fog = displacement_under("fog")
    rec("weather::fog_baseline_moves", d_clear > 1e-9,
        f"clear disp={d_clear:.6f} (non-vacuous)")
    rec("weather::fog_le_clear", d_fog <= d_clear + 1e-9,
        f"fog={d_fog:.6f} <= clear={d_clear:.6f}")
    # Mechanism probe: the attract-radius gate is wired into tick's well
    # loop. With a tiny radius, a well 100 units away exerts no force.
    owner = _owner("t5m")
    _clean(owner)
    try:
        p = _prog(owner)
        p.place("a", "alpha river", x=-50.0, y=0.0)
        p.place("b", "beta stream", x=50.0, y=0.0)
        _set_scores(p, {"a": 10.0, "b": 0.5})
        orig = sa.weather_modulation
        sa.weather_modulation = lambda c: {
            "disp_mult": 1.0, "friction": 0.90,
            "attract_radius_mult": 1e-8, "jitter": 0.0}  # radius = 10
        try:
            x0, y0 = _pos(p, "b")
            p.spatial.tick(p)
            x1, y1 = _pos(p, "b")
            d = math.hypot(x1 - x0, y1 - y0)
        finally:
            sa.weather_modulation = orig
        # Well at distance 100 > radius 10 -> skipped. No separation
        # (100 >> 2.5), no springs, no jitter -> exactly 0.
        rec("weather::distant_well_gated", d == 0.0,
            f"well@100 radius@10 -> disp={d}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 6 + 7. Environmental + semantic isolation (shared snapshot helper)
# ---------------------------------------------------------------------------

def _semantic_snapshot(p, owner, idea_ids):
    from form.dell_matrix import canonical_lifecycle
    from form.dell_matrix.graph_harmony import graph_neighbor_ids
    from form.mandell.semantic_graph import SemanticGraph
    from form.mandell.idea_persist import load_idea
    units = _units(p)
    unit_sem = {}
    for uid, u in units.items():
        unit_sem[uid] = (u.label, u.words, u.detail, tuple(u.goals),
                         canonical_lifecycle.resolve_lifecycle(p, uid))
    g = SemanticGraph.load(owner)
    edges = {uid: tuple(sorted(graph_neighbor_ids(g, uid)))
             for uid in units}
    props = {iid: load_idea(iid, owner).get_active_properties()
             for iid in idea_ids}
    scores = dict(p.scores())
    return (unit_sem, edges, props, scores)


def _semantic_fixtures(p, owner, prov):
    from form.mandell.idea import Idea
    from form.mandell.idea_persist import save_idea
    from form.mandell.semantic_graph import SemanticGraph, RelationshipType
    for iid, title, color in (("a", "alpha river", "blue"),
                             ("b", "beta stream", "green")):
        idea = Idea(idea_id=iid, title=title)
        idea.set_property("color", color, prov)
        save_idea(idea, owner)
    g = SemanticGraph.load(owner)
    g.add_relationship(RelationshipType.RELATED_TO, "a", "b", prov,
                       cause="p4le")


def t6_environmental_isolation() -> None:
    from form.mandell.idea import Provenance, ProvenanceSource
    owner = _owner("t6")
    _clean(owner)
    try:
        p = _prog(owner)
        p.place("a", "alpha river", x=10.0, y=10.0, words="current",
                detail="flow detail", goals=["g1"])
        p.place("b", "beta stream", x=50.0, y=20.0, words="bank",
                detail="bank detail")
        prov = Provenance(source=ProvenanceSource.SYSTEM, activity="p4le",
                          agent="p4le")
        _semantic_fixtures(p, owner, prov)
        _set_scores(p, {"a": 3.0, "b": 1.0})
        before = _semantic_snapshot(p, owner, ("a", "b"))
        for mode in ("clear", "rain", "fog", "storm"):
            p.set_weather(mode)
            for _ in range(5):
                p.force_tick()
        after = _semantic_snapshot(p, owner, ("a", "b"))
        rec("env::semantic_unchanged", before == after,
            "20 ticks across 4 weather modes: zero semantic change")
    finally:
        _clean(owner)


def t7_semantic_isolation_location() -> None:
    from form.mandell.idea import Provenance, ProvenanceSource
    owner = _owner("t7")
    _clean(owner)
    try:
        p = _prog(owner)
        p.place("a", "alpha river", x=10.0, y=10.0, words="w1")
        p.place("b", "beta stream", x=60.0, y=10.0, words="w2")
        prov = Provenance(source=ProvenanceSource.SYSTEM, activity="p4le",
                          agent="p4le")
        _semantic_fixtures(p, owner, prov)
        _set_scores(p, {"a": 5.0, "b": 0.5})
        pos_before = {uid: _pos(p, uid) for uid in ("a", "b")}
        sem_before = _semantic_snapshot(p, owner, ("a", "b"))
        for _ in range(10):
            p.force_tick()
        pos_after = {uid: _pos(p, uid) for uid in ("a", "b")}
        moved = max(math.hypot(pos_after[u][0] - pos_before[u][0],
                               pos_after[u][1] - pos_before[u][1])
                    for u in pos_before)
        sem_after = _semantic_snapshot(p, owner, ("a", "b"))
        rec("semo::moved", moved > 1e-6,
            f"max displacement={moved:.4f} (non-vacuous)")
        rec("semo::truth_unchanged", sem_before == sem_after,
            "location changed; properties/lifecycle/edges/scores identical")
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 8. Causal mutants
# ---------------------------------------------------------------------------

def _mutant_prog(owner):
    _clean(owner)
    p = _prog(owner)
    p.place("a", "alpha river", x=10.0, y=10.0)
    p.place("b", "beta stream", x=60.0, y=10.0)
    _set_scores(p, {"a": 5.0, "b": 0.5})
    return p


def _settle_total_movement(p, max_ticks=50):
    before = {uid: _pos(p, uid) for uid in _units(p)}
    p.spatial_settle(max_ticks=max_ticks)
    after = {uid: _pos(p, uid) for uid in _units(p)}
    return sum(math.hypot(after[u][0] - before[u][0],
                          after[u][1] - before[u][1]) for u in before)


def t8a_mutant_owner_bypass() -> None:
    from form.dell_matrix.spatial_authority import SpatialAuthority
    owner = _owner("t8a")
    p = _mutant_prog(owner)
    try:
        base = _settle_total_movement(p)
        rec("mutant::baseline_moves", base > 1e-9,
            f"settle moved total={base:.4f} (non-vacuous)")
    finally:
        _clean(owner)
    p = _mutant_prog(owner)
    orig = SpatialAuthority.tick
    def noop(self, program):
        return {"moved": 0, "max_displacement": 0.0, "max_force": 0.0,
                "converged": True, "state": "noop", "tick": self.tick_count,
                "temperature": self.temperature}
    SpatialAuthority.tick = noop
    try:
        try:
            total = _settle_total_movement(p)
            assert total > 1e-9, \
                f"settle moved nothing despite nonzero forces"
            detected = False
        except AssertionError:
            detected = True
    finally:
        SpatialAuthority.tick = orig
        _clean(owner)
    rec("mutant::owner_bypass_detected", detected,
        "no-op owner -> stability assertion fails")


def t8b_mutant_weather_write() -> None:
    import form.dell_matrix.spatial_authority as sa
    from form.dell_matrix.spatial_authority import MAX_DISP_PER_TICK, COOLING
    owner = _owner("t8b")
    _clean(owner)
    try:
        p = _prog(owner)
        # Massive well very close: force-limited displacement would exceed
        # the honest bound if the cap is raised by the mutant.
        p.place("a", "alpha river", x=10.0, y=10.0)
        p.place("b", "beta stream", x=12.0, y=10.0)
        _set_scores(p, {"a": 1000.0, "b": 0.5})
        p.set_weather("storm")
        orig = sa.weather_modulation
        sa.weather_modulation = lambda c: {
            "disp_mult": 100.0, "friction": 0.90,
            "attract_radius_mult": 1.0, "jitter": 0.0}
        try:
            violated, detail = False, ""
            for i in range(5):
                rep = p.spatial.tick(p)
                temp_during = rep["temperature"] / COOLING
                honest = (MAX_DISP_PER_TICK * 1.0 * temp_during
                          + 0.1 * MAX_DISP_PER_TICK + 1e-9)
                if rep["max_displacement"] > honest:
                    violated = True
                    detail = (f"tick {i}: disp={rep['max_displacement']:.2f} "
                              f"> honest {honest:.2f}")
                    break
        finally:
            sa.weather_modulation = orig
        rec("mutant::weather_write_detected", violated,
            detail or "mutant did NOT break the bound (bad mutant)")
    finally:
        _clean(owner)


def t8c_mutant_persist_skip() -> None:
    from form.persist_rest import save, load
    from form.persist import _path
    from form.dell_matrix.spatial_authority import SpatialLoadError
    owner = _owner("t8c")
    _clean(owner)
    try:
        p = _prog(owner)
        p.place("a", "alpha river", x=10.0, y=10.0)
        path = save(p)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        rec("mutant::spatial_member_present", "spatial" in data,
            "non-vacuous: spatial member persisted")
        data["spatial"] = {"version": 999}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        try:
            load(owner)
            raised = None
        except Exception as e:  # noqa: BLE001 - asserting fail-closed
            raised = e
        rec("mutant::persist_skip_failclosed",
            isinstance(raised, SpatialLoadError),
            f"raised={type(raised).__name__}: {raised}")
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 9. Malformed spatial state
# ---------------------------------------------------------------------------

def t9_malformed_spatial() -> None:
    from form.dell_matrix.spatial_authority import (
        SpatialAuthority, SpatialLoadError)
    try:
        SpatialAuthority.from_dict({"version": 999})
        r1 = False
    except SpatialLoadError:
        r1 = True
    rec("malformed::bad_version", r1, "version 999 raises")
    inst = SpatialAuthority.from_dict(None)
    rec("malformed::none_fresh",
        inst.tick_count == 0 and inst.temperature == 1.0,
        "None -> fresh (declared)")
    try:
        SpatialAuthority.from_dict(
            {"version": 1, "velocities": {"a": [float("nan"), 0.0]}})
        r3 = False
    except SpatialLoadError:
        r3 = True
    rec("malformed::nan_velocity", r3, "NaN velocity raises")
    try:
        SpatialAuthority.from_dict("not-a-dict")
        r4 = False
    except SpatialLoadError:
        r4 = True
    rec("malformed::nondict", r4, "non-dict raises")


# ---------------------------------------------------------------------------

def main() -> int:
    t1_lattice_derived()
    t2_no_independent_lattice_truth()
    t3_weather_semantics()
    t4_weather_bounded()
    t5_fog_local_emphasis()
    t6_environmental_isolation()
    t7_semantic_isolation_location()
    t8a_mutant_owner_bypass()
    t8b_mutant_weather_write()
    t8c_mutant_persist_skip()
    t9_malformed_spatial()
    n = len(FAILURES)
    print(f"P4 LATTICE+ENV: {'ALL PASS' if not n else f'{n} FAILURES: {FAILURES}'}",
          flush=True)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
