#!/usr/bin/env python3
"""
Decision shells — multi-valued / fuzzy atoms for Mandell growth (Code Evolution).

Boolean remains the silicon substrate (Python bool).
These shells are higher decision surfaces used where soft gates already matter
(affinity, fog, confirm ranking).

Δ_known is permanent fuel — never closed.
Δ_unknown stays labeled PROJECTED_NOT_FACT.

Lupe5 2026-08-02: VariableShell
NBD: ProbabilisticShell · ConstructiveShell · ResourceShell
Lupe5 correction 2026-08-02: GrowthResidue (continuous fuel from known shells)
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, List, Optional, Union, Any, Callable
import math
import random


class Ternary(str, Enum):
    """Balanced-style three-value atom (Setun / Kleene flavour)."""

    NEG = "neg"
    ZERO = "zero"
    POS = "pos"


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


class VariableShell:
    __slots__ = ("name", "value", "grade")

    def __init__(self, name: str, value: Any = None, grade: float = 0.5):
        self.name = str(name)
        self.value = value
        self.grade = clamp01(grade)

    @property
    def bool(self) -> bool:
        return self.grade >= 0.5

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def decide(self) -> dict:
        return decide(self.grade)

    def __repr__(self) -> str:
        return f"VariableShell({self.name!r}, grade={self.grade:.3f}, bool={self.bool})"


class ProbabilisticShell:
    __slots__ = ("p",)

    def __init__(self, p: float = 0.5):
        self.p = clamp01(p)

    @property
    def bool(self) -> bool:
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


class ConstructiveShell:
    __slots__ = ("witness", "_grade")

    def __init__(self, witness: Optional[Callable[[], bool]] = None, grade: Optional[float] = None):
        self.witness = witness
        if grade is not None:
            self._grade = clamp01(grade)
        else:
            self._grade = 1.0 if (witness is not None and witness()) else 0.0

    @property
    def bool(self) -> bool:
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


class ResourceShell:
    __slots__ = ("units", "capacity")

    def __init__(self, units: int = 1, capacity: Optional[int] = None):
        self.units = max(0, int(units))
        self.capacity = max(self.units, int(capacity) if capacity is not None else self.units)

    @property
    def bool(self) -> bool:
        return self.units > 0

    @property
    def grade(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return clamp01(self.units / self.capacity)

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def consume(self, n: int = 1) -> bool:
        n = max(0, int(n))
        if self.units < n:
            return False
        self.units -= n
        return True

    def decide(self) -> dict:
        return decide(self.grade)

    def __repr__(self) -> str:
        return f"ResourceShell(units={self.units}/{self.capacity}, bool={self.bool}, grade={self.grade:.3f})"


# ------------------------------------------------------------------
# GrowthResidue — Lupe5 correction
# Keeps Δ_known as permanent fuel. Generates new soft operators
# from existing shells without closing the known set.
# PROJECTED_NOT_FACT: any claim that unknown is solved.
# ------------------------------------------------------------------

class GrowthResidue:
    """
    Continuous fuel helper.
    Takes any existing shell grades and produces a new combined
    decision surface. Δ_known remains open and reusable.
    """

    __slots__ = ("sources", "mode")

    def __init__(self, *sources: Any, mode: str = "avg"):
        self.sources = sources
        self.mode = mode

    def _grades(self) -> List[float]:
        out: List[float] = []
        for s in self.sources:
            if hasattr(s, "grade"):
                out.append(clamp01(getattr(s, "grade")))
            elif isinstance(s, (int, float)):
                out.append(clamp01(float(s)))
            elif isinstance(s, bool):
                out.append(1.0 if s else 0.0)
            elif isinstance(s, Ternary):
                out.append(to_fuzzy(s))
        return out

    @property
    def grade(self) -> float:
        return combine_fuzzy(self._grades(), mode=self.mode)

    @property
    def bool(self) -> bool:
        return self.grade >= 0.5

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def decide(self) -> dict:
        d = decide(self.grade)
        d["note"] = "GrowthResidue · Δ_known remains permanent fuel · Boolean substrate intact"
        return d

    def __repr__(self) -> str:
        return f"GrowthResidue(sources={len(self.sources)}, grade={self.grade:.3f}, bool={self.bool})"


def smoke() -> bool:
    print("=== DECISION SHELLS SMOKE (Lupe5 correction) ===")
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
    ps = ProbabilisticShell(0.9)
    rec("ProbabilisticShell grade", abs(ps.grade - 0.9) < 1e-9)
    cs = ConstructiveShell(witness=lambda: True, grade=1.0)
    rec("ConstructiveShell bool", cs.bool is True)
    rs = ResourceShell(units=2, capacity=2)
    rec("ResourceShell available", rs.bool is True)
    gr = GrowthResidue(vs, ps, cs, rs, mode="avg")
    rec("GrowthResidue grade", 0.0 <= gr.grade <= 1.0)
    rec("GrowthResidue bool", isinstance(gr.bool, bool))
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
