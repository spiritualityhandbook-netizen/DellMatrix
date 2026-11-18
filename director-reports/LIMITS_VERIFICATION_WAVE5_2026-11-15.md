# LIMITS VERIFICATION — WAVE 5 (2026-11-15)

Read-only verification of register items **R22–R26** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 4 (`LIMITS_VERIFICATION_WAVE4_2026-11-15.md`), re-verified first-hand at
**current main `56b6d9cb40cb68d3f50e4c39537769b242cb13a7`** (g31proof_clone
fetched, checked out at that head, verified clean before and after — probe-owner
state `W5PROBE` removed). No code changed; nothing committed. Functional probes
ran for every item (throwaway owner `W5PROBE`; selector probe used the
diagnostics fixture's direct-injection pattern — confirmed proposals in
`nursery.proposals` + matching `plane.units`).

**Numbering:** R22–R26 are taken exactly as Wave 4's queue named them, matching
the census's ranked HINDERS-US register (R22 knowledge selection max 5 · R23
outcome evidence cuts + search cap 100 · R24 translate operand slices · R25
Compare/Threshold shorthand token drop · R26 DuoBeta ledger detail 120).
Census file paths for R22/R23 named `form/dell_matrix/`; both modules live in
`form/mandell/` today. Line numbers are today's throughout.

**Method (wave-4 ruled-semantics separation, binding):** every item separates
**(a) the value hinders** (a realistic workload needs more), **(b) the mechanism
disobeys its ruling / loses silently** (DEFECT), and **(c) FAITHFUL-GUARD** (the
bound implements its ruling, refusal visible, nothing silent — a small value
alone is not a defect). Rulings are cited from the working plan
(`director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md`) and test-pinned contracts;
where no ruling exists, the item says UNRULED plainly.

**Headline of the wave:** the data/evidence family is back, and it is mostly
silent. Four of five items carry a DEFECT finding — all of them silence-shaped
rather than value-shaped: outcome evidence is cut at capture with no marker
(R23), English operands are rewritten before execution (R24), a pinned
shorthand contract answers a different question than the one asked (R25), and
the DuoBeta learning record's text is cut at three separate sites (R26). Only
R22 is a pure value finding — and it is the wave's most honest mechanism: its
cap is disclosed in its own receipt, and explicit choice bypasses it entirely.

---

## R22 — Automatic knowledge selection returns at most 5

- **Census sites:** knowledge_selector.py:117; :334-348.
- **Sites today:** `max_selected: int = 5` — the default parameter of
  `select_for_context` at `form/mandell/knowledge_selector.py:117`;
  enforcement at `:334` (`remaining_slots = max(0, max_selected -
  len(explicit_scored))`), `:335` (automatic candidates sliced to the
  remaining slots), and the assembly at `:346-355`. The one production
  caller, the Dell-37 grow path at `form/mandell/core_i_ops.py:602-604`,
  passes **no** `max_selected` — the default 5 governs production.
  (`knowledge_influence.py:347` also calls with defaults.)
- **The ruling:** none found for this 5. `select_for_context` /
  `max_selected` / "Relevance V2" occur nowhere in the plan. The plan's
  several "top-5" values (e.g. plan :411, :1035, :1988) belong to the
  **Nursery ranking formula** (top-5 per topic) — a different mechanism,
  and one Q-LC.2 classified UNIMPLEMENTED in the Nursery. The two 5s must
  not be conflated: the selector's 5 is **UNRULED**.
- **Probe (functional, injected confirmed knowledge, 56b6d9c):** 8
  confirmed units all matching the context → `eligible_count = 8`,
  `selected = 5`, and the result's own reason string reads *"relevance v2:
  5 of 8 eligible (exact_phrase, ordered, coverage, jaccard; ID
  tie-break)"* — the cap is **disclosed at the selector's own surface**,
  with `eligible_count` carried in the result. With 7 explicit IDs →
  `selected = 7`: explicit choices are placed first and the combined list
  is **never re-sliced**, exactly as the census said — explicit choice
  bypasses the cap by construction.
