#!/usr/bin/env python3
"""
AI Companion — first-class entity on Program (persistable).

Local only. Modes: manual · wander · follow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import random

_FACING_DELTA = {
    "N": (0, 1), "NE": (1, 1), "E": (1, 0), "SE": (1, -1),
    "S": (0, -1), "SW": (-1, -1), "W": (-1, 0), "NW": (-1, 1),
}
_FACING_ORDER = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
_MAX_TRAIL = 16


@dataclass
class AICompanion:
    name: str = "AI"
    label: str = "AI"
    pos: List[float] = field(default_factory=lambda: [2.0, 1.0])
    facing: str = "N"
    mode: str = "manual"  # manual | wander | follow
    doing: str = "idle"
    last_action: str = "spawned"
    trail: List[List[float]] = field(default_factory=list)

    def _push_trail(self) -> None:
        pt = [float(self.pos[0]), float(self.pos[1])]
        if self.trail:
            lx, ly = self.trail[-1]
            if abs(lx - pt[0]) < 0.01 and abs(ly - pt[1]) < 0.01:
                return
        self.trail.append(pt)
        while len(self.trail) > _MAX_TRAIL:
            self.trail.pop(0)

    def step(self, steps: int = 1) -> Tuple[float, float]:
        dx, dy = _FACING_DELTA.get(self.facing, (0, 1))
        self.pos[0] = float(self.pos[0]) + dx * steps
        self.pos[1] = float(self.pos[1]) + dy * steps
        self.doing = "walking"
        self.last_action = f"walked to ({self.pos[0]:.0f},{self.pos[1]:.0f})"
        self._push_trail()
        return float(self.pos[0]), float(self.pos[1])

    def backstep(self, steps: int = 1) -> Tuple[float, float]:
        dx, dy = _FACING_DELTA.get(self.facing, (0, 1))
        self.pos[0] = float(self.pos[0]) - dx * steps
        self.pos[1] = float(self.pos[1]) - dy * steps
        self.doing = "backstep"
        self.last_action = f"backstep ({self.pos[0]:.0f},{self.pos[1]:.0f})"
        self._push_trail()
        return float(self.pos[0]), float(self.pos[1])

    def turn(self, steps: int = 1) -> str:
        idx = _FACING_ORDER.index(self.facing) if self.facing in _FACING_ORDER else 0
        self.facing = _FACING_ORDER[(idx + steps) % 8]
        self.doing = "turning"
        self.last_action = f"turned to {self.facing}"
        return self.facing

    def face(self, direction: str) -> str:
        d = direction.upper()
        if d not in _FACING_DELTA:
            return self.facing
        self.facing = d
        self.doing = "looking"
        self.last_action = f"faced {d}"
        return self.facing

    def goto(self, x: float, y: float) -> Tuple[float, float]:
        self.pos = [float(x), float(y)]
        self.doing = "moved"
        self.last_action = f"goto ({x},{y})"
        self._push_trail()
        return float(self.pos[0]), float(self.pos[1])

    def set_mode(self, mode: str) -> str:
        m = (mode or "manual").lower()
        if m not in ("manual", "wander", "follow"):
            m = "manual"
        self.mode = m
        if m == "manual":
            self.doing = "idle"
        self.last_action = f"mode → {m}"
        return self.mode

    def tick(self, user_pos: Optional[List[float]] = None) -> None:
        if self.mode == "wander":
            if random.random() < 0.35:
                self.turn(1 if random.random() < 0.5 else -1)
            self.step(1)
            self.doing = "wandering"
        elif self.mode == "follow" and user_pos:
            ux, uy = float(user_pos[0]), float(user_pos[1])
            ax, ay = float(self.pos[0]), float(self.pos[1])
            dx, dy = ux - ax, uy - ay
            dist = math.hypot(dx, dy)
            if dist > 1.2:
                ang = math.degrees(math.atan2(dy, dx)) % 360
                best, best_d = "E", 999.0
                for name, (fx, fy) in _FACING_DELTA.items():
                    fa = math.degrees(math.atan2(fy, fx)) % 360
                    d = min(abs(fa - ang) % 360, 360 - abs(fa - ang) % 360)
                    if d < best_d:
                        best_d, best = d, name
                self.facing = best
                self.step(1)
                self.doing = "following"
                self.last_action = f"follow → ({self.pos[0]:.0f},{self.pos[1]:.0f})"
            else:
                self.doing = "near user"
                self.last_action = "holding near"

    def z(self) -> float:
        return round(math.hypot(float(self.pos[0]), float(self.pos[1])) * 0.15, 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "pos": [float(self.pos[0]), float(self.pos[1])],
            "facing": self.facing,
            "mode": self.mode,
            "doing": self.doing,
            "last_action": self.last_action,
            "trail": [list(p) for p in self.trail[-_MAX_TRAIL:]],
            "z": self.z(),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AICompanion":
        if not data:
            return cls()
        c = cls(
            name=str(data.get("name") or "AI"),
            label=str(data.get("label") or data.get("name") or "AI"),
            pos=[float((data.get("pos") or [2, 1])[0]), float((data.get("pos") or [2, 1])[1])],
            facing=str(data.get("facing") or "N"),
            mode=str(data.get("mode") or "manual"),
            doing=str(data.get("doing") or "idle"),
            last_action=str(data.get("last_action") or "loaded"),
        )
        trail = data.get("trail") or []
        c.trail = [[float(p[0]), float(p[1])] for p in trail if isinstance(p, (list, tuple)) and len(p) >= 2]
        return c


def smoke() -> bool:
    print("=== COMPANION SMOKE ===")
    c = AICompanion()
    c.step(1)
    c.set_mode("follow")
    c.tick([0, 0])
    d = c.to_dict()
    c2 = AICompanion.from_dict(d)
    ok = c2.name == "AI" and len(c2.trail) >= 1
    print(f"[{'PASS' if ok else 'FAIL'}] serialize roundtrip")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
