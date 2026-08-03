#!/usr/bin/env python3
"""
Decision shells — multi-valued / fuzzy atoms for Mandell growth (Code Evolution).

Boolean remains the silicon substrate of the host Python runtime.
These shells are higher decision surfaces.

Δ_known is permanent fuel — never closed.
Δ_unknown stays labeled PROJECTED_NOT_FACT.

DEFAULT GROWTH PATH:
  prefer_open(shell) keeps graded / ternary information and only collapses
  to True/False when .as_bool() is called explicitly.

MULTI-DIRECTIONAL FLOW (permanent continuous fuel):
  Code in nature does not move left-to-right on a page.
  Code is shared-context language executable mentally or digitally.
  8 cardinal + 9 upper + 9 lower directions.

  FlowShell          = observation / movement atom
  look(direction)    = single-direction observation (looking=True)
  move(direction)    = single-direction movement (looking=False)
  multi_look(...)    = fan-out observation
  aggregate_looks()  = combine → GrowthResidue → prefer_open

Minimal usage:
  one_look = look(Cardinal.N, grade=0.7)
  one_move = move(Cardinal.E, grade=0.6)
  looks = multi_look([Cardinal.N, Cardinal.E, Upper.U], grade=0.6)
  surface = aggregate_looks(looks)
"""

from __future__ import annotations

from enum import Enum
from typing import Iterable, List, Optional, Union, Any, Callable, Sequence
import math
import random


class Ternary(str, Enum):
    NEG = "neg"
    ZERO = "zero"
    POS = "pos"


class Cardinal(str, Enum):
    N = "N"
    NE = "NE"
    E = "E"
    SE = "SE"
    S = "S"
    SW = "SW"
    W = "W"
    NW = "NW"


class Upper(str, Enum):
    U = "U"
    UN = "UN"
    UNE = "UNE"
    UE = "UE"
    USE = "USE"
    US = "US"
    USW = "USW"
    UW = "UW"
    UNW = "UNW"


class Lower(str, Enum):
    D = "D"
    DN = "DN"
    DNE = "DNE"
    DE = "DE"
    DSE = "DSE"
    DS = "DS"
    DSW = "DSW"
    DW = "DW"
    DNW = "DNW"


Direction = Union[Cardinal, Upper, Lower]


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


class GrowthResidue:
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


class OpenShell:
    """
    Decision surface that defers the Boolean cut.
    Primary identity: grade + ternary + optional witness.
    .as_bool() is the only explicit last-resort silicon cut.
    bool(open_shell) raises TypeError.
    PROJECTED_NOT_FACT: true non-Boolean host runtime.
    """

    __slots__ = ("grade", "witness", "label")

    def __init__(self, grade: float = 0.5, witness: Optional[Callable[[], bool]] = None, label: str = "open"):
        self.grade = clamp01(grade)
        self.witness = witness
        self.label = str(label)

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def as_bool(self) -> bool:
        if self.witness is not None:
            try:
                return bool(self.witness())
            except Exception:
                return False
        return self.grade >= 0.5

    def decide(self) -> dict:
        return {
            "score": self.grade,
            "ternary": self.ternary.value,
            "gate": soft_gate(self.grade),
            "label": self.label,
            "collapsed": False,
            "note": "OpenShell · Boolean cut deferred · host still has Boolean underneath · PROJECTED_NOT_FACT on non-Boolean runtime",
        }

    def __bool__(self) -> bool:
        raise TypeError(
            "OpenShell refuses silent Boolean collapse. "
            "Call .as_bool() explicitly if the silicon cut is required."
        )

    def __repr__(self) -> str:
        return f"OpenShell(label={self.label!r}, grade={self.grade:.3f}, ternary={self.ternary.value}, collapsed=False)"


