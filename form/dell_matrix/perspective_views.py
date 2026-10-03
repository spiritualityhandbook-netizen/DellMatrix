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

# ---- Epistemic status law (GDP-001 §15 / docs/RUNTIME_TRUTH_INVARIANTS.md) ----
# Every view result carries "epistemic_status" (one of EPISTEMIC_STATUSES) and
# "data_source" (where the node inventory was read from). A view that cannot
# verify its node data reports UNKNOWN (no readable source) or UNAVAILABLE
# (source exists but could not be read) and MUST NOT emit a confident
# "count": 0 — "count" is present ONLY when the inventory was verified.
# Honest UNKNOWN beats a confident empty report.
EPISTEMIC_STATUSES = ("REAL", "PARTIAL", "UNAVAILABLE", "UNKNOWN", "UNSUPPORTED")

REAL = "REAL"                # read from the verified canonical Program state path
PARTIAL = "PARTIAL"          # read from a legacy/non-canonical adapter path
UNAVAILABLE = "UNAVAILABLE"  # a state source exists but could not be read
UNKNOWN = "UNKNOWN"          # no verifiable state source
UNSUPPORTED = "UNSUPPORTED"  # requested operation is not supported

# Canonical node inventory path on the real Program (form.open.Program):
# program.cube.session.plane.units  (Plane.units: id -> Unit)
_REAL_NODE_PATH = "program.cube.session.plane.units"

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
            return {"ok": False, "error": f"unknown mode {mode}", "modes": list(MODES),
                    "epistemic_status": UNSUPPORTED, "data_source": "none"}
        v = self.viewers.get(id)
        if v is None:
            return {"ok": False, "error": f"unknown viewer {id}",
                    "epistemic_status": UNKNOWN, "data_source": "none"}
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


def _skin_str(skin: Any) -> str:
    # Skin is a str-Enum; str() may render "Skin.CUBE" — prefer .value.
    v = getattr(skin, "value", None)
    if isinstance(v, str):
        return v
    if isinstance(skin, str):
        return skin
    return str(skin or "")


def _normalize_node(n: Any) -> Dict[str, Any]:
    if isinstance(n, dict):
        return {
            "id": n.get("id"),
            "label": n.get("label", "?"),
            "x": float(n.get("x", 0) or 0),
            "y": float(n.get("y", 0) or 0),
            "skin": _skin_str(n.get("skin")),
        }
    return {
        "id": getattr(n, "id", None) or getattr(n, "label", "?"),
        "label": getattr(n, "label", str(n)),
        "x": float(getattr(n, "x", 0) or 0),
        "y": float(getattr(n, "y", 0) or 0),
        "skin": _skin_str(getattr(n, "skin", "")),
    }


def _probe_nodes(program) -> Tuple[List[Dict[str, Any]], str, str]:
    """Read the node inventory with an honest epistemic status.

    Returns (nodes, data_source, epistemic_status). Priority:
      1. canonical real path  program.cube.session.plane.units -> REAL
      2. legacy adapter        program.plane.all_nodes()/nodes   -> PARTIAL
      3. source exists but unreadable                            -> UNAVAILABLE
      4. no readable source                                       -> UNKNOWN
    """
    # 1. Canonical real path.
    try:
        plane = getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None)
        units = getattr(plane, "units", None)
        if isinstance(units, dict):
            return ([_normalize_node(u) for u in units.values()],
                    _REAL_NODE_PATH, REAL)
        if plane is not None:
            return ([], _REAL_NODE_PATH, UNAVAILABLE)
    except Exception:
        return ([], _REAL_NODE_PATH, UNAVAILABLE)
    # 2. Legacy / non-canonical adapter (synthetic planes, test fakes,
    #    or older embeddings). Data may be stale or non-authoritative.
    try:
        plane = getattr(program, "plane", None)
        if plane is not None:
            items: List[Any] = []
            if hasattr(plane, "all_nodes"):
                items = plane.all_nodes() or []
            elif hasattr(plane, "nodes"):
                raw = plane.nodes
                items = list(raw.values()) if isinstance(raw, dict) else list(raw or [])
            return ([_normalize_node(n) for n in items],
                    "program.plane (legacy adapter)", PARTIAL)
    except Exception:
        return ([], "program.plane (legacy adapter)", UNAVAILABLE)
    # 3. Blind — no verifiable source. NOT "empty".
    return ([], "no readable node source", UNKNOWN)


