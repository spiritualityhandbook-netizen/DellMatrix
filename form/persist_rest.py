#!/usr/bin/env python3
"""Persist save/load/checkpoint/smoke bound from persist.py."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import sys

from form.mandell.floor import FLOOR, assert_floor_intact
from form.mandell.language import bind, empty_language, parse_language
from form.dell_matrix.plane import Perspective, Skin
from form.dell_matrix.resonance import ResonanceState
from form.dell_matrix.main_field import MainContribution, PullRecord
from form.dell_matrix.harmonic_lattice import HarmonicLattice, OverlayMode, Perspective as LatPerspective
from form.dell_matrix.perception import Form
from form.avatar import Facing, Posture, Locomotion, Reach, Expression
from form.open import Program, open_program
from form.persist_core_ii import restore_core_ii
from form.persist import serialize, _path, _cp_path, _safe_owner, _STATE_DIR, VERSION


def save(program: Program, path: Optional[str] = None) -> str:
    path = path or _path(program.owner)
    data = serialize(program)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
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
    for enum, attr, default in ((Facing, "facing", "N"), (Posture, "posture", "STAND"), (Locomotion, "locomotion", "IDLE"), (Reach, "reach", "CLOSE")):
        try:
            setattr(body, attr, enum[av.get(attr, default)])
        except Exception:
            setattr(body, attr, enum[default])
    body.holding = av.get("holding")
    try:
        p.face.current = Expression(av.get("expression", "neutral"))
    except Exception:
        p.face.current = Expression.NEUTRAL
    p.face.custom_face = av.get("custom_face")


def _restore_lattice(p: Program, data: Dict[str, Any]) -> None:
    raw = data.get("lattice") or {}
    if not raw:
        return
    try:
        p.lattice = HarmonicLattice(size=int(raw.get("size", 12)))
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
        for _key, cell in (raw.get("cells") or {}).items():
            try:
                p.lattice.put(int(cell.get("h", 0)), int(cell.get("v", 0)), int(cell.get("f", 0)), content=cell.get("content"), label=cell.get("label", ""), tags=list(cell.get("tags") or []))
            except Exception:
                continue
    except Exception:
        p.lattice = HarmonicLattice(size=12)


class ProgramLoadError(ValueError):
    """Program file content is missing/invalid or its owner binding is inconsistent; raised before any swap."""


# Proven historical envelope versions (RTPH-I-R4C): every value below was written by
# serialize() into the DellMatrixProgramState envelope at the cited commit. No version 0
# or negative version was ever emitted by the supported writer.
#   v1  2e786ce  NBD: Persist (first envelope)
#   v2  2818dfc  NBD: Surface coherence
#   v3  b3c72d5  NBD: Persist L3
#   v4  c13d7c9  Form 1.00 scope lock
#   v5  747d3e3  SUS code pass
#   v6  4c3ab5c  Solid session save/load v6 (VERSION = 6)
#   v7  7768f20  NBD 1: HarmonicLattice (VERSION = 7, current)
_LEGACY_VERSIONS = frozenset((1, 2, 3, 4, 5, 6))


def _validate_envelope_version(data: Dict[str, Any]) -> None:
    """Explicit envelope-version contract (RTPH-I R4, narrowed by RTPH-I-R4C).

    Raises ProgramLoadError LOUDLY on unsupported versions. This runs inside
    _validate_program_data, i.e. before any semantic swap: a failed validation changes no binding,
    no CELLS/customs, no Program, and rewrites no file (load() never writes).

    Policy:
      version == VERSION (7)  → current format: ACCEPT.
      version missing         → legacy envelope: ACCEPT explicitly (deliberate RTPH-I leniency;
                                no migration invented; resave stamps the current version).
      version in {1, 2, 3, 4, 5, 6} → legacy envelope: ACCEPT explicitly. Git history proves
                                each of v1..v6 was emitted by the supported writer
                                (see _LEGACY_VERSIONS). No migration semantics are invented:
                                the file is read by the current reader, and any resave stamps
                                the current version.
      any other explicit int  → REJECT. Version 0 and negatives never existed; versions > 7
                                are unknown future schemas that must never be silently misread.
      version present but not an int → REJECT (covers "7", null/None, bool, float, ...).
          bool is rejected explicitly: isinstance(True, int) is True in Python.
    """
    if "version" not in data:
        return  # legacy envelope: accepted explicitly, no migration invented
    v = data["version"]
    if isinstance(v, bool) or not isinstance(v, int):
        raise ProgramLoadError(f"program file has non-integer envelope version {v!r}: refusing load")
    if v == VERSION:
        return  # current format
    if v in _LEGACY_VERSIONS:
        return  # legacy envelope: proven historical version, no migration invented
    raise ProgramLoadError(
        f"program file envelope version {v} is not supported (current {VERSION}, legacy 1-6): refusing load"
    )


def _validate_program_data(data: Any, owner: str) -> str:
    """VALIDATE the program envelope (language is validated by parse_language). Returns the resolved owner."""
    if not isinstance(data, dict):
        raise ProgramLoadError("program file is not a JSON object")
    _validate_envelope_version(data)
    if data.get("floor") != list(FLOOR):
        raise RuntimeError("Floor mismatch — refuse load")
    plane = data.get("plane")
    if not isinstance(plane, dict) or not isinstance(plane.get("units", {}), dict):
        raise ProgramLoadError("program data missing or invalid: 'plane' (with 'units') must be an object")
    file_owner = data.get("owner")
    if file_owner is not None and (not isinstance(file_owner, str) or not file_owner):
        raise ProgramLoadError("program data invalid: 'owner' must be a non-empty string")
    return file_owner or owner


def load(owner: str = "Operator", path: Optional[str] = None, activate: bool = True) -> Program:
    """READ > VALIDATE COMPLETE INPUT > PREPARE language > PREPARE Program > ASSERT OWNER/BINDING > SWAP > RETURN.

    Every step before the swap only builds private objects: a failure raises and leaves the bound owner, the
    working copy (CELLS/customs) and every existing Program unchanged. The swap is bind(p) (skipped with
    activate=False, e.g. AUTO loading AutoGrow). The Program's owner is the file's owner (Q-016 resolution);
    its nursery and language are that owner's and nothing of the previously bound owner is combined into it.
    A missing file yields a fresh owner: empty cells + default customs (D2), never the active owner's language.
    load() writes no file."""
    assert_floor_intact()
    path = path or _path(owner)
    if not os.path.isfile(path):
        p = open_program(owner)
        p.language = empty_language()
        if activate:
            bind(p)
        return p
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    resolved = _validate_program_data(data, owner)
    lang = parse_language(data)
    p = _prepare_program(resolved, data)
    p.language = lang
    from form.dell_matrix.nursery import owner_nursery_path
    if p.owner != resolved or getattr(p.nursery, "path", None) != owner_nursery_path(resolved):
        raise ProgramLoadError(f"owner binding mismatch: prepared {p.owner!r} for file owner {resolved!r}")
    if activate:
        bind(p)
    return p


def _prepare_program(owner: str, data: Dict[str, Any]) -> Program:
    """PREPARE a private Program from validated data. Touches no process language state."""
    p = open_program(owner)
    plane = p.cube.session.plane
    plane.units.clear()
    plane.sandboxes.clear()
    for uid, u in data.get("plane", {}).get("units", {}).items():
        try:
            skin = Skin(u.get("skin", "cube"))
        except ValueError:
            skin = Skin.CUBE
        plane.place(uid, u.get("label", uid), words=u.get("words", ""), detail=u.get("detail", "") or "", goals=list(u.get("goals") or []), skin=skin, x=float(u.get("x", 0)), y=float(u.get("y", 0)), parents=list(u.get("parents") or []), origin=str(u.get("origin") or "placed"), lineage_version=int(u.get("lineage_version") or 1), restore=True)
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
    st = ResonanceState(scores={k: float(v) for k, v in res.get("scores", {}).items()}, tags={k: {t: float(w) for t, w in bucket.items()} for k, bucket in res.get("tags", {}).items()})
    st.pulse_count = int(res.get("pulse_count", 0))
    p.enhance.state = st
    p.main.tags = {k: float(v) for k, v in data.get("main", {}).get("tags", {}).items()}
    p.main.contributions = []
    for c in data.get("main", {}).get("contributions", []):
        p.main.contributions.append(MainContribution(from_units=tuple(c.get("from_units", ("", ""))), labels=tuple(c.get("labels", ("", ""))), note=c.get("note", ""), weight=float(c.get("weight", 1.0)), ts=c.get("ts", "")))
    p.main.pulls = []
    for pr in data.get("main", {}).get("pulls", []):
        p.main.pulls.append(PullRecord(unit_id=pr.get("unit_id", ""), tag=pr.get("tag", ""), weight=float(pr.get("weight", 0)), ts=pr.get("ts", "")))
    target_gen = int(data.get("duo_generation", 0))
    while p.duo.generation < target_gen:
        p.duo.evolve("28[Rollback] :: persist load")
    _restore_avatar(p, data)
    # Nursery decisions are NOT restored from the serialized "nursery" field (kept in the file format for
    # back-compat only). p.nursery is the owner's live nursery file loaded by Program; restore never
    # creates pending/confirmed/rejected transitions and never writes any nursery file.
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
        p.user_trail = [[float(t[0]), float(t[1])] for t in trail if isinstance(t, (list, tuple)) and len(t) >= 2][-16:]
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
    restore_core_ii(p, data)
    return p


DURABLE_KEYS = (
    "type", "version", "level", "floor", "owner",
    "enhance_on", "sandbox_on", "network_url", "internet", "ambient",
    "resonance", "main", "plane", "duo_generation", "avatar",
    "companion", "inspire", "self_knowledge", "ux", "forces", "bimo",
    "nursery", "lattice", "history", "latinmandell_customs",
    "mandell_language", "core_ii",
)


def durable(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: data.get(k) for k in DURABLE_KEYS}


def smoke() -> bool:
    print("=== PERSIST v7 SESSION SMOKE ===")
    r = []
    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))
    from form.mandell.latinmandell import customize, root_of, clear_customs as cc
    from form.mandell.seed import CELLS, define_cell, expand_cell
    from form.avatar import Expression
    p = open_program("PersistV7")
    bind(p)  # owner-bound language: edits below belong to PersistV7, whatever owner was bound before
    cc()
    p.place("biz", "Business", words="CRM", detail="field ops", goals=["reliability"], skin=Skin.BUILDING, x=1)
    p.avatar.step(3)
    p.face.set(Expression.JOY)
    p.lattice.to_sphere()
    customize("lumen", dell=9, term="Show", sense="light made visible", la="lumen")
    define_cell("PersistCell", "08[Create] :: persist-cell")
    path = save(p)
    rec("save file", os.path.isfile(path))
    cc()
    CELLS.clear()
    p2 = load("PersistV7")
    rec("units", "biz" in p2.cube.session.plane.units)
    u = p2.cube.session.plane.units["biz"]
    rec("detail", getattr(u, "detail", "") == "field ops")
    rec("goals", list(getattr(u, "goals", [])) == ["reliability"])
    rec("latinmandell custom", root_of("lumen") is not None and root_of("lumen").get("custom") is True)
    rec("avatar nondefault", p2.face.current == Expression.JOY)
    rec("lattice nondefault", p2.lattice.perception.form.value == "sphere")
    rec("mandell language cells", "PersistCell" in CELLS and expand_cell("PersistCell").ok)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rec("version 7", data.get("version") == 7)
    rec("unit has detail key", "detail" in data.get("plane", {}).get("units", {}).get("biz", {}))
    rec("mandell_language key", isinstance(data.get("mandell_language"), dict))
    rec("serialize load domain parity", set(DURABLE_KEYS) <= set(data.keys()))
    cc()
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


USAGE = "usage: python -m form.persist --smoke   (persist v7 session smoke; the module is otherwise a library)"


def main(argv: Optional[List[str]] = None) -> int:
    """Explicit module entry: `--smoke` runs the smoke (exit 0/1); no argument prints usage (exit 0, no work);
    anything else is a usage error (exit 2)."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--smoke"]:
        return 0 if smoke() else 1
    if not args:
        print(USAGE)
        return 0
    print(f"{USAGE}\nerror: unrecognized arguments: {' '.join(args)}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
