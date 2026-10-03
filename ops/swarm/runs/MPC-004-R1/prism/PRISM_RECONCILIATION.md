# PRISM RECONCILIATION — MPC-004-R1 Dell Operational Truth Baseline

**Role:** PRISM (reconciliation/synthesis). **Read-only. Authorizes nothing.**
**Base:** `53919043224b18e12516bd9e885b9352de33422f` / tree `561a09934aa103608ae09fb25c2bfa5d3e29977b`
**Run:** MPC-004-R1 · **Phase:** PRISM_RECONCILE · **Mode:** SWARM
**Inputs reconciled:** 57 evidence entries (ORACLE ×7 streams, ARGUS, NULL ×6, UNI ×3, HARNESS ×1) + 9 contradictions (C-R1-001…C-R1-009; 1 RESOLVED, 8 OPEN).

**Hard rules honored:** disagreement preserved (no majority vote); UNKNOWN never converted to PASS; every claim carries provenance (agent · classification · source); no semantics invented.

**Coverage note:** ORACLE stream for Dells 51–69 was still RUNNING at reconciliation time. Dells 51–69 below rest on the MPC-003 audit (background record) plus R1 probes where available. Dells 52, 53 and registry names for 81, 83 have **no evidence** — marked UNKNOWN, not assumed.

---

## A. AGREEMENTS (≥2 agents independently verified)

| # | Claim | Provenance |
|---|---|---|
| A1 | "57 handlers" is false as a completeness claim; true inventory is 99–101 ids, not 57. All /57 ratios invalid. | UNI · VERIFIED · executor.py + executor_leaf.py — 100 ids (0–99) · ORACLE · VERIFIED · 99 (1–99) + Dell 0 edge · ARGUS · VERIFIED · 101 dispatch ids (multi-idiom scan) |
| A2 | All 9 Flow operators operationally implemented (>, >>, >>>, :, ::, :>, <:, <:>, <<[Delta]). MPC-003 "DEFINED-only" matrix was audit-scope error. | ORACLE · VERIFIED · operator_bridge.compose_execute + cac_i_test · NULL · VERIFIED · chain_exec.py:119-163 _apply_flow + live probes → C-R1-002 RESOLVED |
| A3 | Predicate-evaluation half of conditional execution EXISTS (predicate.py contract live, Branch(60)+eval_condition works, 91/92 are condition-gated primitives). Only the English→condition encoding + per-atom condition slot are missing. English guard must stay. | NULL · VERIFIED · predicate.py PREDICATES, chain_exec.py:164,249, live probes · ORACLE · VERIFIED · spectrum_ops.py:239-256 (91/92) |
| A4 | Prior packets on Dells 84–88 hold on this base (typed args, composition bridge, English routes, MPC-001 guard intact for 7 verbs). | ORACLE · VERIFIED · probes on pinned SHA · ARGUS · VERIFIED · 57/67/68/69 typed hold; guard holds for 7 listed verbs |
| A5 | Dell21 = live-unit merge via live_identity (executor.py:28); leaf 21/22 branches in executor_leaf.py are dead/shadowed; determinism is state-dependent. | ORACLE · VERIFIED · executor.py:28 · ARGUS · VERIFIED · "HOLDS with caveats: dormant-but-importable, determinism state-dependent" |
| A6 | Typed signature count = 14: [8, 51, 54, 56, 57, 58, 67, 68, 69, 84, 85, 86, 87, 88]. | ARGUS · VERIFIED · signatures.py · ORACLE · VERIFIED · 0/10 in 70–79, 0/10 in 90–99, 5/10 in 80–89 (84–88) |
| A7 | English reachability is broader than `Intent.dell` suggests; real mapping lives in `Intent.mandel`. English reaches (inter alia) 4, 8, 9, 13, 15, 27, 31, 32, 34 plus 51, 56, 58, 84–88. | UNI · VERIFIED · translate.py Intent.mandel, 27-phrase corpus · ORACLE · VERIFIED · 12/25 leaf Dells English-reachable (4,5,6,8,9,10,11,12,13,15,19,25) |
| A8 | `>`-composition is brittle: `::` lab atoms swallow a following `>` (parse-level); `>`-strip truncation proven; case-mismatch writes phantom keys; `::` binds via rpartition so `08[Create] :: x > 09[Show]` swallows the chain into the label. | ORACLE · VERIFIED · probes (74, 78/79, 55>56) · ARGUS · VERIFIED · phantom-key + truncation probes · ORACLE · VERIFIED · rpartition probe |
| A9 | Registry names overstate mechanisms in multiple places (95 "atomic", 90 "provenance", 94 "error class", 71 "Measure", 40 "TokenCount", leaf 29/30/38/43/49, 37 "Stream"). | ORACLE · VERIFIED · spectrum_ops.py:232-291; query_ops.py:84-93; core_i_ops.py:816-827; executor_leaf.py · ORACLE · VERIFIED · core_i_ops.py:334-560 vs registry |
| A10 | `st.limit` (Dell72) is not persisted; weights/causes/deps are. | ORACLE · VERIFIED · persist_core_ii.py field list; grep "limit" → no hits |

