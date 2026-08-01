#!/usr/bin/env python3
"""
H / V / F Harmonic Lattice + shared perception forms.

One lattice. Cube/core, square/circle, cube/sphere, Flower of Life
are perception modes — coordinates stay; reading changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from form.dell_matrix.perception import (
    Form,
    Perception,
    flower_to_lattice_coords,
    shared_lattice_principle,
)

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FIFTH = 7
MAJOR_THIRD = 4


class OverlayMode(str, Enum):
    HARMONIC = "harmonic"
    STRUCTURAL = "structural"
    CONCEPTUAL = "conceptual"


class Perspective(str, Enum):
    TOP = "top"
    SIDE = "side"
    CORNER = "corner"
    FULL3 = "full3"


@dataclass
class Cell:
    h: int
    v: int
    f: int = 0
    content: Any = None
    label: str = ""
    tags: List[str] = field(default_factory=list)

    @property
    def coords(self) -> Tuple[int, int, int]:
        return (self.h, self.v, self.f)


@dataclass
class SnapModule:
    id: str
    kind: str = "lattice2d"
    axis: str = "H"
    index: int = 0
    cells: Dict[Tuple[int, int, int], Cell] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HarmonicLattice:
    size: int = 12
    overlay: OverlayMode = OverlayMode.HARMONIC
    perspective: Perspective = Perspective.TOP
    perception: Perception = field(default_factory=lambda: Perception(Form.CUBE))
    cells: Dict[Tuple[int, int, int], Cell] = field(default_factory=dict)
    modules: Dict[str, SnapModule] = field(default_factory=dict)
    origin_note: int = 0

    def note_at(self, h: int, v: int, f: int = 0) -> str:
        idx = (self.origin_note + h * FIFTH + v * MAJOR_THIRD) % 12
        name = NOTES[idx]
        if self.overlay == OverlayMode.STRUCTURAL:
            return f"({h},{v},{f})"
        if self.overlay == OverlayMode.CONCEPTUAL:
            cell = self.cells.get((h, v, f))
            return cell.label or f"cell[{h},{v},{f}]"
        return f"{name}_o{f}"

    def put(
        self, h: int, v: int, f: int = 0, *,
        content: Any = None, label: str = "", tags: Optional[List[str]] = None,
    ) -> Cell:
        cell = Cell(h=h, v=v, f=f, content=content, label=label, tags=list(tags or []))
        self.cells[(h, v, f)] = cell
        return cell

    def get(self, h: int, v: int, f: int = 0) -> Optional[Cell]:
        return self.cells.get((h, v, f))

    def chord_neighbors(self, h: int, v: int, f: int = 0) -> List[Tuple[int, int, int]]:
        return [(h, v, f), (h + 1, v, f), (h, v + 1, f)]

    def pull_chord(self, h: int, v: int, f: int = 0) -> List[Dict[str, Any]]:
        out = []
        for coord in self.chord_neighbors(h, v, f):
            cell = self.cells.get(coord)
            out.append({
                "coords": coord,
                "note": self.note_at(*coord),
                "label": cell.label if cell else "",
                "shell": self.perception.shell(*coord),
                "skin": self.perception.skin_name(),
                "has_content": cell is not None and cell.content is not None,
            })
        return out

    def set_overlay(self, mode: OverlayMode) -> None:
        self.overlay = mode

    def set_perspective(self, p: Perspective) -> None:
        self.perspective = p

    def set_form(self, form: Form) -> None:
        self.perception.set_form(form)

    def toggle_form(self) -> Form:
        """cube↔sphere, square↔circle, etc."""
        return self.perception.toggle_dual()

    def to_core(self) -> None:
        self.perception.set_form(Form.CORE)

    def to_cube(self) -> None:
        self.perception.set_form(Form.CUBE)

    def to_sphere(self) -> None:
        self.perception.set_form(Form.SPHERE)

    def to_flower(self) -> None:
        self.perception.set_form(Form.FLOWER)

    def plant_flower(self, rings: int = 2) -> int:
        """Place Flower of Life centers onto the lattice as empty cells."""
        self.to_flower()
        n = 0
        for pt in flower_to_lattice_coords(rings=rings):
            h, v, f = pt["h"], pt["v"], pt["f"]
            if (h, v, f) not in self.cells:
                self.put(h, v, f, label=f"flower_{h}_{v}", tags=["flower"])
                n += 1
        return n

    def cells_by_shell(self, shell: int) -> List[Cell]:
        out = []
        for (h, v, f), cell in self.cells.items():
            if self.perception.shell(h, v, f) == shell:
                out.append(cell)
        return out

    def snap_in(self, module: SnapModule) -> str:
        self.modules[module.id] = module
        for coord, cell in module.cells.items():
            if coord not in self.cells:
                self.cells[coord] = cell
        return module.id

    def snap_out(self, module_id: str) -> bool:
        mod = self.modules.pop(module_id, None)
        if not mod:
            return False
        for coord in list(mod.cells.keys()):
            if coord in self.cells:
                del self.cells[coord]
        return True

    def latch_plane(
        self, module_id: str, *,
        axis: str = "H", index: int = 0, width: int = 3, depth: int = 3,
        label_prefix: str = "latch",
    ) -> SnapModule:
        cells: Dict[Tuple[int, int, int], Cell] = {}
        axis = axis.upper()
        for a in range(width):
            for b in range(depth):
                if axis == "H":
                    h, v, f = index, a, b
                else:
                    h, v, f = a, index, b
                cells[(h, v, f)] = Cell(h=h, v=v, f=f, label=f"{label_prefix}_{h}_{v}_{f}")
        mod = SnapModule(id=module_id, kind="lattice2d", axis=axis, index=index, cells=cells,
                         meta={"width": width, "depth": depth})
        self.snap_in(mod)
        return mod

    def render_ascii(self, f: int = 0, max_n: int = 8) -> str:
        n = min(self.size, max_n)
        lines = [
            f"HarmonicLattice size={self.size} overlay={self.overlay.value} "
            f"perspective={self.perspective.value} form={self.perception.form.value}",
            f"skin={self.perception.skin_name()}  modules={len(self.modules)} cells={len(self.cells)}",
            "",
        ]
        lines.append("V\\H " + "  ".join(f"{h:4d}" for h in range(n)))
        for v in range(n - 1, -1, -1):
            row = [f"{self.note_at(h, v, f):>6}" for h in range(n)]
            lines.append(f"{v:3d} " + " ".join(row))
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "size": self.size,
            "overlay": self.overlay.value,
            "perspective": self.perspective.value,
            "form": self.perception.form.value,
            "dual": self.perception.dual().value,
            "skin": self.perception.skin_name(),
            "cells": len(self.cells),
            "modules": list(self.modules.keys()),
            "principle": "one lattice · many perceptions",
            "example_origin": self.note_at(0, 0, 0),
        }


def smoke() -> bool:
    print("=== LATTICE+PERCEPTION SMOKE ===")
    r = []
    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))
    lat = HarmonicLattice(size=12)
    rec("cube default", lat.perception.form == Form.CUBE)
    lat.to_sphere()
    rec("sphere", lat.perception.form == Form.SPHERE)
    lat.to_core()
    rec("core", lat.perception.form == Form.CORE)
    lat.to_cube()
    lat.toggle_form()
    rec("toggle sphere", lat.perception.form == Form.SPHERE)
    n = lat.plant_flower(1)
    rec("flower planted", n >= 7 and lat.perception.form == Form.FLOWER)
    print(shared_lattice_principle())
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
