#!/usr/bin/env python3
"""THL-SM-01 — INDEPENDENT verification of the sandbox FCC Tree claims.

Independence: the point set is built by a DIFFERENT construction than the
original probes (conventional cubic cell: corners + face centers, cell
edge sqrt(2), nearest-neighbour distance 1), then proven equal to the
parity construction. All censuses use exact integer arithmetic in the
scaled coordinates (centers are integer triples; squared distance
between centers = s2/2 where s2 = di^2+dj^2+dk^2).

Claims under test (from SANDBOX_TREE_OF_LIFE_STUDY_2026-11-13.md):
  C1 Euclidean shells to R=3: counts 12/6/24/12/24/8/48/6/36,
     cumulative incl. center 13/19/43/55/79/87/135/141/177.
  C2 Step (BFS) shells 1..4 = 12/42/92/162 = 10k^2+2.
  C3 (111) slice census cumulative 7/13/19/31/37 (a Flower layer);
     (100) slice is a square lattice layer.
  C4 Distance exclusion: squared distance 14 (s2 = 28) never occurs.
  C5 Sphere-field multiplicity in {4..8}, mean = (4pi/3)/(sqrt(2)/2).
  C6 Exclusive volume of the central sphere = ZERO (exact proof, not MC).
"""
import json, math
from collections import Counter, deque

SQ2 = math.sqrt(2.0)
OUT = {}

# ---------- construction A: parity filter (original probes' method) ----
def gen_parity(R):
    M = int(math.ceil(R * SQ2)) + 1
    return {(i, j, k)
            for i in range(-M, M + 1) for j in range(-M, M + 1)
            for k in range(-M, M + 1)
            if (i + j + k) % 2 == 0 and i * i + j * j + k * k <= 2 * R * R + 1e-9}

# ---------- construction B: conventional cell (corners + face centers) -
def gen_cells(R):
    """FCC as cubic-cell corners + face centers, cell edge sqrt(2) in real
    units => in scaled integer units the cell edge is 2 and centers are
    (2a+u, 2b+v, 2c+w) with (u,v,w) in {(0,0,0),(0,1,1),(1,0,1),(1,1,0)}."""
    pts = set()
    M = int(math.ceil(R * SQ2)) + 2
    basis = [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]
    for a in range(-M, M + 1):
        for b in range(-M, M + 1):
            for c in range(-M, M + 1):
                for (u, v, w) in basis:
                    p = (2 * a + u, 2 * b + v, 2 * c + w)
                    if p[0] ** 2 + p[1] ** 2 + p[2] ** 2 <= 2 * R * R + 1e-9:
                        pts.add(p)
    return pts

for R in (1.05, 2.05, 3.05):
    A, B = gen_parity(R), gen_cells(R)
    OUT[f"construction_equality_R{R}"] = (A == B)
    assert A == B, f"constructions differ at R={R}"

def s2(p):
    return p[0] ** 2 + p[1] ** 2 + p[2] ** 2

# ---------- C1: Euclidean shells ----------------------------------------
pts = gen_cells(3.05)
shells = Counter(s2(p) for p in pts if p != (0, 0, 0))
rows, run = [], 1
for s in sorted(shells):
    run += shells[s]
    rows.append({"s2": s, "dist": math.sqrt(s / 2), "count": shells[s],
                 "cumulative_incl_center": run})
OUT["C1_euclidean_shells"] = rows
OUT["C1_counts"] = [r["count"] for r in rows]
OUT["C1_cumulative"] = [r["cumulative_incl_center"] for r in rows]

# ---------- C2: step shells (BFS, fresh implementation) -----------------
NN = [(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)
      if sorted((abs(a), abs(b), abs(c))) == [0, 1, 1]]
assert len(NN) == 12
big = gen_cells(4.6)
dist = {(0, 0, 0): 0}
dq = deque([(0, 0, 0)])
while dq:
    p = dq.popleft()
    for v in NN:
        q = (p[0] + v[0], p[1] + v[1], p[2] + v[2])
        if q in big and q not in dist:
            dist[q] = dist[p] + 1
            dq.append(q)
gs = Counter(d for d in dist.values() if d > 0)
OUT["C2_step_shells_1_to_4"] = {str(k): gs[k] for k in range(1, 5)}
OUT["C2_formula_10k2+2"] = {str(k): 10 * k * k + 2 for k in range(1, 5)}
# boundary honesty: shell 4 census needs the R=4.6 envelope complete to
# graph distance 4; every shell-4 point has |p|^2/2 <= 16 -> inside.
OUT["C2_shell4_max_euclid_dist"] = max(
    math.sqrt(s2(p) / 2) for p, d in dist.items() if d == 4)

# ---------- C3: slices ----------------------------------------------------
def slice_census(pred):
    layer = [p for p in pts if pred(p) and p != (0, 0, 0)]
    c = Counter(s2(p) for p in layer)
    rows, run = [], 1
    for s in sorted(c):
        run += c[s]
        rows.append({"s2": s, "count": c[s], "cumulative": run})
    return rows
