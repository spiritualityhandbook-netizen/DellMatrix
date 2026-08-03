#!/usr/bin/env python3
"""
Decision shells — multi-valued / fuzzy atoms for Mandell growth (Code Evolution).

Boolean remains the silicon substrate (Python bool).
These shells are higher decision surfaces used where soft gates already matter
(affinity, fog, confirm ranking).

Δ_known runnable today · Δ_unknown stays labeled PROJECTED_NOT_FACT elsewhere.
Lupe5 2026-08-02: VariableShell (beyond static container).
NBD 2026-08-02: ProbabilisticShell (light distribution residue).
NBD 2026-08-02: ConstructiveShell (witness residue).
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, List, Optional, Union, Any, Callable
import math
import random


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


# ------------------------------------------------------------------
# VariableShell — Lupe5 (beyond static named container)
# ------------------------------------------------------------------

class VariableShell:
    """
    Minimal binding beyond pure static container.
    - name remains a label
    - value can be any Python object
    - grade / ternary give a decision surface over the binding itself
    - Boolean substrate is recovered via .bool
    PROJECTED_NOT_FACT: living / morphogenetic growth of the binding.
    """

    __slots__ = ("name", "value", "grade")

    def __init__(self, name: str, value: Any = None, grade: float = 0.5):
        self.name = str(name)
        self.value = value
        self.grade = clamp01(grade)

    @property
    def bool(self) -> bool:
        """Silicon substrate cut."""
        return self.grade >= 0.5

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def decide(self) -> dict:
        return decide(self.grade)

    def __repr__(self) -> str:
        return f"VariableShell({self.name!r}, grade={self.grade:.3f}, bool={self.bool})"


# ------------------------------------------------------------------
# ProbabilisticShell — light distribution residue
# ------------------------------------------------------------------

class ProbabilisticShell:
    """
    Light probabilistic decision surface.
    - p = probability of positive outcome [0,1]
    - sample() draws a Boolean from that p (silicon cut)
    - expected grade remains continuous
    PROJECTED_NOT_FACT: full Bayesian networks or sampling languages.
    """

    __slots__ = ("p",)

    def __init__(self, p: float = 0.5):
        self.p = clamp01(p)

    @property
    def bool(self) -> bool:
        """Silicon substrate via single sample."""
        return random.random() < self.p

    @property
    def grade(self) -> float:
        return self.p

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.p)

    def decide(self) -> dict:
        return decide(self.p)

    def __repr__(self) -> str:
        return f"ProbabilisticShell(p={self.p:.3f})"


# ------------------------------------------------------------------
# ConstructiveShell — NBD addition (witness residue)
# Intuitionistic flavour: truth carries a witness callable.
# Still collapses to Boolean substrate. No full type theory claimed.
# ------------------------------------------------------------------

class ConstructiveShell:
    """
    Minimal constructive / witness decision surface.
    - claim is accepted only when a witness function returns True
    - .bool recovers the silicon cut from the witness result
    - grade is 1.0 when witnessed, 0.0 otherwise (or partial if provided)
    PROJECTED_NOT_FACT: full Martin-Löf type theory, dependent types, or proof assistants.
    """

    __slots__ = ("witness", "_grade")

    def __init__(self, witness: Optional[Callable[[], bool]] = None, grade: Optional[float] = None):
        self.witness = witness
        if grade is not None:
            self._grade = clamp01(grade)
        else:
            self._grade = 1.0 if (witness is not None and witness()) else 0.0

    @property
    def bool(self) -> bool:
        """Silicon substrate via witness execution."""
        if self.witness is None:
            return False
        try:
            return bool(self.witness())
        except Exception:
            return False

    @property
    def grade(self) -> float:
        return self._grade if self.witness is not None else 0.0

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def decide(self) -> dict:
        return decide(self.grade)

    def __repr__(self) -> str:
        has_w = self.witness is not None
        return f"ConstructiveShell(witness={'yes' if has_w else 'no'}, grade={self.grade:.3f}, bool={self.bool})"


def smoke() -> bool:
    print("=== DECISION SHELLS SMOKE (NBD) ===")
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
    vs = VariableShell("x", value=42, grade=0.73)
    rec("VariableShell bool", vs.bool is True)
    rec("VariableShell ternary", vs.ternary is Ternary.POS)
    ps = ProbabilisticShell(0.9)
    rec("ProbabilisticShell grade", abs(ps.grade - 0.9) < 1e-9)
    rec("ProbabilisticShell ternary", ps.ternary is Ternary.POS)
    cs = ConstructiveShell(witness=lambda: True, grade=1.0)
    rec("ConstructiveShell bool", cs.bool is True)
    rec("ConstructiveShell ternary", cs.ternary is Ternary.POS)
    cs2 = ConstructiveShell(witness=None)
    rec("ConstructiveShell no-witness", cs2.bool is False)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
