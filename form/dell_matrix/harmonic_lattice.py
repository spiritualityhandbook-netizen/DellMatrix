#!/usr/bin/env python3
"""
H / V / F Harmonic Lattice — foundation for DellMatrix creativity space.

H = Harmonic  (horizontal) — default: perfect fifths (+7 semitones)
V = Vibrational (vertical) — default: major thirds (+4 semitones)
F = Frequency / Forward    — depth layer (octave / register / detail)

Laws:
- Structural coordinates always exist.
- Harmonic overlay is optional (can turn off).
- Sparse storage (infinite-as-needed).
- Snap modules in/out without destroying the lattice.
- Perspective is a view filter, not a different universe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Interval steps (semitones) for Tonnetz-style plane
FIFTH = 7
MAJOR_THIRD = 4
MINOR_THIRD = 3


class OverlayMode(str, Enum):
    HARMONIC = "harmonic"       # musical identities
    STRUCTURAL = "structural"   # pure coordinates only
    CONCEPTUAL = "conceptual"   # free labels / idea mode


class Perspective(str, Enum):
    TOP = "top"           # HV plane, F compressed
    SIDE = "side"         # HF or VF slice
    CORNER = "corner"     # isometric-style center focus
    FULL3 = "full3"       # all three axes acknowledged


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
    """A latchable lattice or cube block."""
    id: str
    kind: str = "lattice2d"  # lattice2d | cube | capability
    axis: str = "H"          # latch axis H or V
    index: int = 0           # line index on that axis
    cells: Dict[Tuple[int, int, int], Cell] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HarmonicLattice:
    """Sparse H/V/F matrix. Default zone size 12 (musical) or 16 (fractal-friendly)."""

    size: int = 12
    overlay: OverlayMode = OverlayMode.HARMONIC
    perspective: Perspective = Perspective.TOP
    cells: Dict[Tuple[int, int, int], Cell] = field(default_factory=dict)
    modules: Dict[str, SnapModule] = field(default_factory=dict)
    origin_note: int = 0  # C

    def note_at(self, h: int, v: int, f: int = 0) -> str:
        """Tonnetz-style note from H fifths + V major thirds; F = octave label."""
        idx = (self.origin_note + h * FIFTH + v * MAJOR_THIRD) % 12
        name = NOTES[idx]
        if self.overlay == OverlayMode.STRUCTURAL:
            return f"({h},{v},{f})"
        if self.overlay == OverlayMode.CONCEPTUAL:
            cell = self.cells.get((h, v, f))
            return cell.label or f"cell[{h},{v},{f}]"
        return f"{name}_o{f}"

    def put(
        self,
        h: int,
        v: int,
        f: int = 0,
        *,
        content: Any = None,
        label: str = "",
        tags: Optional[List[str]] = None,
    ) -> Cell:
        cell = Cell(h=h, v=v, f=f, content=content, label=label, tags=list(tags or []))
        self.cells[(h, v, f)] = cell
        return cell

    def get(self, h: int, v: int, f: int = 0) -> Optional[Cell]:
        return self.cells.get((h, v, f))

    def chord_neighbors(self, h: int, v: int, f: int = 0) -> List[Tuple[int, int, int]]:
        """Major triad shape on Tonnetz: root, +fifth (H+1), +major third (V+1)."""
        return [(h, v, f), (h + 1, v, f), (h, v + 1, f)]

    def pull_chord(self, h: int, v: int, f: int = 0) -> List[Dict[str, Any]]:
        out = []
        for coord in self.chord_neighbors(h, v, f):
            cell = self.cells.get(coord)
            out.append({
                "coords": coord,
                "note": self.note_at(*coord),
                "label": cell.label if cell else "",
                "has_content": cell is not None and cell.content is not None,
            })
        return out

    def set_overlay(self, mode: OverlayMode) -> None:
        self.overlay = mode

    def set_perspective(self, p: Perspective) -> None:
        self.perspective = p

    def snap_in(self, module: SnapModule) -> str:
        self.modules[module.id] = module
        # merge module cells into lattice (non-destructive to existing unless same coord)
        for coord, cell in module.cells.items():
            if coord not in self.cells:
                self.cells[coord] = cell
        return module.id

    def snap_out(self, module_id: str) -> bool:
        mod = self.modules.pop(module_id, None)
        if not mod:
            return False
        for coord in list(mod.cells.keys()):
            # only remove if still the same object / belongs to module
            if coord in self.cells and coord in mod.cells:
                del self.cells[coord]
        return True

    def latch_plane(
        self,
        module_id: str,
        *,
        axis: str = "H",
        index: int = 0,
        width: int = 3,
        depth: int = 3,
        label_prefix: str = "latch",
    ) -> SnapModule:
        """
        Create a 2D lattice module and snap it onto an H or V line.
        Demonstrates lattice-latch → 3D opening.
        """
        cells: Dict[Tuple[int, int, int], Cell] = {}
        axis = axis.upper()
        for a in range(width):
            for b in range(depth):
                if axis == "H":
                    h, v, f = index, a, b
                else:
                    h, v, f = a, index, b
                cells[(h, v, f)] = Cell(
                    h=h, v=v, f=f,
                    label=f"{label_prefix}_{h}_{v}_{f}",
                )
        mod = SnapModule(
            id=module_id,
            kind="lattice2d",
            axis=axis,
            index=index,
            cells=cells,
            meta={"width": width, "depth": depth},
        )
        self.snap_in(mod)
        return mod

    def slice_top(self, f: int = 0) -> List[List[str]]:
        """HV view at fixed F — top-down perspective."""
        # show a window around occupied or 0..size
        grid = []
        for v in range(self.size - 1, -1, -1):
            row = [self.note_at(h, v, f) for h in range(self.size)]
            grid.append(row)
        return grid

    def render_ascii(self, f: int = 0, max_n: int = 8) -> str:
        n = min(self.size, max_n)
        lines = [
            f"HarmonicLattice size={self.size} overlay={self.overlay.value} perspective={self.perspective.value}",
            f"axes: H=fifths V=major_thirds F=frequency  modules={len(self.modules)} cells={len(self.cells)}",
            "",
        ]
        # header
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
            "cells": len(self.cells),
            "modules": list(self.modules.keys()),
            "example_origin": self.note_at(0, 0, 0),
            "example_fifth": self.note_at(1, 0, 0),
            "example_third": self.note_at(0, 1, 0),
        }


def recommend_size(prefer_music: bool = True, prefer_fractal: bool = False) -> int:
    """Practical size chooser."""
    if prefer_fractal:
        return 16
    if prefer_music:
        return 12
    return 12


def smoke() -> bool:
    print("=== HARMONIC LATTICE SMOKE ===")
    r = []
    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))
    lat = HarmonicLattice(size=12)
    rec("origin C", lat.note_at(0, 0, 0).startswith("C"))
    rec("fifth G", "G" in lat.note_at(1, 0, 0))
    rec("third E", "E" in lat.note_at(0, 1, 0))
    lat.put(0, 0, 0, label="seed", content="ima")
    chord = lat.pull_chord(0, 0, 0)
    rec("chord 3", len(chord) == 3)
    lat.set_overlay(OverlayMode.STRUCTURAL)
    rec("structural", lat.note_at(0, 0, 0) == "(0,0,0)")
    lat.set_overlay(OverlayMode.HARMONIC)
    lat.latch_plane("plane_b", axis="H", index=0)
    rec("snap", "plane_b" in lat.modules)
    lat.snap_out("plane_b")
    rec("snap out", "plane_b" not in lat.modules)
    print(lat.render_ascii(max_n=4))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