---

## B. CONTRADICTIONS — final status

| ID | Parties | Status | Statement | Blocks | Path to resolve |
|---|---|---|---|---|---|
| C-R1-001 | UNI / ORACLE / MPC-003 | **OPEN** | Inventory: UNI 100 (0–99) · ORACLE 99 (1–99) + Dell 0 edge/locked · ARGUS 101 dispatch ids (double-counts 21/22: dead leaf branches + live_identity dispatch). All agree 57 is false; disagree on exact count. | Any denominator claim (typed coverage, closure %); scope of "all Dells" in future directives. | Director decision on what counts as "executable Dell": reachable-via-execute_seed (→100) vs distinct dispatch targets (→101) vs 1–99 + Dell-0-edge (→99+edge). |
| C-R1-002 | ORACLE / MPC-003 | **RESOLVED** | Flow 9/9 operational. NULL + ORACLE independently verified via `_apply_flow` (chain_exec.py:119-163) with live probes. MPC-003 matrix corrected; debt item 5 removed. | — (closed) | — |
| C-R1-003 | ORACLE / registry.py, core_ii.py | **OPEN** | Registry verbs not implemented: 95 "atomically accept staged mutation" (mark-only, no isolation) · 90 "follow provenance/execution/data path" (buffer dump, transient) · 94 "handle failure/error class" (generic catch, no dispatch). | Any certification or doc citing registry semantics for 90/94/95; honesty of user-facing descriptions. | Registry correction (Director authority) or mechanism change (not authorized this round). |
| C-R1-004 | ORACLE / registry.py | **OPEN** | Dell37: registry "Stream"/"Chunked out" vs implementation + translate "Nurture" (nursery lifecycle). | Registry consistency; English already uses Nurture. | Registry edit (Director). |
| C-R1-005 | ORACLE / DIRECTOR | **OPEN** | Dell87 Replace: mechanism is **key-rename** (`store[new]=store.pop(old)`); registry/signature language suggests value substitution. | Typed-signature semantics for 87; certification of English "replace A with B". | Director semantic decision — do not choose here. |
| C-R1-006 | NULL / MPC-003 | **OPEN** (narrowed) | MPC-003: "faithful predicate encoding contract does not exist." NULL: predicate contract EXISTS (`empty: store:X` live); genuinely missing = per-atom condition slot (~15-line evolution of `_payload_cond`) + English→condition encoding. | Conditional-execution design; debt item 1 wording. | Director-authorized implementation round; English guard stays regardless. |
| C-R1-007 | ORACLE / translate.py, english_brain.py | **OPEN** | English misroutes: "resume" → 28[Rollback] (via english_brain.py:72 'resume'→'load') instead of 33[Resume] · "make a macro" → 08[Create] instead of 48[Macro]. | English safety certification; any claim of faithful English routing. | Fix english_brain.py:72 + macro route (Director-authorized UNI work) or document as known. |
| C-R1-008 | ARGUS / MPC-001/002/003 | **OPEN** | Guard generality false: 'patch X to Y if X is empty' → 88[Patch] **EXECUTED**, store mutated ('original'→'y if x is empty'). Root cause: `_DESTRUCTIVE_VERBS` omits 'patch'. | "Zero mutation" safety claim; MPC-001 packet generality. | Minimal correction: add 'patch' to `_DESTRUCTIVE_VERBS` (NOT repaired — read-only round). **Top broken-link candidate.** |
| C-R1-009 | ORACLE / gate_discipline.py | **OPEN** | `EXTENDED_DELL_RESERVE` legacy names for 51–99 (e.g. 51 'Harmonic', 56 'ManifestAct') contradict current CORE_II semantics. | Any authority claim citing gate_discipline names for Core-II. | Remove/update stale table (Director). |

---

## C. UNKNOWNS (consolidated — survive reconciliation)

