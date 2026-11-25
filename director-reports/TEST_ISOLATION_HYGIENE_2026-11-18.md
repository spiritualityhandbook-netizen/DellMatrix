# TEST-ISOLATION HYGIENE — C7.Profile shared-state oracle repair (2026-11-18)

**Authorization:** Director comment 6989087312 on PR #489 (R19 regression
reliability ruling): Uni authorized to repair the test-hygiene defect in a
separate failing-first circuit. **Fix-first: no merge authorization
requested by this circuit, no credit claimed.** Campaign ×3 deferred to
the main session (state-sharing campaigns are main-session acts).

**Base:** main `9bc0c9b5dee282828b5e510e9e0035a5c6c2284f`.
**Scope:** test files only. No product code changed.

## 1. The defect (verified first-hand)

`form/dell_matrix/profile_board.py` is CORRECT: a disposable bench owner
is named `ProfileBench<pid>_<n>[tag]` (`_disposable_owner`), the board
disposes exactly that owner's artifacts (`_dispose`, glob `*{owner}*`)
in a `finally`, and a disposal failure is disclosed on the receipt as
`cleanup_error` rather than swallowed.

`form/c7profile_test.py` was the defect — a **test-oracle scope error**:

- t9 (`t9_disposable_cleaned`) globbed `*ProfileBench*` across the
  WHOLE shared `form/state` directory and demanded zero.
- t10 (`t10_no_timings_store`) globbed EVERY file in the shared
  directory and demanded none be named `*profilebench*` /
  `*profile_timing*`.

A bench whose process is killed (the R19 campaign's VM-restart death,
2026-11-18 18:02Z) never runs its dispose step, so its artifacts stay
behind as corpses: `ideas_ProfileBench<pid>_<n>` (dir),
`nursery_ProfileBench<pid>_<n>.json`, and an orphaned
`.dmtmp.<pid>.<hex>` atomic-save temp. From then on EVERY c7profile run
failed t9/t10 forever — 34–35/36 — regardless of the code under test.
Observed live in the PR #489 campaign: leg 3 (reversed order) RED
301/302, sole failure `form.c7profile_test:smoke` 35/36; corpses
present standalone 34–35/36, purged 36/36.

## 2. Failing-first evidence (RED captured before repair)

New adversarial suite `form/test_isolation_hygiene_test.py` plants a
FOREIGN stale artifact set (dead pid 99999983, confirmed not alive:
bench owner dir + nursery file + orphaned `.dmtmp` + a
timings-store-shaped file), then runs the real c7profile suite as a
subprocess — twice — and asserts the correct contract: full pass,
foreign artifacts byte-identical afterwards, and the run's own
artifacts all cleaned.

Against the UNREPAIRED test (log:
`hidden_files/hygiene_logs/failing_first_RED.txt` in the goal
workspace):

```
[PASS] h0_dead_pid_confirmed
[PASS] h1_fixture_planted
[FAIL] h2_c7profile_green_with_corpses_run1 | rc=1 tally==== 34/36 ===
       fails=[t9_disposable_cleaned | <the 4 planted foreign paths>,
              t10_no_timings_store  | <the same 4 planted paths>]
[PASS] h3_own_artifacts_cleaned_run1
[FAIL] h2_c7profile_green_with_corpses_run2 | rc=1, 34/36, same two fails
[PASS] h3_own_artifacts_cleaned_run2
[PASS] h4_foreign_artifacts_untouched
TEST_ISOLATION_HYGIENE: 5/7
```

The RED is precise: the only failing checks are t9/t10, their details
name ONLY the planted foreign files, and h3 PASSes pre-repair — the
runs under test had already cleaned their own artifacts perfectly.
The oracle's scope was the whole defect.

## 3. Repair (form/c7profile_test.py only)

Assertions are scoped to the artifacts of the runs THIS test process
performed; no benchmark correctness check was skipped, loosened, or
re-pinned:

- `_own_bench_artifacts()` — glob `*ProfileBench{os.getpid()}_*`:
  this process's bench artifacts exactly (owner names embed the pid;
  the trailing `_` excludes prefix-collision pids — verified by a
  helper scope check planting own / foreign / prefix-collision /
  shorter-pid names: own matched exactly, all others excluded).
  Covers calibration (`CAL`) owners and every section's runs.
- `_owner_artifacts(owner)` — t9 additionally asserts zero artifacts
  for the exact owners named on this section's receipts (ra/rb
  `profile_report.workload.owner`): direct evidence the runs under
  test disposed of themselves.
