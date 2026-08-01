#!/usr/bin/env python3
"""
Perception forms on one shared lattice.

Law: geometry underneath stays the same.
Perception only changes how distance, boundary, and neighborhood are read.

  square  ↔ circle
  cube    ↔ sphere
  cube    ↔ core   (radial shells from origin)
  flower of life   (equal circles on triangular centers)

Spheres and cubes share lattice points; only the metric/skin changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import math


class Form(str, Enum):
    SQUARE = "square"
    CIRCLE = "circle"
    CUBE = "cube"
    SPHERE = "sphere"
    CORE = "core"       # radial shells from origin
    FLOWER = "flower"   # Flower of Life style


# Dual pairs (same lattice, different reading)
DUALS = {
    Form.SQUARE: Form.CIRCLE,
    Form.CIRCLE: Form.SQUARE,
    Form.CUBE: Form.SPHERE,
    Form.SPHERE: Form.CUBE,
    Form.CORE: Form.CUBE,     # core ↔ cubic grid
    Form.FLOWER: Form.CIRCLE, # flower built from circles
}


@dataclass
class Perception:
    form: Form = Form.CUBE
    origin: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def dual(self) -> Form:
        return DUALS.get(self.form, self.form)

    def toggle_dual(self) -> Form:
        self.form = self.dual()
        return self.form

    def set_form(self, form: Form) -> None:
        self.form = form

    # --- metrics on the same coordinates ---

    def distance(self, h: float, v: float, f: float = 0.0) -> float:
        """Distance from origin under current perception."""
        x = h - self.origin[0]
        y = v - self.origin[1]
        z = f - self.origin[2]
        if self.form in (Form.SQUARE, Form.CUBE):
            # Chebyshev / cubic shell feel for cube; euclidean for square plane often L2
            if self.form == Form.CUBE:
                return max(abs(x), abs(y), abs(z))  # cubic shells
            return math.hypot(x, y)
        if self.form in (Form.CIRCLE, Form.SPHERE, Form.CORE, Form.FLOWER):
            if self.form == Form.CIRCLE:
                return math.hypot(x, y)
            return math.sqrt(x * x + y * y + z * z)  # spherical / core radial
        return math.sqrt(x * x + y * y + z * z)

    def shell(self, h: float, v: float, f: float = 0.0) -> int:
        """Integer shell index from origin."""
        return int(round(self.distance(h, v, f)))

    def skin_name(self) -> str:
        return {
            Form.SQUARE: "square",
            Form.CIRCLE: "circle",
            Form.CUBE: "cube",
            Form.SPHERE: "sphere",
            Form.CORE: "seed",      # core reads as radial seed shells
            Form.FLOWER: "flower",
        }.get(self.form, "cube")


def flower_centers(rings: int = 2, radius: float = 1.0) -> List[Tuple[float, float]]:
    """
    Flower of Life center points in 2D.
    Ring 0: origin
    Ring 1: 6 centers at 60° around origin
    Ring 2+: continue hexagonal packing
    """
    centers: List[Tuple[float, float]] = [(0.0, 0.0)]
    if rings < 1:
        return centers
    # ring 1
    for k in range(6):
        ang = math.radians(60 * k)
        centers.append((radius * math.cos(ang), radius * math.sin(ang)))
    # further rings: hexagonal lattice points with axial coords
    for r in range(2, rings + 1):
        for i in range(r):
            # walk hex ring
            pass
        # six corners + edges
        for corner in range(6):
            ang0 = math.radians(60 * corner)
            # from corner along edge to next
            ang1 = math.radians(60 * ((corner + 1) % 6))
            c0 = (r * radius * math.cos(ang0), r * radius * math.sin(ang0))
            c1 = (r * radius * math.cos(ang1), r * radius * math.sin(ang1))
            centers.append(c0)
            for e in range(1, r):
                t = e / r
                centers.append((c0[0] * (1 - t) + c1[0] * t, c0[1] * (1 - t) + c1[1] * t))
    # dedupe roughly
    out: List[Tuple[float, float]] = []
    seen = set()
    for x, y in centers:
        key = (round(x, 5), round(y, 5))
        if key not in seen:
            seen.add(key)
            out.append((x, y))
    return out


def flower_to_lattice_coords(
    rings: int = 2,
    radius: float = 1.0,
) -> List[Dict[str, Any]]:
    """Map Flower centers onto approximate integer H/V lattice slots."""
    pts = flower_centers(rings=rings, radius=radius)
    mapped = []
    for x, y in pts:
        h = int(round(x))
        v = int(round(y))
        mapped.append({
            "h": h,
            "v": v,
            "f": 0,
            "x": x,
            "y": y,
            "form": "flower",
        })
    return mapped


def shared_lattice_principle() -> str:
    return (
        "One lattice. Many perceptions.\n"
        "Square and circle share centers; only boundary reading changes.\n"
        "Cube and sphere share coordinates; only distance metric changes\n"
        "  (cubic max-norm shells vs spherical radial shells).\n"
        "Core mode is radial shells from origin on the same points.\n"
        "Flower of Life places equal circles on a triangular packing\n"
        "  that still snaps to the same coordinate family.\n"
        "Snap/overlay never destroys the structural lattice."
    )


def smoke() -> bool:
    print("=== PERCEPTION SMOKE ===")
    r = []
    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))
    p = Perception(Form.CUBE)
    rec("cube shell", p.distance(2, 0, 0) == 2)
    p.set_form(Form.SPHERE)
    rec("sphere dist", abs(p.distance(3, 4, 0) - 5) < 1e-9)
    p.set_form(Form.SQUARE)
    p.toggle_dual()
    rec("dual to circle", p.form == Form.CIRCLE)
    p.set_form(Form.CUBE)
    p.toggle_dual()
    rec("dual to sphere", p.form == Form.SPHERE)
    centers = flower_centers(1)
    rec("flower ring1", len(centers) == 7)  # origin + 6
    mapped = flower_to_lattice_coords(1)
    rec("flower map", len(mapped) >= 7)
    print(shared_lattice_principle())
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
