#!/usr/bin/env python3
"""
Spatial audio cues — offline-first.

Maps world positions relative to the listener into:
  · pan   (-1 left … 0 center … +1 right)
  · gain  (distance attenuation)
  · band  (near / mid / far / silent)
  · ear   (L / R / C)

Does not require hardware. Emits cue dicts the live UI / TTS / Web Audio
can consume. Optional terminal bell for near-field alerts.

  cues_for_view(program, vision_or_nodes)
  spatialize(listener_pos, listener_facing, sources)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import math
import time

# facing name → degrees (math angle, x-right y-up-ish; match vision)
_FACING_ANGLE = {
    "E": 0, "NE": 45, "N": 90, "NW": 135,
    "W": 180, "SW": 225, "S": 270, "SE": 315,
}


def _facing_deg(facing: str) -> float:
    return float(_FACING_ANGLE.get(str(facing).upper(), 90))


def _rel_polar(
    listener: Tuple[float, float],
    facing: str,
    src: Tuple[float, float],
) -> Tuple[float, float]:
    """Return (distance, signed_bearing_deg relative to facing)."""
    lx, ly = listener
    sx, sy = src
    dx, dy = sx - lx, sy - ly
    dist = math.hypot(dx, dy)
    if dist < 1e-9:
        return 0.0, 0.0
    world = math.degrees(math.atan2(dy, dx)) % 360
    face = _facing_deg(facing)
    # signed delta in (-180, 180]: positive = right of facing
    rel = (world - face + 180) % 360 - 180
    return dist, rel


def pan_from_bearing(rel_deg: float) -> float:
    """Map relative bearing to stereo pan -1..1."""
    # ±90° → full side; clamp
    return max(-1.0, min(1.0, rel_deg / 90.0))


def gain_from_distance(dist: float, *, near: float = 1.5, far: float = 14.0) -> float:
    if dist <= 0.05:
        return 1.0
    if dist >= far:
        return 0.0
    if dist <= near:
        return 1.0
    # linear falloff near→far
    return max(0.0, 1.0 - (dist - near) / (far - near))


def band_from_distance(dist: float) -> str:
    if dist <= 2.0:
        return "near"
    if dist <= 6.0:
        return "mid"
    if dist <= 12.0:
        return "far"
    return "silent"


def ear_from_pan(pan: float) -> str:
    if pan < -0.25:
        return "L"
    if pan > 0.25:
        return "R"
    return "C"


@dataclass
class SpatialAudio:
    last_cues: List[Dict[str, Any]] = field(default_factory=list)
    bell_near: bool = False  # terminal bell if near-field

    def spatialize(
        self,
        listener_pos: Tuple[float, float],
        listener_facing: str,
        sources: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        cues: List[Dict[str, Any]] = []
        for s in sources:
            try:
                sx = float(s.get("x", 0))
                sy = float(s.get("y", 0))
            except (TypeError, ValueError):
                continue
            dist, rel = _rel_polar(listener_pos, listener_facing, (sx, sy))
            pan = pan_from_bearing(rel)
            gain = gain_from_distance(dist)
            band = band_from_distance(dist)
            if band == "silent" or gain <= 0.01:
                continue
            cue = {
                "id": s.get("id") or s.get("label"),
                "label": s.get("label") or s.get("id") or "?",
                "skin": s.get("skin"),
                "dist": round(dist, 2),
                "bearing": round(rel, 1),
                "pan": round(pan, 3),
                "gain": round(gain, 3),
                "band": band,
                "ear": ear_from_pan(pan),
                "hz_hint": 440 + int(max(-200, min(200, -rel))),  # slight pitch by side
            }
            cues.append(cue)
        cues.sort(key=lambda c: c["dist"])
        self.last_cues = cues
        if self.bell_near and any(c["band"] == "near" for c in cues):
            try:
                print("\a", end="", flush=True)
            except Exception:
                pass
        return cues

    def cues_for_program(self, program, nodes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        from form.dell_matrix.perspective_views import _pose_from_program, _nodes_from_program
        pos, facing = _pose_from_program(program)
        if nodes is None:
            nodes = _nodes_from_program(program)
        cues = self.spatialize(pos, facing, nodes)
        return {
            "ok": True,
            "listener": {"pos": list(pos), "facing": facing},
            "cues": cues,
            "count": len(cues),
            "summary": [
                f"{c['ear']} {c['label'][:20]} d={c['dist']} pan={c['pan']} gain={c['gain']}"
                for c in cues[:12]
            ],
            "ts": time.time(),
            "law": "spatial cues offline · UI/WebAudio may render",
        }

    def cues_from_sight(self, program, sight: Dict[str, Any]) -> Dict[str, Any]:
        """Use nodes already in a perspective sight result."""
        nodes = sight.get("nodes")
        if not nodes and isinstance(sight.get("vision"), dict):
            nodes = (sight["vision"] or {}).get("nodes") or []
        return self.cues_for_program(program, nodes=list(nodes or []))


AUDIO = SpatialAudio()


def spatialize(listener_pos, listener_facing, sources):
    return AUDIO.spatialize(listener_pos, listener_facing, sources)


def cues_for_view(program, sight: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if sight:
        return AUDIO.cues_from_sight(program, sight)
    return AUDIO.cues_for_program(program)


def smoke() -> bool:
    print("=== SPATIAL AUDIO SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(bool(ok))

    a = SpatialAudio()
    cues = a.spatialize((0, 0), "N", [
        {"id": "1", "label": "Front", "x": 0, "y": 3, "skin": "core"},
        {"id": "2", "label": "Right", "x": 4, "y": 0, "skin": "edge"},
        {"id": "3", "label": "Left", "x": -4, "y": 0, "skin": "edge"},
        {"id": "4", "label": "Far", "x": 0, "y": 20, "skin": "x"},
    ])
    rec("some_cues", len(cues) >= 2)
    ears = {c["ear"] for c in cues}
    rec("has_sides", "L" in ears or "R" in ears or "C" in ears)
    far = [c for c in cues if c["label"] == "Far"]
    rec("far_silent_or_low", len(far) == 0 or far[0]["gain"] < 0.2)
    front = [c for c in cues if c["label"] == "Front"]
    rec("front_centerish", not front or abs(front[0]["pan"]) < 0.5)
    print("sample:", cues[:3])
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
