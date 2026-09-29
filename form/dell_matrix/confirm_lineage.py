#!/usr/bin/env python3
"""Native confirm-proposal lineage body. Called by Program.confirm_proposal."""
from __future__ import annotations

from typing import Any, Dict, List

from form.dell_matrix.lineage import assign_lineage
from form.dell_matrix.nursery import NurseryConflictError
from form.dell_matrix.plane import Skin


def _goals(prop, units) -> List[str]:
    g = getattr(prop, "goals", None)
    if isinstance(g, (list, tuple)) and g:
        return [str(x) for x in g if str(x).strip()]
    for pid in list(getattr(prop, "parents", None) or []):
        u = units.get(pid)
        if u and getattr(u, "goals", None):
            return list(u.goals)
    return []


def _detail(prop, units) -> str:
    d = str(getattr(prop, "detail", "") or "").strip()
    if d:
        return d
    for pid in list(getattr(prop, "parents", None) or []):
        u = units.get(pid)
        if u and getattr(u, "detail", ""):
            return str(u.detail)
    return ""


def confirm_proposal(program, pid: str) -> Dict[str, Any]:
    """Canonical confirmation authority (the only caller of Nursery.confirm).

    Order: SELECT PENDING > VALIDATE/ASSIGN LINEAGE > PLACE > COMMIT CONFIRMATION + PERSIST (Nursery.confirm)
    > RETURN SUCCESS. Any failure before the commit leaves the proposal pending (memory and disk), so it
    stays retryable and rejectable. A placement exception propagates without committing.
    """
    nursery = program.nursery
    prop = nursery.proposals.get(pid)
    if not prop or prop.status != "pending":
        return {"ok": False, "reason": "not found or not pending"}
    units = program.cube.session.plane.units
    rec = assign_lineage(units, getattr(prop, "parents", None), origin="confirmed", child_id=prop.id)
    if not rec.get("ok"):
        return {"ok": False, "reason": rec.get("error") or "invalid_lineage", "missing": rec.get("missing")}
    existed = prop.id in units
    try:
        program.place(
            prop.id, prop.label, words=prop.words, detail=_detail(prop, units), goals=_goals(prop, units),
            skin=Skin.SEED, parents=list(rec["parents"]), origin=rec["origin"], lineage_version=int(rec["lineage_version"]),
        )
    except Exception:
        if not existed:
            units.pop(prop.id, None)
        raise
    try:
        nursery.confirm(pid)  # COMMIT CONFIRMATION + PERSIST (reverts to pending itself if persisting fails)
    except NurseryConflictError as e:
        if not existed:
            units.pop(prop.id, None)
        return {"ok": False, "reason": "nursery_conflict", "error": str(e)}
    try:
        text = " ".join([str(prop.label or ""), str(getattr(prop, "words", "") or ""), str(getattr(prop, "detail", "") or "")])
        aff = float(getattr(prop, "affinity", 1.0) or 1.0)
        program.inspire.prefs.observe_confirm(text, aff)
    except Exception:
        pass
    program.note_seed(50, "Manifest", prop.label)
    return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind}
