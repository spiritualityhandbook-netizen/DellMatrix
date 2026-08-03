#!/usr/bin/env python3
"""
Decision shells — multi-valued / fuzzy atoms for Mandell growth (Code Evolution).

Boolean remains the silicon substrate (Python bool).
These shells are higher decision surfaces used where soft gates already matter
(affinity, fog, confirm ranking).

Δ_known runnable today · Δ_unknown stays labeled PROJECTED_NOT_FACT elsewhere.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, List, Optional, Union
import math


class Ternary(str, Enum):
    """Balanced-style three-value atom (Setun / Kleene flavour)."""

    NEG = "neg"      # -1 · reject / false-leaning
    ZERO = "zero"    #  0 · unknown / hold
    POS = "pos"      # +1 · accept / true-leaning


def clamp01(x: float) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(v) or math.isinf(v):
        return 0.0
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def from_bool(b: bool) -> Ternary:
    return Ternary.POS if b else Ternary.NEG


def from_fuzzy(x: float, *, low: float = 0.33, high: float = 0.66) -> Ternary:
    """Map continuous [0,1] → ternary."""
    v = clamp01(x)
    if v < low:
        return Ternary.NEG
    if v > high:
        return Ternary.POS
    return Ternary.ZERO


def to_fuzzy(t: Ternary) -> float:
    if t is Ternary.POS:
        return 1.0
    if t is Ternary.NEG:
        return 0.0
    return 0.5


def soft_gate(
    score: float,
    *,
    solstice: float = 0.28,
    equinox: float = 0.16,
    standstill: float = 0.10,
) -> str:
    """Same thresholds as RingedGrowth — explicit decision surface."""
    s = float(score)
    if s >= solstice:
        return "Solstice"
    if s >= equinox:
        return "Equinox"
    if s >= standstill:
        return "Standstill"
    return "None"


def combine_fuzzy(values: Iterable[float], mode: str = "avg") -> float:
    xs = [clamp01(v) for v in values]
    if not xs:
        return 0.0
    m = (mode or "avg").lower()
    if m == "min":
        return min(xs)
    if m == "max":
        return max(xs)
    return sum(xs) / len(xs)


def decide(
    *sources: Union[bool, float, Ternary],
    mode: str = "avg",
) -> dict:
    """
    Unify bool / fuzzy / ternary sources into one decision report.
    Runnable today — does not replace host Boolean.
    """
    fuzz: List[float] = []
    for s in sources:
        if isinstance(s, bool):
            fuzz.append(1.0 if s else 0.0)
        elif isinstance(s, Ternary):
            fuzz.append(to_fuzzy(s))
        else:
            fuzz.append(clamp01(float(s)))
    score = combine_fuzzy(fuzz, mode=mode)
    tern = from_fuzzy(score)
    gate = soft_gate(score)
    return {
        "score": score,
        "ternary": tern.value,
        "gate": gate,
        "sources": len(fuzz),
        "mode": mode,
        "note": "Boolean substrate intact · shell is soft decision surface",
    }


def smoke() -> bool:
    print("=== DECISION SHELLS SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    rec("from_bool", from_bool(True) is Ternary.POS)
    rec("from_fuzzy mid", from_fuzzy(0.5) is Ternary.ZERO)
    rec("clamp", clamp01(2.5) == 1.0)
    d = decide(True, 0.8, Ternary.ZERO, mode="avg")
    rec("decide score", 0.0 <= d["score"] <= 1.0)
    rec("soft_gate", soft_gate(0.3) == "Solstice")
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
