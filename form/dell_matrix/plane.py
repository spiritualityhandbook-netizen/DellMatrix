#!/usr/bin/env python3
"""
Dell Matrix Plane — L3 surface.

08[Create] >> 15[Map] : 09[Show] :: Plane

Geometric plane + perspectives + skins + sandbox + richer page/zoom layouts.

Run:
  python -m form.dell_matrix.plane --smoke
  python -m form.dell_matrix.plane --demo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import json
import math
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest


class Perspective(str, Enum):
    TABLE = "table"
    PAGE = "page"
    CUBE = "cube"
    CIRCLE = "circle"
    FLOWER = "flower"
    SPHERE = "sphere"


class Skin(str, Enum):
    CUBE = "cube"
    SPHERE = "sphere"
    SEED = "seed"
    FLOWER = "flower"
    BUILDING = "building"
    WORDS = "words"
    CIRCLE = "circle"


@dataclass
class Unit:
    id: str
    label: str
    words: str = ""
    skin: Skin = Skin.CUBE
    x: float = 0.0
    y: float = 0.0
    sandboxed: bool = False
    sandbox_id: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None

    def display(self) -> str:
        box = f"[box:{self.sandbox_id}]" if self.sandboxed else "[connected]"
        return f"{self.skin.value}:{self.label}@{self.x:.1f},{self.y:.1f}{box}"


@dataclass
class Sandbox:
    id: str
    label: str = "sandbox"
    member_ids: List[str] = field(default_factory=list)


@dataclass
class Plane:
    """Dell Matrix as geometric plane (L3)."""

    perspective: Perspective = Perspective.TABLE
    zoom_target: Optional[str] = None
    units: Dict[str, Unit] = field(default_factory=dict)
    sandboxes: Dict[str, Sandbox] = field(default_factory=dict)
    focus: Optional[str] = None
    level: int = 3

    def __post_init__(self):
        assert_floor_intact()

    def place(
        self,
        id: str,
        label: str,
        *,
        words: str = "",
        skin: Skin = Skin.CUBE,
        x: float = 0.0,
        y: float = 0.0,
        manifest: Optional[Manifest] = None,
    ) -> Unit:
        u = Unit(
            id=id,
            label=label,
            words=words,
            skin=skin,
            x=x,
            y=y,
            manifest=manifest.to_dict() if manifest else None,
        )
        self.units[id] = u
        return u

    def remove(self, id: str) -> bool:
        if id not in self.units:
            return False
        self.unbox(id)
        del self.units[id]
        if self.zoom_target == id:
            self.zoom_out()
        return True

    def move(self, id: str, x: float, y: float) -> bool:
        u = self.units.get(id)
        if not u:
            return False
        u.x, u.y = x, y
        return True

    def set_skin(self, id: str, skin: Skin) -> bool:
        u = self.units.get(id)
        if not u:
            return False
        u.skin = skin
        return True

    def box(self, unit_ids: List[str], sandbox_id: str = "box1") -> Sandbox:
        sb = self.sandboxes.get(sandbox_id) or Sandbox(id=sandbox_id)
        for uid in unit_ids:
            u = self.units.get(uid)
            if not u:
                continue
            u.sandboxed = True
            u.sandbox_id = sandbox_id
            if uid not in sb.member_ids:
                sb.member_ids.append(uid)
        self.sandboxes[sandbox_id] = sb
        return sb

    def unbox(self, unit_id: str) -> bool:
        u = self.units.get(unit_id)
        if not u:
            return False
        sid = u.sandbox_id
        u.sandboxed = False
        u.sandbox_id = None
        if sid and sid in self.sandboxes:
            self.sandboxes[sid].member_ids = [
                m for m in self.sandboxes[sid].member_ids if m != unit_id
            ]
        return True

    def set_perspective(self, p: Perspective) -> None:
        self.perspective = p

    def zoom_in(self, unit_id: str) -> bool:
        if unit_id not in self.units:
            return False
        self.zoom_target = unit_id
        self.focus = unit_id
        return True

    def zoom_out(self) -> None:
        self.zoom_target = None
        self.focus = None

    def enhance_scope(self, unit_id: str) -> List[str]:
        u = self.units.get(unit_id)
        if not u:
            return []
        if u.sandboxed and u.sandbox_id:
            sb = self.sandboxes.get(u.sandbox_id)
            return [m for m in (sb.member_ids if sb else []) if m != unit_id]
        return [i for i, o in self.units.items() if i != unit_id and not o.sandboxed]

    def neighbors(self, unit_id: str, radius: float = 2.0) -> List[str]:
        """Spatial neighbors by Euclidean distance on the plane."""
        u = self.units.get(unit_id)
        if not u:
            return []
        out = []
        for i, o in self.units.items():
            if i == unit_id:
                continue
            d = math.hypot(o.x - u.x, o.y - u.y)
            if d <= radius:
                out.append(i)
        return out

    def relation_middle(self, left_id: str, right_id: str) -> Dict[str, Any]:
        a, b = self.units.get(left_id), self.units.get(right_id)
        if not a or not b:
            return {"ok": False}
        return {
            "ok": True,
            "left": a.label,
            "right": b.label,
            "middle": f"relation({a.label}⊗{b.label})",
            "distance": math.hypot(a.x - b.x, a.y - b.y),
            "note": "Flower/Vesica — shared middle from two centers",
        }

    def _layout_hint(self, u: Unit) -> str:
        """Perspective-specific coordinate readout."""
        if self.perspective == Perspective.CIRCLE:
            ang = math.degrees(math.atan2(u.y, u.x)) if (u.x or u.y) else 0.0
            rad = math.hypot(u.x, u.y)
            return f"θ={ang:.0f}° r={rad:.1f}"
        if self.perspective == Perspective.CUBE:
            return f"grid({int(round(u.x))},{int(round(u.y))})"
        if self.perspective == Perspective.SPHERE:
            return f"field({u.x:.1f},{u.y:.1f})"
        return f"({u.x:.1f},{u.y:.1f})"

    def render(self, scores: Optional[Dict[str, float]] = None) -> str:
        scores = scores or {}
        lines = [
            f"+- DellMatrix PLANE L{self.level} · perspective={self.perspective.value} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| zoom={'overview' if not self.zoom_target else self.zoom_target}  units={len(self.units)}",
        ]
        if self.zoom_target and self.zoom_target in self.units:
            u = self.units[self.zoom_target]
            lines.append(f"| —— PAGE / CELL ——")
            lines.append(f"| title: {u.label}")
            lines.append(f"| skin: {u.skin.value}  pos: {self._layout_hint(u)}")
            lines.append(f"| state: {'SANDBOX '+u.sandbox_id if u.sandboxed else 'CONNECTED'}")
            lines.append(f"| score: {scores.get(u.id, 0.0):.2f}")
            lines.append(f"| words:")
            text = u.words or "(empty)"
            for chunk in text.split("\n"):
                lines.append(f"|   {chunk}")
            lines.append(f"| enhance → {self.enhance_scope(u.id)}")
            lines.append(f"| neighbors → {self.neighbors(u.id)}")
        else:
            mode = {
                Perspective.PAGE: "top-down page (cells)",
                Perspective.CIRCLE: "circular plane",
                Perspective.FLOWER: "flower / vesica",
                Perspective.SPHERE: "expanded sphere field",
                Perspective.CUBE: "cube-based grid",
                Perspective.TABLE: "table plane",
            }.get(self.perspective, self.perspective.value)
            lines.append(f"| view: {mode}")
            # sort for stable overview
            for u in sorted(self.units.values(), key=lambda z: (z.y, z.x, z.id)):
                sc = scores.get(u.id)
                sc_s = f" sc={sc:.2f}" if sc is not None else ""
                lines.append(f"|  · {u.display()} {self._layout_hint(u)}{sc_s}")
            if self.perspective == Perspective.FLOWER and len(self.units) >= 2:
                ids = list(self.units.keys())
                rel = self.relation_middle(ids[0], ids[1])
                if rel.get("ok"):
                    lines.append(f"|  vesica: {rel['middle']}")
            for sb in self.sandboxes.values():
                lines.append(f"|  box {sb.id}: {sb.member_ids}")
        lines.append("+" + "-" * 52 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "perspective": self.perspective.value,
            "zoom": self.zoom_target,
            "unit_count": len(self.units),
            "units": {i: u.display() for i, u in self.units.items()},
            "sandboxes": {i: sb.member_ids for i, sb in self.sandboxes.items()},
            "floor": list(FLOOR),
        }


def smoke() -> bool:
    print("=== PLANE L3 SMOKE ===")
    r = []

    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))

    p = Plane()
    p.place("a", "A", words="line1\nline2", skin=Skin.CUBE)
    p.place("b", "B", skin=Skin.CIRCLE, x=1)
    rec("level 3", p.level == 3)
    rec("place", "a" in p.units)
    rec("neighbors", "b" in p.neighbors("a"))
    p.zoom_in("a")
    txt = p.render(scores={"a": 1.5})
    rec("page words", "line1" in txt and "line2" in txt)
    rec("page score", "1.50" in txt or "score: 1.5" in txt)
    p.zoom_out()
    p.set_perspective(Perspective.CIRCLE)
    rec("circle hint", "θ=" in p.render() or "r=" in p.render())
    p.remove("b")
    rec("remove", "b" not in p.units)
    rec("floor", p.status()["floor"] == list(FLOOR))
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("08[Create] >> 15[Map] : 09[Show] :: Plane L3")
    p = Plane()
    p.place("biz", "Business", words="stain-seal\nCRM routes", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    p.set_perspective(Perspective.PAGE)
    p.zoom_in("biz")
    print(p.render(scores={"biz": 2.0}))
    p.zoom_out()
    p.set_perspective(Perspective.FLOWER)
    print(p.render())


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