- **DISPOSITION: CONFIRMED-HINDERS (the value).** The mechanism is honest
  — nothing here is silent at the selector's receipt level, hard laws
  (revision/dependency/eligibility/conflict) all run before the cap, and
  the ASI re-sort never adds or removes candidates. What hinders is the
  unruled default governing the production door: the grow pass that
  consumes the selection (`core_i_ops.py:602`) receives only the top 5
  eligible confirmed units; the remaining eligible units are counted in
  the receipt but do not reach that pass's work. Automatic discovery is
  precisely the path the doctrine calls scope of vision, and no design
  document defends 5 for it (contrast R21's documented caps in wave 4).
  Workload evidence is the constructed probe above (8 eligible → 5
  reach), stated as such; the census's 30-eligible scenario is the same
  shape at field scale.
  *Failing-first sketch:* seed 8+ eligible confirmed units matching one
  context, run the production grow-selection path, and assert every
  eligible unit reaches the consumer (or that the consumer's receipt
  names the unselected eligible IDs, not only their count) — fails today
  at `knowledge_selector.py:335` (only 5 IDs leave the selector).
  Repair shape: raise the default to a practical selection size or have
  the production caller pass all-eligible, keeping explicit-choice
  priority, the hard-law gate order, and the `eligible_count` disclosure
  exactly as they are.

## R23 — Outcome evidence truncated at capture; outcome search capped at 100

- **Census sites:** outcome_ledger.py:83-88; :362-404; search :495.
- **Sites today:** constants at `form/mandell/outcome_ledger.py:83-88`
  (`_MAX_INPUT = 200`, `_MAX_ERROR = 300`, `_MAX_MESSAGE = 200`,
  `_MAX_MESSAGES = 12`, `_MAX_STATE_NOTE = 300`, `_MAX_FLOW_PROGRAM =
  500`), applied through `_bound` at `:91-93` (`s[:limit]` — no marker,
  no flag, no counter) at capture: input `:362`, error `:364`, messages
  `:365` (`messages[:12]`, each `[:200]`), state_note `:366`, flow_program
  `:404`. Search: `find_outcomes` at `:471`, cap at `:495`
  (`n = max(1, min(int(limit), 100))`), return `out[:n]` at `:498` — no
  total-match count, no offset. The sibling `list_outcomes` at `:501`
  clamps from below only (`:507`) and honors any limit.
- **The ruling:** no plan ruling names these values — **UNRULED**. The
  only authority at the site is the in-code design comment at `:82`:
  *"Bounds: records carry bounded evidence, never huge arbitrary
  snapshots."* That comment justifies bounding; it does not mention —
  and cannot authorize — silence about the bounding.
- **Probe (functional, `capture_outcome` + direct record seeding,
  56b6d9c):** a receipt with input 250 / error 400 / state_note 400 /
  15 messages × 250 chars captured as input **200**, error **300**,
  state_note **300**, **12 messages × 200** — and the record carries **no
  truncation marker of any kind** (no `truncated` field or flag exists in
  the record). With 150 records matching a query:
  `find_outcomes(limit=500)` → **100**; `list_outcomes(limit=500)` →
  **150**. The search silently overrides the caller's explicit limit and
  returns no signal that 50 further matches exist.
- **DISPOSITION: DEFECT-CONFIRMED (both halves — silent loss, not the
  values).** The outcome record is the system's only durable evidence of
  what a route did; text cut at capture is unrecoverable, and downstream
  consumers (DuoBeta extraction, outcome search itself) act on the cut
  text as if it were complete — the wave-4 R21 contrast is exact: there,
  every eviction was counted at its site under a documented design; here,
  nothing is counted or marked anywhere. The search half is the same
  family in miniature: an explicit caller parameter (`limit=500`)
  silently shrunk to 100 with no total disclosed, while the sibling
  listing function honors the same request in full — the two doors
  disagree and the stricter one doesn't say so.
  *Failing-first sketch:* (i) capture a receipt whose input is 250 chars
  and assert the stored record either holds it whole or carries a
  truncation marker naming the cut — fails today at
  `outcome_ledger.py:362` (200 stored, no marker); (ii) seed 150 matching
  outcomes, call `find_outcomes(limit=500)`, and assert 150 results or a
  disclosed total — fails today at `:495` (100 returned, no total).
  Repair shape: store fields whole (the ledger's retention is already an
  unbounded exemplar — only its per-field cuts bind), or store a
  `truncated` marker + full-text spill per field; align `find_outcomes`
  with `list_outcomes`' clamp-from-below shape and disclose the total
  match count (or accept an offset), keeping newest-first order.

## R24 — Translate slices operands before execution

- **Census sites:** translate.py:299-720 (drifted).
- **Sites today (all in `form/mandell/translate.py`, all inside Intent
  construction — the cut text is what the Intent carries into
  execution):** find-idea query `[:60]` at `:457`; supersede words
  `[:240]` at `:468`; grow-context `[:80]` at `:509`; add-idea label
  `[:80]` at `:515` and `:519`; set/assign values `[:60]` at `:676` and
  `:685`; predicate/pattern `[:60]` (with quotes stripped) at `:750` and
  `:759`; create-branch name fallback `[:48]` at `:805` and words
  `[:120]` at `:810` (code-read — see probe note); stamp mark `[:48]` at
  `:824`; label `[:120]` at `:878`; query `[:80]` at `:892`. None of
  these sites refuses, names the bound, or marks the cut.
- **The ruling:** no ruling names any of these values — **UNRULED**. The
  governing law is DD-44 EXTENDED (plan §12.63a.2, cited in wave 4):
  wherever a limit is in play for a Dell-involving operation, the number
  is stated, or the operation asks, or it fails with the full why — **no
  silent defaults anywhere in the family**. These slices feed Dell
  operations directly (37[Nurture] supersede/add-idea, 35[Discover]
  find-idea) and rewrite the operand *before* the operation runs.
- **Probe (functional, `translate()`, 56b6d9c):** "add idea " + a
  100-char label → Intent args carry a label of **80**. "supersede idea
  W5K1 with " + 300 chars of words → the Intent's Mandell seed carries
  **240** chars of words — the supersession that executes is over a text
  the user never wrote (and whose store-end contract the Q-S2.3 circuit
  just repaired; the front door re-cuts it). "find idea " + an 80-char
  query → seed query **60** — the search that runs is for a prefix of the
  asked term. All three report success; nothing names a cut. (The
  create-branch phrasing in the probe took a different branch and
  returned label/words whole at Intent level, so `:805`/`:810` are
  classified code-read only; their cuts bind on phrasings that reach
  that branch, and the strong-create door's own caps are R29's item.)
- **DISPOSITION: DEFECT-CONFIRMED.** This is pre-execution rewriting,
  the census's exact charge: validation may refuse loudly, but it may
  not quietly rewrite — here the slice happens before the Intent/seed is
  built, success is reported, and the object created, the text
  superseded, or the term searched is *different from what was
  specified*. It is also the front end of the same operand chain whose
  store end waves 1–3 verified (R13–R16): a chain in which the front
  door cuts at 240/80/60 and the store (pre-repair) cut again is a chain
  with no honest surface at either end.
  *Failing-first sketch:* `translate("supersede idea X with " + 300
  chars)` and assert the resulting Intent's seed carries the full 300
  (or an explicit refusal naming the bound) — fails today at
  `translate.py:468` (240 carried, success reported). Same shape for the
  add-idea label (`:515`) and find-idea query (`:457`). Repair shape:
  remove pre-execution slicing of user operands; where a grammar
  genuinely needs a bound, refuse with the operand and bound named, or
  pass the operand whole and let the owning operation's own contract
  (which, after the SYS-C29 family repairs, refuses explicitly) govern.

## R25 — Compare/Threshold shorthand drops tokens past 2

- **Census sites:** query_ops.py:90 (Dell 57); :176 (Dell 73).
- **Sites today:** Dell 57 at `form/mandell/query_ops.py:77-99` — the
  shorthand rewrite at `:91` builds `eq:` + the first **two** tokens
  (`[:2]`); Dell 73 at `:164-190` — the sibling rewrite at `:177` builds
  `gte:{parts[0]} {parts[1]}`, likewise discarding tokens past the
  second. Both carry the DD-42 infix refusal in front of the rewrite
  (57: `:80-89`; 73: `:172-176`): a second token that is an operator
  refuses `condition_unparseable`.
- **The ruling / the pin:** DD-42 (plan §12.47a, Ace: "Get that fixed",
  2026-11-09) ruled the **infix** degradation: an infix condition must
  REFUSE honestly (or genuinely parse), never degrade to truthiness —
  class: *"silent semantic degradation — the DD-14 family (a receipt
  claiming work that did not happen)."* DD-42's facts never address the
  non-operator extra-token drop. That drop is instead protected by a
  **test pin**: `d1_dell57_compare_test.py:142`
  (`rewrite_drops_tokens_beyond_two`), whose sibling check at `:137` is
  named `bare_form_rewrites_to_eq_of_first_two_tokens` — the rewrite is
  deliberate, pinned contract. A test pin is a contract, not an
  Ace/Director ruling on the question.
