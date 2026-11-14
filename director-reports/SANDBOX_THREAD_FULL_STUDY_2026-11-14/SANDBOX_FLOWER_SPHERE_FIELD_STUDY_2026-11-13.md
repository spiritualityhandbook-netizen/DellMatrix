# THE FLOWER / SPHERE FIELD STUDY — CIRCLES, SPHERES, SHARED SPACE, NEGATIVE SPACE

## Sandbox study by Ace's order, 2026-11-13. Status: SANDBOX —
## developed here until Ace accepts it. Nothing in this study is
## implemented, placed in any plan, or authorized by its existence.
## Placement proposals in §7 are proposals only, awaiting Ace.

Ace's charge: the Flower of Life was studied before and lives in the
codebase — as a 2D perspective of circles, and by making each circle a
sphere, from a 3D perspective. Negative space and overlapping circles
that share space were discovered there. Study that, mirror it with
DellMatrix and with the Future Plan, and uncover whether it is its own
system, better suited inside other systems, or both.

**Method.** (1) Recovered the prior study of record — the MPC-012-R
Flower/sphere recovery of 2026-10-03 (`~/workspace/
mpc012r-flower-sphere-recovery.md`, assessment-only at the time) — and
re-inspected the live mechanisms in a checked clone
(`~/workspace/nbd-omega-wake`, branch `uni/track-d-bridge-planning`,
head `05859c0`). (2) Ran new bounded mathematical probes built for
this study (scripts and raw output preserved under
`hidden_files/flower_sphere_study/`). Every headline number below was
produced by two independent instruments that agree, or is labeled
with the single instrument and its budget. Geometry claims are
mathematics; semantic claims are graded MECHANISM / PATTERN /
METAPHOR in the mirror sections, per the mirror-atlas convention.

**Honesty lock.** Overlap is not truth (the in-tree law: coherence ≠
truth). A shared region is a *measured meeting*, nothing more. No
claim in this study assigns meaning to a void, a channel, or a lens
until a DellMatrix consumer with a falsification test exists — the
same discipline the codebase already carries in
`sacred_geometry.py`'s header, where Čech nerves, power diagrams,
and alpha filtrations stand DEFERRED (GDP-001 Phase 3, items
3.4.2–3.4.4) "only with proven consumers and a mathematical
derivation admitted under the admission contract." This study's job
is to find out what the geometry actually does, and which consumers
could honestly exist.

---

# 1. WHAT IS ALREADY IN THE CODEBASE (recovered, verified today)

| Piece | Where | State |
|---|---|---|
| Flower centers (hex packing) | `form/dell_matrix/sacred_geometry.py::flower_centers` | LIVE. rings 0/1/2/3/4 → 1/7/19/37/61 centers = hexagonal numbers 1+3r(r+1). Re-verified today. |
| Two-circle overlap (vesica) | `sacred_geometry.py::vesica` | LIVE. Classification coincident/separate/contained/vesica + correct lens geometry (unit circles at d=1: lens width √3, re-verified). Its `verita` *score* is a heuristic (see below). |
| Pairwise edges on ideas | `sacred_geometry.py::verita_between_nodes` → `graph_view.build_view` | LIVE. Overlap → `kind="vesica"` graph edges. Radius is derived from idea score by an arbitrary mapping (`1.2×(0.6+0.4·min(2,score))`) — mathematically unjustified, flagged since 2026-10-03. Failure is honest: if geometry raises, graph_view records "vesica geometry unavailable" and fabricates nothing (P3 R3.4 proof). |
| One canonical vesica | `verita.py::vesica_strength` delegates to `sacred_geometry.vesica` | FIXED since the recovery era: the 2026-10-03 duplicate-authority finding (R4-A1) is closed; a 424-case delegation sweep + mutation test stand in `form/mandell/p3_r34_geometry_proof.py`. |
| Flower as perspective | `perception.py` Form.FLOWER; `plane.py` Perspective.FLOWER; `harmonic_lattice.plant_flower` | LIVE as a *reading*: centers snap onto the same lattice; coordinates stay, the reading changes. The Future Plan's settled perspective set (square, circle, cube, sphere, core, flower) already contains it. |
| Sphere form | Form.SPHERE / Perspective.SPHERE; `first_person.neighbors_sphere` | LIVE as a reading (radial shells, same centers). It is **not** a 3D ball field: no sphere of radius R is ever placed in 3D space. |
| Legacy dual lattice | `src/core/dual_lattice.js` (frozen 2026-08-01) | HISTORICAL. Nodes carried `{x,y,z}` sphere coordinates with **z ≡ 0 always**; `computeVesica` used 3D distance on 2D data; `negativeSpace = {channels: [], activeForces: []}` — channels declared, **never populated, never computed**. |
| Space force | `forces.py::SpaceForce` | LABEL ONLY. Description: "Negative space and voids between nodes — room to grow." No computation behind it (allowlisted as benign in the R3.4 proof). |
| Positions | `plane.py::Unit` (x, y; default 0.0) + `spatial_authority.py` | CHANGED since 2026-10-03. A canonical Spatial Authority now owns post-placement positions/dynamics under admitted equations, with the laws LOCATION != TRUTH and DISTANCE != RELATIONSHIP AUTHORITY written into its header. The old "(0,0) vacuity" blocker is therefore *partially* retired: positions can be meaningful now — but a Flower *radius* for an idea still has no admitted meaning. |
| True 3D sphere field | — | **NEVER BUILT.** No 3D packing, no volumetric voids, no triple/higher-order overlap, no pockets/cavities, no channel computation exists anywhere in the tree (grep-verified today; the R3.4 policy proof asserts the same for form/). |

