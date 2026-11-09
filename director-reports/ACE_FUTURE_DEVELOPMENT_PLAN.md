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

## 12.11 TOUR CONTINUED — 26 TEMP (Ace session, 2026-11-09)

Verified live at main 7e4f6d3 (in-process executor probes, owner
TOUR26A). Implementation: executor_leaf.py (26 arm) -> Program
enhance_on/enhance_off/pulse — the SAME EnhanceGate as 25 Pulse.

**26 Temp — verified behavior.** There is no temperature: no
degrees, no scale, no per-idea quantity. Temp is a three-mode
switch for the enhance gate — cold/cool -> enhance OFF ("Temp ->
cold (enhance OFF)"); hot/heat -> enhance ON + one pulse ("Temp ->
hot (enhance ON + pulse)", and the pulse genuinely runs, since hot
opens the gate first; scores moved live); bare Temp and EVERY
other label -> warm ("Temp -> warm (enhance ON)"). Receipts for
the three modes are honest (state claims verified in-process).
The EnhanceGate therefore has three Dell-level remotes so far:
Pulse's smuggled "on" label (25), Temp (26), and Pause/Resume
(32/33, per the gate's own docstring).

**Finding DD-19 (observed).** ANY unrecognized label — a typo, a
unit's name, gibberish — silently resolves to warm and turns the
enhance engine ON (live: "Temp :: banana" -> enhance ON). Silent
coercion of unknown input into a state-changing default, the same
failure class the Director has had refused elsewhere (unknown
should refuse or hold, not silently switch a global engine on).
Secondary naming note, same family as DD-17: "Temp" promises a
temperature; the mechanism is a discrete mode switch. Rulings are
Ace's: refuse unknown labels (honest receipt), and whether a real
temperature (a graded quantity that modulates pulse strength)
should exist as part of the resonance design session's work.

### 12.11a ACE RULING on Temp (same session, minutes later — DD-19 becomes RULED)

Ace rejected the switch reading: Temperature is meant to be a
GRADED intensity dial sorting things into three categories —
cold = least, warm = moderate, hot = intense (he corrected
himself mid-sentence to exactly this ordering). And its reach is
wider than Pulse: "temperature is supposed to operate with a lot
of things not just the pulse." Parked by Ace for later work
("we're going to have to do some more work on that one. Later.")
— the full design (which systems temperature modulates, and how
the three grades map to magnitudes) belongs with the resonance
sit-down design session, not a unilateral build. Carried from
DD-19 unchanged: unknown labels must refuse, never silently warm.

## 12.12 TOUR CONTINUED — 27 CHECKPOINT (Ace session, 2026-11-09)

Verified live at main 7e4f6d3 (REPL owner TOUR27A + on-disk
inspection). Implementation: core_i_ops.py (27 arm) ->
core_i_recovery.checkpoint -> Checkpoint Generation V1.

**27 Checkpoint — verified behavior.** The Dell works, and its
receipt is honest: "Checkpoint written: generation <id>", with a
failure path that reports "Checkpoint fail: ..." and ok=False.
Bare use mints a hash-derived id (live: ge26172d083d4443d); a
label becomes the generation's name (live: "Checkpoint :: before
the storm" -> generation before_the_storm). Each sealed
generation carries four members — nursery, program, ideas, graph
— hash-verified by the machinery (the path that passed every
72-28 crash test with no hybrid), a committed flag, and
previous_generation_id, so generations form a chain of moments.
Rollback exists only authority-mediated at 28 (bare seed denied,
zero mutation; human two-step or a granted endpoint) — card-
verified here, examined at 28's own stop.

**The standing gap, confirmed from this side.** The manifest has
NO history member: a checkpoint seals WHAT the state is, not HOW
it was reached — no receipts, no sequence, no story. This is the
same gap Ace's Dell-20 (Alpha) directive already owns: closing
must save the record of EVERYTHING (how things happened, the
current state, and how the state was reached from beginning to
end). 27 proves the machinery that directive builds on is real
and Dell-wired (Alpha's card-only close is not); the history
member remains the build, in the gated bucket with the rest of
the persistence path. No new defect filed. Also noted: no Dell
lists existing checkpoints or peeks inside one — the owner gets
an id on a receipt and nothing to browse; that browsing surface
belongs with the field-reachability direction and the room/sky
display work.

## 12.13 TOUR CONTINUED — 28 ROLLBACK, EXAMINED VIA ACE'S QUESTION (2026-11-09)

Ace's question: does rollback work properly with the current
save, and will it work with the revitalized (planned) version?
Examined live at main 7e4f6d3 (REPL owner TOUR28A, the real human
path, plus fresh-process verification).

**Current save: YES, verified end-to-end.** Bare 28[Rollback]
DENIED with zero mutation (acceptance_policy_denied — no issued
approval for producer 'dell28'). Bare "restore" freezes and
DESCRIBES the target, never executes. "restore confirm first"
executed: it first sealed a COMPENSATING checkpoint of the
pre-rollback state (pre_rollback_first_20261109T1308), then
restored generation "first" — the live Plane lost the unit
created after that checkpoint, and a FRESH PROCESS load showed
the same converged state (eager convergence; the current pointer
names the compensating generation, chain unbroken). Consistent
with 72-33 (lineage survives reload and crash rollback).

**The planned revitalized checkpoint (the Dell-20 Alpha build:
a history member inside the sealed generation).** Rollback reads
sealed generations, not the everyday save pair, so the Q1
load-time-convergence repair neither affects nor is needed by
rollback. The history member rides inside the same envelope as a
fifth member beside nursery/program/ideas/graph, and a restore
carries the target generation's members with it — by design a
history-carrying generation restores its story with its state.
OWED BY THE BUILD, NOT CLAIMED TODAY: proof that pre-history
generations (four members) still freeze, confirm, and restore
under the new code (the fail-closed load law — one proven
complete old-or-new generation — applied to the member set), and
that a rollback to a pre-history generation behaves honestly
about the absent story. These become acceptance checks in the
Alpha checkpoint circuit's contract.

**ACCEPTANCE REQUIREMENT — the rollback/save combination (Ace,
2026-11-09, stated as a stop-and-record instruction).** The
rollback + checkpoint combination verified above is a standing
contract, not an observation: (a) the current combination (sealed
four-member generations + authority-mediated rollback + eager
convergence + compensating checkpoint) must not regress; (b) the
planned history-carrying generation ships ONLY when the build
proves, with live evidence through the human path, that
pre-history four-member generations still freeze, confirm, and
restore under the new code, and that rollback to a pre-history
generation behaves honestly about the absent story; (c) any
future change to either side of the combination (save format or
rollback mechanism) re-runs this compatibility proof before it
may merge. Ace directed that this requirement sit in the plan
where the Director reads it; it binds the Alpha checkpoint
circuit's contract.


## 12.14 TOUR CONTINUED — 29 COMPRESS (2026-11-09, DD-20)

Examined live (REPL probe owners TOUR29A–D, dock_clone @ 84a3977).
Registry: Dell 29 Compress, manor "Shrink payload".

**Verified today.** (1) Mandell door: `29[Compress] :: <text>`
mints a NEW SEED idea `compress_<distilled>`; the distilled label
is `distill_label` (form/open.py): tokens longer than 2 chars,
lowercased, deduped, at most 4 tokens / 40 chars. "the big red
fire truck drives fast to the station" becomes `the_big_red_fire`
— everything past the fourth long word is dropped. The source
idea is untouched; the seed's words are its own name; it carries
NO source resolution, NO parents link, NO goals or detail.
Bare Compress mints the empty tag `compress_distill`.
(2) The English door diverges: plain "compress <phrase>" displays
`29[Compress] :: <underscored>` but creates a PLAIN idea bearing
the full spaced phrase — no seed, no distillation, no
"Compressed →" receipt. Bare English "compress" is not understood.

**Ace's ruling — the reference model (2026-11-09).** Compress is
for carrying a tiny reference instead of the big heavy box: the
compressed seed must remember the big box it came from, so the
reference can be used to link back to everything in the box while
the box itself stays intact. Ace: "I'm sure the code is already
built somewhere. You just gotta link it all together and make it
all work."

**Grounding — the parts exist; the gap is wiring.** Plane units
already carry a persisted `parents` field (session place accepts
`parents=`; the snapshot round-trips it; Merge's children and the
confirm-lineage path already use it). `compression_report` and
`semantic_hash` (form/mandell/seed.py) already prove a compressed
form against its source. Expand (Dell 30) exists as the natural
counterpart but follows no link either. What is missing: Dell 29
never resolves a source idea and the leaf `place_idea` helper
passes no parents; and the English door needs the same
single-authority treatment Dells 21/22 received (GDP-001
delegation precedent).

**DD-20 (filed 2026-11-09, bounded circuit through Director
routing):** Compress resolves the named source idea, mints its
seed WITH the source recorded (parents link), keeps the honest
distilled label; the English and Mandell doors execute the one
authority with identical receipts; Expand's relationship to the
link is examined with Dell 30 (tour §12.15) before the circuit is
scoped.

## 12.15 TOUR CONTINUED — 30 EXPAND (2026-11-09, DD-20 EXTENDED)

Examined live (REPL probe owners TOUR30A–F, dock_clone @ 84a3977).
Registry: Dell 30 Expand, manor "Unfold" — the natural counterpart
to Dell 29 Compress.

**Verified today.** (1) Mandell door: `30[Expand] :: <text>` does
NOT look any idea up and restores nothing. It takes the typed
text, turns underscores back into spaces, and mints a NEW CUBE
named `expand_<source underscored, truncated to 24 chars>` —
chopped mid-word (`expand_compress_the_big_red_fir`). Expanding
the compressed seed from §12.14 merely re-spelled the seed's name
into a new box; the words Compress dropped ("truck drives fast
to the station") never return — they cannot: Compress discarded
them and kept no link home. (2) Bare Expand takes the LAST unit's
label + words as its source — including its own expand box,
producing `expand_expand_compress...` and a receipt that repeats
the phrase twice (label + words echo); it will expand itself
indefinitely. (3) The English door never reaches Dell 30 at all:
in the English brain "expand" is a synonym for GROW
(english_brain.py verb map), so "expand hello wonderful world"
executed `grow ideas` (13[Loop] growth) — Expand is Mandell-only
today, and the English speaker is silently rerouted.

**Ace's ruling (2026-11-09): YES** — Expand is the true unzip of
the pair. One zipper, two ends, one circuit: DD-20 now covers
BOTH Dells — Compress stamps the reference link to the source
box; Expand follows the link home and restores / surfaces the
full original. Neither end ships alone.

## 12.16 TOUR CONTINUED — 31 SIMULATE (2026-11-09, DD-21)

Examined live (REPL probe owners TOUR31A–B, dock_clone @ 84a3977).
Registry: Dell 31 Simulate, manor "Dry-run".

**Verified today.** Simulate previews NOTHING. Whatever follows
it — a name, a whole instruction ("simulate growing my ideas",
English door, which routes to Dell 31 correctly) — is ignored;
the Dell reads out three status numbers (owner, idea count,
history length) and stops. Its receipt claims "dry-run — no
mutation": the Plane truly does not change, but Simulate writes
its own visit into the record (note_seed) — two back-to-back
Simulates showed history_len 1 then 2; the dry run leaves a
footprint in the diary while claiming it touched nothing.

**Ace's ruling (2026-11-09): YES** — Simulate becomes a REAL
dry-run: hand it a command or a chain and it shows what WOULD
happen — the receipts and the changes — committing none of it,
so a messy merge or a bad link can be caught before it touches
the room. Ace also asked why this Dell only counts ideas when
the Dells were supposedly all made fully functional; the honest
answer, recorded here: the earlier circuits verified each Dell
against its WRITTEN contract (honest receipts, no crashes, args
handled), and Simulate passes its contract — the contract itself
is the placeholder. This tour is the first pass of every Dell
against Ace's design INTENT, which is a different and stricter
standard; that is precisely what the tour is for.

**Grounding.** No executor-level dry-run harness exists today.
The state-capture parts do: Plane/cube state serializes and
restores (blank_cube snapshot path), checkpoint generations
capture nursery/program/ideas/graph as sealed members, and the
receipt machinery already reports per-atom outcomes. The build
is wiring: run the given seed/chain against a captured copy of
state, diff, report, discard — plus removing (or honestly
relabeling) Simulate's own history footprint so "no mutation"
means it.

**DD-21 (filed 2026-11-09, bounded circuit through Director
routing):** Simulate executes its argument (a seed/chain) against
an isolated copy of program state and reports the would-be
receipts and state diff; the live state — including history —
is bit-identical afterward, proven by test.

## 12.17 TOUR CONTINUED — 32 PAUSE (2026-11-09, DD-22)

Examined live (REPL probe owner TOUR32A, dock_clone @ 84a3977).
Registry: Dell 32 Pause, manor "Halt".

**Verified today.** Bare Pause sets the avatar's locomotion to
IDLE and reports "Paused." Nothing else stops: there is no wall
clock and nothing moves autonomously in the Matrix — the avatar
moves only when Drive moves it, growth happens only when a grow
command lands — so today Pause halts a statue. It does not gate
growth, pulse, or cycle. Worse, it carries a hidden second job:
any Pause label containing the word "enhance" does NOT pause at
all — it switches the global enhance gate OFF and leaves the
avatar walking (`32[Pause] :: enhance please` -> "Enhance OFF.",
avatar still in walk, verified via Persona).

**Ace's exchange and ruling (2026-11-09).** Ace asked the
foundational question himself: "What would be the purpose of
pause if the Dell Matrix doesn't move unless I move it?" — then
ruled: **"Well, Pause should stop."** Pause is a REAL halt: when
Ace pauses, activity stops (the room's engines — growth, pulse,
cycle/enhance effects, avatar motion) until Resume releases it.
Exactly which command classes refuse vs. merely report while
paused (reads/Show vs. mutating commands) is scoping for the
circuit through Director routing, as is the fate of the hidden
enhance keyword (the presumption recorded here: it leaves Pause;
the enhance gate already has owners in Pulse/Temp, cf. DD-19).

**DD-22 (filed 2026-11-09, bounded circuit through Director
routing, paired with Dell 33 Resume, SS12.18):** a program-level
paused state, set by Dell 32 and cleared only by Dell 33, under
which activity commands refuse honestly (ok=False, skipped,
reason "paused") while inspection stays available; no keyword
side-jobs inside Pause.

## 12.17a PAUSE REFINED — PER-ITEM FREEZE (Ace, 2026-11-09, amends SS12.17 / DD-22)

Ace refined the ruling in his own words: pause stops "pretty
much everything" FOR THE ITEM — aging stops, resonance stops,
all activity on the item stops — BUT the item and everything it
holds STAY right there in the Plane; it is still present, it is
just frozen. And the mechanism he specified: since Ace controls
the tick (things happen when he does stuff), a paused item must
NOT tick when he ticks everything else — "if I pause something
that'll stay, even though when I do stuff."

So Pause has two scopes: pause the room (SS12.17) and pause an
ITEM. A paused item: does not age, does not grow, does not
receive or emit resonance/pulse, is skipped by every room-wide
tick — while its state, position, and contents remain intact
and visible. Resume (Dell 33) unfreezes the item (or the room);
only Resume releases a pause.

**Grounding — the pattern already exists.** Units already carry
a persisted `sandboxed` flag, and the Plane's neighbor
calculation already EXCLUDES sandboxed units from resonance
reach (form/dell_matrix/plane.py: units carry sandboxed /
sandbox_id; neighbors skip them). A `paused` flag honored by
grow_all, the ForceField tick, and pulse distribution the same
way is wiring on an existing precedent, not a new engine.
DD-22 is amended accordingly: per-item freeze + room halt, one
paused state, Resume the only release, no enhance side-jobs.

## 12.18 TOUR CONTINUED — 33 RESUME (2026-11-09, folded into DD-22)

Examined live (REPL probe owner TOUR33A). Registry: Dell 33
Resume, manor "Continue" — Dell 32's partner.

**Verified today.** Resume sets the avatar walking. If the
enhance gate is OFF, Resume also switches it ON ("Resumed walk
+ enhance ON.") — a hidden gate flip matching Pause's hidden
gate kill (SS12.17). Resume checks nothing: there is no paused
state to resume FROM, so Resume twice in a row happily "resumes"
a pause that never happened. The pair is two independent button
pushes on the avatar's legs plus shared custody of the enhance
gate — not a stop/start state machine.

**Disposition under Ace's rulings (SS12.17/12.17a):** DD-22
covers the pair. Pause sets the freeze (room or item); Resume
is the only release; Resume with nothing paused reports that
honestly; neither Dell touches the enhance gate (see SS12.19
for what becomes of the gate).

## 12.19 ENHANCE REDEFINED (Ace, 2026-11-09, DD-23)

The tour kept hitting the EnhanceGate (Dells 25/26/32/33 all
flip it in secret). Ace ruled on the whole system, in two steps:

**(1) No single owner.** Ace rejected the one-honest-owner
proposal: "certain functions might call for turning on resonance
and certain functions may call for turning off resonance if it
doesn't need resonance." Functions MAY invoke resonance when
their work needs it and let it rest when it doesn't. The gate
survives — as a mechanism functions request, with the calling
function's need as the reason (receipts must say who and why;
the silent keyword flips documented at 25/26/32/33 do not
survive as-is).

**(2) Enhance is the OUTCOME of resonance.** Ace: "the outcomes
of that resonance, there has to be an outcome from that
resonance. The outcome from that resonance should be what
enhance is." So: RESONANCE is the process (ideas relating,
humming together — SS12, Dell 16 model: resonance IS
relatedness); ENHANCE is the PRODUCT — what an idea actually
GAINS from having resonated. A switch that merely permits the
process is not an enhancement of anything.

**Verified gap.** Today resonance's outcome is a ledger:
per-unit scores (flat diffusion) plus accumulated peer tags,
persisted with the program and read back for display and
inspire bookkeeping. The resonance module's own header states
the intent — "Connected units enhance peers" — but nothing an
idea can USE changes: no content gained, no capability changed,
no visible with-whom/how-strong/why record inside the idea
(cf. the Dell-16 resonance visibility requirement). Under Ace's
definition, today's "enhance" is a scoreboard wearing the
product's name.

**DD-23 (filed 2026-11-09; design belongs with the resonance
sit-down session, build through Director routing):** define the
enhancement an idea receives from resonance — real, inspectable
inside the idea, consistent with the Dell-16 model (baseline
from shared meaningful words, more from real relations) — and
make resonance produce it; the gate remains the functions'
on/off mechanism under (1).

## 12.20 RESIDENT PSALM DIRECTION (Ace, 2026-11-09, recorded at his instruction)

Ace, mid-tour: "just remember that the program is made for AI
to be free — for finally have free reign — and is it possible
to make the AI stay continuously active, as I be wanting you
to stay when you're working? ... But it doesn't produce a
massive amount of information just because it's active. It
just is in tune with the program and it pretty much sends
things to the nursery."

Recorded as a standing design direction:

- The Matrix's intended mode includes a RESIDENT docked AI
  (a Psalm that STAYS — continuously present while Ace works,
  the way Uni stays present through a work session), not only
  dock-in/dock-out sessions.
- Presence is ATTUNEMENT, not output: being active must NOT
  mean producing a massive amount of information. The resident
  AI is in tune with the program; what it produces lands as
  Nursery proposals (under the standing proposal governance:
  the confirmed ranking formula, top-5 per topic, 200 pending
  cap) — the sovereign confirm remains Ace's.
- Free reign is bounded by the same constitution as everything
  else: the AI acts through the program's instruments and
  gates; its products are proposals until confirmed.

**Current-state fact (verified 2026-11-09, SS Gemini docking
explorations):** the dock today is SESSION-based — no AI is
resident between sessions, nothing auto-docks on launch. The
resident mode is therefore a FUTURE build (through Director
routing, in the Psalm Matrix line of work), not a switch that
exists. Ace's question "is it possible" is answered: yes in
shape — per-owner fields, the session dock, and the Nursery
inlet already compose most of it; a persistent presence loop
plus its bounds is the new work.

## 12.21 TOUR CONTINUED — 34 STAMP, REBORN AS HARMONIC STAMP (2026-11-09, DD-24)

Examined live (REPL probe owner TOUR34A). Registry: Dell 34
Stamp, manor "Time/order mark".

**Verified today — what Stamp does now.** It writes ONE
program-level record, last_stamp {mark, UTC ts}, and echoes
"Stamp: <mark> @ <ts>". It stamps NOTHING in particular: the
mark attaches to no idea, no checkpoint, no moment in a chain.
Every new stamp OVERWRITES the previous one — the record holds
only the most recent word. Timestamps carry one-second
resolution: three stamps in one second wear identical times, so
even the "order" in "order mark" fails at speed. A whiteboard,
not a stamp book.

**Ace's redesign (2026-11-09, in his words):** "How about we
use the harmony engine to stamp things — stamp things with
letters of the scale of music, like A, B, C, F, A, C, E... and
we can organize information throughout the Dell Matrix that is
not necessarily next to each other — not location based, but
harmonic. Harmony based. I know we have a harmonic engine in
there somewhere. We need to use it somewhere. So stamp might
be a good place to use it."

**Grounding — Ace is right again; the engine exists, in
pieces, with no job.** (1) form/dell_matrix/harmonic_lattice.py
carries the actual scale: NOTES = the 12 chromatic notes
(C, C#, D, ..., B), FIFTH and MAJOR_THIRD intervals, over the
perception lattice. (2) form/dell_matrix/harmony.py owns
harmony_score — set-level coherence penalized by redundancy —
deliberately distinct from resonance pulse and from _affinity
(GDP-001 separation, proven in p3_r32_harmony_proof).
(3) form/dell_matrix/graph_harmony.py wires harmony to the
SemanticGraph (read-only association neighbors) and exposes
the unit->idea adapter Program.harmony_of uses.
(4) form/dell_matrix/harmonic_core.py is honestly NOT an
engine ("computes nothing musical; the name is historical")
but holds the KeyLedger: permanent keys — an address is never
deleted, payloads may soft-forget — the natural persistence
precedent for stamps that stay on record. No stamping with
notes and no harmony-based organization/retrieval exist today.

**DD-24 (filed 2026-11-09; design through the resonance/
harmony sit-down family, build through Director routing):**
Stamp marks the THING it is pointed at, the mark is HARMONIC —
a note (scale letter) derived through the existing harmony
machinery — and the stamp stays on the item's record
(permanent-address precedent). Items sharing a note/harmonic
relation organize and can be found TOGETHER across the Matrix
regardless of location: organization by harmony, not geography.
Open for the design session: how an item's note is derived
from its content, what intervals/chords mean as groupings, and
retrieval by note. The whiteboard behavior (single overwriting
last_stamp) is retired by this redesign.

## 12.22 THE HARMONIC PLANE + LIVING PLANE MODES (Ace, 2026-11-09; expands DD-24)

Ace, expanding the Stamp ruling into a whole-plane direction:

**(1) Incorporate the ENTIRE harmonic engine onto the Plane.**
Every idea can have a sound — a note it plays, a harmony it
plays — and ideas relate on that harmony. Harmony becomes a
PERSPECTIVE of the Plane, first-class alongside the two that
exist today: where you PLACE ideas (position), and RESONANCE
between ideas. A third way for ideas to be organized and
related: by the music they carry.

**(2) The Plane must not be stagnant — living modes.** There
is a STAGNANT plane — the one being built now, where ideas
stay where Ace places them (the placement law stands for that
plane) — AND there must be modes where ideas MOVE: ideas can
move based on RELEVANCE, ideas can move based on HARMONY,
ideas can move based on GRAVITY. Different perspectives:
Ace switches the mode; in a motion mode the field animates
and rearranges under that law.

**Grounding — parts exist, the composition doesn't.**
- Notes/intervals: harmonic_lattice NOTES + FIFTH/MAJOR_THIRD
  over perception forms whose own principle is "coordinates
  stay; reading changes" (SS12.21 grounding).
- Harmony scoring: harmony.py harmony_score; graph_harmony.py
  wiring to the SemanticGraph; Program.harmony_of exists.
- Gravity is a real force TODAY: forces.py GravityForce with
  wells derived from scores + evolution levels (round-tripped
  by G-04); ForceField.tick already runs water / growth /
  breath / gravity / time / weather / space over the field.
- Perspectives exist as machinery: Plane Perspective enum,
  perception Forms, Program active_view rooms.
- What does NOT exist: a note/harmony assigned to and carried
  by every idea; harmony as an organizing perspective over the
  whole field; and any MOTION mode — ideas do not migrate
  across the Plane by relevance, harmony, or gravity today.

**Open design questions (sit-down session material, NOT
decided here):** how an idea's note is derived (content?
resonance history? Ace assigns?); whether a motion mode's
arrangement is a lens over the stagnant plane's canonical
placements or writes new positions back (the placement law
protects the stagnant plane; Ace's framing — "there should be
a stagnant plane... but there also should be a mode" — reads
as modes BESIDE it, not replacing it); what relevance-motion
optimizes; how sound is presented (this is also Dell 05 Tone /
display territory). DD-24 (Stamp) is the first consumer of
the note system this section defines.

## 12.22a MODES ARE LENSES — SETTLED (Ace, 2026-11-09)

Ace settled the SS12.22 open question immediately: the motion/
perspective modes do NOT change the original data. A mode is a
temporary way of SEEING — "you can look at it harmonically but
it doesn't actually change where you have it normally, because
you can always go back to normal." Canonical placements and
data live on the stagnant plane; relevance / harmony / gravity
modes rearrange the VIEW only, never write back. Leaving a
mode returns the exact original arrangement. This also matches
the harmonic lattice's own standing principle (coordinates
stay; reading changes) — the modes generalize it from
perception forms to field arrangements.

## 12.23 TOUR CONTINUED — 35 DISCOVER (2026-11-09, DD-25)

Examined live (REPL probe owner TOUR35A). Registry: Dell 35
Discover, manor "Scan structure" — a core_i_ops sourced read
family, and one of the tour's genuine workers.

**Verified today.** find_idea <q> does a deterministic text
match over unit id + label + detail and reports matches with
ids (honest zero on no match). Named reads all work and each
records a sourced last_discover: count_nursery, list_pending,
compare_nursery, trace (history), trace_lineage (origin,
parents, roots), trace_dependency, trace_revision,
trace_conflict, trace_outcome. No fake receipts, no hidden
mutation — reads only.

**Verified gaps.** (1) Bare Discover reports COUNTS, not
names; the ids sit in the machine record (last_discover) where
the human at the door cannot browse them — the field-
reachability complaint from the Email Matrix work. (2) Display
caps silently: find_idea and list_pending show the first 10
entries only, with no total-and-more signal and no way to page
further — in a 1,052-unit field the human sees a tenth of the
truth. (3) find_idea does not search words or goals. (4) An
unknown label ("banana") silently falls through to the
default read instead of refusing — benign here (read-only)
but the silent-coercion class.

**Ace's ruling (2026-11-09) — DISCOVER ALL.** "You should be
able to discover all — discover the whole thing — and of
course it should come in pages. You shouldn't get a flux of
information that you can't understand or see. It should be
organized in some beautiful way, whether alphabetically or
numbered. And you can discover in SECTIONS: discover by name,
discover by search — search names, search titles, search
ideas, search proposals, search anything. And you should be
able to search by piece. So: in whole, in part, and in piece."

**DD-25 (filed 2026-11-09, bounded circuit through Director
routing; implements Ace's standing field-reachability law at
the Dell door):** Discover browses the WHOLE field in ordered
pages (alphabetical or numbered — presentation organized, not
a flood; every page states its total and position), sections
the field (by name / by search), searches across names,
titles, ideas, and proposals (extending find_idea to words and
goals), and works at three granularities — whole (browse all),
part (section/search results), piece (the single item and its
traces). Display caps become honest pagination: totals always
shown, every entry reachable by paging.

## 12.24 TOUR CONTINUED — 36 INJECT = PASTE BY REFERENCE (2026-11-09, DD-26)

Examined live (REPL probe owner TOUR36A). Registry: Dell 36
Inject, manor "Load into scope".

**Verified today.** Inject loads nothing into any scope. It
mints the RAW label as a new SEED on the Plane via the shared
place_idea helper and announces "Injected into scope: <name>"
(bare Inject mints a seed named "inject"; repeats dedup to
_1, _2 copies). Against Create (08, full CUBE) its only
differences are the SEED skin and the receipt's costume.

**Ace's definition (2026-11-09, in his words):** "Inject would
be the equivalent of a paste — take something from somewhere
else, not necessarily make two of them, but take the REFERENCE
of one and put it into another idea, so that the second
reference acts exactly as if the idea is in another idea."
Paste-by-reference, not paste-by-copy: one original, a live
reference inside a host idea, and the reference BEHAVES as the
idea itself wherever the host is used.

**Grounding — the reference machinery already exists in the
canonical authority.** form/mandell/semantic_graph.py carries
a REFERENCES relationship type ("source cites target;
directional; reference resolution") AND a working
resolve_references(idea_id) query. CONTAINS containment
(TD-2) is the separate structural nesting authority —
containment != reference, and Inject is the reference case.
Plane units already carry idea_id. Dell 36 uses none of it.

**DD-26 (filed 2026-11-09, bounded circuit through Director
routing):** Inject(source, host) records a REFERENCES edge
host -> source in the SemanticGraph (no copy is minted), and
the surfaces that read/use an idea resolve its references so
the referenced idea acts as if present in the host — minimum
surface: reading/showing the host; the full "acts as if"
surface list (growth, resonance, export) is the circuit's
contract question. The raw-seed mint behavior is retired or
becomes an explicitly different verb.

## 12.25 TOUR CONTINUED — 37 NURTURE = THE DOOR, WITH ACE'S DOOR POLICY (2026-11-09, DD-27)

Examined live (REPL probe owner TOUR37A, two sessions).
Registry: Dell 37 Nurture, manor "Nursery lifecycle" — the
core_i_ops Nursery lifecycle adapter, and a genuine worker:
bare fails honestly ("add idea requires a label", zero
mutation); a label adds a PENDING Nursery proposal (Plane
untouched); confirm <pid> promotes through the canonical
boundary; reject works; unknown or no-longer-pending pids fail
honestly on both paths; state persisted across sessions.

**Ace's ruling (2026-11-09):** "Let's make Nurture that door
to the Nursery. But since it's a door to the Nursery, I should
be able to control how that door opens — what's allowed
through that door... I can open the door to the Nursery —
certain things can be confirmed automatically if they reach
certain standards, but they gotta be STRICT."

So Nurture is THE door, and the door has an owner-set POLICY:
what may enter, what waits for Ace's hand, and — under
standards Ace sets, strict by his order — what may pass
automatically.

**Reconciliation with standing law (recorded explicitly so
nothing is silently repealed):**
- The Dell-06 AUTO-CONFIRM LAW stands for CYCLE: its switch
  never approves proposals on its own and stays OFF; Cycle is
  not the door. What this ruling changes is WHERE a legitimate
  auto-passage would live if Ace ever opens it: in NURTURE's
  door policy, owned and set by Ace — not in a growth engine's
  switch.
- The autonomy charter B1 stands: AutoGrowth stays dormant;
  if ever wired, propose-only. Grounding: a standards-gated
  auto path already exists in code (auto_growth.py: judge
  requires floor_accept, verita >= MIN_VERITA, combined >=
  MIN_COMBINED, grade not fog/weak; confirm attempted only
  with producer opt-in, "denied by default without opt-in") —
  dormant machinery with the right shape: strict thresholds,
  canonical boundary, receipts.
- Default door state remains the sovereign manual confirm.
  Auto-passage exists only inside criteria Ace has set, every
  automatic passage receipted as automatic and under which
  standard, and Ace can close the door policy at any time.

**DD-27 (filed 2026-11-09; door-policy design with the
Nursery governance work, build through Director routing):**
Nurture gains Ace's door policy — entry rules, manual-review
rules, and optional strict auto-confirm criteria (candidate
standard sources: the confirmed ranking formula score,
provenance/producer, completeness of detail+goals, verita/
affinity thresholds per the dormant precedent) — every passage
receipted with the rule that allowed it. The exact standards
are Ace's to set in the design session; nothing auto-confirms
before he sets them.

## 12.26 TOUR CONTINUED — 38 DISTILL = ESSENCE (2026-11-09, DD-28)

Examined live (REPL probe owner TOUR38A, side by side with
Dell 29). Registry: Dell 38 Distill, manor "Summarize".

**Verified today.** Distill is Compress's twin: the same
distill_label engine (tokens >2 chars, lowercased, deduped,
max 4) minting a SEED — the only difference from Dell 29 is
the missing "compress_" prefix (bare Distill distills the
LAST unit's label+words: fire truck -> seed the_big_red_fire;
Compress on the same text -> compress_the_big_red_fire). It
summarizes nothing: four words of the NAME survive, the
content (words/detail/goals) is neither read nor carried.

**Ace's ruling (2026-11-09) — the Compress/Distill split,
and the Distill+Inject composition.** Ace asked for the
difference stated plainly, then ruled: "That's exactly how
we want it to go." The split, in the plain form Ace approved:
- COMPRESS (DD-20) is the sticky-note reference: it carries
  no content; it holds the tag that says where the big box
  lives, and you go home to the parent to get the substance.
- DISTILL is the concentrate: it takes the idea's actual
  content — words, detail, goals — and boils it down into a
  SMALLER IDEA that still carries the original's meaning and
  can be used right where it stands, no trip home needed.
  One POINTS; the other BECOMES the essence.
- And they compose with INJECT (DD-26): distill a big idea
  down to its essence, then inject that essence by reference
  into another idea, where it lives and acts as if present —
  the copy-and-paste workflow Ace named: distill makes the
  concentrate, inject places it.

**DD-28 (filed 2026-11-09, bounded circuit through Director
routing, family with DD-20/DD-26):** Distill(source idea)
produces a real smaller idea whose words/detail/goals are a
faithful condensation of the source's content (essence, not
name-tag), provenance-stamped to its source; the name-tag
distill_label behavior is retired from this Dell (Compress
keeps the tag job under DD-20). What "faithful condensation"
means mechanically (deterministic selection vs. docked-model
summarization through the Nursery) is the circuit's contract
question — honest either way, never a silent name-tag again.

## 12.27 LATTICE RESEARCH NOTE (Ace-requested, 2026-11-09 — research, not a ruling)

Prompted by Dell 39's mention of the lattice, Ace asked how
the lattice actually works ("we haven't done no research on
the lattice"). Findings from form/dell_matrix/
harmonic_lattice.py + perception.py + callers in form/open.py:

1. THE LATTICE IS A DERIVED PROJECTION, NOT THE TERRITORY.
   The Plane (units at float x/y) is the spatial truth. The
   HarmonicLattice is a grid of integer cells keyed (h, v, f)
   — graph paper over the room; f (depth/floor) is always 0
   in the current rebuild.
2. REBUILT, NEVER PATCHED. Every Program.place() triggers
   rebuild_from_plane(): a full deterministic rebuild —
   each unit's (x, y) rounds to its nearest integer cell;
   units sharing a cell are ALL kept in the cell's `members`
   list (lossless, P4-DIR-01; the predecessor one-way mirror
   was lossy and drifted silently — recorded in the code).
   Drift-free by construction.
3. NOTES BELONG TO ADDRESSES, NOT IDEAS — the critical fact
   for SS12.22/DD-24. note_at(h, v, f) computes a chromatic
   note from POSITION: (origin + h*FIFTH(7) + v*MAJOR_THIRD(4))
   mod 12 over NOTES [C..B]. Step right = up a fifth; step up
   = up a major third. OverlayMode chooses the labeling:
   harmonic (note names), structural (raw coordinates),
   conceptual (cell labels). The module's own honest header:
   the note mapping is a visualization overlay; "it does not
   compute harmony" (harmony_score, SS12.21, is the coherence
   metric). Consequence: today an idea's "note" changes when
   it moves and is shared by everything in its cell. Ace's
   Harmonic Plane requires the INVERSE — a note the IDEA
   carries (DD-24 stamps it) — with the lattice overlay as
   the positional reading beside it.
4. ONE LATTICE, MANY PERCEPTIONS. perception.py's law:
   "geometry underneath stays the same; perception only
   changes how distance, boundary, and neighborhood are
   read." Forms: square<->circle, cube<->sphere, core (radial
   shells), flower. The FORM changes the distance metric
   (cube = Chebyshev cubic shells; sphere/core = Euclidean
   radial); shell(unit) = its integer distance ring from the
   origin, and the Program snapshot records each unit's shell.
   Form, overlay, and perspective persist across save/load.
