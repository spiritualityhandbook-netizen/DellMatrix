#!/usr/bin/env python3
"""
Nature of Code physics tick — call from Program.force_tick.

Uses NatureBridge to move idea nodes under gravity wells + friction +
Ch3 oscillation driven by BreathForce phase.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from form.dell_matrix.nature_code import NatureBridge, _BRIDGE


def physics_tick(nodes: List[Dict[str, Any]], wells: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    updates = _BRIDGE.step_nodes(nodes or [], wells=wells)
    return {
        "ok": True,
        "moved": len(updates),
        "nature_updates": updates,
        "status": _BRIDGE.status(),
    }


def apply_updates_to_plane(plane, updates: List[Dict[str, Any]]) -> int:
    applied = 0
    units = getattr(plane, "units", {}) or {}
    for u in updates or []:
        unit = units.get(u.get("id"))
        if unit is None:
            continue
        unit.x = float(u["x"])
        unit.y = float(u["y"])
        applied += 1
    return applied


def program_force_tick_nature(program) -> Dict[str, Any]:
    """Full nature step on a Program: physics + write positions + breath sync."""
    nodes = program.nodes_payload() if hasattr(program, "nodes_payload") else []
    wells = []
    if hasattr(program, "forces") and program.forces:
        # Breath → oscillation phase
        try:
            phase = getattr(program.forces.breath, "phase", "inhale")
            _BRIDGE.set_breath_phase(phase)
        except Exception:
            pass
        for w in program.forces.gravity.wells:
            nid = w.get("id")
            match = next((n for n in nodes if n.get("id") == nid), None)
            if match:
                wells.append({"x": match.get("x", 0), "y": match.get("y", 0), "mass": w.get("mass", 2.0)})
    report = physics_tick(nodes, wells=wells or None)
    plane = program.cube.session.plane
    report["nature_applied"] = apply_updates_to_plane(plane, report.get("nature_updates") or [])
    return report
