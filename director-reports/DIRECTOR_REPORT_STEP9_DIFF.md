# DIRECTOR REPORT — STEP 9: DIFF (B13/B14)

## Ruling requested / identity / exceptions
Requested: bounded re-ruling on B13 and B14 within the
scope below. Identity: PR #190 merged as 2abf04c;
candidate 6c766bd, tree 020fbc8 (merge tree == candidate
tree; parents 13e1df6 + 6c766bd). Exceptions: none known
within the presented scope; limitations below.
Status: SUBMITTED 2026-11-01 — circuit closed (frozen
candidate, CI, merge and fresh-clone recorded in
Evidence). This report is evidence submitted, never a
certificate. Merged != certified.

## Findings addressed
- B13 Diff: Diff with no established baseline claimed
  "changed=[] baseline=current" — a vacuous success that
  reports no change against a baseline that never
  existed.
- B14 Set/Diff: Set did not participate in the shared
  baseline lifecycle, so a Set-only change was invisible
  to a following Diff (visible only after an unrelated
  writer captured a baseline).

## Before (failing-first probe, reproduced 2026-11-01 on
## unmodified ea44bb8 by hidden_files/step9_probe.py,
## public seed path, synthetic owners)
- P1 fresh Diff: ok=True "Diff changed=[] baseline=
  current" — B13 vacuous claim.
- P2 Set-only then Diff: store {'a':'1'} but Diff still
  "changed=[] baseline=current" — B14 Set invisible.
- P3 repeated fresh Diffs: both vacuous current claims.
- P4 Set then Copy: Diff reports only the Copy change —
  Set visible only via an unrelated writer's baseline.
- P5 typed-roles Set then Diff: store {'tk':'tv'} but
  changed=[] baseline=current — B14 on the typed path.
- P6 save/load: loaded store {'tk':'tv2'}, Diff claims
  changed=[] baseline=current — vacuous after load.

## After (candidate 6c766bd; runtime identical to
## 6947f1b — see Evidence)
All six probe lines flip: P1/P3/P6 refuse with
baseline_missing; P2/P5 Set is visible to Diff
immediately, on both Set branches.

## Mechanism (shared baseline authority, no second one)
- spectrum_ops Dell 89 (Diff) arm: the "current"
  fallback is DELETED. With no baseline, Diff returns
  ok=False, reason baseline_missing, last_diff
  {baseline:"missing", available:False, changed:None,
  before:None, after:current store} — changed is
  unknown, never fabricated as empty. The transaction
  and immediate branches are unchanged. _note_mutation
  is unchanged in behavior; its docstring now states
  the shared authority.
- query_ops Dell 55 (Set) arm: BOTH branches (typed
  roles and legacy) capture via _note_mutation(st,
  "set", lab, _ckpt(st)) after refusal checks,
  immediately before the mutation. The ambiguous legacy
  Set still refuses, with no capture and no mutation.
- core_ii_exec: CoreIIState gains a declared
  diff_baseline field (default None; session-only, not
  serialized — CORE_II_DURABLE unchanged), so a loaded
  state honestly has no baseline until a writer
  captures one.
- Dell cards 55/89/95 rewritten to the new contract;
  DELL_PROOF_CARDS.md regenerated from live probes
  (bare Diff is now a named failure: baseline_missing).

## Evidence
- Suite STEP9_DIFF 17/17 (regress entry 215);
  re-verified 17/17 on the final candidate 6c766bd in
  the closing run (passk 1/1 GREEN).
- Mutants (defect-restoring, all killed, all reverted
  by inverse edit and diff-verified clean, on
  6947f1b): M1 vacuous "current" fallback restored
  11/17 (exactly the B13 checks); M2 Set capture
  removed (both branches) 7/17; M3 Diff clears baseline
  on read 15/17 (exactly the repeated-read checks);
  M4 Set captures AFTER mutation 10/17. Suite
  re-verified 17/17 after all reverts.
- Neighborhoods: d1_registry_spectrum 48/48,
  spectrum_closure 57/57, d1_registry_coreii_a 30/30,
  unified_runtime 37/37, core_ii_persist 20/20,
  core_ii_smoke 36/36, d1_proof_cards 6/6, step8 22/22,
  step7 28/28, step6 34/34 — all GREEN.
- Regress x3 on 6947f1b: fwd 215/215, --twice 215/215
  both passes, --order rev 215/215 — all GREEN.
- Candidate refresh: main 13e1df6 (PR #191, workflow
  integration) merged in, forming 6c766bd. Delta vs
  6947f1b verified by git diff: 24 files, all under
  director-reports/, zero form/ runtime change — the
  mutant and neighborhood evidence above therefore
  applies to the identical runtime delta.
- Regress x3 RE-RUN on 6c766bd (step 3b precedent):
  fwd 215/215 GREEN (522s); --twice pass1 215/215 +
  pass2 215/215 GREEN (1056s); --order rev 215/215
  GREEN (518s). Logs: hidden_files/step9_logs/
  reg_6c766bd_leg1_fwd.log, reg_6c766bd_leg2_twice.log,
  reg_6c766bd_leg3_rev.log.
- Exact-head CI on 6c766bd verified COMPLETE SUCCESS
  in a separate step before merge: package run
  41305436357 SUCCESS completed 2026-11-01T12:14:00Z;
  smoke run 41305436339 SUCCESS completed
  2026-11-01T12:30:39Z; both head_sha == 6c766bd.
- PR #190 merged as 2abf04c (2026-11-01T13:07:28Z);
  merge tree 020fbc8 == candidate tree; parents
  13e1df6 + 6c766bd.
- Fresh-clone regress at merge 2abf04c: 215/215 GREEN
  (log hidden_files/step9_logs/freshclone_regress.log).

## Limitations
- diff_baseline is session-only by design: after
  save/load there is no baseline, and Diff refuses
  (baseline_missing) until a writer captures one. No
  durable-baseline claim is made.
- The refusal reports the current store in
  last_diff.after; `changed` stays None (unknown). No
  consumer may read the refusal as "no changes".
- Cross-surface wording consistency for Diff/Set
  remains step 11 scope, as ordered.

## Anticipated probes
- Fresh state, Diff twice in a row: expected — both
  refuse baseline_missing; a refusal never creates a
  baseline (M3-class check is in the suite).
- Set (either branch), then Diff, then Diff again:
  expected — first Diff reports the Set change against
  the captured baseline; the baseline survives reads.
- Ambiguous legacy Set, then Diff: expected — Set
  refuses, captures nothing, mutates nothing; Diff
  still baseline_missing.
- Set inside a transaction, then Diff: expected — the
  staged capture follows the shared lifecycle (pinned
  exhibit in d1_registry_spectrum, 48/48).
- Save after Set, load, Diff: expected —
  baseline_missing (session-only baseline), never a
  vacuous "current" claim (probe P6 class).

## Questions for the Director
Q1. The session-only baseline means a loaded state has
no Diff baseline until a writer runs. The alternative —
persisting the baseline — would make Diff claims about
a store snapshot the current session never witnessed.
Uni recommends certifying the session-only reading; it
unblocks no other step, but a contrary ruling would
add a persistence contract to step 11's wording scope.
Q2. Uni recommends the step 9 ruling be bounded to the
Diff/Set baseline mechanism and the 55/89/95 card
contract as submitted, leaving cross-surface wording
consistency to step 11 as ordered.

## Requested ruling
Bounded re-ruling on B13 and B14 within the scope
above: honest baseline_missing refusal (no vacuous
"current" claim) and Set participation in the shared
_note_mutation baseline lifecycle on both branches.