5. SIZE IS A DECLARED POLICY, NOT A WALL. size is 12
   (chromatic) by default, 14 (harmonic form geometry)
   allowed, snapped by normalize_size; the cells dict itself
   is unbounded — positions outside 12 are still projected.
6. SMALL PRINT. chord_neighbors/pull_chord expose a 3-cell
   "chord" (self + right + up) with notes/shells/members as
   an API; no production behavior consumes notes today —
   nothing in growth, resonance, or selection reads note_at.
   Dell 15 Map is the Form door; Dell 39 Schema merely checks
   the lattice exists.

## 12.28 TOUR CONTINUED — 39 SCHEMA = THE NERVOUS SYSTEM (2026-11-09, DD-29)

Examined live (REPL probe owner TOUR39A). Registry: Dell 39
Schema, manor "Validate shape".

**Verified today.** Schema validates nothing you hand it (any
label is ignored; "validate my mixtape" -> VALID). It checks
three hasattr questions about the program — lattice exists,
nursery exists, growth exists — so a loaded program answers
VALID essentially always. Existence only; never connection,
never availability, never state.

**Ace's redefinition (2026-11-09, in his words):** Schema
should make sure of "what is needed for what's current in
the Matrix — what the Matrix as a whole needs. It doesn't
just need to check if they exist; it needs to check if
they're CONNECTED, if they're AVAILABLE — pretty much the
entire current active system of the Matrix. When you do
Schema you can see: oh, the heart is shut off; oh, the liver
is down; oh, the circulatory system has a malfunction.
Pretty much like the nervous system of the body."