1. Exact executable inventory: 99 vs 100 vs 101 (C-R1-001).
2. **Dell 52, Dell 53**: no evidence of any kind (semantics, executor, tests).
3. Registry names for **Dell 81, Dell 83** (not in evidence).
4. `eval_predicate` "count" field semantics across all contexts.
5. `resolve_manifest` confidence semantics + exception behavior (Dell76).
6. Producers of `st.traces` in production (Dell90).
7. Production population of `st.snapshots` (Dell96 fallback branch reachability).
8. Malformed-condition behavior for Dell91/92.
9. Cross-process semantics of tx frames (93–96).
10. Intent of `st.limit` non-persistence (deliberate vs oversight).
11. Direct test coverage for 71, 72, 73, 75, 76, 77, 78, 79 (none found in scanned tests).
12. Whether Dell21 store-merge has any real use case (NULL: need unfalsified — do not promote to gap).
13. Dell99 Compose immediate-execution: intended or incidental.
14. Dell22 Split: only partially evidenced (executor route known; 12-dim audit not done).
15. Dells 51–69 ORACLE stream was still RUNNING at reconciliation; 52/53/55/59–66 rest on MPC-003 background audit.

---

## D. OPERATIONAL MATRIX (all Dell ids)

Legend — evidence class: **V**=VERIFIED (probe/code-read this round or MPC-003), **D**=DERIVED, **U**=UNKNOWN.
Columns: executor · one-line real semantics · typed? · English? · composes? · failure mode · persistence · class.

### Leaf layer — executor_leaf.py (Dells 0–50; single-atom routing; 21/22 dead branches)

| Dell | Registry name | Executor | Real semantics | Typed | English | Composes | Failure | Persist | Ev |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Nova | executor_leaf | no-op placeholder | No | No | single-atom | none (ok=True) | n/a | V |
| 1 | Initiate | executor_leaf | executes; invalid labels degrade to defaults | No | No | single-atom | uncaught exceptions only | n/a | V |
| 2 | Persona | executor_leaf | read-only status, sets nothing | No | No | single-atom | none | n/a | V |
| 3 | Logic | executor_leaf | prints unenforced constraints | No | No | single-atom | none | n/a | V |
| 4 | Transform | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 5 | Tone | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 6 | Cycle | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 7 | Link | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 8 | Create | executor_leaf | creates unit via place(); **uid-collision SILENT OVERWRITE defect** | **Yes** | Yes | single-atom | uncaught exc | units persist | V |
| 9 | Show | executor_leaf | placeholder render | No | Yes | single-atom | none | n/a | V |
| 10 | Keep | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 11 | Architect | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 12 | Test | executor_leaf | self-test; **tautologies inflate own score** | No | Yes | single-atom | none | n/a | V |
| 13 | Loop | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 14 | Bind | executor_leaf | binds uid (collision overwrite via place()) | No | No | single-atom | uncaught exc | n/a | V |
| 15 | Map | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 16 | Decay | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 17 | Shadow | executor_leaf | prints 'not live' | No | No | single-atom | none | n/a | V |
| 18 | Mirror | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 19 | Drive | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 20 | Alpha | executor_leaf | advisory only | No | No | single-atom | none | n/a | V |
| 21 | Merge | live_identity (executor.py:28); leaf branch **DEAD** | ≥2 live units → child w/ parent lineage, parents unmutated | No | ? | ? | missing_source etc. | ? | V (+caveats: determinism state-dependent) |
| 22 | Split | live_identity; leaf branch **DEAD** | splits live unit | No | ? | ? | ? | ? | V (partial) |
| 23 | Lock | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 24 | Unlock | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 25 | Pulse | executor_leaf | executes | No | Yes | single-atom | uncaught exc | n/a | V |
| 26 | Temp | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |

### Core-I ops — core_i_ops.py (single-atom ONLY by routing design, executor.py:24; no `>` / control blocks)