So Ace's memory is right about the *study* and the *intent*
(`docs/DUAL_LATTICE.md` records the origin verbatim: "2D circles →
equal units, shared centers… Circles → spheres → contact packing,
volumetric voids. Negative space → real medium for forces."), and
the 2D half is real code. The 3D half — spheres actually occupying
space, sharing volume, enclosing voids — was designed, named, and
never built. This study builds the mathematics in the sandbox and
measures what it would do.

---

# 2. THREE MODELS THAT MUST NEVER BE MERGED

Most confusion in the historical record comes from one word —
"negative space" — covering three different objects. The study
separates them permanently:

**MODEL F — FILLED.** Each center carries a filled disk (2D) or ball
(3D) of radius R. Questions: how much space is shared (intersection
measure), how much is exclusive, what does the *complement* (true
negative space) look like — exterior, pockets, cavities, channels.

**MODEL O — OUTLINE.** Each center carries only a circumference (2D)
or spherical surface (3D). The curves/surfaces partition space into
faces/cells. Every face has a constant *membership pattern* (the set
of disks/balls containing it). These faces are what the eye sees as
the Flower's petals and "negative space" in drawings — but a face
inside three disks is not outside anything; it is boundary-carved
space, not complement.

**MODEL N — NATIVE 3D.** Centers themselves leave the plane and form
a 3D close-packed (FCC) arrangement. This is an *extension*, not the
historical lift; it answers "what if the Flower were born in 3D?"

And one dial governs all three: **ρ = R / s**, radius over
center spacing. The Flower lives at **ρ = 1** (spacing = radius,
which is why neighbors form the classic vesica). Everything below
shows the Flower's character comes from that one choice.

Unless stated otherwise, R = s = 1.

---

# 3. MEASURED RESULTS

## 3.1 The sharing cascade (Model F, one Flower cell)

Exact formulas, cross-checked by independent quadrature / sampling
(pair lens area: closed form vs polar quadrature agree to 5×10⁻⁹;
triple/quad: QMC vs polar-slice integration agree to ≤0.05%).

| Sharing | 2D disks (area) | % of each disk | 3D lifted balls (volume) | % of each ball |
|---|---|---|---|---|
| Pair (d = 1) | 2π/3 − √3/2 = **1.228370** | **39.10%** | 5π/12 = **1.308997** | **31.25%** |
| Triple (unit triangle) | **0.704771** | **22.43%** | **0.671830** | **16.04%** |
| Quad (unit rhombus) | **0.181172** | **5.77%** | **0.107742** | **2.57%** |
| 5 or more | point only | 0 | point only | 0 |

Two structural facts inside the table:

- **The cascade is positive through order 4, then stops dead.**
  Five Flower balls never share a *region* — only points (e.g. a
  center lies exactly on its six neighbors' surfaces; the six outer
  circumferences concur at the center). Shared *space* in the Flower
  is a 1–2–3–4 phenomenon. Any future "meeting" semantics that needs
  a 5+-way shared region is geometrically empty here.
- **The rhombus identity (derived, then measured).** The 4-fold
  common region of a unit rhombus equals *exactly* the lens of its
  long-diagonal pair: in 2D, quad area 0.181172147 = lens at d = √3
  = π/3 − √3/2 to nine digits; in 3D, quad volume 0.1077415 (slice
  integration) vs diagonal lens formula 0.1077416. Proof sketch: the
  diagonal pair's lens is convex, its extreme points are the other
  two centers (2D) / a circle through them (3D), and direct
  computation shows every lens point lies within both side balls —
  so the side balls cut nothing from the diagonal lens. The heart
  of a four-way meeting *is* a two-way meeting of the far pair.

## 3.2 Multiplicity fields — how shared is a typical point?

Periodic fields (infinite lattice), deterministic grids; every
distribution's mean was checked against an independent analytic
density (agreement ≤0.07% in the worst, FCC, case; ≤5×10⁻⁵ in the
lifted case).

**Flat Flower (2D, ρ = 1).** Every point of the plane lies in
exactly 3 or 4 disks (open regions): **37.24% of area is 3-fold,
62.76% is 4-fold.** There is *no* open region belonging to fewer
than 3 disks — no exclusive space, no pair-only space, anywhere in
the interior. Per disk: **30.80% of each disk is 3-fold shared,
69.20% is 4-fold shared** (derived from the analytic mean
multiplicity 3.69203, confirmed by direct sampling of one disk:
30.8% / 69.2%).

**Lifted Flower (3D, same centers in z = 0, balls).** Within the
slab |z| ≤ 1 around the plane, volume by multiplicity:
0-fold 7.31%, **1-fold 21.12%**, 2-fold 12.66%, 3-fold 40.25%,
4-fold 18.66%. Per ball: **8.73% exclusive**, 10.47% pair-only,
49.94% triple, 30.86% quad (QMC, 2¹⁹ samples; mean multiplicity
3.0293 matches the analytic sum of lens volumes to 1.4×10⁻⁵).
The lift *creates* private and pair-only volume that the flat
Flower does not have — while leaving the planar sharing untouched.

**Native 3D FCC Flower (Model N, spacing 1, radius 1).** Volume by
multiplicity: 4-fold 11.35%, 5-fold 11.30%, 6-fold 52.01%,
7-fold 24.72%, 8-fold 0.62% — and **nothing below 4-fold at all**.
Born in 3D, the Flower is *more* shared, not less: no private,
pair-only, or triple-only volume exists in its interior.

## 3.3 The pattern census — faces vs membership patterns (Model O)

Outline arrangements counted exactly by planar Euler characteristic
(instrument validated on controls: two overlapping circles → 4
faces; three Venn circles → 8 faces; vertex-incidence sums match
edge counts at every ring). Membership patterns counted by dense
sampling (two resolutions, 1001² and 2001², identical census at
ring 3).

| Flower | Bounded faces (Euler) | Distinct membership patterns (sampled) | Pattern breakdown (1/2/3/4-fold) |
|---|---|---|---|
| rings = 1 (7 circles) | **24** | **24** | 6 / 6 / 6 / 6 |
| rings = 2 (19 circles) | **78** | **78** | 12 / 12 / 24 / 30 |
| rings = 3 (37 circles) | **162** | **137** | 16 / 18 / 46 / 57 |

- At rings 1–2 the two instruments agree *exactly*: every bounded
  face carries its own membership pattern. (Bounded-face counts fit
  3r(5r+3) for r = 1, 2, 3 — recorded as a fit, not a theorem.)
- At ring 3 they split: **162 faces, 137 patterns ⇒ at least 25
  faces repeat a pattern that another, disconnected face already
  carries.** PATTERN ≠ PLACE from ring 3 outward: *which* ideas
  share does not determine *where* the sharing happens. Any system
  built on this geometry needs two keys — the pattern (a set) and
  the address (a place) — never one.
- **The lift is a strict superset.** For rings 1–2, every 2D pattern
  survives in 3D, the triple and quad pattern *sets are identical*,
  and the lift adds exactly the patterns the plane hides:
  ring 1: +7 (the center's exclusive pattern + the 6 spoke-pair
  patterns); ring 2: +37 (7 hidden singles + 30 hidden pairs).
  Total lifted patterns: ring 1 → **31**, ring 2 → **115**. The
  added patterns live in the caps above/below the plane: in 2D,
  spoke-pair lenses and inner disks are entirely covered by
  neighbors; in 3D their caps rise out of the crowd and become
  their own.
- Codebase tie-in: `vesica_pairs_from_centers` today returns exactly
  the nearest-neighbor pairs (12 / 42 / 90 / 156 at rings 1–4,
  re-verified) — i.e. the current code sees the *edge* layer of a
  four-layer structure (edges, triangles, rhombi) whose upper layers
  it has never computed.

## 3.4 Negative space, settled per model

**Model F, flat (2D, ρ = 1): there is no interior negative space.**
The triangular lattice's covering radius is 1/√3 ≈ 0.577 < R, so
the disks cover the plane outright. For a finite Flower, the
complement is one connected exterior (raster cross-check at ring 2,
700² grid: exactly 1 complement component, 0 enclosed). What looks
like "space between the circles" in a drawing is Model O faces —
inside the disks.

**Model F, lifted (3D, ρ = 1): no enclosed voids, ever.** Any
complement point with z > 0 escapes straight up (distance to every
center, all in z = 0, grows monotonically), and z < 0 straight
down. A finite lifted Flower's complement is a single connected
exterior; the infinite one's is two open half-spaces. Inside the
slab, the plane stays covered up to |z| = √(2/3) ≈ 0.816 (where the
cross-section radius √(R²−z²) falls to the covering radius);
beyond that, gaps open — as *openings*, not cavities.

**Model F, native FCC (ρ = 1): no negative space at all.** FCC
covering radius is √2/2 ≈ 0.707 < R (octahedral holes sit 0.707
from their six centers, tetrahedral 0.612 from their four), so the
balls cover space — consistent with the measured minimum
multiplicity of 4.

**Where voids and channels honestly live: ρ < 1.** The dial, for
the record (s = spacing):

| Regime | 2D triangular | 3D FCC |
|---|---|---|
| ρ ≥ covering (0.577 / 0.707) | plane covered; no voids | space covered; no voids |
| overlap with pockets | 0.5 ≤ ρ < 0.577: one enclosed curvilinear-triangular pocket per unit triangle | 0.577 < ρ < 0.707: enclosed octahedral/tetrahedral cavities, **no throats** |
| channel network | — (pockets stay sealed at every ρ with overlap) | 0.5 ≤ ρ < 0.577: cavities joined by throats at triangle-face centers (throat clearance (1/√3 − ρ)·s) — a true channel network |
| ρ < 0.5 | disks disjoint; complement fully open | balls disjoint; complement fully open |

And the dimensional twist: a 2D pocket (enclosed at ρ ∈ [0.5,
0.577)) becomes, under the lift, a **vertical well** — the pocket's
cross-section only widens as |z| grows, so what is a sealed void in
the flat Flower is an open passage in the lifted one. *Dimension
converts pockets into channels.* In the flat model, channels with
overlap do not exist at all; anyone who wants channels must either
lower ρ, break the lattice's regularity (defects = doors), or lift.

---

# 4. FINDINGS (the discoveries, numbered)

- **FL-1 — The flat Flower has no privacy.** At ρ = 1 every
  interior point belongs to ≥3 disks. Exclusive and pair-only
  regions exist only at a finite Flower's boundary. A flat,
  fully-woven field cannot hold a private or two-party space in
  its interior — privacy requires a boundary or a dimension.
- **FL-2 — The lift creates privacy without separation.** Making
  each circle a sphere adds exclusive caps (8.73% of each ball)
  and pair-only caps, while the shared planar pattern — triples
  and quads identical, as sets — is untouched. Privacy comes from
  *depth*, not distance: nothing had to move apart.
- **FL-3 — Sharing has a hard ceiling of 4 (Flower geometry).**
  Positive-measure common intersection exists only for singles,
  nearest-neighbor pairs, unit triangles, and unit rhombi. The
  honest higher-order structure is a *thick nerve* on those four
  layers — not the thin Čech nerve, which would also count
  measure-zero touches (a center point where 7 disks "meet")
  as meetings.
- **FL-4 — Pattern ≠ place (ring 3+).** 162 faces / 137 patterns.
  The same sharing combination occurs in disconnected places.
  Identity needs address + pattern, two keys.
- **FL-5 — "Negative space" was three things.** Complement void
  (Model F), arrangement faces (Model O), and cross-section
  pockets that become wells under lift. The historical code's
  empty `channels: []` and the Space force's label conflated all
  three. Each kind is computable; they are not interchangeable.
- **FL-6 — At the Flower's own ratio, there are no channels.**
  Channels (throat-connected cavities) exist only at ρ ≲ 0.577
  in 3D, or as Model O face adjacency, or via lattice defects.
  A "channel" displayed at ρ = 1 in the filled model would be
  theater — the exact failure the codebase's no-theater law and
  R3.4 policy proof exist to prevent.
- **FL-7 — The center of the Flower is the most public place in
  it.** The central disk has *no* exclusive area in 2D (its
  neighbors cover it entirely; it is the only ring-1 disk with no
  single pattern), and its center point is the unique 7-fold
  touch. Middle ≠ private.
- **FL-8 — Native 3D intensifies sharing.** FCC Flower: minimum
  multiplicity 4, typical 6. Going 3D natively does not open the
  Flower up; it closes it further. The *lift* (2D centers, 3D
  balls) is the version with air in it.
- **FL-9 — The four-way heart is a two-way lens.** Rhombus
  identity, §3.1: the deepest sharing in the Flower is carried by
  its far pair. Depth of sharing and breadth of sharing trade
  against each other measurably (39% → 22% → 6% in 2D).
- **FL-10 — The structure is finite and enumerable.** Patterns
  per Flower: 24 / 78 / 137 (2D), 31 / 115 (lifted, rings 1–2).
  The whole sharing anatomy of a Flower field is a small,
  computable, cacheable census — not an emergent fog.

---

# 5. MIRROR — DELMATRIX SYSTEMS

Grades: MECHANISM (the geometry computes something the system can
honestly consume), PATTERN (structural rhyme worth designing with),
METAPHOR (picture only; must never be wired as if it were a
mechanism).

| DellMatrix system | Mirror | Grade |
|---|---|---|
| **Plane / perspectives** | Flower and Sphere are already settled perspectives (readings over one lattice). The study changes nothing about them — and warns against promoting the Flower reading into a spatial truth: the Spatial Authority owns positions; the Flower may only *measure* what those positions imply. LOCATION != TRUTH stands. | MECHANISM (as constraint) |
| **Spatial Authority** | The missing substrate from 2026-10-03 now exists: admitted positions and dynamics. A Flower field becomes computable the moment an idea *radius* is admitted. Today radius-from-score is arbitrary; the honest radius candidates are Scope/reach records, not score. Until a radius rule passes the admission contract, Flower measurement over real ideas stays refused — geometry over the *formal* Flower (equal radii) is the only admitted case today. | MECHANISM (gated) |
| **Verita (VERITA-MEET)** | Pair Verita today is a heuristic score stapled to a correct lens. The cascade gives it a defined replacement family: lens fraction of union (Jaccard) or of the smaller disk for pairs — and, new, *meeting measures* for triples and rhombi (common-intersection fraction). A "Verita of a meeting" for a set, not just a pair. Firewall unchanged: coherence-of-meet ≠ truth; the three Veritas stay namespaced. | MECHANISM (candidate) |
| **Graph view / SemanticGraph** | Today's vesica edges are the nerve's 1-skeleton. The thick nerve adds triangle and rhombus *hyperedges* with measured shared fractions — the graph becomes a simplicial structure where a triple-shared region is a fact of a different kind than three pairwise edges (three pairs can overlap with *no* common point; in Flower geometry they always have one — in irregular fields the distinction is real and checkable). | MECHANISM (candidate) |
| **Resonance** | Resonance currently *logs* the word "vesica" while computing tag/affinity scores (EQ-RES-003, rename-or-wire action R4-A4 still open in the ledger). The nerve could supply real geometric candidates to resonance — under R4-A5's reconcile-don't-merge law: geometry proposes, resonance's own authority disposes; never averaged into one number. | PATTERN |
| **Nursery & sandboxes** | A sandbox is an *engineered exclusive zone* — precisely what the flat Flower cannot grow naturally (FL-1). The lifted model shows the second way to make one: a cap, private volume over a shared projection. Sandbox semantics today are identity-based (sandbox_id, isolation key) and need no geometry; the cap is the *picture* of why a sandbox can be fully private while its members stay placed in the shared field. | PATTERN |
| **Growth (SELECT law)** | Growth already works on selections, never the whole field by default. A nerve *diff* is the natural preview receipt for a growth step: patterns created / destroyed / moved, computed before applying — "this growth creates 2 triple meetings, dissolves 1 rhombus, isolates nothing." Falsifiable against the post-growth census. | MECHANISM (candidate) |
| **Forces — Space** | The Space force's label ("negative space and voids… room to grow") can finally be given an honest, computable referent: the field's *negative-space class* — COVERED / POCKETED / CHANNELED / OPEN — computed from positions + radius + ρ regime (§3.4 table). As a *report*, not a force: nothing in the geometry pushes anything. | PATTERN (report, not force) |
| **Harmonic lattice / cube** | Flower centers already plant onto the same lattice (`plant_flower`). The nerve census is a *derived projection* in exactly the harmonic sense: rebuilt from source records, never hand-filled, lossless back to member IDs. It belongs in the same epistemic class as the cube — a witness instrument, not a store. | MECHANISM (as projection class) |
| **DuoBeta** | Nerve changes (a pattern born when ideas move, a rhombus dissolved) are *observations* — the cleanest kind: deterministic, receipted, content-free. They may enter DuoBeta only through its existing gate (≥3 matching outcome evidences, propose → gate → apply); geometry never learns on its own, and advisory reranking stays truth-identical. | PATTERN |
| **Completeness Law / census (X11)** | The pattern census is the Completeness Law's spatial face: an idea whose disk/ball shares *nothing* — no pair pattern, in no triangle — is the geometric form of an orphan: present, covering nothing with anyone. Conversely a component can be *covered* (participating) or *stood down* exactly as the law's receipts describe. The census makes "neglected" *visible as a hole* the same way the atlas does. | PATTERN |
| **Elastic Limits** | The Flower grows by shells: ring r adds exactly 6r centers, and the pattern census grows with it (24 → 78 → 137). Nothing pre-allocated, nothing walled: the Flower is a second native example of the doctrine's shape — capacity as a growing shell structure, each shell's cost and content computable in advance. | PATTERN |
| **The Dock / Psalm seats** | The cap picture (FL-2) is the Dock's sandbox-room picture with geometry under it: a docked Psalm's work can be *exclusive in depth* while its planar projection — what it is working on, where it sits in the field — stays witnessable. Privacy without leaving the room. This matches the Dock spec's "sandbox reflects the whole, does not affect it" and the Witness Law; it adds no permission by itself. | PATTERN |
| **LatinMandell** | No honest mirror found. Morpheme sharing is set overlap over *tokens*, already served by existing token/Jaccard machinery; dressing it in Flower geometry would be costume. Recorded as a deliberate non-mirror. | REJECTED (as mirror) |

---

# 6. MIRROR — THE FUTURE PLAN

- **Perspectives are settled — this study asks for no new one.**
  The Future Plan's six forms stand (Ace, 2026-11-08). Flower and
  Sphere are already among them. What the study adds is not a
  seventh perspective but a *measurement layer under two existing
  ones*.
- **Room and Sky are the two models.** The Future Plan's Plane as
  a ROOM (3D, walkable) and as a SKY (2D, clouds) maps exactly
  onto Model F-lifted (volumes, caps, sharing) and Model O (the
  visible face pattern). Sky shows the pattern; Room contains the
  sharing. One field, two honest readings — the same dual the
  codebase's perception law already states ("coordinates stay;
  reading changes").
- **Afterplan placement — PROPOSED, not placed.** If Ace accepts
  this study, the natural home is the Afterplan's perspective
  neighborhood (§5A Smith tab, §5B Atlas family): a **Flower /
  Nerve witness tab** beside the cube, Smith, and atlas tabs —
  one more derived witness instrument showing, per idea, its
  exclusive / pair / triple / rhombus sharing and the field's
  negative-space class, every number resolving back to records.
  It is *not* placed by this study; the Afterplan changes only on
  Ace's word, as with §5A/§5B before it.
- **HCN organs (Afterplan §5B.1 identities, extended by rhyme
  only).** WARD's watchlist gains a geometric meaning: the field's
  boundary and its coverage class. SEED VAULT as cache: the
  pattern census is compute-once-serve-by-address material.
  RETURN: a rollback restores an earlier *field state*, and the
  nerve diff between states is its receipt. TUNE: ρ is literally
  a tuning dial — the one knob that moves a field between
  covered, pocketed, channeled, and open. These are design
  rhymes for the future circuits to confirm or discard, not
  amendments to the frozen R3 baseline.

---

# 7. VERDICT — ITS OWN SYSTEM, A SHARED LAYER, OR BOTH

**Both — asymmetrically. The Flower/Sphere field is its own
KERNEL and a shared DERIVED LAYER. It is not an authority.**

Anatomy check against the Foundation of Dells
(DELL = ADDRESS × OPERATION × PRODUCT × TEST × TRACE), at field
scale:

- **ADDRESS** — the center: a lattice point / idea ID. Permanent,
  issued, never derived from content. ✓ exists today.
- **OPERATION** — overlap & cover: given centers + an admitted
  radius rule, compute intersections, multiplicities, patterns,
  complement class. Pure function of its inputs. ✓ mathematics
  proven in this study; ✗ radius rule for real ideas not yet
  admitted.
- **PRODUCT** — the nerve census: per-idea exclusive/shared
  measures, the pattern list (pairs / triangles / rhombi), the
  negative-space class, and diffs between field states. ✓
  computable, enumerable, finite (FL-10).
- **TEST** — the cover test: does the census from the kernel
  match an independent sampling of the same field (the exact
  agreement pattern this study used: Euler vs sampling, analytic
  means vs QMC)? A field whose two instruments disagree is a
  field mis-measured. ✓ demonstrated.
- **TRACE** — every product resolves back to center IDs and the
  radius rule that produced it; a census is rebuilt from records,
  never hand-filled (the harmonic projection rule). ✓ by design
  class.

So the kernel earns its own existence the way the harmonic
lattice did: one job (measure sharing), real borders, receipts.
But its *outputs* are a shared service — Verita-meet measures,
graph hyperedges, growth previews, WARD's border report, the
Dock's cap picture all read the same census — and its *standing*
is derived: it owns no truth, grants no eligibility, moves
nothing. In HCN language it is an organ, not a seat. In the
codebase's language it joins `sacred_geometry` where it already
lives: a calculator with a census, awaiting admitted inputs.

**What would make it costume** (refuse on sight): overlap read
as truth or agreement; a channel drawn at ρ = 1 in the filled
model; a radius invented from score without admission; a
5+-way "shared region" claimed in Flower geometry; the Flower
used as a worldview rather than a measurement.

**Falsification tests for any future circuit** (the study's
teeth; a circuit that cannot pass them does not open):

- **F1 (kernel correctness).** For any field state, kernel census
  vs independent dense sampling must agree on pattern sets and
  multiplicity means within stated tolerance — the standard this
  study's own probes met.
- **F2 (consumer reality).** At least one named consumer must
  make a *different, checkable decision* with the census than
  without it (growth-preview accuracy against post-growth
  census is the standing candidate). No consumer ⇒ display
  only, forever.
- **F3 (radius admission).** No semantic use until a radius rule
  passes the Mathematical Admission Contract with a named
  source quantity. Score-derived radius as-is does not pass.
- **F4 (privacy picture honesty).** The cap model of sandbox
  privacy stays a picture unless a mechanism consumes it;
  sandbox isolation remains the existing identity-based
  authority meanwhile.
- **F5 (channel honesty).** Any claimed channel must exhibit a
  computed connected complement path at the field's actual ρ
  and model. At ρ = 1 (filled), the prediction is *none* — a
  displayed channel falsifies the display.

**Standing gates respected.** This study overrides nothing:
GDP-001's deferrals (3.4.2–3.4.4) stand until a circuit with
proven consumers reopens them; the Director's Verita PARK and
the Dell Plan gate stand; the frozen HCN R3 baseline is
untouched; no plan file was edited by this study. If Ace
accepts it, the study becomes a *candidate input* to those
gates — evidence with falsifiers attached — not a ruling.

---

# 8. INSTRUMENTS (candidate designs, HCN organ anatomy)

Each: NAME × JOB × HAND-OFF × HEALTH TEST × LEDGER.

1. **THE SHARE LEDGER.** Job: per idea, its exclusive / pair /
   triple / rhombus shared fractions (the cascade, per member).
   Hand-off: Verita-meet and graph consumers read it; it
   decides nothing. Health test: fractions sum against the
   field's analytic mean multiplicity (F1). Ledger: the census
   itself, rebuilt per field state.
2. **THE COVER TEST.** Job: classify the field's negative space
   — COVERED / POCKETED / CHANNELED / OPEN — from ρ and the
   complement's computed connectivity. Hand-off: Space force's
   report; WARD's watchlist. Health test: a classified channel
   must exhibit its path (F5). Ledger: class + the path or the
   covering proof.
3. **THE RHO DIAL.** Job: hold the field's radius/spacing ratio
   as an explicit, receipted parameter; report which regime the
   dial selects. Hand-off: TUNE. Health test: regime prediction
   vs measured complement class. Ledger: dial setting + regime
   receipt per field state.
4. **THE NERVE DIFF.** Job: patterns created / destroyed / moved
   between two field states. Hand-off: growth preview (before)
   and rollback receipt (after). Health test: predicted diff vs
   post-change census (F2). Ledger: the diff, keyed by pattern
   AND address (FL-4: both keys, always).
5. **THE CAP RULE.** Job (picture with a test): a sandbox or a
   docked seat is exclusive *in depth* over a shared projection.
   Hand-off: Dock / Psalm Matrix design. Health test: any
   mechanism claiming the picture must show what the projection
   witnesses and what the cap hides (F4). Ledger: the witness
   list, not the picture.

---

# 9. OPEN QUESTIONS LEFT ON THE TABLE (honest residue)

- **Q-F1.** What is an idea's radius, admitted? (Scope/reach is
  the standing candidate; nothing else in the record qualifies.)
  Until answered, semantic Flower measurement stays closed;
  formal-Flower mathematics stays open.
