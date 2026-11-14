# SANDBOX — THE POLYGON LADDER: TRIANGLE TO DECAGON, FLAT AND LIFTED

**Status: SANDBOX, Part II of the Flower/Sphere line (Part I:
`SANDBOX_FLOWER_SPHERE_FIELD_STUDY_2026-11-13.md`). Developed at Ace's order
2026-11-13 19:09 CST ("turn the circles into triangles and then squares,
pentagons hexagons all the way up to decagon then go 3D on each — do we
discover anything new? And patterns? Any benefit to the DellMatrix?").
Nothing in any plan; no code touched; no implementation authorized.
Acceptance is Ace's.**

Probes preserved:
`hidden_files/flower_polygon_study/probe_polygons.py` → `probe_output.json`;
`probe_fans_bipyramid.py` → `fan_bipyramid_clean.json`.

---

## 1. EXPERIMENT DESIGN (controlled substitution)

Part I studied circles (R = 1) on the Flower lattice (triangular lattice,
centre spacing s = 1). This study changes **one variable**: the shape.

- **Flat fields:** regular n-gons, n = 3…10, same centres, same circumradius
  R = 1, same orientation φ = 0 (one vertex on the +x axis). Pair / triple /
  quad overlaps by exact convex polygon clipping; field multiplicity and
  exclusive fractions by dense sampling, cross-checked against the analytic
  mean multiplicity (shape area ÷ cell area √3/2) — agreement ≤ 0.1% for
  every shape.
- **3D lifts, two kinds:** the **PRISM** (constant cross-section — the
  control; depth that changes nothing) and the **BIPYRAMID** (cross-section
  scales by 1 − |z|, apex distance 1 — the sphere-analogue, since a sphere's
  cross-sections also shrink; the bipyramid's shrink is linear, the sphere's
  is √(1−z²), so the bipyramid is the *pointier* cousin).
- **Two side questions, answered from established mathematics:** each
  polygon in its *own* natural arrangement (tiling), and each polygon as the
  *face* of a 3D solid (closure).

**Instrument honesty note.** The first field run restricted its centre set
to the origin's 7 nearest centres; points near the sampling cell's far
corner are covered by centres outside that set, and the run reported false
gaps (triangle 8.3%, square 1.0%). The analytic mean check caught it
(sampled means disagreed with area ratios); the probe was repaired to the
full lattice neighbourhood and rerun. All numbers below are from the
repaired instrument. The episode is Part I's lesson repeated: the mean is
the instrument's conscience.

## 2. THE MASTER TABLE (flat fields, R = s = 1, φ = 0)

Pair share = mean pair overlap as % of the shape's own area. Quad = common
area of a centre plus a fan of 3 neighbours, in the two inequivalent fan
orientations (fan@0 / fan@60). Field = % of the plane at each multiplicity.
Exclusive = % of one shape covered by no other.

| n | shape | area | pair classes | pair share | triple | quad fan@0 / fan@60 | field multiplicity | exclusive |
|---|-------|------|----|--------|--------|----------|------------|-----------|
| 3 | triangle | 1.299 | 1 | 11.11% | 0 | 0 / 0 | 1: 49.9%, 2: 50.1% | **33.33%** |
| 4 | square | 2.000 | 2 | 25.60% | 0.201 | **0.0359 / 0** | 1: 15.5%, 2: 42.3%, 3: 38.1%, 4: 4.2% | 6.60% |
| 5 | pentagon | 2.378 | 2 | 31.19% | 0.357 | 0.0275 / 0.0103 | 1: 7.8%, 2: 15.4%, 3: 71.3%, 4: 5.6% | 2.85% |
| 6 | hexagon | 2.598 | 1 | 33.33% | 0.433 | 0 / 0 | **3: ~100%** | 0% |
| 7 | heptagon | 2.736 | 2 | 35.17% | 0.509 | 0.0668 / 0.0621 | 1: 1.5%, 2: 3.2%, 3: 73.3%, 4: 22.1% | 0.47% |
| 8 | octagon | 2.828 | 2 | 36.09% | 0.550 | 0.0867 / 0.0874 | 1: 0.4%, 2: 2.7%, 3: 66.6%, 4: 30.2% | 0.13% |
| 9 | nonagon | 2.893 | 1 | 36.70% | 0.579 | 0.1038 / 0.1038 | 2: 2.0%, 3: 62.1%, 4: 35.9% | 0% |
| 10 | decagon | 2.939 | 2 | 37.22% | 0.604 | 0.125 / 0.1131 | 1: 0.2%, 2: 0.9%, 3: 58.5%, 4: 40.5% | 0.05% |
| ∞ | circle (Part I) | π | 1 | 39.10% | 0.705 | 0.181 / 0.181 | 3: 37.2%, 4: 62.8% | 0% |

Exact values spotted: triangle pair overlap = √3/12 (exactly 1/9 of the
triangle); hexagon pair share exactly 1/3, triple exactly √3/4.

## 3. DISCOVERIES

**PL-1 — Every polygon covers the plane; the triangle does it on a
razor's edge.** At φ = 0 no shape 3–10 leaves any gap. For n ≥ 4 this is
guaranteed by the inscribed circle (apothem ≥ 0.707 > the lattice covering
radius 1/√3 ≈ 0.577). The triangle's apothem is only 0.5 — it covers
*because* at exact alignment each Voronoi vertex lands exactly on its
edges. Rotate it and the cover leaks, measured: uncovered fraction 0% at
0°, 0.32% at 5°, 1.09% at 10°, 2.82% at 20°, 3.65% at 30°. Coverage slack
(apothem − 1/√3) grows monotonically: −0.077 (triangle, negative — covered
by alignment, not by fat), +0.130, +0.232, +0.289, +0.324, +0.347, +0.362,
+0.374, circle +0.423.

**PL-2 — The triangle field has NO group sharing at all.** Multiplicity is
only ever 1 or 2: pairs share (exactly 1/9 of each triangle), triples and
quads share nothing but boundary points, and a full third of every triangle
is exclusively its own. It is the pairwise-only world.

**PL-3 — The hexagon field is a pure triple field.** Multiplicity is
exactly 3 almost everywhere (the mean is exactly 3 by area: the R = 1
hexagon is the lattice's Voronoi cell scaled by √3, and (√3)² = 3). No
exclusive space, no pair-only space, no four-way room in any fan
orientation. Every point of the plane is shared by exactly three hexagons.
The cleanest sharing census any shape produces.

**PL-4 — Four-way rooms are orientation-locked for squares.** The square's
fan quad is 0.0359 in the fan@0 orientation and exactly 0 in fan@60: its
4-fold regions (4.2% of the plane) exist only around fans pointing along a
vertex axis. Part I's rhombus number is the fan@60 class (cross-checked:
the rhombus clip equals fan@60 for every n).

**PL-5 — The pentagon is the first shape with a true four-way room** on
this lattice (both fan orientations positive) — and, in the same breath,
the first shape that cannot tile the flat plane at all (§4). What it loses
in flatland it wins in closure (§5).

**PL-6 — The sharing ceiling survives every shape.** No polygon 3–10
produces a 5-fold common region; the multiplicity ceiling is 4, as with
circles. Part I's thick-nerve conclusion (singles / pairs / triangles /
rhombi) is shape-robust on this lattice.

