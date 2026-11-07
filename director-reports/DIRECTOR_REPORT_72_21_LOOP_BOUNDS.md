# DIRECTOR REPORT — 72-21: Until/While Bounds Exact; Nested Skips Contained

Circuit: 72-21 (Master Objective Register §6.7) — "Stress
Until/While/ForEach bounds + nested control inheritance
(= SM-18)." Remaining action as registered: "While-specific
bounds; nested skip inheritance."

Executed as an EVIDENCE circuit under Sleep Protocol v2.
Branch: uni/72-21-loop-bounds, base main
6cf22dd34473179b1b68a97bcdb09945294d2d8f (PR #320 merge).
Suite SHA: 71c91cda924e7183c4554a51ba81985de80404a0.
NO production code changed. NO defect found.

## 1. Result (FACT)

A dedicated 27-check suite (form/loop_bounds_test.py,
registered in form/regress.py — canonical count 251)
stresses the loop bounds and nested inheritance at the
public entry path (probe: hidden_files/72-21_probe.py,
9 compositions):

- While bounds are EXACT: Limit 3 runs exactly 3
  iterations (settled frame iterations=3, bound=3, status
  'bounded', chain error bound_reached); with no Limit
  the default bound is exactly 8 (8 iterations); a body
  that clears the condition exits after 1 iteration with
  the frame 'ok' and the bound still exposed; a false
  initial condition runs zero iterations — the body
  occurrence is a skipped receipt, the frame is 'zero',
  the Join passes, and the chain is ok AND partial.
  Until mirrors the discipline at Limit 3.
- Verdict division (pinned): after a bound_reached loop
  the closing Join's receipt is ok — it judges the
  EXECUTED atom receipts, all of which succeeded — while
  the chain error carries the loop's terminal verdict.
- Nested skip inheritance: a skip is CONTAINED. A
  zero-iteration While inside a Sequence leaves the
  later Sequence member running and the outer Join
  passing. An unchosen Branch arm containing a whole
  loop frame skips the ENTIRE subtree (While head, body,
  and the frame's own Join are all skipped receipts) and
  nothing inside it mutates. A ForEach with an empty
  selection skips an inner loop frame through two levels
  (frame status 'empty') while the ForEach's own Join
  still passes.
- An inner bound failure does not halt the outer body:
  an Until hitting Limit 2 inside a Sequence leaves the
  later Sequence member running, the outer Join passing,
  yet the chain ends not-ok with bound_reached — the
  inner frame's terminal verdict reaches the chain
  surface without poisoning the outer frame's receipts.

## 2. Verification

- Suite: 27/27 at base (pins observed contract).
- Mutant: the loop guard made <= (off-by-one bound) ->
  20/27, exactly the seven bound-exactness checks fail
  (W1 x2, W2 x2, W5 x2, N3), iterations inflated by
  exactly 1 in every case; inverse-reverted, tree clean,
  suite back to 27/27.
- Regression at the suite SHA (logs
  hidden_files/72-21_logs/run1/): TERMINAL GREEN 251/251 x3 (fwd / --twice / --order rev; LEG1_RC=LEG2_RC=LEG3_RC=0, CHAIN_DONE present; the new suite runs inside the harness at 27/27)
- CI at the final PR head: __FINAL_CI__

## 3. Records carried in this PR

- This report + INDEX row.
- responses/DIRECTOR_REVIEW_EMAIL_2026-11-06_72_20_
  CONDITIONAL_PASS.md: archive of your 72-20 ruling
  (bounded technical PASS conditional on terminal CI —
  condition satisfied before merge; Q-72-20.1 YES;
  Q-72-20.2 synonyms retained).
- DIRECTOR_REPORT_72_20_FRAME_GUARANTEES.md: the
  CI/merge receipt placeholder completed (final-head CI
  all terminal PASS — Python package 42342298181,
  browser-acceptance 42342298231, Form smoke 42342298271
  PASS 18m20s; PR #320 merged
  6cf22dd34473179b1b68a97bcdb09945294d2d8f, tree
  298e8f16eead9e53a8b8f5c646d0b70d1c3bad2f; merged-main
  CI terminal SUCCESS — package 42343632836, Form smoke
  42343632844).
- Register: 72-21 row updated (bounds + nested-inheritance
  stress landed; status stays PARTIAL).

## Anticipated probes

- "Is the Join-after-bound_reached 'ok' receipt a false
  success?" — It is the same verdict division you settled
  in Step 11 and re-confirmed in 72-20: a Join judges
  executed atom receipts. The loop's terminal verdict is
  not an atom receipt; it surfaces on the chain error
  and the settled frame (status 'bounded', error
  bound_reached). No surface claims the chain succeeded:
  result.ok is False.
- "Does an inner bound failure leaving the outer body
  running violate Sequence's contract?" — It is
  Sequence's documented failure-continues semantics
  (72-20 S2) applied through nesting; the failure is
  fully reported on the chain surface. A halt-on-inner-
  bound policy would be a contract change, not a fix.

## Questions for the Director

- Q-72-21.1: Confirm the bounds stress + nested skip
  inheritance proof satisfies 72-21's remaining action
  (row stays PARTIAL for SM-18's wider scope), or name
  the bound/inheritance composition you still want
  stressed.
