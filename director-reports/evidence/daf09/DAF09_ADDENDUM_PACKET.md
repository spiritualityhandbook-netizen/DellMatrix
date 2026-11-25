# DAF-09 ADDENDUM PACKET — session-escape + cancellation coverage

Status: IN FLIGHT (opened 2026-10-31, cycle after step 3b closure).
Base: main 1ab1afe (PR #168 merge, tree 6e666ec).
Branch: uni/daf09-addendum in ~/workspace/nbd-omega-daf09add.

## Mandate
Director Mode D narrowed DAF-09's certification to executed
coverage: Linux ordinary-descendant cleanup, timeout verdict,
bystander survival. Session-escaping descendants and cancellation
are NOT certified — the submitted suite (7/7) does not exercise
them. Add both checks before claiming those paths proven
(DIRECTOR_FINDINGS_REGISTER.md, DAF-09 entry). Pre-ground:
hidden_files/daf09_addendum_ground.md.

## SWAT unanimity (recorded BEFORE implementation, 4/4)
- CUSTODIAN: agreement. Kill-set evidence must be witnessed
  state: only PIDs observed as descendants while attached, plus
  the entry's own process group. No name/cmdline matching, no
  speculative signalling. Zombie-aware liveness, as in the
  existing suite.
- INTERPRETER: agreement. Verdict semantics unchanged: timeout
  still (False, "TIMEOUT"); cancellation still propagates
  KeyboardInterrupt after cleanup. No new verdict vocabulary.
- SENTINEL: agreement. Scope invariant is the security core:
  the bystander must survive BOTH new checks; widening the kill
  set beyond witnessed descendants would be a scope breach,
  not a fix.
- MECHANIC: agreement. Any tracking during the wait must be
  bounded (short poll interval, /proc snapshot cost per poll
  only) and the suite's added wall time bounded (~15-20s).
  Failing-first: suite checks land before any regress.py fix.
Disposition: UNANIMOUS 4/4 — proceed failing-first; if the
escape check fails, bounded fix in form/regress.py only
(track descendant set during the wait; union into kill set).

## Ground facts (form/regress.py at 1ab1afe)
- run_entry: Popen(start_new_session=True);
  communicate(timeout=TIMEOUT_S); on TimeoutExpired ->
  _kill_process_tree; on KeyboardInterrupt ->
  _kill_process_tree + re-raise.
- _kill_process_tree: snapshot _descendant_pids(root) via /proc
  ppid walk AT KILL TIME; killpg(root group); SIGKILL snapshot;
  bounded reap.
- Escape hole (code-reading NOTE, to be falsified by execution):
  a grandchild that setsid()s and whose parent exits before the
  kill-time snapshot reparents to init — invisible to the ppid
  walk and outside the root's process group.

## Checks added (suite-first)
Escape: entry spawns an intermediate; intermediate spawns a
setsid grandchild (writes its pid; writes marker at +3s; sleeps),
sleeps 1.0s, exits — grandchild reparented before the 2s
timeout snapshot. Assert: TIMEOUT verdict, grandchild pid
recorded, no marker after the write window, grandchild dead.
Cancellation: a driver subprocess runs run_entry (TIMEOUT_S=60)
on a hang fixture; the suite sends SIGINT to the DRIVER only;
assert driver reports INTERRUPTED (KeyboardInterrupt
propagated), tree child dead, no post-cancel marker, bystander
alive.

## Failing-first result (2026-10-31, candidate 2aa1a30)
Suite extended FIRST (16 checks): on unfixed 1ab1afe code —
14/16. Escape check FAILS both assertions (escaping grandchild
wrote its marker; grandchild still alive, pid recorded).
Cancellation PASSES on current code (driver interrupted, tree
child dead, no marker, bystander alive) — recorded honestly as
passing-first coverage, not a defect.

## Fix (form/regress.py only, per SWAT bound)
- _communicate_tracked(proc): communicate in 0.1s slices to the
  same deadline; each slice first unions _descendant_pids into a
  witnessed set stashed on the proc object. Verdict semantics
  unchanged; KeyboardInterrupt still propagates from the slice.
- _kill_process_tree: kill set = kill-time snapshot UNION the
  witnessed set. Scope unchanged: only witnessed descendants +
  the entry's own process group are ever signalled.
Suite after fix: 16/16.

## Mutant
Defect-restoring mutant (witnessed union replaced by an empty
loop, applied only after the real work was committed at
2aa1a30): suite 14/16 — exactly the two escape assertions fail.
Mutant reverted by the inverse edit; git diff verified clean;
suite re-run 16/16 on the restored candidate.

## Regress x3 (candidate 2aa1a30)
Leg 1 (fwd): 209/209 GREEN — durable log
hidden_files/daf09add_regress_leg1.log ("REGRESS FINAL:
GREEN (order=fwd)"). NOTE: the exec session's delivery
falsely reported this leg FAILED (exit 1) at 805s while the
process was verifiably still running (ps + log growth);
final evidence is the log's own summary, per the
verify-don't-trust-delivery rule. No duplicate chain was
launched.
Leg 2 (--twice): 209/209 GREEN both passes ("REGRESS
FINAL: GREEN (order=fwd, twice)", exit 0; log
hidden_files/daf09add_regress_leg2.log).
Leg 3 (--order rev): 209/209 GREEN ("REGRESS FINAL: GREEN
(order=rev)", exit 0; log daf09add_regress_leg3.log).
REGRESS x3 COMPLETE on frozen candidate 2aa1a30.
PR #170 OPEN: https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/170
(head 2aa1a30, base main 1ab1afe).

## Remaining closure phases
Exact-head CI on PR #170 verified COMPLETE in a SEPARATE
step -> merge (merge tree == candidate tree) -> fresh-clone
regress -> ledger + POST_PLAN + register -> Director report
addendum finalized + published to director-reports/ (draft
at ~/workspace/DIRECTOR_REPORT_DAF09_ADDENDUM_DRAFT.md).
Sequencing note: docs PR #169 (CI already verified complete
in a separate step) merges AFTER PR #170, so the code PR
keeps exact merge-tree equality with no redundant regress
x3 re-run — the step 3b merge-in lesson applied in advance.

## Queue note (Director ruling landed mid-cycle)
Step 3b was DECLINED as complete by the Director at 1ab1afe
(in-place sanitization of last_result/Revert state) — NEW
STEP 3c is queued FIRST in the wave, ahead of step 5b.
Ground: hidden_files/step3c_ground.md. DAF-02 remains OPEN.
Docs PR #169 (step 3b report): exact-head CI verified COMPLETE
this cycle in a separate step (package 41223175102 pass;
smoke 41223175006 SUCCESS) — merge is the next cycle's first
action, per the separate-step discipline.

## CLOSURE ADDENDUM (2026-10-31)
PR #170 merged as f1c02051af42de0fc7c35e137111ca746b3800bc
(candidate 2aa1a30, merge tree 1e5019b == candidate tree;
parents 1ab1afe + 2aa1a30). Exact-head CI verified COMPLETE
in a separate step before merge (package 41227141641 SUCCESS
completed 17:59:41Z; smoke 41227141655 SUCCESS completed
18:15:54Z). Fresh-clone regress at merge f1c0205: 209/209
GREEN. Ledger row + POST_PLAN note done; register DAF-09
addendum -> IMPLEMENTED-VERIFIED (widened coverage
re-presented). Director report finalized:
DIRECTOR_REPORT_DAF09_ADDENDUM.md, published to
director-reports/ via the follow-up docs PR after PR #169.
NOT certified.
