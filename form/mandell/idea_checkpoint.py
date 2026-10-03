#!/usr/bin/env python3
"""Idea checkpoint integration — GDP-001 Phase 1, MF-5 resolution.

Integrates canonical Idea state with Phase-0 checkpoint/rollback WITHOUT
creating a second checkpoint system and WITHOUT weakening Phase-0.

Seam: Ideas are snapshotted to a single owner-scoped file
(`ideas_{owner}.json`) which becomes a third member of the Phase-0
journaled transaction (program + nursery + ideas).

On checkpoint: the snapshot is written atomically, then sealed.
On rollback: the snapshot is restored, then individual idea files
are rehydrated from it.

This preserves:
- Phase-0 sealed-generation authority (no bypass)
- Journaled transaction guarantees (no hybrids)
- Fail-closed recovery (existing machinery)
"""

from __future__ import annotations

import json
import os
from typing import Dict, List

from form.dell_matrix.atomic_write import atomic_write_json
from form.persist import _STATE_DIR, _safe_owner


class CheckpointError(Exception):
    """Local checkpoint error (avoids import cycle with checkpoint_generation)."""
    pass


def ideas_snapshot_path(owner: str) -> str:
    """Single-file snapshot of all Ideas for an owner."""
    return os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}.json")


def ideas_rehydrate_marker_path(owner: str) -> str:
    """Marker for an interrupted rehydration (R2, NULL N2).

    Present => a rehydration from the live canonical snapshot did not
    complete. The next reader must complete it before observing state.
    """
    return os.path.join(_STATE_DIR, f"ideas_rehydrate_{_safe_owner(owner)}.pending")


def ensure_ideas_rehydrated(owner: str) -> None:
    """Complete any interrupted rehydration from the live canonical snapshot.

    Idempotent. Fail-closed: if the marker exists but the live snapshot
    is missing, refuse to guess.
    """
    marker = ideas_rehydrate_marker_path(owner)
    if not os.path.isfile(marker):
        return
    snap = ideas_snapshot_path(owner)
    if not os.path.isfile(snap):
        raise CheckpointError(
            f"ideas rehydration marker present for {owner!r} but live "
            f"snapshot missing; refusing to guess"
        )
    restore_ideas_from_snapshot(owner, snap)
    os.remove(marker)


def snapshot_ideas(owner: str) -> str:
    """Atomically snapshot all Ideas to the owner file.

    Returns the snapshot path. This file is a checkpoint member.

    R2: records per-idea validation and a skip manifest. Structural
    failures are recorded (not silently dropped).
    """
    from form.mandell.idea_persist import list_idea_ids, _idea_path
    from form.mandell.idea import Idea

    # R2 (PRISM R2-P1): never bake a partially-rehydrated working set into
    # a new sealed generation. Complete any pending rehydration first.
    ensure_ideas_rehydrated(owner)

    ideas_data = {}
    skipped = []
    for idea_id in list_idea_ids(owner):
        path = _idea_path(idea_id, owner)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # Structural validation: Idea.from_dict must accept it.
            Idea.from_dict(data)
            ideas_data[idea_id] = data
        except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
            skipped.append({"id": idea_id, "error": str(exc)[:120]})

    snapshot = {
        "owner": owner,
        "ideas": ideas_data,
        "skipped": skipped,
    }
    path = ideas_snapshot_path(owner)
    atomic_write_json(path, snapshot)
    return path


def restore_ideas_from_snapshot(owner: str, snapshot_path: str) -> None:
    """Restore individual idea files from a snapshot.

    Called during rollback eager convergence.

    R2 (PRISM R2-P1): WRITE-THEN-DELETE. All target files are written
    FIRST, then stale files deleted. An interruption leaves a superset
    (stale extras, no data loss) rather than a partial target. Stale
    files have IDs not in the snapshot and can be garbage-collected;
    load_idea of a stale ID still works (it is a complete idea file),
    so the reader never observes missing data.
    """
    from form.mandell.idea_persist import _idea_path, _idea_dir

    with open(snapshot_path, encoding="utf-8") as f:
        snapshot = json.load(f)

    ideas_data = snapshot.get("ideas", {})
    if not isinstance(ideas_data, dict):
        raise ValueError("rollback: ideas snapshot member has invalid structure")
    idea_dir = _idea_dir(owner)
    os.makedirs(idea_dir, exist_ok=True)

    # 1. Write all target files FIRST (each atomic via atomic_write_json).
    target_ids = set()
    for idea_id, data in ideas_data.items():
        target_ids.add(idea_id)
        path = _idea_path(idea_id, owner)
        atomic_write_json(path, data)

    # 2. Delete stale files (IDs not in snapshot) AFTER targets written.
    # Filenames embed a hash of the ID, so compare by computed filename.
    target_files = {os.path.basename(_idea_path(iid, owner)) for iid in target_ids}
    for fn in os.listdir(idea_dir):
        if fn.startswith("idea_") and fn.endswith(".json"):
            if fn not in target_files:
                os.remove(os.path.join(idea_dir, fn))

    # 3. R2 (NULL N2): post-rehydration verification. Every snapshot ID
    # must have its file present, and the file count must match (no
    # extras). Any mismatch fails closed rather than leaving a silently
    # divergent working set. (Filenames embed a hash of the ID, so we
    # verify via _idea_path rather than filename parsing.)
    files = [fn for fn in os.listdir(idea_dir)
             if fn.startswith("idea_") and fn.endswith(".json")]
    if len(files) != len(target_ids):
        raise CheckpointError(
            f"ideas rehydration verification failed for {owner!r}: "
            f"{len(files)} files != {len(target_ids)} snapshot ideas"
        )
    for idea_id in target_ids:
        if not os.path.isfile(_idea_path(idea_id, owner)):
            raise CheckpointError(
                f"ideas rehydration verification failed for {owner!r}: "
                f"idea {idea_id!r} file missing after restore"
            )
