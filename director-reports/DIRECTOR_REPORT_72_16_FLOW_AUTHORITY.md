# DIRECTOR REPORT — 72-16: Legacy Flow Executor vs Canonical Chain Ownership (Investigation)

Report ID: DIRECTOR_REPORT_72_16_FLOW_AUTHORITY
Base: main f92e5b1865ba765b11f1bab94cc2de3204607a7b
Evidence: `director-reports/evidence/72-16-flow-authority/` (q16_probe.py, two identical runs 16/16 exit 0, MANIFEST.sha256 verified)
Scope: investigation only. No product code changed. No remedy implemented.

## The question

Is `form/mandell/flow_executor.py` (DCC-IV) an independent execution
authority next to the canonical chain executor (`chain_exec.py`, reached
via the `executor.execute_seed` front door), or a subordinate
implementation of it? Required evidence (Director, Mode A 2026-11-05):
call graph, execution entry points, state mutation boundaries, and a
reproducible authority-conflict test if dual authority exists.

## Call graph (FACT, code at base)

Front door (`executor.execute_seed`, executor.py):
- multi-atom seed or Core II primary → `chain_exec.execute_chain`
- single Core I atom → `core_i_ops` / `live_identity` / `executor_leaf`
- flow_executor is **not** in this path.

chain_exec per atom (`_run_atom`):
- Core II (51–99): `execute_core_ii` directly, with typed-arg validation,
  reference resolution, and ARGUMENT_CONFLICT law in chain_exec itself.
- Core I (00–50): re-emits the atom (typed args and label preserved) into
  `execute_seed(program, leaf, _leaf=True)`.
- Composition state is chain-owned: `attach(program)` carries
  flow_taken, context, refs, route, snapshots; `_apply_flow` implements
  all nine FLOW_CONTRACT operators (`>`, `>>`, `>>>`, `:`, `::`, `:>`,
  `<:`, `<:>`, `<<[Delta]`).

flow_executor per node (`execute_program`):
- builds a `translate.Intent` and calls
  `semantic_router.route_intent`, which executes through
  `executor.execute_seed` (semantic_router names
  `_AUTHORITY_EXECUTOR = "form.mandell.executor.execute_seed"`).
- contains **no** direct call to `executor_leaf` or `execute_core_ii`
  (probe C1, source census).
- generalized Core II nodes (no CORRESPONDENCE pair) route via
  `operator_bridge.resolve` for identity and the chain_exec authority
  for execution (semantic_router `_route_generalized`).

## Execution entry points reaching flow_executor (LIVE census)

1. `english_composer.execute_composite` — English multi-clause input is
   compiled to a Mandell program (`" > "` joins only) and executed via
   flow_executor. Live from the REPL English branch and direct API.
2. REPL DCC-IV branch (repl.py, after the P10 pre-claim): lines
   containing `>` or `:` that are **not** parseable multi-atom seeds.
   The P10 pre-claim sends every parseable multi-atom seed to the
   canonical seed path first, so at the public REPL path the flow
   branch is a fallback for non-seed composed text only.
3. Direct programmatic API (`parse_program` / `execute_program`) —
   consumers in-repo are tests (dcc_xx, p0r3, ssi_i, english_composer,
   flow_executor suites).
4. `operator_bridge` imports only the `_args_from_label` helper — not
   an execution path.

Studio (`gui/server.py`) executes via `execute_seed` only; no flow path.

## State mutation boundaries (FACT)

flow_executor owns no store, no state file, no Dell state. It mutates
only (a) through `route_intent → execute_seed` results, threading
`receipt.new_program` into the next node, and (b) `program.note_seed`
history bookkeeping (best-effort, swallowed on failure). Every Dell
mutation a flow program causes is performed by the canonical
executor/leaf/Core II authorities, identically to the chain path.

## Probe results (two identical clean runs, 16/16, exit 0)

Convergence controls (shared domain — semantics agree):
- A1: `34[Stamp] :: created > 40[TokenCount]` — both paths run both
  atoms, all ok.
- A2: `28[Rollback] >> 40[TokenCount]` — both paths block atom 40 after
  the rollback failure (ok=False, skipped=True, explicit reason).
  FlowThru policy converges, including the cascade rule.
