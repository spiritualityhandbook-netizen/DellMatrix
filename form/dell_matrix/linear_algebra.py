#!/usr/bin/env python3
"""
Linear Algebra cores — geometric intuition from 3Blue1Brown Essence of Linear Algebra.

Sources (Phase 5 + full series):
  Ch1 Vectors · Ch2 Span/basis · Ch3 Linear transforms/matrices ·
  Ch4 Composition · Ch6 Determinant · Ch9 Dot · Ch14 Eigen · Ch15 Eigen trick

Maps idea positions and force fields as 2D transforms. Offline · Boolean host intact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math

from form.dell_matrix.nature_code import Vec2


@dataclass
class Mat2:
    """2x2 matrix as two column vectors (3B1B style: where i-hat and j-hat land)."""
    a: float = 1.0  # col0.x  (i-hat x)
    c: float = 0.0  # col0.y  (i-hat y)
    b: float = 0.0  # col1.x  (j-hat x)
    d: float = 1.0  # col1.y  (j-hat y)

    @staticmethod
    def identity() -> "Mat2":
        return Mat2(1, 0, 0, 1)

    @staticmethod
    def scale(sx: float, sy: Optional[float] = None) -> "Mat2":
        sy = sx if sy is None else sy
        return Mat2(sx, 0, 0, sy)

    @staticmethod
    def rotate(radians: float) -> "Mat2":
        c, s = math.cos(radians), math.sin(radians)
        return Mat2(c, s, -s, c)

    @staticmethod
    def shear_x(k: float) -> "Mat2":
        return Mat2(1, 0, k, 1)

    @staticmethod
    def from_columns(i_hat: Vec2, j_hat: Vec2) -> "Mat2":
        return Mat2(i_hat.x, i_hat.y, j_hat.x, j_hat.y)

    def columns(self) -> Tuple[Vec2, Vec2]:
        return Vec2(self.a, self.c), Vec2(self.b, self.d)

    def apply(self, v: Vec2) -> Vec2:
        """Linear transform: new = M · v (columns weighted by coords)."""
        return Vec2(self.a * v.x + self.b * v.y, self.c * v.x + self.d * v.y)

    def compose(self, other: "Mat2") -> "Mat2":
        """self after other: self · other (3B1B composition right-to-left apply)."""
        # (self · other) · v = self · (other · v)
        o = other
        return Mat2(
            self.a * o.a + self.b * o.c,
            self.c * o.a + self.d * o.c,
            self.a * o.b + self.b * o.d,
            self.c * o.b + self.d * o.d,
        )

    def det(self) -> float:
        """Signed area scale factor (Ch6)."""
        return self.a * self.d - self.b * self.c

    def inverse(self) -> Optional["Mat2"]:
        det = self.det()
        if abs(det) < 1e-12:
            return None
        inv = 1.0 / det
        return Mat2(self.d * inv, -self.c * inv, -self.b * inv, self.a * inv)

    def transpose(self) -> "Mat2":
        return Mat2(self.a, self.b, self.c, self.d)

    def trace(self) -> float:
        return self.a + self.d

    def eigenvalues(self) -> Tuple[complex, complex]:
        """2x2 closed form (Ch14/15): roots of λ² - tr λ + det = 0."""
        tr = self.trace()
        det = self.det()
        disc = tr * tr - 4 * det
        if disc >= 0:
            s = math.sqrt(disc)
            return ((tr + s) / 2, (tr - s) / 2)
        s = math.sqrt(-disc)
        return (complex(tr / 2, s / 2), complex(tr / 2, -s / 2))

    def eigenvector_for(self, lam: float, eps: float = 1e-9) -> Optional[Vec2]:
        """Nullspace of (M - λI) — simple 2D solve."""
        # (a-λ) x + b y = 0
        aa, bb = self.a - lam, self.b
        cc, dd = self.c, self.d - lam
        # prefer more stable row
        if abs(bb) > abs(aa) and abs(bb) > eps:
            # y free=1 → x = -b/y term
            return Vec2(-bb, aa).normalize() if abs(aa) + abs(bb) > eps else Vec2(1, 0)
        if abs(aa) > eps:
            return Vec2(-bb, aa).normalize() if abs(aa) + abs(bb) > eps else Vec2(0, 1)
        if abs(dd) > eps or abs(cc) > eps:
            return Vec2(-dd, cc).normalize() if abs(cc) + abs(dd) > eps else Vec2(1, 0)
        return Vec2(1, 0)

    def eigen_pairs(self) -> List[Dict[str, Any]]:
        evs = self.eigenvalues()
        out = []
        for ev in evs:
            if isinstance(ev, complex) and abs(ev.imag) > 1e-9:
                out.append({"eigenvalue": {"re": ev.real, "im": ev.imag}, "vector": None, "note": "complex"})
            else:
                lam = float(ev.real if isinstance(ev, complex) else ev)
                vec = self.eigenvector_for(lam)
                out.append({
                    "eigenvalue": lam,
                    "vector": {"x": vec.x, "y": vec.y} if vec else None,
                })
        return out

    def to_dict(self) -> Dict[str, float]:
        return {"a": self.a, "c": self.c, "b": self.b, "d": self.d, "det": self.det(), "trace": self.trace()}


def dot(u: Vec2, v: Vec2) -> float:
    return u.x * v.x + u.y * v.y


def cross2(u: Vec2, v: Vec2) -> float:
    """2D cross magnitude (signed area)."""
    return u.x * v.y - u.y * v.x


def project(u: Vec2, onto: Vec2) -> Vec2:
    """Scalar projection of u onto onto."""
    m2 = onto.mag_sq()
    if m2 < 1e-12:
        return Vec2(0, 0)
    s = dot(u, onto) / m2
    return onto.copy().mult(s)


def linear_combine(coeffs: List[float], basis: List[Vec2]) -> Vec2:
    """Ch2: span element c0*b0 + c1*b1 + ..."""
    out = Vec2(0, 0)
    for c, b in zip(coeffs, basis):
        out.add(b.copy().mult(c))
    return out


def transform_nodes(nodes: List[Dict[str, Any]], m: Mat2) -> List[Dict[str, Any]]:
    """Apply linear transform to node x,y — lattice geometry move."""
    out = []
    for n in nodes:
        v = m.apply(Vec2(float(n.get("x") or 0), float(n.get("y") or 0)))
        nn = dict(n)
        nn["x"] = round(v.x, 4)
        nn["y"] = round(v.y, 4)
        out.append(nn)
    return out


def apply_transform_to_plane(plane, m: Mat2) -> int:
    applied = 0
    for u in (getattr(plane, "units", {}) or {}).values():
        v = m.apply(Vec2(float(u.x), float(u.y)))
        u.x, u.y = v.x, v.y
        applied += 1
    return applied


def program_transform(program, kind: str = "rotate", amount: float = 0.1) -> Dict[str, Any]:
    """Apply named transform to all idea positions on the plane."""
    kind = (kind or "rotate").lower()
    if kind == "rotate":
        m = Mat2.rotate(float(amount))
    elif kind == "scale":
        m = Mat2.scale(float(amount))
    elif kind == "shear":
        m = Mat2.shear_x(float(amount))
    elif kind == "identity":
        m = Mat2.identity()
    else:
        m = Mat2.rotate(float(amount))
    n = apply_transform_to_plane(program.cube.session.plane, m)
    try:
        program.note_seed(15, "Map", f"la_{kind}")
    except Exception:
        pass
    return {"ok": True, "kind": kind, "amount": amount, "moved": n, "mat": m.to_dict(), "det": m.det()}


def smoke() -> bool:
    print("=== LINEAR_ALGEBRA SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    m = Mat2.rotate(math.pi / 2)
    v = m.apply(Vec2(1, 0))
    rec("rotate_i_to_j", abs(v.x) < 1e-9 and abs(v.y - 1) < 1e-9)
    rec("det_rotate", abs(m.det() - 1) < 1e-9)
    s = Mat2.scale(2, 3)
    rec("det_scale", abs(s.det() - 6) < 1e-9)
    comp = Mat2.rotate(math.pi / 4).compose(Mat2.scale(2))
    rec("compose", abs(comp.det() - 2) < 1e-6)
    eigs = Mat2.scale(2, 3).eigen_pairs()
    rec("eigen", len(eigs) == 2)
    inv = s.inverse()
    rec("inverse", inv is not None and abs(inv.det() - 1 / 6) < 1e-9)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
