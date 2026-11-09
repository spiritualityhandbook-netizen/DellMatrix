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

## 12.45 TOUR CONTINUED — 55 SET: THE WORKBENCH NOTEBOOK (2026-11-09)

WORKS, no defect. Set writes the Core II runtime store
(`Set key=value`); overwrites freely; Get (56) is its read hand.
Director-ruled PERMANENT legacy coercions (72-13, do not
"fix"): bare `Set ready` stores ready=1; `Set =orphan` stores
under the literal key "value". Set does NOT write on ideas and
does NOT create Nursery proposals. Probe caveat (artifact, not
a defect): a freshly loaded Program needs attach() before
.core_ii exists; the store persists per core_ii_persist_test.

## 12.46 TOUR CONTINUED — 56 GET: THE READ HAND (2026-11-09)

WORKS. Existing key -> value with matched=true. Missing key ->
honest soft miss (ok with matched=false, value=null, error
"missing"), no crash, store untouched. Bare Get returns the
currently-live note. No defect.

## 12.47 TOUR CONTINUED — 57 COMPARE: STRUCTURED COMPARISON (2026-11-09)

Registry: (57, "Compare", "Structured comparison between >=2
targets"); handler form/mandell/query_ops.py ->
form/mandell/predicate.py eval_predicate / _cmp_typed. NOTE:
"Patch" is NOT a numbered Dell (it exists only as a typed
seed-level operation from DAF-01); an early spoken tour slip
calling 57 "Patch" was corrected to Ace in-session.
Verified semantics (as amended by SS12.47a's deeper probes):
gt/lt REQUIRE both operands numeric, else type_mismatch with
no verdict; eq/ne require same type; contains/starts/ends are
case-insensitive string ops. Operands resolve in order: store
(Set notes, classify_value-typed) -> st.weights -> literal.
Reserved tokens shadow store keys: `count` = current selection
count (count_ref), plus selected, last_result, store:<key>.
The designed grammar is PREFIX (gt:level 3) and is numerically
exact; the INFIX degradation defect is DD-42 (SS12.47a).
"heavier" = a number somebody wrote down (store note or
weight) — nothing semantic; "more important" is NOT a Compare
concept (importance lives in Rank's formula + selection); Dell
categories are DECLARED registry constants, never computed.

## 12.48 TOUR CONTINUED — 58 MATCH: THE NAME SIFTER (2026-11-09)

WORKS. Name-pattern sifter over the current selection only
(contains/prefix on unit name/id, case-insensitive). Verified:
Select-all (4 units) -> Match 'solar' narrowed to 2; Match
'pool' on the narrowed set -> 0 (one-way, like Filter — it
cannot reach back for tossed units); bare Match keeps all.
Filter asks "does it qualify?" (fields/conditions); Match asks
"does its name fit?" The overlap is acknowledged in the record.

## 12.49 TOUR CONTINUED — 59 ROUTE: THE PATH REGISTER (2026-11-09)

WORKS. Sets the chain's route register — any label accepted
(it need not exist); bare Route -> "primary". Downstream flow
(Branch/FlowTowards/DynamicFlow in chain_exec) reads it.
Inside a Branch chain a 59 atom is CONSUMED as the Else marker
and never executes as Route (registry-documented). Working
state only. Ace's extended vision (work on a path -> the dock
drafts a consequence-preview proposal -> confirm changes the
Matrix) is DESIGN for the DD-41/DD-21 family, NOT current
behavior, and is recorded as such.

## 12.50 TOUR CONTINUED — 60 BRANCH: THE FORK (2026-11-09)

Handler: control_runtime.eval_condition -> records {cond,
taken, path} + ControlFrame; message "unchosen_not_run"; bare
Branch = true. Chain structure: Branch > true-atoms > 59 (as
Else) > false-atoms > 61 Join; without an Else atom, atoms
after Branch run regardless (verified). AS AMENDED BY
SS12.47a: the working condition grammar is PREFIX (gt:count 3
style via eval_predicate); INFIX conditions silently degrade
to truthiness (DD-42 — the true path is always taken when the
key is truthy, with no comparison performed). The earlier
spoken claim that prefix conditions "quietly take the false
path" was a poisoned probe (the test key was the reserved word
"count") and is reversed in SS12.47a: prefix is correct, infix
is the silent path. Join semantics are at SS12.51.

## 12.47a DD-42 — INFIX CONDITIONS SILENTLY DEGRADE TO TRUTHINESS (Ace: "Get that fixed", 2026-11-09)

Verified live at main 7399ee5 during the Dell 57/60 examination
(probes T60C/T60D/T60F, throwaway owners, predicate engine level).

FACTS:
- The designed condition grammar is PREFIX: `gt:level 3`.
  With store level=5 the full battery is numerically exact
  (gt 3 T, gt 99 F, lt 99 T, lt 3 F, eq 5 T, gte 5 T; mode=number).
  Compare (57) and Branch (60) share this engine (predicate.py
  eval_predicate -> _cmp_typed); both are CORRECT in prefix form.
- Reserved operand tokens exist and shadow store keys:
  `count` = current selection count (count_ref), plus selected,
  last_result, store:<key>. A store key literally named "count"
  is unreachable by bare name in conditions (use store:count).
- DEFECT: an INFIX condition (`level gt 99`, `level lt 3`) —
  the natural human phrasing — matches no predicate prefix, so
  eval_predicate falls through to its truthy fallback: it checks
  only that the first token resolves truthy and IGNORES the
  operator and the second operand entirely. `level gt 99` and
  `level lt 3` BOTH return matched=True with level=5. A Branch
  on an infix condition therefore always takes the true path
  (when the key is truthy) while its frame/receipt presents a
  comparison verdict. No error, no type_mismatch, no warning.

CLASS: silent semantic degradation — the DD-14 family (a receipt
claiming work that did not happen), condition-semantics branch.
Ace directed the fix on sight (2026-11-09). FIX-FIRST family,
Cluster 1 (SS13.5): the repair must make an unparseable/infix
condition REFUSE honestly (or genuinely parse infix), never
degrade to truthiness silently; failing-first suite must cover
Compare (57), Branch (60), Guard/Assert paths sharing
eval_condition, and the truthy fallback's legitimate uses
(bare key conditions are a designed feature — `truthy`/`exists`
predicates — and must keep working when the user asks for them
by name or by a bare key ALONE, with no operator present).

CORRECTIONS TO THE TOUR RECORD (same session): SS12.47's claim
that Compare "compares the operands she's handed, not store
keys" was probe error (the probe key was the reserved word
"count"); SS12.50's claim that prefix conditions "quietly take
the false path" was the same poisoned probe — reversed: prefix
is correct, infix is the silent path. Join (61) policy/failure
propagation verified (join_fail under all/any on a failed block);
her Else-arm skip semantics need ONE clean re-test in prefix
grammar before being claimed (the tour probes were confounded
by the infix defect above).

## 12.51 DELL 61 — JOIN (examined 2026-11-09, chain level)

Verified: Join closes a control block and judges its EXECUTED
results under its label policy (default "all"). An all-ok block
-> Join ok, chain ok. A block containing a refused atom (Scope
'Nowhere') -> Join status fail, error join_fail, chain ok=False
under BOTH 'all' and 'any' in the probe (the block's executed set
was the failed atom alone). Skipped atoms are omissions, not
failures (B7/DAF-08 law; 72-27 Director-confirmed: Guard/Assert
verdicts propagate through Joins). Under DD-43 (SS12.52a/b),
Join additionally becomes the parallel merge point and the
surface where per-arm Mirror reflections (Dell 18, SS12.51a
below) present side-by-side in the preview. Else-arm skip
semantics still owe ONE clean re-test in prefix grammar
(SS12.47a) before being claimed.

### 12.51a PARALLEL x MIRROR (Ace question, 2026-11-09)

Verified distinction: Parallel (62) is an EXECUTION mode (runs a
block; ordering/concurrency per SS12.52); Mirror (18) is a
READ-ONLY reflection (lists up to 16 live Plane ideas + count;
writes nothing — executor_leaf.py handler read first-hand).
Paralleling a Mirror is therefore conflict-free by construction
(Mirror never writes, so it can never create a merge conflict),
and under DD-43 each arm's Mirror reflects its own isolated
copy — the Join preview's natural side-by-side compare surface,
which is the compare/diff capability Ace ordered at Dell 18.
Precedent noted: Dell 17 Shadow already keeps a track labeled
"parallel — not live."

## 12.52 DELL 62 — PARALLEL (examined 2026-11-09, chain level)

Verified current behavior (main 7399ee5): the block executes in
listed order, sequentially; a failing sibling (Scope 'Nowhere'
between two Sets) is captured ("parallel fail captured" message),
the remaining operations still run (both Sets landed), and the
chain receipt stays honestly ok=False. Registry row states the
sequential truth verbatim (72-20, PR #320). Ace's rulings
SS12.52a (DD-43: true concurrency via isolated arms + Join
merge), SS12.52b (dock pre-run + full-information proposal +
confirm), SS12.52c (contract generalized program-wide incl.
personas through BIMO) govern the future build; until then the
sequential contract stands and the registry keeps saying so.

## 12.52a DD-43 — PARALLEL MUST MEAN PARALLEL (Ace ruling, 2026-11-09)

Ace, on examining Dell 62: Parallel is "supposed to be running
things parallel to each other. Two Dells at once... I don't know
if that's possible, but it should be."

CURRENT CONTRACT (verified this session): 62 executes its block
in listed order, sequentially; a sibling failure is captured in
the record and the remaining operations still run (chain receipt
stays honestly not-ok). Registry row states this verbatim; the
semantics were Director-confirmed in 72-20 (PR #320) when the
row was corrected FROM a concurrency claim TO the sequential
truth. The name has already lied once; it must not lie again.

FEASIBILITY (grounded 2026-11-09): the chain interpreter is
single-threaded over one shared mutable Program (store,
selection, Plane, frames). There is NO threading/multiprocessing
anywhere in form/mandell or the Core II runtime (the only product
thread is the Studio live-visual server). Raw threads over the
shared state would race the store and the Plane — the exact
state-sharing failure class this project has standing law
against (campaigns run sequentially or in isolated state).

DESIGN DIRECTION FOR THE CIRCUIT (Director routing; design
first, no build authorized by this note): arms execute
CONCURRENTLY AGAINST ISOLATED working copies (the snapshot /
sandbox authority already provides the isolation shape), and
Join (61) becomes the merge point with an explicit conflict
rule (same-key writes from two arms = a surfaced conflict,
never a silent last-writer win). That yields TRUE parallel
execution — two Dells genuinely at once — with deterministic,
receipt-visible merging, and it composes with DD-38 (Macro
shelf isolation) and DD-22 (freeze semantics). Until that
circuit ships and is certified, the sequential contract stands
and the registry keeps saying so.

### 12.52b DD-43 AMENDED — PREVIEW BEFORE PARALLEL (Ace, 2026-11-09)

Ace extends the DD-43 ruling: he runs things parallel, "and
before it actually happens, I get all the information on it —
of course, my dock runs it — and then" [it happens on his
confirm]. The Parallel execution contract is therefore:

1. PRE-RUN: the docked AI executes the parallel arms in
   isolation first (the DD-21 Simulate/rehearsal machinery over
   the DD-43 isolated copies) — nothing touches the live field.
2. FULL INFORMATION: Ace receives the complete preview as a
   Nursery proposal — per-arm effects, the Join merge outcome,
   and every same-key conflict surfaced by name — before any
   real execution.
3. CONFIRM GATES REALITY: only Ace's confirm runs the arms
   against the live matrix; the preview's merge result is the
   committed result or the run refuses (no preview/reality
   drift — the same no-hybrid discipline as the checkpoint
   path).

This composes DD-43 with DD-21 (Simulate as a real rehearsal),
DD-41 (the consequence-preview proposal), and the standing
Nursery law (dock output is PENDING-only). It also sharpens
DD-21: a Simulate of a Parallel block must report per-arm
effects and merge conflicts, not a single blended outcome.

### 12.52c PARALLEL GENERALIZED — NOT DELLS ONLY (Ace ruling, 2026-11-09)

Ace generalizes DD-43 beyond Dell chains: "Dells shouldn't be
the only thing I should be able to run parallel with each other.
I should be able to run personas parallel, pretty much through
the BIMO. And possibly other things."

RULED: the parallel contract (DD-43 + SS12.52b) is a
PROGRAM-WIDE capability, one contract everywhere it applies:
isolated concurrent run -> full-information preview proposal ->
Ace confirm -> merge with conflicts surfaced by name.

Scopes named by Ace:
- Dell chains (DD-43 proper).
- PERSONAS through BIMO: multiple persona forms working in
  parallel. HONEST BOUNDARY (verified standing fact): today
  BIMO is descriptive fusion-body/persona metadata — the roster
  (11 personas) is read-only, the avatar carries ONE active
  form, and persona slots confer no execution authority.
  Parallel personas therefore requires the persona layer to
  gain real execution instances — an authority change routed
  through the Director and the owed multi-Psalm harmony design
  session (SS12.36e), where roles/limits/no-clash rules are
  decided. The multi-dock evidence (SS12.36a/b: many sessions
  live at once, provenance-tagged) shows the session layer can
  already hold parallel minds; personas are the missing
  instance layer.
- "Possibly other things": any future runnable (macros on the
  DD-38 shelf, docked Psalms, field processes) inherits the
  same contract by default rather than inventing its own
  concurrency rules.

One contract, every scope — no per-feature concurrency dialects.

## 12.53 DELL 63 — SEQUENCE (examined 2026-11-09, chain level)

FINDING: Sequence is currently behaviorally IDENTICAL to
Parallel. The same failing-block chain (Set a=1, Scope 'Nowhere',
Set b=2, Join all) under both heads produced: both Sets landed,
chain ok=False — the ONLY difference is that Parallel logs a
"parallel fail captured" message and Sequence does not. The
chain executor calls the same execute_range for both heads
(chain_exec.py, n==62 / n==63 branches). Whatever distinction
Sequence's name promises (a strict order where each step's
completion gates the next) is NOT implemented as a behavioral
difference today; gating exists only through the explicit flow
operators (FlowThru blocks the next atom after a failure, per
Director Decision 1 in execute_range). Recorded as an
observation for Ace/Director: either Sequence gains real
sequential-gating semantics, or its registry row must say what
it actually is. No ruling taken in the tour.

## 12.54 DELL 64 — UNTIL (examined 2026-11-09, chain level)

