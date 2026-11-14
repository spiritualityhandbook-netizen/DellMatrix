# SANDBOX — THE TREE OF LIFE: THE FLOWER COMPLETED IN ALL DIRECTIONS

**Status: SANDBOX, Part III of the Flower line (Part I:
`SANDBOX_FLOWER_SPHERE_FIELD_STUDY_2026-11-13.md`; Part II:
`SANDBOX_FLOWER_POLYGON_LADDER_STUDY_2026-11-13.md`). Developed at Ace's
order 2026-11-13 19:47 CST: take the 3D shapes off the flat plane, place
spheres 360° in all dimensions around a centre out to the Flower's outer
edge — "let's call this Tree of Life" — for all relevant shapes; then
centre dots, lines between every pair of points, corner dots, lines from
corners to centres, and halving across every axis combination; mirror
against DellMatrix, Mandell, DuoBeta, the main plan and the future plan.
Nothing in any plan; no code touched; acceptance is Ace's.**

**Naming note.** "Tree of Life" is Ace's name for this construction. It is
not the Kabbalistic diagram (a different, historical figure); no mapping
between them exists in this work and none is claimed.

Probes preserved in `hidden_files/tree_of_life_study/`:
`probe_tree_exact.py` (exact integer censuses), `probe_tree_fields.py`
(seeded Monte Carlo fields), `probe_tree_corners.py` (corner censuses).

---

## 1. THE CONSTRUCTION

Parts I–II put centres on one flat layer — the Flower's own plane. Ace's
step removes the plane: around a centre, neighbours go in **every**
direction at the same spacing (1), out to the same radius the flat
Flower reaches.

The arrangement this forces is the **FCC lattice** (face-centred cubic):
centres (i, j, k)/√2 with i+j+k even. It is the canonical completion for
three checkable reasons: (a) its horizontal layers perpendicular to the
(1,1,1) axis are *exactly* the 2D Flower's triangular lattice, stacked
ABC at height √(2/3) ≈ 0.8165; (b) it is a true lattice (one centre
repeats by translation); (c) each centre has **12 nearest neighbours** —
the 3D kissing number. The alternative stacking (HCP, ABAB) shares the
first shell (12 neighbours) and differs only deeper; FCC is used
throughout, and the choice is recorded as a choice (Q-T1).

All solids keep Part II's conventions: circumradius 1; bipyramids (the
polygon lifts) stand with their axis along (1,1,1), so their equators lie
*in* Flower layers and their equatorial vertices can point at neighbours.

## 2. CENTRE DOTS ALONE — SHELLS, AND THE TWO FLOWERS INSIDE

**Euclidean shells** (centres at each exact distance from the centre;
exact integer arithmetic):

| distance | 1 | √2 | √3 | 2 | √5 | √6 | √7 | 2√2 | 3 |
|---|---|---|---|---|---|---|---|---|---|
| centres | 12 | 6 | 24 | 12 | 24 | 8 | 48 | 6 | 36 |
| cumulative | 13 | 19 | 43 | 55 | 79 | 87 | 135 | 141 | 177 |