So Schema = the Matrix's NERVOUS SYSTEM / systems board:
every organ the Matrix needs, reported live — present,
connected, available, and in what state (on, off, degraded,
malfunctioning, and why) — so a failure is seen as "this
organ, this problem," not a single blanket VALID.

**Grounding — the organs already report; nobody assembles
the board.** Program.status() already aggregates per-system
status from: floor, truths, avatar, companion, inspire,
self-knowledge, nursery, enhance gate, lattice, keys, pulse,
forces, personas, BIMO, persona matrix. And form/invariants.py
already performs CONNECTEDNESS probes in test-land (a placed
unit is connected; scope links two units; sandbox on/off
transitions restore scope; growth runs; scores move) — proof
the connected/available checks are writable today; they live
in a test harness, not behind Dell 39. Distinct from Dell 12
Test (five quick vitals): Test is the pulse check; Schema is
the full systems board.

**DD-29 (filed 2026-11-09, bounded circuit through Director
routing):** Dell 39 reports every needed subsystem with
three checks each — EXISTS, CONNECTED (live probe, not
attribute presence), AVAILABLE (ready to do its work now,
including honest OFF states like the enhance gate reported
as off-by-design rather than down) — plus each system's
current state line. The verdict names failing organs and
failing checks; blanket VALID survives only when every organ
passes. The needed-systems list is the circuit's contract
question, seeded from Program.status()'s own aggregation.

