# MPC_011_PACKET — DELL37 RECONCILIATION + CLAUDE EXTERNAL-AUDIT DIFFERENTIAL

## BASE
- BASE_SHA: `72008c36236574ed41978d48d740e752975134d3`
- BASE_TREE: `63ee41260edd6725b3c6ef4c622ed3182f60ed0f`
- Branch: `mpc-011-work` (fresh from exact main; Director-verified base confirmed by independent `git rev-parse`)

## DELL37 RECONCILIATION
- DELL37_FINAL_AUTHORITY: **NURTURE / NURSERY LIFECYCLE** (C-R1-004 RESOLVED SEMANTICALLY — no new behavior invented)
- DELL37_REGISTRY_CORRECTION: `form/mandell/registry.py:52` — `37: {"name": "Stream", "manor": "Chunked out"}` → `37: {"name": "Nurture", "manor": "Nursery lifecycle"}` (APPLIED)
- DELL37_DOC_CORRECTION: `form/mandell/CORE_I.md:37` — `37 Stream` → `37 Nurture`; `CORE_I.md:46` — `37 Stream is history replay, not a network stream` → `37 Nurture is nursery lifecycle (confirm/reject/use/supersede), not a network stream` (APPLIED)
- DELL37_DEAD_BRANCH_REACHABILITY: re-proven on exact current main across all 7 routes — single-atom NURTURE, multi-atom (`>>` chain) NURTURE, raw Mandell NURTURE, English NURTURE, Flow/composition NURTURE, direct executor NURTURE, tests pin Nurture. The `executor_leaf.py` Stream branch was reachable ONLY via direct Python import of `executor_leaf.execute_seed` (zero production callers; sole production importer is `executor.py` itself, which always runs the Core-I HANDLED check first). `core_ii_smoke.py:120` uses it only for `inspect.getsource`. No test depends on direct leaf invocation.
- DELL37_DEAD_BRANCH_ACTION: **REMOVED** (`form/mandell/executor_leaf.py` — 10-line `elif primary == 37:` Stream-history block deleted). Regression added: `form/mandell/dell37_nurture_test.py` (6/6 GREEN) proving Dell37 routes to Nurture authority on every production route.

## CLAUDE AUDIT
- CLAUDE_AUDIT_ID: CA-01
- CLAUDE_BASELINE: `d38df51bbcbad4e54ac86fc9fba7a7f66c71ac26`
- CLAUDE_COMPLETION_STATUS: PARTIAL_PHASE_I_LIMIT_REACHED (NOT a completed architectural assessment; incomplete areas remain UNKNOWN; severity/order not inherited)
- INDEPENDENTLY_CORROBORATED_SUPERSEDED (historical corroboration, not current defects):
  - resume: ordinary resume/load family no longer causes Dell28 checkpoint rollback (MPC-008 semantics hold)
  - macro: macro-creation requests no longer silently become ideas (verified: `48[Macro]` path honest)
  - uid collision: raw-Mandell duplicate UID overwrite corrected incl. >50 residual — nonregression PROVEN via `Program.load` path (`cuid3_beta`, `cuid3_beta_1` preserved; post-load duplicate → honest `cuid3_beta_2` receipt)
  - Dell87 naming: runtime is key rename despite old substitution wording — corroborated (registry corrected MPC-009)

## CA01_CURRENT_MAIN_RESULTS

