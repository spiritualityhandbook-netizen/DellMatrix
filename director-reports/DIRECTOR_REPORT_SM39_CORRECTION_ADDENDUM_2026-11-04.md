# CORRECTION ADDENDUM — SM-39 Persistence Closure Report

Date: 2026-11-04 · Corrects: DIRECTOR_REPORT_SM39_PERSISTENCE_CLOSURE.md
(precedent: the step-13 checksum reconciliation — a dated
correction record; the submitted report is NOT rewritten.)

## The false sentence

The SM-39 report's investigation section states:

> "Persistence of plants is plainly intended (the field's other
> scalars — intensity, evolution, breath, time, weather, gravity
> wells-as-records — all round-trip; growth plants were the
> outlier, and gravity already persists records, not a count)."

**"Gravity wells-as-records all round-trip" is FALSE**, and the
evolution claim is false for four of the six forces. Verified by
direct round-trip probe (ForceField in-memory, first-hand,
2026-11-04, code at main 24099af lineage — `forces.py` unchanged
since):

| Field | Serialized by to_dict | Restored by from_dict |
| --- | --- | --- |
| gravity wells | FULL records (2 wells in payload) | **NO — []** (from_dict never reads the gravity/space sections) |
| gravity evolution_level | yes (set 4.5) | **NO — resets to 1.0** |
| space evolution_level | yes (set 1.5) | **NO — resets to 1.0** |
| time evolution_level | yes (set 3.5) | **NO — resets to 1.0** (tick survives) |
| weather evolution_level | yes (set 2.5) | **NO — resets to 1.0** (condition survives) |
| water streams / pools | count only (3 / 1) | **NO — []** (already disclosed as a sibling observation in the original report) |
| growth plants (the SM-39 repair) | count + plant_records | YES — round-trip re-verified in the same probe |

Additional Water consequence, probe-verified: after the lossy
reload, the next `flow()` mints `stream-1` again, colliding with
the pre-save stream-1 identity.

## Scope of the correction

- The SM-39 REPAIR and its evidence are UNAFFECTED: plant records
  round-trip (suite 12/12, regress 231/231 ×3, re-verified above).
  What dies is only the comparative supporting premise — plants
  were NOT the lone outlier, and gravity does NOT already persist
  records end-to-end (it serializes them and discards them on
  load).
- This addendum exists so the Director's pending separate T2
  ruling does not rest on the false premise. The T2 exception
  status is unchanged by this addendum.

## Repair posture (NOT authorized, NOT implemented)

The sibling losses are mapped in Uni's working papers with a
repair shape mirroring SM-39 (records alongside legacy counts,
identity-disciplined restore, legacy payloads load empty) and two
honest options for gravity wells (restore them, or stop emitting
what load ignores — wells are derived state, recomputed from node
scores). Water additionally requires pool/stream re-linking on
restore (pools alias stream objects). Uni recommends restoring
the four evolution scalars with whichever wells option the
Director chooses. Implementation awaits a Director ruling.
