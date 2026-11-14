# SANDBOX — THE FORCES OF NATURE, FULLY DEVELOPED & FITTED
## Ace's order 2026-11-13 21:22 CST: "The forces of nature like space, and
## gravity, etc need to all be fully developed and fit into where they
## belong in the Dellmatrix" — with synchronization against the whole
## future plan named of utmost importance for when the sandbox opens.
### SANDBOX DESIGN. No code touched; builds belong to future Director-gated circuits.

Evidence base: read-only codebase inventory, clone `nbd-omega-wake`
HEAD `05859c0` (2026-11-04): `form/dell_matrix/forces.py` (493 lines)
is the one home of all seven forces; `ForceField` rides the Program
(`form/open.py:266`); forces are the Matrix Body's CIRCULATION organ
(Dell 83, `matrix_body.py:31–32`); tick law in code: "body pulse
first · forces circulate · weather tracks organ health."

---

## §1 THE DEVELOPMENT CONSTITUTION (five laws every force must satisfy)

- **L1 PERSISTENCE SYMMETRY.** What save writes, load reads; what a
  force keeps, its save-scope NAMES. Write-only or never-read fields
  are defects by definition. (Standing violations found: Gravity's
  wells, Space's level — §3.)
- **L2 RESTORE PARITY.** A damaged forces section must behave like
  the sections beside it: fail closed or report — never silently
  substitute a fresh field. (Today: try/except-pass in
  `persist_rest.py:464–468` vs the spatial restore's fail-closed
  directly below.)
- **L3 NO ORPHANS (Completeness Law applied).** Every force is
  PARTICIPATING (a named consumer reads it) or STOOD DOWN WITH A
  RECEIPT. A force nobody reads is an orphan, however pretty.
- **L4 DERIVED BEATS STORED, WHERE HONEST.** If a force's state is a
  pure function of records (Gravity's wells of node scores; Growth's
  plants of live units — the REPL already rebuilds them), the
  developed form RECOMPUTES it on load under the lattice's
  rebuild-only rule instead of persisting a copy that can drift.
- **L5 ONE AUTHORITY.** ForceField stays the single home. The HCN
  reads the same forces AS the circulation organ; no second forces
  system, in the sandbox designs or anywhere else.

## §2 THE SEVEN, ONE BY ONE — today / the gap / the developed form / its home

### WATER — flow, merge, settle
- TODAY: idea → stream (volume 1.0); last two merge → river (volumes
  add, parents recorded); stream settles → pool. Intensity 0.7.
- GAP: stream/pool records are NOT saved (counts + levels only);
  merging is restricted to the LAST TWO streams (an accident of the
  list, not a meeting rule); pools are terminal (no re-flow); the
  tick feeds Water only the first 3 node labels.
- DEVELOPED: streams carry endpoints (from → to) and merge by
  MEETING (any two streams whose ideas the field brings together),
  with the river receipt naming parents + combined volume (the
  existing shape, generalized). Pools are a STATE, not a tomb: a
  settled stream can be re-flowed by an explicit act. Persistence:
  stream records join the canonical save OR the counts-only scope
  is kept and LABELED as the scope in every status surface — the
  circuit chooses; silence about the scope is the one unlawful
  option. (Project records certify Water within a save/bind scope;
  development must say the scope out loud, in the product.)
- HOME: circulation organ; consumers today = REPL evolve path,
  first-person skins, status. Tree reading: streams run along the
  nerve's edges; a pool is a settled, exclusive zone (a cap that
  came to rest).

### GROWTH — ideas as plants
- TODAY: plants with stages seed→sprout→stem→branch→leaf→fruit;
  grow_all ages/heightens by intensity; identity dedupe by unit.
  Save = plant COUNT only; the REPL evolve path rebuilds plants
  from live units.
- GAP: the rebuild is the de-facto persistence model but is nowhere
  declared as such; stage history is lost between sessions.
