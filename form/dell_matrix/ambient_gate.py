#!/usr/bin/env python3
"""
AmbientGate — Form-safe skeleton only (NBD x10).

32[Pause] :: 33[Resume] > 35[Discover] :: AmbientGate

DEFAULT ALL OFF. No file/screen/mic intake implemented.
Registers source slots so future Form can snap real adapters under the same gate.

Full ambient intake remains Pre-form (preform/pages/14_AMBIENT_ENHANCE.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact

SOURCES = ("files", "screen", "mic", "clipboard")


@dataclass
class AmbientGate:
    """Opt-in ambient slots — no intake engines yet."""

    enabled: Dict[str, bool] = field(default_factory=lambda: {s: False for s in SOURCES})
    master_on: bool = False  # must be on AND per-source
    level: int = 1  # skeleton only

    def turn_on(self) -> None:
        assert_floor_intact()
        self.master_on = True

    def turn_off(self) -> None:
        self.master_on = False

    def enable_source(self, name: str) -> bool:
        if name not in self.enabled:
            return False
        self.enabled[name] = True
        return True

    def disable_source(self, name: str) -> bool:
        if name not in self.enabled:
            return False
        self.enabled[name] = False
        return True

    def active_sources(self) -> List[str]:
        if not self.master_on:
            return []
        return [s for s, on in self.enabled.items() if on]

    def intake(self) -> Dict[str, Any]:
        """No-op intake — returns empty until Pre-form engines land."""
        assert_floor_intact()
        if not self.master_on:
            return {"ok": False, "reason": "ambient master OFF", "items": []}
        active = self.active_sources()
        if not active:
            return {"ok": False, "reason": "no sources enabled", "items": []}
        # Explicit: no real capture in Form skeleton
        return {
            "ok": True,
            "items": [],
            "note": "skeleton only — no file/screen/mic capture implemented",
            "active": active,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "self": "AmbientGate",
            "level": self.level,
            "master_on": self.master_on,
            "enabled": dict(self.enabled),
            "active": self.active_sources(),
            "floor": list(FLOOR),
            "intake_implemented": False,
        }


def smoke() -> bool:
    print("=== AMBIENT GATE SKELETON SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    g = AmbientGate()
    rec("default master off", g.master_on is False)
    rec("default sources off", all(v is False for v in g.enabled.values()))
    rec("intake blocked", g.intake().get("ok") is False)
    g.turn_on()
    g.enable_source("files")
    out = g.intake()
    rec("intake empty skeleton", out.get("ok") is True and out.get("items") == [])
    rec("no silent sources", "files" in out.get("active", []))
    rec("floor", g.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("32[Pause] :: AmbientGate skeleton (no intake)")
    print(AmbientGate().status())


if __name__ == "__main__":
    main()
