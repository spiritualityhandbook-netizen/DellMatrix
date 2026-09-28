#!/usr/bin/env python3
"""Mandell seed executor — front door.

Multi-atom seeds and Core II (51-99) run through chain_exec so every atom executes.
Single-atom CORE_I (00-50) uses the original leaf implementation in executor_leaf.py.
"""
from __future__ import annotations

from typing import Any, Dict

from .seed import parse_seed


def execute_seed(program: Any, seed_text: str, _leaf: bool = False) -> Dict[str, Any]:
    s = parse_seed(seed_text)
    if not s.ok:
        return {"ok": False, "error": s.error, "messages": [f"Seed error: {s.error}"]}

    if not _leaf:
        primary = s.primary_dell()
        multi = len(s.atoms) > 1
        core_ii = primary is not None and 51 <= int(primary) <= 99
        if multi or core_ii:
            from .chain_exec import execute_chain
            return execute_chain(program, s, seed_text)

    from .executor_leaf import execute_seed as execute_leaf
    return execute_leaf(program, seed_text)
