#!/usr/bin/env python3
"""
Eigenvalue stability analysis for DellMatrix.

Continuous linearization:  dx/dt = A x
  All Re(λ) < 0  → asymptotically stable (sink)
  Any  Re(λ) > 0 → unstable (source / saddle)
  Pure imag     → center (marginal)

Discrete map / Poincaré:  x_{n+1} = A x_n
  All |λ| < 1   → asymptotically stable
  Any  |λ| > 1  → unstable

Logistic map fixed-point multiplier |f'(x*)| < 1 → attracting.

Offline · educational dynamics · Boolean host intact.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import math
import cmath

from form.dell_matrix.linear_algebra import Mat2
from form.dell_matrix.nature_code import Vec2


def _re(lam) -> float:
    return float(lam.real) if isinstance(lam, complex) else float(lam)


def _im(lam) -> float:
    return float(lam.imag) if isinstance(lam, complex) else 0.0


def _mod(lam) -> float:
    if isinstance(lam, complex):
        return abs(lam)
    return abs(float(lam))


def classify_continuous(eigenvalues: Tuple) -> Dict[str, Any]:
    """Stability of continuous system dx/dt = A x from spectrum of A."""
    reals = [_re(e) for e in eigenvalues]
    imags = [_im(e) for e in eigenvalues]
    max_re = max(reals) if reals else 0.0
    min_re = min(reals) if reals else 0.0
    has_pos = any(r > 1e-9 for r in reals)
    has_neg = any(r < -1e-9 for r in reals)
    all_neg = all(r < -1e-9 for r in reals)
    all_zero_re = all(abs(r) <= 1e-9 for r in reals)
    has_imag = any(abs(i) > 1e-9 for i in imags)

    if all_neg:
        kind = "asymptotically_stable"  # sink / spiral sink
        if has_imag:
            kind = "spiral_sink"
        else:
            kind = "nodal_sink"
    elif has_pos and has_neg:
        kind = "saddle"  # unstable
    elif has_pos and not has_neg:
        kind = "source" if not has_imag else "spiral_source"
    elif all_zero_re and has_imag:
        kind = "center"  # marginal / Lyapunov stable but not asymptotic
    elif all_zero_re:
        kind = "degenerate"  # zero eigenvalues — higher-order needed
    else:
        kind = "marginal_or_mixed"

    stable = kind in ("asymptotically_stable", "spiral_sink", "nodal_sink")
    return {
        "mode": "continuous",
        "kind": kind,
        "stable": stable,
        "asymptotic": stable,
        "max_re": max_re,
        "min_re": min_re,
        "eigenvalues": [
            {"re": _re(e), "im": _im(e), "mod": _mod(e)} for e in eigenvalues
        ],
    }


def classify_discrete(eigenvalues: Tuple) -> Dict[str, Any]:
    """Stability of discrete map x → A x from spectrum of A."""
    mods = [_mod(e) for e in eigenvalues]
    max_mod = max(mods) if mods else 0.0
    all_inside = all(m < 1.0 - 1e-9 for m in mods)
    any_outside = any(m > 1.0 + 1e-9 for m in mods)
    on_circle = any(abs(m - 1.0) <= 1e-9 for m in mods)

    if all_inside:
        kind = "asymptotically_stable"
    elif any_outside:
        kind = "unstable"
    elif on_circle and not any_outside:
        kind = "marginal"  # |λ|=1 — needs nonlinear terms
    else:
        kind = "marginal_or_mixed"

    return {
        "mode": "discrete",
        "kind": kind,
        "stable": all_inside,
        "asymptotic": all_inside,
        "max_mod": max_mod,
        "eigenvalues": [
            {"re": _re(e), "im": _im(e), "mod": _mod(e)} for e in eigenvalues
        ],
    }


def stability_of_mat2(m: Mat2, mode: str = "continuous") -> Dict[str, Any]:
    """Full stability report for a Mat2 linearization."""
    evs = m.eigenvalues()
    tr = m.trace()
    det = m.det()
    base = {
        "trace": tr,
        "det": det,
        "disc": tr * tr - 4 * det,
        "mat": m.to_dict(),
    }
    if mode == "discrete":
        report = classify_discrete(evs)
    else:
        report = classify_continuous(evs)
    report.update(base)
    # 2×2 continuous trace-det quick view (Strogatz plane)
    if mode != "discrete":
        if det < 0:
            report["phase_plane"] = "saddle"
        elif det > 0 and tr < 0 and tr * tr > 4 * det:
            report["phase_plane"] = "nodal_sink"
        elif det > 0 and tr < 0 and tr * tr < 4 * det:
            report["phase_plane"] = "spiral_sink"
        elif det > 0 and tr > 0 and tr * tr > 4 * det:
            report["phase_plane"] = "nodal_source"
        elif det > 0 and tr > 0 and tr * tr < 4 * det:
            report["phase_plane"] = "spiral_source"
        elif det > 0 and abs(tr) < 1e-12:
            report["phase_plane"] = "center"
        else:
            report["phase_plane"] = "boundary_or_degenerate"
    return report


def logistic_fixed_points(r: float) -> List[Dict[str, Any]]:
    """
    Logistic map f(x) = r x (1-x).
    Fixed points: x=0 and x=1-1/r (r≠0).
    Multiplier μ = f'(x*) = r(1-2x*).
    Attracting iff |μ| < 1.
    """
    pts = []
    # x* = 0
    mu0 = r * (1 - 0)  # r
    pts.append({
        "x": 0.0,
        "multiplier": mu0,
        "abs_multiplier": abs(mu0),
        "stable": abs(mu0) < 1.0,
        "note": "extinction fixed point",
    })
    if abs(r) > 1e-12:
        x1 = 1.0 - 1.0 / r
        mu1 = r * (1 - 2 * x1)  # = 2 - r
        pts.append({
            "x": x1,
            "multiplier": mu1,
            "abs_multiplier": abs(mu1),
            "stable": abs(mu1) < 1.0,
            "note": "carrying-capacity fixed point",
        })
    return pts


def logistic_stability(r: float) -> Dict[str, Any]:
    """Regime + fixed-point stability for given r."""
    from form.dell_matrix.logistic_map import classify_regime
    fps = logistic_fixed_points(r)
    return {
        "r": r,
        "regime": classify_regime(r),
        "fixed_points": fps,
        "attracting": [p for p in fps if p["stable"]],
        "source": "logistic map multiplier analysis",
    }


def analyze_transform_stability(kind: str = "rotate", amount: float = 0.1) -> Dict[str, Any]:
    """Convenience: build Mat2 from named transform and classify."""
    if kind == "rotate":
        m = Mat2.rotate(float(amount))
    elif kind == "scale":
        m = Mat2.scale(float(amount))
    elif kind == "shear":
        m = Mat2.shear_x(float(amount))
    else:
        m = Mat2.identity()
    cont = stability_of_mat2(m, mode="continuous")
    disc = stability_of_mat2(m, mode="discrete")
    return {"transform": kind, "amount": amount, "continuous": cont, "discrete": disc}


def smoke() -> bool:
    print("=== EIGEN_STABILITY SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    # sink: scale by 0.5 → eigenvalues 0.5, 0.5
    s = Mat2.scale(0.5)
    c = stability_of_mat2(s, "continuous")
    rec("scale_0.5 continuous stable", c["stable"] is True)
    d = stability_of_mat2(s, "discrete")
    rec("scale_0.5 discrete stable", d["stable"] is True)

    # source: scale by 2
    s2 = Mat2.scale(2.0)
    c2 = stability_of_mat2(s2, "continuous")
    rec("scale_2 continuous unstable", c2["stable"] is False)

    # pure rotation → center (continuous) / discrete on unit circle
    rot = Mat2.rotate(math.pi / 3)
    cr = stability_of_mat2(rot, "continuous")
    rec("rotate continuous center/marginal", cr["kind"] in ("center", "marginal_or_mixed"))
    dr = stability_of_mat2(rot, "discrete")
    rec("rotate discrete marginal", dr["kind"] in ("marginal", "asymptotically_stable") or abs(dr["max_mod"] - 1) < 1e-6)

    # logistic: r=2.5 → |2-r|=0.5 < 1 → stable carrying capacity
    ls = logistic_stability(2.5)
    attracting = ls["attracting"]
    rec("logistic r=2.5 has attracting fp", len(attracting) >= 1)

    # logistic: r=3.5 → |2-3.5|=1.5 > 1 → unstable fixed point (period-doubling)
    ls2 = logistic_stability(3.5)
    rec("logistic r=3.5 fixed pts unstable", all(not p["stable"] for p in ls2["fixed_points"] if p["x"] != 0))

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
