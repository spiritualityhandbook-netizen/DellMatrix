#!/usr/bin/env python3
"""
One program boot — surface coherent (scores on render + persist pulls).

01[Initiate] > 15[Map] >> 09[Show] :: Open
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import json
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.registry import DELLS
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField, sync_planes, voluntary_pull
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.duobeta.growth import DuoBeta
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.registry import DELLS
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField, sync_planes, voluntary_pull
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.duobeta.growth import DuoBeta


@dataclass
class Program:
    owner: str = "Operator"
    matrix: DellMatrix = field(default_factory=DellMatrix)
    main: MainField = field(default_factory=MainField)
    enhance: EnhanceGate = field(default_factory=EnhanceGate)
    cube: BlankCube = field(init=False)
    duo: DuoBeta = field(init=False)

    def __post_init__(self):
        assert_floor_intact()
        self.cube = give(self.owner)
        self.duo = DuoBeta(matrix=self.matrix)
        for name, kind, dell, term in (
            ("PlaneSurface", "tool", 15, "Plane"),
            ("MainField", "main", 21, "MainThird"),
            ("BlankCube", "cube", 8, "BlankCube"),
            ("GraphView", "tool", 9, "GraphView"),
            ("EnhanceGate", "tool", 32, "EnhanceGate"),
            ("Persist", "tool", 10, "Persist"),
        ):
            self.matrix.snap(
                SnapCandidate(
                    name=name,
                    kind=kind,
                    manifest=manifest_from_dell(dell, term),
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

    def enhance_on(self) -> None:
        self.enhance.turn_on()

    def enhance_off(self) -> None:
        self.enhance.turn_off()

    def pulse(self) -> Dict[str, Any]:
        return self.enhance.pulse(self.cube.session.plane)

    def sync_with(self, other: "Program", unit_self: str, unit_other: str) -> Dict[str, Any]:
        return sync_planes(self.cube.session, other.cube.session, self.main, unit_self, unit_other)

    def pull(self, unit_id: str, tag: str) -> Dict[str, Any]:
        return voluntary_pull(self.cube.session, unit_id, self.main, tag)

    def grow(self, n: int = 1) -> None:
        for _ in range(max(1, n)):
            self.duo.evolve("13[Loop] > 04[Transform] :: Open.grow")

    def view(self) -> Dict[str, Any]:
        return build_view(self.cube.session.plane).to_dict()

    def scores(self) -> Dict[str, float]:
        return dict(self.enhance.state.scores)

    def save(self, path: Optional[str] = None) -> str:
        from form.persist import save as persist_save

        return persist_save(self, path)

    @staticmethod
    def load(owner: str = "Operator", path: Optional[str] = None) -> "Program":
        from form.persist import load as persist_load

        return persist_load(owner, path)

    def render(self) -> str:
        scores = self.scores()
        plane_txt = self.cube.session.plane.render(scores=scores)
        lines = [
            f"+- DellMatrix PROGRAM · owner={self.owner} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| enhance={'ON' if self.enhance.on else 'OFF'}  gen={self.duo.generation}  main={len(self.main.contributions)}",
            f"| main top: {self.main.top_tags(3)}",
        ]
        for ln in plane_txt.splitlines():
            if ln.startswith("+-"):
                continue
            lines.append(ln if ln.startswith("|") else f"| {ln}")
        lines.append("+" + "-" * 52 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "owner": self.owner,
            "floor": floor_status(),
            "enhance": self.enhance.status(),
            "scores": self.scores(),
            "main": self.main.summary(),
            "matrix": self.matrix.understand(),
            "view": self.view(),
        }


def open_program(owner: str = "Operator") -> Program:
    return Program(owner=owner)


def smoke() -> bool:
    print("=== SURFACE COHERENCE SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("Surface")
    p.place("biz", "Business", words="US&S", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    p.enhance_on()
    p.pulse()
    txt = p.render()
    rec("render has scores", "sc=" in txt or "score:" in txt, txt[0:200])
    rec("status scores", any(v > 0 for v in p.scores().values()))
    rec("main summary", "top_tags" in p.main.summary())
    path = p.save()
    p2 = Program.load("Surface")
    rec("load scores", any(v > 0 for v in p2.scores().values()) or p2.enhance.on)
    rec("verify open snaps", p.matrix.verify().get("ok") is True)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)

    owner = "Operator"
    do_load = "--load" in sys.argv
    do_save = "--save" in sys.argv
    do_pulse = "--pulse" in sys.argv
    do_enhance = "--enhance-on" in sys.argv
    do_json = "--json" in sys.argv

    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]

    print("01[Initiate] > 15[Map] >> 09[Show] :: Open")
    p = Program.load(owner) if do_load else open_program(owner)
    if not do_load and not any(u != "welcome" for u in p.cube.session.plane.units):
        p.place("seed", "First", words="on the plane", skin=Skin.SEED)
    if do_enhance:
        p.enhance_on()
    if do_pulse:
        print("pulse:", p.pulse())
    if do_save:
        print("10[Keep] ::", p.save())
    print(p.render())
    if do_json:
        print(json.dumps(p.view(), indent=2))


if __name__ == "__main__":
    main()