### SET_DETAIL_GOALS (G)
- CLAUDE_BASELINE_RESULT: `set detail alpha hello world` → `idea not found: detail`; `set goals alpha g1; g2` → `idea not found: goals`, while help advertises both
- CURRENT_MAIN_RESULT: **STILL_PRESENT — worse than baseline.** Silent wrong-target mutation: with decoy ideas named `detail`/`goals` present, `set detail alpha hello world` wrote `detail="alpha hello world"` onto the idea NAMED "detail"; `alpha` untouched, user told success.
- Root cause: `raw_line.split(maxsplit=2)` on the FULL line in `form/repl.py:1566-1584` and `form/dell_matrix/live_visual.py:714-731` → `parts[1]` ("detail") used as idea ref instead of the actual id.
- PROBE_SCOPE: PUBLIC_ENTRY_PATH (separate OS process, piped stdin into shipped `python3 -m form.repl`) + INTEGRATION (direct API save/load roundtrip)
- STATE_BEFORE: fresh owner, `alpha` (detail —, goals —). STATE_AFTER (pre-fix): unchanged on miss; decoy absorbed edits in mis-target case
- PUBLIC_REACHABILITY: yes — shipped REPL; identical bug in `/cmd` path
- CLASSIFICATION: **PARSER_BUG**
- NULL_RESULT: fix needed; intended syntax unambiguous from 5 consistent help sources; smallest parser correction authorized
- ARGUS_RESULT: injection payloads inert (`;`, quotes, multiword); real hazard is silent mis-targeting
- ACTION: **FIXED** — both parsers now strip the command prefix then split into `<ref> <text>`; `set detail alpha` (no text) now returns usage. E2E verified: create → set detail/goals → inspect → save → fresh-process load → detail/goals persist; missing id names the ref; decoy untouched. Regression: `form/mandell/set_detail_goals_test.py` (7/7 GREEN)

### LIVE_CMD_SECURITY (H)
- CLAUDE_BASELINE_RESULT: localhost POST /cmd — no authentication observed, `Access-Control-Allow-Origin: *`, command mutation accepted from spoofed Origin/Host via curl; Claude did NOT prove a real-browser exploit
- CURRENT_MAIN_RESULT (code-verified on exact main; live browser proof unavailable — see below):
  - bind address: `127.0.0.1` ONLY (`live_visual.py:22`, `start_live`) — remote network reachability FALSIFIED
  - authentication: NONE on `/cmd` — any local process can POST mutating commands
  - Origin validation: NONE (headers never read); Host validation: NONE
  - CORS: `Access-Control-Allow-Origin: *` on every JSON response; OPTIONS → 204 + ACAO:*
  - accepted content types: JSON `{"cmd"}`/`{"command"}`; raw-body fallback executes ANY text as a command (simple `text/plain` POST needs no preflight)
  - command authority: FULL — `_run_command` fallthrough executes any English line or Mandell seed with mutation
- PROBE_SCOPE: source inspection of `form/dell_matrix/live_visual.py` (handler `_make_handler`, `_run_command`, `start_live`); live curl-level behavior corroborated by probe B's I-item server tests
- CLASSIFICATION:
  - LOCAL_CLIENT_COMMAND_ACCESS: **VERIFIED** (no auth; local POST mutates)
  - CROSS_ORIGIN_BROWSER_WRITE: **NOT PROVEN** — mechanics permit (simple POST executes; JSON preflight passes), but two browser-task attempts to obtain browser-level evidence were refused by browser-side safety review. Per directive, NOT claimed exploitable.
  - CROSS_ORIGIN_BROWSER_READ: **NOT PROVEN** (ACAO:* present, but read follows from unproven write)
  - DNS_REBINDING_PRECONDITION: **UNKNOWN** (not tested)
  - REMOTE_NETWORK_REACHABILITY: **FALSIFIED**
- NULL_RESULT: no existing auth mechanism; correction requires Director policy decision (open question: should missing-Origin curl/local tooling remain allowed?)
- ARGUS_RESULT: browser-level hostile-origin proof attempted twice, refused; simple-POST and preflight mechanics verified from source
- ACTION: **NOT IMPLEMENTED** (per directive — security semantics need Director decision). Bounded correction candidate returned: validate Origin/Host on `/cmd` against the server's own origin (reject mismatches with 403), drop wildcard ACAO. Intended local visual operation is same-origin (UI served from the same server), so the candidate preserves it; the missing-Origin policy is the Director's call.