| Dell | Registry name | Executor | Real semantics | Typed | English | Composes | Failure | Persist | Ev |
|---|---|---|---|---|---|---|---|---|---|
| 27 | Checkpoint | core_i_ops | real checkpoint; PAC-I generation ids; tested | No | Yes ("checkpoint now") | No (structural) | checkpoint fail → ok=False | durable (generations) | V |
| 28 | Rollback | core_i_ops | restores checkpoint | No | **MISROUTED** ("resume"→28!) | No | rollback_missing | restores state | V |
| 29 | Compress | executor_leaf | creates idea; **NO compression** | No | No | single-atom | uncaught exc | n/a | V |
| 30 | Expand | executor_leaf | **no unfolding** | No | No | single-atom | uncaught exc | n/a | V |
| 31 | Simulate | executor_leaf | executes | No | Yes ("simulate X") | single-atom | uncaught exc | n/a | V |
| 32 | Pause | executor_leaf | executes | No | Yes ("pause"→32) | single-atom | uncaught exc | n/a | V |
| 33 | Resume | executor_leaf | executes | No | **BROKEN** ("resume"→28) | single-atom | uncaught exc | n/a | V |
| 34 | Stamp | core_i_ops | timestamp mark | No | Yes ("stamp X") | No | ? | ? | V (partial) |
| 35 | Discover | core_i_ops | broad read-only introspection; rich English | No | Yes | No | n/a (read-only) | n/a | V |
| 36 | Inject | executor_leaf | **~= Dell 8 Create (duplicate)** | No | No | single-atom | uncaught exc | n/a | D/V |
| 37 | Nurture (registry stale: "Stream") | core_i_ops | nursery lifecycle mutation authority; fail-safe | No | Yes (37[Nurture]) | No | fail-safe | ? | V |
| 38 | Distill | executor_leaf | keyword slugger; **no summary** | No | No | single-atom | uncaught exc | n/a | V |
| 39 | Schema | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 40 | TokenCount | core_i_ops | **weighted heuristic, NOT actual count** | No | No | No | n/a | n/a | V |
| 41 | Sanitize | executor_leaf | regex-redacts **LABEL ONLY**; touches no stored state — false safety impression | No | No | single-atom | uncaught exc | n/a | V |
| 42 | Retry | executor_leaf | re-executes last history seed; **INDISCRIMINATE (re-runs destructive)** | No | No | single-atom | per-item try/except | n/a | V |
| 43 | Fallback | executor_leaf | prints static text | No | No | single-atom | none | n/a | V |
| 44 | Bridge | core_i_ops | **honestly unavailable** (offline-origin); tested | No | No | No | unavailable (tested) | n/a | V |
| 45 | Translate | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 46 | Rank | executor_leaf | executes | No | No | single-atom | uncaught exc | n/a | V |
| 47 | Embed | core_i_ops | **honestly unavailable** (offline-origin); tested | No | No | No | unavailable (tested) | n/a | V |
| 48 | Macro | executor_leaf | replay last-n seeds OR emits re-parseable composition chain; **inconsistent n defaults (3 vs 5)** | No | **MISROUTED** ("make a macro"→08) | single-atom | uncaught exc | n/a | V |
| 49 | Profile | executor_leaf | status dump; **no benchmarking** | No | No | single-atom | uncaught exc | n/a | V |
| 50 | Manifest | executor_leaf | ~= Dell 8 (duplicate-ish) | No | No | single-atom | uncaught exc | n/a | D |

### Core-II — query_ops.py / control_runtime.py / chain_exec.py (Dells 51–79)

