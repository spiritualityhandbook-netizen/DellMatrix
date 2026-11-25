# DAF-09 INSTRUMENTED INVESTIGATION — EVIDENCE PACKET (Course 1, steps b+c)

Date: 2026-11-01 (sleep mode). Base: origin/main 5f1120e (verified
this run; form/regress.py 800 lines, form/daf09_timeout_tree_test.py
442 lines, both byte-identical to the step-(a) re-verification base).
Status: session-escape WITHHELD; cross-environment discrepancy
UNRESOLVED (AGENTS.md §31.3). Local results below calibrate the
instrumentation and identify one local mechanism; they do NOT
resolve the Director's 19/22.

## Method (per daf09_mapping_reverify_2026-11-01.md §4)

Driver: hidden_files/daf09instr_driver.py. The suite file was NOT
edited (worktree git status clean after every run). The driver
pre-injects the real regress module object with logging wrappers
as sys.modules["form.regress"]; the suite's main() runs unchanged.
Check-name list (22 names) is identical across all 7 runs and the
final line shape is the suite's own `DAF09_TIMEOUT_TREE: n/22`.
Hooks logged (JSONL, monotonic+wall): env header (kernel, Python
3.12.3, 4 CPUs, pidfd_open available, pid-ns inode self==init
4026532497, /proc mount hidepid=none shown), minimal positive
fixture BEFORE the checks, _descendant_identities (duration,
entry count, returned identities, None starttimes, skipped),
_proc_starttime (value/None, in-signal context), _signal_identity
(expected, pre-read classified MISSING/CHANGED/MATCH, outcome,
pidfd proxy status), pidfd_open result/errno + target /proc state
(driver v2), _communicate_tracked enter/exit + witnessed union,
_kill_process_tree enter (snapshot/witnessed/union, ppid per
identity at kill time) / exit (kill report, alive-after),
run_entry outcome path, external marker/pidfile observer (0.05s).

Logs: hidden_files/daf09instr_logs/ (baseline_uninstrumented.log,
run1..run7 *.jsonl + *.stdout.log).

## Runs

- baseline (uninstrumented): 22/22.
- run1/run2/run3 idle, run5 idle (v2 driver): 22/22 each.
- run4 saturated (6 CPU hogs, 4 CPUs): 21/22.
- run6 saturated (v2): 22/22.
- run7 saturated (v2): 21/22.
Minimal positive fixture: SUPPORTED in all 7 instrumented runs
(scan sees sleeper; starttime non-None and equal to scan record;
_signal_identity => "signalled"; bounded wait observes death).
The observer environment is therefore classifiable as SUPPORTED
for cleanup judgement; no run is environment evidence only.

## Findings keyed to the Director's three failures (Ruling #7)

(1) Escaping grandchild post-timeout marker — NOT REPRODUCED.
In all 7 runs: kill_report=signalled for the escapee, identity_now
=None at assertion, marker absent, grandchild dead. Witness scans:
max duration 0.0014s idle, 0.0658s saturated (~50x coarsening under
saturation, escapee still witnessed and signalled). H2 (marker
slack ~1s, §2 of the re-verification) remains a live explanation
for his environment only; local timing does not support it here.
Classification: UNKNOWN for his environment.

(2) Identity positive control kill_report=refused — NOT
REPRODUCED (control passed 7/7). Every local "refused" outcome is
a designed class: CHANGED (stale +1 starttime, negative control),
MISSING (gone instance, expected=None), fixture-cleanup gone
instance, and run6's hang descendant MATCH->refused (pidfd_open
succeeded; the already group-killed instance failed the post-open
recheck/send — the benign refused class). No live matching
identity was refused without a recorded reason.

(3) Pidfd-failure control refused:[(22,None)] — NOT REPRODUCED
for a live process: the control's identity was captured with a
real starttime in all 7 runs (MATCH, then "unavailable" under the
injected pidfd_open failure; driver proxy flag confirms the
injection replaced pidfd_open in exactly that section). The seam
from step (a) is nevertheless PROVEN locally: in every run the
gone-instance control produces (pid, None) -> "refused" before
pidfd is attempted, because _proc_starttime returns None for a
dead process. If in the Director's environment the capture of a
LIVE victim's starttime returned None (identity *acquisition*
failure), the observed shape follows exactly. The acquisition
failure itself was not reproduced; its cause in his environment
is UNKNOWN.

