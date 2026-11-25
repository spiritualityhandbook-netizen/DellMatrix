# DIRECTOR REPORT — 72-17 REPAIR: Studio __RENDER__ Leak (R-B Structured Directive)

**Circuit:** 72-17 repair, executed under **Ace's FIX-FIRST
ruling (2026-11-05 19:53 CST)** and Sleep Protocol v2 queue
item 3. The R-B shape was the Director's preferred candidate
in the 2026-11-05 13:47 CST review of the 72-17 investigation,
and the Director's 2026-11-05 23:34 CST ruling (Class D
SCOPED_PASS, archived in this PR) directed Uni to proceed to
the Studio __RENDER__ leak. This merge (when gated) is
Ace-authorized, **not** Director-certified. **Base:** main
`f7c6ec0` (merge of PR #310). **Defect:** bare `09[Show]`
appended the machine sentinel `__RENDER__` to the human
`messages` list (`form/mandell/executor_leaf.py`, the only
producer). The REPL intercepted the token and printed the
real render (terminal clean), but the Studio `/api/execute`
payload carried it and the frontend dumped the raw result
JSON into the user console — the placeholder was
USER-VISIBLE in Studio. Chains passed the token through to
the same boundaries.

## Root cause

A machine control signal rode inside the human messages
list. The one intended consumer (the REPL renderer) had to
intercept a magic string in prose traffic, and every other
surface that faithfully displayed messages (Studio console,
chain results, `live_visual` raw collection) leaked it.

## Repair (bounded, R-B shape)

- `executor_leaf.py`: the bare-Show branch sets a structured
  `directive = "render"` on the leaf result instead of
  appending `__RENDER__` to messages. The token is never
  produced.
- `chain_exec.py`: an atom's directive propagates via the
  shared chain state to the chain result; minimal atom
  receipts are unchanged.
- `repl.py`: `_apply_seed_result` renders when
  `result["directive"] == "render"`, after the message loop
  (bare Show has no other tail messages, so ordering parity
  is exact for the only producer). The legacy token
  interception is retained for stale producers.
- `dell_cards.py` Dell 9 note + regenerated
  `DELL_PROOF_CARDS.md` (1-line diff) document the new
  contract; `d1_registry_leaf2_test.py` bare-Show expectation
  updated deliberately to the new contract.
- New suite `form/show_render_directive_test.py` registered
  in `form/regress.py` (LIST 240 -> 241).
- No frontend change: the Studio JSON dump stops containing
  the token because the payload no longer carries it. No
  persistence change; no save-path change.

Files changed: `form/mandell/executor_leaf.py`,
`form/mandell/chain_exec.py`, `form/repl.py`,
`form/mandell/dell_cards.py`,
`form/mandell/DELL_PROOF_CARDS.md`,
`form/mandell/d1_registry_leaf2_test.py`,
`form/show_render_directive_test.py` (new), `form/regress.py`.

## Evidence

- **Failing-first:** suite run at unrepaired head (branch
  commit `ee81174` on main `f7c6ec0`): **7/15 PASS, exit 1** —
  all 8 defect checks FAIL (bare/chain/Studio sentinel +
  directive checks); all 7 controls PASS (bare ok;
  avatar/lattice/visual unchanged + no directive; create no
  directive; REPL cross-process no-sentinel + render shown,
  REAL_USER_PATH).
- **Suite after repair:** `form/show_render_directive_test.py`
  **15/15 PASS, rc=0**, including the Studio-surface checks
  (`studio.no_sentinel_in_messages`,
  `studio.no_sentinel_serialized`, `studio.directive_render`)
  over the `/api/execute` result shape. Neighbours:
  d1_registry_leaf2 33/33, d1_proof_cards 6/6,
  translate_word_counts 21/21, translate_dead_args 21/21,
  translate_intent_args 18/18. First implementation run was
  14/15 — `chain.directive_render` missed because chain atom
  receipts are deliberately minimal; fixed via shared-state
  propagation, receipts untouched.
- **Mutant:** restoring the token append in executor_leaf ->
  suite **7/15** (the exact failing-first profile). Reverted
  by **inverse edit only**; suite back to 15/15; diff clean.
- **Regression:** full regress x3 sequential — **ALL TERMINAL
  GREEN** (logs in the goal workspace,
  `hidden_files/72-17-repair_logs/`): leg 1 (order=fwd)
  241/241 GREEN, `LEG1_RC=0`; leg 2 (order=fwd, twice)
  pass 1 241/241 + pass 2 241/241 GREEN, `LEG2_RC=0`;
  leg 3 (order=rev) 241/241 GREEN, `LEG3_RC=0`; `CHAIN_DONE`.
- **CI browser path:** the PR's Studio Browser Acceptance
  workflow runs at the exact head; its terminal state is
  part of the hard merge gate (no merge on a pending or
  failed mandatory check). No exact-head claim is made in
  this report beyond the checks recorded at merge time in
  SLEEP_V2_STATE.md.
- **Register:** the 72-17 line records this repair; its
  status prefix is unchanged pending the Director's
  confirmation — no status the evidence does not support is
  claimed, and 72-17 is not counted COMPLETED.

## Anticipated probes

- *"Why keep the legacy token interception in the REPL?"* —
  it is a harmless compatibility shim for any stale producer
  outside this codebase's control; the only in-repo producer
  no longer emits the token, and the suite pins that.
- *"Why propagate the directive through chain state instead
  of atom receipts?"* — atom receipts are deliberately
  minimal and pinned by other suites; the chain result is
  the surface that carried the token, so it is the surface
  that now carries the directive.
- *"Is REPL semantics changed?"* — no: the same render is
  printed, keyed off the structured field instead of a magic
  string; the suite's REPL controls are cross-process
  REAL_USER_PATH checks and pass before and after.

## Questions for the Director

- Q-17R.1: Certification review of this R-B repair is
  requested; the merge proceeds under Ace's FIX-FIRST
  authority and is labeled accordingly.