| Dell | Name | Executor | Real semantics | Typed | English | Composes | Failure | Persist | Ev |
|---|---|---|---|---|---|---|---|---|---|
| 51 | Select | query_ops | ids from ids_fn; optional predicate; **mutates selected**; publishes | **Yes** | Yes ("select items") | Yes | ? | selected transient | V |
| 52 | ? | ? | **UNKNOWN — no evidence** | No | ? | ? | ? | ? | U |
| 53 | ? | ? | **UNKNOWN — no evidence** | No | ? | ? | ? | ? | U |
| 54 | Query | query_ops | queries selected; optional predicate; publishes hits; selected unchanged | **Yes** | No | Yes | ? | n/a | V |
| 55 | Set | query_ops | store[key]=value | No | No | `::` unusable in chains | ? | ? | V (partial) |
| 56 | Get | query_ops | store[key]; missing → matched=False, error="missing"; read-only | **Yes** | Yes | Yes | missing → matched=False | n/a | V |
| 57 | Compare | query_ops | predicate comparison | **Yes** | No | Yes | type_mismatch | n/a | V |
| 58 | Match | query_ops | substring match over ids; **mutates selected** | **Yes** | Yes ("search for shopping") | Yes | none (empty valid) | selected | V |
| 59 | Route | control_runtime | else/branch marker (control atom) | No | No | structural | multiple_else → fail | n/a | V |
| 60 | Branch | chain_exec | if/else via eval_condition over branch ranges | No | No | block ranges | ? | n/a | V |
| 61 | Join | core_ii_exec / control_runtime | block terminator | No | No | structural | ? | n/a | V |
| 62 | Parallel | chain_exec | execute range; failures captured non-fatal | No | No (not needed — NULL) | block | captured | n/a | V |
| 63 | Sequence | chain_exec | execute range in order | No | No | block | ? | n/a | V |
| 64 | Until | chain_exec | post-check loop; bound via st.limit | No | No | block | ? | **limit NOT persisted (gap)** | V |
| 65 | While | chain_exec | pre-check loop | No | No | block | ? | **limit NOT persisted** | V |
| 66 | ForEach | chain_exec | iterate selected members as context | No | No | block | empty → valid | n/a | V |
| 67 | Any | query_ops | any(selected matches predicate) → bool | **Yes** | No | Yes | none | n/a | V |
| 68 | All | query_ops | all match → bool | **Yes** | No | Yes | none | n/a | V |
| 69 | None | query_ops | none match → bool | **Yes** | No | Yes | none | n/a | V |
| 70 | Count | query_ops | len(selected) → last_result | No | canonical only | Yes | none (0 valid) | n/a | V |
| 71 | Measure | query_ops | **float(len(selected)); unit/kind labels DECORATIVE** | No | No | Yes | none | n/a | V |
| 72 | Limit | query_ops | sets st.limit (loop bound) | No | No | `::` unusable in chains | invalid_limit → ok=False | **GAP: not persisted** | V |
| 73 | Threshold | query_ops | predicate → bool; **never fails hard** (error field only) | No | No | Yes | soft only | n/a | V |
| 74 | Weight | query_ops | weights[key]=float; rejects NaN/inf | No | No | `::` unusable in chains | nonfinite_weight → ok=False | durable | V |
| 75 | Normalize | query_ops | weights /= sum; **zero_set returns ok=True (inconsistent)** | No | No | Yes | soft (inconsistent) | durable (weights) | V |
| 76 | Resolve | query_ops | manifest_resolver → name + confidence | No | No | `::` unusable in chains | exceptions may propagate | n/a | V (partial; confidence U) |
| 77 | Infer | query_ops | labels projection: projected=True, fact=False, matched=False — **honest by design** | No | No | `::` unusable in chains | none | n/a | V |
| 78 | Cause | query_ops | appends (a,b) to st.causes from "a>b"; **`>`-composition STRUCTURALLY IMPOSSIBLE** | No | No | **No** | malformed/self/duplicate | durable | V |
| 79 | Depend | query_ops | **~=78 → st.deps; near-duplicate** (target list + message only) | No | No | **No** | same as 78 | durable | V |

### Spectrum — spectrum_ops.py via apply_spectrum (Dells 80–99)

| Dell | Name | Executor | Real semantics | Typed | English | Composes | Failure | Persist | Ev |
|---|---|---|---|---|---|---|---|---|---|
| 80 | Context | spectrum_ops | never-fail total function | No | No | **D-1: (...) args SILENTLY DISCARDED** | none | ? | V |
| 81 | ? (name U) | spectrum_ops | never-fail total function | No | No | D-1 / D-5 | none | ? | V (partial) |
| 82 | Group | spectrum_ops | groups selected; **empty selection → falls back to ALL program ids** | No | No | D-1 / D-5 | none | ? | V |
| 83 | ? (name U) | spectrum_ops | never-fail total function | No | No | D-1 / D-5 | none | ? | V (partial) |
| 84 | Copy | spectrum_ops | copies store value; **missing key → GHOST copy (stores key name as value)** | **Yes** | Yes | Yes | ghost (defect) | store | V |
| 85 | Move | spectrum_ops | move | **Yes** | Yes | Yes | ? | store | V |
| 86 | Delete | spectrum_ops | deletes key; guard holds for 7 verbs | **Yes** | Yes | Yes | ? | store | V |
| 87 | Replace | spectrum_ops | **KEY-RENAME** (`store[new]=store.pop(old)`); NOT value substitution — Director question (C-R1-005) | **Yes** | Yes ("replace A with B") | Yes | ? | store | V |
| 88 | Patch | spectrum_ops | patches value; **GUARD BYPASS — conditional patch EXECUTES (C-R1-008)** | **Yes** | Yes | Yes | ? | store | V |
| 89 | Diff | spectrum_ops | publishes to **volatile last_diff** (invisible to composition); baseline overwritten per mutation | No | No | No (volatile) | none | volatile | V |
| 90 | Trace | spectrum_ops | **dumps st.traces buffer — NOT provenance** (C-R1-003) | No | No ("trace"→35) | Yes | none | transient | V |
| 91 | Assert | spectrum_ops | eval_condition → PASS/FAIL; false → assert_fail + tx frame failed | No | No | Yes | assert_fail | last_assert durable | V |
| 92 | Guard | spectrum_ops | eval_condition + **"block"/"deny" literal override** → guard_block | No | No | Yes | guard_block | last_guard durable | V (**no behavioral test**) |
| 93 | Try | spectrum_ops | pushes tx frame w/ deep-copy checkpoint | No | No | Yes | none | transient (process-lifetime) | V |
| 94 | Catch | spectrum_ops | marks caught; **NO error-class dispatch; does NOT restore** (C-R1-003) | No | No | Yes | catch_illegal | transient | V |
| 95 | Commit | spectrum_ops | **mark-only; stages nothing, isolates nothing — "atomic" name-only** (C-R1-003) | No | No | Yes | commit_illegal etc. | staged transient | V |
| 96 | Revert | spectrum_ops | restores checkpoint; **partial** (excludes traces/tx/staged/last_error) | No | No | Yes | unrelated_revert / revert_illegal | in-memory | V |
| 97 | Define | spectrum_ops | defs[name]=meaning; no validation | No | No | Yes | none | durable | V |
| 98 | Alias | spectrum_ops | aliases[name]=target; cycle + missing guards | No | No | Yes | alias_missing / alias_cycle | durable | V |
| 99 | Compose | spectrum_ops | define + **IMMEDIATELY EXECUTES body**; invoke re-runs stored chain | No | No | meta | malformed / compose_fail | durable | V |