def prefer_open(shell: Any, label: str = "preferred") -> OpenShell:
    """
    DEFAULT GROWTH PATH.
    Convert any collapsing shell (including FlowShell) into OpenShell form
    so graded information is kept and the Boolean cut is deferred.
    """
    if isinstance(shell, OpenShell):
        return shell
    grade = 0.5
    witness = None
    if hasattr(shell, "grade"):
        grade = clamp01(getattr(shell, "grade"))
    elif isinstance(shell, (int, float)):
        grade = clamp01(float(shell))
    elif isinstance(shell, bool):
        grade = 1.0 if shell else 0.0
    elif isinstance(shell, Ternary):
        grade = to_fuzzy(shell)
    if hasattr(shell, "witness"):
        witness = getattr(shell, "witness")
    return OpenShell(grade=grade, witness=witness, label=label)


class ReversibleShell:
    """
    Classical reversible decision surface.
    Keeps both the forward decision and an inverse recovery path.
    Still sits on Boolean host.
    PROJECTED_NOT_FACT: native quantum superposition or entanglement.
    """

    __slots__ = ("forward", "inverse", "label")

    def __init__(self, forward: float, inverse: Any = None, label: str = "reversible"):
        self.forward = clamp01(forward)
        self.inverse = inverse
        self.label = str(label)

    @property
    def grade(self) -> float:
        return self.forward

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.forward)

    def recover(self) -> Any:
        return self.inverse

    def decide(self) -> dict:
        return {
            "score": self.forward,
            "ternary": self.ternary.value,
            "gate": soft_gate(self.forward),
            "label": self.label,
            "reversible": True,
            "has_inverse": self.inverse is not None,
            "note": "ReversibleShell · classical reversible residue · Boolean host intact · PROJECTED_NOT_FACT on quantum runtime",
        }

    def __repr__(self) -> str:
        return f"ReversibleShell(forward={self.forward:.3f}, has_inverse={self.inverse is not None}, label={self.label!r})"


class FlowShell:
    """
    Multi-directional decision / observation surface.

    Architecture pattern:
      - grade: continuous strength
      - direction: 8 cardinal | 9 upper | 9 lower
      - looking: True = observe without moving; False = move
      - context: shared-context language label

    No forced left-to-right order.
    Lift via .as_open() or prefer_open(flow).
    PROJECTED_NOT_FACT: full 3D matrix navigation runtime.
    """

    __slots__ = ("grade", "direction", "looking", "context")

    def __init__(
        self,
        grade: float = 0.5,
        direction: Optional[Direction] = None,
        looking: bool = False,
        context: str = "shared",
    ):
        self.grade = clamp01(grade)
        self.direction = direction
        self.looking = bool(looking)
        self.context = str(context)

    @property
    def ternary(self) -> Ternary:
        return from_fuzzy(self.grade)

    def as_open(self, label: str = "flow") -> OpenShell:
        return OpenShell(grade=self.grade, label=label)

    def decide(self) -> dict:
        dir_val = self.direction.value if self.direction is not None else None
        return {
            "score": self.grade,
            "ternary": self.ternary.value,
            "gate": soft_gate(self.grade),
            "direction": dir_val,
            "looking": self.looking,
            "context": self.context,
            "note": "FlowShell · multi-directional · shared-context language · no forced left-to-right · Boolean host intact · PROJECTED_NOT_FACT on full 3D navigation",
        }

    def __repr__(self) -> str:
        d = self.direction.value if self.direction is not None else "none"
        mode = "looking" if self.looking else "moving"
        return f"FlowShell(grade={self.grade:.3f}, dir={d}, {mode}, context={self.context!r})"


def look(
    direction: Direction,
    grade: float = 0.5,
    context: str = "shared",
) -> FlowShell:
    """Single-direction observation (looking=True, no movement)."""
    return FlowShell(grade=clamp01(grade), direction=direction, looking=True, context=context)


