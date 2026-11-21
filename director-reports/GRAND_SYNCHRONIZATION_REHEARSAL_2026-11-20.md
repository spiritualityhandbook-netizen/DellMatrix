# GRAND SYNCHRONIZATION REHEARSAL — GP-E27 RECORD (Part VII, PR #502)

**Governing plan:** `director-reports/PART_VII_PLAN_2026-11-20.md`
(sections cited as "plan §n"). This file carries, per plan §10: the
rehearsal record proper, the §6 sequence readiness record, and the
§2.3 merge-queue landing annex.

**Stage honesty:** the GP-E27 rehearsal *executions* run against
merged main after Parts 0–VI and IV's records have landed (plan
§5.1). What exists today is (a) the landing annex, filled as landings
occur, and (b) BASELINE harness runs (plan §5.1(iii)): the harness
suites executing in isolated state against the pre-Parts system.
Baseline grades are evidence about the harness and the current
program — never rehearsal grades, never product certification.

---

## 1. Merge-queue landing annex (plan §2.3)

Landing order (merge queue only): **0 → V → III → II → I → VI → IV →
VII**. One row per Part PR, filled by the main session at each
landing. The "board after landing" column is intentionally not
restated as a completion number: Ace ruled 2026-11-21 that the
board's completion number is inaccurate and must not be used; progress
is reported in plain words until he says otherwise.

| # | Part | PR | Head at confirm | Director act | Keeper act | Campaign receipt | Merge SHA | Merged-main smoke | Rows flipped |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 — Scoreboard | #503 | f67f7d3a | FINAL CODE CONFIRM + §32 authorization 7061231824 | Grok CODE CONFIRM 7061148370; Gemini CODE CONFIRM 7061151965 | Part 0 ×3 ALL_PASS (7057264913) | c380e7a6567ae58db792a4d474b363a59da3a4b6 | ALL SUCCESS at merged main | per #503 record (GP-E25 S1–S3 still owed) |
| 2 | V — Scoreboard Reconciliation | #504 | 1ce65c88 | authorization 7061243773 | Gemini CODE CONFIRM 7061152347 | n/a (records/tooling) | 437976ea8304713e84c46a3160c6eaea67d29848 | ALL SUCCESS at merged main | #90/#93/#94 implemented |
| 3 | III — Incompleteness Register | #501 (plan) + #509 (code) | #509 head b9f70da | conditional authorization 7061236041, discharged by campaign | #509 CONFIRM 7061152744 (Gemini); 7061147590 (Grok) | serial ×3 ALL_PASS, REGRESS 306/306 ×3 (7061966516) | #501: 23936fc6; #509: d1e1fb254b6913afce2f94f2977d9108ac436198 | #509 merged-main smoke: one timing-oracle failure, root-caused to a test instrument defect; re-run attempt 2 TERMINAL SUCCESS; exception closers still owed (post-repair merged-main proof) | #120/#172/#174 COMPLETE; #21 stays OPEN |
| 4 | II — Dell Plan | #506 | — | — | — | — | — | — | — |
| 5 | I — Architecture | #508 | — | — | — | — | — | — | — |
| 6 | VI — Unknowns | #507 | — | — | — | — | — | — | — |
| 7 | IV — Far Stratum | #505 | — | — | — | — | — | — | — |
| 8 | VII — Execution Order | #502 (this PR) | — | — | — | program-final ×3 (last slot) | — | — | — |

## 2. §5 sequence readiness record (plan §6)

Filled from evidence at rehearsal time. Every row reads NOT YET
ASSESSED until its closure evidence exists.

| Unified §5 step | Edition 1 counterpart | Owning Part(s) | Status |
|---|---|---|---|
| SEQ1 Dell Plan gate | P1 Dell Plan (+ P0 Integrity beneath it) | II (gate), 0 (integrity) | NOT YET ASSESSED |
| SEQ1.5 Census X11 | P1.5 Runtime X11 | I / III | NOT YET ASSESSED |
| SEQ2 HCN build (frozen R3) | P5 HCN R3 | I (GP-E22) | NOT YET ASSESSED |
| SEQ3 The Dock live | P6 Dock/Psalm (first half) | I (GP-E23) | NOT YET ASSESSED |
| SEQ4 Psalm Matrix surface | P6 Dock/Psalm (second half) | I | NOT YET ASSESSED |
| SEQ5 Windowed Workspace | P7 Surfaces | I (GP-E24/E25/E26) | NOT YET ASSESSED |
| SEQ6 Grand Synchronization | P8 Grand Synchronization | VII (GP-E27) | NOT YET ASSESSED — harness construction in progress (Annex A) |
| §7 Far Stratum (step 7) | P9 Far Stratum | IV (designs), future turns (builds) | NOT YET ASSESSED — opens only after SEQ6 closes |

## Annex A — BASELINE harness packets (plan §5.1(iii), §5.3 fields)