**Step shells** (centres reachable in k nearest-neighbour steps, BFS):
12, 42, 92, 162 — exactly **10k² + 2**; cumulative 13, 55, 147, 309.
Same neighbourhood, two organisations: *by radius* and *by steps*. They
are not interchangeable — e.g. the 12 centres at distance exactly 2 are
2-step reachable (straight double-steps), while some centres at distance
√5 need 3 steps. (Part I's pattern-versus-place distinction, in 3D dress.)

**Slices.** Cut the Tree through its centre and two different 2D flowers
fall out:

- The **(111) slice is the Flower itself**: centres at distances 1, √3,
  2, √7, 3 with cumulative counts 7, 13, 19, 31, **37** — the flat
  Flower's own centre census (rings 0–3 = 37). The Flower is the Tree's
  waist.
- The **(100) slice is a square flower**: a square lattice (shells 4 at
  1, 4 at √2, 4 at 2, 8 at √5, 4 at 2√2, 4 at 3; cumulative 5, 9, 13, 21,
  25, 29). Part II's square was hiding inside the Tree as a slice.

> **T-1. The Tree contains both the triangular Flower and a square
> flower as central slices. Which 2D world you see is a choice of cut,
> not a choice of object.**

## 3. THE FIELDS — WHAT THE EXTRA DIRECTIONS DO TO SHARING

Seeded Monte Carlo (200,000 field points; means match the analytic
volume ratios within 0.6% for every solid):

**The sphere Tree.** Multiplicity: 4 → 10.9%, 5 → 11.6%, **6 → 51.9%**,
7 → 24.9%, 8 → 0.6%. Mean 5.93. No gaps (proven independently: FCC
covering radius 0.707 < 1). And the headline:

> **T-2. In the completed Tree, a sphere's exclusive volume is ZERO**
> (0 exclusive points in 400,000 samples of the ball; < ~10⁻⁵). Part I's
> private caps (8.73%) were an artefact of having only one layer: the
> layers above and below move into the caps. *Privacy by lifting was a
> flatland loan; the Tree collects it.* Minimum sharing is 4 (the
> tetrahedral-hole neighbourhoods) — in the Tree, a sphere shares
> everything, at least four ways, everywhere.

**Bipyramid Trees** (gaps = % of space in no solid; excl = % of one solid
covered by no other; Part II single-layer exclusivity in brackets):

| shape | gaps | max sharing | exclusive |
|---|---|---|---|
| triangle | **8.36%** | 3 | **49.4%** [77.6] |
| square | 0.49% | 5 | 19.6% [51.0] |
| pentagon | 0.14% | 4 | 10.3% [41.0] |
| hexagon | 0.10% | 4 | 5.5% [33.6] |
| heptagon | ~0.002% | 5 | 5.1% [~] |
| octagon | 0 (sample) | 5 | 4.2% |
| nonagon | ~0.001% | 4 | 3.7% |
| decagon | 0 (sample) | 4 | 3.4% |
| sphere | 0 (proven) | 8 | **0%** [8.73] |

> **T-3. The Tree inverts Part II's privacy story.** Completed in all
> directions, privacy belongs to the *pointy* solids (triangle bipyramid
> keeps half of itself), the sphere keeps none — and the triangle pays
> for its privacy with **voids**: 8.36% of its Tree is in no solid at
> all. The flat critical cover (Part II, PL-1) does not survive the
> third dimension. Octagon and decagon bipyramids show no gaps at
> sampling resolution (upper bound ~1.5×10⁻⁵); the hexagon's ~0.1%
> pinprick voids are real at this sampling (their exact location is
> Q-T2).

## 4. LINES BETWEEN EVERY POINT AND EVERY OTHER POINT

The complete graph on the Tree's centres. On the 13-centre Tree: **78
lines, but only 4 distinct lengths** — 36 at 1, 12 at √2, 24 at √3, 6 at
2. On the 55-centre Tree: **1,485 lines, 14 distinct lengths** (216 at 1;
264 at √3 is the most common class; only 6 lines span the full diameter
4). The length spectrum is a **fingerprint**: it is exactly the pair
correlation function crystallography uses to identify a lattice from
scattering. Any two Trees can be compared by spectrum alone.

One hole in the spectrum is number theory, not sampling: **no pair of
centres in any FCC Tree, however large, sits at distance √14** — 28 is
not a sum of three squares (Legendre), so that length is forbidden
everywhere, forever.

The sphere's own marks — contact points where touching spheres meet —
are all distinct: 36 contact points for 36 touching pairs (13-Tree), 216
for 216 (55-Tree). A tested hypothesis falsified and recorded: contact
points never coincide; the near-miss meeting places of six spheres (the
octahedral holes) are a different species of point, where spheres
*almost* touch but don't.

## 5. CORNER DOTS

The sphere has **no corners** — in the corner census it contributes only
its centre and its contact dots. Every other solid contributes n+2
(bipyramids) or its Platonic count. Over the 13-centre Tree:

| solid | corners | corner instances | distinct points | corners on centres |
|---|---|---|---|---|
| tri. bipyramid | 5 | 65 | 60 | 39 |
| sq. bipyramid | 6 | 78 | 77 | 26 |
| pent. bipyramid | 7 | 91 | **91 (no two ever meet)** | 13 |
| hex. bipyramid | 8 | 104 | **69 (heavy stacking)** | 78 |
| hept. bipyramid | 9 | 117 | **117 (no two ever meet)** | 13 |
| oct. bipyramid | 10 | 130 | 129 | 26 |
| non. bipyramid | 11 | 143 | 138 | 39 |
| dec. bipyramid | 12 | 156 | 155 | 26 |
| cube | 8 | 104 | 104 (none shared, none on centres) | 0 |
| octahedron | 6 | 78 | 78 | 0 |
| tetrahedron | 4 | 52 | 52 | 0 |
| dodecahedron | 20 | 260 | 260 | 0 |

> **T-4. The gcd rule.** An equatorial vertex lands exactly on a
> neighbouring centre iff its direction is a multiple of 60°, so the
> central solid's vertex-on-centre hits are exactly **gcd(n, 6)** —
> 3, 2, 1, 6, 1, 2, 3, 2 for n = 3…10 (probe-verified), and the whole
> cluster's corner-on-centre instances are 13 × gcd(n, 6). Apexes never
> land on centres; Platonic corners never do. Corner-to-centre contact
> is a commensurability phenomenon: it happens exactly where the
> polygon's symmetry and the lattice's 6-fold symmetry share a divisor.

The hexagon's corners *stack*: one point (a centre) carries 6 corner
instances — every in-plane neighbour points a vertex into it — with
further 3- and 2-stacks across the cluster (69 distinct points from 104
instances). The pentagon's and heptagon's corners, by contrast, are
perfectly solitary: 91 and 117 instances, zero meetings. Whether corners
meet at all is decided by the same gcd arithmetic (gcd(n,6) = 1 shapes
keep their corners to themselves, except the square/octagon/decagon's
single accidental pair-meeting each).

## 6. LINES FROM CORNERS TO CENTRES (SPOKES)

Every spoke has length 1 by construction — the same radius that carries
the 12 neighbour centres. So on the unit sphere around any centre sit
three kinds of marks: **12 neighbour centres, the solid's own corners,
and (for spheres) 12 contact dots at half-radius toward neighbours**.
The spoke *angle sets* are each solid's fingerprint:

- tetrahedron: a single angle, **109.47°** — the most uniform object in
  the study; every pair of its corners is identically related.
- cube: {70.53°, 109.47°, 180°} — note it *contains* the tetrahedron's
  angle (a cube's alternate corners are a tetrahedron).
- bipyramids: {90°, 180°} ∪ {multiples of 360°/n}: triangle adds 120°,
  pentagon adds 72°/144°, hexagon {60, 90, 120, 180}, decagon six
  values. The 90° is universal — apex-to-equator is always a right
  angle at this apex height.
- dodecahedron: {41.81°, 70.53°, 109.47°, 138.19°, 180°}.

Direction sharing: the hexagon bipyramid's 6 equatorial corner
directions *are* 6 of the 12 neighbour directions; the cube's 8 corner
directions are completely disjoint from the 12 neighbour directions —
20 distinct marked directions on the sphere, no overlaps.

## 7. HALVING THE TREE — EVERY AXIS, EVERY COMBINATION

**Centres halve perfectly on every central plane tried** (55-centre
Tree): x=0 → 21 / 13 on-plane / 21; x=y → 22 / 11 / 22; x=−y → 22 / 11 /
22; the (111) equator → 18 / 19 / 18. The halves are always equal — but
the **waist differs by cut** (13, 11, or 19 centres lie in the cut
itself, and the waist is a different 2D flower per §2). Equal halves,
different waists. The octant census is perfectly uniform: exactly 3
centres in every strict octant (the remainder lie on the axis planes).
Two cautions ride along: the (111) cut halves *by count* through
inversion symmetry, but it is **not a mirror plane** of the cluster —
count-equal is not mirror-identical; and —

> **T-5. Corners do not halve like centres.** Across its own equator
> every bipyramid splits cleanly (all n corners ON the plane, apexes
> 1/1). Across x=0, the pentagon splits 3/4 with nothing on the plane,
> the heptagon 5/4, the nonagon 5/5 with one on, the decagon 6/6.
> Centres are cut-agnostic (the cluster's symmetry guarantees balance);
> corners are cut-sensitive (balance only on planes their own
> orientation respects). Halving a Tree of shapes is centre-exact and
> corner-negotiable.

## 8. MIRRORS — DELLMATRIX, MANDELL, DUOBETA, THE PLANS (graded)

**Codebase (FACT).** No FCC / Tree / coordination structure exists in
`form/` (search: no hits beyond unrelated "coordination" comments).
`harmonic_lattice.py` is a rectangular (h, v, f) grid with
`plant_flower` for the 2D form. The Tree is a new sandbox object, not a
recovered one — Parts I–II's fields were its equatorial layer all along
without the codebase ever completing it.

**MECHANISM-consistency.** The Flower is the Tree's (111) waist slice;
the Part I "lift" was exactly one layer of the Tree; Part II's polygon
fields were that layer's shapes. The three parts are one object at three
completions: layer (I–II) → all directions (III).

**PATTERN — growth & the Completeness Law.** The Tree is the geometric
form of Ace's two laws meeting: growth with **ALL** explicitly selected
(every direction around a centre, considered) and the component census
(every neighbour accounted for, by shell). It also hands the census an
honest dual bookkeeping: count a neighbourhood *by steps* (10k²+2) or
*by radius* (Euclidean shells) — same territory, different totals, both
exact. A census that doesn't say which ruler it used is ambiguous.

**PATTERN — DuoBeta / the symbiosis census.** The complete graph of §4
is a *finished* pairwise census at toy scale: 55 nodes, 1,485 pairs,
14 relation classes, zero unclassified pairs — the same gesture as the
9,900-pair symbiosis programme, with arithmetic instead of semantics.
Its transferable instrument-candidate: **fingerprint a relational field
by its pairwise-class histogram**; a change in the histogram is an
observation (DuoBeta's lawful input), and the histogram is computable
from records without touching truth. Not built; a candidate.

**PATTERN — Mandell.** A chain radiating from a centre has two honest
addresses per node — step-shell and radius — and they can disagree
(a distance-2 node can be 2 steps away; a √5 node is closer in space
than a √7 node but no closer in steps). Chain geography inherits the
pattern ≠ place distinction.

**PATTERN — HCN.** The coordination unit (centre + 12) gives "full
neighbourhood" a definite size and shell structure; WARD's watchlist
borders (§5B.1 of the Afterplan study line) are shell boundaries in this
geometry.

**PATTERN — the Future Plan's Room and Sky.** Ace's plan pairs a 3D
ROOM with a 2D SKY. The Tree is a candidate skeleton for that pair: one
object whose equatorial slice is the Flower-Sky and whose vertical
slice is a square Sky (§2) — the Room and its Skies are cuts of a single
structure, so "switching pages keeps you inside the idea you were in"
has a geometric reading: move the cut, keep the centre. The 12-neighbour
coordination is a candidate layout law for the Room (every idea has
exactly 12 nearest neighbours) — offered as a candidate, not proposed
as a perspective (the perspective set is settled, Ace 2026-11-08).

**PATTERN — elastic limits.** The Tree grows by shells with exact
counts (13 / 55 / 147 / 309 by steps) — demand-grown capacity with a
receipt, the Harmonic-Cube growth posture in lattice form.

**REJECTED.** Tree-of-Life correspondences with the Kabbalistic figure;
13 / 55 / 147 as significant numbers (they are lattice arithmetic);
the Tree as a new perspective; any claim that DellMatrix *should*
adopt FCC addressing (the harmonic lattice's rectangular grid is the
codebase's authority; the Tree is a study object and a mirror, not a
migration proposal).

## 9. VERDICT

Yes — the completion discovers new things, and the largest is an
inversion: **the sphere, hero of the flat studies, is the Tree's most
public object (zero private volume, everything shared ≥ 4 ways), while
privacy survives only in the pointy solids, paid for in voids.** Around
it: the Tree unifies the menagerie (both 2D flowers are its slices —
T-1), its neighbourhoods carry two exact censuses (steps vs radius),
its complete graph is a finished pairwise fingerprint with one
number-theoretically forbidden length, its corners obey a gcd law
(T-4), and it halves evenly by centres on any cut while its corners
negotiate (T-5). The Tree is not a new system and claims no authority:
it is the Flower *completed*, and its DellMatrix value is as a mirror
and instrument-candidate set (§8) for the census, the Room/Sky pair,
and pairwise fingerprinting. Still sandbox; placement is Ace's call,
as with Parts I–II.

## 10. OPEN QUESTIONS

- **Q-T1.** The HCP stacking (ABAB) differs from FCC beyond the first
  shell; its field/corner statistics are unprobed. If a consumer ever
  cares which Tree, this is the fork.
- **Q-T2.** The hexagon bipyramid's ~0.1% voids: exact location and
  shape unprobed (candidates: mid-height seams between layers).
- **Q-T3.** Mixed Trees (sphere centres, polygon shells; a different
  shape per shell) are unconstructed.
- **Q-T4.** Corner-to-corner lines (the complete graph on corner dots)
  unprobed; only corner-to-centre spokes were drawn, per the order.
- **Q-T5.** Corner stacking at Tree radius 2–3 (55/177 centres) is
  unprobed; the 13-Tree stacks are the centre-weighted case.

## APPENDIX — KEY NUMBERS

Euclidean shells (dist: count): 1:12, √2:6, √3:24, 2:12, √5:24, √6:8,
√7:48, 2√2:6, 3:36. Step shells: 10k²+2 = 12, 42, 92, 162. Complete
graph, 55 centres, edges by distance: 1:216, √2:90, √3:264, 2:114,
√5:192, √6:48, √7:240, 2√2:27, 3:108, √10:48, √11:48, √12:36, √13:48,
4:6 (total 1,485). Sphere Tree multiplicity: {4: 10.9%, 5: 11.6%,
6: 51.9%, 7: 24.9%, 8: 0.6%}, mean 5.93. gcd(n,6) vertex hits:
n=3…10 → 3, 2, 1, 6, 1, 2, 3, 2. Halving waists (on-plane centres,
55-Tree): x=0 → 13, x=±y → 11, (111) → 19.

---

## ADDENDUM (2026-11-13 20:23 CST) — CAN THE TREE BE UNDERSTOOD HARMONICALLY LIKE THE CUBE?

Ace's question: the Tree divides into 6 and 12 — can it be understood
harmonically like the cube? **Answer: YES, verified by exhaustive search**
(probe: `hidden_files/tree_of_life_study/probe_harmonic.py`).

The cube's harmony (harmonic_lattice.note_at) is a *linear mod-12
labelling of the address*: pitch class = (7h + 4v) mod 12 — fifths along
one axis, major thirds along the other. The same species of labelling
exists on the Tree: pitch(i,j,k) = (a·i + b·j + c·k) mod 12 over the FCC
centres. All 12³ = 1,728 labellings were tested against the 12
nearest-neighbour pitch differences:

- **96 labellings are strict-clean:** no nearest neighbour anywhere is a
  unison (0), a semitone-class interval (1/11), or a tritone (6).
- **168 labellings are layer-pure:** all 6 in-layer neighbour intervals
  lie in the Tonnetz consonant set {3, 4, 5, 7, 8, 9} (minor/major
  thirds, fourth, fifth, minor/major sixths).
- **24 labellings achieve both.** Their neighbour difference spectrum is
  identical: {2, 3, 3, 4, 5, 5, 7, 7, 8, 9, 9, 10}, with the in-layer set
  exactly {3, 4, 5, 7, 8, 9} — each consonant interval exactly once
  around every centre. Over the 177-centre Tree the champion labellings
  use all 12 pitch classes (11–16 centres per class).
- The cube's own coefficients extended naively, (7, 4, 0), are already
  layer-pure (in-layer exactly {3, 4, 5, 7, 8, 9}) and clean except for
  exactly 2 of the 12 neighbours landing on the semitone class {1, 11}
  — the diagonal up-neighbours.

Why this works (not a coincidence): the triangular lattice *is* pitch
geometry — the Tonnetz of music theory is a triangular lattice whose 6
neighbour moves are exactly the consonant intervals above; the FCC Tree
is that lattice's 3D completion, and its 12 neighbours are the 12
directions the labelling paints with 12 pitch classes. The 6 and the 12
Ace spotted are the same numbers in both worlds because both worlds are
built on this lattice family.

**Honesty limits (the standing cube verdict applies unchanged):** the
harmony is a *labelling* — address-derived, an attention sense and a
derived projection, never identity or evidence (a centre's note says
where it sits, not what it holds). And the Tree has no single true
harmony: 24 labellings pass both tests, so harmonizing the Tree is a
*design choice among verified options*, exactly as the cube's (7, 4)
was. What is proven is admissibility, not destiny.

### Addendum 2 (2026-11-13 20:31 CST) — THE 24, SORTED: TWO FAMILIES

Ace asked to explore all 24 perfect labellings in order to pick one
(probe: `probe_harmonic_families.py`). Result: the 24 collapse into
**exactly 2 families of 12** under the lattice's own symmetries (signed
permutations of the address axes × pitch negation). Within a family
every member has an *identical* measured signature — same neighbour
spectrum {2,3,3,4,5,5,7,7,8,9,9,10}, same out-of-layer multiset
{2,3,5,7,9,10}, same second-shell axis classes {0,2,6} (at distance √2
the axis points carry a unison, a whole-tone class, and a tritone —
the perfection covers nearest neighbours only), same nearest same-note
distance √2, same same-note count (14 others in the 177-Tree). Family
members are one harmony rotated / flipped / transposed.

The families differ in exactly one structural property:

- **FAMILY A — THE STRIPED HARMONY (12).** One coefficient is 0
  (representative: pitch = (3j + 7k) mod 12). The note ignores one
  address axis entirely; the 3D harmony is the 2D Tonnetz extruded, and
  same-note centres repeat along straight rails parallel to the silent
  axis (period √2).
- **FAMILY B — THE FULL 3D HARMONY (12).** No coefficient is 0
  (representative: pitch = (i + 6j + 9k) mod 12; every member carries a
  ±6 coefficient). All three axes sing — one steps by a tritone per
  coordinate unit, but single-axis steps are not neighbour moves, so no
  neighbour ever hears it. Same-note centres scatter diagonally; no
  straight repeat rails.

What Ace is choosing is therefore NOT the neighbour music — that is
identical in all 24 — but the repeat geometry: stripes (A) vs full-3D
scatter (B), plus cosmetic orientation/key within the family. Ace's
pick is pending; nothing is implemented either way.

**Correction to Addendum 2 (2026-11-13 20:39 CST, on Ace's challenge
"sounds like all pros no cons").** Two repairs. (1) Family B was
described as having "no straight repeat rails" — wrong. B always
carries a ±6 coefficient, and centres along that axis sit 2 address
units apart, and 2 × 6 ≡ 0 (mod 12): B has a monochromatic rail along
its 6-axis too (verified: axis lines for the representatives —
A (0,3,7): x-line constant, y-line alternates 0/6, z-line cycles
0,2,4,6; B (1,6,9): y-line constant, x-line cycles, z-line alternates).
The surviving true differences: A's harmony *ignores one coordinate in
the formula* (slices perpendicular to the silent axis are note-for-note
identical; per-axis steps {0, minor third, fifth} — all friendly),
while B reads all three coordinates (per-axis steps {semitone,
tritone, major sixth} — harsh singly, never heard between true
neighbours; slices transpose per step along every axis: semitone creep,
tritone flip, sixth). (2) A third option was not presented: **the
cube's own recipe (7,4,0) on the Tree** — layer-pure, one harmony for
the whole program, at the price of exactly 2 of 12 neighbours on the
semitone class. Global cons of ANY Tree labelling, for the record: it
changes no program behaviour (the Tree is sandbox; even on the cube,
notes exist and nothing consumes them yet — a labelling is future
overlay paint, an attention sense, never identity/evidence); the
perfection is nearest-neighbour only (second shell carries unison and
tritone classes in both families); "perfect" is relative to the
consonance rules chosen for the test; and picking A or B creates a
second harmonic convention alongside the cube's (7,4) unless the cube
recipe is chosen instead. Ace's pick is now among THREE options.

### Addendum 3 (2026-11-13 21:03 CST) — COMBINING THE THREE, MEASURED

Ace asked whether Families A and B and the cube recipe (7,4,0) can be
combined (probe: `probe_combine.py`; chord triple checked separately).
Directed NN pairs in the 177-Tree: 1,608.

- **Layer alternation FAILS at the seams.** A on even (111)-layers, B on
  odd: 264 banned pairs. A alternating with the cube recipe: 260. The
  perfection is a property of neighbour *differences*; swapping the rule
  between layers makes cross-layer differences effectively arbitrary.
- **The braid FAILS.** A with a tritone flip on alternate layers: 268
  banned — the flip converts A's clean cross-layer diffs into banned
  ones at exactly the cube recipe's own flaw rate (268 = 2/12 of pairs).
- **Recipe sums DO NOT COMBINE VIRTUES.** A+B = (1,9,4): 268 banned.
  B+cube = (8,10,9): 804 banned AND 804 in-layer impure — it fails the
  flat-layer test everywhere. Sums of recipes are new untested recipes,
  not combinations.
- **The CHORD WORKS.** Carrying the notes as separate channels: the
  pair (A-note, B-note) takes 114 distinct values over 177 centres,
  most-shared pair = 3 centres, nearest same-pair centre at 2√2
  (vs √2 for any single note; single-note max sharing = 15 centres).
  The triple (A, B, cube) is UNIQUE FOR ALL 177 CENTRES — most-shared
  triple = 1. Three weak positional readings, stacked, become an
  identity-grade fingerprint of position (still derived, still a
  projection — identity OF ADDRESS, not of content).
- Species note: the cube recipe and Family A are the same species
  (striped; cube = major-third flavour {0,4,7}, A = minor-third flavour
  {0,3,7}); B is the other species. "Combine all three" therefore
  resolves to: one striped channel + the full-3D channel + the
  program's own striped channel, carried as a chord.

### Addendum 4 (2026-11-13 21:22 CST) — ACE'S DECISION: ALL THREE, AS A CHORD

Ace ruled: **"we go with all 3"** — the Tree's harmony is the CHORD
(A-note, B-note, cube-note carried as three channels; Addendum 3's
uniqueness result stands: the triple identifies all 177 centres).
The either/or pick of a single primary recipe is CLOSED. Ace's
standing requirement, recorded verbatim in substance: the chord
**must synchronize with the whole program where it fits** — it is a
derived reading over the program's existing addressing (KeyLedger /
lattice rebuild rules), never a second authority, never identity or
evidence. Ace further ruled in the same message: Smith belongs in
the future plan as **the other side of Verita** (joint research:
`SANDBOX_SMITH_VERITA_TWO_SIDES_2026-11-13.md`; Afterplan §5A
amended accordingly), and **the forces of nature must all be fully
developed and fitted where they belong** (design study:
`SANDBOX_FORCES_FULL_DEVELOPMENT_2026-11-13.md`) — with
synchronization against the whole future plan named by Ace as of
utmost importance for when the sandbox eventually opens. All of it
remains sandbox design until the sandbox-opening gates (Dell Plan,
Director circuits) admit it.
