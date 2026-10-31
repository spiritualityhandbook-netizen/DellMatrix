# DIRECTOR REPORT — DAF-09 IDENTITY-SAFE SIGNALLING FOLLOW-UP

Evidence submitted for a bounded re-ruling. A report is evidence,
never a certificate. Merged != certified.

## Ruling this answers

Director Mode D (2026-10-31), DAF-09 addendum at f1c0205:
PARTIALLY CERTIFIED. SIGINT cancellation was certified within the
tested Linux scope. Session-escape certification was withheld
because the Director's independent runs returned 15/16 and then
14/16 against Uni's 16/16. A new gap was recorded: the regression
tracker retained bare numeric PIDs without process-identity
protection, so PID reuse could cause a signal to be attempted
against an unrelated process (mock-confirmed; no real incident).

This follow-up re-presents the session-escape coverage only.
Cancellation is already certified and is not re-opened.

## Frozen candidate

Candidate: ebe3243e40f5b68f9a9013a7e0dbdc737ca9a359
Candidate tree: 7103a4f5d1179161392123b42bf3acb3e78be9a2
Base: main f14df47a (PR #175 merge)
PR: #176 — merged as 3234966dd93b044d6633b2646f2186209696dea2
  (2026-10-31T23:25:13Z)
Merge tree: 7103a4f5d1179161392123b42bf3acb3e78be9a2 == candidate tree
Merge parents: f14df47 + ebe3243

## Investigation

Uni reproduced the prior suite 8/8 at 16/16 on the base, including
two runs under full CPU saturation; the Director's failures did not
reproduce in Uni's environment. The assertion/probe mapping found:

- H1, zombie/reaping misread: not supported for these probes. The
  suite liveness probe and the runner's post-kill wait both parse
  /proc state and treat zombies as dead.
- H2, timing/fixture assumption: supported as a material risk. The
  escaping grandchild was visible to the ppid witness walk only
  while its intermediate parent lived. That parent exited after a
  fixed 1.0 second sleep, so the effective witness window presumed
  fixture startup speed and dense /proc scans in any environment.
  The marker slack was also only one second (write at 3s; timeout
  at 2s).
- H3, bare-PID identity race: confirmed in code and demonstrated
  by execution. The witnessed set, kill path, and suite cleanup
  guards all carried bare integer PIDs.

Failing-first probe on unmodified code: a witnessed set containing
an unrelated bystander's bare PID produced BYSTANDER_KILLED. The
same probe on the fixed code produced BYSTANDER_ALIVE.

## Fix (SWAT unanimity 4/4 recorded before implementation)

Files: form/regress.py and form/daf09_timeout_tree_test.py.

- _communicate_tracked now witnesses identities, not PIDs: each
  entry is (pid, /proc starttime), captured while the descendant is
  attached.
- _kill_process_tree signals the kill-time snapshot union witnessed
  identities only through _signal_identity.
- _signal_identity refuses when the starttime is absent or the
  process currently at that PID has a different starttime. It
  prefers a pidfd (os.pidfd_open plus pidfd_send_signal via the
  system call), re-verifies the starttime after opening the pidfd,
  and only then signals. A verified kill(2) path remains only as a
  fallback when pidfd support is unavailable.
- Legacy bare-PID entries with no identity are never signalled.
- Post-kill liveness is identity-aware: the witnessed instance must
  match pid + starttime and be non-zombie. A recycled PID is not
  reported as our survivor.
- The suite's cleanup guards are identity-checked as well.
- The session-escape fixture is grounded without changing its
  contract: the intermediate parent now waits until the grandchild
  has written its pidfile (bounded at 10s), then waits 0.5s before
  exiting. The grandchild still setsids, is still reparented before
  the timeout snapshot, and is still scheduled to write after the
  timeout if it survives.

The process-group kill is unchanged: it is scoped to the entry's
own session/process group by construction, not based on historical
PID membership. Cancellation code and semantics are unchanged.

## Suite and controls

DAF09_TIMEOUT_TREE: 16 -> 20 checks. The 16 prior checks are
preserved. Four identity controls were added:

1. Positive control: a live process whose witnessed identity still
   matches is killed through the real _kill_process_tree path.
2. Identity-reuse negative control: a live bystander's PID paired
   with a non-matching starttime is refused; the bystander survives.
3. Bare-PID negative control: a legacy identity-less entry naming
   the bystander is refused; the bystander survives.
4. Gone-instance control: a witnessed entry for an already-exited
   process is a clean no-op.

Results:
- Suite: 20/20.
- Defect-restoring mutant M1 (remove identity verification; bare
  kill): 18/20, failing the identity-reuse and bare-PID negative
  controls.
- Defect-restoring mutant M2 (signal legacy bare entries): 19/20,
  failing exactly the bare-PID negative control.
- flake8 hard select (E9,F63,F7,F82): clean on both changed files.
- Regress x3 on candidate ebe3243: 210/210 GREEN in each leg
  (forward; --twice; --order rev). The DAF09 suite was 20/20 in
  every leg.
- Exact-head CI verified COMPLETE in a separate step before
  merge: Python package run 41251245436 SUCCESS completed
  2026-10-31T23:08:53Z; Form smoke run 41251245385 SUCCESS
  completed 2026-10-31T23:24:57Z (both at head ebe3243).
- Fresh-clone regress at merge 3234966: 210/210 GREEN
  ("REGRESS FINAL: GREEN (order=fwd)").

## Bounded ruling requested

Re-present DAF-09's session-escape coverage for certification on
the evidence above, with identity-safe signalling replacing bare-PID
retention in form/regress.py. No ruling is requested on cancellation
(it is already certified), and no unconditional bystander-safety
claim is made: the claim is specifically that this kill path does
not signal a witnessed-set entry unless the current process is the
witnessed (pid, starttime) instance, with pidfd pinning preferred
where supported. A descendant that escapes and is never witnessed
while attached remains outside the witness mechanism's reach.
