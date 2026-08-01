#!/usr/bin/env python3
"""
DEPRECATED for public growth — experimental resonance only.

NBD 2026-08-01: One growth entrypoint.
Public / controlled growth path is RingedGrowth only.

IdeaGrow mutates live plane tags and word crumbs.
That violates the Nursery quarantine law for average-user growth.
Keep this file for research / resonance experiments only.
Do not call from Program, REPL, or visual for user-facing growth.

Correct public path:
  program.grow_ideas(cycles)  →  RingedGrowth.run(...)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set
import math
import re
import sys
import warnings

warnings.warn(
    "idea_grow.IdeaGrow is deprecated for public growth. Use RingedGrowth via program.grow_ideas()",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.open import open_program
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.open import open_program

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)


def tokens_of(label: str, words: str) -> Set[str]:
    raw = f"{label} {words}".lower()
    return {m.group(0).lower() for m in _TOKEN.finditer(raw) if not m.group(0).startswith("pulled")}


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def distance(plane: Plane, a: str, b: str) -> float:
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return float("inf")
    return math.hypot(ua.x - ub.x, ua.y - ub.y)


def pair_affinity(plane: Plane, a: str, b: str) -> Dict[str, float]:
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return {"affinity": 0.0}
    ta, tb = tokens_of(ua.label, ua.words), tokens_of(ub.label, ub.words)
    jac = jaccard(ta, tb)
    dist = distance(plane, a, b)
    spatial = 1.0 / (1.0 + dist)
    scope_a = set(plane.enhance_scope(a))
    can = 1.0 if b in scope_a else 0.0
    practical = jac * 0.6 + spatial * 0.3 + can * 0.1
    if can == 0.0:
        practical *= 0.15
    return {
        "jaccard": jac,
        "distance": dist if dist != float("inf") else -1.0,
        "spatial": spatial,
        "in_scope": can,
        "affinity": practical,
        "shared_tokens": float(len(ta & tb)),
    }


@dataclass
class GrowEvent:
    cycle: int
    source: str
    target: str
    affinity: float
    action: str
    detail: str


@dataclass
class IdeaGrow:
    """Experimental live-plane resonance only. Not the public growth path."""

    gate: EnhanceGate = field(default_factory=EnhanceGate)
    events: List[GrowEvent] = field(default_factory=list)
    cycle: int = 0
    annotate_words: bool = True

    def __post_init__(self):
        assert_floor_intact()
        self.gate.turn_on()

    def step(self, plane: Plane) -> Dict[str, Any]:
        assert_floor_intact()
        self.cycle += 1
        ids = list(plane.units.keys())
        if len(ids) < 2:
            return {"ok": False, "reason": "need ≥2 ideas", "cycle": self.cycle}

        pulse_out = self.gate.pulse(plane)
        pair_stats = []
        actions = 0
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                aff = pair_affinity(plane, a, b)
                pair_stats.append((a, b, aff))
                if aff["in_scope"] < 1.0 or aff["affinity"] < 0.05:
                    self.events.append(
                        GrowEvent(self.cycle, a, b, aff["affinity"], "skip", "sandbox or weak")
                    )
                    continue
                self.gate.harmonize(plane, a, b)
                actions += 1
                self.events.append(
                    GrowEvent(
                        self.cycle, a, b, aff["affinity"], "harmonize",
                        f"jac={aff['jaccard']:.2f}",
                    )
                )
                ua, ub = plane.units[a], plane.units[b]
                ta, tb = tokens_of(ua.label, ua.words), tokens_of(ub.label, ub.words)
                st = self.gate.state
                for tok in list(tb - ta)[:3]:
                    bucket = st.tags.setdefault(a, {})
                    bucket[tok] = bucket.get(tok, 0.0) + 0.2 * aff["affinity"]
                for tok in list(ta - tb)[:3]:
                    bucket = st.tags.setdefault(b, {})
                    bucket[tok] = bucket.get(tok, 0.0) + 0.2 * aff["affinity"]

        pair_stats.sort(key=lambda t: -t[2]["affinity"])
        top = [{"a": a, "b": b, **aff} for a, b, aff in pair_stats[:8]]
        return {
            "ok": True,
            "cycle": self.cycle,
            "ideas": len(ids),
            "pairs": len(pair_stats),
            "actions": actions,
            "pulse": pulse_out.get("ok"),
            "scores": dict(self.gate.state.scores),
            "top_pairs": top,
            "deprecated": True,
            "note": "Use RingedGrowth / program.grow_ideas for controlled growth",
        }

    def run(self, plane: Plane, cycles: int = 10) -> List[Dict[str, Any]]:
        return [self.step(plane) for _ in range(max(1, cycles))]

    def summary(self) -> Dict[str, Any]:
        by_action = {}
        for e in self.events:
            by_action[e.action] = by_action.get(e.action, 0) + 1
        return {
            "cycles": self.cycle,
            "events": len(self.events),
            "by_action": by_action,
            "deprecated": True,
            "floor": list(FLOOR),
        }


def smoke() -> bool:
    print("=== IDEA GROW (deprecated) SMOKE ===")
    print("Note: public growth path is RingedGrowth")
    p = open_program("IdeaGrowDep")
    p.cube.session.plane.units.clear()
    p.place("a", "A", words="one", skin=Skin.CUBE)
    p.place("b", "B", words="two", skin=Skin.CUBE)
    g = IdeaGrow()
    out = g.run(p.cube.session.plane, cycles=2)
    ok = all(o.get("ok") for o in out)
    print("PASS" if ok else "FAIL")
    return ok


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    print("idea_grow is deprecated for public growth.")
    print("Use: program.grow_ideas() → RingedGrowth")


if __name__ == "__main__":
    main()
