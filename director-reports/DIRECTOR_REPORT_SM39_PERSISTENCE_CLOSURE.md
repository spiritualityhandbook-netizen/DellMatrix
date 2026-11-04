# DIRECTOR REPORT — SM-39 Persistence Closure

Circuit: DIR-SUS-WAKE-2026-11-04 Priority 2 · Base: `8391ddc`
Director finding addressed: morning review 2026-11-04 — "ForceField
to_dict() serializes the number of plants, not the individual plant
records; its loader does not restore the unit-ID-keyed plant records.
Identity preservation across save/reload NOT certified."

## Investigation (premise verified, and wider than keyed records)

`form/persist.py:298` saves `program.forces.to_dict()`;
`form/persist_rest.py:466` restores via `ForceField.from_dict(...)`.
`to_dict()` wrote `"growth": {"plants": len(plants), ...}` — a count —
and `from_dict()` restored no plants at all. The gap was therefore
not limited to unit-ID keying: **every** save/reload silently reset
the entire GrowthForce plant list. Persistence of plants is plainly
intended (the field's other scalars — intensity, evolution, breath,
time, weather, gravity wells-as-records — all round-trip; growth
plants were the outlier, and gravity already persists records, not
a count).

Sibling observation (NOT repaired, out of the bounded scope): the
Water force's streams/pools are likewise count-only in `to_dict()`.
Flagged for a future ruling; this circuit touches Growth only.

## Repair (bounded, backward-compatible, same authority)

`form/dell_matrix/forces.py` only — the GrowthForce remains the one
growth-state authority; no second store is introduced.

- `to_dict()`: the growth section keeps the legacy `"plants"` count
  (older readers see the identical shape) and gains
  `"plant_records"`: a deep copy of the full records (id, idea,
  idea_full, unit_id, planter, stage, height, age, history).
- `from_dict()`: when `plant_records` is present, records are
  restored verbatim under `plant()`'s own identity discipline —
  a record needs a non-empty `unit_id`, else its full label
  (`idea_full`, falling back to `idea`); a record with no proven
  identity is skipped; a duplicate identity keeps the FIRST record
  (never a merge, never an overwrite). Legacy count-only payloads
  load with zero plants: a count is never expanded into invented
  records.

## Evidence

- **Failing-first:** new suite `form/growth_persistence_test.py`
  aborts on pristine code at "to_dict carries the full plant
  records" (checks before it pass, including "to_dict keeps the
  legacy plant count").
- **Targeted:** 12/12 GREEN after the repair — two identical-label
  units (unit-aaa/unit-bbb) stay distinct with divergent stages and
  heights after round-trip; unit IDs and plant IDs stable; a
  label-keyed legacy plant round-trips with its full label; a
  legacy count-only payload loads empty; malformed records
  (non-dict, identity-less) are skipped while valid siblings
  restore; a duplicate unit_id keeps the first record; and the
  full Program path (open_program → plant uid-keyed →
  persist_rest.save → persist_rest.load on an isolated state file)
  carries both units end to end.
- **Mutant:** removing the duplicate-identity guard kills exactly
  the malformed/duplicate checks; restored.
- **No regression in the in-memory repair:** SM-39's
  growth_unit_identity suite still 10/10.
- **Regression:** full `form.regress` ×3 sequential at the code
  head — forward GREEN 231/231, `--twice` GREEN (462 checks),
  `--order rev` GREEN 231/231. The new suite is registered in
  `form/regress.py` (canonical count 230 → 231) and exposes the
  required `smoke()` entrypoint.

## Request

This is the independent persistence round-trip evidence the morning
review required before the full T2 identical-label exception lift
can be considered. The lift itself is the Director's ruling; nothing
here claims it.

## Remaining boundaries

- Water streams/pools count-only persistence (above) is untouched.
- Records with a stage outside the canonical set restore verbatim;
  the growth lens and `grow_all` already tolerate that without
  inventing a stage (lens filters to canonical stages; grow_all
  indexes defensively). No stage is fabricated on load.
- Exchange travel of plant records is not addressed (out of scope).
