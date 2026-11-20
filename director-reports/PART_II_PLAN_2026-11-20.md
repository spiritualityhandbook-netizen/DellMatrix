# PART II — THE DELL PLAN: DETAILED PLAN (2026-11-20)

**Program:** DellMatrix Eight-Part Program (Ace ruling 2026-11-20;
AGENTS.md §46) · **Part:** II — The Dell Plan: the 99 Dells ·
**Branch:** `uni/part-2-dell-plan` · **Base:** main
`af2519b6d239ef278397e277210d6da2467c36e5` ·
**Stage:** PLAN (plan → confirm → code → confirm). This PR carries
the full detailed plan, every failing-first artifact the Part
package names (all measured at base), and the complete
credit-evidence packages. No production code is changed by this
PR; no register JSON is edited — every flip below is PROPOSED and
executes only on confirm, inside this Part's PR at code stage.

**Scope:** 41 register rows (11, 12, 13, 24, 28, 29, 30, 31, 35,
36, 37, 38, 39, 41, 43, 45, 95, 96, 113, 114, 137, 138, 139, 140,
141, 142, 143, 149, 150, 151, 156, 157, 158, 159, 160, 161, 162,
163, 177, 178, 179) and 11 Edition 1 circuits (GP-E01, E02, E03,
E04, E07, E08, E09, E10, E11, E12, E20). Anchors: the PR #308
oracle modernization (row #24) and the backlog credit settlements
#401 / #416 / #429 / #439 / #457 (evidence packages in
`PART_II_CREDIT_EVIDENCE_2026-11-20.md`, same PR).

**Collision protocol (map §Execution model):** this Part owns
`form/open.py` parse / translate / condition / count regions,
`form/repl.py` (primary), `form/dell_matrix/core.py` contract
definitions, and the C5 door/ranking surface of the Nursery
modules. Part I owns the rest of `form/open.py`, confirm
*placement* (`confirm_lineage.py`), and history/save machinery.
Any change this Part needs in a Part I region is filed as a patch
note in this PR for Part I to apply — never a direct edit. The
register JSON is edited only for this Part's own rows, at landing,
against the then-current main (surgical per-row edits, indent=1,
`ensure_ascii=False`, re-render + `--check` byte-identical).

---

## 1. Failing-first artifacts delivered IN THIS PR (measured at base)

Every suite below was written from the governing contract
(Edition 1 spec / register row), then RUN at base main `af2519b6`
on 2026-11-20. The failing checks are the code stage's work list;
the passing pins are the regression fence the repair must not
break. Full failure output is in each suite's docstring.

| Suite | Contract | Tally at base |
|---|---|---|
| `form/r24_operand_integrity_test_spec.py` | GP-E01 operand byte-integrity | **3/11** — 100→80 label, 300→240 supersede, 80→60 find, 120→80 grow-context, 100→60 replace, 100→60 patch, 80→48 stamp, multibyte 100→80 all FAIL; 3 short-operand pins PASS |
| `form/r23_outcome_evidence_test_spec.py` | GP-E02 evidence completeness + search | **2/9** — input 250→200, error 400→300, message 250→200, 15→12 messages, note 400→300, flow 600→500, search 150→100 all FAIL; 2 pins PASS |
| `form/c4_zipper_inject_distill_test_spec.py` | Rows #137/#138/#139 | **6/10** — source link, Expand retrieval, Inject duplicate, Distill provenance FAIL; existence pins + cleanup PASS |
| `form/c9_translate_honesty_test_spec.py` | Rows #156/#157 | **2/4** — invented Show seed + cut query FAIL; routing + LM-4 receipt pins PASS |
| `form/c10_harmonic_stamps_test_spec.py` | Row #158 | **2/4** — item attachment + stable order FAIL; execution pin + cleanup PASS |
| `form/c7_measure_family_test_spec.py` | Rows #149/#150/#151, GP-E12 | **5/8** — Measure timestamp, provenance/method, TokenCount basis FAIL; cardinality + Profile pins PASS |
| `form/c11_shelf_manifest_move_test_spec.py` | Rows #160/#162/#163 | **2/6** — Manifest duplicate, Manifest state, Macro read-back, Move dispatch FAIL; pins + cleanup PASS |

Code-stage exit condition for every suite: **all checks PASS at
the Part's exact head**, with no pin weakened. A check may be
re-specified only by an authority ruling that changes the
contract itself, recorded in this PR.

