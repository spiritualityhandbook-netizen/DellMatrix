#!/usr/bin/env python3
"""
08_FACE_STATE_CYCLES.py
Code Phase 3 · Artifact 8
Status: TRUE
Offline · Zero dependencies · Stdlib only

Grows the living structure:
- Extends ExpressionField (Artifact 7)
- Attaches cleanly to Avatar (Artifact 6)
- Prepares for later ASCII animation player

Face-state cycles are still static frames for now.
True timed animation belongs to the ASCII player cell.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import prior True artifacts (same directory)
try:
    from expression_field import Expression, ExpressionField, EXPRESSION_MAP
except ImportError:
    # fallback definitions if run standalone
    class Expression(Enum):
        NEUTRAL = "neutral"
        FOCUS = "focus"
        JOY = "joy"
        CALM = "calm"
        INTENSE = "intense"
        CURIOUS = "curious"
        RESOLUTE = "resolute"
        SOFT = "soft"
    EXPRESSION_MAP = {}
    class ExpressionField:
        def __init__(self):
            self.current = Expression.NEUTRAL
        def set(self, expr):
            self.current = expr
        def get(self):
            return {"expression": self.current.value, "kaomoji": "(·_·)"}
        def as_show(self):
            return self.get().get("kaomoji", "(·_·)")

class CycleMode(Enum):
    HOLD = "hold"          # single expression
    PULSE = "pulse"        # alternate two frames
    SEQUENCE = "sequence"  # walk a list of expressions

@dataclass
class FaceCycle:
    """
    A named cycle of face states.
    Still offline and static — the ASCII player will later advance frames.
    """
    name: str
    frames: List[Expression]
    mode: CycleMode = CycleMode.SEQUENCE
    current_index: int = 0

    def current(self) -> Expression:
        if not self.frames:
            return Expression.NEUTRAL
        return self.frames[self.current_index % len(self.frames)]

    def advance(self) -> Expression:
        if self.mode == CycleMode.HOLD or len(self.frames) <= 1:
            return self.current()
        self.current_index = (self.current_index + 1) % len(self.frames)
        return self.current()

    def reset(self) -> None:
        self.current_index = 0

@dataclass
class FaceStateController:
    """
    Grows ExpressionField into a cycle-aware controller
    that can be attached to an Avatar.
    """
    field: ExpressionField = field(default_factory=ExpressionField)
    active_cycle: Optional[FaceCycle] = None
    cycles: Dict[str, FaceCycle] = field(default_factory=dict)

    def register(self, cycle: FaceCycle) -> None:
        self.cycles[cycle.name] = cycle

    def set_cycle(self, name: str) -> bool:
        if name not in self.cycles:
            return False
        self.active_cycle = self.cycles[name]
        self.active_cycle.reset()
        self.field.set(self.active_cycle.current())
        return True

    def hold(self, expr: Expression) -> None:
        self.active_cycle = None
        self.field.set(expr)

    def tick(self) -> Dict[str, Any]:
        """Advance the active cycle one frame (or hold). Returns current show data."""
        if self.active_cycle:
            expr = self.active_cycle.advance()
            self.field.set(expr)
        return self.field.get()

    def show(self) -> str:
        return self.field.as_show()

# Default cycles that grow the structure immediately
DEFAULT_CYCLES = [
    FaceCycle("idle", [Expression.NEUTRAL, Expression.SOFT], CycleMode.PULSE),
    FaceCycle("focus_pulse", [Expression.FOCUS, Expression.NEUTRAL], CycleMode.PULSE),
    FaceCycle("joy_seq", [Expression.SOFT, Expression.JOY, Expression.SOFT], CycleMode.SEQUENCE),
    FaceCycle("resolute", [Expression.RESOLUTE], CycleMode.HOLD),
]

def build_default_controller() -> FaceStateController:
    ctrl = FaceStateController()
    for c in DEFAULT_CYCLES:
        ctrl.register(c)
    ctrl.set_cycle("idle")
    return ctrl

def demo():
    ctrl = build_default_controller()
    print("Idle cycle:")
    for _ in range(4):
        print(" ", ctrl.tick()["expression"], ctrl.show())
    ctrl.set_cycle("joy_seq")
    print("Joy sequence:")
    for _ in range(4):
        print(" ", ctrl.tick()["expression"], ctrl.show())

if __name__ == "__main__":
    demo()