def _nodes_from_program(program) -> List[Dict[str, Any]]:
    """Backward-compatible list-only accessor.

    Prefer _probe_nodes() when honesty about the data source matters —
    this helper discards the epistemic status.
    """
    nodes, _src, _status = _probe_nodes(program)
    return nodes


def _blind_report(mode: str, source: str, status: str) -> List[str]:
    return [
        f"{mode.capitalize()} view: node inventory {status} — cannot verify state",
        f"  data_source: {source}",
        "  (no confident empty report is made over unverified state)",
    ]


def _pose_from_program(program) -> Tuple[Tuple[float, float], str]:
    body = getattr(getattr(program, "avatar", None), "body", None)
    if body is not None:
        pos = getattr(body, "pos", (0, 0))
        facing = getattr(getattr(body, "facing", None), "name", None) or str(getattr(body, "facing", "N"))
        return (float(pos[0]), float(pos[1])), str(facing)
    return (0.0, 0.0), "N"


def see_first(program, viewer: Viewer) -> Dict[str, Any]:
    from form.dell_matrix.vision import compute_vision, format_look_report
    nodes, source, status = _probe_nodes(program)
    pos = list(viewer.pos)
    base: Dict[str, Any] = {
        "mode": "first",
        "viewer": viewer.id,
        "role": viewer.role,
        "scope": "cone_in_front_only",
        "epistemic_status": status,
        "data_source": source,
    }
    if status in (UNKNOWN, UNAVAILABLE):
        # No verifiable nodes: do not fabricate a vision over invented data.
        return {**base, "report": _blind_report("first", source, status)}
    vis = compute_vision(pos, viewer.facing, nodes, range_=6.0, half_angle=55.0)
    return {
        **base,
        "vision": vis,
        "report": format_look_report(vis),
    }


def see_third(program, viewer: Viewer) -> Dict[str, Any]:
    """Around the body — not limited to forward cone."""
    nodes, source, status = _probe_nodes(program)
    px, py = viewer.pos
    radius = 10.0
    base: Dict[str, Any] = {
        "mode": "third",
        "viewer": viewer.id,
        "role": viewer.role,
        "center": [px, py],
        "radius": radius,
        "scope": "ring_around_body",
        "epistemic_status": status,
        "data_source": source,
    }
    if status in (UNKNOWN, UNAVAILABLE):
        return {**base, "report": _blind_report("third", source, status)}
    around = []
    for n in nodes:
        dx = float(n.get("x", 0)) - px
        dy = float(n.get("y", 0)) - py
        dist = math.hypot(dx, dy)
        if 0.01 < dist <= radius:
            around.append({**n, "dist": round(dist, 2)})
    around.sort(key=lambda x: x["dist"])
    return {
        **base,
        "nodes": around[:40],
        "count": len(around),
        "report": [f"Third-person around ({px:.1f},{py:.1f}) r={radius}",
                   f"  {len(around)} nodes nearby"] + [
            f"  · {n.get('label')} d={n.get('dist')}" for n in around[:12]
        ],
    }