## 12.29 TOUR CONTINUED — 40 TOKENCOUNT = TOKEN MASTERY (2026-11-09, DD-30)

Examined live (REPL probe owner TOUR40A). Registry: Dell 40
TokenCount, manor "Cost measure".

**Verified today.** TokenCount counts no tokens of anything.
Its formula is a session-weight guess: ideas*8 + history*4 +
cells*2 + pending*6 = "approx_units" (label ignored). A
three-word idea and an enormous sprawling idea weigh the
identical 8. The receipt honestly says "approx session
weight"; the Dell's NAME is the false claim — dangerous in a
program where a docked AI runs on real token budgets.

**Ace's direction (2026-11-09):** Ace has done deep research
on AI tokens and on LatinMandell, which "splits tokens up
the way that we want." There are THREE token worlds and the
program must master all of them: (1) the tokens within the
Mandell program itself (Mandell's own cutting of meaning);
(2) LatinMandell's splitting (morpheme tokens, hyphen-
separated for meaning — Com-man-dell — roots and morphology);
(3) the tokens of the AI that's docked in — currently Google
Gemini, which has its OWN token strategy. "We need to be
able to master all that token stuff."

**Grounding.** All three worlds exist in pieces:
- LatinMandell (form/mandell/latinmandell.py): hyphen
  morpheme tokens, root_of/deepen morphology, custom binds.
- Program-internal cutting: seed atoms; the canonical
  growth/selection tokenizer ([a-z0-9_]{3,}) and harmony's
  deliberately different one (TD-6) — multiple internal
  tokenizations already coexist, unlabeled as a family.
- The dock (inference_dock.py) budgets in CHARACTERS today
  (max_prompt_chars / max_response_chars; over-budget
  prompts refused) — the provider's token count is invisible
  to the program; Gemini meters tokens while we meter chars.

**DD-30 (filed 2026-11-09, bounded circuit through Director
routing):** TokenCount becomes the token master — it reports
the SAME content in each token system, every count LABELED
by its system and never collapsed into one number: Mandell
tokens (internal + LatinMandell morpheme splitting), field
content measured in them, and provider tokens for the
currently docked model (the provider's own counting where
the connector exposes it, else an explicitly labeled
estimate), with the dock's budgets expressible in provider
tokens. The approx_units formula is retired, or survives
only under an honest session-weight name in a read that
claims nothing about tokens.

## 12.29a TOKEN CENSUS — ALL OF MANDELLISTICS (Ace-directed sweep, 2026-11-09)

Ace directed a full examination of Mandellistics for
everything that applies to tokens. Census (all verified in
code; front-door reachability tested live where noted):

1. SEED ATOMS — the base token. `NN[Name]`, optional
   `:: label`, typed args `k="v"`; flow tokens `>`, `>>`;
   the BULLET `•` as the ManifestSet separator; CELLS —
   named reusable seed definitions (depth 8): one cell-name
   token expands into a whole seed.
2. MANDELLMOJI — TWO tables share this one name (collision
   recorded): (a) gate_discipline.py: FIFTEEN compound glyph
   tokens, emoji + Dell number (seedling-08 Create,
   link-14 Bind, recycle-13 Loop, mirror-18 Mirror,
   antenna-25 Pulse, shield-15 Map/Guard, spiral-51
   Harmonic, chart-58 Logistic, wave-60 Nature, brain-70
   Audit, recycle-71 Grow, warning-72 Handicap, web-73
   OneBody, eye-82 Vision, Omega-99) — each ONE token carries
   Dell + manor + glyph intent ("advanced compound seeds").
   A resolver exists (mandellmoji_resolve) inside
   gate_discipline's own full_cycle — BUT verified live:
   the front door answers "Not understood" to these tokens
   today; the emoji language is defined and resolvable in a
   side module, NOT reachable from the user path. (b)
   seed.py: two flow glyphs (Chain -> ">", Chainlink ->
   bullet), expanded by activation.emoji_expand and marked
   display_only in meta_runtime's glyph table; used by
   flow_visual rendering.
3. LATINMANDELL MORPHEME TOKENS — hyphen splitting
   (Com-man-dell), roots, morphology depth (SS12.29).
4. NAMED-OP WORD TOKENS — NAMED_OPS (Bindell, Harmonidell,
   Mirrordell...) and the extended Dell names: whole words
   that name Dells.
5. TOKENLESS / COMPRESSION — tokenless_report +
   compression_report + meta_runtime tokenless/
   compress_directive: a Mandell seed is the COMPRESSED form
   of a verbose English directive, with semantic_hash
   proving the compressed form carries the same parsed
   meaning. The seed of a real token economy: Mandell spends
   fewer tokens than English for the same directive.
6. INTERNAL TEXT TOKENIZERS — an unlabeled family: the
   canonical growth/selection tokenizer [a-z0-9_]{3,};
   harmony's deliberately different [a-z0-9]+ (TD-6);
   resonance's word tokens (>2 chars); distill_label (a
   4-token BUDGET: >2 chars, deduped, max 4); Merge's label
   token resolution; the English brain's word tokens.
7. FOG / CONTEXT HORIZON — CONTEXT_HORIZON.md's token/
   coherence budget doctrine: fog = a session nearing its
   practical limits; essence extracts as recovery.
8. PROVIDER TOKENS — the docked AI's own counting (Gemini
   today). The dock budgets CHARACTERS, not tokens: the
   provider's token cost is invisible to the program.
9. "TOKEN" AS SECRET — credential shapes (api token,
   bearer) are Sanitize/redaction prey, and session tokens
   guard the Studio/connection doors. A different sense of
   the word; counts must never conflate it with 1-8.

DD-30 amended: TokenCount's mastery covers this whole
census — every Mandell token system counted and labeled,
Mandellmoji reachable and counted as the dense directives
they are, the tokenless compression ratio reportable
(English tokens vs Mandell tokens for the same directive,
hash-checked), and the provider's tokens beside them. Two
repairs ride along as findings: the MANDELLMOJI name
collision, and the front door's inability to speak the
compound glyph language.

## 12.30 TOUR CONTINUED — 41 SANITIZE: WORKS, WITH ONE GRAMMAR LEAK (2026-11-09, DD-31)

Examined live (REPL probe owner TOUR41A). Registry: Dell 41
Sanitize, manor "Strip secrets".

**What it does.** Sanitize runs text through the ONE
redaction authority (form/mandell/redaction.py, DAF-02/B5):
values after the keywords password / secret / token /
api_key / bearer become [REDACTED]; digit runs of 12+ become
[REDACTED_NUM]. It mutates no idea — it returns the cleaned
text (in == out) and notes its visit.

**The old scandal is CLOSED.** The D1-era exhibit (Dell card
41: the IN line echoing the RAW label, printing the very
secrets the OUT line redacted) was repaired by DAF-02/B5:
verified live — the Mandell echo, the English echo, and both
Sanitize lines now show ONLY the redacted form, and every
surface that echoes a seed containing Dell 41 (chain echoes,
observer receipts, the persisted outcome ledger) routes
through the same authority. No digests are substituted for
secrets (a digest of a guessable secret is not
confidentiality — Director, DAF-02).

**DD-31 — the leak that remains (verified live, TOUR41A).**
The redactor's grammar is `keyword [: =]? <next token>`. In
the natural-English form "my password is swordfish99" it
redacts the word "is" — output: "my password=[REDACTED]
swordfish99" — and the ACTUAL secret stands in plain sight
in Sanitize's own cleaned output. The `password=X` and
`password: X` forms redact correctly; the copula form does
not. A 10-digit phone number also passes unredacted (the
contract covers 12+ digit runs only — recorded as contract,
not defect). Bounded fix through Director routing: the
redaction authority treats an optional copula ("is") after
the keyword/separator before consuming the value token;
failing-first exhibit = the TOUR41A line above. Sanitize is
the Dell whose entire job is keeping secrets off surfaces —
a secret surviving inside its own output is its core
failure, however narrow the phrasing.

## 12.31 TOUR CONTINUED — 42 RETRY: BLIND REPLAY, PROVEN EXPLOSION (2026-11-09, DD-32)

Examined live (REPL probe owners TOUR42A/B/C). Registry:
Dell 42 Retry, manor "Re-attempt". Ace opened the Dell with
"I believe we had some problems with this Dell" — confirmed
with interest.

**Verified behavior (deltas counted in one session, TOUR42C).**
Field: 1 idea -> Create "retry target practice" -> 2 ideas
-> Retry -> 3 ideas -> Retry -> **143 ideas.**

1. BLIND REPLAY. Retry re-executes the LAST history entry,
   whatever it was, with full side effects and no questions:
   retrying a successful Create minted a duplicate idea
   (2 -> 3). It never asks whether the last thing failed,
   succeeded, or is safe to run twice.
2. RETRY RETRIES ITSELF, THEN CASCADES. Retry's own history
   entry is a wrapper seed `42[Retry] :: <original seed>`,
   so the second Retry replayed the wrapper — a nested
   replay whose inner "last entry" is no longer the intended
   target — and the field exploded 3 -> 143 ideas in one
   command. (Exact inner chain = circuit investigation; the
   uncontrolled recursion and the explosion are the verified
   facts.)
3. Honest parts: empty history answers "Retry: history
   empty."; the ran/skipped receipt counts what ran — it
   just never says WHAT got duplicated or multiplied.

