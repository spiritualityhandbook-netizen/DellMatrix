# DIRECTOR REPORT — 72-60: Four-Way Equivalence Proven — REPL Leg Closes the Register Gap (closure proposed)

Circuit: 72-60 (Master Objective Register) —
"Prove identical executable semantics across
GUI/API/REPL/Python (P1/E) (= SM-52)." The
register's own remaining gap was: "REPL leg of
the four-way equivalence" (gui_api_test already
proved GUI/API through the public paths).

Executed as an EVIDENCE circuit under Sleep
Protocol v2 / completion-first reset (Director
ruling 2026-11-07 21:10 CST: finish the nearest
safely closable objective). Branch:
uni/72-60-four-way-equivalence, base main
16c50bf1e4feb73b01209b33698f8397a4463b31
(PR #328 merge, 72-40/DD-13). Suite head:
88bef39325d1b8e0d43bd5783908d76475ff74f9.
Records ride on top, records-only. NO production
code changed. NO defect found.

## 1. Closure card

- Acceptance criterion (register): prove the
  REPL leg of the four-way equivalence — the
  only remaining action on the row.
- Evidence: sections 2-3 below (probe + 14-check
  suite + regress x3 terminal GREEN + fresh-clone
  re-verification).
- Single remaining gap: NONE within the row's
  scope. The one observed asymmetry (last_result
  not surviving save/load) is a round-trip
  property common to ALL surfaces, not a surface
  divergence — see section 2; its durability
  question belongs to the persistence objectives
  and is posed as Q-72-60.2, not broadened here.
- Verdict proposed: PASS — 72-60 COMPLETED,
  proposed in this PR's register update FOR
  DIRECTOR VERIFICATION (Q-72-60.1). Strict
  completed moves 17/72 -> 18/72 only on your
  confirmation; until then the on-main scoreboard
  stands at 17/72, OCI 53.6%.

## 2. Findings (probe, terminal, fresh clone at base)

Representative seed set (7): Create, Set, Get,
Nurture labelled, Nurture bare (failure honesty),
Create>>reserved-151 chain (skipped honesty),
Set>>Set chain (state accumulation).

- Python API (open_program + execute_seed) vs
  GUI/API (Studio server /api/execute, real HTTP):
  normalized receipts IDENTICAL for all 7 seeds;
  final snapshots IDENTICAL (store {tempo:99,
  mode:probe}, nursery_pending 1, plane labels
  [EqAlpha, EqBeta, Welcome]).
- REPL leg (REAL_USER_PATH, literal
  `python3 -m form.repl --owner ...` subprocess,
  piped seeds + "save" + "quit", rc=0):
  stdout-visible effect for every seed matches
  the Python/GUI outcome; post-save reload
  snapshot (store, nursery_pending, plane labels)
  IDENTICAL.
- Apparent asymmetry RESOLVED as not a REPL
  divergence: the REPL save+reload snapshot has
  last_result={} while in-memory Python/GUI
  snapshots carry the Get receipt. A second probe
  shows the Python leg loses last_result
  identically through persist save/load AND
  through the Dell-10 Keep save path. last_result
  non-persistence is a save/load round-trip
  property common to all surfaces (cf.
  persist.CORE_II_DURABLE), NOT a 72-60 surface
  divergence. Recorded as an observed common
  property; not silently broadened into 72-60.

## 3. Verification

- Suite form/four_way_equivalence_test.py
  (14 checks, smoke() -> bool per the harness
  contract; registered in form/regress.py):
  14/14 PASS rc=0 at the suite head. Legs:
  Python execute_seed; GUI/API real Studio HTTP;
  REPL literal subprocess. Like-for-like law:
  receipts compared Python vs GUI directly; REPL
  compared on stdout-visible per-seed effects and
  on the final snapshot after save+reload against
  Python/GUI legs ALSO put through save+reload
  (never in-memory vs reloaded). Owners synthetic/
  unique; cleanup uses canonical state paths and
  fails loudly on cleanup error.
- Regression x3 TERMINAL GREEN at the suite head
  (main-session chain, logs
  hidden_files/72-60_logs/run1/): leg1 259/259
  GREEN (fwd), leg2 259/259 x2 GREEN (fwd, twice),
  leg3 259/259 GREEN (rev); LEG1_RC=LEG2_RC=
  LEG3_RC=0, CHAIN_DONE 2026-11-08T08:47:13Z.
- Independent re-verification (2026-11-08 03:01
  CST cycle, in the branch clone at 88bef39):
  suite 14/14 PASS rc=0.
- CI at the final PR head: __FINAL_CI__

## 4. Records carried in this PR

- This report + INDEX row.
- Register: 72-60 row -> COMPLETED (proposed for
  Director verification, Q-72-60.1), evidence cell
  records the REPL-leg proof. No other row changed.
- Reconciliation publication (per your 2026-11-07
  22:36 CST ruling, item 2 — responded via GitHub
  reports/INDEX, never via Ace relay): the on-main
  register was reconciled against landed evidence
  this cycle — OCI on-main (16c50bf) = 53.6%
  (17 completed, 49 partial, 3 investigation,
  2 open, 1 blocked; strict 17/72). PR #308's
  branch register is STALE (52.6%, strict 16/72;
  it predates the 72-31/72-36/72-40 register
  updates) and is not the leading in-flight
  reading. With this PR's proposed 72-60 closure
  the in-flight register reads 54.4% (strict
  18/72) — a PROPOSAL until you verify it.
- #328 merged-main receipt (per the same ruling):
  main-push CI at merge commit
  16c50bf1e4feb73b01209b33698f8397a4463b31
  TERMINAL SUCCESS — Python package run
  42446903961 SUCCESS; Form smoke run 42446903962
  SUCCESS (each verified individually via gh).

## 5. Anticipated probes

- "Is the REPL compared like-for-like?" Yes: the
  REPL leg is compared on visible effects plus a
  save+reload snapshot against Python/GUI legs put
  through the same save+reload — never in-memory
  vs reloaded.
- "Does COMPLETED claim more than the row?" No:
  the row's scope is the four-way equivalence;
  GUI/API was already proven on file; this circuit
  proves the REPL leg, the row's only named gap.
- "What about last_result durability?" Observed,
  common to all surfaces, explicitly out of scope
  here; Q-72-60.2 asks where it belongs.

## 6. Questions for the Director

- Q-72-60.1: Confirm 72-60 COMPLETED on this
  evidence (strict 17/72 -> 18/72), or name the
  remaining gap.
- Q-72-60.2: last_result non-persistence across
  save/load (all surfaces) — assign to an existing
  persistence objective, or record as accepted
  behavior?

## 7. Ask

Bounded ruling on this PR at its final head.
Merge executes ONLY from the main session under
the post-#307 containment, after a section-32
re-check with any new Director mail body read,
and only on all required checks terminal PASS at
the exact head (disagreement-veto rule applied).
