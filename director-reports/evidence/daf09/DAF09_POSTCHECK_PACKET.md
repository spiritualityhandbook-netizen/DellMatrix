# DAF-09 Q2 POST-CHECK — PACKET (sleep-mode NBD-4)

Date: 2026-11-02 (sleep mode). Base: origin/main c9d5a82
(verified this run via gh; lineage includes the NBD-1
ESRCH-at-open fix, PR #210 merged 4ba052c). Status:
EVIDENCE COMPLETE. NOT certified. Session-escape remains
WITHHELD; the Director's cross-environment discrepancy
remains UNRESOLVED (AGENTS.md §31.3) — local results below
resolve nothing about his 19/22.

## Question
DAF09_ESRCH_PACKET.md Q2: should the instrumented driver
be re-run under saturation on the fixed code as a
post-check (expecting verdict-exact runs), or is the suite
control sufficient? This circuit runs the post-check and
records what it does and does not establish; sufficiency
remains the Director's call at his return.

## Method
Driver: hidden_files/daf09instr_driver.py, UNCHANGED from
Course 1. Worktree nbd-omega-daf09instr fetched and
checked out at c9d5a82 this run; git status clean before
and after every run (suite file unedited). Suite on fixed
main is 23 checks: the original 22 preserved in substance
plus the ESRCH-at-open control. Saturation: 6 CPU hogs on
4 CPUs, as in Course 1 runs 4/6/7; hogs killed after each
run (verified none left). Ground + SWAT pre-mortem:
hidden_files/daf09post_ground.md. Logs:
hidden_files/daf09post_logs/ (baseline_uninstrumented.log,
post1_idle, post2-post4_saturated; .jsonl + .stdout.log).

## Runs — all verdict-exact
- baseline (uninstrumented, direct suite): 23/23.
- post1 idle instrumented: 23/23.
- post2/post3/post4 saturated instrumented: 23/23 each.
- Minimal positive fixture: SUPPORTED in all 4
  instrumented runs.
- Check-name list identical across all 4 instrumented
  runs (suite RESULTS dumped verbatim in each JSONL).
- Hang and escape run_entry verdicts exactly "TIMEOUT"
  in every run; no cleanup_unavailable suffix anywhere
  in a real-path verdict.

## Saturation comparability
Witness-scan durations coarsened under saturation as in
Course 1: idle max 0.0015s; saturated max 0.0690s /
0.0559s / 0.0629s (Course 1 saturated max 0.0658s). The
saturation was real, not nominal.

## Did the ESRCH race fire?
NOT OBSERVED in these runs. Driver pidfd_open log: zero
errors in all 4 runs. Real-path _signal_identity tally
per run: 5 signalled; the only refused outcomes are the
designed controls (CHANGED stale identity, MISSING gone
instance, and the suite's ESRCH-at-open stub control,
which classes refused exactly as designed); the only
unavailable outcome per run is the suite's designed
pidfd-failure control (proxy flag False — the suite's
own stub replaced pidfd_open; its kill report shows the
control victim alive by design, as in Course 1).

## Classification
- The post-check establishes: on fixed main, the
  instrumented suite is verdict-exact under saturation
  comparable to the conditions that produced 21/22 twice
  in Course 1 (runs 4 and 7).
- It does NOT directly demonstrate the live race landing
  in the refused bucket, because the race did not fire
  in 3 saturated runs. That landing is instead pinned
  deterministically by the suite's ESRCH-at-open
  control — present and passing in every run here, and
  mutant-killed in NBD-1 (branch disabled -> 22/23,
  exactly that control fails).
- No code or test changes in this circuit. No claim
  changes: discrepancy UNRESOLVED, session-escape
  WITHHELD, cancellation certification not re-opened.

## Anticipated probes
- "Four greens prove the fix." No: they prove verdict
  exactness under these saturated runs. The fix itself
  rests on the NBD-1 deterministic control + mutant.
  A run in which the live race fires and lands refused
  would be stronger; it is recorded as not observed,
  not rounded up.
- "Saturation was weaker this time." Scan coarsening
  matches Course 1's saturated magnitude (~45x idle);
  hog/CPU counts identical.
- "The unavailable in the kill report is a failure."
  It is the designed pidfd-failure control's own kill,
  the explicit-reporting behavior check 21 asserts.

## Questions for the Director
Q1. Is verdict-exactness under saturation (race not
    observed) plus the deterministic suite control
    sufficient closure for the ESRCH follow-up, or do
    you want saturated runs continued until the live
    race is observed landing refused?
Q2. Should this post-check pattern (re-run the
    instrumented driver on the fixed code) become the
    standing tail for future DAF-09-class fixes?
