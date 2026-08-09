#!/usr/bin/env python3
"""
Incorporation Audit — test universal properties across DellMatrix cores
implemented in the recent educational wave (Nature, LA, eigen stability,
logistic, Fourier).

Run:
  python -m form.dell_matrix.incorporation_audit
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple
import math


def _rec(results: List[Tuple[str, bool]], name: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}")
    results.append((name, ok))


def audit_linear_algebra(results: List[Tuple[str, bool]]) -> None:
    print("\n-- linear_algebra --")
    from form.dell_matrix.linear_algebra import Mat2
    from form.dell_matrix.nature_code import Vec2

    # identity leaves vectors unchanged
    v = Vec2(3, 4)
    w = Mat2.identity().apply(v)
    _rec(results, "identity_preserves", abs(w.x - 3) < 1e-12 and abs(w.y - 4) < 1e-12)

    # rotation by π/2: (1,0) → (0,1)
    r = Mat2.rotate(math.pi / 2).apply(Vec2(1, 0))
    _rec(results, "rotate_pi2", abs(r.x) < 1e-9 and abs(r.y - 1) < 1e-9)

    # det of rotation = 1 (area preserving)
    _rec(results, "det_rotation_1", abs(Mat2.rotate(0.7).det() - 1) < 1e-9)

    # compose scale then rotate has det = scale product
    m = Mat2.rotate(0.3).compose(Mat2.scale(2, 3))
    _rec(results, "compose_det", abs(m.det() - 6) < 1e-6)

    # inverse of scale
    inv = Mat2.scale(2, 4).inverse()
    _rec(results, "inverse_exists", inv is not None and abs(inv.det() - 0.125) < 1e-9)


def audit_eigen_stability(results: List[Tuple[str, bool]]) -> None:
    print("\n-- eigen_stability --")
    from form.dell_matrix.linear_algebra import Mat2
    from form.dell_matrix.eigen_stability import stability_of_mat2, logistic_stability

    # contracting scale is stable in both senses
    c = stability_of_mat2(Mat2.scale(0.5), "continuous")
    d = stability_of_mat2(Mat2.scale(0.5), "discrete")
    _rec(results, "scale_0.5_stable", c["stable"] and d["stable"])

    # expanding scale unstable
    c2 = stability_of_mat2(Mat2.scale(2.0), "continuous")
    _rec(results, "scale_2_unstable", not c2["stable"])

    # pure rotation → center / marginal
    cr = stability_of_mat2(Mat2.rotate(1.0), "continuous")
    _rec(results, "rotation_center_or_marginal", cr["kind"] in ("center", "marginal_or_mixed", "spiral_sink"))

    # logistic r=2.5 has attracting fixed point
    ls = logistic_stability(2.5)
    _rec(results, "logistic_2.5_attracting", len(ls["attracting"]) >= 1)

    # logistic r=3.5 fixed points lose stability
    ls2 = logistic_stability(3.5)
    unstable_carry = all(not p["stable"] for p in ls2["fixed_points"] if abs(p["x"]) > 1e-9)
    _rec(results, "logistic_3.5_unstable_fp", unstable_carry)


def audit_logistic(results: List[Tuple[str, bool]]) -> None:
    print("\n-- logistic_map --")
    from form.dell_matrix.logistic_map import iterate, classify_regime, LogisticDriver

    xs = iterate(0.5, 2.0, 30)
    _rec(results, "iterate_bounded", all(0 <= x <= 1 for x in xs))

    _rec(results, "regime_stable", classify_regime(2.5) == "stable_fixed")
    _rec(results, "regime_chaos", classify_regime(3.9) == "chaos")

    d = LogisticDriver(r=3.2, x=0.4)
    for _ in range(20):
        d.step()
    _rec(results, "driver_step_ok", 0 < d.x < 1)


def audit_fourier(results: List[Tuple[str, bool]]) -> None:
    print("\n-- fourier --")
    from form.dell_matrix.fourier import (
        dft, idft, make_sine, make_square,
        dominant_frequencies, continuous_ft_sample, gaussian_pulse,
    )

    s = make_sine(64, 3.0)
    X = dft(s)
    recon = idft(X)
    err = sum(abs(a - b) for a, b in zip(s, recon)) / len(s)
    _rec(results, "dft_idft_roundtrip", err < 1e-9)

    dom = dominant_frequencies(s, top=1)
    _rec(results, "sine_peak_k3", abs(dom[0]["k"] - 3) <= 1)

    sq = make_square(64, 1.0)
    doms = dominant_frequencies(sq, top=5)
    ks = {d["k"] for d in doms}
    _rec(results, "square_odd_harmonics", 1 in ks or 3 in ks)

    cg = continuous_ft_sample(gaussian_pulse, n_t=64, n_f=32)
    _rec(results, "continuous_ft_runs", len(cg["magnitudes"]) == 32 and max(cg["magnitudes"]) > 0)


def audit_high_value_surface(results: List[Tuple[str, bool]]) -> None:
    print("\n-- high_value_api surface --")
    from form.dell_matrix.high_value_api import open_wired
    from form.dell_matrix.fourier import make_sine

    try:
        p = open_wired("Audit")
        p.place("a", "Alpha", x=1, y=0)
        ok_attrs = all(hasattr(p, name) for name in (
            "la_transform", "logistic_tick", "fourier_analyze",
            "eigen_stability", "force_tick",
        ))
        _rec(results, "methods_present", ok_attrs)

        ft = p.force_tick()
        _rec(results, "force_tick_has_nature", isinstance(ft.get("nature"), dict))

        tr = p.la_transform("scale", 1.1)
        _rec(results, "la_transform_ok", tr.get("ok") is True)

        fa = p.fourier_analyze(make_sine(32, 2.0))
        _rec(results, "fourier_analyze_ok", fa.get("ok") is True)

        es = p.eigen_stability("rotate", 0.5)
        _rec(results, "eigen_stability_ok", "continuous" in es and "discrete" in es)
    except Exception as e:
        _rec(results, "surface_exception", False)
        print(f"    exception: {e}")


def audit_universal_properties(results: List[Tuple[str, bool]]) -> None:
    print("\n-- universal properties --")
    # 1. Offline: no network imports required for cores
    import sys
    forbidden = {"requests", "urllib3", "http.client"}
    leaked = [m for m in forbidden if m in sys.modules]
    _rec(results, "no_network_modules_required", len(leaked) == 0)

    # 2. Pure math consistency: det(AB)=det(A)det(B)
    from form.dell_matrix.linear_algebra import Mat2
    A = Mat2.scale(2, 3)
    B = Mat2.rotate(0.4)
    _rec(results, "det_multiplicative", abs(A.compose(B).det() - A.det() * B.det()) < 1e-9)

    # 3. DFT energy roughly preserved (Parseval soft check on pure sine)
    from form.dell_matrix.fourier import dft, make_sine
    s = make_sine(32, 2.0)
    X = dft(s)
    time_energy = sum(x * x for x in s)
    freq_energy = sum(abs(c) ** 2 for c in X) / len(X)
    # Parseval: sum |x|² = (1/N) sum |X|²  → ratio ~ 1
    ratio = freq_energy / max(1e-12, time_energy)
    _rec(results, "parseval_soft", abs(ratio - 1.0) < 0.05)

    # 4. Logistic stays in (0,1) under valid r
    from form.dell_matrix.logistic_map import logistic_step
    x = 0.3
    for r in (1.5, 2.5, 3.2, 3.9):
        x = logistic_step(x, r)
    _rec(results, "logistic_invariant_unit_interval", 0 < x < 1)


def run_audit() -> bool:
    print("=== DELLMATRIX INCORPORATION AUDIT ===")
    results: List[Tuple[str, bool]] = []
    audit_linear_algebra(results)
    audit_eigen_stability(results)
    audit_logistic(results)
    audit_fourier(results)
    audit_high_value_surface(results)
    audit_universal_properties(results)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n=== AUDIT RESULT: {passed}/{total} ===")
    if passed != total:
        fails = [n for n, ok in results if not ok]
        print("Failed:", fails)
    return passed == total


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_audit() else 1)