- DEVELOPED: declare plants a DERIVED projection (L4): rebuilt from
  live units + the growth ledger's stage receipts, so a plant's
  history is the ledger's, not a copy's. Stage transitions get
  receipts (they are the moments Profile/behavior maps will chart).
- HOME: circulation organ; the Nursery is its visible garden
  (proposals ranked/grown there); growth SELECT law governs its
  scope (never whole-field unless ALL is chosen).

### BREATH — the pacing force
- TODAY: inhale gathers / exhale releases counts; a heartbeat =
  one pair; phase + cycle are saved AND restored — the persistence
  EXEMPLAR of the seven (L1-compliant already).
- GAP: nothing consumes the phase; breath counts but does not pace.
- DEVELOPED: breath becomes the tick's PACING signal — the body
  pulse already runs first in tick(); the developed form lets
  force work declare which breath phase it belongs to (gather
  work on inhale, release work on exhale), receipted in the tick
  report. Candidate-grade: the circuit must show a consumer whose
  behavior differs by phase, or breath stays a counter, honestly.
- HOME: circulation organ + Cycle's metronome; Psalm Matrix live
  feed is its natural display (the field, breathing, is witnessable).

### GRAVITY — heavy ideas pull
- TODAY: top-3 scored nodes become wells, mass = score + 1.
- GAP: wells are WRITTEN to the save and NEVER restored (L1's
  clearest violation); top-3 is a hard cap (Elastic Limits: a
  field with 4 heavy ideas is lied about); wells move nothing —
  no consumer pulls anything toward them yet, though the Dell
  tour's living-Plane design (§12.22) already slates motion "by
  gravity."
- DEVELOPED: wells become DERIVED (L4): recomputed from current
  scores on load — the save field is removed or read, never both
  written and ignored. The cap becomes elastic (wells = every node
  past a stated mass threshold, receipted). The consumer is the
  living Plane: ideas drift toward wells in the motion modes,
  with the drift on receipts (placement law intact — gravity
  proposes motion, Ace's placement law disposes; auto-drift of
  Ace-placed ideas is OFF unless the mode is on).
- HOME: circulation organ + Plane dynamics; atlas subject (well
  births/deaths are behavior-map events).

### TIME — cycles move only forward
- TODAY: a tick counter; saved + restored; "cycles move only forward."
- GAP: the counter is global only — things do not carry their ages.
- DEVELOPED: per-thing AGE (the tour's ruling: time surfaces as
  AGE — felt, not counted): every unit/proposal/plant carries
  born-at tick + age derived from Time's counter. Time's product
  stops being a number nobody reads and becomes the age on every
  face. DuoBeta generations and checkpoint generations already
  count this way in their lanes; Time is their shared clock,
  named as such.
- HOME: everywhere ages show (Nursery cards age at 3/7/14 days and
  fade at 30 under Ace's ruling — that IS Time, working: the
  developed form wires proposal aging to Time explicitly).

### WEATHER — the readout wearing a force's coat
- TODAY: condition ∈ clear/rain/storm/fog, SET FROM BODY HEALTH in
  tick() (≥8 missing organs → fog, ≥4 → rain). Saved + restored.
- GAP: weather is not a force — it is a DASHBOARD. It acts on
  nothing; it reports the body's organ health. Keeping it in the
  forces list mislabels a witness as an actor (an orphan inverted:
  all consumers, no action).
- DEVELOPED: honest reclassification — Weather moves to the
  WITNESS side: it becomes the field-condition line of Schema's
  nervous-system health report (DD-29) and the Psalm Matrix live
  feed. If a future design gives weather a genuine INPUT of its
  own (field activity rates, error weather), it may re-earn a
  force's seat with the mechanism named; until then its seat is
  in the witness layer, and the forces list says six + weather
  reported beside them.
- HOME: Schema health surface + live feed; HCN WARD reads it
  (organ health IS WARD's watchlist, in weather's clothing).

### SPACE — "room to grow"
- TODAY: a description and nothing else — no methods, no state;
  its evolution_level is saved and never restored. The Completeness
  Law's standing exhibit among the forces.
