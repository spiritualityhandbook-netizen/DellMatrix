#!/usr/bin/env python3
"""
SandboxGate — global isolation mode.

23[Lock] :: 24[Unlock] > 32[Pause] :: SandboxGate

DEFAULT OFF — ideas are connected on the plane.
ON — new places auto-box; existing units can be boxed as a group.
OFF — unbox-all restores connected enhance scope.

Per-unit box/unbox still works either way.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane


@dataclass
class SandboxGate:
    """Global sandbox mode — default OFF."""

    on: bool = False  # DEFAULT OFF
    auto_box_id: str = "auto_sandbox"
    level: int = 1

    def turn_on(self) -> None:
        assert_floor_intact()
        self.on = True

    def turn_off(self) -> None:
        self.on = False

    def toggle(self) -> bool:
        self.on = not self.on
        return self.on

    def apply_on(self, plane: Plane, unit_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Box all (or given) units into auto sandbox."""
        assert_floor_intact()
        self.on = True
        ids = unit_ids if unit_ids is not None else list(plane.units.keys())
        if not ids:
            return {"ok": True, "on": True, "boxed": []}
        plane.box(ids, self.auto_box_id)
        return {"ok": True, "on": True, "boxed": ids, "box": self.auto_box_id}

    def apply_off(self, plane: Plane) -> Dict[str, Any]:
        """Unbox every unit — connected plane again."""
        assert_floor_intact()
        self.on = False
        freed = []
        for uid in list(plane.units.keys()):
            if plane.units[uid].sandboxed:
                plane.unbox(uid)
                freed.append(uid)
        return {"ok": True, "on": False, "unboxed": freed}

    def maybe_auto_box(self, plane: Plane, unit_id: str) -> None:
        """If gate ON, newly placed unit joins auto sandbox."""
        if not self.on:
            return
        if unit_id in plane.units:
            plane.box([unit_id], self.auto_box_id)

    def status(self) -> Dict[str, Any]:
        return {
            "self": "SandboxGate",
            "on": self.on,
            "default": False,
            "auto_box_id": self.auto_box_id,
            "level": self.level,
            "floor": list(FLOOR),
            "note": "OFF = connected; ON = isolation mode",
        }


def smoke() -> bool:
    print("=== SANDBOX GATE SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    from form.open import open_program
    from form.dell_matrix.plane import Skin

    g = SandboxGate()
    rec("default off", g.on is False)
    p = open_program("SB")
    p.cube.session.plane.units.clear()
    p.place("a", "A", skin=Skin.CUBE)
    p.place("b", "B", skin=Skin.SEED, x=1)
    rec("place connected", not p.cube.session.plane.units["a"].sandboxed)
    g.apply_on(p.cube.session.plane)
    rec("on boxes", p.cube.session.plane.units["a"].sandboxed and p.cube.session.plane.units["b"].sandboxed)
    g.apply_off(p.cube.session.plane)
    rec("off unboxes", not p.cube.session.plane.units["a"].sandboxed)
    g.turn_on()
    g.maybe_auto_box(p.cube.session.plane, "a")
    # place path tested via Program
    rec("floor", g.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print(SandboxGate().status())


if __name__ == "__main__":
    main()