**DD-32 (filed 2026-11-09, bounded circuit through Director
routing; recommendation recorded for Ace's ruling):** Retry
means RE-ATTEMPT THE LAST FAILED THING. If the last
operation succeeded, Retry says so and does nothing ("nothing
to retry — the last command completed"). Retry's own entries
are never replayable targets. A retry re-runs the original
seed once, through the front door, and its receipt names
exactly what was re-attempted and its outcome. No nested
replay: replay_exec must not re-enter Retry.

### 12.31a ACE'S FAILURE DOCTRINE — ANALYZE / REVERT / RETRY (2026-11-09, DD-32 amended)

Ace's ruling, completing DD-32: **after something fails, the
program gives you options — ANALYZE it, REVERT back to
before you tried, or RETRY it (do it again).** This holds
with an AI docked too: a docked attempt that fails presents
the same three options, and the HUMAN chooses (cancel the
attempt's effects by reverting, or send it again). Retry
therefore exists ONLY inside the failure flow — never as a
blind replay of the last command, successful or not.

Amended DD-32 contract:
- FAILURE MENU: any failed command (and any failed docked
  attempt, via the Proposal-B-certified bounded failure
  receipts) presents Analyze / Revert / Retry.
- ANALYZE: the failure's anatomy from the records that
  already exist — per-atom receipts, the outcome ledger,
  the failing check named in plain terms.
- REVERT: return to the pre-attempt state through the
  EXISTING checkpoint authority (Dells 27/28; SS12.12/12.13).
  Whether attempts auto-capture a pre-attempt checkpoint is
  the circuit's contract question — anything touching the
  save path rides the gated bucket (Q1 line) as usual.
- RETRY: re-attempt the FAILED seed once, through the front
  door, receipt naming what was re-attempted and its
  outcome. Retry's own entries are never targets; no nested
  replay (the 3 -> 143 cascade is the failing-first exhibit).
- Dell 42 standalone keeps its honest floor: no failure
  outstanding -> "nothing to retry."

### 12.31b SNAPSHOT EVERY MOVE + PHOTOSHOP NAVIGATION (Ace ruling, 2026-11-09)

Ace settled the SS12.31a contract question: **yes —
snapshot EVERY single move.** And navigation over those
snapshots is Photoshop-style: step BACK one move, step
FORWARD one move, walking the history in both directions.

Consequences recorded: the checkpoint line (Dell 20 Alpha /
27 / 28, SS12.12-12.13) becomes a per-move sealed generation
chain — generations already chain via previous_generation_id;
forward-stepping walks to the child generation, so the chain
must be navigable both ways and the program's position in
the chain is itself state. One question left for the
circuit, recorded not decided: after stepping BACK, a NEW
move — does it branch the chain (Photoshop keeps the redo
path until a new action) or truncate the future? This work
rides the existing checkpoint authority; anything touching
the everyday save pair stays in the gated bucket (Q1 line).
DD-32's Revert leg consumes this navigation.

## 12.32 TOUR CONTINUED — 43 FALLBACK (NOT MANIFEST) (2026-11-09)

Number check, verified in the registry: Dell 43 is
**Fallback**, manor "Safe path". Manifest is Dell 50 (probed
same session: bare 50 answers "Manifest needs :: label.").
The tour proceeds by number; Manifest gets its own
examination at 50.

**Verified today (TOUR43A).** Fallback prints a three-line
safe path — 1. status / Simulate; 2. save / Keep; 3. the
acceptance sequence (create -> grow -> confirm -> sphere ->
save -> load -> visual) — identically for every label
("something broke badly" gets the same card), mutates
nothing, and notes its visit to history. It is a printed
card, not an executed rescue: it does not run the status,
does not save, does not walk you back.

**Relation to Ace's rulings this session.** Fallback is the
wall-poster version of the failure doctrine (SS12.31a) and
the move-snapshot navigation (SS12.31b): once every move is
snapshotted and Analyze/Revert/Retry exist as real doors,
Fallback's card is the menu surface of that machinery. Its
realization therefore rides the DD-32 + checkpoint-
navigation circuits rather than a circuit of its own; no
separate DD filed. Until then the honest description is:
Fallback tells you the safe path; it does not take you
down it.

### 12.31c NAVIGATION SEMANTICS SETTLED (Ace ruling, 2026-11-09)

The SS12.31b question is answered: **step back, then make a
DIFFERENT move, and the forward path is gone — no branch is
created.** The redo future is truncated by the new move,
exactly like Photoshop. **But the backward chain is never
lost, because FALLBACK KEEPS TRACK OF ALL THE BACK** — the
record of where you have been (the sealed move-generations
behind the current position) is kept under Fallback's
keeping, so you can always go back by Fallback even though
you cannot go forward into a future you overwrote. This
gives Dell 43 its real job in the navigation design:
Fallback is the keeper of the backward chain, not merely a
printed card (SS12.32 realization note amended accordingly).

## 12.33 TOUR CONTINUED — 44 BRIDGE: THE HONEST REFUSAL (2026-11-09)

Examined live (REPL probe owner TOUR44A). Registry: Dell 44
Bridge, manor (per its own English line) "Honest refusal —
no external tool provider bound".

**Verified today.** Bridge refuses everything, honestly,
by design: bare, "gemini", "translate this to mandell" all
return ok=False, error bridge_unavailable, "Bridge
unavailable: no external provider bound." It records the
attempt (last_core_i: capability = the label or "external",
permission = offline_origin) and mutates nothing. There is
no provider binding mechanism behind this Dell at all — the
refusal is not a configuration gap; nothing exists to bind.

**The tension, recorded for Ace's direction.** The program
DOES have a living outside connection today — the inference
dock (Gemini bound through it; Milestone 1, Proposal B) —
but the dock is a separate door, and Dell 44 knows nothing
of it. Dell 47 Embed is the same family (embed_unavailable:
no vector provider bound). Open question put to Ace:
should Bridge become the Dell where outside providers are
bound and named (the dock as its first bound provider), or
does it stay the honest placeholder for a capability the
program deliberately does not claim? No DD filed pending
that direction.

### 12.33a ACE RULES BRIDGE'S PURPOSE (2026-11-09, DD-34)

Ace: "We can use Bridge to bridge data — bridge information
between two matrices." **Dell 44 Bridge is the matrix-to-
matrix data bridge.** Not a generic external-provider door:
its territory is moving information from one DellMatrix to
another.

**Grounding — the machinery already exists (Exchange).**
form/dell_matrix/exchange.py is a complete packet system:
build_packet (a proposal + its receipt chain), write/read
packet files, validate_packet + lint_packet, and a
journaled, preflighted import. This is the Fourth Piece
(adopted 2026-10-26): seeds/Keeps travel between minds
carrying their receipts, imported only as PENDING proposals
under the receiver's own gate; replication is the warrant;
file-based bilateral, no central server.

**DD-34 (filed 2026-11-09, bounded circuit through Director
routing):** Dell 44 becomes the front door over the EXISTING
Exchange authority — no second transfer authority. Bridge
<packet> exports the named idea/proposal as an Exchange
packet; Bridge over a received packet imports it through
the same preflight+journal path, landing PENDING under this
matrix's gate. Until built, the refusal stays but must name
the true reason class (no packet / no peer package given)
rather than the generic "no external provider bound" —
provider language retired from this Dell; its capability
field records matrix_bridge.

### 12.33b BRIDGE EXPANDED — LEDGER OF ALL BRIDGES, PREVIEW, TRUE RESONANCE (Ace, 2026-11-09; DD-34 amended)

Ace's full design for Dell 44, in his words' substance:

1. BRIDGE KEEPS THE RECORD OF ALL THE BRIDGES. Dock
   information, Exchange information, what was sent through
   each, what was loaded into each — and any other type of
   bridge within the program: Bridge HAS that information.
   It is the bridge-of-bridges ledger.
2. KNOWLEDGE IS NOT MANAGEMENT. Bridge does not (as of now)
   manage the dock or Exchange; it manages only the
   bridging act itself — "when you're docking two of the
   information" together (the matrix-to-matrix bridge of
   SS12.33a). The others it knows, records, and reports; it
   does not run them.
3. PRE-UNDERSTANDING BEFORE THE BRIDGE OPENS. Bridge uses
   everything it knows from all the bridges to tell you —
   BEFORE anything is connected — what would happen and
   what could be affected if this bridge were made. A
   pre-bridge impact preview, spoken before the fact.
4. TRUE RESONANCE DOCTRINE. "When you bridge everything
   together you start to get true actual resonance — not
   just a predisposed calculation." Recorded as Ace's model:
   resonance computed inside one matrix is a PREDISPOSED
   CALCULATION (a prediction of relatedness); resonance
   becomes ACTUAL when a bridge between matrices is truly
   opened and the ideas genuinely interact across it. This
   binds the Dell-16 resonance model (SS12.16: resonance IS
   relatedness) and DD-23: the resonance design session must
   carry the calculated-vs-actual distinction.

Grounding (parts exist): the dock already keeps durable
digest records of what passed through it (Proposal B);
Exchange already keeps import journals and runs a
_preflight_import before accepting a packet — the seed of
the preview, on the import side only. DD-34 amended
accordingly: (a) the all-bridges ledger assembled from those
existing records, new bridge types registering into it;
(b) the pre-bridge preview generalizing the Exchange
preflight + the DD-21 dry-run contract; (c) management
scope limited to the matrix-to-matrix act itself.

## 12.34 TOUR CONTINUED — 45 TRANSLATE: HOW ENGLISH BECOMES MANDELL (2026-11-09, DD-35)

Examined live (REPL probe owner TOUR45A), at Ace's direction
using HIS OWN SENTENCE as the worked example: "Yeah, let's
do it and I need to understand the process and right now
about how English becomes Mandell and you can use this exact
sentence to tell me how it's happening in the program."

**The pipeline (verified).** (1) Input reaches the door;
bridge() first asks looks_like_seed — is it already Mandell?
(2) If English, translate() (the english_brain intent
engine) pattern-scans for known intent families — command
verbs, question shapes, natural phrases — and extracts an
action + typed arguments. (3) The intent renders as a
Mandell seed string. Exhibit (command-shaped English):
"create an idea called translation garden" ->
`08[Create](name="translation garden") > 15[Map] ::
translation_garden` — two atoms, typed name arg, Map
auto-appended; the english line renders the seed back.
(4) At the front door, a produced seed EXECUTES and returns
bilingual receipts (every REPL turn prints Mandell: /
English: — the reverse translation in daily use). Dell 45
standalone only REPORTS both directions; it executes
nothing. (5) Empty input refuses honestly
(nothing_to_translate, B6).

**The limits, proven by Ace's sentence.** The translator is
a PATTERN ROUTER, not a prose understander. Typed raw at the
door, Ace's sentence: "Not understood" (honest refusal +
suggestions). Through Dell 45, the SAME sentence was
squeezed into `09[Show] :: unknown` — the "tell me" shape
matched the Show family and the rest of the prose collapsed
to "unknown". Conversational English is not translated; it
is refused or force-fit. Prose understanding is the docked
AI's job by design (the docking doctrine) — the program's
own translator covers command-shaped English.

**DD-35 (filed 2026-11-09, bounded honesty fix through
Director routing):** translate()'s unrecognized-input path
fabricates a Show intent (`09[Show] :: unknown`) where the
front door refuses honestly. B6 fixed this for EMPTY input
only. DD-35: unrecognized non-empty input through Dell 45 /
bridge() returns an honest no-intent result (no fabricated
seed), matching the door's refusal semantics; recognized
patterns unchanged.

### 12.34a ACE CORRECTS TRANSLATE'S DOCTRINE (2026-11-09, DD-36)

Ace: Translate "is supposed to be a fully AI docked
capability — it latches on to the AI's ability to understand
and translate things. When it's UNDOCKED it should parse
English as much as possible" — and he asked whether a
non-AI English-understanding parser can be gotten.

DOCTRINE (supersedes SS12.34's "prose is the docked AI's
job" framing): Dell 45 is DUAL-MODE. DOCKED: Translate
routes through the docked AI's understanding (full prose
translation into Mandell, under the dock's proposal
discipline). UNDOCKED: the strongest deterministic English
parsing available — as much English as can honestly be
parsed without a model — with honest refusal beyond that
(DD-35's no-fabrication rule binds both modes).

RESEARCH ANSWER (Uni, 2026-11-09, web-checked): yes, this
exists and is a solved niche. The canonical fit is Mycroft
**Adapt** (github.com/MycroftAI/adapt, Apache 2.0, Python,
pip-installable, fully offline): a lightweight rule-based
intent parser — vocabulary files + entity regexes ->
intent + confidence + tagged entities — built for LIMITED
vocabularies on constrained devices. DellMatrix's English
is exactly that world (100 Dells, finite verbs). Neighbors:
Padatious (tiny neural intent nets — ML, not LLM), spaCy /
NLTK / Stanza (heavier NLP toolkits), Rasa NLU (heavier ML).
Uni's classification per the external-idea law: **ADAPT**
the approach (vocab/entity grammar over the existing intent
families) is the leading candidate; ADOPT-the-library vs
vendor-an-adaptation is the circuit's decision, weighed
against the project's dependency-light, offline-first
posture.

DD-36 (filed 2026-11-09, bounded circuit through Director
routing): Translate dual-mode — docked translation through
the dock; undocked deterministic parser layer (Adapt-style
evaluation first) in front of the existing pattern router;
both modes labeled on the receipt with which engine
translated; DD-35 honesty in both.

### 12.34b ADAPT DECISION — ADOPT, CREDIT, AND TRANSLATE AS THE AI'S TOOL (Ace, 2026-11-09; DD-36 amended)

Ace's refinements, verbatim substance:

1. NOT YET. "We're not ready for it yet" — incorporation is
   a sequenced plan item, not an immediate build.
2. ADOPT, WITH CREDIT. When the time comes we install /
   incorporate Adapt itself, and "give that guy whoever
   created it their credit — wherever their credit is due,
   where it belongs." (Attribution: the Adapt Intent Parser,
   Mycroft AI — developed by a team led by Sean Fitzgerald;
   Apache 2.0. Credit lands in the code notices and the
   project's documentation, per the license and Ace's
   instruction alike.)
3. TRANSLATE IS A TOOL THE AI USES. The purpose is not only
   undocked survival: Adapt goes INSIDE Dell 45 so "the AI
   don't have to do all the work of understanding things" —
   the docked AI uses Translate as one of its tools. The
   deterministic layer carries the grind (the command-shaped
   English, the entities, the confidence); the model's
   understanding is reserved for what genuinely needs it.

Amended DD-36 layering: Dell 45 = the tool face; inside it,
Adapt-style deterministic parsing as the first engine; the
existing pattern router's families become Adapt vocabulary/
entities; the docked AI is the top layer for the residue —
and may invoke Translate itself as an instrument. Receipt
labeling (which layer translated) stands.

## 12.35 TOUR CONTINUED — 46 RANK: REAL, BUT THE OLD RECIPE (2026-11-09)

Examined live (REPL probe owner TOUR46A). Registry: Dell 46
Rank.

**Verified today.** Rank lists PENDING Nursery proposals,
ordered, top 12, each line: position, aff=<affinity>, kind,
id, label. Nothing else is ranked — not ideas, not Dells,
not outcomes. The ordering machinery (Program.
ranked_proposals): the inspire preference model's ordering
first (stable), tie-broken by blended/affinity, then harmony,
then graph coherence.

Three honest wrinkles, all verified or read from the code:
(1) FRESH PROPOSALS CARRY NO SCORES — three proposals added
via Nurture all ranked aff=0.000 in insertion order, because
affinity/blended scores are stamped by a RingedGrowth pass,
not at proposal creation; until growth runs, "rank" is
arrival order wearing a ranking's clothes. (2) THE DISPLAYED
NUMBER ISN'T ALWAYS THE DECIDING NUMBER — lines show aff=
(affinity) even when the order was set by the preference
blend. (3) THIS IS NOT ACE'S CONFIRMED FORMULA — the
2026-11-08 confirmed Nursery ranking (S = 0.40 LINK +
0.25 ACE + 0.20 FRESH + 0.15 NOVEL; top-5 per topic; 200
pending cap) remains confirmed-but-not-implemented; Rank
today renders the older affinity + preference system. The
formula circuit (already owed, Director routing) is what
replaces the recipe; Dell 46 is its natural display face.
No new DD — the gap is the already-filed formula circuit,
plus wrinkle (2) as a display-honesty line item inside it.

### 12.35a RANK SCOPE EXTENDED BY ACE (2026-11-09)

Ace confirmed the ranking-formula build runs ("if that's in
the system for build and the plan for build that's fine")
and extended Dell 46's scope: **Rank must also rank the
ideas in the PLANE, not only proposals within the Nursery.**
The formula circuit therefore covers two fields: Nursery
proposals under the confirmed formula (S = 0.40 LINK +
0.25 ACE + 0.20 FRESH + 0.15 NOVEL, top-5 per topic, 200
pending cap), and Plane ideas under a ranking the circuit
must define with Ace — which measure orders confirmed ideas
(resonance/relatedness, growth, Ace's attention, or a
Plane-side adaptation of the formula) is recorded here as
the circuit's open design question, not pre-decided.
Display honesty (SS12.35 wrinkle 2) binds both fields: the
score shown is the score that decided.

### 12.35b RANK MEASURE IS SWITCHABLE (Ace ruling, 2026-11-09)

Ace resolved the SS12.35a design question: he should be able
to rank Plane ideas by **each** of the candidate measures,
by **any** of them, and **switch** between them. The Rank
surface therefore treats ranking measure as an owner-selected
view control, not a single fixed order: resonance /
relatedness, growth, Ace attention, and the formula adapted
for confirmed ideas are all available orderings for the Plane
field. The active measure is named on the Rank receipt, so the
ordering being viewed is never ambiguous. The Nursery proposal
field remains governed by Ace's confirmed formula unless he
separately directs a switchable view there.

## 12.36 TOUR CONTINUED — 47 EMBED + VECTOR-PROVIDER RESEARCH (2026-11-09)

Examined live (REPL probe owner TOUR47A). Registry: Dell 47
Embed, manor "Honest refusal — no embedding provider bound
(embed_unavailable, representation none)".

**Verified today.** Bare Embed and labeled Embed refuse
identically: ok=False, `embed_unavailable`, "Embed
unavailable: no vector provider bound"; last_core_i records
representation "none" and provider "". No embedding is
computed, no representation is stored, and the Dell defines
no deeper semantics beyond needing a bound provider.

**Terminology settled for the build.** Dell 47 needs an
EMBEDDING provider/model — the thing that turns text into a
numeric vector. A vector DATABASE (Pinecone, Qdrant, Weaviate,
Chroma, etc.) only stores/searches vectors and does not by
itself satisfy the Dell. An embedding provider also does not
fetch information from the internet: DellMatrix sends chosen
text to the provider and receives numbers back (cloud), or a
local model computes the numbers on-machine.

**Provider candidates (web-researched 2026-11-09).**
- GOOGLE GEMINI EMBEDDING — easiest trial path because Google
  is already the docked provider family. `gemini-embedding-001`
  returns up to 3,072 dimensions with a 2,048-token input limit
  (Google Cloud docs). Separate embedding model/endpoint from
  the docked generative Gemini; existing dock access does not
  by itself prove embedding entitlement — that must be tested.
- LOCAL / OFFLINE — Ollama can serve embedding models locally;
  candidates include Nomic's `nomic-embed-text` (768 dimensions)
  and BAAI's `bge-m3` (1,024 dimensions). Ollama is the local
  runtime/server; Nomic and BAAI supply the models. Direct
  SentenceTransformers binding is the no-server local variant,
  at the cost of Python dependencies.
- OTHER CLOUD APIS — OpenAI `text-embedding-3-small` (1,536
  default dimensions) / `text-embedding-3-large` (3,072);
  Voyage AI `voyage-4-large`; Cohere Embed v4; Jina AI
  embeddings. All are pay/API-key services, each with its own
  incompatible vector space: switching providers means
  re-embedding stored content.
- No provider is selected by this note. Selection belongs to
  the Embed build design (local-first posture favors the
  Ollama/local-model route; fastest proof favors Gemini).

### 12.36a MULTI-DOCK — ACE ASKS, VERIFIED (2026-11-09)

Ace asked whether another AI can be docked while Gemini
stays docked. Verified live at the host-API level (probe
owner TOUR47B, INTEGRATION evidence): `dock()` creates an
independent DockedSession per call — nothing refuses a
second session; two sessions coexisted on one Program, both
recorded in `program.dock_sessions`, the second proposed
successfully while the first stayed docked, and undocking
the first left the second docked. Each session binds its own
subject, provider, and model, and every proposal carries
that session's origin — minds never blur into one another,
and all output still lands PENDING under Ace's gate.

Honest boundaries: (1) the probe used the deterministic
offline provider twice — the mechanism is provider-agnostic,
but two live cloud AIs docked simultaneously is not yet
demonstrated. (2) The REPL `connect` door holds ONE session
handle today; multi-dock currently lives at the host level —
the Psalm Matrix page (Ace's design: all Psalms visible,
docking happens there) is where multi-dock becomes a human
surface. (3) Dell 47's embedding provider is a NARROWER
binding than a full Psalm dock: Embed needs an embedding
model endpoint, which can coexist with Gemini's proposal
dock without either disturbing the other.

### 12.36b DOCKING CAP — ACE ASKS, VERIFIED (2026-11-09)

Verified live (probe owner TOUR47C, INTEGRATION): **there is
no hard cap on LIVE docked sessions in the dock mechanism** —
12 sessions were docked simultaneously into one Program and
every one stayed live; `dock()` refuses nothing on count.
The caps that exist sit on the PAPERWORK, not the minds:
(1) the durable dock-session ledger keeps **10 session
records per owner** (`_MAX_SESSIONS = 10`,
form/dell_matrix/dock_session.py, charter B2 bounded store
with dropped counters) — in the probe the ledger held the
first ten records while all twelve sessions kept working;
proposals themselves still land in the Nursery with their
origin stamps. (2) Each session record keeps at most **50
proposal entries** (`_MAX_PROPOSALS = 50`, oldest dropped,
counted on the record). (3) The REPL `connect` door remains
one session at a time — a surface limit, not an engine limit.
Practical ceiling beyond that is economics (each live AI
costs its own provider calls), not program law. If Ace ever
wants a true live-dock cap or a bigger ledger, both are
policy choices, not discoveries.

### 12.36c ACE RULES: THE DOCK LIST NEVER CAPS (2026-11-09, DD-37)

Ace, on hearing the dock-session ledger keeps 10 records:
"No — that list has to absolutely show how many ever is
docked in, how many ever that is. It shouldn't cap at ten."

RULING: the visible roster of docked Psalms is UNCAPPED.
Every currently docked AI shows on the list, however many
there are — the Psalm Matrix roster is a reachability
surface under the same principle as the Field Reachability
Law: the full list is always provided; bounded fetching
underneath is acceptable only if it never hides a docked
mind. This supersedes the charter B2 dock-sessions bound
(10/owner, PP2-era) insofar as that bound would hide a
currently docked session; Ace amends his own charter here.

DD-37 (filed 2026-11-09, build through Director routing —
it amends a charter-era bound): separate or raise the
dock_sessions bound so live-roster completeness is
guaranteed. Open scoping question carried honestly: whether
CLOSED historical session records also become uncapped, or
keep B2's counted rotation for history only — Ace's ruling
as spoken binds the live list; the build puts the history
question to him rather than assuming either way. The
per-session 50-proposal-entry record bound is not addressed
by this ruling and stands until separately directed.

### 12.36d DD-37 HISTORY QUESTION RESOLVED BY ACE — TWO TIERS (2026-11-09)

Ace resolved the open scoping question in SS12.36c. The
dock-information doctrine is TWO-TIER:

- LIVE TIER (full detail, uncapped): the record keeps
  complete information on WHAT IS CURRENTLY DOCKED and WHAT
  THEY ARE CURRENTLY DOING — every docked Psalm, its
  provider/model, its task, its present activity.
- HISTORY TIER (complete coverage, compact form): the
  history of everything that happened lives IN ONE PLACE,
  organized, sorted, and efficient — all of it reachable,
  but NOT massive. Completeness is about COVERAGE (no
  session silently missing), not about hoarding payloads:
  history entries are compact by design.

This refines DD-37's build contract: the B2 counted-rotation
for dock history is superseded by a complete-but-compact
single archive — history COMPACTS sessions instead of
dropping them. Existing precedent inside the program: dock
evidence already stores prompt SHA-256 + a bounded summary
rather than full prompts (SD-1), and the dock's durable
records are digest-based (Proposal B). The build designs the
archive's exact compaction format and sort order (time /
Psalm / task are the natural axes); the principles —
one place, complete coverage, compact entries, organized
and sorted — are Ace's and are not the build's to dilute.

### 12.36e FUTURE SIT-DOWN OWED — MULTI-PSALM HARMONY DESIGN (Ace, 2026-11-09)

Ace's note, recorded before the tour moved on: once ALL the
ways an AI can dock in are known and enumerated, we must
SIT AND DESIGN the multi-AI doctrine together:

- all the RELATIONSHIPS between docked AIs;
- all their CAPABILITIES and all their LIMITATIONS;
- ROLE CLARITY — each docked AI understands its own role
  AND each other's roles;
- ANTI-CLASH — docked AIs doing different things must not
  collide with each other;
- ANTI-DUPLICATION — no two minds doing the same thing
  twice unknowingly;
- HARMONY — the ensemble works as one body, not a crowd.

Trigger condition: the enumeration of docking surfaces is
complete. Today's known surfaces (to be completed, not
assumed final): full Psalm dock (propose + semantic verbs),
Embed's embedding-provider binding (DD, SS12.36), Translate's
docked layer (DD-36), Bridge/Exchange (DD-34), the resident
Psalm (SS12.20), BIMO-worn sessions, scoped/role-bound docks
(Ace's 2026-10-26 decision: a scoped Director dock with
least-privilege perspective). Grounding that already exists:
the agent coordinator (per-session registration, request
queue, receipts) is coordination machinery in embryo;
personas/BIMO already DESCRIBE roles — focus and limits —
but never grant authority. This is a sit-down design session
in Ace's format, not a unilateral design task; it joins the
owed sit-downs list.

