#!/usr/bin/env python3
"""Persist save/load/checkpoint/smoke bound from persist.py."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json, os, sys
from form.mandell.latinmandell import import_customs, clear_customs
from form.dell_matrix.plane import Skin
from form.dell_matrix.nursery import Proposal
from form.open import Program, open_program
from form.persist_core_ii import restore_core_ii
from form.mandell.floor import FLOOR, assert_floor_intact
from form.persist import serialize, _path, _cp_path, _safe_owner, _STATE_DIR


def save(program: Program, path: Optional[str] = None) -> str:
    path = path or _path(program.owner)
    data = serialize(program)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    program.nursery.proposals = {k: Proposal(**v) if isinstance(v, dict) else v for k, v in data.get("nursery", {}).items()}
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
    return [os.path.join(_STATE_DIR, name) for name in sorted(os.listdir(_STATE_DIR)) if name.startswith(prefix) and name.endswith(".json")]


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
        plane.place(uid, u.get("label", uid), words=u.get("words", ""), detail=u.get("detail", "") or "", goals=list(u.get("goals") or []), skin=skin, x=float(u.get("x", 0)), y=float(u.get("y", 0)))
        unit = plane.units[uid]
        unit.sandboxed = bool(u.get("sandboxed", False))
        unit.sandbox_id = u.get("sandbox_id")
    for sid, members in data.get("plane", {}).get("sandboxes", {}).items():
        plane.box(list(members), sid)
    clear_customs()
    import_customs(data.get("latinmandell_customs") or {})
    try:
        from form.mandell.language import restore_language
        restore_language(data)
    except Exception:
        pass
    restore_core_ii(p, data)
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
    p.place("biz", "Business", words="CRM", detail="field ops", goals=["reliability"], skin=Skin.BUILDING, x=1)
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
