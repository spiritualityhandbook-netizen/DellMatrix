# VISION SURFACE PLAN — V-01..V-13, THE H TRACK, #176 (2026-11-20)

**Part IV plan-stage deliverable** (branch `uni/part-4-far-stratum`,
base main `af2519b6d239ef278397e277210d6da2467c36e5`). Full-depth
design packages for register rows #99–#111 (V-01..V-13), the Human
Surface track #171 (consolidated, cross-filed with the V rows it
shares), and the parked wave-field instrument #176.

**Register posture (verbatim-grade):** every V row is DEFERRED in the
register — in the plan, not authorized to build. Ace opened the
stratum 2026-11-14; by the Unified Edition's law the stratum begins
only after the Grand Synchronization (Part VII) closes.

**SPLIT (applies to every section below):** DESIGNS proceed now, at
full depth, in this plan. BUILDS wait on Part VII + Ace's unparking
act per row + each row's own certification. Nothing below proposes
building anything in this PR.

## 0. Shared surface architecture (binds all V rows)

One rule keeps thirteen vision rows from becoming thirteen products:

1. **One canonical data model.** Cards, shapes, SKY, ROOM, and the
   page set are VIEWS over the existing canonical stores (Nursery
   store, Plane, Dell registry) — never new stores. A perspective
   that keeps its own copy of the data is a second authority and is
   refused at design review.
2. **Views are derived and rebuild-only (HS-1).** A view renders from
   records; it never writes to them except through the existing
   doors' operations (confirm / reject / modify run the same
   machinery whatever surface invoked them).
3. **View state is view state.** Positions (SKY/ROOM), shapes, and
   looks are presentation metadata kept in a view-state layer,
   labeled as such; losing view state loses arrangement, never
   ideas.
4. **Parity is testable.** SKY and ROOM show THE SAME canonical data
   (register, V-05/V-06); parity fixtures (§5/§6) are the proof
   shape, designed now.
5. **FAR-11 applies:** every map/perspective states its scale law on
   its face; rescaling carries the law with the view.

---

## §1 — V-01 · #99 — Nursery proposal CARDS

- **STATE:** Register: "Nursery proposal CARDS (visual, glanceable;
  confirm / reject / modify) — DEFERRED, not authorized." Today the
  Nursery is worked through text doors (SEE browse/search/get, the
  C5R.4 lens ranking) — no visual card surface exists.
