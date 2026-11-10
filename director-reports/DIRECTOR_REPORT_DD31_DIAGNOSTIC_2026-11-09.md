# DIRECTOR REPORT — DD-31 diagnostic circuit: harness capture + controlled pair

Ordered by the Director's ruling 2026-11-09 21:43 CST (Q-DD14.1:
exception not granted; instrument, reproduce under control, publish
the exact assertion or an honest sampling matrix). Authority:
DIR-SLEEP-V3-R2. Status: DIAGNOSTIC DELIVERED — mechanism UNKNOWN;
DD-31 stays OPEN; no closure or exception is claimed by this report.

## 1. Instrumentation (this PR, form/regress.py only)
run_entry() now retains, on a FAILED entry only: the child's own
FAIL lines verbatim, bounded stdout/stderr tails (25/15 lines,
300 chars/line, token-shape scrub for AKIA/ghp_/github_pat_), the
exit status and verdict string, the pass label, and a names+sizes
inventory of the copy's form/state (first 200 entries + total
count). The block prints to the harness's stdout (CI job logs will
carry it) and is filed under REGRESS_FAILURE_DIR
(default ./regress_failures). Verdict computation is byte-identical;
capture runs after the verdict and cannot change it (errors inside
capture are reported inside the block).
Proofs: (a) synthetic failing suite — FAIL line captured verbatim,
block printed + filed, verdict unchanged; (b) real dd31 suite green
run — no capture emitted, no directory created; (c) full runs below
reproduced stock verdicts on every entry.
Acceptance requested: bounded acceptance of this harness patch as
the permanent evidence seam (per the 2026-11-09 19:17 CST note that
a permanent instrumentation patch takes its own bounded acceptance).

## 2. Controlled reproduction (same machine, same order, --twice)
- capA — delivered main 7780dff (product code), instrumented
  harness: GREEN 263/263 both passes, rc=0. No dd31 capture.
- capB attempt 1 — INVALID, owned: main's regress.py was overlaid
  wholesale on the #348 tree, dropping #348's dd14 registry line;
  the run refused on OMITTED INTENDED ENTRY before executing.
  Discarded; method corrected to a patch on the tree's own file.
- capB2 — PR #348 head 813b2aa + capture patch on its own
  regress.py: GREEN 264/264 both passes, rc=0; dd31 21/21 in both
  passes. No dd31 capture.
- Prior instrumented run (diag_driver, DD-14 tree 7dc9ef0):
  264/264 both passes.
Nested captures DID fire — only for by-design inner fixture
failures (daf09 escape/hang inner TIMEOUTs; mini_fail / mini_flaky
/ zz_coupled_probe inner runs). Outer verdicts stayed green.
Interpretation: the seam captures at every nesting level; nested
captures are evidence about inner fixtures, not outer failures.
Bonus datum: one nested capture's inventory counted 7,891 files
in the shared copy's form/state late in a pass (vs ~5,662 measured
earlier in another pass) — state growth in the shared --twice copy
is real and now measurable at failure time.

## 3. Sampling matrix (full-list passes, honestly counted)
Historical observed full-list passes: ~24, of which 7 failed
(always dd31 20/21 NOT_RETURNED_TRUE, pass 1, pass 2, or both;
CI and local). Capture-grade instrumented passes since: 6 of 6
green. Non-reproduction stands. At the historical per-pass rate
(~29%), six consecutive greens have probability ~13% — this
matrix neither exonerates nor convicts; it bounds the hunt.
No indefinite retries are proposed (Director's bound).

## 4. What is still missing
The exact failing assertion remains UNCAPTURED: it has never fired
under instrumentation. Mechanism UNKNOWN (AGENTS SS31.3). The
suite-level suspects stand as hypotheses only: fixed owner
dd31mainZZ, owner-glob cleanup + directory-wide residue assertion,
shared-copy state growth between passes, Program/observer checks
among the suite's 21 (16 pure-string + 5 Program/observer).

## 5. Questions for the Director
Q-DD31-D1: bounded acceptance of the instrumentation patch (this
PR) so future CI failures self-report the FAIL line?
Q-DD31-D2: renewed disposition for PR #348 on this matrix, or does
the capture hunt continue with a stated finite sampling budget
(e.g. instrumented --twice runs attached to future PR smokes at
no extra cost, since the seam rides the harness)?
