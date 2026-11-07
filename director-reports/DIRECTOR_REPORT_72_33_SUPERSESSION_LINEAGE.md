# DIRECTOR REPORT — 72-33: Supersession Acceptance Lineage Survives Restart, Link for Link

Circuit: 72-33 (Master Objective Register §6.8) —
"Verify supersession crash + acceptance lineage
across restart (P1/E) (= SM-30)." Remaining action:
"Present suite evidence for ruling, or extend lineage
assertions." Executed per your 2026-11-07 04:10 CST
instruction: existing evidence inspected and reused;
only the missing bounded assertions added.

Executed as an EVIDENCE circuit under Sleep Protocol
v2. Branch: uni/72-33-supersession-lineage, base main
3ebef3515e2de66cb27a313b95794f71647a232b (PR #324
merge). Suite SHA: 9b838d4084a577d64b71599140f0663a565fb7fa.
NO production code changed. NO defect found.

Sequencing note (transparent): 72-10 was opened at
04:01 CST, before your 72-33 instruction arrived; Ace
(Overseer) was asked to sequence the two and ruled
72-10 first, then — when its worktree's mutant-revert
step hit a tooling refusal — accepted Uni's judgment
to park 72-10 (branch pushed at 92046c9, worktree
frozen, nothing merged) and run 72-33 first. 72-10
resumes after this circuit closes; no 72-34 work has
begun or run in parallel.

## 1. What already existed (reused, not duplicated)

form/mandell/supersession_failure_test.py proves the
hard failure paths: an interrupted supersession with
an INCOMPLETE rollback and fresh-process recovery
(Scenario A), unsafe-save closure (B), checkpoint-path
closure (C), and spatial verification sensitivity.
This circuit does not re-prove those.

## 2. Result (FACT) — the missing lineage assertions

A dedicated 11-check suite
(form/supersession_lineage_restart_test.py, registered
in form/regress.py) adds the lineage contract at the
production public path (probe:
hidden_files/72-33_probe.py):

- A 3-link acceptance chain (A confirmed; B
  supersedes A; C supersedes B) carries exact lineage
  in-process: per-link supersedes / superseded_by,
  one shared revision root (A), revision numbers
  1 / 2 / 3, and the full ordered chain [A, B, C]
  readable identically from every link.
- The ENTIRE lineage survives restart: a fresh OS
  process (subprocess child) loading the owner through
  the production path reports inspections IDENTICAL
  to the in-process values for every link — links,
  lifecycle states, numbers, chain — with every link's
  ACCEPTED status still "confirmed", exactly the tip
  active, and recovery reporting "none" (no pending
  intent on a clean chain).
- A crash on the SECOND link of a chain (injected at
  the documented "confirm" window, SupersedeError
  injected_failure) rolls back COMPLETELY: no
  successor proposal exists afterward, the
  predecessor stays active with its lineage untouched
  (chain still [D, E]), and a fresh-process restart
  confirms the identical coherent state.

Labels: INTEGRATION in-process; CROSS_PROCESS for
both restart legs (fresh OS process, production
recover_supersede_intent + open_program).

## 3. Verification

- Suite: 11/11 at base (pins observed contract).
- Mutant: the backward link write silenced
  (old.superseded_by_id = None in
  form/mandell/supersession.py) -> the suite fails at
  the chain-build step: production itself detects the
  broken bidirectional link and refuses the second
  supersession (SupersedeError malformed_revision:
  broken_bidirectional_link). The mutant cannot
  produce a silently wrong lineage — the invariant is
  enforced by production validation, and the suite's
  base-green depends on it. Inverse-reverted,
  verified ZERO-DIFF against HEAD, 11/11.
- Regression at the suite SHA (logs
  hidden_files/72-33_logs/run1/): TERMINAL GREEN 255/255 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE 2026-11-07 06:53 CST; the new suite runs inside the harness at 11/11). Disclosure: the first chain launch was killed by a runtime/VM restart ~58s in (partial leg 1 = NO RESULT, never recorded as pass or fail); the relaunched run1 chain above is the deciding evidence.
- CI at the final PR head: __FINAL_CI__

## 4. Records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-07_72_27_
  BOUNDED_PASS.md: archive of your 2026-11-07 04:10
  CST ruling (72-27 bounded ALL_AI_CONFIRMATION_PASS;
  Q-72-27.1 semantics accepted with the wording
  correction routed to a separate future hygiene
  circuit; Q-72-27.2 YES; 72-33 authorized).
- DIRECTOR_REPORT_72_27_GUARD_ASSERT_PROPAGATION.md:
  the CI/merge receipt placeholder completed, per
  your asks (final-head CI all terminal PASS —
  Python package 42361191482, browser-acceptance
  42361191528, Form smoke 42361191883 PASS 12m26s;
  PR #324 merged 3ebef3515e2de66cb27a313b95794f71647a232b;
  delivered merge tree 316162a9c863d0db24c1cfe6ac87e03ad5af43e3
  IDENTICAL to the frozen candidate head tree —
  git-verified on both commits; merged-main CI on
  the push-workflow route terminal SUCCESS — package
  42362064170, Form smoke 42362064258, both
  watch-observed).
- Register: 72-33 row updated (lineage assertions
  landed; status stays PARTIAL for SM-30's wider
  scope); canonical regress count on this branch
  255 (254 on main + this suite; the parked 72-10
  branch carries its own +1 — union on its later
  merge gives 256).

## Anticipated probes

- "Why is the crash leg's rollback complete here
  while Scenario A of the failure suite is
  incomplete?" — Different windows, different
  injections: Scenario A injects a plane.remove
  failure DURING rollback, forcing incompleteness;
  this circuit injects only the operation failure
  (confirm window) with rollback intact, so
  compensation completes before the error surfaces
  and no journal remains. The two suites are
  complementary, not contradictory.
- "Are the unit ids deterministic?" — Observed: the
  revision ids repeat across owners and runs
  (content-derived). The suite never hardcodes them;
  it reads ids from the supersede results.

## Questions for the Director

- Q-72-33.1: Confirm the lineage assertions satisfy
  72-33's remaining action (row stays PARTIAL for
  SM-30's wider scope), or name the lineage surface
  still wanted.
- Q-72-33.2: After this circuit, Uni resumes the
  parked 72-10 (Ace's sequencing) before any 72-34
  work — confirm that ordering, or direct otherwise.
