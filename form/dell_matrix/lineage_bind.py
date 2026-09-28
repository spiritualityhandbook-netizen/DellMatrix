#!/usr/bin/env python3
"""Bind confirm and load so live units keep proposal parents."""
from __future__ import annotations


def _units_of(program):
    plane = getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None)
    return getattr(plane, "units", None) or {}


def _stamp_from_nursery(program) -> None:
    nursery = getattr(program, "nursery", None)
    props = getattr(nursery, "proposals", None) or {}
    units = _units_of(program)
    for prop in props.values():
        uid = getattr(prop, "id", None)
        u = units.get(uid) if uid else None
        if not u:
            continue
        parents = list(getattr(prop, "parents", None) or [])
        if parents and not getattr(u, "parents", None):
            u.parents = parents
        if getattr(prop, "status", "") == "confirmed":
            u.origin = "confirmed"
            if parents:
                u.parents = parents


def bind() -> None:
    from form.open import Program
    if not getattr(Program.confirm_proposal, "_lineage_bound", False):
        raw = Program.confirm_proposal

        def confirm_proposal(self, pid: str):
            prop = (getattr(self, "nursery", None).proposals or {}).get(pid) if getattr(self, "nursery", None) else None
            parents = list(getattr(prop, "parents", None) or []) if prop else []
            out = raw(self, pid)
            uid = (out or {}).get("id")
            units = _units_of(self)
            if (out or {}).get("ok") and uid and uid in units:
                units[uid].parents = parents
                units[uid].origin = "confirmed"
                units[uid].lineage_version = int(getattr(units[uid], "lineage_version", 1) or 1)
            return out

        confirm_proposal._lineage_bound = True
        Program.confirm_proposal = confirm_proposal

    try:
        import form.persist as persist
        if not getattr(persist.load, "_lineage_bound", False):
            raw_load = persist.load

            def load(owner="Operator", path=None):
                program = raw_load(owner, path)
                _stamp_from_nursery(program)
                return program

            load._lineage_bound = True
            persist.load = load
    except Exception:
        pass


bind()
