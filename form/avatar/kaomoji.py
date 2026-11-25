#!/usr/bin/env python3
"""Kaomoji packs for expression."""

from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from .face import Expression

KAOMOJI_PACKS: Dict[str, List[str]] = {
    "classic": [":-)", "^_^", "(^^)", ";-)", ":D"],
    "smiling": ["(^_^)", "(◕‿◕)", "(￣▽￣)", "(∗‿∗)"],
    "love": ["(♥ω♥)", "(♡‿♡)", "(´∀｀)♡"],
    "hugging": ["(つ≧▽≦)つ", "(づ｡◕‿‿◕｡)づ"],
    "flexing": ["ᕦ(ò_óˇ)ᕤ", "(ง'̀-'́)ง"],
    "pointing": ["→_→", "←_←", "(→_→)"],
    "sparkling": ["✧(≖ ◡ ≖)", "✦(◕‿◕)✦", "★"],
    "worrying": ["(;_;)", "(⊙_⊙)", "(´；ω；`)"],
    "disapproving": ["ಠ_ಠ", "(¬_¬)"],
    "crying": ["(T_T)", "(ಥ﹏ಥ)"],
}

PACK_TO_EXPRESSION = {
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
}


@dataclass
class KaomojiRegistry:
    packs: Dict[str, List[str]] = field(default_factory=dict)
    active: Optional[str] = None
    index: int = 0

    def load_defaults(self) -> None:
        self.packs = dict(KAOMOJI_PACKS)
        self.active = "classic"
        self.index = 0

    def set_pack(self, name: str) -> bool:
        if name not in self.packs:
            return False
        self.active = name
        self.index = 0
        return True

    def current(self) -> str:
        if not self.active or self.active not in self.packs:
            return "(·_·)"
        tokens = self.packs[self.active]
        return tokens[self.index % len(tokens)]

    def advance(self) -> str:
        if not self.active:
            return "(·_·)"
        tokens = self.packs[self.active]
        self.index = (self.index + 1) % len(tokens)
        return tokens[self.index]

    def list_packs(self) -> List[str]:
        return list(self.packs.keys())

    def expression_for(self, pack: str) -> Expression:
        return PACK_TO_EXPRESSION.get(pack, Expression.NEUTRAL)


def build_default_registry() -> KaomojiRegistry:
    reg = KaomojiRegistry()
    reg.load_defaults()
    return reg
