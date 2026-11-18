# LIMITS VERIFICATION — WAVE 4 (2026-11-15)

Read-only verification of register items **R17–R21** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 3 (`LIMITS_VERIFICATION_WAVE3_2026-11-15.md`), re-verified first-hand at
**current main `04abc1ea9c1296e0605ed18b303eb9b6babfb799`** (merge of PR #422,
2026-11-15 07:35 CST; g31proof_clone fetched, checked out at that head, and
verified clean before and after — probe-owner state removed). No code changed;
nothing committed. Functional probes ran for every item (throwaway owners
`W4D4/W4D5/W4CYC/W4LOP/W4TR`, state deleted after; cell probes used temporary
`CELLS` entries, removed after).

**Numbering:** R17–R21 are taken exactly as Wave 3's queue named them, which
matches the census's ranked HINDERS-US register (R17 Mandell statement ceilings
MAX_BOUND=64 + phantom 8 · R18 control nesting depth 4 · R19 Cycle/Loop clamp
1..5 · R20 cell expansion depth 8 · R21 Core II evidence evictions 512/64/16).
Census line numbers had drifted for several sites; today's are given per item.

**Wave-4 method (per the brief's caution):** this wave enters ruled-semantics
territory, so every item separates **(a) the value hinders** — the bound's size
blocks legitimate work, on workload evidence — from **(b) the mechanism disobeys
its ruling** — the code's bound differs from the ruled value/shape, or enforces
silently where the ruling required visibility. A bound faithfully implementing
its ruling is classified **FAITHFUL-GUARD**, with the evidence that would change
that stated. Rulings are cited from the working plan
(`director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md`, §12) and in-code ruling
citations; where no ruling exists, the item says UNRULED plainly.

**Headline of the wave:** of the census's five HINDERS-US verdicts, only one
survives intact (R20). R17 splits — its phantom-8 half is a live ruling
violation, its 64 half a genuine value hindrance. R19's value turns out to be
*ruled*, and what remains defective is visibility on three of its six paths
plus one unreconciled ceiling. R18 and R21 do not survive the ruling check:
both mechanisms refuse/count exactly as their documented designs require.

---

## R17 — Mandell statement ceilings: MAX_BOUND=64 + the phantom 8

- **Census sites:** predicate.py:14-15/:281-284/:292; query_ops.py:147-157;
  spectrum_ops.py:11/:713-725.
- **Sites today:** `MAX_BOUND = 64` at `form/mandell/predicate.py:14`,
  `DEFAULT_BOUND = 8` at `:15`; `validate_bound` at `:281-295` — empty or
  `"max"` input returns `(True, DEFAULT_BOUND)` at `:284`, `n > MAX_BOUND`
  returns `invalid_limit` at `:292`. The Dell-72 Limit handler
  (`form/mandell/query_ops.py:140-160`) intercepts *before* `validate_bound`:
  bare Limit refuses `limit_unspecified` (`:143-146`), `"max"` stores
  `str(MAX_BOUND)` (`:147-150`). The Compose path's `_compose_bound` at
  `form/mandell/spectrum_ops.py:713-716` intercepts **nothing** — it calls
  `validate_bound(st.limit or "")` directly and falls back to
  `COMPOSE_BOUND = 8` (`spectrum_ops.py:11`) when validation fails; the
  resulting bound gates composition expansion depth at `:723`
  (`depth > bound` → `compose_depth`). The honest accessor exists and the
  loop family uses it: `bound_detail` at `form/mandell/control_runtime.py:39`.
- **The ruling:** DD-44 (plan §12.56, Ace ruling 2026-11-09) — loop bounds
  must be explicit: the number is stated, or the loop asks, or it fails with
  the why; the silent default 8 is "the defect this ruling removes."
  DD-44 EXTENDED (plan §12.63a, same date) generalizes it program-wide:
  "wherever a limit is in play for a Dell-involving operation, the number is
  stated, or the operation asks, or it fails with the full why. **No silent
  defaults anywhere in the family**" (§12.63a.2), and "no per-Dell private
  caps invented ad hoc" (§12.63a.3) — quantity dimensions must be boundable
  by the one stated Limit authority.
- **Probe (functional, pure functions + stub state, 04abc1e):**
  `validate_bound("")` → `(True, 8, "")`; `validate_bound("max")` →
  `(True, 8, "")` (function level — the Dell-72 path intercepts `"max"`
  first, so this half is latent everywhere except direct consumers);
  `validate_bound("64")` → `(True, 64, "")`; `validate_bound("100")` →
  `(False, 8, "invalid_limit")`. `_compose_bound` on a state with **no Limit
  ever stated** → **8**; with `limit="3"` → 3. `bound_detail` on the same
  unstated state → `{"status": "unspecified", "value": None}` — the honest
  answer the Compose path never asks for. Consumer audit: `validate_bound`
  has exactly three production consumers — `bound_detail` (intercepts empty
  and `"max"` before calling), the Dell-72 handler (same interceptions), and
  `_compose_bound` (no interceptions). The phantom's live reach is exactly
  the Compose path, as the census said.
- **DISPOSITION: DEFECT-CONFIRMED (phantom-8 half) + CONFIRMED-HINDERS
  (MAX_BOUND=64 value half).**
  - *Phantom 8 — (b), disobeys its ruling.* With no Limit stated, a Compose
    expansion silently runs under a bound of 8 that nobody stated, asked
    for, or saw refused — the precise shape DD-44 abolished and §12.63a.2
    extended to every Dell-involving quantity. `COMPOSE_BOUND` is itself a
    per-Dell private cap of the kind §12.63a.3 forbids, and it is nearly
    dead code: because `validate_bound("")` returns ok, the fallback fires
    only on an *invalid* stored limit — which then also silently becomes 8
    instead of DD-44's "invalid" refusal. The depth refusal at the bound
    (`compose_depth`) is visible; what is invisible is that the bound was
    never stated.
  - *MAX_BOUND=64 — (a), the value hinders; the mechanism is honest.* No
    ruling names 64 (the string `MAX_BOUND` occurs nowhere in the plan;
    DD-44 governs explicitness, not the ceiling). Enforcement is an explicit
    `invalid_limit` refusal — nothing silent. But a stated `Limit 100` is
    refused and `Limit max` resolves to 64, so a count-driven While/Until
    over a 100+-member workload cannot be stated in one command. Recorded
    mitigation, honestly: ForEach (Dell 66) iterates a selection per-member
    and is not under `MAX_BOUND` (plan §12.57), so the per-member idiom
    exists; the hindrance binds count-stated loops specifically.
  *Failing-first sketch:* (i) on a fresh state with no Limit stated, run a
  composition whose expansion depth exceeds 8 and assert the operation
  refuses with an explicit limit-unspecified receipt instead of executing
  under 8 — fails today at `spectrum_ops.py:715` (executes, bound 8);
  (ii) state `72[Limit] :: 100` and assert the statement is accepted —
  fails today at `predicate.py:292` (`invalid_limit`). Repair shape: route
  `_compose_bound` through `bound_detail` (unspecified → refuse/ask, never
  8; retire `COMPOSE_BOUND`), and raise `MAX_BOUND` to a practical ceiling
  with the explicit refusal kept above it.

## R18 — Control nesting depth 4

- **Census sites:** control_runtime.py:9; chain_exec.py:319-323.
- **Sites today:** `MAX_DEPTH = 4` at `form/mandell/control_runtime.py:9`;
  enforcement moved to `form/mandell/chain_exec.py:360-364` — a control head
  (CONTROL_HEADS = {60, 62, 63, 64, 65, 66}, `control_runtime.py:10`)
  encountered at `depth >= MAX_DEPTH` appends the message
  `control depth bound 4`, sets `state["error"] = "depth_bound"`, records a
  failed per-atom result, and returns. Depth is **not** settable via Dell 72:
  `bound_detail`'s domain is the loop bound (`control_runtime.py:39-67`
  names no depth), and no other setter exists.
