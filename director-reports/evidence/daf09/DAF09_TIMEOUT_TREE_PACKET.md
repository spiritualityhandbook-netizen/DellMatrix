# DAF-09 PACKET — regress timeout kills the whole process tree
Director order step 2 (Director Certification Audit 2026-10-31, §8.2 / DAF-09 P2)
Status: IMPLEMENTED-VERIFIED by Uni, awaiting Director re-ruling (step 14). NOT certified.

## Finding
DAF-09 (P2): form/regress.py run_entry used subprocess.run(timeout=...);
on timeout only the direct child was killed. A descendant spawned by the
timed-out entry survived and could write afterwards, contaminating later
suites and invalidating timeout isolation.

## SWAT unanimity (recorded BEFORE implementation, 4/4)
- CUSTODIAN: timeout must leave no writer alive; state before/after and
  marker witness required; isolated synthetic fixtures only.
- INTERPRETER: verdict semantics unchanged — timeout stays (False, "TIMEOUT");
  no other verdict path may change.
- SENTINEL: kill scope must be exactly the tree rooted at the spawned entry;
  an unrelated bystander must survive (proven in-suite).
- MECHANIC: no timeout weakening (900s bound unchanged); reap must be
  bounded; cost only on the timeout/cancel path.
Unanimous: fix inside the canonical runner only; no second runner.

## Failing-first probe (on b352e39, unmodified)
Synthetic fixture spawns a child that writes a marker 3s after start,
then sleeps 30s. TIMEOUT_S patched to 2 in the probe process only.
Result: run_entry -> (False, "TIMEOUT") at 2.0s, marker_exists: True
(descendant wrote after the timeout). Defect reproduced as executed.

## Implementation (branch uni/daf09-timeout-tree-kill, candidate c104043, tree 4882544)
form/regress.py only (plus the new suite):
- run_entry now uses Popen(start_new_session=True) — entry in its own
  session/process group.
- On TimeoutExpired or KeyboardInterrupt: _kill_process_tree snapshots
  descendants from /proc parent links BEFORE killing (children reparent
  once the parent dies), SIGKILLs the process group, SIGKILLs every
  snapshotted descendant (covers descendants that left the group),
  kills and reaps the entry (bounded wait), then a bounded liveness
  settle (zombies treated as dead). Returns (False, "TIMEOUT") unchanged.
- Success path verdict logic (rc/token/count/traceback) byte-preserved
  via a _Completed shim over the Popen result.
form/daf09_timeout_tree_test.py: 7 checks — TIMEOUT verdict, bound
respected, descendant started, no post-timeout marker, descendant dead,
bystander survives, fast-entry positive control.

## Evidence
- Probe after fix: (False, "TIMEOUT") at 2.0s, marker_exists: False,
  child dead; positive control core_ii_smoke (True, rc=0 last=36/36).
- Targeted suite: DAF09_TIMEOUT_TREE 7/7.
- Mutant (defect-restoring: timeout kills only the direct child):
  suite FAILS on "no post-timeout marker write" (6/7, smoke False).
  Restored code: 7/7. Mutant reverted from a saved copy, diff verified.
- Neighborhoods (passk, fresh copies): passk_test, regress_coverage_test,
  daf09 suite, launchers_test — all GREEN 1/1.
- Full regress x3 on candidate c104043 (logs /tmp/daf09_regress_{fwd,twice,rev}.log): fwd 205/205 GREEN; --twice pass1 205/205 + pass2 205/205 GREEN; --order rev 205/205 GREEN. New suite inside all legs at 7/7.
- Exact-head CI: see closure addendum below.
- Merge / fresh-clone: see closure addendum below.

## Closure addendum (verified 2026-10-31, continuation cycle)
- PR #163 created 2026-10-31T11:00:23Z, head c104043a39c33a988cea71a5543233862fc04e82.
- Exact-head CI verified COMPLETE before merge in a separate step:
  Python package run 41195033715 SUCCESS (build 3.10 + 3.11, completed
  11:01:22Z); Form smoke run 41195033730 SUCCESS (completed 11:14:19Z);
  merge followed at 11:15:11Z.
- Merge: e4b13ec217435a2b7f938482067c6a43db8420de, normal merge commit,
  parents b352e39 (prior main) + c104043 (candidate); merge tree
  48825447855ed8b775de4de5cbb8e340ccf73443 == candidate tree
  48825447855ed8b775de4de5cbb8e340ccf73443; diff candidate..merge empty.
- Fresh-clone regress at the merge (clone HEAD e4b13ec, main):
  205/205 GREEN, daf09 suite 7/7 inside (log daf09_freshclone_regress.log,
  witnessed in the 2026-10-31 06:49 CDT continuation run before /tmp
  cleanup). Independent targeted re-verification in that same run:
  a second fresh clone at e4b13ec ran form.daf09_timeout_tree_test
  directly — DAF09_TIMEOUT_TREE 7/7, exit 0.
- Post-merge CI at exact head e4b13ec also SUCCESS: Python package
  run 41196080009, Form smoke run 41196080002 (per 06:37 CDT heartbeat
  verification).
- Status: IMPLEMENTED-VERIFIED, awaiting Director re-ruling (step 14).
  NOT certified. Regress at 205.

## Limits
Linux//proc is the proven platform (the project's runtime). Where /proc
is unavailable the process-group kill still applies; a descendant that
both leaves the group AND is on a non-/proc platform is the documented
residual — no such platform is in use. A descendant that creates its own
session AND whose parent chain is broken before the snapshot is outside
the proven scope; ordinary and group-escaping descendants are covered.
