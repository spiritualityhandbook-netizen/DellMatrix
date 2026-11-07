# DIRECTOR REPORT — 72-19: First-Failure Provenance Composition Proof

Circuit: 72-19 (Master Objective Register §6.7) — "Preserve
first-failure provenance through mixed chain receipts
(P1/E)." Remaining action as registered: "Final composition
proof retained as outstanding in the dispositions table"
(Step 7 CERTIFIED W/ EXCEPTIONS; Step 8 PARTIAL; per-frame
provenance proven by PRs #186/#188). Original acceptance:
"Failed, successful, and skipped atoms must retain the
original failure and accurate partial-result accounting."

Executed as an EVIDENCE circuit under Sleep Protocol v2.
Branch: uni/72-19-first-failure-provenance, base main
2893e3d390d72ade13c0f2a5da53ff00c6968503 (PR #318 merge).
Suite SHA: 69fa879807da4fcde6c02bfd02508a9fd479d4c2.
NO production code changed. NO defect found.

## 1. Result (FACT)

A dedicated 39-check suite (form/first_failure_provenance_
test.py, registered in form/regress.py — canonical count
249) composes thirteen mixed chains through the public
entry path (execute_seed) and pins the provenance division
of labor across all three surfaces. Every composition
retains the original failure; partial accounting is
accurate in each. The per-surface semantics, previously
implicit in chain_exec.py's code and comments, are now
executably pinned:

- Receipt surface (atom_results): occurrence-complete and
  execution-ordered in ALL compositions — leaf sequences,
  Branch arms (unchosen = skipped receipts), Sequence and
  Parallel bodies, Until/While iterations (order preserved
  across iterations), ForEach members (member-annotated),
  nested frames (Branch in Sequence), refused control
  heads, and Join verdicts. The first failing occurrence
  is always the true first failure, error verbatim. A Join
  whose incoming body failed records its own downstream
  join_fail verdict AFTER the body failure — it never
  displaces it (C4, C5, C6, C9, C12, C13).
- Chain summary (result.error): the LAST leaf failure in
  execution order (execute_chain names the variable
  last_error), with first-preserving guards: a refused
  control head (UNSUPPORTED_ARGS) and a Join failure fill
  it only when no earlier failure stands (C8a, C10); a
  loop's bound_reached is the frame's terminal verdict and
  closes it (C6). Where the surfaces diverge by design —
  refused head first, leaf failure second — the receipt
  keeps the refusal first while the summary names the leaf
  (C8b); both sides are pinned.
- Outcome surface (note_atom_failure, transaction open):
  with failures composed INSIDE a Sequence frame, the tx
  frame's error is the first root cause (delete_missing:
  txfirst), later failures accumulate in extra_errors in
  order ([txsecond, join_fail]), and the tx root cause
  EQUALS the receipt surface's first failure (C9) —
  cross-surface agreement proven, complementing Step 8's
  per-frame proofs.
- Accounting: clean chain (ok, not partial, no skips);
  lawful-skip chain (ok AND partial AND any_skipped —
  Step 7 semantics); mixed chains (not ok, partial) —
  C1–C13, C11a/b.

## 2. Verification

- Suite: 39/39 at base (probe-driven: hidden_files/
  72-19_probe.py mapped all thirteen compositions before
  pinning).
- Mutant: chain error made first-wins (the leaf assignment
  operand order swapped) -> 35/39, exactly the four
  chain_error_is_last_leaf checks fail (C1, C5, C8b, C12);
  inverse-reverted, tree clean, suite back to 39/39.
- Regression at the suite SHA (logs
  hidden_files/72-19_logs/run1/): TERMINAL GREEN 249/249 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 39/39)
- CI at the final PR head: __FINAL_CI__

## 3. Records carried in this PR

- This report + INDEX row.
- DIRECTOR_REPORT_72_13_TYPED_SIGNATURE_AUDIT.md: the
  CI/merge receipt placeholder completed (final-head CI
  all terminal PASS — package 42326464425, browser-
  acceptance 42326464409, smoke 42326464379 PASS 16m35s;
  PR #318 merged 2893e3d390d72ade13c0f2a5da53ff00c6968503,
  tree 8f83b144d57906ff84129fe28a4fabf9fa65a1ad;
  merged-main CI terminal SUCCESS — package 42327922946,
  Form smoke 42327922971).
- Register: 72-19 row updated (final composition proof
  landed; status stays PARTIAL — Step 8's wider scope is
  not exhausted by this proof).

## Anticipated probes

- "Is last-leaf chain error itself the defect?" — It is
  the documented-in-code semantic (the variable is named
  last_error; DIRECTOR DECISION 1 aggregates derive from
  atom_results), and the register's acceptance speaks of
  retaining the original failure in the RECEIPTS, which
  holds everywhere. If you want the summary surface to
  carry the first failure instead, that is a contract
  change with consumers to re-audit (Q-72-19.2) — this
  circuit pins the current division rather than silently
  redefining it.
- "Join join_fail receipts pollute failure lists." —
  They are real verdicts of an executed atom (the Join
  evaluates its incoming frame), ordered downstream of
  the failure they judge, and Step 8's hook treats them
  as extra evidence, never root cause. A consumer that
  takes failures[0] gets the truth in every composition
  tested.

## Questions for the Director

- Q-72-19.1: Confirm the composition proof satisfies the
  outstanding final-composition action for 72-19 (row
  stays PARTIAL for Step 8's wider scope), or name the
  composition class you still want proven.
- Q-72-19.2: Should result.error remain the last-leaf
  summary (receipts carrying first-failure provenance),
  or should a future circuit propose changing the summary
  surface to the first failure, with a consumer audit?
