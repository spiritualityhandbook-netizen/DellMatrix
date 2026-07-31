#!/usr/bin/env python3
"""
Avatar body FSM.
Law: Body first. Thinks second. Thinks always reads real body state.
"""

from __future__ import annotations
from enum import Enum, auto
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass, field

Coord = Tuple[int, int]


class Facing(Enum):
    N = (0, 1)
    NE = (1, 1)
    E = (1, 0)
    SE = (1, -1)
    S = (0, -1)
    SW = (-1, -1)
    W = (-1, 0)
    NW = (-1, 1)

    @property
    def delta(self) -> Coord:
        return self.value


class Posture(Enum):
    STAND = auto()
    SIT = auto()
    BEND = auto()
    JUMP = auto()


class Locomotion(Enum):
    IDLE = auto()
    WALK = auto()
    JOG = auto()
    RUN = auto()


class Reach(Enum):
    CLOSE = 1
    AWAY = 2
    FAR = 3


@dataclass
class BodyState:
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    posture: Posture = Posture.STAND
    locomotion: Locomotion = Locomotion.IDLE
    reach: Reach = Reach.CLOSE
    holding: Optional[str] = None


@dataclass
class Avatar:
    """Body-first Avatar. All movement goes through body methods."""
    name: str = "Avatar"
    body: BodyState = field(default_factory=BodyState)

    def face(self, direction: Facing) -> None:
        self.body.facing = direction

    def set_posture(self, posture: Posture) -> str:
        if posture == Posture.SIT and self.body.locomotion != Locomotion.IDLE:
            self.body.locomotion = Locomotion.IDLE
        self.body.posture = posture
        return posture.name.lower()

    def set_locomotion(self, loco: Locomotion) -> str:
        if self.body.posture in (Posture.SIT, Posture.BEND):
            self.body.posture = Posture.STAND
        self.body.locomotion = loco
        return loco.name.lower()

    def step(self, steps: int = 1) -> Coord:
        if self.body.locomotion == Locomotion.IDLE:
            self.body.locomotion = Locomotion.WALK
        dx, dy = self.body.facing.delta
        x, y = self.body.pos
        self.body.pos = (x + dx * steps, y + dy * steps)
        return self.body.pos

    def turn(self, steps: int = 1) -> str:
        """Positive = clockwise."""
        order = list(Facing)
        idx = order.index(self.body.facing)
        self.body.facing = order[(idx + steps) % 8]
        return self.body.facing.name

    def turn_left(self, steps: int = 1) -> str:
        return self.turn(-steps)

    def turn_right(self, steps: int = 1) -> str:
        return self.turn(steps)

    def pick_up(self, item: str) -> bool:
        if self.body.holding is not None:
            return False
        self.body.holding = item
        return True

    def place_down(self) -> Optional[str]:
        item = self.body.holding
        self.body.holding = None
        return item

    def set_reach(self, tier: Reach) -> str:
        self.body.reach = tier
        return tier.name.lower()

    def read_body(self) -> BodyState:
        """Mind always reads real body state."""
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
            "posture": b.posture.name.lower(),
            "locomotion": b.locomotion.name.lower(),
            "reach": b.reach.name.lower(),
            "holding": b.holding,
        }

    def describe(self) -> str:
        b = self.body
        hold = f", holding {b.holding}" if b.holding else ""
        return (
            f"{self.name} is at {b.pos}, facing {b.facing.name}, "
            f"{b.posture.name.lower()}, {b.locomotion.name.lower()}{hold}"
        )
