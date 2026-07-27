#!/usr/bin/env python3
"""
15_INTEGRATOR.py
Code Phase 3 · Artifact 15
Status: TRUE
Offline · Zero dependencies · Stdlib only

Unified runner that wires prior True artifacts into one steppable system.
Addresses P0 from SUS audit:
- Single entry point
- Intent bridge (Thinks → Reach / Anim)
- Live GodWorkSpace tick

This file embeds minimal compatible stand-ins so it runs standalone.
When the package import path is stable, stand-ins can be replaced by
real imports of 05–14 without changing the public API.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import time

Coord = Tuple[int, int]

# =============================================================================
# Minimal compatible cores (stand-ins for 05–14)
# =============================================================================

class Facing(Enum):
    N, NE, E, SE, S, SW, W, NW = range(8)
    @property
    def delta(self) -> Coord:
        return [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)][self.value]
    @property
    def name(self) -> str:
        return ["N","NE","E","SE","S","SW","W","NW"][self.value]

class Reach(Enum):
    CLOSE = 1
    AWAY = 2
    FAR = 3

class Intent(Enum):
    IDLE = auto()
    MOVE = auto()
    TURN = auto()
    PICK = auto()
    PLACE = auto()
    STOW = auto()
    DRAW = auto()
    EXPRESS = auto()
    NOTE = auto()

@dataclass
class Body:
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    reach: Reach = Reach.CLOSE
    holding: Any = None

@dataclass
class Avatar:
    body: Body = field(default_factory=Body)
    name: str = "Avatar"
    def read_body(self) -> Body:
        return Body(pos=self.body.pos, facing=self.body.facing,
                    reach=self.body.reach, holding=self.body.holding)
    def step(self, n: int = 1) -> Coord:
        dx, dy = self.body.facing.delta
        x, y = self.body.pos
        self.body.pos = (x + dx * n, y + dy * n)
        return self.body.pos
    def turn(self, n: int = 1) -> Facing:
        idx = (list(Facing).index(self.body.facing) + n) % 8
        self.body.facing = list(Facing)[idx]
        return self.body.facing

@dataclass
class Cell:
    x: int
    y: int
    content: Any = None

class Grid:
    def __init__(self):
        self._cells: Dict[Coord, Cell] = {}
    def get(self, x: int, y: int) -> Cell:
        k = (x, y)
        if k not in self._cells:
            self._cells[k] = Cell(x, y)
        return self._cells[k]
    def set(self, x: int, y: int, content: Any = None) -> Cell:
        c = self.get(x, y)
        c.content = content
        return c
    def clear(self, x: int, y: int) -> None:
        k = (x, y)
        if k in self._cells:
            del self._cells[k]

@dataclass
class Inventory:
    slots: List[Any] = field(default_factory=lambda: [None, None, None])
    def add(self, item: Any) -> bool:
        for i, s in enumerate(self.slots):
            if s is None:
                self.slots[i] = item
                return True
        return False
    def remove(self, i: int = 0) -> Any:
        if 0 <= i < len(self.slots):
            item = self.slots[i]
            self.slots[i] = None
            return item
        return None
    def list_items(self) -> List[Any]:
        return [s for s in self.slots if s is not None]

class ReachInventory:
    def __init__(self, avatar: Avatar, grid: Grid):
        self.avatar = avatar
        self.grid = grid
        self.inventory = Inventory()
    def _dist(self, a: Coord, b: Coord) -> int:
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def can_reach(self, target: Coord) -> bool:
        return self._dist(self.avatar.body.pos, target) <= self.avatar.body.reach.value
    def pick(self, target: Coord) -> bool:
        b = self.avatar.body
        if b.holding is not None or not self.can_reach(target):
            return False
        cell = self.grid.get(*target)
        if cell.content is None:
            return False
        b.holding = cell.content
        self.grid.clear(*target)
        return True
    def place(self, target: Coord) -> bool:
        b = self.avatar.body
        if b.holding is None or not self.can_reach(target):
            return False
        cell = self.grid.get(*target)
        if cell.content is not None:
            return False
        self.grid.set(*target, content=b.holding)
        b.holding = None
        return True
    def stow(self) -> bool:
        b = self.avatar.body
        if b.holding is None:
            return False
        if self.inventory.add(b.holding):
            b.holding = None
            return True
        return False
    def draw(self, i: int = 0) -> bool:
        b = self.avatar.body
        if b.holding is not None:
            return False
        item = self.inventory.remove(i)
        if item is None:
            return False
        b.holding = item
        return True

@dataclass
class Anim:
    id: str
    frames: List[str]
    index: int = 0
    loop: bool = True
    def current(self) -> str:
        if not self.frames:
            return "(·_·)"
        return self.frames[self.index % len(self.frames)]
    def advance(self) -> str:
        if self.frames and (self.loop or self.index < len(self.frames)-1):
            self.index = (self.index + 1) % len(self.frames)
        return self.current()

class AsciiPlayer:
    def __init__(self):
        self.anims: Dict[str, Anim] = {}
        self.active: Optional[str] = None
        self.register(Anim("idle", ["(·_·)", "(·-·)", "(·_·)", "(·o·)"]))
        self.register(Anim("sparkle", ["✧", "✦", "★", "☆"], loop=False))
        self.register(Anim("joy", ["(^_^)", "(◕‿◕)", "(^∇^)"]))
        self.set_active("idle")
    def register(self, anim: Anim) -> None:
        self.anims[anim.id] = anim
    def set_active(self, aid: str) -> bool:
        if aid not in self.anims:
            return False
        self.active = aid
        self.anims[aid].index = 0
        return True
    def tick(self) -> str:
        if not self.active:
            return "(·_·)"
        return self.anims[self.active].advance()
    def show(self) -> str:
        if not self.active:
            return "(·_·)"
        return self.anims[self.active].current()

@dataclass
class Thought:
    content: str
    intent: Optional[Intent] = None
    payload: Dict[str, Any] = field(default_factory=dict)

class Thinks:
    def __init__(self):
        self.queue: List[Thought] = []
        self.notes: List[str] = []
        self.last_body: Optional[Body] = None
    def observe(self, avatar: Avatar) -> Body:
        self.last_body = avatar.read_body()
        return self.last_body
    def think(self, content: str, intent: Optional[Intent] = None, **payload) -> Thought:
        if self.last_body is None:
            content = f"[no body] {content}"
        t = Thought(content=content, intent=intent, payload=payload)
        self.queue.append(t)
        if intent is None:
            self.notes.append(content)
        return t
    def next_intent(self) -> Optional[Thought]:
        for i, t in enumerate(self.queue):
            if t.intent is not None:
                return self.queue.pop(i)
        return None

class GodWorkSpace:
    def __init__(self):
        self.temp = "W"
        self.seed_strip = ""
        self.messages: List[str] = []
        self.avatar_status: Dict[str, Any] = {}
        self.frame = "(·_·)"
        self.holding: Any = None
        self.inventory: List[Any] = []
    def log(self, msg: str) -> None:
        self.messages.append(msg)
        self.messages = self.messages[-12:]
    def render(self) -> str:
        lines = [
            f"┌─ GodWorkSpace ─ Temp:{self.temp} ─┐",
            f"│ Avatar : {self.avatar_status}",
            f"│ Frame  : {self.frame}",
            f"│ Hand   : {self.holding}",
            f"│ Inv    : {self.inventory}",
            f"│ SEED   : {self.seed_strip or '(none)'}",
            f"│ LOG    : {self.messages[-3:] if self.messages else '—'}",
            "└" + "─"*36 + "┘",
        ]
        return "\n".join(lines)

class TokenWorkMem:
    def __init__(self, limit: int = 4096):
        self.limit = limit
        self.used = 0
        self.runs: List[str] = []
        self.fails: List[str] = []
    def estimate(self, text: str) -> int:
        return max(1, len(text)//4)
    def charge(self, text: str) -> bool:
        c = self.estimate(text)
        if self.used + c > self.limit:
            return False
        self.used += c
        return True
    def record_run(self, msg: str) -> None:
        self.runs.append(msg)
    def record_fail(self, msg: str) -> None:
        self.fails.append(msg)

# =============================================================================
# Integrator
# =============================================================================

@dataclass
class Integrator:
    """
    Single offline steppable system.
    Public API:
      boot()     — place demo world items, set seed strip
      tick()     — advance anim, process one Thinks intent, refresh GWS
      command()  — inject a high-level intent from outside
      render()   — GodWorkSpace text pane
      status()   — machine-readable snapshot
    """
    grid: Grid = field(default_factory=Grid)
    avatar: Avatar = field(default_factory=Avatar)
    reach: Optional[ReachInventory] = None
    anim: AsciiPlayer = field(default_factory=AsciiPlayer)
    thinks: Thinks = field(default_factory=Thinks)
    gws: GodWorkSpace = field(default_factory=GodWorkSpace)
    mem: TokenWorkMem = field(default_factory=TokenWorkMem)
    ticks: int = 0

    def __post_init__(self):
        self.reach = ReachInventory(self.avatar, self.grid)

    def boot(self) -> None:
        """Seed a tiny demo world."""
        self.grid.set(1, 0, content={"kind": "tool", "name": "wrench"})
        self.grid.set(0, 1, content={"kind": "note", "name": "seed-card"})
        self.gws.seed_strip = "08[Create] >> 14[Bind] :: integrator"
        self.gws.temp = "W"
        self.thinks.observe(self.avatar)
        self.mem.record_run("Integrator boot")
        self.gws.log("boot")
        self._sync_gws()

    def _sync_gws(self) -> None:
        b = self.avatar.read_body()
        self.gws.avatar_status = {
            "pos": b.pos,
            "facing": b.facing.name,
            "reach": b.reach.name,
        }
        self.gws.frame = self.anim.show()
        self.gws.holding = b.holding
        self.gws.inventory = self.reach.inventory.list_items() if self.reach else []

    def _execute(self, thought: Thought) -> bool:
        """Intent bridge: Thinks → body / reach / anim."""
        intent = thought.intent
        p = thought.payload
        if intent is None:
            return False

        if intent == Intent.MOVE:
            self.avatar.step(int(p.get("steps", 1)))
            self.anim.set_active("idle")
            return True

        if intent == Intent.TURN:
            self.avatar.turn(int(p.get("steps", 1)))
            return True

        if intent == Intent.PICK:
            target = tuple(p.get("target", (1, 0)))  # type: ignore
            ok = self.reach.pick(target) if self.reach else False
            if ok:
                self.anim.set_active("sparkle")
            return ok

        if intent == Intent.PLACE:
            target = tuple(p.get("target", (0, 1)))  # type: ignore
            return self.reach.place(target) if self.reach else False

        if intent == Intent.STOW:
            return self.reach.stow() if self.reach else False

        if intent == Intent.DRAW:
            return self.reach.draw(int(p.get("slot", 0))) if self.reach else False

        if intent == Intent.EXPRESS:
            name = p.get("anim", "joy")
            return self.anim.set_active(str(name))

        if intent == Intent.NOTE:
            self.gws.log(thought.content)
            return True

        return False

    def command(self, content: str, intent: Optional[Intent] = None, **payload) -> None:
        """External injection into Thinks (after observe)."""
        self.thinks.observe(self.avatar)
        self.thinks.think(content, intent=intent, **payload)

    def tick(self) -> str:
        """One system step."""
        self.ticks += 1
        self.thinks.observe(self.avatar)

        # Process at most one intent per tick
        thought = self.thinks.next_intent()
        if thought:
            ok = self._execute(thought)
            msg = f"{thought.intent.name if thought.intent else 'NOTE'}:{'ok' if ok else 'fail'}"
            self.gws.log(msg)
            if ok:
                self.mem.record_run(msg)
            else:
                self.mem.record_fail(msg)

        # Advance animation
        frame = self.anim.tick()
        self.gws.frame = frame

        self._sync_gws()
        return self.render()

    def render(self) -> str:
        return self.gws.render()

    def status(self) -> Dict[str, Any]:
        b = self.avatar.read_body()
        return {
            "ticks": self.ticks,
            "pos": b.pos,
            "facing": b.facing.name,
            "holding": b.holding,
            "inventory": self.reach.inventory.list_items() if self.reach else [],
            "frame": self.anim.show(),
            "thinks_queue": len(self.thinks.queue),
            "mem_runs": len(self.mem.runs),
            "mem_fails": len(self.mem.fails),
            "budget_used": self.mem.used,
        }

# =============================================================================
# Demo — proves end-to-end function
# =============================================================================

def demo():
    sys = Integrator()
    sys.boot()
    print(sys.render())
    print()

    # Scripted scenario: pick wrench, stow, express joy, step
    sys.command("Pick the wrench", intent=Intent.PICK, target=(1, 0))
    print(sys.tick())
    print()

    sys.command("Stow it", intent=Intent.STOW)
    print(sys.tick())
    print()

    sys.command("Show joy", intent=Intent.EXPRESS, anim="joy")
    print(sys.tick())
    print()

    sys.command("Step forward", intent=Intent.MOVE, steps=1)
    print(sys.tick())
    print()

    print("STATUS:", sys.status())

if __name__ == "__main__":
    demo()