- **The ruling:** none found. `MAX_DEPTH` / `depth_bound` occur nowhere in
  the plan or the decision register. (The HCN blueprint's "DRAFT depth 4
  below the Program" and its open question Q-R2.8 concern HCN host nesting —
  a different, unbuilt mechanism — and are a draft question, not a ruling on
  this constant.) The value 4 is **UNRULED**. The mechanism, however, is
  test-pinned contract: `control_runtime_test.py:77` pins
  `error == "depth_bound"` for the five-deep nest.
- **Probe (functional, public `execute_seed` path, 04abc1e):** four nested
  `63[Sequence]` heads around a body → runs, body context set (`TrueArm`),
  no error. Five nested Sequences → `error = depth_bound`, `ok = False`,
  nothing executed. The census scenario (While > ForEach > Branch >
  Sequence > a fifth control head) is the same shape and refuses the same
  way.
- **DISPOSITION: FAITHFUL-GUARD** — the mechanism disobeys nothing: there is
  no ruled value to disobey, the refusal is explicit and receipted (message,
  error name, failed atom result, whole-range refusal — nothing is silently
  skipped or partially run), and the guard's named failure (runaway control
  recursion) is real. The census's HINDERS-US reading does not survive:
  unlike the store cuts of Waves 1–3, a refused composition loses no data
  and mis-executes nothing; the author restructures (Sequence bodies, named
  cells) and re-runs. Two honest qualifications: (1) the value is UNRULED,
  so "faithful" certifies the mechanism's honesty, not the number's
  authority; (2) DD-44 EXTENDED §12.63a.1 says quantity dimensions "must be
  boundable by a stated Limit" — depth is not yet wired under Dell 72, an
  unbuilt-coverage gap §12.63a.3 itself says to claim only per-Dell from
  tests. *Evidence that would change this verdict:* a real composition the
  pipeline or Ace needs that cannot be restructured under depth 4 and is
  refused (none recorded), or a ruling stating a depth value/depth-under-
  Limit contract — at which point any divergence becomes a (b) finding.
  No repair sketch (no CONFIRMED/DEFECT finding); the §12.63a wiring of
  depth under Limit is named here as future authorized scope, not a defect.

