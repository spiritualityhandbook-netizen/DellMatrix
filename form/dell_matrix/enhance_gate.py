#!/usr/bin/env python3
"""
EnhanceGate L3.

32[Pause] :: 33[Resume] > 25[Pulse] :: EnhanceGate

Default OFF. Gates resonance pulse/harmonize/decay/clear.
L3: pulse budget, decay/clear via gate, richer status.

Run:
  python -m form.dell_matrix.enhance_gate --smoke
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
    from form.dell_matrix.resonance import (
        ResonanceState,
        pulse,
        harmonize_pair,
        decay,
        clear,
        status as res_status,
    )
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.resonance import (
        ResonanceState,
        pulse,
        harmonize_pair,
        decay,
        clear,
        status as res_status,
    )


@dataclass
class EnhanceGate:
    """Opt-in enhance — L3."""

    on: bool = False
    state: ResonanceState = field(default_factory=ResonanceState)
    level: int = 3
    # 0 = unlimited; else max successful pulses while on this session
    max_pulses: int = 0
    session_pulses: int = 0

    def turn_on(self) -> None:
        assert_floor_intact()
        self.on = True

    def turn_off(self) -> None:
        self.on = False

    def toggle(self) -> bool:
        self.on = not self.on
        return self.on

    def _blocked(self) -> Optional[Dict[str, Any]]:
        if not self.on:
            return {"ok": False, "reason": "enhance OFF", "on": False}
        if self.max_pulses > 0 and self.session_pulses >= self.max_pulses:
            return {
                "ok": False,
                "reason": "pulse budget exhausted",
                "on": True,
                "session_pulses": self.session_pulses,
                "max_pulses": self.max_pulses,
            }
        return None

    def pulse(self, plane: Plane) -> Dict[str, Any]:
        assert_floor_intact()
        blocked = self._blocked()
        if blocked:
            return blocked
        self.state = pulse(plane, self.state)
        self.session_pulses += 1
        return {
            "ok": True,
            "on": True,
            "session_pulses": self.session_pulses,
            "pulse_count": self.state.pulse_count,
            "scores": dict(self.state.scores),
        }

    def harmonize(self, plane: Plane, a: str, b: str) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "reason": "enhance OFF", "on": False}
        return harmonize_pair(plane, a, b, self.state)

    def decay(self, factor: float = 0.9) -> Dict[str, Any]:
        if not self.on:
            return {"ok": False, "reason": "enhance OFF", "on": False}
        self.state = decay(self.state, factor)
        return {"ok": True, "scores": dict(self.state.scores)}

    def clear(self) -> Dict[str, Any]:
        # clear allowed even when off — user may reset residue
        self.state = clear(self.state)
        self.session_pulses = 0
        return {"ok": True, "cleared": True}

    def status(self) -> Dict[str, Any]:
        return {
            "self": "EnhanceGate",
            "level": self.level,
            "on": self.on,
            "session_pulses": self.session_pulses,
            "max_pulses": self.max_pulses,
            "floor": list(FLOOR),
            "resonance": res_status(self.state),
        }


def smoke() -> bool:
    print("=== ENHANCE GATE L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    g = EnhanceGate()
    cube = give("E", clean=True)
    cube.place_idea("biz", "Business", words="crm", skin=Skin.BUILDING, x=1)
    cube.place_idea("music", "Music", words="song", skin=Skin.SEED, x=-1)
    plane = cube.session.plane

    rec("level 3", g.level == 3)
    rec("default off", g.on is False)
    rec("pulse blocked", g.pulse(plane).get("ok") is False)

    g.turn_on()
    rec("pulse on", g.pulse(plane).get("ok") is True and g.session_pulses == 1)
    rec("harmonize", g.harmonize(plane, "biz", "music").get("ok") is True)

    before = g.state.score_of("biz")
    g.decay(0.5)
    rec("decay via gate", abs(g.state.score_of("biz") - before * 0.5) < 1e-9)

    g.max_pulses = 1
    g.session_pulses = 1
    rec("budget block", g.pulse(plane).get("reason") == "pulse budget exhausted")

    g.clear()
    rec("clear", g.state.score_of("biz") == 0.0 and g.session_pulses == 0)
    rec("floor", g.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("32[Pause] :: 33[Resume] > 25[Pulse] :: EnhanceGate L3")
    g = EnhanceGate()
    cube = give("Demo", clean=True)
    cube.place_idea("a", "A", words="alpha", skin=Skin.CUBE)
    cube.place_idea("b", "B", words="beta", skin=Skin.SEED, x=1)
    print("off:", g.pulse(cube.session.plane))
    g.turn_on()
    print("on:", g.pulse(cube.session.plane))
    print(json.dumps(g.status(), indent=2))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
