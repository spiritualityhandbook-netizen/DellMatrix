#!/usr/bin/env python3
"""
OneProgramBoot — NBD (equation after BlankCube).

01[Initiate] > 15[Map] >> 09[Show] :: Open

One entry that opens the program:
  Mandell Floor + registry
  Dell Matrix snap host
  Plane (perspectives / skins / sandbox)
  Main third-field
  BlankCube personal session
  DuoBeta self-understand + optional grow tick

Run:
  python -m form.open
  python -m form.open --smoke
  python -m form.open --owner Ace
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.registry import DELLS, lookup
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField, sync_planes, voluntary_pull
    from form.dell_matrix.blank_cube import BlankCube, give
    from form.duobeta.growth import DuoBeta
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.registry import DELLS, lookup
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField, sync_planes, voluntary_pull
    from form.dell_matrix.blank_cube import BlankCube, give
    from form.duobeta.growth import DuoBeta


@dataclass
class Program:
    """The one program — open this."""

    owner: str = "Operator"
    matrix: DellMatrix = field(default_factory=DellMatrix)
    main: MainField = field(default_factory=MainField)
    cube: BlankCube = field(init=False)
    duo: DuoBeta = field(init=False)

    def __post_init__(self):
        assert_floor_intact()
        self.cube = give(self.owner)
        self.duo = DuoBeta(matrix=self.matrix)
        # snap live surfaces into host
        self.matrix.snap(
            SnapCandidate(
                name="PlaneSurface",
                kind="tool",
                manifest=manifest_from_dell(15, "Plane"),
                payload={"module": "form.dell_matrix.plane"},
            )
        )
        self.matrix.snap(
            SnapCandidate(
                name="MainField",
                kind="main",
                manifest=manifest_from_dell(21, "MainThird"),
                payload={"module": "form.dell_matrix.main_field"},
            )
        )
        self.matrix.snap(
            SnapCandidate(
                name="BlankCube",
                kind="cube",
                manifest=manifest_from_dell(8, "BlankCube"),
                payload={"owner": self.owner},
            )
        )
        self.duo.evolve("01[Initiate] > 15[Map] >> 09[Show] :: Open")

    def place(self, id: str, label: str, **kwargs):
        return self.cube.place_idea(id, label, **kwargs)

    def set_perspective(self, name: str) -> bool:
        try:
            self.cube.session.plane.set_perspective(Perspective(name))
            return True
        except Exception:
            return False

    def box(self, unit_ids: List[str], sandbox_id: str = "box1"):
        return self.cube.session.plane.box(unit_ids, sandbox_id)

    def sync_with(self, other: "Program", unit_self: str, unit_other: str) -> Dict[str, Any]:
        return sync_planes(
            self.cube.session,
            other.cube.session,
            self.main,
            unit_self,
            unit_other,
        )

    def pull(self, unit_id: str, tag: str) -> Dict[str, Any]:
        return voluntary_pull(self.cube.session, unit_id, self.main, tag)

    def grow(self, n: int = 1) -> None:
        for _ in range(max(1, n)):
            self.duo.evolve("13[Loop] > 04[Transform] :: Open.grow")

    def render(self) -> str:
        lines = [
            f"+- DellMatrix PROGRAM · owner={self.owner} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| dells={len(DELLS)}  gen={self.duo.generation}",
            f"| Main contributions={len(self.main.contributions)} tags={len(self.main.tags)}",
            f"| ports={self.matrix.understand().get('ports', {})}",
            "| -- personal plane --",
        ]
        # reuse plane render body
        plane_txt = self.cube.session.plane.render()
        for ln in plane_txt.splitlines():
            if ln.startswith("+-"):
                continue
            lines.append(ln if ln.startswith("|") else f"| {ln}")
        lines.append("+" + "-" * 48 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "owner": self.owner,
            "floor": floor_status(),
            "dell_count": len(DELLS),
            "matrix": self.matrix.understand(),
            "main": self.main.understand(),
            "cube": self.cube.status(),
            "duo": self.duo.understand_self(),
        }


def open_program(owner: str = "Operator") -> Program:
    return Program(owner=owner)


def smoke() -> bool:
    print("=== ONE PROGRAM BOOT SMOKE ===")
    r: List[bool] = []

    def rec(name: str, ok: bool, detail: str = "") -> None:
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("Ace")
    rec("open", p.owner == "Ace")
    rec("floor", p.status()["floor"]["locked"] is True)
    rec("dells", p.status()["dell_count"] == 51)
    p.place("biz", "Business", words="US&S", skin=Skin.BUILDING, x=1)
    rec("place", "biz" in p.cube.session.plane.units)
    rec("perspective", p.set_perspective("page"))
    p2 = open_program("Friend")
    p2.place("art", "Art", words="logo", skin=Skin.SPHERE)
    before = p.cube.session.plane.units["biz"].words
    out = p.sync_with(p2, "biz", "art")
    rec("sync Main", out.get("ok") is True and p.cube.session.plane.units["biz"].words == before)
    rec("main non-empty", len(p.main.contributions) >= 1)
    p.grow(1)
    rec("duo gen", p.duo.generation >= 2)
    rec("render", "DellMatrix PROGRAM" in p.render() and "LOCKED" in p.render())
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Operator"
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    print("01[Initiate] > 15[Map] >> 09[Show] :: Open")
    print("English: One program boot.\n")
    p = open_program(owner)
    p.place("seed", "First", words="on the plane", skin=Skin.SEED)
    print(p.render())
    print("\n09[Show] :: status (compact)")
    st = p.status()
    print(
        json.dumps(
            {
                "owner": st["owner"],
                "floor": st["floor"],
                "dell_count": st["dell_count"],
                "ports": st["matrix"].get("ports"),
                "main": st["main"],
                "gen": st["duo"].get("generation"),
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
