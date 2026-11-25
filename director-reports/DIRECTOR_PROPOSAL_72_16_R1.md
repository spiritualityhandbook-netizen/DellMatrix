# DIRECTOR PROPOSAL — 72-16 R-1: Repair the flow_executor label-args class (B4 silent operand rewrite)

Proposal ID: DIRECTOR_PROPOSAL_72_16_R1
Base: main 57b92925577c1094c93d3e8b91db74d8fd70b215
Type: GATE-bucket proposal only. **No product code changed, no repair
implemented, no failing-first suite committed.** Implementation begins
only on the Director's ruling on Q-R1.1–Q-R1.3 below.
Authority for this proposal: Director work order, Gmail
1a1bb7d8dde15388 (2026-11-08 08:08 CST) — "finish and publish the
bounded R-1 proposal already underway… R-1 remains proposal-only until
its own ruling" — confirmed Gmail 1a1bcd768e270708 (2026-11-08 14:26
CST). Both rulings are archived verbatim in `responses/` alongside
this proposal.
Investigation of record: DIRECTOR_REPORT_72_16_FLOW_AUTHORITY
(16/16 probe x2; Addendum 1 entrypoint probe 6/6 x2, E5 pinning the
open divergence).

## 1. The defect class, re-verified at this base (FACT)

`form/mandell/flow_executor.py::parse_program` builds each node's
Intent args solely from `_args_from_label(action, seed.label)`. That
function carries exactly three actions:

| action | Dell | label carried as | seed builder reads |
|---|---|---|---|
| stamp | 34 | `mark` (label, ≤48 chars) | `intent.args["mark"]` |
| cycle | 6 | `count` (int, clamped 1–99) | `intent.args["count"]` |
| form | 15 | `form` (cube/sphere/core/flower) | `intent.args["form"]` |
| **grow** | **13** | **— nothing (returns `{}`)** | **`intent.args["cycles"]`** |

Every other CORRESPONDENCE builder either takes no operand
(save/measure/test/architect/simulate/checkpoint/rollback/retry) or
reads the label from the parsed seed itself (discover, nurture —
`route_intent` re-parses `intent.mandel`, which is the node text, so
`parsed.label` reaches those builders intact). **grow is the sole
args-dependent action `_args_from_label` does not carry.**

Consequence (B4): `_seed_grow` defaults `cycles` to 1, so a flow
program `13[Loop] :: 3` executes `13[Loop] :: 1` — a different program
than the caller wrote, with the receipt recording the rewritten seed.

Fresh re-verification at this base (parse only, no state touched),
2026-11-08:

```
parse_program('13[Loop] :: 3 > 40[TokenCount]')
  -> node 13 grow args={}        (label '3' dropped)
  -> node 40 measure args={}
parse_program('06[Cycle] :: 3 > 40[TokenCount]')
  -> node 6 cycle args={'count': 3}   (control: carried)
```

## 2. Caller mapping (compatibility surface)

Callers of `flow_executor` at this base (from the investigation census,
unchanged since):

1. `english_composer.execute_composite` — LIVE. Compiles English
   multi-clause input to ` > `-joined Mandell and executes via
   flow_executor. No English clause compiles to a Loop program today
   (verified clause set in the investigation report), so B4 is not
   reachable through English composition at this base.
2. REPL DCC-IV branch — LIVE but fenced: the P10 pre-claim routes every
   parseable multi-atom seed to the canonical chain path first; the
   flow branch is a fallback for non-seed composed text only.
   Cross-process D1 proved REPL seed text executes with chain
   semantics (`:: 3` preserved).
3. Direct programmatic API (`parse_program` / `execute_program`) —
   in-repo consumers are tests only. **This is the only surface where
   B4 is reachable today.**
4. `operator_bridge` imports only the `_args_from_label` helper — not
   an execution path, but a second consumer of the exact function this
   proposal changes; its import must keep working unchanged in
   signature.

## 3. Operand comparison (chain vs flow, identical input)

| Input node | Canonical chain (`execute_seed`) | flow_executor today |
|---|---|---|
| `13[Loop] :: 3` | executes `:: 3` as written | **rewrites to `:: 1`** (B4) |
| `06[Cycle] :: 3` | executes `:: 3` | `count=3` carried; builder caps at 5 — converges |
| `34[Stamp] :: hello` | executes with mark `hello` | `mark` carried — converges |
| `15[Map] :: sphere` | executes form sphere | `form` carried — converges |
| `35[Discover] :: X` / `37[Nurture] :: X` | label executed | label reaches builder via parsed seed — converges |
| `13[Loop] :: abc` (non-numeric) | chain executes the seed as written; the Loop leaf receives the label text | label dropped; executes `:: 1` silently |

