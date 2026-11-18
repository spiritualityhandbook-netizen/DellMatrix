# R19 — Cycle Count Truthfulness Repair (2026-11-18)

**Circuit:** R19 (Limits Census row 19; Limits Verification Wave 4
classification: value faithful, visibility DEFECT-CONFIRMED).
**Authority:** Director ruling 2026-11-18 (R19 binding contract,
published on GitHub): Dell 06 Cycle, including its flow-program
route, uses the same ruled 1..5 execution bound as the other
Cycle/Loop paths; the unruled flow ceiling of 99 is removed; the
receipt must explicitly show requested / executed / remaining
without implying the full request succeeded; invalid counts refuse
without executing growth; automatic continuation beyond five is
NOT authorized.
**Base:** main `3a8b1412e026cfdc646bf66793749212ddb672d8`.

## Defect (reproduced on base by the R19 census probe, 11/11)

1. `form/mandell/executor_leaf.py` Cycle arm clamped the parsed
   count and printed ONLY the clamped value (`Cycle x5` for a
   request of 20); the request was lost. `note_seed` likewise
   recorded only the clamped value (unchanged by this repair: it
   records the seed as executed; the receipt is the disclosure
   surface — flagged here for the record).
2. `form/mandell/semantic_router.py` `_seed_cycle` clamped inside
   seed construction, so no downstream receipt could name the loss.
   The Loop seed builder (`_seed_grow`) applies no upper clamp —
   the in-codebase precedent this repair follows.
3. `form/mandell/translate.py` cycle arm clamped inside Intent
   construction the same way (`cycle 20` -> count 5).
4. `form/mandell/flow_executor.py` `_args_from_label` applied an
   UNRULED 99 ceiling: flow step record (count 20) and execution
   (clamped to 5 downstream) disagreed, undisclosed.

## Repair (this PR)

- **executor_leaf Cycle arm:** keep `requested`, clamp only the
  executed count, append a truthful count line mirroring the Loop
  B2 pattern — `Cycle: requested 20, executed 5, remaining 15.
  (clamped to 1..5)`; `requested 0, executed 1. (clamped to 1..5)`
  for under-range; unadorned `requested 3, executed 3.` in range.
  DIR-F13 unparseable-label default of 1 preserved (pinned sibling
  semantics, not changed). The `Cycle x{executed}:` growth line is
  unchanged.
- **semantic_router._seed_cycle / translate cycle arm:** early
  upper clamp removed (floor kept); the requested count travels in
  the Intent/seed; the leaf is the single clamp + report authority.
- **flow_executor._args_from_label:** the 99 ceiling removed; the
  requested count travels as-is and the leaf receipt reconciles
  with the flow step record.
- **chain_exec.py:480:** verified consistent (Loop-body repetition
  re-derives from the effective label and clamps identically); no
  change.

## Evidence

- Failing-first suite `form/r19_cycle_receipt_test.py` (registered
  in `form/regress.py`): 21 checks — seed Cycle at 0/1/5/6/20/100,
  in-range exactness, DIR-F13 default guard, Loop receipt guard,
  router seeds, translate Intent + end-to-end, flow args +
  reconciliation end-to-end, chain containing a Cycle atom at 20.
  RED on base (clamps hid the request at every face; flow capped
  at 99), GREEN 21/21 after the repair. Seed legs are
  PUBLIC_ENTRY_PATH (real Program via execute_seed); router /
  translate / flow-args legs are INTEGRATION.
- Named regressions GREEN after the repair: loop_bounds_test,
  dirf13_loop_count_test, dd14_loop_body_test,
  core_i_arg_gate_test, translate_word_counts_test,
  d1_registry_leaf_test.
- Full regression campaign x3 + exact-head CI: see the PR's
  campaign receipt (posted on completion).

## Scope / non-claims

- No bound changed: 1..5 stands exactly as ruled. No automatic
  continuation. Loop arm untouched. `translate("run 20 cycles")`
  routes to Drive (Dell 19) and never reaches Cycle — recorded by
  the census probe, OUT of R19 scope.
- No scoreboard credit is claimed by this report; CODE credit
  settles only under the standing rule (merged-main behavioral
  proof + both authorities' acts).
