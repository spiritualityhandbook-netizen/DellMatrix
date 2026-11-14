# G31-CONTRACT-01 — EXECUTION PROFILES PROPOSAL (BOUNDED, DESIGN ONLY)

Prepared under the Director's FL-G31-02 disposition
(2026-11-14): KEEP_ISOLATED accepted; one authoritative
operator vocabulary with explicit execution profiles
replaces the earlier blanket executor-unification proposal
(SUPERSEDED). This proposal changes no product code,
authorizes no implementation, PR, or merge. It preserves S3
behavior and the existing seven refusals exactly.

AMENDED 2026-11-14 under the Director's CONDITIONAL
CONFIRM: corrections C-1 (refusal visibility) and C-2
(failure-state persistence) are resolved at contract level
in sections 4 (D-6/D-7), 5, and 6 (T-5a/T-5b/T-5c), with
behavioral evidence at pin 1c5129e cited in place.

## 1. THE VOCABULARY (ONE AUTHORITY)

The single vocabulary authority remains
control_runtime.FLOW_CONTRACT (form/mandell/
control_runtime.py:130): nine operators — > FlowTo,
>> FlowThru, >>> FlowOver, : FlowBy, :: DeepFlowBy,
:> FlowTowards, <: FlowFrom, <:> DynamicFlow,
<<[Delta] DeltaFlow. Profiles below are VIEWS over this
vocabulary, never second vocabularies. An operator's NAME
and MEANING are profile-independent; its EXECUTION is
profile-defined. Any future contract documentation lands as
annotations on this one authority — no new contract file,
no duplicate table.

## 2. PROFILE A — CANONICAL CHAIN PROFILE

Surfaces: chain_exec.execute_chain;
operator_bridge.compose_execute (delegates, + its
fail-closed unknown-Dell boundary, operator_bridge.py:367);
the REPL raw-seed branch (form/repl.py:3441).
Operators: ALL NINE, with the semantics documented in
FL-G31-02 section 2, restated as profile law:
- ">" runs the successor unconditionally; ">>" alone gates
  (blocked successor receipted skipped); ">>>" skips to
  Join/end with honest skip receipts; the five binding
  operators WRITE their bindings and run the successor even
  after a failed predecessor (chain ok=False preserved);
  "<<[Delta]" appends a chain snapshot (failed states
  included, labeled by chain ok) that is NOT a committed
  generation.
- All flow writes pass the ONE mutation door with a
  checkpoint captured before each write (chain_exec.py:
  245-254). A failed atom writes nothing.
- Receipts: per-atom {dell, ok, skipped, reason} +
  bilingual messages.
- Rollback: untouched by this profile — 28[Rollback] stays
  authority-mediated over committed generations only.

## 3. PROFILE B — CORRESPONDENCE COMPOSITION PROFILE

Surface: flow_executor (form/mandell/flow_executor.py) —
parse_program :187 / execute_program :220.
Consumers: english_composer.execute_composite
(english_composer.py:201-211); the REPL residual DCC-IV
branch (repl.py:3466).
Operators: ">" and ">>" ONLY. The other seven are refused
at parse with classification-named errors (flow_executor.py
:174: REQUIRES_RUNTIME_SUPPORT for >>> and <<[Delta];
DESCRIPTIVE_ONLY for :, ::, :>, <:; UNSAFE/AMBIGUOUS for
<:>). THE REFUSALS ARE CONTRACT, preserved verbatim — they
are the r2 honesty suite's "no silent downgrade" guarantee.
Profile-B semantics on the shared two, stated so the
profiles never pretend to be one: nodes route through
semantic CORRESPONDENCE actions via the semantic router
(not Core dispatch); Assert does NOT consume the seed label
payload the way Profile A does (the divergence P10's REPL
comment records); receipts are per-step {index, mandel,
action, dell, arguments, ok, error, skipped} with
completed/failed/skipped counts.
Composer discipline: english_composer emits only " > "
joins (english_composer.py:170) — Profile B's lawful input
alphabet is ">" (joins) and ">>" (within parsed programs);
a composed program outside the profile fails at parse,
never mid-execution.

## 4. DISPATCH RULES (PUBLIC PATH)