## R19 — Cycle/Loop repetition clamp 1..5 (and the flow path's 99)

- **Census sites:** executor_leaf.py:164/:239; chain_exec.py:403;
  semantic_router.py:154; translate.py:681; flow_executor.py:58.
- **Sites today (all six, drifted):**
  - Cycle arm: `form/mandell/executor_leaf.py:167` — `n = max(1, min(n, 5))`;
    the receipt at `:168` reports only the executed count (`Cycle x{n}: …`).
  - Loop arm: `executor_leaf.py:242` — `executed = max(1, min(requested, 5))`,
    reported at `:248-250` (`Loop: requested R, executed E.` +
    `(clamped to 1..5)` when they differ).
  - Chain Loop-body repetition: `form/mandell/chain_exec.py:480` —
    `_executed = max(1, min(_parsed, 5))`, clamped identically to the leaf
    (comment `:460-479`); the leaf's own receipt carries the report.
  - Router seed: `form/mandell/semantic_router.py:158` —
    `n = max(1, min(n, 5))  # Dell 6 caps at 5` inside `_seed_cycle`; the
    clamped number is baked into the seed text itself.
  - English translate: `form/mandell/translate.py:839` — same clamp, same
    comment, inside the `cycle` intent builder; the Intent carries the
    clamped count.
  - Flow path: `form/mandell/flow_executor.py:70` —
    `n = max(1, min(99, n))` for the same `"cycle"` action.
- **The ruling:** the 1..5 value is **RULED** — Director FIX step 6, item
  B2, cited in code at `executor_leaf.py:219-222`: *"Loop uses Cycle's
  finite 1..5 bound, reports requested vs executed counts and any clamp, and
  refuses malformed/non-numeric labels explicitly."* (The plan references
  Director FIX step 6 as the repair event throughout, e.g. §12 at
  ACE_FUTURE_DEVELOPMENT_PLAN.md:462/:486.) So the value is not this wave's
  to second-guess: the census's "the value is what hinders" is superseded
  by the ruling evidence — 5 is the contract until an authority re-rules it.
  For the flow path's **99, no ruling was found** (plan/register/code
  comments silent); the census's "UNKNOWN which ceiling is intended"
  remains unknown after this wave's search.
