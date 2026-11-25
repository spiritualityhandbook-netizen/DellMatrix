#!/usr/bin/env python3
"""THL-SM-01 — coordinate-defined, mathematically exact 3D reference
model of the Tree of Harmonic Life candidate (FCC completion), with a
reproducible 2D projection cross-checked against the product's own
sacred_geometry.flower_centers.

DEFINITION (exact). Centers are the points
    C = { (i, j, k)/sqrt(2) : i, j, k in Z, i + j + k even }.
Nearest-neighbour distance is exactly 1. Squared distance between two
centers is (di^2 + dj^2 + dk^2)/2 — an exact rational. All censuses in
this model are integer computations in the scaled coordinates (i, j, k).

PROJECTION. The (111) layer L = {p in C : i + j + k = 0} is projected
onto the plane x + y + z = 0 with the orthonormal basis
    e1 = (1, -1, 0)/sqrt(2),  e2 = (1, 1, -2)/sqrt(6),
giving 2D coordinates (p . e1, p . e2) in real units (NN distance 1).
"""
import json, math, sys
from collections import Counter

SQ2, SQ6 = math.sqrt(2.0), math.sqrt(6.0)

def centers(R):
    M = int(math.ceil(R * SQ2)) + 1
    return [(i, j, k)
            for i in range(-M, M + 1) for j in range(-M, M + 1)
            for k in range(-M, M + 1)
            if (i + j + k) % 2 == 0
            and i * i + j * j + k * k <= 2 * R * R + 1e-9]

def real(p):
    return (p[0] / SQ2, p[1] / SQ2, p[2] / SQ2)

def project(p):
    x, y, z = real(p)
    return (x / SQ2 - y / SQ2,
            x / SQ6 + y / SQ6 - 2 * z / SQ6)

model = {}
allc = centers(3.05)
model["definition"] = ("C = {(i,j,k)/sqrt(2) : i+j+k even}; "
                       "NN distance 1; d^2 = (di^2+dj^2+dk^2)/2")
model["centers_R3_count"] = len(allc)
model["centers_R3"] = sorted(allc)

layer = [p for p in centers(2.6) if sum(p) == 0]
proj = {p: project(p) for p in layer}
inner = {p: xy for p, xy in proj.items()
         if math.hypot(*xy) <= 2.0 + 1e-9}
model["slice_111_points_within_d2"] = len(inner)

# ---- cross-check against the product's sacred_geometry ------------------
sys.path.insert(0, "/home/hatch/workspace/g31-contract02")
from form.dell_matrix.sacred_geometry import flower_centers
fc = flower_centers(rings=2)  # 19 centers, NN distance 1, 2D
mine = sorted(inner.values())
def dist_multiset(pts):
    c = Counter()
    for a in range(len(pts)):
        for b in range(a + 1, len(pts)):
            d = math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
            c[round(d, 6)] += 1
    return dict(sorted(c.items()))
model["crosscheck_product_flower_count"] = len(fc)
model["crosscheck_distance_multisets_equal"] = (
    dist_multiset(fc) == dist_multiset(mine))
# explicit symmetry fit: try the 12 hexagonal symmetries
def symmetries(pt):
    x, y = pt
    out = []
    for k in range(6):
        t = k * math.pi / 3
        xr = x * math.cos(t) - y * math.sin(t)
        yr = x * math.sin(t) + y * math.cos(t)
        out.append((xr, yr))
        out.append((xr, -yr))
    return out
fit = None
for si in range(12):
    cand = sorted(symmetries(mine[0])[si] for _ in [0])
    mapped = []
    for pt in mine:
        mapped.append(symmetries(pt)[si])
    ok = all(any(math.hypot(m[0] - f[0], m[1] - f[1]) < 1e-9 for f in fc)
             for m in mapped)
    if ok:
        fit = si
        break
model["crosscheck_explicit_symmetry_fit_found"] = fit is not None
model["crosscheck_symmetry_index"] = fit

# ---- reproducible SVG of the (111) projection (37 centers, d <= 2.6) ----
W = 520
scale = 78
def sx(x):
    return W / 2 + x * scale
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{W}">',
       '<rect width="100%" height="100%" fill="white"/>']
for p, (x, y) in sorted(proj.items(), key=lambda kv: math.hypot(*kv[1])):
    d = math.hypot(x, y)
    if d <= 2.6 + 1e-9:
        svg.append(f'<circle cx="{sx(x):.2f}" cy="{sx(-y):.2f}" r="{scale:.2f}" '
                   f'fill="none" stroke="#888" stroke-width="0.7"/>')
for p, (x, y) in proj.items():
    if math.hypot(x, y) <= 2.6 + 1e-9:
        svg.append(f'<circle cx="{sx(x):.2f}" cy="{sx(-y):.2f}" r="2.6" fill="#111"/>')
svg.append('<text x="10" y="20" font-family="monospace" font-size="12">'
           'THL reference model — (111) projection of the FCC Tree '
           '(37 centres, d &lt;= 2.6; unit circles on the 19 Flower centres)'
           '</text>')
svg.append('</svg>')
open("/home/hatch/workspace/goals/dellmatrix-capability-circuits/"
     "hidden_files/thl_sm_01/thl_projection_111.svg", "w").write("\n".join(svg))
model["projection_svg"] = "thl_projection_111.svg (37 centers, unit circles on inner 19)"
print(json.dumps(model, indent=2))
