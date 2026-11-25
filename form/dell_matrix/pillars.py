#!/usr/bin/env python3
"""
6-Pillar Evaluation Matrix — ported from src/core/six_pillar_audit.js

Standing · Spect · Tonea · Spirea · ManDetail · Omegate
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _clamp(v: float) -> float:
    try:
        x = float(v)
    except Exception:
        x = 0.0
    return max(0.0, min(1.0, x))


def score_pillars(input_scores: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    d = input_scores or {}
    standing = _clamp(d.get("standing", 0.75))
    spect = _clamp(d.get("spect", 0.7))
    tonea = _clamp(d.get("tonea", 0.6))
    spirea = _clamp(d.get("spirea", 0.7))
    mandetail = _clamp(d.get("mandetail", 0.8))
    omegate = _clamp(d.get("omegate", 0.75))
    average = round((standing + spect + tonea + spirea + mandetail + omegate) / 6, 3)
    # form/ uses practical 0.70 "healthy"; 0.95 is aspirational LEGACY threshold
    healthy = average >= 0.70
    pass_strict = average >= 0.95
    return {
        "standing": standing,
        "spect": spect,
        "tonea": tonea,
        "spirea": spirea,
        "mandetail": mandetail,
        "omegate": omegate,
        "average": average,
        "healthy": healthy,
        "pass_strict": pass_strict,
        "label": "PASS" if pass_strict else ("HEALTHY" if healthy else "GROWING"),
    }


def audit_program(program) -> Dict[str, Any]:
    """Derive pillar scores from live Program state."""
    ideas = len(program.cube.session.plane.units) if hasattr(program, "cube") else 0
    gen = int(getattr(getattr(program, "duo", None), "generation", 0) or 0)
    nursery = 0
    if hasattr(program, "nursery"):
        try:
            nursery = int(program.nursery.summary().get("pending", 0))
        except Exception:
            nursery = 0
    scores = program.scores() if hasattr(program, "scores") else {}
    score_mass = sum(float(v) for v in scores.values()) if scores else 0.0
    history = len(getattr(program, "history", []) or [])
    forces_evo = 0.0
    if hasattr(program, "forces"):
        try:
            for f in program.forces.list_forces():
                forces_evo += float(f.get("evolution_level") or 1) - 1.0
        except Exception:
            pass

    return score_pillars({
        "standing": min(1.0, 0.45 + ideas * 0.06 + (0.1 if hasattr(program, "look_around") else 0)),
        "spect": min(1.0, 0.4 + min(0.4, score_mass * 0.15) + history * 0.02),
        "tonea": min(1.0, 0.55 + (0.1 if getattr(program, "persona_lens", None) else 0)
                     + (0.1 if getattr(program, "active_view", None) else 0)),
        "spirea": min(1.0, 0.45 + gen * 0.03 + forces_evo * 0.05 + nursery * 0.02),
        "mandetail": min(1.0, 0.65 + (0.15 if program.cube.session.plane.zoom_target else 0)
                         + min(0.2, ideas * 0.02)),
        "omegate": min(1.0, 0.55 + (0.15 if getattr(program, "enhance", None) and program.enhance.on else 0)
                       + min(0.2, gen * 0.02)),
    })


def format_audit(audit: Dict[str, Any]) -> List[str]:
    return [
        f"6-Pillar · {audit.get('label')} · avg={audit.get('average')}",
        f"  Standing  {audit.get('standing'):.2f}  comprehension",
        f"  Spect     {audit.get('spect'):.2f}  observation",
        f"  Tonea     {audit.get('tonea'):.2f}  voice / modularity",
        f"  Spirea    {audit.get('spirea'):.2f}  creative growth",
        f"  ManDetail {audit.get('mandetail'):.2f}  fractal zoom",
        f"  Omegate   {audit.get('omegate'):.2f}  predictive lock",
    ]


def smoke() -> bool:
    print("=== PILLARS SMOKE ===")
    a = score_pillars()
    ok = 0.0 <= a["average"] <= 1.0 and "label" in a
    print(f"[{'PASS' if ok else 'FAIL'}] avg={a['average']}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
