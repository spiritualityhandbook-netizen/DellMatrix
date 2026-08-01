#!/usr/bin/env python3
"""One program — Form front door with Avatar + Ringed Growth Nursery + HarmonicLattice."""

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
    from form.dell_matrix.main_field import MainField
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.dell_matrix.sandbox_gate import SandboxGate
    from form.dell_matrix.nursery import Nursery
    from form.dell_matrix.ringed_growth import RingedGrowth
    from form.dell_matrix.harmonic_lattice import HarmonicLattice
    from form.dell_matrix.perception import Form
    from form.duobeta.growth import DuoBeta
    from form.avatar import Avatar, FaceController, Expression, build_default_registry
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact, floor_status
    from form.mandell.manifest import manifest_from_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.main_field import MainField
    from form.dell_matrix.blank_cube import give, BlankCube
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.dell_matrix.ambient_gate import AmbientGate
    from form.dell_matrix.sandbox_gate import SandboxGate
    from form.dell_matrix.nursery import Nursery
    from form.dell_matrix.ringed_growth import RingedGrowth
    from form.dell_matrix.harmonic_lattice import HarmonicLattice
    from form.dell_matrix.perception import Form
    from form.duobeta.growth import DuoBeta
    from form.avatar import Avatar, FaceController, Expression, build_default_registry


