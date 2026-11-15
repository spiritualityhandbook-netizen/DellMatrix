# C5 GROUNDING — Ranking / Search (failing-first)

Date: 2026-11-15 · Grounded at main **04abc1ea9c1296e0605ed18b303eb9b6babfb799**
(the PR #422 merge; clone g31proof_clone, origin/main fetched 2026-11-15).
Method: plan text read first-hand; every code claim traced first-hand at
this head; one rerunnable failing-first probe (runtime evidence,
INTEGRATION level — the probe drives `Program.ranked_proposals()`, the
exact function the REPL `rank` command and the Dell 46 leaf render).
Nothing committed; no product code changed.

Companion probe: `C5_GROUNDING_PROBE_2026-11-15.py` (same directory).

---

## 1. THE PLAN-STATED C5 CONTRACT (the plan is the authority)

Source: `director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md` — the C5
circuit card (§14-era card set, "C5 NURSERY DOOR, RANKING &
DISCOVERY"), its §13.1 twin, SS12.35/35a/35b (the Dell 46 tour), and
MWL rows 140–143 + 177 (`master_work_list_items.json`).

**Slices** (card, verbatim): "C5.Formula (confirmed ranking formula);
C5.PlaneRank (switchable Plane ranking); C5.Search (DD-25 Discover +
DD-49 Resolve as two faces of ONE search machinery); C5.Door (DD-27
door policy)."

**C5.Formula acceptance** (card, verbatim): "formula is exactly
S = 0.40 LINK + 0.25 ACE + 0.20 FRESH + 0.15 NOVEL; inputs,
normalization, missing data, ties, and revisions defined; Ace's FRESH
half-life choice (Q-N3) stays EXPLICIT and open (SS14.8); top five per
topic; global pending cap 200; tombstoned evictions; NO cap
transferred to the idea field; the score that decided the order is
displayed."

**Corpus and consumers.** Two fields (SS12.35a, Ace 2026-11-09): the
Nursery proposal field under the confirmed formula, and the Plane idea
field. SS12.35: "The formula circuit … is what replaces the recipe;
Dell 46 is its natural display face." The Rank face today is the REPL
`rank` command and Dell 46[Rank].

**C5.PlaneRank** (SS12.35b, Ace ruling 2026-11-09): the Plane measure
is an owner-selected, SWITCHABLE view control — "resonance /
relatedness, growth, Ace attention, and the formula adapted for
confirmed ideas are all available orderings for the Plane field. The
active measure is named on the Rank receipt." The Nursery field stays
under the fixed confirmed formula unless Ace separately directs a
switchable view there. MWL 141 (C5.PlaneRank): OPEN.

**C5.Search acceptance** (card, verbatim): "Search/browse reaches
every authorized item through stable ordered pages, reports
totals/coverage and honest unavailable sections, handles identical
labels by stable IDs, and never treats a 16-ID retrieval round as a
field-size cap; search results never become authority." Dependencies
(card): "existing Nursery, G-11 retrieval, C2's settled relatedness
(for that ranking mode), C7 measurements, C4 references, C11
contained parts/rooms as those types become available." MWL 142
(DD-25/DD-49/C5.Search): OPEN.

**C5.Door** (card): "auto-passage stays OFF until Ace supplies
standards and scope; future receipts name policy version and
authorizing rule; revocation takes effect before application; Cycle
never approves its own proposals." MWL 143: OPEN. (§13.2.6 records
that the Cycle AUTO-CONFIRM law and DD-27 agree: OFF — no conflict
to discover.)

**FRESH / Q-N3.** Two plan statements coexist and the build must not
conflate them: (a) the card and §13.6/§14.7 keep "Q-N3 FRESH
half-life (all corpora vs per-corpus)" OPEN as Ace's choice; (b) MWL
177 records Ace's 2026-11-10 RULING on aging: "proposals age at
3/7/14-day marks and fade at 30 days ONLY while new proposals are
arriving (a quiet field never expires); implementation rides the C5
ranking circuit" — status OPEN (ruled, unimplemented). MWL 140
(C5.Formula) status: PARTIAL, titled "…(machinery exists; FRESH aging
RESOLVED by Ace 2026-11-10…)" — the "machinery exists" half of that
title is the old recipe (§2); the formula itself is not implemented.

**Stop conditions** (card): "hidden truncation, fabricated full
coverage, rank-derived permission, invented replacement scores for
missing signals." Plus §13.2.2: "The ranking formula exists in three
statements (2026-11-08 confirmation; SS12.35's old live recipe;
SS12.35a/b scope + switchability). C5 is the single implementation
reading."