## NEW MECHANISM IDENTIFIED LOCALLY (evidence-backed)

_signal_identity maps ANY pidfd_open OSError to "unavailable",
including ESRCH — the witnessed instance died between the
starttime pre-read and pidfd_open (frequently because killpg at
the top of _kill_process_tree already killed it). Under CPU
saturation the pre-read->open window widens and this fired in
2 of 3 saturated runs:

- run4: hang descendant pid 34833, pre-read MATCH (1796438),
  outcome "unavailable" (v1 driver did not capture the errno;
  mechanism inference for this run is by outcome class only).
  Verdict became "TIMEOUT cleanup_unavailable=1:34833"; the
  descendant was in fact dead, no marker wrote; suite 21/22,
  failing only "timed-out entry reports TIMEOUT" (exact-equality
  check on the verdict string).
- run7: escape mid pid 35111, pre-read MATCH (1812456), then
  pidfd_open raised errno 3 (ESRCH, "No such process") with
  /proc state None at open attempt => "unavailable". Verdict
  "TIMEOUT cleanup_unavailable=1:35111"; suite 21/22, failing
  only "escape entry reports TIMEOUT". The escapee grandchild
  itself was signalled and dead; marker absent.

Contrast run6: the same race landed one step later (open
succeeded, post-open/send failed) => "refused", verdict stayed
exactly "TIMEOUT", 22/22. So the bucket an already-dead
witnessed instance lands in is timing-dependent (refused vs
unavailable), and only "unavailable" pollutes the timeout
verdict. This is a local classification defect (gone-at-open is
the refused/no-op class, not pidfd unavailability), distinct
from the Director's three failures: it explains none of them,
and it does not resolve the discrepancy (§31.3). It is recorded
as NBD candidate 1 for a bounded follow-up circuit (pidfd_open
ESRCH => "refused"; other errnos stay "unavailable"; suite gains
an ESRCH-at-open control; exact 22 checks preserved in substance
plus the new control, as in prior follow-ups). NOT implemented
in this investigation (evidence only, per the directive).

## Classification (step c)

- Mechanism identified with evidence: YES, locally — the
  ESRCH-at-open misclassification (above). It is a NEW finding,
  not an explanation of the Director's 19/22.
- Director's failures (1)/(2)/(3): not reproduced; not shown
  insensitive by design; discrepancy UNRESOLVED. The
  discriminating evidence remains an instrumented run in the
  Director's environment: this driver + spec are packaged for
  that run unchanged (driver takes worktree root + output path).
- No code or test changes in this circuit. No claim changes.
  Session-escape stays WITHHELD. Cancellation certification
  stands and is not re-opened.

## Anticipated probes

- "Is the ESRCH mechanism just your saturation rig?" The hogs
  only widen a race window that exists in the code as written:
  pre-read and open are separate syscalls with no atomicity, and
  killpg precedes the per-identity loop by construction. run6
  vs run7 show both landings of the same race.
- "Why is ESRCH 'refused' rather than 'unavailable'?" Because
  _signal_identity already treats pidfd_send_signal ESRCH as
  "refused" (pinned instance already dead: nobody signalled).
  ESRCH at open is the same fact observed one syscall earlier.
- "Did instrumentation change the suite?" No: suite file
  untouched (git status clean), check names identical in all
  runs, uninstrumented baseline 22/22 at the same HEAD, and the
  designed pidfd-failure control still produced exactly its
  designed outcome under the driver (proxy flag records where
  the suite's own injection replaced pidfd_open).

## Questions for the Director

Q1. In your 19/22 environment, can the packaged driver be run
    (python3 daf09instr_driver.py <repo> <out.jsonl> dir-rerun)?
    Its signal_identity + pidfd_open records separate MISSING /
    CHANGED / MATCH-then-ESRCH / genuine pidfd failure for each
    of your three failing checks.
Q2. Is the bounded ESRCH-at-open follow-up (classification fix
    + one new control) in scope for the DAF-09 queue, or should
    it wait until your instrumented rerun classifies (1)-(3)?