**Matrix totals:** ~100 ids mapped · typed 14/100 · English-reachable ≈ 20 ids (prose) + canonical `N[Name]`/`dell N` references · explicit UNKNOWN cells: 52, 53 (full), 81/83 names, 21/22/34/40/47 persistence details, 91/92 malformed-condition behavior.

---

## E. FALSE-CLOSURE CLAIMS FOUND (final, with severity)

| # | Claim | Verdict | Severity | Provenance |
|---|---|---|---|---|
| F1 | "57 Dell handlers" as complete inventory | **FALSIFIED** — true count 99–101 | HIGH — invalidated every /57 ratio (typed coverage, closure %) | UNI·V, ORACLE·V, ARGUS·V |
| F2 | MPC-003 Flow matrix: 6 operators DEFINED-only | **FALSIFIED** — 9/9 operational | MEDIUM-HIGH — was audit-scope error, now RESOLVED (C-R1-002) | NULL·V, ORACLE·V |
| F3 | "Conditional destructive English → UNKNOWN, zero mutation" (general) | **FALSIFIED** — Patch bypasses guard, VERIFIED mutation | **HIGH** — demonstrated destructive-mutation bypass | ARGUS·V (C-R1-008) |
| F4 | 95 Commit "atomically accept staged mutation" | Name-only — mark-only, no staging, no isolation | MEDIUM | ORACLE·V (C-R1-003) |
| F5 | 90 Trace "follow provenance/execution/data path" | Buffer dump; transient | MEDIUM | ORACLE·V (C-R1-003) |
| F6 | 94 Catch "handle failure/error class" | Generic catch; no dispatch; no restore | LOW-MEDIUM | ORACLE·V (C-R1-003) |
| F7 | 71 Measure as measurement | Always len(selected); labels decorative | LOW | ORACLE·V |
| F8 | 40 TokenCount as count | Weighted heuristic | LOW | ORACLE·V |
| F9 | 41 Sanitize "strip secrets" | Redacts label only; touches no stored state — false safety impression | MEDIUM (safety-adjacent) | ORACLE·V |
| F10 | 12 Test self-score | Tautologies inflate score | LOW | ORACLE·V |
| F11 | gate_discipline EXTENDED_DELL_RESERVE names for 51–99 | Stale authority contradicting core_ii.py | MEDIUM | ORACLE·V (C-R1-009) |
| F12 | 37 registry "Stream" | Stale; implementation is Nurture | LOW | ORACLE·V (C-R1-004) |
| F13 | "`>`-composition generally works" | **WEAKENED** — `::` labs swallow `>` (78/79 structurally impossible); `>`-strip truncation; phantom keys on case-mismatch; rpartition binding | MEDIUM | ORACLE·V, ARGUS·V |
| F14 | Leaf "executability" (ok=True everywhere) | Unconditional ok=True; failures are uncaught exceptions; name≠semantics widespread (0,2,3,9,17,20,29,30,38,43,49) | LOW-MEDIUM | ORACLE·V |

---

## F. EXISTING CAPABILITIES RECOVERED (underappreciated, real)

