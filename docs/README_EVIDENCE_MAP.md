# DellMatrix README Code-Truth Evidence Map

**Research date:** 2026-10-04 America/Chicago
**Source SHA:** `f3c9007ea446af4aeb7f2f2f7a7a8add74a2704f` (production main at review time, PR #75 merge, 2026-10-04)
**Current production:** `ea9b76a` (main, post PR #79 merge, 2026-10-07 — Phase 5 admitted)
**Phase 5:** MERGED to production via PR #79 (Director admission PASS)

> This map is historical evidence for the 2026-10-04 review. It was not
> fully re-executed on the Phase-5 candidate. Phase-5 behaviors were
> candidate-only until PR #79 merged (2026-10-07); they are production
> behavior as of `ea9b76a`. The walkthrough evidence below remains dated
> historical evidence at the cited SHAs.
**Research env:** isolated clone at /tmp/dm_readme_research, Python 3.12.3, Linux
**Method:** source reads + live REPL walkthroughs with temp owners (`README_TEST_*`), state cleaned after.

---

## 1. Entrypoints

### 1a. `launch.py` (repo root)
- **SOURCE:** `launch.py` (20 lines)
- **REACHABILITY:** Public. `python launch.py [OwnerName]`, also `Launch DellMatrix.bat` / `.command`.
- **COMMAND:** `python launch.py` → prints banner → `from form.repl import run` → `run(owner="Operator")`.
- **OBSERVED RESULT:** VERIFIED WORKING. Launched REPL with owner `README_LAUNCH_TEST`, prompt `you>` appeared.
- **EVIDENCE STATUS:** Tested this session. No dependencies beyond stdlib (requirements.txt confirms: no non-stdlib packages in core runtime; Python 3.10+ required).

### 1b. `form/repl.py` — `run(owner, do_load)`
- **SOURCE:** `form/repl.py` (2783 lines), `run()` at line 2704, `main()` at 2773.
- **REACHABILITY:** Public via `python3 -m form.repl [--owner NAME] [--load]`, `python launch.py`, `python -m form` (via `form/__main__.py` → `form.open.main()`, which only renders — does NOT start REPL).
- **WHAT IT DOES:** Opens/creates a `Program` for owner, binds Mandell language, prints render, then loops on `you>` input. Each line mints a UUIDv4 interaction_id, then dispatches via `_dispatch_public_line` in this order: ROS-I read-only commands → DuoBeta learn → KIE why → lifecycle → Greek floor operators → Mandell flow (`>`/`:`) → seed execution → English multi-step composer ("and then") → `translate(line)` → `_execute_intent`.
- **OBSERVED RESULT:** VERIFIED WORKING. All walkthroughs below used `python3 -m form.repl --owner <name>`.
- **EVIDENCE STATUS:** Tested this session (piped stdin, EOF exits cleanly).

### 1c. `form/open.py` — `Program` class + `open_program`
- **SOURCE:** `form/open.py` (1631 lines). `class Program` at line 103, `open_program(owner)` at 1581, `confirm_proposal(pid)` at 1334.
- **REACHABILITY:** Python API (`from form.open import open_program`). Not directly user-facing; REPL is the public path.
- **KEY METHODS (verified present):** `confirm_proposal`, `nursery` (Nursery with proposals), `cube.session.plane.units` (Idea store), `place`, `render`, `save/load` via `form.persist` / `form.persist_rest`, `look_around`, `zoom_to`, `evolve`, `audit`, Greek/floor ops, `spatial_*`, lifecycle, DuoBeta hooks.
- **OBSERVED RESULT:** `open_program` + `confirm_proposal` + `persist_rest.save/load` verified working in walkthroughs and API probes.
- **EVIDENCE STATUS:** Tested this session.

### 1d. Command registry
- **SOURCE:** The canonical operator registry is `form/mandell/registry.py` (True Dell registry, numbered operators CORE_I 00-50, CORE_II 51-99). Dispatch is in `form/repl.py::_dispatch_public_line` → `form/mandell/translate.py::translate()` → `_execute_intent`. `form/dell_matrix/actions_registry.py` provides UI action lists (`actions_flat`, `actions_for_mode`) for visual modes, not the language operator definitions.
- **CORRECTION (2026-10-04):** An earlier draft incorrectly called `actions_registry.py` the Dell/operator registry. The canonical registry is `form/mandell/registry.py`.
- **REACHABILITY:** Internal. Users interact via English lines at the `you>` prompt.
- **EVIDENCE STATUS:** Code-verified. `help` lists 9 categories: create, knowledge, learn, explain, save, recover, look, dell, system.

---

## 2. Docs claims vs code

### `docs/INSTALL.md`
- **CLAIMS:** Python 3.10+, `python launch.py`, offline core loop, acceptance path `create → grow → confirm → sphere → save → load → visual`.
- **MATCHES CODE:** YES. All verified working this session (see walkthroughs). Windows `.bat` / Mac `.command` launchers exist at root but were NOT executed (Linux env); do not claim tested.

### `docs/TUTORIAL.md`
- **CLAIMS:** `tutorial` command walks the acceptance path; manual table matches.
- **MATCHES CODE:** YES. `tutorial` ran and walked steps 1–3+ correctly.

### `docs/START_HERE.md`
- **CLAIMS:** Labeled "(DEV)". Commands `create … detail: … goals: …`, `what next`, `ready`, `history`, `undo`, `self`.
- **MATCHES CODE:** Partially verified. `create` with `detail:`/`goals:` inline syntax observed working in help text; `what next`/`ready` not executed this session — UNVERIFIED, do not claim.

### Root `README.md` (current)
- **CLAIMS:** "**Status:** [User-ready (offline)](docs/USER_READY.md)".
- **MATCHES CODE:** NO — unsupported blanket claim. The system works for the tested acceptance path, but "user-ready" implies a completeness not established by evidence (known RED suites in CI, partial features below). This is the claim the rewrite must remove/replace with a scoped status table.

---

## 3. Walkthrough results (historical: all on f3c9007, temp owners, cleaned up, 2026-10-04)

### W1. Create / store / reload an idea — WORKING
- **COMMANDS:** `create an idea called walktest` → `save` → new process `python3 -m form.repl --owner README_TEST_02 --load`
- **OBSERVED:** `Created idea: "walktest" id=walktest`; save wrote `form/state/program_README_TEST_02.json`; `--load` printed "Loaded session for README_TEST_02."
- **STATUS:** VERIFIED.

### W2. Propose / review / confirm — WORKING
- **COMMANDS:** `grow ideas 2` → `proposals` → `confirm all`
- **OBSERVED:** Grow executed Dell 13, nursery pending 1; `proposals` listed `welcome_walktest_4794 [evolved]` with affinity; `confirm all` → "Confirmed 1 proposal(s)."
- **STATUS:** VERIFIED.

### W3. Inspect relationships — WORKING
- **COMMANDS:** `lineage welcome_walktest_4794`, `rank`, `look`
- **OBSERVED:** lineage showed parents/affinity/status; `rank` sorted 3 proposals by affinity; `look` showed facing/range/entities.
- **STATUS:** VERIFIED. (Note: `lineage` needs the proposal ID, not the idea label — `lineage walktest` returned "No proposal or idea for id".)

### W4. Resonance / harmony — PARTIAL
- **COMMANDS:** `resonance` → "Not understood".
- **OBSERVED:** No REPL command named `resonance`/`harmony`. Resonance exists as library code (`resonance_rank` in `form/dell_matrix/first_person.py`) and surfaces in `page` output as `res=` scores and in `rank` affinity ordering. Phase-3 geometry proofs exist as test files, not user commands.
- **STATUS:** PARTIAL — scoring machinery exists and is exercised by rank/page; no direct user-facing resonance command. Do not document as a runnable command.

### W5. Supersession / history — WORKING (with correction)
- **Python API:** `supersede_proposal(p, old_id, words=...)` → receipt with `{'ok': True, 'old_id': ..., 'new_id': ...}`, old lifecycle → `superseded`. VERIFIED WORKING.
- **REPL:** `supersede idea <id> with <words>` → VERIFIED WORKING with genuine confirmed proposal ID (re-tested 2026-10-04). Earlier failure was due to testing with unconfirmed/unknown ID.
- **History:** `history 3` → "History · 0 notes (empty — act, then history fills)". Command exists; empty state honest.
- **STATUS:** API WORKING; REPL WORKING with genuine ID. 
- **CORRECTION (2026-10-04):** An earlier draft labeled the REPL command BROKEN based on a test with an unconfirmed ID. That conclusion is withdrawn; the retest with a genuine confirmed ID succeeds.

### W6. Visual output — WORKING
- **COMMANDS:** `visual`, `sphere`, `lattice`
- **OBSERVED:** `visual` generated `DellMatrix_UI.html` (29KB, offline); `sphere` → "Form → sphere (skin=sphere)"; `lattice` rendered harmonic lattice grid.
- **STATUS:** VERIFIED (file generation; browser rendering not tested).

### W7. DuoBeta learn lifecycle — WORKING (with real gating)
- **COMMANDS:** `learn propose refinement 35 from outcome 1` → `learn inspect 2` → `learn gate 2` → `learn ledger`
- **OBSERVED:** Proposal staged; inspect showed details; **gate REJECTED with `forbidden_kind`** (real policy enforcement, not a rubber stamp); ledger showed `[REJECTED]`.
- **STATUS:** VERIFIED. Note: proposals are session-staged; `learn ledger` in a fresh process showed empty (not persisted across processes in this test).

### W8. `tutorial` — WORKING
- **COMMAND:** `tutorial`
- **OBSERVED:** Walked acceptance path steps (create → grow → confirm → …).
- **STATUS:** VERIFIED.

### Additional verified commands
`save`, `load` (via `--load`), `confirm <id>`, `proposals`, `help` (+9 categories), `quit`/`exit`, `outcomes` ("No outcomes recorded." — honest empty).

---

## 4. `python launch.py` / platform / deps

- **SOURCE:** `launch.py` → `form.repl.run(owner)`.
- **OBSERVED:** Works on Python 3.12.3, Linux, zero third-party deps (requirements.txt: stdlib only for core runtime; SIDE modules like `form/llm` may need extras).
- **Offline:** TRUE for core loop — no network calls in tested paths.
- **Windows/Mac launchers:** `Launch DellMatrix.bat`, `Launch DellMatrix.command` exist but were NOT executed. Do not claim tested platforms.

---

## 5. Directory roles

| Dir | Role | Evidence |
|-----|------|----------|
| `form/` | **LIVE runtime** (Python) | All imports resolve here; `src/README.md` itself says "Live runtime is `form/` only". |
| `src/` | **FROZEN legacy** (JavaScript) | `src/README.md`: "# src/ — LEGACY (frozen). Do not extend. This is the old JavaScript dual-era DellMatrix." Only "ported from" comments reference it. |
| `preform/` | **Historical** (docs/notes) | Zero imports from `form/` (`grep` for `from preform`/`import preform` in `form/` → none). |
| `docs/` | Documentation (large, mixed currency) | Many audit/packet docs; currency varies. |

---

## 6. Working vs broken/partial

### WORKING (verified this session on f3c9007)
- REPL launch (`launch.py`, `python3 -m form.repl`), `--owner`, `--load`, EOF/quit
- `create an idea called <name>` (with strength/detail/goals coaching)
- `grow ideas N` (Dell 13, nursery proposals)
- `proposals`, `confirm <id>`, `confirm all`
- `save` / `load` (file persistence + reload)
- `lineage <proposal-id>`, `rank` (affinity-ordered), `look`, `page`
- `sphere`, `lattice` (skin/form change + grid render)
- `visual` (offline HTML generation)
- `tutorial`, `help` (+9 categories)
- `history`, `outcomes` (honest empty states)
- DuoBeta `learn propose/inspect/gate/ledger` (real policy gating)
- Python API: `open_program`, `confirm_proposal`, `persist_rest.save/load`, `supersede_proposal`
- Offline operation; stdlib-only core deps; Python 3.10+ per requirements

### PARTIAL
- **Resonance/harmony:** scoring machinery real (`resonance_rank`, affinity in rank/page); no direct user command. Phase-3 proofs are test files, not features.
- **DuoBeta learn:** works within a session; cross-process persistence of staged proposals not observed.
- **`visual`:** file generates; in-browser rendering untested.

### BROKEN / GAP (do not document as working)
- **REPL `supersede idea <id> with <words>`:** fails on the normal user flow (`unknown_predecessor` for labels, `not_on_plane` for proposal IDs). Python API works.
- **`lineage` by idea label:** requires proposal ID; label lookup fails.
- **Root README "User-ready (offline)":** unsupported blanket claim.

### UNVERIFIED (do not claim)
- Windows `.bat` / Mac `.command` launchers; `what next`, `ready`, `undo`, `replay`, `reissue`, Spanish/French commands (`es`/`fr` claimed in README — not executed); `live`, `zoom`, avatar/persona features; any LLM/network features.

---

## 7. Honest status assessment

DellMatrix at f3c9007 is a **working offline idea environment** for its tested core loop: create → grow → propose → confirm → inspect → save → reload, plus DuoBeta learning with real policy gates and offline HTML visual export. The claim "User-ready (offline)" overstates: it implies general readiness that the evidence (partial features, REPL gaps in supersession, CI RED suites on the repair branch, unverified platforms/languages) does not support. A scoped status table (WORKING / PARTIAL / IN REPAIR / PLANNED) with the exact reviewed SHA is the honest replacement.

---

## 8. Key sources for README claims

- Entrypoints: `launch.py`, `form/repl.py` (run/dispatch/help), `form/__main__.py`, `form/open.py` (Program)
- Routing: `form/mandell/translate.py`, `form/dell_matrix/actions_registry.py`
- Persistence: `form/persist.py`, `form/persist_rest.py`, `form/mandell/checkpoint_generation.py`
- Nursery/lifecycle: `form/dell_matrix/nursery.py`, `form/dell_matrix/confirm_lineage.py`, `form/lifecycle.py`
- Supersession: `form/mandell/supersession.py`, `form/mandell/core_i_recovery.py`
- Learning: DuoBeta handlers in `form/repl.py::_handle_learn_command`, `form/duobeta/`
- Resonance: `form/dell_matrix/first_person.py::resonance_rank`, `form/mandell/harmonic_truths.py`
- Visual: `visual` command in repl → `DellMatrix_UI.html`
- Legacy note: `src/README.md`, `form/LEGACY.md`
- Deps: `requirements.txt` (Python 3.10+, stdlib-only core)

---

## 9. R6.1 capability-authority circuit (candidate stage, 2026-10-07)

> **Status:** CANDIDATE — implemented on branch `gdp-phase6-r61-authority`
> (GDP_PHASE_6_CAPABILITY_AUTHORITY_CIRCUIT, Director 2026-10-07). NOT
> merged to production. NOT certified. The claims below describe the
> candidate branch, verified by the registered proof suite.

- **SOURCE:** `form/dell_matrix/acceptance_policy.py` (grant issuance,
  attenuation, revocation, `check()` grant branch), new module
  `form/dell_matrix/agent_authority.py` (trusted dispatch adapter),
  `form/open.py::Program.confirm_proposal` (`_subject` trusted binding),
  `form/dell_matrix/confirm_lineage.py` (writer re-validation +
  test-only `_BETWEEN_STAGES` hook, None in production).
- **WHAT IT DOES:** opaque session-scoped grant handles
  (`grant_<uuid4hex>`) backed by canonical issuance records; root
  issuance is trusted-path-only; `attenuate_grant` narrows only
  (subject/owner/operation equality, target/content narrow-or-equal,
  strictly decreasing delegation depth); `_grant_chain_valid`
  recursively validates the full ancestor chain at execution time;
  revocation of any ancestor denies unfinished descendants; committed
  history survives revocation/restart; audit references grants by
  sequence number, never by handle value.
- **SCOPE:** the `nursery.confirm` capability only. Human approval and
  opt-in paths unchanged. Threat boundary: untrusted agent requests
  through mediated interfaces; NOT malicious in-process Python; NOT
  concurrent-execution race safety (single-threaded dispatcher).
- **PROOFS:** `form/mandell/r61_authority_test.py` — 140/140 checks
  (in-process INTEGRATION + CROSS_PROCESS via fixed child scripts
  `form/mandell/r61_child.py` with JSON arguments), registered in
  `form/regress.py` LIST. `form/mandell/r61_oracle_test.py` — 25/25
  independent-oracle checks (stdlib-only model vs production, 11
  scenarios, sensitivity proven).
- **AMEND (Director 2026-10-07):** content defect fixed — `content=None`
  is unconstrained (documented), every Mapping including `{}` is hashed
  and bound; attenuation never drops inherited restrictions. Agent
  identity boundary: `bind_agent(program, trusted_subject)` creates a
  subject-bound `AgentEndpoint` whose request surface is exactly
  `confirm(pid, grant_handle)` — no subject/issuer/producer/review
  context accepted; mint/revoke/controller methods absent from the
  surface.
- **EVIDENCE STATUS:** candidate-branch only. Awaiting Director review;
  no merge without authorization.
