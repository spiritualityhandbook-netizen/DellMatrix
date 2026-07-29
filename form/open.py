#!/usr/bin/env python3
"""One program — AmbientGate skeleton + shared snapshot (NBD x10)."""

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
    from form.dell_matrix.ambient_gate import AmbientGate
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
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.duobeta.growth import DuoBeta


@dataclass
class Program:
    owner: str = "Operator"
    matrix: DellMatrix = field(default_factory=DellMatrix)
    main: MainField = field(default_factory=MainField)
    enhance: EnhanceGate = field(default_factory=EnhanceGate)
    ambient: AmbientGate = field(default_factory=AmbientGate)
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
            ("Visual", "tool", 9, "Visual"),
            ("SharedMain", "main", 21, "SharedMain"),
            ("AmbientGate", "tool", 32, "AmbientGate"),
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

    def push_main(self, path: Optional[str] = None) -> Dict[str, Any]:
        from form.dell_matrix.shared_main import push_to_shared, DEFAULT_SHARED

        return push_to_shared(self.main, self.owner, path or DEFAULT_SHARED)

    def pull_main(self, path: Optional[str] = None, mode: str = "merge") -> Dict[str, Any]:
        from form.dell_matrix.shared_main import pull_from_shared, DEFAULT_SHARED

        return pull_from_shared(self.main, path or DEFAULT_SHARED, mode=mode, owner=self.owner)

    def snapshot_main(self) -> str:
        from form.dell_matrix.shared_main import snapshot

        return snapshot()

    def shared_main_summary(self) -> Dict[str, Any]:
        from form.dell_matrix.shared_main import shared_summary

        return shared_summary()

    def grow(self, n: int = 1) -> None:
        for _ in range(max(1, n)):
            self.duo.evolve("13[Loop] > 04[Transform] :: Open.grow")

    def view(self) -> Dict[str, Any]:
        return build_view(self.cube.session.plane, scores=self.scores()).to_dict()

    def scores(self) -> Dict[str, float]:
        return dict(self.enhance.state.scores)

    def save(self, path: Optional[str] = None) -> str:
        from form.persist import save as persist_save

        return persist_save(self, path)

    def checkpoint(self) -> str:
        from form.persist import checkpoint as persist_cp

        return persist_cp(self)

    def visual(self) -> Dict[str, str]:
        from form.dell_matrix.visual import write_visual

        return write_visual(self.cube.session.plane, owner=self.owner, scores=self.scores())

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
            f"| enhance={'ON' if self.enhance.on else 'OFF'} ambient={'ON' if self.ambient.master_on else 'OFF'} gen={self.duo.generation}",
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
            "ambient": self.ambient.status(),
            "scores": self.scores(),
            "main": self.main.summary(),
            "shared_main": self.shared_main_summary(),
            "matrix": self.matrix.understand(),
            "view": self.view(),
        }


def open_program(owner: str = "Operator") -> Program:
    return Program(owner=owner)


def smoke() -> bool:
    print("=== OPEN NBD x10 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("NBD10")
    rec("ambient default off", p.ambient.master_on is False)
    rec("AmbientGate snap", p.matrix.has_snap("AmbientGate"))
    rec("view scores key", "score" in p.view()["nodes"][0] if p.view()["nodes"] else True)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    owner = "Operator"
    for i, a in enumerate(sys.argv):
        if a == "--owner" and i + 1 < len(sys.argv):
            owner = sys.argv[i + 1]
    p = open_program(owner)
    print(p.render())


if __name__ == "__main__":
    main()
