# DIRECTOR REPORT — 72-27: Guard/Assert Failures Propagate as Verdicts, Never as Halts

Circuit: 72-27 (Master Objective Register §6.7) —
"Adjudicate Guard/Assert frame propagation
(= SM-19 extension)." Remaining action on the row:
"Dedicated frame-propagation recheck." Acceptance:
"Deterministic frame/error behavior when guards fail
inside control compositions."

Executed as an EVIDENCE circuit under Sleep Protocol v2.
Branch: uni/72-27-guard-assert-propagation, base main
8c6f1f5f20b118d443c02efc77a4e7bae62487df (PR #323 merge).
Suite SHA: b7b3bcb497bc97be7452cf7ff750ed51de599843.
NO production code changed. NO defect found.

## 1. Result (FACT)

Guard (92) and Assert (91) evaluate their label as a
condition (control_runtime.eval_condition): a failed
Assert records last_assert=FAIL and fails assert_fail;
a blocked Guard records last_guard=BLOCK and fails
guard_block (labels "block"/"deny" force BLOCK); both
also fail any open transaction frame. The registry
spectrum suite pins the two Dells standalone and Step 8
pins the transaction Catch discipline. What remained
unproven was how their failures PROPAGATE through the
control compositions. A dedicated 16-check suite
(form/guard_assert_propagation_test.py, registered in
form/regress.py — canonical count 254) adjudicates it
at the public entry path (probe:
hidden_files/72-27_probe.py; independently reproduced
by the hourly cycle in a fresh clone at the same base):

- Bare in a chain, a Guard block / Assert fail is an
  honest failure receipt, the chain error is the Dell's
  own, and the NEXT atom still runs. Their failures are
  captured verdicts, not chain halts — the same
  continue-on-failure contract pinned for every atom in
  72-19/72-20. Guard's registry text ("Prevent
  execution unless conditions hold") is honored at the
  verdict and transaction-frame level, not as a
  control-flow halt; see Q-72-27.1.
- Inside a Sequence: the frame settles 'fail', the
  Join judges the executed failure (join_fail), later
  members still run. A passing Guard settles 'ok'
  end to end.
- Inside a Branch: a failing Assert in the taken arm
  fails the branch frame and the Join; an Assert in
  the UNCHOSEN arm is skipped and never evaluated
  (last_assert untouched), branch and Join 'ok'.
- Nested Sequences: propagation is exactly one Join
  per level (inner join_fail -> outer join_fail),
  both frames settle 'fail', the chain error remains
  the Assert's own, and the outer Sequence's later
  member still runs.
- Inside a While body: the Guard failure is one
  executed failure in that iteration — the body's
  remaining member still runs in the same iteration,
  the loop ends on its condition (one iteration), the
  frame settles 'fail', the Join judges join_fail.
- Inside Try/Catch: Catch executes (its receipt is
  ok — it consumes the transaction frame's error),
  while the chain error remains guard_block (the
  standing last-leaf summary contract, 72-19).
- Condition surface: a store-presence condition
  allows (last_guard=ALLOW); the explicit "block"
  label blocks; a passing Assert records PASS.

## 2. Verification

- Suite: 16/16 at base (pins observed contract).
- Mutant: both failures silenced in the spectrum arms
  (ok=True, err="") -> 7/16: all nine propagation
  checks fail (bare verdicts, deny label, Sequence
  frame/Join, Branch frame, nested Joins, While
  frame, Try/Catch chain error) while the pass-direction
  checks survive; note last_guard/last_assert still
  recorded BLOCK/FAIL under the mutant — the records
  outliving the verdicts is exactly the dishonesty the
  suite exists to catch. Reverted and verified
  ZERO-DIFF against HEAD (git diff empty), 16/16.
- Regression at the suite SHA (logs
  hidden_files/72-27_logs/run1/): TERMINAL GREEN 254/254 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 16/16)
- CI at the final PR head: all terminal PASS at the final head 2be9b92c — Python package 42361191482, browser-acceptance 42361191528, Form smoke 42361191883 PASS 12m26s; PR #324 merged 3ebef3515e2de66cb27a313b95794f71647a232b; delivered merge tree 316162a9c863d0db24c1cfe6ac87e03ad5af43e3 IDENTICAL to the frozen candidate head tree (git-verified on both commits); merged-main CI on the push-workflow route terminal SUCCESS — package 42362064170, Form smoke 42362064258, both watch-observed.

## 3. Records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-07_72_25_
  PASS_72_26_NEXT.md: archive of your 2026-11-07 02:44
  CST ruling (72-25 bounded ALL_AI_CONFIRMATION_PASS
  on Q-72-25.1; 72-26 merge instruction — executed:
  PR #323 merged 8c6f1f5f20b118d443c02efc77a4e7bae62487df,
  tree 2e6609331b15faead58712b589c432c14ae993cd;
  merged-main CI terminal SUCCESS — package
  42357533609, Form smoke 42357533583).
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-07_72_26_
  BOUNDED_PASS.md: archive of your 2026-11-07 03:33
  CST ruling (72-26 ALL_AI_CONFIRMATION_PASS bounded
  to Q-72-26.1; 72-27 authorized). Its receipt asks,
  answered: the frozen candidate tree (head 56676412)
  and the delivered merge tree are IDENTICAL —
  2e6609331b15faead58712b589c432c14ae993cd on both
  (git rev-parse, both commits); merged-main CI was
  verified on the push-workflow route at the merge
  commit (package 42357533609, Form smoke 42357533583,
  both terminal SUCCESS, watch-observed) — the empty
  commit-specific PR-workflow lookup is a lookup-route
  artifact, not missing runs.
- DIRECTOR_REPORT_72_26_MANIFESTSET_ISOLATION.md: the
  CI/merge receipt placeholder completed (final-head
  CI all terminal PASS — Python package 42356605061,
  browser-acceptance 42356605082, Form smoke
  42356605114 PASS 13m1s; PR #323 merged as above).
- Register: 72-27 row updated (frame-propagation
  recheck landed; status stays PARTIAL).

## Anticipated probes

- "Should a blocked Guard HALT the rest of the chain
  (its manor says 'prevent execution')?" — The
  observed contract is uniform with every other atom
  failure across 72-19/72-20/72-21: failures are
  captured as receipts, judged by Joins, and fail open
  transaction frames; nothing except a loop bound
  stops a body mid-walk. A Guard-specific halt would
  be a second, inconsistent failure semantics. This
  circuit reports the behavior; whether the manor
  text should be narrowed (as 72-20 narrowed Dell
  62's concurrency claim) is Q-72-27.1 — no text was
  changed unilaterally.
- "Does Catch hide the Guard failure?" — No: Catch
  consumes the transaction frame's pending error
  (Step 8 / B16 discipline); the atom receipt and the
  chain summary both still carry guard_block.

## Questions for the Director

- Q-72-27.1: Is verdict-level propagation (receipt +
  frame + Join, never a halt) the intended reading of
  Guard's "Prevent execution unless conditions hold",
  or should the registry manor text be narrowed as in
  72-20? No behavior change is proposed either way.
- Q-72-27.2: Confirm this recheck satisfies 72-27's
  remaining action (row stays PARTIAL for SM-19's
  wider scope), or name the composition still wanted.
