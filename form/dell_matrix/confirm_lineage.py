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


def confirm_proposal(program, pid: str, _skip_checkpoint: bool = False) -> Dict[str, Any]:
    """Canonical confirmation authority (transactional).

    Uses the checkpoint generation transaction (DCC-XVIII) to atomically
    commit Program + Nursery state. The logical transition is:

    OLD: proposal=PENDING, Idea absent from accepted Plane
    NEW: proposal=CONFIRMED, Idea present in accepted Program state

    Externally observable durable state is either OLD complete or NEW
    complete, never a hybrid. Any failure before the commit boundary
    leaves the proposal pending (memory and disk), so it stays retryable
    and rejectable.

    _skip_checkpoint: Internal use only. When True, skips the checkpoint
    commit (caller manages durability). Used by supersede_proposal which
    has its own transaction boundary.
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
    # Stage the nursery confirmation in memory (do NOT save yet).
    # The checkpoint transaction will persist both Program and Nursery atomically.
    prop.status = "confirmed"
    if not _skip_checkpoint:
        try:
            from form.mandell.checkpoint_generation import commit_checkpoint
            commit_checkpoint(program)
        except Exception as exc:
            # Transaction failed: revert in-memory state to OLD.
            # Proposal stays pending (retryable), Idea removed if newly placed.
            prop.status = "pending"
            if not existed:
                units.pop(prop.id, None)
            # Check if it's a nursery conflict (optimistic concurrency)
            from form.dell_matrix.nursery import NurseryConflictError
            if isinstance(exc, NurseryConflictError) or "conflict" in str(exc).lower():
                return {"ok": False, "reason": "nursery_conflict", "error": str(exc)}
            raise
    else:
        # Skipping checkpoint (caller manages durability, e.g., supersession).
        # Fall back to legacy nursery.save() for backward compatibility.
        try:
            nursery.save()
        except Exception:
            prop.status = "pending"
            if not existed:
                units.pop(prop.id, None)
            raise
    try:
        text = " ".join([str(prop.label or ""), str(getattr(prop, "words", "") or ""), str(getattr(prop, "detail", "") or "")])
        aff = float(getattr(prop, "affinity", 1.0) or 1.0)
        program.inspire.prefs.observe_confirm(text, aff)
    except Exception:
        pass
    program.note_seed(50, "Manifest", prop.label)
    return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind}
