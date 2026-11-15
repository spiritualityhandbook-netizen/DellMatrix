# LIMITS VERIFICATION — WAVE 3 (2026-11-15)

Read-only verification of register items **R12–R16** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 2 (`LIMITS_VERIFICATION_WAVE2_2026-11-15.md`), re-verified first-hand at
**current main `04abc1ea9c1296e0605ed18b303eb9b6babfb799`** (merge of PR #422,
2026-11-15 07:35 CST; g31proof_clone fetched and clean before and after).
No code changed; nothing committed. Probes ran against the clone's own `form/`
tree with an isolated temp-file Nursery and a throwaway probe owner
(`W3PROBE`, state files removed after). Probe result: **every check behaved as
the census described** — all four Nursery cuts reproduce exactly, and the
Director-records eviction reproduces with its counter intact.

**Numbering:** R12–R16 are taken exactly as Wave 2's queue named them, which
matches the census's ranked HINDERS-US register (R12 Director records evicted
at 200 · R13 Nursery label 80 · R14 Nursery detail 2,000 · R15 Nursery goals
8 × 200 · R16 Nursery reason 160). No ambiguity found.

**In-flight caution (per the wave brief):** R13–R16 are the SYS-C29 sibling
family. Their repairs are in flight on separate branches — words on PR #429
(`uni/sysc29-nursery-words`, unmerged: `words[:240]` still sits at
`nursery.py:212` on this main), the label circuit (Director-authorized
Q-S2.1) and the reason circuit building in their own clones. **Nothing in
this wave is marked fixed by an unmerged branch**; every disposition below
is the state of main `04abc1e`.

---

## R12 — Director records evicted at 200, counted

- **Census sites:** director_records.py:30; director_session.py:121-130; persist.py:173.
- **Sites today (all three exact):** `_MAX_ENTRIES = 200` at
  `form/dell_matrix/director_records.py:30`, also fed as `max_keep` into the
  section validate/serialize kit at `director_records.py:112` and `:125`;
  record-time eviction in `DirectorSession._record` at
  `form/dell_matrix/director_session.py:121` (`while len(entries) >
  _records._MAX_ENTRIES: entries.pop(oldest_key(entries))`, victim chosen
  oldest-first by the shared DAF-05 policy) with the eviction counted at the
  moment of loss at `:126-130` (`director_records_dropped_total += 1`);
  persist layer passes the same cap in its section table at
  `form/persist.py:173`, and the counter rides the saved section as
  `dropped_total` (`persist.py:460-464`).
- **Mechanism:** every scoped-Director act — recommendation, evidence
  request, directive, refusal — appends one entry to the per-owner
  `director_records` section. The 201st entry evicts the oldest at record
  time (and the serialize/validate kit trims to the same 200 at save/load).
  The evicted entry's *content* is gone; only the running count survives.
  These records are the pipeline's advice trail — the provenance the human
  gate reads when weighing a recommendation.
- **Probe (functional, bound DirectorSession on a throwaway owner,
  04abc1e):** 205 `recommend()` calls against one proposal →
  after 200 records: **200 entries, dropped_total = 0**; after 205:
  **200 entries, dropped_total = 5**, and the first-recorded entry is the
  evicted one (no longer present). Fresh-process reload via the canonical
  `persist_rest.load`: **200 entries, dropped_total = 5** — the trimmed set
  and its counter are what persist.
- **DISPOSITION: CONFIRMED-HINDERS** — unchanged since the census, and the
  same shape as Wave 2's R10 verdict: the loss is *counted*, never silent
  (the AF-4 counter increments at the moment/place of eviction), so this is
  not DEFECT-CONFIRMED — but the count is all that survives. At 201
  Director acts in one owner's history, the oldest advice — which may be
  the refusal or recommendation a later dispute turns on — is
  unrecoverable, while the section itself is small structured records
  whose retention costs little.
  *Failing-first sketch:* bind a DirectorSession, record 201 entries, save,
  reload, and assert all 201 are retrievable — fails today at
  `director_session.py:121` (200 kept, `dropped_total` = 1 after the 201st).

## R13 — Nursery label cut to 80