- **Probe (functional, public paths, 04abc1e):**
  - `06[Cycle] :: 20` → receipt `Cycle x5: +0 new +0 evolved` — executed 5;
    the requested 20 appears **nowhere** in the receipt. Clamp silent.
  - `13[Loop] :: 20` → receipt `Loop: requested 20, executed 5.
    (clamped to 1..5)` — the B2 contract, obeyed in full.
  - Router: `_seed_cycle` with `count=20` → seed text `06[Cycle] :: 5` —
    the 20 is discarded at seed construction, before any receipt exists.
  - English: `translate("cycle 20")` → Intent `cycle`, `args={"count": 5}`,
    seed `06[Cycle] :: 5` — same silent pre-clamp.
  - Flow: `_args_from_label("cycle", "20")` → `{"count": 20}` — the flow
    path honors 20 under its unruled 99 ceiling: the same semantic, two
    ceilings, and which one governs depends on which door the user entered.
- **DISPOSITION: DEFECT-CONFIRMED (visibility + reconciliation halves);
  the 1..5 value itself is FAITHFUL to its ruling.** The Loop arm and the
  chain body-repetition obey B2 completely — value *and* reporting. Three
  paths disobey the family's ruled shape: the Cycle arm executes the ruled
  value but never reports the clamp (the receipt shows only `x5`, so a user
  who asked for 20 cycles sees a normal success receipt for 5 — the exact
  under-reporting B2 was written to end on the sibling arm); the router and
  translate paths clamp *before* execution, inside seed/Intent
  construction, where no receipt can ever name the loss; and the flow path
  silently applies a different, unruled ceiling (99) to the same action,
  so the ruled contract does not govern every door. None of this is silent
  *data* loss — it is silent *work* loss: the un-run repetitions simply
  never happen, and on three paths nothing says so.
  *Failing-first sketch:* `06[Cycle] :: 20` (directly, and via
  `translate("cycle 20")` and the router) and assert the receipt/intent
  names requested 20 vs executed 5 — fails today at `executor_leaf.py:168`
  (receipt shows only 5), `semantic_router.py:158` and `translate.py:839`
  (intent/seed carry only 5). Repair shape: report requested-vs-executed
  on the Cycle arm exactly as Loop does; carry the requested count through
  router/translate into the execution receipt instead of clamping at seed
  construction; and reconcile `flow_executor.py:70`'s 99 with the ruled
  contract **by ruling** (fold to 1..5 with reporting, or rule a distinct
  flow ceiling explicitly) — the code must not keep two ceilings for one
  semantic on no authority.

## R20 — Cell expansion depth 8

- **Census sites:** seed.py:44, :352-353.
- **Sites today (exact):** `CELL_DEPTH = 8` at `form/mandell/seed.py:44`;
  enforcement at `:352-353` — `if depth > CELL_DEPTH: return
  Seed(ok=False, error="cell_depth")`, failing the **whole** seed
  expansion. The independent cycle guard sits immediately below at
  `:355-358` (`key in seen` → `error="cell_cycle"`).
- **The ruling:** none found — `CELL_DEPTH` / `cell_depth` occur nowhere in
  the plan or the decision register. The value 8 is **UNRULED**.
- **Probe (functional, `expand_cell` over temporary `CELLS` entries,
  04abc1e):** an 8-link alias chain (cell → cell → … → plain seed) expands
  whole (`ok`). A 10-link chain → `ok=False, error="cell_depth"` — the
  entire expansion fails, not just the deep tail. A self-referential cell
  → `ok=False, error="cell_cycle"` — the seen-set guard fires on its own,
  confirming the runaway protection does not depend on the depth number.
