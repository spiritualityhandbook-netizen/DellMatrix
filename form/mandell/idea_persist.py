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


def _idea_dir(owner: Optional[str] = None) -> str:
    from form.persist import _STATE_DIR, _safe_owner
    if owner:
        d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}")
    else:
        d = os.path.join(_STATE_DIR, "ideas")
    os.makedirs(d, exist_ok=True)
    return d


def _idea_path(idea_id: str, owner: Optional[str] = None) -> str:
    # Use a hash of the ID to avoid sanitization collisions.
    # MF-3 fix: "house!" and "house" must not map to the same file.
    import hashlib
    digest = hashlib.sha256(idea_id.encode("utf-8")).hexdigest()[:16]
    safe = "".join(c for c in idea_id if c.isalnum() or c in "-_")[:32]
    return os.path.join(_idea_dir(owner), f"idea_{safe}_{digest}.json")


def save_idea(idea: Idea, owner: Optional[str] = None) -> str:
    """Atomically save an Idea. Returns the path."""
    path = _idea_path(idea.id, owner)
    atomic_write_json(path, idea.to_dict())
    return path


def load_idea(idea_id: str, owner: Optional[str] = None) -> Idea:
    """Load an Idea by ID. Fail-closed on corrupt/missing.

    R2: completes any interrupted rehydration (single isfile check) before
    observing the working set.

    Raises:
        FileNotFoundError: if the Idea does not exist.
        ValueError: if the persisted data is corrupt/unreadable.
    """
    if owner:
        from form.mandell.idea_checkpoint import ensure_ideas_rehydrated
        ensure_ideas_rehydrated(owner)
    path = _idea_path(idea_id, owner)
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


def list_idea_ids(owner: Optional[str] = None) -> List[str]:
    """List all persisted Idea IDs (from file content, not filename)."""
    d = _idea_dir(owner)
    ids = []
    for fn in os.listdir(d):
        if fn.startswith("idea_") and fn.endswith(".json"):
            path = os.path.join(d, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "id" in data:
                    ids.append(data["id"])
            except (OSError, json.JSONDecodeError):
                continue
    return ids


def scan_idea_files(owner: Optional[str] = None) -> List[Dict[str, Optional[str]]]:
    """Full accounting of every idea file persisted for ``owner``.

    Returns one entry per ``idea_*.json`` file, in filename order:

        {"file": <basename>, "id": <str|None>, "error": <str|None>}

    A file is healthy iff ``error`` is None: it reads, decodes as
    UTF-8, parses to a JSON object carrying a string ``id``, and sits
    at that id's canonical filename. Every other file — unreadable,
    undecodable, unparseable, structurally invalid, or misplaced —
    is accounted with the reason in ``error``. Nothing is silently
    omitted: this is the inventory the checkpoint seal is judged
    against (Critic F4; Director ruling 7181902882). ``list_idea_ids``
    above keeps its legacy semantics for its existing callers.
    """
    d = _idea_dir(owner)
    entries: List[Dict[str, Optional[str]]] = []
    for fn in sorted(os.listdir(d)):
        if not (fn.startswith("idea_") and fn.endswith(".json")):
            continue
        path = os.path.join(d, fn)
        entry: Dict[str, Optional[str]] = {"file": fn, "id": None, "error": None}
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            entry["error"] = f"unreadable idea file: {exc}"[:160]
            entries.append(entry)
            continue
        if not isinstance(data, dict) or not isinstance(data.get("id"), str):
            entry["error"] = (
                "structurally invalid idea file: not a JSON object "
                "carrying a string id"
            )
            entries.append(entry)
            continue
        entry["id"] = data["id"]
        if os.path.basename(_idea_path(data["id"], owner)) != fn:
            entry["error"] = (
                "structurally invalid idea file: filename is not the "
                "canonical filename for its id"
            )
        entries.append(entry)
    return entries


def idea_exists(idea_id: str, owner: Optional[str] = None) -> bool:
    return os.path.isfile(_idea_path(idea_id, owner))