- **Census site:** nursery.py:211.
- **Site today (exact):** `label=label[:80]` at
  `form/dell_matrix/nursery.py:211`, inside `Nursery.add()` — the one store
  every proposal passes through. Upstream the same field is admitted at
  200: the dock's schema bound `MAX_LABEL_CHARS = 200`
  (`form/dell_matrix/inference_dock.py:43`, enforced
  `validate_proposal_output`/`validate_semantic_output`), so a docked
  proposal whose label the dock *accepted* at up to 200 chars is cut to 80
  by the store, silently — three bounds for one field in one chain
  (200 reject → 80 store → the 512-char snapshot view of Wave 1/2's R3).
- **Mechanism / who hits it:** every `Nursery.add()` caller — the dock
  (both landing paths), exchange import, growth producers, host code. The
  loss is display/full-text fidelity: proposal identity is *not* corrupted,
  because the ID slug derives from `label[:28]` (`nursery.py:83`), so two
  labels differing only past char 80 keep distinct IDs but become
  indistinguishable in stored text.
- **Probe (functional, isolated Nursery, 04abc1e):** `add("L"×150)` →
  stored label length **80**; `add()` returned normally, no error, no
  marker; a fresh `Nursery.load` from disk shows the same 80 — the cut is
  durable. Control: a short label stores whole.
- **DISPOSITION: DEFECT-CONFIRMED** — silent loss of admitted data,
  reproduced: the dock admits labels to 200 and the store destroys
  everything past 80 with no refusal, counter, or marker, on the main
  production path. **In-flight repair named, not credited:** the bounded
  label circuit (Director ruling Q-S2.1, 2026-11-15 — prove the mismatch,
  preserve admitted labels losslessly, refuse beyond the admitted bound
  before mutation) is building on its own branch; it has **not merged**,
  and main `04abc1e` still cuts at `:211`.
  *Failing-first sketch:* `Nursery.add` with labels of 150 and 200 chars
  (and the same through the dock propose path) and assert the stored label
  equals the input — fails today at `nursery.py:211` (stores 80).

## R14 — Nursery detail cut to 2,000, silently

- **Census site:** nursery.py:220.
- **Site today (exact):** `detail=detail[:2000] if isinstance(detail, str)
  else ""` at `form/dell_matrix/nursery.py:220`, in the same `Nursery.add()`
  construction as R13. Detail is the authored substance of
  synthesize/comprehend verdicts and of exchange landings.
- **Mechanism / who hits it — with the scope stated precisely:** the cut is
  silent at the store surface, but today's producers pre-bound detail to
  the *same* 2,000 before the store sees it: the dock by whole-output
  schema rejection (`MAX_DETAIL_CHARS = 2000`,
  `inference_dock.py:552` — Wave 2's R9), and exchange by its own pre-cut
  (`detail_text = "\n".join(detail_lines)[:2000]` at
  `form/dell_matrix/exchange.py:730`). So no current production caller is
  observed losing detail at the store today; the loss binds any direct
  `Nursery.add` producer that composes detail past 2,000 without
  pre-cutting — the store neither refuses, nor marks, nor counts what it
  destroys.
- **Probe (functional, isolated Nursery, 04abc1e):** `add(detail="D"×3000)`
  → stored detail length **2,000**; returned normally, no marker; fresh
  load from disk shows the same 2,000. Control: short detail stores whole.
- **DISPOSITION: DEFECT-CONFIRMED (store surface; latent for today's
  callers)** — silent loss of accepted data, reproduced at the store's own
  API: `add()` accepts the call and a 3,000-char detail, then stores 2,000
  with no signal. This *sharpens* the SYS-C29 packet's sibling
  classification of detail as a "bound-consistent guard": that reading is
  true of the dock/exchange *chain* (both pre-bound at exactly 2,000),
  but at the store contract itself there is no bound, no refusal, and no
  marker — the census's R14 defect reading is the store-level truth, and
  any future producer composing long detail (the field is authored
  substance) loses its tail silently. No repair for detail is in flight;
  the SYS-C29 family circuits cover words (PR #429), label (Q-S2.1), and
  reason — detail awaits its own authorization.
  *Failing-first sketch:* `Nursery.add` with a 3,000-char detail and
  assert the stored detail equals the input (or, under a repair contract
  that keeps a bound, that the call refuses explicitly before mutation) —
  fails today at `nursery.py:220` (stores 2,000, silently).

## R15 — Nursery goals window 8 × 200

- **Census sites:** nursery.py:221-222.
- **Sites today (exact):** `goals=[g[:200] for g in (goals or [])
  if isinstance(g, str) and g.strip()][:8]` at
  `form/dell_matrix/nursery.py:221-222`. Two distinct mechanisms in one
  expression: the *window* — each goal cut to 200 chars, the list cut to
  the first 8 — and a *validation filter* (non-string and blank goals are
  dropped), which is shape validation and is not part of this item's
  verdict.
- **Mechanism / who hits it — scope as for R14:** at the store surface,
  goals 9+ vanish entire and every goal past 200 chars loses its tail,
  with no receipt, counter, or marker. Today's producers pre-bound to the
  same window: the dock schema caps goals at 8 × 200
  (`MAX_GOALS = 8` / `MAX_GOAL_CHARS = 200`, `inference_dock.py:553-554`,
  whole-output rejection past them — R9), and exchange passes a single
  short composed goal (`exchange.py:769-770`). As with detail, the live
  loss is latent for current callers and live at the store contract.
- **Probe (functional, isolated Nursery, 04abc1e):** `add(goals=` 20 goals
  of ~507 chars each`)` → **8 goals stored, each exactly 200 chars**;
  goals 9–20 absent; returned normally, no receipt; fresh load from disk
  shows the same 8 × 200. Control: a single short goal stores whole.
- **DISPOSITION: DEFECT-CONFIRMED (store surface; latent for today's
  callers)** — silent loss of accepted data, reproduced: twelve whole
  goals and every surviving goal's tail past 200 chars are destroyed by
  the store with no signal of any kind. The same sharpening of the
  SYS-C29 packet's "bound-consistent guard" label applies as in R14: the
  chain-level bounds coincide, the store-level cut is silent and
  unmarked. No repair for goals is in flight (see R14).
  *Failing-first sketch:* `Nursery.add` with 20 goals × 500 chars and
  assert all 20 are stored whole — fails today at `nursery.py:221-222`
  (8 stored × 200).

## R16 — Nursery reason cut to 160

- **Census site:** nursery.py:216 (exchange pre-cuts its own to 160 at exchange.py:716).
- **Site today (exact):** `reason=reason[:160]` at
  `form/dell_matrix/nursery.py:216`, same `Nursery.add()` construction.
  The admitted bound upstream is **1,000**, at three dock admission points
  in this tree — `inference_dock.py:607` (semantic-output validation),
  `:1120-1122` (host reason in `propose()`: *"Reason exceeds 1000
  chars"*), `:1639-1641` (semantic-verb entry) — and the Director's own
  session names the same constant (`MAX_REASON_CHARS = 1000`,
  `form/dell_matrix/director_session.py:43`). The store cuts all of it to
  160. Producer pre-cuts compound it, both verified in this tree:
  exchange composes its import reason and cuts it to 160 itself
  (`exchange.py:716`), and auto_growth does the same
  (`auto_growth.py:138`) — a long reason on those paths is cut before the
  store, then the store's cut is moot; on the dock path the store's cut
  is the live one.
- **Mechanism / who hits it:** the reason is the *why* of a proposal —
  the text the human confirm decision reads (and the dock evidence
  record copies verbatim). A docked proposal carrying a host-supplied
  1,000-char rationale lands with 160. One consumer depends on the cut
  today: the dock-session evidence validator requires reason ≤ 160
  (`form/dell_matrix/dock_session.py:143`), so any repair must reconcile
  that validator in the same circuit — it is already named in the reason
  circuit's brief.
- **Probe (functional, isolated Nursery, 04abc1e):** `add(reason="R"×500)`
  → stored reason length **160**; returned normally, no error, no marker;
  fresh load from disk shows the same 160. Control: a short reason stores
  whole.
- **DISPOSITION: DEFECT-CONFIRMED** — silent loss of admitted data,
  reproduced, and live on the main production path (unlike R14/R15, the
  dock itself feeds the store reasons up to 1,000 that the store then
  cuts to 160). This confirms first-hand the Q-S2.2 investigation's
  upgrade of the SYS-C29 packet's preliminary "silent bound" label to a
  silent-loss defect. **In-flight repair named, not credited:** the
  bounded reason circuit (admitted bound 1,000, lossless storage,
  pre-mutation refusal beyond, `dock_session.py:143` reconciliation,
  producer pre-cuts in scope) is building on its own branch; it has
  **not merged**, and main `04abc1e` still cuts at `:216`.
  *Failing-first sketch:* `Nursery.add` with a 500-char reason — and the
  same through dock `propose()` with a 500-char host reason — and assert
  the stored reason equals the input — fails today at `nursery.py:216`
  (stores 160).

---

## Wave summary

| Item | Site today (main 04abc1e) | Disposition | One-line basis |
|---|---|---|---|
| R12 — Director records evicted at 200, counted | director_records.py:30; eviction director_session.py:121, counter :126-130; persist.py:173 | **CONFIRMED-HINDERS** | Probe: 205 records → 200 kept, `dropped_total` = 5, oldest evicted, and the trimmed set + counter are what persist across reload — content gone, loss counted, never silent |
| R13 — Nursery label cut to 80 | nursery.py:211 | **DEFECT-CONFIRMED** | Probe: label 150 → stored 80, silently and durably, though the dock admitted it at ≤200 (inference_dock.py:43); identity survives only because the slug uses label[:28]; label repair (Q-S2.1) in flight, unmerged |
| R14 — Nursery detail cut to 2,000, silently | nursery.py:220 | **DEFECT-CONFIRMED** (store surface; latent for today's callers) | Probe: detail 3,000 → stored 2,000, no marker; today's producers pre-bound at the same 2,000 (dock schema :552, exchange pre-cut exchange.py:730), so the silent cut binds at the store contract, not yet a live caller |
| R15 — Nursery goals window 8 × 200 | nursery.py:221-222 | **DEFECT-CONFIRMED** (store surface; latent for today's callers) | Probe: 20 goals × ~507 → 8 stored × 200, goals 9–20 vanished with no receipt; producers pre-bound identically (dock schema :553-554), so the loss is latent for current callers, live at the store API |
| R16 — Nursery reason cut to 160 | nursery.py:216; pre-cuts exchange.py:716, auto_growth.py:138 | **DEFECT-CONFIRMED** | Probe: reason 500 → stored 160, silently and durably, though the dock admits reasons to 1,000 at three points (:607/:1120/:1639) and director_session.py:43 names the same 1,000; dock_session.py:143 depends on the 160 and must be reconciled by the in-flight, unmerged reason circuit |

**Queued for wave 4 (next five in register order):**
R17 — Mandell statement ceilings: MAX_BOUND=64 + phantom 8 on the Compose path (predicate.py:14-15; query_ops.py:147-157; spectrum_ops.py:11 at census) ·
R18 — Control nesting depth 4 (control_runtime.py:9; chain_exec.py:319-323 at census) ·
R19 — Cycle/Loop repetition clamp 1..5 at five sites, 99 on the sibling path (executor_leaf.py:164/:239; chain_exec.py:403; semantic_router.py:154; translate.py:681; flow_executor.py:58 at census) ·
R20 — Cell expansion depth 8 (seed.py:44, :352-353 at census) ·
R21 — Core II session evidence evictions: traces 512, snapshots 64, terminal tx 16 (core_ii_exec.py:7-8; spectrum_ops.py:14 at census).
*Wave-4 note:* R17–R21 leave the persistence/store family for the Mandell
execution family — several are Ace/Director-ruled semantics (R19's clamp
value was ruled in FIX step 6; DD-44 governs R17's bound honesty), so wave 4
must distinguish "the value hinders" from "the mechanism disobeys its own
ruling" item by item, and re-verify against the main of its day, including
whether the SYS-C29 family repairs (words PR #429, label, reason) have by
then merged and moved R13–R16's sites.
