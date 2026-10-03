#!/usr/bin/env python3
"""Executable invariant checks for the DELLMATRIX_EQUATION_LEDGER (GDP-001 R4).

Covers ledger invariants that can be verified without implementation changes:
- EQ-GEO-001/EQ-VER-001 duplicate consistency (documents R4-A1)
- EQ-GEO-003 lens geometry (sqrt(3) verification)
- EQ-GEO-004 overlap classification boundaries
- EQ-GEO-005 flower center counts (1/7/19)
- EQ-GEO-013 contradiction documentation (true behavior of strength)
- EQ-RES-001 _harmonic bounds
- EXT-SMI-001 Smith-chart inverse roundtrip (pure reference math)

Ledger: docs/DELLMATRIX_EQUATION_LEDGER.md
Contract: docs/MATHEMATICAL_ADMISSION_CONTRACT.md
"""
from __future__ import annotations

import math
import random

from form.dell_matrix.sacred_geometry import vesica, flower_centers
from form.dell_matrix.verita import vesica_strength
from form.dell_matrix.ringed_growth import _harmonic


def smoke() -> bool:
    print("=== EQUATION LEDGER INVARIANTS ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    # EQ-GEO-001 == EQ-VER-001 (duplicate consistency, R4-A1)
    rng = random.Random(20261003)
    dup_ok = True
    for _ in range(200):
        r1 = rng.uniform(0.1, 5.0)
        r2 = rng.uniform(0.1, 5.0)
        d = rng.uniform(0.0, r1 + r2 + 1.0)
        sg = vesica(0.0, 0.0, r1, d, 0.0, r2)
        vy = vesica_strength(r1, r2, d)
        if abs(sg["strength"] - vy["strength"]) > 1e-9:
            dup_ok = False
            break
    rec("duplicate strength formulas agree (R4-A1)", dup_ok)

    # EQ-GEO-003: equal unit circles at d=1 -> lens_width = sqrt(3)
    v = vesica(0.0, 0.0, 1.0, 1.0, 0.0, 1.0)
    rec("lens geometry sqrt(3)", abs(v["lens_width"] - math.sqrt(3)) < 1e-3,
        f"got {v['lens_width']}")

    # EQ-GEO-004: classification boundaries
    rec("separate boundary", vesica(0, 0, 1, 3, 0, 1)["type"] == "separate")
    rec("contained boundary", vesica(0, 0, 2, 0.5, 0, 1)["type"] == "contained")
    rec("vesica case", vesica(0, 0, 1, 1, 0, 1)["type"] == "vesica")
    rec("coincident case", vesica(0, 0, 1, 0, 0, 1)["type"] == "coincident")

    # EQ-GEO-005: hexagonal counts
    rec("flower rings=1 -> 7", len(flower_centers(1)) == 7, f"got {len(flower_centers(1))}")
    rec("flower rings=2 -> 19", len(flower_centers(2)) == 19, f"got {len(flower_centers(2))}")

    # EQ-GEO-013: document the TRUE behavior (comment contradicts formula)
    classic = vesica(0, 0, 1, 1, 0, 1)["strength"]       # classic vesica: d == R
    contained = vesica(0, 0, 2, 0.1, 0, 1)["strength"]   # near-containment
    rec("strength peaks at containment not classic vesica (EQ-GEO-013)",
        abs(classic - 0.5) < 1e-9 and contained > classic,
        f"classic={classic} contained~{contained}")

    # EQ-GEO-001 invariants: bounds, symmetry, monotonicity in d
    inv_ok = True
    for _ in range(200):
        r1 = rng.uniform(0.2, 4.0)
        r2 = rng.uniform(0.2, 4.0)
        d = rng.uniform(0.0, r1 + r2)
        s = vesica(0, 0, r1, d, 0, r2)["strength"]
        s_swap = vesica(0, 0, r2, d, 0, r1)["strength"]
        if not (0.0 <= s <= 1.0) or abs(s - s_swap) > 1e-9:
            inv_ok = False
            break
    # monotonic decrease in d on (diff, sum) for fixed radii
    mono_ok = all(
        vesica(0, 0, 1.5, d, 0, 1.0)["strength"] >= vesica(0, 0, 1.5, d + 0.1, 0, 1.0)["strength"]
        for d in [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
    )
    rec("strength bounds+symmetry", inv_ok)
    rec("strength monotone decreasing in d", mono_ok)

    # EQ-RES-001: _harmonic in [0,1], symmetric-ish, zero on empties
    h_ok = True
    toks = [set("abcdefghij"), set("abcxyz"), set(), set("mnop")]
    for a in toks:
        for b in toks:
            h = _harmonic(a, b)
            if not (0.0 <= h <= 1.0):
                h_ok = False
    rec("_harmonic bounds [0,1]", h_ok)
    rec("_harmonic empty-empty is 0", _harmonic(set(), set()) == 0.0)

    # EXT-SMI-001: Gamma inverse roundtrip (pure reference math, complex)
    rt_ok = True
    for zr, zx in [(50.0, 0.0), (25.0, 30.0), (100.0, -40.0), (0.0, 50.0)]:
        z = complex(zr, zx) / 50.0
        gamma = (z - 1) / (z + 1)
        z_back = (1 + gamma) / (1 - gamma)
        if abs(z_back - z) > 1e-9 or abs(gamma) > 1 + 1e-9:
            rt_ok = False
    rec("smith inverse roundtrip z=(1+G)/(1-G)", rt_ok)

    ok = all(r)
    print(f"=== {'ALL PASS' if ok else 'FAILURES PRESENT'} ({sum(r)}/{len(r)}) ===")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if smoke() else 1)
