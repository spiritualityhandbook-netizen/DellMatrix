# LIMITS VERIFICATION — WAVE 6 (2026-11-15)

Read-only verification of register items **R27–R31** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 5 (`LIMITS_VERIFICATION_WAVE5_2026-11-15.md`), re-verified first-hand at
**current main `56b6d9cb40cb68d3f50e4c39537769b242cb13a7`** (merge of PR #430;
g31proof_clone fetched, checked out at that head, verified clean before and
after — all probe-owner state `W6*` removed). No code changed; nothing
committed. Functional probes ran for every item: R27 at the REPL door itself
(piped input through `python3 -m form.repl --owner W6R27 --load` against a
seeded owner), R28/R29/R30/R31 through the production APIs on throwaway
owners.

**Numbering:** R27–R31 are taken exactly as Wave 5's queue named them,
matching the census's ranked HINDERS-US register (R27 REPL door clamps ·
R28 forces/grow side-effect slices · R29 idea-create field caps · R30
checkpoint retention current+previous · R31 coordinator audit eviction 500).
Line numbers are today's throughout.

**Method (wave-4 ruled-semantics separation, binding):** every item separates
**(a) the value hinders** (a realistic workload needs more), **(b) the
mechanism disobeys its ruling / loses silently** (DEFECT), and **(c)
FAITHFUL-GUARD** (the bound implements its ruling, refusal visible, nothing
silent — a small value alone is not a defect). Rulings are cited from the
working plan (`director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md`) and
test-pinned contracts; where no ruling exists, the item says UNRULED plainly.

**Headline of the wave:** the door family is as the census described it, with
per-door disclosure gradations the census flattened — two REPL receipts
announce the clamped count as if it were the request (`ce develop`,
`evolve loop`), two print honest totals while offering no way past them
(`ledger`, `history`). The forces slices are worse than their census line in
one respect: the slice is insertion-ordered, so the same first units win
every activation and the rest are excluded *permanently*, not per-run. R29
narrows — its strength sub-claim does not reproduce. And R30 does not survive
the design-intent check: current+previous retention is the checkpoint
protocol's documented conservative shape, receipted at its own API, with the
frozen-target escape exactly where the one flow that needs it looks. The
wave's only pure silence defect is R31.

---

## R27 — REPL door clamps silently shrink explicit requests

- **Census sites:** repl.py:2270 (`ce develop` ≤20), :2310 + open.py:964
  (`evolve loop` ≤150), repl.py:4413 (connection `grow` ≤5), :2113
  (`ledger` ≤200), :2207 (`history` ≤48).
