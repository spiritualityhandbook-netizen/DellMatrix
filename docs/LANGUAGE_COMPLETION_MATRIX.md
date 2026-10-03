# LANGUAGE COMPLETION MATRIX — GDP-001 Phase 0, Requirement 2

**Branch:** `gdp-p0r2` · **Base:** `1c90cecf9e5bbbf6bda055f3157ecada299f6840` (post-PR-#69)
**Date:** 2026-10-03 · **Author:** SUSX100 (Uni Ω) · **Status:** Phase-0 reconciliation evidence

This matrix reconciles, for every active Dell, the eight R2 completion
dimensions. **Every cell is grounded in code evidence (`file:line`), not
opinion.** Where evidence ends, the cell says UNKNOWN — semantics are never
invented to fill a gap.

## Column definitions and shared evidence

| Column | Meaning | Shared evidence (applies to every row unless Notes says otherwise) |
|---|---|---|
| REGISTERED | Present in the authoritative registry | `form/mandell/registry.py:16-66` (`DELLS` 0–99); `form/mandell/address_space.py:36-88` (`RESERVED_DOMAIN`) |
| PARSEABLE | `parse_seed("NN[Name]")` succeeds | `form/mandell/seed.py:178-182` (registry lookup gate; `ok=False` "unknown Dell {n}" otherwise) |
| TRANSLATABLE | English can produce an Intent naming this Dell **that reaches execution**. YES = routed by `semantic_router` (CORRESPONDENCE or SSI-I Core-II). PARTIAL = English-triggerable only via direct `_execute_intent` handlers that bypass router/executor. NO = no English path. | CORRESPONDENCE `form/mandell/semantic_router.py:140-316` (14 pairs); SSI-I `form/repl.py:2487` → `semantic_router.py:506`; Intent emissions `form/mandell/translate.py:395-617`; direct handlers `form/repl.py:2200-2250,2296-2437` |
| EXECUTABLE | A real executor path exists for the Dell | `form/mandell/registry.py:91-152` (`execution_standing`); dispatcher `form/mandell/executor.py:20-66`; `core_i_ops.py:8` (HANDLED); `chain_exec.py:347` |
| PUBLICLY_REACHABLE | Reachable from the public REPL path | `form/repl.py:2555` (`looks_like_seed` → `observe_seed_execution` → `execute_seed`) covers every registered Dell; English-reachable subset = TRANSLATABLE |
| TESTED | Exercised by at least one named test module | Method: number-pattern grep (`NN[`, `dell NN`, `primary == NN`, `execute_core_ii(..., NN`, …) over every `form/**/*_test.py` + smoke modules. Name-only coverage may be missed; absence is a **gap signal**, not proof of no coverage. |
| SEMANTICALLY_CONSISTENT | Implementation matches the registry manor/name semantics | Core I leaf audit: `form/mandell/executor_leaf.py` per-branch verdicts (REAL / PARTIAL / STUB). Core II audit: `form/mandell/query_ops.py`, `spectrum_ops.py`, `core_ii_exec.py`, `chain_exec.py` verdicts. |
| PERSISTENT | The Dell's primary state effect survives process restart | Payload `form/persist.py:150-215` (plane units, avatar, nursery, lattice, history last-24, core_ii durable, outcome ledger); `serialize_core_ii` / `CORE_II_DURABLE`; `form/mandell/core_ii_persist_test.py` |

**Value key:** YES = verified · PARTIAL = verified but limited (see Notes) ·
NO = verified absent/failing · N/A = not applicable (no state effect beyond the
history note; history persists last-24 per `form/persist.py:198`) ·
UNKNOWN = not verified in R2 (never fabricated).

**Standing key (EXECUTABLE):** ACTIVE = real dispatch path ·
ACTIVE_REFUSAL = dispatches to an honest `ok=False` refusal ·
RESERVED_NOT_ACTIVE = registered but no production executor (honest skip in
chains; **see §4 finding re single-seed path**).

## §1 — Core I Dells (0–50)

| Dell | Name | REGISTERED | PARSEABLE | TRANSLATABLE | EXECUTABLE | PUBLICLY_REACHABLE | TESTED | SEMANTICALLY_CONSISTENT | PERSISTENT | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 00 | Nova | YES | YES | NO | ACTIVE | YES | YES (4 mods) | NO — STUB | N/A | Leaf `executor_leaf.py:67-71`: messages only ("floor stays locked"), touches nothing. |
| 01 | Initiate | YES | YES | NO | ACTIVE | YES | YES (3) | NO — STUB | N/A | Leaf `:72-73`: prints `owner=`; no mutation. |
| 02 | Persona | YES | YES | NO | ACTIVE | YES | YES (5) | PARTIAL | N/A | Reads `program.avatar_status()`; prints only (`:74-76`). |
| 03 | Logic | YES | YES | NO | ACTIVE | YES | YES (5) | PARTIAL | N/A | Prints static constraints; only mutation is the history note (`:77-86`). |
| 04 | Transform | YES | YES | PARTIAL | ACTIVE | YES | YES (1) | YES | YES | Leaf mutates avatar + `lattice.toggle_form()` (`:87-107`); lattice persisted (`persist.py:196`). English: turn/sit/stand/jump via direct `_execute_intent` handlers (`translate.py:537-543`, `repl.py:2296-2437`) — bypasses router. Jump sets JUMP then immediately STAND in the same call (`executor_leaf.py:~100`). |
| 05 | Tone | YES | YES | PARTIAL | ACTIVE | YES | YES (2) | YES | YES | `program.face.set(expr)` (`:108-117`); avatar persisted (`persist.py:176`). English: express → direct handler (`translate.py:546-550`). |
| 06 | Cycle | YES | YES | YES | ACTIVE | YES | YES (3) | YES | YES | `program.grow_ideas(n)` → nursery proposals (`:118-125`); nursery persisted. Router-routed (CORRESPONDENCE). |
| 07 | Link | YES | YES | NO | ACTIVE | YES | YES (1) | YES | YES | `place_idea` → `program.place()` → plane units (`:126-127`); plane persisted (`persist.py:161-164`). |
| 08 | Create | YES | YES | PARTIAL | ACTIVE | YES | YES (17) | YES | YES | Leaf creates unit (`:128-129`); typed args enforced, bad args → honest `ok=False` (`executor_leaf.py:31-51`, TOAM). English "place"/"create" → `p.place()` **directly**, never touches router/executor (`phrases.py:11-13`, `repl.py:2200-2250`) — parallel create authority (R2 §4). |
| 09 | Show | YES | YES | PARTIAL | ACTIVE | YES | YES (8) | PARTIAL | READ-ONLY | Real reads (`visual()`, `avatar_status()`, `lattice.render_ascii()`); fallback prints literal `__RENDER__` placeholder (`:130-142`). English: show/help/avatar_status → direct handlers. |
| 10 | Keep | YES | YES | YES | ACTIVE | YES | YES (8) | YES | YES | `program.save()` writes session file (`:143-148`). Router-routed (CORRESPONDENCE). |
| 11 | Architect | YES | YES | YES | ACTIVE | YES | YES (4) | PARTIAL | READ-ONLY | Reads owner/units/lattice; only mutation is history note (`:149-156`). |
| 12 | Test | YES | YES | YES | ACTIVE | YES | YES (12) | PARTIAL | READ-ONLY | `hasattr` checks incl. **tautology** `len(units) >= 0` (always PASS, inflates score) (`:157-170`). |
| 13 | Loop | YES | YES | YES | ACTIVE | YES | YES (3) | YES | YES | `program.grow_ideas(cycles)` → nursery proposals (`:171-178`). |
| 14 | Bind | YES | YES | NO | ACTIVE | YES | YES (1) | YES | YES | `place_idea` → new cube unit (`:179-180`). |
| 15 | Map | YES | YES | YES | ACTIVE | YES | YES (6) | YES | YES | `lattice.to_cube/sphere/core/flower()` (`:181-189`); lattice persisted. |
| 16 | Decay | YES | YES | NO | ACTIVE | YES | YES (2) | YES | UNKNOWN | `program.enhance.decay(factor)` mutates enhance state (`:190-203`); enhance persistence not verified in R2. |
| 17 | Shadow | YES | YES | NO | ACTIVE | YES | YES (1) | NO — STUB (theater) | N/A | Announces "Shadow track (parallel — not live)"; **no track object created anywhere** (`:204-208`). |
| 18 | Mirror | YES | YES | NO | ACTIVE | YES | YES (5) | PARTIAL | N/A | Reads all plane units; prints only (`:209-216`). |
| 19 | Drive | YES | YES | PARTIAL | ACTIVE | YES | YES (1) | YES | YES | `avatar.set_locomotion()` + `avatar.step()` (`:217-227`). English: walk/run/jog/backstep/strafe → direct `p.avatar.step()` (`repl.py:2314-2360`) — bypasses router; duplicates the leaf arm. |
| 20 | Alpha | YES | YES | NO | ACTIVE | YES | YES (4) | PARTIAL | READ-ONLY | Reads units/lattice; prints summary (`:228-234`). |
| 21 | Merge | YES | YES | NO | ACTIVE | YES | YES (3) | YES | UNKNOWN | **Dead leaf** (`:235-236`); production path `live_identity.merge_live` (`executor.py` intercept, before leaf). Live-identity persistence not audited in R2. |
| 22 | Split | YES | YES | NO | ACTIVE | YES | YES (3) | YES | UNKNOWN | **Dead leaf** (`:237-246`); production path `live_identity.split_live`. |
| 23 | Lock | YES | YES | NO | ACTIVE | YES | YES (4) | YES | YES | `program.sandbox_on()` (`:247-249`); sandboxes in plane payload (`persist.py:164`). |
| 24 | Unlock | YES | YES | NO | ACTIVE | YES | YES (3) | YES | YES | `program.sandbox_off()` (`:250-252`). |
| 25 | Pulse | YES | YES | PARTIAL | ACTIVE | YES | **NO** | YES | UNKNOWN | `program.enhance_on()` / `program.pulse()` (`:253-260`); enhance persistence not verified. English: enhance_on/pulse → direct handlers (`translate.py:609-613`). **Test gap.** |
| 26 | Temp | YES | YES | NO | ACTIVE | YES | **NO** | YES | UNKNOWN | `enhance_on()/enhance_off()` toggle (`:261-275`); persistence not verified. **Test gap.** |
| 27 | Checkpoint | YES | YES | YES | ACTIVE | YES | YES (9) | YES | YES | **Dead leaf** (`:276-285`); production `core_i_ops.apply_core_i` (`core_i_ops.py:20`). Checkpoint generations sealed via program member (`persist.py:203-205`). |
| 28 | Rollback | YES | YES | YES | ACTIVE | YES | YES (8) | YES | YES | **Dead leaf** (`:286-289`); production `core_i_ops`. Restores persisted state. |
| 29 | Compress | YES | YES | NO | ACTIVE | YES | **NO** | YES | YES | `distill_label()` + `place_idea(..., Skin.SEED)` (`:290-293`). **Test gap.** |
| 30 | Expand | YES | YES | NO | ACTIVE | YES | **NO** | YES | YES | `place_idea(..., Skin.CUBE)` (`:294-304`). **Test gap.** |
| 31 | Simulate | YES | YES | YES | ACTIVE | YES | YES (1) | PARTIAL | N/A | Labeled "dry-run — no mutation" yet **mutates `program.history`** via `note_seed` (`:305-311`). Self-contradicting label. |
| 32 | Pause | YES | YES | PARTIAL | ACTIVE | YES | YES (1) | YES | UNKNOWN | `program.enhance_off()` or avatar → IDLE (`:312-318`); enhance persistence not verified. English: stop/enhance_off → direct handlers (`translate.py:534,611`). |
| 33 | Resume | YES | YES | NO | ACTIVE | YES | YES (1) | YES | YES | Avatar → WALK, optionally `enhance_on()` (`:319-327`); avatar persisted. |
| 34 | Stamp | YES | YES | YES | ACTIVE | YES | YES (4) | YES | UNKNOWN | **Dead leaf** (`:328-333`); production `core_i_ops`. `last_stamp` persistence not verified. |
| 35 | Discover | YES | YES | YES | ACTIVE | YES | YES (15) | YES | READ-ONLY | **Dead leaf** (`:334-341`); production `core_i_ops`. Reads persisted nursery. |
| 36 | Inject | YES | YES | NO | ACTIVE | YES | YES (1) | YES | YES | `place_idea(name, Skin.SEED)` (`:353-358`). |
| 37 | Nurture | YES | YES | YES | ACTIVE | YES | YES (12) | YES | YES | **No leaf branch by design** (MPC-011 Stream→Nurture correction); production `core_i_ops`. Nurture proposals persisted. R2 reconciliation test pins this (`r2_registry_reconciliation_test.py`). |
| 38 | Distill | YES | YES | NO | ACTIVE | YES | **NO** | YES | YES | `distill_label()` + `place_idea(..., Skin.SEED)` (`:359-368`). **Test gap.** |
| 39 | Schema | YES | YES | NO | ACTIVE | YES | YES (2) | PARTIAL | READ-ONLY | Real `hasattr` validity checks; prints VALID/INVALID (`:369-385`). |
| 40 | TokenCount | YES | YES | YES | ACTIVE | YES | YES (6) | YES | READ-ONLY | **Dead leaf** (`:386-396`); production `core_i_ops`. Reads state; honest measure. |
| 41 | Sanitize | YES | YES | NO | ACTIVE | YES | **NO** | PARTIAL | N/A | Name overclaims: real regex redaction **only of the ephemeral label string**; sanitizes no stored state (`:397-408`). **Test gap.** |
| 42 | Retry | YES | YES | YES | ACTIVE | YES | YES (2) | YES | YES | Delegates to `program.replay_exec(1)` — genuine recursive re-execution via `execute_seed` (`:409-420`). No depth guard visible at leaf (bounded by history length). |
| 43 | Fallback | YES | YES | NO | ACTIVE | YES | **NO** | NO — STUB | N/A | Prints safe-path instructions; no state effect (`:421-427`). **Test gap.** |
| 44 | Bridge | YES | YES | NO | ACTIVE_REFUSAL | YES | YES (2) | YES | N/A | **Dead leaf** (`:428-436`, was message-only STUB); production `core_i_ops` returns honest `ok=False` / `bridge_unavailable` (origin offline). R2 honesty test pins this. |
| 45 | Translate | YES | YES | NO | ACTIVE | YES | **NO** | YES | N/A | Real `form.mandell.bridge.bridge(label)` → mandel/english dict (`:437-441`). **Test gap.** |
| 46 | Rank | YES | YES | NO | ACTIVE | YES | **NO** | PARTIAL | READ-ONLY | Reads `ranked_proposals()`/`list_proposals()`, sorts, prints; no mutation (`:442-450`). **Test gap.** |
| 47 | Embed | YES | YES | PARTIAL | ACTIVE_REFUSAL | YES | YES (2) | YES | N/A | **Dead leaf** (`:451-453`); production `core_i_ops` honest `ok=False` / `embed_unavailable`. English "visual" builds `09[Show] >> 47[Embed]` (`translate.py:607`) but `_execute_intent` handles "visual" via direct show path. |
| 48 | Macro | YES | YES | NO | ACTIVE | YES | YES (1) | YES | YES | `replay_exec(n)` / `macro_seed(n)` over real history (`:454-472`). |
| 49 | Profile | YES | YES | NO | ACTIVE | YES | YES (2) | PARTIAL | READ-ONLY | Reads `program.status()`; prints (`:473-482`). |
| 50 | Manifest | YES | YES | NO | ACTIVE | YES | YES (4) | PARTIAL | YES | "Acceptance" arm message-only; label arm really creates a unit (`:483-487`). |

**Core I summary:** 51 registered · 51 parseable · 14 translatable-YES + 8 PARTIAL ·
51 executable (49 ACTIVE + 2 ACTIVE_REFUSAL) · 51 publicly reachable ·
42 tested-YES / 9 test gaps (25, 26, 29, 30, 38, 41, 43, 45, 46) ·
SEMANTICALLY_CONSISTENT: 34 YES / 13 PARTIAL / 4 NO (00, 01, 17, 43).

## §2 — Core II Dells (51–99)

Dispatch: single-atom or multi-atom seeds with a Core-II primary route to
`chain_exec.execute_chain` (`form/mandell/executor.py:63-64`), then to
`core_ii_exec` families: QUERY_DELLS → `query_ops` (`core_ii_exec.py:76`);
53 inline scope (`:78`); control 60–66 → `control_runtime`
(`core_ii_exec.py:80-131`); 80–99 → `spectrum_ops` (`core_ii_exec.py:132`).
The `unmapped` else in `core_ii_exec.py:76-137` is unreachable in production
(verified: family sets cover 51–99 exactly) and honest when hit.

| Dell | Name | REGISTERED | PARSEABLE | TRANSLATABLE | EXECUTABLE | PUBLICLY_REACHABLE | TESTED | SEMANTICALLY_CONSISTENT | PERSISTENT | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 51 | Select | YES | YES | YES | ACTIVE | YES | YES (17) | YES | PARTIAL | `query_ops.py:14` sets `st.selected`, writes `st.last_result` (`core_ii_exec.py:76`). SSI-I canonical "dell 51" / `Intent("select",…)` (`translate.py:510`). CoreIIState durable subset only (see PERSISTENT def). |
| 52 | Filter | YES | YES | YES | ACTIVE | YES | YES (6) | YES | PARTIAL | `query_ops.py:19` filters `st.selected` in place. |
| 53 | Scope | YES | YES | YES | ACTIVE | YES | YES (7) | YES | PARTIAL | Inline `st.scope = lab or "plane"` (`core_ii_exec.py:78`); notably absent from QUERY_DELLS. |
| 54 | Query | YES | YES | YES | ACTIVE | YES | YES (4) | YES | PARTIAL | `query_ops.py:24`; read-only hits → `st.last_result`. |
| 55 | Set | YES | YES | YES | ACTIVE | YES | YES (12) | YES | PARTIAL | `query_ops.py:29`: `st.store[key]=val` + snapshot before write. |
| 56 | Get | YES | YES | YES | ACTIVE | YES | YES (4) | YES | PARTIAL | `query_ops.py:35`; MISSING/empty handled explicitly. English: get/find → `Intent("get"/"find", 56, …)` (`translate.py:480-496`). |
| 57 | Compare | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `query_ops.py:45` `eval_predicate`; honest `ok=False` on `type_mismatch`. |
| 58 | Match | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `query_ops.py:54` substring-filters `st.selected`. English: `Intent("match", 58, …)` (`translate.py:518`). |
| 59 | Route | YES | YES | YES | ACTIVE | YES | YES (4) | YES | PARTIAL | `query_ops.py:60` sets `st.route`. |
| 60 | Branch | YES | YES | YES | ACTIVE | YES | YES (8) | PARTIAL | PARTIAL | Single atom: evaluates cond, records frame, executes nothing (`core_ii_exec.py:80`). In chain: `_run_control` (`chain_exec.py:237-267`) runs the chosen body, skips the other. |
| 61 | Join | YES | YES | YES | ACTIVE | YES | YES (7) | PARTIAL (vacuous in blocks) | PARTIAL | Inside control blocks the join atom runs at `chain_exec.py:335` **before** `_run_control` writes body results (`:341`) → `incoming` always 0 → `ok=True` vacuous. Message honestly reports `incoming=0`, but join semantics are theater in that position (R2 §4). |
| 62 | Parallel | YES | YES | YES | ACTIVE | YES | YES (1) | PARTIAL | PARTIAL | Body executes **sequentially in order** (`chain_exec.py:269-271`); no parallelism. Message "offline_deterministic" is honest about it. |
| 63 | Sequence | YES | YES | YES | ACTIVE | YES | YES (2) | PARTIAL | PARTIAL | Records frame only (`core_ii_exec.py:109`); chain bodies are inherently ordered, so the frame adds nothing as a single atom. |
| 64 | Until | YES | YES | YES | ACTIVE | YES | YES (2) | PARTIAL | PARTIAL | Single atom: frame only. In chain: loops body until cond true with `bound_of` limit; `bound_reached` fails honestly (`chain_exec.py:274-303`). |
| 65 | While | YES | YES | YES | ACTIVE | YES | YES (2) | PARTIAL | PARTIAL | Same shape as 64 (zero-it/loop/bound) (`chain_exec.py:304-331` region). |
| 66 | ForEach | YES | YES | YES | ACTIVE | YES | YES (3) | PARTIAL | PARTIAL | Single atom: pending frame. In chain: iterates `st.selected`, sets `st.context`/`st.route` per member, restores after (`chain_exec.py:304-331`). |
| 67 | Any | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `query_ops.py:65` `any()` over `st.selected`. |
| 68 | All | YES | YES | YES | ACTIVE | YES | YES (1) | YES | PARTIAL | `query_ops.py:70`. |
| 69 | None | YES | YES | YES | ACTIVE | YES | YES (1) | YES | PARTIAL | `query_ops.py:75` `not any()`. |
| 70 | Count | YES | YES | YES | ACTIVE | YES | YES (9) | YES | PARTIAL | `query_ops.py:80` `len(st.selected)` → `st.last_result`. |
| 71 | Measure | YES | YES | YES | ACTIVE | YES | YES (1) | YES | PARTIAL | `query_ops.py:84` count with parsed unit/kind. |
| 72 | Limit | YES | YES | YES | ACTIVE | YES | YES (3) | YES | PARTIAL | `query_ops.py:95` `validate_bound` → `st.limit`; honest `ok=False` on invalid bound. |
| 73 | Threshold | YES | YES | YES | ACTIVE | YES | YES (3) | YES | PARTIAL | `query_ops.py:105` `eval_predicate` → `st.last_result`. |
| 74 | Weight | YES | YES | YES | ACTIVE | YES | YES (3) | YES | PARTIAL | `query_ops.py:117` `st.weights[key]=w`; honest `ok=False` on nonfinite weight. |
| 75 | Normalize | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `query_ops.py:132`; honest `zero_set` failure. |
| 76 | Resolve | YES | YES | YES | ACTIVE | YES | YES (1) | YES | PARTIAL | `query_ops.py:141` `manifest_resolver.resolve_manifest` → result cell, clamped confidence. |
| 77 | Infer | YES | YES | YES | ACTIVE | YES | YES (1) | YES | PARTIAL | `query_ops.py:151`: writes projection cell with explicit `projected=True, fact=False, matched=False`, message `PROJECTED_NOT_FACT` — explicit about not being fact. |
| 78 | Cause | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `query_ops.py:159`: appends `(a,b)` to `st.causes`; rejects malformed/self-relations honestly. |
| 79 | Depend | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `query_ops.py:161` same pattern on `st.deps`. |
| 80 | Context | YES | YES | YES | ACTIVE | YES | YES (9) | YES | PARTIAL | `spectrum_ops.py:87` `st.context = lab or st.scope` (`core_ii_exec.py:132`). |
| 81 | Reference | YES | YES | YES | ACTIVE | YES | YES (3) | YES | PARTIAL | `spectrum_ops.py:90` `st.refs[name]=target`; message accurately says `no_copy`. |
| 82 | Group | YES | YES | YES | ACTIVE | YES | YES (4) | YES | PARTIAL | `spectrum_ops.py:95` `st.groups[name] = selected`. |
| 83 | Ungroup | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `spectrum_ops.py:99`: pops group; restores selection from members. |
| 84 | Copy | YES | YES | YES | ACTIVE | YES | YES (4) | YES | PARTIAL | `spectrum_ops.py:105`: deep-copies store value to `copy_<src>`; publishes dest. English: `Intent("copy", 84, …)` (`translate.py:426`). |
| 85 | Move | YES | YES | YES | ACTIVE | YES | YES (3) | YES | PARTIAL | `spectrum_ops.py:117` `st.store[dest]=st.store.pop(src)`; honest `malformed_move`/`move_missing`. English: `Intent("move", 85, …)` (`translate.py:417`). |
| 86 | Delete | YES | YES | YES | ACTIVE | YES | YES (7) | YES | PARTIAL | `spectrum_ops.py:147`: removes store key/group; honest `delete_missing`; deliberately publishes non-matched result ("NO_AUTHORITATIVE_RESULT"). English: `Intent("delete", 86, …)` (`translate.py:435`). |
| 87 | Replace | YES | YES | YES | ACTIVE | YES | YES (3) | YES | PARTIAL | `spectrum_ops.py:176`: renames store key; **honest refusal** on occupied destination (`replace_occupied`, zero mutation). English: `Intent("replace", 87, …)` (`translate.py:443`). `dell87_refusal_test.py` pins the refusal. |
| 88 | Patch | YES | YES | YES | ACTIVE | YES | YES (4) | YES | PARTIAL | `spectrum_ops.py:208`; honest `patch_miss`. English: `Intent("patch", 88, …)` (`translate.py:451`). |
| 89 | Diff | YES | YES | YES | ACTIVE | YES | YES (2) | YES | PARTIAL | `spectrum_ops.py:228`: changed store keys vs baseline → `st.last_diff`. |
| 90 | Trace | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:243`: reads `st.traces` → `st.last_result`. **Test gap** (name-pattern; verify). |
| 91 | Assert | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:250`: `eval_condition`; on fail `ok=False, assert_fail` **and** fails open tx (`_fail_open_tx`). **Test gap.** |
| 92 | Guard | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:258`: `st.last_guard = ALLOW/BLOCK`; BLOCK → `ok=False, guard_block` + fails open tx. **Test gap.** |
| 93 | Try | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:268`: pushes tx frame with deep checkpoint; syncs `st.try_depth`. **Test gap.** |
| 94 | Catch | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:274`: marks active tx `caught`; honest `catch_illegal`. **Test gap.** |
| 95 | Commit | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:286`: marks `committed`, appends staged; honest `commit_illegal`/`commit_without_try`. **Test gap.** |
| 96 | Revert | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:303`: restores checkpoint or pops snapshot; honest refusals for committed/reverted frames; "Revert nothing" → `ok=True` (lenient, message-honest). **Test gap.** |
| 97 | Define | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:323` `st.defs[name]=meaning`. **Test gap.** |
| 98 | Alias | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:328`: cycle + missing-target checks **before** write; honest `alias_cycle`/`alias_missing`. **Test gap.** |
| 99 | Compose | YES | YES | YES | ACTIVE | YES | **NO** | YES | PARTIAL | `spectrum_ops.py:345`: parses body (cycle/depth/malformed checks, bound via `st.limit`), then **recursively executes the sub-chain** via `execute_seed` (`spectrum_ops.py:371`). **Test gap.** |

**Core II summary:** 49 registered · 49 parseable · 49 translatable-YES (SSI-I) ·
49 executable (all ACTIVE) · 49 publicly reachable ·
39 tested-YES / **10 test gaps (90–99, the tx/frame family)** ·
SEMANTICALLY_CONSISTENT: 42 YES / 7 PARTIAL (60–66: real in chains, limited as single atoms; 61 vacuous join noted) ·
PERSISTENT: 49 PARTIAL (durable subset persisted; snapshots/staged/traces/try_depth/parallel/branch/last_diff/limit are transient — `core_ii_persist_test.py`).

## §3 — Reserved domain (address_space.RESERVED_DOMAIN, 49 entries)

All 49 are REGISTERED with status `RESERVED_NOT_ACTIVE`
(`form/mandell/address_space.py:36-88`); all are PARSEABLE
(`parse_seed` succeeds — the parser only checks registration); none are
TRANSLATABLE (translate emits no reserved references), none are EXECUTABLE
(`execution_standing` → RESERVED_NOT_ACTIVE, dispatch "none"), none are
PUBLICLY_REACHABLE through an honest path, none are TESTED, PERSISTENT is
N/A. Roster: 151 Harmonic, 167, 168, 176, 257, 258, 259, 361, 463, 560, 564,
571, 583, 584, 586, 587, 654, 655, 662, 666, 673, 679, 685, 688, 692, 696, 697,
698, 775, 777, 778, 782, 821, 822, 850, 865, 869, 870, 872, 874, 880, 881, 889,
890, 891, 893, 894, 895, 999 Omega.

**Known gap (R2 §4 finding):** in multi-atom chains a reserved Dell is
honestly skipped (`chain_exec.py:108-111` → `ok=True, skipped=True`,
"reserved/not-active"). But the **single-seed executor leaf** answers
`ok=True` "recognized — runtime thin" for reserved dells
(`form/mandell/executor_leaf.py:492-500`) and will `place_idea(label)` as a
side effect. Reachable today via the public raw-seed path
(`form/repl.py:2555`). The registry authority (`execution_standing(151)` →
RESERVED_NOT_ACTIVE) is honest; the leaf is not. **MUST_FIX_BEFORE_GATE.**
Exact patch for the coordinator (executor files are outside R2's file
allowlist, so this is handed over, not applied):
`form/mandell/executor_leaf.py`, in the final `else:` branch — before the
`ok=True` return, add:
`if primary is not None and primary > 99: return {"ok": False, "error": f"Dell {primary:02d} reserved/not-active", ...}`
with **no** `place_idea` side effect on that path. This keeps parseability
(parser contract unchanged) while making execution honest.

## §4 — Honesty-critical notes (from R2 audits)

1. **44 Bridge / 47 Embed** are the only ACTIVE_REFUSAL dells: production
   path `core_i_ops` returns honest `ok=False` with named errors
   (`bridge_unavailable`, `embed_unavailable`). Their old leaf arms
   (`executor_leaf.py:428-436,451-453`) were message-only stubs and are now
   dead in every production path. Pinned by
   `form/mandell/r2_semantic_honesty_test.py`.
2. **Dell 61 Join inside control blocks is vacuous** (`chain_exec.py:335`
   runs before `:341` writes body results → `incoming` always 0). The
   message is honest (`incoming=0`); the join semantics are not. Recorded
   as a semantic-consistency PARTIAL, not a crash risk.
3. **Dell 62 Parallel runs sequentially** (`chain_exec.py:269-271`); the
   message says "offline_deterministic" — honest about the limitation.
4. **Chains are not atomic**: mid-chain failure records `ok=False` but
   execution continues; a Core I leaf exception aborts the chain with no
   receipts for unexecuted atoms (chain_exec audit).
5. **The raw-seed REPL bypass** (`form/repl.py:2555`) skips english_brain,
   translate, `_execute_intent`, and the router — it is the only public path
   that reaches the dishonest leaf else-branch. The router itself is honest
   by construction (CORRESPONDENCE allowlist + "refusing to guess").
6. **`english_brain.understand()` is dead in production** (zero callers;
   only tests). The live "English brain" is `normalize_english` only
   (`translate.py:324-325`, `repl.py:1228-1238`).
7. **Flow principles** (`form/mandell/rules_v0.py`): Free-Origin, Symmetry,
   Fractal-Nesting are STATED_ONLY (zero code readers of `rules_v0`);
   Flow-Priority, No-Orphans, Typed-Sockets, Cross-Layer-Routing are PARTIAL
   (real mechanisms exist — `flow_executor` DCC-IV, `chain_exec` 9-operator
   set, TOAM typed args for 14 dells, diagonal context bindings — but none
   enforces the principle as stated). Two live composition authorities
   (`flow_executor` for `>`/`>>`, `chain_exec` for all 9 operators) with a
   silent fall-through between them (`repl.py:2543-2566`).
8. **Floor Spirit licensing is nowhere in the execution chain** (grep over
   repl/router/executor/translate/brain/composer: zero matches). In-chain
   authority gates are: the router CORRESPONDENCE allowlist, operator_bridge
   BLOCKED/RAW_ONLY, the MPC-008 macro guard, and the MPC-001 semantic-loss
   guard.

## Summary counts

| Dimension | Core I (0–50) | Core II (51–99) | Reserved (49) |
|---|---|---|---|
| REGISTERED | 51 | 49 | 49 |
| PARSEABLE | 51 | 49 | 49 |
| TRANSLATABLE YES / PARTIAL / NO | 14 / 8 / 29 | 49 / 0 / 0 | 0 / 0 / 49 |
| EXECUTABLE (ACTIVE + ACTIVE_REFUSAL) | 49 + 2 | 49 + 0 | 0 (RESERVED_NOT_ACTIVE) |
| PUBLICLY_REACHABLE | 51 | 49 | 0 honest (leaf gap noted) |
| TESTED (name-pattern method) | 42 YES / 9 gaps | 39 YES / 10 gaps | 0 |
| SEMANTICALLY_CONSISTENT YES / PARTIAL / NO | 32 / 13 / 6 | 42 / 7 / 0 | N/A |
| PERSISTENT YES / PARTIAL / READ-ONLY / N/A / UNKNOWN | 23 / 0 / 9 / 12 / 7 | 0 / 49 / 0 / 0 / 0 | N/A |

**Test gaps (no name-pattern hits; verify before treating as uncovered):**
Core I — 25 Pulse, 26 Temp, 29 Compress, 30 Expand, 38 Distill, 41 Sanitize,
43 Fallback, 45 Translate, 46 Rank. Core II — 90 Trace, 91 Assert, 92 Guard,
93 Try, 94 Catch, 95 Commit, 96 Revert, 97 Define, 98 Alias, 99 Compose
(the whole transaction/frame family).

**New R2 tests (both registered in the regress LIST by auto-discovery):**
- `form/mandell/r2_registry_reconciliation_test.py` — 315/315 GREEN.
  Pins CORE_I_CLOSABLE == core_i_ops.HANDLED, per-Dell dispatch standing,
  leaf-branch presence (and 37's deliberate absence), Core-II family
  coverage, reserved/unregistered honesty.
- `form/mandell/r2_semantic_honesty_test.py` — 27/27 GREEN. Proves honest
  failure for parse/registry/router/arm-refusal/flow/composer/translate
  cases (representative coverage for Obj 0.2.4).

**Method note on SEMANTICALLY_CONSISTENT:** verdicts come from two read-only
specialist audits (Core I leaf, Core II executor) that traced every branch
to its state effects; STUB = messages/history-note only, PARTIAL = real but
name-overclaiming or self-contradicting, NO = theater (00, 01, 17, 43).
Nothing was invented: cells with unverified persistence say UNKNOWN.
