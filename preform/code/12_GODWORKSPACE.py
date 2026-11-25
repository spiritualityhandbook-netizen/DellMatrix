#!/usr/bin/env python3
"""
12_GODWORKSPACE.py
Code Phase 3 · Artifact 12
Status: TRUE (minimal terminal shell)
Offline · Zero dependencies · Stdlib only

Grows from:
- ExpressionField / Face-State / Kaomoji / ASCII Animation
- Avatar + Reach/Inventory + Grid
- Page 08 keep-blend requirements (text form)

This is the offline GodWorkSpace pane.
Full graphical UI remains future; this shell is the living True core.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time

# ---------- Minimal internal status bus ----------

@dataclass
class WorkspaceState:
    """Central read-only status that all panes can query."""
    header: str = "GodWorkSpace"
    phase: str = "Code Phase 3"
    temp: str = "W"          # C / W / H
    avatar_status: Dict[str, Any] = field(default_factory=dict)
    anim_frame: str = "(·_·)"
    inventory: List[Any] = field(default_factory=list)
    holding: Any = None
    seed_strip: str = ""     # read-only Mandel seed display
    messages: List[str] = field(default_factory=list)
    drafts: Dict[str, str] = field(default_factory=dict)  # local only

    def log(self, msg: str) -> None:
        self.messages.append(msg)
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]

# ---------- Panels (keep-blend) ----------

class HeaderPanel:
    def render(self, state: WorkspaceState) -> str:
        return f"┌─ {state.header} ─ {state.phase} ─ Temp:{state.temp} ─┐"

class StatusPanel:
    def render(self, state: WorkspaceState) -> str:
        lines = [
            "│ STATUS",
            f"│   Avatar : {state.avatar_status or '—'}",
            f"│   Frame  : {state.anim_frame}",
            f"│   Hand   : {state.holding}",
            f"│   Inv    : {state.inventory}",
        ]
        return "\n".join(lines)

class SeedStripPanel:
    """Read-only Mandel seed strip — do not disturb."""
    def render(self, state: WorkspaceState) -> str:
        seed = state.seed_strip or "(no seed)"
        return f"│ SEED (read-only): {seed}"

class MessagePanel:
    def render(self, state: WorkspaceState) -> str:
        if not state.messages:
            return "│ LOG: —"
        recent = state.messages[-5:]
        lines = ["│ LOG"] + [f"│   {m}" for m in recent]
        return "\n".join(lines)

class DraftPanel:
    """localStorage-style drafts (in-memory until True confirm)."""
    def render(self, state: WorkspaceState) -> str:
        if not state.drafts:
            return "│ DRAFTS: (empty)"
        lines = ["│ DRAFTS"] + [f"│   {k}: {v[:40]}…" if len(v) > 40 else f"│   {k}: {v}" for k, v in state.drafts.items()]
        return "\n".join(lines)

# ---------- GodWorkSpace shell ----------

@dataclass
class GodWorkSpace:
    """
    Minimal offline terminal GodWorkSpace.
    Satisfies page 08 keep-blend in text form:
    header+status · panels · Temp · seed strip · drafts.
    """
    state: WorkspaceState = field(default_factory=WorkspaceState)
    header: HeaderPanel = field(default_factory=HeaderPanel)
    status: StatusPanel = field(default_factory=StatusPanel)
    seed: SeedStripPanel = field(default_factory=SeedStripPanel)
    log: MessagePanel = field(default_factory=MessagePanel)
    drafts: DraftPanel = field(default_factory=DraftPanel)

    def set_temp(self, level: str) -> None:
        if level in ("C", "W", "H"):
            self.state.temp = level
            self.state.log(f"Temp → {level}")

    def set_avatar_status(self, status: Dict[str, Any]) -> None:
        self.state.avatar_status = status

    def set_frame(self, frame: str) -> None:
        self.state.anim_frame = frame

    def set_inventory(self, items: List[Any], holding: Any = None) -> None:
        self.state.inventory = items
        self.state.holding = holding

    def set_seed_strip(self, seed: str) -> None:
        """Read-only. Overwrites the display strip only."""
        self.state.seed_strip = seed

    def save_draft(self, key: str, text: str) -> None:
        self.state.drafts[key] = text
        self.state.log(f"Draft saved: {key}")

    def clear_draft(self, key: str) -> None:
        if key in self.state.drafts:
            del self.state.drafts[key]
            self.state.log(f"Draft cleared: {key}")

    def render(self) -> str:
        """Full text pane."""
        parts = [
            self.header.render(self.state),
            self.status.render(self.state),
            self.seed.render(self.state),
            self.log.render(self.state),
            self.drafts.render(self.state),
            "└" + "─" * 42 + "┘",
        ]
        return "\n".join(parts)

    def tick_demo(self) -> None:
        """Simple live feel for demo."""
        self.state.log("tick")

# ---------- Demo ----------

def demo():
    gws = GodWorkSpace()
    gws.set_temp("W")
    gws.set_avatar_status({"pos": (0, 0), "facing": "N", "reach": "CLOSE"})
    gws.set_frame("(◕‿◕)")
    gws.set_inventory([{"name": "wrench"}], holding=None)
    gws.set_seed_strip("08[Create] >> 14[Bind] :: demo")
    gws.save_draft("note1", "test draft — local only")
    gws.state.log("GodWorkSpace online")

    print(gws.render())
    print()
    gws.set_temp("H")
    gws.set_frame("✧")
    print(gws.render())

if __name__ == "__main__":
    demo()