**PL-7 — Flat privacy comes from corners.** Part I found the flat circle
field has zero exclusive space. Polygon fields break that: exclusive
fractions 33.3% (triangle), 6.6% (square), 2.85% (pentagon), 0.47%
(heptagon), 0.13% (octagon), 0.05% (decagon) — but exactly 0 for hexagon
and nonagon. In flatland, privacy is a corner phenomenon; the two shapes
whose corners align with the lattice's own geometry (hexagon) or average
out (nonagon) have none.

**PL-8 — Direction classes.** Pair overlap depends on neighbour direction
in 2 classes for n = 4, 5, 7, 8, 10, but is perfectly isotropic (1 class)
for n = 3, 6, 9 — the multiples of 3. The nonagon is the stealth circle:
isotropic pairs *and* identical quads in both fan orientations.

**PL-9 — As n grows, everything converges to the circle and the only new
content is corners.** Area → π, pair share → 39.1%, slack → the circle's.
What polygons add over circles is exactly: direction-dependence,
flat exclusive corners, exact tilings (3/4/6), and closure behaviour
(5 closes, 7+ flare). Nothing else.

## 4. THE TILING DIVIDE AND THE CURVATURE BOUNDARY AT SIX

In its *own* arrangement (angles around a point must sum to 360°):

| n | interior angle | around a point | tiles flat alone? |
|---|----|----|----|
| 3 | 60° | 6 × 60 = 360 | **yes** (3⁶) |
| 4 | 90° | 4 × 90 = 360 | **yes** (4⁴) |
| 5 | 108° | 3 × 108 = 324, gap 36° | no |
| 6 | 120° | 3 × 120 = 360 | **yes** (6³) |
| 7 | 128.57° | 2 = 257.1 (gap 102.9); 3 = 385.7 (overlap) | no |
| 8 | 135° | 2 = 270, gap exactly 90° | no — but the gap is a square: **4.8.8** Archimedean tiling |
| 9 | 140° | 2 = 280, gap 80° (no regular partner) | no |
| 10 | 144° | 2 = 288, gap 72° | no Archimedean tiling contains a decagon |

