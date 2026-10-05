#!/usr/bin/env python3
"""Native confirm-proposal lineage body. Called by Program.confirm_proposal."""
from __future__ import annotations

import os
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
    def _remove_newly_placed():
        """Remove a newly placed Idea from all in-memory structures.
        F2: program.place() has multiple side effects beyond units:
        - plane.units[pid]: the Unit object
        - spatial.velocities[pid]: velocity tuple
        - spatial.placements[pid]: placement record
        - lattice: rebuilt from plane (derived, will be rebuilt on next save)
        - history: new entry (append-only log, cannot be removed without corruption)
        - keys: remembered label (index, stale entry harmless)

        For complete compensation, we remove the units entry and the
        spatial entries. The lattice is derived and will be rebuilt.
        History is append-only; a failed-operation entry is honest (it
        records the attempt). Keys index is harmless if stale.

        After in-memory cleanup, the caller restores baseline file bytes
        to disk, ensuring a later save cannot reintroduce effects.
        """
        units.pop(prop.id, None)
        try:
            spatial = program.cube.session.spatial
            if hasattr(spatial, 'velocities'):
                spatial.velocities.pop(prop.id, None)
            if hasattr(spatial, 'placements'):
                spatial.placements.pop(prop.id, None)
        except Exception:
            pass
        # Note: lattice is derived from plane on save; history is append-only
        # and honestly records the attempt; keys index staleness is harmless.
    try:
        program.place(
            prop.id, prop.label, words=prop.words, detail=_detail(prop, units), goals=_goals(prop, units),
            skin=Skin.SEED, parents=list(rec["parents"]), origin=rec["origin"], lineage_version=int(rec["lineage_version"]),
        )
    except Exception:
        if not existed:
            _remove_newly_placed()
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
        try:
            write_confirm_intent(program.owner, prop.id)
        except Exception:
            # F1: Intent-write failure must restore newly placed memory.
            # The Idea was placed in-memory but no journal exists to enable
            # recovery. Remove it to prevent exposing unrecoverable hybrid.
            if not existed:
                _remove_newly_placed()
            raise
    # Stage the nursery confirmation in memory (do NOT save yet).
    # The checkpoint transaction will persist both Program and Nursery atomically.
    # ARGUS-3: All persistence failures must preserve/restore pre-operation state.
    prop.status = "confirmed"
    if not _skip:
        # F2: Capture baseline file bytes before commit. If commit fails
        # after partial saves, restore these bytes directly. This is more
        # robust than trying to surgically revert all in-memory side
        # effects of program.place() (units, velocities, placements,
        # lattice, history, keys).
        _baseline_program_bytes = None
        _baseline_nursery_bytes = None
        _baseline_ok = False
        try:
            from form.persist import _path as _ppath
            from form.dell_matrix.nursery import owner_nursery_path
            _p_path = _ppath(program.owner)
            _n_path = owner_nursery_path(program.owner)
            # F2: Do not suppress baseline read failures. If we cannot
            # capture baseline, compensation cannot be verified; leave
            # journal for recovery instead of claiming success.
            if os.path.isfile(_p_path):
                with open(_p_path, 'rb') as f:
                    _baseline_program_bytes = f.read()
            # Legitimate absence: file doesn't exist, None is correct
            if os.path.isfile(_n_path):
                with open(_n_path, 'rb') as f:
                    _baseline_nursery_bytes = f.read()
            _baseline_ok = True
        except Exception as e:
            # Baseline capture failed; compensation cannot be verified.
            # Leave journal for recovery (do not clear).
            _baseline_ok = False
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
                _remove_newly_placed()
            # Revert the live files that checkpoint may have dirtied.
            # F2: Restore baseline bytes directly for complete compensation.
            # A Nursery-only revert leaves durable Program with Idea but no
            # journal for recovery. Use atomic_write_bytes (not raw open)
            # to avoid partial writes.
            reverted = False
            # F2: Only attempt compensation if baseline was captured.
            # Otherwise leave journal for recovery (fail closed).
            if _baseline_ok:
                try:
                    from form.dell_matrix.atomic_write import atomic_write_bytes
                    # Restore Program file from baseline bytes (complete revert)
                    if _baseline_program_bytes is not None:
                        atomic_write_bytes(_p_path, _baseline_program_bytes)
                    elif not existed:
                        # No baseline (new file): save reverted in-memory state
                        from form import persist_rest
                        persist_rest.save(program)
                    # Restore Nursery file from baseline (has pending status)
                    if _baseline_nursery_bytes is not None:
                        atomic_write_bytes(_n_path, _baseline_nursery_bytes)
                    else:
                        nursery.save()
                    reverted = True
                except Exception:
                    # If we can't revert both files, leave journal for recovery.
                    pass
            # If baseline capture failed (_baseline_ok=False), reverted stays
            # False, journal is preserved for recovery.
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
                _remove_newly_placed()
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
