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

### A.9 — J-06 Rollback (family suite `form/journey_rollback_test.py`)

- journey_id: J-06
- feature_scope: the file 06 oracle executed verbatim — seal
  named generation, make further edits, invoke authorized
  freeze/grant/confirm rollback, cold reload and compare exact
  restored scope; the failure oracle (bare rollback refuses;
  cross-owner and stale-grant refusal, injected partial
  restore, evidence remains immutable and current status not
  faked)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ af81d457f5a36ba6e5e652dae2916ddab57cfc23
  (baseline run executed before this section's commit; the
  suite is carried by this PR)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions (piped stdin) —
  PUBLIC_ENTRY_PATH for every journey action (create, Dell 27
  seal, bare restore, Dell 28 seed, restore confirm)
- owner: per-run isolated owners (JRoll<run>, JAlias<run>,
  JStale<run>, JCross<run>, JTamper<run>), cleaned up after;
  the isolation boundary is proven in-suite (no state files
  exist for any of the family's five owners before the
  sessions start)
- input_fixture_digest: suite file sha256
  b72f486140a0ecbcfaf4dcac854dfc95d505207e2ebb696c29d885e1b2b9b10e
  (inputs are fixed strings in the suite; the compensating
  generation IDs are date-stamped by the product and parsed
  from its receipts, never assumed)
- fixture note (disclosed): two fixture mechanics only — the
  tamper injection flips one byte in the sealed target's
  program member file on disk (the fault being injected; the
  rollback attempt itself runs at the public path, and the
  member's original bytes are restored in a finally block),
  and the aliasing probe compares the target's frozen member
  fingerprints through the read-only freeze door
  (freeze_rollback_target performs no writes). All journey
  actions run at the public path.
- raw command/log: `python3 -m form.journey_rollback_test` —
  **28/28 PASS** (tally line `JOURNEY_ROLLBACK`, printed
  last; expectations were grounded in scratch-owner probes
  run before the suite was written, and the suite passed its
  first full run — no product defect was exposed by this
  journey). Mutant sensitivity: disabling the freeze re-hash
  in rollback_authority.freeze_rollback_target (inverse-edit
  mutant) fails exactly j06_tampered_member_refused_at_freeze
  (27/28); reverted by inverse edit, suite back to 28/28.
- expected_state_diff: `27[Checkpoint] :: alpha_base` seals
  the named generation and CURRENT names it; further edits +
  `27[Checkpoint] :: beta_base` advance CURRENT; bare
  `restore` describes the beta_base rollback and executes
  nothing; a bare `28[Rollback]` seed is denied
  (acceptance_policy_denied, no issued approval) with zero
  mutation; `restore confirm alpha_base` prints the restored
  receipt + compensating checkpoint ID, and after cold reload
  the live scope equals the alpha_base seal-time scope
  EXACTLY (units with content fields, nursery statuses,
  boxes, history — Gamma gone, nothing of the later state
  leaking in); confirming the compensating generation undoes
  the rollback exactly; a post-rollback live mutation leaves
  the sealed generation's frozen fingerprints (four members
  + manifest) untouched, and a second rollback to the same
  target restores the exact sealed scope again (the mutation
  is gone, not merged into the seal — rollback copies the
  sealed target into independent live state, never aliases)
- observed_state_diff: exactly the expected diff, in the
  loader snapshots and after cold reload, on every leg
