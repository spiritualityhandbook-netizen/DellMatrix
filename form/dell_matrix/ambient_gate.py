#!/usr/bin/env python3
"""
AmbientGate — ALL sources realized as local folder adapters (out of preform).

Sources (each default OFF; master default OFF):
  files      → form/state/inbox/
  screen     → form/state/screen/     (drop text/png captions .txt)
  mic        → form/state/mic/        (drop transcripts .txt)
  clipboard  → form/state/clipboard/  (drop .txt pastes)

No silent capture of OS mic/screen — operator drops artifacts in folders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
import os
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact

SOURCES = ("files", "screen", "mic", "clipboard")
_STATE = os.path.join(os.path.dirname(__file__), "..", "state")
_DIRS = {
    "files": os.path.join(_STATE, "inbox"),
    "screen": os.path.join(_STATE, "screen"),
    "mic": os.path.join(_STATE, "mic"),
    "clipboard": os.path.join(_STATE, "clipboard"),
}
for d in _DIRS.values():
    os.makedirs(d, exist_ok=True)


def _read_dir(source: str) -> List[Dict[str, Any]]:
    folder = _DIRS[source]
    items = []
    if not os.path.isdir(folder):
        return items
    for name in sorted(os.listdir(folder)):
        if name.startswith("."):
            continue
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        # text-like only
        if not (name.endswith(".txt") or name.endswith(".md") or name.endswith(".csv")):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read().strip()
        except OSError:
            continue
        stem = os.path.splitext(name)[0]
        items.append(
            {
                "source": source,
                "id": f"{source}_{stem}",
                "label": f"{source}:{stem}",
                "words": text[:4000],
                "path": path,
            }
        )
    return items


@dataclass
class AmbientGate:
    enabled: Dict[str, bool] = field(default_factory=lambda: {s: False for s in SOURCES})
    master_on: bool = False
    level: int = 3  # all folder adapters live

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
        assert_floor_intact()
        if not self.master_on:
            return {"ok": False, "reason": "ambient master OFF", "items": []}
        active = self.active_sources()
        if not active:
            return {"ok": False, "reason": "no sources enabled", "items": []}
        items: List[Dict[str, Any]] = []
        for s in active:
            items.extend(_read_dir(s))
        return {
            "ok": True,
            "items": items,
            "active": active,
            "dirs": {s: _DIRS[s] for s in active},
            "level": self.level,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "self": "AmbientGate",
            "level": self.level,
            "master_on": self.master_on,
            "enabled": dict(self.enabled),
            "active": self.active_sources(),
            "dirs": dict(_DIRS),
            "floor": list(FLOOR),
            "mode": "folder adapters — drop .txt/.md into source dirs",
            "files_implemented": True,
            "screen_implemented": True,
            "mic_implemented": True,
            "clipboard_implemented": True,
        }


def smoke() -> bool:
    print("=== AMBIENT ALL SOURCES SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    g = AmbientGate()
    rec("default off", g.master_on is False)
    for s, folder in _DIRS.items():
        path = os.path.join(folder, f"_smoke_{s}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"sample from {s}")
    g.turn_on()
    for s in SOURCES:
        g.enable_source(s)
    out = g.intake()
    rec("intake ok", out.get("ok") is True)
    rec("all sources", len(out.get("items", [])) >= 4, str(len(out.get("items", []))))
    rec("level 3", g.level == 3)
    for s, folder in _DIRS.items():
        try:
            os.remove(os.path.join(folder, f"_smoke_{s}.txt"))
        except OSError:
            pass
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print(AmbientGate().status())


if __name__ == "__main__":
    main()
