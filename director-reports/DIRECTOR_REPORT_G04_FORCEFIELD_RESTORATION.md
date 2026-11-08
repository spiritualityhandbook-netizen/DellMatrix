# DIRECTOR REPORT — G-04: ForceField Gravity Wells + Evolution-Scalar Restoration

Circuit: G-04 (Master Objective Register) — "Gravity wells +
evolution-scalar restoration (ForceField): wells serialize
but never restore; gravity/space/time/weather evolution_level
resets to 1.0." Executed as a FIX circuit under Sleep
Protocol v2 / Ace FIX-FIRST authority. NOT a combined
ForceField repair: scope is exactly the two named losses.

Branch: uni/g04-forcefield-restoration, base main
28719de02e3c78807aa4d6329d57a5e4881d5beb (PR #316 merge).
Repair SHA: 359ca76265e7a4a7aafa97dc5307a74e64295809.
Defect ID: DD-11.

## 1. Defect (FACT, failing-first)

ForceField.to_dict (form/dell_matrix/forces.py) serializes
the gravity wells and the gravity/space/time/weather
evolution_levels into the persisted "forces" envelope
section. ForceField.from_dict — the restore used by the
program load path (form/persist_rest.py:591) — never read
them back. Every load therefore silently reset the wells to
[] and all four scalars to 1.0 while the file on disk kept
the true values: stored state that could not influence the
loaded program, the inverse of the SM-39 Water/Growth
losses, whose restores are certified and serve here as the
pattern and the controls.

Failing-first, two instruments at unrepaired main:
- Probe (hidden_files/g04_probe.py): serialized wells
  [{a,Alpha,4.0},{b,Beta,3.0},{c,Gamma,2.0}] and levels
  gravity 1.35 / space 2.5 / time 0.75 / weather 3.25
  restore as wells [] and 1.0/1.0/1.0/1.0; controls water
  1.5 and growth 1.6 restore correctly.
- Dedicated suite at base: 8/23 PASS — every defect-family
  check fails (unit, evolve-path, public save/load,
  status(), second-roundtrip stability); all controls pass.

## 2. Repair

from_dict gains the missing restores, mirroring the
certified Water/Growth/Breath discipline in the same
function:

- Gravity wells restore as the saved SNAPSHOT — the
  register's recorded Director design for this item
  ("restore wells as snapshots, recompute on ticks"):
  deep-copied verbatim; only dict records restore;
  malformed entries are skipped, never fabricated. The
  next tick recomputes wells from live nodes, exactly as
  tick() already does when gravity is active (verified by
  the suite's TICK check).
- gravity/space/time/weather evolution_level restore with
  the same unguarded float() discipline the certified
  restores use; a legacy payload without the sections
  restores defaults without error.

Nothing else in the function changes; gravity intensity is
NOT serialized by to_dict and is therefore out of scope
(nothing exists to restore).

## 3. Verification

- Suite form/forcefield_gravity_evolution_test.py (23
  checks; registered in form/regress.py — canonical count
  247): unit roundtrip incl. snapshot alias-freedom both
  directions, malformed-entry skip, non-list guard, legacy
  defaults; PUBLIC_ENTRY_PATH save->load through persist
  (wells, levels, status()); tick-recompute pairing;
  second-roundtrip stability. 23/23 after repair.
- Controls: water_persistence_test 14/14,
  growth_persistence_test 12/12 — unchanged, green.
- Mutants (inverse-reverted, tree clean, suite back to
  23/23): M-G1 wells restore disabled -> 17/23, exactly the
  six wells-dependent checks fail. M-G2 all four scalar
  restores pinned to 1.0 -> 15/23, exactly the eight
  level-dependent checks fail.
- Regression at the repair SHA: TERMINAL GREEN 247/247 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 23/23)
- Fresh clone from GitHub at the repair SHA: fresh clone from GitHub at 359ca76: suite 23/23, water_persistence 14/14, growth_persistence 12/12, tree clean
- CI at the final PR head: ALL TERMINAL PASS at final head 7161281 — Python package run 42319878197 (3.10 + 3.11), Studio Browser Acceptance run 42319878212, Form smoke run 42319878231 (PASS, 16m24s). PR #317 MERGED 2026-11-06: merge commit 6b0454fc8954971739c3f83bfb6bcb88562d9301, tree 37eab0a206ecf4d0f12f287e54e141f84d02bce0; merged-main CI terminal SUCCESS (Python package 42321548225, Form smoke 42321548267). Director verdict (2026-11-06 19:33 CST, archived in the 72-13 circuit records): ALL_AI_CONFIRMATION_PASS bounded to the DD-11 restoration; G-04 remains COMPLETED; Q-G04.2 intensity asymmetry designated a separate inventory/proposal item, no production change until separately reviewed.

## 4. Records carried in this PR

- This report + INDEX row.
- Register: G-04 row closed (the row's scope is exactly
  the two named losses; both repaired and proven);
  DD-11 recorded FIXED.
- DIRECTOR_REPORT_72_35_ATOMIC_WRITE_BOUNDARIES.md: the
  CI/merge receipt placeholder completed (final-head CI
  all terminal PASS — package run 42313372252, browser-
  acceptance 42313372226, Form smoke 42313372264 PASS
  19m6s; PR #316 merged 28719de02e3c78807aa4d6329d57a5e4881
  d5beb, tree 3e10b90512902b72892a0767aec1d46ff168ebf5;
  merged-main CI terminal SUCCESS (Python package run 42315407459, Form smoke run 42315407553)).

## Anticipated probes

- "Why unguarded float()? A corrupt evolution_level now
  fails a load that previously ignored the section." —
  Deliberate consistency: the certified Water/Growth/
  Breath restores in the same function use the identical
  discipline, and the loader's standing posture is
  fail-closed on unproven state. Singling gravity out for
  leniency would create two disciplines in one restore.
- "Could restoring stale wells mislead? They are derived
  from node scores that may have changed." — That is
  precisely the snapshot semantics the register records as
  your design: the snapshot is the state as of the save;
  the next tick with live nodes recomputes. Between load
  and first tick, status() now reports the saved truth
  instead of an empty field that contradicts the file.
- "Is anything else in to_dict unrestored?" — Checked
  field by field against from_dict in this circuit: after
  this repair every serialized member restores (active,
  water incl. records/pools, growth incl. records, breath,
  gravity incl. wells, time incl. tick, weather incl.
  condition, space). Gravity intensity is never
  serialized, so there is nothing to restore; whether it
  SHOULD serialize is a separate question (Q-G04.2).

## Questions for the Director

- Q-G04.1: Confirm G-04 closes on this evidence (the row
  moves to COMPLETED in this PR's register update), or
  state what further proof you require.
- Q-G04.2: ForceField.to_dict does not serialize gravity
  (or breath/time/weather/space) intensity; only water
  and growth carry it. Should intensity persistence be
  uniform across forces (a new, separate item), or is the
  current asymmetry intended?