### LIVE_RESPONSE_INTEGRITY (I)
- CLAUDE_BASELINE_RESULT: command mutates successfully, then JSON serialization fails on Unit; client receives apparent failure
- CURRENT_MAIN_RESULT: **STILL_PRESENT — CONFIRMED VERBATIM.** Defect chain: `do_POST` runs `_run_command` FIRST (mutation completes), then `_json` calls plain `json.dumps` (no encoder). `result["create"]["unit"]` holds the raw `Unit` dataclass (with `Skin` Enum) from `parse_and_place` (`needs.py:67`). `TypeError: Object of type Unit is not JSON serializable` → socketserver closes with **NO HTTP status** (curl: exit 52, HTTP 000, 0 bytes). Client cannot distinguish success from server death.
- PROBE_SCOPE: real HTTP server (127.0.0.1, ephemeral port) + real HTTP client; 17-command in-process sweep; unique owners
- STATE_BEFORE: units `{welcome}`. STATE_AFTER: `{welcome, srvprobe1}`; 2 identical retries → `{welcome, srvprobe1, srvprobe1_1, srvprobe1_2}` (MPC-009 dedup prevents overwrite; each retry mints a new idea). Mutations do NOT auto-persist — server restart loses the un-receipted mutation.
- PUBLIC_REACHABILITY: shipped `/cmd` endpoint; any local client; no auth
- CLASSIFICATION: **FALSE_FAILURE** (primary); **RETRY_DUPLICATION_RISK** demonstrated as consequence
- NULL_RESULT: fix needed; zero consumers of `res["unit"]` repo-wide; `main_field.py:175` already sets the `"unit": u.id` convention; `dataclasses.asdict` rejected (Skin Enum still raises); `json.dumps(default=str)` rejected (hides future defects)
- ARGUS_RESULT: only `parse_and_place` entries fail JSON; malformed POSTs don't crash; retry duplicates rather than corrupts
- ACTION: **FIXED** — `parse_and_place` now returns a JSON-safe unit summary `{id, label, skin, x, y}`. Test: `form/mandell/live_response_integrity_test.py` (6/6 GREEN) — HTTP 200 (not conn drop), valid JSON, receipt↔`/state` consistency, retry → honest `<id>_1`

### DELL87_DESTINATION_COLLISION (J)
- CLAUDE_BASELINE_RESULT: store `k=1, z=ZZ`; `87 Replace k>z` → `z=1`, ZZ destroyed, ok=True
- CURRENT_MAIN_RESULT: **REPRODUCED exactly** (REPL PUBLIC_ENTRY_PATH + `execute_seed` INTEGRATION). Full Dell87 matrix: source-missing → False/`replace_missing:ghost`, unchanged; dest-missing → True; **dest-occupied → True, ZZ destroyed silently, no warning**; src==dst → True net no-op (shot + mutation recorded); empty-dest `k>` → True with MISLEADING receipt `Replace k->` (`new or old` fallback); normal rename ok. Dell85 same-matrix: dest-occupied → True, ZZ destroyed; src==dst → explicit no-op (`Move same identity`, no mutation); empty-dest → False/`malformed_move` (85 refuses what 87 accepts). English NOT a public route to either (87 blocked: destructive via English deferred; 85 "move k to z" intercepted as physical movement). Rollback: 87 pushes `shot_fn()` → Dell96 restores destroyed ZZ; 85 pushes none → ZZ permanently lost.
- PROBE_SCOPE: PUBLIC_ENTRY_PATH + INTEGRATION; authority from `git show HEAD:` (implementation, tests, registry, signatures, history, rollback)
- STATE_BEFORE/AFTER: per-case table in probe report (hidden_probe_c.md)
- PUBLIC_REACHABILITY: yes — raw Mandell on shipped REPL
- CLASSIFICATION: **UNSPECIFIED_OVERWRITE** — not DEFECT (no authority violated), not INTENDED_OVERWRITE (nothing specifies it), not AMBIGUOUS (no conflicting authorities), not UNKNOWN (behavior fully determined). MPC-009's dedup invariant covers UID/place creation — a different subsystem from `st.store` key rename.
- NULL_RESULT: no source anywhere (registry, signatures, docs, comments, tests, history) specifies overwrite as intentional; none forbids it either
- ARGUS_RESULT: full adversarial matrix; incidental findings — (1) 87 empty-new misleading receipt, (2) 87 `signatures.py` retains STALE pre-MPC-009 "substitutes" wording + stale line numbers, (3) 85 irrecoverable-overwrite asymmetry
- ACTION: **NO IMPLEMENTATION** (semantics unestablished). DIRECTOR DECISION REQUIRED: (A) accept overwrite as implicit key-rename semantics (+ optional registry/signature note); (B) refuse with `replace_occupied`/`move_occupied` error; (C) require explicit overwrite flag. Plus: is 85's irrecoverable asymmetry vs 87's snapshot recovery intended?

