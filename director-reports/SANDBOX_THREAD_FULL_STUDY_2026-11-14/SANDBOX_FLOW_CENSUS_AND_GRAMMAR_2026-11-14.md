# FLOW — CENSUS, MIRROR, AND THE UNWRITTEN GRAMMAR (SANDBOX)

Ace's order, 2026-11-14: flow is underdeveloped. Research
everything in the program that requires flow or can use it
optionally; every flow idea that exists but is not
implemented (some may need modification first); possibly new
flow ideas that are needed — hidden flow named explicitly;
mirror against all components and against the Grand Plan;
research the internet for anything that benefits flow. Goal
in Ace's words: so we can WRITE, SEE, UNDERSTAND, and COMMAND
all the ways anything can flow.

Method: live codebase at main
8dd4c5295023573b61e0ae89017cf9944c52cfb7 (flow_executor.py,
chain_exec.py, control_runtime.py read in full at the flow
sections); the Grand Plan file; the early-Mandell segment
(VB.3's sixteen flows); web research (Reactive Streams,
information-flow security, Petri nets, Kahn/CSP — cited).

## 1. THE HEADLINE — ONE GRAMMAR, TWO EXECUTORS, TWO TRUTHS

The canonical contract (control_runtime.FLOW_CONTRACT) names
nine flows: > FlowTo, >> FlowThru, >>> FlowOver,: FlowBy,
:: DeepFlowBy,:> FlowTowards, <: FlowFrom, <:> DynamicFlow,
<<[Delta] DeltaFlow.

- The DIRECT chain path (chain_exec.py) implements ALL NINE.
The seven beyond > and >> are not decorations: ":" writes
the chain's context, "::" writes a deep ref, ":>" writes
the route, "<:" writes a from-ref, "<:>" writes both,
">>>" skips forward to Join (skipped atoms receipted
ok=False skipped=True, the DAF-08 honesty rule), and
"<<[Delta]" appends a state snapshot. Since DD-51 Ring 1,
these writes pass through the ONE mutation door with a
checkpoint captured first — they are receipted writers.
- The COMPOSED path (flow_executor.py — the English/REPL
composition route) executes only > and >> and REFUSES the
other seven (REQUIRES_RUNTIME_SUPPORT / DESCRIPTIVE_ONLY /
UNSAFE-AMBIGUOUS).

So the same seed text is a working program on one road and a
refusal on the other. This is the registry schizophrenia the
VB.2 corpse audit killed, one level down: not two registries
this time, but two flow contracts wearing one grammar. Every
other finding in this study is downstream of this split.

## 2. THE FLOW CENSUS — EVERYTHING THAT FLOWS TODAY

CHAIN FLOW (Mandell): the nine operators above; plus the
control Dells that bend flow from inside: 60[Branch] (with
59[Route] consumed as its Else marker), 61[Join], 63[Sequence],
13[Loop], 06[Cycle], 64[Until], 65[While], 66[ForEach],
93[Try], 94[Catch], 91[Assert], 92[Guard], 42[Retry],
43[Fallback], 32[Pause], 33[Resume].

BODY FLOW: ForceField.tick is a circulation loop (body pulse
first, forces circulate, weather reads health). Water is a
literal flow system: streams merge into rivers (volumes add,
parents recorded), streams settle into pools. Breath is a
two-stroke cycle. Resonance DIFFUSES over the resonance
graph — flow across edges over time, the program's one true
field flow.