### A.1 — J-01 Chain (family suite `form/journey_chain_test.py`)

- journey_id: J-01
- feature_scope: typed + legacy Mandell chains in the REPL; per-atom
  receipts; mid-chain refusal precedence; cold reload comparison
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base; suite executed in the PR #502 clone)
- PR/head: #502 @ bf75581245b7d45ecc6c3031c6335964e817fec4
  (baseline run executed before this section's commit; the suite is
  carried by this PR)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH
- owner: per-run isolated owners (JChain<run>), cleaned up after
- input_fixture_digest: suite file sha256
  763f915cb2681a28be435ae8ca87ac0076fce5342ffc367154651a493b0956ee
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_chain_test` — 16/16 PASS
  (tally line `JOURNEY_CHAIN`, printed last)
- expected_state_diff: typed Create lands; legacy Set/Get round-trips
  120; the ARGUMENT_CONFLICT atom refuses, its predecessor's effect
  (jfirst=1) stands and is reported, its successor's effect (jlast)
  never lands; the reserved 999 atom blocks its chain the same way
  (jparse never lands)
- observed_state_diff: exactly the expected diff, in-session and
  after cold reload; reloaded store = {jtempo: '120', jfirst: '1'},
  labels = [JParseOak, Journey Typed Oak, Welcome]; the refused
  Create left no idea (no ConflictA/ConflictB labels)
- refusal_class: ARGUMENT_CONFLICT (execution refusal, precedence
  order); ADDRESS_RESERVED block (999[Omega])
- persistence_generation: save executed in-session ("Session
  saved."); reload in a second process with --load
- cold_restart: YES — second REPL process; values and absences
  identical after reload
- consumer_views: REPL receipt text + persistence-loader snapshot
  (reloaded vs reloaded basis)
- test_suite: form/journey_chain_test.py (J-01 checks: 10 of the
  suite's 16, incl. shared exit/cleanup checks)
- CI run: pending — this PR's CI at the section head (see the §45
  package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (code-stage confirm)
- completion_status: **BASELINE — FULL_SCOPE_PASS** (baseline grade:
  evidence about the harness and the current program only; the
  rehearsal grade is assigned at rehearsal time, plan §5.1)
- uncovered_cases: REAL_USER_PATH not claimed (piped REPL is
  PUBLIC_ENTRY_PATH); manifest-set/chainlink chain forms not in
  this baseline's scope; Studio surface leg belongs to J-13's family
- timestamp: 2026-11-21T15:47Z

### A.2 — J-02 Refusal (family suite `form/journey_chain_test.py`)

- journey_id: J-02
- feature_scope: the four refusal classes of file 06's J-02, each
  refused before execution, session state and on-disk generation
  proven unchanged
- source_main_sha / PR/head / public_action / owner / fixture
  digest / test_suite / CI / checker / Director disposition: as A.1
- raw command/log: same suite run — the J-02 battery ran in a fresh
  isolated owner whose session contained ONLY the four refusals, a
  status read, and quit
- expected_state_diff: none — no idea created, no key set, no state
  file or generation created
- observed_state_diff: none — after the battery: ideas=1 (the
  start-of-session Welcome idea), nursery=0, and zero state files
  exist for the owner
- refusal_class: unknown Dell 500 (unsupported address); duplicate
  role 'name' (malformed role); aggregate Dell conflict (ambiguous
  identifier — aggregate/atom form); Dell 151 reserved/not-active
  refused (unauthorized mutation — reserved-address execution
  attempt; DC-8 documented refusal). Every refusal names its source
  (address, role, or form) — no source/identity detail hidden.
- persistence_generation: none created (the proof)
- cold_restart: n/a (no state was written; nothing to reload)
- consumer_views: REPL session output only — by design: no PP3/GUI
  substitute was involved on this path
- completion_status: **BASELINE — FULL_SCOPE_PASS** (same baseline
  caveat as A.1)
- uncovered_cases: a literal cross-owner mutation attempt is J-18's
  family (journey_exchange_test.py), not J-02's; the unauthorized
  case here is the reserved-address execution attempt, stated openly
- timestamp: 2026-11-21T15:47Z

### A.3 — J-03 English → LatinMandell (family suite `form/journey_language_test.py`)

- journey_id: J-03
- feature_scope: a documented supported English action end to end —
  recognized intent and typed roles, LM stage / translation basis,
  Mandell seed, exact executed operation; the file 06 failure oracle
  (long admissible operand whole; uncertain analysis declines; no
  fabricated fallback Show; truthful source labels on the offline
  deterministic path)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ a65f498db054bc5765abbebda8ac52324d0883ae
  (baseline run executed before this section's commit; the suite and
  the one-line product fix below are carried by this PR)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH
- owner: per-run isolated owners (JLang<run>, JDecline<run>),
  cleaned up after; the isolation boundary is proven in-suite (no
  state files exist for either owner before the sessions start)
- input_fixture_digest: suite file sha256
  9ab6404827ab638c8749a5b1240ecc9335e8734448527c15f0743563ac08e687
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_language_test` —
  failing-first spec run 17/19 (only the two long-operand checks
  failing, for the reason below); after the fix, **19/19 PASS**
  (tally line `JOURNEY_LANGUAGE`, printed last)
