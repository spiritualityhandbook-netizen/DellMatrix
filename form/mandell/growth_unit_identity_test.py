"""SM-39: Growth unit identity — identical full labels are NOT identity.

Before: GrowthForce.plant() deduped by full label and the growth lens
keyed stages by full label, so two distinct Plane units sharing one
identical label collapsed into one plant and both inherited its stage
(the T2 retained exception).

Now: plant(..., unit_id=...) keys identity by unit id; the lens
attributes a uid-keyed plant only to the node whose id matches.
Label-only plants/records keep the exact legacy label rules.

Checks run through the canonical lens + GrowthForce, plus the
ForceField.tick production path. No Program/persistent state used.
"""
from __future__ import annotations

CHECKS: list = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(f"{name}: {detail}")


def run_all() -> None:
    from form.dell_matrix.forces import ForceField, GrowthForce
    from form.dell_matrix.view_rooms import filter_nodes_for_room

    label = "Identical Label"
    gf = GrowthForce()
    a = gf.plant(label, unit_id="unit-AAA")
    b = gf.plant(label, unit_id="unit-BBB")
    check("two units, one label -> two plant records",
          len(gf.plants) == 2 and a is not b, f"plants={len(gf.plants)}")
    check("plant records carry their unit ids",
          a.get("unit_id") == "unit-AAA" and b.get("unit_id") == "unit-BBB")
    again = gf.plant(label, unit_id="unit-AAA")
    check("re-plant same unit returns its own record",
          again is a and len(gf.plants) == 2)

    # Set AAA's plant stage directly (grow_all would grow both).
    gf.plants[0]["stage"] = "branch"
    nodes = [{"id": "unit-AAA", "label": label, "score": 0.0},
             {"id": "unit-BBB", "label": label, "score": 0.0}]
    out = filter_nodes_for_room("growth", nodes, plants=gf.plants)
    by_id = {n["id"]: n for n in out}
    check("grown unit reports its own stage",
          by_id["unit-AAA"].get("stage") == "branch"
          and by_id["unit-AAA"].get("stage_source") == "growth_force",
          f"{by_id['unit-AAA']}")
    check("same-label sibling does NOT inherit the stage",
          by_id["unit-BBB"].get("stage") == "seed"
          and by_id["unit-BBB"].get("stage_source") == "growth_force",
          f"{by_id['unit-BBB']}")

    # A uid plant alone: the sibling visible alone stays unplanted.
    gf2 = GrowthForce()
    gf2.plant(label, unit_id="unit-AAA")
    gf2.plants[0]["stage"] = "branch"
    out = filter_nodes_for_room(
        "growth", [{"id": "unit-BBB", "label": label, "score": 0.0}],
        plants=gf2.plants)
    check("sibling alone never inherits a uid plant by label",
          out[0].get("stage") is None
          and out[0].get("stage_source") == "unplanted",
          f"{out[0]}")

    # Legacy label-only behavior is unchanged.
    gf3 = GrowthForce()
    gf3.plant(label)
    dup = gf3.plant(label)
    check("label-only plant() twice keeps one record (legacy)",
          len(gf3.plants) == 1 and dup is gf3.plants[0]
          and "unit_id" not in gf3.plants[0])
    gf3.plants[0]["stage"] = "stem"
    out = filter_nodes_for_room(
        "growth", [{"id": "any-node", "label": label, "score": 0.0}],
        plants=gf3.plants)
    check("label-only plant still attributes by exact label (legacy)",
          out[0].get("stage") == "stem"
          and out[0].get("stage_source") == "growth_force", f"{out[0]}")
    mixed = gf3.plant(label, unit_id="unit-CCC")
    check("label-only call does not collapse into / block a uid plant",
          mixed.get("unit_id") == "unit-CCC" and len(gf3.plants) == 2)

    # Production tick path: node ids thread through, no duplicates.
    ff = ForceField()
    ff.activate("growth")
    tick_nodes = [{"id": "unit-AAA", "label": label, "score": 0.0},
                  {"id": "unit-BBB", "label": label, "score": 0.0}]
    ff.tick(tick_nodes)
    ff.tick(tick_nodes)
    check("ForceField.tick plants both same-label units, once each",
          len(ff.growth.plants) == 2
          and {p.get("unit_id") for p in ff.growth.plants}
          == {"unit-AAA", "unit-BBB"},
          f"plants={[(p.get('unit_id'), p.get('idea_full')) for p in ff.growth.plants]}")

    print(f"SM-39 growth-unit-identity: {len(CHECKS)}/{len(CHECKS)} checks passed")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"SM39 SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