IDEA FLOW: the knowledge lifecycle is a pipeline with gates —
STORED > ELIGIBLE > SELECTED > ROUTABLE > USED > OBSERVED >
LEARNED — and the Knowledge Influence Chain exists to explain
any item's passage. The Nursery is a flow with weather:
proposals are born, ranked, aged (3/7/14, fade 30), confirmed
(Ace's hand), placed. DuoBeta is an evidence flow: outcomes >
proposals > gate (>=3) > advisory reranking. Exchange moves
seed packets BETWEEN minds, landing as PENDING proposals.
36[Inject] is a named inflow.

DERIVED FLOW: the Derivation Discipline is computation
flowing from records to readings (lattice views, notes, the
chord, wells, plants, maps) — flow that must be rebuildable
and may never flow backward into the records. Distill (38)
and Compress (29) are flow narrowings. Checkpoints are state
flowing through TIME as sealed generations; 28[Rollback] is
the one sanctioned reverse flow; DeltaFlow's snapshot is its
marker.

AUTHORITY FLOW: rulings flow Ace > Director/Keeper > Uni >
repository on timed cycles (hourly, 15-minute) with
watermarks (DIRECTOR_MAIL_LAST_PROCESSED is, literally, a
stream-processing watermark). Heartbeat is an observation
flow. The Psalm Matrix live feed is a flow of work-states to
the witness.

## 3. THE GRAND PLAN MIRROR

The Grand Plan says the word "flow" nine times and is
secretly a flow architecture end to end: the idea's JOURNEY
(§5) is a pipeline whose every arrow is "a gate with a
receipt"; the GATE ECONOMY is a valve system (nothing
crosses without a gate + receipt — flow control, stated as
law); the RECEIPT COMMONS is flow instrumentation; H4's
forces are the body's CIRCULATION; the Derivation Discipline
is its flow direction law (records -> readings, never back).
What the Grand Plan does NOT have: a flow GRAMMAR item. Its
register G-01..G-28 contains no entry for the two-executor
split, the refused seven, or backpressure. PROPOSED (not
filed): G-31 FLOW UNIFICATION, in §4's style — one contract,
both paths; zoo disposition per §4 below; the two sanctioned
new flows of §5; a hidden-flow pass inside the X11 census.

## 4. THE UNIMPLEMENTED ZOO — DISPOSITIONS

From VB.3's sixteen (the nine above are §1-2):
- +Flow (append to stream): PARTIAL today via 63[Sequence]
and ManifestSets. Disposition: ADAPT as sugar only if a
circuit shows a seed that Sequence cannot say plainly.
- =Flow (parallel paths): the real gap behind 62[Parallel]
executing sequentially (G-11, OWNED: DD-43 isolated copies
+ Join). Disposition: MODIFY FIRST — implement only under
the token/channel discipline of §5 (F-N2/F-N3); a bare
"run both" operator without join semantics is how races
are born.
- /\Flow (flow against / opposition): no operator exists,
but the PROGRAM grew the honest version elsewhere — the
conflict router and disposition machinery (H5): opposing
flows are routed to a ruling, not threaded through each
other. Disposition: ADAPT as a ROUTE, not an operator —
opposition flows to disposition with a receipt.
- #Flow (hard stop): PARTIAL (32[Pause], chain halt on
Assert/Guard failure). Disposition: ADAPT — name the
existing halts honestly instead of adding a symbol.
- ^Flow (eject to parent scope): PARTIAL — FlowOver's
skip-to-Join is a scope exit wearing a jump's name.
Disposition: MODIFY — separate the two ideas (see >>>).
-!Flow (execute regardless of state): REJECT as syntax.
Forcing past gates contradicts the gate economy at its
root. Its lawful residue already exists and is not an
operator: an AUTHORITY override (Ace/Director ruling) with
a receipt.
-?Flow (conditional, loop-guard): composition of 60[Branch]
+ 64[Until] says it today. Disposition: ADAPT as sugar at
most; no new semantics.
- {}Flow (flow within isolation): the MECHANISM exists
(isolated copies, sandbox rooms, per-owner state) with no
operator naming it. Disposition: ADOPT candidate — promote
the mechanism to a named flow when DD-43 lands, because
what has a name can be receipted.

From today's own grammar (modify-before-implement):
- >>> FlowOver: VB.3 meant "major conceptual jump"; the code
does "skip to Join." Both useful; they are different
flows. MODIFY: keep the implemented one (skip-to-Join) and
let the topic-jump meaning retire to SEQUENCE boundaries
between seeds, where it already lives.
- <:> DynamicFlow: classified UNSAFE/AMBIGUOUS on the
composed path, implemented on the direct path as a double
write (from-ref + route). MODIFY: disambiguate by contract
— it is a two-write operator; both writes receipted (they
already are, via the mutation door); then admit it on both
paths or neither.
- <<[Delta] DeltaFlow: code appends a snapshot; VB.3 read it
as pulling the past into now. MODIFY the WORDS, not the
code: DeltaFlow = mark a snapshot here; 28[Rollback] =
travel to one. Already true in mechanism; the contract
should say it.