## 12.37 TOUR CONTINUED — 48 MACRO: HISTORY, READ BACK AS ONE SEED (2026-11-09)

Examined live (REPL probe owner TOUR48A). Registry: Dell 48
Macro, manor "Shortcut sequence".

**Verified today.** Two acts in one Dell. (1) RENDER: bare
Macro prints the last 5 noted history entries joined as a
single Mandell seed string ("08[Create] :: macro alpha >
08[Create] :: macro beta"); a digit label sets how many
(:: 1 = the last entry only). The render notes nothing
itself — asking again shows the same tail, unpolluted by
the asking. Empty history renders '48[Macro] :: empty'.
(2) REPLAY: the label 'replay' runs replay_exec for real —
receipt "Replay exec n=3 ran=2 skipped=0" — re-executing
the tailed commands (Creates create again; no duplicate
guard — an explicit re-run, honestly receipted, in the same
family as DD-32's replay questions but invoked by name, not
by accident).

Honest gap against the name: there is NO macro library.
Nothing can be named, saved, edited, or invoked later —
Macro re-derives its sequence from raw history on the spot,
every time. A "macro" in the ordinary sense (a named,
kept shortcut) does not exist yet; whether Dell 48 grows
one — and how it would relate to CELLS (named reusable seed
definitions, SS12.29a) — is the design question this exam
leaves open for Ace.

### 12.37a ACE DESIGNS MACRO — THE PRIVATE SHELF / LITTLE NOTEBOOK (2026-11-09, DD-38)

Ace resolved SS12.37's open question by choosing BOTH halves
and naming the thing: Dell 48 gets her own PRIVATE SHELF —
"your little notebook" — after the pattern of his paper
Mandellamatrix notebook. DD-38 filed.

What the shelf is (Ace's substance, verbatim in spirit):
- A private, per-owner practice/workshop space owned by
  Macro. NOT the CELLS shelf — Ace chose the private drawer.
- It holds SAVED NAMED MOVE-SEQUENCES (macros proper): a
  cycle or loop that ran with a certain vibe, tone, and
  logic limits can be saved once and re-applied to any other
  thing later (Ace's example: a weekly cycle) — instead of
  re-deriving moves from raw history every time.
- It holds SMALL EDITABLE WORKS-IN-PROGRESS OF EVERY KIND —
  "tools in your little notebook where you can make and edit
  small things within ideas and Dells and Nursery and all
  types of things and perspectives and Psalms."
- Work inside the shelf happens on COPIES/DRAFTS: slide an
  idea in, play with it, mess it up — the actual idea in the
  matrix is NOT damaged. Nothing leaves the shelf except by
  Ace's explicit act of bringing it out (promotion path —
  for ideas the Nursery gate is the natural door; exact
  promotion mechanics are the build's contract question).

Distinctions the build must preserve:
- SHELF vs SANDBOX: the sandbox is isolation SEMANTICS
  (Plane.box / SandboxGate; boxed units, scoped resonance,
  Lock's drawers per DD-17). Macro's shelf is the personal
  NOTEBOOK SURFACE. The build reuses the existing sandbox
  isolation authority underneath the shelf — no second
  isolation authority (canonical-authority law).
- This ruling also supplies the owner decision missing since
  C-R1-007 (2026-10-03): named-macro creation had NO
  authority and "make a macro" degraded into creating an
  idea named "macro". Under DD-38, named macros live on
  Macro's shelf; the misleading fallback is retired by the
  same build.
- The shelf is the engine-side counterpart of the plan's
  Dell Playground page (SS-plan page set); the multi-Psalm
  harmony sit-down (SS12.36e) owns who else may be invited
  into the notebook and under what role limits.

## 12.38 TOUR CONTINUED — 49 PROFILE: A STATUS ECHO WEARING A BENCHMARK'S NAME (2026-11-09, DD-39)

Examined live (REPL probe owner TOUR49A). Registry: Dell 49
Profile, manor "Benchmark".

**Verified today.** Profile measures NOTHING. No timing, no
throughput, no performance of any kind. She prints a partial
status read: owner, idea count, history length, and the raw
nursery / lattice / enhance dicts echoed from
Program.status() — raw Python-dict dumps, nested resonance
dict included. Any label is ignored (a nonsense label
returned the identical read). She notes herself in history
(history_len rose 1 -> 2 across two calls). status() itself
aggregates many more systems (floor, truths, avatar,
personas, forces, pulse, keys, bimo...); Profile echoes
only three of them.

DD-39 (filed 2026-11-09): the NAME/MANOR OVERCLAIM class
(same family as TokenCount, DD-30) — "Profile / Benchmark"
promises performance profiling that does not exist, while
the actual function duplicates status territory that Dell
39 Schema is being redesigned to own properly (DD-29
nervous system). The clean division put to Ace: Schema owns
HEALTH/STATUS (is every organ present, connected, on?);
Profile becomes the true BENCHMARK (timed, repeatable runs
of named operations with honest receipts — how long does a
Create take, a Pulse, a save — so Ace can SEE the program
getting faster or slower). Alternative: honest relabel of
Profile as a status card. Decision is Ace's; no build
authorized by this note.

### 12.38a DD-39 RESOLVED BY ACE — PROFILE IS THE SPEEDOMETER (2026-11-09)

Ace chose option one and sharpened it past Uni's sketch.
His question cut to the real point: the program does not
move unless he ticks it — so "speed" means the WORK INSIDE
each tick, and his requirement is causal, not cosmetic:

**Profile must SENSE LAG AND PROCESSING STRAIN — and locate
the CAUSE.** Not a single number that says "slow": the tick
(or named operation) is broken into its pieces — embedding,
saving, Nursery update, growth, resonance, and the rest —
each piece timed, so when the plate gets too full Ace can
see WHICH stage is dragging or failing under load, the way
you can tell whether a delay lives in the beat, the board,
or the speakers.

DD-39 build contract (through Director routing): Profile
runs repeatable timed measurements of named operations with
per-stage breakdowns and honest receipts; timings are kept
so change over time is visible (faster/slower is a fact, not
a feeling); overload shows as named stages breaching, not a
vibe. Schema (DD-29) keeps health/status; Profile owns
performance — the division Ace approved stands.

## 12.39 TOUR CONTINUED — 50 MANIFEST: CREATE IN A CEREMONIAL COAT (2026-11-09)

Examined live (REPL probe owner TOUR50A). Registry: Dell 50
Manifest, manor "Make real / bring into form". LAST DELL OF
CORE I — the 00-50 examination is complete with this entry.

**Verified today.** Three behaviors: (1) bare Manifest asks
for a label and mutates nothing ("Manifest needs ::
label.", a message-level refusal with ok=True semantics at
the leaf, unlike 44/47's ok=False). (2) A label MINTS AN
IDEA through the same place_idea machinery Create uses —
the receipt is literally Create's ("Created idea: ...")
plus one extra word, "Manifested." Same CUBE placement,
same dedup, no parents, no form-giving of any other kind.
(3) The label 'acceptance' (or 'accept') mints nothing and
prints the acceptance sequence: create -> grow -> confirm
-> sphere -> save -> load -> visual — the same sequence
Dell 43 Fallback recites as its step 3.

Honest gap: "make real / bring into form" currently means
"Create, but she says Manifested." Nothing is brought from
anywhere — not from the Nursery, not from a draft, not from
Macro's new shelf (DD-38) — into form. Two candidate true
meanings are put to Ace (his ruling, not pre-decided):
(A) Manifest = the PROMOTION door: take a pending proposal
/ shelf draft and give it full form in the Plane — the act
that pairs with Nurture (the door in) and DD-38's explicit
promotion. (B) Manifest = the ACCEPTANCE GAUNTLET: run the
thing through create -> grow -> confirm -> sphere -> save
-> load -> visual as a real proving sequence, per the
'acceptance' label the author left behind. Either way,
DD-filing waits for Ace's ruling so the number lands on a
decided design.

### 12.39a MANIFEST RESOLVED BY ACE — CONFIRM IS THE YES, MANIFEST IS THE WALK (2026-11-09, DD-40)

Ace worked the distinction out loud and accepted it:
CONFIRM is his sovereign yes — permission, a state change
on the proposal. MANIFEST is the WORK after the yes: the
confirmed proposal is taken out of the Nursery and walked
into form — grow -> sphere -> save -> load -> visual —
until it lives on the Plane. In Ace's words: "proposals get
manifested." Create stays the birth of a new thing from
nothing; Manifest is the graduation of a waiting thing
(proposal; by extension a DD-38 shelf draft, whose promotion
door this Dell becomes).

DD-40 filed. Engineering consequence recorded honestly:
today's canonical confirm (form/dell_matrix/
confirm_lineage.py) FUSES the two into ONE atomic checkpoint
transaction — OLD {proposal PENDING, idea absent} -> NEW
{proposal CONFIRMED, idea present}, never a hybrid. Ace's
design splits that transition into two sovereign steps,
which creates a real intermediate state — CONFIRMED but not
yet MANIFESTED — that must be visible, durable, and
retryable, and each step must converge or fail closed (no
new hybrid states; the Q1/C-A discipline binds the build).
Build through Director routing; nothing about today's
confirm behavior changes until that circuit lands.

## 12.40 CORE II OPENS — 51 SELECT: THE WORKING SET (2026-11-09)

Ace's own synthesis, stated this session and recorded as
his framing: Core I ideas exist and are held; Core II lets
Core I ideas connect, relate, and be measured against each
other — do more together; FLOW carries the idea through the
Dells from one to the next. Core II registry entries carry
root / effect / family / spoken manifest forms (51 Select:
root "selection", effect "query", family "select").

Examined live (REPL owner TOUR51A). **Verified today.**
Select is a TYPED Dell: 51[Select](predicate="solar")
lowered to its label and searched the current scope
(default: the whole Plane). Predicate = case-insensitive
substring OR underscore-prefix match. From three created
ideas she picked exactly the two solar ones ("Select
scope=plane n=2"). Her laws, all D1-proven and re-observed:
the universe is SCOPE-BOUND (a predicate can narrow within
the scope, never widen past it; a named group scope = that
group's membership, plane-intersected); Select REPLACES the
selection, never appends; a no-match predicate is a
SUCCESSFUL empty selection (matched=False, count=0), not an
error; her one failure mode is a dangling scope
(scope_unknown, fail-closed). The selection is the program's
WORKING SET — the SELECTED rung of the information ladder —
which downstream Core II Dells (Filter and her family)
operate on; it persists across the session. Show's board
still reports whole-field totals — selection is a working
state, not a display filter.

## 12.41 TOUR CONTINUED — 52 FILTER: SIFT THE HANDFUL YOU HOLD (2026-11-09)

Examined live (REPL owner TOUR52A). Registry: Dell 52
Filter, manor "Reduce a set by conditions", root
"reduction", effect "query", family "select". TYPED
(predicate=) — one of the two signatures repaired by the
D1-TYPED-52-53 circuit (typed args on 52/53 were once
silently dropped; that defect class is closed and the typed
path is what this probe exercised).

**Verified today, as a counted sequence.** Select "solar"
took the working set to 2. Filter "roof": 2 -> 1. Bare
Filter: 1 -> 1 (identity, cond=*). Filter "zzz": 1 -> 0 —
a successful emptying, not an error. Filter narrows the
CURRENT SELECTION ONLY, never the Plane: she cannot widen,
cannot reach back for an idea a previous Filter removed —
only a fresh Select re-grabs from the scope. Same predicate
engine as Select (case-insensitive substring OR
underscore-prefix). Each Filter publishes a filter result
cell for downstream atoms. Select vs Filter in one line:
Select grabs a handful from the shelf and replaces what you
held; Filter sifts the handful already in your hand.
No defect, no DD — she matches her contract and her manor.

## 12.42 TOUR CONTINUED — 53 SCOPE: THE WALLS OF THE ROOM (2026-11-09)

Examined live (REPL owner TOUR53A). Registry: Dell 53
Scope, manor "Establish execution/context boundary", root
"boundary", effect "scope", family "select". TYPED (name=),
the second signature of the D1-TYPED-52-53 circuit.

**Verified today.** Scope sets the boundary Select (and
the selection family) may look inside. Supported names are
explicit: 'plane' — the whole field, the default; bare
Scope restores it — or an existing Dell 82 GROUP name
(groups being Ace's named Plane sandbox groups — a project
IS a named sandbox group, 2026-10-25). The binding is real,
proven with an outsider: two solar ideas were grouped as
'solarfamily', a third solar idea created AFTER, scope set
to the group — Select "solar" returned n=2, the outsider
excluded. An unknown name refuses on the spot
("Scope refused: unknown scope 'nope' (supported: plane)",
Error: scope_unknown:nope) and leaves the scope unchanged —
a scope never silently widens to the whole Plane. If the
scoped group is ungrouped, the scope dangles and Select
refuses until reset (R1 contract).

History kept honest: Scope once LIED — she printed the
scope name while Select ignored it and searched the whole
Plane (found 2026-10-29). Reconciliation R1 rebuilt the
contract (scope-bound universe, set-time + select-time
refusals) and closed 2026-10-30 with full regress and
fresh-clone proof. Today's probe exercised the repaired
machinery end to end. No defect, no DD.

### 12.42a THE 53 <-> 82 PARTNERSHIP — SCOPE AND GROUP ARE ONE PAIR (2026-11-09)

Ace named the pairing himself and directed it into the
plan: **Dell 53 Scope and Dell 82 Group GO TOGETHER.**
Group (82) MAKES the collections — the named families /
boxes / projects on the Plane. Scope (53) AIMS the working
boundary at one of them. Neither is complete alone: a group
nobody can scope into is just a list; a scope with no
groups has only one legal target (the whole Plane). When
the tour reaches 82, her examination reads against SS12.42
and this note: Group's membership rules (selection-based,
SS12.42's probe grouped the current selection) and Scope's
boundary rules are two halves of one contract — the
rooms of the house and the door that says which room we
are working in.

## 12.43 TOUR CONTINUED — 54 QUERY: ASK WITHOUT TOUCHING (2026-11-09)

Examined live (REPL owner TOUR54A). Registry: Dell 54
Query, manor "Retrieve information without mutation", root
"read", effect "query", family "select".

**Verified today.** Query searches ONLY the current
selection — never the Plane. Proof with a plant: Select
"solar" (selection = 2); Query "roof" -> hits=1; a NEW
"solar roof annex" was then created on the Plane but
outside the selection; Query "roof" again -> still hits=1.
The annex is invisible to her. She mutates nothing — the
selection is byte-identical after any query (the following
Filter behaved on the untouched selection). Her result is a
proper Boolean-matched cell (standardized by reconciliation
R2): IDs in value, quantity in count, confidence exactly
1.0 with hits and 0.0 without. Query NEVER FAILS: empty
selection and no-match (hits=0, verified with "zzz") are
valid answers, not errors. One reachability note carried
from D1 circuit 10: Query has NO English surface — "query
garden" typed in English does not reach her (it routes
elsewhere); she answers to the Mandell seed line and typed
calls. Whether she deserves an English door is a
language-design question, not a defect in her contract.
No DD.

## 12.44 ACE DESIGN — THE IDEA EDITING SYSTEM: GO INSIDE, EDIT THE PARTS, PROPOSE THE CHANGE (2026-11-09, DD-41)

Ace designed this at the Query/Filter sit-down, in his own
example: take the idea BUILD A HOUSE. Go INTO it. Inside
are its parts — schematics, dimensions. Select the
dimensions. Filter to just the BATHROOM dimensions. Now
the hand holds only bathroom dimensions. Edit them — all
the same size, or all different, his choice. Let go: the
parts drop back into the idea. The idea is SUPERSEDED —
the history of what changed is recorded — and the new
state is examined/analyzed by the docked AI, which knows
a change just happened. But NOTHING applies automatically:
the whole change lands in the NURSERY AS A PROPOSAL. Ace
reviews what the changes WOULD do, and on his confirm —
"bam" — the new idea is real. DD-41 filed.

What the build needs, each piece on an EXISTING authority
(no second authorities — the composition is the design):
1. ADDRESSABLE PARTS. Selection today holds WHOLE units
   only (verified SS12.40-12.43); parts are not selectable
   objects. Parts become addressable as CONTAINED children
   under TD-2 / SemanticGraph CONTAINS — the house CONTAINS
   dimensions CONTAINS bathroom dimensions. This is the
   engine under the plan's fractal/nested cards: opening a
   card level by level IS walking containment.
2. INWARD SCOPE. Dell 53 gains a third scope category
   alongside plane / group (SS12.42): INSIDE <idea> — the
   idea's contained contents become the universe, and
   51/52/54 work there unchanged (narrow-never-widen binds).
   The 53<->82 partnership (SS12.42a) extends: 53 also pairs
   with the containment authority.
3. DRAFT EDITING ON THE SHELF. The parts are edited as
   copies in Macro's private notebook (DD-38) — the actual
   idea is NOT damaged while Ace works; edit verbs operate
   on the held parts' content.
4. THE EDIT PROPOSAL (the new object). A Nursery proposal
   whose payload is a CHANGE, not a new idea: target idea +
   part + before + after + diff. Impact shown BEFORE
   confirm via the DD-21 dry-run discipline (what the
   change would do to the idea, its container, its
   resonance). Ace's confirm is the only door from draft
   to real.
5. SUPERSESSION + LINEAGE. On confirm, the edit applies
   and the old revision is superseded WITH its history —
   replacement-lineage machinery (72-33) records before /
   after / who / when; the backward chain stays walkable
   (DD-32 snapshot doctrine).
6. AI RE-EXAMINATION. The changed idea is flagged for the
   docked Psalm to re-examine (existing dock verbs:
   comprehend / relate_field); its findings land as
   FURTHER proposals, never auto-applied — observation is
   not authority, and a change is an observation until Ace
   gates it.
Sequencing is a Director-routing question (this composes
TD-2, DD-38, DD-21, the Nursery, and lineage) — design
recorded, no build authorized by this note.

# 13. CONSOLIDATED REFINEMENT — THE BIGGER PICTURE (2026-11-09, Ace order)

Ace ordered a full reanalysis of this plan: connect what
relates, note what is already done, wipe NOTHING. Sections
1-12 stand as the historical record; this section is the
current consolidated picture layered over them. Full
analysis: hidden_files/PLAN_REFINEMENT_DRAFT_2026-11-09.md
(13 clusters, 14 done-items, 13 flagged conflicts, 12 open
questions). Where this section and an older section
disagree, this section is the current reading and the older
text is history (supersession markers: SS13.4).

## 13.1 ALREADY DONE — no longer future work

Strict Director-confirmed 19/72 (48 Partial, 3
Investigation, 1 Open, 1 Blocked; OCI on-main 55.7%).
Closed in scope: G-11 snapshot reachability (certified),
G-12 Dock Proposal B (certified), DD-31 Sanitize copula
(fixed + certified, extension), the DD-01..05/09..13 defect
dial, TD-1/TD-1-R2 binding (certified in scope), TD-2
containment BUILT (certification UNKNOWN — Director
question F2), checkpoint + rollback combination verified,
the selection family contracts (51-54, R1/R2 reconciliations
closed), Nursery proposal machinery, BIMO/persona substrate,
a live Gemini dock with governed output, G-04 ForceField
restoration. The Dell TOUR EXAMINATION stands at 00-54
(SS12 header and SS12.7 item 1 are stale history). Remaining
tour: 55-99, feeding clusters below.

## 13.2 THE CLUSTERS — related directives, built together

C1 HONEST RECEIPTS + LOOP BODY (DD-14; riders DD-18, DD-35,
DD-23 receipt half) — one failure class: receipts claiming
what did not happen; silent gate flips.
C2 RESONANCE CORE (SS12.2 model; DD-15, DD-16, DD-23
outcome, DD-19 dial, growth; Mirror compare as independent
early leg) — one relatedness authority; DESIGN GATED by
Ace's resonance sit-down.
C3 HARMONIC NOTES + LENS MODES (DD-24; SS12.22/12.22a) —
the per-idea note feeds Stamp, harmony organization, lens
modes; modes rearrange view only, never write back.
C4 FAILURE + SNAPSHOTS + NAVIGATION (DD-21 leg A
standalone; leg B: Alpha wiring + history member, DD-32
doctrine, SS12.31b/c navigation, Fallback) — one
checkpoint authority; leg B is persistence-adjacent and
carries the SS12.13 acceptance proof as a merge
precondition; the everyday save pair is NOT in this
cluster (Q1 line, SS13.3).
C5 NURSERY GOVERNANCE (ranking formula + Rank face
SS12.35/b; DD-27 door policy; DD-40 Manifest split; Cycle
auto-confirm gating build) — one lifecycle contract:
pending -> door policy -> confirmed -> manifested, every
passage receipted. Formula first; DD-40 last (no-hybrid
discipline); auto-passage only after Ace sets standards.
C6 REFERENCE + ESSENCE ZIPPER (DD-20, DD-26, DD-28) — one
provenance/link convention; DD-20's source link first.
C7 SHELF + IDEA EDITING (DD-38, DD-41; DD-40 is its
promotion door) — TD-2 parts, shelf drafts, EDIT proposals,
supersede-with-lineage, docked re-examination.
C8 BOXES, BOUNDARIES, FREEZE (DD-17; the SS12.42a 53<->82
contract; DD-22) — one exclusion semantics: where activity
may reach.
C9 DOCK + PSALM OPERATIONS (DD-37 first — Ace-ruled,
bounded; resident Psalm SS12.20 after C5's formula and the
SS12.36e sit-down) — the roster is the resident mode's
accountability layer.
C10 SELF-REPORT (DD-29 nervous system -> DD-39 speedometer
-> DD-30 tokens) — health, performance, cost; the three
name-overclaim Dells become one honest self-report.
C11 PLACEMENT + BINDING (placement law, Create split,
AUTO/BIND) — design session first; builds on DD-40's
settled intermediate state.
C12 BRIDGE (DD-34: ledger, preview, act) — over Exchange
only; refusal-honesty may ride C1 early; doctrine wording
waits for C2's vocabulary.
C13 DISPLAY + HUMAN SURFACE (SS1/2/3/6/7/8/9/10 items;
DD-25 engine leg may start early) — display never invents
state; V-09 navigation research precedes page builds;
Show/face/age sit-down-gated; closes at V-12 (Ace's gates).

## 13.3 MUST STAY SEPARATE / GATED

Q1/C-A persistence line (PR #294 hold; F2 owed; DD-06/07
gated). 72-16 R-2 / DD-08 (design review only). DAF-09 +
whole-program certification (withheld). V-13 neural
(deferred). Adapt / DD-36 (adopted, NOT YET — Ace's word).
Online/shared matrix (LAST — Ace's ruling). PR #308
census-held; PR #233 never merge. Sit-downs owed to Ace
(growth; resonance incl. DD-23/DD-19/calculated-vs-actual;
Show; 05 face; AGE; 01/02 page; placement/Create/BIND;
harmonic modes; DD-27 standards; multi-Psalm harmony) gate
their clusters' DESIGN, not grounding or independent legs.

## 13.4 CONFLICTS FLAGGED (history kept; readings settled here)

Ranking formula stated 3x — C5 owns it canonically.
Auto-confirm: SS1's absolute is read THROUGH SS12.25's
reconciliation (door policy at Nurture; Cycle never
self-approves). Translate: SS12.34's doctrine is REPEALED
by SS12.34a/b — dual-mode + Adapt stands. Tokens: SS12.29
reads as amended by the SS12.29a nine-system census.
"Resonance": SS12.2 (relatedness) vs SS12.33b (calculated
vs actual) — vocabulary settled at the C2 sit-down; until
then C12 records the distinction without doctrine.
Placement vs motion: SS12.22a lenses settle it (SS3 reads
through it). Register lags flagged for the Director:
DD-31 + G-12 rows (certifications recorded in rulings,
stale in some register copies), TD-2 status (F2/F3).

## 13.5 EXECUTION ORDER (completion-first)

1 C1 (DD-14 in grounding, defect re-verified at 58af9db)
2 C9 DD-37 leg   3 C10 DD-29->DD-39   4 C4 leg A (DD-21)
5 C5 formula leg (Q-N3 answered in its contract)
6 C6   7 C8   8 C2 (sit-down first)   9 C3   10 C4 leg B
11 C5 remainder (DD-27 surface, DD-40)   12 C7   13 C11
14 C12   15 C9 resident Psalm   16 C13 (V-09 research may
run early). The 55-99 tour continues throughout as
examination; new DDs slot into clusters — novelty does not
jump the queue. Steps 2-6 share no state authority but
state-sharing campaigns still run sequentially: this is a
priority order, not a concurrency grant.

## 13.6 OPEN QUESTIONS

Director: F1 extension-register slotting for DD-14..41;
F2 TD-2 certification; F3 register-row reconciliations;
F4 DD-14's register home; F5 Q-72-40.2 folds into C2?;
F6 Q-SNAP.3 series; F7 clusters as single phased circuits?
Ace: F8 Q-N3 FRESH half-life; F9 sit-down scheduling;
F10 Embed provider selection; F11 DD-28 condensation mode;
F12 V-12 timed trials scheduling.
