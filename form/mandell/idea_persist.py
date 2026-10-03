#!/usr/bin/env python3
"""Idea persistence — GDP-001 Phase 1, Requirement 1.1.5.

Ideas persist via Phase-0 fail-closed persistence:
- Atomic writes (no torn files)
- Fail-closed on corrupt/unreadable state
- Sealed history immutable (Phase-0 contracts)

An Idea's identity (UUID) is stable across save/load/checkpoint/rollback.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from form.dell_matrix.atomic_write import atomic_write_json
from form.mandell.idea import Idea


def _idea_dir() -> str:
    from form.persist import _STATE_DIR
    d = os.path.join(_STATE_DIR, "ideas")
    os.makedirs(d, exist_ok=True)
    return d


def _idea_path(idea_id: str) -> str:
    # Use a hash of the ID to avoid sanitization collisions.
    # MF-3 fix: "house!" and "house" must not map to the same file.
    import hashlib
    digest = hashlib.sha256(idea_id.encode("utf-8")).hexdigest()[:16]
    safe = "".join(c for c in idea_id if c.isalnum() or c in "-_")[:32]
    return os.path.join(_idea_dir(), f"idea_{safe}_{digest}.json")


def save_idea(idea: Idea) -> str:
    """Atomically save an Idea. Returns the path."""
    path = _idea_path(idea.id)
    atomic_write_json(path, idea.to_dict())
    return path


def load_idea(idea_id: str) -> Idea:
    """Load an Idea by ID. Fail-closed on corrupt/missing.

    Raises:
        FileNotFoundError: if the Idea does not exist.
        ValueError: if the persisted data is corrupt/unreadable.
    """
    path = _idea_path(idea_id)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Idea {idea_id!r} not found")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Idea {idea_id!r} persisted data corrupt: {exc}") from exc
    # Validate required fields.
    if not isinstance(data, dict) or "id" not in data:
        raise ValueError(f"Idea {idea_id!r} persisted data invalid: missing id")
    if data["id"] != idea_id:
        raise ValueError(
            f"Idea ID mismatch: path {idea_id!r} vs data {data['id']!r}"
        )
    return Idea.from_dict(data)


def list_idea_ids() -> List[str]:
    """List all persisted Idea IDs."""
    d = _idea_dir()
    ids = []
    for fn in os.listdir(d):
        if fn.startswith("idea_") and fn.endswith(".json"):
            ids.append(fn[5:-5])
    return ids


def idea_exists(idea_id: str) -> bool:
    return os.path.isfile(_idea_path(idea_id))
