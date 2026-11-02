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

Label-identity addendum (DIR-2026-11-02-R1 Priority 3): plant()
stores idea=label[:80], so two distinct labels sharing that
prefix collapse to one plant key. The lens must not attribute
one plant's stage to another node: colliding keys and
stage-conflicted keys report stage=None, stage_source=
"ambiguous". Unique labels, agreeing duplicate plants, and
identical-label duplicate nodes still resolve normally.

DIR-T2-R2 addendum (DIR-2026-11-02-CONSOLIDATED-R1): the P3
detector only saw labels present in the node list, so an
unplanted node B alone in the lens inherited plant A's stage
through their shared truncated key. plant() now retains the
exact identity as idea_full (C-Q3), and the lens attributes a
stage only where identity is proven: exact plants resolve to
their own nodes (both-visible collided pairs included), a
plant provably belonging to another label contributes nothing,
and legacy records without idea_full stay prefix-only —
"ambiguous" — wherever stored key != node label (C-Q4:
agreeing stages never prove identity). Two checks in
part_ambiguous changed verdict for exactly this reason: with
idea_full the planted node's identity IS provable, so it now
resolves to its own stage, and its unplanted sibling reports
"unplanted" (the only plant is provably not its) instead of
"ambiguous". The anti-theft contract — B never receives A's
stage — is preserved and strengthened.
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


