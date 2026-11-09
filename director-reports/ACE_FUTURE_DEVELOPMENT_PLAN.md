# THE SUPER ASSESSED PLAN — Ace's Future Development Plan

Consolidated and assessed 2026-11-04 at Ace's order, from the
full voice session of that day. This document is the single
complete statement of everything Ace directed for future
development in that session (sections 1–10), plus the reserved
slot for the Director's forthcoming item (section 11). These
are directions for what gets built AFTER the current Director
cycle (TD-1-R2 and its certification round) finishes. They are
product vision, not yet engineered directives — each becomes a
real directive when Ace says go.

> **Revamp note — 2026-11-08 (Ace's order, voice review, sleep
> mode).** This plan previously lived only in Uni's workspace.
> At Ace's direction it is now IN THE REPOSITORY, revamped with
> everything worked on during the 2026-11-08 Dell-by-Dell tour:
> a new **section 12, THE DELLS PLAN**, holding the tour, its
> findings, and Ace's directives from that day. Sections 1-11
> are the 2026-11-04 original, unchanged. Section 12's items
> expand the objective space beyond the original 72 - Ace, in
> session: "it's going to be more than 72." Register IDs and
> statuses for the new items are the Director's to assign; this
> plan authorizes nothing by itself.


## 1. Proposal cards in the Nursery

