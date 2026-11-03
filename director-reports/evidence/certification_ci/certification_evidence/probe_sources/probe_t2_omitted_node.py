import os, sys
sys.path.insert(0, os.getcwd())
from form.dell_matrix.forces import GrowthForce
from form.dell_matrix.view_rooms import filter_nodes_for_room

PREFIX = "Q" * 80
LABEL_A = PREFIX + " first-planted-idea"
LABEL_B = PREFIX + " never-planted-node"
fails = []

def case(name, cond, detail=""):
    print(("[PASS] " if cond else "[FAIL] ") + name
          + (" -- " + detail if detail else ""))
    if not cond:
        fails.append(name)

gf = GrowthForce()
gf.plant(LABEL_A)
for _ in range(4):
    gf.grow_all(2.0)
stage_a = gf.plants[0]["stage"]
case("sanity: plant A grew past seed", stage_a not in (None, "seed"),
     "A stage=%r" % (stage_a,))

out = filter_nodes_for_room(
    "growth", [{"id": "b", "label": LABEL_B, "score": 0.0}],
    plants=gf.plants)
case("DIR-T2-R2 counterexample: omitted node B never receives A's stage",
     out[0].get("stage") is None,
     "B stage=%r source=%r" % (out[0].get("stage"),
                               out[0].get("stage_source")))

out = filter_nodes_for_room(
    "growth", [{"id": "a", "label": LABEL_A, "score": 0.0}],
    plants=gf.plants)
case("positive control: node A resolves to A's own stage",
     out[0].get("stage") == stage_a
     and out[0].get("stage_source") == "growth_force",
     "A stage=%r source=%r" % (out[0].get("stage"),
                               out[0].get("stage_source")))

out = filter_nodes_for_room(
    "growth", [{"id": "b", "label": LABEL_B, "score": 0.0}],
    plants=[{"idea": PREFIX, "stage": "branch"}])
case("legacy prefix-only plant: B stays ambiguous, never attributed",
     out[0].get("stage") is None
     and out[0].get("stage_source") == "ambiguous",
     "B stage=%r source=%r" % (out[0].get("stage"),
                               out[0].get("stage_source")))

print("=== probe_t2_omitted_node: %d/4 ===" % (4 - len(fails)))
sys.exit(1 if fails else 0)