1. **91 Assert / 92 Guard** — undocumented conditional primitives on the live `eval_condition`/predicate machinery. The predicate half of conditional execution already exists. (NULL·V, ORACLE·V)
2. **93–96 checkpoint-revert** — working recovery system (not atomic transactions; document honestly). (ORACLE·V)
3. **99 Compose** — meta-compositional define/invoke; define-mode immediately executes (semantic subtlety noted). (ORACLE·V)
4. **98 Alias** — guarded binding with cycle detection. (ORACLE·V)
5. **48 Macro** — only leaf Dell emitting re-parseable composition chains (dual-mode; n-default inconsistency noted). (ORACLE·V)
6. **42 Retry** — genuine re-execution with per-item try/except; best failure handling in leaf (safety caveat: indiscriminate). (ORACLE·V)
7. **35 Discover** — broad read-only introspection with rich English. (ORACLE·V)
8. **27/28** — real tested checkpoint/rollback pair (PAC-I generation ids). (ORACLE·V)
9. **37 Nurture** — nursery-mutation authority, fail-safe. (ORACLE·V)
10. **77 Infer** — honesty mechanism (projected≠fact) working as designed. (ORACLE·V)
11. **44/47** — honestly-unavailable offline Dells, tested; not false closure. (ORACLE·V)
12. **Flow 9/9** — full operator set operational via `_apply_flow`. (NULL·V, ORACLE·V)
13. **English reach** — wider than claimed: 4, 8, 9, 13, 15, 27, 31, 32, 34 (+84–88, 51, 56, 58). (UNI·V, ORACLE·V)

---

## G. ACTUAL MISSING CAPABILITIES (NULL-tested, genuinely missing)

1. **Per-atom condition slot** for conditional execution (~15-line evolution of `_payload_cond`; predicate contract exists — C-R1-006). English guard stays until built + authorized.
2. **'patch' in `_DESTRUCTIVE_VERBS`** — list membership; the guard's generality claim depends on it (C-R1-008).
3. **`::` lab chaining inside `>` seeds** — parser limitation affecting 55, 71–74, 76, 78, 79, 80–83, 89 (D-5).
4. **`st.limit` persistence** — or a documented transient-by-design decision.
5. **English route corrections** — "resume"→33, "make a macro"→48 (C-R1-007).
6. **place() uid-collision guard** — silent overwrite on 8/14.
7. **Behavioral tests** — 92 Guard (block/deny override); direct tests for 71, 72, 73, 75, 76, 77, 78, 79.
8. **Registry corrections** — 37, 90/94/95 verbs, EXTENDED_DELL_RESERVE 51–99 (Director authority).
9. **Dell87 semantic decision** — key-rename vs value-substitution (Director; C-R1-005).

**NOT missing (NULL falsified — do not build):** control-block English for 62–66 · new Flow operators/semantics · blanket typing of all untyped Dells (≤ ~15 warranted: 55, 60, 64, 65, 72, 73, 74, 76, 78, 79, 91, 92, 97, 98, 99) · Dell21 store-merge expansion (no demonstrated need) · atomic transaction layer on 93–96 · English conditionals before the per-atom slot exists.

---

## H. AUTHORITY DEBT RECALCULATED

| # | MPC-003 item | R1 status |
|---|---|---|
| 1 | Conditional-execution predicate encoding | **NARROWED** — predicate contract EXISTS (NULL·V); missing = per-atom condition slot + English→condition encoding. Name 91/92 as existing primitives. English guard STAYS. |
| 2 | Full 12-dimension closure matrix | **SUBSTANTIALLY ADVANCED, denominator corrected** — this report is the first ~100-Dell matrix. Remaining: 52/53 UNKNOWN, 81/83 names UNKNOWN, leaf failure contracts (uncaught exceptions), 51–69 ORACLE stream incomplete at reconcile time. Denominator 57 → 99–101 (C-R1-001 OPEN). |
| 3 | Dell21 store-merge scope | **KEPT, deprioritized** — NULL found no use case; Patch + copy-patch cover merge-shaped tasks. Director decision required only if ever pursued; do not promote to gap. |
| 4 | Control-block English 62–66 | **REMOVED** — NULL falsified necessity (capability exists at Mandell layer; English adds ambiguity, zero new capability). Do not build. |
| 5 | Unimplemented Flow operators | **REMOVED** — falsified; 9/9 operational (C-R1-002 RESOLVED). |

**Added by R1:**