- **Q-F2.** Irregular fields: real idea fields will not sit on a
  perfect triangular lattice. The cascade's clean ceiling (4)
  and the pattern algebra are lattice theorems; irregular fields
  need the general nerve (with the thick/thin distinction kept)
  and their own censuses. The lattice is the calibration case,
  not the claim.
- **Q-F3.** Finite FCC blocks: interior covering is proven;
  boundary cavity behaviour of finite native-3D clusters was
  not separately probed.
- **Q-F4.** The bounded-face fit 3r(5r+3) was a three-point fit
  (rings 1–3); it has since passed its first out-of-sample test —
  the Euler instrument's ring-4 count is **276 bounded faces**,
  exactly the fit's prediction (3·4·(5·4+3) = 276). Still labeled
  conjecture: four points and a quadratic is evidence, not proof.
- **Q-F5.** The original "Flower of Life analysis" document
  referenced by the 2026-07-25 founding commit was never found
  (UNKNOWN since the 2026-10-03 recovery). If Ace holds it, it
  outranks this study's reconstruction of intent wherever they
  differ.

---

## Appendix — probe inventory (all under `hidden_files/flower_sphere_study/`)

- `probe_flower_sphere.py` → `probe_output.json`: codebase Flower
  census (centers, distance histograms, current vesica-pair
  counts); pair lens area/volume (closed form vs quadrature);
  outline arrangement Euler counts with controls; periodic
  multiplicity fields (2D / lifted / FCC); triple common
  intersection (QMC); finite complement raster (ring 2).
- `probe_membership_patterns.py` → `pattern_output.json`:
  membership-pattern sampling, 2D (801² / 901²) and lifted 3D
  (161³ / 129³), rings 1–2; subset and identity checks between
  models verified in follow-up probes (ring-3 2D census at 1001²
  and 2001²: 137 patterns, stable).
- Ring-4 Euler check (arrangement instrument only): 85 vertices,
  360 edges, 276 bounded faces — the §3.3 fit's out-of-sample
  prediction (see Q-F4).
- Independent checks run alongside: polar-integration triple
  area 0.704771 and slice-integration triple volume 0.671830 vs
  QMC 0.704717 / 0.672165; polar quad area 0.181172 and slice
  quad volume 0.107741 vs QMC 0.181229 / 0.107753; analytic mean
  multiplicities (disk 3.69203, ball 3.02933, lifted field
  2.41840) vs sampled (3.69202, 3.02934, 2.41840).

— END — Sandbox study. Ace's acceptance, placement, or further
development are his moves; nothing here reaches a plan or the
codebase without them.
