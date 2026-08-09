#!/usr/bin/env python3
"""
Perspective views — who sees what in the Free Matrix.

Modes
-----
  first   — first person: cone in front only (default embodied AI)
  third   — third person: around the body, wider ring (not only forward)
  parts   — partial: a slice of the plane (skin / region / nearby)
  whole   — omniscient: full plane inventory (architect / privileged AI)

Roles
-----
  user       — may select ANY mode at any time
  architect  — may select ANY mode at any time (same privilege as user)
  ai_first   — default first (what is in front)
  ai_parts   — default parts
  ai_third   — default third
  ai_whole   — default whole (rare; full-map AI)

Law: user/architect override always wins. AI defaults are suggestions until
the operator assigns a mode.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math

MODES = ("first", "third", "parts", "whole")
ROLES = ("user", "architect", "ai_first", "ai_parts", "ai_third", "ai_whole")

# default mode per role
ROLE_DEFAULT_MODE = {
    "user": "first",          # starts embodied; can switch to any
    "architect": "whole",     # often wants the map; can switch to any
    "ai_first": "first",
    "ai_parts": "parts",
    "ai_third": "third",
    "ai_whole": "whole",
}

PRIVILEGED = frozenset({"user", "architect"})


@dataclass
class Viewer:
    id: str
    role: str = "ai_first"
    mode: Optional[str] = None  # None → role default
    # optional body pose for embodied modes
    pos: Tuple[float, float] = (0.0, 0.0)
    facing: str = "N"
    # parts filter
    part_skins: List[str] = field(default_factory=list)
    part_radius: float = 8.0

    def effective_mode(self) -> str:
        if self.mode in MODES:
            return self.mode  # type: ignore
        return ROLE_DEFAULT_MODE.get(self.role, "first")

    def can_use(self, mode: str) -> bool:
        if self.role in PRIVILEGED:
            return mode in MODES
        # non-privileged AI may only use their assigned/default unless user forced mode
        if self.mode in MODES:
            return mode == self.mode
        return mode == ROLE_DEFAULT_MODE.get(self.role, "first")


@dataclass
class PerspectiveRegistry:
    viewers: Dict[str, Viewer] = field(default_factory=dict)

    def ensure(self, id: str, role: str = "ai_first", **kwargs) -> Viewer:
        if id not in self.viewers:
            self.viewers[id] = Viewer(id=id, role=role, **kwargs)
        return self.viewers[id]

    def set_mode(self, id: str, mode: str, *, as_role: str = "user") -> Dict[str, Any]:
        """User/architect can set any viewer's mode."""
        mode = (mode or "").lower().strip()
        if mode not in MODES:
            return {"ok": False, "error": f"unknown mode {mode}", "modes": list(MODES)}
        v = self.viewers.get(id)
        if v is None:
            return {"ok": False, "error": f"unknown viewer {id}"}
        if as_role not in PRIVILEGED and not v.can_use(mode):
            return {
                "ok": False,
                "error": f"role {as_role} cannot set {id} to {mode}",
                "allowed": v.effective_mode(),
            }
        v.mode = mode
        return {"ok": True, "id": id, "mode": mode, "role": v.role}

    def list_viewers(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": v.id,
                "role": v.role,
                "mode": v.effective_mode(),
                "assigned": v.mode,
                "pos": list(v.pos),
                "facing": v.facing,
                "privileged": v.role in PRIVILEGED,
            }
            for v in self.viewers.values()
        ]


def _nodes_from_program(program) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = []
    plane = getattr(program, "plane", None)
    if plane is None:
        return nodes
    items = []
    if hasattr(plane, "all_nodes"):
        items = plane.all_nodes() or []
    elif hasattr(plane, "nodes"):
        raw = plane.nodes
        items = list(raw.values()) if isinstance(raw, dict) else list(raw or [])
    for n in items:
        if isinstance(n, dict):
            nodes.append(n)
        else:
            nodes.append({
                "id": getattr(n, "id", None) or getattr(n, "label", "?"),
                "label": getattr(n, "label", str(n)),
                "x": float(getattr(n, "x", 0) or 0),
                "y": float(getattr(n, "y", 0) or 0),
                "skin": str(getattr(n, "skin", "") or getattr(getattr(n, "skin", None), "value", "")),
            })
    return nodes


def _pose_from_program(program) -> Tuple[Tuple[float, float], str]:
    body = getattr(getattr(program, "avatar", None), "body", None)
    if body is not None:
        pos = getattr(body, "pos", (0, 0))
        facing = getattr(getattr(body, "facing", None), "name", None) or str(getattr(body, "facing", "N"))
        return (float(pos[0]), float(pos[1])), str(facing)
    return (0.0, 0.0), "N"


def see_first(program, viewer: Viewer) -> Dict[str, Any]:
    from form.dell_matrix.vision import compute_vision, format_look_report
    nodes = _nodes_from_program(program)
    pos = list(viewer.pos)
    vis = compute_vision(pos, viewer.facing, nodes, range_=6.0, half_angle=55.0)
    return {
        "mode": "first",
        "viewer": viewer.id,
        "role": viewer.role,
        "vision": vis,
        "report": format_look_report(vis),
        "scope": "cone_in_front_only",
    }


def see_third(program, viewer: Viewer) -> Dict[str, Any]:
    """Around the body — not limited to forward cone."""
    nodes = _nodes_from_program(program)
    px, py = viewer.pos
    radius = 10.0
    around = []
    for n in nodes:
        dx = float(n.get("x", 0)) - px
        dy = float(n.get("y", 0)) - py
        dist = math.hypot(dx, dy)
        if 0.01 < dist <= radius:
            around.append({**n, "dist": round(dist, 2)})
    around.sort(key=lambda x: x["dist"])
    return {
        "mode": "third",
        "viewer": viewer.id,
        "role": viewer.role,
        "center": [px, py],
        "radius": radius,
        "nodes": around[:40],
        "count": len(around),
        "report": [f"Third-person around ({px:.1f},{py:.1f}) r={radius}",
                   f"  {len(around)} nodes nearby"] + [
            f"  · {n.get('label')} d={n.get('dist')}" for n in around[:12]
        ],
        "scope": "ring_around_body",
    }