WORKS — the honest looper. Verified all three paths live
(prefix grammar conditions, SS12.47a):
- Condition ALREADY true -> zero iterations; every body atom
  gets an explicit skip receipt ("until condition already
  true"), nothing silently omitted.
- Body flips the condition -> exactly one iteration, condition
  re-checked before AND after the body, clean exit, chain ok.
- Condition never satisfied -> exactly 8 iterations (the chain
  bound, DEFAULT_BOUND), then status bounded, error
  bound_reached, chain ok=False. No infinite loop, no fake
  success.
Notable for DD-14: Until proves the codebase already owns REAL
chain-body repetition (execute_range re-invoked per iteration in
chain_exec.py's 64/65 branch) — Dell 14 Loop's missing mechanism
has an in-house precedent one floor up. While (65) shares this
branch with inverted polarity (zero iterations when the
condition starts false; bounded failure when it never turns
false) — code-read, to be probe-confirmed at her own stop.

## 12.55 DELL 65 — WHILE (examined 2026-11-09, chain level)

WORKS — probe-confirmed on all three paths (the SS12.54 note
promised this confirmation): condition starts FALSE -> zero
iterations with an explicit skip receipt, chain ok; body flips
the condition false -> exactly one iteration, clean exit;
condition stays true -> exactly 8 iterations (chain bound),
then bound_reached, chain ok=False. While and Until are one
mechanism with inverted polarity, exactly as their shared
chain_exec branch reads. No defect, no ruling needed.

## 12.56 DD-44 — LOOP BOUNDS MUST BE EXPLICIT; NO SILENT 8 (Ace ruling, 2026-11-09)

Ace, on learning While stops at 8 by default: the bound must
not silently default. RULED, for the loop family (While 65 and
Until 64 share the bound machinery; Dell 14 Loop noted as the
same family):

1. SPECIFY: running a loop requires stating exactly how many
   iterations are wanted. The number is part of the command,
   not a hidden constant.
2. ASK: if the count is not specified, the loop ASKS the user
   how many — it does not quietly pick 8 (or any number).
3. FAIL WITH THE WHY: if the count still isn't known (no
   answer), the loop FAILS and the user gets ALL the
   information on why — the DD-32 failure doctrine's ANALYZE
   door applied to loops: what was asked, what was missing,
   what did and did not run.

CURRENT MECHANISM (verified at the SS12.54 examination):
bound_of(st) reads st.limit (Dell 72 Limit is the setter
family); empty or invalid input falls through validate_bound
to DEFAULT_BOUND = 8 silently — that silent fallback is the
defect this ruling removes. CONTRACT NOTE: 72-21 (PR #321,
Director-confirmed) certified "loop bounds exact INCLUDING
default 8" — DD-44 supersedes the default half of that
contract on Ace's authority as Overseer; bounds being exact
stands, the silent default goes. Implementation routes
through the Director as a contract change, with failing-first
evidence: unspecified bound -> ask/refusal receipt, never a
run; specified bound -> exact iteration count, as today.

## 12.57 DELL 66 — FOREACH (examined 2026-11-09, chain level)

WORKS. Verified: with a selection of 4 established (the fresh
field's starter unit + 3 created ideas), ForEach ran its body
exactly 4 times, once per member in selection order; every body
receipt is stamped member=<id>; during each pass the chain's
context AND route point at the current member (the body can
tell whose turn it is), and both are restored to their prior
values when the block ends. Empty selection -> zero iterations,
explicit skip receipts, chain still ok ("ForEach empty
selection valid") — an empty guest list is not an error.

OBSERVATION (verified behavior, mechanism not yet isolated):
composition inside ONE chain — Create, Create, Select in a
single seed — leaves the selection EMPTY (selected=[]) even
though the same steps as separate chains select all 4 and the
chain reports ok. Select inside a chain does not see ideas
created earlier in that same chain. Any chain that builds its
own working set before a Select/Filter/ForEach block is exposed
to this. Recorded as an open finding for investigation
(candidate sources: chain-start snapshot vs live plane, or a
selection reset at frame boundaries — UNPROVEN either way);
the same-chain wart does not affect ForEach reading a selection
established before the block, which is verified above.

## 12.57a DD-45 — SELECT IN A CHAIN SILENTLY ERASES SAME-CHAIN CREATES (Ace: fix it, 2026-11-09)

ESCALATION of the SS12.57 observation, mechanism narrowed by
discriminating probes (T66C/T66D/T66E, throwaway owners, main
7399ee5):

- Create+Create in ONE chain: both ideas land on the Plane. OK.
- Create then Set (55), or Create then Show (09): lands. OK.
- Create, Create, then SELECT (51) in one chain: chain reports
  ok=True, selection comes back EMPTY — and after the chain the
  Plane contains ONLY the starter unit. The two creates are not
  merely unselected; they are GONE. A second Select-only chain
  afterwards still finds nothing (correctly — there is nothing).
- The same steps as separate chains work perfectly (Select via
  the API found all 4 units; SS12.57's ForEach proof).

So a Select atom inside a chain destroys the chain's own
earlier, successfully-reported Create work — silent data loss
under a success receipt, the worst honesty class this project
tracks. The Select handler itself (query_ops n==51 ->
scope_universe -> _ids(program)) reads as a pure reader; the
destruction therefore sits in how chain execution stages or
commits Core I work around a query atom — full trace is the
circuit's first job, not guessed here.

Ace directed the fix on sight (2026-11-09). FIX-FIRST, front of
Cluster 1 with DD-14/DD-42/DD-44: failing-first suite must pin
(a) creates survive any later atom in the same chain, Select
included; (b) Select sees same-chain creates; (c) the chain's
ok receipt can never again cover vanished work. Blast radius
to check in the circuit: every QUERY_DELLS member (51-59,
67-79) as a potential same-chain eraser, and Filter/Query/
ForEach reading selections built in-chain.

CORRECTION (2026-11-09, DD-45 FIX CIRCUIT — the mechanism
above is DISPROVEN and replaced): the creates were never
destroyed, and Select/Filter never erased anything. Atom-level
tracing proved the tour's probe seeds (carrying trailing '::'
empty labels) were REFUSED by parse_seed ("too many flow
operators"), and chain_exec.execute_chain — alone among
execution surfaces — never checked seed.ok: it executed the
empty atom list and returned ok=True with ZERO atoms executed.
The fresh plane's starter 'welcome' unit read as "everything
erased." The true defect class is worse in kind: A SUCCESS
RECEIPT OVER A REFUSED PARSE, for any Dell and any parse
failure, in the chain authority itself. FIXED (PR #345,
commit 531601e): execute_chain fails closed on a parser-refused
seed — ok=False, the parse error named, zero atoms executed,
zero state mutated. Suite form/dd45_chain_parse_refusal_test.py:
99/113 at base -> 113/113 fixed; mutants killed; regress x3
GREEN 264/264. Select in a chain DOES see same-chain creates
under valid grammar (proven at base, pinned in the suite).
Grammar disposition (whether trailing empty labels should
parse at all) is Q-DD45.2, the Director's question. Status:
FIXED, Ace-authorized (fix-first), NOT Director-certified;
strict stays 19/72.

## 12.58 DELL 67 — ANY (examined 2026-11-09, API level)

Registry truth: 67 is ANY — the existential quantifier — not
"Assert" (a spoken slip in the tour, corrected here; Guard/
Assert are chain-level constructs, cf. 72-27, not numbered
Dells in this family). 67-69 are the typed quantifier triple:
Any / All / None over the current selection, matching by the
shared name-pattern predicate (the Match matcher).

Verified: selection of 3 (starter + Alpha + Beta) — Any
'alpha' -> matched=True; Any 'zzz' -> matched=False; the
result cell reports count = selection size. Empty selection ->
matched=False, count=0 (existential over nothing is false —
logically correct). Any is a QUESTION, not a gate: the atom
executes ok and publishes its verdict in last_result for
Branch/Guard consumers; it does not fail a chain by itself.
No defect.

## 12.59 DELL 68 — ALL (examined 2026-11-09, API level; Any re-verified with her)

Ace directed a hard verification of the Any/All pair. Battery
run live (selection [welcome, alpha, beta], then filtered to
[alpha, beta]); ALL 9 expectations met:

ANY (67): 'a' True; '' (bare) True; 'alpha' on the filtered
pair True; 'zzz' False (SS12.58); empty selection False.
ALL (68): 'a' over the full trio False (welcome has no 'a' —
one dissenter fails the universal, correct); '' True; after
Filter 'a' narrowed the hand to [alpha, beta]: All 'a' True,
All 'alpha' False (beta dissents, correct).

DESIGN FACT, stated not buried: All over an EMPTY selection
returns TRUE (vacuous truth — the code's `if ids else True`,
and standard logic: a universal claim about nothing cannot be
falsified). Paired with Any-over-empty = False, the triple is
logically coherent. Flagged here because it surprises: a chain
that asks All before selecting anything hears "yes." If Ace
wants empty-All to refuse instead, that is a one-line contract
change for a future circuit — NO ruling taken in the tour.

## 12.60 DELL 69 — NONE (examined 2026-11-09, API level)

WORKS. None is the explicit absence claim: "not one in my
hand matches." Verified against the same trio selection:
None 'zzz' True; None 'alpha' False; None '' False (the bare
pattern matches everything, so matches exist); None 'a' False.
Cross-checked against Any in every case: None(lab) ==
not Any(lab), all four — None is literally `not any(...)` in
the handler, and the behavior honors the code. Empty selection
-> True (an absence claim about nothing holds). The quantifier
triple 67/68/69 is now fully verified and logically coherent:
Any-over-empty False, All-over-empty True (vacuous, SS12.59),
None-over-empty True. No defect, no ruling needed.

## 12.61 DELL 70 — COUNT (examined 2026-11-09, API level)

WORKS. The registry row carries her own clarification:
"Cardinality — not token count" (she is NOT Dell 40
TokenCount; she counts ideas, not words). Verified: Count
reports the size of the current SELECTION exactly — 3 with
the full trio selected, 2 after Filter 'a', 0 after Filter
'zzz'. matched=True in all three cases, correctly: Count is a
measurement, not a claim, and zero is a successful measurement,
not a failure. She is also the visible face of the reserved
`count` operand that Compare/Branch conditions read (SS12.47):
the number conditions weigh IS this Dell's number, the size of
the handful. No defect.

## 12.62 DELL 71 — MEASURE (examined 2026-11-09, API level)

DECLARED PLACEHOLDER — the registry tells the truth about
her, and behavior matches the confession. Verified: with a
selection of 3, Measure '' -> 3.0 (predicate=count); Measure
'height' -> 3.0 (predicate=height); Measure 'weight:height' ->
3.0 (predicate=height); Measure 'bananas' -> 3.0. Whatever
property she is asked for, she returns the SELECTION SIZE as a
float and echoes the label as annotation. Her registry row
states it verbatim: "Count selected-set cardinality only
(kind/unit label is annotation, not a property measurement;
property vocabulary deferred)". She is Count (70) with a float
and a label — no hidden lie (the row was honest, unlike
Parallel's pre-72-20 row), but no property measurement exists.
OPEN DESIGN QUESTION for Ace/Director (no ruling taken):
should Measure grow a real property vocabulary — unit detail
fields, growth height, store weights are candidate measurable
properties already in the system — or stay an annotated Count?

### 12.62a DD-46 — MEASURE LEARNS REAL MEASUREMENT (Ace ruling, 2026-11-09)

Ace answers the SS12.62 open question: Measure "should learn
measures — you should be able to measure distance, you should
be able to measure difference in resonance between items, you
should be able to measure anything that's measurable — within
the Plane."

RULED: Measure gains a real property vocabulary scoped to the
Plane. The measurable inventory already in the system includes:
distance between ideas (units carry x/y positions — verified
in the G-11 snapshot circuit's revalidation), resonance values
and their DIFFERENCES between items (the resonance model
itself is owned by the owed resonance sit-down; Measure reads
settled values, she does not define them), growth height,
weights, and numeric detail fields. Ace's principle is the
general one: anything the system actually carries as a number,
Measure can be asked for by name.

HONESTY CLAUSE (same family as DD-42/DD-45): the current
silent fallback — answering selection cardinality for ANY
label — dies with this build. A property that does not exist
or is not measurable gets an honest refusal naming what was
asked, never a substituted number wearing the label. Measure
is a design+build circuit (property vocabulary is a contract),
Director-routed; until it ships, the registry's confession at
SS12.62 stands as the true description.

## 12.63 DELL 72 — LIMIT (examined 2026-11-09, API + chain level)

WORKS. Limit is the setter for the loop bound (bound_of reads
st.limit — SS12.54/DD-44). Verified: Limit 3 -> st.limit='3',
and a While whose condition never turns false then ran its
body EXACTLY 3 times before bound_reached failed the chain —
the bound is real, exact, and enforced (the 72-21 contract:
bounds exact). Limit 'abc' -> honest refusal (ok=False,
error=invalid_limit) with the previous limit untouched.
Limit 0 -> accepted (st.limit='0'; a loop under it runs zero
times and bound-fails). DD-44 CROSS-REF: a BARE Limit (empty
label) routes through validate_bound's ''/'max' -> DEFAULT 8
silently — the silent-8 lives here at the setter as well as at
bound_of's fallback, and DD-44's contract change must cover
both mouths of it: under Ace's law, Limit without a stated
number asks/refuses rather than minting 8.

### 12.63a DD-44 EXTENDED — LIMIT APPLIES TO ANYTHING INVOLVING DELLS (Ace ruling, 2026-11-09)

Ace generalizes the loop-bound law: Limit "can be applied to
anything — and when I'm saying anything I mean all the things
that involve Dells." RULED:

1. Limit is a PROGRAM-WIDE bounding authority, not a loop-only
   setting. Any Dell operation with a quantity dimension —
   iteration, repetition, collection size, expansion, retry
   counts, page/result sizes, per-session proposal volumes —
   must be boundable by a stated Limit.
2. DD-44's explicitness law travels with it: wherever a limit
   is in play for a Dell-involving operation, the number is
   stated, or the operation asks, or it fails with the full
   why. No silent defaults anywhere in the family.
3. The DD-44 circuit's scope therefore includes an AUDIT:
   enumerate which Dells carry quantity dimensions today, which
   already honor st.limit (verified: only the Until/While
   branch reads bound_of at the SS12.63 examination), and wire
   the rest under the one authority — no per-Dell private caps
   invented ad hoc. Coverage is claimed only per-Dell, from
   tests, never for the family wholesale.

Same generalization pattern as DD-43 (SS12.52c): one contract,
every scope.

## 12.64 DELL 73 — THRESHOLD (examined 2026-11-09, API level)

WORKS as a one-shot boundary check. Verified 6/6 (store
level=5, selection count=3): 'gte:level 3' True; 'gte:level
99' False; the loose form 'level 3' is coerced to gte:level 3
(True); a bare number compares against the SELECTION COUNT
('2' True, '9' False — Count's number again, SS12.61); bare
Threshold defaults to gte:count 0 (always true). Verdict lands
in last_result via the shared eval_predicate engine (prefix
grammar, SS12.47a applies). HONEST SCOPE NOTE: despite the
registry's "Trigger/qualify at boundary" wording, Threshold
does not WATCH anything — she evaluates once, at call time,
and reports crossed/not-crossed. A standing tripwire that
fires when a value crosses later does not exist in her today;
if Ace wants the watching kind, that is a design item (she
would compose with Pulse/ticks and DD-22 freeze semantics) —
no ruling taken in the tour.

### 12.64a DD-47 — THRESHOLD REPORTS THE MARGIN AND COMPOSES (Ace ruling, 2026-11-09)

Ace extends Threshold (73): "the threshold should be known
exactly how far have you crossed the threshold, not just if
you did or not. It should take the measurements. And then
should be able to be used with other Dells — to maybe be used
with Limit in order to limit the threshold and different
stuff like that. That's the goal."

RULED:
1. MARGIN, NOT JUST VERDICT: Threshold's result carries the
   signed distance past the line (measured value minus the
   threshold) alongside crossed/not-crossed — by how much you
   crossed, or by how much you missed.
2. SHE TAKES THE MEASUREMENT through the DD-46 Measure
   vocabulary (SS12.62a) — one measuring authority; Threshold
   does not grow a private ruler.
3. COMPOSABILITY IS THE GOAL: Threshold's outputs (value,
   margin, verdict) are first-class operands for other Dells —
   conditions/Branch can already read last_result's verdict
   (the predicate engine's last_result operand); the margin
   extends what they can weigh. Named composition: Threshold x
   Limit (72) — a threshold may itself be limited (cap the
   margin that counts, bound evaluations per SS12.63a's
   program-wide Limit law). Further pairings are discovered in
   the build, under the same one-authority rule.

Design+build item, Director-routed, clusters with DD-46
(Measure's vocabulary lands first or together — Threshold's
margin is only as real as the measurement underneath it).

## 12.65 DELL 74 — WEIGHT (examined 2026-11-09, API level)

WORKS. Weight assigns a named number to the weights table —
the table Compare/Branch conditions read as operands (the
"heavier" source, SS12.47). Verified: Weight gravity=2.5 ->
weights {gravity: 2.5}, and a condition immediately weighs it
(gt:gravity 2 -> matched, mode=number). Garbage is refused
with the table untouched: 'bad=abc' -> ok=False,
error=nonfinite_weight (the unparseable value degrades to NaN
and the finite check rejects it — one refusal mouth);
'x=inf' -> same refusal. Bare Weight writes target=1.0.
No defect.

ACE COMPOSITION NOTE (2026-11-09, asked at this stop): the
measurement/composition family (Measure DD-46, Threshold
DD-47, Limit DD-44, Weight) "should also work with Schema."
CONFIRMED AS DIRECTION, NOT AS CURRENT FACT: today Schema
(39) consumes none of it — she checks that three engines
exist (SS12.28). Under DD-29 (Schema as the nervous system),
her whole-body report must READ this family: are the measuring
systems live, what limits are set, which thresholds are
crossed and by what margin — the body's numbers belong in the
body's report. Recorded here and owed in DD-29's build notes;
no integration exists until DD-29 ships.

### 12.65a DD-48 — WEIGHT GOES UNIVERSAL: EVERYTHING CALCULATED, EVERYTHING WEIGHED, SCHEMA READS IT (Ace ruling, 2026-11-09)

Ace expands Weight (74) far beyond her current trade: "that
pretty much is how ideas can be weighed and linked to each
other... I need everything — this should calculate everything
in the program and give everything a weight, and then that way
the AIs can come in and schema the whole thing. And this data
should work hand in hand with Schema."

RULED:
1. UNIVERSAL WEIGHTING: Weight CALCULATES across the whole
   program and assigns a weight to everything — every idea
   and every measurable quantity (Measure, DD-46, reads the
   numbers; Weight assigns their significance). Weighted
   relations are the fabric ideas are linked by.
2. THE DOCK READS THE MAP: docked AIs survey the whole body
   through that weighted map — the weights are the legible
   surface an AI uses to understand what matters in the field.
3. HAND IN HAND WITH SCHEMA: the universal weight data is a
   primary input to Schema's nervous-system report (DD-29) —
   extending SS12.65's composition note into a full ruling.
   The quantitative cluster is one build family: DD-46 Measure
   (reads) + DD-48 Weight (assigns) + DD-47 Threshold (margins)
   + DD-44 Limit (bounds) -> DD-29 Schema (reports the body).

DISTINCTION PRESERVED: Ace's phrase "through the neural
network" is recorded as the weighted-connection fabric above.
The deferred V-13 neural item (Ace's own plan) is a SEPARATE,
later thing and is NOT un-deferred by this ruling.

CURRENT TRUTH (verified SS12.65): Weight today is one manual
key=value write into a small operand table. Universal
calculated weighting does not exist; this is a design+build
direction, Director-routed. No part of it is claimed built.

## 12.66 DELL 75 — NORMALIZE (examined 2026-11-09, API level)

WORKS, within a narrower trade than her registry line
("convert differing scales/forms to common basis") suggests.
Verified: Normalize rescales the WEIGHTS table so its entries
sum to exactly 1.0 — {a:2, b:1} -> {a:0.667, b:0.333} — each
weight becomes its SHARE of the whole. Failure honesty is
clean: an empty table, or a table whose weights sum to zero
({a:1, b:-1}), returns matched=False with error=zero_set and
leaves the table untouched — she refuses rather than dividing
by zero or inventing a basis. Scope note: today she normalizes
the weights table only — no other scale or form passes through
her. In the DD-48 world (SS12.65a) she is the natural
comparability step for universal weights: many assigners, one
rescaling to a common basis. No defect; the scope note is the
record.

### 12.65b DD-48 EXTENDED — THE INCORPORATION SWEEP (Ace ruling, 2026-11-09)

Ace: "once all of that stuff about weights and schema is all designed then
that means that we'll have to incorporate that with everything it can be
incorporated with like resonance and distances and anything that can be
weighed up."

RULED: after the quantitative family's core design (DD-46/47/48 +
DD-29 Schema) lands, an INCORPORATION SWEEP audits every subsystem for
weighable quantities and wires them into the one weight authority:
resonance values and their differences (DD-46 already names them),
Plane distances/positions, GRAVITY (the force field: wells,
intensity — including the G-04 sibling asymmetry item), HARMONY
(the harmonic engine of SS12.22: each idea's note, lattice
notes from position SS12.27, consonance/dissonance between
ideas), PERSPECTIVE (Ace, same ruling: "even perspective" —
quantities a perspective surfaces or computes are weighable
too; the lenses of SS12.22a change how the room is seen, and
what a lens reveals can still be weighed), PSALMS AND
PERSONAS (Ace, same ruling: "psalm perspective and personas,
all that" — what a docked Psalm's perspective surfaces, and
the persona layer's carried quantities, are weighable too;
BIMO stays descriptive metadata — its slots confer no
execution authority, SS12.52c — but what it carries as
numbers enters the sweep), growth heights,
token counts (SS12.29),
profile timings (DD-39), limits in force (DD-44) — anything the system
actually carries as a number. Each incorporated quantity becomes
weightable, normalizable (75), threshold-readable (73/DD-47), and
visible in Schema's body report. Same audit pattern as DD-44's Limit
sweep (SS12.63a): coverage claimed per-subsystem from tests, never for
the whole program at once; a quantity that cannot be incorporated
honestly is recorded with its reason, not silently skipped.

## 12.67 DELL 76 — RESOLVE (examined 2026-11-09, API level)

WORKS, and she carries a redemption story. Resolve answers
"which Dell is that?" — she looks a name or number up in the
active registry. Verified 4/4: 'Weight' -> hit, canonical name,
confidence 1.0; '62' -> hit, Parallel; 'Banana' -> honest MISS
(matched=False, confidence 0.0, error=missing); bare Resolve
-> matched=False, error=target_required. The atom itself stays
ok=True in every case — the result CELL carries the verdict,
the Get (56) precedent: asking is never the failure; the answer
may be "no such Dell." Reserved/not-active registry records
are honest misses, never hits. HISTORY (from her handler's own
comment, Step 10 / B11): she once resolved unknown labels
through a manifest fallback and published matched=True at
confidence 0.40 for ANYTHING — a confident liar. That path was
cut; today a miss is a miss. No defect.

### 12.67a DD-49 — RESOLVE BECOMES THE SEARCH ENGINE OF THE MATRIX (Ace ruling, 2026-11-09)

Ace expands Resolve (76): "Resolve should do more than that. Resolve
should be almost like a search engine for Dells — and not just Dells
but also a search engine for ideas within the matrix. So when I search
something I should pretty much be able to pull up like Google — for
the Dell Matrix."

RULED:
1. ONE SEARCH DOOR: a query goes in and results come back across BOTH
   Dells (the registry, with her honest hit/miss discipline intact)
   AND ideas (the whole field: Plane ideas, Nursery proposals,
   groups, saved material) — partial and in-piece, not only exact
   names.
2. RESULTS RANKED: result ordering composes with Rank (46) and Ace's
   switchable measure (SS12.35b) — search does not invent a private
   relevance; the DD-48 weight map is its natural signal.
3. NO SECOND AUTHORITY: Discover (35, DD-25 "Discover All") already
   owns browsing the field in organized pages with name/title
   search. Resolve-as-search and Discover must be ONE search
   machinery with two faces (query door / browse pages), settled in
   the design — not two competing indexes. The field reachability
   LAW (whole field reachable, system provides the names) is the
   constitutional basis.
4. The lookup honesty carries over: zero results is a calm, true
   answer; a search that cannot reach part of the field SAYS which
   part, never silently returns a partial field dressed as whole.

CURRENT TRUTH (verified SS12.67): Resolve today is an exact
name/number registry lookup only. The search engine is a
design+build direction, Director-routed.

## 12.68 DELL 77 — INFER (examined 2026-11-09, API level)

WORKS — and she is the most epistemically honest Dell on the
tour. Infer does not reason and does not discover: she takes a
stated conclusion and FILES it under the correct epistemic
class. Verified: Infer 'the field is warming' -> matched=False,
fact=False, projected=True, conclusion=the label, confidence
0.6 (a bare assertion's default). Truly fresh + bare -> conf
0.0. Her message line reads PROJECTED_NOT_FACT. Whatever passes
through her comes out stamped PROJECTION — she can never mint
a fact, never mark herself matched, at ANY confidence. This is
the chain-level twin of the dock law (model output lands as
PENDING proposals, never authority) and of the information
ladder (OBSERVED never collapses into LEARNED).
OBSERVATION (no ruling taken): confidence is inherited from
the prior result cell when one exists — after a conf=1.0
Resolve hit, a bare Infer carries conf=1.0 while asserting
nothing. The structural flags (fact=False, projected=True)
still carry the truth, so consumers honoring them are safe;
a consumer reading confidence ALONE could be misled. Recorded
for the design family; not a defect claim.

## 12.69 DELLS 78+79 — CAUSE AND DEPEND (examined 2026-11-09, API level)

TWINS, one mechanism (_relation), two ledgers: Cause records
"a > b" into st.causes ("a causes b"); Depend records into
st.deps ("a requires b"). Verified battery: valid pair ->
appended, matched=True. Malformed input (no arrow, or an empty
side) -> ok=False, error=malformed_relation, ledger untouched.
Self-relation ('rain > rain') -> refused, error=self_relation —
nothing causes or requires ITSELF in these books. Duplicate
pair -> the atom stays ok but the cell reports matched=False,
error=duplicate_relation, and the pair is NOT written twice —
the ledger stays a set of distinct claims. HONEST SCOPE: these
are RECORDED relations — a claim ledger, not a physics engine.
Writing 'rain > flood' does not make the program believe rain
causes floods (correlation/causation law); the pair sits in the
working state as a stated relation other Dells may consult.
Whether recorded cause/dep pairs should project into the
SemanticGraph as first-class edges is a design question for
the DD-48/DD-29 family (weighed relations) — not current
behavior, no ruling taken.

## 12.70 DELL 80 — CONTEXT (examined 2026-11-09, API level)

WORKS. Context sets the working-context register — the
"what are we talking about right now" pointer of the working
state. Verified: Context 'harbor' -> st.context='harbor';
bare Context falls back to the current scope (the room you
are standing in becomes the subject). The register is real
infrastructure: ForEach (66) points it at each member in turn
and restores it after (SS12.57), and the explicit-context
door used for human-confirmed relations reads it. HONEST
SCOPE: she accepts any string without validation — she is a
pointer, not a librarian; a context naming nothing real is a
label, not an error, until a consumer tries to resolve it.
No defect.
CROSS-CHECK (Ace order, 2026-11-09 — "check them across
everything"): Context is FULLY wired. Writers: the Dell
herself, chain constructs (chain_exec), ForEach's
borrow-and-restore (SS12.57). Readers: conditions can weigh
the current topic directly — the predicate engine's reserved
'context' operand resolves to st.context (context_ref).
Carriage: snapshots/Revert include her (spectrum_ops state
round-trip) and she PERSISTS across save/load
(persist_core_ii). Verdict: no missing function found.

## 12.71 DELL 81 — REFERENCE (examined 2026-11-09, API level)

WORKS. Reference pins a POINTER to a thing in the refs book
(st.refs: name -> target) and — her message says it outright —
makes NO COPY. Verified: with two ideas selected, bare
Reference points at the first selected unit; Reference
'external-thing-42' adds that pointer; the Plane's unit count
is unchanged afterward (2 before, 2 after). She is the working
mechanism underneath Inject's paste-by-reference law (DD-26,
SS12.24): one real thing, many pointers, no duplicates to
drift apart. Bookkeeping note from the same stop (Ace asked):
topic-changing is Dell 80 Context (SS12.70); 81 Reference is
the pointer — the two sit side by side in spectrum_ops and
are easily confused by number.

### 12.71a REFERENCE CROSS-CHECK — ONE MISSING FUNCTION (Ace order, 2026-11-09)

Same cross-check for Reference (81). WIRED: written by the
Dell and by chain machinery (DynamicFlow keeps refs['from']
and reads it back for its routing message); carried by
snapshots/Revert; PERSISTED across save/load (persist_core_ii
round-trips the whole refs book). MISSING: nothing in the
program can FOLLOW a pointer. The predicate engine has
operand kinds for count/context/selected/last_result/store —
no ref: kind; Inject (36), whose law Reference supposedly
implements (DD-26), never consults the book; no Dell
dereferences refs[name] to reach its target. Today the refs
book is write-and-keep state: durable, inspectable, and
inert. A reference nobody can follow is half a reference.
GAP RECORDED for the design family (DD-26 Inject completion /
DD-49 Resolve-as-search, whose engine is the natural
dereferencer): add a ref: operand kind and an Inject path
that resolves through the book. Not a defect ruling — a
completeness gap, recorded per Ace's instruction at this stop.

### 12.71b THE MAIN OBJECTIVE FOR DELLS (Ace, standing doctrine, 2026-11-09)

Ace states the constitutional purpose of the Dells: "make sure that
every last Dell is a tool that AI can use. That's the main objective
for Dells within this program." DOCTRINE: every Dell must be wieldable
by a docked AI (a Psalm) as a tool — reachable through the surfaces an
AI actually operates (the front door / chains / the dock), composable
with the other Dells, and returning receipts an AI can read and reason
over. A Dell that only works through human clicking, or only through
Uni's internal access, FAILS this objective no matter how well it
works there. This is the standard the tour's cross-checks enforce
(SS12.70/SS12.71a): wiring is judged by whether an AI's hand can close
around the tool. Every future Dell circuit inherits this test.

## 12.72 DELL 82 — GROUP (examined 2026-11-09, API level)

WORKS — and the 53<->82 partnership (SS12.42a) is now verified
END TO END. Group captures the current selection under a name
in st.groups. Verified: Select-all (4 units) -> Match 'alpha'
narrows to 2 -> Group 'alphas' stores exactly those 2 -> Scope
'alphas' aims the walls -> Select inside returns exactly the 2
group members. Group builds the collections; Scope aims at
them; neither does the other's job. Bare Group takes the name
'group'. One behavior to know: with an EMPTY selection, Group
captures the WHOLE Plane (her fallback reads the full id list)
— consistent with the family's empty-hand semantics but worth
stating, since an accidental empty-hand Group silently becomes
a group of everything. Groups persist (persist_core_ii) and
are snapshot-carried like the rest of the working state.
No defect.

## 12.73 DELL 83 — UNGROUP (examined 2026-11-09, API level)

WORKS. Ungroup dissolves a COLLECTION and releases its
members — the ideas themselves are never touched (verified:
Plane unit count unchanged across every case). Battery 4/4:
named existing group -> dissolved, members released (into the
selection when the hand is empty); named MISSING group ->
ok=False, error=ungroup_missing:<name>, every other group
untouched; bare Ungroup -> dissolves the LAST group; bare with
no groups at all -> refusal, ungroup_missing:empty. History
(her handler's comment, Step 10 / B12): a missing named group
once returned a silent released=0 SUCCESS — "no such group"
indistinguishable from an existing empty group — until that
repair made it an honest refusal. The twins 82/83 are a clean
pair: Group freezes a hand under a name (SS12.72); Ungroup
thaws the name and hands the members back. No defect.

## 12.74 DELL 84 — COPY (examined 2026-11-09, API level)

WORKS — in the STORE, not on the Plane. Copy duplicates a
Set/Get note under the name copy_<src>, deep-copied: verified
Copy 'level' (store level=5) -> copy_level=5; then Set
level=9 leaves copy_level at 5 — the copy is independent the
moment it exists ("original_intact" is her receipt line).
Bare Copy takes the first selected id as its source name. One
habit to know, from her code (store.get(src, src)): copying a
name that is NOT a store note copies the WORD itself —
copy_ghost='ghost' — consistent with the store's literal
habits (Dell 55's family), recorded here as observed behavior,
not endorsed design. Scope honesty: Copy does not duplicate
Plane IDEAS — idea-level duplication lives in Create/Macro's
copies (DD-38) and the DD-41 notebook; a Dell named Copy that
copies notes is narrower than her name suggests to a newcomer.
No defect claim; the scope note is the record.

## 12.75 DELL 85 — MOVE (examined 2026-11-09, API level)

WORKS — again in the STORE (Copy's neighborhood, SS12.74):
Move relocates a note from one key to another; the value keeps
its identity, the source key is gone ("identity_preserved").
Verified battery: Set cargo=77 -> Move 'cargo > vault' ->
store {vault: 77}, cargo gone. Move from a missing key ->
refused, error=move_missing, store untouched. Move onto
itself ('vault > vault') -> honest no-op success ("same
identity"). Malformed (no destination) -> malformed_move.
And the guard from her typed contract (DAF-01): when a flat
label could partition two ways, she REFUSES with
ambiguous_move and demands typed roles instead of guessing
which key you meant — the delimiter can never retarget a move
onto a colliding neighbor. Failing producers publish no
successful result (C2 discipline in her code: the result cell
carries the error, value=None). Scope note matches Copy's:
Move relocates notes; moving Plane IDEAS is another family's
work (cf. Bridge/Move semantics in Core I) — recorded, not a
defect claim.

### 12.75a DD-50 — MOVE MOVES ANYTHING MOVABLE (Ace ruling, 2026-11-09)

Ace: "it should be able to do both then. It should be able to move
things in the notebook and it should be able to move ideas on the
plane. As a matter of fact, Move should be able to move anything
that is movable."

RULED: Move (85) becomes the ONE relocation door for every movable
thing in the program — store notes (her current trade, SS12.75),
Plane ideas (repositioning), containment relations (nest/promote/
reparent), group memberships, refs, proposals between states —
anything whose location can change. Her existing virtues generalize
with her: identity preserved (the thing moved is the same thing,
receipt says so), ambiguity refuses instead of guessing, missing
source refuses, moving onto itself is an honest no-op. AUTHORITY
DISCIPLINE: Move is the DOOR, not a second engine — Plane positions
route through Map's coordinate authority (15), containment through
the SemanticGraph (TD-2's sole containment authority), placement
law stays Create's (08). One door, the same engines behind it.
CURRENT TRUTH: today she moves store notes only; the universal
door is a design+build direction, Director-routed.
ONE EXCEPTION (Ace, same ruling, minutes later): "It should be
able to move anything except the avatar body." The BIMO avatar
body is NOT a movable object — Move refuses it by class, not by
missing capability. The body is where a Psalm IS; everything
else in the program is furniture.
GOVERNANCE (Ace, same ruling, developed minutes later): Move is
"pretty much the Psalms' ability — the AI's ability to move
things throughout the program" — Move is a Psalm-wielded tool
under the SS12.71b doctrine, and the exception is restated in
its general form: Move moves everything EXCEPT THE PSALMS
themselves (a Psalm, its body, its person are never freight).
And when a Psalm wields her: "before anything actually gets
moved, it goes into the Nursery as a proposal" — an AI-initiated
move lands as a PENDING Nursery proposal naming the thing, the
source, and the destination; Ace's confirm executes it, exactly
the preview->proposal->confirm pattern of DD-43 (SS12.52b).
A move proposed is not a move made.

## 12.76 DELL 86 — DELETE (examined 2026-11-09, API level)

WORKS — store notes and groups; NOT Plane ideas. Verified:
Delete a store note -> gone. Delete a group name -> the
collection is dissolved from the book (its member ideas are
unharmed, cf. Ungroup SS12.73). Delete a Plane idea by name ->
refused, delete_missing — idea removal lives in Core I's
lifecycle, not here (scope note, matching Copy/Move SS12.74-75).
Delete a missing name -> ok=False, delete_missing:<name>.
Two design virtues in her code worth naming: (1) a SNAPSHOT is
taken BEFORE the deletion fires (shot_fn before the pop) —
Ace's snapshot-every-move law (DD-32) honored inside the
working state; (2) NO_AUTHORITATIVE_RESULT: deletion produces
nothing, so her result cell is deliberately value=None,
matched=False — an earlier result can never masquerade as
something Delete produced. She publishes an absence honestly.

ACE BOUNDARY (2026-11-09, at this stop): "delete should never
be able to actually delete the history or the full information
of something." RULED for Delete's whole family: deletion is
removal from the WORKING SET, never erasure of the record.
The history of a thing — that it existed, what it held, what
happened to it, the receipts — is not Delete's to destroy, at
any scope, for any caller. Current posture already leans this
way (snapshot before deletion, mutation notes, sealed
generation history); this ruling makes it a hard boundary the
family's design must prove, not a habit it happens to have.

## 12.77 DELL 87 — REPLACE (examined 2026-11-09, API level)

WORKS — the store family's careful renamer. Replace moves a
note's VALUE to a new key (old key retired), snapshot first,
under three refusals, all verified: ambiguous label ->
ambiguous_replace (typed roles demanded, as Move SS12.75);
missing source -> replace_missing:<old>; OCCUPIED destination
-> replace_occupied:<dest>, ZERO mutation — she will not
silently overwrite a neighbor to make room (MPC-012/MPC-011
ruling in her comments: occupied refuses by default, no
overwrite flag exists). Verified: draft=rough -> Replace
'draft > sketch' -> sketch=rough, draft gone; 'sketch > final'
with final=polished already home -> refused, both notes
intact. SIBLING OBSERVATION (recorded, no ruling): Move (85)
has NO occupied check — Move onto an existing key silently
overwrites it. Two sisters, two doctrines on the same
collision. Under DD-50 (Move universal), the family should
settle on one — Replace's refusal is the honest candidate.

## 12.78 DELL 88 — PATCH (examined 2026-11-09, API level)

WORKS. Patch modifies the VALUE of an EXISTING store note in
place, snapshot first: verified Set note='old draft' -> Patch
'note=new draft' -> store note='new draft', same key, nothing
else touched. Missing key -> refused, patch_miss:<key> — she
will not CREATE (creation is Set's job; a patcher who invents
her target is a liar). Ambiguous label -> ambiguous_patch,
typed roles demanded, the family armor (SS12.75/12.77).
CORRECTION TO THE RECORD (Uni owns this one): at Dell 57's
stop (SS12.47) Uni corrected "57 is Patch" by declaring Patch
"not a numbered Dell, typed seed-level operation only." That
correction overshot: Patch lives TWICE — as the DAF-01 typed
seed-level operation AND as numbered Dell 88 in Core II, the
registry's own row ("Partial targeted modification"). Both
facts stand; the earlier blanket denial is struck. With Patch,
the typed family 84-88 is fully examined: Copy, Move, Delete,
Replace, Patch — the store's five clerks, each with refusal
manners and snapshot discipline.

## 12.79 DELL 89 — DIFF (examined 2026-11-09, API level + front-door seed)

WORKS. Diff answers one question exactly: "what changed?"
She compares the STORE (the Set/Get notebook) as it is NOW
against a BASELINE — a captured picture of the store as it
was — and produces the exact CHANGE-SET: the list of keys
that were added, removed, or had their value altered. Her
full receipt lives in st.last_diff = {before, after, changed,
label, baseline}: both complete store pictures plus the
changed-key list, so old and new values are recoverable from
her own receipt. She publishes nothing into last_result; her
product has its own slot.

THE BASELINE LIFECYCLE (Step 9, B13/B14 — one lifecycle for
every writer, verified live this stop):
(1) Every store mutation — Set (55) and the clerks (84-88)
alike, through the shared _note_mutation authority —
captures the store AS IT WAS immediately before that write.
That capture is the baseline (baseline=immediate). So a
standalone Diff answers: "what did the LAST write change?"
Verified: Set alpha=1 -> Diff changed=['alpha']; Set beta=2
-> Diff changed=['beta'] only; Patch alpha=9 -> changed=
['alpha']; Delete beta -> changed=['beta'] (a removal is a
change, named by key).
(2) ONE STEP DEEP, honestly: two writes in a row, then Diff
shows ONLY the second (Set gamma=3, Set delta=4 -> changed=
['delta']). She is a one-step microscope, not a session log.
(3) TRANSACTION MODE: inside an open Try (93) frame, the
frame's checkpoint governs (baseline=transaction) and Diff
answers "what has changed since this transaction began?" —
verified: Try, then Set alpha=100 + Set eps=5 -> changed=
['alpha','eps'], every key since the frame opened. The
front-door seed check ran while the frame was still open and
Diff correctly kept the transaction baseline.
(4) NO BASELINE, NO STORY: with no capture in this session
Diff REFUSES — ok=False, baseline_missing, changed=None
(never a fake empty []), available=False. Verified as the
very first act on a fresh owner.
(5) READING NEVER TOUCHES THE BASELINE: Diff does not
capture, replace, or clear it — repeated reads return the
identical result (verified byte-identical).
(6) SESSION-ONLY: the baseline is NOT persisted. After
save/load, Diff refuses baseline_missing until the next
mutation captures a fresh one (verified) — a restored state
never fabricates a comparison (B14).

THE COMPARATOR (DIR-F15, Director-reviewed 2026-11-01):
a change is MEMBERSHIP difference OR value inequality. The
pre-fix comparator used plain .get(k) equality, which
conflates an ABSENT key with a key stored as None (both read
None) — a None-valued key added or removed vanished from
changed. Fixed at the one site in spectrum_ops.py; a key
present on both sides holding None is NOT a change. Suite
24/24; defect-restoring mutant 20/24 (only the four
membership witnesses). Her history: B13 was the gaslighting
diff (no baseline -> shrugged out an empty change-set, as if
nothing had happened); B14 unified the baseline lifecycle
across all writers. B13/B14 CERTIFIED WITH NOTED EXCEPTIONS
by the Director 2026-11-01 (merge 2abf04c).

SCOPE, stated plainly: Diff watches the STORE. Plane idea
changes are not her beat today. Her kinship: Mirror (18)
holds Ace's order for true compare/diff over Plane ideas
(SS12.51a family); Diff is the store-level change-set engine
that exists and is certified. What she feeds: the audit step
after any clerk writes (did Patch touch exactly one key?),
the pre-commit review inside a transaction (everything the
frame is about to change, named before it lands), and the
ANALYZE door of DD-32 — receipts like hers are what "what
broke / what changed" answers are built from. Against the
main objective (SS12.71b): she is fully AI-wieldable today —
front door and chains verified, receipt machine-readable.

## 12.79a ACE ON DIFF — LAST-MOVE ONLY, KEPT BY DESIGN (2026-11-09)

Ace confirmed Diff's shape and ruled on its memory:
(1) LAST-MOVE ONLY IS THE DESIGN, KEPT. The program does
NOT hold memory of all past diffs. No diff archive. Diff
keeps exactly what she keeps today: the baseline from the
most recent write and the latest computed record.
(2) THE RECORD, ONCE SET, IS THE RECORD WE HOLD. When Diff
runs, her result lands in the last_diff slot (before /
after / changed / baseline source). That single latest
record is what gets held, wherever it lives — the next Diff
run replaces it, and that is fine by design.
(3) VERIFY-AFTER-MOVE IS THE EXPECTED DISCIPLINE. Ace:

"after every diff then that should be checked and ran to
make sure that everything ran right." Verified status of
the machinery underneath: the BASELINE CAPTURE is fully
automatic — _note_mutation fires inside every writer (Set
55 via query_ops, clerks 84-88), after all refusal checks
and immediately before the mutation, so the comparison is
always armed and always fresh; a refused write captures
nothing and mutates nothing. What is NOT automatic today:
Diff herself runs when CALLED — no engine step auto-runs
her after every move and alarms on a mismatch. The
run-Diff-and-check habit is the standing discipline; an
automatic post-move verification step (compute the
change-set after a move/chain and check it against what
the move claimed) is recorded here as Ace's design intent
for the Diff circuit family, Director-routed, NOT current
behavior and not claimed as such.

## 12.79b DIFF ASSESSMENT — WHAT NEEDS COMPARING (2026-11-09, Ace order)

Ace: "diff should also do some other things too... assess
diff and the things that need to be compared." Assessment
grounded in the handler, the _ckpt authority, the writer
census, and a live invisibility probe (owner T89B*).

HEADLINE: THE PHOTO IS WIDE, THE COMPARISON IS NARROW.
_ckpt — the baseline picture every covered writer takes —
captures FOURTEEN slices: scope, selected, store, groups,
defs, aliases, compositions, weights, context, route,
refs, causes, deps, last_assert, last_guard. Diff compares
exactly ONE: store. Thirteen slices are photographed on
every covered write and never examined.

RING 1 — IN THE PHOTO, NEVER COMPARED. Content slices
(real data a write can change silently): weights, groups,
refs, causes, deps, defs, aliases, compositions. Working-
state slices (where you are standing): selected, scope,
context, route. Verdict ephemera: last_assert, last_guard.
Diff reading more of her own baseline is the cheap ring —
no new capture machinery needed for covered writers.

RING 2 — WRITERS WHO NEVER GET PHOTOGRAPHED. The
_note_mutation census: only Set (55) and the clerks
84-88 call it. These writers change checkpointed state
with NO baseline capture: Weight (74) and Normalize (75)
rewrite the weights table; Group (82) / Ungroup (83) write
groups; Reference (81) writes refs; Context (80) writes
context; Cause (78) / Depend (79) append to the ledgers;
Define / Alias / Compose write defs / aliases /
compositions. LIVE PROOF of the consequence (probe
T89B1B0999): Set alpha=1, then Weight gravity=2.5, then
Diff -> changed=['alpha'] and the gravity change is
INVISIBLE; then Group 'team', Reference, Cause rain>flood
-> Diff STILL answers ['alpha'], because the baseline was
never refreshed — Diff keeps retelling the last STORE
write's story while unwitnessed writes pile up behind it.
B14's law said "one baseline lifecycle for EVERY writer";
the census shows it covers the store writers only. Ring 2
is the integrity gap: these writers must join the one
_note_mutation door (no second capture authority), or
their changes stay unprovable — the exact failure class
Diff exists to kill.

RING 3 — TERRITORIES OUTSIDE THE PHOTO ENTIRELY (not in
_ckpt, not Core II store state): (a) PLANE IDEAS — creates,
edits, moves, growth, resonance changes; the biggest
territory; Mirror (18) already holds Ace's compare/diff
order for ideas, so coordination not duplication: one
comparison doctrine, two scopes, settled in design.
(b) NURSERY PROPOSALS — pending -> confirmed / rejected
transitions and proposal contents. (c) SEMANTICGRAPH
containment edges (TD-2 sole authority — Diff reads, never
becomes a second graph authority). (d) GENERATION vs
GENERATION — sealed checkpoint generations against live
state: "what changed since generation N" is a natural Diff
question the checkpoint machinery (SS12.31 snapshots,
checkpoint_generation.py) already stages. (e) FORCES —
gravity wells / evolution levels (G-04 round-trip family).

RECOMMENDED SHAPE (for Ace's ruling; a ruling here becomes
DD-51): Diff becomes the ONE comparison authority with a
SCOPE WORD — Diff of the store (today), of the weights,
of the groups, of the whole Core II checkpoint (Rings 1+2
together: every writer photographed, every content slice
compared), and in transaction mode the same widened lens
against the frame checkpoint. Ring 3 items join one at a
time as their own bounded scopes, Mirror coordination
first. The honesty rules do not move: no baseline -> the
wider Diff refuses baseline_missing too; last-move only
per SS12.79a (no archive); a slice she cannot compare is
NAMED as unexamined, never silently skipped — silent
skipping is the B13 gaslight in a new dress. Assessment
only; no build authorized by this section.

## 12.79c DD-51 — DIFF BECOMES THE ONE COMPARISON AUTHORITY (Ace ruling, 2026-11-09)

Ace, on the SS12.79b assessment: "Yes, that sounds about
right." RULED:
(1) ONE COMPARISON AUTHORITY, AIMED BY A SCOPE WORD. Diff
is the program's comparison engine, not a notebook-only
tool. She runs ON what she is aimed at: Diff of the store
(today's behavior, kept), Diff of the weights, of the
groups, of the refs, of the ledgers, of the definitions —
and Diff of the WHOLE Core II checkpoint. Ace: "I should
be able to run diff on it" — anything in the program that
can change can be diffed, and Diff is who runs it.
(2) RINGS 1+2 ARE ONE FIX. Every writer walks through the
one _note_mutation door — Weight (74), Normalize (75),
Group (82), Ungroup (83), Reference (81), Context (80),
Cause (78), Depend (79), Define / Alias / Compose join
Set (55) and the clerks (84-88); NO second capture
authority. And Diff compares every CONTENT slice in the
photo (store, weights, groups, refs, causes, deps, defs,
aliases, compositions), in standalone last-move mode and
in transaction mode alike. Working-state slices
(selected, scope, context, route) and verdicts
(last_assert, last_guard) are compared when the whole-
checkpoint scope is named.
(3) RING 3 JOINS ONE TERRITORY AT A TIME, each as its own
bounded scope in later circuits: Plane ideas FIRST in
coordination with Mirror (18) — one comparison doctrine,
two scopes, no duplicate engine; then Nursery proposal
state; then SemanticGraph containment (read-only —
SemanticGraph stays sole containment authority, TD-2);
then generation-vs-generation against the checkpoint
machinery; forces quantities ride the DD-48 sweep.
(4) THE HONESTY RULES DO NOT MOVE. Last-move only, no
diff archive (SS12.79a). No baseline -> the widened Diff
refuses baseline_missing, for every scope. A slice or
territory she cannot yet compare is NAMED as unexamined
in her receipt — never silently skipped. The record she
sets is the record held (last_diff, widened to carry
per-slice change-sets under the named scope).
(5) VERIFY-AFTER-MOVE (SS12.79a part 3) rides this
directive: the automatic post-move check — compute the
change-set after a move/chain and check it against what
the move claimed — is designed as part of the DD-51
circuit family, not as a separate mechanism.
STATUS: design directive recorded in the plan at Ace's
order. Implementation routes through the Director as a
bounded circuit family (Rings 1+2 first), one circuit at
a time per the completion-first order; nothing in this
section is built yet, and today's Diff remains the
store-only Dell verified in SS12.79.

## 12.80 DELL 90 — TRACE (examined 2026-11-09, API level + front-door seed)

WORKS, as the session's execution log reader. ONE writer:
mark() inside execute_core_ii appends one line for every
Core II atom that executes — format NN[Name]::label
(verified through the front door: '55[Set]::alpha=1',
'74[Weight]::gravity=2.5'). Single-writer authority, no
side doors. Her display shows the LAST 8 entries; her
receipt (last_result) carries the FULL list plus count,
matched=True — the window is small, the record is whole.
Fresh owner: calm "(empty)", count 0, ok — no refusal
(contrast Diff's baseline_missing: an empty log is a true
answer, not a missing comparison).

VERIFIED BEHAVIORS:
(1) REFUSED ATOMS ARE LOGGED. A patch_miss Patch still
left its entry (probe: traces grew by 1, entry present).
The log records ATTEMPTS in order — but entries carry NO
outcome mark: a refused Patch and a landed Patch read
identically ('88[...]::...'). Outcomes live in the
receipts of the moment, not in her lines.
(2) TRACE LOGS HERSELF — one step late. mark() runs after
the handler, so her report never includes her own current
call; the NEXT Trace shows the previous Trace's entry
('90[Trace]::' verified in the post-chain log).
(3) SHE CANNOT BE AIMED. A label filters nothing: Trace
'alpha' returned the whole log (count grew by her own
entry only). "Show me everything that touched THIS value"
is not answerable today — entries are not indexed by key
or by Dell. Her registry line ("Follow provenance /
execution / data path") is TRUE for the execution path —
what ran, in what order — and NOT yet true for per-value
provenance: which atom produced this value, from what,
is recorded nowhere in the entry.
(4) BOUNDED MEMORY, COUNTED LOSS. Cap 512 entries
(TRACES_CAP); oldest drop off, and the drop is counted
by traces_dropped_total (AF-5 heritage) — within a
session, loss is never silent, only bounded.
(5) SESSION-ONLY. traces are absent from CORE_II_DURABLE:
save/load and the store survives (verified alpha=9 kept)
while the log resets to empty. Provenance does not cross
a restart. The whole Core II witness layer is uniformly
session-scoped: Diff's baseline, Trace's log, snapshots,
tx frames.
(6) SANITIZE INTERPLAY (DAF-02 Step 3b, from her writer's
code): under a Sanitize chain's redaction flag, trace
labels are sanitized for display while the handler
executed with the real label — her log is DISPLAY
evidence. Snapshots are deliberately NOT sanitized
(Step 3c) because Revert executes from them.
(7) CORE II ONLY. Core I atoms never enter this log;
mark() also feeds the program-level note_seed history,
which is a different book.

KINSHIP: Diff (89) says WHAT changed in the last move;
Trace (90) says WHAT RAN, in what order, this session.
Together they are the evidence the DD-32 ANALYZE door
reads. OBSERVED GAPS (recorded, no ruling taken): outcome
marks on entries; aiming/filtering by key or Dell;
per-value provenance. If Ace rules on any of these they
join the DD-51 comparison/witness family in design.

## 12.80a DD-52 — TRACE COVERS THE ENTIRE CURRENT PROCESS (Ace ruling, 2026-11-09)

Ace: "When you use trace she should be able to trace
back the entire current process. For the entire current
process." RULED:
(1) COMPLETENESS WITHIN THE PROCESS IS THE CONTRACT.
When Trace is called, she must be able to walk back the
ENTIRE current process — from its start to now — not a
recent window dressed as the whole. The last-8 display
stays a display choice only; retrieval of the full
process must actually reach the beginning (bounded
fetching underneath is fine, per the field-reachability
pattern — it must not feel like a wall).
(2) COVERAGE = THE WHOLE PROCESS, NOT CORE II ONLY.
Today her log holds Core II atoms only (SS12.80 (7)).
The entire current process includes Core I atoms, chain
structure, and front-door executions as they happened.
The design must establish ONE writer census for the
process log — every execution surface accounted for,
no silent unwitnessed lane (the DD-51 Ring-2 lesson
applied to testimony). Which program-level books
(note_seed history and kin) merge into or feed the one
process log is settled in design; a second competing
log authority is not created.
(3) THE 512 CAP MUST RECONCILE WITH "ENTIRE." A process
that outgrows its log cannot claim an entire trace.
The bounded-store counter (traces_dropped_total) stays
as honest bookkeeping, but under this ruling the design
owes an answer — carry the whole current process, or
the limit is surfaced as a stated boundary of the trace
itself (DD-44 explicitness pattern: stated, never
silent). Pretended completeness is the B13 failure in
testimony form and is prohibited.
(4) SCOPE WORDS: "current process" is Ace's boundary —
session/process lifetime. SS12.80 (5) stands: testimony
does not cross a restart, and this ruling does not ask
it to. What changes is that WITHIN the process, the
trace is whole.
(5) The SS12.80 observed gaps (outcome marks, aiming,
per-value provenance) remain recorded under this
section; a faithful walk-back of the entire process is
the ground they stand on, and any Ace ruling on them
joins the DD-51/DD-52 witness family in design.
STATUS: design directive recorded at Ace's order;
Director-routed with the witness family; not built.
Today's Trace remains the Dell verified in SS12.80.

## 12.80b DD-52 AMENDED — TRACE FOLLOWS THE CURRENT PROCESS; SHE IS NOT HISTORY (Ace, 2026-11-09)

Ace, minutes after DD-52: "when you change processes
then trace changes to update that full current process...
that's not history, that's things that have happened in
this session." RULED, amending SS12.80a:
(1) PROCESS-FOLLOWING. Trace's subject is always the
CURRENT process. Change processes — a new process, a
new session — and her book becomes THAT process's book,
in full: complete for the process now running. No
blending of two processes into one log; no lines carried
over from a previous process into the new one's trace.
(2) TRACE IS NOT HISTORY. Her jurisdiction is exactly
"things that have happened in this session." She is
session testimony, not the durable historical record —
history belongs to the machinery built for it (sealed
generations, checkpoints, the records). This blesses
SS12.80 (5) as DEFINITION rather than limitation: the
session-only scope verified today is her correct shape;
what DD-52 changes is completeness and coverage WITHIN
the session she serves, and that she always serves the
process that is current when she is called.
(3) "Entire current process" (SS12.80a) and "changes
when the process changes" (this section) read together:
one process, one whole trace, always the live one.

## 12.81 DELL 91 — ASSERT (examined 2026-11-09, deep battery: API + chains + transactions + persistence)

WORKS — the program's judge. Assert takes a CLAIM (a
condition), evaluates it against current state through
the shared judge (control_runtime.eval_condition -> the
predicate engine), and stamps the verdict. She writes
nothing else: verified, the store is byte-identical
across PASS and FAIL asserts. A judge, not a writer.

HER GRAMMAR, exactly:
- Bare Assert -> the claim defaults to "true" -> PASS.
- Literal verdict words (case-insensitive): pass / true /
allow / ok / yes (and empty) judge TRUE; fail / false /
block / deny / no judge FALSE.
- Real conditions ride the predicate engine in PREFIX
grammar with the full operand set (store, weights,
reserved count / context / selected): verified with
store level=5 — 'gt:level 3' PASS, 'gt:level 99' FAIL.

THE STAMP: st.last_assert = PASS / FAIL, sticky — only
another Assert overwrites it. The stamp is DURABLE:
last_assert sits in CORE_II_DURABLE and in _ckpt, so it
survives save/load (verified: reload kept the PASS stamp)
and is captured by snapshots — unlike Diff's baseline
and Trace's log, her verdict crosses restarts. She does
NOT publish into last_result: her verdict channel is the
stamp itself (verified: the returned result cell after
an Assert carries nothing from her).

THE TEETH — A FAIL IS A FAILURE, IN THREE PLACES:
(1) THE ATOM: ok=False, err=assert_fail.
(2) THE TRANSACTION: a FAIL fires the canonical outcome
hook (note_atom_failure, B15/B16) and marks the
innermost open Try frame FAILED — verified end to end:
Try -> Set -> Assert false -> Commit REFUSED
(commit_illegal, "Commit illegal from failed"); the
clean twin — Try -> Assert PASS -> Commit accepted.
Her stamp can starve a transaction to death.
(3) THE CHAIN — VERDICT-LEVEL, NO HALT (72-27,
Director-confirmed): a failed Assert mid-chain under a
plain > records the failure (chain ok=False) and LATER
ATOMS STILL RUN AND MUTATE — verified: c1=1 landed,
Assert false, c2=2 landed. The halt, when wanted, is
the chain's FlowThru (>>) operator: verified, the atom
after a failed Assert under >> is SKIPPED. Inside
control blocks her verdict propagates: the block's Join
reports the failure (join_fail); an Assert in an
unchosen Branch arm never evaluates and leaves no stamp
(72-27 evidence). Q-72-27.1 stands: these semantics are
RULED, not a defect — no Assert-specific halt will be
introduced.

SUPERSESSION NOTED: the 2026-10-30 C22 exhibit "only
Assert/Guard failures mark a tx frame failed" no longer
holds — since B15/B16 the canonical hook fires for EVERY
executed atom failure (core_ii_exec on any ok=False;
chain_exec for leaf failures), first root cause
preserved in frame["error"], later failures recorded in
extra_errors. Assert's distinction today is not unique
access to the hook; it is that her failure is a JUDGED
VERDICT — a claim found false — rather than an
operational error.

DD-42 CONFIRMED LIVE ON ASSERT (this stop): with store
level=5, Assert 'level gt 99' — INFIX grammar — returned
PASS. The infix form matches no predicate prefix, so
eval_condition's underlying predicate falls through to
truthiness of the first token and never reads the
operator or the 99. Assert will stamp PASS on a claim
that is numerically FALSE when the claim is phrased
infix. This is exactly DD-42's named blast radius
(Compare / Branch / Guard / Assert share the judge);
the fix family is unchanged: refuse honestly or parse
infix genuinely, never degrade silently. Prefix grammar
is exact (battery above); the defect is the silent
fallback, and on the judge Dells it is at its most
dangerous, because their whole product is the verdict.

KINSHIP: Guard (92) is her twin — same judge, ALLOW /
BLOCK stamp (last_guard, also durable), guard_block
error; Dell 92's stop examines her own wording law
('block' / 'deny' as labels force BLOCK). Together
91/92 are the verdict pair whose stamps Diff's widened
lens (DD-51) will compare under the whole-checkpoint
scope.

## 12.82 DELL 92 — GUARD, AND THE VERDICT PAIR TOGETHER (examined 2026-11-09, deep battery: API + chains + transactions + persistence + idea-facing chains)

WORKS — Assert's twin in a bouncer's uniform. Guard
judges the SAME claims through the SAME judge
(eval_condition -> predicate engine) and stamps
st.last_guard = ALLOW / BLOCK (default ALLOW). Verified
battery: bare Guard -> ALLOW ("default"); 'gt:level 3'
(level=5) -> ALLOW; 'gt:level 99' -> BLOCK, ok=False,
err=guard_block. THE FORCE WORDS: the labels 'block' and
'deny' force BLOCK twice over — eval_condition already
judges them false literals, and her handler overrides to
False again on an exact match. Belt and braces; same
result either way.
TEETH, IDENTICAL TO ASSERT: a BLOCK fires the canonical
hook and poisons the innermost Try frame — verified:
Try -> Guard block -> Commit REFUSED (commit_illegal).
STAMPS ARE INDEPENDENT AND BOTH DURABLE: Assert FAIL
left last_guard untouched; Guard ALLOW left a standing
last_assert=FAIL untouched; after save/load BOTH stamps
survived (last_guard=BLOCK, last_assert=FAIL) — the pair
are separate witnesses, each keeping her own last word.
Like Assert, she publishes no last_result; the stamp is
her channel. Like Assert, she mutates nothing else.

THE NAME VS THE REALITY (the open wording debt): her
registry line reads "Prevent execution unless conditions
hold." She does NOT, by herself, prevent the next atom:
in a plain chain the atom after a BLOCK still runs and
mutates (72-27, verified at the While-body composition —
the guarded Delete ran). The Director ACCEPTED the
verdict-level semantics (Q-72-27.1) and parked the
wording correction as a separate hygiene circuit; it is
still open. Prevention is real only IN COMPOSITION:
(a) Guard + FlowThru (>>) — the next atom is SKIPPED on
BLOCK (verified at SS12.81 for Assert, at this stop for
Guard); (b) Guard inside Try — BLOCK poisons the frame
and Commit refuses, so the deal cannot close; (c) Guard
inside a control block — her verdict propagates to the
Join. Read her registry line as the composition she
belongs to, not a solo power.

THE PAIR, SIDE BY SIDE (one judge, two uniforms):
ASSERT (91): asks "is this claim TRUE?" — the language
of proof. Stamp PASS/FAIL, error assert_fail. Used to
REQUIRE that the world is as expected before the result
is trusted.
GUARD (92): asks "may this PROCEED?" — the language of
permission. Stamp ALLOW/BLOCK, error guard_block, plus
the force words block/deny. Used to GATE an action on
its preconditions.
Same engine, same grammar, same teeth, same durability;
the difference is the question being asked and the stamp
other machinery reads.

TWO SHARED TRAPS, BOTH VERIFIED AT THIS STOP:
(1) DD-42 INFIX: Guard 'level gt 99' (level=5) -> ALLOW.
The bouncer waves through the same false claim Assert
certified. One judge, one silent-truthiness fallback,
two uniforms lied to. Fix family unchanged (DD-42).
(2) BARE WORDS ARE NOT LOOKUPS. Guard 'gate' with
gate=open in the store -> ALLOW; Guard 'nosuchkey' with
NO such key anywhere -> ALSO ALLOW. A bare word judges
the truthiness of the word itself (the predicate's
truthy fallback; unknown words resolve to literal), it
never checks existence. 'exists:gate' does not rescue
this: verified ALLOW with gate missing — the word
resolves to a literal token, whose type is never
"missing," so exists reports true for any word. The
honest existence instrument is Get (56) — matched=false
names a miss. Do not build gates out of bare words.

THE CHAIN-USAGE LAW — LABEL INHERITANCE (AF-2), found at
this stop and worth the whole dig: an atom's effective
label is its OWN segment label if it has one, else the
SEED's label — and the seed's label is the LAST segment's
label (seed.py's own comment; chain_exec._eff_label).
Consequence, verified by bisection: end a chain with a
labeled verdict Dell and every BARE atom upstream
inherits that label as its payload. 'Create > Select >
Assert gt:count 1' failed with Select scope=plane n=0 —
not a plane split, not an Assert defect: the bare Select
inherited 'gt:count 1' as a NAME PATTERN, matched no
idea, selected nothing, and Assert honestly judged
count=0. Give the atom its own label and the identical
chain runs clean (below). Historical grammar, documented
in the parser, invisible from the receipts unless you
know it — the tour records it as the standing rule for
mixed chains: IN A CHAIN, EVERY ATOM THAT NEEDS ITS OWN
MEANING CARRIES ITS OWN LABEL; a bare atom means "give
me the seed's trailing label," whether you meant that
or not.

HOW THE PAIR IS USED WITH IDEAS — VERIFIED PATTERNS:
(1) THE CHECKPOINT (Assert): gather ideas into the hand
(Select / Filter), then Assert on the hand itself via
the reserved count operand. Verified end to end:
Select 'harbor' (1 idea in hand) > Assert 'gt:count 0'
-> PASS, chain ok. The claim is about the IDEAS IN HAND:
"we are holding at least one harbor idea" is a judged,
stamped fact.
(2) THE GATE (Guard + FlowThru): Select 'harbor' >
Guard 'gt:count 0' >> Set proceeded=yes -> ALLOW, the
Set LANDED (verified). The empty-hand twin: hand at
zero -> Guard BLOCK, the Set was SKIPPED, chain failed
honestly. This is the program's working door-lock for
idea operations: the operation after >> happens only
if the hand (or any judged condition — weights,
resonance-side store facts, context) says it may.
(3) THE VETO (either twin inside Try): stage work in a
transaction, let a verdict judge it before Commit; a
FAIL/BLOCK makes Commit refuse (verified for both).
The verdict pair are how a chain — human- or
Psalm-driven — says "prove it before I trust it" and
"not unless this holds" about ideas, with stamps that
outlast the session and receipts (Trace 90, Diff 89)
that show exactly what was judged. That is the pair's
seat in the main objective (SS12.71b): they are the
cheapest quality gate a docked AI can put inside its
own chains.

## 12.83 DELL 93 — TRY (examined 2026-11-09, API battery with frame introspection)

WORKS — the transaction family's door. Registry: "Begin
recoverable/failable operation," and that is exactly the
size of her promise: she opens a FRAME; she does not
promise the work inside is safe, staged, or undone.
Verified mechanics:
(1) OPENING: Try appends a frame to st.tx — mechanical
id (tx0, tx1, ...; a label is ignored), status "open",
depth = count of currently active frames, and a FULL
_ckpt checkpoint of Core II state captured at the door.
st.try_depth syncs to the active-frame count.
(2) NO ISOLATION — WRITES ARE LIVE IMMEDIATELY: verified,
a Set inside Try is readable by Get BEFORE any Commit,
and a Patch lands the same way. Try is not a staging
room; it is a witnessed room. The frame's staged_changes
ledger records the writes as they happen — and since
B14's one-authority repair, Set (55) is recorded
alongside the clerks (verified ledger: set, then patch).
SUPERSESSION: the 2026-10-30 C22 exhibit "staged_changes
records ONLY spectrum mutations 84-88, never Set" no
longer holds. The exhibit's other half STANDS and is
her defining honesty: Commit is mark/accept, not atomic
staging — the registry never promised her isolation,
and she has none.
(3) FAILABLE, NOT SELF-HEALING: an Assert FAIL inside
flips the frame to status "failed" with the first root
cause in frame["error"] (assert_fail) — and NOTHING
rolls back. Verified: after the failure, the patched
value ('live') is still in the store, still readable.
Recovery is somebody else's job: Catch (94) consumes
the failure, Revert (96) restores the checkpoint,
Commit (95) refuses a failed frame. Try alone leaves a
failed frame and live changes, indefinitely.
(4) NESTING / LIFO: Try inside Try opens depth 1 (even
inside a failed frame's shadow — verified); Commit
accepts the INNERMOST active frame first. Frame
statuses: ACTIVE = open / failed / caught; TERMINAL =
committed / reverted. A failed frame still counts as
active (it awaits Catch, Revert, or abandonment); it is
never pruned while active. Terminal frames are kept to
the newest 16 (TERMINAL_TX_KEEP, AF-5); pruned count in
tx_dropped_total keeps ids monotonic for the session.
(5) SESSION-ONLY FRAME, DURABLE WORK — the sharp edge:
tx frames are absent from CORE_II_DURABLE. Verified:
save/load with frames open (one failed, one committed,
one open) -> after reload, ZERO frames, try_depth 0 —
and the store kept the uncommitted transaction's
changes ('live'). If a session ends mid-deal, the deal
is forgotten and the changes stay. There is no rollback
fairy at the persistence boundary; a Try left open is a
deal the next session never heard of, written in ink it
keeps.
(6) HER TENANTS: while a frame is open, Diff (89) reads
HER checkpoint as the baseline (transaction mode);
Assert/Guard (91/92) failures land in her frame through
the one canonical hook; _note_mutation logs each write
to her staged_changes. She is the room the whole
witness family works in.
Family map for the coming stops: 93 Try opens, 94 Catch
consumes a failure, 95 Commit accepts, 96 Revert
restores the checkpoint. Her registry line is honest as
written: recoverable (the checkpoint exists) and
failable (the frame can fail) — a frame, not a vault.

## 12.84 DELL 94 — CATCH (examined 2026-11-09, API battery + full transaction chain)

WORKS — the transaction family's forgiver. Registry:
"Handle failure/error class." What she actually does,
verified end to end: Catch takes the INNERMOST active
frame's PENDING failure and CONSUMES it — the frame's
error slot is emptied, the error moves into the frame's
archive (caught_error = the latest, caught_history =
every catch in order), and the frame's status becomes
"caught", from which Commit may legally close.
(1) NO FRAME, NO CATCH: with no active frame she
refuses — ok=False, catch_illegal (verified).
(2) NOTHING TO FORGIVE: on a clean open frame she
answers "Catch (no error)", ok=True, and touches
NOTHING — status and error stay exactly as they were.
(3) FORGIVENESS IS NOT UNDOING: verified — Try, Set
work=1, Assert false, Catch: frame caught, and the
store STILL holds work=1. She removes the failure's
power over the frame; the work done inside stands
exactly as it landed. Undo belongs to Revert (96)
alone.
(4) NO DOUBLE-CATCHING (B16-C, verified): a second
Catch finds the pending slot empty, answers "(no
error)", and the archive is unchanged — a consumed
error can never be caught twice.
(5) NOT SELECTIVE, DESPITE THE REGISTRY WORDING: her
label is never consulted. Verified: a frame failed with
guard_block, Catch labeled 'assert_fail' — she consumed
guard_block anyway and her message named the ACTUAL
error ("Catch guard_block"). She handles THE failure,
whatever class it is; "error class" in her registry
line is the same species of wording debt as Guard's
"prevent execution" (SS12.82) — behavior ruled and
accepted, wording awaiting its hygiene circuit.
(6) THE ARCHIVE IS APPEND-ONLY EVIDENCE: a failure
AFTER a catch becomes a NEW pending root cause on the
same frame (verified: patch_miss:ghost after a caught
guard_block); a second Catch consumes it; the history
grows [guard_block, patch_miss:ghost] and caught_error
updates to the latest — earlier catches are never
erased or resurrected (DIR-F14: pending and consumed
are distinct state).
(7) INNERMOST ONLY: nested frames — Catch consumed the
inner frame's failure; the outer frame stayed open and
untouched (verified).
(8) SHE FORGIVES THE FRAME, NOT THE RECORD — chain
truth, verified by seed: Try > Set a=1 > Assert false >
Catch > Commit ran every atom, committed the frame,
landed the work — and the CHAIN still reports ok=False,
err=assert_fail. The failure remains the chain's
reported outcome (72-27 semantics). Catch changes what
the failure can still DO (block a Commit), never what
the record SAYS happened.
HER HISTORY: B16 — she once read the sticky global
last_error, so she could "catch" an error from before
the transaction existed, even a commit_illegal raised
on the same frame, overwriting the true root cause;
B16-C — consecutive Catches re-consuming one error.
Both repaired in Step 8 (2026-11-01) by the frame-owned
pending slot + archive design verified above. Her old
C22-era description ("marks frame caught and records
st.last_error") is superseded: last_error is not her
book anymore; the frame's own slots are.

## 12.84a DD-53 — ROOMS ARE ACE'S TO CLOSE; THE SESSION WARNS BEFORE IT ENDS (Ace ruling, 2026-11-09)

Ace, across the Try/Catch conversation, in his words:
rooms stay TEMPORARY ("we want to keep them
disappearing... people can make decisions right now and
the idea can move forward"); he can have MULTIPLE rooms
open at the same time; rooms must NOT close just
because he is outside them — HE decides when his rooms
close; before the session closes, the session WARNS him
that rooms are still open and will not be saved, and
asks whether he is sure; and Bridge should be able to
bridge rooms together. RULED:
(1) TEMPORARY, AFFIRMED. Rooms (Try frames) remain
session-only by design (SS12.83 (5) becomes definition,
as with Trace SS12.80b). No persistence for frames is
to be built under this directive.
(2) MULTIPLE ROOMS, OWNER-CLOSED. Current truth,
stated exactly: frames already persist for the whole
session and NEVER auto-close mid-session (verified
SS12.83/12.84 — frames sat open across unrelated work);
but they form a LIFO NEST, and Catch / Commit / Revert
can only ever address the INNERMOST. DD-53 requires
rooms to be INDIVIDUALLY ADDRESSABLE (by id, and
findable through the DD-49 search door): Ace opens
several rooms, leaves them, returns, and closes the
one HE chooses. The nest may remain the opening order;
closing order becomes the owner's decision. Design
settles the mechanics (a current-room pointer vs a
room set); no second frame authority.
(3) THE SESSION-CLOSE WARNING. No warning exists today
(verified: no frame check on the save / REPL-exit
paths; frames evaporate silently, SS12.83 (5)). DD-53
requires: before a session ends, if rooms are still
active, the program WARNS — naming each open room (id,
status, what it has staged) — states plainly that the
rooms will not be saved, and requires explicit
confirmation before closing. The natural home is the
session-closing ceremony beside Alpha (20), whose
standing ruling already requires closing to save a
full checkpoint including history: one ceremony — save
the checkpoint, warn on open rooms, confirm, close.
(4) BRIDGE BETWEEN ROOMS. Bridge (44) gains a
room-to-room mode: connecting two OPEN rooms so
information can flow between them, under her standing
law (DD-34): she keeps the record of it, and BEFORE
opening she PREVIEWS what would flow and what could be
affected. The natural preview instrument is DD-51's
lens aimed room-vs-room: the Diff between two rooms is
what a bridge between them would carry. What actually
flows (staged state, copies by reference per DD-26, or
proposals) is settled in the Bridge design session —
inbound-to-a-room material lands as the room's staged
work, never silently merged into live state outside
the room's own ledger.

## 12.84b ASSESSMENT — DELLS THAT CAN BE USED WITH ROOMS (Ace order, 2026-11-09)

Ace: "you have to assess Dells that can be used with
it... Maybe sandbox... mirror or parallel... There's a
lot of different Dells." Assessment, grounded in this
tour's verified behavior:
ALREADY NATIVE (verified at SS12.79-12.84): Diff (89)
reads the room's photo as her baseline — she is the
room's inspector today. Assert / Guard (91/92) deliver
their verdicts INTO the room (a failed verdict is the
room's failure). Every writer feeds the room's ledger
through the one _note_mutation door. Catch / Commit /
Revert (94/95/96) are the room's own sisters. Trace
(90) logs the work done inside rooms — GAP: her lines
carry no room id, so the log cannot yet say which room
a line happened in; under DD-52 (entire current
process) room open / close / boundary marks belong in
her log.
SANDBOX — THE HONEST ANSWER: there is NO Dell named
Sandbox. The sandbox concept exists in three forms:
(a) Dell 23 Lock carries the sandbox SWITCH — it sets
sandboxed=True over every live unit ("Sandbox ON/OFF",
registry + executor_leaf); a switch over units, not a
room. (b) Dell 17 Shadow — "Background parallel," the
not-live track: work that runs without being live.
(c) THE PATTERN THAT WORKS TODAY: Try + Revert IS a
sandbox — open a room, do real live work, tear it up
with Revert and the photo restores; Try + Commit is
the same room kept. A room opened while Lock's sandbox
switch is ON is the natural composition (live work,
sandboxed units, owner-closed) — recorded as the
sandbox direction: no new Dell; rooms + the existing
switch + Shadow's not-live doctrine compose it.
STRONG CANDIDATES: Mirror (18) — a ROOM'S-EYE VIEW:
show the room as it was at its photo vs as it is now —
Diff in picture form, and the compare Mirror already
owes (SS12.51a); under DD-43 her isolated-arm
reflections are the same idea in another uniform.
Parallel (62) / DD-43 — arms are room-shaped: isolated
copies + a Join merge is architecturally a set of rooms
with a merge-closing; the DD-43 design and the room
family should be ONE mechanics, not two competing
isolation stories. Simulate (31) / DD-21 — a rehearsal
IS a room you always Revert: Try + run + Diff + Revert
is a truthful dry-run engine, and Simulate's report is
the room's Diff; candidate implementation shape for
DD-21. Retry (42) / DD-32 — retry INSIDE a room: a
failed attempt is caught in-frame and re-attempted, or
the room is reverted and the attempt rerun clean; the
room is what makes "try again" safe to mean anything.
Macro (48) / DD-38 — her notebook is the COPIES room;
Try rooms hold LIVE work. Complementary, not rivals:
rehearse on copies in Macro's room, witness the real
thing in Try's. Alpha (20) — the session-closing
ceremony (see DD-53 (3)). Resolve (76) / DD-49 — rooms
become findable, addressable citizens of the search
door. Group (82) — naming a SET of rooms is recorded as
an open question, not a claim.
Assessment only, with DD-53; builds route through the
Director with the transaction / witness family.

## 12.85 DELL 95 — COMMIT, AND COMMIT vs ALPHA (examined 2026-11-09, API battery; Alpha handler read)

WORKS — the transaction family's closer. Registry,
repaired by B17 into plain honesty: "Mark/accept
current live state (live mark/accept only — no atomic
isolation, no staging area; Revert covers only the Try
checkpoint fields)." Verified mechanics:
(1) WHAT SHE DOES: Commit flips the INNERMOST active
frame from open or caught to "committed", files
frame["accepted"] = a DEEP COPY of the whole current
store as it stands at that moment, and appends
{op: commit, id, accepted: True} to the program-level
st.staged ledger. try_depth drops accordingly.
(2) WHAT SHE DOES NOT DO: she applies NOTHING (the
work inside the room was live from the first keystroke,
SS12.83), saves NOTHING to disk (no persistence call —
durability remains the ordinary save path's job), and
creates no isolation retroactively. Commit is a
signature on a deal already in effect, not the moment
the deal takes effect.
(3) THE ACCEPTED COPY IS A TRUE SNAPSHOT OF THE
SIGNING MOMENT: verified — after committing
{a: 1, b: 2}, setting a=99 left the live store at 99
while frame["accepted"] still reads {a: 1, b: 2}. The
copy is deepcopy; later work cannot rewrite what was
signed.
(4) HER REFUSALS DISTINGUISH THE TWO WAYS TO BE WRONG:
no frame ever opened -> commit_without_try; frames
exist but none active (all terminal) -> commit_illegal;
innermost active but FAILED -> commit_illegal ("Commit
illegal from failed", SS12.81/12.82) — the twins' veto.
A failed room must be Caught (94) or Reverted (96);
it cannot be signed.
(5) POINT OF NO RETURN — FOR THE UNDO: verified,
Revert against a committed frame refuses
(unrelated_revert, "Revert refused committed
transaction"). Before Commit, Revert can restore the
room's photo; after Commit, that room's undo is gone
by design — the accepted copy is evidence, not a
restore point she will use.
(6) NESTING: inner Commit closes the inner room only;
the outer room stays open at depth 1 (verified).
COMMIT vs ALPHA (Ace's question, answered from the
code): Alpha (20) is a Core I lifecycle Dell — the
SESSION's closing ceremony; Commit (95) is a Core II
transaction verb — ONE ROOM's closing signature.
Scope: Commit = one frame; Alpha = the whole program.
Durability: Commit writes memory only (a status, a
copy, a ledger line); Alpha's ruled job (Ace, Dell 20
tour stop) is the durable seal — closing must save a
full CHECKPOINT of everything, state AND the history
of how it was reached, via the existing
commit_checkpoint machinery. TODAY'S HONEST STATE:
Alpha's handler only prints a closing card (idea
count, form, and the tip "save before exit —
10[Keep]") and notes the seed — she saves nothing
herself; Ace REJECTED the card-only close, and wiring
her to the checkpoint authority (plus closing the
no-history-member gap) is the standing ALPHA CHECKPOINT
DIRECTIVE in the gated persistence bucket, not yet
built. Frequency: Commit signs many times a session;
Alpha closes once, at the end. Pairing: Try / Catch /
Commit / Revert are one family; Initiate (01) / Alpha
(20) are the session's birth / death pair. Under
DD-53 (3), Alpha's closing ceremony is also where the
open-rooms warning belongs: Commit signs rooms one by
one; Alpha is warned about every room left unsigned.

## 12.86 DELL 96 — REVERT (examined 2026-11-09, API battery incl. the snapshot ladder)

WORKS, with ONE composition wart recorded below.
Registry: "Undo a mutation/change-set." She is a
ladder of four answers, in strict priority order:
(1) A ROOM IS ACTIVE: she restores the innermost
frame's checkpoint through _restore — ALL fifteen
_ckpt slices (store, weights, groups, refs, ledgers,
selection, context, route, verdict stamps) — marks
the frame "reverted", and answers "Revert <id>
exact." Verified exact: inside a Try the store,
weights, and even the Assert stamp were changed;
after Revert every one read as at Try-open. Works on
a FAILED frame too — Revert is the failed room's
second exit (Catch forgives, Revert undoes; SS12.84).
Nested rooms unwind LIFO, one room per Revert
(verified: inner restore left the outer room open;
the second Revert restored the outer).
(2) NO ROOM ACTIVE, LAST FRAME COMMITTED: refusal,
unrelated_revert — Commit's point of no return
(SS12.85 (5)).
(3) NO ROOM ACTIVE, LAST FRAME REVERTED:
revert_illegal — a torn-up room cannot be torn up
twice (verified).
(4) THE CLERKS' SAFETY NET: with no frames in play she
pops the SNAPSHOT STACK — the pre-write snapshots the
clerk Dells capture before mutating (Set, Delete,
Replace, Patch via shot()). Verified on a Try-free
owner: Delete removed a note, Revert popped the
snapshot and the note was back ("Revert snapshot
snapshots=N"). With neither frames nor snapshots she
answers "Revert nothing", ok=True — a calm no-op,
not an error.
THE WART — SNAPSHOT SHADOWING (verified live, open
question for Ace): the ladder checks the LAST FRAME
before the snapshot stack, and terminal frames are
kept (newest 16), so once ANY transaction has
committed or reverted in a session, rungs (2)/(3)
answer every later Revert and the snapshot stack
becomes UNREACHABLE for the rest of the session.
Verified: Try -> Commit; Set victim=1; Delete victim
(clerk snapshot captured, stack depth 2); Revert ->
REFUSED unrelated_revert, victim stays deleted, the
snapshot sits unpopped and unusable. Practical
meaning: in any session that uses transactions,
single-write undo (the Delete / Replace / Patch
safety net) silently stops working the moment the
first room closes, even though the snapshots keep
being captured. The ladder conflates two questions —
"may this transaction be undone?" (committed: no) and
"may the last clerk write be undone?" (the snapshot
exists precisely to say yes) — and answers only the
first. Recorded as an OBSERVATION in the DD-32
three-doors family (Revert is one of the doors), not
a defect ruling: the fix shape (fall through to the
snapshot when the frame refusal is about a DIFFERENT
operation than the snapshot's) is a design question
for Ace / the Director, alongside DD-51's witness
family. SUPERSEDED AS A STANDALONE ITEM by DD-54
(SS12.86a): Ace ruled the wart unacceptable and
ordered the full undo/redo model; the shadowing case
becomes DD-54's first failing-first exhibit.

## 12.86a DD-54 — UNDO AND REDO LIKE A REAL PROGRAM (Ace ruling, 2026-11-09: "Unacceptable... as any Windows program works")

Ace, verbatim substance: undo something, then redo
it, for as many steps — starting with up to 30 steps /
iterations, and the depth must be modifiable and
adjustable, like Photoshop or Word. RULED:
(1) MULTI-STEP UNDO: the session keeps a real undo
history. Starting depth: 30 steps. The depth is
ADJUSTABLE by Ace (a setting, not a constant — today's
SNAPSHOTS_CAP=64 hard constant retires into it; DD-44's
Limit (72) is the natural bounding authority to settle
in design).
(2) REDO EXISTS: after undoing, redo walks forward
again through the same steps. CURRENT TRUTH: the word
"redo" appears NOWHERE in the production code — no
redo mechanism exists at all; today's Revert pops one
snapshot and the future it came from is discarded.
(3) LINEAR HISTORY, NO BRANCHING — Ace already ruled
this at the Fallback stop (SS12.31c): step back, then
make a DIFFERENT move, and the forward path is gone;
FALLBACK keeps track of all the back. DD-54 inherits
that semantics exactly: a new edit after an undo
discards the redo tail.
(4) ONE HISTORY AUTHORITY: the existing snapshot
stack (append_snapshot, the one append path) grows
into the undo/redo history — no second undo
mechanism, no competing store. Revert (96) remains
the undo door; redo's door (a Revert mode vs the
DD-32 family's third door) is settled in design — no
new Dell number is invented here.
(5) EVERY WRITE IS A STEP: a Windows-grade undo covers
the program's edits, not only the clerks who snapshot
today. Coverage follows the DD-51 Ring-2 census
(SS12.79b): writers that never get photographed today
(Weight, Group, Reference, Context, the ledgers,
Define/Alias/Compose, and room work) join the one
capture door; coverage is claimed per-writer, from
tests, never in blanket.
(6) UNDO WALKS STATE, NEVER RECORDS: undoing past a
Commit restores earlier STATE; it does not un-commit
the frame, alter its accepted copy, or erase any
record (Ace's history law, SS12.76). How undo composes
with an OPEN room (steps inside the room vs the room's
own checkpoint Revert) is a named design question —
the room revert stays exact and frame-scoped; the
session undo is the wider river.
(7) THE SHADOWING DIES: frame status never again
blocks the history door (SS12.86's exhibit is the
first failing-first case). A committed room refuses
FRAME-revert; the session's undo history is a
different question and stays answerable.
STATUS: design directive, Director-routed with the
transaction / witness family (DD-32, DD-51, DD-53);
not built. Today's truth stands in SS12.86: one-step
snapshot undo at best, shadowed after any room closes,
no redo, fixed cap 64.

## 12.87 DELLS 97/98/99 — DEFINE / ALIAS / COMPOSE, THE WORD-MAKERS (examined together 2026-11-09, Ace order; API battery + front door)

THE FAMILY WORKS — one system in three parts, all in
the "abstract / create" manor. Define keeps the
MEANINGS book (st.defs), Alias keeps the NAMES book
(st.aliases), Compose is the only mouth that RUNS
what the books hold (st.compositions + expansion).
All three books are DURABLE (CORE_II_DURABLE —
verified across save/load, chains included), the
opposite of the transaction family's session-only
frames: words outlive sessions; rooms do not.
(1) DEFINE (97) — "Create reusable semantic
definition." Stores name = meaning text, publishes
NO result cell, and validates NOTHING: verified, a
Dell-number fragment (mark=55) and pure prose
(motto=stay ready) are stored with equal cheer.
Redefinition silently overwrites. A def is a named
seed FRAGMENT: it means something only when Compose
expands it — prose expanded into a composition fails
then, honestly (malformed_composition, verified),
never at Define time. Define is the permissive
librarian; runnability is Compose's department.
(2) ALIAS (98) — "Bind alternate expression to
existing semantic identity." An alias must resolve,
through any chain of aliases, to a DEF or a
COMPOSITION: resolution is checked at write time by
_alias_resolve. Verified: alias to a composition
written and invocable through the alias; chains
resolve (b -> a -> stampit); alias to nothing refuses
alias_missing and writes nothing; a redefinition that
would close a loop refuses alias_cycle. An alias
cannot point at a bare Dell — its terminal must be a
word in the books.
(3) COMPOSE (99) — "Create reusable higher-order
operation from Dells." Two modes. DEFINE MODE
(name=body): the body is parsed (parts split on > or
,; a DIGIT becomes a bare atom NN[ComposeStep]; a
NAME expands recursively from the books — cycle ->
compose_cycle, depth beyond the bound (st.limit,
DD-44's authority, else the compose default) ->
compose_depth; a body containing '[' runs VERBATIM
as a seed through the front door) — and then, since
Step 10 (B18), the body is RUN FIRST and the name is
published ONLY if the define-run succeeds. Verified:
a runtime-failing body (95 with no frame ->
commit_without_try) ran, failed, and was NOT
published, its error carried in the receipt; a failed
REdefinition RETAINS the previous valid body. The
define-run's own effects PERSIST — no rollback is
implied or performed (stated in the code; the family
lives with Try as its undo neighbor). EXECUTE MODE
(bare name): resolves aliases, expands, and runs the
stored composition/def through execute_seed — the
front door itself. Verified end to end via
99[Compose]:: name in a real seed.
(4) THE FAMILY QUIRK (C22 exhibit, re-verified live):
a composed DIGIT atom runs as NN[ComposeStep] with
the term doubling as its label, so a composed bare
Set writes the key 'ComposeStep' = 1 (verified in the
store). Composed steps carry no labels of their own;
a composition that needs labeled writes uses the
verbatim seed form (verified: via=verbatim landed
exactly).
(5) THE BOUNDARY (SS12.71b test): the books' names are
NOT seed atoms — a bare seed 'stampit' is refused by
the seed parser (unexpected at 0, verified). The
word-makers are wieldable by a docked AI exactly one
way: through Dell 99 herself, in chains and at the
front door (and nested inside other compositions).
The names live in the books' namespace, never in the
registry's. Same shape as Reference's gap (SS12.71a):
durable, inspectable, wired to exactly one runner.
Whether defined names should become first-class
chain atoms is a design question for the Director —
recorded, not ruled.
FAMILY VERDICT: Define proposes words, Alias renames
them safely, Compose makes them DO things — with
publish-only-on-success discipline (72-25) that the
rest of the program could learn from. WITH THIS STOP
THE TOUR IS COMPLETE: all 100 Dells, 00-99, examined
live at the real path, ruled or recorded.

### 12.87a ACE RULING — SHORTHAND EVERYWHERE, TOKEN SYSTEMS IN HARMONY (2026-11-09, closing the tour)

Ace, closing the word-makers: Alias's shorthand is
"very important... that needs to be done all over the
damn place" — nicknaming a long recipe once and pointing
to it is a program-wide efficiency discipline, not a
Dell-98 nicety. And the token systems of DD-30 (SS12.29)
must be used IN UNISON AND IN HARMONY with it: Mandell
Emoji (the 15 dense glyphs, one glyph carrying a whole
directive — built, not yet wired to the front door) and
LatinMandell (Ace's meaningful splitting) are shorthand
layers of the same kind — a compact sign that resolves
to the full thing. Recorded as one connected directive
for the DD-30 / word-maker work: (1) Alias resolution
available everywhere a defined name can be used, chains
included, landing always on something real, never a
loop; (2) TokenCount (DD-30) reports and the front door
parses across ALL systems together — Mandell atoms,
LatinMandell, Mandell Emoji, the docked provider's
tokens — each count labeled by its system; (3) the
efficiency claim is measured, not asserted: the same
directive expressed longhand vs shorthand (alias /
glyph) is counted in every system, and the savings (or
lack of them) are reported honestly per system. Design
and build route through the Director with the DD-30
circuit; no new authority — Alias/Define/Compose stay
the word authority, TokenCount stays the measurer.

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

---

## 13. REANALYSIS — THE WHOLE PLAN, CONNECTED (Ace order, 2026-11-09; Uni, main session)

Ace ordered a full reanalysis: connect directives that can be built
together, mark what is already done, wipe nothing. This section is
appended synthesis; every earlier section stands as history.

### 13.0 DONE / CLOSED — no longer future work

- **DD-31 (Dell 41 Sanitize copula leak): FIXED + SCOPED-CERTIFIED**
  (PR #342 merged 58af9db; Director Q-DD31.1, 2026-11-09). Wider
  secret grammar remains out of scope (Q-DD31.2).
- **G-11 snapshot retrieval (Q-SNAP.1): BUILT + SCOPED-CERTIFIED**
  (PRs #336/#337; Director 2026-11-09 07:39).
- **G-12 Dock Proposal B (Q-LD.1/Q-LD.2): BUILT + SCOPED-CERTIFIED**
  (PR #340; Director Q-LD.5, 2026-11-09 09:43).
- **Selection family 51-54 (Select/Filter/Scope/Query): VERIFIED
  WORKING** on the tour (typed-filter and scope-wall defects were
  historical and already fixed). Query's English door is a coverage
  gap, not a defect.
- Standing machinery the tour kept re-discovering as "to build"
  already exists: containment (TD-2, SemanticGraph authority),
  checkpoint generations + rollback (Dells 27/28 verified live),
  supersession lineage, Nursery proposal lifecycle, per-owner
  fields, Exchange v1 (file-based, imports as PENDING).
- Tour coverage: Dells 00-54 examined; 55-99 unexamined.
- Strict score unchanged by any of the above: **19/72**. Extension
  closures (G-11, G-12, DD-31) never count as original-72 progress.

### 13.1 THE CLUSTERS — thirteen buildable circuits

- **C1 CHAIN TRUTH (receipt honesty).** DD-14 Loop (defect
  re-verified at main 58af9db; IN PROGRESS — grounding complete) +
  DD-18 Pulse receipt/gate honesty. One disease: receipts claiming
  effects that never ran. Shared mechanism: chain executor +
  receipt construction. Ungated; Ace-directed (DD-14).
- **C2 RESONANCE CORE.** Dell 16 relatedness model + DD-15 Merge
  fusion + DD-16 Split partition + DD-23 Enhance = the product an
  idea keeps from resonance + DD-19 Temp graded dial + growth
  directions. ALL consume one relatedness fact; building any one
  alone forks the definition. GATE: Ace's resonance design
  session first.
- **C3 FAILURE & TIME.** DD-32 failure doctrine (analyze / revert /
  retry) + snapshot-every-move + Photoshop navigation (step back
  then act = forward path dies, NO branching; Fallback keeps the
  back-trail) + Dell 20 Alpha history-carrying checkpoint + Dell
  43 Fallback as the failure menu. Rides the EXISTING checkpoint
  authority. Persistence-path adjacency = GATE bucket: Director
  routing required before implementation.
- **C4 REFERENCE FAMILY (the zipper).** DD-20 Compress (link-
  stamped reference) + DD-28 Distill (self-contained essence) +
  DD-26 Inject (paste by reference). One reference mechanism over
  the containment/lineage authority; Distill+Inject is Ace's
  paste workflow. Ungated bounded build.
- **C5 NURSERY DOOR & RANKING.** DD-27 Nurture door policy
  (auto-confirm stays OFF under both the Cycle law and the door
  policy; Ace-set strict standards + named-rule receipts are a
  future policy layer, not a mechanism) + the Ace-confirmed
  ranking formula (2026-11-08: S = 0.40 LINK + 0.25 ACE + 0.20
  FRESH + 0.15 NOVEL; top-5 per topic; global PENDING cap 200,
  Nursery-only) extended per SS12.35a/b to Plane ideas with a
  SWITCHABLE measure (resonance / growth / attention / adapted
  formula; receipt names the active measure) + DD-25 Discover
  All (paged, organized, searchable by name/title/idea/proposal,
  whole/part/piece; rides G-11 retrieval machinery). Q-N3 (FRESH
  half-life) still open.
- **C6 BOXES, FREEZE & PLACEMENT.** DD-17 Lock (one always-present
  locked personal box + multiple drawable sandboxes, own locks,
  resonance inside a chosen sandbox) + DD-22 Pause/Resume
  per-item freeze (frozen items skip tick/resonance/growth until
  Resume) + Scope<->Group partnership (SS12.42a) + placement law
  and Create split / AUTO-BIND modes. One substrate: the existing
  sandbox authority EXTENDED — never a second authority.
- **C7 SELF-REPORT (honest instruments).** DD-29 Schema = nervous
  system (existence + connection + availability of the active
  system, organ-level fault reporting) + DD-39 Profile =
  speedometer (per-stage timing inside a tick; names the dragging
  stage) + DD-30 TokenCount = token mastery (Mandell atoms /
  LatinMandell roots / Mandell Emoji glyphs / provider tokens —
  each system counted and LABELED separately; never one blended
  number). Read-only introspection; DD-30's provider side reads
  the C8 provider identity.
- **C8 DOCK & PSALMS.** DD-37 dock roster (NO cap on the live
  list; two tiers — live sessions full detail, history compact
  and organized in one place, digests not transcripts) +
  resident Psalm direction (SS12.20: continuously present,
  in-tune, low-volume, Nursery-bound output — design item) +
  multi-Psalm harmony design session owed (SS12.36e: roles,
  capabilities, limitations, anti-clash/anti-duplication) +
  Embed provider binding (SS12.36: Gemini embeddings vs local
  Ollama — Ace's choice; Embed is a docked provider, not a web
  fetch) + inside-out Mandell-chain authoring as proposals
  (explored 2026-11-09). Multi-dock verified: no engine cap;
  the 10-record rotation DD-37 removes is a records cap only.
- **C9 TRANSLATE.** DD-35/DD-36 dual-mode: docked = the AI
  understands; undocked = Adapt (ADOPTED as-is, credit: Adapt
  Intent Parser by the Mycroft AI team, Apache-2.0, notices in
  code + docs) — and Adapt sits INSIDE Translate as the docked
  AI's own tool for command-shaped English. SEQUENCING: "not
  yet" (Ace, 2026-11-09). Nothing starts until Ace calls it.
- **C10 HARMONIC PLANE.** DD-24 harmonic Stamp (first consumer:
  note-stamps that attach, persist, keep order) + harmonic
  perspective on the Plane + living modes (relevance / harmony /
  gravity) as LENSES — canonical placement never moves (SS12.22a
  SETTLED). Gravity already ticks; notes ride the lattice
  note_at machinery (SS12.27).
- **C11 IDEA EDITING.** DD-41 (enter an idea, extract parts into
  the notebook, edit, preview consequences, confirm -> new
  version supersedes with history kept; the docked AI analyzes
  the change as PENDING proposals only) + DD-38 Macro private
  shelf / little notebook (the workbench: copies of ideas,
  Dells, Nursery bits, perspectives, Psalms; nothing leaves
  except by Ace's hand) + DD-40 Manifest (confirm is the YES;
  Manifest is the WALK from Nursery/notebook to the Plane; the
  middle state must stay clean). Director-level build:
  containment + supersession + Nursery in one circuit.
- **C12 BRIDGE.** DD-34: matrix<->matrix transfer over the
  EXISTING Exchange v1 (Bridge is the face; Exchange is the
  machinery) + Bridge as ledger of all bridges (dock, Exchange,
  any future) + pre-connection preview (what would flow, what
  could be affected) + true resonance on contact (vs in-matrix
  calculated resonance — vocabulary settled in C2's session).
  Online/shared matrix remains "way way later" (Ace) — C12 is
  local file-based only; Phase G DEFER stands.
- **C13 SIMULATE.** DD-21: a true rehearsal — run any command or
  chain against a shadow state and report the would-be changes;
  ZERO writes, including no history self-write (the current
  implementation's quiet history append is part of the defect).
  Shares executor introspection with C1/C3.

### 13.2 CONFLICTS & SUPERSESSIONS (history preserved, readings settled)

1. SS12.34's Translate observations are SUPERSEDED by SS12.34a/b
   (dual-mode doctrine + Adapt decision).
2. The ranking formula exists in three statements (2026-11-08
   confirmation; SS12.35's old live recipe; SS12.35a/b scope +
   switchability). C5 is the single implementation reading.
3. "Resonance is relatedness" (Dell 16) vs "calculated vs actual
   resonance" (SS12.33b): one vocabulary must win; C2's design
   session settles it — neither text is edited meanwhile.
4. Temp: DD-19's graded-dial ruling supersedes the descriptive
   3-mode switch text; unknown labels refuse (both texts agree).
5. Manifest: DD-40's line (confirm = permission, Manifest =
   work) supersedes any reading of confirm-as-materialization;
   current code fuses them — a build constraint, not a doc edit.
6. Cycle AUTO-CONFIRM law and DD-27 door policy agree (OFF);
   recorded so no future circuit "discovers" a conflict.
7. PR #342 merge attribution is UNRESOLVED (found merged at the
   pre-merge check; every Director condition was factually met
   56s prior). Containment stands: merges from the main session;
   the incident is recorded, not explained away.

### 13.3 DESIGN SESSIONS OWED (Ace's format — never designed unilaterally)

Resonance (C2 gate) · growth model · multi-Psalm harmony (C8) ·
resident Psalm (C8) · Show · Dell 05 animated face · age-as-time
surfacing · 01/02 personal page · Temp full design (inside C2) ·
placement/Create modes detail (inside C6).

### 13.4 SLEEP-MODE FINDINGS (Ace asked: stuck on anything?)

- NOT stuck. Closed this sleep period: G-11 (certified), G-12
  Proposal B (certified), DD-31 (certified), DD-14 grounded.
  Throughput is verification-bound, not will-bound: each code
  circuit costs regress x3 (~45-60 min) + PR smoke (~15-20 min)
  + merged-main smoke (~15-20 min) + a records PR with its own
  smoke. That is the price of the hard gate; it is not waste.
- Real friction, recorded honestly: (a) VM replacements kill
  long chains — mitigated by durable logs + recovery chains;
  lost legs are re-run, never assumed. (b) A cycle worker once
  reported a Director mail ID that does not exist in the mailbox
  (phantom 1a1c0e0195fdb76e) — rule now: cycle-reported mail IDs
  are re-verified by the main session before any action.
  (c) The #342 merge attribution (13.2.7). (d) Records PRs
  multiply — required by the Director's evidence discipline;
  accepted cost.
- Gates that look like stalls are ownership, not blockage: Q1
  (#294), R-1 implementation, #308, C-A/F2 sit with the Director;
  V-12 human gates sit with Ace. Uni-side queue is never empty
  while DD-14 and the clusters stand.

### 13.5 RECOMMENDED SEQUENCE (completion-first)

C1 (DD-14 + DD-18) -> C8 DD-37 slice -> C7 Schema slice ->
C13 Simulate -> C5 ranking -> C4 zipper -> C6 boxes ->
C2 design session, then C2 build -> C3 (after Director
routing) -> C11 -> C9 (on Ace's call) -> C10 -> C12.
Rationale: ungated bounded defects first, smallest closable
units early, design-gated clusters wait for their sessions,
gated persistence work waits for its rulings. The Director
sequences certification; Ace sequences design.

### 13.7 REITERATION — TOUR COMPLETE + ACE'S EVOLVE/ENHANCE PROTOCOL (2026-11-09)

The Dell tour is COMPLETE: all 100 Dells (00-99) examined
live, SS12.1-SS12.87a. Material the tour produced AFTER the
SS13 consolidation (Dells 55-99) folds in here:

- DD-42 (Compare/Branch natural-order grammar silently
  always-true) and DD-44 (While/Until explicit-limit law,
  Limit as the single quantity authority) join Cluster 1's
  honesty family beside DD-14/DD-18: receipts and verdicts
  must never claim what did not happen.
- DD-45 (silent creation loss under Select/Filter) is
  FIXED and in PR #345, held only by the DD-31 pass-2
  isolation circuit (Director, 2026-11-09 13:35).
- The measurement family is ONE design: Measure must
  measure real Plane quantities (DD-46), Threshold
  reports distance past the line, Weight feeds everything
  weighable (resonance, distance, gravity, harmony,
  perspective, personas, Psalms) into the one weight
  authority, Normalize makes weights comparable, Schema
  (DD-29) reports the whole body from those numbers, and
  Resolve becomes the field's search door over the same
  index (no second search authority).
- DD-51 (Diff as the one scoped comparison authority),
  DD-52 (Trace = the full current process, session-scoped),
  DD-54 (undo/redo, 30 steps adjustable, Photoshop-style,
  riding the existing snapshot ladder), the rooms rulings
  (Try rooms stay temporary BY ACE'S DECISION; addressable,
  close on Ace's order only, session-end warning beside
  Alpha's checkpoint, Bridge previews room-to-room via
  Diff), and SS12.87a (Alias shorthand program-wide;
  Mandell Emoji + LatinMandell in harmony with TokenCount,
  DD-30, savings measured per system) all stand as ruled.

ACE'S PROTOCOL FOR THIS PLAN (2026-11-09, verbatim intent):
the completed plan is reiterated by Uni (this pass), put
through CI, and sent to the Director; the Director goes
through ALL of it and evolves/enhances it; it comes back
to Uni, who evolves/enhances it a SECOND time; THAT
second-evolved version is the version used as THE plan;
then it is implemented. Passes: (1) Uni reiteration =
SS13 + this SS13.7, published via PR #344; (2) Director
evolve/enhance via his review channel; (3) Uni second
evolve/enhance folding his pass in; (4) the result is
adopted as the working plan; (5) implementation proceeds
circuit by circuit under the standing gates (Director
certification, Ace design sessions, gated buckets
unchanged). Nothing in the passes erases history: each
pass layers over the last, supersessions marked.

### 13.8 PAIRWISE RECORD RECONCILED (Ace order, 2026-11-09)

Ace asked that the Dells be checked against each other and
the existing record verified against today's standard.
FOUND IN THE REPO (director-reports/evidence/step13/):
the full pairwise pass EXISTS and is complete as a sweep —
Step 13 re-derivation, all 9,900 ordered pairs + 100
identity, ledger v2 (SHA-256 checksummed), classified
FUNCTIONAL 1,989 / FUNCTIONAL_INDEPENDENT 6,375 /
INTENDED_CLASH 1,528 / UNIQUE 8 / DEFECT 0; identity 89
IDEMPOTENT / 11 HONEST_REFUSAL.
LIMITS, stated plainly: (1) it ran on a FROZEN baseline at
the repaired step-11 head (early Nov 2026) — exact for
that baseline, not for today's code; (2) it is
harness-level evidence (per-owner isolated Program state),
not a public-entry-path execution; (3) its classification
semantics are the frozen Gate-0 seed's — they predate the
tour's rulings.
STALE-BY-CHANGE: pairs touching any Dell whose production
behavior changed after the freeze (typed-arg refusal
gates 72-13, owner guards DD-12, pulse exclusions DD-13,
redaction DD-31, chain fail-closed DD-45) or whose
INTENDED behavior the tour re-ruled (Loop DD-14, Compare
grammar DD-42, Parallel DD-43, the DD-44 limit law, and
the DD-15..DD-54 design rulings) cannot be carried
forward as current-standard verdicts. A pair marked
FUNCTIONAL under behavior Ace has since ruled defective
is the headline case (Loop's pairs).
PRESCRIPTION (for the implementation phase, Director
routing): a DELTA re-derivation — re-run only the pairs
touching changed or re-ruled Dells against current main
under the tour-era classification standard (classes a-d),
diff against ledger v2, and publish ledger v3 with the
diff as evidence. The untouched remainder of v2 stands
as-is; history is preserved, nothing is wiped or
re-claimed wholesale.