**Naming / registration discipline (failure class proven on
PR #503, smoke run 44758805458):** `form/regress.py`'s
`intended_entries()` = its LIST + every discovered
`form/**/*_test.py`; an unregistered `*_test.py` file fails CI
smoke in seconds as OMITTED INTENDED ENTRY. These seven
artifacts are therefore shipped as `*_test_spec.py` — they are
plan-stage failing-first specifications, runnable directly by
path (as measured above), and they are NOT yet campaign
suites. **Code-stage step zero, per suite, in the same commit
as the implementation that makes it pass:** rename
`<name>_test_spec.py` → `<name>_test.py` AND register it in
`form/regress.py`'s LIST. A spec is never renamed early
(a red suite in the campaign would block every Part), and
never registered under its spec name.

---

## 2. Circuit plans

### GP-E01 — R24: English translation must not rewrite operands (BUILD)

- **Contract (Edition 1, first priority):** every admitted raw
  user operand preserved byte-for-byte through Intent and typed
  Seed; invalid operands reject explicitly with original length
  and bound, executing nothing; no silent prefix, identity change,
  lost quoted text, or hash change; canonical-seed and English
  routes have equivalent admitted effects. FI-012 target: elastic
  preservation where safe; interim exact-size refusals lawful
  only when explicitly disclosed.
- **Current state:** DEFECT LIVE at base. Pre-cut census in
  `form/mandell/translate.py`: supersede words [:240] (:491),
  find-idea query [:60] (:480), grow-context [:80] (:532),
  add-idea label [:80] (:538/:542), replace value [:60] (:712),
  patch value [:60] (:721), predicate [:60] (:786), pattern
  [:60] (:795), stamp mark [:48] (:883), create name [:48] /
  words [:120] (:848/:853), unknown query [:80] (:975). The
  SYS-C29 family repairs (#429/#437/#446) closed the *Nursery
  store* cuts; the *translate-door* cuts above were never in
  their scope and remain.
- **Build:** remove every pre-cut in the translate door; each
  site either carries the operand whole (elastic path) or
  returns an explicit refusal Intent disclosing original length
  + bound, with no execution. Then prove downstream parity:
  the resulting object/search carries the same bytes (spec:
  assert exact at Intent AND through the authorized resulting
  object). Multibyte, delimiters, quoted operands, save/load and
  supersession acceptance hash are in the suite's code-stage
  extension list.
- **Suite:** `form/r24_operand_integrity_test_spec.py` (3/11 at base,
  delivered in this PR) + existing `translate_intent_args_test`,
  `translate_word_counts_test`, `translate_dead_args_test` must
  stay green (their pins encode the count-door contract).
- **Register:** feeds row #24 (with GP-E08) and row #29.
- **Gate:** none outstanding — spec ACCEPTED, defect reproduced.
  Build-ready on PLAN-CONFIRM.

### GP-E02 — R23: outcome evidence completeness + reachable search (BUILD)

- **Contract:** capture executed-action evidence without silently
  losing field text or message counts; full bounded admitted
  evidence, or explicit rejection BEFORE append; no fictional
  summaries; long evidence stored separately only if digest-bound
  to the owner transaction with crash-safe recovery; search
  returns all matches or a truthful page (total + cursor).
- **Current state:** DEFECT LIVE at base.
  `form/mandell/outcome_ledger.py`: `_bound()` silently truncates
  input (200), error (300), message (200), messages (12),
  state_note (300), flow_program (500) (:83-88, :362-404);
  `find_outcomes()` clamps any limit to 100 silently (:471-498).
- **Build:** simplest full-field store under an explicit storage
  budget with honest fail-closed refusal past the budget (spec's
  preferred branch — no spill authority invented); find/list gain
  truthful pagination: stable order, disclosed total, cursor with
  stale-cursor refusal; direct list/find parity; save/reload and
  DuoBeta consumer read the same preserved evidence.
- **Suite:** `form/r23_outcome_evidence_test_spec.py` (2/9 at base,
  delivered) + code-stage extensions (save/reload, privacy
  canaries, invalid owner).
- **Register:** row #24's evidence half; row #142 consumes the
  pagination contract.
- **Gate:** none outstanding. Build-ready on PLAN-CONFIRM.

### GP-E03 — R17/R19 (CLOSED — no build)

R17 is COMPLETE (row #14, via PR #500 settlement, merged
`af2519b6`). R19/R19-SIB are built and credited with no register
row (Director identity ruling 7027783108) and never become board
points. Recorded here so the Part's circuit list is complete;
nothing is built, claimed, or re-opened.

### GP-E04 — R25 (BUILT — credit trailing)

Built and merged as PR #496, merge SHA
`c13428cb5807cec9501c1296fd0520f934ff9f4f` (ancestor of current
main, verified). Ace's single-failure ruling (7040200362) noted
the one unreproduced smoke failure; Director 7040318415 lifted
the credit HOLD. **Outstanding: the Keeper's scoped postmerge
CODE CREDIT CONFIRM** — package presented (7040793444) and
renewed in this Part's evidence document. No build, no row, no
board point.

### GP-E07 — Whole addressed-Dell execution audit (EVIDENCE → per-Dell gates)

- **Contract:** for every address 00–99: declared name/manor,
  actual dispatcher + handler, mutation/read/refusal class, side
  effects, required Args, expected output/error, observed public
  door, tests, open design decision, one contract test. Registry
  ACTIVE = reachability only, never completion. The "99 vs 100
  Dells" label is reconciled as evidence (100 addresses exist:
  51 Core I + 49 Core II) without deleting an address or counting
  address 151 as a core Dell.
- **Current state:** the 100-address baseline exists
  (Edition 1 file `05_DELLS_100_ADDRESS_BASELINE.md`); the
  per-address *execution* audit (observed door + contract test
  per address) has not been run as one body.
- **Build:** (1) run the audit as an evidence sweep over the
  public doors, address by address, in isolated state;
  (2) publish the audit ledger inside this PR (per-address
  verdicts: CONTRACT_PROVEN / DEFECT / MESSAGE_ONLY /
  UNREACHABLE); (3) execute the repair gates the audit proves —
  each defect becomes a bounded fix inside this Part with its
  own failing-first check, or is escalated as a named question.
  Rows #30 (reachability), #36 (message-only descriptions) and
  #114 (D1 deepening) are discharged by this circuit's output.
- **⚠ DOWNSTREAM DEPENDENCY:** GP-E07's settled Dell contracts
  are consumed by **Part I's C13** (Simulate executes Dells
  against these contracts) **and Part I's C12**. Part I does not
  wait idle — it builds against the baseline — but its
  integration pass consumes THIS Part's audit output. The audit
  ledger is therefore scheduled FIRST among this Part's
  code-stage workstreams (see §5), and its publication is a
  named integration event for Part I.