- **DISPOSITION: CONFIRMED-HINDERS (the value)** — with the mechanism's
  honesty recorded: the failure is an explicit named error, not a silent
  cut, so this is not a defect. But the bound is unruled, and its cost is
  pure hindrance: infinite recursion is already prevented by the
  `cell_cycle` seen-set (proven above), so the depth cap adds no
  protection the system lacks — it only forbids a legitimate composition
  shape (a macro library layered 9+ deep: macro built on macro, the cell
  system's stated purpose) and forbids it wholesale, failing the entire
  seed rather than the deep branch. Workload evidence is the constructed
  probe above (a 10-link alias chain), stated as such: no field-observed
  9+-deep production cell library was measured, and if one is ever
  measured the verdict strengthens from constructed to observed.
  *Failing-first sketch:* define a 10-link cell alias chain and assert
  `expand_cell` returns the fully expanded seed — fails today at
  `seed.py:352` (`cell_depth`). Repair shape: raise `CELL_DEPTH` to a
  generous named backstop (e.g. 64) and let the seen-set cycle guard carry
  the runaway protection, or drop the depth check on paths the cycle guard
  covers — one constant, test-pinned by the chain probe.

## R21 — Core II session evidence evictions: traces 512, snapshots 64, terminal tx 16

- **Census sites:** core_ii_exec.py:7-8/:66-79/:132; spectrum_ops.py:14.
- **Sites today:** `TRACES_CAP = 512` at `form/mandell/core_ii_exec.py:7`,
  `SNAPSHOTS_CAP = 64` at `:8`; trims via `_trim_oldest` at `:79`
  (snapshots, inside `append_snapshot` — the AF-5 one append path) and
  `:132` (traces, inside the atom runner's `mark()`); counters
  `traces_dropped_total` / `snapshots_dropped_total` / `tx_dropped_total`
  at `:54-56`. `TERMINAL_TX_KEEP = 16` at `form/mandell/spectrum_ops.py:14`;
  pruning in `_prune_tx` at `:66-83` — TERMINAL frames only, newest 16
  kept, **all** active frames kept, pruned count added to
  `tx_dropped_total` at `:83`. The whole witness layer is session-only:
  `serialize_core_ii` (`form/persist_core_ii.py:59`) writes scope/selected/
  store/groups/defs/aliases/compositions and no traces, snapshots, or tx
  frames at all.
- **The rulings / documented design:** three separate authorities converge.
  (1) The plan's Dell-90 examination (ACE_FUTURE_DEVELOPMENT_PLAN.md, at
  :3934) records the trace contract as design: *"BOUNDED MEMORY, COUNTED
  LOSS. Cap 512 entries (TRACES_CAP); oldest drop off, and the drop is
  counted by traces_dropped_total (AF-5 heritage) — within a session, loss
  is never silent, only bounded"* and *"(5) SESSION-ONLY… The whole Core II
  witness layer is uniformly session-scoped."* (2) The Try examination
  (:4281) records the same for frames: *"Terminal frames are kept to the
  newest 16 (TERMINAL_TX_KEEP, AF-5); pruned count in tx_dropped_total."*
  (3) The counters' session-only scope is a stated decision at the site
  itself (`core_ii_exec.py:51-53`): *"session-only dropped counters (never
  durable — the collections reset on load, so a durable counter would
  false-witness session loss across a reload)."* One forward ruling does
  touch the family: DD-54 (plan §12.86a (1)) rules that "today's
  SNAPSHOTS_CAP=64 hard constant **retires into**" DD-54's adjustable undo
  depth — but DD-54 is itself an unimplemented circuit (Wave 1's R4; its
  correction plan is the Q-LC.1 plan stage), so the retirement is that
  circuit's tracked scope, not an unexecuted detail of this cap.
- **Probe (functional, 04abc1e):** 65 `append_snapshot` calls on a real
  `CoreIIState` → 64 kept, `snapshots_dropped_total = 1`. 513 Core II atoms
  (`70[Count]`) executed through `execute_seed` on one program → 512 traces
  kept, `traces_dropped_total = 1`. `_prune_tx` over 17 committed + 2 open
  frames → 18 kept (16 newest terminal + both active),
  `tx_dropped_total = 1`.
- **DISPOSITION: FAITHFUL-GUARD (all three caps).** Every eviction is
  counted at the moment and site of loss; active transaction frames are
  never pruned; the newest terminal frame (the refusal-identity witness)
  is always retained; and the session-only scope of both the collections
  and their counters is the documented design, with its reasoning written
  at the counter definition. The census's sharpest point — "counters
  reset on load, so across sessions the loss is invisible" — is answered
  by that design: the collections themselves do not cross a reload, so a
  surviving counter would witness losses from a log that no longer exists;
  within the session the design's own terms promise, the loss is never
  silent. No mechanism here disobeys a ruling, and no value is shown to
  block a recorded workload. The one owed change is named, not hidden:
  `SNAPSHOTS_CAP`'s retirement into an adjustable depth is DD-54's scope
  and lands when that circuit is built. *Evidence that would change this
  verdict:* a real session whose provenance question (Dell 90) or Revert
  target was lost to a trim and the loss mattered (none recorded), or
  DD-54's execution leaving the hard constant in place afterward.
  No repair sketch (no CONFIRMED/DEFECT finding).