As **faces of convex solids** the sign of curvature flips at six:
triangle → tetrahedron / octahedron / icosahedron; square → cube;
pentagon → dodecahedron (positive curvature: the shape *closes*);
hexagon → nothing (3 × 120° = 360° is exactly flat — zero curvature);
heptagon and above → no convex closure (angle sums exceed 360° — negative
curvature; they tile the *hyperbolic* plane, e.g. {7,3}, {8,3}).

**The fullerene law.** Any closed trivalent skin made of pentagons and
hexagons contains **exactly 12 pentagons** (Euler's formula) — the
soccer ball is 12 pentagons + 20 hexagons. A hexagon world cannot close
without its twelve pentagons; the pentagons are where the curvature lives.

Space-fillers by extrusion: triangular prism, cube, and hexagonal prism
tile 3D space (the three flat tilers, extruded). The truncated octahedron
(square + hexagon faces) also tiles space alone.

## 5. THE 3D LIFTS

**Prism (the control).** Cross-section never changes, so every flat result
carries up verbatim: multiplicity, patterns, coverage (never breaks), and
exclusive volume fraction = the flat exclusive fraction. A prism adds
*storage depth* and nothing else.

**Bipyramid (the sphere-analogue).** Cross-section scale s = 1 − |z|.

- **Exclusive volume fraction of one solid:** triangle **77.6%**, square
  51.0%, pentagon 41.0%, hexagon 33.6%, heptagon 32.9%, octagon 31.3%,
  nonagon 30.1%, decagon 29.5% — against the **sphere's 8.73%** (Part I).
  The taper rate is a privacy dial: the pointier the solid, the more of it
  is private, because overlaps die quadratically as the sections shrink.
- **Above half-height, every bipyramid field is fully disjoint** (at
  z = 0.5 the sections reach exactly halfway to each neighbour — touching
  at most). The entire upper half of every bipyramid is cap. The sphere,
  shrinking as √(1−z²), still overlaps at z = 0.5.
- **Covered height** — the fraction of the half-height over which the
  field stays gapless (analytic, from apothems; z* = 1 − 1/(√3·a)):

| shape | triangle | square | pentagon | hexagon | heptagon | octagon | nonagon | decagon | sphere |
|---|---|---|---|---|---|---|---|---|---|
| covered height | 0 (base only) | 0.184 | 0.286 | 0.333 | 0.359 | 0.375 | 0.386 | 0.393 | **0.816** |

  The sphere keeps its shared floor far deeper than any bipyramid —
  roundness is what makes depth *shared*; pointiness makes depth private.

## 6. BENEFIT TO DELLMATRIX (graded)

**MECHANISM-grade**

- **B1 — A selection theorem for the Part I kernel.** If the Flower kernel
  ever wants polygonal cells, the ladder prices every choice. The
  **hexagon** is the unique polygon that (a) tiles alone — at apothem
  sizing it *is* the Voronoi partition, every point assigned to exactly
  one centre; (b) at Flower radius gives the pure constant-3 sharing
  field (PL-3); (c) is direction-isotropic on the lattice. Circle =
  maximal group sharing; hexagon = exact triple sharing + partition mode;
  triangle = pairwise-only sharing. Those three are the load-bearing
  shapes; the rest are priced variants.
- **B2 — Pairwise-only topology exists geometrically.** A structure that
  must enforce "two-party sharing, no group rooms" (a strict pairwise
  channel topology, if one is ever wanted) is enforced *by the geometry
  itself* in a triangle field (PL-2), not by a rule other code must
  remember. Price: the critical-cover alignment obligation (PL-1 leak
  curve is the maintenance receipt).
- **B3 — The privacy dial is quantified.** Exclusive volume by solid:
  bipyramids 29–78%, sphere 8.7%, prisms = flat values. If idea depth is
  ever given a shape, the shape *is* the privacy policy, with numbers
  attached; covered-height (§5) says how deep the shared floor extends
  before caps begin.
- **B4 — A packing constraint for the windowed workspace (Future Plan).**
  Only triangle / square / hexagon windows tile a screen gaplessly.
  Octagon windows require square companions (4.8.8). Pentagon windows
  cannot tile — they leave 36° wedge gaps that would have to be *designed*
  as corridors or docks, never discovered as accidents.
- **B5 — The 12-pentagon receipt for closed worlds.** If the Sphere
  perspective / Room is ever skinned in hexagonal cells, closure requires
  exactly 12 pentagonal cells, placed deliberately. A hard, checkable
  design receipt (§4).

**PATTERN-grade**

- **B6 — A curvature vocabulary for field topology:** pentagon =
  closing, hexagon = flat, heptagon+ = flaring. Flat Plane, closed world,
  open flare — three postures a field can take, named by the shape that
  forces them.
- **B7 — Three kinds of depth:** prism = uniform depth (storage),
  bipyramid = fast-tapering depth (essence/summary), sphere =
  slow-tapering depth (the Part I cap). A vocabulary for how an idea's
  private depth is shaped; no consumer yet.
- **B8 — Anisotropy as a receipt:** a field can report its direction
  classes (1 = isotropic sharing, 2 = direction-dependent). The nonagon's
  isotropy is recorded as a curiosity with no consumer.

**REJECTED (costume)**

- **B9** — Assigning polygon counts to idea types or Dells ("pentagon
  ideas"). No mechanism; rejected.
- **B10** — Polygon perspectives. The perspective set is settled (Ace,
  2026-11-08); nothing proposed.
- **B11** — Heptagon–decagon fields as DellMatrix structures. They work,
  but everything they do, the circle does with more sharing; their only
  surplus is corners nobody consumes.

## 7. VERDICT

Yes, the ladder discovers new things — and its deepest result is a
*sorting*: of the eight shapes, exactly three carry distinct structural
jobs (**triangle = pairwise-only + flat privacy, hexagon = partition +
pure triple sharing, circle = maximal group sharing**), two carry priced
specialities (**square = the practical tiler whose group rooms are
orientation-locked; pentagon = the closer, flatland's failure and 3D's
key**), and three (heptagon, octagon, nonagon, decagon — four, counting
honestly) mostly *confirm the circle from below*, contributing the
curvature boundary at six, the 4.8.8 partnership, and the fullerene
twelve. The ladder is not a new system and proposes no authority; it is a
**price list and selection evidence for the Part I kernel**, plus two
design receipts (B4, B5) banked for the Future Plan's workspace and world
builders. Corners are the content: everything a polygon knows that a
circle doesn't is written in its corners.

## 8. OPEN QUESTIONS

- **Q-P1.** Orientation φ was probed as a dial only for the triangle
  (PL-1). A φ-sweep for n = 4, 5, 7, 8, 10 would price alignment
  sensitivity per shape; the hexagon/nonagon/circle are φ-immune or
  φ-averaged by symmetry.
- **Q-P2.** All fields sat on the Flower (triangular) lattice. A square
  field on a *square* lattice is the classic grid — unprobed here; the
  comparison would separate shape effects from lattice effects.
- **Q-P3.** Mixed tilings as fields (4.8.8 octagon+square sharing anatomy)
  are unprobed; the mixed field's nerve is the natural next census if a
  consumer appears.
- **Q-P4.** The bipyramid's per-layer *pattern census* (Part I's Model O
  programme lifted) was not run — only coverage and exclusivity by layer.
- **Q-P5.** Whether any DellMatrix consumer actually wants pairwise-only
  topology (B2) or shaped depth (B3) is UNKNOWN; both stay sandbox
  instruments until one does.

## APPENDIX — KEY NUMBERS

Pair overlap (mean over 6 neighbour directions), absolute: 3: √3/12 ≈
0.144338; 4: 0.511966 (directions 0.5 / 0.517949); 5: 0.741590; 6: √3/2 ≈
0.866025; 7: 0.962481; 8: 1.020853; 9: 1.061696; 10: 1.093765; circle:
1.228370. Triple (unit triangle of centres, both orientations agree for
every n): 0 / 0.200962 / 0.356577 / 0.433013 / 0.508530 / 0.550079 /
0.579285 / 0.604196; circle 0.704771. Mean multiplicity (= area ÷ √3/2):
1.5 / 2.309 / 2.746 / 3.0 / 3.160 / 3.266 / 3.340 / 3.394; circle 3.628.
Triangle rotation leak (uncovered % of plane): 0° 0; 5° 0.32; 10° 1.09;
20° 2.82; 30° 3.65. Bipyramid exclusive volume %: 77.6 / 51.0 / 41.0 /
33.6 / 32.9 / 31.3 / 30.1 / 29.5 (sphere 8.73, Part I).
