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


def ideas_snapshot_path(owner: str) -> str:
    """Single-file snapshot of all Ideas for an owner."""
    return os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}.json")


def snapshot_ideas(owner: str) -> str:
    """Atomically snapshot all Ideas to the owner file.

    Returns the snapshot path. This file is a checkpoint member.
    """
    from form.mandell.idea_persist import list_idea_ids, _idea_path
    from form.mandell.idea import Idea

    ideas_data = {}
    for idea_id in list_idea_ids(owner):
        path = _idea_path(idea_id, owner)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            ideas_data[idea_id] = data
        except (OSError, json.JSONDecodeError):
            # Skip corrupt files; they fail closed on individual load.
            continue

    snapshot = {
        "owner": owner,
        "ideas": ideas_data,
    }
    path = ideas_snapshot_path(owner)
    atomic_write_json(path, snapshot)
    return path


def restore_ideas_from_snapshot(owner: str, snapshot_path: str) -> None:
    """Restore individual idea files from a snapshot.

    Called during rollback eager convergence.
    """
    from form.mandell.idea_persist import _idea_path, _idea_dir

    with open(snapshot_path, encoding="utf-8") as f:
        snapshot = json.load(f)

    ideas_data = snapshot.get("ideas", {})
    idea_dir = _idea_dir(owner)

    # Clear existing idea files for this owner (to remove ideas
    # created after the checkpoint).
    for fn in os.listdir(idea_dir):
        if fn.startswith("idea_") and fn.endswith(".json"):
            os.remove(os.path.join(idea_dir, fn))

    # Restore from snapshot.
    for idea_id, data in ideas_data.items():
        path = _idea_path(idea_id, owner)
        atomic_write_json(path, data)
