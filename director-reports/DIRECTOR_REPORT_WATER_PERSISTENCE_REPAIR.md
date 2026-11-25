# DIRECTOR REPORT — Water Persistence Repair

Circuit: ForceField sibling repair, bounded Water scope
(Director disposition 2026-11-04, Mode D review: one bounded
Water persistence repair authorized after TD-1-R1; no combined
repair authorized). Gravity wells and evolution scalars are NOT
in this circuit.
Base: main 6f1f651 (PR #283). Branch: uni/water-persistence-repair.

## The defect (as corrected and confirmed)

ForceField.to_dict() wrote only the stream/pool COUNTS for
Water; from_dict() restored nothing. Every save/reload silently
emptied the water, and the next flow() then re-minted `stream-1`,
colliding with the pre-save identity. Same defect class SM-39
closed for GrowthForce plants, in the same single authority
(`form/dell_matrix/forces.py`).

## What changed (forces.py only, plus one suite + registration)

- to_dict: legacy counts retained for older readers; the full
  stream records ride alongside as `stream_records` (deep copy),
  and pool membership rides as `pool_ids` — stream-id references,
  because pools ALIAS stream objects in memory (settle() appends
  the same dict); serializing pools as records would create
  divergent duplicates on restore.
- from_dict: records restore verbatim under the SM-39 identity
  discipline — a record needs a non-empty string `id`, malformed
  records are skipped, a duplicate id keeps the FIRST record.
  Pools are rebuilt by re-linking to the restored stream objects
  by id (a pool id with no restored stream is skipped, never
  fabricated; without an explicit `pool_ids`, membership derives
  from the restored records' own `form == "pool"` — still the
  same objects). Legacy count-only payloads load empty; a count
  is never expanded into invented records.
- Identity after reload: `WaterForce._next_id` mints the
  historical len-based id but skips any id already present, so
  an identifier is never reused while its record lives (dense
  case ids are unchanged; the gap case is suite-pinned).
- A stream's `idea` is the 80-char value flow() itself stored;
  it restores verbatim. No fuller label exists and none is
  invented (contrast Growth, which carries idea_full).

## Evidence

- Failing-first: on pristine code the suite aborts at
  "to_dict carries the full stream records" (the SM-39-analogous
  point).
- Suite `form/water_persistence_test.py`: **14/14 GREEN**
  (registered; canonical count 234). Covers: river parents/
  volumes/forms round-trip; pool membership; pool aliasing by
  object identity after load; water scalars; first flow/merge
  after reload mint non-colliding ids; legacy count-only loads
  empty; malformed/duplicate discipline (first wins); pool
  re-link skipping missing ids; minting across an id gap; full
  Program save/load path end to end.
- Mutants (defect-restoring, each killed by exactly its target):
  restore block disabled → round-trip check fails; pools restored
  as independent copies → aliasing check fails; collision-skip
  removed from _next_id → gap check fails. All reverted by
  inverse edit; tree clean.
- Growth persistence suite: 12/12 GREEN unchanged.
- Full regression x3 sequential: **234/234 GREEN in all legs**
  (fwd, twice pass1+pass2, rev).
- Exact-head CI and fresh-clone verification: reported with the
  closure identifiers on the PR.

Test realism: INTEGRATION (in-memory ForceField round-trip plus
the real persist_rest Program save/load boundary on an isolated
state file).

## Anticipated probes

1. River parents pointing at streams a malformed payload dropped:
   the river record restores with its parents as stored — no
   invention, no deletion; disclosed in the suite ground rules.
2. Consumers (status counts in open.py/repl.py/neuroevo) are
   count-based today and unchanged; tick() now operates over
   restored records, which is the intended consequence.
3. resonance_log remains session-only (never serialized for any
   force) — unchanged by this circuit; whether that is intended
   stays an open question, not a claim.

## Questions for the Director

1. Gravity wells next, per the preferred design already ruled
   (restore the serialized records as snapshots, then normal
   score-based recomputation on ticks), with evolution scalar
   restoration and its regression tests in the same circuit —
   or scalars first as their own bounded step?