### IAC_STATE_CONTAMINATION (K)
- CLAUDE_BASELINE_RESULT: official `form.regress` isolated/safe; direct `iac_i_test` invocation overwrote `form/state/program_Operator.json` and destroyed saved alpha
- CURRENT_MAIN_RESULT: **CONFIRMED VERBATIM.** Official runner SAFE (70/70 GREEN, state byte-identical). Direct `python3 -m form.mandell.iac_i_test` → 36/36 green AND destroyed seeded Operator alpha (hash `47ee2dd2…` → `4fa6ebe9…`; units `['alpha','welcome']` → `['welcome']`).
- Mechanism: `iac_i_test.py:30` `Program()` (default owner "Operator") + inventory includes `"save"` → `_run_command "save"` → `program.save()` → `_path("Operator")` → atomic overwrite. Nursery embedded in same file → clobbered too.
- PROBE_SCOPE: seeded Operator canary + sha256 before/after; official runner vs direct invocation; sibling sweep across all `*_test.py` save paths
- PUBLIC_REACHABILITY: developer/operator path only; NOT public REPL/HTTP; NOT CI (CI runs only `form.regress --twice`/`--order rev`; regress `_copy_tree` excludes `form/state`)
- CLASSIFICATION: **DIRECT_TEST_INVOCATION_USER_STATE_RISK** (not CI contamination)
- NULL_RESULT: fix needed; production persistence semantics must NOT change (per directive)
- ARGUS_RESULT: sibling sweep found NO other contaminators (all other `.save()` callers use unique owners or temp paths)
- ACTION: **FIXED** — `iac_i_test.py` uses test-local unique owner (`iac1_test_<hex>`) at all 3 `Program()` sites. Verified: direct run 36/36 green, Operator hash unchanged, canary intact, save landed in `program_iac1_test_*.json`. Regression: `form/mandell/iac_isolation_test.py` (4/4 GREEN)

### STALE_SMOKE_DOC (L)
- CLAUDE_BASELINE_RESULT: docs instruct `python -m form.smoke_all` while `smoke_all.py` was deleted
- CURRENT_MAIN_RESULT: **STILL_PRESENT.** `form/smoke_all.py` absent (deleted `da6e154`); `fcnd_i_test.py:25` asserts NOT importable; yet 13 instruction files still reference it. Authoritative runner: `python -m form.regress` (CI runs `--twice` + `--order rev`).
- CLASSIFICATION: **STILL_PRESENT** (instructional docs; historical audit reports excluded per §17)
- NULL_RESULT: documentation-only truth correction authorized
- ARGUS_RESULT: n/a
- ACTION: **FIXED** — 13 files corrected to `python[3] -m form.regress` (historical-result comment preserved in FORM_MATRICES_FROM_SRC.md)

### MISSING_SESSION_RECEIPT (M)
- CLAUDE_BASELINE_RESULT: CLI `--load --owner Nobody` with no persistence file prints "Loaded session for Nobody." but creates fresh state
- CURRENT_MAIN_RESULT: **STILL_PRESENT** at CLI entry (`form/repl.py` `run()`). Semantics INTENTIONAL — `persist.load()` docstring: missing file yields fresh owner, writes no file. Observation defect only. (In-REPL resume/reload already corrected via ARGUS vector 9; CLI entry was missed.)
- PROBE_SCOPE: PUBLIC_ENTRY_PATH (real CLI flags, separate process)
- CLASSIFICATION: **STILL_PRESENT** (honesty/observation defect)
- NULL_RESULT: receipt-only correction; no semantic change
- ARGUS_RESULT: n/a
- ACTION: **FIXED** — CLI now checks `os.path.isfile(_persist_path(owner))` before load: `Loaded session for {owner}.` vs `No saved session for {owner}; started fresh.` (mirrors existing in-REPL guard)

