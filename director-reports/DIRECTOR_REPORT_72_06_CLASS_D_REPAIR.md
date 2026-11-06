# DIRECTOR REPORT — 72-06 Class D REPAIR: Zombie zoom/weather Args

**Circuit:** 72-06 follow-on repair, executed under **Ace's
FIX-FIRST ruling (2026-11-05 19:53 CST)** and the Director's
2026-11-05 22:30 CST ruling (SCOPED_PASS for the Class E repair,
PR #309), which directed: proceed immediately to Class D under
Fix-First; the proposed shape (carry the operand through the
mandel the router reads, retire the dead args) is acceptable as
a bounded repair approach. This merge (when gated) is
Ace-authorized, **not** Director-certified. **Base:** main
`02955dd` (merge of PR #309). **Defect:** 72-06 census Class D
(PR #308): `translate()` emitted intents whose mandel dropped
the zoom/weather operand while the operand rode in
`Intent.args` keys (`ref` / `condition`) that **no consumer
anywhere in `form/` or `gui/` reads** — zombie args. The routed
mandel path therefore executed zoom/weather with no operand;
the bare REPL appeared to work only because its raw-line
handlers re-parse the original English text.

## Root cause

- `form/mandell/phrases.py` — the zoom seed was
  `15[Map] :: zoom` and the weather seed was
  `25[Pulse] :: weather`: the captured label was never
  substituted into the seed, so the mandel (the channel the
  router actually reads) carried no operand.
- `form/mandell/translate.py` — the phrase branch built
  `args = {"ref": label}` for zoom and
  `args = {"condition": ...}` for weather. A consumer sweep
  over `form/` + `gui/` for `args.get("ref")` /
  `args.get("condition")` is empty: the args were written and
  never read.

## Repair (bounded, shape approved in the 22:30 ruling)

- phrases.py: zoom seed -> `15[Map] :: zoom {label}`; weather
  seed -> `25[Pulse] :: weather {label}` (`match_phrase`
  already substitutes `{label}` from the capture group,
  underscores for spaces — the same mechanism the
  distill/compress label seeds use). User labels/operands are
  preserved verbatim in the mandel.
- translate.py: the zoom/weather phrase branches now set
  `args = {}` — the dead `ref` / `condition` args are retired,
  with an in-code comment recording why.
- New suite `form/translate_dead_args_test.py` registered in
  `form/regress.py` beside `translate_word_counts_test`
  (LIST 239 -> 240).
- No persistence change; no R-2 architecture change (per the
  ruling's bounds).

Files changed: `form/mandell/phrases.py`,
`form/mandell/translate.py`, new suite
`form/translate_dead_args_test.py`, `form/regress.py`.

## Evidence

- **Failing-first:** suite run at unrepaired head (branch
  commit `3c1da65` on main `02955dd`): **3/21 PASS, exit 1** —
  all 18 defect checks FAIL (mandel carries no operand x8,
  dead arg present x8, parsed seed label lacks operand x2);
  all 3 controls PASS (unzoom neighbour unchanged; REPL
  cross-process controls `Idea page · beta` and
  `Weather → rain`, REAL_USER_PATH).
- **Suite after repair:** `form/translate_dead_args_test.py`
  **21/21 PASS, rc=0**. Neighbours: translate_word_counts
  21/21, translate_intent_args 18/18, mandell.phrase_tests
  rc=0.
- **Mutant:** dropping `{label}` from the zoom seed (the
  original defect shape) -> suite **17/21, 4 FAIL, rc=1**.
  Reverted by **inverse edit only**; worktree verified clean
  afterward; suite back to 21/21.
- **Regression:** full regress x3 sequential — **ALL TERMINAL
  GREEN** (logs in the goal workspace,
  `hidden_files/72-06-classd_logs/`): leg 1 (order=fwd)
  240/240 GREEN, `LEG1_RC=0`; leg 2 (order=fwd, twice) pass 1
  240/240 + pass 2 240/240 GREEN, `LEG2_RC=0`; leg 3
  (order=rev) 240/240 GREEN, `LEG3_RC=0`; `CHAIN_DONE`.
- **Register:** per the 22:30 ruling, the 72-06 register line
  is updated in this PR **without waiting for PR #308**: it
  now records the Class E repair as FIXED (PR #309, Director
  SCOPED_PASS) and this Class D repair. The item's overall
  status stays PARTIAL — the full Intent.args contract census
  (PR #308) has not merged, and no status the evidence does
  not support is claimed.

## Anticipated probes

- *"Why retire the args instead of adding a consumer?"* — the
  mandel is the channel the router reads; a second operand
  channel in args would be a duplicate authority for the same
  fact. The census showed zero consumers, so the args were
  pure zombie state.
- *"Does any other file pin the old seed strings?"* — blast
  radius grep over `form/` + `gui/` for the exact strings
  `15[Map] :: zoom` / `25[Pulse] :: weather` outside
  phrases.py is empty; phrase_tests lists the phrases only.
  `parse_seed('15[Map] :: zoom beta')` parses ok with label
  `zoom beta` (operand present).

## Questions for the Director

- Q-06D.1: Certification review of this repair is requested;
  the merge proceeds under Ace's FIX-FIRST authority and is
  labeled accordingly.
- Q-06.2 is now ANSWERED by the 22:30 ruling (shape
  acceptable); no objection outstanding.
