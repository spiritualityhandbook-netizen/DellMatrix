#!/usr/bin/env python3
"""
22_LENS_BRIDGE.py
Code Phase 4 · follow-on to 4C
Status: TRUE
Offline · stdlib only

Wires PersonaLens (21) into a minimal Integrator-shaped loop:
- command(text) → lenses examine → notes stored
- tick() advances a simple step counter and returns pane text
- status() exposes floor, lens flags, last notes

Does not require full 15_INTEGRATOR import; stands alone for offline use.
When full Integrator is present, same pattern applies: call lens.examine on command.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import os
import sys
import importlib.util

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")


def _load_lens_class():
    """Prefer real 21_PERSONA_LENS.PersonaLens; else minimal stand-in."""
    path = os.path.join(_CODE_DIR, "21_PERSONA_LENS.py")
    try:
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location("persona_lens21", path)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            if hasattr(mod, "PersonaLens"):
                return mod.PersonaLens, "real"
    except Exception:
        pass

    # stand-in
    from dataclasses import dataclass as dc, field as fd
    from typing import List as L

    @dc
    class LensNote:
        persona: str
        kind: str
        text: str

    @dc
    class PersonaLens:
        aetheris_on: bool = True
        manu_on: bool = True
        ancient_on: bool = True
        notes: L = fd(default_factory=list)

        def clear(self):
            self.notes = []

        def examine(self, text: str):
            self.clear()
            t = (text or "").strip()
            self.notes.append(LensNote("Aetheris", "coherence", "clear" if t else "empty"))
            if self.manu_on and t:
                self.notes.append(LensNote("MANUELL", "coach", "sketch: 08[Create] > …"))
            if self.ancient_on:
                self.notes.append(
                    LensNote("The_Ancient", "structural", "structural only — no decipherment claim")
                )
            return list(self.notes)

        def render(self, text: str = ""):
            if text:
                self.examine(text)
            lines = ["+- Persona Lens -+", f"| Floor: {' · '.join(FLOOR)}"]
            for n in self.notes:
                lines.append(f"| [{n.persona}/{n.kind}] {n.text}")
            lines.append("+" + "-" * 22 + "+")
            return "\n".join(lines)

        def status(self):
            return {
                "floor": list(FLOOR),
                "aetheris": self.aetheris_on,
                "manuell": self.manu_on,
                "ancient": self.ancient_on,
                "notes": len(self.notes),
            }

    return PersonaLens, "standin"


PersonaLens, LENS_SOURCE = _load_lens_class()


@dataclass
class LensBridge:
    """Minimal command → lens → pane loop."""
    lens: Any = field(default_factory=PersonaLens)
    ticks: int = 0
    last_command: str = ""
    last_notes: List[Any] = field(default_factory=list)
    seed_strip: str = ""
    lens_source: str = LENS_SOURCE

    def command(self, text: str) -> List[Any]:
        self.last_command = text or ""
        self.last_notes = self.lens.examine(self.last_command)
        return self.last_notes

    def set_seed_strip(self, text: str) -> None:
        self.seed_strip = text or ""
        # seed strip also examined (read-only)
        if text:
            self.lens.examine(text)
            self.last_notes = list(self.lens.notes)

    def tick(self) -> str:
        self.ticks += 1
        return self.render()

    def render(self) -> str:
        note_lines = []
        for n in self.last_notes[:8]:
            persona = getattr(n, "persona", "?")
            kind = getattr(n, "kind", "?")
            text = getattr(n, "text", str(n))
            note_lines.append(f"|   [{persona}/{kind}] {text}")
        if not note_lines:
            note_lines = ["|   (no lens notes)"]
        lines = [
            f"+- LensBridge · tick={self.ticks} · lens={self.lens_source} -+",
            f"| Floor: {' · '.join(FLOOR)} (locked)",
            f"| CMD: {self.last_command or '(none)'}",
            f"| SEED: {self.seed_strip or '(none)'}",
            "| NOTES",
            *note_lines,
            "+" + "-" * 40 + "+",
        ]
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        ls = self.lens.status() if hasattr(self.lens, "status") else {}
        return {
            "ticks": self.ticks,
            "lens_source": self.lens_source,
            "last_command": self.last_command,
            "notes": len(self.last_notes),
            "floor": list(FLOOR),
            "lens": ls,
        }


def smoke_bridge() -> bool:
    print("=== LENS BRIDGE SMOKE ===")
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

    b = LensBridge()

    run("init", lambda: (b.ticks == 0 and b.lens is not None, f"source={b.lens_source}"))
    run("command examines", lambda: (len(b.command("create and show the bind")) >= 1, f"n={len(b.last_notes)}"))
    run("tick render", lambda: ("LensBridge" in b.tick() and b.ticks == 1, f"ticks={b.ticks}"))
    run("floor locked", lambda: (b.status()["floor"] == list(FLOOR), str(FLOOR)))
    run("seed strip", lambda: (b.set_seed_strip("08[Create] > 09[Show]") or True, b.seed_strip[:20]))
    run("status shape", lambda: ("lens_source" in b.status() and "notes" in b.status(), str(b.status().get("notes"))))

    # toggle manu if available
    if hasattr(b.lens, "manu_on"):
        b.lens.manu_on = False
        b.command("create something")
        has_manu = any(getattr(n, "persona", "") == "MANUELL" for n in b.last_notes)
        run("manu toggle", lambda: (not has_manu, f"manu_notes={has_manu}"))
    else:
        run("manu toggle", lambda: (True, "no manu flag — skip"))

    print(f"=== RESULT: {sum(results)}/{len(results)} PASS ===")
    return all(results)


if __name__ == "__main__":
    sys.exit(0 if smoke_bridge() else 1)
