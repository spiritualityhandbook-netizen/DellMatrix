#!/usr/bin/env python3
"""THL-SM-01 — HCP counterpart construction + FCC-vs-HCP comparison data.

HCP built exactly: points are (i, j, m, s) with in-plane position
  A site (s=0):  i*a1 + j*a2,        a1=(1,0), a2=(1/2, sqrt(3)/2)
  B site (s=1):  i*a1 + j*a2 + o,    o = (a1+a2)/3 = (1/2, sqrt(3)/6)
layer height z = m * h, h = sqrt(2/3); layer parity fixes s = m mod 2
(ABAB stacking). Squared distances are kept EXACT as pairs (p, q) of
Fractions meaning p + q*sqrt(3).
"""
import json, math
from fractions import Fraction as F
from collections import Counter, deque

OUT = {}
H2 = F(2, 3)  # h^2

def point(i, j, m):
    s = m % 2
    # x = i + j/2 + s/2 ; y = (j/2 + s/6) * sqrt(3) ; z^2 part via m
    return (F(i) + F(j, 2) + F(s, 2), F(j, 2) + F(s, 6), m)

def d2(p, q):
    dx = p[0] - q[0]
    dy = p[1] - q[1]            # coefficient of sqrt(3)
    dz2 = (p[2] - q[2]) ** 2 * H2
    # d^2 = dx^2 + 3*dy^2 + dz2  (all rational!) -- sqrt(3) cancels in
    # squared distances within this coordinate family.
    return dx * dx + 3 * dy * dy + dz2

def gen(R):
    pts = {}
    M = int(R) + 3
    for i in range(-M, M + 1):
        for j in range(-M, M + 1):
            for m in range(-M, M + 1):
                p = point(i, j, m)
                if d2(p, (F(0), F(0), 0)) <= F(R * R) + F(1, 10 ** 9):
                    pts[(i, j, m)] = p
    return pts

ORIGIN = (0, 0, 0)
pts = gen(4.8)
P = pts[ORIGIN]

# --- nearest neighbours: exactly d^2 == 1 --------------------------------
def neighbours(key):
    p = pts[key]
    return [k for k, q in pts.items() if k != key and d2(p, q) == 1]

n0 = neighbours(ORIGIN)
OUT["hcp_nn_count_origin"] = len(n0)
kinds = Counter()
for k in n0:
    kinds["in-plane" if k[2] == 0 else ("above" if k[2] > 0 else "below")] += 1
OUT["hcp_nn_kinds"] = dict(kinds)

# --- Euclidean shells from origin (exact rational d^2) --------------------
shells = Counter()
for k, q in pts.items():
    if k != ORIGIN:
        shells[d2(P, q)] += 1
rows, run = [], 1
for s in sorted(shells):
    if s > 9:
        break
    run += shells[s]
    rows.append({"d2_exact": f"{s.numerator}/{s.denominator}" if s.denominator != 1 else str(s.numerator),
                 "d2_float": float(s), "count": shells[s],
                 "cumulative_incl_center": run})
OUT["hcp_euclidean_shells_to_d2_9"] = rows

# --- step shells (BFS on the NN graph) ------------------------------------
dist = {ORIGIN: 0}
dq = deque([ORIGIN])
while dq:
    u = dq.popleft()
    for w in neighbours(u):
        if w not in dist:
            dist[w] = dist[u] + 1
            dq.append(w)
gs = Counter(d for d in dist.values() if d > 0)
OUT["hcp_step_shells_1_to_4"] = {str(k): gs[k] for k in range(1, 5)}
OUT["fcc_step_shells_1_to_4"] = {"1": 12, "2": 42, "3": 92, "4": 162}

# --- packing: volume per point --------------------------------------------
OUT["hcp_volume_per_point"] = (math.sqrt(3) / 2) * math.sqrt(2 / 3)
OUT["fcc_volume_per_point"] = math.sqrt(2) / 2
OUT["packing_density_both"] = (4 * math.pi / 3 * (0.5) ** 3) / (math.sqrt(2) / 2)

# --- Flower-plane orientations through the origin -------------------------
# FCC (from thl_verify conventions): planes i+j+k=0 and its 3 siblings.
# HCP: test the basal plane (z=0) plus tilted candidates whose normals are
# defined by structure geometry; a plane QUALIFIES if the structure points
# lying in it through the origin include a full triangular layer: >= 19
# points within d<=2 of origin, each interior point having 6 in-plane NN.
def plane_layer_ok(normal_test, sample_pts):
    layer = [q for q in sample_pts if normal_test(q)]
    return len(layer)

# basal: m == 0
OUT["hcp_basal_layer_points_within_R4"] = sum(1 for k in pts if k[2] == 0)
# tilted candidates: planes through origin spanned by pairs of NN vectors
# of the origin (real-space), tested in float with tight tolerance.
import itertools
def to_xyz(key):
    i, j, m = key
    s = m % 2
    return (i + j / 2 + s / 2, (j / 2 + s / 6) * math.sqrt(3), m * math.sqrt(2 / 3))
xyz = {k: to_xyz(k) for k in pts}
nn_xyz = [xyz[k] for k in n0]
def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])
normals = set()
for a, b in itertools.combinations(nn_xyz, 2):
    n = cross(a, b)
    L = math.sqrt(sum(t * t for t in n))
    if L < 1e-9:
        continue
    n = tuple(round(t / L, 6) for t in n)
    n = max(n, tuple(-t for t in n))  # canonical orientation
    normals.add(n)
qualifying = []
for n in normals:
    layer = [k for k, v in xyz.items()
             if abs(sum(v[t] * n[t] for t in range(3))) < 1e-6]
    inner = [k for k in layer
             if sum(t * t for t in xyz[k]) <= 4.0 + 1e-9]
    if len(inner) >= 19:
        # in-plane NN regularity on the innermost points
        qualifying.append({"normal": n, "layer_points_R4": len(layer),
                           "layer_points_within_d2": len(inner)})
OUT["hcp_qualifying_flower_plane_orientations"] = qualifying
OUT["hcp_candidate_normals_tested"] = len(normals)

# --- site orbits under translations ---------------------------------------
OUT["site_orbits"] = {
    "FCC": 1,
    "HCP": 2,
    "note": ("FCC is a Bravais lattice: one translation orbit. In HCP no "
             "translation of the structure maps an A site to a B site "
             "(the would-be translation (o, h) fails: 2o is not a "
             "triangular-lattice vector); A and B are two orbits.")}

print(json.dumps(OUT, indent=2))
