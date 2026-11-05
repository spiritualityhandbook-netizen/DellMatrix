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