- expected_state_diff: the `mandell` door shows the seed
  `08[Create](name="Seed Probe") > 15[Map] :: Seed_Probe` and
  executes nothing; `create an idea called Journey Language Oak`
  lands exactly that idea, its LM trace naming the intent basis
  (curated governs: Dell 08), the operands typed as user data
  (traced, not routed), and the spine labeled a projection;
  `grow ideas 1` executes Dell 13 with the full route receipt
  (ARGUMENTS cycles=1); the 189-char long-operand idea lands with
  its label whole; both declines change no state
- observed_state_diff: exactly the expected diff, in-session and
  after cold reload; reloaded labels = [Journey Language Oak,
  JourneyLongOperand <160 x's> ZzEndmark (whole, 189 chars),
  Welcome]; the decline owner's session shows ideas=1, nursery=0,
  and no state file was ever created for it
- refusal_class: NOT_UNDERSTOOD decline (uncertain analysis —
  gibberish input, no intent fabricated; the unknown intent's seed
  echo `09[Show] :: unknown` is a labeled translation artifact, NOT
  an executed Show — no Dell executed, no state changed);
  AMBIGUITY decline (bare `restore`: checkpoint vs session reading,
  genuinely ambiguous, not guessed — `Restore unavailable:`,
  nothing executed)
