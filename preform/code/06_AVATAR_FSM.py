#!/usr/bin/env python3
"""
06_AVATAR_FSM.py
Code Phase 2 · Artifact 6
Status: TRUE
Offline · Zero dependencies · Stdlib only

Minimal Avatar finite-state machine.
Body-first law: body tick is stable; mind is async and always reads real body state.
Lives on the Grid from 05_GRID.py.
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Tuple, Optional, Dict, Any, List
from dataclasses import dataclass, field

Coord = Tuple[int, int]

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

class Posture(Enum):
    STAND = auto()
    SIT   = auto()
    BEND  = auto()
    JUMP  = auto()   # transient

class Locomotion(Enum):
    IDLE = auto()
    WALK = auto()
    JOG  = auto()
    RUN  = auto()

class Reach(Enum):
    CLOSE = 1
    AWAY  = 2
    FAR   = 3

@dataclass
class BodyState:
    """Stable body state. Mind always reads this."""
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    posture: Posture = Posture.STAND
    locomotion: Locomotion = Locomotion.IDLE
    reach: Reach = Reach.CLOSE
    holding: Optional[Any] = None          # what is currently picked up

@dataclass
class Avatar:
    """
    Body-first Avatar.
    All movement and posture changes go through body methods.
    Mind layer (later) may only read body.state and issue high-level intents.
    """
    body: BodyState = field(default_factory=BodyState)
    name: str = "Avatar"

    # ----- body primitives (stable tick) -----

    def face(self, direction: Facing) -> None:
        self.body.facing = direction

    def set_posture(self, posture: Posture) -> None:
        # simple legality: cannot walk while sitting, etc.
        if posture == Posture.SIT and self.body.locomotion != Locomotion.IDLE:
            self.body.locomotion = Locomotion.IDLE
        self.body.posture = posture

    def set_locomotion(self, loco: Locomotion) -> None:
        if self.body.posture in (Posture.SIT, Posture.BEND):
            # must stand first
            self.body.posture = Posture.STAND
        self.body.locomotion = loco

    def step(self, steps: int = 1) -> Coord:
        """Move forward in current facing. Returns new position."""
        if self.body.locomotion == Locomotion.IDLE:
            self.body.locomotion = Locomotion.WALK
        dx, dy = self.body.facing.delta
        x, y = self.body.pos
        self.body.pos = (x + dx * steps, y + dy * steps)
        return self.body.pos

    def turn(self, steps: int = 1) -> Facing:
        """Rotate facing by 45° steps (positive = clockwise)."""
        order = list(Facing)
        idx = order.index(self.body.facing)
        new_idx = (idx + steps) % 8
        self.body.facing = order[new_idx]
        return self.body.facing

    def pick_up(self, item: Any) -> bool:
        if self.body.holding is not None:
            return False
        self.body.holding = item
        return True

    def place_down(self) -> Optional[Any]:
        item = self.body.holding
        self.body.holding = None
        return item

    def set_reach(self, tier: Reach) -> None:
        self.body.reach = tier

    # ----- read-only for mind -----

    def read_body(self) -> BodyState:
        """Mind always reads real body state. Returns a snapshot."""
        return BodyState(
            pos=self.body.pos,
            facing=self.body.facing,
            posture=self.body.posture,
            locomotion=self.body.locomotion,
            reach=self.body.reach,
            holding=self.body.holding,
        )

    def status(self) -> Dict[str, Any]:
        b = self.body
        return {
            "name": self.name,
            "pos": b.pos,
            "facing": b.facing.name,
            "posture": b.posture.name,
            "locomotion": b.locomotion.name,
            "reach": b.reach.name,
            "holding": b.holding is not None,
        }


def demo():
    av = Avatar(name="Test")
    print("Initial:", av.status())
    av.set_locomotion(Locomotion.WALK)
    av.step(2)
    av.turn(2)          # face east
    av.step(1)
    av.set_posture(Posture.SIT)
    print("After moves:", av.status())
    print("Mind reads:", av.read_body())

if __name__ == "__main__":
    demo()
