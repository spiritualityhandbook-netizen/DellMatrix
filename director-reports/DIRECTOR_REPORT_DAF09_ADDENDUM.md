# DIRECTOR REPORT — DAF-09 ADDENDUM (session-escape + cancellation)

Evidence submitted for re-ruling. A report is evidence, never a
certificate. Merged != certified.

## Ruling this answers
Director Mode D (2026-10-31): DAF-09 CERTIFIED WITH NOTED
EXCEPTIONS, narrowed to executed coverage (Linux ordinary-
descendant cleanup, timeout verdict, bystander survival).
Session-escaping descendants and cancellation were NOT
certified because the submitted suite did not exercise them.

## Frozen candidate
Candidate: 2aa1a30eec46c1e276857af3ae91bb9135ba086a
Candidate tree: 1e5019b02613fb43872bcac5414db6d74e289600
Base: main 1ab1afeacbcef7f519c7138c6c617c1e0365e732 (PR #168 merge)
PR: #170 — merged as f1c02051af42de0fc7c35e137111ca746b3800bc
Merge tree: 1e5019b02613fb43872bcac5414db6d74e289600 == candidate tree
Merge parents: 1ab1afe + 2aa1a30

## What was added
Suite form/daf09_timeout_tree_test.py: 7 -> 16 checks.
- Session-escape check: entry -> intermediate -> grandchild
  that setsid()s; intermediate exits 1.0s in, reparenting the
  grandchild to init before the 2s timeout snapshot.
- Cancellation check: driver subprocess runs an entry with a
  60s bound; SIGINT is sent to the driver only; the driver's
  KeyboardInterrupt path must kill the tree and propagate.

## Failing-first (base 1ab1afe)
14/16. The escape check failed both assertions: the escaping
grandchild wrote its post-timeout marker and remained alive —
a kill-time /proc ppid snapshot plus process-group kill cannot
see a descendant that has both setsid()ed and been reparented.
The cancellation checks passed on the unfixed code (coverage
widening, no defect claimed there).

## Fix (SWAT unanimity 4/4 recorded before implementation)
form/regress.py only:
- run_entry now waits via _communicate_tracked: 0.1s slices to
  the same deadline, witnessing the descendant set (/proc ppid
  walk) during the wait and stashing the union on the proc.
- _kill_process_tree kills the union of the kill-time snapshot
  and the witnessed set, plus the entry's process group.
- Scope invariant preserved: only witnessed descendants and
  the entry's own group are ever signalled; bystander survival
  is asserted in both new checks. Verdict semantics unchanged
  (TIMEOUT verdict; KeyboardInterrupt re-raised).

## Results
- Suite after fix: 16/16.
- Defect-restoring mutant (witnessed union disabled): 14/16,
  exactly the two escape assertions fail. Mutant reverted by
  inverse edit, diff verified clean; suite re-verified 16/16.
- Regress x3 on candidate 2aa1a30: 209/209 GREEN each leg
  (fwd; --twice both passes; --order rev). Logs:
  hidden_files/daf09add_regress_leg1/2/3.log.
- Exact-head CI verified COMPLETE in a separate step before
  merge: Python package run 41227141641 SUCCESS completed
  2026-10-31T17:59:41Z; Form smoke run 41227141655 SUCCESS
  completed 2026-10-31T18:15:54Z.
- Fresh-clone regress at merge f1c0205: 209/209 GREEN (log hidden_files/daf09add_freshclone_regress.log; "REGRESS FINAL: GREEN (order=fwd)").

## Bounded ruling requested
Widen the DAF-09 certificate's executed coverage to include
session-escaping descendants (witnessed during the wait) and
cancellation, on the evidence above. Known limit, stated
plainly: a descendant that escapes AND is never witnessed
while attached (e.g. spawned and reparented entirely within
one 0.1s poll slice) is outside this mechanism's reach; no
such case is claimed. Cancellation coverage is the SIGINT /
KeyboardInterrupt path exercised above, on Linux.