- persistence_generation: save executed in-session ("Session
  saved."); reload in a second process with --load
- cold_restart: YES — second REPL process; labels and counts
  identical after reload
- consumer_views: REPL receipt text (route receipt + LM-4
  decomposition trace) + persistence-loader snapshot (reloaded vs
  reloaded basis)
- test_suite: form/journey_language_test.py (19 checks; J-03 is the
  family's only journey)
- DEFECT FOUND AND FIXED IN THIS SECTION: the long-operand oracle
  point failed at baseline — `form/idea_create.py`
  `parse_create_line` carried `"label": label[:80]`, silently
  cutting an admissible 189-char operand's stored label at exactly
  80 chars (tail and end marker lost, no provenance, no refusal).
  Mechanism: REPL create door → `dell_matrix/needs.parse_and_place`
  → `parse_create_line` → `Program.place` (the cut label is the
  stored unit label). Fix: the label is stored whole (one line;
  the canonical 40-char `slug_id` address cap is a separate,
  disclosed constraint and is unchanged). Neighbor suites after
  the fix: idea_create smoke 4/4, d1_dell8_create 21/21,
  p3_wiring 26/26, journey_chain 16/16. Sibling cuts in the same
  function (`detail[:2000]`, `goals[:12]`, and the `words`
  detail[:120] at line 33) were observed and NOT touched here —
  the words-cap provenance item already belongs to Part I's
  FI-012 remediation wave (PR #507 matrix); the J-03 operand is
  the label.
- CI run: pending — this PR's CI at the section head (see the §45
  package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (code-stage confirm)
- completion_status: **BASELINE — FULL_SCOPE_PASS** (baseline grade:
  evidence about the harness and the current program only; the
  rehearsal grade is assigned at rehearsal time, plan §5.1)
- uncovered_cases: REAL_USER_PATH not claimed (piped REPL is
  PUBLIC_ENTRY_PATH); no dock was connected on this path — the
  dock-optional label evidence is the offline deterministic path's
  own labels (curated LM basis; spine labeled projection); the
  docked path itself is J-10's family; LatinMandell `la` door
  exercised in probes (translates and executes with `english:` /
  `mandel:` source labels) but not pinned in this baseline suite
- timestamp: 2026-11-21T20:33Z

### A.4 — J-04 Create/persist Idea (family suite `form/journey_idea_lifecycle_test.py`)

- journey_id: J-04
- feature_scope: create an Idea with detail/goals at the public
  door — stable canonical ID, chosen position — then cold reload
  with all text/provenance/links identical; the file 06 failure
  oracle (invalid Unicode, 5000 words limit, idempotent retry;
  the interrupted pair-save clause is graded below)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ e434797206a930eacfc28d33e69a1f5bc8b84edd
  (baseline run executed before this section's commit; the suite
  and the product fix below are carried by this PR)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH
- owner: per-run isolated owners (JLife<run>, JLong<run> for this
  packet), cleaned up after; the isolation boundary is proven
  in-suite (no state files exist for any of the family's five
  owners before the sessions start)
- input_fixture_digest: suite file sha256
  bea0567993af62d37d0ab4fa406433612eb73fd45eb9bdf608dd324069339e97
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_idea_lifecycle_test` —
  failing-first run 29/34 (only the five long-text checks failing,
  for the reason below); after the fix, **34/34 PASS** (tally line
  `JOURNEY_IDEA_LIFECYCLE`, printed last; this packet covers the
  11 J-04 checks)
- expected_state_diff: the strong create lands `Lifecycle Oak`
  under canonical id `lifecycle_oak` with its detail/goals whole
  and the spatial authority's chosen position; the Unicode unit
  (accented Latin + CJK + emoji label, combining-mark detail)
  stores byte-exact; reissuing the create mints the canonical
  suffixed `lifecycle_oak_1` and leaves the first unit untouched
  (P3/TD-5 dedup — the door's explicit retry behavior); `save`
  issued twice converges (two receipts, reloaded state identical,
  no duplicate, no hybrid); a 5,000-word detail and 13 goals
  store whole
- observed_state_diff: exactly the expected diff, in-session and
  after cold reload (loader snapshot before/after reload equal
  on id, label, detail, goals, words, position, idea binding)
- refusal_class: none exercised on this journey's happy path; the
  oracle's refusal-shaped point (interrupted pair-save) is graded
  below, not silently passed
- persistence_generation: save executed in-session, twice
  ("Session saved." x2); reload in a second process with --load
- cold_restart: YES — second REPL process; full loader snapshot
  identical after reload, including the 31,009-char detail
- consumer_views: REPL create receipt + idea view +
  persistence-loader snapshot (reloaded vs reloaded basis)
- test_suite: form/journey_idea_lifecycle_test.py (34 checks
  across J-04/J-16/J-17, plus the shared isolation and cleanup
  checks; 11 are J-04's)
- DEFECT FOUND AND FIXED IN THIS SECTION: the 5000-words oracle
  point failed at baseline — `form/idea_create.py`
  `parse_create_line` carried `"detail": detail[:2000]` and
  `"goals": goals[:12]`, silently cutting a 5,000-word admissible
  detail at exactly 2,000 chars (tail and end marker lost) and
  dropping a 13th goal, no provenance, no refusal. Mechanism:
  REPL create door → `needs.parse_and_place` →
  `parse_create_line` → `Program.place`. Fix: detail and goals
  are stored whole (the SYS-C29 family contract: admitted
  content byte-exact or refused typed before mutation). The
  sibling edit-door cut (`needs.set_detail` `[:2000]`) is fixed
  under J-17 below. Observed siblings NOT touched here:
  `needs.set_goals`' parts[:12] (no journey in this family edits
  goals) and the `words` summary field's detail[:120] (the words
  contract is Part I's FI-012 remediation item, PR #507 matrix;
  this suite checks words for persistence fidelity only).
  Neighbor suites after the fix: journey_chain 16/16,
  journey_language 19/19, d1_dell8_create 21/21,
  undo_redo_depth 53/53, set_detail_goals 7/7, idea_create
  smoke 4/4, needs smoke 10/10. Mutant control: the create-door
  detail cut reintroduced by inverse edit on the fixed tree →
  33/34, failing exactly `j04_long_detail_stored_whole`;
  reverted by inverse edit, suite back to 34/34.
- CI run: pending — this PR's CI at the section head (see the §45
  package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (code-stage confirm; PR #502 is
  under the Director MERGE HOLD 7068847023 — new-section code
  review pending; this section builds under the standing Part
  workflow, no merge sought)
- completion_status: **BASELINE — PARTIAL_SCOPE** (baseline
  grade: evidence about the harness and the current program
  only; the rehearsal grade is assigned at rehearsal time,
  plan §5.1). Executed scope: create/persist with detail/goals,
  canonical ID, chosen position, Unicode round-trip, the
  5000-words limit point, save-retry idempotency, cold-reload
  identity. The one oracle clause not executed is named below.
- uncovered_cases: literal mid-save interruption injection
  (kill during the pair-save) is NOT executed in this family —
  crash injection at each save phase is J-12's family
  (journey_crash_test.py); the coherent-pair behavior it
  protects is evidenced here by save-retry convergence and
  byte-identical reload, and J-04 is graded PARTIAL_SCOPE for
  exactly this gap; invalid Unicode in the strict byte sense
  (undecodable bytes) cannot traverse the text REPL door — the
  suite exercises non-ASCII, combining-mark, CJK and emoji
  content byte-exact; REAL_USER_PATH not claimed (piped REPL is
  PUBLIC_ENTRY_PATH); the position is the spatial authority's
  chosen placement at this door (explicit x/y exists at the
  Program.place API level, not on the English create door) —
  what is proven is the chosen position's persistence
- timestamp: 2026-11-21T20:59Z

### A.5 — J-16 Nested Idea → promote (family suite `form/journey_idea_lifecycle_test.py`)

- journey_id: J-16
- feature_scope: the plan §5.2.1 designed oracle — create a
  nested Idea via the public path, promote to top-level;
  association/lineage preserved, old history intact after cold
  reload, stable canonical ID unchanged; negative: promotion by
  a non-owner refuses
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ e434797206a930eacfc28d33e69a1f5bc8b84edd
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH;
  containment door (`nest` / `promote` / `containment`, ID refs)
- owner: per-run isolated owners (JNest<run>, JForeign<run>),
  cleaned up after; isolation boundary proven in-suite
- input_fixture_digest: suite file sha256
  bea0567993af62d37d0ab4fa406433612eb73fd45eb9bdf608dd324069339e97
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_idea_lifecycle_test`
  — **34/34 PASS** (this packet covers the 11 J-16 checks; no
  J-16 check failed at baseline — no product defect found on
  this journey)
- expected_state_diff: `nest child_lifecycle under
  parent_lifecycle` binds both units to canonical Idea IDs and
  records the CONTAINS edge; the containment view shows path
  "Parent Lifecycle > Child Lifecycle" and the parent's
  children; `promote child_lifecycle` supersedes the edge and
  the path becomes the child itself; a second promote is an
  honest no-op ("Already top level"); unit IDs and Idea IDs
  unchanged throughout and after cold reload
- observed_state_diff: exactly the expected diff; after reload
  the SemanticGraph log for the pair holds the ACTIVE entry and
  its SUPERSEDED successor under one rel_id, the folded current
  parent is None, and the public containment view in a fresh
  process still shows the child at top level
- refusal_class: NON-OWNER refusal — a foreign owner's REPL
  answers `Containment refused (unit_not_found): no unit with
  id or label 'child_lifecycle'`; the attempt created no state
  file and mutated nothing
- persistence_generation: save executed in-session ("Session
  saved."); graph log persisted by the containment mutations
  themselves; reload in a second process with --load
- cold_restart: YES — second REPL process + SemanticGraph loader
  on the persisted log
- consumer_views: REPL containment receipts + containment view +
  persistence-loader snapshot + SemanticGraph loader (the
  canonical relationship authority's own log)
- test_suite: form/journey_idea_lifecycle_test.py (11 J-16
  checks)
- CI run: pending — this PR's CI at the section head (see the
  §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (as A.4)
- completion_status: **BASELINE — PARTIAL_SCOPE** (baseline
  grade, as A.4). Executed scope: nest, promote, lineage and
  history after cold reload, stable canonical IDs, the
  non-owner negative, the already-top-level honesty point.
- uncovered_cases: the wall-breaking negative (promotion/nest
  that would break a sandbox wall refuses with receipt —
  the mechanism's `sandbox_boundary` kind, TD7) is NOT
  executed: no public REPL path in this baseline scope mints
  a sandboxed unit to attempt the crossing with, and J-16 is
  graded PARTIAL_SCOPE for exactly this gap; REAL_USER_PATH
  not claimed
- timestamp: 2026-11-21T20:59Z

### A.6 — J-17 Undo/redo across the save/session boundary (family suite `form/journey_idea_lifecycle_test.py`)

- journey_id: J-17
- feature_scope: the plan §5.2.1 designed oracle — create + edit
  an Idea and its detail, undo/redo within the session, save,
  cold reload, and verify the exact retained history the Q-LC.1
  contract promises (Q-LC.1's settled credit is session-local)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ e434797206a930eacfc28d33e69a1f5bc8b84edd
  (baseline run executed before this section's commit; the
  suite and the edit-door fix below are carried by this PR)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH
- owner: per-run isolated owner (JUndo<run>), cleaned up after;
  isolation boundary proven in-suite
- input_fixture_digest: suite file sha256
  bea0567993af62d37d0ab4fa406433612eb73fd45eb9bdf608dd324069339e97
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_idea_lifecycle_test` —
  the three long-edit checks failed at baseline (reason below);
  after the fix, **34/34 PASS** (this packet covers the 10
  J-17 checks)
- expected_state_diff: create pushes a place action; `set detail
  undo_oak revised detail text` applies and pushes an edit;
  `undo` restores the original detail ("Restored detail on
  undo_oak"); `redo` re-applies it; `undo depth` names the
  ruled default 30 over the session action history; a final
  >2,000-char edit applies whole; save persists exactly that
  state under the same canonical ID; the undo/redo evidence
  notes (24[Unlock]) persist in program history; after cold
  reload the stacks are honestly empty ("nothing to undo" /
  "nothing to redo") and the state is byte-identical to the
  saved state
- observed_state_diff: exactly the expected diff at every step,
  in-session (public idea view) and after cold reload (loader
  snapshot equal to the post-save snapshot)
- refusal_class: BOUNDARY honesty — the reloaded session's
  undo/redo answer explicit "nothing to undo" / "nothing to
  redo" refusals with hints; no stack is silently reconstructed
  across the boundary (the action/redo stacks are not persisted;
  `undo_depth` the setting is, and persists)
- persistence_generation: save executed in-session ("Session
  saved."); reload in a second process with --load
- cold_restart: YES — second REPL process; state identical,
  stacks empty, evidence notes retained
- consumer_views: REPL receipts + idea view + undo-depth surface
  + persistence-loader snapshot (incl. persisted program
  history)
- test_suite: form/journey_idea_lifecycle_test.py (10 J-17
  checks)
- DEFECT FOUND AND FIXED IN THIS SECTION: the edit door's
  sibling of the J-04 cut — `form/dell_matrix/needs.py`
  `set_detail` carried `u.detail = (detail or "").strip()[:2000]`,
  silently truncating a >2,000-char edited detail (end marker
  lost) with no provenance or refusal. Fix: the edited detail
  is stored whole. Neighbors and mutant as A.4.
- CI run: pending — this PR's CI at the section head (see the
  §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (as A.4)
- completion_status: **BASELINE — FULL_SCOPE_PASS** (baseline
  grade: evidence about the harness and the current program
  only). Every step of the plan §5.2.1 oracle has executable
  public-path proof at this head: create + edit, in-session
  undo/redo, save, cold reload, and the exact Q-LC.1 retention
  (state + evidence notes persist; stacks do not).
- uncovered_cases: the room/multi-actor remainder (register
  row #135's retained scope) is explicitly uncovered, per the
  plan oracle's own scope-honesty clause — not a silent pass;
  the Core II snapshot stack is a separate authority and is
  not exercised here (the undo-depth surface names the
  separation); undo of a place and redo-of-place restoration
  are covered by form/mandell/undo_redo_depth_test.py (53/53)
  and are not re-exercised at the public path in this baseline;
  REAL_USER_PATH not claimed
- timestamp: 2026-11-21T20:59Z

### A.7 — J-05 Human confirm (family suite `form/journey_confirm_test.py`)

- journey_id: J-05
- feature_scope: the file 06 oracle executed verbatim — create a
  pending cross-Idea candidate, inspect reason and source,
  manually confirm; the unit appears with inherited wall or
  explicitly selected mixed-parent wall; the failure oracle
  (rejected remains non-live; stale proposal ID/conflicting
  generation refuses; actor-supplied text is not authentication;
  auto-confirm stays sandbox-first only where already permitted)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ 3ab62f41368c0ac8aa18e1d189fe20ec461518a0
  (baseline run executed before this section's commit; the suite
  is carried by this PR)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH
- owner: per-run isolated owners (JConf<run>, JWall<run>,
  JMixed<run>, JOutside<run>, JActor<run>, JAuto<run>,
  JAutoMix<run> for this packet), cleaned up after; the
  isolation boundary is proven in-suite (no state files exist
  for any of the family's eight owners before the sessions start)
- input_fixture_digest: suite file sha256
  7aa4b9978c5624390c6f7b07e48b6eb83ed861810ce818c44f1abb211e4b2376
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_confirm_test` —
  **38/38 PASS** (tally line `JOURNEY_CONFIRM`, printed last;
  this packet covers the 26 J-05 checks; expectations were
  grounded in scratch-owner probes run before the suite was
  written, and the suite passed its first full run — no product
  defect was exposed by this journey; the one observation is
  recorded as a finding below, not a fix)
- expected_state_diff: `grow ideas` over two word-sharing ideas
  yields the [new] cross-Idea candidate with origin
  growth:token and its Solstice reason on the review face;
  manual confirm places the unit under the proposal's ID with
  both parents as lineage and origin "confirmed"; same-wall
  parents (both grouped before growth) → the unit inherits the
  wall (unit flags AND box member_ids, the canonical pair);
  a parent grouped after the proposal exists → bare confirm
  refuses placement_choice_required with the choice prompt, and
  the explicit `in <box>` / `outside` choices land it in the
  chosen wall / on the open field; reject leaves the proposal
  rejected and never a unit; the auto-confirm sweep (explicit
  opt-in) stages every eligible proposal into auto_staging and
  skips the mixed-wall candidate
- observed_state_diff: exactly the expected diff, in-session and
  after cold reload (loader snapshots equal before/after reload
  for the confirm and same-wall journeys, statuses included)
- refusal_class: STALE_ID ("not found or not pending" —
  confirm-after-confirm, confirm-after-reject,
  reject-after-reject, unknown ID, and the same stale confirm
  repeated after cold reload); PLACEMENT_CHOICE_REQUIRED
  (mixed-wall bare confirm, with the lawful choices named);
  INVALID_PLACEMENT_CHOICE (a real non-parent box and a
  nonexistent box both refuse — a caller can never name an
  arbitrary box); MISSING_PARENT (confirm whose parents are
  absent from the loaded program refuses fail-closed — observed
  in probes when a nursery outlives an unsaved program; correct
  behavior, recorded here because the probes exposed it)
- persistence_generation: save executed in-session ("Session
  saved."); reload in second processes with --load
- cold_restart: YES — second/third REPL processes; statuses,
  units, walls and memberships identical after reload, and the
  stale confirm refuses identically after reload
- consumer_views: REPL proposals view (origin + reason on the
  review face), `lineage <pid>`, `proposals get <pid>`, idea
  view, group views + persistence-loader snapshot (units,
  boxes/member_ids, proposal statuses, program history)
- test_suite: form/journey_confirm_test.py (38 checks across
  J-05/J-21, plus the shared isolation and cleanup checks; 26
  are J-05's)
- FINDING RECORDED, NOT FIXED HERE (receipt freshness at the
  grow door): the Dell-13 route receipt for `grow ideas` prints
  the growth stage's nursery snapshot ("Nursery pending: 3")
  even when the auto-confirm sweep inside the same grow_ideas
  call has already confirmed every proposal. grow_ideas' own
  result carries the correct post-sweep count
  (result["nursery_pending"]), and the proposals view, status
  and the loader reconcile in the same session — the stale
  figure is confined to that one receipt line, and no J-05
  oracle point reads it. Not a confirm-path defect; recorded
  for the growth-receipt owner. FI-011 overlap check (Part I's
  remediation wave on PR #508 owns A7 replay receipts, A8 raw
  Nursery.confirm without actor/grant/receipt, A12 origin-blind
  auto-confirm): NONE of A7/A8/A12 is exposed at the public path
  by this journey — the REPL confirm door is policy-mediated
  end to end (dispatch-fixed producer "repl_user", session
  review context, writer revalidation, placement law), the
  sweep is opt-in-only and mixed-wall-noneligible, and replay
  of a confirm refuses as stale. No confirm-path fix is made
  on this branch.
- Mutant control: the placement-choice gate in
  confirm_lineage._resolve_confirm_placement mutated (a
  mixed-wall confirm without a choice silently places into the
  first wall key) → 34/38, failing exactly the four mixed-wall
  checks (requires-choice, stays-pending, invalid-choices,
  in-box placement); reverted by inverse edit, suite back to
  38/38, worktree diff verified clean of the mutant.
- CI run: pending — this PR's CI at the section head (see the
  §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (code-stage confirm; PR #502 is
  under the Director MERGE HOLD 7068847023 — new-section code
  review pending; this section builds under the standing Part
  workflow, no merge sought)
- completion_status: **BASELINE — FULL_SCOPE_PASS** (baseline
  grade: evidence about the harness and the current program
  only; the rehearsal grade is assigned at rehearsal time,
  plan §5.1). Every file 06 oracle point has executable
  public-path proof at this head: cross-Idea candidate created
  pending, reason/source inspected, manual confirm, inherited
  wall, explicitly selected mixed-parent wall (both choices),
  rejected non-live, stale-ID refusals (incl. after reload),
  actor-supplied text not authentication, auto-confirm
  sandbox-first under opt-in with mixed-wall non-eligibility.
- uncovered_cases: the "conflicting generation" clause at the
  durable-file level (NurseryConflictError on a stale store
  generation) is evidenced at the API level by
  form/confirm_placement_test.py T18 (generation race) and
  form/nursery_confirm_race_test.py, not re-exercised at the
  public path here — the public-path stale cases (double
  confirm, post-reject, post-reload) are this packet's proof;
  a docked (agent-origin) proposal's human confirm is J-10's
  family (no dock connected at baseline); REAL_USER_PATH not
  claimed (piped REPL is PUBLIC_ENTRY_PATH)
- timestamp: 2026-11-21T21:17Z

### A.8 — J-21 Visual Nursery at scale (family suite `form/journey_confirm_test.py`)

- journey_id: J-21
- feature_scope: the plan §5.2.1 designed oracle — seed a large
  proposal set (1,000 proposals), browse with shown/total on
  every view, confirm and reject through the visual path;
  counts reconcile exactly with the store after cold reload;
  the docked organizer clause is graded below
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ 3ab62f41368c0ac8aa18e1d189fe20ec461518a0
  (baseline run executed before this section's commit; the suite
  is carried by this PR)
- public_action: literal `python3 -m form.repl --owner <isolated>`
  subprocess sessions (piped stdin) — PUBLIC_ENTRY_PATH for
  every journey action (browse, search, get, confirm, reject)
- owner: per-run isolated owner (JScale<run>), cleaned up after;
  the isolation boundary is proven in-suite
- input_fixture_digest: suite file sha256 as A.7; the seeded
  fixture's own digest (sha256 over pid|label|words in creation
  order, first 16 hex) printed by the suite: 2dbccede7779ca82
  for the recorded run (IDs are deterministic given the fixture
  strings; the digest is per-run evidence, recomputed each run)
- fixture note (disclosed): the plan's own word for the setup is
  "seed" — the 1,000 proposals are added through the canonical
  Nursery.add door (the same door growth uses; origin
  "suite:seeded", parentless), with the per-add saves batched
  into one canonical save at the end. Every stored record is
  add()'s own (validation, bounds, seed-rule metadata); only
  the save cadence is batched. Seeding is fixture setup, not a
  journey action; all journey actions run at the public path.
- raw command/log: `python3 -m form.journey_confirm_test` —
  **38/38 PASS** (tally line `JOURNEY_CONFIRM`, printed last;
  this packet covers the 10 J-21 checks)
- expected_state_diff: the store holds exactly 1,000 pending
  proposals; the plain proposals face states "showing 20 of
  1000"; browse headers state shown/total_matches/
  total_searched/total_inventory on every page; five size:200
  cursor pages walk the whole set (shown sums to 1,000, each
  page's item lines count equals its shown figure) and end at
  end-of-results; search states its totals (unique term 1 of 1,
  common term 50 of 1000 on the default page); an over-max page
  size (500) refuses typed; three confirms and two rejects at
  the public path move the store to 995 pending / 3 confirmed /
  2 rejected / 1,000 total, with the confirmed live and the
  rejected non-live, identical after cold reload
- observed_state_diff: exactly the expected diff, in-session,
  in the loader snapshot, and after cold reload (post-reload
  browse: status:pending total_matches 995, status:confirmed
  shown 3 of 3; loader summary and per-proposal statuses
  identical before/after reload)
- refusal_class: PAGE_SIZE_INVALID (browse size:500 — "page
  size must be an integer 1..200 (got 500); sizes are never
  silently clamped": the SEE door refuses typed rather than
  silently clamping to SEE_MAX_PAGE)
- persistence_generation: fixture save + in-session "Session
  saved." after the decisions; reload in further processes
  with --load
- cold_restart: YES — the reconciliation session and the loader
  snapshots are post-reload
- consumer_views: REPL proposals face, SEE browse/search pages
  (headers + item lines), status-filtered browse +
  persistence-loader snapshot (summary + per-proposal statuses
  + units)
- test_suite: form/journey_confirm_test.py (38 checks across
  J-05/J-21, plus the shared isolation and cleanup checks; 10
  are J-21's)
- CI run: pending — this PR's CI at the section head (see the
  §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (as A.7)
- completion_status: **BASELINE — FULL_SCOPE_PASS** (baseline
  grade: evidence about the harness and the current program
  only). Every executed oracle step has public-path proof at
  this head: 1,000-proposal set, shown/total on every view
  exercised, full cursor walk reconciling to the store,
  confirm/reject through the path, exact post-reload
  reconciliation.
- uncovered_cases: the docked-organizer clause ("if present,
  proposes only PENDING suggestions") is NOT exercised — no
  dock is connected at baseline; the clause's condition is
  unmet, and dock behavior is J-10's family
  (journey_dock_test.py); the Studio visual surface is J-13's
  family — at baseline the "visual path" is the REPL's
  proposals/SEE views, the consumer views this suite exercises;
  REAL_USER_PATH not claimed (piped REPL is
  PUBLIC_ENTRY_PATH)
- timestamp: 2026-11-21T21:17Z

## Annex B — harness construction status (plan §5.2 families)

| Family suite | Journeys | Status |
|---|---|---|
| journey_chain_test.py | J-01, J-02 | BUILT — baseline 16/16 (Annex A) |
| journey_language_test.py | J-03 | BUILT — baseline 19/19 (Annex A.3; one product defect found + fixed) |
| journey_idea_lifecycle_test.py | J-04, J-16, J-17 | BUILT — baseline 34/34 (Annex A.4–A.6; two product defects found + fixed: create-door detail/goals silent cuts, edit-door detail silent cut) |
| journey_confirm_test.py | J-05, J-21 | BUILT — baseline 38/38 (Annex A.7–A.8; no product defect found; one receipt-freshness finding recorded in A.7) |
| journey_rollback_test.py | J-06 | not built |
| journey_views_test.py | J-07, J-08, J-13, J-23 | not built |
| journey_growth_test.py | J-09, J-14 | not built |
| journey_dock_test.py | J-10, J-22 | not built |
| journey_hcn_test.py | J-11 | not built (subject NOT BUILT until GP-E22 lands) |
| journey_crash_test.py | J-12 | not built |
| journey_exchange_test.py | J-18, J-19 | not built (J-19 known gap: duplicate-replay idempotency absent — the rehearsal reports the program as it is) |
| journey_offline_test.py | J-20 | not built (trace record exists from plan stage) |
| journey_index_test.py | J-15 | not built |
| journey_perf_test.py | J-24 | not built |
| journey_canary_test.py | J-25 | not built |