@dataclass
class Program:
    owner: str = "Operator"
    matrix: DellMatrix = field(default_factory=DellMatrix)
    main: MainField = field(default_factory=MainField)
    enhance: EnhanceGate = field(default_factory=EnhanceGate)
    ambient: AmbientGate = field(default_factory=AmbientGate)
    sandbox: SandboxGate = field(default_factory=SandboxGate)
    network_url: str = ""
    cube: BlankCube = field(init=False)
    duo: DuoBeta = field(init=False)
    avatar: Avatar = field(init=False)
    face: FaceController = field(init=False)
    kaomoji: Any = field(init=False)
    nursery: Nursery = field(init=False)
    growth: RingedGrowth = field(init=False)
    lattice: HarmonicLattice = field(init=False)
    history: List[str] = field(default_factory=list)
    history_max: int = 24

    def __post_init__(self):
        assert_floor_intact()
        self.cube = give(self.owner)
        self.duo = DuoBeta(matrix=self.matrix)
        self.avatar = Avatar(name=self.owner)
        self.face = FaceController()
        self.kaomoji = build_default_registry()
        self.nursery = Nursery.load()
        self.growth = RingedGrowth(nursery=self.nursery)
        self.lattice = HarmonicLattice(size=12)
        for name, kind, dell, term in (
            ("PlaneSurface", "tool", 15, "Plane"),
            ("MainField", "main", 21, "MainThird"),
            ("BlankCube", "cube", 8, "BlankCube"),
            ("GraphView", "tool", 9, "GraphView"),
            ("EnhanceGate", "tool", 32, "EnhanceGate"),
            ("Persist", "tool", 10, "Persist"),
            ("Visual", "tool", 9, "Visual"),
            ("Nursery", "growth", 23, "Nursery"),
            ("RingedGrowth", "growth", 13, "RingedGrowth"),
            ("Avatar", "entity", 2, "Avatar"),
            ("HarmonicLattice", "lattice", 15, "Lattice"),
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

    def note(self, action: str) -> None:
        """Macro Dell 48 — record last actions as reusable history."""
        self.history.append(action[:120])
        if len(self.history) > self.history_max:
            self.history = self.history[-self.history_max :]

    def macro_seed(self, n: int = 5) -> str:
        """Build a compact seed from last N actions."""
        recent = self.history[-max(1, n) :]
        if not recent:
            return "48[Macro] :: empty"
        body = " > ".join(recent)
        return f"48[Macro] :: {body}"[:200]

    def distill_label(self, text: str) -> str:
        """Dell 38 — compress words into a short label."""
        tokens = [t for t in (text or "").replace("_", " ").split() if len(t) > 2]
        if not tokens:
            return "distill"
        # keep distinctive tokens, max 4
        seen = []
        for t in tokens:
            tl = t.lower()
            if tl not in seen:
                seen.append(tl)
            if len(seen) >= 4:
                break
        return "_".join(seen)[:40]

    def avatar_status(self) -> Dict[str, Any]:
        return {
            "body": self.avatar.status(),
            "face": self.face.status(),
            "describe": self.avatar.describe(),
            "look": self.face.show(),
        }

    def place(self, id: str, label: str, **kwargs):
        u = self.cube.place_idea(id, label, **kwargs)
        self.sandbox.maybe_auto_box(self.cube.session.plane, id)
        try:
            h = int(round(getattr(u, "x", 0) or 0))
            v = int(round(getattr(u, "y", 0) or 0))
            self.lattice.put(
                h, v, 0,
                content=id,
                label=label,
                tags=["idea"] + ([kwargs.get("words")] if kwargs.get("words") else []),
            )
        except Exception:
            pass
        self.note(f"08[Create]::{label}")
        return u

    def grow_ideas(self, cycles: int = 1) -> Dict[str, Any]:
        if not self.enhance.on:
            self.enhance.turn_on()
        result = self.growth.run(self.cube.session.plane, cycles=cycles)
        self.duo.evolve(f"13[Loop] :: RingedGrow x{cycles}")
        self.note(f"13[Loop]::growx{cycles}")
        return result

    def list_proposals(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.nursery.pending()]

    def confirm_proposal(self, pid: str) -> Dict[str, Any]:
        prop = self.nursery.confirm(pid)
        if not prop:
            return {"ok": False, "reason": "not found or not pending"}
        self.place(prop.id, prop.label, words=prop.words, skin=Skin.SEED)
        self.note(f"50[Manifest]::{prop.label}")
        return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind}

    def reject_proposal(self, pid: str) -> Dict[str, Any]:
        prop = self.nursery.reject(pid)
        if not prop:
            return {"ok": False, "reason": "not found or not pending"}
        self.note(f"24[Unlock]::reject")
        return {"ok": True, "id": prop.id, "label": prop.label}

    def sandbox_on(self, all_units: bool = True) -> Dict[str, Any]:
        if all_units:
            return self.sandbox.apply_on(self.cube.session.plane)
        self.sandbox.turn_on()
        return {"ok": True, "on": True}

    def sandbox_off(self) -> Dict[str, Any]:
        return self.sandbox.apply_off(self.cube.session.plane)

    def enhance_on(self) -> None:
        self.enhance.turn_on()

    def enhance_off(self) -> None:
        self.enhance.turn_off()

    def pulse(self) -> Dict[str, Any]:
        return self.enhance.pulse(self.cube.session.plane)

    def scores(self) -> Dict[str, float]:
        return dict(self.enhance.state.scores)

    def save(self, path: Optional[str] = None) -> str:
        from form.persist import save as persist_save
        self.nursery.save()
        self.note("10[Keep]")
        return persist_save(self, path)

    def visual(self) -> Dict[str, str]:
        from form.dell_matrix.visual import write_visual
        self.note("09[Show]>>47[Embed]")
        return write_visual(
            self.cube.session.plane,
            owner=self.owner,
            scores=self.scores(),
            avatar=self.avatar_status(),
            nursery=self.list_proposals(),
            rings=list(self.duo.rings),
            form=self.lattice.perception.form.value,
            skin=self.lattice.perception.skin_name(),
        )

    @staticmethod
    def load(owner: str = "Operator", path: Optional[str] = None) -> "Program":
        from form.persist import load as persist_load
        return persist_load(owner, path)

    def render(self) -> str:
        scores = self.scores()
        plane_txt = self.cube.session.plane.render(scores=scores)
        av = self.avatar_status()
        ns = self.nursery.summary()
        form_name = self.lattice.perception.form.value
        lines = [
            f"+- DellMatrix · owner={self.owner} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| {av['look']}  {av['describe']}",
            f"| ideas={len(self.cube.session.plane.units)}  nursery={ns['pending']}  gen={self.duo.generation}",
            f"| lattice form={form_name} cells={len(self.lattice.cells)}  size={self.lattice.size}",
            f"| rings: {' → '.join(self.duo.rings)}  (Voynich-inspired)",
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
            "avatar": self.avatar_status(),
            "nursery": self.nursery.summary(),
            "ideas": len(self.cube.session.plane.units),
            "rings": list(self.duo.rings),
            "enhance": self.enhance.status(),
            "lattice": self.lattice.status(),
            "history_len": len(self.history),
        }


def open_program(owner: str = "Operator") -> Program:
    return Program(owner=owner)


def smoke() -> bool:
    print("=== OPEN SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    p = open_program("Smoke")
    p.place("a", "A", words="one")
    p.place("b", "B", words="two")
    out = p.grow_ideas(1)
    rec("grow", out.get("ok") is True)
    rec("lattice bound", hasattr(p, "lattice") and p.lattice is not None)
    rec("lattice cells", len(p.lattice.cells) >= 2)
    rec("history", len(p.history) >= 2)
    rec("macro", p.macro_seed(3).startswith("48[Macro]"))
    paths = p.visual()
    rec("visual", "html" in paths)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print(open_program().render())


if __name__ == "__main__":
    main()
