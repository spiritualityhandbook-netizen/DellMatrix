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
    }


def save(program: Program, path: Optional[str] = None) -> str:
    path = path or _path(program.owner)
    data = serialize(program)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    program.nursery.proposals = {
        k: Proposal(**v) if isinstance(v, dict) else v
        for k, v in data.get("nursery", {}).items()
    }
    program.nursery.save()
    return path


def checkpoint(program: Program) -> str:
    cp = _cp_path(program.owner)
    with open(cp, "w", encoding="utf-8") as f:
        json.dump(serialize(program), f, indent=2)
    save(program)
    return cp


def list_checkpoints(owner: str) -> List[str]:
    prefix = f"program_{_safe_owner(owner)}_cp_"
    if not os.path.isdir(_STATE_DIR):
        return []
    return [
        os.path.join(_STATE_DIR, name)
        for name in sorted(os.listdir(_STATE_DIR))
        if name.startswith(prefix) and name.endswith(".json")
    ]


def _restore_avatar(p: Program, data: Dict[str, Any]) -> None:
    av = data.get("avatar") or {}
    if not av:
        return
    body = p.avatar.body
    if "name" in av:
        p.avatar.name = av["name"]
    if "pos" in av and isinstance(av["pos"], (list, tuple)) and len(av["pos"]) >= 2:
        body.pos = (int(av["pos"][0]), int(av["pos"][1]))
    try:
        body.facing = Facing[av.get("facing", "N")]
    except Exception:
        body.facing = Facing.N
    try:
        body.posture = Posture[av.get("posture", "STAND")]
    except Exception:
        body.posture = Posture.STAND
    try:
        body.locomotion = Locomotion[av.get("locomotion", "IDLE")]
    except Exception:
        body.locomotion = Locomotion.IDLE
    try:
        body.reach = Reach[av.get("reach", "CLOSE")]
    except Exception:
        body.reach = Reach.CLOSE
    body.holding = av.get("holding")
    try:
        p.face.current = Expression(av.get("expression", "neutral"))
    except Exception:
        p.face.current = Expression.NEUTRAL
    p.face.custom_face = av.get("custom_face")


def _restore_nursery(p: Program, data: Dict[str, Any]) -> None:
    raw = data.get("nursery") or {}
    p.nursery.proposals = {}
    for k, v in raw.items():
        try:
            if isinstance(v, dict):
                p.nursery.proposals[k] = Proposal(**v)
        except Exception:
            continue
    p.nursery.save()


def _restore_lattice(p: Program, data: Dict[str, Any]) -> None:
    raw = data.get("lattice") or {}
    if not raw:
        return
    try:
        size = int(raw.get("size", 12))
        p.lattice = HarmonicLattice(size=size)
        try:
            p.lattice.overlay = OverlayMode(raw.get("overlay", "harmonic"))
        except Exception:
            pass
        try:
            p.lattice.perspective = LatPerspective(raw.get("perspective", "top"))
        except Exception:
            pass
        try:
            p.lattice.perception.set_form(Form(raw.get("form", "cube")))
        except Exception:
            p.lattice.perception.set_form(Form.CUBE)
        p.lattice.origin_note = int(raw.get("origin_note", 0))
        for key, cell in (raw.get("cells") or {}).items():
            try:
                p.lattice.put(
                    int(cell.get("h", 0)), int(cell.get("v", 0)), int(cell.get("f", 0)),
                    content=cell.get("content"),
                    label=cell.get("label", ""),
                    tags=list(cell.get("tags") or []),
                )
            except Exception:
                continue
    except Exception:
        p.lattice = HarmonicLattice(size=12)


