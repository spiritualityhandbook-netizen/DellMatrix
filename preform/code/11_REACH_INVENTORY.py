#!/usr/bin/env python3
"""
11_REACH_INVENTORY.py
Code Phase 3 · Artifact 11
Status: TRUE
Offline · Zero dependencies · Stdlib only

Grows the living structure:
- Extends Avatar (Artifact 6) pick/place + Reach tiers
- Uses Grid (Artifact 5) for world items
- Body-first law: all actions go through body; mind only reads

Reach tiers (from page 09):
  CLOSE = 1 cell
  AWAY  = 2 cells
  FAR   = 3 cells
"""

from __future__ import annotations
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum, auto

Coord = Tuple[int, int]

# ---------- Minimal fallbacks (so file runs standalone) ----------
class Reach(Enum):
    CLOSE = 1
    AWAY  = 2
    FAR   = 3

class Facing(Enum):
    N  = (0, 1)
    NE = (1, 1)
    E  = (1, 0)
    SE = (1, -1)
    S  = (0, -1)
    SW = (-1, -1)
    W  = (-1, 0)
    NW = (-1, 1)
    @property
    def delta(self) -> Coord:
        return self.value

@dataclass
class BodyState:
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    reach: Reach = Reach.CLOSE
    holding: Optional[Any] = None

@dataclass
class SimpleAvatar:
    body: BodyState = field(default_factory=BodyState)
    name: str = "Avatar"
    def read_body(self) -> BodyState:
        return BodyState(
            pos=self.body.pos,
            facing=self.body.facing,
            reach=self.body.reach,
            holding=self.body.holding,
        )

@dataclass
class SimpleCell:
    x: int
    y: int
    content: Optional[Any] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    @property
    def pos(self) -> Coord:
        return (self.x, self.y)

class SimpleGrid:
    def __init__(self):
        self._cells: Dict[Coord, SimpleCell] = {}
    def get(self, x: int, y: int) -> SimpleCell:
        key = (x, y)
        if key not in self._cells:
            self._cells[key] = SimpleCell(x=x, y=y)
        return self._cells[key]
    def set(self, x: int, y: int, content: Any = None, **meta) -> SimpleCell:
        cell = self.get(x, y)
        cell.content = content
        cell.meta.update(meta)
        return cell
    def clear(self, x: int, y: int) -> None:
        key = (x, y)
        if key in self._cells:
            del self._cells[key]

# ---------- Inventory ----------

@dataclass
class InventorySlot:
    item: Any = None
    label: str = ""

@dataclass
class Inventory:
    """
    Small fixed inventory (body-held + belt).
    holding (hand) is separate and lives on Avatar.body.holding.
    """
    slots: List[InventorySlot] = field(default_factory=lambda: [
        InventorySlot(label="belt_1"),
        InventorySlot(label="belt_2"),
        InventorySlot(label="belt_3"),
    ])

    def add(self, item: Any) -> bool:
        for s in self.slots:
            if s.item is None:
                s.item = item
                return True
        return False  # full

    def remove(self, index: int) -> Optional[Any]:
        if 0 <= index < len(self.slots):
            item = self.slots[index].item
            self.slots[index].item = None
            return item
        return None

    def list_items(self) -> List[Any]:
        return [s.item for s in self.slots if s.item is not None]

    def is_full(self) -> bool:
        return all(s.item is not None for s in self.slots)

# ---------- Reach + Inventory controller ----------

@dataclass
class ReachInventory:
    """
    Ties Avatar body + Grid + Inventory.
    All actions are body-first.
    """
    avatar: Any                    # Avatar or SimpleAvatar
    grid: Any                      # Grid or SimpleGrid
    inventory: Inventory = field(default_factory=Inventory)

    def _distance(self, a: Coord, b: Coord) -> int:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    def can_reach(self, target: Coord) -> bool:
        body = self.avatar.read_body()
        dist = self._distance(body.pos, target)
        return dist <= body.reach.value

    def look_at(self, target: Coord) -> Optional[Any]:
        """Read what is on the target cell if in reach. Mind-safe."""
        if not self.can_reach(target):
            return None
        cell = self.grid.get(*target)
        return cell.content

    def pick(self, target: Coord) -> bool:
        """
        Pick item from grid cell into hand (body.holding).
        Fails if out of reach, hand full, or cell empty.
        """
        body = self.avatar.body
        if body.holding is not None:
            return False
        if not self.can_reach(target):
            return False
        cell = self.grid.get(*target)
        if cell.content is None:
            return False
        body.holding = cell.content
        self.grid.clear(*target)
        return True

    def place(self, target: Coord) -> bool:
        """
        Place hand item onto grid cell.
        Fails if out of reach, hand empty, or cell occupied.
        """
        body = self.avatar.body
        if body.holding is None:
            return False
        if not self.can_reach(target):
            return False
        cell = self.grid.get(*target)
        if cell.content is not None:
            return False
        self.grid.set(*target, content=body.holding)
        body.holding = None
        return True

    def stow(self) -> bool:
        """Move hand item into first free inventory slot."""
        body = self.avatar.body
        if body.holding is None:
            return False
        if self.inventory.add(body.holding):
            body.holding = None
            return True
        return False

    def draw(self, slot_index: int = 0) -> bool:
        """Draw item from inventory slot into hand."""
        body = self.avatar.body
        if body.holding is not None:
            return False
        item = self.inventory.remove(slot_index)
        if item is None:
            return False
        body.holding = item
        return True

    def set_reach(self, tier: Reach) -> None:
        self.avatar.body.reach = tier

    def status(self) -> Dict[str, Any]:
        body = self.avatar.read_body()
        return {
            "pos": body.pos,
            "facing": body.facing.name if hasattr(body.facing, "name") else str(body.facing),
            "reach": body.reach.name if hasattr(body.reach, "name") else str(body.reach),
            "holding": body.holding,
            "inventory": self.inventory.list_items(),
        }

# ---------- Demo ----------

def demo():
    grid = SimpleGrid()
    av = SimpleAvatar()
    ri = ReachInventory(avatar=av, grid=grid)

    # Place a world item
    grid.set(1, 0, content={"kind": "tool", "name": "wrench"})
    print("World item at (1,0):", grid.get(1, 0).content)

    # Too far with CLOSE reach
    print("Can reach (1,0) with CLOSE?", ri.can_reach((1, 0)))
    print("Pick attempt (should fail if facing wrong / distance):", ri.pick((1, 0)))

    # Move avatar next to it
    av.body.pos = (0, 0)
    av.body.reach = Reach.CLOSE
    print("Pick after move:", ri.pick((1, 0)))
    print("Status:", ri.status())

    # Stow to inventory
    print("Stow:", ri.stow())
    print("Status after stow:", ri.status())

    # Draw and place elsewhere
    ri.draw(0)
    print("Place at (0,1):", ri.place((0, 1)))
    print("Grid (0,1):", grid.get(0, 1).content)
    print("Final status:", ri.status())

if __name__ == "__main__":
    demo()