def see_parts(program, viewer: Viewer) -> Dict[str, Any]:
    nodes, source, status = _probe_nodes(program)
    px, py = viewer.pos
    skins = [s.lower() for s in (viewer.part_skins or [])]
    radius = float(viewer.part_radius or 8.0)
    base: Dict[str, Any] = {
        "mode": "parts",
        "viewer": viewer.id,
        "role": viewer.role,
        "filters": {"skins": skins, "radius": radius},
        "scope": "filtered_slice",
        "epistemic_status": status,
        "data_source": source,
    }
    if status in (UNKNOWN, UNAVAILABLE):
        return {**base, "report": _blind_report("parts", source, status)}
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
        **base,
        "nodes": parts[:40],
        "count": len(parts),
        "report": [
            f"Parts view skins={skins or 'any'} r={radius}",
            f"  {len(parts)} matching",
        ] + [f"  · {n.get('label')} [{n.get('skin')}]" for n in parts[:12]],
    }


def see_whole(program, viewer: Viewer) -> Dict[str, Any]:
    nodes, source, status = _probe_nodes(program)
    base: Dict[str, Any] = {
        "mode": "whole",
        "viewer": viewer.id,
        "role": viewer.role,
        "scope": "omniscient_plane",
        "epistemic_status": status,
        "data_source": source,
    }
    if status in (UNKNOWN, UNAVAILABLE):
        # NEVER confidently report "0 nodes" over unverified state.
        return {**base, "report": _blind_report("whole", source, status)}
    by_skin: Dict[str, int] = {}
    for n in nodes:
        skin = str(n.get("skin", "") or "none")
        by_skin[skin] = by_skin.get(skin, 0) + 1
    return {
        **base,
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
        return {"ok": False, "error": f"bad mode {m}",
                "epistemic_status": UNSUPPORTED, "data_source": "none"}
    if viewer.role not in PRIVILEGED and mode and mode != viewer.effective_mode():
        # AI trying to peek beyond assignment without privileged override
        if viewer.mode and mode != viewer.mode:
            return {
                "ok": False,
                "error": f"viewer {viewer.id} locked to {viewer.effective_mode()}",
                "hint": "user/architect can set_mode to change",
                "epistemic_status": UNSUPPORTED, "data_source": "none",
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
    # legacy FakePlane path is honest about being non-canonical
    rec("first_partial", first.get("epistemic_status") == "PARTIAL")
    third = see_as(p, user, "third")
    rec("third", third.get("ok") is True and third.get("count", 0) >= 1)
    whole = see_as(p, reg.viewers["architect"], "whole")
    rec("whole", whole.get("ok") is True and whole.get("count") == 3)
    rec("whole_partial_src", whole.get("data_source") == "program.plane (legacy adapter)")

    # R5: canonical real path — program.cube.session.plane.units -> REAL
    class RealPlane:
        def __init__(self):
            self.units = {
                "u1": {"id": "u1", "label": "One", "x": 1.0, "y": 1.0, "skin": "cube"},
                "u2": {"id": "u2", "label": "Two", "x": 2.0, "y": 2.0, "skin": "sphere"},
            }
    class RealProg:
        def __init__(self):
            self.cube = type("C", (), {"session": type("S", (), {"plane": RealPlane()})()})()
            self.avatar = FakeAvatar()
    rp = RealProg()
    nodes, src, status = _probe_nodes(rp)
    rec("real_path_probe", status == "REAL" and src == _REAL_NODE_PATH and len(nodes) == 2)
    rw = see_as(rp, reg.viewers["architect"], "whole")
    rec("real_path_whole", rw.get("ok") is True and rw.get("count") == 2
        and rw.get("epistemic_status") == "REAL")

    # R5: blind program — UNKNOWN, never a confident zero
    class BlindProg:
        pass
    bp = BlindProg()
    bn, bsrc, bstatus = _probe_nodes(bp)
    rec("blind_probe", bstatus == "UNKNOWN" and bn == [])
    bw = see_whole(bp, reg.viewers["architect"])
    rec("blind_no_confident_zero",
        "count" not in bw
        and bw.get("epistemic_status") == "UNKNOWN"
        and "0 nodes" not in " ".join(bw.get("report") or []))
    bf = see_first(bp, reg.viewers["user"])
    rec("blind_first_honest", bf.get("epistemic_status") == "UNKNOWN"
        and "vision" not in bf)

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
