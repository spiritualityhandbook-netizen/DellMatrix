#!/usr/bin/env python3
"""CORE_I leaf executor.

Historical full leaf lives at executor.py SHA 670faba8577a7b84cc2f601443067ef2c17c6e0f.
This module must keep execute_seed(program, seed_text) for the front-door leaf path.

Status: PLACEHOLDER. Single-atom CORE_I runtime is not claimed complete in this file.
Restore the 670faba leaf body here without the chain dispatch (dispatch stays in executor.py).
"""
from __future__ import annotations

from typing import Any, Dict

from .seed import parse_seed


def execute_seed(program: Any, seed_text: str) -> Dict[str, Any]:
    s = parse_seed(seed_text)
    if not s.ok:
        return {"ok": False, "error": s.error, "messages": [f"Seed error: {s.error}"]}
    primary = s.primary_dell()
    return {
        "ok": False,
        "error": "CORE_I_LEAF_NOT_RESTORED",
        "seed": s.as_mandel() if s.ok else "",
        "english": s.as_english() if s.ok else "",
        "primary": primary,
        "messages": [
            "CORE_I leaf placeholder",
            "Restore executor body from SHA 670faba8577a7b84cc2f601443067ef2c17c6e0f",
            "PROJECTED_NOT_FACT: this is not the historical CORE_I runtime",
        ],
        "new_program": None,
    }
