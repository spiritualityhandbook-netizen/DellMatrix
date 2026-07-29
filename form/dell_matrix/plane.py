#!/usr/bin/env python3
"""
Dell Matrix Plane — first working surface.

08[Create] >> 15[Map] : 09[Show] :: Plane

- Geometric plane (table-like)
- Place units (concepts) with perception skins
- Perspectives: table | page | cube | circle | flower | sphere
- Connected vs sandbox (box)
- Same foundation; display changes, unit identity stays

Run:
  python -m form.dell_matrix.plane
  python -m form.dell_matrix.plane --demo
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
import json
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
    TABLE = "table"       # standing before plane
    PAGE = "page"         # top-down like a page
    CUBE = "cube"         # cube-based layout
    CIRCLE = "circle"     # circular plane
    FLOWER = "flower"     # flower of life / vesica relations
    SPHERE = "sphere"     # expanded field


class Skin(str, Enum):
    """Perception only — unit identity unchanged."""
    CUBE = "cube"
    SPHERE = "sphere"
    SEED = "seed"
    FLOWER = "flower"
    BUILDING = "building"
    WORDS = "words"
    CIRCLE = "circle"


@dataclass
class Unit:
    """An idea/concept on the plane."""

    id: str
    label: str
    words: str = ""
    skin: Skin = Skin.CUBE
    x: float = 0.0
    y: float = 0.0
    sandboxed: bool = False  # box/void — no enhance outside
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
    """Dell Matrix as geometric plane."""

    perspective: Perspective = Perspective.TABLE
    zoom_target: Optional[str] = None  # unit id or None = overview
    units: Dict[str, Unit] = field(default_factory=dict)
    sandboxes: Dict[str, Sandbox] = field(default_factory=dict)
    focus: Optional[str] = None

    def __post_init__(self):
        assert_floor_intact()

    # --- place / move ---
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

    # --- sandbox (box / void) ---
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

    # --- perspective / zoom ---
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

    # --- resonance scope ---
    def enhance_scope(self, unit_id: str) -> List[str]:
        """Who this unit can enhance (connected plane vs sandbox only)."""
        u = self.units.get(unit_id)
        if not u:
            return []
        if u.sandboxed and u.sandbox_id:
            sb = self.sandboxes.get(u.sandbox_id)
            return [m for m in (sb.member_ids if sb else []) if m != unit_id]
        # connected: all non-sandboxed others
        return [i for i, o in self.units.items() if i != unit_id and not o.sandboxed]

    def relation_middle(self, left_id: str, right_id: str) -> Dict[str, Any]:
        """Vesica-style middle relation sketch (flower perspective)."""
        a, b = self.units.get(left_id), self.units.get(right_id)
        if not a or not b:
            return {"ok": False}
        return {
            "ok": True,
            "left": a.label,
            "right": b.label,
            "middle": f"relation({a.label}⊗{b.label})",
            "note": "Flower/Vesica view — shared middle from two centers",
        }

    # --- render (ASCII stand-in for real UI) ---
    def render(self) -> str:
        lines = [
            f"+- DellMatrix PLANE · perspective={self.perspective.value} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| zoom={'overview' if not self.zoom_target else self.zoom_target}",
        ]
        if self.zoom_target and self.zoom_target in self.units:
            u = self.units[self.zoom_target]
            lines.append(f"| PAGE/CELL: {u.label} skin={u.skin.value}")
            lines.append(f"| words: {u.words or '(empty)'}")
            lines.append(f"| enhance → {self.enhance_scope(u.id)}")
        else:
            if self.perspective == Perspective.PAGE:
                lines.append("| view: top-down page (cells as squares)")
            elif self.perspective == Perspective.CIRCLE:
                lines.append("| view: circular plane")
            elif self.perspective == Perspective.FLOWER:
                lines.append("| view: flower / vesica relations")
            elif self.perspective == Perspective.SPHERE:
                lines.append("| view: expanded sphere field")
            elif self.perspective == Perspective.CUBE:
                lines.append("| view: cube-based grid")
            else:
                lines.append("| view: table plane (place units)")
            for u in self.units.values():
                lines.append(f"|  · {u.display()}")
            for sb in self.sandboxes.values():
                lines.append(f"|  box {sb.id}: {sb.member_ids}")
        lines.append("+" + "-" * 48 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "perspective": self.perspective.value,
            "zoom": self.zoom_target,
            "units": {i: u.display() for i, u in self.units.items()},
            "sandboxes": {i: sb.member_ids for i, sb in self.sandboxes.items()},
            "floor": list(FLOOR),
        }


def demo() -> None:
    print("08[Create] >> 15[Map] : 09[Show] :: Plane")
    print("English: Dell Matrix plane — place units, change perspective, box sandbox.\n")
    p = Plane()
    p.place("biz", "Business", words="stain-seal routes CRM", skin=Skin.BUILDING, x=1, y=0)
    p.place("music", "Music", words="Bombs Away ep4", skin=Skin.SEED, x=-1, y=0)
    p.place("cube1", "HarmonicCube", words="core concept", skin=Skin.CUBE, x=0, y=1)
    print(p.render())
    print()
    p.set_perspective(Perspective.PAGE)
    p.zoom_in("biz")
    print("09[Show] :: zoom page into Business")
    print(p.render())
    print()
    p.zoom_out()
    p.set_perspective(Perspective.FLOWER)
    print("09[Show] :: flower / vesica middle")
    print(p.relation_middle("biz", "music"))
    print()
    p.box(["cube1"], "sandbox_A")
    print("23[Lock] :: box HarmonicCube — no outside enhance")
    print("enhance music →", p.enhance_scope("music"))
    print("enhance cube1 →", p.enhance_scope("cube1"))
    print()
    p.set_skin("biz", Skin.SPHERE)
    p.set_perspective(Perspective.TABLE)
    print("04[Transform] :: Business skin cube→sphere (same unit)")
    print(p.render())
    print()
    print("09[Show] :: status")
    print(json.dumps(p.status(), indent=2))


def smoke() -> bool:
    print("=== PLANE SMOKE ===")
    r = []

    def rec(n, ok, d=""):
        print(f"[{len(r)+1}] {n}: {'PASS' if ok else 'FAIL'}" + (f" | {d}" if d else ""))
        r.append(bool(ok))

    p = Plane()
    p.place("a", "A", skin=Skin.CUBE)
    p.place("b", "B", skin=Skin.CIRCLE, x=1)
    rec("place", "a" in p.units and "b" in p.units)
    rec("skin change", p.set_skin("a", Skin.SPHERE) and p.units["a"].skin == Skin.SPHERE)
    rec("perspective", (p.set_perspective(Perspective.CIRCLE) or True) and p.perspective == Perspective.CIRCLE)
    rec("zoom", p.zoom_in("a") and p.zoom_target == "a")
    p.zoom_out()
    rec("enhance connected", set(p.enhance_scope("a")) == {"b"})
    p.box(["a", "b"], "s1")
    rec("sandbox", p.units["a"].sandboxed and "b" in p.enhance_scope("a"))
    p.unbox("a")
    rec("unbox", not p.units["a"].sandboxed)
    rec("floor", p.status()["floor"] == list(FLOOR))
    rec("vesica", p.relation_middle("a", "b").get("ok") is True)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