Proposals (from the docked AI) must be easy to SEE and understand:
card-style presentation in the Nursery, readable at a glance —
what is proposed, what it touches, and the confirm/reject choice
obvious. Ace's ruling: this is something to develop deliberately,
not an afterthought. (Verified current state, 2026-11-04:
proposals live in `form/dell_matrix/nursery.py` as records with
status pending | confirmed | rejected; only Ace's confirm moves
them. The card-style look is the future work, not today's fact.)

## 2. Custom idea shapes, chosen in the Nursery

When Ace creates an idea, he can also build how it LOOKS: a
circle, a square/box, a triangle, or a custom-drawn outline. The
shape is chosen in the Nursery before commit and is held with
the idea as part of its identity presentation.

## 3. The space: room (3D) and sky (2D)

Ace's mental model for the Plane, to drive future display work:

- ROOM = 3D environment. Walk around it. Boxes can be placed,
  stacked on other boxes, opened. Every square has a 3D
  coordinate (up/down/left/right/depth).
- SKY = 2D environment. Ideas float as clouds on a 2D coordinate
  field.
- Ideas stay where Ace puts them in both views; nothing moves
  unless he moves it.
- The display must NOT look stagnant or boring — depth, soft
  motion in presentation (shadows, drift, unfolding) — while the
  underlying state stays put.
- Navigation must not be step-by-step through coordinates (that
  is boring and easy to get lost in): zoom out to see the whole
  room/sky, tap an idea to glide to it. Keep the whole space
  held together and organized.

## 4. Gates before the human-testing push

- A real AI must be docked (live dock session, not scripted).
- Ace works the DellMatrix himself as a human user.
- Until both happen, development continues on the engineering
  side; the look gets refined after Ace has reviewed it himself.
- Ace wants the bumps and rough edges mapped on paper first,
  before the testing push.

## 5. Director's forthcoming items

Ace has been talking with the Director separately; the Director
has further development items he will route to Uni through Ace
later in development. Nothing to invent — they arrive as
directives when they arrive.

## 6. AI-suggested looks + a shape language (added later in the session)

The AI can also choose what things look like — as proposals in
the Nursery, never as silent decisions:

- Semantic icons: an idea about a house gets a house; an idea
  about studio time gets its fitting image.
- A consistent shape FORMAT for the whole DellMatrix: boxes mean
  something, circles mean something — shapes carry category
  meaning, so the space is readable at a glance.
- Ace sees the AI's suggested look in the Nursery and commits
  it, or overrides it with his own (see section 2).

## 7. The two most important screens

- THE NURSERY is the most important screen in the program. It is
  where the user spends the most time and where ALL decisions
  about ideas are made. It must feel like painting / building
  artwork — fun, organized, game-like to move around in. It must
  NOT be a bundle of suggestions and dumped information. Looking
  at what an idea could be, choosing what to do next, playing
  with the possibilities — that experience is the product.
- THE PLANE is the second: where you look at your ideas, zoom
  into them, and examine them — but decisions route back to the
  Nursery.

## 8. The page set — few pages, all linked, context-preserving

Ace's page inventory (keep it small):

1. The Plane (main view of the space)
2. The Nursery (decisions)
3. The Dells page — all the Dells and how they operate
4. The Dell Playground — where the human pulls ideas using
   Dells themselves, hands-on
5. The AI place — somewhere to talk to the AI in pure English
   text that is NOT a chat box. A new concept to be invented:
   something more than a chat box.

Every page is LINKED and context-preserving: open an idea, then
switch to the Nursery and you are still in that idea; switch to
the Dells and you see that idea's Dells. Zoom out and you return
to the main Plane, the main Nursery, all the Dells.

## 9. Navigation placement — RESEARCH FIRST (Ace's correction)

Ace first said pages on top, then corrected himself: do
examination on the internet and decide from evidence where page
navigation belongs (top, bottom, side) for this kind of creative
spatial tool. The placement is a researched design decision in
the future GUI work, not a guess.

## 10. The fifth page is the PSALM MATRIX (everything AI)

Ace's naming, spelled P-s-a-l-m-s: in this program AIs are
called **Psalms**. The AI page (section 8, item 5) is the
**Psalm Matrix**, and it is where everything AI happens:

- Talk to the AI in pure English (more than a chat box — section 8).
- The **Persona Matrix** lives inside it: there are different
  personas, and the user chooses the persona there.
- See all your Psalms and where they are docked.
- Docking itself happens there.

Verified against the codebase in-session: personas.py holds a
persona registry (including Ancient_Psalms); the actions
registry carries psalms commands (workshop psalms, view
ancient_psalms); matrices_hub lists Persona and Psalms among
the matrices. Persona/BIMO material remains descriptive
metadata — it never confers authority (agent_coordinator.py).

## 11. RESERVED — the Director's forthcoming item (neural, later)

Per Ace (2026-11-04): the Director has ONE thing coming for
this plan. Ace's preview of it: it has to do with neural
networks; it is pretty advanced, so it is for later on; its
purpose is to let us enhance AI that is not as powerful —
lifting a weaker AI through what the Matrix gives it.

Recorded as Ace described it, nothing further invented. The
actual directive arrives from the Director through Ace, and
this section is replaced by it verbatim when it lands. Uni
stays ready to receive it.

## Codebase facts established in the same session (verified by search)

- BIMO exists in the codebase: an actions-registry command group
  (bimo, bimo fuse, bimo pilot, bimo defaults, bimo clear,
  workshop bimo — "fusion body") and, in agent_coordinator.py,
  BIMO slots/personas and bimo_binding explicitly classed as
  DESCRIPTIVE behavior metadata that never confers authority.
  It is not a separate running AI authority.
- Proposals: `form/dell_matrix/nursery.py` (Proposal, status
  pending | confirmed | rejected; Nursery.add/pending/confirm/
  reject), fed by the inference dock (inference_dock.py,
  dock_session.py), persisted per owner.

## Addendum — Correction recorded 2026-11-04 (Ace + Uni, after the voice session)

During the live session, Uni wrongly denied BIMO's existence after
searches in the voice layer failed, and Ace accepted that denial.
Corrected the same day, verified first-hand by grep over form/:

- BIMO IS real, existing machinery: `form/dell_matrix/personas.py`
  defines BIMOBody — a fusion body with named dock slots (logic,
  growth, morph, fusion, ancient, language, quality, voice,
  execute, watch, body) and dock/undock/dock_defaults/clear/
  set_pilot/fuse; `form/open.py` carries `Program.bimo` with
  status/dock/fuse methods; it persists via persist_rest and has
  live commands (live_visual.py, actions_registry.py). It is a
  persona fusion/docking system — the "mecha suit" territory —
  not a separate running AI authority, and docking confers no
  authority. Consequence for §10: the Psalm Matrix page builds
  its interface on this EXISTING BIMO/persona machinery; the
  future work is presentation and wiring, not a new engine.
- Proposals likewise already exist as machinery
  (`form/dell_matrix/nursery.py`: Proposal records with
  pending | confirmed | rejected, fed by the inference dock,
  persisted per owner; only Ace's confirm moves them).
  Consequence for §1: the future work is the card-style LOOK
  only — the proposal system underneath is built.
- Standing rule from this correction (Uni, permanent): a failed
  search means "unproven," never "not there." Absence claims
  require a completed, verified search of the codebase.

## 12. THE DELLS PLAN (2026-11-08 - Ace's Dell-by-Dell tour)

Ace is walking every Dell personally, 00 through 99, examining
what each one ACTUALLY does against what its name promises, and
directing corrections as he goes. Progress: **00-20 examined.**
The tour paused at 20 on 2026-11-08 (Ace going to sleep; sleep
mode continues under the Director) and **resumes at 21 (Merge)**.
Findings for 15-20 below were verified first-hand from code at
main `61f10b3` on 2026-11-08; 00-14 findings and directives are
carried in 12.6 as recorded during the earlier tour sessions.

### 12.1 Findings by Dell (15-20, verified 2026-11-08)

- **15 Map** (manor: "Coordinate / index"). Not a map. A shape
  word (cube / sphere / core / flower) switches the lattice
  PERCEPTION form - a lens: it changes how distance and shells
  are READ (cube = max-norm cubic shells; sphere/core =
  straight-line radial distance from origin; core's skin reads
  as "seed"). Positions NEVER move. Any non-shape word births a
  plain idea with that name (same place_idea family as 07/08/14).
  Bare Map reports a unit census. Finding: the Form enum holds
  SIX forms (square, circle, cube, sphere, core, flower) but the
  seed's word list reaches only four - "Map square" births an
  idea named square instead of switching the lens.
- **16 Decay** (manor: resonance cooling). A MANUAL-ONLY
  multiplier over accumulated resonance scores: default 0.9,
  clamp 0.1-1.0, junk input keeps 0.9 and never raises. Behind
  the enhance gate - with the gate OFF it refuses honestly
  (ok=False, "scores unchanged"); no bypass path. No timer,
  tick, or hook calls it anywhere. It fades SCORES only, never
  ideas. See 12.2 for Ace's resonance model, which supersedes
  this picture as the design target.
- **17 Shadow** (manor: "Background parallel"). MESSAGE-ONLY.
  It mints a track id ("shadow_" + label, bare = "shadow_bg"),
  announces "parallel - not live", and notes the seed. No copy,
  track, or parallel program is created; the live census is
  unchanged. The gap is documented, not hidden: CORE_I.md lists
  "17 Shadow is not parallel compute" as an external blocker.
- **18 Mirror** (manor: "Compare / diff"). A read-only ROSTER:
  header carries the true total ("Mirror: N live ideas"), then
  one bullet (unit id, label, skin) per unit, CAPPED AT 16
  bullets, with no truncation line. It performs NO comparison.
  See the directive at 12.3.
- **19 Drive** (manor: "Direction / intensity"). Avatar feet
  only. Bare/any word = walk 1 step along current facing; a
  word containing "run" = 2 steps; containing "stop" = idle.
  No direction argument and no distance argument exist;
  turning belongs to 04 Transform. Stepping stands the avatar
  up first if sitting/bending.
- **20 Alpha** (manor: "Close / finalize"). A sign-off CARD
  only: idea census, the current lattice form (the form Map
  set - its one unique read), and the tip "save before exit -
  10[Keep]". It does NOT save, close, finalize, or checkpoint
  anything. See the directive at 12.4.

### 12.2 The resonance model (Ace, 2026-11-08, at Dell 16)

Ace's definition, which the current build does NOT yet honor:

- **Resonance IS relatedness.** Ideas that relate resonate;
  the more they relate, the stronger the resonance. Shared
  MEANINGFUL words (house, car, apartment) create baseline
  resonance; universal words (the, and) create none. A real
  relation outweighs a shared word: a car resonates with many
  things because you drive it to many places; a job and a sport
  that only share a schedule resonate slightly.
- **Pulse must be targeted and changeable** - when Ace pulses,
  WHAT he is pulsing is his choice, not one fixed global blast.
- **Resonance must be VISIBLE within a thing** - opening an
  idea shows its resonances: with whom, how strong, and why.
- **Decay happens only when resonance is going down** - decay
  is the decline of resonance as relations weaken, not a
  free-standing dial that can be spun at any time.

Verified current-state gap (code, 2026-11-08): pulse is flat
DIFFUSION - every active unit gives each enhance-scope peer
+0.25 score and +0.15 shared tokens, unweighted by how much
the pair actually shares; the Dell 25 path is whole-field and
untargeted. A relatedness pair-score (ringed_growth._affinity:
0.40 harmonic + 0.22 shared-word Jaccard + 0.13 spatial +
0.13 in-scope + goal/body boosts) EXISTS but serves only
Cycle's growth proposals, is invisible as resonance, and never
feeds the pulse/decay scores (the GDP-001 concept separation
keeps the two apart). No per-pair resonance view exists for
the human. This model is design-session material (with the
growth redesign, 12.6) - not a unilateral cycle build.

### 12.3 Directive - Mirror gains the true compare (Ace)

"Make sure mirror does that. It can do everything that it
currently does, but it needs to also do that." Dell 18 keeps
its live roster AND gains a true SIDE-BY-SIDE COMPARE/DIFF of
two ideas - shared vs differing content, laid out to be read -
because, in Ace's stated reason, **the docked AI needs to be
able to do that.** Verified absent today: the only pair
machinery is scorers that collapse a comparison into one
number (verita_of_pair coherence; _affinity for growth) and
the dock's relate verb (the model judges a pair in its own
head and lands a proposal; the system gives it no structured
diff to read). Bounded circuit through Director routing when
scoped; the 16-bullet roster cap rides along in that scoping.

### 12.4 Directive - Alpha creates the checkpoint (Ace)

Ace, rejecting the card-only close: "At the very least it
should save a snapshot of the record of everything - of how
things happened, what the current state is, and how everything
reached the current state from beginning to end. And that
will create the checkpoint."

Verified current state: the checkpoint MACHINERY exists and is
strong - commit_checkpoint (form/mandell/checkpoint_generation.py,
reached via core_i_recovery.checkpoint / core_i_ops) seals
the current state as one hash-verified GENERATION (members:
nursery, program, ideas, graph; manifest; atomic pointer swap;
retention keeps current + previous; crash-tested in 72-28,
where the checkpoint path never showed a hybrid). BUT: no Dell
invokes it, and the sealed generation carries NO history
member - the program's seed history is bounded and in-memory,
so "how everything reached the current state, beginning to
end" is NOT captured by a checkpoint today. The build, when
scoped: wire Dell 20 to the EXISTING checkpoint authority (no
second authority) and close the history-member gap honestly,
including what "beginning to end" can mean under bounded
history. Persistence-path work: the gated bucket rules apply
(F2-style failing-first evidence before implementation).

### 12.5 Perspectives - settled (Ace decision, 2026-11-08)

Custom perspectives named into existence through Map (a
non-shape word birthing an idea that would later become a
lens) were considered in session and REMOVED from the design
plan by Ace. The designed Form set stands as-is: square,
circle, cube, sphere, core, flower. If a new perspective is
wanted later, it will be designed deliberately. The history
of the idea is preserved here and in Uni's session records;
do not re-propose it. (The square/circle reachability gap in
12.1 remains a finding, separate from this decision.)

### 12.6 Directions carried from the earlier tour sessions (00-14)

Recorded during Ace's 2026-11-08 tour of Dells 00-14 (same
voice review series; full session records in Uni's workspace
state files):

