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
    """Canonical confirmation authority (transactional).

    Uses the checkpoint generation transaction (DCC-XVIII) to atomically
    commit Program + Nursery state. The logical transition is:

    OLD: proposal=PENDING, Idea absent from accepted Plane
    NEW: proposal=CONFIRMED, Idea present in accepted Program state

    Externally observable durable state is either OLD complete or NEW
    complete, never a hybrid. Any failure before the commit boundary
    leaves the proposal pending (memory and disk), so it stays retryable
    and rejectable.

    Internal: Set confirm_lineage._SKIP_CHECKPOINT = True to bypass the
    checkpoint (caller manages durability). Used by supersede_proposal
    which has its own transaction boundary.
    """
    # Check for skip flag (set by supersede_proposal)
    _skip = getattr(confirm_proposal, '_SKIP_CHECKPOINT', False)
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
    # R3: Record intent BEFORE any durable writes. The journal enables
    # recovery to distinguish "crashed confirmation" from "legitimate
    # historical record". Recovery uses recorded intent, not visibility.
    # R3-COMPLETION-GATE: Skip journal if supersession is managing the
    # transaction (it uses its own enclosing journal). Do not publish
    # independent successor acceptance and clear recovery evidence before
    # the supersession outcome is recoverable.
    from form.mandell.core_i_recovery import write_confirm_intent, clear_confirm_intent
    _skip_journal = getattr(confirm_proposal, '_SKIP_JOURNAL', False)
    if not _skip_journal:
        write_confirm_intent(program.owner, prop.id)
    # Stage the nursery confirmation in memory (do NOT save yet).
    # The checkpoint transaction will persist both Program and Nursery atomically.
    # ARGUS-3: All persistence failures must preserve/restore pre-operation state.
    prop.status = "confirmed"
    if not _skip:
        try:
            from form.mandell.checkpoint_generation import commit_checkpoint
            commit_checkpoint(program)
            # Success: clear the intent journal (unless supersession manages it).
            if not _skip_journal:
                clear_confirm_intent(program.owner)
        except Exception as exc:
            # Transaction failed: revert in-memory state to OLD.
            # Proposal stays pending (retryable), Idea removed if newly placed.
            # Never claim success, never silently discard, never expose hybrid.
            #
            # PRISM FINDING (2026-10-04): The checkpoint saves the LIVE nursery
            # file before the program file. If program save fails, the live
            # nursery file is left dirty with status="confirmed". The production
            # loader reads live files directly (bypasses checkpoint pointer),
            # so we MUST rewrite the live nursery file with reverted status.
            # Otherwise a crash here exposes confirmed+Idea-absent hybrid.
            #
            # R3: The intent journal remains for crash recovery. If this
            # handler completes the revert, clear the journal. If the process
            # dies before clearing, recovery will use the journal.
            prop.status = "pending"
            if not existed:
                units.pop(prop.id, None)
            # Revert the live nursery file that checkpoint may have dirtied.
            reverted = False
            try:
                nursery.save()
                reverted = True
            except Exception:
                # If we can't revert the file, leave journal for recovery.
                pass
            if reverted:
                if not _skip_journal:
                    clear_confirm_intent(program.owner)
            # Check if it's a nursery conflict (optimistic concurrency).
            # The checkpoint wraps the original error, so check the chain.
            from form.dell_matrix.nursery import NurseryConflictError
            def _is_conflict(e):
                if isinstance(e, NurseryConflictError):
                    return True
                if "conflict" in str(e).lower():
                    return True
                # Check wrapped cause (checkpoint wraps nursery errors)
                cause = getattr(e, '__cause__', None)
                if cause is not None and cause is not e:
                    return _is_conflict(cause)
                return False
            if _is_conflict(exc):
                return {"ok": False, "reason": "nursery_conflict", "error": str(exc)}
            raise
    else:
        # Skipping checkpoint (caller manages durability, e.g., supersession).
        # R3: Save BOTH nursery and program. The caller (supersession Phase 4)
        # will update predecessor links, but the successor's Idea must be
        # durable before Phase 4 begins. Otherwise a crash in Phase 4 leaves
        # the successor confirmed in nursery but absent from program.
        # Write intent journal for this confirmation as well, so crash
        # recovery can distinguish it from historical records.
        try:
            nursery.save()
            from form import persist_rest
            persist_rest.save(program)
            if not _skip_journal:
                clear_confirm_intent(program.owner)
        except Exception:
            prop.status = "pending"
            if not existed:
                units.pop(prop.id, None)
            # Leave journal for recovery (do not clear).
            raise
    try:
        text = " ".join([str(prop.label or ""), str(getattr(prop, "words", "") or ""), str(getattr(prop, "detail", "") or "")])
        aff = float(getattr(prop, "affinity", 1.0) or 1.0)
        program.inspire.prefs.observe_confirm(text, aff)
    except Exception:
        pass
    program.note_seed(50, "Manifest", prop.label)
    return {"ok": True, "id": prop.id, "label": prop.label, "kind": prop.kind}
