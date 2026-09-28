#!/usr/bin/env python3
"""Native confirm-proposal lineage body. Called by Program.confirm_proposal."""
from __future__ import annotations

from typing import Any, Dict

from form.dell_matrix.lineage import assign_lineage
from form.dell_matrix.plane import Skin


def confirm_proposal(program, pid: str) -> Dict[str, Any]:
    prop = program.nursery.confirm(pid)
    if not prop:
        return {"ok": False, "reason": "not found or not pending"}
    rec = assign_lineage(
        program.cube.session.plane.units,
        getattr(prop, "parents", None),
        origin="confirmed",
        child_id=prop.id,
    )
    if not rec.get("ok"):
        return {"ok": False, "reason": rec.get("error") or "invalid_lineage"}
    program.place(
        prop.id,
        prop.label,
        words=prop.words,
        skin=Skin.SEED,
        parents=list(rec["parents"]),
        origin=rec["origin"],
        lineage_version=int(rec["lineage_version"]),
    )
    try:
        text = " ".join([
            str(prop.label or ""),
            str(getattr(prop, "words", "") or ""),
            str(getattr(prop, "detail", "") or ""),
        ])
        aff = float(getattr(prop, "affinity", 1.0) or 1.0)
        program.inspire.prefs.observe_confirm(text, aff)
    except Exception:
        pass
    program.note_seed(50, "Manifest", prop.label)
    return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind}
