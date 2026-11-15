# LIMITS VERIFICATION — WAVE 8 (2026-11-15) — FINAL WAVE

Read-only verification of register items **R37–R42** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 7 (`LIMITS_VERIFICATION_WAVE7_2026-11-15.md`), re-verified first-hand at
**current main `56b6d9cb40cb68d3f50e4c39537769b242cb13a7`** (the same head Waves 6
and 7 verified; g31proof_clone fetched, checked out at that head, verified clean
before and after — probes ran in-memory on throwaway owners `w8probe*` through
the production APIs, probe-owner Nursery state files removed afterward, no code
changed, nothing committed). Functional probes ran for every item; network-facing
functions were probed through stubbed transports (`_http_json`, `_json_get`,
`research_topic`), so every bound was exercised through the real code path with
no live network call.

**Numbering:** R37–R42 are taken exactly as Wave 7's queue named them, matching
the census's ranked HINDERS-US register (R37 Bimo framing 1,200 · R38 bridge
serialization 8,000 · R39 Claude output cap 2,048 · R40 research intake windows ·
R41 harmonic lattice size snap {12, 14} · R42 entities payload 12 ghosts). R42
closes the ranked list. Line numbers are today's throughout.

**Method (wave-4 ruled-semantics separation, binding):** every item separates
**(a) the value hinders** (a realistic workload needs more), **(b) the mechanism
disobeys its ruling / loses silently** (DEFECT), and **(c) FAITHFUL-GUARD** (the
bound implements its ruling, refusal visible, nothing silent — a small value
alone is not a defect). Rulings are cited from the working plan
(`director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md`) and test-pinned contracts;
where no ruling exists, the item says UNRULED plainly. Where a census claim fails
first-hand, this report says so and withdraws it, per the standing wave standard
(Wave 6's R29 strength sub-claim, Wave 7's R32/R33/R35 corrections).

**Headline of the wave:** the two bridge items split exactly as Wave 7's queue
predicted — R38's serializer silently amputates whole results for every
`to_dict()` consumer, and R39's Claude cap is the file's only output bound that
`dispatch()` cannot reach, with the provider's own truncation signal
(`stop_reason`) dropped on the floor. R37 reproduces with a configuration the
Forge itself validates: a fully-worn maximal Bimo frames at 1,287 chars and is
cut to exactly 1,200, severing the last slot's line mid-word, while the session
record carries the configuration as worn. Against that, the census is wrong
twice more in this stretch: R40's intake windows bind exactly as inventoried but
no production caller reaches either search function today, so the
Nursery-starvation scenario is not live (and both functions disclose their full
counts, a mitigation the census line never mentioned); and R42's slice lives in
`all_entities()`, not the `nodes_payload()` the census named — in both its
ranked line and its register row. R41, the doctrine's namesake, acquits as a
declared, test-pinned shape policy whose only door discloses the resulting size
and the allowed set, and loses nothing.

---

## R37 — Bimo framing cut to 1,200, silently

- **Census sites:** inference_dock.py:970 (`"\n".join(lines)[:1200]`).
- **Sites today:** `_bimo_framing` at `form/dell_matrix/inference_dock.py:993`;
  the cut is its return at **`:1024`** (census line drifted +54). The framing is
  prepended to the prompt in `propose()` at `:1176-1178` and to verb prompts at
  `:1845-1847`. The session evidence record carries only the configuration's
  name (`record["bimo"] = bimo_config["name"]`, dock `__init__`, ~:956).
- **The mechanism:** the framing is one line per worn element — a header, the
  pilot block (pilot / focus / limits), then one line per filled slot
  (`slot {slot}: {name} — {role}; limits: …`). Slots are a **closed set**:
  `personas.BIMO_SLOTS` has exactly 11 members, configuration validation
  rejects any other slot (bimo_forge.py:101-103), and the persona registry
  holds 11 personas. The framing is therefore bounded by construction — the
  census's own sketch premise — and its maximum is computable exactly.
- **Probe (functional, 56b6d9c):** the maximal *valid* configuration — every
  legal slot filled, each assigned the persona whose text maximizes its line,
  pilot likewise — passes `bimo_forge.validate_configuration` (`(True, '')`).
  Its uncut join is **1,287 chars across 15 lines**. `DockedSession._bimo_framing`
  on that configuration returns **exactly 1,200 chars**: the final slot line
  (`slot body: …`) is severed mid-word (the output ends `…\nslot body`), the
  last persona's role and limits never reach the prompt, and there is **no
  truncation marker** of any kind. The dock's session record for such a wear
  carries the configuration name — worn, by the record; partial, in the prompt.
