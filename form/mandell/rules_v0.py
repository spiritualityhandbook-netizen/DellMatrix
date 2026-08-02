#!/usr/bin/env python3
"""
Mandel Lang — 7 Core Rules (V0 locked subset for Origin).

High-S intake from Mandel Syntactic Codex.
These constrain execution; they do not replace Dells 00–50.
"""

from __future__ import annotations

from typing import Dict, List

RULES: List[Dict[str, str]] = [
    {
        "id": 1,
        "name": "Free-Origin",
        "rule": "Absolute origin is locked. All execution flows must trace back to origin.",
        "form": "Floor + Program origin + lattice (0,0,0). Nova is not Floor.",
    },
    {
        "id": 2,
        "name": "Flow-Priority",
        "rule": "Prefer Right (→), then Down (↓), then Diagonal (↘/↙). Up (↑) is fallback for loops only.",
        "form": "Seed flow uses > and >>; growth loops are explicit fallback paths.",
    },
    {
        "id": 3,
        "name": "No-Orphan",
        "rule": "Every node, port, source, sink has an active trace to the flow.",
        "form": "History note_seed · Nursery confirm · no silent live writes.",
    },
    {
        "id": 4,
        "name": "Zeros / Sockets",
        "rule": "Typed sockets define entry/exit. Zero coordinate cannot initialize Nova_Line.",
        "form": "Floor locked; Nova = cheat-only edge — never main init.",
    },
    {
        "id": 5,
        "name": "Diagonal Cross-Layer",
        "rule": "Diagonals route data (↘/↙) and metadata (↗/↖) across layers.",
        "form": "Documented; full diagonal grid runtime deferred (low-S for now).",
    },
    {
        "id": 6,
        "name": "Symmetry",
        "rule": "Mirrored elements share operational type and structural weight.",
        "form": "Perception duals (cube↔sphere, square↔circle) honor pair symmetry.",
    },
    {
        "id": 7,
        "name": "Fractal Nesting",
        "rule": "Any container/cell may host an independent nested Mandel plane.",
        "form": "RingedGrowth cycles + session containers; full nested Program deferred.",
    },
]


def rules() -> List[Dict[str, str]]:
    return [dict(r) for r in RULES]


def status() -> Dict:
    return {
        "spec": "Mandel Lang V0 rules · Origin subset",
        "count": len(RULES),
        "rules": rules(),
        "locked": True,
    }
