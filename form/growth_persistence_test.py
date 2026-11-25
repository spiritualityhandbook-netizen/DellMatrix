"""SM-39 persistence closure — Growth plant records survive save/reload.

Director finding (morning review 2026-11-04): ForceField.to_dict()
serialized the NUMBER of growth plants, not the records, and
from_dict() restored none — so every save/reload silently reset the
whole GrowthForce plant list, and the SM-39 unit-ID identity repair
was in-memory only. This suite pins the bounded repair:

  * to_dict carries the full plant records (identity, stage, height,
    age, history) alongside the legacy count, which is retained so
    older readers see the same shape;
  * from_dict restores records — two identical-label units stay
    distinct with their own stages, unit IDs and plant IDs stable;
  * legacy count-only payloads load with zero plants (nothing is
    fabricated from a count);
  * malformed records (non-dict, no identity) are skipped, duplicate
    identities keep the first record — degrade honestly, never merge
    or invent;
  * the full Program save/load path (form.persist_rest) carries the
    records end to end.

Run: python3 -m form.growth_persistence_test
"""
from __future__ import annotations

import copy
import os
import shutil
import sys
import tempfile

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}"
          + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        raise AssertionError(name)


def _field_with_plants():
    from form.dell_matrix.forces import ForceField
    ff = ForceField()
    g = ff.growth
    g.plant("Shared Label", unit_id="unit-aaa")
    g.plant("Shared Label", unit_id="unit-bbb")
    g.plant("Legacy Label Only")
    # Diverge the two same-label units: grow only until stages differ.
    for _ in range(12):
        g.grow_all(2.0)
        stages = {p.get("unit_id"): p["stage"]
                  for p in g.plants if p.get("unit_id")}
        if stages.get("unit-aaa") != stages.get("unit-bbb"):
            break
    # Force a deterministic divergence if growth kept them in lockstep:
    for p in g.plants:
        if p.get("unit_id") == "unit-bbb":
            p["stage"] = "leaf"
            p["height"] = 9.5
    return ff


def run_all():
    from form.dell_matrix.forces import ForceField

    ff = _field_with_plants()
    before = copy.deepcopy(ff.growth.plants)
    check("fixture holds two distinct same-label uid plants + legacy",
          len(before) == 3
          and len({p.get("unit_id") for p in before
                   if p.get("unit_id")}) == 2)

    data = ff.to_dict()
    g = data.get("growth") or {}
    check("to_dict keeps the legacy plant count for old readers",
          g.get("plants") == 3)
    records = g.get("plant_records")
    check("to_dict carries the full plant records",
          isinstance(records, list) and len(records) == 3
          and all(isinstance(r, dict) for r in records))

    ff2 = ForceField.from_dict(copy.deepcopy(data))
    after = ff2.growth.plants
    check("round-trip restores every plant record", len(after) == 3)
    by_uid = {p.get("unit_id"): p for p in after if p.get("unit_id")}
    check("identical-label units remain distinct after reload",
          set(by_uid) == {"unit-aaa", "unit-bbb"}
          and by_uid["unit-aaa"]["idea_full"] == "Shared Label"
          and by_uid["unit-bbb"]["idea_full"] == "Shared Label")
    check("different growth stages survive save/reload",
          by_uid["unit-aaa"]["stage"]
          == [p for p in before if p.get("unit_id") == "unit-aaa"][0]["stage"]
          and by_uid["unit-bbb"]["stage"] == "leaf"
          and by_uid["unit-bbb"]["height"] == 9.5)
    check("unit IDs and plant IDs are stable across the round-trip",
          {p["id"] for p in after} == {p["id"] for p in before})
    legacy = [p for p in after if not p.get("unit_id")]
    check("label-keyed legacy plant round-trips with its full label",
          len(legacy) == 1
          and legacy[0].get("idea_full") == "Legacy Label Only")

    # Legacy payload: exactly what pre-repair files contain.
    legacy_data = {"growth": {"plants": 3, "intensity": 0.65,
                              "evolution_level": 1.0}}
    ff3 = ForceField.from_dict(copy.deepcopy(legacy_data))
    check("legacy count-only payload loads with zero plants "
          "(nothing fabricated from a count)",
          ff3.growth.plants == [])

    # Malformed + duplicate records degrade honestly.
    messy = {"growth": {"plants": 5, "plant_records": [
        {"id": "plant-1", "idea": "Ok", "idea_full": "Ok",
         "unit_id": "unit-ok", "stage": "stem", "height": 3.0,
         "age": 2, "history": [{"stage": "seed"}, {"stage": "stem"}]},
        "not-a-dict",
        {"idea": "", "idea_full": ""},
        {"id": "plant-2", "idea": "Dup", "idea_full": "Dup",
         "unit_id": "unit-ok", "stage": "fruit", "height": 9.0,
         "age": 9, "history": []},
        {"id": "plant-3", "idea": "NoId", "idea_full": "NoId",
         "stage": "seed", "height": 0.0, "age": 0, "history": []},
    ]}}
    ff4 = ForceField.from_dict(copy.deepcopy(messy))
    kept = ff4.growth.plants
    check("malformed records are skipped, valid ones restored",
          len(kept) == 2
          and {p.get("unit_id") for p in kept} == {"unit-ok", None})
    dup = [p for p in kept if p.get("unit_id") == "unit-ok"]
    check("duplicate identity keeps the first record, never merges",
          len(dup) == 1 and dup[0]["stage"] == "stem")

    # Full Program path: persist_rest save -> load with an isolated
    # state file; plants planted through the Program's own force
    # field must be present in the reloaded program.
    from form.open import open_program
    from form import persist_rest
    tmpdir = tempfile.mkdtemp(prefix="growth-persist-")
    owner = "GrowthPersistProbe"
    try:
        path = os.path.join(tmpdir, "state.json")
        prog = open_program(owner)
        prog.forces.growth.plant("Persisted Alpha", unit_id="unit-p1")
        prog.forces.growth.plant("Persisted Alpha", unit_id="unit-p2")
        persist_rest.save(prog, path)
        prog2 = persist_rest.load(owner, path, activate=False)
        got = {p.get("unit_id") for p in prog2.forces.growth.plants}
        check("Program save/load carries uid-keyed plants end to end",
              got == {"unit-p1", "unit-p2"})
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"GROWTH-PERSIST: {sum(1 for _, c in RESULTS if c)}"
          f"/{len(RESULTS)} GREEN")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"GROWTH-PERSIST SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
