#!/usr/bin/env python3
"""G-04 — ForceField gravity wells + evolution-scalar
restoration.

Defect (register G-04; SM-39 sibling losses beyond the
certified Water repair): ForceField.to_dict serializes the
gravity wells and the gravity/space/time/weather
evolution_levels, but ForceField.from_dict never restored
them — every load silently reset the wells to [] and all
four scalars to 1.0, while the file on disk kept the true
values. The SM-39 report once claimed these round-tripped;
that claim was corrected by dated addendum (2026-11-04).

Repair (Director's preferred design, per the register):
restore the wells as the saved SNAPSHOT (deep-copied,
verbatim); the next tick recomputes wells from live nodes,
exactly as tick() already does. Evolution levels restore
with the same unguarded float() discipline the certified
Water/Growth/Breath restores use. Record discipline mirrors
those repairs: only dict well records restore; anything
else is skipped, never fabricated; a legacy payload without
the sections restores defaults without error.

Existing coverage (NOT duplicated): water_persistence_test
and growth_persistence_test pin the Water/Growth record
restores; they serve here as controls.

Labels: UNIT (dict roundtrip) + PUBLIC_ENTRY_PATH (persist
save/load) + INTEGRATION (tick recompute). State hygiene:
uuid-unique owners; exact-pattern cleanup; cleanup failures
reported, never swallowed.
"""
from __future__ import annotations

import copy
import os
import sys
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []

from form.dell_matrix.forces import ForceField  # noqa: E402

RUN = uuid.uuid4().hex[:8]
NODES = [{"id": "a", "label": "Alpha", "score": 3.0},
         {"id": "b", "label": "Beta", "score": 2.0},
         {"id": "c", "label": "Gamma", "score": 1.0}]
LEVELS = {"gravity": 1.35, "space": 2.5, "time": 0.75,
          "weather": 3.25}


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _field():
    ff = ForceField()
    ff.gravity.set_wells_from_scores(NODES)
    ff.gravity.evolution_level = LEVELS["gravity"]
    ff.space.evolution_level = LEVELS["space"]
    ff.time.evolution_level = LEVELS["time"]
    ff.weather.evolution_level = LEVELS["weather"]
    ff.water.evolution_level = 1.5
    ff.growth.evolution_level = 1.6
    return ff


def _levels(ff):
    return {"gravity": ff.gravity.evolution_level,
            "space": ff.space.evolution_level,
            "time": ff.time.evolution_level,
            "weather": ff.weather.evolution_level}


