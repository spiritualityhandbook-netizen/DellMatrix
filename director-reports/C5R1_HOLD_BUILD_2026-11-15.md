# C5R.1 HOLD — Build Packet (2026-11-15)

Slice: C5R.1 HOLD (nothing is ever lost) of the C5 REPLAN
(director-reports/C5_REPLAN_2026-11-15.md, PR #450 merged).
Authorization: Director EXE 2026-11-15 11:27 — bounded C5R.1 build
after preconditions (i) records gates, (ii) source-contract /
storage-migration review, (iii) failing-first persistence tests.
All three preconditions DONE: (i) PR #450 merged 4f6f1bd7;
(ii) review 2026-11-15 16:43 CST; (iii) persistence half 17:13 CST
(10/13, H3/H4/H5 failing first) + read-path half 17:43 CST
(2/7, R3–R7 failing first). C5R.2–C5R.6 NOT authorized, NOT built.

Base: main 052b42f3dab2d54811674e420243fb6d8c0bf0d2 (PR #456 merged).
Branch: uni/c5r1-hold-build. Commits: d364a6f (failing-first
persistence suite), 209bc55 (failing-first read-path suite),
05139a7 (the build).

## What changed (4 product files, +97/−5)

1. form/dell_matrix/nursery.py — the last silent truncations in
   Nursery.add now follow the SYS-C29 family contract (store
   byte-exact OR refuse typed BEFORE any mutation), at the bounds
   the inference dock already enforces by explicit refusal:
   - origin: MAX_ORIGIN_CHARS = 120, NurseryOriginError. (The
     dock's _origin_for segments are built to fit this bound.)
   - detail: MAX_DETAIL_CHARS = 2000, NurseryDetailError
     (dock MAX_DETAIL_CHARS = 2000).
   - goals: MAX_GOALS = 8, MAX_GOAL_CHARS = 200, NurseryGoalsError
     (dock MAX_GOALS / MAX_GOAL_CHARS). Non-string goal entries,
     previously silently dropped, now refuse explicitly; admitted
     goals are stored byte-exact, in order, empties included.
   Caller trace: every production Nursery.add caller passes values
   already inside these bounds (dock validated + stripped;
   ringed_growth/auto_growth short origins, no goals; exchange one
   short goal) — no caller can newly hit a refusal with admitted
   content.
2. form/open.py — Program.all_entities() no longer caps nursery
   ghosts at [:12]: every pending proposal appears (the R42 defect:
   the capped count was presented as the count in the REPL
   `entities` door and look_report()).
3. form/repl.py — subset views state shown/total on their face
   (AC-1.2): `proposals` prints "(showing 20 of N)" when N > 20;
   `rank` prints "(showing 12 of N)" when N > 12. When everything
   is shown the legacy headers are byte-identical (pinned by
   d1_registry_leaf4_test: "Ranked 0/2 proposals:" exact).
4. form/regress.py — both C5R.1 suites registered.

## Acceptance criteria

- AC-1.1 PASS: holding H1/H2 — 1,000 proposals at maximal admitted
  fields stored, reload byte-exact, CROSS_PROCESS digest equal.
- AC-1.2 PASS: readpath R1–R7 — list/ranked APIs agree; both REPL
  subset views state shown/total; ghost counts agree everywhere
  (25/25 probe). Browse leg: no Nursery browse path exists at this
  head; dispositioned C5R.2 scope (AC-2.1), not passed by silence.
- AC-1.3 PASS with classification: no capacity eviction exists;
  add/confirm/reject remove nothing as a side effect (H9). The sole
  removal path, clear_rejected(), is a deliberate human-invoked
  operation returning the exact removed count; per-item receipts
  are C5R.5's contract (AC-5.1/5.3) and were NOT expanded here
  (precondition (ii) finding 4 disposition).
- AC-1.4 PASS: family suites on this head — words 11/11,
  label 15/15, reason 24/24; precuts 9/9.

## Evidence (this head, focused runs)

- nursery_c5r1_holding_test: 13/13 PASS (failing-first was 10/13)
- nursery_c5r1_readpath_test: 7/7 PASS (failing-first was 2/7)
- nursery_confirm_race_test: 57/57 PASS
- d1_registry_leaf4_test: 36/36; polyglot_user_path_test: 37/37;
  dock_proposal_b_test: 17/17
- Mutants killed: (a) all_entities [:12] restored → R5/R6/R7 FAIL;
  (b) origin/goals refusal checks disabled + truncations restored
  → H3/H5 FAIL, suite exit 1. (A truncation-only restore is NOT a
  live mutant: the refusal checks pre-empt it — recorded honestly.)
  All mutants reverted by inverse edit; post-revert diff verified
  to be exactly the build diff; readpath re-run 7/7 after revert.
- Logs: goal hidden_files/c5r1_build/ (holding_build1.log,
  readpath_build1.log, family + neighbor logs, mutant logs).

## Remaining gates (not done by the build cycle)

x3 regression campaign on the slice head (main-session background
chain), exact-head CI, Keeper stamp, Director review, §32 at merge,
post-merge proofs. No completion credit taken; belts unchanged
(PLAN 10 / CODE 4) until merged + credited.

## Anticipated probes

- Why refuse goals non-strings instead of dropping? Silent dropping
  is the defect class being closed; no production caller passes
  non-strings (traced above).
- Empty-string goals are now stored, not dropped: the dock's own
  validator admits them (len ≤ 200); storage is byte-exact or
  refusal — filtering belongs to producers, not the store.

## Questions for the Director

- Q-C5R1.1: none blocking. The clear_rejected receipt upgrade is
  assumed C5R.5 scope per the precondition (ii) disposition —
  flag if it should ride C5R.1 instead.
