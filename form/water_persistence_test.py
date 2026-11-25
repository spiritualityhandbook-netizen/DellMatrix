"""Water persistence repair — ForceField stream/pool round-trip.

Director disposition 2026-11-04 (Mode D review): authorize ONE
bounded Water persistence repair after TD-1-R1 — preserve
stream/pool relationships and ensure identifiers are not reused
after reload. This is the same defect class SM-39 closed for
GrowthForce plants: ForceField.to_dict() wrote only the stream
and pool COUNTS for Water, and from_dict() restored nothing, so
every save/reload silently emptied the water — and the next
flow() then re-minted stream-1, colliding with the pre-save
identity.

Contract pinned here (mirrors the SM-39 plant discipline in the
same single authority, form/dell_matrix/forces.py):

  * to_dict keeps the legacy counts and adds the full stream
    records plus the pool membership as stream ids (pools ALIAS
    stream objects in memory — settle() appends the same dict —
    so pools serialize as references, never as second copies).
  * from_dict restores records verbatim under identity
    discipline: a record needs a non-empty string id; malformed
    records are skipped; a duplicate id keeps the FIRST record.
    Pools are rebuilt by re-linking to the restored stream
    objects by id, so the in-memory aliasing is re-established.
    Legacy count-only payloads load empty — a count is NEVER
    expanded into invented records.
  * A stream record's `idea` is the 80-char-truncated value
    flow() itself stored; it is restored verbatim (there is no
    fuller label to recover, and none is invented).
  * After a restored reload, freshly minted stream/river ids
    never collide with restored ids.

Run: python3 -m form.water_persistence_test
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


def _scenario(ff):
    """Two streams, one merged river, the river settled to a pool."""
    ff.water.flow("Alpha idea")
    ff.water.flow("Beta idea")
    river = ff.water.merge_last_two()
    ff.water.settle()
    return river


def run_all():
    from form.dell_matrix.forces import ForceField

    ff = ForceField()
    river = _scenario(ff)
    check("scenario builds a river with both parents",
          river is not None and river["id"] == "river-3"
          and river["parents"] == ["stream-1", "stream-2"]
          and river["volume"] == 2.0)

    data = ff.to_dict()
    w = data["water"]
    check("to_dict carries the full stream records",
          isinstance(w.get("stream_records"), list)
          and len(w["stream_records"]) == 3
          and w.get("streams") == 3 and w.get("pools") == 1)
    check("to_dict carries pool membership as stream ids",
          w.get("pool_ids") == ["river-3"])

    ff2 = ForceField.from_dict(copy.deepcopy(data))
    ids = [s["id"] for s in ff2.water.streams]
    check("streams round-trip with ids, forms, volumes, parents",
          ids == ["stream-1", "stream-2", "river-3"]
          and ff2.water.streams[2]["form"] == "pool"
          and ff2.water.streams[2]["parents"] == ["stream-1",
                                                  "stream-2"]
          and ff2.water.streams[2]["volume"] == 2.0
          and ff2.water.streams[0]["idea"] == "Alpha idea")
    check("pool membership round-trips",
          [s["id"] for s in ff2.water.pools] == ["river-3"])
    check("pool aliasing is re-established (same object)",
          ff2.water.pools[0] is ff2.water.streams[2])
    check("water scalars still round-trip",
          ff2.water.intensity == ff.water.intensity
          and ff2.water.evolution_level == ff.water.evolution_level)

    fresh = ff2.water.flow("Gamma idea")
    check("first flow after reload mints a non-colliding id",
          fresh["id"] not in ids and fresh["id"] == "stream-4")
    river2 = ff2.water.merge_last_two()
    check("first merge after reload mints a non-colliding id",
          river2 is not None and river2["id"] not in ids + ["stream-4"])

    legacy = {"water": {"streams": 3, "pools": 1, "intensity": 0.7,
                        "evolution_level": 1.0}}
    ff3 = ForceField.from_dict(copy.deepcopy(legacy))
    check("legacy count-only payload loads honestly empty",
          ff3.water.streams == [] and ff3.water.pools == [])

    messy = {"water": {
        "stream_records": [
            {"id": "stream-1", "idea": "One", "form": "stream",
             "volume": 1.0},
            "not-a-dict",
            {"idea": "no id at all", "form": "stream"},
            {"id": "", "idea": "empty id", "form": "stream"},
            {"id": "stream-1", "idea": "DUPLICATE", "form": "stream",
             "volume": 9.0},
            {"id": "stream-2", "idea": "Two", "form": "pool",
             "volume": 1.0},
        ],
        "pool_ids": ["stream-2", "stream-missing"],
    }}
    ff4 = ForceField.from_dict(copy.deepcopy(messy))
    check("malformed skipped, duplicate id keeps FIRST, "
          "valid siblings restore",
          [s["id"] for s in ff4.water.streams] == ["stream-1",
                                                   "stream-2"]
          and ff4.water.streams[0]["idea"] == "One")
    check("pool re-link skips ids with no restored stream",
          [s["id"] for s in ff4.water.pools] == ["stream-2"]
          and ff4.water.pools[0] is ff4.water.streams[1])

    gapped = {"water": {"stream_records": [
        {"id": "stream-1", "idea": "One", "form": "stream",
         "volume": 1.0},
        {"id": "stream-3", "idea": "Three", "form": "stream",
         "volume": 1.0},
    ]}}
    ff5 = ForceField.from_dict(copy.deepcopy(gapped))
    minted = ff5.water.flow("After the gap")
    check("minting never reuses a live id, even across id gaps",
          minted["id"] not in ("stream-1", "stream-3"))

    # Full Program path: persist_rest save -> load on an isolated
    # state file — the records must survive the real boundary.
    from form.open import open_program
    from form import persist_rest
    tmpdir = tempfile.mkdtemp(prefix="water-persist-")
    owner = "WaterPersistProbe"
    try:
        path = os.path.join(tmpdir, "state.json")
        prog = open_program(owner)
        _scenario(prog.forces)
        persist_rest.save(prog, path)
        prog2 = persist_rest.load(owner, path, activate=False)
        got = [s["id"] for s in prog2.forces.water.streams]
        check("Program save/load carries water records end to end",
              got == ["stream-1", "stream-2", "river-3"]
              and [s["id"] for s in prog2.forces.water.pools]
              == ["river-3"]
              and prog2.forces.water.pools[0]
              is prog2.forces.water.streams[2])
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"WATER: {sum(1 for _, c in RESULTS if c)}/{len(RESULTS)} GREEN")


def smoke() -> bool:
    try:
        run_all()
        return True
    except Exception as e:
        print(f"WATER SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
    sys.exit(0)
