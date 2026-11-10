# DD-31 Bounded Exception Request — PR #348 (C1.Loop / DD-14) ONLY

Status: SUBMITTED 2026-11-09 (CST) for Director disposition under DIR-SLEEP-V3-R2. Prepared by a background cycle; verified and corrected by the main session before publication (corrections: the two --twice logs are now stated separately and exactly; the diff claim is stated against the PR's final diff; the capture plan is stated as bounded scoped runs per the Director's wording).
Channel: publish on GitHub (Uni → Director channel law). This draft does
not merge anything and does not extend to any other PR.

## Request

A scoped red-check exception for PR #348's merge, limited to the single
known DD-31 flicker (`form.dd31_sanitize_copula_test:smoke`, 20/21,
NOT_RETURNED_TRUE), on the grounds below. DD-31 itself stays OPEN as its
own circuit; this request does not close, waive, or reclassify it, and
does not extend to PR #345 (runtime code, separate disposition).

## Independence proof (mechanical, diff-verified 2026-11-10)

PR #348's final diff changes exactly two product files:

- `form/mandell/chain_exec.py` (+34) — Loop chained-body execution
- `form/regress.py` (+1) — registry line for the new dd14 suite only

Plus the new suite `form/dd14_loop_body_test.py` and docs
(`director-reports/` report + INDEX row; INDEX union was the sole
rebase conflict onto main 7780dff, resolved keeping both records;
code byte-identical to the Director-reviewed head b18c063).

The PR touches NO Sanitize, redaction (`form/mandell/redaction.py`),
Program persistence, state-cleanup, or dd31-suite code. The failing
suite and the changed code share no file and no code path except the
regress registry list itself.

## Failure pattern (evidence, with bounds)

- DD-31 red has appeared on: PR #345's smoke, the docs-only PR #346
  head (zero product code), merged main itself, and PR #348's local
  `--twice` legs — i.e. it occurs with and without the Loop change,
  and with no product change at all.
- Local --twice chain logs (`hidden_files/dd14_logs/`), stated
  separately and exactly:
  - leg_twice.log (original leg, interrupted by the wake-mode halt
    during pass 2 — pass 2 has NO RESULT): pass 1 RED 263/264,
    sole red dd31 20/21 NOT_RETURNED_TRUE; dd14 11/11 in that pass.
  - leg_twice_r2.log (fresh complete leg): pass 1 RED 263/264,
    sole red dd31 20/21; pass 2 GREEN 264/264; dd14 11/11 in both
    passes.
- PR #348 exact-head CI: all terminal SUCCESS at reviewed head
  b18c063 (Director-verified) and again at reconciled head 813b2aa
  (builds, browser, full smoke 19m39s clean; PR mergeable).
- Instrumented capture run (`hidden_files/dd31_diag_logs/diag_run.log`,
  source dd14_work tree): full 264-entry list twice, dd31 through a
  capture variant retaining full stdout/stderr + state inventories —
  264/264 on both passes, dd31 21/21 both, zero dd31 residue
  before/after. The failure did NOT reproduce under instrumentation.
- Honest bounds: local greens do NOT resolve the discrepancy
  (AGENTS §31.3). Reproduction is probabilistic; the exact failing
  one of the suite's 21 assertions is still UNCAPTURED because
  `form/regress.py run_entry()` discards per-entry stdout/stderr —
  the suite's printed `FAIL {name}: {detail}` line never reaches
  any log. Mechanism remains UNKNOWN. Leading unproven hypothesis:
  pass-order/state coupling in the shared copied tree the `--twice`
  mode reuses (suites write state into that one copy as they run).

## Residual risk if granted

- Merging #348 does not make DD-31 worse: the flicker pre-dates the
  PR, occurs on main, and the PR's diff cannot influence the dd31
  suite's inputs.
- DD-31 remains an open reliability defect: future PR smokes will
  keep showing intermittent attempt-1 reds until it is captured and
  repaired; each must still be classified, never waved through by
  this exception (it is scoped to #348 only).
- Loop's own risk is separately bounded: failing-first 6/11 → 11/11,
  mutant killed (5/11), neighbours green, reverse regression 264/264.

## What continues regardless of disposition

- Capture hunt continues as bounded, separately scoped diagnostic
  runs (the Director's framing) until a red is captured with full
  stdout/stderr, exact assertion, and before/after state
  inventories (driver already built:
  `hidden_files/dd31_diag_logs/diag_driver.py`). Each run is a
  discrete scoped step reported on its own result; no unattended
  retry loop.
- If a non-gated defect reproduces, FIX-FIRST minimal repair with
  failing-first + mutant + exact-head CI, per Director directive.
- §32 Director-mail freshness check immediately before any #348 merge.

## Decision required

Director only (DIR-SLEEP-V3-R2 delegated authority; no Ace action):
grant or deny this #348-scoped exception. If denied, #348 stays on
MERGE HOLD and the capture hunt remains the critical path for both
#348 and #345.
