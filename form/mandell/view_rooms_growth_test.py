"""View-rooms growth referent proofs (WS-THEATER T2).

The growth room claimed a stage for every node, derived from its
score (stage = seed..fruit at int(score*2)) — a second, invented
growth authority. The canonical authority is GrowthForce: it
plants node labels and grows them through the same stage list
(forces.py). This suite proves the lens now reports ONLY plant
stages, through the lens function and through the real Program
production path (Program.view_status).

All Program fixtures use disposable-copy isolation (unique owners)
with canonical-path cleanup that fails loudly.
"""

from __future__ import annotations

import glob
import os
import sys
import uuid

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))


def unique_owner(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _cleanup(owner: str) -> None:
    base = os.path.join(os.path.abspath("."), "form", "state")
    for pat in (f"program_{owner}.json", f"nursery_{owner}.json",
                f"checkpoint_{owner}_*", f"confirm_journal_{owner}.json",
                f"confirm_gen_{owner}.json", f"confirm_current_{owner}.json",
                f"exchange_journal_{owner}.json"):
        for p in glob.glob(os.path.join(base, pat)):
            try:
                os.remove(p)
            except FileNotFoundError:
                pass
            except OSError as e:  # loud, per program cleanup law
                raise AssertionError(f"cleanup failed for {p}: {e}")
    d = os.path.join(base, f"ideas_{owner}")
    if os.path.isdir(d):
        import shutil
        shutil.rmtree(d)


def part_lens() -> None:
    from form.dell_matrix.view_rooms import filter_nodes_for_room
    from form.dell_matrix.forces import GrowthForce

    gf = GrowthForce()
    gf.plant("Alpha")
    for _ in range(4):
        gf.grow_all(2.0)
    alpha_stage = gf.plants[0]["stage"]
    check("growth: fixture plant actually grew past seed",
          alpha_stage != "seed", alpha_stage)

    out = filter_nodes_for_room(
        "growth", [{"id": "a", "label": "Alpha", "score": 0.0}],
        plants=gf.plants)
    check("growth: planted node stage is the plant's stage (score 0)",
          out[0].get("stage") == alpha_stage
          and out[0].get("stage_source") == "growth_force",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    out = filter_nodes_for_room(
        "growth", [{"id": "a", "label": "Alpha", "score": 99.0}],
        plants=gf.plants)
    check("growth: score cannot move a planted node's stage",
          out[0].get("stage") == alpha_stage, f"{out[0].get('stage')}")

    out = filter_nodes_for_room(
        "growth", [{"id": "x", "label": "Ghost", "score": 3.0}],
        plants=gf.plants)
    check("growth: unplanted node claims no stage",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "unplanted",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    out = filter_nodes_for_room(
        "growth", [{"id": "a", "label": "Alpha", "score": 3.0}])
    check("growth: no plants supplied -> no stage claim",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "unavailable",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    out = filter_nodes_for_room(
        "growth", [{"id": "a", "label": "Alpha", "score": 0.0}],
        plants=[{"idea": "Alpha", "stage": "not-a-stage"}])
    check("growth: non-canonical plant stage is not passed through",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "unplanted",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    out = filter_nodes_for_room(
        "water", [{"id": "a", "label": "Alpha", "score": 0.2}],
        plants=gf.plants)
    check("growth: other rooms untouched (water has no stage field)",
          "stage" not in out[0] and out[0].get("view_tag") == "water")


def part_production_path() -> None:
    from form.open import Program
    owner = unique_owner("vrgrowth")
    _cleanup(owner)
    try:
        prog = Program(owner=owner)
        plane = prog.cube.session.plane
        plane.place("vg_a", "Alphafern", words="alpha")
        plane.place("vg_b", "Betastone", words="beta")
        prog.active_view = "growth"
        # Plant + grow ONLY Alphafern through the canonical force.
        prog.forces.growth.plant("Alphafern", owner)
        for _ in range(4):
            prog.forces.growth.grow_all(2.0)
        plant_stage = prog.forces.growth.plants[0]["stage"]
        vs = prog.view_status()
        by_label = {n.get("label"): n for n in vs.get("nodes") or []}
        a = by_label.get("Alphafern") or {}
        b = by_label.get("Betastone") or {}
        check("production: view_status planted node carries plant stage",
              a.get("stage") == plant_stage and plant_stage != "seed"
              and a.get("stage_source") == "growth_force",
              f"{a.get('stage')}/{a.get('stage_source')} vs plant {plant_stage}")
        check("production: view_status unplanted node claims no stage",
              b.get("stage") is None
              and b.get("stage_source") == "unplanted",
              f"{b.get('stage')}/{b.get('stage_source')}")
    finally:
        _cleanup(owner)


def _run_all() -> int:
    part_lens()
    part_production_path()
    passed = sum(1 for _, ok in CHECKS if ok)
    print(f"=== view-rooms growth referent: {passed}/{len(CHECKS)} ===")
    return 0 if passed == len(CHECKS) else 1


def smoke() -> bool:
    """Regression-harness entry (form.regress calls module:smoke)."""
    global CHECKS
    CHECKS = []
    return _run_all() == 0


def main() -> int:
    return _run_all()


if __name__ == "__main__":
    sys.exit(main())
