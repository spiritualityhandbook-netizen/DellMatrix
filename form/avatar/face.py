#!/usr/bin/env python3
"""Face state + expression cycles for Avatar."""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field


class Expression(Enum):
    NEUTRAL = "neutral"
    FOCUS = "focus"
    JOY = "joy"
    CALM = "calm"
    INTENSE = "intense"
    CURIOUS = "curious"
    RESOLUTE = "resolute"
    SOFT = "soft"


# Simple default faces (kaomoji can override)
DEFAULT_FACE = {
    Expression.NEUTRAL: "(·_·)",
    Expression.FOCUS: "(・_・)",
    Expression.JOY: "(^_^)",
    Expression.CALM: "(˘_˘)",
    Expression.INTENSE: "(¬_¬)",
    Expression.CURIOUS: "(o_o)",
    Expression.RESOLUTE: "(•̀_•́)",
    Expression.SOFT: "(◕‿◕)",
}


@dataclass
class FaceController:
    current: Expression = Expression.NEUTRAL
    custom_face: Optional[str] = None

    def set(self, expr: Expression) -> str:
        self.current = expr
        self.custom_face = None
        return self.show()

    def set_raw(self, face: str) -> str:
        self.custom_face = face
        return face

    def show(self) -> str:
        if self.custom_face:
            return self.custom_face
        return DEFAULT_FACE.get(self.current, "(·_·)")

    def status(self) -> Dict:
        return {"expression": self.current.value, "face": self.show()}
