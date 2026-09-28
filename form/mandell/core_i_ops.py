#!/usr/bin/env python3
"""Locally closable Core I arms that wrap the leaf without rewriting it."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

HANDLED = {27, 28, 34, 35, 40, 44, 47}


def apply_core_i(program: Any, seed_text: str, seed: Any) -> Optional[Dict[str, Any]]:
    n = seed.primary_dell()
    if n not in HANDLED:
        return None
    label = seed.label or ""
    messages = [f"Mandell: {seed.as_mandel()}", f"English: {seed.as_english()}"]
    base = {
        "seed": seed.as_mandel(),
        "english": seed.as_english(),
        "primary": n,
        "messages": messages,
        "new_program": None,
    }
    if n == 27:
        from .core_i_recovery import checkpoint
        try:
            cp = checkpoint(program, stamp=label or None)
            program.last_core_i = {"dell": 27, "path": cp, "ok": True}
            messages.append(f"Checkpoint written: {cp}")
            return {**base, "ok": True, "error": ""}
        except Exception as exc:
            program.last_core_i = {"dell": 27, "ok": False, "error": str(exc)}
            messages.append(f"Checkpoint fail: {exc}")
            return {**base, "ok": False, "error": str(exc)}
    if n == 28:
        from .core_i_recovery import rollback
        target = label if label.endswith(".json") else getattr(program, "last_checkpoint", None)
        try:
            restored = rollback(program.owner, target)
            program.last_core_i = {"dell": 28, "ok": True}
            messages.append("Checkpoint restored.")
            return {**base, "ok": True, "error": "", "new_program": restored}
        except FileNotFoundError:
            program.last_core_i = {"dell": 28, "ok": False, "error": "rollback_missing"}
            messages.append("Rollback missing checkpoint")
            return {**base, "ok": False, "error": "rollback_missing"}
    if n == 34:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        mark = label or "stamp"
        program.last_stamp = {"mark": mark, "ts": ts}
        program.last_core_i = {"dell": 34, "value": program.last_stamp, "ok": True}
        messages.append(f"Stamp: {mark} @ {ts}")
        return {**base, "ok": True, "error": ""}
    if n == 35:
        lab = label.lower()
        if "nursery" in lab:
            pending = program.list_proposals()
            program.last_discover = {"ids": [p.get("id") for p in pending], "count": len(pending), "source": "nursery"}
            messages.append(f"Nursery pending: {len(pending)}")
        else:
            ids = list(program.cube.session.plane.units.keys())
            ns = program.nursery.summary()
            program.last_discover = {"ids": ids, "count": len(ids), "nursery": ns.get("pending", 0)}
            st = program.avatar_status()
            messages.append(f"{st['look']}  {st['describe']}")
            messages.append(f"ideas={len(ids)} nursery={ns.get('pending', 0)}")
        program.last_core_i = {"dell": 35, "value": program.last_discover, "ok": True}
        return {**base, "ok": True, "error": ""}
    if n == 40:
        ideas = len(program.cube.session.plane.units)
        hist = len(getattr(program, "history", []))
        cells = len(program.lattice.cells)
        pending = program.nursery.summary().get("pending", 0)
        approx = ideas * 8 + hist * 4 + cells * 2 + pending * 6
        program.last_measure = {"value": approx, "ideas": ideas, "history": hist, "cells": cells, "pending": pending, "unit": "approx_units"}
        program.last_core_i = {"dell": 40, "value": program.last_measure, "ok": True}
        messages.append("TokenCount (approx session weight):")
        messages.append(f"  ideas={ideas} history={hist} cells={cells} pending={pending}")
        messages.append(f"  approx_units={approx}")
        return {**base, "ok": True, "error": ""}
    if n == 44:
        program.last_core_i = {"dell": 44, "ok": False, "error": "bridge_unavailable", "capability": label or "external", "permission": "offline_origin"}
        messages.append("Bridge unavailable: no external provider bound")
        return {**base, "ok": False, "error": "bridge_unavailable"}
    if n == 47:
        program.last_core_i = {"dell": 47, "ok": False, "error": "embed_unavailable", "representation": "none", "provider": ""}
        messages.append("Embed unavailable: no vector provider bound")
        return {**base, "ok": False, "error": "embed_unavailable"}
    return None
