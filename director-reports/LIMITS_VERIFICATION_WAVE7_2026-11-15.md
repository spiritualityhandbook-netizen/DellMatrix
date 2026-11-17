# LIMITS VERIFICATION — WAVE 7 (2026-11-15)

Read-only verification of register items **R32–R36** from the Limits Census
(`hidden_files/limits_census/CENSUS.md`, inventoried at main `a9e8b561`), queued by
Wave 6 (`LIMITS_VERIFICATION_WAVE6_2026-11-15.md`), re-verified first-hand at
**current main `56b6d9cb40cb68d3f50e4c39537769b242cb13a7`** (the same head Wave 6
verified; g31proof_clone fetched, checked out at that head, verified clean
before and after — probes ran in-memory on throwaway owners `W7*` through the
production APIs, no state files persisted, nothing committed). Functional
probes ran for every item; the one exception is R32's Studio half, which is
code-read (no JS runtime probe) and labeled as such.

**Numbering:** R32–R36 are taken exactly as Wave 6's queue named them,
matching the census's ranked HINDERS-US register (R32 graph vision caps ·
R33 growth fog gate 72 · R34 Bimo configurations cap 10 · R35 scrub_context
2,000 · R36 context nodes cap 1,000). R35/R36 were verified together, per
Wave 6's note — and the pairing itself produced a finding: the two
mechanisms are alternatives, not a pipeline (see R35). Line numbers are
today's throughout.

**Method (wave-4 ruled-semantics separation, binding):** every item separates
**(a) the value hinders** (a realistic workload needs more), **(b) the
mechanism disobeys its ruling / loses silently** (DEFECT), and **(c)
FAITHFUL-GUARD** (the bound implements its ruling, refusal visible, nothing
silent — a small value alone is not a defect). Rulings are cited from the
working plan (`director-reports/ACE_FUTURE_DEVELOPMENT_PLAN.md`) and
test-pinned contracts; where no ruling exists, the item says UNRULED plainly.
Where a census claim fails first-hand, this report says so and withdraws it,
per the Wave 6 standard (its R29 strength sub-claim).

**Headline of the wave:** the census is wrong twice in this stretch, and
both errors are the same shape — it charged silence where the code either
discloses (R32's payload) or never runs (R35's `scrub_context` has no
caller). R32 narrows to one genuinely silent slice, in the Studio's draw
call, *below* the payload's own disclosed cap. R33's headline scenario
likewise does not reproduce: the 72-char fog ceiling is unreachable at both
production call sites because both label constructors cap below it. The
wave's real defects are R34 (committed user state retired silently at
*three* sites, one of them at commit time in the REPL handler, which the
census did not name) and R36 (an honest refusal whose node budget is
internally inconsistent with its own char budget by ~5× at field scale).

---

## R32 — Graph vision caps: 480 edges (live visual), 400 edges (Studio)

- **Census sites:** live_visual.py:192/:194 (`raw_edges[:480]`, "no
  truncation flag in the payload"), assets/js/core.js:288
  (`edges.slice(0, 400)` at draw, silent).
- **Sites today:** identical lines. `_EDGE_CAP = 480` at
  `form/dell_matrix/live_visual.py:192`, slice at `:194`, under the site's
  own comment (:190-191): *"Live UI only needs a sample of edges (full
  plane can be 20k+ and stalls the browser). Cap keeps lattice page
  responsive without dropping graph capability elsewhere."* The payload
  dict carries `"edges"` **plus `"edges_total": len(raw_edges)` and
  `"edges_shown": len(edges)`** at `live_visual.py:265-267`. Studio draw:
  `edges.slice(0, 400)` at `form/dell_matrix/assets/js/core.js:288`, inside
  `drawLatticeMap` (:212).
- **The census's coverage claim does not reproduce — for the payload.**
  `edges_total`/`edges_shown` exist at the census's own pin (`a9e8b561`
  carries them at :266-267), so the "no truncation flag in the payload"
  charge was already inaccurate when inventoried. Two front-end pages
  display the coverage: `assets/fp_world.html:1021` renders
  `` `${edges_shown}/${edges_total} edges` ``, and
  `assets/pages/lattice.html:152` prints `edges ${shown}/${total}` in its
  lede. The comment's second claim also verifies: `build_view`
  (graph_view.py:111) is itself uncapped, and the graph machinery reads
  the plane directly — the cap binds only this payload's sample.
