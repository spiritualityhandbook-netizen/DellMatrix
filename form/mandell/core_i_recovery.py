#!/usr/bin/env python3
"""Core I 27/28 program checkpoints. Distinct from Core II 93-96 transactions."""
from __future__ import annotations

from typing import Optional
import json
import os

from form.persist import _STATE_DIR, _safe_owner, load, serialize


def _cp_path(owner: str, stamp: Optional[str] = None) -> str:
    from datetime import datetime, timezone
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stamp = "".join(c if c.isalnum() else "_" for c in stamp)[:32]
    return os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}_cp_{stamp}.json")


def checkpoint(program, stamp: Optional[str] = None) -> str:
    cp = _cp_path(program.owner, stamp)
    data = serialize(program)
    os.makedirs(_STATE_DIR, exist_ok=True)
    with open(cp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    latest = os.path.join(_STATE_DIR, f"program_{_safe_owner(program.owner)}_cp_latest.json")
    with open(latest, "w", encoding="utf-8") as f:
        json.dump({"path": cp, "saved": data.get("saved"), "owner": program.owner}, f)
    program.last_checkpoint = cp
    return cp


def list_checkpoints(owner: str):
    prefix = f"program_{_safe_owner(owner)}_cp_"
    if not os.path.isdir(_STATE_DIR):
        return []
    return [
        os.path.join(_STATE_DIR, name)
        for name in sorted(os.listdir(_STATE_DIR))
        if name.startswith(prefix) and name.endswith(".json") and not name.endswith("_cp_latest.json")
    ]


def latest_checkpoint(owner: str) -> Optional[str]:
    pointer = os.path.join(_STATE_DIR, f"program_{_safe_owner(owner)}_cp_latest.json")
    if os.path.isfile(pointer):
        try:
            with open(pointer, encoding="utf-8") as f:
                path = (json.load(f) or {}).get("path")
            if path and os.path.isfile(path):
                return path
        except Exception:
            pass
    named = [p for p in list_checkpoints(owner) if os.path.isfile(p)]
    return named[-1] if named else None


def rollback(owner: str, path: Optional[str] = None):
    target = path or latest_checkpoint(owner)
    if not target or not os.path.isfile(target):
        raise FileNotFoundError("rollback_missing")
    return load(owner, target)
