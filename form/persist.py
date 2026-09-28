#!/usr/bin/env python3
"""Persist v7 — matrix + avatar + nursery + lattice + history + LatinMandell customs + idea detail/goals."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import sys
from datetime import datetime, timezone

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.latinmandell import export_customs, import_customs, clear_customs
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.dell_matrix.main_field import MainContribution, PullRecord
    from form.dell_matrix.nursery import Nursery, Proposal, NURSERY_PATH
    from form.dell_matrix.harmonic_lattice import HarmonicLattice, OverlayMode, Perspective as LatPerspective
    from form.dell_matrix.perception import Form, Perception
    from form.avatar import Facing, Posture, Locomotion, Reach, Expression
    from form.open import Program, open_program
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.latinmandell import export_customs, import_customs, clear_customs
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.dell_matrix.main_field import MainContribution, PullRecord
    from form.dell_matrix.nursery import Nursery, Proposal, NURSERY_PATH
    from form.dell_matrix.harmonic_lattice import HarmonicLattice, OverlayMode, Perspective as LatPerspective
    from form.dell_matrix.perception import Form, Perception
    from form.avatar import Facing, Posture, Locomotion, Reach, Expression
    from form.open import Program, open_program

_STATE_DIR = os.path.join(os.path.dirname(__file__), "state")
os.makedirs(_STATE_DIR, exist_ok=True)
LEVEL = 7
VERSION = 7

from form.persist_core_ii import (
    CORE_II_DURABLE,
    CORE_II_STATE_VERSION,
    restore_core_ii,
    serialize_core_ii,
)


def _safe_owner(owner: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in owner) or "operator"


def _path(owner: str) -> str:
    return os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}.json")


def _cp_path(owner: str, stamp: Optional[str] = None) -> str:
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}_cp_{stamp}.json")


def _serialize_avatar(program: Program) -> Dict[str, Any]:
    b = program.avatar.body
    return {
        "name": program.avatar.name,
        "pos": list(b.pos),
        "facing": b.facing.name,
        "posture": b.posture.name,
        "locomotion": b.locomotion.name,
        "reach": b.reach.name,
        "holding": b.holding,
        "expression": program.face.current.value,
        "custom_face": program.face.custom_face,
    }


def _serialize_nursery(program: Program) -> Dict[str, Any]:
    return {k: v.to_dict() for k, v in program.nursery.proposals.items()}


def _serialize_lattice(program: Program) -> Dict[str, Any]:
    lat = program.lattice
    cells = {}
    for (h, v, f), cell in lat.cells.items():
        cells[f"{h},{v},{f}"] = {
            "h": cell.h, "v": cell.v, "f": cell.f,
            "label": cell.label,
            "tags": list(cell.tags),
            "content": cell.content if isinstance(cell.content, (str, int, float, bool, type(None))) else str(cell.content),
        }
    return {
        "size": lat.size,
        "overlay": lat.overlay.value,
        "perspective": lat.perspective.value,
        "form": lat.perception.form.value,
        "origin_note": lat.origin_note,
        "cells": cells,
        "modules": list(lat.modules.keys()),
    }


def serialize(program: Program) -> Dict[str, Any]:
    assert_floor_intact()
    plane = program.cube.session.plane
    units = {
        uid: {
            "label": u.label,
            "words": u.words,
            "detail": getattr(u, "detail", "") or "",
            "goals": list(getattr(u, "goals", []) or []),
            "skin": u.skin.value,
            "x": u.x,
            "y": u.y,
            "sandboxed": u.sandboxed,
            "sandbox_id": u.sandbox_id,
        }
        for uid, u in plane.units.items()
    }
    sandboxes = {sid: list(sb.member_ids) for sid, sb in plane.sandboxes.items()}
    main = program.main
    amb = program.ambient
    return {
        "type": "DellMatrixProgramState",
        "version": VERSION,
        "level": LEVEL,
        "saved": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "floor": list(FLOOR),
        "owner": program.owner,
        "enhance_on": program.enhance.on,
        "sandbox_on": program.sandbox.on,
        "network_url": program.network_url or "",
        "internet": program.internet.to_dict() if getattr(program, "internet", None) and hasattr(program.internet, "to_dict") else {"on": False},
        "ambient": {"master_on": amb.master_on, "enabled": dict(amb.enabled)},
        "resonance": {
            "scores": dict(program.enhance.state.scores),
            "tags": {k: dict(v) for k, v in program.enhance.state.tags.items()},
            "pulse_count": getattr(program.enhance.state, "pulse_count", 0),
        },
        "main": {
            "tags": dict(main.tags),
            "contributions": [
                {
                    "from_units": list(c.from_units),
                    "labels": list(c.labels),
                    "note": c.note,
                    "weight": c.weight,
                    "ts": getattr(c, "ts", ""),
                }
                for c in main.contributions
            ],
            "pulls": [
                {"unit_id": p.unit_id, "tag": p.tag, "weight": p.weight, "ts": p.ts}
                for p in main.pulls
            ],
        },
        "plane": {
            "perspective": plane.perspective.value,
            "zoom": plane.zoom_target,
            "units": units,
            "sandboxes": sandboxes,
        },
        "duo_generation": program.duo.generation,
        "avatar": _serialize_avatar(program),
        "companion": program.companion.to_dict() if hasattr(program, "companion") else {},
        "inspire": program.inspire.to_dict() if hasattr(program, "inspire") and hasattr(program.inspire, "to_dict") else {},
        "self_knowledge": program.self_knowledge.to_dict() if hasattr(program, "self_knowledge") and hasattr(program.self_knowledge, "to_dict") else {},
        "ux": {
            "mode": getattr(program, "ux_mode", "builder"),
            "skin_filter": getattr(program, "skin_filter", None),
            "persona_lens": getattr(program, "persona_lens", None),
            "grid_snap": bool(getattr(program, "grid_snap", False)),
            "active_workshop": getattr(program, "active_workshop", None),
            "click_mode": getattr(program, "click_mode", "inspect"),
            "camera_follow": bool(getattr(program, "camera_follow", True)),
            "show_nursery_ghosts": bool(getattr(program, "show_nursery_ghosts", True)),
            "user_trail": list(getattr(program, "user_trail", []) or [])[-16:],
            "active_view": getattr(program, "active_view", "growth"),
            "body_style": getattr(program, "body_style", "stick"),
            "auto_confirm_grow": bool(getattr(program, "auto_confirm_grow", False)),
        },
        "forces": program.forces.to_dict() if hasattr(program, "forces") else {},
        "bimo": program.bimo.to_dict() if hasattr(program, "bimo") else {},
        "nursery": _serialize_nursery(program),
        "lattice": _serialize_lattice(program),
        "history": list(getattr(program, "history", []) or [])[-24:],
        "latinmandell_customs": export_customs(),
        "core_ii": serialize_core_ii(program),
    }
