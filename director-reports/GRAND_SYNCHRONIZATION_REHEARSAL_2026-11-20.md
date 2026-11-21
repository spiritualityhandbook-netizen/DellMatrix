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

## Annex B — harness construction status (plan §5.2 families)

| Family suite | Journeys | Status |
|---|---|---|
| journey_chain_test.py | J-01, J-02 | BUILT — baseline 16/16 (Annex A) |
| journey_language_test.py | J-03 | not built |
| journey_idea_lifecycle_test.py | J-04, J-16, J-17 | not built (J-20 trace exists from plan stage; suite not built) |
| journey_confirm_test.py | J-05, J-21 | not built |
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
