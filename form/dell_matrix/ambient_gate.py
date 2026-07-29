#!/usr/bin/env python3
"""
AmbientGate — realized files source (opt-in, local inbox only).

32[Pause] :: 33[Resume] > 35[Discover] :: AmbientGate

- master default OFF
- sources default OFF
- files: reads form/state/inbox/*.txt and *.md when enabled
- screen / mic / clipboard: still not implemented (return empty)
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
_INBOX = os.path.join(os.path.dirname(__file__), "..", "state", "inbox")
os.makedirs(_INBOX, exist_ok=True)


@dataclass
class AmbientGate:
    enabled: Dict[str, bool] = field(default_factory=lambda: {s: False for s in SOURCES})
    master_on: bool = False
    level: int = 2  # files realized

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

    def _intake_files(self) -> List[Dict[str, Any]]:
        items = []
        if not os.path.isdir(_INBOX):
            return items
        for name in sorted(os.listdir(_INBOX)):
            if not (name.endswith(".txt") or name.endswith(".md")):
                continue
            path = os.path.join(_INBOX, name)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read().strip()
            except OSError:
                continue
            stem = os.path.splitext(name)[0]
            items.append(
                {
                    "source": "files",
                    "id": f"file_{stem}",
                    "label": stem,
                    "words": text[:2000],
                    "path": path,
                }
            )
        return items

    def intake(self) -> Dict[str, Any]:
        assert_floor_intact()
        if not self.master_on:
            return {"ok": False, "reason": "ambient master OFF", "items": []}
        active = self.active_sources()
        if not active:
            return {"ok": False, "reason": "no sources enabled", "items": []}

        items: List[Dict[str, Any]] = []
        notes = []
        if "files" in active:
            items.extend(self._intake_files())
        for s in ("screen", "mic", "clipboard"):
            if s in active:
                notes.append(f"{s}: not implemented")

        return {
            "ok": True,
            "items": items,
            "active": active,
            "notes": notes,
            "inbox": _INBOX,
        }

    def status(self) -> Dict[str, Any]:
        return {
            "self": "AmbientGate",
            "level": self.level,
            "master_on": self.master_on,
            "enabled": dict(self.enabled),
            "active": self.active_sources(),
            "floor": list(FLOOR),
            "files_implemented": True,
            "screen_implemented": False,
            "mic_implemented": False,
            "clipboard_implemented": False,
            "inbox": _INBOX,
        }


def smoke() -> bool:
    print("=== AMBIENT REALIZED SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    g = AmbientGate()
    rec("default off", g.master_on is False and g.intake().get("ok") is False)
    # seed inbox
    sample = os.path.join(_INBOX, "_smoke_idea.txt")
    with open(sample, "w", encoding="utf-8") as f:
        f.write("realized ambient sample idea")
    g.turn_on()
    g.enable_source("files")
    out = g.intake()
    rec("files intake", out.get("ok") is True and len(out.get("items", [])) >= 1, str(len(out.get("items", []))))
    rec("has words", any("realized" in (i.get("words") or "") for i in out.get("items", [])))
    try:
        os.remove(sample)
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
