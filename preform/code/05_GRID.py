#!/usr/bin/env python3
"""
05_GRID.py
Code Phase 2 · Artifact 5
Status: TRUE
Offline · Zero dependencies · Stdlib only

Minimal coordinate layer.
Provides an (x, y) plane that later Avatar FSM and expression fields can occupy.
No rendering. Pure data + movement primitives.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any, Optional, List
from dataclasses import dataclass, field

Coord = Tuple[int, int]

@dataclass
class Cell:
    """One location on the grid."""
    x: int
    y: int
    content: Optional[Any] = None          # can hold a DELL node, TEXT, or later Avatar state
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def pos(self) -> Coord:
        return (self.x, self.y)

class Grid:
    """
    Sparse offline grid.
    Only stores cells that have been written.
    Origin (0, 0) is the default center.
    """
    def __init__(self, origin: Coord = (0, 0)):
        self.origin = origin
        self._cells: Dict[Coord, Cell] = {}

    def get(self, x: int, y: int) -> Cell:
        key = (x, y)
        if key not in self._cells:
            self._cells[key] = Cell(x=x, y=y)
        return self._cells[key]

    def set(self, x: int, y: int, content: Any = None, **meta) -> Cell:
        cell = self.get(x, y)
        cell.content = content
        cell.meta.update(meta)
        return cell

    def clear(self, x: int, y: int) -> None:
        key = (x, y)
        if key in self._cells:
            del self._cells[key]

    def move(self, from_pos: Coord, to_pos: Coord) -> Optional[Cell]:
        """Move content from one cell to another. Returns the destination cell."""
        fx, fy = from_pos
        tx, ty = to_pos
        src = self.get(fx, fy)
        if src.content is None and not src.meta:
            return None
        dest = self.set(tx, ty, content=src.content, **src.meta)
        self.clear(fx, fy)
        return dest

    def neighbors(self, x: int, y: int, include_diag: bool = False) -> List[Cell]:
        """4-directional by default. 8-directional if include_diag=True."""
        deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if include_diag:
            deltas += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        return [self.get(x + dx, y + dy) for dx, dy in deltas]

    def occupied(self) -> List[Cell]:
        """All cells that currently hold content or meta."""
        return [c for c in self._cells.values() if c.content is not None or c.meta]

    def bounds(self) -> Optional[Tuple[Coord, Coord]]:
        """Return ((min_x, min_y), (max_x, max_y)) or None if empty."""
        if not self._cells:
            return None
        xs = [c.x for c in self._cells.values()]
        ys = [c.y for c in self._cells.values()]
        return ((min(xs), min(ys)), (max(xs), max(ys)))

    def __repr__(self) -> str:
        occ = len(self.occupied())
        return f"Grid(origin={self.origin}, occupied={occ})"


# ---------------------------------------------------------------------------
# Convenience helpers for later Avatar / expression use
# ---------------------------------------------------------------------------

def place_dell(grid: Grid, x: int, y: int, dell_num: int, flow: Optional[str] = None) -> Cell:
    """Place a DELL evaluation result onto the grid."""
    return grid.set(x, y, content={"kind": "DELL", "value": dell_num, "flow": flow})

def place_text(grid: Grid, x: int, y: int, text: str) -> Cell:
    """Place English / display text onto the grid."""
    return grid.set(x, y, content={"kind": "TEXT", "value": text})


def demo():
    g = Grid()
    place_dell(g, 0, 0, 50, flow=">")
    place_dell(g, 1, 0, 8)
    place_text(g, 0, 1, "English display")
    print(g)
    print("Occupied:", [(c.pos, c.content) for c in g.occupied()])
    print("Neighbors of origin:", [c.pos for c in g.neighbors(0, 0)])

if __name__ == "__main__":
    demo()