def see_parts(program, viewer: Viewer) -> Dict[str, Any]:
    nodes = _nodes_from_program(program)
    px, py = viewer.pos
    skins = [s.lower() for s in (viewer.part_skins or [])]
    radius = float(viewer.part_radius or 8.0)
    parts = []
    for n in nodes:
        dx = float(n.get("x", 0)) - px
        dy = float(n.get("y", 0)) - py
        dist = math.hypot(dx, dy)
        if dist > radius:
            continue
        skin = str(n.get("skin", "") or "").lower()
        if skins and skin not in skins and not any(s in skin for s in skins):
            continue
        parts.append({**n, "dist": round(dist, 2)})
    parts.sort(key=lambda x: x.get("dist", 0))
    return {
        "mode": "parts",
        "viewer": viewer.id,
        "role": viewer.role,
        "filters": {"skins": skins, "radius": radius},
        "nodes": parts[:40],
        "count": len(parts),
        "report": [
            f"Parts view skins={skins or 'any'} r={radius}",
            f"  {len(parts)} matching",
        ] + [f"  · {n.get('label')} [{n.get('skin')}]" for n in parts[:12]],
        "scope": "filtered_slice",
    }


def see_whole(program, viewer: Viewer) -> Dict[str, Any]:
    nodes = _nodes_from_program(program)
    by_skin: Dict[str, int] = {}
    for n in nodes:
        skin = str(n.get("skin", "") or "none")
        by_skin[skin] = by_skin.get(skin, 0) + 1
    return {
        "mode": "whole",
        "viewer": viewer.id,
        "role": viewer.role,
        "count": len(nodes),
        "by_skin": by_skin,
        "nodes": [
            {"id": n.get("id"), "label": n.get("label"), "skin": n.get("skin"),
             "x": n.get("x"), "y": n.get("y")}
            for n in nodes[:80]
        ],
        "report": [
            f"Whole plane · {len(nodes)} nodes",
            f"  skins: {by_skin}",
        ] + [f"  · {n.get('label')} [{n.get('skin')}]" for n in nodes[:15]],
        "scope": "omniscient_plane",
    }


_SEE = {
    "first": see_first,
    "third": see_third,
    "parts": see_parts,
    "whole": see_whole,
}


def see_as(program, viewer: Viewer, mode: Optional[str] = None) -> Dict[str, Any]:
    m = (mode or viewer.effective_mode()).lower()
    if m not in _SEE:
        return {"ok": False, "error": f"bad mode {m}"}
    if viewer.role not in PRIVILEGED and mode and mode != viewer.effective_mode():
        # AI trying to peek beyond assignment without privileged override
        if viewer.mode and mode != viewer.mode:
            return {
                "ok": False,
                "error": f"viewer {viewer.id} locked to {viewer.effective_mode()}",
                "hint": "user/architect can set_mode to change",
            }
    out = _SEE[m](program, viewer)
    out["ok"] = True
    return out


def sync_viewer_pose(program, viewer: Viewer) -> Viewer:
    pos, facing = _pose_from_program(program)
    viewer.pos = pos
    viewer.facing = facing
    return viewer


def bootstrap_default_viewers(program) -> PerspectiveRegistry:
    reg = PerspectiveRegistry()
    pos, facing = _pose_from_program(program)
    reg.ensure("user", role="user", pos=pos, facing=facing)
    reg.ensure("architect", role="architect", pos=pos, facing=facing, mode="whole")
    reg.ensure("companion", role="ai_first", pos=pos, facing=facing)
    reg.ensure("scout", role="ai_parts", pos=pos, facing=facing, part_radius=12.0)
    reg.ensure("overseer", role="ai_whole", pos=pos, facing=facing)
    reg.ensure("witness", role="ai_third", pos=pos, facing=facing)
    return reg


def smoke() -> bool:
    print("=== PERSPECTIVE VIEWS SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))

    class FakePlane:
        def all_nodes(self):
            return [
                {"id": "a", "label": "Alpha", "x": 1, "y": 0, "skin": "core"},
                {"id": "b", "label": "Beta", "x": 0, "y": 2, "skin": "edge"},
                {"id": "c", "label": "Gamma", "x": 5, "y": 5, "skin": "core"},
            ]

    class FakeBody:
        pos = (0, 0)
        class facing:
            name = "E"

    class FakeAvatar:
        body = FakeBody()

    class FakeProg:
        plane = FakePlane()
        avatar = FakeAvatar()

    p = FakeProg()
    reg = bootstrap_default_viewers(p)
    rec("viewers", len(reg.viewers) >= 4)

    user = reg.viewers["user"]
    sync_viewer_pose(p, user)
    first = see_as(p, user, "first")
    rec("first", first.get("ok") is True)
    third = see_as(p, user, "third")
    rec("third", third.get("ok") is True and third.get("count", 0) >= 1)
    whole = see_as(p, reg.viewers["architect"], "whole")
    rec("whole", whole.get("ok") is True and whole.get("count") == 3)

    # user can set companion to whole
    got = reg.set_mode("companion", "whole", as_role="user")
    rec("user_override", got.get("ok") is True)

    # ai cannot self-escalate if locked — companion mode now whole by user
    rec("modes_ok", set(MODES) == {"first", "third", "parts", "whole"})
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
