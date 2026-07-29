#!/usr/bin/env python3
"""
Persist — NBD (equation after EnhanceGate).

10[Keep] > 27[Checkpoint] >> 28[Rollback] :: Persist

Save / load program state so the matrix survives restarts:
- personal units (label, words, skin, x/y, sandbox)
- perspective / zoom
- enhance on/off + resonance scores/tags
- Main contributions + tags
- owner, generation

Run:
  python -m form.persist --smoke
  python -m form.persist --demo
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
import os
import sys
from datetime import datetime, timezone

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.open import Program, open_program
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Perspective, Skin
    from form.dell_matrix.resonance import ResonanceState
    from form.open import Program, open_program

_STATE_DIR = os.path.join(os.path.dirname(__file__), "state")
os.makedirs(_STATE_DIR, exist_ok=True)


def _path(owner: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in owner) or "operator"
    return os.path.join(_STATE_DIR, f"program_{safe}.json")


def serialize(program: Program) -> Dict[str, Any]:
    assert_floor_intact()
    plane = program.cube.session.plane
    units = {}
    for uid, u in plane.units.items():
        units[uid] = {
            "label": u.label,
            "words": u.words,
            "skin": u.skin.value,
            "x": u.x,
            "y": u.y,
            "sandboxed": u.sandboxed,
            "sandbox_id": u.sandbox_id,
        }
    sandboxes = {sid: list(sb.member_ids) for sid, sb in plane.sandboxes.items()}
    main = program.main
    return {
        "type": "DellMatrixProgramState",
        "version": 1,
        "saved": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "floor": list(FLOOR),
        "owner": program.owner,
        "enhance_on": program.enhance.on,
        "resonance": {
            "scores": dict(program.enhance.state.scores),
            "tags": {k: dict(v) for k, v in program.enhance.state.tags.items()},
        },
        "main": {
            "tags": dict(main.tags),
            "contributions": [
                {
                    "from_units": list(c.from_units),
                    "labels": list(c.labels),
                    "note": c.note,
                    "weight": c.weight,
                }
                for c in main.contributions
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
    data = serialize(program)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def load(owner: str = "Operator", path: Optional[str] = None) -> Program:
    """Load state into a fresh Program. Floor must match."""
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
    # clear default welcome if restoring full units
    plane.units.clear()
    plane.sandboxes.clear()

    for uid, u in data.get("plane", {}).get("units", {}).items():
        skin_name = u.get("skin", "cube")
        try:
            skin = Skin(skin_name)
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

    persp = data.get("plane", {}).get("perspective", "table")
    try:
        plane.set_perspective(Perspective(persp))
    except Exception:
        pass
    zoom = data.get("plane", {}).get("zoom")
    if zoom:
        plane.zoom_in(zoom)

    if data.get("enhance_on"):
        p.enhance.turn_on()
    else:
        p.enhance.turn_off()

    res = data.get("resonance", {})
    p.enhance.state = ResonanceState(
        scores={k: float(v) for k, v in res.get("scores", {}).items()},
        tags={k: {t: float(w) for t, w in bucket.items()} for k, bucket in res.get("tags", {}).items()},
    )

    from form.dell_matrix.main_field import MainContribution

    p.main.tags = {k: float(v) for k, v in data.get("main", {}).get("tags", {}).items()}
    p.main.contributions = []
    for c in data.get("main", {}).get("contributions", []):
        p.main.contributions.append(
            MainContribution(
                from_units=tuple(c.get("from_units", ("", ""))),
                labels=tuple(c.get("labels", ("", ""))),
                note=c.get("note", ""),
                weight=float(c.get("weight", 1.0)),
            )
        )

    # restore generation marker
    target_gen = int(data.get("duo_generation", 0))
    while p.duo.generation < target_gen:
        p.duo.evolve("28[Rollback] :: persist load")

    return p


def smoke() -> bool:
    print("=== PERSIST SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("PersistTest")
    p.place("biz", "Business", words="CRM", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="Ep4", skin=Skin.SEED, x=-1)
    p.enhance_on()
    p.pulse()
    path = save(p)
    rec("save file", os.path.isfile(path), path)

    p2 = load("PersistTest")
    rec("load owner", p2.owner == "PersistTest")
    rec("units restored", "biz" in p2.cube.session.plane.units and "music" in p2.cube.session.plane.units)
    rec("words", p2.cube.session.plane.units["biz"].words == "CRM")
    rec("enhance on", p2.enhance.on is True)
    rec("scores restored", p2.enhance.state.score_of("biz") > 0 or p2.enhance.state.score_of("music") > 0)
    rec("floor", p2.status()["floor"]["locked"] is True)

    # cleanup test file optional — keep for inspect
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo() -> None:
    print("10[Keep] > 27[Checkpoint] >> 28[Rollback] :: Persist")
    p = open_program("Demo")
    p.place("idea", "Idea", words="keep me", skin=Skin.CUBE)
    path = save(p)
    print("saved", path)
    p2 = load("Demo")
    print("loaded units", list(p2.cube.session.plane.units.keys()))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()


if __name__ == "__main__":
    main()
