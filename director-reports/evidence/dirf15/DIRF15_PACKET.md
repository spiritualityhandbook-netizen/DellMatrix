# DIR-F15 PACKET — Diff comparator: absent key vs stored None (Dell 89)

Status: CLOSED 2026-11-01 — IMPLEMENTED-VERIFIED (closure addendum at end)
Base: main f24f7b4 (verified via gh API this run). Branch: uni/dirf15-diff-none
Worktree: ~/workspace/nbd-omega-dirf15
Register: DIR-F15 P2 OPEN — step 9 certificate carves out the
null-membership case until repaired. Ground:
hidden_files/dirf15_ground.md (complete, code-verified).

## Director's counterexample (on merge 2abf04c)
Seed store with nullable: None; public 86[Delete] :: nullable
succeeds; 89[Diff]: before contains the key, after lacks it,
yet changed=[] and ok=True. Cause (verified in fresh clone at
f24f7b4, spectrum_ops.py Diff branch): the comparator builds
the union key set correctly, then compares with plain
.get(k) != .get(k) — None for both "absent" and "stored None".

## SWAT Director's-eye pre-mortem (BEFORE implementation)
- Custodian: one comparator site only (searched form/ — no
  second last_diff/changed authority; core_ii_exec.py:22 only
  declares the field). Fix must not touch baseline capture,
  missing-baseline refusal, changed ordering, or message format.
- Interpreter: the contract is MEMBERSHIP change OR value
  change => key in changed. changed stays a plain key list;
  do NOT annotate add/remove kind (no register basis, would
  break certified consumers matching "Diff changed={changed}").
- Sentinel: over-broad repairs are the risk — "None always
  changed" would falsely report a retained None. A retained-
  None guard witness is mandatory. Seeding is direct state
  seeding (Director's own probe method; store is
  Dict[str, Any]); the suite must say so and must NOT claim a
  public writer emits None (string-only Set cannot).
- Mechanic: minimal predicate: (k in b) != (k in a) or
  b.get(k) != a.get(k). Defect-restoring mutant = revert to
  plain .get equality; witnesses must fail, guards must pass.
- Director's-eye attacks anticipated: (1) addition direction
  as well as removal; (2) transaction baseline as well as
  immediate; (3) retained None NOT reported; (4) null->value
  and value->null still reported; (5) missing-baseline refusal
  byte-identical; (6) persistence of a stored None on
  save/load — out of repair scope (baselines are session-only
  by certified design); if a probe shows None drops on
  save/load that registers as a SEPARATE finding, not folded in.
SWAT agreement: 4/4 on the one-site membership-aware fix and
the witness matrix below. Per DIR-WF-001 amendment, unanimity
is recorded as method, not as a truth gate; no dissent recorded.