- **DD-14 - Dell 13 Loop.** Its receipt ("requested 3,
  executed 3") implies the whole chain repeated; in fact the
  count is spent on the shared growth engine only and chained
  atoms (Pulse, Decay) execute ONCE. Dell 06 Cycle uses the
  same engine but its receipt scopes itself to growth honestly
  and is NOT implicated. Ace: "fix that crap" - the Loop fix is
  the next-best-directive pick after the snapshot circuit and
  dock Proposal B clear. Ace's lean: Loop learns TRUE
  chain-body repetition, making it genuinely distinct from
  Cycle; honestly scoping Loop's grammar/receipt to growth-only
  remains the alternative inside the DD-14 contract.
- **Growth redesign.** Growth must be DEVELOPMENT-COUPLED -
  "an idea can't just grow because it exists; it has to grow
  when an idea develops into something greater." Attention is
  the SMALLEST factor in growth (tiny, but a factor). Growth
  must be MUCH slower - fruit in 29 passes is too fast; a stage
  like fruit is an ACHIEVEMENT. Current build (verified):
  flat per-pass growth for every plant, not development-
  coupled. Ace wants a dedicated SIT-DOWN design session to
  develop the growth model together before any implementation.
- **Placement law.** Creating an idea takes Ace to the Plane
  with the new idea IN HAND to place it himself. A
  replacement/superseding idea takes the replaced idea's SAME
  spot. A child lands AROUND/near its parents, in surrounding
  spaces Ace can choose. Nursery confirmations of new ideas
  are placed by Ace.
- **Create split + modes.** Create must offer: idea-only (in
  the book, no body), body-only (an empty Plane shape, no
  idea), or both together. The program gets an owner-held mode
  switch: AUTO mode (today's behavior - create/confirm fuses
  idea+body onto the Plane automatically) vs BIND mode (ideas
  stay in the book, bodies go on the canvas, nothing fuses
  until Ace binds it by hand through the bind machinery). The
  Plane is Ace's canvas; ideas can live to the side until
  bound - that is the BIND-mode vision, not current behavior.
  Verified today: AUTO-only; confirming DOES land the idea on
  the Plane fused; no unbind operation exists.
- **Auto-confirm law (Cycle, Dell 06).** Cycle's auto-confirm
  switch may operate ONLY when the human commands it WHILE an
  AI is docked and in control of Cycle, with the AI choosing
  accept/reject from the data (ranking formula / next-best-
  directive machinery). It stays OFF until a build enforces
  exactly that.
- **Human surface.** (a) Dells 01/02 are the user's personal
  page - identity and presence should be VISIBLE on entry, not
  hidden behind commands. (b) Time should surface as AGE on
  things (felt, human) with the tick kept underneath; plants
  already carry an age field. (c) Dell 05 Tone's face should be
  ANIMATED, emoji-based, and fun (personas already wear emojis;
  a face-wardrobe system exists underneath; the animation
  layer is the missing piece). (d) Dell 09 Show needs its own
  sit-down design session (with growth, the face, and age) so
  showing feels like entering the room.
- **Idea-field reachability.** The WHOLE idea field must be
  reachable and browsable by Ace - the system provides the
  list of idea names (he cannot be expected to know the names
  of ingested ideas, e.g. a ~1,000-idea email field). Bounded
  fetching underneath is acceptable; it must not feel like a
  wall or a limit. (The snapshot repair circuit of 2026-11-08
  is the first step on this line.)
- **Nursery proposal governance - formula CONFIRMED by Ace.**
  S = 0.40 LINK (connection strength) + 0.25 ACE (Ace's
  signal/focus) + 0.20 FRESH + 0.15 NOVEL; top-5 retained per
  topic bucket; evictions tombstoned, never silent; the
  200 ceiling is NURSERY-PENDING-ONLY (the idea field itself
  is uncapped). Open: Q-N3 (30-day FRESH half-life for all
  corpora vs per-corpus). Incorporation is a bounded circuit
  through Director routing. (Full design: workspace file
  NURSERY_PROPOSAL_RANKING_FORMULA_2026-11-08.md.)

### 12.7 Register note - beyond the 72

Ace, 2026-11-08: the new work means the objective space is
"going to be more than 72." Proposed for inclusion in the
Master Objective Register as a Dells series (IDs, statuses,
and folding are the Director's to assign; several items touch
existing 72 rows and the defect register - DD-14 is already
tracked there):

1. Complete the Dell-by-Dell tour, 21-99 (in progress: 00-20).
2. DD-14 Loop chain-repetition repair (12.6).
3. Resonance model build - targeted pulse, visible resonance,
   decline-coupled decay (12.2).
4. Mirror compare/diff (12.3).
5. Alpha checkpoint wiring + history member (12.4).
6. Growth redesign - development-coupled growth (12.6;
   design session with Ace first).
7. Placement law + Create split + AUTO/BIND modes (12.6).
8. Human surface - personal page, AGE surfacing, animated
   face, Show design (12.6; design sessions first).
9. Nursery ranking formula incorporation (12.6).
10. Auto-confirm gating build (12.6).

Each item becomes a real directive through the ordinary
routing (Director confirms scope; gated-bucket rules apply
to persistence-path items such as 12.4). Nothing in this
section is certified, and nothing here claims a capability
the code does not have today - the verified current state is
stated beside every direction so the gap is the record.

## 12.8 TOUR CONTINUED — 21 MERGE, 22 SPLIT (Ace session, 2026-11-09)

Tour resumed at 21 per Ace's direction. Verified live at main 7e4f6d3
(REPL, probe owners TOUR21*/TOUR22A; implementation form/mandell/
live_identity.py via executor.py:89).

**21 Merge — verified behavior.** Resolves named sources on the PLANE
(id -> exact label -> case-insensitive label; joiner words skipped);
2+ sources mint child merge_<p1>_<p2> (repeats suffix _2, _3 — a repeat
MINTS another child, never refuses); parents recorded, guarded
unmutated, and survive; child lands on the Plane beside its parents.
Bare/single/unknown-source invocations refuse missing_source with zero
mutation (the former silent last-two-units fallback was the B3 defect,
Director FIX step 6); an ambiguous label refuses ambiguous_source.
LIMITS: Plane units only (book/Nursery ideas invisible); no graph edge
(lineage = the child's parents list only); the child's words are the
literal pointer string "merge <p1> <p2>" — NO parent content, words,
goals, or data are inherited or combined.

**ACE RULING (2026-11-09, voice): the receipt child is UNACCEPTABLE.**
A Merge child must be a FUSION: a fusion of the parents' name AND a
fusion of their resonating data — the child carries the parents'
combined meaningful content (per the resonance model of section 12.2:
meaningful shared words and relations are the substance), not a
pointer string. Filed as defect **DD-15**; the repair is a bounded
circuit through Director routing in the Dells series (section 12.7),
exact fusion semantics (word union/shared-first ordering, goals
handling, repeat-merge behavior) to be pinned in that circuit's
contract. Until then, Merge's current behavior stands as the verified
baseline this ruling supersedes in intent.

**22 Split — verified behavior.** Takes the FIRST resolved source only
(extra named sources silently ignored); mints <src>_a and <src>_b with
labels "<label> A" / "<label> B", BOTH carrying the identical pointer
words "split <src>", parents [source], origin split; the source is
preserved and guarded unmutated (source_mutated check). Bare/unknown
refuses missing_source with zero mutation (former silent last-unit
fallback = the B4 defect, Director FIX step 6). Split children can be
re-merged (round trip verified live). LIMIT: the halves inherit NONE
of the source's words/goals — nothing is divided; A and B are empty
identical twins distinguished only by their labels. Same content-
poverty class as DD-15, in reverse; logged as finding **DD-16**
(observed; Ace's ruling on the division semantics is his to give —
the DD-15 fusion principle suggests its mirror: a split should
divide the source's actual data between the halves).

**ACE RULING — SPLIT SEMANTICS (2026-11-09, voice, same session).**
Ace resolved DD-16's open question in his own words: when you split an
idea, you take the things inside it that relate to each other the
LEAST — "kind of like opposite but not necessarily opposite; things
that relate to each other the least" — and you put one side's things
in one child and the other side's things in the other child. "And
then you have two children but you don't lose the main." Formally:
partition the source's content items (words/goals, per the resonance
model of section 12.2, where relatedness is meaningful shared words
and real relations) into two groups that MINIMIZE cross-group
relatedness (items within a group hang together; the two groups have
the least to do with each other), child A inherits group one's data,
child B inherits group two's data, and the parent survives whole and
unmutated (current verified behavior, retained). NOT opposites-
detection and NOT an even-count deal: the cut follows relatedness.
DD-16 is now RULED, not merely observed; the partition algorithm and
its edge cases (single item, empty content, ties) are pinned in the
repair circuit's contract, built as a bounded circuit through
Director routing in the Dells series alongside DD-15 (the two are
one family: Merge fuses resonating data, Split divides by least
resonance).

**ACE CLARIFICATION — RESONATING ITEMS STAY TOGETHER (2026-11-09,
voice, same session).** Ace sharpened the split rule: items that
RESONATE with each other are kept together — a resonating cluster is
never torn across the two children ("they also keep both resonating
ideas"). The split line is drawn BETWEEN clusters: the groups that
are opposite / least related to each other land on opposite sides
("one go to one side and one go to the other"). So the partition is:
cluster by resonance first (resonating items bind together), then
separate the clusters into the two least-related camps, one camp per
child; the parent is not lost. This refines, and is consistent with,
the least-relatedness partition above: maximize within-side
resonance, minimize cross-side resonance, never split a resonating
cluster.

## 12.9 TOUR CONTINUED — 23 LOCK (Ace session, 2026-11-09)

Verified live at main 7e4f6d3 (REPL, probe owner TOUR23A;
implementation executor_leaf.py:359 -> Program.sandbox_on ->
SandboxGate.apply_on, form/dell_matrix/sandbox_gate.py).

**23 Lock — verified behavior.** Ignores its label entirely; one
invocation boxes EVERY live unit into a single auto sandbox
(auto_sandbox): each unit sandboxed=True with the shared sandbox_id;
Show flips units from [connected] to [box:auto_sandbox] and lists
the box membership. The gate stays ON: units created or minted
(Create, Merge children) while locked are auto-boxed on arrival
(maybe_auto_box). The boxed state persists (sandboxed + sandbox_id
are saved and restored). What the box DOES (code-verified):
interaction isolation — containment/Bind cannot cross the sandbox
boundary (TD7 isolation key: (sandboxed, sandbox_id)), and
pulse/enhance resonance scope does not cross between boxed and
unboxed units. What it does NOT do: freeze anything. Merge executed
normally inside the box (verified live); units remain editable.
24 Unlock (verified live as the pair): unboxes everything,
"Sandbox OFF.", [connected] restored; clean round trip.

**Finding DD-17 (observed; ruling is Ace's/Director's).** The name
overpromises in two ways. (1) "Lock" implies protection or
immutability; the behavior is GROUPING into one shared box — and
because the Dell boxes everything into the SAME box, the isolation
never actually separates anything at Dell level (within-box work
proceeds normally); selective boxing exists only at the API level
(apply_on accepts unit subsets) and no Dell exposes it. (2) The name
collides with the sovereign Lock of the Mandell discipline — the
human-kept step beside Commit and the learning gate (Ace,
2026-10-26) — while Dell 23 is an ordinary atom any chain can fire.
Registry text itself disclaims: "not per-unit immutability, not a
permission grant." Candidate directions (not decided): rename the
Dell to match its grouping behavior; expose named/selective boxes;
or give Lock real freeze semantics under the owner's hand. Tour
stands at 00-23 examined (24 verified as Lock's pair); resumes at
24/25 as Ace directs.

**ACE RULING — THE LOCK/SANDBOX SYSTEM (2026-11-09, voice).**
DD-17 is resolved by direction, in Ace's own terms. He needs three
things from Lock:
(1) A STANDING AUTO-LOCKED BOX: a box that is simply always there
and locked, into which he can put things when he wants and take
them out — putting a thing in takes it OUT of the Plane's general
field and OUT of resonance.
(2) DRAWN, CUSTOM BOXES: he can draw boxes (on the Plane, per the
ROOM framing) and make CUSTOM locks and CUSTOM sandboxes from
them — owner-defined boxes, not only the one auto box.
(3) MULTIPLE SANDBOXES AT ONCE: as many as he wishes; things
resonate WITHIN the sandbox he chose, another sandbox resonates
within itself, and neither affects the entire Plane — resonance is
scoped per box, and the open Plane is not dragged in.
Grounding (verified this session): the Plane model already carries
multiple Sandbox records (id, label, member_ids) and the isolation
semantics already key on (sandboxed, sandbox_id) — containment
(TD7) and enhance scope already respect box boundaries; what does
not exist is the owner-facing surface: named/multiple boxes,
membership put/take by the owner, a standing locked box, and
Dell-level addressing of a chosen box (today's Gate has ONE
auto_box_id and Lock boxes everything). The build extends the
existing sandbox authority — no second authority. DD-17 status:
RULED (design direction set); implementation = bounded circuit
through Director routing in the Dells series, contract to pin:
box naming/creation via the Dells, put/take verbs, the standing
box's identity, per-box resonance scoping proof, persistence.

## 12.10 TOUR CONTINUED — 25 PULSE (Ace session, 2026-11-09)

Verified live at main 7e4f6d3 (REPL owner TOUR25A; in-process
executor probes owner TOUR25B). Implementation: executor_leaf.py
(25 arm) -> Program.pulse -> EnhanceGate (form/dell_matrix/
enhance_gate.py) -> resonance.pulse (form/dell_matrix/resonance.py).

**25 Pulse — verified behavior.** The enhance engine is OFF by
default and gated: with the gate off, resonance.pulse never runs.
With the gate on, one pulse makes every in-scope unit send a FLAT
+0.25 score (plus +0.15/token tag spread of the sender's tokens) to
every peer in its enhance scope (scope is spatial + sandbox aware);
the score is NOT weighted by relatedness — an unrelated unit in
scope receives the same +0.25 per sender as a kindred one (live:
welcome, house, car each +0.5 from two senders). Faded/inactive
units neither send nor receive (72-40, canonical lifecycle,
fail-closed). Enhance state (on flag, scores) DOES persist across
a save/load (verified in-process); in the raw REPL flow it can lag
behind Create's autosave-on-add, so a session that never saves can
lose flips at exit (observed, mechanism = save boundary).

**Defect DD-18 — Pulse's receipt lies when the gate is off.** The
leaf discards the gate's result and ALWAYS prints "Pulse sent." —
including when the gate refused with "enhance OFF" and zero pulses
occurred (live: session_pulses stayed 0, scores stayed {}). Same
receipt-honesty class as DD-14. The fix class is known: surface the
gate's verdict in the receipt (honest refusal when off/budget-
exhausted). Also observed: the on-switch is smuggled into Pulse's
label ("on"/"enhance_on" turn the engine ON instead of pulsing —
"Enhance ON."); every other label, including a unit's name, is
discarded, so NO targeted pulse exists at the Dell, and the receipt
shows nothing of what a real pulse did (no scores, no targets, no
per-pair detail — though the engine logs every transfer
internally). These last two are Ace's standing Dell-16 directions
(targeted/changeable pulse; resonance VISIBLE inside an idea),
filed for the sit-down design session; DD-18 is the bounded
receipt-honesty repair, routed like DD-14.
