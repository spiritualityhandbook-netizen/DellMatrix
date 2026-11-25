# APPENDIX — FCC vs HCP: THE ROAD NOT TAKEN, PRESERVED

**Status:** PERMANENT ADMISSION APPENDIX, created under Director ruling
Q-THL2 (THL-SM-01, 2026-11-14): *"YES. Preserve FCC-versus-HCP
permanently as an appendix, including HCP's valid properties and
reasons for nonselection."*
**Purpose:** if FCC is ever admitted as the canonical geometric
reference model for the Tree of Harmonic Life, this appendix is the
auditable record of the alternative that was considered, what it
genuinely offers, and exactly why it was not selected. If FCC is not
admitted, this appendix stands as the comparison record either way.
**Evidence:** THL-SM-01 return (`SANDBOX_THL_SM_01_FCC_VERIFICATION_2026-11-14.md`);
probes `hidden_files/thl_sm_01/thl_hcp.py`, `thl_verify.py` (outputs
alongside). Repository pin: main `715bfc21`.

## The two candidates

Both are Barlow stackings of triangular layers — the two regular ways
to stack close-packed layers so every sphere touches twelve others.

- **FCC** (ABCABC stacking): centres
  C = { (i, j, k)/√2 : i, j, k ∈ Z, i + j + k even } — a Bravais
  lattice; equivalently the corners and face-centres of a cubic cell
  of edge √2. Nearest-neighbour distance 1.
- **HCP** (ABAB stacking): triangular layers at height m·√(2/3),
  alternate layers offset by (a1 + a2)/3 with a1 = (1, 0),
  a2 = (1/2, √3/2). A lattice plus a two-point basis; not itself a
  Bravais lattice.

## HCP's valid properties — stated fairly, in full

HCP is not a failed construction. It is one of the two optimal
sphere packings in three dimensions, and the record must say so:

1. **Optimal density.** HCP packs at π/(3√2) ≈ 0.7405, identical to
   FCC (volume per centre √2/2, verified exactly in THL-SM-01). On
   packing efficiency the two are exactly tied — both attain the
   Kepler bound.
2. **Full coordination.** Every HCP centre has exactly 12 nearest
   neighbours at distance 1 (6 in-plane, 3 above, 3 below) — the same
   kissing number as FCC.
3. **A true Flower layer.** HCP's basal plane is a genuine triangular
   layer: through every centre there is one orientation in which the
   Flower of Life sits exactly (19 centres within distance 2, verified).
4. **Deterministic construction.** HCP is fully deterministic and was
   constructed exactly in THL-SM-01: squared distances in the adapted
   coordinates are exact rationals (the √3 terms cancel in squared
   distances), so its censuses are exact arithmetic, not sampling.
5. **Physical reality.** HCP is realized in nature (e.g., magnesium,
   cobalt, ice under pressure regimes) — it is not a mathematical
   curiosity.

Any future reader who asks "was HCP dismissed because it is worse
mathematics?" gets the answer from this section: **no.**

## Measured differences (THL-SM-01, exact)

| Measurement | FCC | HCP |
|---|---|---|
| Packing density / volume per centre | 0.7405 / √2/2 | 0.7405 / √2/2 (tie) |
| Coordination | 12 | 12 (tie) |
| Step shells 1–4 (neighbour-graph distance) | 12 / 42 / 92 / 162 = 10k² + 2 | 12 / 44 / 96 / 170 |
| Euclidean shell census | Isotropic; counts independent of direction | Anisotropic; an extra shell appears at d² = 8/3 (the two same-column centres two layers away) with no FCC counterpart |
| Flower-plane orientations through a centre | **4** (the {111} family) | **1** (basal only; 22 candidate normals tested) |
| Site orbits under translations | 1 (Bravais) | 2 (A/B sites; no structure translation maps A to B — the candidate translation (offset, height) fails because twice the offset is not a triangular-lattice vector) |
| Indexing | Integer triple (i, j, k) + parity — pure integer arithmetic for every census | (i, j, layer) + basis flag; layer height √(2/3) is irrational in any cubic frame |

## Reasons for nonselection (in the order the Director's criteria give)

1. **2D Flower compatibility (decisive).** The Tree exists as the
   completion of the Flower. In FCC the Flower layer occurs in four
   orientations through every centre — the 2D pattern is woven
   through the 3D structure in every {111} direction. In HCP it
   occurs in exactly one orientation: the stacking axis is privileged
   and the Flower is a floor, not a weave. A Tree whose Flower only
   faces one way contradicts the originating construction (spheres
   grown from the Flower in all directions).
2. **DellMatrix's stated requirements (decisive).** The Tree was
   defined as the completion of the Harmonic Cube's centre set. FCC
   *is* that completion — the cube's corners plus its face centres —
   and THE CHORD's 177-centre set is an FCC set. HCP has no
   relationship to the cube at all; adopting it would orphan the
   cube, the chord, and the lattice's (h, v, f) integer indexing in
   one move.
3. **Deterministic indexing.** FCC centres are integer triples under
   a parity rule — the same indexing form `HarmonicLattice` already
   uses — and every census in the verification is exact integer
   arithmetic. HCP requires a basis flag and an irrational layer
   height in any cubic frame.
4. **Symmetry fit.** FCC's shells are isotropic and its sites form a
   single orbit; HCP's census depends on the stacking axis and its
   sites split into two orbits. DellMatrix's surrounding structures
   (cube, lattice, chord) are cubic-symmetric; FCC's symmetry is the
   compatible one.
5. **The step-shell law.** The Tree study's signature count,
   10k² + 2, is a property of the FCC neighbour graph. HCP's graph
   diverges from shell 2 (44 ≠ 42): the two graphs are not
   isomorphic, so results proven on one do not transfer to the other.

**Not** reasons: density (tied), coordination (tied), validity (both
valid), naturalness (both realized in nature).

## What would have to change for HCP to be reconsidered

- A DellMatrix requirement that privileges a single axis (making the
  basal Flower orientation a feature rather than a limitation); or
- abandonment of the cube-completion definition of the Tree; or
- a demonstrated defect in the FCC evidence itself.
Absent one of those, the nonselection stands on the criteria above —
and this appendix is where a future challenger starts.

## Custody

Preserved with the THL-SM-01 evidence package (PR #419) and the goal
workspace (`hidden_files/thl_sm_01/`). To be attached to any future
admission record for the Tree of Harmonic Life geometry, per Q-THL2.

*End of appendix.*
