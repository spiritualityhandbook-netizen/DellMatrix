#!/usr/bin/env python3
"""BlankCube — givable starter with same DEV capabilities, no personal lore."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import os
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.main_field import MainField, MatrixSession, sync_planes, voluntary_pull
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.main_field import MainField, MatrixSession, sync_planes, voluntary_pull

_PACK_DIR = os.path.join(os.path.dirname(__file__), "..", "state", "packs")
os.makedirs(_PACK_DIR, exist_ok=True)


@dataclass
class BlankCube:
    owner: str
    contact: str = ""
    clean: bool = False
    level: int = 3
    session: MatrixSession = field(init=False)
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    enhance_on: bool = False

    def __post_init__(self):
        assert_floor_intact()
        self.session = MatrixSession(name=self.owner)
        if not self.clean:
            self.session.place(
                "welcome",
                "Welcome",
                words="Blank cube on Dell Matrix. Place ideas with detail and goals.",
                detail="Starter surface — same capabilities as DEV, no personal lore.",
                goals=["learn the acceptance path", "add ideas with detail and goals"],
                skin=Skin.WORDS,
                x=0,
                y=0,
            )

    def place_idea(
        self,
        id: str,
        label: str,
        *,
        words: str = "",
        detail: str = "",
        goals: Optional[List[str]] = None,
        skin: Skin = Skin.CUBE,
        x: float = 0.0,
        y: float = 0.0,
    ):
        return self.session.place(
            id, label, words=words, detail=detail, goals=goals or [], skin=skin, x=x, y=y
        )

    def status(self) -> Dict[str, Any]:
        p = self.session.plane
        return {
            "level": self.level,
            "owner": self.owner,
            "contact": self.contact,
            "created": self.created,
            "floor": list(FLOOR),
            "enhance_on": self.enhance_on,
            "clean": self.clean,
            "perspective": p.perspective.value,
            "units": {i: u.display() for i, u in p.units.items()},
            "sandboxes": {i: sb.member_ids for i, sb in p.sandboxes.items()},
            "blank": True,
        }

    def export(self) -> Dict[str, Any]:
        plane = self.session.plane
        units = {
            uid: {
                "label": u.label,
                "words": u.words,
                "detail": getattr(u, "detail", "") or "",
                "goals": list(getattr(u, "goals", []) or []),
                "skin": u.skin.value,
                "x": u.x,
                "y": u.y,
                "sandboxed": u.sandboxed,
                "sandbox_id": u.sandbox_id,
            }
            for uid, u in plane.units.items()
        }
        return {
            "type": "BlankCubePack",
            "version": 4,
            "level": self.level,
            "owner": self.owner,
            "contact": self.contact,
            "created": self.created,
            "floor": list(FLOOR),
            "enhance_on": self.enhance_on,
            "give": {
                "title": "Dell Matrix Blank Cube",
                "rules": [
                    "Floor Alpha·Delta·Omega·Omni never changes",
                    "Your cube is yours — Main sync does not overwrite it",
                    "Ideas need detail + goals so growth is aimed",
                    "Same capabilities as DEV — no personal Ace/Worldwide lore included",
                ],
            },
            "plane": {
                "perspective": plane.perspective.value,
                "units": units,
                "sandboxes": {s: list(sb.member_ids) for s, sb in plane.sandboxes.items()},
            },
        }

    def write_pack(self, path: Optional[str] = None) -> str:
        path = path or os.path.join(_PACK_DIR, f"blank_{self.owner}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.export(), f, indent=2)
        return path

    @classmethod
    def from_pack(cls, path: str) -> "BlankCube":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("floor") != list(FLOOR):
            raise RuntimeError("Floor mismatch in pack")
        b = cls(owner=data.get("owner", "Friend"), contact=data.get("contact", ""), clean=True)
        plane = b.session.plane
        plane.units.clear()
        for uid, u in data.get("plane", {}).get("units", {}).items():
            try:
                skin = Skin(u.get("skin", "cube"))
            except ValueError:
                skin = Skin.CUBE
            plane.place(
                uid,
                u.get("label", uid),
                words=u.get("words", ""),
                detail=u.get("detail", ""),
                goals=list(u.get("goals") or []),
                skin=skin,
                x=float(u.get("x", 0)),
                y=float(u.get("y", 0)),
            )
            unit = plane.units[uid]
            unit.sandboxed = bool(u.get("sandboxed", False))
            unit.sandbox_id = u.get("sandbox_id")
        for sid, members in data.get("plane", {}).get("sandboxes", {}).items():
            plane.box(list(members), sid)
        b.enhance_on = bool(data.get("enhance_on", False))
        return b


def give(owner: str, contact: str = "", clean: bool = False) -> BlankCube:
    return BlankCube(owner=owner, contact=contact, clean=clean)


def smoke() -> bool:
    print("=== BLANK CUBE SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    b = give("Alice")
    rec("welcome", "welcome" in b.session.plane.units)
    rec("welcome goals", len(b.session.plane.units["welcome"].goals) >= 1)
    b.place_idea("job", "Work", detail="ops", goals=["finish route"], words="field", skin=Skin.BUILDING, x=1)
    path = b.write_pack()
    loaded = BlankCube.from_pack(path)
    rec("pack goals", loaded.session.plane.units["job"].goals == ["finish route"])
    rec("floor", b.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Friend"
    clean = "--clean" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--give" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    b = give(owner, clean=clean)
    print(json.dumps(b.status(), indent=2))
    print("pack →", b.write_pack())


if __name__ == "__main__":
    main()
