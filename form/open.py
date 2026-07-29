#!/usr/bin/env python3
"""One program — SUS open with full required snaps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField, sync_planes, voluntary_pull
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.dell_matrix.sandbox_gate import SandboxGate
    from form.dell_matrix.idea_grow import IdeaGrow
    from form.duobeta.growth import DuoBeta
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField, sync_planes, voluntary_pull
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.graph_view import build_view
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.dell_matrix.sandbox_gate import SandboxGate
    from form.dell_matrix.idea_grow import IdeaGrow
    from form.duobeta.growth import DuoBeta


@dataclass
class Program:
    owner: str = "Operator"
    matrix: DellMatrix = field(default_factory=DellMatrix)
    main: MainField = field(default_factory=MainField)
    enhance: EnhanceGate = field(default_factory=EnhanceGate)
    ambient: AmbientGate = field(default_factory=AmbientGate)
    sandbox: SandboxGate = field(default_factory=SandboxGate)
    idea_grow: IdeaGrow = field(default_factory=IdeaGrow)
    network_url: str = ""
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
            ("IdeaGrow", "growth", 13, "IdeaGrow"),
            ("SandboxGate", "tool", 23, "SandboxGate"),
            ("NetworkMain", "main", 21, "NetworkMain"),
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
        u = self.cube.place_idea(id, label, **kwargs)
        self.sandbox.maybe_auto_box(self.cube.session.plane, id)
        return u

    def sandbox_on(self, all_units: bool = True) -> Dict[str, Any]:
        if all_units:
            return self.sandbox.apply_on(self.cube.session.plane)
        self.sandbox.turn_on()
        return {"ok": True, "on": True}

    def sandbox_off(self) -> Dict[str, Any]:
        return self.sandbox.apply_off(self.cube.session.plane)

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

    def grow_ideas(self, cycles: int = 1) -> List[Dict[str, Any]]:
        self.idea_grow.gate = self.enhance
        if not self.enhance.on:
            self.enhance.turn_on()
        out = self.idea_grow.run(self.cube.session.plane, cycles=cycles)
        self.duo.evolve(f"13[Loop] :: IdeaGrow x{cycles}")
        return out

    def ambient_intake(self, apply: bool = True) -> Dict[str, Any]:
        out = self.ambient.intake()
        if not out.get("ok") or not apply:
            return out
        placed = []
        for it in out.get("items", []):
            self.place(it["id"], it["label"], words=it.get("words", ""), skin=Skin.WORDS)
            placed.append(it["id"])
        out["placed"] = placed
        return out

    def set_network(self, url: str) -> None:
        self.network_url = url.rstrip("/")

    def net_push(self) -> Dict[str, Any]:
        if not self.network_url:
            return {"ok": False, "error": "set network_url first"}
        from form.dell_matrix.network_main import client_push

        return client_push(self.network_url, dict(self.main.tags), self.owner)

    def net_pull(self, mode: str = "merge") -> Dict[str, Any]:
        if not self.network_url:
            return {"ok": False, "error": "set network_url first"}
        from form.dell_matrix.network_main import pull_into_local

        return pull_into_local(self.main, self.network_url, mode=mode)

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
            f"| enhance={'ON' if self.enhance.on else 'OFF'} sandbox={'ON' if self.sandbox.on else 'OFF'} ambient={'ON' if self.ambient.master_on else 'OFF'} gen={self.duo.generation}",
            f"| net={self.network_url or 'off'} main top: {self.main.top_tags(3)}",
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
            "sandbox": self.sandbox.status(),
            "ambient": self.ambient.status(),
            "network_url": self.network_url,
            "idea_grow": self.idea_grow.summary(),
            "scores": self.scores(),
            "main": self.main.summary(),
            "shared_main": self.shared_main_summary(),
            "verify": self.matrix.verify(),
            "matrix": self.matrix.understand(),
            "view": self.view(),
        }


def open_program(owner: str = "Operator") -> Program:
    return Program(owner=owner)


def smoke() -> bool:
    print("=== OPEN SUS SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("OpenSUS")
    v = p.matrix.verify()
    rec("verify required", v.get("ok") is True, str(v.get("missing")))
    rec("sandbox default off", p.sandbox.on is False)
    rec("enhance default off", p.enhance.on is False)
    rec("ambient default off", p.ambient.master_on is False)
    p.place("a", "A", words="one")
    p.place("b", "B", words="two", x=1)
    out = p.grow_ideas(2)
    rec("grow ideas", all(o.get("ok") for o in out))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print(open_program().render())


if __name__ == "__main__":
    main()