- A3: `06[Cycle] :: 3` via flow — label→args yields count=3 (cycle is
  one of flow's three hardcoded label actions).

Divergences (composition semantics — reproducible authority conflicts):
- B1: `40[TokenCount] >>> 12[Test]` — chain executes (40 ok; 12 skipped
  by FlowOver, honest receipt). Flow refuses the whole program at parse:
  "flow '>>>' is REQUIRES_RUNTIME_SUPPORT, not executable".
- B2: `40[TokenCount] : 12[Test]` — chain runs both atoms (FlowBy binds
  context). Flow refuses: "flow ':' is DESCRIPTIVE_ONLY".
- B3: `34[Stamp](mark="hello") > 40[TokenCount]` — chain refuses
  **per atom** under the certified Core I gate (atom 34 ok=False,
  UNSUPPORTED_ARGS: mark) and the chain **continues** (atom 40 ok=True).
  Flow refuses the **whole program** at tokenize time ("expected flow
  at 9"), zero atoms execute, with a generic tokenizer error instead of
  the gate's named diagnostic.
- B4: `13[Loop] :: 3 > 40[TokenCount]` — chain executes the seed as
  written (`13[Loop] :: 3`). Flow **rewrites it to `13[Loop] :: 1`**:
  `_args_from_label` has no `grow` case, so the label is dropped,
  Intent args are `{}`, and the correspondence seed builder defaults
  cycles to 1. The flow receipt's own messages record the executed
  seed `13[Loop] :: 1` — a different program than the caller wrote.

Public-path fence (cross-process, REAL_USER_PATH):
- D1: the B4 text piped into `python3 -m form.repl` executes with
  chain semantics (seed as written, `:: 3`; no `:: 1` rewrite). The
  P10 pre-claim fences the divergence off the REPL seed path.

Exposure classification for B4 (verified, not assumed): no English
clause compiles to a Loop program today (`grow`/`loop`/`iterate`/
`repeat … times and then …` all fail composition honestly), so B4 is
reachable today only through direct flow-API callers with Mandell
text. It becomes a live-path defect the moment any composer mapping
emits a `13[Loop] :: N` program with N ≠ 1, or any future caller routes
seed text to flow_executor.

## Verdict

**flow_executor is NOT an independent Dell-execution authority.** It
executes no Dell itself; every node delegates to the canonical
router → front door, and it owns no state. On Dell execution, it is a
subordinate composition layer.

**flow_executor IS an independent composition-semantics authority**
over the domain it accepts: its own tokenizer grammar (rejects
typed-arg syntax), its own flow classification (2 of 9 operators
executable; refuses the other seven that chain_exec implements), its
own label→args construction (3 hardcoded actions; silently resets
`grow` counts to 1), and its own refusal granularity (whole-program at
parse time vs the chain's per-atom refusal with continuation). Within
that domain the two authorities return different verdicts, different
diagnostics, and — for B4 — execute different programs from identical
input.

The system is protected today by routing discipline, not by semantic
unity: the P10 REPL pre-claim, the composer's `>`-only compilation,
and the correspondence gate keep production traffic inside the
convergent subset.

## Remedy options (for ruling — nothing implemented)

- R-1 (narrowest): fix the B4 class inside flow_executor — build node
  args from the parsed seed's label for every action via the
  correspondence seed builders' own label handling, or refuse labels
  flow cannot carry (fail-closed instead of silent rewrite).
- R-2: converge composition semantics — make flow_executor delegate
  program execution to `execute_seed` on the raw program text
  (retaining its receipt format), retiring its private flow
  classification; english_composer keeps its compile-then-execute
  shape.
- R-3: formally fence flow_executor as an API-only legacy layer:
  document its domain (>-only, label-args for stamp/cycle/form),
  refuse everything else with named diagnostics, and pin B1–B4
  behaviors as accepted limitations.

Uni recommendation: R-1 first (kills the one silent-rewrite class),
with R-2 vs R-3 as the Director's architectural call.

## Anticipated probes

- "Is B4 reachable by a real user today?" — Not via REPL seeds (D1)
  and not via current English composition (verified clause set above).
  Reachable via the module's public API with Mandell text. Labeled
  API-level, not REAL_USER_PATH.
- "Does flow_executor bypass the UNSUPPORTED_ARGS gate?" — It never
  reaches it: its tokenizer rejects typed-arg syntax first (B3). The
  divergence is refusal shape and diagnostic, not a gate bypass.
- "Are outcome records duplicated?" — No: flow nodes capture Outcome
  V1 once in the route_intent wrapper; the generalized path is
  explicitly single-capture (semantic_router comment).
- "Did the probe mutate real state?" — No: every run used per-owner
  isolated Programs (Q16* owners); the operator's state was untouched.

## Questions for the Director

- Q-16.1: Which remedy — R-1 (repair the label-args class in place),
  R-2 (converge onto execute_seed), or R-3 (formal fence as legacy)?
- Q-16.2: Should the B3 refusal shape converge — i.e., is
  whole-program parse refusal an acceptable contract for the flow
  API, or must non-executable nodes refuse per-node with the chain's
  named diagnostics?
- Q-16.3: Is the 2-of-9 flow classification (DCC-IV's FLOW_CLASSIFICATION)
  a deliberate product contract to preserve under any remedy, or
  superseded by chain_exec's nine-operator FLOW_CONTRACT ownership?
