#!/usr/bin/env python3
"""
Three Absolute Truths — Harmonic Core directives aligned to Mandell Origin.

From Harmonic 14×14 form analysis. Practical law only — no NPC engine.
"""

from __future__ import annotations

from typing import Dict, List

# LatinMandell depth + English surface
TRUTHS: List[Dict[str, str]] = [
    {
        "id": "existence",
        "name": "Existence",
        "tonic": "Tonic / Root",
        "la": "existentia",
        "rule": "Everything declared exists. Context is shifted, not deleted.",
        "form": "Keys permanent. Floor locked. Units may move or soft-forget payload; address remains.",
    },
    {
        "id": "change",
        "name": "Change",
        "tonic": "Harmony / Intervals",
        "la": "mutatio",
        "rule": "Everything changes. Outputs are not clones.",
        "form": "Controlled growth via Nursery. RingedGrowth never silent-writes live plane.",
    },
    {
        "id": "oneness",
        "name": "Oneness",
        "tonic": "Octave",
        "la": "unitas",
        "rule": "The All is the One — different frequencies of one spine.",
        "form": "One lattice · many perceptions. One Dell spine · many surface languages.",
    },
]


def truths() -> List[Dict[str, str]]:
    return [dict(t) for t in TRUTHS]


def truth_ids() -> List[str]:
    return [t["id"] for t in TRUTHS]


def status() -> Dict:
    return {
        "truths": truths(),
        "locked": True,
        "note": "Harmonic Core directives · Origin-aligned · no NPC layer",
    }
