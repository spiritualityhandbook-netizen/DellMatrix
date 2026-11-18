# LIMITS VERIFICATION — WAVE 2 (2026-11-15)

Read-only verification of register items **R7–R11** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 1 (`LIMITS_VERIFICATION_WAVE1_2026-11-15.md`), re-verified first-hand at
**current main `17ae4ce86743d9c5ff848a1b48111119d9bf9a32`** (g31proof_clone, clean
tree before and after). No code changed; nothing committed. All probes ran against
the clone's own `form/` tree with stub programs / scripted-judge dock sessions /
throwaway probe owners (state files removed after). Probe result: **21/21 checks
behaved as the census described**, except R7's refusal half (see below — the R2
repair discharged it).

**Numbering:** R7–R11 are taken exactly as Wave 1's queue named them, which matches
the census's ranked HINDERS-US register (R7 flag field index · R8 dock response
bound · R9 whole-output schema rejections · R10 exchange replication caps ·
R11 REPL review surfaces 20/12). No ambiguity found.

---

## R7 — flag defeats itself at field scale (40-neighbour index)

- **Census sites:** inference_dock.py:1731-1735 (40 neighbours, words[:120]/detail[:200]).
- **Sites today:** the flag branch of `_verb` at `form/dell_matrix/inference_dock.py:1832`;
  the neighbour list is built at `:1833-1837` — `words[:120]` at `:1834`,
  `detail[:200]` at `:1835`, `[:40]` at `:1837`. The list is drawn from `index`,
  which `_verb` builds from the coordinator snapshot (`snapshot_for` at `:1779`,
  index construction `:1783-1790`) — i.e. the 40-window sits *inside* the R3
  snapshot window (200 proposals / 200 units): on a field past 200, flag's
  candidates come from the snapshot slice first, then only 40 of those are shown.
  The prompt bound the assembled prompt is checked under (`:1853-1856`) is now
  `self._max_prompt_chars`, whose production default is **1,000,000**
  (`DEFAULT_MAX_PROMPT_CHARS`, `inference_dock.py:54`, raised by PR #416 — Wave 1 R2).
- **Probe (functional, scripted-judge dock session at the production default
  bounds, 17ae4ce):** a field of 45 placed units (words 300 chars each); `flag`
  on one target →
  - call **admitted** (`ok=True`) — the assembled prompt measured **10,244 chars**
    (words-only entries; the census's ≈20,800 estimate used full detail-bearing
    entries) — above the old 8,000 bound, far below today's 1,000,000 default;
  - the `[field]` section of the prompt the judge actually received contained
    **exactly 40** of the 44 non-target entries;
  - neighbour words arrived cut to **exactly 120** chars (stored 300).
  The `detail[:200]` cut at `:1835` is the same expression and is cited on code
  reading (the probe's entries carried no detail); everything else is probed.
- **DISPOSITION: CONFIRMED-HINDERS** — split verdict on the item's two halves:
  the *self-defeating refusal* half is **ALREADY-FIXED** (it rode on R2, exactly
  as the census sketch predicted: at the raised default the assembled flag prompt
  is admitted). The *vision* half binds unchanged: however large the field, the
  flag judge ever sees at most **40 neighbours, each cut to 120 chars of words
  and 200 of detail**, drawn from an already-windowed snapshot (R3) — on the
  1,052-unit Email Matrix field that is 40 truncated glimpses out of a 200-entry
  window out of 1,052.
  *Failing-first sketch:* place 45+ units with distinctive content in neighbour
  #41+ and in the tail past char 120 of neighbour #1's words; call `flag` and
  assert the judge's prompt contains neighbour #41 and the full words — fails
  today at `:1837` (count) and `:1834` (cut).

## R8 — Dock response bound 8,000 discards whole responses

- **Census sites:** inference_dock.py:47; rejection :1154-1155/:1781-1782.
- **Sites today:** `DEFAULT_MAX_RESPONSE_CHARS = 8000` at
  `form/dell_matrix/inference_dock.py:55` (unmoved in value; the constant moved
  one line). Enforcement today: propose path — transport rejection at `:1207`,
  post-return length rejection at `:1233` (`len(raw) > self._max_response_chars`
  → `response_too_large`, before parsing); verb path — `:1865` (transport) and
  `:1884` (length). The bound is also passed to the provider as `max_chars` on
  every `generate()` call. `dock()` exposes it as a parameter
  (`inference_dock.py:1976`, defaulting to the constant) and the `dock()`
  validator at `:2023-2032` deliberately keeps the response range at
  1..100,000 under the comment *"the response bound keeps its own unchanged
  range and default"* — while the prompt side of the same validator was raised
  by PR #416. So the bound is caller-raisable to 100,000, but **the default is
  8,000 and no production caller overrides it** (grep of `form/`: the only
  explicit non-default value is `form/mandell/r62_child.py:43`, a cross-process
  test child passing 10 on purpose).
- **Probe (functional, scripted-judge sessions at defaults, 17ae4ce):**
  - `propose()` with an 8,001-char provider response → `response_too_large`,
    **zero proposals created** — discarded before parsing.
  - A **9,812-char schema-valid** semantic output (label 200, words 5,000,
    detail 2,000, goals 8×200, reason 900 — every field inside its own schema
    bound) **passes `validate_semantic_output` itself**, but the same text
    returned by the judge on the `flag` path → `response_too_large`, discarded
    whole. The response bound, not the schema, is what kills it.
- **DISPOSITION: CONFIRMED-HINDERS** — the R2 repair raised the prompt side of
  this constant family and left the response side at 8,000 by explicit comment;
  every production dock session runs at that default, so a legitimate long
  synthesis/analysis is discarded *entire* (loudly — the refusal is a named
  receipt, not silent loss; this is not DEFECT-CONFIRMED). The discard is
  pre-parse: nothing is salvaged, no partial record lands.
  *Failing-first sketch:* dock a session at defaults whose judge returns the
  9,812-char schema-valid output above; assert a proposal lands — fails today
  at `:1884` (verb path) / `:1233` (propose path).

## R9 — Whole-output schema rejections (one long field kills the entire docked output)

- **Census sites:** inference_dock.py:43 (label 200), :44 (words 5,000),
  :544 (detail 2,000), :545 (goals 8), :546 (goal 200); enforcement :518-595.
- **Sites today (all present, enforcement unmoved in shape):** constants
  `MAX_LABEL_CHARS = 200` (`inference_dock.py:43`), `MAX_WORDS_CHARS = 5000`
  (`:44`), `MAX_DETAIL_CHARS = 2000` (`:552`), `MAX_GOALS = 8` (`:553`),
  `MAX_GOAL_CHARS = 200` (`:554`). Enforcement in `validate_proposal_output`
  at `:526` (label), `:528` (words), `:533` (detail), `:537-538` (goals/goal) —
  each raises `ProviderError`, rejecting the **whole** output; the same five in
  `validate_semantic_output` at `:593`, `:595`, `:598`, `:601-603`.
- **Probe (functional, direct validator calls, 17ae4ce):** a sound output with
  exactly one field one unit over its bound is rejected whole, five for five —
  label 201 → `ProviderError: label length out of bounds`; words 5,001 →
  rejected; detail 2,001 → rejected; **9 goals** → rejected; one goal of 201
  chars → rejected. Control: the same output with every field in bounds is
  admitted. Semantic path: label 201 → rejected identically. In every rejection
  **nothing lands** — no proposal, no partial record (the validators return a
  complete field dict or raise; there is no partial path).
- **DISPOSITION: CONFIRMED-HINDERS** — unchanged since the census. The rejection
  is explicit (a `ProviderError` surfacing as a refusal receipt), so this is
  not silent loss; the hindrance is the *granularity*: one over-long field
  converts an otherwise sound docked judgment into total non-landing, where
  per-field handling (store whole where the store allows; mark-and-truncate
  only the offending field where a bound genuinely remains) would preserve it.
  Interaction noted for the repair circuit: the label gate is doubly hollow on
  current main because the Nursery then cuts stored labels to 80 anyway (R13).
  *Failing-first sketch:* for each of the five fields, submit an output with
  only that field one unit over and assert the judgment still lands with the
  other fields intact (and the offending field handled per the repair
  contract) — fails today at `:526/:528/:533/:537-538` and `:593-:603`.

## R10 — Exchange replication caps (50/packet, 200 stored, refusal at 200 live)

- **Census sites:** exchange.py:63/:64/:955; persist retention persist.py:182/:185.
- **Sites today (all unmoved in value):** `MAX_RECEIPTS = 50` at
  `form/dell_matrix/exchange.py:63`, enforced in `validate_packet` at `:203`
  (`receipts out of bounds`, whole packet refused); `_MAX_RECEIPT_ENTRIES = 200`
  at `:64`, enforced in `record_receipt` at `:922-924` (evict oldest +
  `_bump_dropped` counter) and at serialize via `serialize_receipts_section`'s
  `max_keep` (`:877/:891`); `_MAX_SEED_ENTRIES = 200` at `:955`, enforced in
  `record_seed_payload` at `:1059-1085` (evict oldest *non-live* payload +
  counter; if every retained payload is live, delete the new entry and raise).
  Second enforcements at serialize: `form/persist.py:181` (receipts section)
  and `:184` (seeds section), both feeding the same `max_keep` machinery.
- **Probe (functional, stub programs, 17ae4ce):**
  - 201 `record_receipt` calls → **200 stored**, `exchange_receipts_dropped_total
    == 1` (the 2026-10-30 silent-loss defect stays fixed: eviction is counted —
    but the evicted receipt's *content* is still gone).
  - `validate_packet` with **51 receipts → `ExchangeError: receipts out of
    bounds`** (whole packet refused); control with 50 → admitted. A Keep backed
    by 51+ receipts still cannot be exported or imported at all.
  - `record_seed_payload` with 200 retained payloads **all live** → the 201st
    is **refused outright** (`exchange_seeds is full and every retained payload
    belongs to a live proposal; refusing to evict a live original`), store
    unchanged at 200.
  The census's downstream conversion — an evicted receipt later makes
  re-export refuse as provenance-incomplete — rests on code reading: the seed
  entry stamps `receipts_expected` + `receipts_hash` at record time
  (`exchange.py:1040-1049`), so a receipt evicted from the 200-store can no
  longer substantiate the export the stamp promises.
- **DISPOSITION: CONFIRMED-HINDERS** — all three caps bind exactly as the census
  described. The mitigations are real (drops counted, live-original eviction
  refused fail-closed) and are why this is not DEFECT-CONFIRMED: nothing is
  *silently* lost. But at scale the caps still convert into hard stops on
  legitimate work: the 201st live import is refused, a 51-receipt Keep cannot
  move at all, and the receipt store's content is still evicted at 201 with
  only a counter surviving.
  *Failing-first sketch:* (a) build a packet carrying 51 receipts for one Keep
  and assert export+import round-trips — fails today at `exchange.py:203`;
  (b) record 201 receipts and assert all 201 remain retrievable — fails today
  at `:922-924`; (c) import a 201st live seed payload and assert it lands —
  fails today at `:1059-1085`.

## R11 — Ace's review surfaces show 20 of N / 12 of N

- **Census sites:** repl.py:525 (`pending[:20]`), repl.py:1231 (`ranked[:12]`).
- **Sites today:** `_show_proposals` (`form/repl.py:556`, invoked from the REPL
  command path at `:2726`) slices `pending[:20]` at **`repl.py:587`**, under a
  header at `:586` that prints the true total (`Nursery has {len(pending)}
  proposal(s):`); the rank handler `_handle_macro_rank` (`:1247`) slices
  `ranked[:12]` at **`repl.py:1293`**, under a header printing `Ranked
  {len(ranked)} proposals:`. Neither surface prints a continuation / "…and N
  more" line (verified on captured output: no `more`/`...` line). The
  underlying sources are uncapped — `p.list_proposals()` and
  `p.ranked_proposals()` return everything; only the doors slice.
- **Probe (functional, direct handler calls with a stub program, 17ae4ce):**
  - 25 pending proposals → header prints **25**, exactly **20** numbered
    entries shown; proposals #21–25 are not displayed, hence cannot be
    selectively confirmed or rejected from this surface.
  - 15 ranked proposals → header prints **15**, exactly **12** numbered
    entries shown.
- **DISPOSITION: CONFIRMED-HINDERS** — unchanged since the census. The totals
  are honest (the header admits N exists), but there is no paging or
  continuation the same command accepts, so selective human judgment — the
  entire point of Ace's primary Nursery review surface — is impossible past
  entry 20 (proposals) / 12 (rank) in a single viewing; `confirm all` is not a
  substitute for selective review.
  *Failing-first sketch:* seed 25 pending proposals, invoke the proposals
  surface, and assert all 25 are reachable for selective action (shown, or
  paged via a continuation the surface itself offers); same with 15 on the
  rank surface — fails today at `repl.py:587` / `:1293`.

---

## Wave summary

| Item | Site today (main 17ae4ce) | Disposition | One-line basis |
|---|---|---|---|
| R7 — flag 40-neighbour index, words[:120]/detail[:200] | inference_dock.py:1832-1837 (index from snapshot :1779) | **CONFIRMED-HINDERS** (refusal half ALREADY-FIXED) | Probe: at the raised 1,000,000 default the 10,244-char flag prompt is admitted (R2 discharged the self-refusal), but the judge still sees exactly 40 of 44 neighbours, words cut 300→120 |
| R8 — dock response bound 8,000 | inference_dock.py:55; enforcement :1233/:1884 | **CONFIRMED-HINDERS** | Probe: 8,001-char response discarded pre-parse with zero proposals; a 9,812-char schema-valid output passes the schema yet is discarded whole by the response bound; default unoverridden by any production caller |
| R9 — whole-output schema rejections | inference_dock.py:43/:44/:552-554; enforcement :526-:538, :593-:603 | **CONFIRMED-HINDERS** | Probe: five-for-five — one field one unit over (label 201, words 5,001, detail 2,001, 9 goals, goal 201) rejects the entire output; nothing lands, no partial path |
| R10 — exchange caps 50 / 200 / 200-live | exchange.py:63/:64/:955; persist.py:181/:184 | **CONFIRMED-HINDERS** | Probe: 51-receipt packet refused whole (50 admitted); 201st receipt evicts oldest (counted, content gone); 201st all-live seed payload refused outright |
| R11 — REPL surfaces 20 of N / 12 of N | repl.py:587 (_show_proposals); repl.py:1293 (_handle_macro_rank) | **CONFIRMED-HINDERS** | Probe: 25 pending → header says 25, 20 shown, no continuation; 15 ranked → 12 shown; underlying list/ranked sources are uncapped |

**Queued for wave 3 (next five in register order):**
R12 — Director records evicted at 200, counted (director_records.py:30; director_session.py:121-130; persist.py:173 at census) ·
R13 — Nursery label cut to 80 (nursery.py:211 at census) ·
R14 — Nursery detail cut to 2,000, silently (nursery.py:220 at census) ·
R15 — Nursery goals window 8 × 200 (nursery.py:221-222 at census) ·
R16 — Nursery reason cut to 160 (nursery.py:216 at census).
*Wave-3 note:* R13–R16 are the SYS-C29 sibling family — repairs for this family
are in flight on separate branches (words landed as PR #429; the label circuit
was Director-authorized 2026-11-15), so wave 3 must re-verify against the main
of its day and state which sites, if any, the merged repairs already moved.
