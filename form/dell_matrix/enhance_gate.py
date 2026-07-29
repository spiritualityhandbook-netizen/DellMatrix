#!/usr/bin/env python3
"""
EnhanceGate — NBD (equation after ResonanceAct).

32[Pause] :: 33[Resume] > 25[Pulse] :: EnhanceGate

Opt-in switch around resonance:
- default OFF (no ambient enhance)
- ON → pulse / harmonize allowed
- OFF → pulse rejected (safe idle)

Run:
  python -m form.dell_matrix.enhance_gate --smoke
  python -m form.dell_matrix.enhance_gate --demo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.resonance import ResonanceState, pulse, harmonize_pair, status as res_status
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.resonance import ResonanceState, pulse, harmonize_pair, status as res_status


@dataclass
class EnhanceGate:
    """Opt-in enhance. Default off."""

    on: bool = False
    state: ResonanceState = field(default_factory=ResonanceState)

    def turn_on(self) -> None:
        assert_floor_intact()
        self.on = True

    def turn_off(self) -> None:
        self.on = False

    def toggle(self) -> bool:
        self.on = not self.on
        return self.on

    def pulse(self, plane: Plane) -> Dict[str, Any]:
        assert_floor_intact()
        if not self.on:
            return {"ok": False, "reason": "enhance OFF", "on": False}
        self.state = pulse(plane, self.state)
        return {"ok": True, "on": True, "scores": dict(self.state.scores)}

    def harmonize(self, plane: Plane, a: str, b: str) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "reason": "enhance OFF", "on": False}
        return harmonize_pair(plane, a, b, self.state)

    def status(self) -> Dict[str, Any]:
        return {
            "self": "EnhanceGate",
            "on": self.on,
            "floor": list(FLOOR),
            "resonance": res_status(self.state),
        }


def smoke() -> bool:
    print("=== ENHANCE GATE SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    g = EnhanceGate()
    cube = give("E")
    cube.place_idea("biz", "Business", words="crm", skin=Skin.BUILDING, x=1)
    cube.place_idea("music", "Music", words="song", skin=Skin.SEED, x=-1)
    plane = cube.session.plane

    rec("default off", g.on is False)
    off = g.pulse(plane)
    rec("pulse blocked when off", off.get("ok") is False and off.get("reason") == "enhance OFF")
    rec("scores untouched when off", g.state.score_of("biz") == 0.0)

    g.turn_on()
    on = g.pulse(plane)
    rec("pulse works when on", on.get("ok") is True and g.state.score_of("biz") > 0)
    rec("harmonize on", g.harmonize(plane, "biz", "music").get("ok") is True)

    g.turn_off()
    rec("off again", g.pulse(plane).get("ok") is False)
    rec("floor", g.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("32[Pause] :: 33[Resume] > 25[Pulse] :: EnhanceGate")
    print("English: Enhance default off; turn on to pulse.\n")
    g = EnhanceGate()
    cube = give("Demo")
    cube.place_idea("a", "A", words="alpha", skin=Skin.CUBE)
    cube.place_idea("b", "B", words="beta", skin=Skin.SEED, x=1)
    print("off pulse:", g.pulse(cube.session.plane))
    g.turn_on()
    print("on pulse:", g.pulse(cube.session.plane))
    print(json.dumps(g.status(), indent=2))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