def main():
    # -- unit roundtrip: the defect family
    ff = _field()
    data = ff.to_dict()
    rt = ForceField.from_dict(data)
    expect_wells = [{"id": "a", "label": "Alpha", "mass": 4.0},
                    {"id": "b", "label": "Beta", "mass": 3.0},
                    {"id": "c", "label": "Gamma", "mass": 2.0}]
    check("WELLS.snapshot_restored", rt.gravity.wells == expect_wells,
          str(rt.gravity.wells))
    check("LEVELS.all_four_restored", _levels(rt) == LEVELS,
          str(_levels(rt)))
    for name in ("gravity", "space", "time", "weather"):
        check(f"LEVELS.{name}", _levels(rt)[name] == LEVELS[name],
              str(_levels(rt)[name]))
    check("CONTROL.water_level_kept", rt.water.evolution_level == 1.5)
    check("CONTROL.growth_level_kept",
          rt.growth.evolution_level == 1.6)
    check("CONTROL.time_tick_kept", isinstance(rt.time.tick, int))
    check("CONTROL.weather_condition_kept",
          rt.weather.condition == ff.weather.condition)

    # -- snapshot is a copy, not an alias (both directions)
    data2 = _field().to_dict()
    rt2 = ForceField.from_dict(data2)
    data2["gravity"]["wells"][0]["mass"] = 999.0
    check("WELLS.no_alias_from_payload",
          len(rt2.gravity.wells) == 3
          and rt2.gravity.wells[0]["mass"] == 4.0,
          str(rt2.gravity.wells))
    if rt2.gravity.wells:
        rt2.gravity.wells[0]["mass"] = 777.0
    rt3 = ForceField.from_dict(_field().to_dict())
    check("WELLS.no_alias_between_restores",
          len(rt3.gravity.wells) == 3
          and rt3.gravity.wells[0]["mass"] == 4.0,
          str(rt3.gravity.wells))

    # -- malformed discipline: skip, never fabricate
    data3 = _field().to_dict()
    data3["gravity"]["wells"] = [
        {"id": "a", "label": "Alpha", "mass": 4.0},
        "not-a-record", 42, None,
        {"id": "b", "label": "Beta", "mass": 3.0}]
    rt4 = ForceField.from_dict(data3)
    check("WELLS.malformed_entries_skipped",
          [w["id"] for w in rt4.gravity.wells] == ["a", "b"],
          str(rt4.gravity.wells))
    data4 = _field().to_dict()
    data4["gravity"]["wells"] = {"id": "a"}
    rt5 = ForceField.from_dict(data4)
    check("WELLS.non_list_stays_empty", rt5.gravity.wells == [],
          str(rt5.gravity.wells))

    # -- legacy payload: sections absent -> defaults, no error
    legacy = {"active": [], "water": {}, "growth": {},
              "breath": {}}
    rt6 = ForceField.from_dict(legacy)
    check("LEGACY.defaults_restored",
          rt6.gravity.wells == [] and _levels(rt6) == {
              "gravity": 1.0, "space": 1.0, "time": 1.0,
              "weather": 1.0},
          str(_levels(rt6)))
    rt7 = ForceField.from_dict(None)
    check("LEGACY.none_payload_defaults",
          rt7.gravity.wells == []
          and rt7.space.evolution_level == 1.0)

    # -- evolved via the producer API also restores
    ff8 = ForceField()
    ff8.space.evolve(0.5)
    ff8.time.evolve(0.25)
    rt8 = ForceField.from_dict(ff8.to_dict())
    check("LEVELS.evolve_path_restored",
          rt8.space.evolution_level == 1.5
          and rt8.time.evolution_level == 1.25,
          f"{rt8.space.evolution_level} {rt8.time.evolution_level}")

    # -- public path: save -> load through persist
    from form.open import open_program
    from form.persist import save
    from form.persist_rest import load
    owner = f"T7G04{RUN}"
    p = open_program(owner)
    p.forces.gravity.set_wells_from_scores(NODES)
    p.forces.gravity.evolution_level = LEVELS["gravity"]
    p.forces.space.evolution_level = LEVELS["space"]
    p.forces.time.evolution_level = LEVELS["time"]
    p.forces.weather.evolution_level = LEVELS["weather"]
    save(p)
    q = load(owner, activate=False)
    check("PUBLIC.wells_restored",
          q.forces.gravity.wells == expect_wells,
          str(q.forces.gravity.wells))
    check("PUBLIC.levels_restored",
          _levels(q.forces) == LEVELS, str(_levels(q.forces)))
    check("PUBLIC.status_shows_wells",
          q.forces.status()["gravity_wells"] == expect_wells)

    # -- tick recomputes from live nodes (design pairing);
    # gravity ticks only when active (the default active set is
    # growth/water/breath), so activate it first, as a program
    # using gravity would
    q.forces.activate("gravity")
    q.forces.tick([{"id": "z", "label": "Zeta", "score": 9.0}],
                  owner=owner)
    check("TICK.recomputes_wells",
          [w["id"] for w in q.forces.gravity.wells] == ["z"],
          str(q.forces.gravity.wells))

    # -- roundtrip stability: load -> save -> load, no drift
    save(q)
    r = load(owner, activate=False)
    check("STABILITY.second_roundtrip_levels",
          _levels(r.forces) == LEVELS, str(_levels(r.forces)))

    # -- cleanup (exact patterns for this owner)
    from form.persist import _STATE_DIR, _safe_owner
    from form.dell_matrix.nursery import owner_nursery_path
    state = Path(_STATE_DIR)
    safe = _safe_owner(owner)
    cands = [state / f"program_{safe}.json",
             Path(owner_nursery_path(owner))]
    cands += list(state.glob(f"*{safe}*"))
    for pth in set(cands):
        try:
            if pth.is_dir():
                import shutil
                shutil.rmtree(pth)
            elif pth.exists():
                pth.unlink()
        except OSError as exc:
            _CLEANUP_ERRORS.append(f"{pth}: {exc}")
    check("cleanup.no_errors", not _CLEANUP_ERRORS,
          str(_CLEANUP_ERRORS))

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"forcefield_gravity_evolution_test: "
          f"{passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