### DELL85_VS_87 (N)
- CLAUDE_BASELINE_RESULT: apparently identical behavior in limited probes
- CURRENT_MAIN_RESULT: happy-path rename/move state-identical, but NOT duplicates — 5 real differences: (1) empty-dest: 85 refuses / 87 silently self-renames; (2) src==dst: 85 explicit no-op / 87 pop+reset with shot; (3) rollback: 87 snapshots / 85 none; (4) failure vocabulary differs; (5) shared core mutation idiom. History: both introduced `f913307` already-distinct; never the same implementation; never copied.
- CLASSIFICATION: **OVERLAPPING**
- NULL_RESULT: no authority treats them as duplicates; no action
- ARGUS_RESULT: differences found adversarially; registry gives distinct names/manors
- ACTION: none (no redesign authorized)

## INCOMPLETE LEADS (remain UNKNOWN per directive)
Full DuoBeta assessment, full security assessment, Flow-first precedence, complete Dell taxonomy, resource scaling, concurrency, symlink handling, external architectural comparison. NOT promoted to defects.

## FILES_CHANGED
- `form/mandell/registry.py` — Dell37 → Nurture / Nursery lifecycle (D)
- `form/mandell/CORE_I.md` — 2 stale Stream references → Nurture (D)
- `form/mandell/executor_leaf.py` — dead Stream branch removed (E, -10 lines)
- `form/repl.py` — set detail/goals parser fix (G); `--load` honest receipt (M)
- `form/dell_matrix/live_visual.py` — set detail/goals parser fix (G, /cmd path)
- `form/dell_matrix/needs.py` — JSON-safe unit summary in parse_and_place (I)
- `form/mandell/iac_i_test.py` — test-local unique owner (K)
- `form/regress.py` — 4 new suites registered
- 13 doc files — smoke_all → form.regress (L)
- NEW: `form/mandell/dell37_nurture_test.py`, `form/mandell/set_detail_goals_test.py`, `form/mandell/live_response_integrity_test.py`, `form/mandell/iac_isolation_test.py`

## SEMANTIC_DELTA
1. Dell37 public truth = Nurture (registry + docs); dead contradictory executable semantics removed — no live behavior change (branch was unreachable)
2. `set detail`/`set goals` now address the intended idea on both public front-ends (was: silent wrong-target mutation)
3. `/cmd` create responses are now complete JSON (was: connection drop after successful mutation)
4. Direct `iac_i_test` invocation can no longer destroy the default user's persisted state
5. `--load` receipt distinguishes loaded vs fresh sessions
6. No Dell87/Dell85 runtime semantics changed (J/N are decisions, not implementations)

## TEST_RESULTS
- New suites: dell37_nurture 6/6 · set_detail_goals 7/7 · live_response_integrity 6/6 · iac_isolation 4/4
- iac_i_test direct: 36/36 (post-fix, Operator state byte-identical)
- Full `form.regress` (authoritative, `--order fwd`): **GREEN, 74/74 entries, EXIT 0** (2026-10-03)
  - Note: first regress pass flagged `core_ii_smoke` 34/35 — its structural check pinned `primary == {n}` for all n in 0..50, which the authorized Dell37 dead-branch removal intentionally breaks. Updated to the true architectural invariant (a missing leaf branch is legitimate IFF the Dell is Core-I HANDLED); second pass 35/35.
- py_compile + AST parse clean on all touched Python files (CI flake8 E9/F63/F7/F82 gate equivalent; flake8 not installable in this env per PEP 668)

