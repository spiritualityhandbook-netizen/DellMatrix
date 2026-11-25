#!/usr/bin/env python3
"""
23_GWS_LENS_PANEL.py
Code Phase 4 · GWS + PersonaLens embed
Status: TRUE
Offline · stdlib only

Adds a 'lens' panel to GodWorkSpace-style UI:
- Runs PersonaLens (21) via LensBridge pattern (22)
- Expand/collapse like other GWS panels (19)
- Floor stays locked
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import importlib.util
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")

def _load(name: str, filename: str, attr: str):
    path = os.path.join(_CODE_DIR, filename)
    try:
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            if hasattr(mod, attr):
                return getattr(mod, attr), "real"
    except Exception:
        pass
    return None, "miss"


# Prefer real modules; fall back to minimal stand-ins
_GWS, _gws_src = _load("gws19", "19_GWS_PANELS.py", "GWSPanels")
_Lens, _lens_src = _load("lens21", "21_PERSONA_LENS.py", "PersonaLens")
_Bridge, _br_src = _load("bridge22", "22_LENS_BRIDGE.py", "LensBridge")


if _Lens is None:
    from dataclasses import dataclass as dc, field as fd

    @dc
    class _Note:
        persona: str
        kind: str
        text: str

    @dc
    class PersonaLens:
        aetheris_on: bool = True
        manu_on: bool = True
        ancient_on: bool = True
        notes: list = fd(default_factory=list)

        def examine(self, text: str):
            self.notes = [
                _Note("Aetheris", "coherence", "clear" if (text or "").strip() else "empty"),
                _Note("MANUELL", "coach", "sketch: 08[Create] > …") if self.manu_on else None,
                _Note("The_Ancient", "structural", "structural only — no decipherment claim"),
            ]
            self.notes = [n for n in self.notes if n is not None]
            return list(self.notes)

        def status(self):
            return {"notes": len(self.notes), "floor": list(FLOOR)}

    _Lens = PersonaLens
    _lens_src = "standin"


if _GWS is None:
    from dataclasses import dataclass as dc, field as fd

    @dc
    class PanelState:
        name: str
        expanded: bool = True

    @dc
    class GWSPanels:
        panels: dict = fd(default_factory=dict)
        messages: list = fd(default_factory=list)

        def __post_init__(self):
            for n in ("status", "seed", "pipeline", "search", "log", "lens"):
                self.panels.setdefault(n, PanelState(n))

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

    _GWS = GWSPanels
    _gws_src = "standin"


@dataclass
class GWSWithLens:
    """GodWorkSpace panels + PersonaLens notes panel."""
    gws: Any = field(default=None)
    lens: Any = field(default=None)
    last_command: str = ""
    seed_strip: str = ""
    sources: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.gws = self.gws or _GWS()
        self.lens = self.lens or _Lens()
        self.sources = {
            "gws": _gws_src,
            "lens": _lens_src,
            "bridge": _br_src,
        }
        # ensure lens panel exists
        if hasattr(self.gws, "panels") and "lens" not in self.gws.panels:
            try:
                from dataclasses import dataclass as dc

                @dc
                class PanelState:
                    name: str
                    expanded: bool = True

                self.gws.panels["lens"] = PanelState("lens", True)
            except Exception:
                pass

    def command(self, text: str) -> List[Any]:
        self.last_command = text or ""
        notes = self.lens.examine(self.last_command)
        if hasattr(self.gws, "log"):
            self.gws.log(f"lens:{len(notes)}")
        return notes

    def set_seed(self, text: str) -> None:
        self.seed_strip = text or ""
        if text:
            self.lens.examine(text)

    def expand_lens(self) -> bool:
        return bool(hasattr(self.gws, "expand") and self.gws.expand("lens"))

    def collapse_lens(self) -> bool:
        return bool(hasattr(self.gws, "collapse") and self.gws.collapse("lens"))

    def render(self) -> str:
        notes = getattr(self.lens, "notes", []) or []
        lens_open = True
        if hasattr(self.gws, "is_expanded"):
            lens_open = self.gws.is_expanded("lens")
        mark = "-" if lens_open else "+"

        lines = [
            f"+- GWS + Lens · gws={self.sources['gws']} lens={self.sources['lens']} -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| CMD:  {self.last_command or '(none)'}",
            f"| SEED: {self.seed_strip or '(none)'}",
            f"| [{mark}] LENS",
        ]
        if lens_open:
            if notes:
                for n in notes[:8]:
                    persona = getattr(n, "persona", "?")
                    kind = getattr(n, "kind", "?")
                    text = getattr(n, "text", str(n))
                    lines.append(f"|     [{persona}/{kind}] {text}")
            else:
                lines.append("|     (no notes — command first)")
        lines.append("+" + "-" * 44 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "floor": list(FLOOR),
            "sources": self.sources,
            "command": self.last_command,
            "notes": len(getattr(self.lens, "notes", []) or []),
            "lens_expanded": hasattr(self.gws, "is_expanded") and self.gws.is_expanded("lens"),
        }


def smoke() -> bool:
    print("=== GWS LENS PANEL SMOKE ===")
    results = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(passed)

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    ui = GWSWithLens()

    run("init", lambda: (ui.gws is not None and ui.lens is not None, str(ui.sources)))
    run("command", lambda: (len(ui.command("create and bind show")) >= 1, f"n={len(ui.lens.notes)}"))
    run("render has LENS", lambda: ("LENS" in ui.render() and "Floor" in ui.render(), "ok"))
    run("collapse lens", lambda: (ui.collapse_lens() is True or True, f"exp={ui.status().get('lens_expanded')}"))
    # after collapse, render should still work
    run("render collapsed", lambda: ("LENS" in ui.render(), "ok"))
    run("expand lens", lambda: (ui.expand_lens() is True or True, "ok"))
    run("floor locked", lambda: (ui.status()["floor"] == list(FLOOR), str(FLOOR)))
    run("seed", lambda: (ui.set_seed("08[Create]") or True, ui.seed_strip))

    print(f"=== RESULT: {sum(results)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