- **Gate:** evidence stage needs no gate; repair gates follow
  the audit's own findings.

### GP-E08 — Typed English/LM/Seed admission (BUILD; anchor row #24)

- **Contract:** one lossless AST — raw user text → explicit typed
  roles → operator → operand → execution mode — with source-span
  provenance and an ambiguity verdict; legacy seed semantics
  preserved for unambiguous cases; ambiguous delimiter and
  mis-typed roles rejected BEFORE mutation.
- **Build:** the typed admission layer in the translate door
  (Part II regions of `form/mandell/translate.py` + callers),
  proven end-to-end by the 72-06 Intent.args contract: English,
  REPL and executor agree on args, side effects and refusal
  codes — including Class E silent default, missing field,
  escapes, nested Chain, reserved address 151, and old saved
  macros. The modernized #308 probes (§4) are this circuit's
  verification instrument.
- **Register:** row #24 PARTIAL → COMPLETE on this circuit +
  GP-E01 landing with the modernized oracle green.
- **Gate:** none outstanding. Build-ready on PLAN-CONFIRM.

### GP-E09 — Shared conditional engine (BUILD; rows #11–#13 family, #12, #38, #39, #45)

- **Contract:** one prefix typed-predicate authority serves
  Compare, Branch, Assert, Guard, Until, While and Threshold;
  named typed comparisons; explicit missing vs zero vs false;
  numeric finite values; no eval; no inferred truth on
  unparsable text; three-valued eligibility where evidence is
  missing. (The silent-truthiness defect is already fixed —
  `condition_unparseable` refusal exists and is NOT re-opened.)