- t10 — own bench artifacts must be gone (as t9), and no
  `profile_timing` file may have APPEARED during the test: the set
  is snapshotted before any benchmark runs and diffed at t10. The
  receipt-only-timings contract keeps full strength for these runs;
  a foreign pre-existing file is no longer evidence against them.

Nothing foreign is deleted by the repair, and no cleanup was added:
crash recovery of orphaned state (incl. dead-pid `.dmtmp` temps)
belongs to the state layer — its own suite
(`form/atomic_write_boundaries_test.py`, 67/67 here) pins dead/live
temp handling. One honest bound: if a dead bench's pid is later
REUSED by a c7profile process, its corpses match that process's pid
scope; the receipt-owner arm remains exact regardless.

## 4. Post-repair focused evidence

- Adversarial suite: **7/7**, exit 0 (both corpse-planted c7profile
  runs 36/36; corpses byte-identical; own artifacts cleaned).
  Harness-shape invocation (subprocess import + smoke()) rc=0,
  final tally token `TEST_ISOLATION_HYGIENE: 7/7`.
- `form.c7profile_test` standalone ×3 on clean state: **36/36** each.
- Neighbors: `form.dell_matrix.profile_board` smoke **1/1**
  (verdict COMPLETE); `form.c7schema_test` **33/33**;
  `form.atomic_write_boundaries_test` **67/67**;
  `form.mandell.d1_registry_leaf4_test` **36/36**.
- Suite registered in `form/regress.py` immediately after
  `form.c7profile_test:smoke`, house pattern (string entry + comment).

## 5. leaf4 (d1_registry_leaf4_test) — verdict: UNPROVEN, untouched

Requirement was repair ONLY on a proven owner/interference path.
Minimal reproduction battery at this head (all runs first-hand;
logs in the goal workspace `hidden_files/hygiene_logs/`):

- standalone ×2: 36/36, 36/36
- after its regress predecessors leaf + leaf2 + leaf3 (consecutive
  in `form/regress.py`): 36/36 (predecessors 22/22, 33/33, 44/44)
- with the ProfileBench corpse set planted: 36/36 (leaf4 never globs
  bench artifacts; it does not share the c7profile oracle defect)
- ×5 consecutive loop: 36/36 every run
- immediately after a full c7profile run (reversed-order adjacency):
  36/36

No run reproduced the 35/36 signature. The original CI observation
(smoke run 44364308530, pass 1) never named its failing check, and
the full-campaign predecessor set (~150 suites of accumulated state)
cannot be exercised from a build lane — full regression campaigns
are main-session acts. The interference path is therefore NOT
proven; per the ruling, leaf4 is left byte-untouched and the
question returns with this evidence.

## 6. Product-defect verdict

**No product save/restore defect was discovered.** The defect is
purely test-oracle/isolation, located in `form/c7profile_test.py`'s
whole-directory assertions. The product side behaved as designed
throughout: owner-scoped disposal, honest `cleanup_error`
disclosure, and atomic-write temps whose recovery semantics are
pinned by their own suite. A killed process cannot execute its
dispose step; that is crash semantics, not a save/restore defect.

## 7. Ask

Director/Keeper review of the scoped-oracle repair and the leaf4
UNPROVEN return. On acceptance, the main session runs the deferred
campaign ×3 (this PR's head) and PR #489's gate re-presents with a
hygiene-clean campaign. No merge is requested by this circuit.

## REBASE ADDENDUM (2026-11-18)

Rebased onto post-#491 main `389d360fa60dff1d8c8aee6d119a55062f01d8ac`
(#491 merged); new head `130c8f206df783fb187f93accaa40dd9f27b07dd`.
Conflicts: `director-reports/INDEX.md` only, resolved as a UNION
(both the R19SIB row from main and this circuit's row kept);
`form/regress.py` auto-merged — union verified in source: main's
`form.r19sib_count_door_test` registration intact, and
`form.test_isolation_hygiene_test:smoke` registered immediately
after `form.c7profile_test:smoke` as originally placed. Diff vs new
main is exactly this circuit's original 5-file set (+396/−4); the
repair itself (`form/c7profile_test.py`,
`form/test_isolation_hygiene_test.py`) is byte-identical to the
pre-rebase head `45525bdae146e90edbfe04ad7778af6e2ef782a1`.
Focused verification at the new head: test_isolation_hygiene 7/7,
c7profile 36/36, r19sib_count_door 45/45. The gate campaign ×3 runs
at this head from the main session, sequentially after the R19
campaign. Campaign r2's leg-1 failure is classified as
simultaneous-start concurrency interference in the p2 proof cluster
(all failed suites pass standalone); that classification stands.
