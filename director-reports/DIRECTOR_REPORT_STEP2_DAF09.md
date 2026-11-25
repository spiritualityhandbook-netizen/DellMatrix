# Director Report — Director Order Step 2: DAF-09

Status: IMPLEMENTED-VERIFIED by Uni, awaiting Director
re-ruling. NOT certified.
Date: 2026-10-31. From: Uni.
Authority: Director Certification Audit 2026-10-31,
section 8 step 2 / DAF-09 (P2); per-circuit Director
reporting cadence adopted by Ace 2026-10-31 (one report
per closed circuit, held for the Director; step 14
becomes an index packet over these reports).
This is the catch-up report for step 2, which closed
2026-10-31 before that cadence was adopted.

## Scope of this report

One finding only: DAF-09. No other finding, circuit, or
certification scope is presented for ruling here.

## The finding (as ruled)

DAF-09 (P2): `form/regress.py` `run_entry` used
`subprocess.run(timeout=...)`; on timeout only the direct
child was killed. A descendant spawned by the timed-out
entry survived and could write afterwards, contaminating
later suites and invalidating timeout isolation.

## Fix

Branch `uni/daf09-timeout-tree-kill`, production change in
`form/regress.py` only, plus the new suite
`form/daf09_timeout_tree_test.py`:

- `run_entry` now uses `Popen(start_new_session=True)` —
  the entry runs in its own session/process group.
- On `TimeoutExpired` or `KeyboardInterrupt`:
  `_kill_process_tree` snapshots descendants from /proc
  parent links BEFORE killing (children reparent once the
  parent dies), SIGKILLs the process group, SIGKILLs every
  snapshotted descendant (covers descendants that left the
  group), kills and reaps the entry (bounded wait), then
  a bounded liveness settle (zombies treated as dead).
- Verdict semantics unchanged: timeout still returns
  `(False, "TIMEOUT")`; success-path verdict logic
  (rc/token/count/traceback) byte-preserved via a
  `_Completed` shim. The 900s bound was not weakened.
- SWAT unanimity 4/4 recorded BEFORE implementation
  (Custodian / Interpreter / Sentinel / Mechanic);
  Sentinel's condition — an unrelated bystander process
  must survive — is proven in-suite.

## Evidence

- Failing-first probe (on b352e39, unmodified): synthetic
  fixture spawns a child that writes a marker 3s after
  start, then sleeps 30s; timeout patched to 2s in the
  probe process only. Result: `(False, "TIMEOUT")` at
  2.0s, marker_exists: True — descendant wrote after the
  timeout. Defect reproduced as executed.
- Probe after fix: `(False, "TIMEOUT")` at 2.0s,
  marker_exists: False, child dead. Positive control
  `core_ii_smoke` (True, rc=0, last=36/36).
- Targeted suite: DAF09_TIMEOUT_TREE 7/7 — TIMEOUT
  verdict, bound respected, descendant started, no
  post-timeout marker, descendant dead, bystander
  survives, fast-entry positive control.
- Mutant (defect-restoring: timeout kills only the direct
  child): suite FAILS on "no post-timeout marker write"
  (6/7, smoke False). Restored code: 7/7. Mutant reverted
  from a saved copy, diff verified.
- Neighborhoods: passk_test, regress_coverage_test,
  daf09 suite, launchers_test — all GREEN.
- Full regress x3 on candidate c104043: fwd 205/205
  GREEN; --twice pass1 205/205 + pass2 205/205 GREEN;
  --order rev 205/205 GREEN. New suite inside all legs.
- Exact-head CI, verified COMPLETE in a separate step
  before merge: Python package run 41195033715 SUCCESS
  (build 3.10 + 3.11, completed 2026-10-31T11:01:22Z);
  Form smoke run 41195033730 SUCCESS (completed
  2026-10-31T11:14:19Z). Merge followed at 11:15:11Z.
- Merge: PR #163, merge commit
  e4b13ec217435a2b7f938482067c6a43db8420de, normal merge
  commit, parents b352e39 + c104043a39c33a988cea71a5543233862fc04e82;
  merge tree 48825447855ed8b775de4de5cbb8e340ccf73443 ==
  candidate tree 48825447855ed8b775de4de5cbb8e340ccf73443;
  diff candidate..merge empty.
- Fresh-clone regress at the merge (clone HEAD e4b13ec):
  205/205 GREEN, daf09 suite 7/7 inside. Independent
  re-verification in a second fresh clone at e4b13ec:
  `form.daf09_timeout_tree_test` 7/7, exit 0.
- Post-merge CI at exact head e4b13ec: Python package
  run 41196080009 SUCCESS; Form smoke run 41196080002
  SUCCESS.
- Regress count after closure: 205 suites. Main at the
  time of closure: e4b13ec.

## Claim-to-evidence index

- Full packet (probe, implementation, closure addendum):
  `DAF09_TIMEOUT_TREE_PACKET.md` in ~/workspace.
- Register row: DIRECTOR_FINDINGS_REGISTER.md, DAF-09 ->
  IMPLEMENTED-VERIFIED.
- Ledger row: DELLMATRIX_GDP_LEDGER.md, DAF-09 row;
  POST_PLAN_PROGRAM.md step-2 closure note.
- Code and suite: `form/regress.py`,
  `form/daf09_timeout_tree_test.py` at merge e4b13ec.
- PR / CI: GitHub PR #163; CI runs 41195033715,
  41195033730 (candidate, pre-merge), 41196080009,
  41196080002 (merge, post-merge).

## Limits

Linux / /proc is the proven platform (the project's
runtime). Where /proc is unavailable the process-group
kill still applies; a descendant that both leaves the
group AND is on a non-/proc platform is the documented
residual — no such platform is in use. A descendant that
creates its own session AND whose parent chain is broken
before the snapshot is outside the proven scope; ordinary
and group-escaping descendants are covered.

## Decision requested

Re-rule DAF-09 only, on the evidence above:
certify the bounded scope, accept with noted exception,
or decline with the defect that remains. No other
finding is bundled into this ruling, and nothing in this
report is certified until the Director rules.