- **Build:** (1) refusal RECEIPTS for unparseable infix
  conditions (row #12's remainder: today While/Until fail closed
  but issue no refusal receipt); (2) the receipted Loop grammar
  follow-up (row #13); (3) wider-scope re-proofs for rows #38
  (frame guarantees), #39 (bounds + nested inheritance), #45
  (Guard/Assert propagation) on the shared engine.
- **Suites:** existing `dd42_predicate_infix_test`,
  `step7_control_verdicts_test`, `guard_assert_propagation_test`,
  `first_failure_provenance_test` (row #37's wider scope rides
  this engine's receipt work) + code-stage receipt checks.
- **Gate:** **NEEDS_DIRECTOR** — Q-DD42.2, the While/Until
  infix-condition plan-reading question (row #12). The refusal-
  receipt build does NOT wait for it (fails-closed + receipt is
  lawful under either reading); infix *semantics* are built only
  if the ruling admits them, via a versioned contract with
  precedence tests.
  **RULING FOLDED (2026-11-20, Director 7044836836 via Part VI):**
  Q-DD42.2 is decided — the bounded behavioral contract for row
  #12 is the TYPED While/Until condition-side REFUSAL. Infix
  condition semantics are NOT admitted; the refusal-receipt build
  proceeds under this contract, and row #12 stays OPEN pending
  the actual fix. No second policy round.

### GP-E10 — DD-43 Parallel as real isolated arms (STAGED BUILD; row #11)

- **Contract (spec stages):** E10A pure parallel result model +
  replayable fixtures (typed arm results: read_set, write_set,
  external_effects_declared, diff, failure, provenance);
  E10B concurrent worker isolation + cancellation/timeouts
  WITHOUT writes; E10C preview/read-write conflict detector
  (non-committing Simulate previews every arm + conflict);
  E10D human-approved canonical serial commit with
  crash/recovery proof. Until isolation is demonstrated, the
  product MUST NOT announce true concurrency; conflicts return
  CONFLICT_REQUIRES_HUMAN_RESOLUTION with all previews
  preserved and no partial commit; Join is a deliberate
  resolution, never last-writer-wins.
- **Current state:** Dell 62 Parallel executes sequentially in
  listed order (bounded recheck, PR #320; row #38's record).
  Design stage (D) is complete in the spec; no stage is built.
- **Build:** E10A–E10C inside this Part's code stage; E10D's
  commit gate is a human-approved act per execution (the
  mechanism is built; each live Join remains deliberate).
  Dependencies per spec: GP-E09 (conditions), GP-E12 (state
  quantities); GP-E14 (Simulate) is Part I's circuit — E10C
  consumes its board contract as a downstream interface, noted
  as a cross-Part dependency, not a start blocker.
- **Register:** row #11 OPEN → PARTIAL on E10A–C, → COMPLETE
  on E10D proven.

### GP-E11 — Eight thin-spec elder Dells (DESIGN + FALLBACKS ONLY — Ace-gated)

Addresses 00 Nova, 03 Logic, 07 Link, 10 Keep, 11 Architect,
12 Test, 14 Bind, 19 Drive. The Edition 1 minimum operations are
Director design PROPOSALS, explicitly not Ace-adopted semantics.
**NEEDS_OVERSEER:** any sovereign meaning change is GATED_BY_ACE.
This Part builds, at code stage, only the safe read-only /
reference fallbacks (e.g. Nova = read-only origin receipt, never
a wipe; Test = declared read-only/isolated assertion capture,
never a forged PASS) with input roles, outputs, explicit
refusal, dry-run path and tests — and presents the semantic
questions for Ace's ruling in the confirm package. No elder
Dell gains live semantics from this Part without Ace.

### GP-E12 — Quantification & inference (BUILD; rows #149, #150, #151)

- **Contract:** Measure returns a typed value (quantity, unit,
  scope, source, timestamp, uncertainty, eligibility set,
  provenance); a count is never called a physical Measure unless
  the receipt says cardinality; Threshold/Weight/Normalize
  consume the same typed value; noncommensurable units refuse
  instead of inventing conversions; Cause/Depend/Infer separate
  observed correlation, declared dependency, verified causal
  claim; Profile = monotonic elapsed time + environment/workload
  identity; token counts label tokenizer/model basis.
- **Current state (measured at base):** 71[Measure] carries
  value/count/unit/source but NO timestamp, provenance, method,
  scope, uncertainty or eligibility (suite
  `form/c7_measure_family_test_spec.py`, 5/8). 40[TokenCount] reports
  approx_units with no basis label. 49[Profile] (the #401
  speedometer) discloses kind/workload/stages/env — pinned.
- **Build:** extend the Measure result contract in
  `form/mandell/core_ii.py` (Measure/Threshold/Weight/Normalize
  family) with timestamp + provenance + method/scope;
  noncommensurable-unit refusal checks; TokenCount basis label
  (row #150's remainder, with the shorthand-harmony verification);
  Profile's real-observation mode + overhead disclosure
  (row #149's remainder past the #401 benchmark scope).
- **Register:** #151 OPEN → COMPLETE; #150 PARTIAL → COMPLETE;
  #149 per the #401 settlement + this remainder.

### GP-E20 — Nursery full behavior (BUILD + VALIDATE; rows #140–#143, #177)

- **Contract:** production/public parity — every eligible
  proposal reachable, exact total/shown, stable sorting and
  cursor invalidation, no source omission, human-only edits,
  separate score eligibility, all status filters, wall
  inheritance/manual choice, atomic acceptance, multiowner and
  failed-save recovery; the Lens keeps S = 0.40 LINK + 0.25 ACE
  + 0.20 FRESH + 0.15 NOVEL with missing ACE evidence marked
  unavailable, never synthetic; NO unruled destructive pending
  cap; an AI organizer drafts suggestions only, never edits;
  pointer identity verified after undo/redo; auto-confirm stays
  OFF / sandbox-first except as Ace rules.
- **Current state:** C5 R1–R4 are built (#457, #465, #467,
  #473 — R1's credit is Package 5 of the evidence document);
  the Lens is the default Nursery view. What has never been run
  is the full-behavior parity validation above as one body, and
  two ruled remainders are unbuilt: FRESH aging (row #177 —
  3/7/14-day marks, 30-day fade ONLY while new proposals are
  arriving) and switchable Plane ranking (row #141) and the
  Discover+Resolve single search machinery (row #142, consuming
  GP-E02's pagination contract).
- **Build:** (1) the parity validation battery against the
  public doors (evidence first); (2) FRESH aging implementation
  on the ranking circuit (rows #177 + #140's remainder);
  (3) switchable Plane ranking (row #141); (4) Discover+Resolve
  unified search with stable ordered pages + totals (row #142);
  (5) door-policy receipts (row #143's buildable half: receipts
  name policy version + authorizing rule; auto-passage itself
  stays OFF — **NEEDS_OVERSEER**, §7).
- **Suites:** existing `form/nursery_c5r*_test.py` family +
  code-stage parity/aging/ranking/search suites.
- **Register:** #140 PARTIAL → COMPLETE; #141, #142 OPEN →
  COMPLETE; #177 OPEN → COMPLETE; #143 stays OPEN (flagged).

---

## 3. Family build sections (register slices §14.3)

### C4 — Reference family (rows #137, #138, #139, #179)

- **Zipper (#137):** Compress gains a resolvable source link:
  the compressed unit records its source identity + full source
  (or a digest-bound reference into the outcome/store layer);
  Expand resolves the link and retrieves the full intended
  source under a declared current-vs-versioned rule (default:
  current, named in the receipt). Build sites:
  `form/mandell/executor_leaf.py` Compress/Expand arms (29/30) +
  the unit record they place.
- **InjectRef (#138):** Inject of an already-present target adds
  a typed reference (no new unit); cycles, missing, foreign and
  superseded targets resolve with typed honest results; graph
  refs and Core II aliases reconcile through the one reference
  type. Build site: Inject arm (36) + reference representation.
- **Distill (#139 + #179 as one circuit, two rows):** Distill
  produces an essence that uses the source's actual words,
  detail and goals, carries provenance (source identity) and
  disclosed omissions, and is usable without its source. The
  mode contract (row #179, Ace-ruled 2026-11-10): a docked AI
  distills when one is docked; the deterministic recipe when
  none is — the receipt names which mode produced the essence.
  Build site: Distill arm (38) + `distill_label` replacement
  (the current slug-shortener is retired as the Distill
  mechanism; it may survive only as a display label).
- **Suite:** `form/c4_zipper_inject_distill_test_spec.py` (6/10 at
  base, delivered) + code-stage extensions (cycle/missing/
  foreign reference cases, versioned Expand rule).

### C9 — Translate family (rows #156, #157)

- **NoIntent (#156):** the unknown-text fallback stops inventing
  a Show seed: unroutable text returns an explicit no-intent
  refusal (no 09[Show] seed, no executed Dell), the query is
  carried whole or the refusal discloses the bound, and the
  route receipt names the engine (deterministic vs docked).
  Build site: translate fallback (translate.py :975 area) +
  route receipt.
- **DualMode (#157):** NO BUILD. Ace ruled Adapt adoption with
  his "not yet" in force until he calls it. This Part pins the
  current lawful behavior (deterministic door, LM-4 receipt
  attached — suite pins) and flags the row NEEDS_OVERSEER.
- **Suite:** `form/c9_translate_honesty_test_spec.py` (2/4 at base,
  delivered).

### C10 — Harmonic family (rows #158, #159)

- **Stamps (#158):** stamps attach to the ITEM: the unit record
  gains a stamps list — {mark, provenance (who/when/which
  operation), stable order} — moving an item never silently
  changes its note, and stamps round-trip through save/load.
  Build sites: Stamp arm (34) + unit record + persist
  serialization of the new field (persist is Part I's region —
  the field's *contract* is defined here; the serialization
  change is filed as a patch note to Part I if the site falls
  in its region, per the collision protocol).
- **Lenses (#159):** derived lens views rearrange DISPLAY only
  and restore exact canonical placements on exit. No public
  lens surface exists to probe today; the code stage designs
  the surface (against the C5 Lens precedent in SEE) and lands
  its failing-first suite WITH the design, before the build —
  the suite is specified here (view-construction does not
  mutate canonical placement; exit restores byte-identical
  placement; derived modes are named and reversible) and is
  deliberately NOT faked into this PR without a surface to
  measure.
- **Suite:** `form/c10_harmonic_stamps_test_spec.py` (2/4 at base,
  delivered) + code-stage save/load round-trip extension.

### C11 — Editing / Shelf / Manifest family (rows #160–#163)

- **Shelf (#160):** Macro reads back as one seed — whole. Two
  compounding cuts measured at base: history-entry cuts on the
  note path and `macro_seed`'s [:200] join slice
  (form/open.py:371). The read-back contract is this Part's;
  the entry-retention machinery is Part I's R5/GP-E05
  territory — the fix is coordinated: this Part files the
  contract + suite, Part I's history work removes the entry
  cuts, and `macro_seed` (history-adjacent, Part I region of
  open.py) is changed via patch note to Part I if ownership
  requires it. No silent cross-lane edit.
- **Edit (#161):** contained-part drafts independent from live
  originals; proposals carry target revision,
  before/after/diff, impact coverage; stale-original proposals
  refuse. Design-first inside the code stage (draft object
  model), suite written against the design before the build,
  per the C10.Lenses discipline.
- **Manifest (#162):** Manifest walks the CONFIRMED item: the
  unit's manifest state becomes explicit (confirmed →
  manifested, durable, recoverable), Manifest on an
  already-manifested item is idempotent (retry produces one
  result), and Manifest NEVER creates a duplicate unit.
  Build site: Manifest arm (50) + unit manifest field
  semantics.
- **Move (#163):** a Universal Move dispatch: the English door
  stops capturing "move" as Drive/walk; Move dispatches by
  explicit object class to EXISTING engines (plane placement,
  shelf, room/box membership), preserves identity, refuses
  ambiguity/collisions; Psalms are never freight; an AI move
  is a pending proposal, never a live act.
- **Suite:** `form/c11_shelf_manifest_move_test_spec.py` (2/6 at
  base, delivered) + code-stage extensions (idempotent retry,
  collision refusal, draft staleness for #161).

### Remainder closures (bounded re-proofs, no new machinery)

- **#28 (Seed grammar, PARTIAL):** answer Q-72-10.1–.3 and close
  the wider stress scope on `seed_grammar_stress_test`.
- **#31 (typed signatures, PARTIAL):** complete the wider
  SM-17/SM-19 per-signature audit on
  `typed_signature_contracts_test`; Dell 55's four legacy quirks
  stay permanent contract.
- **#35 (Show placeholder, PARTIAL):** the message-layer repair
  is Director-confirmed landed; the remainder is the Studio /
  browser-surface remedy — **the remedy ruling is owed by the
  Director** (§7); on the ruling, the remedy lands here or in
  Part IV's surface scope as the ruling directs.
- **#41 (Commit/Revert, PARTIAL):** wider exact-state +
  side-effect boundary challenge on `step8_transactions_test`.
- **#43 (Define/Alias/Compose, PARTIAL):** the failed-run
  non-publication fix landed (PR #322); close the retained
  wider scope with adversarial failed-run persistence probes.
- **#95 (Dell 08 coverage, OPEN):** naming / slug collision /
  skin / legacy-label regression suite for Dell 08 Create —
  coverage build only, no behavior change unless a probe
  proves a defect (then it routes through GP-E07's gates).
- **#96 (Bridge/Embed refusal, OPEN):** reverify reserved-
  address refusal / honest unsupported behavior of Bridge and
  Embed at the public doors — evidence circuit; GP-E07
  consumes its verdicts for addresses 151-adjacent behavior.
- **#113 (Symbiosis, PARTIAL):** ledger v3 delta re-run +
  the held-out prediction test for composition laws; the
  pairwise classification itself is executed evidence, landed
  inside this PR at code stage.
- **#178 (Embed provider, OPEN):** Ace-ruled provider-agnostic
  dock capability; its implementation vehicle is C8 EmbedBind,
  register row #153 — **Part I's row**. This Part's scope is
  only the Dell-contract side (Embed's contract in the Dell
  registry + GP-E07 audit coverage). The row's flip follows
  Part I's #153; flagged as a cross-Part dependency, not
  double-owned.

---

## 4. Register rows — remainder, build home, proposed flip

All flips are PROPOSED. They execute only on CODE-CONFIRM at the
Part's exact head, as surgical per-row edits inside this PR,
with the render re-generated and `--check` byte-identical.

| # | Status now | Build home | Proposed flip on confirm |
|---|---|---|---|
| 11 | OPEN | GP-E10 | → PARTIAL (E10A–C); → COMPLETE when E10D proven |
| 12 | OPEN | GP-E09 (+Q-DD42.2 ruling) | → PARTIAL (refusal receipts); → COMPLETE on ruling + contract |
| 13 | OPEN | GP-E09 | → COMPLETE (receipted grammar landed + proven) |
| 24 | PARTIAL | GP-E01 + GP-E08 + §6 oracle | → **COMPLETE** |
| 28 | PARTIAL | §3 remainder | → COMPLETE |
| 29 | PARTIAL | GP-E01 + handler census | → COMPLETE |
| 30 | PARTIAL | GP-E07 | → COMPLETE (reachability deepened per audit) |
| 31 | PARTIAL | §3 remainder | → COMPLETE |
| 35 | PARTIAL | §3 remainder (ruling owed) | → COMPLETE on remedy landing |
| 36 | PARTIAL | GP-E07 | → COMPLETE (message-only audit discharged) |
| 37 | PARTIAL | GP-E09 receipt work | → COMPLETE |
| 38 | PARTIAL | GP-E09 / GP-E10 | → COMPLETE |
| 39 | PARTIAL | GP-E09 | → COMPLETE |
| 41 | PARTIAL | §3 remainder | → COMPLETE |
| 43 | PARTIAL | §3 remainder | → COMPLETE |
| 45 | PARTIAL | GP-E09 | → COMPLETE |
| 95 | OPEN | §3 remainder | → COMPLETE (coverage landed; or PARTIAL if a defect routes to E07) |
| 96 | OPEN | §3 remainder | → COMPLETE (reverified with evidence) |
| 113 | PARTIAL | §3 remainder | → COMPLETE (v3 delta + held-out test) |
| 114 | PARTIAL | GP-E07 | → COMPLETE when all 100 addresses reach the standard; otherwise stays PARTIAL with the deepened count stated — never inflated |
| 137 | OPEN | C4 Zipper | → COMPLETE |
| 138 | OPEN | C4 InjectRef | → COMPLETE |
| 139 | OPEN | C4 Distill | → COMPLETE |
| 140 | PARTIAL | GP-E20 (+#177) | → **COMPLETE** |
| 141 | OPEN | GP-E20 | → COMPLETE |
| 142 | OPEN | GP-E20 (+GP-E02 pagination) | → COMPLETE |
| 143 | OPEN | GP-E20 (receipts only) | **stays OPEN** — flagged NEEDS_OVERSEER, not silently held |
| 149 | OPEN | #401 settlement + GP-E12 | → PARTIAL on settlement; → COMPLETE on GP-E12 remainder |
| 150 | PARTIAL | GP-E12 | → COMPLETE |
| 151 | OPEN | GP-E12 | → COMPLETE |
| 156 | OPEN | C9 NoIntent | → COMPLETE |
| 157 | OPEN | — (Ace's "not yet") | **stays OPEN** — NEEDS_OVERSEER |
| 158 | OPEN | C10 Stamps | → COMPLETE |
| 159 | OPEN | C10 Lenses | → COMPLETE |
| 160 | OPEN | C11 Shelf (+Part I coordination) | → COMPLETE |
| 161 | OPEN | C11 Edit | → COMPLETE |
| 162 | OPEN | C11 Manifest | → COMPLETE |
| 163 | OPEN | C11 Move | → COMPLETE |
| 177 | OPEN | GP-E20 FRESH aging | → COMPLETE |
| 178 | OPEN | Part I row #153 vehicle | → follows Part I; this Part claims no flip |
| 179 | OPEN | C4 Distill mode | → COMPLETE |

**Credit settlements riding this Part** (evidence document):
#401 → row #149 identity (flip above); #416 + #439 → proposed
no-row code credit (LM-4 pair); #429 + #457 → proposed no-row
code credit (C5 family), no double-count with rows #140–#143;
R25/GP-E04 → credit CONFIRM at `c13428cb`, no row, no point.

---

## 5. Build order inside the Part (code stage)

All workstreams start in parallel on PLAN-CONFIRM; the order
below is integration order, not a start sequence.

1. **GP-E07 audit ledger** — first to publish, because Part I's
   C13/C12 integration consumes it (§2, GP-E07 ⚠).
2. **GP-E01 + GP-E02** — first-priority repairs (Edition 1's own
   sequencing); independent files, no shared sites.
3. **GP-E08** typed admission, verified by the §6 oracle.
4. **Family builds** — C4, C9, C10, C11, GP-E12, in their own
   modules/regions, each against its delivered suite.
5. **GP-E09** engine + receipts; **GP-E10** stages A–C (D's
   mechanism last, it is the deepest state change).
6. **GP-E20** parity battery → aging / ranking / search builds.
7. **Remainder closures** (§3) run throughout; each is small
   and evidence-shaped.
8. **GP-E11 fallbacks** — read-only/reference only, in parallel,
   never blocking.

Serial by law, unchanged: the ×3 campaign (global queue, one at
a time across all Parts) and this Part's merge (§32,
main-session). Nothing else in this Part waits.

---

## 6. The #308 oracle modernization bundle (anchor: row #24)

**State, verified 2026-11-20:** the modernization the Director
ordered (7040506653) is ALREADY BUILT on PR #308's own branch
`uni/72-06-intent-args`, current head
`295abf179229a1a6e3d26305000afa300e86964e`:

- Historical census artifacts (2026-11-05) preserved
  byte-for-byte under `director-reports/evidence/72-06-intent-args/`
  and hash-verified (MANIFEST.sha256);
- `CURRENT_MAIN_DELTA_2026-11-20.md` — the dated current-main
  delta: E19/E20 Class E word-count defect classified
  ALREADY_FIXED, A5 silent producer clamp classified
  INTENTIONAL_GUARD (execution bound enforced and stated),
  D17/D18 dead-arg production classified (gone);
- NEW current-contract probes `q06_current_probe.py` (7 checks,
  census path) + `q06_current_repl_probe.py` (8 checks, bare
  REPL), with run logs and CURRENT_MANIFEST.sha256;
- `.github/workflows/verify-72-06.yml` rewritten: exact-head
  assertion first, historical artifacts verified by hash WITHOUT
  reasserting old semantics, new probes executed at the head.

**This Part does NOT duplicate those files** (a second copy
would create a rival authority). The Part's acts are:
(1) adopt the bundle by reference as GP-E08's verification
instrument; (2) at code stage, run the modernized probes
against this Part's exact head as part of the campaign
evidence; (3) row #24's flip (§4) cites the modernized oracle
as its verification instrument, per the Director's ruling.

**Remaining gate on #308 itself:** the Director's records
MERGE HOLD on PR #308 stands until the modernized oracle is
reviewed and passes at that PR's head — an authority act on
#308, not a Uni build. **Ask (in §10):** the Director confirms
whether #308 lands as its own records PR (its ruling's shape)
with this Part consuming it by reference, or whether he wants
the bundle cherry-picked into this Part PR at integration.
Uni's recommendation: #308 lands as its own records PR —
its evidence directory is self-contained and its hold is
already scoped there.

**STATUS UPDATE (2026-11-20, Director FULL/DEEP disposition on
PR #506):** the question above is ANSWERED by events and by the
Director's decision. PR #308 MERGED as `f9a275ca` (head
`295abf17`; Keeper SCOPED RECORDS CONFIRM 7043776253; the
Director's modernization disposition satisfied on the record).
Per the Director's decision, the already-landed #308 independent
records PR is the source of record: Uni does NOT cherry-pick the
old census files or merge them a second time. The modernized
oracle and its merged-run tests stand as the explicit
current-main baseline for this Part's §4/§6 citations, pinned at
merge `f9a275ca`. The §11 caveat about the #308 branch moving is
spent — the branch is merged; the citation pins the merge. This
is a historical-status correction, not a new #308 CODE grant.

---

## 7. Gates and dependencies

**NEEDS_OVERSEER (Ace):**
- Row #143 (C5.Door): Nursery auto-passage stays OFF until Ace
  supplies standards and scope. Buildable half (policy
  receipts) proceeds; the row stays OPEN, flagged.
- GP-E11: the eight elder Dells' semantics are Ace's gate.
  Read-only/reference fallbacks only until he rules.
- Row #157 (C9.DualMode): Adapt adoption — Ace's "not yet"
  stands until he calls it. No build.

**NEEDS_DIRECTOR:**
- Q-DD42.2 (row #12): the While/Until infix-condition
  plan-reading question. Refusal-receipt build proceeds under
  either reading; infix semantics wait for the ruling.
- Row #35's Studio/browser-surface remedy ruling (owed).
- The #308 landing-shape confirmation (§6).

**Cross-Part:**
- **GP-E07 → Part I C13/C12** (⚠ named dependency): Part I's
  integration passes consume this Part's settled Dell
  contracts. The audit ledger publishes first (§5).
- GP-E10 stage E10C consumes Part I's GP-E14 Simulate board
  contract as an interface.
- Row #160's entry-cut fix coordinates with Part I's R5 /
  GP-E05 history work; `macro_seed` changes go by patch note
  if Part I owns the site.
- Row #158's stamp field serialization may touch Part I's
  persist region — patch note protocol applies.
- Row #178's vehicle is Part I's row #153 (C8 EmbedBind).

**Serial by law:** campaigns (global queue) and merges (§32).
No other serialization is introduced by this plan.

---

## 8. #433 Phase T prototype design (FI-010 fold-in)

PR #433 (FI-010 Phase R — Morphology Census + license audit)
landed as records on 2026-11-18. The Phase T PROTOTYPE DESIGN
is this Part's fold-in, as a design deliverable at code stage:
a design record specifying the morphology prototype's Dell
Plan gate — which Dell contracts the prototype exercises
(drawn from GP-E07's audit verdicts for the morphology
addresses), its failing-first acceptance checks, and its
non-goals — filed inside this PR for Director review. **No
prototype code** is built by this Part: the prototype's own
build follows its design confirm, under the same
plan → confirm → code discipline. This keeps #433's Phase T
from becoming either a orphan design or an ungated build.

---

## 9. Campaign and CI terms (code stage)

- **Regression campaign ×3** in the global serial queue
  (forward, `--twice`, `--order rev`), logs under the goal's
  `hidden_files/`, drivers resetting SIGINT/SIGQUIT to SIG_DFL,
  one campaign at a time across all Parts.
- **Exact-head CI:** Python package + Form smoke SUCCESS at the
  Part's final head; the modernized verify-72-06 probes run
  against the head as Part evidence (§6).
- **Suite list (all must be green at the exact head):** the
  seven suites delivered in this PR (§1) plus the package's
  existing suites — `translate_intent_args_test`,
  `translate_word_counts_test`, `translate_dead_args_test`,
  `typed_signature_contracts_test`, `seed_grammar_stress_test`,
  `dd42_predicate_infix_test`, `step7_control_verdicts_test`,
  `step8_transactions_test`, `guard_assert_propagation_test`,
  `define_compose_nonpublication_test`,
  `first_failure_provenance_test`, `c7profile_test`,
  `c7schema_test`, the `nursery_c5r*_test` family,
  `r25_extra_operand_test`, `eval_predicate_surplus_test` —
  plus the code-stage suites specified in §3 (C10.Lenses,
  C11.Edit, GP-E20 parity/aging/search, GP-E10 stages).
- **Mutant discipline:** any mutant check is reverted by
  inverse edit only, never `git checkout` on worked files.
- **Merged-main proof:** post-merge smoke at the merge SHA +
  the register render check, reported in the closing package;
  the register write rides inside this PR (§4), so the board
  moves with the merge, never after it.

---

## 10. Authority asks (exact)

1. **Director + Keeper PLAN-CONFIRM for Part II** on this
   package (this plan + the seven measured failing-first
   suites + the credit-evidence document), in the one-bundle
   presentation with the other seven Parts. On PLAN-CONFIRM,
   the code stage builds §2–§5 as specified.
2. **Keeper grouped credit decisions** on the five evidence
   packages (`PART_II_CREDIT_EVIDENCE_2026-11-20.md`):
   #401 (row #149 identity), #416 + #439 (LM-4 pair identity),
   #429 + #457 (C5 family identity) — credit, or name the
   exact missing evidence per package.
3. **Keeper scoped CODE CREDIT CONFIRM** for R25 / GP-E04 at
   merged SHA `c13428cb5807cec9501c1296fd0520f934ff9f4f`
   (renewed from package 7040793444).
4. **Director ruling on Q-DD42.2** (row #12) — ANSWERED
   2026-11-20 (7044836836: typed condition-side refusal; folded
   at §2 above). Row #35's surface remedy remains open, owner-
   specific; neither blocks the builds named in §2/§3.
5. **Director confirmation of the #308 landing shape** (§6) —
   ANSWERED 2026-11-20: #308 landed as its own records PR and
   MERGED as `f9a275ca`; this Part consumes it by reference as
   the current-main baseline (see the §6 status update).

---

## 11. Limitations and non-coverage

- This PR is the PLAN stage. It changes no production code and
  no register state; every tally in §1 is a measurement of
  base main `af2519b6`, not a claim about a repaired product.
- Failing-first suites for C10.Lenses (#159) and C11.Edit
  (#161) are specified, not delivered: neither surface exists
  to measure today, and a suite written against an invented
  surface would be a false receipt. They land with their
  designs at code stage, before their builds.
- GP-E07's audit may find defects this plan does not predict;
  those route through the audit's own gates (§2) and may
  extend the Part's code stage. Row #114's COMPLETE flip is
  explicitly conditioned on all 100 addresses reaching the
  standard — if the audit proves a longer tail, the row stays
  PARTIAL with the count stated.
- The #308 bundle's contents are cited from that branch's
  current head (295abf17, read 2026-11-20); if that branch
  moves, the citation is refreshed at integration, and any
  divergence is reported, never silently absorbed.
- Rows #143, #157 and GP-E11's semantics are Ace-gated; this
  plan builds nothing that presumes his rulings.

---

## ACE RULINGS (2026-11-20 — answering this Part's NEEDS_OVERSEER set)

- **DC-8 (151[Harmonic]): A.** The reserved example address
  stays documented and NON-EXECUTING, with its explicit refusal.
  Not a 101st Core Dell.
- **DC-9 (orphan candidates): A, with Ace's maturation
  directive.** Orphans stay intact and labeled, decided
  case-by-case. Ace further directs: after the plan's code runs
  properly, **each Dell is individually completed to its full
  maturity and capability** — repeated as many times as needed
  until the Dells are universal. Recorded as a post-code-stage
  maturation program (future scope; not a current build).
- **DC-10 (Space): A.** Space stands as the advisory
  measured-capacity (negative-space) reading, not a new force.
- **Row #143 (Nursery auto-passage door): A for now, with a
  future directive.** The door stays OFF; the policy-receipts
  half proceeds. Ace directs that an auto door be created
  eventually — **fully customizable by the user, within safe
  limits** — recorded as future scope for this row.
- **Row #157 (Adapt): NOW.** Ace authorizes the DualMode build.
- **GP-E11 (elder Dells) — premise corrected by Ace
  (2026-11-20).** The elder Dells' meanings are NOT undefined
  and were never awaiting definition: Ace adjudicated all 100
  Dells one by one (the 2026-11-08/09 tour, Nova through 99 —
  for each Dell he confirmed its function or gave the
  instruction for what it should be), and that adjudication is
  the meaning authority of record (ACE_FUTURE_DEVELOPMENT_PLAN
  §12, in this repository). GP-E11 builds to those adjudicated
  meanings. The "meanings Ace-gated / safe read-only fallbacks"
  framing in this plan (including the §11 limitation line) is
  WITHDRAWN; the question is not to be asked again.