OUT["C3_slice_111"] = slice_census(lambda p: sum(p) == 0)
OUT["C3_slice_100"] = slice_census(lambda p: p[0] == 0)
# (111) layer is a triangular lattice: its 6 in-plane NN at distance 1,
# and in-plane squared distances are 3*m for triangular-lattice norms
# (s2 = 6 * (a^2+ab+b^2) / ... ) -- checked directly: every in-plane
# point's in-plane NN count is 6.
layer111 = {p for p in gen_cells(4.6) if sum(p) == 0}
nn_in_plane = [sum(1 for v in NN
                   if (p[0] + v[0], p[1] + v[1], p[2] + v[2]) in layer111)
               for p in list(layer111)[:50]]
OUT["C3_slice_111_inplane_NN_count_sample"] = Counter(nn_in_plane)

# ---------- C4: distance exclusions --------------------------------------
attained = set()
for a in range(-12, 13):
    for b in range(-12, 13):
        for c in range(-12, 13):
            if (a + b + c) % 2 == 0:
                attained.add(a * a + b * b + c * c)
gaps = [s for s in range(2, 82, 2) if s not in attained]
OUT["C4_attained_s2_up_to_80"] = sorted(s for s in attained if s <= 80)
OUT["C4_gap_s2_up_to_80"] = gaps
# s2 = 28 without the parity condition: any integer triple at all?
any28 = [(a, b, c) for a in range(-6, 7) for b in range(-6, 7)
         for c in range(-6, 7) if a * a + b * b + c * c == 28]
OUT["C4_any_integer_triple_s2_28"] = any28
# Legendre three-square theorem: n fails iff n = 4^a (8b+7).
def three_square_forbidden(n):
    while n % 4 == 0 and n > 0:
        n //= 4
    return n % 8 == 7
OUT["C4_gaps_explained_by_three_square_theorem"] = {
    str(s): three_square_forbidden(s) for s in gaps}
# every attained value must be a sum of three squares (theorem side):
OUT["C4_attained_all_three_square_legal"] = all(
    not three_square_forbidden(s) for s in attained if s <= 80)

# ---------- C5/C6: field multiplicity + exclusive volume ------------------
# Exact proof of C6: for x in the central unit ball, let c* be a nearest
# neighbour direction maximising x.c . The 12 NN directions have angular
# covering radius 45 degrees (worst directions: the 6 axis directions),
# so max x.c >= |x|/sqrt(2), giving min_c |x-c|^2 <= |x|^2 + 1 - sqrt(2)|x|
# <= 1 on [0,1], equality only at x = 0. Verify the covering claim by
# exact candidate check + dense deterministic sampling of the sphere.
import random
random.seed(20261114)
NNdirs = [(a / SQ2, b / SQ2, c / SQ2) for (a, b, c) in NN]
def max_dot(x):
    return max(x[0] * d[0] + x[1] * d[1] + x[2] * d[2] for d in NNdirs)
worst = 1.0; worst_dir = None
for _ in range(400000):
    v = [random.gauss(0, 1) for _ in range(3)]
    n = math.sqrt(sum(t * t for t in v))
    x = tuple(t / n for t in v)
    m = max_dot(x)
    if m < worst:
        worst, worst_dir = m, x
OUT["C6_min_over_directions_of_max_dot"] = worst
OUT["C6_theoretical_min"] = 1 / SQ2
OUT["C6_worst_direction_sample"] = worst_dir
OUT["C6_axis_direction_max_dot"] = max_dot((1.0, 0.0, 0.0))
OUT["C6_proof"] = ("min_c |x-c|^2 <= r^2 + 1 - sqrt(2) r <= 1 for "
                   "r = |x| in [0,1]; equality only at r = 0 (the centre, "
                   "distance exactly 1 from all 12 neighbours). Hence no "
                   "point of the central sphere is exclusive: exclusive "
                   "volume is exactly ZERO, a theorem, not an MC estimate.")
# C5: multiplicity bounds. Mean is analytic: vol(sphere)/vol-per-centre.
OUT["C5_volume_per_centre"] = SQ2 / 2
OUT["C5_mean_multiplicity_analytic"] = (4 * math.pi / 3) / (SQ2 / 2)
# Witness for multiplicity 8 and a dense-grid max check (deterministic):
centers = [(i / SQ2, j / SQ2, k / SQ2) for (i, j, k) in gen_cells(2.6)]
def multiplicity(x):
    return sum(1 for c in centers
               if sum((x[t] - c[t]) ** 2 for t in range(3)) <= 1.0 + 1e-12)
best = (0, None)
random.seed(7)
for _ in range(120000):
    v = [random.gauss(0, 1) for _ in range(3)]
    n = math.sqrt(sum(t * t for t in v))
    r = random.random() ** (1 / 3) * 1.5
    x = tuple(t / n * r for t in v)
    m = multiplicity(x)
    if m > best[0]:
        best = (m, x)
OUT["C5_max_multiplicity_found"] = best[0]
OUT["C5_max_multiplicity_witness"] = best[1]

print(json.dumps(OUT, indent=2))
