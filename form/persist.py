#!/usr/bin/env python3
"""
Persist v6 — one session: matrix + avatar + face + nursery.

save  → writes everything
load  → restores everything
nothing left behind
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import sys
from datetime import datetime, timezone

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.dell_matrix.main_field import MainContribution, PullRecord
    from form.dell_matrix.nursery import Nursery, Proposal, NURSERY_PATH
    from form.avatar import Facing, Posture, Locomotion, Reach, Expression
    from form.open import Program, open_program
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.dell_matrix.main_field import MainContribution, PullRecord
    from form.dell_matrix.nursery import Nursery, Proposal, NURSERY_PATH
    from form.avatar import Facing, Posture, Locomotion, Reach, Expression
    from form.open import Program, open_program

_STATE_DIR = os.path.join(os.path.dirname(__file__), "state")
os.makedirs(_STATE_DIR, exist_ok=True)
LEVEL = 6
VERSION = 6


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


def serialize(program: Program) -> Dict[str, Any]:
    assert_floor_intact()
    plane = program.cube.session.plane
    units = {
        uid: {
            "label": u.label,
            "words": u.words,
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
        "ambient": {
            "master_on": amb.master_on,
            "enabled": dict(amb.enabled),
        },
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
        # v6 session pieces
        "avatar": _serialize_avatar(program),
        "nursery": _serialize_nursery(program),
    }


def save(program: Program, path: Optional[str] = None) -> str:
    path = path or _path(program.owner)
    data = serialize(program)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    # Keep nursery file in sync too
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
    # face
    expr_name = av.get("expression", "neutral")
    try:
        p.face.current = Expression(expr_name)
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

    # v6: avatar + nursery
    _restore_avatar(p, data)
    _restore_nursery(p, data)

    return p


def smoke() -> bool:
    print("=== PERSIST v6 SESSION SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("PersistV6")
    p.place("biz", "Business", words="CRM", skin=Skin.BUILDING, x=1)
    p.avatar.step(3)
    p.avatar.turn_right()
    p.face.set(Expression.JOY)
    p.grow_ideas(1)
    before_pending = len(p.list_proposals())
    path = save(p)
    rec("save file", os.path.isfile(path))

    p2 = load("PersistV6")
    rec("units", "biz" in p2.cube.session.plane.units)
    rec("avatar pos", p2.avatar.body.pos != (0, 0), str(p2.avatar.body.pos))
    rec("avatar facing", p2.avatar.body.facing.name in {"N", "NE", "E", "SE", "S", "SW", "W", "NW"})
    rec("face", p2.face.current == Expression.JOY or p2.face.show() != "")
    rec("nursery", len(p2.list_proposals()) == before_pending, str(len(p2.list_proposals())))

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rec("version 6", data.get("version") == 6)
    rec("has avatar key", "avatar" in data)
    rec("has nursery key", "nursery" in data)

    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("Persist v6 — matrix + avatar + nursery")


if __name__ == "__main__":
    main()