## Witness matrix (extend form/step9_diff_test.py, 17 -> 24)
W1 immediate removal (Director's reproducer): seed
  nullable=None, public Delete, Diff => changed=['nullable'],
  before={'nullable': None}, after={}. FAILING-FIRST expected.
W2 immediate addition: baseline seeded via _ckpt into
  st.diff_baseline (store without nullable), then direct-seed
  nullable=None, Diff => changed=['nullable']. FAILING-FIRST.
W3 transaction removal: seed nullable=None, Try, Delete,
  Diff baseline=transaction => changed=['nullable']. FAILING-FIRST.
W4 transaction addition: Try on empty store, direct-seed
  nullable=None inside frame, Diff baseline=transaction =>
  changed=['nullable']. FAILING-FIRST.
W5 retained None guard: seed nullable=None, Set a=1 (baseline
  includes nullable), Diff => changed=['a'], nullable absent.
  Passes pre- and post-fix (over-broad-repair guard).
W6 null->value guard: seed nullable=None, Patch nullable=x,
  Diff => changed=['nullable']. Passes pre/post (guard).
W7 value->null guard: baseline seeded via _ckpt (nullable='v'),
  direct-seed nullable=None, Diff => changed=['nullable'].
  Passes pre/post (guard).

## Failure-class siblings (§15)
exchange.py:620-622 seed.get(k) vs journal dicts — different
shape (explicit key set, Exchange domain), no reproducer;
NOT widened into this circuit (ground §siblings).

## Closure gates (standing discipline)
Failing-first -> fix -> suite -> defect-restoring mutant ->
neighborhoods (d1_registry_spectrum, spectrum_closure,
unified_runtime, step9 suite itself) -> regress x3 sequential
(fwd / --twice / --order rev) -> PR -> exact-head CI verified
COMPLETE in a SEPARATE step -> merge (tree equality) ->
fresh-clone regress -> ledger + POST_PLAN + register ->
Director report published to director-reports/ + INDEX row.
NOT certified; report is evidence submitted for Director
ruling when he returns (Director asleep — Trinity mode).

## Execution record (2026-11-01, 13:10 CST cycle run)
Candidate: 981d524 (tree cb5c39e) on base f24f7b4,
branch uni/dirf15-diff-none, PR #200 OPEN.
- Failing-first: suite extended FIRST; on unfixed code
  STEP9_DIFF 20/24 — exactly W1-W4 fail, each with
  changed=[] on a None-membership case (immediate
  removal = the Director's reproducer verbatim;
  immediate addition; transaction removal; transaction
  addition). W5-W7 guards + all 17 original pass.
  Log: dirf15_logs/failing_first.log.
- Fix: one site, spectrum_ops.py Diff branch —
  (k in _bs) != (k in _as) or _bs.get(k) != _as.get(k),
  with an explanatory comment. Nothing else in the
  runtime changed (git diff: spectrum_ops.py +10/-1,
  step9_diff_test.py +126).
- Suite fixed: STEP9_DIFF 24/24 (dirf15_logs/suite_fixed.log).
- Mutant: predicate reverted to plain .get equality via
  inverse edit => 20/24, only W1-W4 fail
  (dirf15_logs/mutant.log); fix restored via inverse
  edit, re-verified 24/24, diff inspected.
- Neighborhoods: d1_registry_spectrum 48/48,
  spectrum_closure 57/57, unified_runtime 37/37,
  step7_control_verdicts 28/28, step8_transactions 22/22.
- Anticipated probe (pre-mortem item 6): stored None
  survives save/load with membership intact
  (dirf15_probe.py) — NO separate finding.
- Regress x3 on 981d524, foreground, logs in
  dirf15_logs/: leg1 fwd 218/218 GREEN; leg2 --twice
  pass1 218/218 + pass2 218/218 GREEN; leg3 --order rev
  218/218 GREEN.
REMAINING GATES: exact-head CI on 981d524 verified
COMPLETE SUCCESS in a SEPARATE step -> merge (normal
merge commit, tree equality) -> fresh-clone regress ->
ledger + POST_PLAN + register DIR-F15 ->
IMPLEMENTED-VERIFIED -> Director report
DIRECTOR_REPORT_DIRF15.md + publication PR with INDEX
row SUBMITTED. NOT certified.

## Closure addendum (2026-11-01, 13:30 CST cycle run)
- Exact-head CI on 981d524 verified COMPLETE SUCCESS in a
  SEPARATE step (this run, distinct from the PR-creation
  run): package run 41343445184 SUCCESS (build 3.10/3.11);
  smoke run 41343445193 SUCCESS — job + check-runs API show
  smoke completed 2026-11-01T20:03:35Z. DISCLOSURE: a first
  `gh run watch` reported success while the run-level API
  still read in_progress (updated_at frozen at start);
  Uni did NOT merge on that conflict. The job-level and
  check-runs APIs then independently showed smoke
  completed/success, and only then was the merge called.
- PR #200 MERGED as 8eb76e5110a793d251eb05de4e44bfc2ded2550c
  at 20:04:01Z (normal merge commit; merge tree cb5c39e ==
  candidate tree cb5c39e; parents f24f7b4 + 981d524).
- Fresh-clone regress at merge 8eb76e5 (fresh-clone HEAD
  verified 8eb76e5 before the run): 218/218 GREEN
  (dirf15_logs/freshclone_regress.log).
- Ledger row + POST_PLAN note + register DIR-F15 ->
  IMPLEMENTED-VERIFIED done this run.
- Director report DIRECTOR_REPORT_DIRF15.md finalized;
  publication PR follows under the same discipline
  (INDEX row SUBMITTED; forthcoming line updated to
  steps 10-11). NOT certified — awaiting Director ruling
  on his return (Trinity mode, Director asleep).