- **Probe (functional, `execute_seed`, store N=5 / level=5, 56b6d9c):**
  `57[Compare] :: N 5 dropped` → ok=True, message *"Compare eq:N 5
  matched=True mode=number"* — the asked three-token shorthand was
  evaluated as `eq:N 5`; the word "dropped" vanished. `73[Threshold] ::
  N 5 dropped` → ok=True, *"Threshold gte:N 5 matched=True"* — same
  drop, second door. And the DD-42 half works exactly as ruled:
  `57[Compare] :: level gt 99` → ok=False, *"Compare refused
  (condition_unparseable)"*.
- **DISPOSITION: DEFECT-CONFIRMED — at the contract level; the
  mechanism is faithful to its pin.** The separation matters. The code
  does precisely what its pinned contract says, and it obeys DD-42's
  letter on infix forms. The defect lives in the contract itself: a
  success receipt (`ok=True`, a `matched` verdict) is issued for a
  *different question than the one asked* — `N 5 dropped` is not
  `eq:N 5`, and on the Threshold door a boundary decision is taken on
  the rewritten question. One mitigation is real and recorded: the
  receipt message prints the rewritten expression (`Compare eq:N 5`),
  so the rewrite is visible to anyone reading the full message — but
  nothing flags that a token was dropped, and the verdict attaches to
  the two-token question without qualification. That is DD-42's own
  named class — a receipt presenting a comparison verdict for work that
  did not happen as asked — surviving in the one shape DD-42's fix
  didn't reach, guarded by a pin. **Who can re-pin it:** an Ace/Director
  ruling changing the shorthand contract (refuse over-length
  non-operator shorthands, as DD-42 refuses infix ones; or genuinely
  evaluate all tokens). Only on that ruling does Uni re-pin
  `d1_dell57_compare_test` and the Dell-73 sibling; until then the code
  must keep passing its pin, and this wave recommends no unilateral
  change.
  *Failing-first sketch (conditional on the re-pin ruling):*
  `57[Compare] :: N 5 dropped` and assert an honest
  `condition_unparseable` refusal (or a verdict on the full shorthand) —
  fails today at `query_ops.py:91` (ok=True, `matched` on `eq:N 5`).

