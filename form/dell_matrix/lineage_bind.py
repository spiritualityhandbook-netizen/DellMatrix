#!/usr/bin/env python3
"""Bind confirm_proposal so live units keep proposal parents."""
from __future__ import annotations


def bind() -> None:
    from form.open import Program
    if getattr(Program.confirm_proposal, "_lineage_bound", False):
        return
    raw = Program.confirm_proposal

    def confirm_proposal(self, pid: str):
        prop = (getattr(self, "nursery", None).proposals or {}).get(pid) if getattr(self, "nursery", None) else None
        parents = list(getattr(prop, "parents", None) or []) if prop else []
        out = raw(self, pid)
        uid = (out or {}).get("id")
        plane = getattr(getattr(self, "cube", None), "session", None)
        units = getattr(getattr(plane, "plane", None), "units", None) if plane else None
        if (out or {}).get("ok") and uid and units and uid in units:
            units[uid].parents = parents
            units[uid].origin = "confirmed"
            units[uid].lineage_version = int(getattr(units[uid], "lineage_version", 1) or 1)
        return out

    confirm_proposal._lineage_bound = True
    Program.confirm_proposal = confirm_proposal


bind()
