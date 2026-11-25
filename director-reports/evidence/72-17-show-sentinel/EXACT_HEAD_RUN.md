# EXACT-HEAD RUN — 72-17 verification at the frozen PR #304 head

Purpose (Director review 2026-11-05 14:51 CST,
TARGETED_CORRECTION_REQUIRED on the PR #305 supplement):
verify-72-17 run 42103309741 executed at the ephemeral
pull-request merge ref 74cbdcbe94904b6bdde04bb5ffbe7fbb987e81f9,
NOT at PR #304's frozen head — so exact-head execution
identity was not proven, even though the defect finding
itself was supported.

This file is the trigger + receipt home for
`.github/workflows/verify-72-17-exact-head.yml`, which:
checks out the immutable head
cc8ea8b53ea7bfc8d22fc58ff9669b008fc06986 into `pinned/`,
ASSERTS `git rev-parse HEAD` equals it before any check,
then runs the manifest verification, the bounded surface
probe, and the real-browser Studio probe inside that
pinned tree. PR #304 is not rewritten; head runs and
merge-ref runs remain distinct.

Also confirmed for the record: PR #305's Form smoke is
TERMINAL PASS (18m31s, gh-verified 2026-11-05) — its
nonterminal state at the Director's inspection was timing,
not failure.

RECEIPT: appended below when the run completes.

## RECEIPT — exact-head run (2026-11-05)

- Workflow: verify-72-17-exact-head
- Run: 42110658635 —
  https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/42110658635
- Conclusion: **success** (all steps terminal PASS,
  including PR #306's own builds and Form smoke)
- Pinned checkout: cc8ea8b53ea7bfc8d22fc58ff9669b008fc06986
  with **EXACT_HEAD_ASSERTION: PASS** recorded BEFORE the
  manifest check and both probes ran.
- Manifest at the pinned head: `sha256sum -c` — every entry
  OK, exit 0 (in the run log).
- Surface probe (q17_probe.py) at the pinned head: exit 0,
  classification holds on every surface.
- Browser probe (Chrome/156.0.8078.79): assertions file
  records pinned_sha = cc8ea8b53ea7bfc8d22fc58ff9669b008fc06986
  (the probe's own record, not a workflow label); B3 real
  session token, B1 control console clean, B2 bare-Show
  sentinel PRESENT in the user-visible console text — all
  PASS.

Raw artifacts preserved in `exact-head-ci/` alongside this
file (assertions JSON, full console log, screenshot, probe
logs, chrome log). The merge-ref run 42103309741 remains
of record as a DISTINCT, lesser receipt; this run is the
exact-head evidence of record for the frozen candidate.

PRs #304 and #305 remain HELD for the Director's
re-review. The Studio `__RENDER__` defect remains OPEN;
R-B remains proposed, not authorized, not implemented.