- **Sites today (all in `form/repl.py` unless noted):** `ledger` clamp
  `max(1, min(200, int(rest)))` at `:2191`; `history` clamp
  `max(1, min(48, int(part)))` at `:2294` (default 16); `ce develop` clamp
  `max(1, min(20, int(part)))` at `:2357` (default 10); `evolve loop` clamp
  `max(1, min(150, int(part)))` at `:2397` (default 12), **mirrored inside
  the Program method itself** at `form/open.py:964`
  (`Program.evolve_loop` clamps identically, docstring *"bounded; full 150
  via module"*); connection-session `grow` clamp
  `max(1, min(5, int(parts[1])))` at `:4596`.
- **The ruling:** no ruling names any of these values — **UNRULED**
  (census: historical default / unknown). The governing law is DD-44
  EXTENDED (plan §12.63a.2, cited in waves 4–5): wherever a limit is in
  play, the number is stated, or the operation asks, or it fails with the
  full why — no silent defaults. These doors rewrite the number in play
  before the operation runs and report the rewritten number as the result.
  Two partial disclosures exist and are recorded per door below: the
  `evolve loop` maximum is documented in the REPL's own help text
  (repl.py:130, *"(max 150)"*), and the `history`/`ledger` headers print
  true totals. A documented maximum is not a receipt-level flag that the
  maximum bound *this* request.
- **Probe (functional, at the door — seeded owner W6R27: 30 noted actions,
  250-entry DuoBeta ledger appended at the data level and saved; the door's
  behavior is the claim, not the ledger's growth path; REPL run with
  `--load`, which the door requires to load saved state at all):**
  - `history 100` → header *"History · 24 notes (last 24 shown)"*. The
    door clamp (48) never binds: storage (`history_max` 24, R5 — verified
    wave 1) has already discarded everything past 24, so the door's extra
    headroom is unreachable by construction, exactly as the census said.
    The header honestly discloses both totals; nothing says the request
    for 100 was not honored or that a cap exists.
  - `ledger 500` → header *"Growth ledger · last 200 of 250:"* and exactly
    200 entry lines. Storage beneath is uncapped (251 entries stored);
    the door clamp binds. The header discloses the true total — but the
    handler accepts only N, no offset or paging, so entries older than
    the newest 200 are unreachable from this door at any request size.
  - `ce develop 25` → the door announces *"Developing Code Evolution
    ×20…"* and runs 20. The announcement presents the clamped count as
    the run's size; the request (25) and the clamp appear nowhere.
    Beneath the door, `Program.ce_develop` (open.py:1225-1227) passes
    cycles through to `develop_loop` uncapped — the door is the only
    clamp in this chain.
  - `evolve loop 200` → receipt *"Evolve loop ×150 · gen=404
    mastery=0.577"*. 200 requested, 150 ran, the receipt presents 150
    without flagging the substitution. (The maximum is documented in
    help, above; the Program method clamps identically at open.py:964,
    so for this one door the census's "Program paths beneath are
    uncapped" does not hold — the clamp is duplicated, consistently.)
  - Connection-session `grow` (repl.py:4596) is **code-read**: the clamp
    sits inside the docked connection-session handler; standing up a
    docked session at the door is not a cheap probe. The expression is
    the same shape, and the Program path beneath it (`grow_ideas`) is
    uncapped (R28's main path).
- **DISPOSITION: DEFECT-CONFIRMED (the binding doors) — with the `history`
  door clamp carved out as LATENT.** The defect is the receipt shape, not
  the values: an explicit numeric request is rewritten before execution
  and the success output announces the rewritten number as the answer —
  DD-44 EXTENDED's named silence, at the user-facing door. Gradations,
  stated plainly: `ce develop` is the pure case (binds, undisclosed
  anywhere at the door, Program path beneath uncapped); `evolve loop`
  binds and is receipt-silent but help-documented, with the clamp
  duplicated in the Program method; `ledger` binds with honest totals
  but no reachability past the window; `history`'s door clamp cannot
  bind at all while storage caps at 24 (R5 owns that loss) — it is
  incoherent headroom (48 over 24), not an independent loss.
  *Failing-first sketch:* at the REPL door, `ce develop 25` and assert
  the announcement/receipt either reports 25 cycles run or names the
  clamp that reduced the request — fails today at `repl.py:2357`
  (announces ×20 as the run). Same shape for `evolve loop 200`
  (`repl.py:2397` + `open.py:964`) and `ledger 500` (assert the door
  can reach entries 201–250, by paging or a stated continuation — fails
  today at `repl.py:2191`). Repair shape: doors pass the request
  through where the path beneath is uncapped (`ce develop`,
  connection `grow`); where a bound is genuinely kept (`evolve loop`
  150, `ledger` window), the receipt states the clamp when it binds
  ("requested 200, capped at 150") and display windows gain a
  continuation the same command accepts. No test pins any of these
  clamps (census §"NO pins found"), so the repair is pin-free.

## R28 — Forces/grow side-effect slices skip ideas past 8/3/12/3

- **Census sites:** open.py:890 (force_growth plants [:8]), :903
  (force_water [:3]), :1322 (grow_ideas planting [:12]), :1330
  (grow_ideas water [:3]).
- **Sites today:** identical, at the census's exact lines —
  `form/open.py:890` (`force_growth`, first 8 plane units planted),
  `:903` (`force_water`, first 3 flowed), `:1322` (`grow_ideas`'
  parallel forces stage, first 12 planted), `:1330` (same stage, first
  3 flowed, only when water is active). The main growth engine above
  them (`self.growth.run(...)`, open.py:1313) is uncapped and runs over
  the scoped plane; the slices bind only the forces side-effect stage,
  whose own code comment calls it *"Nature forces grow in parallel
  (visible stages)"* (open.py:1319).
- **The ruling:** none — the census records the setter as unknown for
  all four sites. **UNRULED**.
- **Probe (functional, `open_program` + `place`, 56b6d9c; every fresh
  plane also carries the pre-existing `welcome` unit, so each seeded
  plane held 16 units, welcome first in insertion order):**
  - `force_growth()` on 16 units → **8 planted** (welcome + units
    01–07); units 08–15 not planted. Receipt is `{"ok": True, "lines":
    <growth map's first 8 lines>}` — no planted count, no plane total,
    no skipped names (the map itself is display-sliced at open.py:896).
  - `force_water()` → flowed exactly the first **3** (Welcome, Unit01,
    Unit02 — the latter two then merged into a river by the handler);
    units 03–15 received no flow. Receipt reports stream/pool counts
    only.
  - `grow_ideas(cycles=1)` with water active → **12 planted** (welcome
    + units 01–11); units 12–15 not planted; water stage flowed the
    first 3. The result's forces status carries `resonance_count: 12`
    for Growth — a bare count with no plane total beside it and no
    skipped set anywhere in the receipt.
  - **Permanence (the probe's sharpest finding):** planting is
    cumulative and guarded by a known-set check (open.py:891-894,
    :1323-1326), and the slice is taken over insertion order, which
    only appends. The same first 8/12 win every activation; a unit past
    the slice can never enter it. The exclusion is not per-run — it is
    structural and permanent for the life of the plane.
- **DISPOSITION: DEFECT-CONFIRMED (silent, permanent skip — not the
  slice sizes).** The mechanism takes a prefix of the plane as if it
  were the plane: on any field larger than a handful, the canonical
  force activations simply never touch the remaining ideas, no receipt
  at any of the four sites names or counts the skipped set against the
  plane total, and the insertion-order prefix makes the excluded set
  fixed forever rather than rotating. On the 1,052-unit Email Matrix
  field the census's arithmetic is the operative one: 1,049 ideas get
  no water from `force_water`. The main growth path being uncapped
  confines the defect to the forces stage; it does not disclose it.
  *Failing-first sketch:* seed a 16-unit plane, run `force_growth()`,
  and assert every plane unit is planted (or the receipt names the
  unplanted unit ids) — fails today at `open.py:890` (8 of 16 planted,
  receipt silent). Same shape for `force_water` (:903) and the
  `grow_ideas` forces stage (:1322/:1330). Repair shape: iterate the
  whole plane in the forces stages (their own purpose is field-wide),
  or take an explicit scope parameter in the GS-selection style and
  print the scope in the receipt; a silent prefix is the one shape the
  doctrine forbids.

## R29 — Idea-create field caps at the strong-create door

- **Census sites:** idea_create.py:44-47 (label 80, detail 2,000,
  goals 12, words 500, all silently truncated at parse; strength scored
  on the truncated detail).
- **Sites today:** the return-dict cuts sit exactly at
  `form/idea_create.py:44-47` (`label[:80]`, `detail[:2000]`,
  `goals[:12]`, `words[:500]`). Two mechanism facts the census line
  flattens: (i) `words` is **derived** at `idea_create.py:33` as
  `detail[:120]` — the `[:500]` at :47 is dead, and the operative words
  bound is **120**, tighter than the census's 500; (ii) `strength` is
  computed at `idea_create.py:41` — **before** the cuts, on the full
  detail and full goals list. The consumer is
  `form/dell_matrix/needs.py:27-46` (`parse_and_place`): it places
  `parsed["label"]`, `parsed["words"]`, `parsed["detail"]`,
  `parsed["goals"]` onto the plane via `program.place(...)` — the
  truncated values are what is placed, and through program save what
  persists; its receipt (`format_create_end`) prints the stored fields
  as-is, naming no cut.
- **The ruling:** none names these values — **UNRULED** (census:
  historical default; census §"NO pins found" confirms no test pins
  these caps). The module's own header states the door's law —
  *"Strong-idea law"* — which governs completeness (detail + goals
  present), not these bounds.
- **Probe (functional, `parse_create_line` + `parse_and_place`,
  56b6d9c):** a create line with a 100-char label, a 2,500-char detail
  and 15 goals parses to label **80**, detail **2,000**, goals **12**,
  words **120**. The placed unit carries detail 2,000 and goals 12 —
  the tail of the authored detail and goals 13–15 exist nowhere after
  the door. Strength: the parse returns **1.0 (Strong)**, identical to
  `strength_score(full detail, full goals)` and to
  `strength_score(truncated detail, truncated goals)` — the scoring
  formula (`idea_create.py:64-69`) saturates at 80 chars of detail, 3
  goals and 12 long words, so at any substantive scale the cut cannot
  move the score.
- **DISPOSITION: DEFECT-CONFIRMED — narrowed from the census
  statement.** The storage half reproduces exactly: three fields are
  cut silently at parse, and the cut text is what the strong-create
  door places and persists, with no receipt naming a cut — the store
  end of the operand chain R24 verified at the front end (translate),
  and the two reports should be read together before any repair
  circuit is scoped. The census's strength sub-claim **does not
  reproduce** at today's code and is withdrawn: strength is scored on
  the full detail (idea_create.py:41, before the :44-47 cuts), and
  the saturating formula makes the score insensitive to the cuts
  regardless — no repair is owed on the strength half. The words
  sub-item is corrected, not confirmed as stated: the operative cut
  is the 120-char detail-preview derivation at :33 (undisclosed at
  the door — the placed unit's `words` is a preview of its detail,
  not an authored field), and :47's `[:500]` never binds.
  *Failing-first sketch:* `parse_create_line` with a 2,500-char
  detail and 15 goals, then assert the placed unit (via
  `needs.parse_and_place`) holds the full detail and all 15 goals,
  or that the receipt names each cut with its bound — fails today at
  `idea_create.py:45-46` (2,000 / 12 placed, receipt silent). Repair
  shape: as R24 — refuse loudly with the field and bound named, or
  store whole; if the 120-char words preview is intended as a
  preview, name it as one in the placed record rather than letting it
  stand in the `words` field.

## R30 — Checkpoint retention: current + previous only

- **Census sites:** checkpoint_generation.py:289-295 (via
  open.py:1827 confirm_rollback safety checkpoint).
- **Sites today:** `_retain_current_and_previous` at
  `form/mandell/checkpoint_generation.py:288-331`, invoked at the end
  of every `commit_checkpoint` (receipt carries it at
  `checkpoint_generation.py:395`). The production wrapper is
  `form/mandell/core_i_recovery.py:217-245` (`checkpoint()`), and the
  rollback flow that depends on it is `Program.confirm_rollback`
  (open.py:1814ff): freeze target first, then a safety checkpoint
  whose retention is passed the frozen target as `keep_extra`
  (open.py:1843ff, *"Safety checkpoint (retention preserves the
  frozen target)"*).
- **The design intent (engaged per the brief, from the module
  itself):** Checkpoint Generation V1 (DCC-XVIII, module header) is a
  **cross-file coherence** protocol — immutable generation members +
  an atomic CURRENT pointer — whose recovery contract is pair
  convergence: the pointer names exactly `generation_id` +
  `previous_generation_id`, and loading must prove a complete old
  pair or target pair (the C-A context: this sealed path is the one
  that passed every crash test, under the LOAD-TIME CONVERGENCE
  acceptance contract). The protocol's data model has no slot for a
  third generation. Retention's own docstring names the shape:
  *"Conservative retention: keep current + previous committed
  generations"* (:289-295), with `keep_extra` as the designed escape
  for the one case needing more — R6.3's frozen rollback target.
  No ruling promises multi-generation checkpoint history; the census
  records the setter as unknown, and no plan text found promises
  restore points beyond previous.
- **Probe (functional, `commit_checkpoint` on throwaway owners,
  56b6d9c):** three plain commits (g1, g2, g3) → after g3, **g1's 4
  member files and manifest are deleted**; g2 and g3 stand complete;
  the g3 commit receipt's retention entry reads `{"kept": [g2, g3],
  "removed": 5}` — the deletion is counted and the kept set named on
  the protocol's own receipt. `freeze_rollback_target(owner, g1)`
  then fails (`RollbackTargetError`: manifest unreadable — the files
  are gone); `freeze_rollback_target(owner, g2)` succeeds. Rollback
  reach is exactly current + previous. Committing g3 with
  `keep_extra={g1}` on a second owner → **g1 fully preserved** (4
  members + manifest, retention `removed: 0`). With the CURRENT
  pointer corrupted, `_retain_current_and_previous` deletes nothing
  and reports `{"kept": [], "removed": 0, "note": "pointer
  unreadable; nothing deleted"}` — the fail-safe holds first-hand.
- **DISPOSITION: FAITHFUL-GUARD — the census's HINDERS-US does not
  survive the design-intent check.** Separate the two findings as the
  method requires. (a) *Value:* rollback reach of two generations is
  a real capability limit — a restore point three commits old is
  unrecoverable through this protocol. (b) *Mechanism vs ruling:*
  the mechanism implements its documented design exactly — the
  retention is named and deliberate in its own docstring, every
  commit receipt at the protocol API discloses the kept set and the
  removal count, the delete path fails safe on an unreadable
  pointer, and the frozen-target escape exists and is used by the
  one production flow that needs an older generation to survive
  (confirm_rollback freezes before it checkpoints). Nothing here is
  silent at the mechanism's own surface, and no ruling is disobeyed,
  because no ruling promises more. One visibility gap is recorded
  honestly: the production wrapper `core_i_recovery.checkpoint()`
  returns only the generation id (core_i_recovery.py:243-245),
  dropping the receipt's retention detail — so the removal count
  reaches direct `commit_checkpoint` callers but not the production
  caller's return value. That is a receipt-forwarding gap in the
  wrapper, not silent loss in the retention mechanism. **What would
  change this classification:** a ruling or user surface promising
  checkpoint history beyond previous; a consumer whose contract
  needs generation N−2 (the C-A convergence contract needs exactly
  the old pair vs the target pair); or evidence that frozen targets
  are being reaped despite `keep_extra`. No repair sketch is offered
  — under the evidence, multi-generation retention would be a new
  feature decision for Ace/Director (with `keep_extra` already the
  mechanism to build it on), not a defect repair.

## R31 — Coordinator audit evicts at 500 with no dropped counter

- **Census sites:** agent_coordinator.py:113/:606.
- **Sites today:** `_MAX_AUDIT_RECORDS = 500` at
  `form/dell_matrix/agent_coordinator.py:113`; the eviction loop at
  `:606-608` inside `capture_agent_action` (:547) —
  `while len(records) > _MAX_AUDIT_RECORDS: oldest = min(records.values(),
  key=lambda r: r["audit_seq"]); del records[oldest["audit_id"]]`. A
  grep for `dropped` across the whole module returns **nothing** — no
  counter, no marker, no receipt field. The records are durable:
  `form/persist.py:519-529` serializes `agent_audit_records` into the
  program payload and `persist_rest.py:905ff` restores them, so the
  evicted set is exactly what vanishes from the persisted record.
  Distinguish the sibling bound in the same module: `_MAX_RECEIPTS`
  (500, :109) caps an in-memory idempotency cache whose eviction
  loses only a duplicate-suppression receipt (census: GUARDS-US) —
  the audit store is canonical evidence, and it is the audit store
  that evicts uncounted.
- **The ruling:** no ruling names the value 500 — **UNRULED**. The
  binding family convention is the PP2b/AF-4 counted-eviction repair,
  applied to every sibling writer and verified across waves 2–3:
  exchange bumps `exchange_receipts_dropped_total` /
  `exchange_seeds_dropped_total` at the loss site (exchange.py:99,
  :924, :1086), design_loop keeps `design_loop_dropped_total`
  (design_loop.py:149-153), auto_growth's ledger carries
  `dropped_total` (auto_growth.py:44-85), dock_session and
  director_records count likewise (wave 3, R12: eviction counted,
  *"the loss is counted, never silent"*). The coordinator audit is
  the family's only uncounted eviction — the census's charge, and it
  still stands.
- **Probe (functional, `capture_agent_action` on a real program,
  56b6d9c):** 505 captures, all returning records → **500 retained,
  seq 6–505**: seqs 1–5 are gone. No program attribute contains
  "dropped"; no record field contains "dropped". Serializing the
  program (`form.persist.serialize`) yields an `agent_audit` section
  with exactly the 500 survivors — the five evicted records are
  absent from what persists, and nothing anywhere records that they
  existed. One mitigation is real and recorded: `audit_seq` is
  monotonic, so a gap at the head of the sequence is *detectable*
  after the fact by a reader who thinks to look — but nothing counts
  it, names it, or surfaces it at the eviction site or in
  `list_agent_audit` (:615).
- **DISPOSITION: DEFECT-CONFIRMED (the silence, not the value).**
  The audit trail is evidence on the sovereignty confirm path — the
  one record family whose entire purpose is accounting for agent
  actions — and its oldest records are destroyed at 500 with less
  accounting than any sibling store in the program gives its own
  evictions. Every comparable writer in the family counts its drops
  at the loss site under a repaired convention; this one does not
  count, and because the store persists, the loss is durable across
  sessions, not a session-cache effect.
  *Failing-first sketch:* capture 505 audit records and assert a
  dropped-eviction count of 5 is recorded on the program (and
  survives serialize/load) — fails today at
  `agent_coordinator.py:606` (500 retained, count nowhere). Repair
  shape: apply the family's own pattern at the loss site — bump a
  persisted `agent_audit_dropped_total` inside the eviction loop
  (the `_bump_dropped` shape, exchange.py:99), carried through
  `persist.py`'s `agent_audit` section beside `audit_seq`; whether
  the 500 cap itself should also grow is a separate value question
  this wave does not need to reach.

---

## Wave summary

| Item | Site today (main 56b6d9c) | Disposition | One-line basis |
|---|---|---|---|
| R27 — REPL door clamps | repl.py:2191 (ledger 200), :2294 (history 48), :2357 (ce develop 20), :2397 + open.py:964 (evolve loop 150), repl.py:4596 (connection grow 5, code-read) | **DEFECT-CONFIRMED** (history clamp LATENT) | Door probes: `ce develop 25` announces ×20 and `evolve loop 200` receipts ×150 — the clamped count presented as the answer, DD-44 EXTENDED's named silence; `ledger 500` shows 200 of 250 stored with honest totals but no paging; `history`'s 48 clamp is unreachable headroom over R5's 24 storage cap; values UNRULED, no test pins |
| R28 — Forces/grow side-effect slices | open.py:890 ([:8]), :903 ([:3]), :1322 ([:12]), :1330 ([:3]) | **DEFECT-CONFIRMED** | Probe on a 16-unit plane: force_growth plants 8, force_water flows 3, grow_ideas plants 12 / flows 3; no receipt names or counts the skipped set — and the insertion-order prefix plus cumulative planting make the exclusion permanent, not per-run; main growth engine uncapped; UNRULED |
| R29 — Idea-create field caps | idea_create.py:44-47 (return cuts), :33 (words derivation), :41 (strength); consumer needs.py:27-46 | **DEFECT-CONFIRMED** (narrowed) | Probe: label 100→80, detail 2500→2000, goals 15→12, placed + persisted via parse_and_place, receipt silent; census's strength sub-claim REFUTED (scored on full detail at :41; saturating formula :64-69 insensitive regardless) and its words-500 site is dead (operative bound is :33's 120 preview) |
| R30 — Checkpoint retention current+previous | checkpoint_generation.py:288-331, receipt :395; wrapper core_i_recovery.py:217-245 | **FAITHFUL-GUARD** | Probe: 3 commits reap g1 (receipt: kept [g2,g3], removed 5); freeze(g1) fails, freeze(g2) OK; keep_extra preserves g1 fully (removed 0); unreadable pointer deletes nothing. The shape is the DCC-XVIII protocol's documented conservative design (pointer names current+previous only; C-A convergence needs exactly that pair); one wrapper gap: core_i_recovery.checkpoint returns only the gen id, dropping the retention detail |
| R31 — Coordinator audit eviction 500 | agent_coordinator.py:113, eviction :606-608 in capture_agent_action (:547); persisted via persist.py:519-529 | **DEFECT-CONFIRMED** | Probe: 505 captures → 500 retained (seq 6–505), no "dropped" anywhere in the module, serialized payload carries only the survivors — the family's only uncounted eviction (exchange/design_loop/auto_growth/dock_session/director_records all count at the loss site, PP2b/AF-4 pattern); the value 500 is UNRULED and is not the finding |

**Queued for wave 7 (next five in register order):**
R32 — Graph vision caps: 480 edges (live visual), 400 edges (Studio)
(live_visual.py:192/:194; assets/js/core.js:288 at census) ·
R33 — Growth fog gate bars labels >72 chars (ringed_growth.py:45-46,
:373 at census) ·
R34 — Bimo configurations cap 10 retires committed configurations
(bimo_forge.py:51; retention :261/:274 at census) ·
R35 — scrub_context silently cuts every context scalar to 2,000
(inference_dock.py:341-342 at census) ·
R36 — Context nodes cap 1,000 refuses field-scale contexts whole
(inference_dock.py:351, :385-387 at census).
*Wave-7 note:* R35/R36 are the dock's context-intake pair and should be
verified together — the same context is first cut per-scalar (R35) and
then counted for refusal (R36), so the probe should carry one
field-scale context through `validate_context`/`scrub_context` and
observe both mechanisms on the same input. R32 spans two surfaces
(Python payload and Studio JS) — the payload's coverage honesty, not
just the edge counts, is the claim to test, per the census's contrast
with `snapshot_for`'s coverage reporting. R34's configurations are
user-authored committed state (the R30 lesson applies in reverse:
check for a design intent and a receipt before reaching for the
doctrine — but note the census found retention *silent* there, which
R30's was not).
