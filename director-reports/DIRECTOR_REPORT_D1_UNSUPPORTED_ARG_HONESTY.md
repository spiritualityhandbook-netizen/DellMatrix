# DIRECTOR REPORT — D1-UNSUPPORTED-ARG-HONESTY

Investigation findings + bounded repair proposal. **Investigation and
proposal only: no production code was changed, no signature was
registered, nothing was repaired in this circuit.**

- Circuit: D1-UNSUPPORTED-ARG-HONESTY (named target, Q2 of the
  Director's D1-TYPED-52-53 ruling, 2026-11-03)
- Base: main `91ebe20a5062c741cd07aab77d8ac45001cc1b28` (merge of
  PR #251, the D1-TYPED archival PR)
- Branch: `uni/d1-arg-honesty` (docs-only PR, unmerged by design —
  proposal gate, mirroring PR #250's stop condition)
- Status: **SUBMITTED — awaiting Director review**

## 0. Verdicts (one line per question)

| # | Question | Verdict | Evidence class |
|---|---|---|---|
| Q1 | Untyped Core II Dells (51–99) + typed args | **Silent drop confirmed as the general class behavior on the current tree** — across query, spectrum, and control-head handlers, single-atom and chain forms; the drop has three manifestations (§2.1) | PUBLIC_ENTRY_PATH (`execute_seed`), 10/10 probe expectations |
| Q2 | Registered Core II Dells: unknown roles, value types, duplicates, conflicts | **The refusal law holds; surfacing follows a fixed precedence** — any validation error refuses before mutation, but the receipt carries `errors[0]` only, in the order MISSING_REQUIRED > UNKNOWN_ROLE > INVALID_VALUE; no Core II wrong-value-type surface exists (all Core II roles are strings; the parser carries quoted strings only) | PUBLIC_ENTRY_PATH, 9/9 |
| Q3 | Core I leaf path (00–50) | **Args parse, then are silently ignored on every Core I path except Dell 8** — leaf arms, the `core_i_ops` front-door intercept, and chain re-execution (AF-1) behave identically; Dell 8 is the sole validated exception, single-atom and chained | PUBLIC_ENTRY_PATH, 11/11 |
| Q4 | Reserved/skipped atoms + typed args | **Honest skip receipts; args are never inspected for atoms that do not execute** — reserved, FlowThru-blocked, FlowOver-skipped, and zero-iteration atoms all receipt the skip reason; even a *registered* Dell's args go unvalidated when its atom is flow-blocked | PUBLIC_ENTRY_PATH, 6/6 |
| Q5 | Other public entry paths | **REPL = identical drop, witnessed in the user's own interface; Studio `/api/execute` rides `execute_seed` (code-verified equivalence); `flow_executor` never carries SeedAtom args — its tokenizer refuses parenthesized arg text outright** | REAL_USER_PATH / CROSS_PROCESS (REPL subprocess) + code citation, 3/3 |
| Q6 | Legacy-compatibility surface | **The parser's arg grammar is unambiguous** — typed args exist *only* as `(role="value", …)` immediately after an atom; every other parenthesized/`=`-carrying shape is label data or a parse refusal today. A gate keyed on the parsed `atom.args` dict cannot misclassify any legacy call | Parse-level probes, 15/15 |

Total executed probe expectations: **54/54 confirmed** (three initial
expectations were refuted on the *surfaced error string* and refined
into the precedence law of Q2 — §2.2; the refusal substance held in
every case).

## 1. Method and evidence geography

- All behavior was probed through the public executor
  (`form.mandell.executor.execute_seed`) on throwaway owners at the
  base tree, plus one literal REPL subprocess session
  (`python3 -m form.repl`, CROSS_PROCESS / REAL_USER_PATH).
- Precondition verified, not assumed (AGENTS §8/§9): a new Program is
  **not** empty — it is seeded with exactly one `welcome` unit. The
  probe harness asserts that baseline before every case; the first
  probe run falsified the emptiness assumption and the harness was
  corrected before any verdict was drawn.
- Throwaway owners' state files were removed after each case by
  exact snapshot diff (names containing the throwaway owner string);
  a final sweep confirms zero `ArgHon*` entries remain in
  `form/state/`, and the worktree is clean apart from this PR's docs.
- **Evidence geography (the noted exception from D1-TYPED-52-53,
  answered by inclusion): the probe scripts and logs are IN this
  PR**, at `director-reports/evidence/d1-unsupported-arg-honesty/`
  — 13 files, 55,880 bytes, Uni-produced, SHA-256 manifest in
  Appendix A. The Director can inspect or re-run them directly;
  no claim in this report depends on evidence outside the PR
  except the cited repository code at base `91ebe20`.

Probe files: `probe_lib.py` (harness), `probe_q1_coreii_untyped.py`,
`probe_q2_registered.py`, `probe_q3_corei.py`, `probe_q4_skips.py`,
`probe_q5_paths.py`, `probe_q6_legacy.py`, and `probe_q1.log` …
`probe_q6.log` (full terminal output of the final runs).

## 2. Findings

### 2.1 Q1 — the drop is the class behavior for untyped Core II

The mechanism is one gate in `form/mandell/chain_exec.py`
(`_run_atom`): typed args are inspected **only** under
`if atom_args and 51 <= n <= 99:` and then **only**
`if has_signature(n):`. For the 33 untyped Core II Dells (Appendix B)
none of the validate → resolve → conflict-check → lower sequence
runs; execution falls through on the legacy payload and the args are
never read again. Probed witnesses across all three handler families:

- **82[Group]** (spectrum): `82[Group](name="greens")` → `ok=True`,
  group created under the **default** name `group`. A bogus role
  `(bogus="x")` is likewise accepted with no `UNKNOWN_ROLE`. With
  both typed args and a label, the **label silently wins**
  (`(name="greens") :: blues` → group `blues`). Identical inside a
  chain (`51[Select] >> 82[Group](name="greens")` → group `group`,
  atom receipt `ok=True`, no arg mention).
- **97[Define]** (spectrum): `(name="tempo", meaning="120")` →
  `ok=True`, definition lands under the default name
  (`{'def': ''}`) instead of `tempo`.
- **78[Cause]** (query): `(cause="rain", effect="flood")` →
  `ok=False, error='malformed_relation'` — the args are dropped and
  the handler then fails on the *empty label* with an error that
  never mentions the supplied arguments. The drop is not always
  silent-success; it can also manufacture a misleading failure.
- **60[Branch]** (control head): `(bogus="x")` on the head is
  dropped identically; the frame executes on the label condition.

### 2.2 Q2 — registered Dells refuse correctly, with an error-precedence law

Verified on 55[Set] / 86[Delete] / 56[Get] plus a registry census:

- Refusal before mutation holds for every invalid call probed
  (store byte-identical after each refusal).
- **Precedence (new precision):** `OperatorSignature.validate()`
  collects all errors, but the receipt surfaces `errors[0]` only,
  in fixed order **MISSING_REQUIRED > UNKNOWN_ROLE >
  INVALID_VALUE**. `55[Set](bogus="x")` therefore surfaces
  `MISSING_REQUIRED: key`, not `UNKNOWN_ROLE: bogus`; with the
  required roles present, the same bogus role surfaces as
  `UNKNOWN_ROLE: bogus`. Three probe expectations that assumed the
  unknown-role string were refuted on exactly this point and
  re-probed with discriminators — the refusal and the
  zero-mutation guarantee held in every case.
- Duplicate roles refuse **at parse** (DAF-07): `duplicate role
  'key'`, before any execution.
- Typed+legacy conflict: differing pair → `ARGUMENT_CONFLICT`
  before mutation; identical pair proceeds (the AF-1 law,
  re-verified).
- **No Core II wrong-value-type surface exists:** the registry
  census shows 17 signatures (16 Core II + Dell 8); every Core II
  role is declared type `string`, the parser produces only quoted
  strings, and an unquoted value (`(key=5)`) is a parse refusal
  that never reaches validation. The only typed-value refusal in
  the system is Dell 8's enum `skin` (Q3).
- Gate refusals and handler refusals are distinguishable in the
  receipt: `86[Delete](key="ghost")` passes validation and refuses
  in the handler as `delete_missing:ghost`. A soft miss is a third
  shape: `56[Get](key="ghost")` returns atom `ok=True` with
  `missing` inside the result cell.

### 2.3 Q3 — Core I: parse yes, consume no (except Dell 8)

- The parser is shared: `03[Logic](bogus="x")` parses with
  `args={'bogus': 'x'}`. The question is purely execution.
- **Leaf path:** `03[Logic](bogus="x")` produces a byte-identical
  body to the bare atom; `05[Tone](bogus="x") :: joy` executes
  entirely on the label — args are never consulted by any leaf arm
  except Dell 8's TOAM block.
- **`core_i_ops` intercept** (front door, HANDLED Dells
  27/28/34/35/37/40/44/47): `apply_core_i` reads `seed.label`
  only — `27[Checkpoint](bogus="x")` and `34[Stamp](bogus="x")`
  are outcome-identical to their bare twins.
- **Chain path (AF-1):** args are re-emitted into the leaf
  re-execution seed and ignored there identically
  (`03[Logic](bogus="x") > 55[Set] :: k=v` → both atoms `ok=True`).
- **Dell 8[Create] is the sole exception on every path:**
  unknown role refuses (`UNKNOWN_ROLE`, with the same
  MISSING_REQUIRED-first precedence), non-enum `skin` refuses
  `INVALID_VALUE: skin=BANANA not in [...]`, typed name vs
  differing label refuses `ARGUMENT_CONFLICT` — all before
  mutation, single-atom and chained (in a chain, the refusal
  surfaces as the atom's `ok=False` receipt and FlowTo continues).
- **Existing pin:** the AF-1 suite itself pins today's Core I
  ignore as acceptable — `form/af1_chain_args_test.py` ("untyped
  args parity") asserts `43[Fallback](note="hi")` returns `ok=True`
  single and chained. A Core I gate would re-decide that pinned
  contract.

### 2.4 Q4 — skipped atoms: honest receipts, args never inspected

- Reserved atom in a chain (`151[Harmonic](bogus="x")`): the
  Decision-1 receipt (`ok=False, skipped=True,
  error='reserved/not-active'`, explicit reason); the arg appears
  nowhere. Single-atom reserved atoms route to the leaf and refuse
  as not-executable, identically with and without args.
- FlowThru-blocked atom (`82[Group](name="greens")` after a failing
  `53[Scope]`): receipt `error='flow_thru_block', skipped=True`;
  the Group never ran. The skip is decided in `execute_range`
  **before** `_run_atom`, so no validation ever runs — proven with
  a *registered* Dell: blocked `55[Set](key="k", value="v")`
  receipts the same flow skip, store untouched, no validation
  receipt.
- FlowOver-skipped and While-zero-iteration atoms: occurrence
  receipts with explicit skip reasons; args absent; atoms never
  ran.

Conclusion for the proposal: atoms that do not execute are already
honest, and a gate placed inside `_run_atom` inherits this for
free — it can only fire for atoms that actually execute.

### 2.5 Q5 — entry paths

- **REPL (REAL_USER_PATH, separate OS process):** the literal
  transcript is in `probe_q5.log`. `82[Group](name="greens")`
  created the default `group`; the in-REPL witness then separates
  the two worlds: `53[Scope] :: greens` refused
  `scope_unknown`-style ("unknown scope 'greens'"), while
  `53[Scope] :: group` succeeded. The drop is reachable and
  consequential in the user's own interface.
- **Studio `/api/execute`:** `gui/server.py` imports
  `execute_seed` from `form.mandell.executor` and calls it for the
  endpoint — the same front door, so no separate probe was run
  (equivalence by code citation; the REPL witness covers the
  shared path behaviorally).
- **`flow_executor` (flow programs / workshop path):** a different
  mechanism. Its nodes' `FlowNode.args` are *derived from the
  label* by `_args_from_label` (only stamp→`mark`, cycle→`count`,
  form→`form`); `SeedAtom.args` are never read. Seed-style typed
  args in flow-program text are not dropped — `_tokenize_program`
  refuses the text outright with `ValueError: expected flow …`
  (an unstructured exception, not a receipt). Out of the proposed
  gate's scope; recorded here as a boundary observation.
- **Semantic router (`route_intent`):** the correspondence
  builders emit label-form seeds; the generalized path
  (`_route_generalized`) re-attaches a parsed composition's args
  to the resolved Dell **only** as carried by the composition
  itself, and filters Intent-args to signature roles (an untyped
  Dell therefore receives `args == {}` from the Intent channel).
  Composition-carried args on an untyped Core II Dell *would*
  reach the chain executor — and under the proposed gate would
  refuse honestly there, surfaced in the RouteReceipt. No router
  code changes are proposed.

### 2.6 Q6 — the legacy surface a gate must not break

The parser (`form/mandell/seed.py`) attaches args under exactly
one shape: `_ARGS` — `(role="value", …)` *immediately* after the
atom, **no space**, role names `[A-Za-z_][A-Za-z0-9_]*`, values
double-quoted with no embedded `"` (values may contain `=`, `,`,
parentheses, and may be empty). Everything else is label data or a
parse refusal, probed:

- Labels are free text after `::`: parentheses (`playlist
  (draft) mix`), `=` (`note=a=b`), quotes, and even fully
  arg-shaped text (`predicate="garden"`) all parse as **labels**
  with `args == {}`. Segment labels between chain atoms are the
  same channel. Handler label grammars (`a>b` relations,
  `name=meaning` definitions, `k=v` patches) ride it.
- `(garden)` bare, ` (key="a")` with a space, and `(key=5)`
  unquoted are all **parse refusals today** — no legacy caller can
  depend on them executing.
- A ManifestSet's args dict rides **every** member atom; a
  chainlink pair attaches its args to both members. A per-atom
  gate therefore sees ManifestSet/chainlink args per member —
  stated explicitly in the proposal.
- Typed lowering is lossless where it exists: a value containing
  `=` (`x=y`) round-trips identically through the typed and
  legacy forms (execution twin, Q6).

**The gate-design consequence:** the dangerous misclassification
class is empty *if and only if* the gate keys on the parsed
`atom.args` dict. A gate keyed on raw seed text (e.g. searching
for `(`) would break label data; the proposal forbids that
implementation shape, and mutant M3 (§5) exists to kill it.

## 3. The established law (consolidated)

Typed arguments in DellMatrix today have exactly three regimes:

1. **Registered Dells (16 Core II + Dell 8):** validated before
   mutation on every execution path; refusals are honest receipts
   (`errors[0]` under the precedence MISSING_REQUIRED >
   UNKNOWN_ROLE > INVALID_VALUE; `ARGUMENT_CONFLICT` for
   typed/legacy disagreement; duplicates refused at parse).
2. **Untyped Core II Dells (33):** args are never inspected; the
   legacy payload decides everything. Outcomes range from silent
   success under a default (82, 97) to label-wins (82 with `::`)
   to a misleading handler failure (78). This is the defect class
   the Director named.
3. **Untyped Core I Dells (50, Dell 8 excepted):** args parse and
   are silently ignored on all three Core I paths; the behavior
   is currently *pinned as acceptable* by the AF-1 suite.

Atoms that do not execute (reserved/skipped) are honest in all
regimes and never have their args inspected.

## 4. Proposal — the fail-closed Core II argument gate

### 4.1 Insertion point

One insertion point: `form/mandell/chain_exec.py`, `_run_atom`,
extending the existing TOAM block. Today:

```
if atom_args and 51 <= n <= 99:
    if has_signature(n):
        ... validate -> resolve -> conflict-check -> lower ...
```

The gate adds the missing `else`: when the atom carries typed
args, the Dell is in 51–99, and `has_signature(n)` is false,
return the refusal **before** `execute_core_ii` is called.
This point is the single choke point for Core II execution:
`execute_seed` routes every Core II atom — single-atom seeds and
chains, REPL and Studio alike — through `execute_chain` →
`_run_atom`, and control heads (60–66) pass through it too.
No other production file changes for the gate itself (one
control-frame consequence is priced separately in §4.4).

### 4.2 Refusal semantics

- Error code: **`UNSUPPORTED_ARGS`** — a new code in the existing
  family (`UNKNOWN_ROLE`, `MISSING_REQUIRED`, `INVALID_VALUE`,
  `ARGUMENT_CONFLICT`, `REFERENCE_FAILED`). It must not overload
  `UNKNOWN_ROLE`: that code means "this role is not in the Dell's
  signature"; the gate's fact is stronger and different — "this
  Dell has no signature; no typed role is supported." Keeping
  them distinct preserves the census distinction the Director's
  Q2 ruling depends on.
- Receipt error string: `UNSUPPORTED_ARGS: <role names, sorted>`
  (mirrors the `UNKNOWN_ROLE: <role>` shape — code plus the
  offending input, which is the caller's own text).
- Message (in `messages`): `TOAM: Dell NN[Name] has no registered
  typed signature; typed arguments refused before execution:
  role="value", …` — mirroring the existing "TOAM validation
  failed for …" message shape.
- Atom receipt (via the existing `execute_range` wrapping):
  `{dell, ok: False, skipped: False, error: 'UNSUPPORTED_ARGS: …',
  reason: <same>}` — `skipped: False` because the atom *was*
  evaluated and refused, exactly like today's validation-failure
  receipts (cf. the chained Dell 8 receipt in Q3). Honest per the
  standing atom-result law: an operation that did not execute
  never reports `ok=True`.
- **Before-mutation guarantee:** the refusal returns from
  `_run_atom` before the `execute_core_ii` call — the same
  structural position as today's validation refusal, whose
  zero-mutation property Q2 re-verified. Proof obligations in the
  implementation circuit: full state snapshots (store, groups,
  defs, causes, plane, selection, last_result identity) compared
  around refused atoms, plus mutant M2 (§5).

### 4.3 Chain continuation

A gate refusal is an **atom failure** under the existing policy —
no new policy is created:

- FlowTo (`>` / `>>` chain walk): `last_ok=False`; the chain
  continues per its flow operators exactly as it does for a
  validation failure or a handler failure today.
- FlowThru (`>>`): downstream atoms receipt `flow_thru_block`
  skips, as probed in Q4.
- Chain aggregate: `state.ok=False`, `state.error` = the refusal,
  `partial` computed as today. Callers (executor, router,
  Studio) already surface this shape.

### 4.4 Control heads (60–66) — one priced sub-decision

Control heads pass through `_run_atom`, so the gate fires for
e.g. `60[Branch](bogus="x")`. But `_run_control` builds its frame
from the head's label independently of the head's result: a
refused head would still run its body on the label condition.
Two honest options:

- **(A) Recommended:** `_run_control` checks the head result for
  the gate refusal and short-circuits the frame — body
  occurrences receive skip receipts with reason `control head
  refused: UNSUPPORTED_ARGS …`, frame status `fail`. ~10 lines
  in `chain_exec.py`. The user asked for a typed branch; running
  the branch on the label anyway would be the same dishonesty
  class this circuit exists to close.
- **(B) Defer 60–66:** gate covers the 26 non-control untyped
  Core II Dells first; control heads get their own follow-on.
  Smaller, but leaves a known dishonest seam in place meanwhile.

Question Q-D2 (§7) asks the Director to choose.

### 4.5 What the gate does NOT do

- No signature registrations; the typed count stays 17.
- No handler changes; no Dell behavior changes for any
  `args == {}` call.
- No Core I changes (§4.7). No `flow_executor` changes. No router
  changes. No receipt-shape changes for any existing outcome.
- Skipped/reserved atoms are untouched: the gate sits inside
  `_run_atom`, which skipped atoms never reach (Q4) — an atom
  that does not execute keeps its skip receipt and its args stay
  uninspected, which is correct: there is no execution to refuse.
- Per-Dell signature deepening remains the separate grounded
  program the Director ordered (one Dell, one contract at a
  time); the gate is `has_signature`-driven, so each future
  registration automatically moves its Dell from regime 2 to
  regime 1 with no gate edit.

### 4.6 Legacy preservation contract

The gate fires **iff** `atom.args != {}` on an untyped Core II
atom. By Q6's grammar, that condition is unreachable for every
currently-valid legacy shape. The contract enumerates them; the
implementation circuit must prove zero behavioral change for
each:

1. Labels containing parentheses, `=`, quotes, or arg-shaped
   text, including segment labels between chain atoms.
2. Handler label grammars: relations (`a>b`), definitions
   (`name=meaning`), key/value payloads, scope/group names.
3. Trailing labels on any atom; labels on ManifestSet members.
4. Bare atoms, control frames and their condition labels,
   Else-marker occurrences (never reach `_run_atom`).
5. Typed calls on the 17 registered Dells (unchanged code path).
6. All Core I calls (out of scope, §4.7).

**The one intended behavior change, stated loudly:** a seed that
carries typed args on an untyped Core II Dell — including the
typed+label form where the label silently wins today (Q1) — will
refuse with `UNSUPPORTED_ARGS` instead of executing. That is the
defect being repaired, not a regression. ManifestSet and
chainlink atoms refuse per member (each member atom carries the
args; each receipts its own refusal).

Proof obligations: (i) the full regression (×3 sequential +
exact-head CI + fresh-clone) passes with no suite modifications
except any suite found to pin the drop itself for Core II — the
sibling search (§5) must enumerate those before implementation;
(ii) legacy-twin probes: for each of the 33 untyped Dells, the
legacy label form's outcome on the gated tree is compared
against the base tree's recorded outcome.

### 4.7 Core I disposition — DEFER (evidence-based)

- The Core I ignore is real but structurally different: there is
  **no single insertion point** — args flow through leaf arms,
  the `core_i_ops` intercept, the 21/22 live-identity intercept,
  and AF-1 chain re-emission. A Core I gate is a multi-point
  design, not an `else` branch.
- Today's behavior is **pinned as acceptable** by the AF-1
  suite's "untyped args parity" check (`43[Fallback](note="hi")`
  → `ok=True`). Refusing Core I args re-decides that contract;
  it deserves its own deliberate circuit, not a side effect of
  this one.
- The one Core I Dell with established typed semantics (Dell 8)
  already validates on every path.
- Recommendation: ship the Core II gate; queue Core I as a
  follow-on design question (Q-D3, §7) whose first act is
  re-deciding the AF-1 pin with evidence.

## 5. Implementation plan (future circuit, for Director approval)

- **Failing-first suite:** `form/d1_unsupported_arg_honesty_test.py`
  (coverage law), written and run against the unmodified tree
  first. Checks: per-family refusals (query 78, spectrum 82/97,
  control 60 per §4.4), receipt shape (`ok=False, skipped=False`,
  `UNSUPPORTED_ARGS`), zero-mutation snapshots around refusals,
  FlowTo-continuation and FlowThru-blocking after a refusal,
  typed+label on untyped → refusal, ManifestSet per-member
  refusal, reserved/skipped receipts **unchanged** (151 with
  args; blocked registered 55), registered-Dell behavior
  unchanged (52/53/55 twins), legacy twins for all Q6 shapes.
- **Mutants (defect-restoring, reverted by inverse edit):**
  M1 gate condition inverted (registered refuse / untyped pass)
  — suite must go red on both halves. M2 gate moved after
  `execute_core_ii` — zero-mutation checks must go red.
  M3 gate keyed on raw seed text containing `(` instead of
  `atom.args` — Q6 legacy-twin checks must go red.
  M4 refusal receipt marked `skipped=True` — receipt-shape
  checks must go red.
- **Sibling search scope:** test-corpus scan for typed-arg seeds
  on untyped Core II Dells (method from this investigation: the
  corpus scan found typed-arg usage concentrated on registered
  Dells — 08/51–58/67–69/84–88 — with the only ignore-dependent
  usage being Core I 43 in AF-1, which the gate does not touch);
  the semantic-router generalized path (§2.5); Studio/REPL ride
  `execute_seed` (no separate surface).
- **Gates:** regress ×3 sequential (state-sharing law) +
  exact-head CI verified by direct query + fresh-clone rerun;
  docs/versioning per the Step 11 precedent; live typed count
  unchanged (17) and stated as such.
- **Estimated footprint:** `form/mandell/chain_exec.py` ~15
  lines for the gate (+ ~10 for §4.4 option A), one new test
  file, report + INDEX. Zero handler files, zero signature
  files, zero parser changes.

## 6. SWAT pre-mortem — attacks on this proposal

1. **"Your error can be masked like UNKNOWN_ROLE was."** No:
   the precedence law (Q2) applies *inside* `validate()` for
   registered Dells. The gate produces a single error for an
   atom that has no validation at all; nothing competes with it.
2. **"A chainlink pair with one registered and one untyped
   member now half-refuses."** True, and honest: each member
   atom receipts its own outcome, and `partial` reports the
   split — the same machinery that already reports split
   chainlink outcomes (AF-1 evidence). The alternative (both
   silently execute) is the defect.
3. **"59[Route] as an Else marker will refuse Branch chains."**
   No: Else-marker occurrences are consumed by the chain layer
   and receipted as skips without reaching `_run_atom` (code
   verified). A *standalone* `59[Route](args)` refuses — that is
   the intended class behavior for an executing atom.
4. **"The English/router path will break."** The Intent channel
   is signature-filtered upstream (untyped ⇒ no args presented).
   Composition-carried args on an untyped Dell reach the gate
   and refuse in the RouteReceipt — intended, and strictly more
   honest than today's silent drop on that path.
5. **"Someone's workflow uses `82[Group](name=…)` as an idiom."**
   The corpus scan found no such usage in the test corpus; the
   idiom's current effect is *not* what its text says (it files
   under `group`), so any workflow depending on it depends on a
   mislabeling. The refusal tells the caller exactly what to do
   instead (use `:: name` or wait for a grounded signature).
6. **"Why not fix 78[Cause]'s misleading error instead?"** That
   error is a *symptom* of the drop; the gate removes the cause
   for the whole class. Handler-level error polish is a separate
   grounded change.
7. **"Performance / hot path."** The gate is one dict lookup on
   a branch already conditioned on `atom_args` being non-empty;
   `args == {}` calls take the identical path as today.

## 7. Anticipated probes and Questions for the Director

Anticipated probes (expected results stated in advance):
re-running any Q1 probe seed on the gated tree yields
`UNSUPPORTED_ARGS` with byte-identical pre/post state; Q6 legacy
seeds yield byte-identical outcomes to base; the Q5 REPL witness
(`82[Group](name="greens")` then `53[Scope] :: greens`) yields a
refusal at the first step, making the second step's ambiguity
impossible; `151[Harmonic](bogus="x")` in a chain keeps its
Decision-1 skip receipt unchanged.

Questions for the Director:

- **Q-D1 (naming):** Concur with `UNSUPPORTED_ARGS` as a distinct
  code, or should the refusal live in the `UNKNOWN_ROLE` family
  despite the census distinction in §4.2?
- **Q-D2 (control heads):** §4.4 option A (frame short-circuit
  in the same circuit) or option B (defer 60–66)?
- **Q-D3 (Core I):** Concur with deferring Core I (§4.7), and
  should the follow-on circuit's first act be re-deciding the
  AF-1 "untyped args parity" pin?
- **Q-D4 (scope confirmation):** `flow_executor`'s unstructured
  `ValueError` refusal of arg-shaped text (§2.5) stays out of
  this gate's scope — concur, or should it be receipted in the
  same circuit?

## Appendix A — Evidence manifest (SHA-256)

Evidence included in this PR at
`director-reports/evidence/d1-unsupported-arg-honesty/`
(Uni-produced probe scripts and their full terminal logs,
base `91ebe20`):

| SHA-256 | File |
|---|---|
| `8afbde6be89569929f55a55f0f7522b313f93c2f57f7ab553e0f4eaa25d5664d` | probe_lib.py |
| `264ab026c9a98c23b6d709d79c52663357dff1e9848d80f59b86013996cda843` | probe_q1_coreii_untyped.py |
| `71803dad80751c6090ccdfd9160601989a72ed7ab1f6d5f9547728fdfe35c6f9` | probe_q1.log |
| `61431b9a9b3f2cd3b50f362e23d45e328fc8eb43397d02f9b6f4bd902956dcb6` | probe_q2_registered.py |
| `8f09fd53d81fbaf9e73d9d9c638b95626066657550609d548ef483c93773ef95` | probe_q2.log |
| `5075a7c5c3fb73c49412311a087b6617268f72b013f782f1ee2a0cff0f304a0e` | probe_q3_corei.py |
| `f0228c9f65a44d8c3b6931f4fb54560727f0293823e0a61fda6076d40ae80c4c` | probe_q3.log |
| `d61711b33ad8220b9769a73549b1a39aeac6c676ec4ff61d44813adec97e8897` | probe_q4_skips.py |
| `b5aea5835d98fcbf15cdb1a463ea730cf15f29dad4a241d1037f41aaa69e88bc` | probe_q4.log |
| `806ca92828a3c1977206503a75647946c4d5c77171c98fb07cbc181f15e6e47e` | probe_q5_paths.py |
| `dcd1e9307999b0634c14be474cdac9af3c1d973de779a9602590acc834f19d09` | probe_q5.log |
| `c75c47cf4623554144868cb7c7f1d8a70c50467128c809734f481c79dee076b6` | probe_q6_legacy.py |
| `e0847f56fda2f83fc51dc92b53c80dd24cf41d12b7dc036a6c4789f4762726a0` | probe_q6.log |

## Appendix B — The 33 untyped Core II Dells (gate scope)

59[Route], 60[Branch], 61[Join], 62[Parallel], 63[Sequence],
64[Until], 65[While], 66[ForEach], 70[Count], 71[Measure],
72[Limit], 73[Threshold], 74[Weight], 75[Normalize], 76[Resolve],
77[Infer], 78[Cause], 79[Depend], 80[Context], 81[Reference],
82[Group], 83[Ungroup], 89[Diff], 90[Trace], 91[Assert],
92[Guard], 93[Try], 94[Catch], 95[Commit], 96[Revert],
97[Define], 98[Alias], 99[Compose].

Registered (gate-exempt, regime 1): 51, 52, 53, 54, 55, 56, 57,
58, 67, 68, 69, 84, 85, 86, 87, 88 — plus Core I's Dell 8 under
its own leaf TOAM block.
