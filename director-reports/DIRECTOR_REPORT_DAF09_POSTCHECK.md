# DIRECTOR REPORT — DAF-09 Q2 post-check: instrumented driver re-run under saturation on fixed code

Status: SUBMITTED — held for the Director's return (sleep
mode; nothing certified). Scope: evidence only. This
report answers the data half of DAF09_ESRCH_PACKET.md Q2;
whether the evidence is sufficient is the Director's
ruling, requested at his return. Session-escape remains
WITHHELD; the cross-environment discrepancy remains
UNRESOLVED (§31.3); cancellation certification is not
re-opened.

## Ruling requested
At return: (Q1) accept verdict-exact saturated post-check
runs (live race not observed) plus the deterministic
ESRCH suite control as sufficient closure for the
ESRCH-at-open follow-up, or direct continued saturated
runs until the live race is observed landing "refused";
(Q2) adopt or decline this post-check pattern as the
standing tail for DAF-09-class fixes.

## Identity
- Evidence base: main c9d5a82 (lineage incl. PR #210,
  merged 4ba052c, the ESRCH-at-open fix).
- No code or test changes in this circuit. Packet:
  DAF09_POSTCHECK_PACKET.md (workspace). Ground + SWAT:
  hidden_files/daf09post_ground.md. Logs:
  hidden_files/daf09post_logs/.

## Evidence
- Driver daf09instr_driver.py unchanged; suite file
  unedited (worktree clean before/after every run).
  Suite on fixed main: 23 checks (original 22 in
  substance + ESRCH-at-open control); check-name list
  identical across all instrumented runs.
- Baseline uninstrumented 23/23; post1 idle 23/23;
  post2/post3/post4 saturated (6 hogs, 4 CPUs) 23/23
  each. Fixture SUPPORTED in all instrumented runs.
  Hang/escape verdicts exactly "TIMEOUT" in every run;
  no cleanup_unavailable suffix in any real-path verdict.
- Saturation comparable to Course 1: witness-scan max
  0.056–0.069s saturated vs 0.0015s idle (Course 1
  saturated max 0.0658s, which produced 21/22 twice on
  the pre-fix code via this mechanism).

## Limits (stated, not buried)
- The live ESRCH-at-open race did NOT fire in these
  runs: zero pidfd_open errors in the driver log across
  all 4 instrumented runs. The refused landing is
  therefore not directly re-observed here; it is pinned
  by the suite's ESRCH control (passing in every run;
  mutant-killed in NBD-1). The only unavailable outcome
  per run is the designed pidfd-failure control.
- Local greens resolve nothing about the Director's
  environment (§31.3). His three failures remain not
  reproduced and not explained.

## Anticipated probes
- "Why stop at 3 saturated runs?" The runs answer the
  verdict-exactness question; continuing until a race
  fires is a sufficiency judgment — posed as Q1 rather
  than silently extended or silently assumed.
- "Driver/suite drift since Course 1?" Only the suite's
  own NBD-1 delta (the ESRCH control); the driver is
  byte-identical to Course 1.

## Questions for the Director
Q1/Q2 as in "Ruling requested" above.