| # | New debt | Source |
|---|---|---|
| 6 | Safety-guard generality — Patch bypass, VERIFIED mutation | C-R1-008 (ARGUS·V) — **top priority** |
| 7 | Registry stale authority — 37, 90/94/95 verbs, EXTENDED_DELL_RESERVE 51–99 | C-R1-003/004/009 (ORACLE·V) |
| 8 | Dell87 semantic question — key-rename vs value-substitution | C-R1-005 (ORACLE·V) |
| 9 | English misroutes — resume→28, macro→08 | C-R1-007 (ORACLE·V) |
| 10 | place() uid-collision silent overwrite | ORACLE·V |
| 11 | Parser: `::` lab swallowing `>` in chains; 78/79 structurally un-chainable | ORACLE·V, ARGUS·V |
| 12 | Leaf failure contract — uncaught exceptions, unconditional ok=True | ORACLE·V |
| 13 | st.limit persistence gap | ORACLE·V |
| 14 | 41 Sanitize false safety impression; 42 Retry indiscriminate re-execution | ORACLE·V |

---

## I. FIRST-BROKEN-LINK CANDIDATE

**Top candidate: C-R1-008 — add `'patch'` to `_DESTRUCTIVE_VERBS` in `form/mandell/translate.py`.**

- **Verified severity: HIGH.** ARGUS proved `'patch X to Y if X is empty'` → `88[Patch](key='x', value='y if x is empty')` → **EXECUTED**, store mutated `'original'` → `'y if x is empty'`. The MPC-001 safety claim ("zero destructive mutation") is false as stated. This is a live destructive-mutation bypass of the safety guard, not a theoretical gap.
- **Cheapness of fix: minimal.** One list-membership addition. No new mechanism, no semantic invention, no executor change, no migration. Conditional/negated patch phrases then route to UNKNOWN exactly like the other 7 verbs.
- **Safety relevance: maximal.** Closes the demonstrated bypass; restores the guard's generality claim to true.
- **Exact minimal correction:** in `form/mandell/translate.py`, add `"patch"` to the `_DESTRUCTIVE_VERBS` collection, so that any destructive-verb + conditional/negation-marker phrase involving patch returns UNKNOWN instead of a mutating Patch operation.
- **Not performed this round** — R1 is read-only; requires a Director-authorized implementation round with regression tests (conditional patch → UNKNOWN; unconditional patch still works; MPC-001 guard suite re-run).

**Runner-up:** `english_brain.py:72` — `'resume'`→`'load'` misroute sends users saying "resume" into **28[Rollback]** semantics (safety-adjacent; ORACLE·V).

---

## J. WHAT_NOT_TO_BUILD (NULL + Oracles, consolidated)

1. Control-block English for Dells 62–66 (necessity falsified).
2. New Flow operators or Flow semantics (9/9 operational).
3. Blanket typed signatures for all untyped Dells (ceremony; ≤ ~15 warranted).
4. A second composition engine (fix the `::`/`>` parser instead; 99 Compose + 48 Macro already exist).
5. Dell21 store-merge expansion (no demonstrated need; semantics undecided).
6. An "atomic transaction" layer on 93–96 (mechanism is checkpoint-revert — document honestly, don't rebrand).
7. English conditional execution before the per-atom condition slot exists (guard stays).
8. Consolidation of 78/79 without a Director decision (design question, not a build task).
9. Autonomous evolution / self-modification (AUTONOMY remains NO).
10. Any second evidence/ledger authority duplicating Outcomes (swarm run state is process evidence only).

---

## Mode note (addendum context)

Run manifest shows `mode: "SWARM"` with `mode_history` recording Director-set SWARM, and UNI evidence records dual-mode continuity implemented in `state_machine.py` (`set_mode` / `assume_obligations` / `production_laws_for_mode`; 8/8 mode tests + 17/17 harness tests green). No Dell semantics were modified for it. Reconciliation is mode-agnostic: this report's evidence, contradictions, and UNKNOWNs are persisted in the run manifest and survive SWARM↔CORE transitions per the tested mode invariants.

---

## PRISM provenance statement

This reconciliation was produced from the 57 evidence entries and 9 contradictions in `runs/MPC-004-R1/manifest.json` at phase PRISM_RECONCILE. No agent's evidence was overwritten; contradictions C-R1-001 and C-R1-003…C-R1-009 remain OPEN as recorded; C-R1-002 remains RESOLVED per NULL+ORACLE independent verification. UNKNOWNs listed in §C are carried forward, not resolved. PRISM authorizes nothing; DIRECTOR_GATE is next.

**AUTONOMY: NO.**