**Sequencing.** §13.5: "C13 Simulate -> C5 ranking -> C4 zipper";
§14.4: "-> C5 ranking/search and C4 reference slices ->". C13 closed
(PR #413); C5 is the named next circuit. §14.4 selection rule and the
false-dependency cut both matter for scoping: "search can browse
stable IDs before semantic ranking" — browse does not wait for the
formula.

---

## 2. WHAT EXISTS TODAY (traced first-hand at 04abc1ea)

### 2.1 The Nursery ranking that actually runs — EXISTS-PARTIAL (old recipe)

`Program.ranked_proposals()` — `form/open.py:1485`. Corpus:
`list_proposals()` = `nursery.pending()` (open.py:1370; nursery.py:232)
— PENDING proposals only, insertion order. Ordering: the Inspire
preference model's order first (stable), tie-broken by blended →
harmony → graph_coherence. The preference model
(`form/dell_matrix/inspire_pack.py:378`): `blended = 0.65*affinity +
0.35*tanh(pref_score)`, pref_score from token weights learned from
past confirms/rejects. Fallback on exception: affinity → harmony →
graph_coherence sort.

Consumers (all render this one ordering): REPL `rank` / `rank
proposals` (form/repl.py:1287 — prints top 12 as
`aff=<affinity:.3f> [kind] id — label`); Dell 46[Rank] leaf
(form/mandell/executor_leaf.py:559); the visual
(`Program.visual()` → write_visual, open.py:2091); the session
snapshot's top-12 nursery_ghost entries (open.py:550).

This is exactly SS12.35's "old recipe," verified live there on
2026-11-09 and re-verified today (§4): fresh proposals carry
affinity 0 until a RingedGrowth pass stamps scores, so Rank renders
arrival order; the displayed `aff=` is affinity even when the
preference blend decided the order (wrinkle 2 — the registry's own
Dell 46 card, form/mandell/dell_cards.py:709, still documents the old
contract: "affinity-descending (equal affinities keep insertion
order)").

### 2.2 The confirmed formula — ABSENT

`S = 0.40 LINK + 0.25 ACE + 0.20 FRESH + 0.15 NOVEL` appears nowhere
in `form/` (grep for the weight tuple and the signal names: no
implementation; the 0.40 constants found belong to ringed_growth's
affinity recipe, verita, and idea_create — different formulas).
Component-by-component:

- **LINK** — no signal computed. Raw material exists: `Proposal.parents`
  (nursery.py:94) and `graph_coherence` (a pair score, stamped by
  RingedGrowth; 0.0 = no graph evidence).
- **ACE** — no Ace-attention signal on proposals exists anywhere.
- **FRESH** — the input data EXISTS and is never read by ranking:
  `Proposal.created` timestamp (nursery.py:96, `default_factory=_ts`).
  No aging, no fade, no half-life in any ranking path.
- **NOVEL** — no novelty signal exists.
- **Top five per topic** — ABSENT. Proposals have `kind`, no topic
  field; no per-topic grouping exists (grep "topic" in nursery.py:
  none).
- **Pending cap 200 + tombstoned evictions** — ABSENT. No cap, no
  eviction, no tombstone in nursery.py or open.py (grep evict/
  tombstone: none). Probe §4: 205 adds → 205 pending. (Nursery is
  elastic by accident, per the limits census — the confirmed design
  cap was never built; Q-LC.2 classified the design caps
  UNIMPLEMENTED, consistent with this trace.)
- **Deciding score displayed** — ABSENT for the formula (no S exists);
  the current display shows affinity, which is not always the
  deciding number (SS12.35 wrinkle 2).

### 2.3 Plane ranking — ABSENT (one stub-adjacent surface)

`ranked_proposals()` never includes Plane units (corpus is
nursery.pending() by construction). The only cross-field ranking
surface is `Program.attend(query, top_k=5)` (open.py:2015; REPL
`attend <q>`, repl.py:1998): cosine bag-of-embeddings over
nodes_payload + proposals, whose own docstring reads "Soft attention
over live ideas + nursery (LLM-from-scratch pedagogy)… educational
stub, not a real LLM." No measure switching (resonance/growth/
attention/formula), no receipt naming an active measure, top_k=5
default with no paging or totals. It is a pedagogy surface, not the
C5.PlaneRank authority, and the build must not quietly promote it.

