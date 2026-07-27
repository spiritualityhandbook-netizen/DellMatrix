#!/usr/bin/env python3
"""
07_EXPRESSION_FIELD.py
Code Phase 2 · Artifact 7
Status: TRUE
Offline · Zero dependencies · Stdlib only

Static expression field for Avatar face-state / tone / kaomoji.
Maps into Dell 05 (Tone) and Dell 09 (Show).
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

class Expression(Enum):
    NEUTRAL   = "neutral"
    FOCUS     = "focus"
    JOY       = "joy"
    CALM      = "calm"
    INTENSE   = "intense"
    CURIOUS   = "curious"
    RESOLUTE  = "resolute"
    SOFT      = "soft"

# Minimal static kaomoji / face map (Tone + Show)
EXPRESSION_MAP: Dict[Expression, Dict[str, str]] = {
    Expression.NEUTRAL:  {"kaomoji": "(·_·)",   "tone": "neutral",  "show": "face"},
    Expression.FOCUS:    {"kaomoji": "(｀_´)",   "tone": "focus",    "show": "face"},
    Expression.JOY:      {"kaomoji": "(◕‿◕)",   "tone": "joy",      "show": "face"},
    Expression.CALM:     {"kaomoji": "(￣ー￣)", "tone": "calm",     "show": "face"},
    Expression.INTENSE:  {"kaomoji": "(╬ Ò ‸ Ó)", "tone": "intense", "show": "face"},
    Expression.CURIOUS:  {"kaomoji": "(◎_◎)",   "tone": "curious",  "show": "face"},
    Expression.RESOLUTE: {"kaomoji": "(•̀ᴗ•́)و", "tone": "resolute", "show": "face"},
    Expression.SOFT:     {"kaomoji": "(◕ᴗ◕✿)",  "tone": "soft",     "show": "face"},
}

@dataclass
class ExpressionField:
    """Static expression state that can attach to an Avatar."""
    current: Expression = Expression.NEUTRAL
    custom: Dict[str, str] = field(default_factory=dict)

    def set(self, expr: Expression) -> None:
        self.current = expr

    def get(self) -> Dict[str, Any]:
        base = EXPRESSION_MAP.get(self.current, EXPRESSION_MAP[Expression.NEUTRAL]).copy()
        base.update(self.custom)
        base["expression"] = self.current.value
        return base

    def as_show(self) -> str:
        """Return the display string (kaomoji or custom)."""
        data = self.get()
        return data.get("kaomoji", "(·_·)")

    def as_tone(self) -> str:
        return self.get().get("tone", "neutral")

def demo():
    ef = ExpressionField()
    print("Default:", ef.get())
    ef.set(Expression.FOCUS)
    print("Focus:", ef.as_show(), "|", ef.as_tone())
    ef.set(Expression.JOY)
    print("Joy:", ef.as_show())

if __name__ == "__main__":
    demo()
