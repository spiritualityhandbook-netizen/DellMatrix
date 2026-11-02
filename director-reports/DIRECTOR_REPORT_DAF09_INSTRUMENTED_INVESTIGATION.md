# DIRECTOR REPORT ADDENDUM — DAF-09 INSTRUMENTED INVESTIGATION (session-escape only)

Evidence submitted for a bounded re-ruling. A report is evidence,
never a certificate. Merged != certified.

## Ruling this answers

Director Ruling #7 (DIR-REVIEW-2026-11-01) on the pidfd-hardening
follow-up at 87be4de: PARTIAL — safe-refusal mechanism accepted;
SESSION-ESCAPE CERTIFICATION REMAINS WITHHELD. His independent
run: 19/22 (Uni local 22/22), failing (1) the escaping grandchild
post-timeout marker, (2) the identity positive control
(kill_report=refused), (3) the pidfd-failure unavailable-report
control (refused: [(22, None)], unavailable empty). Directed
action: preserve the exact 22 checks; instrument identity
acquisition at witness AND signal time, /proc visibility,
namespace identity, reparenting, marker timestamps, outcome
path; separate missing from changed identity from pidfd
unavailability; minimal positive fixture proven visible in the
observer's namespace before judging cleanup; classify
unsupported environments explicitly.

This addendum presents the instrumented investigation only.
No code or test changes. Session-escape stays WITHHELD; the
discrepancy is NOT claimed resolved (AGENTS.md §31.3).
Cancellation is CERTIFIED and is not re-opened.

## Method and preservation

Base: main 5f1120e (form/regress.py and the suite byte-identical
to the hardening merge tree for these files). Driver:
hidden_files/daf09instr_driver.py — pre-injects the real regress
module with logging wrappers via sys.modules; the suite file is
untouched (worktree clean after every run) and its main() runs
unchanged. The 22 check names are identical across all runs;
uninstrumented baseline at the same HEAD: 22/22. JSONL logs:
hidden_files/daf09instr_logs/. Full packet:
DAF09_INSTRUMENTED_INVESTIGATION_PACKET.md (Uni workspace).

Environment header (this observer): Linux, Python 3.12.3,
4 CPUs, pidfd_open available, pid namespace self == init
(inode 4026532497), /proc mounted without hidepid.
Minimal positive fixture (before the checks, every run):
SUPPORTED — descendant scan sees the sleeper, its starttime is
non-None and equal to the scan record, _signal_identity returns
"signalled", bounded wait observes death. This environment is
therefore classifiable as supported for cleanup judgement.

## Results

- Idle instrumented runs x4 (run1/2/3/5): suite 22/22 each.
- Saturated runs (6 CPU hogs on 4 CPUs): run6 22/22;
  run4 and run7 21/22 each, both failing ONLY an exact-equality
  "reports TIMEOUT" check because of a cleanup_unavailable
  suffix (mechanism below) — the descendants in question were
  dead and no marker wrote.

Keyed to his three failures:

(1) Escape marker: NOT reproduced in 7/7 runs. Escapee
    kill_report=signalled, identity_now=None, marker absent,
    grandchild dead, idle and saturated. Witness scan duration
    max 0.0014s idle vs 0.0658s saturated. Classification for
    his environment: UNKNOWN.

(2) Positive control refused: NOT reproduced (7/7 pass). All
    local "refused" outcomes carry a recorded designed reason
    (CHANGED stale identity; MISSING gone instance; post-open
    failure on an already group-killed instance).

(3) Pidfd control (pid, None): NOT reproduced for a live
    process — capture returned a real starttime in 7/7 runs
    (MATCH, then "unavailable" under the injected failure).
    The step-(a) seam is proven locally: a (pid, None) identity
    collapses to "refused" before pidfd is attempted (the
    gone-instance control produces exactly this shape every
    run, because _proc_starttime returns None for a dead
    process). If his capture of a live victim returned None,
    the shape follows; the acquisition failure itself was not
    reproduced and its cause there is UNKNOWN.

## New local mechanism (evidence-backed; explains none of (1)-(3))

_signal_identity maps ANY pidfd_open OSError to "unavailable",
including ESRCH — the instance died between the starttime
pre-read and pidfd_open, often because killpg at the top of
_kill_process_tree already killed it. Under saturation this
fired in 2 of 3 saturated runs: run7 records pidfd_open errno 3
(ESRCH), /proc state None at the open attempt, pre-read MATCH
(1812456) for escape mid pid 35111; run4 shows the same outcome
class (MATCH -> unavailable, pid 34833; v1 driver captured no
errno). The unavailable entry appends cleanup_unavailable to
the timeout verdict, failing the suite's exact-equality TIMEOUT
checks even though cleanup in fact succeeded. Run6 shows the
same race landing one syscall later (post-open) => "refused",
verdict clean, 22/22: the bucket for an already-dead witnessed
instance is timing-dependent. ESRCH at open is the same fact
_signal_identity already classes "refused" when it arrives
from pidfd_send_signal. Recorded as a bounded follow-up
candidate (ESRCH-at-open => "refused" + one new control); NOT
implemented here (investigation = evidence only).

## Anticipated probes

- Saturation rig artificial? The hogs only widen a window that
  exists as written: pre-read and open are separate syscalls,
  and killpg precedes the per-identity loop by construction.
- Instrumentation changed behaviour? Suite untouched, check
  names identical, baseline 22/22 same HEAD, and the suite's
  own pidfd-failure injection still produced exactly its
  designed outcome under the driver (proxy flag in the log).

## Questions for the Director

Q1. Can the packaged driver be run in your environment
    (python3 daf09instr_driver.py <repo> <out.jsonl> dir-rerun)?
    Its records separate MISSING / CHANGED / MATCH-then-ESRCH /
    genuine pidfd failure for each failing check.
Q2. Is the bounded ESRCH-at-open follow-up in scope for the
    DAF-09 queue now, or held until your instrumented rerun
    classifies (1)-(3)?

## Bounded ruling requested

None on certification: session-escape remains WITHHELD. This
addendum asks only that the investigation evidence, the new
ESRCH-at-open mechanism, and Q1/Q2 be taken up at his return.
The held stack entry is SUBMITTED.
