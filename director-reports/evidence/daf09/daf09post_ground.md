# DAF-09 Q2 POST-CHECK GROUND — NBD-4 (sleep mode)
# Run 2026-11-02 ~02:34 CST. Base verified THIS RUN via gh:
# origin/main = c9d5a82 (PR #215 merge; lineage incl. NBD-1
# ESRCH fix 4ba052c / PR #210 and its report PR #211 f850fd8).
# No open PRs. Cron: symbiosis-execution-continuation DISABLED;
# only sleep-mode-execution in flight.
# READ FALLBACK USED: an opening read was flagged by a content
# safety check; no instruction was taken from flagged content
# alone. Position corroborated independently (gh main + merged
# PRs #209-#215, git worktree status, cron list, register grep,
# ws_theater_ground.md lines re T4/T8/T11/T12 decision-first,
# ESRCH packet Q2 verbatim in DAF09_ESRCH_PACKET.md) before
# executing the corroborated next action (NBD-4).

## Question (DAF09_ESRCH_PACKET.md Q2, posed to the Director;
## taken up locally as an evidence post-check under sleep NBD —
## the Director's answer is still his; this run supplies data)
Should the instrumented driver be re-run under saturation on
the fixed code as a post-check (expecting verdict-exact runs),
or is the suite control sufficient?

## Scope / contract
- Evidence ONLY. No code or test changes in this circuit.
- Driver: hidden_files/daf09instr_driver.py, UNCHANGED.
  Worktree: nbd-omega-daf09instr, fetched + checked out at
  c9d5a82 this run, clean before runs (verified).
- Suite on fixed main is 23 checks: the exact original 22
  preserved in substance + the ESRCH-at-open control (check 9
  in suite numbering, form/daf09_timeout_tree_test.py:424-451).
  The state file's "exact 22 checks preserved" is read as that
  substance; the driver's own RESULTS dump is authoritative
  for the count in each run.
- Runs: 1 idle instrumented + 3 saturated instrumented
  (saturation = 6 CPU hogs on 4 CPUs, as in Course 1 runs
  4/6/7) + 1 uninstrumented direct suite run.
- Logs: hidden_files/daf09post_logs/, never only /tmp.
- Success shape: every run verdict-exact (all checks pass);
  any ESRCH-at-open event in the JSONL classes "refused",
  never "unavailable", and no cleanup_unavailable verdict
  suffix appears.
- AGENTS.md §31.3: local greens NEVER resolve the Director-
  environment discrepancy. Session-escape stays WITHHELD;
  DAF-09 discrepancy stays UNRESOLVED regardless of outcome.

## SWAT — Director's-eye pre-mortem
1. "Post-check greens prove the fix" -> No claim beyond the
   runs: the suite's ESRCH control (mutant-killed in NBD-1)
   pins the classification deterministically; these runs only
   test whether the LIVE race, when it fires under saturation,
   now lands in the refused bucket with verdict intact. If the
   race never fires, say so — the runs then show verdict
   exactness under saturation, not the race landing.
2. "Driver changed the suite" -> Same defence as Course 1:
   suite file unedited, worktree git status checked after
   every run; driver wraps module functions only.
3. "Saturation rig differs from Course 1" -> Same hog count
   (6) and CPU count (4); loadavg + witness-scan durations
   recorded in each JSONL env header / hooks for comparison
   against run4/6/7 (scan max 0.0658s saturated in Course 1).
4. "You quietly upgraded 22 to 23" -> Count is stated up
   front here and in the packet; check-name lists dumped
   verbatim per run and compared across runs.
5. "A red run gets buried" -> Every run is logged and
   reported whatever its result; a red run is a finding
   (evidence either way), classified, not re-run into green.