- **DESIGN (full):**
  1. **Card (typed unit):** one proposal = one card. Face contents:
     the proposal's gloss (Mandell + English), its Dell composition
     in miniature, provenance chip (producer + generation), state
     chip (PENDING / eligible / selected per the STORED > ELIGIBLE >
     SELECTED pipeline — shown, never blended), age on Ace's fade
     ladder (the C5R.4 lens's freshness bands), and the three
     actions: **confirm / reject / modify**.
  2. **Action parity (the design's spine):** each card action invokes
     EXACTLY the existing door operation — confirm runs the Nursery
     confirmation path (Ace's sovereign act; the card is a surface,
     not a new confirmer), reject and modify likewise. A card action
     that behaves differently from its door twin is a defect by
     definition; parity fixtures (below) are the contract.
  3. **Glanceability rules:** one idea per card; no card carries a
     paragraph — depth lives one tap deeper (the card is the cover,
     not the book); the deck orders by the C5R.4 lens ranking
     (connection strength, freshness, novelty) unless Ace selects
     another lens — ranking is display order only, never admission.
  4. **Modify:** opens the proposal in the existing edit door with
     the card's context carried (see V-08 transitions); the card
     itself hosts no editor.
- **DEPENDS:** the Nursery store + doors (exist, Part II territory);
  the C5R.4 lens (exists). Feeds V-02 (shapes render on cards), V-03
  (suggested looks apply to cards), V-04 (cards are the primary
  screen's unit).
- **ACCEPTANCE:** card actions produce state transitions identical
  to the door operations on a fixture proposal set (parity), and a
  PENDING proposal is confirmable from its card by Ace and only Ace.
- **FAILING-FIRST:** `card_door_parity` — fixture proposals driven
  through both surfaces; at base no card surface exists (FAIL);
  build passes on transition-for-transition equality, including
  refusal cases (an ineligible proposal refuses identically).
- **SPLIT:** Design NOW. Build: B-VII + Ace unpark + own
  certification.

## §2 — V-02 · #100 — Custom idea shapes in the Nursery

- **STATE:** Register: "Custom idea shapes (circle, square/box,
  triangle, custom-drawn outline) — DEFERRED; depends V-01." No
  shape metadata exists.
- **DESIGN (full):** shapes are **view-layer metadata on ideas**,
  nothing more: (1) vocabulary — circle, square/box, triangle,
  custom-drawn outline (a closed path, stored as its point list);
  (2) storage — a shape assignment `(idea_id, shape, source)` in the
  view-state layer, where source ∈ {Ace-assigned, AI-proposed
  (only via V-03's proposals path), default}; (3) semantics — a
  shape MEANS whatever Ace's shape language says it means; the
  system assigns no semantics of its own and no mechanism may read
  shape as data (a shape is a look, not a classification — reading
  it as one would create a shadow taxonomy, refused here by
  design); (4) rendering — shapes render on cards (V-01) and in SKY
  (V-05) identically from the same assignment.
- **DEPENDS:** V-01 (the card surface shapes appear on).
- **ACCEPTANCE:** an Ace-assigned shape survives save/reload and
  renders identically on card and SKY views; removing view state
  removes shapes and nothing else.
- **FAILING-FIRST:** `shape_is_view_only` — fixture: assign shapes,
  delete the view-state layer, assert every idea and its state are
  untouched; at base no shape layer exists (FAIL by absence).
- **SPLIT:** Design NOW. Build: B-VII + Ace; after V-01's build.

## §3 — V-03 · #101 — AI-suggested looks

- **STATE:** Register: "AI-suggested looks (semantic icons + shape
  language) as Nursery proposals ONLY — DEFERRED; depends V-01."
  The register's fence is the design's spine: proposals ONLY.
- **DESIGN (full):** a suggestion pipeline with one exit: (1) a
  docked AI (or any producer) generates a look suggestion — semantic
  icon choice + shape assignment — FOR an idea; (2) the suggestion
  lands as a **Nursery proposal**, visibly marked as a look
  suggestion, carrying its rationale in plain English; (3) it takes
  effect only through the ordinary confirmation path — Ace confirms,
  or it does not happen; (4) no suggestion may touch anything but
  view-layer metadata (V-02's layer) — a suggestion addressed to
  content, state, or ranking is malformed and refuses at intake.
  Icon language: a small, named icon vocabulary mapped to Dell
  families, proposed as part of the build circuit's design
  confirmation (the vocabulary itself is a design artifact Ace sees
  before any suggestion is generated).
- **DEPENDS:** V-01; the Nursery proposal path (exists); FI-011
  gates for any docked-AI producer.
- **ACCEPTANCE:** a generated suggestion appears as a PENDING
  proposal and nowhere else; unconfirmed, the idea's rendering is
  unchanged; confirmed, only view metadata changed.
- **FAILING-FIRST:** `suggested_look_proposals_only` — drive a
  suggestion at base (no pipeline; FAIL); build passes when the
  suggestion is proposal-only and a content-addressed suggestion
  refuses at intake.
- **SPLIT:** Design NOW. Build: B-VII + Ace; after V-01/V-02 builds.

## §4 — V-04 · #102 — Nursery as THE primary decision screen

- **STATE:** Register: "Nursery as THE primary decision screen
  (painting/building feel, fun, organized, never an info dump) —
  DEFERRED." Today the REPL is the primary surface; the Nursery is a
  store behind doors.
- **DESIGN (full):** an information-architecture package, not a
  screen mock: (1) **decision-first layout law** — the screen's
  first visual rank belongs to what awaits Ace's decision (pending
  proposals as cards, V-01), then what changed, then everything
  else; a screen whose first rank is a report violates the law;
  (2) **never an info dump** — every element on the primary screen
  is either actionable or one tap from actionable; read-only
  reporting lives on its own pages (V-08 set); (3) **painting/
  building feel** — direct manipulation where the machinery allows
  it honestly (arrange cards, gather shapes), with every gesture
  resolving to a named door operation underneath (no gesture-only
  state); (4) **fun is a requirement, stated soberly** — the
  register's word; the design treats responsiveness, motion
  (V-06's anti-stagnation), and visible consequence (a confirm
  visibly lands) as the mechanisms of it, not decoration.
- **DEPENDS:** V-01 (its unit), V-08 (the page set it sits in).
  Acceptance is impossible without V-12's gates.
- **ACCEPTANCE:** only via #110 — a real AI docked live AND Ace
  personally working the Matrix on this screen; no lab acceptance
  substitutes (the register's own terms).
- **FAILING-FIRST:** `primary_screen_decision_first` — a layout
  fixture test asserting first-visual-rank = pending decisions; at
  base no such screen exists (FAIL). (The usability verdict itself
  belongs to V-12's gates, not to this test.)
- **SPLIT:** Design NOW. Build: B-VII + Ace; acceptance: V-12 only.

## §5 — V-05 · #103 — SKY perspective

- **STATE:** Register: "SKY perspective (2D; ideas as clouds/shapes;
  persistent positions; same canonical data as ROOM) — DEFERRED."
  No spatial perspective exists in the product.
- **DESIGN (full):** (1) SKY is a 2D view over the canonical store:
  ideas render as clouds/shapes (V-02's vocabulary) at positions;
  (2) **persistent positions** — an idea's place is view-state,
  saved with the view, restored on return; position means nothing
  to the machinery (arrangement is Ace's, semantics are not
  inferred from it — the same refusal as V-02's shape rule);
  (3) **canonical parity** — SKY and ROOM render the same records;
  a fixture field renders the identical idea set with identical
  states in both perspectives (the parity contract, §0.4); (4)
  scale law on the face (FAR-11): zoom levels declare their
  scaling; (5) the wave-field rendering option (#176) is filed as a
  display-only SKY skin under its own fences (§15) — not part of
  SKY's base design.
- **DEPENDS:** the canonical stores; V-02 for shapes. Feeds V-07
  (navigation moves within/between perspectives).
- **ACCEPTANCE:** the parity fixture (same field, both
  perspectives, identical sets + states) and position persistence
  across save/reload.
- **FAILING-FIRST:** `sky_room_parity` — at base neither perspective
  exists (FAIL); build passes on exact set/state equality and
  position round-trip.
- **SPLIT:** Design NOW. Build: B-VII + Ace.

## §6 — V-06 · #104 — ROOM perspective

- **STATE:** Register: "ROOM perspective (3D; walkable;
  stackable/openable boxes; never stagnant-looking) — DEFERRED."
- **DESIGN (full):** (1) ROOM is the 3D sibling of SKY over the same
  canonical data (parity contract §0.4): ideas as boxes in a room;
  (2) **walkable** — first-person movement through the room is
  navigation (V-07 supplies glide/zoom semantics); (3)
  **stackable/openable boxes** — stacking is arrangement (view
  state); opening a box shows the idea's contents through the
  existing doors (an open box is a view, not an extraction);
  (4) **never stagnant-looking** — the register's phrase, designed
  as: idle motion is ambient and meaningless-by-design (slow drift,
  light), clearly distinguished from state-signalling motion
  (change pulses on the affected box only) — ambient motion must
  never be mistakable for an event, or the room would cry wolf;
  (5) performance honesty — ROOM degrades to SKY (same data, 2D)
  rather than dropping ideas: a room that hides records to keep its
  frame rate violates no-silent-loss.
- **DEPENDS:** canonical stores; V-02. Feeds V-07.
- **ACCEPTANCE:** parity fixture (with SKY) + open-box equivalence
  (contents shown = door contents) + degradation test (oversized
  field → SKY fallback, zero records hidden).
- **FAILING-FIRST:** `room_open_box_equivalence` — at base no ROOM
  exists (FAIL); build passes on door-identical contents and the
  zero-hidden-records degradation.
- **SPLIT:** Design NOW. Build: B-VII + Ace.

## §7 — V-07 · #105 — Navigation: zoom + tap-to-glide; recursive exploration

- **STATE:** Register: "Navigation: zoom + tap-to-glide; recursive
  exploration of ideas within ideas — DEFERRED; depends G-01,
  V-05/V-06." G-01 (the growth/idea-containment machinery) is
  main-line; ideas-within-ideas exists as data (projects are ideas
  with ideas inside them) — navigation over it does not.
- **DESIGN (full):** (1) **zoom** — continuous scale movement within
  a perspective, scale law declared at every level (FAR-11);
  (2) **tap-to-glide** — selecting a distant idea moves the view to
  it along a visible path (the user sees the route, never a
  teleport-cut — orientation is a feature: you learn the territory
  by travelling it); (3) **recursive exploration** — entering an
  idea that contains ideas renders the contained field in the same
  perspective (a room inside the box, a sky within the cloud), with
  a breadcrumb of containment depth and a one-gesture return to
  each parent; depth is data (G-01's containment), the breadcrumb
  is view state; (4) **context preservation** — navigation never
  discards the working context: the current idea/selection rides
  every transition (V-08's transition law consumes this).
- **DEPENDS:** G-01 (main-line containment); V-05/V-06 (the spaces
  navigated).
- **ACCEPTANCE:** a nested fixture field (ideas within ideas, three
  depths) navigated end to end: glide paths visible, breadcrumbs
  exact, context intact at every level, zero data mutation from
  navigation alone.
- **FAILING-FIRST:** `navigation_never_mutates` — drive the full
  navigation suite over the fixture and diff the canonical store
  before/after; at base no navigation exists (FAIL); build passes
  on an empty diff + exact breadcrumbs.
- **SPLIT:** Design NOW. Build: B-VII + Ace; after V-05/V-06 builds.

## §8 — V-08 · #106 — The page set

- **STATE:** Register: "Page set: Plane, Nursery, Dells, Dell
  Playground, Psalm Matrix — transitions preserve current
  idea/context — DEFERRED; depends V-09."
- **DESIGN (full):** five pages, one context: (1) the pages —
  **Plane** (the field view), **Nursery** (the decision screen,
  V-04), **Dells** (the Dell registry/contracts surface), **Dell
  Playground** (a sandbox page where Dells can be exercised against
  scratch state — sandbox-first doctrine: nothing in the Playground
  touches canonical state except through the doors), **Psalm
  Matrix** (V-10); (2) **transition law** — moving between pages
  preserves the current idea and working context: the idea you were
  looking at is the idea you arrive with, on every page that can
  show it, and where a page cannot show it the context is parked
  visibly (a context chip), never silently dropped; (3) each page
  is a view in the §0 sense — derived, rebuild-only, acting only
  through the doors.
- **DEPENDS:** **V-09's research precedes any V-08 build** (register
  + map, hard order). The Playground depends on the sandbox
  machinery (exists).
- **ACCEPTANCE:** the transition matrix test — every ordered page
  pair × a fixture context: context preserved or visibly parked,
  never dropped; Playground isolation (canonical store diff =
  empty after a Playground session that used no door).
- **FAILING-FIRST:** `page_transition_context` — at base no page set
  exists (FAIL); build passes on the full matrix + isolation diff.
- **SPLIT:** Design NOW. Build: B-VII + Ace; **only after V-09's
  research has been executed and its placement recommendation
  accepted** (see §9).

## §9 — V-09 · #107 — Navigation placement RESEARCH (precedes V-08)

- **STATE:** Register: "Navigation placement RESEARCHED online
  before implementation — DEFERRED; precedes any V-08 build." No
  research has been executed. This section designs the research at
  full depth NOW; its execution is a design-lane activity of this
  Part (no product code, no authority gate beyond the research
  itself), and its report is the precondition for seeking V-08's
  build authorization.
- **DESIGN — the research protocol (full):**
  1. **Questions (fixed in advance):** (Q1) Where do mature spatial/
     knowledge tools place primary navigation (persistent rail,
     top bar, radial, in-canvas) and what does each placement cost
     in orientation and reachability? (Q2) How do tools with
     recursive containment (file managers, node editors, mind
     maps, game inventories) signal depth and return paths? (Q3)
     What placement patterns keep a *decision* surface (inbox-like)
     primary without burying the *exploration* surfaces? (Q4) What
     do accessibility standards require of spatial navigation
     (keyboard equivalence, reduced motion)?
  2. **Method:** primary sources first (vendor design systems,
     published UX research, the tools' own documentation), community
     experience second (forums/postmortems as leads, not facts);
     every claim carries source + date + evidence quality, per the
     project's research discipline; follow citation chains rather
     than repeating top-result searches.
  3. **Deliverable:** a research report in `director-reports/`
     answering Q1–Q4 with a **placement recommendation for the
     V-08 page set** — one recommended placement + the rejected
     alternatives with their costs — written so the Director can
     confirm or correct it as a design input.
  4. **Boundary:** the research recommends; it does not decide.
     Placement is confirmed in V-08's design confirmation, by the
     authorities, before build.
- **ACCEPTANCE (of the research):** the report exists, answers all
  four questions from cited sources, and its recommendation is
  dispositioned (confirmed / corrected) on the record.
- **FAILING-FIRST:** n/a as a test — the research's failure state is
  named instead: a V-08 build authorization sought WITHOUT this
  report on record is the defect; this protocol makes that state
  impossible to reach honestly.
- **SPLIT:** Protocol NOW (this section). Execution: this Part's
  design lane, before any V-08 build ask — it does NOT wait for
  Part VII (research is design work, and the map's dependency is
  V-09 → V-08 build, not V-09 → Part VII).

## §10 — V-10 · #108 — PSALM MATRIX: the AI page

- **STATE:** Register: "PSALM MATRIX: the AI page — Psalms +
  personas + status + docking visible there; no second authority —
  DEFERRED; depends SM-47 fact base." Its main-line ancestor is
  sequence step 4 (C-SEQ4: the Psalm Matrix surface — docked Psalms
  visible, conversational, witnessed). The page does not exist.
- **DESIGN (full):** (1) **contents** — docked Psalms (who is
  docked, in what mode, since when), personas (the roster from the
  persona registry — the repo's AGENTS.md registry is the roster's
  record), status (each Psalm's session state, receipts tail,
  proposals pending), docking (the dock's door: who may dock, under
  whose grant, revocable how — displayed from the dock machinery's
  own records); (2) **no second authority (hard)** — the page READS
  the dock/persona/session records; it grants nothing, confirms
  nothing, and hosts no controls that bypass the doors — any action
  taken from the page routes through the same machinery as anywhere
  else; (3) **witness posture** — the page is where Ace WATCHES the
  AIs work: live activity is shown as it is receipted (the dock's
  receipts are the feed; a prettified summary that disagrees with
  receipts is a defect); (4) FAR-20's second consumer lives here
  (the live feed gaining melodic movement) — filed as a cross-
  reference, built only under FAR-20's own gate; COMBO-9
  (bet-sized attention) is a PROJECTION-grade display candidate
  filed on this page's line — refinement belongs with the Nursery
  ranking work, carried here so it is not dropped.
- **DEPENDS:** SM-47 fact base (per register); the Dock (Part I,
  GP-E23) for live content; the persona registry (exists).
- **ACCEPTANCE:** page contents equal the underlying records
  (dock/session/persona fixtures rendered and diffed against
  source records — equality, not plausibility); zero page-originated
  authority acts in an action audit.
- **FAILING-FIRST:** `psalm_matrix_reads_only` — at base no page
  exists (FAIL); build passes on record-equality fixtures + an
  action audit showing every page action routed through a door.
- **SPLIT:** Design NOW. Build: B-VII + Ace; live content requires
  the Dock built (Part I).

## §11 — V-11 · #109 — The AI-talk place (an invention brief)

- **STATE:** Register: "AI-talk place: pure English, NOT a chat box
  — a new interaction concept to invent — DEFERRED." No concept
  exists; the register commissions an invention, so this section is
  a full invention brief — the honest maximum designable now.
- **DESIGN — the brief (full):**
  1. **Fixed constraints (from the register + Ace's doctrine):**
     pure English (no Mandell required of the human); NOT a chat
     box (no message-thread metaphor, no send button, no transcript
     as the primary object); the human talks WITH the program's AIs
     as participants in the Matrix, not as a support desk; every
     consequential act still routes through the doors and gates
     (talk is not a bypass); the conversation's products (proposals,
     drafts, decisions) land in the program's real places (Nursery,
     records), not in a chat log.
  2. **Candidate concept directions (to be developed, not chosen
     here):** (a) **the Table** — a shared surface where the human
     and docked AIs gather around the actual objects (ideas, cards,
     Dells) and talk is anchored to objects: you speak about THIS
     card, and the card is present; (b) **the Walk** — conversation
     while moving through SKY/ROOM: talk tied to place, the AIs
     meeting you where the work is; (c) **the Margins** — the human
     annotates the program's living surfaces in English, and AIs
     answer in the margins of the thing itself, the surfaces being
     the shared text. Each direction is developed in the invention
     study against the constraints + the evaluation criteria.
  3. **Evaluation criteria (fixed in advance):** Does it escape the
     chat-box metaphor in mechanism, not just in skin? Does talk
     stay anchored to program objects? Do products land in real
     places? Can Ace tell, at a glance, which AI said what and what
     it did (receipts, not vibes)? Does it degrade gracefully to
     plain text (the REPL remains the floor)?
  4. **Process:** the invention study produces ONE recommended
     concept with the losers' costs recorded; **concept selection is
     a Director/Ace act** — this brief does not select.
- **ACCEPTANCE:** of the brief — the study exists and a concept is
  selected on the record. Of any eventual build — V-12's gates.
- **FAILING-FIRST:** named failure state: a build that is a chat box
  with a new skin fails the brief by definition (criterion 1) — the
  brief exists so that verdict is mechanical, not taste.
- **SPLIT:** Brief NOW. Invention study: design-lane work under this
  Part; build: B-VII + Ace + selection act.

## §12 — V-12 · #110 — Human-validation gates

- **STATE:** Register: "Human-validation gates: (a) a real AI docked
  live AND (b) Ace personally working the Matrix, both required
  before any usability acceptance — register BLOCKED: awaits
  V-circuits + live dock + Ace's own session." The gates cannot be
  run yet — but their PROTOCOL is fully designable now, and is
  designed here so no V-build can claim acceptance by a weaker
  route invented later.
- **DESIGN — the gate protocol (full):**
  1. **Gate (a) — live dock:** a real AI (the FI-017 docked operator
     is the designated first candidate) docks live and works the
     built surfaces as a user: a scripted-but-genuine task list
     (find, propose, organize, draft) executed through the surfaces
     themselves, with the dock's receipts as the evidence — where
     the AI cannot complete a task through the surface, that is a
     gate finding, not an AI failure to be edited away.
  2. **Gate (b) — Ace's own session:** Ace personally works the
     Matrix on the built surfaces, his own tasks, his own pace; his
     verdict is the acceptance. No proxy, no summary-of-a-session:
     the gate is the man himself (NEEDS_OVERSEER by construction).
  3. **Both required:** usability acceptance for ANY V-surface
     requires (a) AND (b) on record, in that order (the dock finds
     the machine-visible defects first; Ace's session is spent on
     judgment, not on tripping over them).
  4. **Evidence format:** per surface — the task list, the receipts,
     the findings (each finding: surface, task, what happened, whose
     gate), and the disposition of each finding (fixed / accepted /
     deferred-by-Ace). The gate record lands in `director-reports/`
     as part of the accepting circuit's package.
- **DEPENDS:** the V-builds themselves; a live dock (Part I
  GP-E23 + FI-017's build).
- **ACCEPTANCE:** this protocol IS the acceptance machinery; a
  V-surface without both gate records is unaccepted by definition.
- **FAILING-FIRST:** named failure state: any usability-acceptance
  claim for a V-surface lacking either gate record — the protocol
  makes the claim self-refuting.
- **SPLIT:** Protocol NOW. Execution: after the V-builds, in their
  circuits; gate (b) is Ace's act whenever he chooses to run it.

## §13 — V-13 · #111 — Reserved neural research (charter only)

- **STATE:** Register: "Reserved neural research: weight-space
  programming / targeted enhancement of a less powerful AI —
  DEFERRED (long-term); **NO IMPLEMENTATION AUTHORIZED**." This
  section respects that fence exactly: it designs NO research and
  NO mechanism. It is a charter stating what a future authorization
  request would have to contain before anyone may even propose
  work — the maximum designable content under a no-implementation
  fence.
- **DESIGN — the charter (full):** a future authorization request
  for V-13 must contain, on its face: (1) the precise claim (what
  weight-space operation, on what model, to what measured end);
  (2) the evidence standard (the claim's falsifier, stated before
  any experiment — the FAR-12 ladder applies: reported results are
  not machine-checked results); (3) the sandbox boundary (no
  production model, no docked operator, no program state is an
  experimental subject; experiments run on disposable copies or
  not at all); (4) the authority path (Ace authorizes; the Director
  reviews the claim's evidence design; the Keeper audits) — a
  request missing any element is incomplete by definition;
  (5) the standing caution from this stratum's own record: FAR-5's
  rule — enhancement claims enter with mechanism + measurement or
  as rejected specimens.
- **ACCEPTANCE / FAILING-FIRST:** none — nothing is built or tested.
  The charter's failure state: any V-13 work product existing
  without an authorization containing (1)–(4).
- **SPLIT:** Charter NOW. Everything else: unrequested, unauthorized,
  unbuilt — by Ace's fence, preserved verbatim.

## §14 — #171 — The Human Surface track (consolidated)

- **STATE:** Register: "Human Surface track (cross-cutting;
  separately authorized — no UI build started): Nursery cards and
  shapes, Plane ROOM/SKY with glide/zoom, the five context-
  preserving pages incl. the Psalm Matrix, personal identity page,
  AGE surfacing, animated face (Dell 05), Show, navigation research,
  Ace's live-use acceptance; wave-field SKY rendering is a
  display-only design option filed here (§14.9)."
- **DESIGN — the consolidation (full):** the H track is the V rows'
  cross-cutting envelope; this plan files it WITHOUT duplication:
  1. **Cross-filed (designed in the sections named, counted once):**
     Nursery cards → §1; shapes → §2; ROOM/SKY + glide/zoom → §5,
     §6, §7; the five pages → §8; Psalm Matrix → §10; navigation
     research → §9; Ace's live-use acceptance → §12 (gate b).
  2. **H-only items (designed here):**
     a. **Personal identity page** — a page in the V-08 set's spirit
        (not a sixth page unless V-08's design confirmation makes it
        one): whose Matrix this is — owner identity, the AIs docked
        under his authority, his standing preferences as the
        surfaces consume them. Read-mostly; edits route through the
        existing preference machinery. Design rule: the page shows
        what the program BELIEVES about its owner, so wrong beliefs
        are visible and correctable — a mirror, not a profile form.
     b. **AGE surfacing** — the program's age/generation information
        (generation counters, checkpoint generations, the program's
        own history depth) surfaced where a human can see it: on the
        identity page and the Plane. Design rule: ages shown are
        read from the records that already keep them (generations
        are receipted facts); no new age-keeping is created for
        display.
     c. **Animated face (Dell 05)** — Dell 05's face as a living
        surface element: the design binds it to REAL state only —
        the face expresses the program's actual condition (working,
        waiting, refusing, idle) read from the same receipts
        everything else reads; a face animated independently of
        state is a decoration that lies, and is refused here.
        Ambient-vs-signal discipline from §6.4 applies (expression
        changes are signals; idle drift is ambient and minimal).
     d. **Show** — the presentation surface: the program showing its
        work (a journey, a field, a result) as a composed view for
        witnessing — Show is a view over records (§0), assembled for
        an audience moment; it writes nothing.
  3. **Track law:** the H track is separately authorized (register)
  — its builds need Ace's act for the track, in addition to each
  row's own gates.
- **ACCEPTANCE:** per item, the cross-filed sections' terms; for
  H-only items: identity page belief-equality fixtures (page =
  records), face state-truth fixtures (forced states → matching
  expression class; a mismatch is a defect), Show's empty write
  diff.
- **FAILING-FIRST:** `face_tells_truth` — force the program into
  named states on fixtures and assert the face's expression class
  matches the receipted state; at base no face surface exists
  (FAIL).
- **SPLIT:** Designs NOW (consolidation + H-only packages). Builds:
  B-VII + Ace's track authorization + per-item gates.

## §15 — #176 — Literal wave-field instrument (parked research filing)

- **STATE:** Register: "Literal wave-field instrument —
  INNOVATE_DEFERRED, parked (§14.9): read-only and nonauthoritative
  if ever built; never feeds resonance scores, Nursery admission,
  vote weights, or threshold decisions; any semantic path is an
  Ace-owned architecture decision." The H track files its display
  form: wave-field SKY rendering as a display-only design option.
- **DESIGN (the filing, full — and deliberately nothing more):**
  (1) what it would be IF Ace ever unparks it: a SKY rendering skin
  where field values render as a wave field — display only, a way
  of SEEING the field, changing nothing it shows; (2) the fences,
  carried verbatim from the register: read-only and
  nonauthoritative if ever built; never feeds resonance scores,
  Nursery admission, vote weights, or threshold decisions; (3) any
  path from this rendering to semantics (values read back into any
  mechanism) is an Ace-owned architecture decision — not a build
  detail, not a lane's call; (4) revisit condition: Ace's decision,
  unscheduled.
- **ACCEPTANCE / FAILING-FIRST:** none — parked. The filing's
  failure state: any wave-field output reaching a score, admission,
  weight, or threshold — the fences exist so that state is a
  named violation, not a design choice.
- **SPLIT:** Filing NOW. No build proposed; no research proposed
  beyond this filing.

---

*End of Vision Surface Plan. Coverage: rows #99–#111 (§1–§13), #171
(§14, with cross-filings counted once), #176 (§15) — each with
state, full design, dependencies, acceptance, failing-first, and
the design/build split.*