## CI_RESULTS
- Exact-head CI:
  - Python 3.10: PASS (runs `37135837108` on `09ddb40`; `37136215171` on `a6eba93`)
  - Python 3.11: PASS (same runs)
  - smoke: PASS — 3m57s on `09ddb40` (run `37135837129`), 3m28s on `a6eba93` (run `37136215247`)
  - github-advanced-security: **EVALUATION_UNAVAILABLE_QUOTA** — run `37135840614`, `SessionModelError`, HTTP 402, `errorCode: "quota"`; AI reviewer never analyzed the diff (standing pattern, never PASS)
- Head chain: `09ddb40` (all executable changes; CI green) → `a6eba93` (packet CI-results sync only; markdown-only delta; CI re-green). Executable tree identical across both; no executable change after the CI-validated head.
- Bounded substitute security review of product diff: PASS (no eval/exec/subprocess/socket/network/file-open/secret patterns in added lines; no workflow/dependency/authority changes)

## CANDIDATE_HEAD / PR_STATE
- CANDIDATE_HEAD: `a6eba93` (executable code identical to CI-green `09ddb40`; delta is packet markdown only)
- PR: https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/69 (base: main `72008c3`, head: `mpc-011-work`)
- PR_STATE: OPEN, CI green (3.10/3.11/smoke PASS on final head; security gate quota-unavailable). **NOT MERGED — awaiting Director merge authorization (AUTONOMY = NO).**

## RESULT_LEDGER
- NEW_CURRENT_DEFECTS (all fixed this round): G parser wrong-target mutation; I /cmd false-failure; K direct-test state destruction; M false load receipt; L stale smoke docs (13 files)
- ALREADY_FIXED: none (all 8 items reproduced on current main)
- FALSIFIED: cross-origin browser exploitability (NOT PROVEN — refused, not disproven); remote network reachability of /cmd (binds 127.0.0.1); Dell85/87 duplication (OVERLAPPING, not duplicate); CI contamination for K (official runner safe)
- AMBIGUOUS: J occupied-destination semantics (UNSPECIFIED_OVERWRITE — Director decision A/B/C); H missing-Origin policy (Director decision)
- UNKNOWN: browser-level cross-origin write/read; DNS rebinding; all O incomplete leads

## R1_DEBT_RECALCULATED
- C-R1-001 taxonomy: OPEN (Director authority)
- C-R1-003 Dell90/94/95 registry/runtime truth: OPEN, QUEUED
- C-R1-004 Dell37: RESOLVED (registry+docs corrected, dead branch removed, regression green)
- C-R1-005 Dell87: RESOLVED (naming; destination-collision now tracked as separate J-decision)
- C-R1-006 conditional slot: OPEN, narrowed
- C-R1-007: RESOLVED
- C-R1-008: CLOSED/FALSIFIED
- C-R1-009 stale names: OPEN, low priority
- NEW: J-decision (Dell85/87 occupied-destination semantics A/B/C + 85/87 snapshot asymmetry) — Director decision required
- NEW: H-decision (/cmd Origin policy + wildcard CORS) — Director decision required

## NEXT_BROKEN_LINK
Ranked by public reachability × data-integrity impact × security boundary × evidence strength (opinion excluded):
1. **J-decision** — occupied-destination rename silently destroys data with ok=True on a PUBLIC raw-Mandell path. Highest-consequence surviving finding; blocked on Director semantic ruling (A/B/C), not on engineering.
2. **H-decision** — /cmd has no auth and permissive CORS on localhost; cross-origin browser write is MECHANICALLY POSSIBLE but UNPROVEN. Bounded correction candidate ready; blocked on Director policy (missing-Origin question).
3. **C-R1-003** — Dell90/94/95 registry-truth audit (queued product work; proceeds once J/H decisions land or Director reprioritizes).

## NEXT_PRODUCT_CLUSTER
C-R1-003 registry-truth audit for Dell90/94/95 (same bounded TARGETED_SWARM method), contingent on J/H Director decisions. Do NOT presume correction or implementation before investigation.

## AUTONOMY
NO

## DIRECTOR_DECISION_REQUIRED
YES — (1) J occupied-destination semantics (A/B/C + snapshot asymmetry); (2) H /cmd Origin policy; (3) merge authorization for the candidate; (4) next cluster confirmation (C-R1-003 default)