- **Probe (functional, `open_program` + `place_idea` + `_state_payload`,
  56b6d9c):** 25 placed units (+ the pre-existing welcome unit = 26) →
  **692 raw edges** (enhance_scope is all-pairs for unboxed units) →
  payload `edges` = **480**, `edges_total` = **692**, `edges_shown` =
  **480**. The cap binds; both numbers are disclosed in the payload
  itself.
- **The Studio half is the real, narrower defect (code-read).**
  `lattice.html:169-172` feeds `STATE.edges` — the payload's already-capped
  array — to `DM.drawLatticeMap`, which slices it *again* to 400 at draw
  (core.js:288). No surface discloses this second cut: the same page's
  lede (lattice.html:152) prints the payload's `edges_shown` (up to 480)
  as the shown count, so whenever the total exceeds 400 the displayed
  coverage **overstates the drawn coverage by up to 80 edges**. The
  payload made the performance decision honestly; the draw then makes a
  second, silent one underneath it.
- **The ruling:** no ruling names 480 or 400 — **UNRULED**; no test pins
  either value.
- **DISPOSITION: RECLASSIFIED-GUARD (live-visual payload) +
  DEFECT-CONFIRMED (Studio draw slice, narrowed).** Separating the
  halves as the method requires. (a) *Payload:* the cap is a documented
  performance sample whose coverage is receipted in the payload and
  displayed on two pages — the honest pattern the census itself praised
  in `snapshot_for` (R3); the census's silence charge is **withdrawn**.
  The value still caps a human-facing drawing at 480 of N with no paging
  past the sample in this payload, but the full graph remains available
  to every other consumer, and the operator is told the fraction — that
  is a disclosed window, not a silent loss. (b) *Studio draw:* the 400
  slice is silent, redundant with the payload's disclosed cap, and makes
  the page's own coverage line inaccurate — a small, precise defect.
  *Failing-first sketch:* serve a payload with 450 edges
  (`edges_shown` 450) to `drawLatticeMap` and assert the drawn edge
  count equals `edges_shown`, or that a draw-level cap is disclosed
  alongside it — fails today at `core.js:288` (400 drawn, 450 claimed).
  Repair shape: draw what the payload sent (the payload already made
  the performance decision), or thread the true drawn count into the
  lede so the coverage line describes the canvas, not the payload.

## R33 — Growth fog gate bars labels >72 chars

- **Census sites:** ringed_growth.py:45-46, :373 (`_aetheris_clear`:
  label <3 or >72 → proposal skipped, counted only in the aggregate
  `fog_cut`).
- **Sites today:** `FOG_MIN_LABEL_LEN = 3` / `FOG_MAX_LABEL_LEN = 72` /
  `FOG_BANNED_FRAGMENTS` at `form/dell_matrix/ringed_growth.py:45-47`;
  `_aetheris_clear` at `:371-382`. Its production call sites are exactly
  three, all inside `RingedGrowth.run`: `:547` (body-pulse restore
  labels, `f"Restore {organ}"` — short by construction), `:681-682`
  (the Solstice path, gating `_combine_label(ua.label, ub.label)`),
  and `:712-713` (the Equinox/Standstill path, gating
  `_evolve_label(...)`). A whole-tree grep finds **no other caller**.
  The run receipt carries the aggregate `"fog_cut"` at `:773`.
- **The mechanism the census line flattens:** the gate never sees a
  parent label. It sees the *composed child label*, and both
  constructors cap below the ceiling: `_combine_label` (:395-399)
  truncates each parent to 22 chars, so a child is at most
  22 + 3 + 22 = **47 chars** (or ≤33 on the "(deepened)" path);
  `_evolve_label` (:402-404) hard-caps its output at `[:70]`. The >72
  arm of `_aetheris_clear` is therefore **unreachable headroom** at
  every call site that exists — the same shape as R27's `history`
  clamp (48 over a 24 cap), not an operative bar.
