#!/usr/bin/env python3
"""Persist L3 — includes ambient gate flags (Form 1.00 completeness)."""

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
    from form.open import Program, open_program
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.dell_matrix.main_field import MainContribution, PullRecord
    from form.open import Program, open_program

_STATE_DIR = os.path.join(os.path.dirname(__file__), "state")
os.makedirs(_STATE_DIR, exist_ok=True)
LEVEL = 3


def _safe_owner(owner: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in owner) or "operator"


def _path(owner: str) -> str:
    return os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}.json")


def _cp_path(owner: str, stamp: Optional[str] = None) -> str:
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}_cp_{stamp}.json")


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
        "version": 4,
        "level": LEVEL,
        "form_scope": "1.00",
        "saved": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "floor": list(FLOOR),
        "owner": program.owner,
        "enhance_on": program.enhance.on,
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
    }


def save(program: Program, path: Optional[str] = None) -> str:
    path = path or _path(program.owner)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serialize(program), f, indent=2)
    return path


def checkpoint(program: Program) -> str:
    cp = _cp_path(program.owner)
    with open(cp, "w", encoding="utf-8") as f:
        json.dump(serialize(program), f, indent=2)
    save(program)
    return cp


def list_checkpoints(owner: str) -> List[str]:
    prefix = f"program_{_safe_owner(owner)}_cp_"
    return [
        os.path.join(_STATE_DIR, name)
        for name in sorted(os.listdir(_STATE_DIR))
        if name.startswith(prefix) and name.endswith(".json")
    ]


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

    return p


def smoke() -> bool:
    print("=== PERSIST V4 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("PersistV4")
    p.place("biz", "Business", words="CRM", skin=Skin.BUILDING, x=1)
    p.enhance_on()
    p.pulse()
    p.ambient.turn_on()
    p.ambient.enable_source("files")
    path = save(p)
    rec("save", os.path.isfile(path))
    p2 = load("PersistV4")
    rec("units", "biz" in p2.cube.session.plane.units)
    rec("ambient master", p2.ambient.master_on is True)
    rec("ambient files", p2.ambient.enabled.get("files") is True)
    rec("enhance", p2.enhance.on is True)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rec("form_scope 1.00", data.get("form_scope") == "1.00" and data.get("version") == 4)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("Persist Form 1.00")


if __name__ == "__main__":
    main()