def load(owner: str = "Operator", path: Optional[str] = None) -> Program:
    assert_floor_intact()
    path = path or _path(owner)
    if not os.path.isfile(path):
        return open_program(owner)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("floor") != list(FLOOR):
        raise RuntimeError("Floor mismatch — refuse load")

    p = open_program(data.get("owner") or owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()

    for uid, u in data.get("plane", {}).get("units", {}).items():
        try:
            skin = Skin(u.get("skin", "cube"))
        except ValueError:
            skin = Skin.CUBE
        plane.place(
            uid,
            u.get("label", uid),
            words=u.get("words", ""),
            detail=u.get("detail", "") or "",
            goals=list(u.get("goals") or []),
            skin=skin,
            x=float(u.get("x", 0)),
            y=float(u.get("y", 0)),
        )
        unit = plane.units[uid]
        unit.sandboxed = bool(u.get("sandboxed", False))
        unit.sandbox_id = u.get("sandbox_id")

    for sid, members in data.get("plane", {}).get("sandboxes", {}).items():
        plane.box(list(members), sid)

    try:
        plane.set_perspective(Perspective(data.get("plane", {}).get("perspective", "table")))
    except Exception:
        pass
    zoom = data.get("plane", {}).get("zoom")
    if zoom:
        plane.zoom_in(zoom)

    if data.get("enhance_on"):
        p.enhance.turn_on()
    else:
        p.enhance.turn_off()

    if data.get("sandbox_on"):
        p.sandbox.turn_on()
    else:
        p.sandbox.turn_off()

    p.network_url = data.get("network_url") or ""
    try:
        from form.dell_matrix.internet_gate import InternetGate
        p.internet = InternetGate.from_dict(data.get("internet") or {})
    except Exception:
        pass

    amb = data.get("ambient", {})
    if amb.get("master_on"):
        p.ambient.turn_on()
    else:
        p.ambient.turn_off()
    for src, on in (amb.get("enabled") or {}).items():
        if on:
            p.ambient.enable_source(src)
        else:
            p.ambient.disable_source(src)

    res = data.get("resonance", {})
    st = ResonanceState(
        scores={k: float(v) for k, v in res.get("scores", {}).items()},
        tags={k: {t: float(w) for t, w in bucket.items()} for k, bucket in res.get("tags", {}).items()},
    )
    st.pulse_count = int(res.get("pulse_count", 0))
    p.enhance.state = st

    p.main.tags = {k: float(v) for k, v in data.get("main", {}).get("tags", {}).items()}
    p.main.contributions = []
    for c in data.get("main", {}).get("contributions", []):
        p.main.contributions.append(
            MainContribution(
                from_units=tuple(c.get("from_units", ("", ""))),
                labels=tuple(c.get("labels", ("", ""))),
                note=c.get("note", ""),
                weight=float(c.get("weight", 1.0)),
                ts=c.get("ts", ""),
            )
        )
    p.main.pulls = []
    for pr in data.get("main", {}).get("pulls", []):
        p.main.pulls.append(
            PullRecord(
                unit_id=pr.get("unit_id", ""),
                tag=pr.get("tag", ""),
                weight=float(pr.get("weight", 0)),
                ts=pr.get("ts", ""),
            )
        )

    target_gen = int(data.get("duo_generation", 0))
    while p.duo.generation < target_gen:
        p.duo.evolve("28[Rollback] :: persist load")

    _restore_avatar(p, data)
    _restore_nursery(p, data)
    _restore_lattice(p, data)

    try:
        from form.dell_matrix.companion import AICompanion
        p.companion = AICompanion.from_dict(data.get("companion") or {})
    except Exception:
        pass

    try:
        from form.dell_matrix.inspire_pack import InspireState
        p.inspire = InspireState.from_dict(data.get("inspire") or {})
    except Exception:
        pass

    try:
        from form.dell_matrix.self_model import SelfKnowledge
        p.self_knowledge = SelfKnowledge.from_dict(data.get("self_knowledge") or {})
    except Exception:
        pass

    ux = data.get("ux") or {}
    if ux:
        try:
            from form.dell_matrix.actions_registry import normalize_mode
            p.ux_mode = normalize_mode(ux.get("mode", "builder"))
        except Exception:
            p.ux_mode = ux.get("mode") or "builder"
        p.skin_filter = ux.get("skin_filter")
        p.persona_lens = ux.get("persona_lens")
        p.grid_snap = bool(ux.get("grid_snap", False))
        p.active_workshop = ux.get("active_workshop")
        p.click_mode = ux.get("click_mode") or "inspect"
        p.camera_follow = bool(ux.get("camera_follow", True))
        p.show_nursery_ghosts = bool(ux.get("show_nursery_ghosts", True))
        trail = ux.get("user_trail") or []
        p.user_trail = [
            [float(t[0]), float(t[1])]
            for t in trail
            if isinstance(t, (list, tuple)) and len(t) >= 2
        ][-16:]
        p.active_view = ux.get("active_view") or "growth"
        p.body_style = ux.get("body_style") or "stick"
        p.auto_confirm_grow = bool(ux.get("auto_confirm_grow", False))

    try:
        from form.dell_matrix.forces import ForceField
        p.forces = ForceField.from_dict(data.get("forces") or {})
    except Exception:
        pass

    try:
        from form.dell_matrix.personas import BIMOBody, PersonaMatrix
        p.bimo = BIMOBody.from_dict(data.get("bimo") or {})
        p.persona_matrix = PersonaMatrix(active=getattr(p, "persona_lens", None))
    except Exception:
        pass

    hist = data.get("history") or []
    if isinstance(hist, list):
        p.history = [str(h)[:120] for h in hist][-24:]

    clear_customs()
    import_customs(data.get("latinmandell_customs") or {})

    return p


def smoke() -> bool:
    print("=== PERSIST v7 SESSION SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    from form.mandell.latinmandell import customize, root_of, clear_customs as cc

    cc()
    p = open_program("PersistV7")
    p.place(
        "biz", "Business", words="CRM", detail="field ops", goals=["reliability"],
        skin=Skin.BUILDING, x=1,
    )
    p.avatar.step(3)
    p.face.set(Expression.JOY)
    p.lattice.to_sphere()
    p.grow_ideas(1)
    customize("lumen", dell=9, term="Show", sense="light made visible", la="lumen")
    path = save(p)
    rec("save file", os.path.isfile(path))

    cc()
    p2 = load("PersistV7")
    rec("units", "biz" in p2.cube.session.plane.units)
    u = p2.cube.session.plane.units["biz"]
    rec("detail", getattr(u, "detail", "") == "field ops")
    rec("goals", list(getattr(u, "goals", [])) == ["reliability"])
    rec("latinmandell custom", root_of("lumen") is not None and root_of("lumen").get("custom") is True)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rec("version 7", data.get("version") == 7)
    rec("unit has detail key", "detail" in data.get("plane", {}).get("units", {}).get("biz", {}))

    cc()
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("Persist v7 — detail/goals + customs + session")


if __name__ == "__main__":
    main()
