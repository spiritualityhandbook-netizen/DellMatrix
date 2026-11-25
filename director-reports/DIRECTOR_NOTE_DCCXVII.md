# DIRECTOR NOTE — DCC-XVII FLAKE: DOCUMENTATION EXCEPTION DISCHARGED

**Status: SUBMITTED — the correction required by the
DCC-XVII FLAKE RULING (REPAIR ACCEPTED WITH DOCUMENTATION
EXCEPTION) is complete in this PR. Independent runtime
certification is not claimed; the provisional ruling stands
as the Director left it.**

## The ruling (recorded)

Target U.sigkill_mid_write; merge 2d92c98. The previous
fixed-delay test could assert mid-write recovery without
establishing that the interruption occurred during the
write; the state-triggered, verified interruption corrects
that test-design weakness. This is a test-harness
correction — NOT evidence that the underlying persistence
implementation was defective — and the production
persistence implementation has not been reopened.

## Corrections made (the documentation exception)

1. **Test comment:** the retracted "local U-probe iter 2"
   claim is removed from the choreography comment in
   `form/mandell/dcc_xvii_test.py`; a labeled retraction
   note points here. (Comment-only change.)
2. **PR #229 description:** corrected in place — a
   CORRECTION banner leads it, and the two retracted claims
   ("reproduced locally", "U-probe reproduced the failure
   at iteration 2") are struck and labeled, with the
   restated evidence basis. Original claims remain visible
   as corrected, not silently deleted.
3. **Evidence published:** the corrected investigation
   packet (leading CORRECTION section), the correction
   evidence note, probes, timing and mutant logs, regress
   legs, fresh-clone log, the CI failure extract, and the
   preserved contaminated run log are in
   `director-reports/evidence/dccxvii/` with an EVIDENCE.md
   SHA-256 manifest.

## What the verdict rests on (restated basis)

The CI event itself (run 41493670559: 81/81, 81/81, then
80/81 on the reverse leg); the measured scheduling margin
(write window ~1.24 s vs fixed 0.5 s kill delay, ~0.7 s of
parent scheduling slack, single-writer timing probe); and
deterministic Mutant B (forced late kill + vacuous
verification reproduces the exact failure signature against
a completed G2) with Mutant B2 (the repair's verification
catches such misses). Under clean sequential conditions the
flake did not reproduce in 114 pre-fix executions,
consistent with the observed CI rate. The retracted claims
are not load-bearing.

## Standing rule recorded

Run state-sharing regression campaigns sequentially or
isolate their state directories. Do not accept interim
output as a completed result. (Both halves were violated by
the investigation itself, producing the retracted claims;
both were already workspace law — TOOLS.md now carries the
campaign form explicitly.)