### 2.4 Search / browse / retrieval — EXISTS-PARTIAL, fragmented

- **Dell 35 Discover** (form/mandell/core_i_ops.py:86; REPL `discover`
  routed via semantic_router): inventory snapshots only —
  count_nursery, list_pending (first 10, insertion order),
  compare_nursery. NOT DD-25 Discover All: no paging, no search by
  name/title/idea/proposal, no whole/part/piece reach, no
  totals/coverage reporting beyond counts.
- **DD-49 Resolve** — no search-machinery face exists; the `resolve_*`
  functions in form/ are ID/reference resolvers (lifecycle, lineage,
  identity), not a browse/search face over the field.
- **G-11 retrieval machinery** (the card's named dependency):
  `AgentCoordinator.snapshot_for` / `retrieve_for`
  (form/dell_matrix/agent_coordinator.py:784, :817) — dock-facing,
  fail-closed, honest about bounds: snapshot slices at
  _MAX_SNAPSHOT_IDEAS=200 / _MAX_SNAPSHOT_UNITS=200 (:110-111,
  first-come slices — the limits-census R3 CONFIRMED-HINDERS item),
  retrieve_for hard-errors past _MAX_RETRIEVE_IDS=16 distinct IDs
  with NO partial result (:112) — precisely the "16-ID retrieval
  round" the C5.Search acceptance says must never be treated as a
  field-size cap. This machinery is an authority for dock snapshots,
  not a user search surface; C5.Search rides it, it does not
  replace it.
- **No REPL `search` command exists** (grep: none). The user-facing
  search/browse surface the card promises does not exist in any form.

### 2.5 knowledge_selector — EXISTS-AUTHORITATIVE, different job (not C5's)

`form/mandell/knowledge_selector.py:111 select_for_context(...,
max_selected=5)` — Relevance V2: selects CONFIRMED, on-plane,
revision-active, dependency-valid knowledge for a chain-execution
context, scored (exact_phrase, ordered, coverage, jaccard) with all
components exposed; hard eligibility laws run before scoring.
Consumers: core_i_ops (Dell execution), knowledge_influence,
runtime_observe. Census R22's `max_selected=5` is this execution
window.

**Overlap analysis (the second-selector question).** Three different
jobs, three different corpora — no two are the same authority:
(1) ranked_proposals orders PENDING proposals for human review
(display/decision support; advisory — rank never confirms anything);
(2) select_for_context picks CONFIRMED knowledge to feed an execution
(eligibility-gated; its output influences behavior, under the
STORED>ELIGIBLE>SELECTED>USED ladder);
(3) C5.Search is browse/retrieval for the human (results "never
become authority"). The collision risk is real but narrow: if
C5.Formula's LINK signal were computed by reusing select_for_context's
relevance scores, or if Rank's order were ever consumed as an
eligibility input, the authorities would fuse. The build must keep
them separate (§3) — C5 adds the missing ranking authority for fields
(1)/(3); it does not create a second execution selector, and
knowledge_selector is not extended into a ranking surface.

### 2.6 Test coverage today

No dedicated rank/inspire suite exists in form/ and none is
registered in form/regress.py. Nearest coverage: the P3 R3.5/R3.6
proofs (form/mandell/p3_r35_integration_proof.py,
p3_r36_graph_harmony_proof.py) pinning the harmony/graph tie-break
consumption — behavior the formula circuit must preserve as
tie-breaks or supersede explicitly, never silently.

---

## 3. THE GAP AS A BOUNDED CIRCUIT (smallest C5 that satisfies the card)

**Verdict: the C5 contract is NOT satisfied today.** The Nursery
field runs the superseded pre-2026-11-08 recipe; the formula, its
caps, its display, the Plane field, and the search face are all
absent. MWL 140's PARTIAL is generous: what exists is the machinery
the formula replaces.

**Proposed circuit: C5.Formula (the formula leg — §13.5 step 5,
"C5 formula leg (Q-N3 answered in its contract)").** PlaneRank and
Search are separate later slices (their dependencies — C2's settled
relatedness for the resonance mode — are not all in place; the
§14.4 false-dependency cut lets Search's browse face proceed
independently when scheduled).

Scope of the formula leg:
1. **One ranking authority.** A single formula implementation living
   with the Nursery field's owner — extend `Program.ranked_proposals`
   (form/open.py) to compute S per pending proposal and order by it,
   with the existing preference/harmony/graph_coherence order
   preserved ONLY as the defined tie-break chain (or explicitly
   retired by the packet — Q-C5.4). No new module-level selector;
   knowledge_selector untouched.
2. **Signal definitions** (inputs/normalization/missing-data are the
   circuit's to define, per the card): LINK from parents/graph
   evidence; ACE from a named Ace-attention source or an explicit
   missing-data rule; FRESH from `Proposal.created` under Ace's
   2026-11-10 staged aging (3/7/14 marks, 30-day fade only under
   inflow — MWL 177), with the Q-N3 half-life question carried
   explicitly (Q-C5.1); NOVEL from a defined field-distance rule or
   an explicit missing-data rule. **Missing signals are never
   invented** (card stop condition): a missing component is reported
   as missing on the receipt, with the defined default applied.
3. **Governance**: top five per topic (requires defining "topic" —
   Q-C5.2); global pending cap 200 with tombstoned evictions
   (eviction is a Nursery lifecycle act: the evicted proposal leaves
   a tombstone record, never a silent disappearance — and per
   Q-LC.2 this is a risk-bearing stateful change needing the
   pre-plan risk check); NO cap on the Plane/idea field.
4. **Display honesty**: the Rank face (REPL `rank`, Dell 46) shows S
   and its four components per line — the score that decided is the
   score displayed (closes SS12.35 wrinkle 2); the Dell 46 registry
   card (dell_cards.py:709) is updated to the new contract in the
   same circuit.
5. **Suite**: new registered suite (failing-first = §4's probe,
   hardened) pinning formula order under controlled signals,
   tie-breaks, missing-signal honesty, cap+tombstone behavior,
   top-5-per-topic, legacy nursery files loading unchanged
   (additive fields only, the Proposal(**record) pattern), and the
   display contract. Mutants: weight permutation, FRESH inversion,
   cap removal — each must kill the suite.
6. **Files**: form/open.py (ranked_proposals), form/dell_matrix/
   nursery.py (cap/tombstone + any additive Proposal fields),
   form/repl.py + form/mandell/executor_leaf.py (display, if the
   rendering changes there), form/mandell/dell_cards.py (46 card),
   new suite + form/regress.py registration, circuit packet.
   NOT touched: knowledge_selector.py, agent_coordinator.py,
   inspire_pack.py (its blended value survives only as a tie-break
   input if Q-C5.4 so decides).

**What FRESH adds later (C5.Formula's own second half / MWL 177):**
the aging lifecycle on top of the formula — staged 3/7/14-day marks
changing the FRESH component, and the 30-day fade under inflow
(fade = score effect or eviction pressure is Q-C5.3's to settle
against the tombstone mechanism). The formula leg defines FRESH's
input; the aging leg animates it over time. Neither exists today.

---

## 4. FAILING-FIRST PROBE (runtime, current main)

Probe: `C5_GROUNDING_PROBE_2026-11-15.py` — seeds three pending
proposals whose LINK and FRESH differ maximally (oldest + 0 parents
added FIRST; newest + 3 parents added last), renders
`ranked_proposals()` in the REPL's exact format, then exercises the
cap and per-topic promises with 205 bulk proposals. Isolation: fresh
probe owner, Nursery repointed to a temp file before any add; the
clone's git status stayed clean and no probe state was written under
form/state/.

Captured output (2026-11-15, head 04abc1ea, exit code 1):

```
Scenario A — REPL `rank` rendering of ranked_proposals() (form/repl.py format):
  1. aff=0.000 [new] oldest_unlinked_9037 — oldest unlinked
  2. aff=0.000 [new] middle_one_parent_1320 — middle one-parent
  3. aff=0.000 [new] newest_three_parent_2041 — newest three-parent
  [FAIL] A1 formula order (newest+linked outranks oldest+unlinked): order=['oldest unlinked', 'middle one-parent', 'newest three-parent']
  [FAIL] A2 deciding score displayed (S + LINK/ACE/FRESH/NOVEL on the row): row score keys present: ['affinity', 'blended', 'graph_coherence', 'harmony', 'pref_score']; formula keys: NONE
  [FAIL] B1 pending cap 200 with tombstoned evictions: pending after 205 adds = 205 (cap would keep <= 200)
  [FAIL] B2 top five per topic: ranked_proposals returned 205 rows; topic field on rows: False

PROBE VERDICT: PLAN CONTRACT NOT SATISFIED — 4/4 checks failed: A1 formula order (newest+linked outranks oldest+unlinked), A2 deciding score displayed (S + LINK/ACE/FRESH/NOVEL on the row), B1 pending cap 200 with tombstoned evictions, B2 top five per topic
```

Reading: A1 reproduces SS12.35 wrinkle (1) at today's head — with no
RingedGrowth pass, Rank is arrival order wearing a ranking's clothes,
and it inverts the formula's most robust implication. A2 shows the
rows carry only the old recipe's numbers (affinity / blended /
pref_score / harmony / graph_coherence) — no S, no components, and
the REPL displays `affinity`, which is not the deciding key when the
preference blend separates them. B1/B2 show the governance half of
the contract (cap, tombstones, per-topic top-5) has no machinery at
all. The Plane-field absence (§2.3) is proven by corpus construction
(open.py:1370 + 1485), not by this probe.

---

## 5. ANTICIPATED DIRECTOR PROBES

1. "Is ranked_proposals' preference order a feature to preserve or
   the defect itself?" — SS12.35 + §13.2.2 settle it: the formula
   replaces the recipe; the open part is only whether the old order
   survives as tie-break (Q-C5.4).
2. "Your probe's LINK/FRESH mapping is invented." — Declared as
   such in the probe header; A1 is normalization-free (any monotone
   LINK/FRESH reading inverts today's order). The circuit defines
   the real normalizations; the probe only falsifies the current
   state.
3. "Does the cap endanger confirmed ideas?" — No: the cap is
   pending-only, Nursery-only; the card forbids transferring it to
   the idea field, and tombstones preserve the evicted record.
4. "Is attend() the PlaneRank seed?" — Its own docstring says
   educational stub; promoting it silently would violate the
   display-honesty and no-invented-scores stops. It is evidence of
   absence, not a foundation.
5. "Why doesn't FRESH ride along free, since `created` exists?" —
   A stored timestamp is not an aging policy: staged marks, the
   inflow condition, and fade semantics are Ace-ruled behavior
   (MWL 177) that no code implements; §3 scopes it as the formula
   circuit's own second half, not a freebie.
6. "Rank-derived permission?" — Rank stays advisory display; the
   circuit adds no path from S to confirmation eligibility
   (knowledge_selector's hard laws remain the only selection gate
   for execution).

## 6. QUESTIONS FOR THE BUILD CIRCUIT (Q-C5.x)

- **Q-C5.1 (Ace, via Director):** Q-N3's residue — is FRESH the
  staged 3/7/14-day aging of MWL 177 as a step function, or a
  continuous half-life (and if so, what half-life, all corpora or
  per-corpus)? The card keeps the half-life choice explicit and
  open; MWL 177 rules the marks. The circuit needs one reading.
- **Q-C5.2:** What is a proposal's "topic" for top-5-per-topic —
  `kind`, a parent/root lineage, a goal tag, or a new field? No
  topic data exists on Proposal today.
- **Q-C5.3:** At the 200 cap, is eviction by lowest S, by age
  (FRESH fade), or oldest-first — and does the 30-day fade evict,
  or only demote? (Interacts with the tombstone design and the
  Q-LC.2 risk inventory.)
- **Q-C5.4:** Does the Inspire preference order survive as the
  formula's tie-break chain (with harmony/graph_coherence), or is
  it retired outright? Either way the packet must say so; silent
  retention would leave two ranking authorities in one function.
- **Q-C5.5:** ACE signal source — what observable counts as Ace
  attention (explicit Ace marks on proposals? confirm/reject
  history? a per-proposal field Ace sets)? If none is defined, is
  the missing-data rule ACE=0 with the component reported missing?
- **Q-C5.6:** NOVEL definition — distance from the existing field
  (token/graph novelty vs pending+confirmed), or a producer-stamped
  field? Must not be invented per-proposal at rank time.
- **Q-C5.7:** Does the formula leg include the Rank display change
  (S + components per line, registry card update) in the same PR,
  or land scoring first behind the old display? (Display honesty is
  a card acceptance item; splitting it leaves wrinkle (2) open.)
- **Q-C5.8 (sequencing):** Do PlaneRank and Search wait for C2's
  settled relatedness (the card lists it as a dependency "for that
  ranking mode" only), with the §14.4 browse-first cut taken for
  Search — or does the Director want the formula leg alone closed
  and certified before either is grounded?

---

*Evidence classes: plan text and code traces are FACT (first-hand at
04abc1ea); the probe is runtime INTEGRATION evidence; §3's circuit
shape is a PROPOSAL for Director disposition, not an authorization.*
