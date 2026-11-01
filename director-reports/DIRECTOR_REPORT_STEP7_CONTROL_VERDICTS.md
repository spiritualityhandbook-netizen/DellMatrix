# DIRECTOR REPORT — STEP 7: CONTROL VERDICTS (B7/B8/B9, DAF-08)

Status: SUBMITTED 2026-11-01 — circuit closed (frozen
candidate, CI, merge and fresh-clone recorded in Evidence).
This report is evidence submitted, never a certificate.

## Findings addressed
- DAF-08 (P2): control receipts omit skipped work and contradict
  their aggregates.
- B7 Join/Parallel: closing Join must evaluate the completed
  block's actual results; a captured sibling failure must be
  represented in the frame verdict; no vacuous incoming=0
  success when children ran.
- B8 Until: chain controller owns condition semantics; empty
  condition follows the true/zero-iteration boundary in both
  surfaces; bound and actual iterations exposed.
- B9 ForEach: empty selection = zero iterations and a valid
  empty execution, without a plane-id fallback; core and chain
  reports agree.

## Before (Director's counterexamples, reproduced 2026-11-01
## on 4937af2 by hidden_files/step7_probe.py)
- 51[Select] >>> 08[Create] > 61[Join]: atom_results [51, 61],
  any_skipped=False, partial=False, chain_skipped=[8].
- 60[false] > 08[Create] > 61[Join]: atom_results [61] only.
- 64[true] > 08[Create] > 61[Join]: atom_results [61] only;
  frame carried no bound.
- 62[Parallel] > 91[false] > 80[TrueArm] > 61[Join]: "Join
  policy=all ok=True incoming=0 fails=0" (vacuous); frame
  status "ok" despite the captured sibling failure.
- Bare 64[Until] in one run: core "cond=false already=False"
  vs chain "already true — zero iterations".
- Bare 66[ForEach] in one run: core "n=1 empty_ok=False"
  (plane fallback) vs chain "empty selection valid".

## After (candidate 2b04300)
- FlowOver probe: receipts [51, 8, 61], any_skipped=True,
  partial=True, chain ok=True (partial = occurrence-level
  incompleteness, documented in chain_exec; not a failure
  verdict).
- Branch probe: receipts [60, 8, 61]; Until-zero: [64, 8, 61]
  with frame bound=8, iterations=0.
- Parallel probe: "Join policy=all ok=False incoming=2
  fails=1"; frame status "fail"; chain error keeps the root
  cause "assert_fail" (join_fail never overwrites it).
- Bare Until: core "cond=true already=True bound=8" agrees
  with the chain. Bare ForEach: core "n=0 empty_ok=True"
  agrees with the chain.

## Mechanism (one receipt authority — atom_results)
- chain_exec emits occurrence-level receipts for every path
  that previously skipped silently: FlowOver skips, Branch
  unchosen arms + Else markers, multiple-else bodies,
  zero-iteration Until/While bodies, empty-ForEach bodies.
  Control head receipts are inserted by execute_range so the
  frame results keep their body+join shape; loop frames now
  expose "bound".
- The closing Join reads the block's actual results because
  _run_control publishes them to last_frame BEFORE the Join
  atom runs; a Join failure sets the block frame status to
  "fail" and the chain state error preserves the first root
  cause.
- core Join failure counting excludes skipped receipts
  (lawful skip != failure) and previous Join verdict receipts
  (owned_by) — the children behind a verdict are themselves
  counted, so no failure is counted twice.
- core Until: empty condition passes through eval_condition
  (true) unchanged. core ForEach: plane-id fallback deleted.

## Evidence
- Suite STEP7_CONTROL_VERDICTS 28/28 (regress entry 213).
- Mutants killed exactly: M1 vacuous Join 24/28; M2 FlowOver
  receipts dropped 25/28; M3 Until `lab or "false"` 27/28;
  M4 ForEach fallback 27/28; M5 head receipts dropped 16/28.
- Amended pins: d1_registry_coreii_a three EXHIBITs became
  the Step 7 contracts (30/30); dell_cards deep notes for
  61/62/64/66 updated; DELL_PROOF_CARDS.md regenerated
  (6/6 drift check). Neighborhoods: control_runtime 38/38,
  eoc_i 146/146, p0r3 80/80, pp5_flow_visual 8/8,
  flow_executor 28/28, p10_flow_grammar 12/12.
- Regress x3 on candidate 2b04300 (tree 6e08d52): fwd
  213/213, --twice 213/213 x2, --order rev 213/213 — all
  GREEN (logs hidden_files/step7_logs/).
- Exact-head CI on 2b04300 verified COMPLETE SUCCESS in a
  separate step before merge: package run 41287370684
  SUCCESS; smoke run 41287370747 SUCCESS completed
  09:22:03Z (an earlier check found smoke IN_PROGRESS and
  the merge waited).
- PR #186 merged as 625bb69 (2026-11-01T09:30:54Z); merge
  tree 6e08d52 == candidate tree; parents 4937af2 +
  2b04300.
- Fresh-clone regress at merge 625bb69: 213/213 GREEN
  (step7 suite 28/28).

## Limitations
- Receipt completeness covers the chain_exec control paths
  named above. Loop/ForEach bodies that execute produce more
  receipts than seed atoms (one set per iteration/member) —
  flow_visual alignment is therefore exact for single-pass
  bodies and falls back to its unaligned rendering for
  multi-iteration bodies, by design.
- Lawful-skip receipts now also reach executor.py's
  executor:skip unknown-recording (same canonical receipt,
  deduped); they are recorded as "did not execute" with the
  lawful reason — no verdict anywhere treats them as failures.

## Anticipated probes
- Recount a post-block Join's incoming by hand from
  atom_results: expected to match (incoming includes the
  closing Join's verdict receipt; fails excludes it and any
  skipped receipts).
- A Branch whose taken arm fails: closing Join fails, frame
  status fail, chain error stays the arm's root cause.
- An Until whose body makes the condition true in iteration
  1 under a Limit: iterations=1, bound exposed, receipts
  [64, body, 61].
- ForEach over a selection, then a bare ForEach on a fresh
  program: member path unchanged; bare path n=0.
- A Sanitize chain containing a Branch: receipts are
  sanitized as detached evidence at the existing step-3c
  boundary; canonical state untouched (step 3c suites are in
  the regression).

## Questions for the Director
Q1. DAF-08 asks Uni to "document whether partial means
conditional omission or failed/incomplete execution". This
circuit documents partial as occurrence-level incompleteness
covering BOTH (lawful omission OR failure), with `ok` as the
separate verdict. If the Director prefers partial to mean
failure-only, the aggregates change in one place
(execute_chain) — Uni recommends the documented dual
definition because it preserves the existing RouteReceipt /
Decision 1 semantics already certified in earlier steps.
Q2. Should a closing Join under policy "any" with ONLY
skipped children (e.g. a zero-iteration Until body) pass?
This implementation passes it (no executed results = no
executed failure, mirroring all/any vacuity rules for empty
incoming). Uni recommends certifying that reading, since the
alternative would convert lawful skips into Join failures,
which step 7 explicitly forbids.

## Requested ruling
Bounded re-ruling on B7, B8, B9 and DAF-08 within the scope
above: occurrence-complete control receipts, actual-results
Join verdicts, Until empty-condition agreement with bound
exposure, and ForEach empty-selection agreement.
