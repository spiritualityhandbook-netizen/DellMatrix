#!/usr/bin/env python3
"""
09_KAOMOJI_PACKS.py
Code Phase 3 · Artifact 9
Status: TRUE
Offline · Zero dependencies · Stdlib only

Grows the living structure:
- Extends ExpressionField (Artifact 7)
- Compatible with FaceStateController (Artifact 8)
- Data packs from page 09 Expression / Kaomoji categories
- Ready for later ASCII animation player (Artifact 10)

Packs are optional expression tokens under Dell 05 Tone and 09 Show.
They are NOT new Dells.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# ---------- Minimal prior-artifact fallbacks (so this file runs standalone) ----------
class Expression(Enum):
    NEUTRAL   = "neutral"
    FOCUS     = "focus"
    JOY       = "joy"
    CALM      = "calm"
    INTENSE   = "intense"
    CURIOUS   = "curious"
    RESOLUTE  = "resolute"
    SOFT      = "soft"

# ---------- Pack data (from page 09 living form) ----------

KAOMOJI_PACKS: Dict[str, List[str]] = {
    "classic": [
        ":-)", ":^)", "^_^", "(^^)", ";-)", "8-)", "B-)", ":D", ";P"
    ],
    "smiling": [
        "(^_^)", "(^∇^)", "◎_◎", "(∗‿∗)", "(◕‿◕)", "(￣▽￣)"
    ],
    "love": [
        "(♥ω♥)", "(✿♥‿♥)", "(♡‿♡)", "(´∀｀)♡"
    ],
    "hugging": [
        "(つ≧▽≦)つ", "(づ｡◕‿‿◕｡)づ", "⊂(・▽・⊂)"
    ],
    "flexing": [
        "ᕦ(ò_óˇ)ᕤ", "(ง'̀-'́)ง", "ᕙ(⇀‸↼‶)ᕗ"
    ],
    "pointing": [
        "→_→", "←_←", "(→_→)", "(←_←)"
    ],
    "sparkling": [
        "✧", "✦", "★", "☆", "✧(≖ ◡ ≖)", "✦(◕‿◕)✦"
    ],
    "worrying": [
        "(;_;)", "(⊙_⊙)", "(；一_一)", "(´；ω；`)"
    ],
    "disapproving": [
        "ಠ_ಠ", "ಠ⌣ಠ", "(¬_¬)", "(ー_ー;)"
    ],
    "crying": [
        "(T_T)", "(´；ω；`)", "(;﹏;)", "(ಥ﹏ಥ)"
    ],
    # Table Flipping is gated (harsh). Include but mark optional.
    "table_flipping": [
        "(╯°□°)╯︵ ┻━┻", "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻"
    ],
}

# Map packs → nearest Expression enum for FaceStateController compatibility
PACK_TO_EXPRESSION: Dict[str, Expression] = {
    "classic": Expression.NEUTRAL,
    "smiling": Expression.JOY,
    "love": Expression.SOFT,
    "hugging": Expression.SOFT,
    "flexing": Expression.RESOLUTE,
    "pointing": Expression.FOCUS,
    "sparkling": Expression.JOY,
    "worrying": Expression.CURIOUS,
    "disapproving": Expression.INTENSE,
    "crying": Expression.SOFT,
    "table_flipping": Expression.INTENSE,
}

# ---------- Loader / Registry ----------

@dataclass
class KaomojiPack:
    name: str
    tokens: List[str]
    default_expression: Expression = Expression.NEUTRAL
    gated: bool = False  # True for harsh packs

    def sample(self, index: int = 0) -> str:
        if not self.tokens:
            return "(·_·)"
        return self.tokens[index % len(self.tokens)]

    def as_list(self) -> List[str]:
        return list(self.tokens)

@dataclass
class KaomojiRegistry:
    """
    Expandable registry of packs.
    Grows ExpressionField by allowing pack-based face selection.
    Compatible with FaceStateController (Artifact 8).
    """
    packs: Dict[str, KaomojiPack] = field(default_factory=dict)
    active_pack: Optional[str] = None
    active_index: int = 0
    allow_gated: bool = False  # Surgical / harsh mode

    def load_defaults(self) -> None:
        for name, tokens in KAOMOJI_PACKS.items():
            gated = name == "table_flipping"
            expr = PACK_TO_EXPRESSION.get(name, Expression.NEUTRAL)
            self.packs[name] = KaomojiPack(
                name=name,
                tokens=tokens,
                default_expression=expr,
                gated=gated,
            )

    def register(self, pack: KaomojiPack) -> None:
        """Add or replace a pack (personal matrix / custom)."""
        self.packs[pack.name] = pack

    def set_pack(self, name: str) -> bool:
        if name not in self.packs:
            return False
        pack = self.packs[name]
        if pack.gated and not self.allow_gated:
            return False
        self.active_pack = name
        self.active_index = 0
        return True

    def current(self) -> str:
        if not self.active_pack or self.active_pack not in self.packs:
            return "(·_·)"
        return self.packs[self.active_pack].sample(self.active_index)

    def advance(self) -> str:
        """Cycle to next token in active pack."""
        if not self.active_pack or self.active_pack not in self.packs:
            return "(·_·)"
        pack = self.packs[self.active_pack]
        self.active_index = (self.active_index + 1) % len(pack.tokens)
        return pack.sample(self.active_index)

    def list_packs(self) -> List[str]:
        return [n for n, p in self.packs.items() if not p.gated or self.allow_gated]

    def get_pack_tokens(self, name: str) -> List[str]:
        if name not in self.packs:
            return []
        return self.packs[name].as_list()

    def as_expression(self) -> Expression:
        if not self.active_pack or self.active_pack not in self.packs:
            return Expression.NEUTRAL
        return self.packs[self.active_pack].default_expression

def build_default_registry(allow_gated: bool = False) -> KaomojiRegistry:
    reg = KaomojiRegistry(allow_gated=allow_gated)
    reg.load_defaults()
    reg.set_pack("classic")
    return reg

# ---------- Demo ----------

def demo():
    reg = build_default_registry()
    print("Available packs:", reg.list_packs())
    print("Active (classic):", reg.current())
    for _ in range(3):
        print("  advance →", reg.advance())

    reg.set_pack("sparkling")
    print("Sparkling:", reg.current(), "| expr:", reg.as_expression().value)

    reg.set_pack("pointing")
    print("Pointing:", reg.current())

    # Custom pack example (personal matrix)
    custom = KaomojiPack(
        name="texas",
        tokens=["(🤠)", "(✧ᴗ✧)", "(•̀ᴗ•́)و Texas"],
        default_expression=Expression.RESOLUTE,
    )
    reg.register(custom)
    reg.set_pack("texas")
    print("Custom Texas pack:", reg.current())

if __name__ == "__main__":
    demo()
