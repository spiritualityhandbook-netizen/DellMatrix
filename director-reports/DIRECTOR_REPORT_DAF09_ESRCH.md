# DIRECTOR REPORT — DAF-09 ESRCH-at-open follow-up

Status: SUBMITTED — held for the Director's return (sleep mode;
nothing certified). Scope: ONE classification correction in the
regress tree-kill, found by the instrumented investigation.
This report does NOT re-present session-escape certification:
that remains WITHHELD and the cross-environment discrepancy
remains UNRESOLVED (§31.3). Cancellation remains CERTIFIED and
is not re-opened.

## Ruling requested
Accept (or decline) the bounded classification contract:
pidfd_open ESRCH => "refused"; all other open errnos and
errno-less failures => "unavailable".

## Identity
- PR #210, merged 4ba052c; candidate a15e099; merge tree
  7c862d7 == candidate tree; parents 48c10f2 + a15e099.
- Code delta: form/regress.py only (_signal_identity ESRCH
  branch + errno import + docstring precision); suite
  form/daf09_timeout_tree_test.py 22 -> 23 checks.

## Defect and evidence
The instrumented investigation (DIRECTOR_REPORT_DAF09_
INSTRUMENTED_INVESTIGATION.md) recorded, at run7: pidfd_open
on pid 35111 raised errno 3 (ESRCH) with the starttime
pre-read MATCH — the witnessed instance had already died
(frequently group-killed at the top of _kill_process_tree).
_signal_identity bucketed ANY pidfd_open OSError as
"unavailable", so the verdict gained a spurious
cleanup_unavailable suffix and exact-equality TIMEOUT checks
failed (21/22 in saturated runs 4 and 7) although every
descendant was dead. Run6 showed the same race landing
post-open classing "refused": the already-dead bucket was
timing-dependent. ESRCH at open is the same fact
pidfd_send_signal ESRCH reports one syscall later, already
classed "refused" in this function.

## Repair and verification
- ESRCH at open -> "refused". Other errnos (EMFILE witness
  retained in the suite) and errno-less OSError -> "unavailable".
  No numeric fallback; no verdict/timing changes.
- SWAT Director's-eye pre-mortem before implementation
  (ground: DAF09_ESRCH_PACKET.md in workspace; sequel sweep:
  only run_entry's verdict suffix / REGRESS print and
  _LAST_KILL_REPORT consume "unavailable").
- Failing-first probe: ESRCH unavailable -> refused after the
  fix; EMFILE unavailable in both.
- Suite 23/23. Mutant (ESRCH branch disabled, applied after
  the real commit, reverted by inverse edit, diff verified):
  22/23 — exactly the new control; suite re-verified 23/23.
- Regress 220/220 x3 on candidate a15e099; exact-head CI
  COMPLETE SUCCESS verified in a separate step before merge
  (package 41383414668; smoke 41383414678); fresh-clone
  regress at merge 4ba052c: 220/220 GREEN.

## Exceptions / limits
- The new suite control asserts the classification BUCKET
  under an injected ESRCH; it does not assert death (under the
  injection nobody is signalled).
- Local evidence only. Nothing here explains the Director's
  19/22; the instrumented-driver rerun in his environment
  (Q1 of the investigation report) remains the discriminating
  evidence for the discrepancy itself.

## Anticipated probes
- "Does 'refused' hide real unavailability?" ESRCH is per-pid
  ("this process does not exist"); availability failures are
  EMFILE/ENFILE/EINVAL-class and still surface as unavailable
  with the cleanup_unavailable verdict suffix.
- "Reused PID whose reuser also died pre-open?" Still refused,
  still honest: the witnessed instance is dead and nobody was
  signalled; "refused" never claims a kill.

## Questions for the Director
Q1. Does ESRCH-at-open => refused match your reading of the
    run7 evidence, or should gone-at-open stay visible in the
    verdict as a separate count?
Q2. Is the suite control sufficient post-evidence, or should
    the instrumented driver be re-run under saturation on the
    fixed code (expecting verdict-exact passes)?
