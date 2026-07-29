#!/usr/bin/env python3
"""
BlankCube — L3 givable starter.

08[Create] >> 50[Manifest] : 10[Keep] :: BlankCube

- Personal MatrixSession on Dell Matrix plane
- Floor locked, enhance default off
- Export / import pack for handoff
- Optional contact field (e.g. email) — not required to operate
- clean=True → empty plane (no welcome unit)

Run:
  python -m form.dell_matrix.blank_cube --smoke
  python -m form.dell_matrix.blank_cube --give Alice
  python -m form.dell_matrix.blank_cube --give Bob --clean
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
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
    """Starter personal matrix — L3."""

    owner: str
    contact: str = ""  # optional email / handle
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
                words="Blank cube on Dell Matrix. Place ideas. Connect when ready.",
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
        skin: Skin = Skin.CUBE,
        x: float = 0.0,
        y: float = 0.0,
    ):
        return self.session.place(id, label, words=words, skin=skin, x=x, y=y)

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
            "version": 3,
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
                    "Enhance is off until you turn it on",
                    "Place ideas; change skins; box sandboxes as needed",
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
        b = cls(
            owner=data.get("owner", "Friend"),
            contact=data.get("contact", ""),
            clean=True,  # load exact units from pack
        )
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
    print("=== BLANK CUBE L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    b = give("Alice", contact="a@example.com")
    rec("level 3", b.level == 3)
    rec("contact", b.contact == "a@example.com")
    rec("welcome default", "welcome" in b.session.plane.units)
    clean = give("Bob", clean=True)
    rec("clean empty", len(clean.session.plane.units) == 0)
    b.place_idea("job", "Work", words="first", skin=Skin.BUILDING, x=1)
    path = b.write_pack()
    rec("write pack", os.path.isfile(path), path)
    loaded = BlankCube.from_pack(path)
    rec("from_pack owner", loaded.owner == "Alice")
    rec("from_pack units", "job" in loaded.session.plane.units)

    main = MainField()
    other = give("Carol", clean=True)
    other.place_idea("art", "Art", words="draw", skin=Skin.SPHERE)
    before = b.session.plane.units["job"].words
    out = sync_planes(b.session, other.session, main, "job", "art")
    rec("sync no clobber", out.get("ok") and b.session.plane.units["job"].words == before)
    rec("floor", b.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo(owner: str = "Friend", clean: bool = False) -> None:
    print("08[Create] >> 50[Manifest] : 10[Keep] :: BlankCube L3")
    b = give(owner, clean=clean)
    if clean:
        b.place_idea("seed1", "FirstIdea", words="start", skin=Skin.SEED)
    path = b.write_pack()
    print(json.dumps(b.status(), indent=2))
    print("pack →", path)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Friend"
    clean = "--clean" in sys.argv
    for i, a in enumerate(sys.argv):
        if a == "--give" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    demo(owner, clean)


if __name__ == "__main__":
    main()