## R26 — DuoBeta ledger detail cut to 120 (three enforcements)

- **Census sites:** duobeta/growth.py:59; duobeta_learn.py:134;
  persist.py:341.
- **Sites today:** `form/duobeta/growth.py:59` —
  `GrowthEntry(..., detail=detail[:120], ...)` inside `DuoBeta.evolve`;
  `form/mandell/duobeta_learn.py:134` — `detail=str(detail)[:120]`
  inside `_append_learn_entry` (the structured learning ledger's append
  path); `form/persist.py:345` — `"detail": str(e.detail)[:120]` in
  `serialize()`'s `duo_ledger` section. No marker, flag, or counter at
  any site. Entry *count* is unlimited at all three — only the text is
  cut.
- **The ruling:** none found — `120` for DuoBeta detail occurs nowhere
  in the plan or the decision register. **UNRULED**.
- **Probe (functional, 56b6d9c):** `duo.evolve("d" × 200)` → stored
  entry detail **120**. `_append_learn_entry(p, "L" × 200, …)` → stored
  entry detail **120**. The persist expression applied to an entry
  holding 200 chars serializes **120** — the third cut binds any entry
  that reaches `serialize()` whole.
- **DISPOSITION: DEFECT-CONFIRMED.** The DuoBeta ledger is the durable
  growth/learning record; its per-entry detail is permanently cut past
  120 chars with no marker, at capture, twice independently — the
  R13–R16 store-cut family living in the learning ledger. The persist
  site deserves its own sentence: today it is redundant (construction
  already cut every entry), but it is a *guaranteeing* redundancy — a
  repair that lifted only the two construction cuts would be silently
  re-imposed at save, so any fix must lift all three sites together or
  prove the third dead. (This is the §15 failure-class shape: fix the
  mechanism — one bound, owned once — not the first symptom found.)
  *Failing-first sketch:* `duo.evolve` with a 200-char detail and
  assert the ledger entry — and its serialized form after a save/load
  round-trip — holds the full 200 — fails today at `growth.py:59`
  (120 stored; and at `persist.py:345` even for a whole entry).
  Repair shape: store detail whole at all three sites; if a bound is
  ever ruled for this record, it lands as one named constant with a
  truncation marker, applied at one site.

