#!/usr/bin/env python3
"""
Mandel Lang operator surface → Dell map (high-S cheat-sheet).

Visual/symbolic operators from Codex mapped onto existing Dells where practical.
"""

from __future__ import annotations

from typing import Dict, List, Optional

# operator glyph/token → dell + sense
OPERATORS: Dict[str, Dict] = {
    "[-]": {"dell": 16, "name": "Decay/Negate", "sense": "logical inversion / polarity flip"},
    "[?]": {"dell": 35, "name": "Discover", "sense": "query / unknown point"},
    "[-?]": {"dell": 35, "name": "Discover", "sense": "deep research · total knowledge seek"},
    "[@>]": {"dell": 15, "name": "Map", "sense": "locator / focus toward coordinate"},
    "[-@>]": {"dell": 24, "name": "Unlock", "sense": "absence of focus / exclusion"},
    "[->]": {"dell": 13, "name": "Loop", "sense": "sequential flow"},
    "[-->]": {"dell": 13, "name": "Loop", "sense": "sequential flow (long)"},
    "[↓]": {"dell": 6, "name": "Cycle", "sense": "descending control layer"},
    "[↑]": {"dell": 33, "name": "Resume", "sense": "fallback upstream / loopback"},
    "[↘]": {"dell": 14, "name": "Bind", "sense": "data forward diagonal"},
    "[↙]": {"dell": 14, "name": "Bind", "sense": "data backward diagonal"},
    "[↗]": {"dell": 11, "name": "Architect", "sense": "metadata forward"},
    "[↖]": {"dell": 11, "name": "Architect", "sense": "metadata backward"},
    "[⇕]": {"dell": 7, "name": "Link", "sense": "bidirectional meta-bind"},
    "[:]": {"dell": 15, "name": "Map", "sense": "label-value binder"},
    "[=]": {"dell": 8, "name": "Create", "sense": "declaration of node/rule"},
    "[&]": {"dell": 21, "name": "Merge", "sense": "co-target multiple sinks"},
    "[>>>]": {"dell": 30, "name": "Expand", "sense": "massive jump across layers"},
    "[{}]": {"dell": 23, "name": "Lock", "sense": "scope block / local isolate"},
    "[___]": {"dell": 37, "name": "Stream", "sense": "channel path / highway"},
}


def lookup(op: str) -> Optional[Dict]:
    key = (op or "").strip()
    if key in OPERATORS:
        return dict(OPERATORS[key])
    # try bracket normalize
    if not key.startswith("["):
        key2 = f"[{key}]"
        if key2 in OPERATORS:
            return dict(OPERATORS[key2])
    return None


def list_ops() -> List[Dict]:
    return [{"op": k, **v} for k, v in OPERATORS.items()]


def seed_for(op: str, label: str = "") -> Optional[str]:
    info = lookup(op)
    if not info:
        return None
    d = int(info["dell"])
    name = info["name"].split("/")[0].strip()
    body = f"{d:02d}[{name}]"
    if label:
        body = f"{body} :: {label[:40]}"
    return body