## 5. NEW FLOWS THE RESEARCH SAYS ARE NEEDED

F-N1 DEMAND FLOW (backpressure) — from Reactive Streams:
data flows downstream, but a DEMAND signal flows upstream —
the consumer's request(n) tells the producer how much it may
send, demand is additive, and a producer must never emit
more than requested. DellMatrix
flows are all push: nothing lets a downstream gate throttle
an upstream producer. Where it bites today: proposal volume
into the Nursery (the 200-PENDING ceiling is a WALL — the
Elastic Limits Doctrine wants a signal instead), dock output
volume, Psalm feed rate. Form: a demand receipt traveling
against the flow; producers receipt their compliance. This
is the one wholly new DIRECTION of flow the program lacks:
backward, against the data, carrying capacity.

F-N2 TOKEN FLOW (Petri nets) — places hold tokens; a
transition fires only when EVERY input place holds one,
consuming and producing tokens;
sequence, choice, parallelism, joining, and resource limits
are all wiring; and the payoff is analysis you can DECIDE —
reachability ("can this order ever end up both shipped and
refunded?") and boundedness.
Mirror: 61[Join] today is a label without a token rule;
DD-43's isolated copies + Join want exactly this semantics.
And the Dock already runs a token pool in disguise: twelve
docks, expiring skill leases = places with limited tokens.
Form: fork emits tokens, Join fires on all-arrived, leases
are token places. ADAPT (as the semantics under Parallel/
Join, not as a new notation).

F-N3 CHANNEL FLOW (Kahn / CSP) — deterministic processes
communicating only through FIFO channels, reads blocking,
no peeking: the network's result is then independent of
timing and schedule.
Mirror: DellMatrix prizes determinism (deterministic replay,
exact-head evidence) but only inside one sequential chain.
Form: Parallel's isolated copies exchange results ONLY
through receipted FIFO channels whose histories ride the
receipt — any schedule, same outcome, provable by replay.
ADAPT (the discipline that makes F-N2 safe to run).

F-N4 HIDDEN FLOW — the one Ace named. Information-flow
security separates EXPLICIT flows (direct assignment) from
IMPLICIT flows (influence through control structure — the
branch taken reveals the guard) and COVERT channels (timing,
termination, exceptions leak what values cannot)
.
DellMatrix's hidden flows, named:
(i) SANCTIONED AND GATED: DuoBeta's advisory reranking is
outcome history flowing into selection — influence with a
gate, a ledger, and a truth firewall. The model citizen.
(ii) SANCTIONED AND DECLARED: derived senses (notes,
chord, weather) are records flowing into perception —
lawful because declared and rebuild-only; the PROJECTION
stamp IS a taint label, in security language.
(iii) EXPLAINED: selection itself is an implicit flow —
what got SELECTED reveals ranking internals; the Knowledge
Influence Chain exists precisely to make this flow
speakable (WHY-USED / WHY-NOT-USED).
(iv) UNSANCTIONED, ON RECORD: ambient persistent state
flowing into a "fresh" Program (KIE-I's ~142 proposals) —
a hidden flow that already caused one incident class; the
Completeness Law's orphans are its cousins (influence with
no caller = flow with no channel).
Policy mirror: STORED =/> USED is a NONINTERFERENCE
policy, and the gate economy is its enforcement. The
instrument the field uses is TAINT TRACKING: labels that
propagate with the data. DellMatrix already mints the
labels (PROJECTED, PENDING, sandbox-only); what is missing
is the AUDIT that follows influence end-to-end and asks of
every arrival: by what channel did you get here?
Disposition: ADOPT as an audit instrument (THE HIDDEN FLOW
AUDIT, §6), not as an operator.

F-N5 WATERMARK FLOW — stream processing's "complete up to
here" marker. DellMatrix already runs two: the mail
watermarks and generation seals. Minor but real: ledger-
reading flows (Atlas maps, the census) should carry the
watermark they were computed at, so a reading can never
silently mix eras. ADAPT as a receipt field, not an operator.

## 6. INSTRUMENTS

- THE FLOW CENSUS (this study is its seed): every flow in
§2, classified EXECUTING / PARTIAL-BY-PATH / NOTATION-ONLY
/ IMPLICIT, refreshed by X11.
- THE TWO-PATH TEST: any seed using any of the nine flows
must behave identically under chain_exec and flow_executor,
or the difference is itself receipted. Falsifies §1's split
forever, one operator at a time.
- THE HIDDEN FLOW AUDIT: pick an influence (a ranking, a
selection, a derived view); trace its channels backward;
any leg with no gate and no receipt is a finding.
- THE DEMAND RECEIPT: a downstream gate's request(n) and the
producer's compliance, recorded as a pair (F-N1's proof).
- THE TOKEN LEDGER: joins and leases recorded as token
movements (F-N2's proof) — the Dock's lease system is the
pilot.

## 7. VERDICT AND OPEN QUESTIONS

Flow is not missing from DellMatrix; it is UNEVENLY
ADMITTED. The body flows, idea flows, and authority flows
are rich and mostly unnamed; the chain grammar is half-
admitted, with its richer half implemented on one road and
refused on the other. The completion path is therefore not
"add flows" but: (1) unify the two executors under the one
contract (the zoo dispositions of §4 are the work list);
(2) admit the two genuinely new mechanics the research
supports — demand flow (F-N1) and token/channel discipline
under Parallel (F-N2/F-N3); (3) run the hidden flow audit
(F-N4) as part of the census, because a program that can
command its flows must first be able to SEE the ones it
didn't declare.

Open: Q-FL1 — does the composed path gain the seven, or does
the grammar narrow to what both paths run? (Director's call;
this study's evidence favors admitting, since the direct
path's semantics are already receipted and tested.) Q-FL2 —
demand flow's first consumer: Nursery intake or dock output?
Q-FL3 — is FlowOver's topic-jump meaning worth a separate
notation, or is seed-boundary enough? Q-FL4 — which hidden
flows beyond (iv) does the first audit find?

— Sandbox study. Nothing implemented, nothing filed into the
Grand Plan; G-31 is proposed above, not entered.

---

## DIRECTOR REVIEW ADDENDUM — 2026-11-14 (MODE A, CONDITIONAL ACCEPT)

Rulings: Q-FL1 ADMIT CONDITIONALLY (preserve the richer
direct-path semantics; equivalence and safety proofs required
before composed-path admission). Q-FL2 Nursery intake is the
demand-flow pilot (bounded; existing capacity enforcement
preserved until replacement behavior is proven). Q-FL3 NO
separate topic-jump notation (>>> stays skip-to-Join; seed
boundaries carry conceptual transitions). Q-FL4 AUDIT FIRST
(no speculation about additional hidden-flow defects).
G-31 FLOW UNIFICATION accepted as a PROPOSED Grand Plan
research item — not an operative closure requirement.
Corrections accepted into this study: (1) bounded FIFO
channels do not guarantee deadlock freedom — F-N2/F-N3's
Parallel/Join design must test blocked reads, full buffers,
cancellation, and resource exhaustion; (2) a projection label
is not a security-grade taint system — F-N4's audit must
trace actual dependencies, including branch decisions and
observable timing/termination effects.
REFINEMENT (from the differential matrix, same day): this
study's section 1 located the split at "the composed path";
the matrix (SANDBOX_FLOW_DIFFERENTIAL_MATRIX_2026-11-14.md)
shows the public composition path (operator_bridge.
compose_execute) was already converged to chain_exec in
2026-10 — S1 and S2 are identical on all 18 runs. The
surviving split is the standalone flow_executor module,
preserved deliberately, refusing the seven fail-closed at
parse. Section 1's framing stands corrected to that extent;
its census, zoo dispositions, and new-flow proposals are
unaffected.

## FL-G31-02 ADDENDUM — 2026-11-14 (Director SCOPED PASS + trace)

The Director returned SCOPED PASS on the differential
matrix, reframed G-31 (not a public-path failure; a
standalone-module consistency and contract-clarity issue),
and revised Q-FL1: do NOT automatically expand S3 — trace
its role first. The trace (SANDBOX_FLOW_FLG31_02_TRACE_
2026-11-14.md, pin 1c5129e) classifies S3 ACTIVE_INTERNAL
(live english_composer consumer; bounded REPL residual
branch; tokenizer authority for seed.py; refusal behavior
itself a tested honesty contract), documents the nine-
operator authoritative contract including bind-after-failure,
verifies the mutation-door/checkpoint invariants under
failure (failed atoms write nothing; binding writes are
receipted and door-checked), and recommends KEEP_ISOLATED.

## FL-G31-02 DISPOSITION + G31-CONTRACT-01 — 2026-11-14

The Director returned SCOPED PASS on FL-G31-02 and
ACCEPTED KEEP_ISOLATED. Architecture ruling: do not unify
executors by forcing identical semantics — instead ONE
authoritative operator vocabulary with explicit EXECUTION
PROFILES (Canonical chain profile: all nine; Correspondence
composition profile: > and >>, seven explicitly refused;
public dispatch routes without silent semantic
substitution). The earlier blanket executor-unification
proposal is SUPERSEDED. G31-CONTRACT-01 prepared per his
next action (SANDBOX_G31_CONTRACT_01_PROPOSAL_2026-11-14.md):
vocabulary on the one FLOW_CONTRACT authority, both
profiles stated (including Profile B's own Assert-label
behavior), dispatch rules D-1..D-5 with the no-silent-
substitution rule, cross-profile safety, and a regression
plan (existing suites named + boundary cases T-1..T-6).
No product-code modification or merge authorized.
Remaining open per the Director: profiles documented in
the runtime contract (future circuit), dispatch-boundary
regression proofs, hidden-flow assessment.

## G31-CONTRACT-01 CONDITIONAL CONFIRM + AMENDMENT — 2026-11-14

The Director returned CONDITIONAL CONFIRM (design
accepted: both profiles, FLOW_CONTRACT authority, refusals
preserved, no automatic switching, T-1..T-6 baseline) with
two required corrections, both now resolved in the amended
proposal: C-1 REFUSAL VISIBILITY — D-6/D-7 added: a Profile
B refusal (recognized operator, flow_executor.py:174) is an
observable act that dispatch must surface, distinct from a
parse miss (malformed; may fall through silently); the
current swallow point is named (repl.py:3480 catches both
classes in one except). C-2 FAILURE-STATE PERSISTENCE —
contract stated (bindings are Core II working state;
generations are minted only by the checkpoint authority,
which chain execution never calls) with behavioral evidence
at pin 1c5129e: committed_generation_state 'absent' before,
after a failed binding chain, and after DeltaFlow; T-5
split into T-5a (save/reload), T-5b (generation census),
T-5c (rollback posture). Amended bounded proposal returned
per his directive; implementation still unauthorized.

## G31-CONTRACT-02 — IMPLEMENTED 2026-11-14 (PR #417, NOT MERGED)

Director bounded implementation directive (MODE=C) executed.
FLOW_PROFILES annotation added beside the unchanged FLOW_CONTRACT
(canonical_chain nine operators; correspondence_composition two,
seven refused, classifications mirrored from
flow_executor.FLOW_CLASSIFICATION and pinned by test). D-6:
flow_executor.FlowRefusal (ValueError subclass) raised at the
parse refusal site; the REPL DCC-IV branch surfaces it and
executes nothing; parse misses still fall through quietly.
New suite form/mandell/g31_contract_test.py (T-1..T-6 incl.
T-5a/b/c, 20 checks), registered in form/regress.py.
Failing-first at base 1c5129e: 12/20 (exactly the new-behavior
legs). After: 20/20. Full local regression 250/251 exit 0 (the
one nonzero, p0r3, prints 80/80 PASS and exits 1 identically on
pristine base — pre-existing harness quirk). Canonical regress
--order rev 286/286 GREEN. Exact-head CI at a20997d ALL GREEN
(build 3.10/3.11, browser-acceptance, smoke). Head:
a20997d55c5d1a3e75510cc1c2c8caed75f9e0ec. Merge NOT authorized;
PR awaits Director review.