Scope boundary: B1 (`>>>` refusal), B2 (`:` refusal) and B3
(whole-program typed-arg refusal) are **not** part of R-1. They are the
R-2 convergence questions (Q-16.2/Q-16.3, still open). R-1 changes
nothing about flow classification, tokenization, or refusal shape.

## 4. The proposed repair (R-1, bounded)

One function, one file, plus its test:

1. `form/mandell/flow_executor.py::_args_from_label` gains a `grow`
   case symmetric with `cycle`: parse the label as an integer and
   return `{"cycles": n}` (the builder `_seed_grow` applies its own
   `max(1, cycles)` floor, exactly as the chain path relies on it).
2. Fail-closed on an uncarryable grow label: if the label is present
   and not an integer, `parse_program` refuses the node with a named
   diagnostic (e.g. `grow label 'abc' is not an integer count`) instead
   of silently defaulting to 1. This is the one behavioral choice the
   Director is asked to rule on (Q-R1.2); the alternative is the
   cycle-style silent clamp, which this proposal recommends **against**
   because silent defaulting is the defect class itself.
3. No other action changes. No signature change (`operator_bridge`'s
   import is unaffected). No change to `semantic_router`, `chain_exec`,
   the composer, or the REPL.

## 5. Failing-first evidence specification (to be implemented with the repair, T2)

New suite `form/flow_grow_label_test.py`, registered in
`form/regress.py` beside the other circuit suites, with a `smoke()`
entry point (the 72-32 suite-contract lesson):

- F1 (parse, defect): `parse_program('13[Loop] :: 3 > 40[TokenCount]')`
  node 0 args == `{'cycles': 3}`. Fails today (`{}`).
- F2 (execution, defect, isolated owner): executing that program
  records the resolved seed `13[Loop] :: 3`, never `:: 1`. Fails today.
- F3 (fail-closed, defect): `13[Loop] :: abc` refuses at parse with the
  named diagnostic; zero atoms execute. Fails today (executes `:: 1`).
- F4 (controls): cycle/stamp/form/discover/nurture operand preservation
  through `parse_program` + execution receipts — must pass before and
  after.
- F5 (mutant): deleting the grow case returns the suite to the exact
  F1–F3 failing profile; revert by inverse edit only.
- Full regress x3 (main-session background chain, logs under the
  goal's hidden_files) + terminal exact-head CI under the hard gate
  before any merge. Evidence tier T2 (behavior; no persistence
  semantics change — flow_executor owns no state).

## 6. What R-1 does NOT claim

- It does not converge the two composition authorities: B1/B2/B3 and
  the 2-of-9 flow classification remain exactly as they are, awaiting
  the R-2 / fence ruling (Q-16.1–Q-16.3 remain open in parallel).
- It does not make the flow API a certified public entry point
  (Q-16.4 remains the Director's call).
- 72-16 does not complete on an R-1 merge: DD-08 stays OPEN/GATED for
  the remaining divergences; the register records the B4 class only.

## Anticipated probes

- "Why not fold this into R-2?" — The Director's 08:08 work order
  sequences R-1 as its own bounded proposal first; R-2 is an
  architecture decision (Director-owned) that R-1 neither pre-empts
  nor obstructs: if R-2 later retires flow's private semantics, the
  grow case disappears with the layer that contained it.
- "Is any real user harmed today?" — No reachable production path
  (Section 2): REPL seeds are fenced by P10, English composition
  emits no Loop program, Studio never routes through flow. The harm
  is latent: any future composer mapping or caller emitting
  `13[Loop] :: N` (N≠1) into flow_executor silently executes N=1.
- "Could the fix change cycle/stamp/form behavior?" — No: the change
  is one added case in a dispatch whose existing cases are untouched;
  F4 pins their current behavior before and after.

## Questions for the Director

- Q-R1.1: Approve R-1 as scoped in Section 4 (one added `grow` case in
  `_args_from_label` + the Section 5 suite, T2, one PR)?
- Q-R1.2: Fail-closed named refusal for a non-integer grow label
  (recommended), or cycle-style silent clamp to 1?
- Q-R1.3: Confirm B1/B2/B3 stay out of this circuit and remain with
  the R-2/fence decision (Q-16.1–Q-16.3)?

## Records carried in this PR (per the 08:08 ruling)

- Register: 72-67 corrected to COMPLETED (scoped to workflow
  permissions + action pinning; strict confirmed 19/72) per
  Q-72-67.1; 72-16 records this proposal as published, awaiting its
  own ruling — no status advance claimed.
- Verbatim archives: `responses/DIRECTOR_REVIEW_EMAIL_2026-11-08_331_RULINGS.md`
  (Gmail 1a1bb7d8dde15388) and
  `responses/DIRECTOR_EMAIL_2026-11-08_CHANNEL_CONFIRM_R1_ORDER.md`
  (Gmail 1a1bcd768e270708).
