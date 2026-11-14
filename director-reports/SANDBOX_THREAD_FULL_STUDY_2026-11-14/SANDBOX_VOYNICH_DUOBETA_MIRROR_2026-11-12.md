# SANDBOX — THE VOYNICH RINGS × DUOBETA MIRROR

Status: SANDBOX research (side chat, 2026-11-12). Exploratory;
nothing here is pipeline law until Ace or the authority lanes
promote it. Commissioned by Ace: DuoBeta was inspired by the
Voynich (Ace's statement of his own design intent); this memo
mirrors the 2026-11-12 Voynich season's ring findings back
onto DuoBeta, hunting enhancements to growth and learning.

## THE TWO SIDES OF THE MIRROR

**DuoBeta as it verifiably stands** (repository + memory
record): an evidence-learning layer. Outcomes are observed
(labeled observation, not truth) → a learn proposal is made
explicitly → a deterministic gate judges it (requires
≥ MIN_EVIDENCE = 3 matching outcomes) → apply writes a
GrowthEntry to the persisted duo_ledger → learned entries
exert advisory influence only (reranking already-eligible
knowledge; truth is bit-identical with learning on/off).
Known gaps on record: rollback policy for learned entries is
IMPLICIT; no first-class disable/reset API; historical
learned state stays UNKNOWN by design (learning never
rewrites history).

**The Voynich rings as this season measured them:**
concentric labeled rings around a readable anchor (f70v:
"mars" at the center); conserved totals with free
arrangement (29/30 day-figures per wheel; 10+19, 15+15,
10+16+4); one figure WITHOUT a label (the nameless nymph);
a four-round wheel whose rounds differ by named, localized
mutations (f57v: 17 signs × 4 rounds; slot 17 mutates after
round 1, slot 9 at round 3); two luminaries exchanging place
AND color across states (f68 foldout); a tally wheel with
ordinal markers 1-2-3-4 interleaved with data loads;
repetition that is always variant-spelled, never verbatim.

## THE MIRROR — SEVEN CANDIDATES, CLASSIFIED

### 1. GROWTH ROUNDS WITH MUTATION RECEIPTS — ADAPT (strongest)
Voynich: f57v's ring is revisited for four rounds; the ring
itself records exactly which slot changed at which round.
DuoBeta today: the ledger is append-only, but a learned
entry's CHANGE HISTORY across growth passes is not a
first-class object, and rollback is implicit (known gap).
Enhancement: model a growth pass as a ROUND over a fixed
ring of learned entries; every change lands as a mutation
receipt (entry, round, slot, before, after, evidence). Any
round's state is then reconstructible as base + mutations —
which makes rollback a computation instead of a policy, and
gives the Director a diff-able artifact per round.
Falsification: reconstruct round N state from receipts for a
recorded growth history; if reconstruction diverges from the
persisted state at any round, the design fails.

### 2. FUZZY EVIDENCE MATCHING AROUND AN EXACT ANCHOR — ADAPT
Voynich: the book repeats nothing verbatim; its pulse fires
1,777 times respelled by a glyph or two. A gate that counts
only EXACT matches would starve in such a world.
DuoBeta today: the gate counts "matching outcomes" toward
MIN_EVIDENCE = 3; the record does not show a similarity
notion in the matching.
Enhancement: allow edit-distance-1 outcome variants to count
toward a proposal's evidence, each fuzzy match receipted
with its distance — CAPPED by requiring at least one exact
anchor match (the star's word sits beside a readable
"mars"; fuzz orbits an anchor, never floats free). This
mirrors the honesty structure of the whole season: near
evidence admitted, labeled, and anchored.
Falsification: replay a recorded outcome stream through
exact-only vs anchored-fuzzy gates; if fuzzy matching flips
any gate decision WITHOUT the extra matches being genuine
variants on inspection, the cap design fails.

### 3. THE CONSERVED RING — CYCLE-BOUNDED EVIDENCE WINDOWS — ADAPT
Voynich: a wheel holds exactly 30 positions; totals are
conserved while arrangement is free; nothing accumulates
past the ring's edge.
DuoBeta today: evidence accumulates unboundedly (43 receipts
by session C on record) and proposals are judged against the
pile.
Enhancement: judge proposals per completed RING — a fixed
window of the most recent N outcomes (the active ring);
older outcomes rotate to an outer archive ring, still
auditable, no longer voting. Growth reports then compare
ring-over-ring: what the current cycle's evidence supports
vs the last, like wheel against wheel.
Falsification: run both windowing regimes over the same
recorded stream; if windowed gates prove LESS stable
(decisions oscillating ring-over-ring without cause),
reject.

### 4. EXPLICIT UNKNOWN SLOTS — ADAPT (cheap, law-aligned)
Voynich: one nymph stands in her ring with NO label, and the
transcribers' numbering had to step around her — the absence
is part of the artifact.
DuoBeta today: a proposal's evidence shows what is PRESENT;
expected-but-absent evidence is silent.
Enhancement: growth rings carry explicit UNKNOWN slots —
positions where a class of evidence is expected and missing
— surfaced in every growth report. This is AGENTS.md §7
(positive evidence law) wearing a ring: absence made visible
instead of mistaken for a pass.
Falsification: none needed beyond display correctness; the
risk is noise, bounded by only slotting evidence classes the
gate already names.

### 5. THE SUN/MOON SWAP — FIRST-CLASS ROLE ALTERNATION — INSPIRE
Voynich: across the f68 panels the two luminaries exchange
place AND color — whoever rises carries the other's color:
the leader takes the checker's constraints with the throne.
DuoBeta is DUO by name but a single pipeline in code
(propose → gate → apply): the duality lives in the stages.
Enhancement (design sketch only): two concentric rings —
PROPOSE (inner) and GATE (outer) — whose contents ROTATE
into each other each cycle with a swap receipt: what was
proposed last cycle is what gets gated this cycle, and the
swap itself is a ledger object. Makes the duo structure a
mechanism rather than a metaphor, and every cycle boundary
auditable.
Falsification: this is architecture, not a tweak — it stands
or falls in a Director-reviewed design pass, not here.

### 6. THE TALLY WHEEL AS GROWTH DASHBOARD — ADAPT (presentation)
Voynich: panel 3 tallies quantities in 8 segments with
ordinal markers interleaved — a one-glance quantitative
state of the whole wheel.
Enhancement: the growth report rendered as a wheel —
segments = knowledge/Dell families; stars per segment =
applied learnings this cycle; small ordinals = the cycle
number ring. Conservation discipline included: the segment
set is FIXED, so cycles are comparable at a glance, and an
empty segment is visible (see candidate 4).
Falsification: not a mechanism claim; succeeds if a reader
can answer "where did learning grow this cycle, and where
is it absent?" from the wheel alone.

### 7. ONE READING DIRECTION — REJECT (already present)
Voynich rings read forward only (Phase 6: every other
direction scores at the shuffle floor). DuoBeta's ledger is
already append-only and forward-reading. Nothing to import;
recorded so the mirror is complete.

## WHAT THE MIRROR DOES NOT LICENSE

The Voynich rings are an interpretive frame over an
undeciphered artifact (meanings established: zero — the
season's standing honesty line). These candidates borrow
STRUCTURE, not authority: each must earn its place through
DellMatrix's own gates (falsification, Director review, the
authorized learning lifecycle). DuoBeta's core laws are
untouched by every candidate above: observation never
becomes truth, learning never rewrites history, the gate
keeps its minimum-evidence spine, and Ace keeps the learning
gate. The strongest near-term candidates are 1 (mutation
receipts -> computable rollback, closing a recorded gap)
and 2 (anchored fuzzy evidence matching), in that order.
