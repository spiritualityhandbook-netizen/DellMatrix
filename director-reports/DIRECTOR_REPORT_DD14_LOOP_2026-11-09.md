# DIRECTOR REPORT — C1.Loop / DD-14: Loop (Dell 13) chained body did not repeat

Circuit: C1.Loop (SS14.4 next single circuit). Authority: SS14 working
plan (adopted, PR #346) + DIR-SLEEP-V3-R2 completion authority.
Classification: FIX (Ace FIX-FIRST; confined to chain execution, not
the save/persistence path). Status: DELIVERED CANDIDATE — Director
review and scoped closure requested. Strict 19/72 unchanged by this
PR alone.

## Defect (verified at tour; grounding re-verified at 58af9db/7399ee5)
A chain headed by Loop printed the requested repetition count but
executed its body ONCE; the receipt claimed the repetitions. Tour
probe: a Loop chain scored 0.45, identical to the no-Loop control.
Until (64) and While (65) prove the system knows proper chain
repetition. Registry note: Dell 13 = Loop; Dell 14 = Bind (DD-14 is
a defect identifier, not a Dell number).

## Repair (form/mandell/chain_exec.py, +34)
execute_range treats Dell 13 as a repetition head: the chained body
executes once per round for the leaf count grammar (clamped 1..5),
and execution STOPS on the first body failure (count/receipt
honesty). No other Dell's path changes.

## Evidence (tiers labeled honestly)
- Failing-first suite form/dd14_loop_body_test.py (11 checks):
  unrepaired 6/11 (all 5 defect checks FAIL; controls + cleanup
  PASS); repaired 11/11. Registered in form/regress.py LIST.
- Mutant: restoring the defect dropped the suite to 5/11 (killed);
  reverted by inverse edit.
- Regression on candidate code (pre-rebase head 7dc9ef0; the three
  changed files are byte-identical at this PR's head c26650a —
  0-line diff verified; suite re-run on the rebased tree: 11/11):
  - leg fwd: GREEN 264/264, rc=0.
  - leg --twice r2: RED 263/264 pass 1 / GREEN pass 2 — sole red
    form.dd31_sanitize_copula_test (the DD31-CI-INTERMITTENT
    flicker, separate named circuit); form.dd14_loop_body_test
    11/11 in BOTH passes.
  - leg --order rev r1: NO RESULT (VM replacement killed the leg
    mid-run; partial log retained, never counted).
  - leg --order rev r3: GREEN 264/264, rc=0.
- Exact-head CI for THIS PR: reported from its own terminal output
  in the PR thread; a dd31-only smoke red, if it occurs, is the
  known flicker and is classified as such — it is not hidden.

## Non-claims
No DD-44 contract change (bounds semantics unchanged). No claim
about Loop compositions beyond the suite's chains. The DD-31
flicker is not resolved by this circuit; the --twice leg has no
fully-green run on this candidate (its only red is the flicker).

## Anticipated probes
- "Is the clamp 1..5 a silent bound?" The leaf count grammar
  already clamps counts 1..5 for sibling heads (Until/While
  family semantics); Loop now shares it. DD-44's explicit-bounds
  redesign remains its own pending slice.
- "Body failure mid-loop?" Covered: stop-on-first-failure is a
  suite check; later rounds do not execute.
- "Receipt honesty?" The suite asserts executed-round counts
  against receipts, not just final state.

## Questions for the Director
Q-DD14.1: scoped closure of DD-14 on this evidence (with the
--twice caveat recorded), or is a fully-green --twice leg required
first (which couples this closure to the DD-31 circuit's outcome)?