def move(
    direction: Direction,
    grade: float = 0.5,
    context: str = "shared",
) -> FlowShell:
    """Single-direction movement (looking=False). Companion to look()."""
    return FlowShell(grade=clamp01(grade), direction=direction, looking=False, context=context)


def multi_look(
    directions: Sequence[Direction],
    grade: float = 0.5,
    context: str = "shared",
    grades: Optional[Sequence[float]] = None,
) -> List[FlowShell]:
    """
    Observe several directions without moving (fan-out observation).
    Optional per-direction grades.
    PROJECTED_NOT_FACT: full simultaneous 3D navigation runtime.
    """
    dirs = list(directions)
    if grades is not None:
        if len(grades) != len(dirs):
            raise ValueError("grades length must match directions length")
        g_list = [clamp01(g) for g in grades]
    else:
        g = clamp01(grade)
        g_list = [g] * len(dirs)
    return [
        FlowShell(grade=g_list[i], direction=dirs[i], looking=True, context=context)
        for i in range(len(dirs))
    ]


def aggregate_looks(
    looks: Sequence[FlowShell],
    mode: str = "avg",
    label: str = "aggregate-look",
) -> OpenShell:
    """
    Combine multiple look / move / multi_look / FlowShell results into one deferred-cut surface.
    Uses GrowthResidue then prefer_open. Boolean cut stays deferred.
    """
    residue = GrowthResidue(*looks, mode=mode)
    return prefer_open(residue, label=label)


def smoke() -> bool:
    print("=== DECISION SHELLS SMOKE ===")
    print("Default growth path: prefer_open(shell)")
    print("Multi-directional: look + move + FlowShell + multi_look + aggregate_looks")
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
    op = OpenShell(grade=0.73, label="evo-pressure")
    rec("OpenShell grade", abs(op.grade - 0.73) < 1e-9)
    rec("OpenShell as_bool", op.as_bool() is True)
    refused = False
    try:
        bool(op)
    except TypeError:
        refused = True
    rec("OpenShell refuses silent bool", refused is True)
    pref = prefer_open(vs, label="from-variable")
    rec("prefer_open type", isinstance(pref, OpenShell))
    rev = ReversibleShell(forward=0.8, inverse={"prior": 0.3}, label="rev-test")
    rec("ReversibleShell grade", abs(rev.grade - 0.8) < 1e-9)
    rec("ReversibleShell recover", rev.recover() == {"prior": 0.3})
    flow = FlowShell(grade=0.65, direction=Cardinal.NE, looking=True, context="shared")
    rec("FlowShell grade", abs(flow.grade - 0.65) < 1e-9)
    rec("FlowShell direction", flow.direction is Cardinal.NE)
    rec("FlowShell looking", flow.looking is True)
    flow_open = flow.as_open()
    rec("FlowShell as_open", isinstance(flow_open, OpenShell))
    one = look(Cardinal.N, grade=0.7, context="single")
    rec("look type", isinstance(one, FlowShell))
    rec("look looking", one.looking is True)
    rec("look direction", one.direction is Cardinal.N)
    moved = move(Cardinal.E, grade=0.55, context="path")
    rec("move type", isinstance(moved, FlowShell))
    rec("move not looking", moved.looking is False)
    rec("move direction", moved.direction is Cardinal.E)
    looks = multi_look([Cardinal.N, Cardinal.E, Upper.U], grade=0.6, context="audit")
    rec("multi_look count", len(looks) == 3)
    rec("multi_look all looking", all(f.looking for f in looks))
    looks2 = multi_look([Cardinal.S, Lower.D], grades=[0.4, 0.9], context="weighted")
    rec("multi_look per-grade", abs(looks2[0].grade - 0.4) < 1e-9 and abs(looks2[1].grade - 0.9) < 1e-9)
    agg = aggregate_looks(looks, mode="avg", label="agg-test")
    rec("aggregate_looks type", isinstance(agg, OpenShell))
    rec("aggregate_looks grade", 0.0 <= agg.grade <= 1.0)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
