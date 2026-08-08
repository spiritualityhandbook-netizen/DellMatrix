#!/usr/bin/env python3
"""
Directional vision — shared by REPL look + live visual.

Cone: range + half-angle from facing. Optional skin/persona lens filters.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import math

VISION_RANGE = 5.5
VISION_HALF_ANGLE = 55.0

_FACING_ANGLE = {
    "E": 0, "NE": 45, "N": 90, "NW": 135,
    "W": 180, "SW": 225, "S": 270, "SE": 315,
}

# Persona lens hints — full roster from personas.vision_lenses()
def _load_persona_lenses() -> dict:
    try:
        from form.dell_matrix.personas import vision_lenses
        return vision_lenses()
    except Exception:
        return {
            "manny": {"emoji": "🕵️", "prefer_skins": ["cube", "building", "words"], "label": "Manny · logic"},
            "melody": {"emoji": "❀", "prefer_skins": ["seed", "flower", "sphere"], "label": "Melody · growth"},
            "aetheris": {"emoji": "🌫️", "prefer_skins": ["circle", "core", "sphere"], "label": "Aetheris · coherence"},
            "mathelody": {"emoji": "🕵️❀🌫️", "prefer_skins": [], "label": "Mathelody · fusion"},
            "the_ancient": {"emoji": "🪨", "prefer_skins": ["core", "words", "building"], "label": "The_Ancient · structure"},
        }


PERSONA_LENSES = _load_persona_lenses()


def facing_angle(facing: str) -> float:
    return float(_FACING_ANGLE.get(str(facing).upper(), 90))


def angle_diff(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


def cone_polygon(
    pos: List[float],
    facing: str,
    range_: float = VISION_RANGE,
    half_angle: float = VISION_HALF_ANGLE,
    steps: int = 12,
) -> List[List[float]]:
    """World-space polygon points for vision cone (including apex)."""
    px, py = float(pos[0]), float(pos[1])
    face = facing_angle(facing)
    pts = [[px, py]]
    start = face - half_angle
    end = face + half_angle
    for i in range(steps + 1):
        t = i / steps
        ang = math.radians(start + (end - start) * t)
        pts.append([px + math.cos(ang) * range_, py + math.sin(ang) * range_])
    return pts


def compute_vision(
    pos,
    facing: str,
    nodes: List[Dict[str, Any]],
    other: Optional[Dict[str, Any]] = None,
    range_: float = VISION_RANGE,
    half_angle: float = VISION_HALF_ANGLE,
    skin_filter: Optional[str] = None,
    persona: Optional[str] = None,
) -> Dict[str, Any]:
    px, py = float(pos[0]), float(pos[1])
    face_ang = facing_angle(facing)
    prefer: List[str] = []
    persona_meta = None
    if persona:
        key = persona.lower().replace(" ", "_")
        persona_meta = PERSONA_LENSES.get(key)
        if persona_meta:
            prefer = list(persona_meta.get("prefer_skins") or [])

    seen_nodes: List[Dict[str, Any]] = []
    in_view_ids: List[str] = []
    for n in nodes:
        dx = float(n.get("x", 0)) - px
        dy = float(n.get("y", 0)) - py
        dist = math.hypot(dx, dy)
        if dist < 0.01 or dist > range_:
            continue
        ang = math.degrees(math.atan2(dy, dx)) % 360
        if angle_diff(ang, face_ang) > half_angle:
            continue
        skin = str(n.get("skin") or "")
        if skin_filter and skin != skin_filter:
            continue
        entry = {
            "id": n.get("id"),
            "label": n.get("label"),
            "skin": skin,
            "score": n.get("score", 0),
            "words": (n.get("words") or "")[:60],
            "detail": (n.get("detail") or "")[:80],
            "goals": n.get("goals") or [],
            "dist": round(dist, 2),
            "z": n.get("z", 0),
            "preferred": (not prefer) or (skin in prefer),
        }
        seen_nodes.append(entry)
        in_view_ids.append(str(n.get("id")))

    # Persona soft-sort: preferred skins first, then distance
    if prefer:
        seen_nodes.sort(key=lambda x: (0 if x.get("preferred") else 1, x["dist"]))
    else:
        seen_nodes.sort(key=lambda x: x["dist"])

    skins: Dict[str, int] = {}
    for sn in seen_nodes:
        skins[sn["skin"]] = skins.get(sn["skin"], 0) + 1
    pattern = {
        "count": len(seen_nodes),
        "skins": skins,
        "avg_score": round(sum(float(s["score"] or 0) for s in seen_nodes) / len(seen_nodes), 2) if seen_nodes else 0,
        "nearest": seen_nodes[0]["label"] if seen_nodes else None,
    }

    other_seen, proximity = None, None
    if other and other.get("pos"):
        ox, oy = float(other["pos"][0]), float(other["pos"][1])
        dx, dy = ox - px, oy - py
        dist = math.hypot(dx, dy)
        proximity = {"name": other.get("name") or other.get("label"), "dist": round(dist, 2)}
        if 0.01 < dist <= range_:
            ang = math.degrees(math.atan2(dy, dx)) % 360
            if angle_diff(ang, face_ang) <= half_angle:
                other_seen = {
                    "name": other.get("name") or other.get("label") or "other",
                    "pos": list(other["pos"]),
                    "facing": other.get("facing"),
                    "dist": round(dist, 2),
                    "doing": other.get("doing"),
                    "last_action": other.get("last_action"),
                }

    return {
        "facing": facing,
        "range": range_,
        "half_angle": half_angle,
        "cone": cone_polygon(list(pos) if not isinstance(pos, list) else pos, facing, range_, half_angle),
        "nodes": seen_nodes[:12],
        "in_view_ids": in_view_ids,
        "pattern": pattern,
        "sees_other": other_seen,
        "proximity": proximity,
        "skin_filter": skin_filter,
        "persona": persona_meta,
    }


def format_look_report(vision: Dict[str, Any]) -> List[str]:
    lines = [
        f"Facing {vision.get('facing')} · range {vision.get('range')} · half-angle {vision.get('half_angle')}°",
    ]
    p = vision.get("pattern") or {}
    lines.append(f"See {p.get('count', 0)} · nearest {p.get('nearest') or '—'} · skins {p.get('skins') or {}}")
    if vision.get("persona"):
        pe = vision["persona"]
        lines.append(f"Persona lens: {pe.get('emoji', '')} {pe.get('label', '')}")
    if vision.get("skin_filter"):
        lines.append(f"Skin filter: {vision['skin_filter']}")
    for n in vision.get("nodes") or []:
        pref = " ★" if n.get("preferred") else ""
        lines.append(f"  · {n.get('label')} [{n.get('skin')}] d={n.get('dist')}{pref}")
    if vision.get("sees_other"):
        o = vision["sees_other"]
        lines.append(f"  · sees {o.get('name')} d={o.get('dist')} ({o.get('doing')})")
    if not (vision.get("nodes") or vision.get("sees_other")):
        lines.append("  (nothing in view — turn or walk closer)")
    prox = vision.get("proximity")
    if prox:
        lines.append(f"Proximity: {prox.get('name')} at {prox.get('dist')}")
    return lines


def smoke() -> bool:
    print("=== VISION SMOKE ===")
    nodes = [
        {"id": "a", "label": "Alpha", "skin": "seed", "x": 0, "y": 2, "score": 1},
        {"id": "b", "label": "Beta", "skin": "cube", "x": 3, "y": 0, "score": 0},
    ]
    v = compute_vision([0, 0], "N", nodes)
    ok = "a" in v["in_view_ids"] and len(v["cone"]) > 3
    print(f"[{'PASS' if ok else 'FAIL'}] north sees seed")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