- **The ruling:** no ruling names 1,200 — **UNRULED**; no test pins the value.
- **DISPOSITION: DEFECT-CONFIRMED.** (b) The cut is silent, mid-line, and
  reachable today by a configuration the Forge's own validator accepts — not
  headroom (contrast R33's unreachable fog arm): a fully legal wear is
  partially worn in the prompt while every durable surface says it is worn.
  The pairing Wave 7 flagged is real: R34 retires configurations silently at
  the store, R37 wears them partially at the prompt, and neither surface
  accounts for the difference. (a) is not separately charged — the value's
  harm *is* the silence; a disclosed bound would be a different item.
  *Failing-first sketch:* build the maximal validated configuration (all 11
  slots, longest-text personas), call `_bimo_framing()`, and assert the output
  equals the full join (or that the wear was refused at dock time with a named
  receipt) — fails today at `inference_dock.py:1024` (1,200 of 1,287, last
  line severed). Repair shape (the census's): assemble whole — framing is
  bounded by the closed slot set and the persona registry, so no bound is
  needed — or refuse the wear if framing exceeds a named bound; never send a
  silently partial wear.

## R38 — Bridge result serialization cuts text to 8,000 for consumers

- **Census sites:** llm/bridge.py:48 (`ProviderResult.to_dict()`), consumed by
  llm/cli.py:71/74 and JSON consumers.
- **Sites today:** identical line — `form/llm/bridge.py:48`,
  `"text": self.text[:8000]`, inside `ProviderResult.to_dict()` (:43-51).
  Consumers today: `form/llm/cli.py:66` and `:72` (census lines drifted −5/−2;
  both print `json.dumps(bridge.call(...).to_dict())` — the sister-terminal
  CLI's entire output), and `bridge.py:495/:497` (`enhance_matrix`, whose
  per-provider results are likewise serialized through `to_dict()`).
- **Probe (functional, 56b6d9c):** `ProviderResult("claude", True,
  text="y"×20000).to_dict()` → the in-memory `.text` is **20,000** chars; the
  serialized dict's `text` is **8,000**. The dict's keys are exactly
  `{provider, ok, text, error, meta}` — no length, total, or truncation field
  exists, so a consumer cannot distinguish a whole 8,000-char answer from the
  first 8,000 of a longer one.
- **The ruling:** none names 8,000 at this site — **UNRULED** (the dock's own
  8,000 response bound is a different mechanism, R8, at inference_dock.py:55;
  nothing rules a second, silent cut at the bridge's serialization boundary).
  No test pins it.
- **DISPOSITION: DEFECT-CONFIRMED.** (b) A serializer's whole job is faithful
  representation; this one silently amputates the payload it exists to carry,
  for *every* consumer of the bridge's public result shape — the in-memory
  result is whole, so the loss is created at the boundary and visible nowhere.
  That is the R23 pattern (silent capture cuts) at a second site, not a
  display window: `to_dict()` is not a view, it is the contract other programs
  read. *Failing-first sketch:*
  `ProviderResult("x", True, text="y"*20000).to_dict()["text"]` equals the
  full text (or the dict carries a disclosed total/truncation flag) — fails
  today at `bridge.py:48` (8,000 of 20,000, no flag). Repair shape (the
  census's): serialize whole; a consumer that needs a preview slices its own
  view and labels it, exactly as the dock's `last_response_view` already does
  with disclosed truncation.

## R39 — Claude output cap 2,048 tokens, hard-coded and unexposed

- **Census sites:** llm/bridge.py:424.
- **Sites today:** `"max_tokens": 2048` at `form/llm/bridge.py:425`, a literal
  in the `_claude` payload (:417-449). `dispatch()` (:233-236) threads
  `model`, `timeout`, and `max_bytes` to every provider — and no output-token
  parameter exists anywhere in the file: a whole-file grep for
  `max_tokens` / `num_predict` / `maxOutputTokens` / `max_output_tokens`
  returns **only :425**. Claude is not merely the only bound not threaded
  through `dispatch()`; it is the only provider whose payload carries an
  output-token bound at all.
- **Probe (functional, stubbed `_http_json`, 56b6d9c):**
  `dispatch("claude", "hello")` sends `max_tokens: 2048` in the payload.
  `dispatch("claude", "hello", max_tokens=8192)` raises
  `TypeError: LLMBridge.dispatch() got an unexpected keyword argument
  'max_tokens'` — no caller can raise the cap, confirming the census's
  "unexposed" charge first-hand. Sharper: when the stubbed response carries
  `"stop_reason": "max_tokens"`, the result comes back `ok=True` with
  `meta = {model, requested_model}` — `_claude` never reads `stop_reason`,
  so a truncated answer is indistinguishable from a complete one in the
  result every consumer receives.
- **The ruling:** none names 2,048 — **UNRULED**. The file's own pattern
  (explicit model/timeout/read-bound "reach the actual provider request",
  dispatch docstring :238-241) is the standing design contract the literal
  bypasses.
- **DISPOSITION: CONFIRMED-HINDERS (the value, unexposed) +
  DEFECT-CONFIRMED (the silence).** Separate as the method requires. (a) Any
  legitimate Claude answer longer than 2,048 tokens is cut by the provider,
  and the one bound a caller most plausibly needs to raise is the one bound
  the bridge's own threading pattern omits — the census scenario reproduces
  exactly. (b) Independently, dropping `stop_reason` means the truncation
  that *does* happen is reported nowhere: the provider discloses it, the
  bridge discards the disclosure. *Failing-first sketch:* dispatch a Claude
  call with an explicit `max_tokens` and assert the payload carries it, and
  assert a `stop_reason: "max_tokens"` response surfaces in the result's
  meta — fails today at `bridge.py:233` (TypeError) and `bridge.py:445-449`
  (meta carries model only). Repair shape (the census's): thread
  `max_tokens` through `dispatch()` and `_claude()` exactly as `max_bytes`
  already is, with a practical default; copy `stop_reason` into `meta` so a
  capped answer is a labeled answer.

## R40 — Research intake windows: far-wide search surfaces ≤24 ideas, words cut to 400

- **Census sites:** internet_gate.py:306-404 (DDG [:8]/[:3], Wikidata [:6],
  hits [:20], topics [:5], ideas [:24]; text [:900]/[:500]/[:400]).
- **Sites today:** `search_public` at `form/dell_matrix/internet_gate.py:284` —
  abstract text `[:900]` (:302), related topics `[:8]` (:306) with title
  `[:80]` / text `[:500]` (:309-310), nested group topics `[:3]` (:315) with
  the same field cuts (:318-319), Wikidata `limit=6` in the URL (:336) and
  `[:6]` (:340), and the return at :357-359: `"hits": hits[:20]` beside
  `"count": len(hits)`. `search_far_wide` at `:362` — idea label `[:72]` /
  words `[:400]` (:370-371), query tokens `[:4]` (:379), expansion topics
  `[:5]` (:382), expansion label/words `[:72]`/`[:400]` (:386-387), and the
  return at :404-405: `"ideas": unique[:24]` beside `"count": len(unique)`.
  Every census slice is present at the inventoried size.
- **Probe (functional, stubbed `_json_get` / `research_topic`, 56b6d9c):**
  with flat related topics the source windows bind first (16 hits, count 16;
  the abstract's 3,000 chars arrive as 900). With grouped related topics the
  outer windows bind exactly as inventoried: **32 hits counted, 20 returned**;
  far-wide: **25 unique ideas, 24 returned**. A 5,000-char source text becomes
  a **400-char** idea `words`, and the idea dict's keys are exactly
  `{label, source, url, words}` — no marker that the text was cut. Two facts
  the census line did not record: both functions **disclose their full
  totals** in `count` (32 and 25 above, against 20 and 24 returned), so the
  windowing is not silent at the count level; and the excess is nonetheless
  **unrecoverable** — neither function takes a paging parameter, so a caller
  is told more exists and given no way to reach it.
- **The census's live scenario does not reproduce: nothing calls either
  function.** A whole-tree grep (form/, gui/, src/, preform/) finds
  `search_far_wide` / `search_public` referenced only inside internet_gate.py
  itself (its own smoke, :425) and in `form/mandell/gate_hardening_test.py`,
  whose header states it flatly (:8): *"No Program/REPL caller reaches
  search_far_wide today."* The Program's internet surface is
  turn_on/turn_off/status/fetch_url/research_topic (open.py:1195-1219);
  `research_topic` — the one live intake path, called by open.py:1219 and
  code_evolution.py:185 — is a different function and carries none of R40's
  windows. No code path converts far-wide ideas into Nursery proposals, so
  "at most 24 ideas ever reach the Nursery proposal path" occurs nowhere in
  the running program.
- **The ruling:** none names these windows — **UNRULED**; the gate's hard
  OFF-by-default posture is ruled and test-pinned (gate_hardening_test), and
  is not in question here.
- **DISPOSITION: REFUTED AS A LIVE LIMIT — RECLASSIFIED (unconsumed intake
  contract).** The windows are real, verified in the gate's return contract
  at their inventoried sizes, and the per-item text cuts ([:900]/[:500]/
  [:400]) are silent at the item level; but the hindrance the census charged
  — research starvation at the Nursery door — has no consumer to starve, and
  the charge is withdrawn in the R35 shape. What remains, recorded honestly:
  a dormant intake contract whose windows a future consumer would inherit
  whole — count-disclosed but unpageable, with item text cut unmarked. If
  far-wide intake is ever wired to proposal creation, the census's sketch
  (return the full set; window explicitly at proposal creation with the
  total reported) is the shape to build then. No repair sketch is owed for
  an unconsumed contract under this wave's method.

## R41 — Harmonic lattice size silently snapped to {12, 14}

- **Census sites:** harmonic_core.py:32-34, :52-58 (`normalize_size`).
- **Sites today:** `SIZE_CHROMATIC = 12` / `SIZE_HARMONIC = 14` /
  `ALLOWED_SIZES = (12, 14)` at `form/dell_matrix/harmonic_core.py:32-34`;
  `normalize_size` at **:48-53** (snap to nearest allowed). Its only
  production caller is `Program.set_lattice_size` (open.py:1089-1094), which
  returns `{"ok": True, "size": s, "allowed": [SIZE_CHROMATIC,
  SIZE_HARMONIC]}`. No REPL door reaches it — the only other callers are
  open.py's own smoke (:2231/:2233).
- **The R30 discipline, applied (what actually consumes size):** nothing
  structural requires the snap. `HarmonicLattice` (harmonic_lattice.py:92)
  takes `size` as a plain field and never normalizes it; its cells are an
  unbounded dict keyed by coordinate (the census's own exemplar finding),
  and `note_at`'s `% 12` is chromatic note *naming*, independent of lattice
  size. Per Wave 7's instruction, the snap was tested as a possible shape
  contract before being called a hindrance — and the module declares it as
  exactly that: the docstring (:5-11) names "a lattice size policy
  (12 | 14)" as one of the module's contents, the constants are commented
  "12 = chromatic convenience · 14 = Harmonic form geometry" (:31), and the
  module's own smoke checks pin the behavior (`harmonic_core.py:191-192`:
  "size 14 allowed", "size snap" — `normalize_size(13) in ALLOWED_SIZES`).
- **Probe (functional, 56b6d9c):** `normalize_size(20)` → **14**,
  `normalize_size(13)` → **12**, `normalize_size(100)` → **14** — the snap
  binds exactly as inventoried. But: `HarmonicLattice(size=20)` works
  natively (size stays 20, cells put/get normally), and
  `Program.set_lattice_size(20)` returns `{"ok": True, "size": 14,
  "allowed": [12, 14]}` with **every lattice cell preserved** — the door
  discloses the resulting size and the full allowed set, and no state of
  any kind is lost in the snap.
- **The ruling:** no Ace/Director ruling names {12, 14} — the value is
  **UNRULED** at the authority level; the policy is the build's own
  declared, test-pinned contract.
- **DISPOSITION: RECLASSIFIED-GUARD.** Separate as the method requires.
  (b) No defect: the mechanism implements its declared policy faithfully,
  the policy is documented in the module header and pinned by its own
  smoke contract, the only door returns the actual size and the allowed
  set (a caller can see precisely what happened), and the snap destroys
  nothing — cells and KeyLedger addresses are untouched by a size change.
  (a) The census's hindrance reading does not survive either: the charge
  was a *silent* shape ceiling, but the ceiling is neither silent at its
  door nor load-bearing anywhere downstream — size is a policy label on
  an unbounded store, not a capacity. Two honest residuals, recorded as
  notes rather than defects: the `set_lattice_size` return does not echo
  the *requested* size (a caller must compare request against `size`
  itself), and whether sizes beyond {12, 14} *should* be legal shapes is
  a value question no authority has ruled — if Ace ever wants a 20-lattice,
  legalizing it is a one-line policy change in a module that would lose
  nothing by it, not a repair. No repair sketch is owed.

## R42 — Entities payload shows 12 Nursery ghosts

- **Census sites:** open.py:550 (`ranked_proposals()[:12]`), named as
  `nodes_payload` in both the ranked line and the census register row
  (CENSUS.md:279).
- **Sites today — with a census correction:** the slice is at
  `form/open.py:550` exactly as inventoried, but the function containing
  it is **`all_entities()`** (open.py:513-574), not `nodes_payload()`.
  `nodes_payload()` (:433-454) contains no ghosts at all — it lists plane
  units only. The census's line number and mechanism were right; its
  function name was wrong in both places it appears, and is corrected
  here. `all_entities()` is the visual-surface payload: consumed by
  live_visual.py:214 and :491 (the lattice/world payloads Ace inspects),
  repl.py:2050, and open.py:484 (`look_report`).
- **Probe (functional, 56b6d9c):** 15 pending proposals on a throwaway
  owner → `list_proposals()` returns **15**, `ranked_proposals()`
  (open.py:1485) returns **15** (uncapped, as the census said), and
  `all_entities()` carries exactly **12** entries of kind
  `nursery_ghost`. No entry anywhere in the payload carries a total,
  count, or continuation — the 13th–15th pending proposals are invisible
  on the surface and their existence is disclosed nowhere on it.
- **The ruling:** none names 12 — **UNRULED**; no test pins the value.
  Family: R11 (the REPL's 20-of-N display window), dispositioned
  CONFIRMED-HINDERS in Wave 2 on the same shape.
- **DISPOSITION: CONFIRMED-HINDERS (the value; display surface).**
  (b) No mechanism defect separate from the window itself: nothing is
  deleted or altered — the underlying listings are uncapped and the
  proposals remain fully actionable through them; the slice disobeys no
  ruling. (a) The hindrance is the R11 shape on the visual surface: the
  payload Ace inspects presents 12 pending ghosts as though they were
  the pending set, with no total stated, so a 13th pending proposal —
  routine after any growth run — cannot be seen, hence cannot be
  selectively judged, from the primary visual surface.
  *Failing-first sketch:* seed 15 pending proposals and assert
  `all_entities()` exposes 15 `nursery_ghost` entries (or a stated
  pending total in the payload) — fails today at `open.py:550` (12 of
  15, no total). Repair shape (the census's, as R11): emit all pending
  as ghosts — they are lightweight entries — or page the ghosts with
  the total stated in the payload.

---

## Wave summary

| Item | Site today (main 56b6d9c) | Disposition | One-line basis |
|---|---|---|---|
| R37 — Bimo framing cut 1,200 | inference_dock.py:1024 (in `_bimo_framing` :993); prepended :1176/:1845 | **DEFECT-CONFIRMED** | Probe: a Forge-validated maximal configuration (all 11 legal slots, real personas) frames at 1,287 chars; the function returns exactly 1,200, severing the last slot line mid-word, no marker — while the session record carries the configuration as worn |
| R38 — Bridge serialization cut 8,000 | bridge.py:48 (`ProviderResult.to_dict`); consumers cli.py:66/:72, bridge.py:495/:497 | **DEFECT-CONFIRMED** | Probe: 20,000-char result serializes to 8,000 with no length/total/flag field — the in-memory result is whole, so the loss is created silently at the boundary every consumer reads |
| R39 — Claude output cap 2,048 | bridge.py:425 (literal in `_claude`); `dispatch()` :233 threads model/timeout/max_bytes only | **CONFIRMED-HINDERS** (value) + **DEFECT-CONFIRMED** (silence) | Probe: payload carries 2048; `dispatch(..., max_tokens=8192)` raises TypeError — the file's only output bound is the one no caller can reach; and a `stop_reason: "max_tokens"` response returns ok=True with the truncation nowhere in meta |
| R40 — Research intake windows | internet_gate.py:284 (`search_public`), :362 (`search_far_wide`); slices :302-:405 | **REFUTED as a live limit — RECLASSIFIED (unconsumed intake contract)** | Probes: windows bind exactly as inventoried (32 counted → 20 hits; 25 unique → 24 ideas; 5,000-char text → 400-char words, unmarked) and both returns disclose full `count` — but a whole-tree grep finds no production caller for either function (gate_hardening_test.py:8 states it), so the Nursery-starvation scenario occurs on no live path |
| R41 — Harmonic lattice size snap {12, 14} | harmonic_core.py:34 (ALLOWED_SIZES), :48-53 (`normalize_size`); only caller open.py:1091 | **RECLASSIFIED-GUARD** | Probe: snap binds (20→14, 100→14) but `HarmonicLattice(size=20)` works natively, `set_lattice_size(20)` returns the actual size + allowed set, and all cells survive — a declared, smoke-pinned shape policy (module docstring; :191-192) on an unbounded store; nothing lost, nothing downstream requires it |
| R42 — Entities payload 12 ghosts | open.py:550, in **`all_entities()`** (:513) — census named `nodes_payload` (:433), which holds no ghosts | **CONFIRMED-HINDERS** (value) | Probe: 15 pending → exactly 12 `nursery_ghost` entries, no total anywhere in the payload, while `list_proposals()` and `ranked_proposals()` both return all 15 — the R11 display-window shape on the visual surface (live_visual.py:214/:491) |

---

## CLOSE-OUT — the census verification program's closing record

Waves 1–8 have now re-verified, first-hand and at a stated head, **every item
on the census's ranked list, R1–R42**. R1 was verified by its own circuit
(SYS-C29) rather than by a wave and is labeled as such. Final dispositions:

| Item | Final disposition | Item | Final disposition |
|---|---|---|---|
| R1 — Nursery words 5,000 → 240 | **DEFECT-CONFIRMED** (census-measured; repair circuit SYS-C29 / PR #429, not wave-verified) | R22 — Knowledge selection max 5 | **CONFIRMED-HINDERS** |
| R2 — Dock prompt bound | **ALREADY-FIXED** | R23 — Outcome evidence cuts + search 100 | **DEFECT-CONFIRMED** |
| R3 — Snapshot vision stack | **CONFIRMED-HINDERS** | R24 — Translate operand slices | **DEFECT-CONFIRMED** |
| R4 — Undo 32, no redo | **CONFIRMED-HINDERS** | R25 — Shorthand token drop | **DEFECT-CONFIRMED** (contract level) |
| R5 — Program history 24 | **CONFIRMED-HINDERS** | R26 — DuoBeta detail 120 ×3 sites | **DEFECT-CONFIRMED** |
| R6 — MAX_PARENTS=4 | **CONFIRMED-HINDERS** | R27 — REPL door clamps | **DEFECT-CONFIRMED** (history arm latent) |
| R7 — Judge index 40 / field cuts | **CONFIRMED-HINDERS** (refusal half already-fixed) | R28 — Forces/grow side-effect slices | **DEFECT-CONFIRMED** |
| R8 — Dock response bound 8,000 | **CONFIRMED-HINDERS** | R29 — Idea-create field caps | **DEFECT-CONFIRMED** (narrowed; census strength sub-claim refuted) |
| R9 — Whole-output schema rejections | **CONFIRMED-HINDERS** | R30 — Checkpoint retention | **FAITHFUL-GUARD** |
| R10 — Exchange caps 50/200 | **CONFIRMED-HINDERS** | R31 — Coordinator audit eviction 500 | **DEFECT-CONFIRMED** |
| R11 — REPL displays 20 / 12 of N | **CONFIRMED-HINDERS** | R32 — Graph vision caps 480 / 400 | **RECLASSIFIED-GUARD** (payload) + **DEFECT-CONFIRMED** (Studio draw slice) |
| R12 — Director records evict 200 | **CONFIRMED-HINDERS** | R33 — Growth fog gate 72 | **RECLASSIFIED-GUARD** (census scenario refuted) |
| R13 — Nursery label 80 | **DEFECT-CONFIRMED** | R34 — Bimo configurations cap 10 | **DEFECT-CONFIRMED** (silence; faithful to its pin) |
| R14 — Nursery detail 2,000 | **DEFECT-CONFIRMED** (store surface; latent) | R35 — scrub_context 2,000 | **REFUTED as a live limit** (dormant code, no caller) |
| R15 — Nursery goals 8 × 200 | **DEFECT-CONFIRMED** (store surface; latent) | R36 — Context nodes cap 1,000 | **CONFIRMED-HINDERS** |
| R16 — Nursery reason 160 | **DEFECT-CONFIRMED** | R37 — Bimo framing 1,200 | **DEFECT-CONFIRMED** |
| R17 — MAX_BOUND=64 + phantom 8 | **DEFECT-CONFIRMED** (phantom 8) + **CONFIRMED-HINDERS** (64 value) | R38 — Bridge serialization 8,000 | **DEFECT-CONFIRMED** |
| R18 — Control nesting depth 4 | **FAITHFUL-GUARD** | R39 — Claude cap 2,048 | **CONFIRMED-HINDERS** (value) + **DEFECT-CONFIRMED** (stop_reason silence) |
| R19 — Cycle/Loop clamp 1..5 + 99 | **DEFECT-CONFIRMED** (visibility; value faithful to its ruling) | R40 — Research intake windows | **REFUTED as a live limit** (unconsumed contract; windows verified, totals disclosed) |
| R20 — Cell expansion depth 8 | **CONFIRMED-HINDERS** | R41 — Harmonic size snap {12, 14} | **RECLASSIFIED-GUARD** |
| R21 — Core II evictions 512/64/16 | **FAITHFUL-GUARD** | R42 — Entities payload 12 ghosts | **CONFIRMED-HINDERS** (census function name corrected: `all_entities`) |

**Counts by lead disposition (compound items counted once, under their lead;
42 items total):**

- **DEFECT-CONFIRMED — 18** (R1, R13, R14, R15, R16, R17, R19, R23, R24, R25,
  R26, R27, R28, R29, R31, R34, R37, R38; defect halves also inside R32 and
  R39)
- **CONFIRMED-HINDERS — 15** (R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R20,
  R22, R36, R39, R42; a hinders half also inside R17)
- **FAITHFUL-GUARD — 3** (R18, R21, R30)
- **RECLASSIFIED-GUARD — 3** (R32, R33, R41)
- **ALREADY-FIXED — 1** (R2; plus R7's refusal half)
- **REFUTED as a live limit — 2** (R35, R40)

The pattern the eight waves establish, stated once: the register's
silent-loss charges were right far more often than its hindrance charges were
wrong — but five census claims did not survive first-hand contact (R29's
strength sub-claim, R32's "no truncation flag", R33's fog scenario, R35's live
limit, R40's live consumer), and two of its acquittals-by-omission were wrong
in the other direction (R34's sharpest site and R42's function were both
misnamed or unnamed in the census). The census was a good map with surveyed
errors; the waves were the survey.

**What remains unverified in the census register — stated honestly:**

1. **The ranked list covered 42 of the census's 70 HINDERS-US items.** The
   other **28 HINDERS-US register rows** stand on census classification only;
   no wave probed them first-hand.
2. **All 15 UNKNOWN-class items remain unverified.** Each carries a named
   deciding measurement in the register (e.g., the PreferenceLedger persist
   window at inspire_pack.py:500, the history-entry [:120] at open.py:338,
   the vision range/angle parameters at vision.py:13-14, the flow/Cycle
   99-vs-5 inconsistency at flow_executor.py:58); no wave ran any of those
   measurements.
3. **The 88 GUARDS-US and 12 ELASTIC items stand on census classification
   only**, except where a ranked item's verification touched a sibling
   (R36's depth/char siblings, R21's Core II family, R41's KeyLedger). Their
   guard character was not independently re-probed.
4. **`gui/server.py` was never inventoried at all** (CENSUS.md:416: the
   Studio server lives outside form/ and "a gui/ sweep is a follow-up lane
   if wanted"). Any limits in the Studio server are outside this program's
   evidence entirely. The same exclusion, by the census's own note, covers
   `form/ancient/` (dead/archived), `form/matrices/` (README-only), and
   executable evidence scripts; `form/mandell/diagnostics/` was inventoried
   as a single flagged non-production row.
5. **R1's verification is circuit-grade, not wave-grade:** its defect was
   measured by the census and its repair built as SYS-C29 (PR #429); it did
   not pass through a wave's independent probe protocol.

The ranked list is closed. Nothing is queued for a wave 9; any further
verification program starts from the remainders above, as a new decision.
