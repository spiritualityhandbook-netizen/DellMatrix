#!/usr/bin/env python3
"""
BlankCube — NBD (equation pick after MainThird).

08[Create] >> 50[Manifest] : 10[Keep] :: BlankCube

Givable starter: personal MatrixSession on Dell Matrix plane.
- Floor locked
- Empty plane (or optional seed note)
- Can place units, change skins/perspectives, sandbox
- Can sync into Main later without clobber
- Not a full UI pack yet — working Form stub you can hand as structure

Run:
  python -m form.dell_matrix.blank_cube --smoke
  python -m form.dell_matrix.blank_cube --demo
  python -m form.dell_matrix.blank_cube --give Alice
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import json
import sys
from datetime import datetime, timezone

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.main_field import MainField, MatrixSession, sync_planes, voluntary_pull
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Perspective, Skin
    from form.dell_matrix.main_field import MainField, MatrixSession, sync_planes, voluntary_pull


@dataclass
class BlankCube:
    """Starter personal matrix — what you give someone."""

    owner: str
    session: MatrixSession = field(init=False)
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    enhance_on: bool = False  # opt-in later; default off

    def __post_init__(self):
        assert_floor_intact()
        self.session = MatrixSession(name=self.owner)
        # optional welcome unit — still a blank *working* surface
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
            "owner": self.owner,
            "created": self.created,
            "floor": list(FLOOR),
            "enhance_on": self.enhance_on,
            "perspective": p.perspective.value,
            "units": {i: u.display() for i, u in p.units.items()},
            "sandboxes": {i: sb.member_ids for i, sb in p.sandboxes.items()},
            "blank": True,
        }

    def export(self) -> Dict[str, Any]:
        """Serializable give-pack (structure, not zip UI yet)."""
        return {
            "type": "BlankCube",
            "version": 1,
            "owner": self.owner,
            "created": self.created,
            "floor": list(FLOOR),
            "enhance_on": self.enhance_on,
            "plane": self.session.plane.status(),
        }


def give(owner: str) -> BlankCube:
    """Create a blank cube for someone."""
    return BlankCube(owner=owner)


def smoke() -> bool:
    print("=== BLANK CUBE SMOKE ===")
    r: List[bool] = []

    def rec(name: str, ok: bool, detail: str = "") -> None:
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    b = give("Alice")
    rec("create", b.owner == "Alice")
    rec("floor", b.status()["floor"] == list(FLOOR))
    rec("enhance default off", b.enhance_on is False)
    b.place_idea("job", "Work", words="first idea", skin=Skin.BUILDING, x=1)
    rec("place", "job" in b.session.plane.units)
    rec("welcome present", "welcome" in b.session.plane.units)

    # can sync with another blank into Main without clobber
    main = MainField()
    other = give("Bob")
    other.place_idea("art", "Art", words="draw", skin=Skin.SPHERE)
    before = b.session.plane.units["job"].words
    out = sync_planes(b.session, other.session, main, "job", "art")
    rec("sync to Main", out.get("ok") is True)
    rec("no clobber", b.session.plane.units["job"].words == before)

    pack = b.export()
    rec("export", pack.get("type") == "BlankCube" and "floor" in pack)

    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo(owner: str = "Friend") -> None:
    print("08[Create] >> 50[Manifest] : 10[Keep] :: BlankCube")
    print(f"English: Give blank cube to {owner}.\n")
    b = give(owner)
    b.place_idea("seed1", "FirstIdea", words="start here", skin=Skin.SEED, x=-1)
    print(json.dumps(b.status(), indent=2))
    print("\nexport keys:", list(b.export().keys()))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Friend"
    for i, a in enumerate(sys.argv):
        if a == "--give" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    demo(owner)


if __name__ == "__main__":
    main()
