"""T2 label-identity probe (Priority 3, DIR-2026-11-02-R1).

Two DISTINCT node labels sharing the first 80 chars collapse to
one plant key. Expected post-fix: neither node claims the plant's
stage (stage=None, stage_source="ambiguous"); a unique-label
node still resolves; a plant-side stage conflict on one key is
ambiguous too. Pre-fix, the unplanted sibling steals the stage.
"""
import os
import sys

# Repo root = three levels up from director-reports/evidence/t2label/.
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..")))

from form.dell_matrix.view_rooms import filter_nodes_for_room  # noqa: E402
from form.dell_matrix.forces import GrowthForce  # noqa: E402

PREFIX = "P" * 80
LABEL_A = PREFIX + " alpha-unique"
LABEL_B = PREFIX + " beta-different"

gf = GrowthForce()
gf.plant(LABEL_A)
for _ in range(4):
    gf.grow_all(2.0)
stage_a = gf.plants[0]["stage"]
print(f"plant stored idea == full label? {gf.plants[0]['idea'] == LABEL_A}"
      f" (stored len {len(gf.plants[0]['idea'])}), stage={stage_a}")

nodes = [{"id": "a", "label": LABEL_A, "score": 0.0},
         {"id": "b", "label": LABEL_B, "score": 0.0}]
out = filter_nodes_for_room("growth", nodes, plants=gf.plants)
for n in out:
    print(f"node {n['id']}: stage={n.get('stage')} "
          f"source={n.get('stage_source')}")

out_c = filter_nodes_for_room(
    "growth", [{"id": "c", "label": "Solo", "score": 0.0}],
    plants=[{"idea": "Solo", "stage": "branch"}])
print(f"unique control: stage={out_c[0].get('stage')} "
      f"source={out_c[0].get('stage_source')}")

out_d = filter_nodes_for_room(
    "growth", [{"id": "d", "label": "Duo", "score": 0.0}],
    plants=[{"idea": "Duo", "stage": "seed"},
            {"idea": "Duo", "stage": "branch"}])
print(f"plant-conflict: stage={out_d[0].get('stage')} "
      f"source={out_d[0].get('stage_source')}")

ok = (out[0].get("stage") is None
      and out[0].get("stage_source") == "ambiguous"
      and out[1].get("stage") is None
      and out[1].get("stage_source") == "ambiguous"
      and out_c[0].get("stage") == "branch"
      and out_c[0].get("stage_source") == "growth_force"
      and out_d[0].get("stage") is None
      and out_d[0].get("stage_source") == "ambiguous")
print("PROBE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