---

## Wave summary

| Item | Site today (main 04abc1e) | Disposition | One-line basis |
|---|---|---|---|
| R17 — MAX_BOUND=64 + phantom 8 | predicate.py:14-15/:281-295; query_ops.py:140-160; spectrum_ops.py:11/:713-716; honest path control_runtime.py:39 | **DEFECT-CONFIRMED** (phantom 8) + **CONFIRMED-HINDERS** (64 value) | Probe: `_compose_bound` with no Limit stated → 8, silently, while `bound_detail` on the same state says "unspecified" — the silent default DD-44 (§12.56) abolished and §12.63a.2 extended family-wide; `validate_bound("100")` → `invalid_limit`, and no ruling names 64 |
| R18 — Control nesting depth 4 | control_runtime.py:9; chain_exec.py:360-364 | **FAITHFUL-GUARD** | Probe: 4 nested Sequences run; 5 refuse with `depth_bound` message + failed atom receipt, test-pinned (control_runtime_test.py:77); value 4 UNRULED but refusal is explicit, loses nothing silently; §12.63a depth-under-Limit wiring named as unbuilt scope, not a defect |
| R19 — Cycle/Loop clamp 1..5 + flow 99 | executor_leaf.py:167 (Cycle), :242/:248-250 (Loop); chain_exec.py:480; semantic_router.py:158; translate.py:839; flow_executor.py:70 | **DEFECT-CONFIRMED** (visibility/reconciliation); value FAITHFUL to its ruling | The 1..5 value is RULED (Director FIX step 6, B2, cited executor_leaf.py:219-222) and Loop obeys it fully (probe: "requested 20, executed 5. (clamped to 1..5)"); but Cycle's receipt shows only "x5", router/translate clamp inside the seed/Intent where no receipt can name it, and the flow path silently applies an unruled 99 to the same action (probe: count 20 admitted) |
| R20 — Cell expansion depth 8 | seed.py:44; :352-353; cycle guard :355-358 | **CONFIRMED-HINDERS** (value) | Probe: 10-link alias chain fails whole with `cell_depth`, 8-link expands, self-reference is caught by the independent `cell_cycle` seen-set — the unruled depth number adds no protection the cycle guard lacks and forbids layered macro composition wholesale (constructed workload, stated as such) |
| R21 — Core II evictions 512/64/16 | core_ii_exec.py:7-8/:54-56/:79/:132; spectrum_ops.py:14/:66-83; persist_core_ii.py:59 | **FAITHFUL-GUARD** | Probes: 65 snapshots → 64 kept/dropped 1; 513 atoms → 512 traces/dropped 1; 17 terminal + 2 active tx → 16+2 kept/dropped 1 — every loss counted at its site, active frames never pruned, session-only scope is the documented design (plan :3934/:4281; reasoning at core_ii_exec.py:51-53); SNAPSHOTS_CAP's retirement is DD-54's tracked scope |

**Queued for wave 5 (next five in register order):**
R22 — Automatic knowledge selection returns at most 5 (knowledge_selector.py:117; :334-348 at census) ·
R23 — Outcome evidence truncated at capture + outcome search capped at 100 (outcome_ledger.py:83-88; search :495 at census) ·
R24 — Translate slices operands before execution (translate.py:299-720 at census) ·
R25 — Compare/Threshold shorthand drops tokens past 2 (query_ops.py:90; :176 at census) ·
R26 — DuoBeta ledger detail cut to 120, two enforcements (duobeta/growth.py:59; duobeta_learn.py:134; persist.py:341 at census).
*Wave-5 note:* R22–R26 return to the data/evidence family. Two carry
classification traps of the wave-4 kind: R25's token drop is a **test-pinned
contract** (`rewrite_drops_tokens`) partially mitigated by DD-42 — a pinned
contract can only be re-pinned by ruling, so wave 5 must separate "the
contract was ruled/pinned" from "the evaluated question differs from the
asked one" exactly as wave 4 separated value from mechanism; and R24's
translate slices are the *front* end of the same operand chain whose store
end Waves 1–3 verified (R13–R16, R29) — wave 5 should state, per slice,
whether the cut is pre-execution rewriting (the census's charge) or a
refusal, and check the DD-44-extended explicitness law (§12.63a) where a
slice feeds a Dell operation.