---

## Wave summary

| Item | Site today (main 56b6d9c) | Disposition | One-line basis |
|---|---|---|---|
| R22 — Knowledge selection max 5 | knowledge_selector.py:117 (default), :334-335; production caller core_i_ops.py:602 passes no override | **CONFIRMED-HINDERS** (value) | Probe: 8 eligible → 5 selected reach the grow pass; mechanism honest (receipt discloses "5 of 8 eligible", `eligible_count` returned, 7 explicit IDs → 7 selected, never re-sliced) — but the value 5 is UNRULED for this selector (the plan's top-5s are the Nursery ranking formula, a different and unimplemented design) and no document defends it |
| R23 — Outcome evidence cuts + search cap 100 | outcome_ledger.py:83-88, :91-93, :362/:364/:365/:366/:404; search :495 vs list :507 | **DEFECT-CONFIRMED** | Probe: input 250→200, error 400→300, 15×250 messages → 12×200, with NO truncation marker anywhere in the record; find_outcomes(limit=500) → 100 of 150 with no total disclosed while list_outcomes(limit=500) → 150; values UNRULED, the in-code "bounded evidence" comment (:82) justifies bounding, never silence |
| R24 — Translate operand slices | translate.py:457 (query 60), :468 (words 240), :509 (context 80), :515/:519 (label 80), :676/:685 (values 60), :750/:759 (60), :805/:810 (48/120, code-read), :824 (mark 48), :878 (label 120), :892 (query 80) | **DEFECT-CONFIRMED** | Probes: add-idea label 100→80, supersede words 300→240, find-idea query 80→60 — all silent pre-execution rewrites inside Intent construction, success reported, a different object/text/term than specified is what executes; UNRULED values, against DD-44 EXTENDED §12.63a.2's no-silent-defaults law for Dell-involving operations |
| R25 — Shorthand token drop past 2 | query_ops.py:91 (Dell 57 `[:2]`), :177 (Dell 73); pin d1_dell57_compare_test.py:142 | **DEFECT-CONFIRMED (contract level)** — mechanism faithful to its pin | Probe: `57 :: N 5 dropped` → ok=True, verdict on `eq:N 5`; `73 :: N 5 dropped` → ok=True on `gte:N 5`; the DD-42 infix half refuses exactly as ruled (`level gt 99` → condition_unparseable). The evaluated question differs from the asked one under a success verdict — DD-42's (§12.47a) named class — protected by a test pin; re-pin requires an Ace/Director ruling on the shorthand contract |
| R26 — DuoBeta detail 120 ×3 | duobeta/growth.py:59; mandell/duobeta_learn.py:134; persist.py:345 | **DEFECT-CONFIRMED** | Probes: evolve detail 200→120 and learn-entry detail 200→120 at the two construction sites, no marker; the persist serialize cut (:345) is redundant today but guarantees the loss for any whole entry — a repair lifting only construction would be re-imposed at save; value UNRULED |

**Queued for wave 6 (next five in register order):**
R27 — REPL door clamps silently shrink explicit requests (repl.py:2270 `ce develop` ≤20; :2310 + open.py:964 `evolve loop` ≤150; repl.py:4413 `grow` ≤5; :2113 `ledger` ≤200; :2207 `history` ≤48 — census sites, drifted) ·
R28 — Forces/grow side-effect slices skip ideas past 8/3/12/3 (open.py:890/:903/:1322/:1330 at census) ·
R29 — Idea-create field caps at the strong-create door (idea_create.py:44-47 at census: label 80, detail 2,000, goals 12, words 500, strength scored on the truncated detail) ·
R30 — Checkpoint retention: current + previous only (checkpoint_generation.py:289-295 at census) ·
R31 — Coordinator audit evicts at 500 with no dropped counter (agent_coordinator.py:113/:606 at census).
*Wave-6 note:* R27 and R28 are the doctrine's inverse pattern — the
engine beneath is elastic and the door/side-effect is not — so probes
should run through the actual REPL door and the actual force/grow
activations, not the uncapped Program paths beneath them. R29 is the
store end of the operand chain R24 verified at the front end; the two
reports should be read together before any repair circuit is scoped.
R31's family contrast is already measured: every sibling writer
(exchange, design_loop, director_records, dock_session, auto_growth)
counts its drops — wave 6 should verify the coordinator site is still
the family's only uncounted eviction.