- **Probe (functional, 56b6d9c):** `_combine_label` on two ~100-char
  parents returns a 33-char child; `_evolve_label` on a 100-char label
  returns exactly 70; `_aetheris_clear("d"×73, …)` is False (the gate
  function *would* bar 73 chars if one reached it) while both composed
  labels pass. Run-level, via `give(clean=True)` + `RingedGrowth.run`:
  two units with 97/101-char labels and shared tokens **grew**
  (proposed_new = 1, fog_cut = 0; the child proposal
  "alpha beta gamma delta (deepened)" landed in the Nursery). A second
  run whose parents' labels contain a banned fragment ("null
  hypothesis…" / "null result…") produced proposed_new = 0,
  **fog_cut = 1** — the fragment arm trips, and the receipt's only fog
  key is the aggregate `fog_cut`; no pair is named.
- **The ruling:** none names 72 or the fog gate — **UNRULED** (the
  plan's two "fog" hits are unrelated senses of the word). No test
  pins the gate. The gate's in-code character is an anti-garbage
  quality filter (banned fragments `asdf`/`test123`/`null`/
  `undefined`, punctuation floods, tokenless labels), not a capacity
  bound.
- **DISPOSITION: RECLASSIFIED-GUARD — the census's HINDERS scenario is
  REFUTED as stated.** (a) *Value:* no legitimate workload is barred
  by the 72 ceiling, because no production path can present a label
  longer than 70 to the gate; long-labeled ideas grow (probe, above).
  The census's claim "any idea whose combined label exceeds 72 chars
  can never be grown from" does not survive contact with
  `_combine_label`'s 22-char parent truncation, and is withdrawn.
  (b) *What survives of the census line:* its secondary observation —
  fog-skipped pairs are counted only in the aggregate `fog_cut`, never
  named — is accurate for the arms that *can* trip (banned fragments,
  punctuation, tokenless). But those arms are the gate working as
  designed (a composed child label containing "null" or "test123" is
  exactly what a fog filter exists to stop), and the count *is*
  disclosed on the run receipt; the skipped objects are proposals
  never created, not stored state. That is a receipt-granularity
  note, not a hindrance and not silent loss. No repair sketch is
  owed; if Ace ever wants per-pair fog attribution, it is a small
  receipt addition, not a defect repair.

## R34 — Bimo configurations cap 10 retires committed configurations

- **Census sites:** bimo_forge.py:51; retention :261/:274 (newest 10
  kept).
- **Sites today:** `_MAX_CONFIGURATIONS = 10` at
  `form/dell_matrix/bimo_forge.py:51`, applied through the shared
  strict-schema kit's `retention_order`
  (`form/dell_matrix/session_section.py:180-186` — newest `max_keep`
  by sort field, the rest simply absent from the returned dict) at
  load (`validate_configurations_section`, :254-265, max_keep at
  :261) and at save (`serialize_configurations_section`, :267-280,
  max_keep at :274). **Plus a third site the census did not name —
  the sharpest one:** the commit handler itself,
  `form/repl.py:4168-4173` in `_commit_forge_config`, trims the
  merged store to a literal `[:10]` *before* the canonical save, so
  the 11th commit retires the oldest configuration in memory, not
  merely at the next serialization.
- **The receipts, all three surfaces:** the commit's success message
  (repl.py:4199) says only *"Committed 'name': … stored as a named
  configuration"*; the session record says `"configuration committed:
  {name}"`; the serialized section carries `{version, configurations}`
  and nothing else. A retired **valid** record is not preserved in
  the section's `malformed` area (only *invalid* records are), and no
  counter exists anywhere. Downstream, the loss surfaces only as a
  refusal: `dock()` rejects the retired name with *"unknown bimo
  configuration '…': not committed in the Forge"*
  (inference_dock.py:2044-2054).
- **Probe (functional, `make_configuration` +
  `serialize_configurations_section` / `validate_configurations_section`,
  56b6d9c):** 12 valid configurations with increasing `saved` →
  serialize keeps the newest **10** (c02–c11); c00 and c01 are absent
  from the section, absent from `malformed`, and no "dropped" string
  appears anywhere in the serialized output. Validating a persisted
  12-record section likewise returns 10.
- **The design intent (engaged per Wave 6's note — the R30 check):**
  boundedness *is* a declared property of the kit — the module
  header (bimo_forge.py:19-22) describes the sections as "bounded,
  owner-bound, malformed evidence preserved" — and the cap is
  **test-pinned**: `form/mandell/r75_forge_test.py:392-396` pins
  "configurations capped at 10" and "most recent configurations
  kept" as R7.5 build contract. But the R30 parallels end there:
  checkpoint retention receipts its removals on every commit and
  carries a designed escape (`keep_extra`); this eviction has **no
  receipt at any surface and no escape**, and what it retires is not
  session evidence but **user-authored committed state** — named
  arrangements Ace deliberately saved, which the dock can later be
  asked to wear by name. No Ace/Director ruling names the value 10;
  the pin is the build's own contract, so re-pinning the value is a
  ruling act (the R25 pattern).
- **DISPOSITION: DEFECT-CONFIRMED (the silence — mechanism faithful
  to its pin).** Three enforcement sites retire the oldest committed
  configuration with zero accounting: no commit-receipt note, no
  counter, no malformed preservation — below the standard every
  sibling store in this family meets (R30's receipted retention,
  R31's counted-eviction family pattern). The defect is the missing
  accounting, and naming it needs no ruling; whether committed
  configurations should be capped *at all* is the separate value
  question the pin currently answers at 10, flagged for Ace/Director
  rather than re-decided here.
  *Failing-first sketch:* commit an 11th configuration through
  `_commit_forge_config` (or serialize 11 valid configurations) and
  assert the retired name is recorded somewhere durable — a counter,
  a preserved retired entry, or a commit receipt naming it — fails
  today at `repl.py:4168` and `bimo_forge.py:274` (10 kept, record
  nowhere). Repair shape: at minimum the family pattern — name the
  retirement on the commit receipt and preserve retired records in
  the section (a `retired` area beside `malformed`); the fuller
  doctrine fix (retain all named configurations; refuse an 11th
  commit loudly if a bound is ever re-ruled) rides on the pin's
  re-ruling, not on this wave.

## R35 — scrub_context silently cuts every context scalar to 2,000

- **Census sites:** inference_dock.py:341-342.
- **Sites today:** `scrub_context` is defined at
  `form/dell_matrix/inference_dock.py:332-350`; the cuts are
  `s[:2000]` at `:349` and `str(obj)[:2000]` at `:350` (census lines
  drifted +8). Its docstring: *"Recursively drop sensitive key names
  from host context… Non-JSON-scalar leaves are stringified with a
  length cap."*
- **The census claim does not reproduce: the function has no
  caller.** A whole-tree grep finds `scrub_context` referenced only
  at its definition and its own two recursive calls (:343/:346) —
  no production path, no test, no dynamic dispatch. The dock's live
  context path is the *other* function: `validate_context`
  (inference_dock.py:363), called by `propose()` at `:1127`, which
  performs its own sensitive-key dropping inside its walk and
  **preserves scalars whole, types intact**. Wave 6's queue note —
  "the same context is first cut per-scalar (R35) and then counted
  for refusal (R36)" — is therefore also refuted: the two functions
  are alternatives, and only one is wired.
- **Probe (functional, 56b6d9c):** `scrub_context({"note": "x"×5000,
  "n": 42, "ok": True})` → the scalar comes back at **2,000** chars,
  and `42` → `"42"`, `True` → `"True"` (the dormant code cuts *and*
  stringifies). `validate_context` on the same inputs → the
  5,000-char scalar returns at **5,000**, `42` returns as the int
  `42`; both functions drop sensitive-named keys identically. The
  docked mind's actual vision of context is the second behavior.
- **The ruling:** none — the census records the setter as unknown;
  **UNRULED**, and no test pins `scrub_context`.
- **DISPOSITION: REFUTED AS A LIVE LIMIT — RECLASSIFIED (dormant
  code).** The HINDERS scenario ("the docked mind's vision of any
  long context string is cut before it reasons over it") occurs on
  no live path, and the charge is withdrawn. What remains is a
  latent hazard and a duplication note, recorded honestly: a
  dormant duplicate of `validate_context`'s scrubbing survives with
  *different* semantics (silent 2,000 cut + stringification of every
  scalar), so any future wiring of it would introduce exactly the
  defect the census described, invisibly. That is a code-health /
  completeness item (delete it, or wire it deliberately with a
  marker — a decision for a cleanup circuit), not a live limit, and
  no repair sketch is owed under this wave's method.

## R36 — Context nodes cap 1,000 refuses field-scale contexts whole

- **Census sites:** inference_dock.py:351, :385-387 (`bad_context:
  nodes exceed 1000`, no provider call).
- **Sites today:** `_MAX_CONTEXT_NODES = 1000` at
  `form/dell_matrix/inference_dock.py:359`, between its siblings
  `_MAX_CONTEXT_DEPTH = 10` (:358) and `_MAX_CONTEXT_CHARS = 100000`
  (:360); enforcement in `validate_context`'s `_budget` (:391-395,
  the raise at :394-395). `validate_context` (:363) is the live
  intake path — `propose()` calls it at `:1127`. Every visited value
  counts: 1 per container, 1 per dict key, 1 per scalar (docstring
  :371-372, deliberate under the AMEND).
- **Probe (functional, the census scenario carried through the live
  function, 56b6d9c):** a context of **200 field entries × 5 short
  scalar fields** = **2,401 counted nodes / 19,890 serialized chars**
  → `DockError: bad_context: nodes exceed 1000`, refused whole,
  before generation, no provider call. An 80-entry context of the
  same shape (961 nodes, 7,910 chars) is **accepted whole**. The
  node budget therefore binds at ~83 field entries of this shape
  while the char budget sits at ~20% used.
- **The ruling:** the AMEND 2026-10-07 header (:355-358) rules the
  *design* — "Bounded processing: depth, node count, and combined
  size are validated BEFORE generation… rejected with a stable
  receipt" — but no ruling names the value 1,000. The census's
  sibling classification stands and is consistent with the probe:
  depth 10 and chars 100,000 are GUARDS-US (the depth/cycle guards
  carry the actual runaway protection; the char ceiling is
  generous). The node budget is the inconsistent sibling: the
  100,000-char budget it shares a contract with implies tens of
  thousands of small nodes, so the two budgets disagree by ~5× on
  exactly the contexts docking over a real field produces.
- **DISPOSITION: CONFIRMED-HINDERS (the value; the mechanism is
  honest).** Separate as the method requires: (b) no defect — the
  refusal is explicit, stable, pre-generation, and disobeys no
  ruling; nothing is cut or lost silently (contrast R35's dormant
  function). (a) The value binds legitimate work at field scale,
  first-hand: a 200-entry field context at one-fifth of the char
  budget is refused entire, and the refusal is total — no partial
  context, no paging — so the dock cannot be given a whole real
  field as context at all.
  *Failing-first sketch:* `validate_context` over a 200-entry ×
  5-field field context (~19,890 chars) and assert acceptance (or a
  node budget consistent with the char budget) — fails today at
  `inference_dock.py:395` (`bad_context: nodes exceed 1000`).
  Repair shape (the census's): raise the node budget to a practical
  figure aligned with the char budget (or derive the node allowance
  from it), keeping the depth and cycle guards that carry the real
  runaway protection; the stable `bad_context` receipt shape is
  unchanged for genuinely excessive contexts.

---

## Wave summary

| Item | Site today (main 56b6d9c) | Disposition | One-line basis |
|---|---|---|---|
| R32 — Graph vision caps 480 / 400 | live_visual.py:192/:194 (cap + slice), :265-267 (payload totals); assets/js/core.js:288 (draw slice) | **RECLASSIFIED-GUARD** (payload) + **DEFECT-CONFIRMED** (Studio slice, narrowed) | Probe: 692 raw edges → payload 480 with `edges_total` 692 / `edges_shown` 480 disclosed and displayed on two pages — the census's "no truncation flag" claim is REFUTED (the fields exist at its own pin); but core.js draws only 400 of the payload's 480 while lattice.html's lede claims the payload's shown count — a second, silent cut that makes the coverage line overstate the canvas by up to 80 |
| R33 — Growth fog gate 72 | ringed_growth.py:45-47 (constants), :371 (gate), :395/:402 (label constructors), call sites :547/:681/:712, receipt :773 | **RECLASSIFIED-GUARD** (census scenario REFUTED) | The gate only ever sees composed child labels: `_combine_label` caps at 47 chars, `_evolve_label` at 70 — the >72 arm is unreachable; probe: ~100-char-labeled parents grew (fog_cut 0). The arms that can trip (banned fragments) skip pairs counted only in aggregate `fog_cut` (probe: "null…" pair, fog_cut 1, no pair named) — the gate working as designed, count disclosed; a granularity note, not a hindrance |
| R34 — Bimo configurations cap 10 | bimo_forge.py:51, :261/:274 via session_section.py:180-186; **repl.py:4168-4173** (commit-time, unnamed by census); dock refusal inference_dock.py:2044-2054 | **DEFECT-CONFIRMED** (silence; faithful to its pin) | Probe: 12 valid configurations → newest 10 kept at serialize and at load; retired records preserved nowhere, counted nowhere, named on no receipt — the 11th commit retires the oldest in the handler itself, and the dock later refuses its name as "unknown". Boundedness is the kit's declared design and the cap is test-pinned (r75_forge_test.py:392-396), but unlike R30 there is no receipt and no escape, and the retired state is user-authored |
| R35 — scrub_context scalar cut 2,000 | inference_dock.py:332 (def), :349/:350 (cuts) | **REFUTED as a live limit — RECLASSIFIED (dormant code)** | Whole-tree grep: `scrub_context` has no caller (definition + its own recursion only). The live path, `validate_context` (:363, called :1127), preserves scalars whole — probe: 5,000-char scalar returns 5,000 and int 42 stays int through validate_context, vs 2,000 and "42" through the dormant function. A latent hazard if ever wired, and a duplicate-scrubbing note — not a live limit |
| R36 — Context nodes cap 1,000 | inference_dock.py:359 (constant), :391-395 (enforcement in validate_context :363; called :1127) | **CONFIRMED-HINDERS** (value) | Probe: 200 entries × 5 fields = 2,401 nodes / 19,890 chars → `bad_context: nodes exceed 1000`, refused whole at ~20% of the char budget; 80 entries (961 nodes) accepted. The refusal is explicit and stable (no defect), but the node budget is inconsistent with its own 100,000-char sibling by ~5× for small-scalar contexts; value UNRULED (AMEND 2026-10-07 rules bounded processing, not the number) |

**Queued for wave 8 (next five in register order):**
R37 — Bimo framing cut to 1,200, silently
(inference_dock.py:970 at census) ·
R38 — Bridge result serialization cuts text to 8,000 for consumers
(llm/bridge.py:48 at census) ·
R39 — Claude output cap 2,048 tokens, hard-coded and unexposed
(llm/bridge.py:424 at census) ·
R40 — Research intake windows: far-wide search surfaces ≤24 ideas,
words cut to 400 (internet_gate.py:306-404 at census) ·
R41 — Harmonic lattice size silently snapped to {12, 14}
(harmonic_core.py:32-34, :52-58 at census).
R42 — nodes_payload shows 12 Nursery ghosts (open.py:550 at census)
is the register's final ranked item and follows wave 8.
*Wave-8 notes:* R37 belongs to R34's family — the framing is assembled
from the worn configuration R34 governs, so verify the pair against
each other (a configuration can now be *retired* silently and, per
R37's census line, *worn partially* silently). R38/R39 are the bridge
pair and should be verified together: one cuts a whole in-memory
result at serialization for every `to_dict()` consumer, the other is
the only provider bound not threaded through `dispatch()` — the
contrast between them is the claim. R41 is the doctrine's namesake
module: apply the R30 discipline — find what actually consumes
lattice size (geometry may genuinely require the snap) before
calling the snap a hindrance rather than a shape contract.
