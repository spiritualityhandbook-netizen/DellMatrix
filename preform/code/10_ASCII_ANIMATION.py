#!/usr/bin/env python3
"""
10_ASCII_ANIMATION.py
Code Phase 3 · Artifact 10
Status: TRUE
Offline · Zero dependencies · Stdlib only

Grows the living structure:
- Consumes Kaomoji Packs (Artifact 9)
- Compatible with FaceStateController (Artifact 8)
- Extends ExpressionField (Artifact 7)
- Implements the Anim model from page 09

Play = Cycle 06 + Show 09 redraw (text frames only).
No GIF · no network · pure terminal / GodWorkSpace ready.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time

# ---------- Minimal fallbacks so the file runs standalone ----------
class Expression(Enum):
    NEUTRAL = "neutral"
    JOY = "joy"
    SOFT = "soft"
    FOCUS = "focus"
    RESOLUTE = "resolute"

# ---------- Anim model (from page 09) ----------

@dataclass
class Anim:
    """
    Text-frame animation.
    frames = list of strings (single-line preferred for mobile).
    """
    id: str
    frames: List[str]
    fps: float = 4.0          # frames per second (soft target)
    loop: bool = True
    pack: Optional[str] = None  # optional kaomoji pack name
    on_end: Optional[str] = None  # future Dell chain placeholder
    current_index: int = 0
    playing: bool = False

    def current_frame(self) -> str:
        if not self.frames:
            return "(·_·)"
        return self.frames[self.current_index % len(self.frames)]

    def advance(self) -> str:
        if not self.frames:
            return "(·_·)"
        if self.loop or self.current_index < len(self.frames) - 1:
            self.current_index = (self.current_index + 1) % len(self.frames)
        return self.current_frame()

    def reset(self) -> None:
        self.current_index = 0

    def stop(self) -> None:
        self.playing = False

    def start(self) -> None:
        self.playing = True
        self.reset()

# ---------- Player ----------

@dataclass
class AsciiPlayer:
    """
    Thin offline player.
    Holds multiple named Anims.
    tick() advances the active one (Cycle 06).
    show() returns the current frame string (Show 09).
    """
    anims: Dict[str, Anim] = field(default_factory=dict)
    active_id: Optional[str] = None
    paused: bool = False

    def register(self, anim: Anim) -> None:
        self.anims[anim.id] = anim

    def set_active(self, anim_id: str) -> bool:
        if anim_id not in self.anims:
            return False
        self.active_id = anim_id
        self.anims[anim_id].start()
        self.paused = False
        return True

    def tick(self) -> str:
        """Advance one frame (Dell 06 Cycle). Returns current frame."""
        if self.paused or not self.active_id:
            return self.show()
        anim = self.anims[self.active_id]
        if not anim.playing:
            return anim.current_frame()
        return anim.advance()

    def show(self) -> str:
        """Current frame only (Dell 09 Show)."""
        if not self.active_id or self.active_id not in self.anims:
            return "(·_·)"
        return self.anims[self.active_id].current_frame()

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False

    def stop(self) -> None:
        if self.active_id and self.active_id in self.anims:
            self.anims[self.active_id].stop()
        self.paused = True

    def list_anims(self) -> List[str]:
        return list(self.anims.keys())

# ---------- Default clips that grow the structure immediately ----------

def build_default_player() -> AsciiPlayer:
    player = AsciiPlayer()

    # Idle pulse (from classic / soft)
    player.register(Anim(
        id="idle",
        frames=["(·_·)", "(·-·)", "(·_·)", "(·o·)"],
        fps=2.0,
        loop=True,
        pack="classic",
    ))

    # Sparkle / success clip (short, non-loop)
    player.register(Anim(
        id="sparkle",
        frames=["✧", "✦", "★", "☆", "✧(◕‿◕)✧"],
        fps=6.0,
        loop=False,
        pack="sparkling",
    ))

    # Pointing attention
    player.register(Anim(
        id="point",
        frames=["→_→", "→_→", "←_←", "→_→"],
        fps=3.0,
        loop=True,
        pack="pointing",
    ))

    # Joy sequence
    player.register(Anim(
        id="joy",
        frames=["(^_^)", "(◕‿◕)", "(^∇^)", "(∗‿∗)"],
        fps=4.0,
        loop=True,
        pack="smiling",
    ))

    # Simple walk indicator (facing glyphs — ready for Grid later)
    player.register(Anim(
        id="walk",
        frames=["→", "⇢", "→", "⇢"],
        fps=5.0,
        loop=True,
    ))

    player.set_active("idle")
    return player

# ---------- Demo (terminal-safe) ----------

def demo():
    player = build_default_player()
    print("ASCII Animation Player — Artifact 10")
    print("Available:", player.list_anims())
    print()

    print("Idle (4 ticks):")
    for _ in range(4):
        print(" ", player.tick())

    print("\nSparkle (non-loop):")
    player.set_active("sparkle")
    for _ in range(6):
        print(" ", player.tick())

    print("\nJoy:")
    player.set_active("joy")
    for _ in range(4):
        print(" ", player.tick())

    print("\nPaused show:", player.show())
    player.pause()
    print("After pause tick (no advance):", player.tick())

if __name__ == "__main__":
    demo()
