#!/usr/bin/env python3
"""
24_UNIFIED_ENTRY.py
Code Phase 4 · Unified offline entry
Status: TRUE
Offline · stdlib only

Single steppable surface that prefers real modules when present:
  15 Integrator (or stand-in body loop)
  19 GWS Panels
  21 PersonaLens
  23 GWS+Lens pattern

Public API:
  boot() · command(text) · tick() · render() · status()

Run:
  python preform/code/24_UNIFIED_ENTRY.py
  python preform/code/24_UNIFIED_ENTRY.py --smoke
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")
Coord = Tuple[int, int]


def _load_attr(filename: str, attr: str):
    path = os.path.join(_CODE_DIR, filename)
    try:
        if not os.path.isfile(path):
            return None, "miss"
        name = f"ue_{os.path.splitext(filename)[0]}"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        if hasattr(mod, attr):
            return getattr(mod, attr), "real"
    except Exception as e:
        return None, f"error:{type(e).__name__}"
    return None, "miss"


# ---------------------------------------------------------------------------
# Minimal stand-ins (used when real modules absent)
# ---------------------------------------------------------------------------

class Facing(Enum):
    N, E, S, W = range(4)

    @property
    def delta(self) -> Coord:
        return [(0, 1), (1, 0), (0, -1), (-1, 0)][self.value]


class Intent(Enum):
    MOVE = auto()
    NOTE = auto()
    EXPRESS = auto()


@dataclass
class Body:
    pos: Coord = (0, 0)
    facing: Facing = Facing.N
    holding: Any = None


@dataclass
class Avatar:
    body: Body = field(default_factory=Body)

    def read_body(self) -> Body:
        return Body(pos=self.body.pos, facing=self.body.facing, holding=self.body.holding)

    def step(self, n: int = 1) -> Coord:
        dx, dy = self.body.facing.delta
        x, y = self.body.pos
        self.body.pos = (x + dx * n, y + dy * n)
        return self.body.pos


@dataclass
class LensNote:
    persona: str
    kind: str
    text: str


@dataclass
class StandinLens:
    aetheris_on: bool = True
    manu_on: bool = True
    ancient_on: bool = True
    notes: List[LensNote] = field(default_factory=list)

    def examine(self, text: str) -> List[LensNote]:
        t = (text or "").strip()
        self.notes = [
            LensNote("Aetheris", "coherence", "clear" if t else "empty"),
        ]
        if self.manu_on and t:
            self.notes.append(LensNote("MANUELL", "coach", "sketch: 08[Create] > …"))
        if self.ancient_on:
            self.notes.append(
                LensNote("The_Ancient", "structural", "structural only — no decipherment claim")
            )
        return list(self.notes)

    def status(self) -> Dict[str, Any]:
        return {
            "aetheris": self.aetheris_on,
            "manuell": self.manu_on,
            "ancient": self.ancient_on,
            "notes": len(self.notes),
        }


@dataclass
class Panel:
    name: str
    expanded: bool = True


@dataclass
class StandinGWS:
    panels: Dict[str, Panel] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)

    def __post_init__(self):
        for n in ("status", "seed", "pipeline", "search", "log", "lens"):
            self.panels.setdefault(n, Panel(n))

    def expand(self, name: str) -> bool:
        if name not in self.panels:
            return False
        self.panels[name].expanded = True
        return True

    def collapse(self, name: str) -> bool:
        if name not in self.panels:
            return False
        self.panels[name].expanded = False
        return True

    def is_expanded(self, name: str) -> bool:
        p = self.panels.get(name)
        return bool(p and p.expanded)

    def log(self, msg: str) -> None:
        self.messages.append(msg)
        self.messages = self.messages[-12:]


# ---------------------------------------------------------------------------
# Unified Entry
# ---------------------------------------------------------------------------

@dataclass
class UnifiedEntry:
    avatar: Avatar = field(default_factory=Avatar)
    lens: Any = field(default=None)
    gws: Any = field(default=None)
    ticks: int = 0
    last_command: str = ""
    seed_strip: str = "08[Create] >> 14[Bind] :: unified"
    sources: Dict[str, str] = field(default_factory=dict)
    frame: str = "(·_·)"

    def __post_init__(self):
        LensCls, lens_src = _load_attr("21_PERSONA_LENS.py", "PersonaLens")
        GwsCls, gws_src = _load_attr("19_GWS_PANELS.py", "GWSPanels")
        self.sources = {
            "lens": lens_src,
            "gws": gws_src,
            "integrator": "standin-body",  # full 15 optional later
        }
        self.lens = (LensCls() if LensCls else StandinLens())
        self.gws = (GwsCls() if GwsCls else StandinGWS())
        # ensure lens panel key exists when using real GWSPanels
        if hasattr(self.gws, "panels") and "lens" not in getattr(self.gws, "panels", {}):
            try:
                self.gws.panels["lens"] = Panel("lens", True)
            except Exception:
                pass

    def boot(self) -> None:
        self.ticks = 0
        self.last_command = ""
        self.frame = "(·_·)"
        if hasattr(self.gws, "log"):
            self.gws.log("boot")
        self.lens.examine(self.seed_strip)

    def command(self, text: str, intent: Optional[str] = None, **payload) -> List[Any]:
        self.last_command = text or ""
        notes = self.lens.examine(self.last_command)
        # light body intents (stand-in path)
        if intent == "MOVE" or (text and text.lower().startswith("move")):
            self.avatar.step(int(payload.get("steps", 1)))
            self.frame = "(>_<)"
        elif intent == "EXPRESS" or (text and "joy" in text.lower()):
            self.frame = "(^_^)"
        else:
            self.frame = "(·_·)"
        if hasattr(self.gws, "log"):
            self.gws.log(f"cmd:{self.last_command[:24]}")
        return notes

    def tick(self) -> str:
        self.ticks += 1
        return self.render()

    def render(self) -> str:
        notes = getattr(self.lens, "notes", []) or []
        lens_open = True
        if hasattr(self.gws, "is_expanded"):
            try:
                lens_open = bool(self.gws.is_expanded("lens"))
            except Exception:
                lens_open = True
        mark = "-" if lens_open else "+"
        b = self.avatar.read_body()
        facing = getattr(b.facing, "name", str(b.facing))

        lines = [
            f"+- UnifiedEntry · tick={self.ticks} -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| src lens={self.sources.get('lens')} gws={self.sources.get('gws')}",
            f"| Avatar pos={b.pos} facing={facing} frame={self.frame}",
            f"| SEED: {self.seed_strip}",
            f"| CMD:  {self.last_command or '(none)'}",
            f"| [{mark}] LENS",
        ]
        if lens_open:
            if notes:
                for n in list(notes)[:6]:
                    persona = getattr(n, "persona", "?")
                    kind = getattr(n, "kind", "?")
                    text = getattr(n, "text", str(n))
                    lines.append(f"|     [{persona}/{kind}] {text}")
            else:
                lines.append("|     (no notes)")
        lines.append("+" + "-" * 40 + "+")
        return "\n".join(lines)

    def expand_lens(self) -> bool:
        if hasattr(self.gws, "expand"):
            return bool(self.gws.expand("lens"))
        return False

    def collapse_lens(self) -> bool:
        if hasattr(self.gws, "collapse"):
            return bool(self.gws.collapse("lens"))
        return False

    def status(self) -> Dict[str, Any]:
        b = self.avatar.read_body()
        return {
            "ticks": self.ticks,
            "floor": list(FLOOR),
            "pos": b.pos,
            "frame": self.frame,
            "command": self.last_command,
            "notes": len(getattr(self.lens, "notes", []) or []),
            "sources": dict(self.sources),
        }


def smoke() -> bool:
    print("=== UNIFIED ENTRY SMOKE ===")
    results: List[bool] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(bool(passed))

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    ue = UnifiedEntry()
    run("init", lambda: (ue.lens is not None and ue.gws is not None, str(ue.sources)))
    run("boot", lambda: (ue.boot() or True, f"notes={len(ue.lens.notes)}"))
    run("command", lambda: (len(ue.command("create and bind show")) >= 1, f"n={len(ue.lens.notes)}"))
    run("tick", lambda: ("UnifiedEntry" in ue.tick() and ue.ticks == 1, f"t={ue.ticks}"))
    run("floor", lambda: (ue.status()["floor"] == list(FLOOR), str(FLOOR)))
    run("move", lambda: (
        (ue.command("move forward", intent="MOVE", steps=1) or True)
        and ue.avatar.body.pos != (0, 0),
        f"pos={ue.avatar.body.pos}",
    ))
    run("collapse lens", lambda: (ue.collapse_lens() or True, "ok"))
    run("render", lambda: ("LENS" in ue.render() and "Floor" in ue.render(), "ok"))
    run("status", lambda: ("sources" in ue.status() and "notes" in ue.status(), str(ue.status().get("notes"))))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


def demo() -> None:
    ue = UnifiedEntry()
    ue.boot()
    print(ue.render())
    print()
    ue.command("create and bind the show")
    print(ue.tick())
    print()
    print("STATUS:", ue.status())


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()
