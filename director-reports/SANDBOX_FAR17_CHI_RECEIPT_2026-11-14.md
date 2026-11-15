# FAR-17 RECEIPT — THE NERVE'S EULER CHARACTERISTIC, COMPUTED
## Authorized: Sandbox Director SD-GP-01 item 4 / Q-S5 (sandbox
## computation ONLY, read-only). Executed: Uni, 2026-11-14.
## Probes + raw output: hidden_files/sd_gp_01/ (probe_far17_chi.py,
## probe_far17_sizes.py, far17_output.json).

## DEFINITIONS (published per audit F3, before results)
- Field: triangular-lattice centres c(i,j) = (i + j/2, j·√3/2);
  patch P(R) = centres at hex distance ≤ R. R=1 → 7 centres,
  R=2 → 19, R=3 → 37 (the Flower studies' rings 0..3).
- Cells: unit disks (ρ = 1, the Flower's own dial), closed.
- A subset S of centres is a simplex of the nerve iff the
  intersection of its disks is nonempty. χ = Σ (−1)^k · n_k
  over ALL feasible subsets (n_k = feasible (k+1)-subsets).
- TWO CONVENTIONS, reported separately:
  CLOSED — a single-point intersection counts (MEC radius ≤ 1).
  PATTERN — Part I's positive-measure sharing (MEC radius
  strictly < 1); boundary subsets (MEC = 1 exactly) are
  counted and reported, never silently assigned.
- Feasibility test: S feasible iff the minimum enclosing
  circle (MEC) of its centres has radius ≤ 1 (the 1-centre
  criterion). Cross-check: a second method (candidate points:
  centres, pair lens corners, triple circumcentres of S)
  must agree on EVERY subset. QUALIFICATION (Director
  return, 2026-11-14): the two methods share the same
  lattice, feasibility definition, and enumeration
  framework — they cross-check the computation, they are
  not fully independent validation of the definitions.

## INSTRUMENT HISTORY (kept on the receipt, per standing law)
- v1 (global candidate set) did not finish (killed; no result
  claimed from it).
- v2 method A initially MISSED tangent pairs (distance exactly
  2: the lens-corner construction excluded d = 2, whose unique
  feasible point is the midpoint). Detected because method
  disagreements equalled the tangent-pair counts exactly
  (3 / 27 / 69 at R = 1 / 2 / 3). Fixed (d ≤ 2, midpoint
  included); after the fix the two methods agree on every
  subset at every patch (0 disagreements).

## COUNTS (method B; method A in full agreement after the fix)
PATTERN convention:
  R=1: n = (7, 18, 18, 6)      χ = 7 − 18 + 18 − 6 = 1
  R=2: n = (19, 72, 84, 30)    χ = 19 − 72 + 84 − 30 = 1
  R=3: n = (37, 162, 198, 72)  χ = 37 − 162 + 198 − 72 = 1
Completeness: feasible 5-fold PATTERN subsets = 0 of 11,628
(R=2) and 0 of 435,897 (R=3); feasibility is downward-closed,
so no higher-order pattern simplex exists; R=1's 5-subsets
are among R=2's. The pattern count is COMPLETE, not truncated.
Boundary subsets (MEC = 1 exactly), excluded above, reported:
pairs 3/27/69, triples 17/137/359, quadruples 29/221/587.

CLOSED convention: truncated sums over sizes ≤ 4 (−14, −110,
−296) are NOT χ and are not reported as such: the closed
nerve has simplices of every order up to patch size (at R=1
every subset shares the centre point: sizes 5/6/7 feasible
21/7/1 — the full 6-simplex — giving χ = 7 − 21 + 35 − 35 +
21 − 7 + 1 = 1). Terminology, corrected per the Director's
source review (C-2, 2026-11-14): for every finite patch the
closed nerve IS finite-dimensional (dimension at most patch
size − 1); it simply cannot be evaluated correctly by
truncating the alternating sum at simplex size four, because
its higher-order simplices genuinely contribute. The PATTERN
convention is the operative one — its simplices provably
stop at size four — and it is also the convention Part I
used.

## VERDICT
**χ = 1** for the Flower's thick nerve at R = 1, 2, 3
(pattern convention; complete counts; two cross-checking
methods). THEOREM SCOPE, stated exactly (Director return,
2026-11-14): the ordinary nerve theorem certifies the
CLOSED convention (nonempty intersections of closed convex
sets; the union of a full patch is contractible, and the
R=1 full-simplex count confirms χ = 1 there directly). The
PATTERN convention EXCLUDES point-only intersections, so
the theorem does NOT automatically establish its Euler
characteristic: for the pattern nerve, χ = 1 is an OBSERVED
BASELINE for the tested ideal patches — its agreement with
the closed value is corroborating evidence, not a
theorem-based proof. Label: 1 is the observed baseline,
NOT an established universal "healthy value" — other
configurations can legitimately have different Euler
characteristics, and departure-detection as a gauge is a
proposed use, not a certified one. HD-6's naive formula
(singles − NN edges + triangles − rhombi) is RETIRED: it
omits √3 pairs and non-unit triples and miscounts rhombi;
it does not compute this χ.

## UNTESTED DOMAINS (explicit, per the Director's return)
This result covers ONLY: ideal triangular-lattice patches,
ρ = 1, R ∈ {1, 2, 3}, the stated conventions. NOT computed:
irregular fields (open question Q-F2); any ρ ≠ 1; patches
R ≥ 4; the lifted (one-layer 3D) and native FCC fields of
the Flower studies; mixed-shape (polygon-ladder) fields;
fields with holes or exclusions by construction. The
gauge's behaviour in every one of those domains is UNKNOWN.

STATUS: a completed read-only sandbox computation with this
receipt. No implementation, no register promotion, no plan
change follows from it (SD-GP-01 stop conditions).