def part_ambiguous() -> None:
    from form.dell_matrix.view_rooms import filter_nodes_for_room
    from form.dell_matrix.forces import GrowthForce

    prefix = "P" * 80
    label_a = prefix + " alpha-unique"
    label_b = prefix + " beta-different"
    gf = GrowthForce()
    gf.plant(label_a)
    for _ in range(4):
        gf.grow_all(2.0)
    grown = gf.plants[0]["stage"]
    check("ambiguous: fixture plant grew and stored truncated key",
          grown != "seed" and gf.plants[0]["idea"] == prefix,
          f"stage={grown} idea_len={len(gf.plants[0]['idea'])}")

    out = filter_nodes_for_room(
        "growth",
        [{"id": "a", "label": label_a, "score": 0.0},
         {"id": "b", "label": label_b, "score": 0.0}],
        plants=gf.plants)
    # DIR-T2-R2: the fixture plant now carries idea_full, so this
    # node's identity is provable and it resolves to its OWN stage
    # (under P3 it reported "ambiguous"). The sibling's plant is
    # provably not its, so it reports "unplanted" — and still never
    # receives A's stage.
    check("r2: planted node under a formerly-collided key resolves by exact identity",
          out[0].get("stage") == grown
          and out[0].get("stage_source") == "growth_force",
          f"{out[0].get('stage')}/{out[0].get('stage_source')} vs grown {grown}")
    check("r2: unplanted sibling cannot steal the plant's stage",
          out[1].get("stage") is None
          and out[1].get("stage_source") == "unplanted",
          f"{out[1].get('stage')}/{out[1].get('stage_source')}")

    out = filter_nodes_for_room(
        "growth", [{"id": "d", "label": "Duo", "score": 0.0}],
        plants=[{"idea": "Duo", "stage": "seed"},
                {"idea": "Duo", "stage": "branch"}])
    check("ambiguous: plants disagreeing on one key -> no stage claim",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "ambiguous",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    out = filter_nodes_for_room(
        "growth", [{"id": "e", "label": "Pair", "score": 0.0}],
        plants=[{"idea": "Pair", "stage": "branch"},
                {"idea": "Pair", "stage": "branch"}])
    check("ambiguous: agreeing duplicate plants still resolve",
          out[0].get("stage") == "branch"
          and out[0].get("stage_source") == "growth_force",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    gf2 = GrowthForce()
    gf2.plant("Twin")
    out = filter_nodes_for_room(
        "growth",
        [{"id": "t1", "label": "Twin", "score": 0.0},
         {"id": "t2", "label": "Twin", "score": 0.0}],
        plants=gf2.plants)
    check("ambiguous: identical-label duplicate nodes are one identity",
          all(n.get("stage") == "seed"
              and n.get("stage_source") == "growth_force" for n in out),
          f"{[(n.get('stage'), n.get('stage_source')) for n in out]}")


def part_r2() -> None:
    from form.dell_matrix.view_rooms import filter_nodes_for_room
    from form.dell_matrix.forces import GrowthForce, ForceField

    prefix = "P" * 80
    label_a = prefix + " alpha-unique"
    label_b = prefix + " beta-different"

    # The Director's counterexample, canonical plant() path:
    # plant A, grow it, supply ONLY unplanted node B.
    gf = GrowthForce()
    gf.plant(label_a)
    for _ in range(4):
        gf.grow_all(2.0)
    grown = gf.plants[0]["stage"]
    check("r2: plant() retains exact identity alongside truncated key",
          gf.plants[0].get("idea_full") == label_a
          and gf.plants[0].get("idea") == prefix,
          f"idea_full={gf.plants[0].get('idea_full')!r}")
    out = filter_nodes_for_room(
        "growth", [{"id": "b", "label": label_b, "score": 0.0}],
        plants=gf.plants)
    check("r2: omitted node B never receives A's stage",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "unplanted",
          f"{out[0].get('stage')}/{out[0].get('stage_source')} vs A {grown}")

    # Legacy record (no idea_full): prefix-only match stays
    # ambiguous for BOTH long labels — identity is unprovable.
    legacy = [{"idea": prefix, "stage": "branch"}]
    out = filter_nodes_for_room(
        "growth", [{"id": "b", "label": label_b, "score": 0.0}],
        plants=legacy)
    check("r2: legacy prefix-only match stays ambiguous (node B)",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "ambiguous",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")
    out = filter_nodes_for_room(
        "growth", [{"id": "a", "label": label_a, "score": 0.0}],
        plants=legacy)
    check("r2: legacy prefix-only match stays ambiguous (node A)",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "ambiguous",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    # C-Q4: agreeing stages never prove identity.
    out = filter_nodes_for_room(
        "growth", [{"id": "b", "label": label_b, "score": 0.0}],
        plants=[{"idea": prefix, "stage": "branch"},
                {"idea": prefix, "stage": "branch"}])
    check("r2: agreeing legacy stages still do not prove identity",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "ambiguous",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    # Both visible with full identities: each node its OWN plant.
    gf3 = GrowthForce()
    gf3.plant(label_a)
    for _ in range(4):
        gf3.grow_all(2.0)
    own_a = gf3.plants[0]["stage"]
    gf3.plant(label_b)
    out = filter_nodes_for_room(
        "growth",
        [{"id": "a", "label": label_a, "score": 0.0},
         {"id": "b", "label": label_b, "score": 0.0}],
        plants=gf3.plants)
    check("r2: both-visible node A resolves to A's own plant",
          out[0].get("stage") == own_a and own_a != "seed"
          and out[0].get("stage_source") == "growth_force",
          f"{out[0].get('stage')}/{out[0].get('stage_source')} vs own {own_a}")
    check("r2: both-visible node B resolves to B's own plant",
          out[1].get("stage") == "seed"
          and out[1].get("stage_source") == "growth_force",
          f"{out[1].get('stage')}/{out[1].get('stage_source')}")

    # Proven plants for one label that disagree are not a fact.
    out = filter_nodes_for_room(
        "growth", [{"id": "a", "label": label_a, "score": 0.0}],
        plants=[{"idea": prefix, "idea_full": label_a, "stage": "seed"},
                {"idea": prefix, "idea_full": label_a, "stage": "branch"}])
    check("r2: exact-identity plants disagreeing -> ambiguous",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "ambiguous",
          f"{out[0].get('stage')}/{out[0].get('stage_source')}")

    # Owner identity rule: one identity = one plant record, so the
    # production dedupe sites cannot mint divergent duplicates.
    gf4 = GrowthForce()
    gf4.plant(label_a)
    again = gf4.plant(label_a)
    check("r2: plant() twice on one identity keeps one record",
          len(gf4.plants) == 1 and again is gf4.plants[0],
          f"plants={len(gf4.plants)}")
    ff = ForceField()
    node = [{"id": "n1", "label": label_a, "score": 0.0}]
    ff.tick(node)
    ff.tick(node)
    check("r2: ForceField.tick does not duplicate a long-label plant",
          len(ff.growth.plants) == 1,
          f"plants={len(ff.growth.plants)}")


def part_r2_production() -> None:
    from form.open import Program
    owner = unique_owner("vrgrowthr2")
    _cleanup(owner)
    try:
        prefix = "P" * 80
        label_a = prefix + " alpha-unique"
        label_b = prefix + " beta-different"
        prog = Program(owner=owner)
        plane = prog.cube.session.plane
        plane.place("r2_b", label_b, words="beta")
        prog.active_view = "growth"
        # Plant + grow ONLY A through the canonical force; B is a
        # plane node that was never planted.
        prog.forces.growth.plant(label_a, owner)
        for _ in range(4):
            prog.forces.growth.grow_all(2.0)
        vs = prog.view_status()
        by_label = {n.get("label"): n for n in vs.get("nodes") or []}
        b = by_label.get(label_b) or {}
        check("r2 production: view_status omitted sibling claims no stage",
              b.get("stage") is None
              and b.get("stage_source") == "unplanted",
              f"{b.get('stage')}/{b.get('stage_source')}")
    finally:
        _cleanup(owner)


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
    part_ambiguous()
    part_r2()
    part_r2_production()
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