From the REPL dispatch as built (repl.py:3441-3483),
stated as rules:
D-1 A line that parses as a valid multi-atom seed routes
to PROFILE A. This branch runs FIRST.
D-2 A line that is not such a seed, contains ">" or ":",
and parses as a flow program with more than one node
routes to PROFILE B.
D-3 English multi-step input ("and then / after that /
then") routes to the composer, whose programs execute
under PROFILE B.
D-4 NO SILENT SUBSTITUTION: a program refused by its
profile is never executed by the other profile in the same
dispatch pass. D-1 precedes D-2 precisely so Profile A
programs cannot fall into Profile B; Profile B's parse
ValueError falls through only to non-flow handlers, never
to Profile A execution of the same text.
D-5 Single atoms and all other lines follow the existing
seed/English paths unchanged.
D-6 REFUSAL vs PARSE MISS (C-1). Two error classes leave
Profile B's parser, and dispatch must treat them
differently. A REFUSAL is the recognized-but-unsupported
case: the operator is in the vocabulary and outside the
profile (flow_executor.py:174 — "flow '<op>' is <CLASS>,
not executable"). A refusal is an intentional, observable
act: dispatch MUST surface it (the REPL prints the refusal;
the composer path propagates it as the call's error). A
refused program is never executed by either profile (D-4).
A PARSE MISS is the malformed case (flow_executor.py:137
expected-atom, :170 expected-flow, :183 node/flow count):
the line was never a flow program; it MAY fall through
quietly to the non-flow handlers. Current state, named as
the gap this contract closes: the REPL's DCC-IV branch
catches both classes in one except ValueError and passes
silently (form/repl.py:3480), so today a refusal disappears
exactly like a miss. The contract requires the classes to
be distinguished at dispatch (by error origin/message
class); the implementing change belongs to the future
authorized circuit — this proposal fixes the CONTRACT:
refusals are visible, misses may be silent, and neither is
ever a silent reroute.
D-7 Within execute_composite, a Profile B refusal already
propagates as an exception to the caller (no catch in
english_composer.py:201-211); D-6 preserves that posture —
propagation is the composer's observable surface.

## 5. CROSS-PROFILE SAFETY

- Shared state, separate semantics: both profiles act on
  the same Program through existing authorities (Profile A
  via Core dispatch; Profile B via the semantic router);
  neither owns private state.
- The Assert-label difference is the one known semantic
  divergence on a shared operator's operand handling; it is
  NAMED here so no future proof assumes operand parity.
- Neither profile may mint rollback rights: DeltaFlow
  snapshots (A) and step receipts (B) are records, not
  committed generations.
- A program's profile is determined at dispatch (section 4)
  and never changes mid-execution.
- FAILURE-STATE PERSISTENCE (C-2). Flow bindings are Core
  II WORKING state. The persistence contract permits working
  state to persist by the ordinary save path — including a
  failed chain's receipted binding, which is working state
  with an honest ok=False on its chain. Committed
  generations are a different substance: they are minted
  ONLY by the checkpoint authority (checkpoint_generation),
  and chain execution under either profile never calls it.
  A receipted binding mutation therefore cannot become an
  authorized committed generation accidentally — the only
  road from working state to a generation is the checkpoint
  path with its own gates. Behavioral evidence at pin
  1c5129e (disposable clone): committed_generation_state
  (checkpoint_generation.py:434) returned ('absent', None)
  for the owner BEFORE, AFTER a failed binding chain (whose
  context="Count" binding did land in working state), and
  AFTER a DeltaFlow chain. Working state moved; the
  generation census did not.

## 6. REGRESSION TEST PLAN (PROPOSED; for the future circuit)

Existing coverage to PRESERVE (named so the circuit does
not rediscover it): p10_flow_grammar_test (Profile A at
REAL_USER_PATH; parse set == contract keys == publicly
executable set; bindings survive save+reload);
flow_executor_test (Profile B executes > / >>; the
classification table itself); r2_semantic_honesty_test
(Profile B refusals); english_composer_test, dcc_xx_test,
ssi_i_test, p0r3_execution_integrity_test (consumers);
af2_delimiter_addressing_test (shared tokenizer authority).
New boundary cases this proposal adds:
T-1 A ">>>" seed line at the REPL executes under Profile A
(skip receipt present) — dispatch-order proof.
T-2 A non-seed flow-program line containing ">>>" is
refused by Profile B and executed by NEITHER profile
(state unchanged; no receipts beyond the refusal path).
T-3 A composer-generated program executes under Profile B
with step receipts; a hand-altered composite containing
":" fails at parse with zero atoms executed.
T-4 The Assert-label pair: the same Assert chain text
under each profile produces its profile's documented
behavior, and the receipts make the difference visible
(no silent divergence).
T-5a Bind-after-failure under Profile A persists through
save+reload exactly as receipted (extends the matrix
probe to the persistence boundary).
T-5b GENERATION CENSUS (C-2): the owner's committed-
generation state (committed_generation_state) is IDENTICAL
before and after a failed binding chain, and after a
DeltaFlow chain — working state may move; no generation is
minted. (Probe evidence at pin 1c5129e: 'absent' in all
three readings.)
T-5c ROLLBACK POSTURE (C-2): after the failed binding
chain, bare 28[Rollback] remains denied exactly as before
the chain — the failed chain conferred no rollback right
and created no rollback target.
T-6 DeltaFlow snapshot followed by bare 28[Rollback]
remains denied under Profile A (separation regression).
Acceptance: each test states its profile, its dispatch
rule, and its receipt evidence; a failure names the profile
or rule that broke, never just the operator.

## 7. BOUNDARIES

In scope: the vocabulary statement, the two profiles, the
dispatch rules, the test plan. Out of scope: any code
change; any S3 expansion (Q-FL1's proof gate stands);
demand flow (Q-FL2's separate pilot); the hidden-flow
assessment (named by the Director as remaining open work —
it proceeds as its own audit, tracing actual dependencies,
not as part of this contract). Documentation of the
profiles in the runtime contract is the future circuit's
first deliverable, placed as annotations on the existing
FLOW_CONTRACT authority per section 1.
