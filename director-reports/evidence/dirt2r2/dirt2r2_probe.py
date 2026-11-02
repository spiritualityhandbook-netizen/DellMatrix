#!/usr/bin/env python3
"""DIR-T2-R2 failing-first probe.

Implements the Director's required counterexample (DIR-2026-11-02-
CONSOLIDATED-R1) plus the compatibility cases from the ground
document. Run from a DellMatrix repo root (cwd = repo root).

Exit 0 = identity integrity holds. Exit 1 = defect present.
"""
import os
import sys

sys.path.insert(0, os.getcwd())

from form.dell_matrix.forces import GrowthForce          # noqa: E402
from form.dell_matrix.view_rooms import filter_nodes_for_room  # noqa: E402

PREFIX = "P" * 80
LABEL_A = PREFIX + " alpha-unique"
LABEL_B = PREFIX + " beta-different"

failures = []


def case(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))
    if not cond:
        failures.append(name)


# Case 1 — the Director's counterexample, canonical plant() path.
gf = GrowthForce()
gf.plant(LABEL_A)
for _ in range(4):
    gf.grow_all(2.0)
stage_a = gf.plants[0]["stage"]
out = filter_nodes_for_room("growth",
                            [{"id": "b", "label": LABEL_B, "score": 0.0}],
                            plants=gf.plants)
case("R2-1 omitted node B never receives A's stage",
     out[0].get("stage") is None,
     f"B got stage={out[0].get('stage')!r} source={out[0].get('stage_source')!r}; A stage={stage_a!r}")

# Case 2 — legacy record (no full identity): prefix-only stays ambiguous.
out = filter_nodes_for_room("growth",
                            [{"id": "b", "label": LABEL_B, "score": 0.0}],
                            plants=[{"idea": PREFIX, "stage": "branch"}])
case("R2-2 legacy prefix-only match stays ambiguous",
     out[0].get("stage") is None
     and out[0].get("stage_source") == "ambiguous",
     f"B got stage={out[0].get('stage')!r} source={out[0].get('stage_source')!r}")

# Case 3 — both visible with full identities: each node its OWN plant.
gf3 = GrowthForce()
gf3.plant(LABEL_A)
for _ in range(4):
    gf3.grow_all(2.0)
own_a = gf3.plants[0]["stage"]
gf3.plant(LABEL_B)  # B's own plant, still seed
out = filter_nodes_for_room(
    "growth",
    [{"id": "a", "label": LABEL_A, "score": 0.0},
     {"id": "b", "label": LABEL_B, "score": 0.0}],
    plants=gf3.plants)
case("R2-3 both-visible: A resolves to A's own stage",
     out[0].get("stage") == own_a
     and out[0].get("stage_source") == "growth_force",
     f"A got {out[0].get('stage')!r}/{out[0].get('stage_source')!r}, own={own_a!r}")
case("R2-4 both-visible: B resolves to B's own stage (seed)",
     out[1].get("stage") == "seed"
     and out[1].get("stage_source") == "growth_force",
     f"B got {out[1].get('stage')!r}/{out[1].get('stage_source')!r}")

# Case 4 — plant() is idempotent on exact identity (owner rule).
gf4 = GrowthForce()
gf4.plant(LABEL_A)
gf4.plant(LABEL_A)
case("R2-5 plant() twice on one identity keeps one record",
     len(gf4.plants) == 1, f"plants={len(gf4.plants)}")

print(f"=== dirt2r2 probe: {5 - len(failures)}/5 ===")
sys.exit(1 if failures else 0)