- DEVELOPED (from Flower Part I): Space stops pretending to be a
  force and becomes the NEGATIVE-SPACE REPORT: for the live field,
  computed from real placements under Spatial Authority —
  COVERED / POCKETED / CHANNELED / OPEN, with the ρ-regime table
  as its calibration where a field model applies. A report has
  consumers by construction: Growth asks it "where is there room?"
  before growing (SELECT still governs WHAT grows; Space answers
  WHERE it fits); the Room layout reads it; WARD's borders cite it.
- HOME: witness layer beside Weather — the two non-forces leave
  the forces list together, each landing in a real job. The
  forces become FIVE actors (Water, Growth, Breath, Gravity,
  Time) + TWO witnesses (Weather, Space), and the count is honest.

## §3 THE STANDING DEFECTS THIS DEVELOPMENT CLOSES (at inventory HEAD)

1. Gravity wells written, never read (L1). 2. Space level written,
never read (L1). 3. Forces restore silently swallows damage while
the neighboring spatial restore fails closed (L2). 4. Water/Growth
contents counts-only — lawful ONLY once the scope is labeled in
the product (L1's naming half). 5. Resonance log hard-capped at 80
events with silent drop (Elastic Limits: becomes a stated,
receipted bound or a grown ring). All five are stated at clone
HEAD 05859c0 (2026-11-04); re-verify on current main in the
circuit that builds any of this (Q-M1 stands).

## §4 SYNCHRONIZATION MATRIX — the forces × the future plan

| Future-plan component | Synchronization |
|---|---|
| Matrix Body / HCN organs | Forces ARE the circulation organ (Dell 83) — one authority (L5); organ atlas names them; WARD = organ-health borders = Weather's data. |
| Nursery | Growth's garden + Time's aging (3/7/14/30-day law runs on Time); Water's pools = settled proposals' picture. Nursery gate unchanged: forces never confirm anything. |
| Plane (Room/Sky) | Gravity = living-mode motion (mode-gated, placement law intact); Space report = the Room's room-to-grow reading; Sky (2D) reads the same field flat. |
| Psalm Matrix | Live feed carries breath phase, weather line, force intensities — witnesses, all read-only for Psalms. |
| Atlas (§5B) | Force behavior maps: intensity/evolution/well-events over ticks; borders = the thresholds (mass line, organ counts 4/8). |
| Smith tab (§5A) | Flow-side candidates live in force country: a stream MEETING a pool is the kind of event pass-rates are counted over. No shared machinery; shared receipts only. |
| The Tree / chord | Streams along nerve edges; wells at high-multiplicity centres (PATTERN); chord addresses = the field's addresses, KeyLedger-permanent (Existence truth). Notes stay senses. |
| Completeness census (X11) | Each force classified PARTICIPATING or STOOD-DOWN-WITH-RECEIPT at sandbox opening; Weather/Space reclassifications recorded as decisions, not drift. |
| Persistence (checkpoint path) | Forces' durability claims ride ONLY the canonical save/bind + checkpoint lanes; the sealed generation is the forces' history too. |

## §5 THE OPENING CONDITION (Ace's "when the sandbox is opened")

Nothing in this study is built by being written here. The sandbox
opens through the standing gates (Dell Plan complete → HCN build →
Dock → surfaces, Afterplan §6). What this study guarantees is that
when the forces' circuits arrive, their development contracts,
their homes, and their synchronization partners are already
named — so the forces land FITTED, not adjacent. Open questions:
Q-Frc1: Water persistence — records-in-save vs labeled counts-only
(circuit's call, with the label mandatory either way). Q-Frc2:
Breath's phase consumer — name one or breath stays a counter.
Q-Frc3: Weather's re-seat — Ace/Director confirmation of the
witness-layer move. Q-Frc4: Space report's first consumer —
Growth's room-check is the standing candidate (F1/F2 falsifiers
from Flower Part I apply).
