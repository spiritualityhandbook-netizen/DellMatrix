#!/usr/bin/env python3
"""Mandell seed executor — front door.

Multi-atom seeds and Core II (51-99) run through chain_exec so every atom executes.
Single-atom CORE_I (00-50) uses the original leaf implementation in executor_leaf.py.
Closable Core I recovery/measure/external contracts run through core_i_ops.
Dell 21/22 live-unit transforms use live_identity lineage.
"""
from __future__ import annotations

from typing import Any, Dict

from .seed import parse_seed


def execute_seed(program: Any, seed_text: str, _leaf: bool = False) -> Dict[str, Any]:
    s = parse_seed(seed_text)
    if not s.ok:
        return {"ok": False, "error": s.error, "messages": [f"Seed error: {s.error}"]}

    from .core_i_ops import HANDLED, apply_core_i
    primary = s.primary_dell()
    if primary in HANDLED and len(s.atoms) == 1:
        handled = apply_core_i(program, seed_text, s)
        if handled is not None:
            return handled

    if primary in (21, 22):
        from .live_identity import merge_live, split_live
        rec = merge_live(program, s.label or "") if primary == 21 else split_live(program, s.label or "")
        messages = [f"Mandell: {s.as_mandel()}", f"English: {s.as_english()}"]
        if not rec.get("ok"):
            messages.append(f"{'Merge' if primary == 21 else 'Split'} failed: {rec.get('error')}")
            return {
                "ok": False,
                "error": rec.get("error") or "missing_source",
                "seed": s.as_mandel(),
                "english": s.as_english(),
                "primary": primary,
                "messages": messages,
                "new_program": None,
            }
        if primary == 21:
            messages.append(f"Merged → {rec['id']} parents={rec['parents']}")
        else:
            messages.append(f"Split → {' + '.join(rec['created'])}")
        if hasattr(program, "note_seed"):
            program.note_seed(primary, "Merge" if primary == 21 else "Split", rec.get("id") or rec.get("source") or "")
        return {
            "ok": True,
            "seed": s.as_mandel(),
            "english": s.as_english(),
            "primary": primary,
            "messages": messages,
            "new_program": None,
        }

    if not _leaf:
        primary = s.primary_dell()
        multi = len(s.atoms) > 1
        core_ii = primary is not None and 51 <= int(primary) <= 99
        if multi or core_ii:
            from .chain_exec import execute_chain
            return execute_chain(program, s, seed_text)

    from .executor_leaf import execute_seed as execute_leaf
    return execute_leaf(program, seed_text)
