#!/usr/bin/env python3
"""
13_THINKS.py
Code Phase 3 · Artifact 13
Status: TRUE
Offline · Zero dependencies · Stdlib only

Grows the living structure:
- Async cognitive thread bound to body state
- Law from page 09: Body first. Thinks second. Thinks always reads real body state.
- Never invents body facts. Narration only queries live body snapshot.

Mind may issue high-level intents; body executes or rejects.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import time

# ---------- Intent vocabulary (high-level only) ----------

class Intent(Enum):
    IDLE        = auto()
    MOVE        = auto()   # request step
    TURN        = auto()
    PICK        = auto()
    PLACE       = auto()
    STOW        = auto()
    DRAW        = auto()
    SET_REACH   = auto()
    EXPRESS     = auto()   # request face/anim change
    NOTE        = auto()   # pure cognitive note (no body action)

@dataclass
class Thought:
    """One cognitive unit. May or may not produce an intent."""
    content: str
    intent: Optional[Intent] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: str = "thinks"

# ---------- Body snapshot (read-only contract) ----------

@dataclass
class BodySnapshot:
    """Immutable view of body. Thinks may only read this."""
    pos: tuple = (0, 0)
    facing: str = "N"
    posture: str = "STAND"
    locomotion: str = "IDLE"
    reach: str = "CLOSE"
    holding: Any = None

    @classmethod
    def from_avatar(cls, avatar: Any) -> "BodySnapshot":
        """Build from any object that has read_body() or .body."""
        if hasattr(avatar, "read_body"):
            b = avatar.read_body()
            return cls(
                pos=getattr(b, "pos", (0, 0)),
                facing=getattr(b.facing, "name", str(getattr(b, "facing", "N"))),
                posture=getattr(b.posture, "name", str(getattr(b, "posture", "STAND"))) if hasattr(b, "posture") else "STAND",
                locomotion=getattr(b.locomotion, "name", str(getattr(b, "locomotion", "IDLE"))) if hasattr(b, "locomotion") else "IDLE",
                reach=getattr(b.reach, "name", str(getattr(b, "reach", "CLOSE"))) if hasattr(b, "reach") else "CLOSE",
                holding=getattr(b, "holding", None),
            )
        # fallback raw
        body = getattr(avatar, "body", None)
        if body is None:
            return cls()
        return cls(
            pos=getattr(body, "pos", (0, 0)),
            facing=str(getattr(body, "facing", "N")),
            holding=getattr(body, "holding", None),
        )

# ---------- Thinks thread ----------

@dataclass
class Thinks:
    """
    Async cognitive layer.
    - Holds a queue of thoughts
    - Can only read BodySnapshot (never writes body directly)
    - Emits intents that a body executor may accept or reject
    """
    queue: List[Thought] = field(default_factory=list)
    last_body: Optional[BodySnapshot] = None
    notes: List[str] = field(default_factory=list)  # pure cognitive log
    max_queue: int = 32

    def observe(self, avatar: Any) -> BodySnapshot:
        """Mandatory: refresh real body state before thinking."""
        snap = BodySnapshot.from_avatar(avatar)
        self.last_body = snap
        return snap

    def think(self, content: str, intent: Optional[Intent] = None, **payload) -> Thought:
        """
        Produce a thought. If intent is given, it is a request only.
        Body must still execute (or refuse).
        """
        if self.last_body is None:
            # Refuse to invent body facts
            content = f"[no body snapshot] {content}"
        t = Thought(content=content, intent=intent, payload=payload)
        self.queue.append(t)
        if len(self.queue) > self.max_queue:
            self.queue = self.queue[-self.max_queue:]
        if intent is None:
            self.notes.append(content)
        return t

    def next_intent(self) -> Optional[Thought]:
        """Pop the next thought that carries an intent."""
        for i, t in enumerate(self.queue):
            if t.intent is not None:
                return self.queue.pop(i)
        return None

    def peek_notes(self, n: int = 5) -> List[str]:
        return self.notes[-n:]

    def status(self) -> Dict[str, Any]:
        return {
            "queue_len": len(self.queue),
            "last_body": self.last_body.__dict__ if self.last_body else None,
            "recent_notes": self.peek_notes(3),
            "pending_intents": sum(1 for t in self.queue if t.intent is not None),
        }

# ---------- Simple executor bridge (body side) ----------

def try_execute(avatar: Any, thought: Thought) -> bool:
    """
    Body-side handler. Returns True if the intent was accepted and applied.
    This is the only place body mutation is allowed from Thinks.
    """
    if thought.intent is None:
        return False

    body = getattr(avatar, "body", None)
    if body is None:
        return False

    intent = thought.intent
    payload = thought.payload

    if intent == Intent.MOVE:
        steps = int(payload.get("steps", 1))
        if hasattr(avatar, "step"):
            avatar.step(steps)
            return True
        # minimal fallback
        if hasattr(body, "pos") and hasattr(body, "facing"):
            dx, dy = getattr(body.facing, "delta", (0, 1))
            x, y = body.pos
            body.pos = (x + dx * steps, y + dy * steps)
            return True

    if intent == Intent.TURN:
        steps = int(payload.get("steps", 1))
        if hasattr(avatar, "turn"):
            avatar.turn(steps)
            return True

    if intent == Intent.NOTE:
        return True  # pure cognitive, always "succeeds"

    # PICK / PLACE / STOW / DRAW / SET_REACH / EXPRESS need richer context
    # (ReachInventory / Anim). Left as intentional no-ops here so the
    # thread stays body-safe without pulling the full stack.
    return False

# ---------- Demo ----------

def demo():
    # Minimal stand-in avatar
    class B:
        pos = (0, 0)
        facing = type("F", (), {"name": "N", "delta": (0, 1)})()
        posture = type("P", (), {"name": "STAND"})()
        locomotion = type("L", (), {"name": "IDLE"})()
        reach = type("R", (), {"name": "CLOSE"})()
        holding = None
    class A:
        body = B()
        def read_body(self):
            return self.body
        def step(self, n=1):
            dx, dy = self.body.facing.delta
            x, y = self.body.pos
            self.body.pos = (x + dx * n, y + dy * n)

    avatar = A()
    thinks = Thinks()

    # Observe first (mandatory)
    snap = thinks.observe(avatar)
    print("Observed body:", snap)

    # Pure note (no intent)
    thinks.think("The grid feels quiet.")
    print("Notes:", thinks.peek_notes())

    # Intent to move
    thinks.think("Advance one step.", intent=Intent.MOVE, steps=1)
    t = thinks.next_intent()
    print("Intent:", t.intent if t else None)
    if t:
        ok = try_execute(avatar, t)
        print("Executed:", ok, "New pos:", avatar.body.pos)

    # Refresh body after action
    thinks.observe(avatar)
    print("Thinks status:", thinks.status())

if __name__ == "__main__":
    demo()