- refusal_class: acceptance_policy_denied (bare Dell 28 seed:
  "Producer 'dell28' has no issued approval or active
  opt-in"); RollbackTargetError surfaced at the REPL as
  "Restore denied: cannot freeze target: ..." for the pruned
  generation gen_a and the unknown gen_bogus_999
  ("unreadable"), for the cross-owner attempt (owner-
  namespaced manifests; the foreign attempt created no state
  files at all), and for the tampered target ("member
  'program' fingerprint mismatch"); bare restore with no
  committed generation answers "Restore unavailable: no
  committed generation for owner ..."
- persistence_generation: named generations alpha_base /
  beta_base, seal_one / seal_two, gen_a / gen_b / gen_c,
  vault_one / vault_two, plus the product's compensating
  (pre-rollback safety) generations; retention pruned gen_a
  once gen_c committed (CURRENT + previous kept)
- cold_restart: YES — every scope comparison is a fresh
  loader snapshot; the restored scope also survives a fresh
  `--load` REPL session unchanged
- consumer_views: REPL restore description + confirm
  receipts, Dell 27/Dell 28 route receipts, persistence-
  loader snapshot (units/nursery/boxes/history), CURRENT
  pointer (checkpoint_generation.current_generation_id),
  read-only freeze fingerprints
- test_suite: form/journey_rollback_test.py (28 checks across
  the seal/edit/rollback/undo, aliasing, stale/unknown,
  cross-owner and tamper legs, plus the shared isolation and
  cleanup checks)
- CI run: pending — this PR's CI at the section head (see the
  §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; PR #502 stands under the
  Director MERGE HOLD (7068847023), which bars merging only
- completion_status: **BASELINE — FULL_SCOPE_PASS
  (public-path scope)** (baseline grade: evidence about the
  harness and the current program only). Every oracle point
  constructible at the public entry path has public-path
  proof at this head: named seal, further edits, bare-restore
  refusal, no-grant Dell 28 denial, authorized
  freeze/grant/confirm rollback, exact restored scope after
  cold reload, compensating-checkpoint undo, the aliasing
  probe (sealed generation immutable under post-rollback
  live mutation), stale (retention-pruned) and unknown
  target refusals, cross-owner refusal, and the injected
  tamper refused at the freeze door with the status quo
  preserved and no restored status faked. Grounded behavior
  recorded: after a rollback the CURRENT pointer names the
  compensating generation (the newest committed generation)
  while live state converges to the target — a bare restore
  afterwards therefore describes the undo point.
- uncovered_cases: grant staleness proper (a grant issued,
  live state then drifting, execution denying at live
  revalidation) is NOT constructible through the REPL text
  door — issuance and execution are a single command there —
  and is exercised by the R6.3 authority circuits at API
  level (form.mandell.r63_rollback_test, green as a
  neighbor); mid-flight crash injection into a running
  rollback (the _fail_at points) is likewise API-level,
  covered by the checkpoint crash-matrix circuits — the
  injected fault exercised here is sealed-member tampering,
  refused at the freeze door before any restore step runs;
  REAL_USER_PATH not claimed (piped REPL is
  PUBLIC_ENTRY_PATH)
- timestamp: 2026-11-21T21:38Z

### A.10 — J-07 Cross-view space (family suite `form/journey_views_test.py`)

- journey_id: J-07
- feature_scope: the file 06 oracle executed verbatim where
  constructible at this head — at least two noncoincident
  Ideas created, the same typed relation drawn and inspected
  in 2D (plane table) / Flower / cube / text projections,
  distinct projection facts vs canonical graph facts; the
  failure oracle (pure visual proximity creates no semantic
  relation; same Idea IDs/status after zoom and reload)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ 5f6dcaefabaf4d7251e8c84e1dac58755f1f4beb
  (baseline run executed before this section's commit; the
  suite is carried by this PR)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions (piped stdin) —
  PUBLIC_ENTRY_PATH for every journey action (create, nest,
  show, cube, zoom/page, flower, flower geometry, vesica,
  verita, rooms)
- owner: per-run isolated owners (JView<run>, JGeom<run>,
  JMany<run>, JStudio<run>), cleaned up after; the isolation
  boundary is proven in-suite (no state files exist for any
  of the family's four owners before the sessions start)
- input_fixture_digest: suite file sha256
  2a9623a58d634fd73cb51e84ce16f9151eee0dcf1fc2da8c62d9a7c572d49390
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_views_test` —
  **29/29 PASS** for the family (J-07 checks: 11 of 29,
  incl. shared isolation/cleanup); expectations were
  grounded in scratch-owner probes run before the suite was
  written. Mutant sensitivity: removing the rooms
  overflow-disclosure line in
  view_rooms.render_room_ascii (inverse-edit mutant) fails
  exactly j07_room_overflow_disclosed (28/29); reverted by
  inverse edit, suite back to 29/29.
- expected_state_diff: four created Ideas land at distinct
  spatial-authority positions (welcome + 4 created = five
  distinct (x, y) pairs); `nest beta_stone under
  alpha_stone` adds exactly one ACTIVE contains entry
  (alpha idea_id -> beta idea_id) to the canonical graph;
  every projection (table `show`, cube-form idea page,
  Flower geometry, rooms) presents the same unit ids,
  positions and detail; view commands mutate nothing.
- observed_state_diff: exactly the expected diff, in the
  loader snapshots and after cold reload, on every leg.
  The Flower projection additionally rendered Verita edges
  for the proximate pairs welcome<->beta_stone and
  beta_stone<->gamma_stone (d=1.0), labeled
  "coherence-of-meet between ideas"; the canonical graph
  gained NO entry for either pair — projection weather
  stayed projection, graph truth stayed exactly the one
  drawn relation. The growth room, given 19 units, listed
  12 and disclosed "… +7 more".
- refusal_class: none exercised by this journey's legs
  (no refusal is in the J-07 oracle); the honest-absence
  answers (`tree`/`space`/`sync` not understood) are
  recorded under A.11/A.13.
- persistence_generation: saves executed in-session
  ("Session saved."); every comparison is a fresh loader
  snapshot in a later process (--load)
- cold_restart: YES — projections and graph compared
  across separate REPL processes after reload
- consumer_views: REPL plane table render, idea page,
  containment + lineage text views, Flower geometry /
  vesica / verita renders, view rooms, persistence-loader
  snapshot, SemanticGraph loader
- test_suite: form/journey_views_test.py (family 6;
  registered in form/regress.py LIST in the same commit)
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; PR #502 stands under the
  Director MERGE HOLD (7068847023), which bars merging only
- completion_status: **BASELINE — FULL_SCOPE_PASS
  (public-path scope)** (baseline grade: evidence about
  the harness and the current program only). Every oracle
  point constructible at the public entry path has
  public-path proof at this head: noncoincident creation,
  the drawn typed relation visible in text views and the
  canonical graph, the same facts under table/cube/Flower
  projections, proximity creating no semantic relation,
  identity/status stable across zoom, form switches and
  cold reload, and rooms shown/total disclosure.
- uncovered_cases: the oracle's pan/move leg is narrowed
  honestly — the public path offers zoom (a pan to a unit)
  but no idea-move verb preserving identity was found in
  the probed REPL surface (movement verbs move the
  avatar/viewer), so identity stability is proven across
  zoom, form switches and reload instead; geometry values
  in the renders carry coordinates and the FoL fixture's
  own parameters (rings/centers/verita/dist), while the
  fixture-assumption labeling the oracle asks of admitted
  geometry belongs to J-08's subject (A.11); REAL_USER_PATH
  not claimed (piped REPL is PUBLIC_ENTRY_PATH)
- timestamp: 2026-11-21T21:45Z

### A.11 — J-08 Tree 3D (family suite `form/journey_views_test.py`)

- journey_id: J-08
- feature_scope: the file 06 oracle — render admitted FCC
  geometry as a typed Tree L1 view and compare rendered
  centers, shells, slices, occupancy and UI scale to
  deterministic fixtures; the failure oracle (before
  Director admission show RESEARCH/PROJECTION only;
  unproven geometry does not alter the kernel; guard
  missing inputs)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 5f6dcaefabaf4d7251e8c84e1dac58755f1f4beb
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl` subprocess
  sessions — PUBLIC_ENTRY_PATH (flower geometry, vesica,
  geometry, lattice, shell, chord, tree probe)
- owner: per-run isolated owners (JGeom<run>, JView<run>),
  cleaned up after; isolation boundary proven in-suite
- input_fixture_digest: suite file sha256
  2a9623a58d634fd73cb51e84ce16f9151eee0dcf1fc2da8c62d9a7c572d49390
- raw command/log: `python3 -m form.journey_views_test` —
  29/29 PASS for the family (J-08 checks: 4 of 29)
- expected_state_diff: NONE — the journey's subject does
  not exist at this head; the expected baseline outcome is
  an honest absence plus a geometry layer that labels
  itself projection and mutates nothing.
- observed_state_diff: exactly that. No FCC geometry and
  no Tree L1 view exists under form/ or gui/ at this head
  (repository search: no FCC, face-centered, Tree L1 or
  tree-render surface — GP-E18 unlanded, #420 independent
  proof outstanding), and the REPL answers `tree` with
  "Not understood" rather than faking a surface. The
  geometry surfaces that DO exist behave per the failure
  oracle's spirit: the sacred-geometry layer labels its
  outputs "Vesica/Verita is coherence-of-meet · Voynich
  rings are organizational · Fractals are deterministic
  pattern tools"; on an owner with no nearby ideas the
  Flower reports "Verita edges=0" with the honest hint
  "(place nearby ideas or grow scores to form vesica
  meets)"; and a full geometry battery (lattice, shell 0,
  chord 0 0, flower geometry, geometry) changed no unit,
  no nursery state and no graph entry — unproven geometry
  does not alter the kernel.
- refusal_class: honest absence ("Not understood") — no
  fabricated surface, no refusal faked as a render
- persistence_generation: saves executed in-session;
  kernel-invariance compared on fresh loader snapshots
- cold_restart: YES — battery run in a --load process
  against the sealed-by-save state
- consumer_views: REPL geometry renders, harmonic lattice
  render, persistence-loader snapshot, SemanticGraph
  loader (empty)
- test_suite: form/journey_views_test.py (family 6)
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **NOT BUILT at baseline** — a
  finding, not a harness failure (plan §5.1(iii)): the
  admitted-FCC Tree L1 subject (GP-E18, #420) has not
  landed, so no rendered-centers/shells/slices/occupancy
  comparison is constructible. The suite's J-08 checks
  pin the baseline contract durably: any future Tree
  surface that answers without RESEARCH/PROJECTION
  labeling fails j08_tree_fcc_surface_projection_labeled_
  or_absent, and the projection-honesty / missing-input /
  no-kernel-mutation legs stand as regression evidence
  for the geometry layer that exists today.
- uncovered_cases: the entire admitted-geometry
  comparison (centers, shells, slices, occupancy, UI
  scale vs deterministic fixtures) awaits GP-E18 +
  Director admission; L3 idea-radius and HCP variant are
  unproven and, per this baseline's evidence, currently
  alter nothing
- timestamp: 2026-11-21T21:45Z

### A.12 — J-13 Studio coherence (family suite `form/journey_views_test.py`)

- journey_id: J-13
- feature_scope: the file 06 oracle — navigate the public
  pages/perspectives, edit an approved idea in one, verify
  refreshed same canonical truth in the other views and
  REPL; the failure oracle (empty/plantless Idea truthfully
  represented; stale token, bad Origin, interrupted load;
  no phantom live nodes)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 5f6dcaefabaf4d7251e8c84e1dac58755f1f4beb
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl` subprocess
  sessions AND the real Studio HTTP server
  (`python3 -m gui.server --owner <isolated> --port
  <ephemeral>`) driven over HTTP with its own client
  protocol (session token served inside the index page) —
  PUBLIC_ENTRY_PATH; the Studio/API surface is the plan's
  named surface for a surface journey (§5.2)
- owner: per-run isolated owners (JView<run>, JMany<run>,
  JStudio<run>), cleaned up after; isolation proven
  in-suite; the Studio server subprocess is terminated
  before cleanup
- input_fixture_digest: suite file sha256
  2a9623a58d634fd73cb51e84ce16f9151eee0dcf1fc2da8c62d9a7c572d49390
- raw command/log: `python3 -m form.journey_views_test` —
  29/29 PASS for the family (J-13 checks: 10 of 29)
- expected_state_diff: an edit made once at the REPL
  (set detail) is the same truth in the receipt, the idea
  page and the cold loader, with identity and position
  preserved; pending Nursery proposals never appear as
  live nodes in any projection; inside the Studio surface,
  an executed seed's effect round-trips through /api/state
  for its owner only.
- observed_state_diff: exactly the expected diff on every
  constructible leg. REPL legs: the edit receipt, idea
  page and loader agree; growth left 10 proposals pending
  and the plane projection still showed exactly the 5
  live units, no pending id rendered as a node; the bare
  Pebble (no detail, no goals) is stored and rendered as
  empty — nothing fabricated (A.10). Studio legs: index
  200 with wordmark + per-launch token; /api/dells =
  exactly the canonical 100; POST without token 401,
  stale token 401, valid token + foreign Origin 403;
  `55[Set] :: tempo=120` executed and tempo=120 /
  store_count=1 read back from a fresh /api/state; a
  foreign owner's state was empty and the first owner's
  intact on return; /api/growth served the server
  program's canonical nodes with stage=None /
  stage_source="unplanted" for the unplanted node — no
  fabricated stage.
- FINDING 1 (cross-surface gap, mechanism named): the
  Studio server opens its program via
  gui.server._get_program -> form.open.open_program,
  which constructs a fresh Program and never consults the
  persisted pair (form.persist.load is the REPL --load
  door; the server never calls it). REPL-created Ideas
  saved to disk therefore do NOT appear in the Studio's
  /api/growth nodes at this head, so the oracle's
  edit-in-one-surface / verify-in-the-other leg across
  the REPL<->Studio boundary is NOT BUILT at baseline.
  This is the GP-E24/E25 windowed-workspace scope (Part
  0, in flight on PR #510), recorded here as a finding
  for that scope — not repaired from Part VII's harness
  PR, and no suite check asserts the gap as desired
  behavior.
- FINDING 2 (DAF-09 D1, exercised at the public path,
  recorded precisely for its home circuit): with 19 true
  history notes (loader count), the REPL `history` view
  lists the last 16 entries truthfully (the listed tail
  matches the loader tail exactly — asserted in-suite)
  but its header prints "History · 16 notes (last 16
  shown)" (form/dell_matrix/needs.py history_report):
  the shown window's size is presented as the note count
  and the true total (19) never appears — the shown/total
  conflation named as DAF-09 defect D1. NOT fixed here:
  the family 6 oracles do not name the history view and
  D1 is a post-completion item with its own circuit; the
  reproduction (19 total vs "16 notes" header, public
  path, this head) is the precise record that circuit
  needs.
- refusal_class: Studio HTTP refusals — 401 "missing or
  invalid session token" (absent and stale token), 403
  "origin not allowed" (foreign Origin with valid token)
- persistence_generation: REPL saves in-session; Studio
  state is the server program's live state (no save door
  exercised — see Finding 1)
- cold_restart: YES for the REPL legs (loader-compared
  across processes); the Studio legs compare the execute
  response against a fresh HTTP read of the same live
  server state
- consumer_views: REPL idea page + plane render +
  containment/lineage, Studio index page, /api/dells,
  /api/state, /api/growth, persistence loader
- test_suite: form/journey_views_test.py (family 6)
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **BASELINE — PARTIAL_SCOPE**
  (baseline grade). Proven at this head: within-REPL
  cross-view coherence of an edit; empty-Idea truthful
  representation; no phantom live nodes; Studio
  token/Origin security legs; Studio within-surface
  execute<->state coherence and owner isolation; honest
  stage attribution in the growth lens. Not proven /
  not built: the five-public-pages navigation (the
  GP-E24/E25 pages do not exist at this head; the
  Studio at this head is a single-page surface),
  REPL<->Studio canonical-truth coherence (Finding 1),
  and the browser-tier legs below.
- uncovered_cases: five-pages web navigation,
  interrupted load, screen-reader/keyboard and narrow
  viewport are browser-surface acts
  (gui/browser_acceptance.py territory), not
  constructible from this harness's REPL/HTTP tier;
  REAL_USER_PATH not claimed
- timestamp: 2026-11-21T21:45Z

### A.13 — J-23 Plan-change sync into Muse Space (family suite `form/journey_views_test.py`)

- journey_id: J-23
- feature_scope: the plan §5.2.1 designed oracle — change
  the plan record, sync; the Space shows the new state
  with provenance, and a stale mirror is labeled stale,
  never presented as current truth
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 5f6dcaefabaf4d7251e8c84e1dac58755f1f4beb
  (baseline run executed before this section's commit)
- public_action: dynamic surface probe from the suite
  (import of form.muse_space_snapshot /
  form.muse_space_views) plus the REPL absence answers
  recorded under A.11 — no sync action exists to execute
  at this head
- owner: n/a (no state touched by this journey's probe;
  the family's owners are recorded in A.10)
- input_fixture_digest: suite file sha256
  2a9623a58d634fd73cb51e84ce16f9151eee0dcf1fc2da8c62d9a7c572d49390
- raw command/log: `python3 -m form.journey_views_test` —
  29/29 PASS for the family (J-23 checks: 1 of 29 — the
  dynamic provenance-contract-or-absent probe)
- expected_state_diff: NONE at baseline — the subject
  does not exist on this branch; the expected outcome is
  an honest absence with no surface claiming a sync.
- observed_state_diff: exactly that. No form.muse_space_*
  module exists on this branch (repository search across
  form/ and gui/: zero hits) and no public surface claims
  a plan sync (the REPL answers `sync` / `space` as not
  understood). GP-E25 — the Muse Space snapshot/views
  build that is this journey's subject — was placed under
  Part 0 by Director ruling and is built on PR #510,
  unmerged; nothing on this head presents a plan mirror,
  stale or otherwise.
- refusal_class: honest absence ("Not understood") — no
  fake sync surface
- persistence_generation: n/a (no state touched)
- cold_restart: n/a at baseline
- consumer_views: none exist for this journey at this
  head
- test_suite: form/journey_views_test.py (family 6) —
  the probe is dynamic: when a future head provides the
  Muse Space modules, the same check requires the
  snapshot code to carry provenance and staleness
  handling before any sync claim is accepted, and the
  full change-record -> sync -> provenance/stale-label
  execution must then be built into this family and
  graded in a successor packet
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **NOT BUILT at baseline** — a
  finding, not a harness failure (plan §5.1(iii)): the
  Muse Space surface (GP-E25) is in flight on PR #510
  and unmerged, so no plan-change sync is constructible
  from this head.
- uncovered_cases: the whole designed oracle (plan
  record change -> sync -> Space shows new state with
  provenance; stale mirror labeled stale) awaits the
  GP-E25 landing and a successor execution of this
  family against it
- timestamp: 2026-11-21T21:45Z

### A.14 — J-09 Resonance to Nursery (family suite `form/journey_growth_test.py`)

- journey_id: J-09
- feature_scope: the file 06 oracle executed verbatim — two
  active eligible Ideas yield an explainable pair score and a
  distinct pending candidate; human accepts with a
  source-bound record; the failure oracle (faded/superseded/
  sandboxed excluded per policy; no fake 'vesica' geometry,
  no automatic graph edge from score; reload accepted
  relationship and provenance)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1; suite executed in the PR #502 clone)
- PR/head: #502 @ 767058efbd2d259d7df650cc1460a7728ea9c8f9
  (baseline run executed before this section's commit; the
  suite is carried by this PR)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions (piped stdin) —
  PUBLIC_ENTRY_PATH for every journey action (create, grow
  ideas, proposals, lineage, confirm, fade, supersede,
  group create/add)
- owner: per-run isolated owners (JRes<run>, JFade<run>,
  JSup<run>, JWall<run> for this journey; J-14's owners are
  recorded in A.15), cleaned up after; the isolation
  boundary is proven in-suite (no state files exist for any
  of the family's seven owners before the sessions start)
- input_fixture_digest: suite file sha256
  d0dc8f7b881a1c0d421bc623b0d122238df7ac7e007765afb774fa89ac23d2ea
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_growth_test` —
  **25/25 PASS** for the family (J-09 checks: 13 of 25,
  incl. shared isolation/cleanup); expectations were
  grounded in scratch-owner probes run before the suite was
  written. Mutant sensitivity: disabling the lifecycle
  participation gate in ringed_growth._affinity
  (inverse-edit mutant) fails exactly
  j09_faded_pair_never_scores and
  j09_superseded_never_parent_successor_grows (23/25);
  reverted by inverse edit (diff verified empty), suite
  back to 25/25.
- expected_state_diff: the Harbor pair's cross candidate is
  born pending with affinity 0.674 and the component reason
  (Solstice harm=0.76 goals=0.02 hs=0.42 gcoh=0.00) on the
  review face and in the stored record; the canonical graph
  gains no entry from scoring or from acceptance; confirm
  places the unit with both parents as lineage while the
  proposal record keeps origin/reason/affinity; faded,
  superseded and cross-wall pairs produce no candidate
  parented by the excluded unit.
- observed_state_diff: exactly the expected diff, on the
  loader basis and after cold reload, on every leg. The
  graph held zero entries before the grow, after the grow
  and after the confirm. The superseded leg's successor
  unit grew its own crosses in the same grow that excluded
  the predecessor — the exclusion is the state. No product
  defect was exposed by this journey; no product code was
  touched by this section.
- refusal_class: supersession of a never-nursery-born unit
  refuses "unknown_predecessor" (observed in probes; the
  public supersede door acts on nursery-born records) —
  recorded as the door's honest boundary, not a defect
- persistence_generation: saves executed in-session
  ("Session saved."); every comparison is a fresh loader
  snapshot in a later process (--load)
- cold_restart: YES — relationship and provenance compared
  across separate REPL processes after reload
- consumer_views: REPL proposals view, lineage view, idea
  view, persistence-loader snapshots, SemanticGraph loader
- test_suite: form/journey_growth_test.py (family 7),
  registered in form/regress.py LIST in the same commit
  (317 entries, membership verified exactly once)
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **BASELINE — FULL_SCOPE_PASS
  (public-path scope)** — every mandatory step of the
  file 06 oracle has executable public-path proof at this
  head
- uncovered_cases: REAL_USER_PATH not claimed (piped REPL
  is PUBLIC_ENTRY_PATH); the docked-mind growth path
  (SD-3 SYNTHESIZE crosses) is J-10's family, not
  exercised here — this family's grows ran the token path
  (origin growth:token on every record)
- timestamp: 2026-11-21T21:56Z

### A.15 — J-14 Scoped growth (family suite `form/journey_growth_test.py`)

- journey_id: J-14
- feature_scope: the file 06 oracle executed verbatim
  where constructible at this head — select a named
  eligible idea scope and grow; only that scope receives
  the new candidate and logged effect; bare grow discloses
  mode; the failure oracle's partial-evidence case
  executed (a context matching one of two eligible units
  selects exactly that one, disclosed as 1 of 2)
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 767058efbd2d259d7df650cc1460a7728ea9c8f9
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions — PUBLIC_ENTRY_PATH for
  every journey action (create, grow ideas, exchange
  export/import, confirm, grow using knowledge about
  <context>, grow mode)
- owner: per-run isolated owners (JBare<run>,
  JScopeSrc<run>, JScopeDst<run> for this journey),
  cleaned up after; isolation boundary proven in-suite
  (see A.14)
- input_fixture_digest: suite file sha256
  d0dc8f7b881a1c0d421bc623b0d122238df7ac7e007765afb774fa89ac23d2ea
  (the two exchange packets are generated in-run from the
  fixed fixture strings and deleted after the run)
- raw command/log: `python3 -m form.journey_growth_test` —
  25/25 PASS for the family (J-14 checks: 11 of 25);
  expectations grounded in scratch-owner probes before
  the suite was written, including the eligibility probes
  that established WHY ordinary REPL state selects
  nothing (next field). Mutant sensitivity: see A.14 (the
  family mutant targets the shared growth gate).
- expected_state_diff: the scoped door with no eligible
  knowledge discloses Eligible 0 / Selected 0 / scope []
  and grows nothing; with two eligible units a
  harbor-only context selects exactly one (scope IDs =
  [harbor unit], no growth), a both-covering context
  selects both and grows exactly one pending candidate
  parented by exactly the scope pair; no live unit's
  record changes at any scoped step.
- observed_state_diff: exactly the expected diff, on the
  loader basis and after cold reload. Manufacturing the
  eligible scope itself ran the public path end to end:
  exchange export in the source owner, exchange import
  landing both records PENDING and parentless in the
  destination, human confirm landing them as parentless
  units. The probes also established the negative space
  honestly: directly-created ideas are not knowledge-store
  records at all, and a confirmed growth candidate whose
  parents are unconfirmed direct units is
  dependency-INVALID under DCC-XV (disclosed on the
  receipt as "Dependency exclusions: 1") — so the
  selection law's eligibility is a real gate, not a
  formality, and the scoped door never broadens past it.
  The built-in Welcome unit never appears as a parent of
  any destination proposal. No product defect was
  exposed; no product code was touched by this section.
- refusal_class: none issued by the scoped door itself —
  an empty selection is a disclosed no-op ("Reason: no
  eligible knowledge"), never a silent full-plane grow;
  bare `grow ideas` in the same state grows the cross,
  proving the door, not the engine, withheld growth
- persistence_generation: saves executed in-session;
  every comparison is a fresh loader snapshot in a later
  process (--load)
- cold_restart: YES — destination units and proposal
  records compared across a cold reload
- consumer_views: REPL contextual-grow receipt (eligible/
  selected/routable counts, reason, scope mode, consumer
  scope IDs), proposals view, grow-mode face,
  persistence-loader snapshots
- test_suite: form/journey_growth_test.py (family 7),
  registered in form/regress.py LIST in the same commit
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **BASELINE — PARTIAL_SCOPE** — the
  scoped-growth mechanism, its selection accounting, its
  no-broaden discipline, the partial-evidence case and
  the no-silent-mutation clause all have executable
  public-path proof at this head; the grade is partial
  because the failure oracle's "stopped" case is
  uncovered (below) and its cross-wall/faded/superseded
  negatives stand on J-09's legs over the same mechanisms
  rather than on J-14-local legs
- uncovered_cases: the "stopped" case — no stopped state
  exists in the growth/selection machinery at this head
  (searches of ringed_growth, knowledge_selector,
  canonical_lifecycle and open.py return no stopped
  state; reported as unproven, never as "not there" —
  a future stopped-state build lands its check in this
  family); REAL_USER_PATH not claimed
- timestamp: 2026-11-21T21:56Z

### A.16 — J-10 AI assist (family suite `form/journey_dock_test.py`)

- journey_id: J-10
- feature_scope: the file 06 oracle executed verbatim
  where constructible at this head — dock a permitted
  provider as Psalm through the Connected World session,
  submit a scoped suggestion (`ask`), display provider/
  model + reason on the receipt and the review face; the
  Nursery receives PENDING, never auto confirmed by the
  dock path itself; the failure oracle's provider outage,
  prompt over-cap, protected-value canary, and
  cross-owner injection legs executed; local Matrix
  continues offline
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 9347881c2a9be98b7983b6c57994321b5453380b
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions — PUBLIC_ENTRY_PATH for
  every journey action (connect, provider, ask, leave,
  proposals, lineage, confirm, reject, grow ideas,
  auto confirm on, grow mode, create)
- owner: per-run isolated owners (JDock<run>,
  JHuman<run>, JOut<run>, JCanary<run>, JSweep<run>,
  JForeign<run>, JGrow<run>), cleaned up after; isolation
  boundary proven in-suite (no state files for any of
  the seven owners before the sessions start)
- input_fixture_digest: suite file sha256
  3d5c5c08db3a038f07eecc6f9797873711161ef7cfd53da2421457dcccdddd25
- raw command/log: `python3 -m form.journey_dock_test` —
  25/25 PASS for the family (J-10 checks: 18 of 25, plus
  the shared isolation check); expectations grounded in
  scratch-owner probes before the suite was written.
  Mutant sensitivity: the connect session's fail-closed
  input screen (`_studio_screen_input` in form/repl.py)
  disabled by inverse edit → 24/25, failing exactly
  j10_protected_canary_refused_and_never_echoed; reverted
  by inverse edit (diff verified empty), suite back to
  25/25.
- expected_state_diff: the ask creates exactly one
  PENDING proposal and no unit; the review face and the
  loader record agree on origin
  "dock:connect:<owner>:fake:fake:valid" and the derived
  reason; the human confirm lands it exactly once; the
  refusals (canary, over-cap) create nothing; a foreign
  owner holds neither the proposal nor a unit under its
  pid.
- observed_state_diff: exactly the expected diff, on the
  loader basis and after cold reload. The ask receipt
  displays provider=fake, model=fake:valid and states the
  proposal "is not confirmed and carries no authority";
  the review face adds the SD-1 evidence join ("task:
  propose · session <id8>"), and the program's durable
  dock_sessions evidence links the pid to task "propose"
  and the ACTUAL model "fake:valid". On file 06's
  "grant" display point: no grant is issued, displayed,
  or carried anywhere — the proposal record and the
  evidence entry hold no grant field; docking confers no
  authority by construction, and the suite asserts the
  absence rather than a displayed grant. The docked
  context itself holds no confirm power: `confirm <pid>`
  inside the connect session refuses as out of scope; the
  human's confirm outside it is the only landing, and a
  second confirm refuses "not found or not pending". The
  canary ask (grant-handle format) is rejected
  "PROTECTED_MATERIAL" before routing and the canary
  string appears nowhere in the transcript; the
  1,000,005-char prompt refuses "prompt_too_large"
  against the disclosed 1,000,000 cap; a local create
  after `leave` succeeds — the Matrix continues offline.
  FINDING 1 (recorded, not fixed here): the auto-confirm
  sweep is ORIGIN-BLIND at this head. Default OFF: a bare
  grow never touches the docked proposal. Under the
  human's explicit `auto confirm on` opt-in (banner
  disclosing "every grow accepts all nursery proposals")
  the next grow sweeps the docked proposal too — status
  "confirmed", landed as a live unit inside the
  auto_staging sandbox box (sandbox-first, never the
  open plane). This is Part VI matrix row A12, whose
  origin-aware repair is already in flight on Part I's
  PR #508; per the lane rule for Part I overlaps the fix
  is NOT duplicated on this branch. The suite pins the
  baseline-true fence parts (default OFF never sweeps;
  opt-in disclosed on its face; swept placement is the
  staging sandbox). FINDING 2 (recorded, not fixed):
  growth inside the connect session prints "Growth
  (docked): 1 new + 2 evolved — all PENDING review",
  but all three proposals carry origin "growth:token"
  (the fake provider's SYNTHESIZE response fails the
  semantic schema; SD-3's per-pair token fallback
  authored them). Proposal-level provenance is truthful;
  the one-line receipt does not disclose the fallback —
  a receipt-precision wart of A.7's class. No product
  code was touched by this section.
- refusal_class: PROTECTED_MATERIAL (canary, fail-closed
  screen, before routing); prompt_too_large (over-cap);
  DOCK_FAILED (unknown provider — J-22's leg, A.17);
  provider_failure (credential-less bridge provider);
  out-of-scope refusal for confirm inside the docked
  session; "not found or not pending" for re-confirm and
  for cross-owner confirm/reject
- persistence_generation: saves executed in-session;
  every comparison is a fresh loader snapshot in a later
  process (--load)
- cold_restart: YES — proposal records, units, boxes,
  and dock evidence compared across cold reloads
- consumer_views: connect status face, ask receipt,
  proposals review face (origin / reason / SD-1 task ·
  session join), lineage face, grow-mode face,
  persistence-loader snapshots
- test_suite: form/journey_dock_test.py (family 8),
  registered in form/regress.py LIST in the same commit
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **BASELINE — PARTIAL_SCOPE** — the
  mandatory core (dock by name, scoped ask, provider/
  model/reason displayed, PENDING-only landing, the
  human gate as the sole landing path, outage/canary/
  over-cap/cross-owner refusals, offline continuation)
  has executable public-path proof at this head; the
  grade is partial because Finding 1 leaves "never auto
  confirmed" untrue under the explicit opt-in until
  Part I's A12 repair lands, and two failure-oracle
  cases are not constructible at the public path (below)
- uncovered_cases: the failure oracle's "response
  stop_reason" case — a bridge transport outcome; the
  credential-less provider refuses before any response
  exists (exercised), but no stop_reason-bearing
  response can be produced offline at the public path.
  The "revoked grant" case as a presented object: no
  grant is ever issued to a docked session, so there is
  no grant object to revoke or present — refusal is by
  construction, evidenced by the no-grant checks. The
  hostile FakeProvider modes (authority, canary_error,
  reflect, timeout, failure, malformed, empty) are not
  selectable at the public path — the connect `provider`
  command takes a name only and the host dock() call
  never exposes fake_mode there, by design; no suite at
  this head was found exercising the non-valid modes
  (the module comment's r62 pointer does not resolve to
  a file at this head — unproven, never "not there").
  REAL_USER_PATH not claimed
- timestamp: 2026-11-21T22:05Z

### A.17 — J-22 Outage/reconnect (family suite `form/journey_dock_test.py`)

- journey_id: J-22
- feature_scope: the plan §5.2.1 oracle executed
  verbatim where constructible at this head — dock a
  provider, sever it mid-session, reconnect; no
  duplicate confirmation; grant state consistent;
  in-flight suggestion either completed once or refused
  with receipt, never landed twice
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 9347881c2a9be98b7983b6c57994321b5453380b
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions — PUBLIC_ENTRY_PATH
  (grow mode, connect, provider <name>, ask, leave,
  proposals, confirm, save)
- owner: per-run isolated owner (JOut<run>), cleaned up
  after; isolation boundary proven in-suite (see A.16)
- input_fixture_digest: suite file sha256
  3d5c5c08db3a038f07eecc6f9797873711161ef7cfd53da2421457dcccdddd25
- raw command/log: `python3 -m form.journey_dock_test` —
  25/25 PASS for the family (J-22 checks: 5 of 25);
  expectations grounded in scratch-owner probes before
  the suite was written, including the two sever forms
  and the reconnect tally. Mutant sensitivity: see A.16
  (the family mutant targets the shared connect screen).
- expected_state_diff: the two in-flight asks during the
  sever land zero proposals between them; the retried
  ask after reconnect creates exactly one pending
  proposal; one human confirm lands exactly one unit;
  policy state reads identically before and after.
- observed_state_diff: exactly the expected diff, on
  the loader basis and after cold reload. Sever form 1:
  `provider nosuchthing` refuses the ask at the dock —
  "DOCK_FAILED: unknown provider 'nosuchthing'". Sever
  form 2: `provider gemini` (a real bridge provider, no
  host credentials in this environment) refuses the ask
  as "Ask failed (provider_failure)" with the sanitized
  cause on the receipt (the suite pins the refusal
  class, not the environment-specific detail). Neither
  sever created a proposal or a session record entry for
  a proposal. Reconnect (`provider fake`) completes the
  retried suggestion exactly once: one creation receipt,
  one pending proposal on the review face. The human
  confirm lands it; an immediate second confirm refuses
  "not found or not pending"; the reload shows one live
  unit, a confirmed record, nothing pending. Grant
  state consistency: no grant exists in this machinery
  to drift (A.16), and the one policy state the journey
  can observe — the auto-confirm mode — reads
  auto_confirm_grow=OFF before the sever and after the
  reconnect/confirm sequence; the landed record's
  provenance still names the reconnected provider
  (dock:connect:<owner>:fake:fake:valid). A second
  probe dimension, recorded in A.16's grounding:
  reconnecting across separate connect sessions mints
  distinct suffixed pids per ask, each attributed to
  its own session's evidence — no cross-session
  duplication either. No product defect was exposed; no
  product code was touched by this section.
- refusal_class: DOCK_FAILED (unknown provider);
  provider_failure (credential-less bridge provider);
  "not found or not pending" (duplicate confirm)
- persistence_generation: saves executed in-session;
  every comparison is a fresh loader snapshot in a later
  process (--load)
- cold_restart: YES — the post-reconnect confirm and the
  final reconciliation are verified across a cold reload
- consumer_views: connect provider/ask receipts,
  proposals review face, grow-mode face,
  persistence-loader snapshots
- test_suite: form/journey_dock_test.py (family 8),
  registered in form/regress.py LIST in the same commit
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending; MERGE HOLD 7068847023
  stands (merging only)
- completion_status: **BASELINE — FULL_SCOPE_PASS
  (public-path scope)** — every §5.2.1 oracle point has
  executable public-path proof at this head: mid-session
  sever in both constructible forms, in-flight
  suggestions refused with receipts and landed zero
  times, the retried suggestion completed exactly once,
  no duplicate confirmation, and grant/policy state
  consistent across the outage
- uncovered_cases: transport-level mid-response
  severance (the fake provider's timeout/failure modes)
  is not selectable at the public path — the connect
  `provider` command takes a name only (see A.16);
  REAL_USER_PATH not claimed
- timestamp: 2026-11-21T22:05Z

### A.18 — J-12 Crash-save (family suite `form/journey_crash_test.py`)

- journey_id: J-12
- feature_scope: the file 06 oracle executed verbatim
  where constructible at the public path — "Inject crash
  at each phase of owner save/checkpoint/Program-Nursery
  convergence, restart and show old or complete new
  generation, never hybrid"; failure oracle: "Broken/
  corrupt envelope refuses and offers diagnosed recovery;
  no false success on directory sync failure; all temp
  cleanup bounded and accounted"
- source_main_sha: b9cebf72446c7a76af8754945c0399aff34c4e27
  (branch base, as A.1)
- PR/head: #502 @ 742988a19459f7b4dcc0f72ba27b7749b9e1ffaf
  (baseline run executed before this section's commit)
- public_action: literal `python3 -m form.repl --owner
  <isolated>` subprocess sessions — PUBLIC_ENTRY_PATH;
  crashes are real signals delivered to the REPL process
  (SIGKILL mid-session; SIGKILL on the save's `.dmtmp.`
  temp sighting; SIGSTOP-frozen mid-seal then SIGKILL).
  Disclosed fixture mechanics: the corruption legs write
  bytes directly to a live member file (the fault being
  injected; the restart runs at the public path), and the
  temp-accounting leg invokes
  atomic_write.sweep_stale_tmps explicitly — the
  documented mechanism, whose production wiring is pinned
  as an explicit-call-only posture by
  form/atomic_write_boundaries_test.py control G (that pin
  is untouched by this section and still passes)
- owner: per-run isolated owners (JCrashMid/JCrashWrite/
  JCrashWriteRef/JCrashSeal/JCrashSealRef/JCrashProg/
  JCrashNurs/JCrashTorn/JCrashPtr/JCrashFresh <run>),
  cleaned up after; isolation boundary proven in-suite
- input_fixture_digest: suite file sha256
  e1571de1bee6cd895645b218ddb81be7c208ac3e5b9ddd5cb2e8c7c6dae16d62
  (inputs are fixed strings in the suite)
- raw command/log: `python3 -m form.journey_crash_test` —
  **25/25 PASS**. Failing-first: the pre-fix run was
  **19/24** (the suite then had 24 checks), failing
  exactly the four corrupt-envelope checks of Defect 1
  below and the missing-program check of Defect 2.
  Expectations were grounded in scratch-owner probes
  before the suite was written (kill windows, orphan
  temp, corrupt-member restarts, pointer behavior,
  grow-before-first-save state). Mutant: the
  ProgramLoadError decode wrap in persist_rest._load_impl
  disabled by inverse edit → **22/25**, failing exactly
  j12_corrupt_program_loader_typed_refusal,
  j12_corrupt_program_repl_diagnosed_refusal and
  j12_truncated_program_repl_diagnosed_refusal; reverted
  by inverse edit (diff verified to be exactly the fix),
  suite back to 25/25. One in-flight suite run was killed
  by a VM restart mid-mutant-check (NO RESULT, not a
  failure); its leftover per-run state files were removed
  and the mutant run was re-executed to its terminal
  result above.
- expected_state_diff: a mid-session kill loses exactly
  the unsaved work and nothing else; a mid-save kill
  leaves the complete old or the complete new generation;
  a mid-seal kill leaves CURRENT on the previously
  committed generation with the live pair complete on one
  side; corrupt members refuse diagnosed with bytes
  preserved; temp orphans number exactly one per killed
  write and are reaped by the explicit sweep
- observed_state_diff: exactly the expected diff on the
  loader basis after cold restart, in every leg. Kill
  legs landed on the old-generation arm in the recorded
  runs (membership in the two-arm disjunction is the
  asserted invariant, per the oracle's "old or complete
  new"). The committed generation restored exactly after
  the mid-seal kill. TWO PRODUCT DEFECTS were found and
  FIXED in this section (the family's failing-first run
  caught both; the fixes are product code in
  form/persist_rest.py + form/repl.py):
  (1) corrupt PROGRAM envelope escaped the loader's typed
  refusal contract — the raw decode in _load_impl raised
  UnicodeDecodeError/JSONDecodeError where every other
  loader step raises ProgramLoadError, and the REPL died
  on the traceback: refusal in effect, but no diagnosed
  recovery offer, unlike the nursery member
  (NurseryLoadError) and the CURRENT pointer (in-session
  diagnosed refusal — this suite's control leg, passing
  at baseline). Fixed: the decode is wrapped in
  ProgramLoadError (file, diagnosis, bytes, preserved),
  and repl startup presents both typed refusals as a
  printed diagnosis naming the surviving sealed
  generation as the recovery source, exit 1, no
  traceback; other exceptions keep their traceback.
  (2) a missing program member with a surviving sealed
  generation exposed a HYBRID — the D2 fresh-owner arm
  fabricated a fresh program and the restart exposed it
  wearing the destroyed book's nursery proposals (their
  parent units absent from the exposed scope). Fixed:
  on the default owner path, a missing program file
  with a committed generation raises ProgramLoadError
  naming the generation as the recovery source.
  Boundary control pinned in-suite: a first session that
  grows before its first save (proposals on disk, no
  program file, NO generation — a legitimate
  program-produced state) still opens with its proposals
  carried; nursery content alone is never treated as
  destruction evidence.
- refusal_class: ProgramLoadError (corrupt program
  member; missing program member with surviving
  generation); NurseryLoadError (corrupt nursery
  member); "Restore unavailable: ... committed CURRENT
  pointer unreadable" (corrupt pointer, in-session)
- persistence_generation: live pair + named generations
  (base_one, seal_one/seal_two); every comparison is a
  fresh loader snapshot in a later process (--load)
- cold_restart: YES — every leg's verdict is read from a
  cold restart's loader scope, never the killed session
- consumer_views: persistence-loader snapshots, REPL
  startup output (diagnosed refusals), restore door
  (committed-generation survival), state-dir file census
  (temp accounting)
- test_suite: form/journey_crash_test.py (family 10),
  registered in form/regress.py LIST in the same commit.
  Neighbors at the section head, all green: journey_chain
  16/16, journey_language 19/19, journey_idea_lifecycle
  34/34, journey_confirm 38/38, journey_rollback 28/28,
  journey_views 29/29, journey_growth 25/25,
  journey_dock 25/25, checkpoint_generation_stress
  15/15, atomic_write_boundaries 67/67 (control G pin
  intact), sm35_pair_atomic GREEN,
  resumability_checkpoint rc=0, graph_journal_crash
  12/12, owner_namespace_collision 12/12,
  nursery_confirm_race 57/57, dcc_xviii GREEN,
  dcc_xvii GREEN, persist_full_roundtrip rc=0,
  test_isolation_hygiene rc=0,
  repl_seed_error_visibility 13/13, growth_persistence
  12/12, water_persistence 14/14
- CI run: pending — this PR's CI at the section head (see
  the §45 package on PR #502)
- checker: Uni (author); Keeper independent check at
  CODE/RECORDS-CONFIRM
- Director disposition: pending (code-stage confirm; PR
  #502 is under the Director MERGE HOLD 7068847023 — the
  hold bars merging only; this section builds under the
  standing Part workflow, no merge sought)
- completion_status: **BASELINE — PARTIAL_SCOPE**
  (baseline grade: evidence about the harness and the
  current program only; the rehearsal grade is assigned
  at rehearsal time, plan §5.1). Executed scope:
  mid-session kill, mid-live-save kill, mid-seal kill at
  the pointer commit boundary, corrupt program/nursery/
  pointer restarts with diagnosed recovery, missing-
  member legs, temp boundedness + explicit accounting.
  The oracle clauses not executed at this tier are named
  below; two product defects found by the journey were
  fixed in-section and are re-proven by the suite at the
  section head.
- uncovered_cases: crash at EACH seal phase and
  directory-sync failure are not constructible at the
  public path — the _fail_at seam (incl. "dir_fsync_fail")
  is a module-global test hook with no REPL door; that
  matrix is covered at API level by
  form/mandell/dcc_xviii_test.py controls A–W and
  form/checkpoint_generation_stress_test.py (directory-
  sync degradation observable in the commit receipt),
  cited, not duplicated. Findings left standing:
  deleting the nursery member loads the program exactly
  and silently drops all pending proposals (no hybrid —
  the loss is the silent part); deleting the program
  member when NO generation survives still starts fresh
  over surviving proposals, indistinguishable from the
  legitimate grow-before-first-save state, so no honest
  loader rule can refuse it. Kill-during-rollback is
  family 5 / R6.3 territory. REAL_USER_PATH not claimed
  (piped REPL is PUBLIC_ENTRY_PATH)
- timestamp: 2026-11-21T22:21Z
- CI repair addendum (2026-11-21, post-first-CI): CI run
  44956493651 at head dc8c1c53 FAILED both regress passes —
  this suite died on a traceback at 0/0 after the nine
  checks preceding the mid-seal leg; all 318 other suites
  passed. Classification: TEST-INSTRUMENT DEFECT (no
  product behavior implicated). The kill legs triggered on
  sighting a `.dmtmp.` temp by polling the shared state
  dir (thousands of accumulated files in the regress
  copy); when the mid-seal sighting missed, the leg's bare
  proc.wait(timeout) raised TimeoutExpired and killed the
  suite before it could report. Reproduced locally by
  slowing the temp poll (identical death signature).
  Repair, suite-only: the seal leg triggers on the temp
  OR the checkpoint intent journal (present for the whole
  seal); spawned-REPL writes/waits go through
  non-raising helpers, so a missed trigger degrades to
  named check FAILs and the suite always reports its full
  count (forced total-miss run: 22/25, three named FAILs,
  no traceback; mutant restoring the raising wait
  resurrected the exact baseline death). Suite re-proven
  25/25 at the repair head; the CI red is closed only by
  terminal CI at the repair head, not by this record.

## Annex B — harness construction status (plan §5.2 families)

| Family suite | Journeys | Status |
|---|---|---|
| journey_chain_test.py | J-01, J-02 | BUILT — baseline 16/16 (Annex A) |
| journey_language_test.py | J-03 | BUILT — baseline 19/19 (Annex A.3; one product defect found + fixed) |
| journey_idea_lifecycle_test.py | J-04, J-16, J-17 | BUILT — baseline 34/34 (Annex A.4–A.6; two product defects found + fixed: create-door detail/goals silent cuts, edit-door detail silent cut) |
| journey_confirm_test.py | J-05, J-21 | BUILT — baseline 38/38 (Annex A.7–A.8; no product defect found; one receipt-freshness finding recorded in A.7) |
| journey_rollback_test.py | J-06 | BUILT — baseline 28/28 (Annex A.9; no product defect found) |
| journey_views_test.py | J-07, J-08, J-13, J-23 | BUILT — baseline 29/29 (Annex A.10–A.13; J-07 FULL_SCOPE_PASS public-path scope, J-13 PARTIAL_SCOPE with the REPL<->Studio load gap + DAF-09 D1 recorded as findings, J-08/J-23 NOT BUILT at baseline — subjects unlanded) |
| journey_growth_test.py | J-09, J-14 | BUILT — baseline 25/25 (Annex A.14–A.15; J-09 FULL_SCOPE_PASS public-path scope, J-14 PARTIAL_SCOPE — "stopped" case uncovered, no stopped state in the machinery at this head; no product defect found) |
| journey_dock_test.py | J-10, J-22 | BUILT — baseline 25/25 (Annex A.16–A.17; J-10 PARTIAL_SCOPE — Finding 1: origin-blind auto-confirm sweep accepts docked proposals under the explicit opt-in, Part VI A12, repair in flight on Part I; Finding 2: docked-growth receipt label vs token provenance; J-22 FULL_SCOPE_PASS public-path scope; no product defect fixed, no product code touched) |
| journey_hcn_test.py | J-11 | not built (subject NOT BUILT until GP-E22 lands) |
| journey_crash_test.py | J-12 | BUILT — baseline 25/25 (Annex A.18; PARTIAL_SCOPE — per-phase + dir-sync crash matrix is API-level only (dcc_xviii A–W, checkpoint_generation_stress), cited not duplicated; TWO product defects found + fixed: corrupt program envelope escaped the typed ProgramLoadError contract and died as a raw REPL traceback (decode wrap + diagnosed REPL presentation), missing program member with a surviving sealed generation exposed a hybrid fresh-program/orphaned-proposals pair (fresh-arm guard on positive generation evidence); findings left standing: missing-nursery silent proposal loss, missing-program-without-generation residue; post-CI instrument repair at the repair head: first CI (44956493651) died 0/0 on a missed temp-sighting + raising wait — classified TEST-INSTRUMENT DEFECT, seal trigger widened to the checkpoint intent journal, all spawned-REPL writes/waits non-raising, re-proven 25/25; see the A.18 CI repair addendum) |
| journey_exchange_test.py | J-18, J-19 | not built (J-19 known gap: duplicate-replay idempotency absent — the rehearsal reports the program as it is) |
| journey_offline_test.py | J-20 | not built (trace record exists from plan stage) |
| journey_index_test.py | J-15 | not built |
| journey_perf_test.py | J-24 | not built |
| journey_canary_test.py | J-25 | not built |
