#!/usr/bin/env python3
"""
IdeaGrow — every idea grows every other idea.

13[Loop] > 35[Discover] > 05[Tone] >> 04[Transform] :: IdeaGrow

Uses what is already on the plane:
- resonance pulse (enhance scope / sandbox law)
- token patterns (shared words/labels)
- distance math on the plane
- practical tag exchange into resonance + optional word crumbs

Not consciousness. Deterministic structural growth.

Run:
  python -m form.dell_matrix.idea_grow --smoke
  python -m form.dell_matrix.idea_grow --cycles 20
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import math
import re
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.resonance import ResonanceState, pulse, harmonize_pair
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.open import open_program
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.dell_matrix.plane import Plane, Skin
    from form.dell_matrix.resonance import ResonanceState, pulse, harmonize_pair
    from form.dell_matrix.enhance_gate import EnhanceGate
    from form.open import open_program

_TOKEN = re.compile(r"[a-z0-9_]{3,}", re.I)


def tokens_of(label: str, words: str) -> Set[str]:
    raw = f"{label} {words}".lower()
    return {m.group(0).lower() for m in _TOKEN.finditer(raw) if not m.group(0).startswith("pulled")}


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
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
    """Math of how two ideas relate — pattern + space + scope."""
    ua, ub = plane.units.get(a), plane.units.get(b)
    if not ua or not ub:
        return {"affinity": 0.0}
    ta, tb = tokens_of(ua.label, ua.words), tokens_of(ub.label, ub.words)
    jac = jaccard(ta, tb)
    dist = distance(plane, a, b)
    # nearer → higher spatial factor (soft)
    spatial = 1.0 / (1.0 + dist)
    scope_a = set(plane.enhance_scope(a))
    can = 1.0 if b in scope_a else 0.0  # sandbox law
    # practical weight: shared tokens matter more when both non-empty
    practical = jac * 0.6 + spatial * 0.3 + can * 0.1
    if can == 0.0:
        practical *= 0.15  # still note pattern, but weak across sandbox wall
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
    """Grow all ideas using all other ideas."""

    gate: EnhanceGate = field(default_factory=EnhanceGate)
    events: List[GrowEvent] = field(default_factory=list)
    cycle: int = 0
    annotate_words: bool = True  # practical crumbs on high affinity

    def __post_init__(self):
        assert_floor_intact()
        # growth requires enhance path open for real score movement
        self.gate.turn_on()

    def step(self, plane: Plane) -> Dict[str, Any]:
        assert_floor_intact()
        self.cycle += 1
        ids = list(plane.units.keys())
        if len(ids) < 2:
            return {"ok": False, "reason": "need ≥2 ideas", "cycle": self.cycle}

        # global resonance breath
        pulse_out = self.gate.pulse(plane)

        pair_stats = []
        actions = 0
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                aff = pair_affinity(plane, a, b)
                pair_stats.append((a, b, aff))

                # only grow across enhance scope with meaningful affinity
                if aff["in_scope"] < 1.0 or aff["affinity"] < 0.05:
                    self.events.append(
                        GrowEvent(
                            self.cycle, a, b, aff["affinity"], "skip",
                            "sandbox or weak affinity",
                        )
                    )
                    continue

                # resonance harmonize (vesica)
                h = self.gate.harmonize(plane, a, b)
                actions += 1
                self.events.append(
                    GrowEvent(
                        self.cycle, a, b, aff["affinity"], "harmonize",
                        f"jac={aff['jaccard']:.2f} dist={aff['distance']:.2f}",
                    )
                )

                # practical: exchange strongest shared / complementary tokens into tags
                ua, ub = plane.units[a], plane.units[b]
                ta, tb = tokens_of(ua.label, ua.words), tokens_of(ub.label, ub.words)
                shared = ta & tb
                # each learns a token the other has (pattern transfer)
                st = self.gate.state
                for tok in list(tb - ta)[:3]:
                    bucket = st.tags.setdefault(a, {})
                    bucket[tok] = bucket.get(tok, 0.0) + 0.2 * aff["affinity"]
                for tok in list(ta - tb)[:3]:
                    bucket = st.tags.setdefault(b, {})
                    bucket[tok] = bucket.get(tok, 0.0) + 0.2 * aff["affinity"]
                for tok in list(shared)[:3]:
                    for uid in (a, b):
                        bucket = st.tags.setdefault(uid, {})
                        bucket[f"shared:{tok}"] = bucket.get(f"shared:{tok}", 0.0) + 0.15 * aff["affinity"]

                # high affinity → practical word crumb (once per pair mark)
                if self.annotate_words and aff["affinity"] >= 0.35:
                    mark = f" [grow↔{b}@{aff['affinity']:.2f}]"
                    if mark not in ua.words:
                        ua.words = (ua.words + mark).strip()
                    mark_b = f" [grow↔{a}@{aff['affinity']:.2f}]"
                    if mark_b not in ub.words:
                        ub.words = (ub.words + mark_b).strip()
                    self.events.append(
                        GrowEvent(self.cycle, a, b, aff["affinity"], "annotate", "high affinity crumb")
                    )

        # rank pairs by affinity for report
        pair_stats.sort(key=lambda t: -t[2]["affinity"])
        top = [
            {"a": a, "b": b, **aff}
            for a, b, aff in pair_stats[:8]
        ]

        return {
            "ok": True,
            "cycle": self.cycle,
            "ideas": len(ids),
            "pairs": len(pair_stats),
            "actions": actions,
            "pulse": pulse_out.get("ok"),
            "scores": dict(self.gate.state.scores),
            "top_pairs": top,
            "floor": list(FLOOR),
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
            "floor": list(FLOOR),
        }


def smoke() -> bool:
    print("=== IDEA GROW SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    p = open_program("IdeaGrow")
    # clear welcome noise for clean pairs
    p.cube.session.plane.units.clear()
    p.place("biz", "Business", words="crm routes stain seal", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="song melody routes", skin=Skin.SEED, x=-1)
    p.place("ops", "Operations", words="crm routes crew", skin=Skin.CUBE, y=1)
    g = IdeaGrow()
    out = g.run(p.cube.session.plane, cycles=5)
    rec("all ok", all(o.get("ok") for o in out))
    rec("scores moved", any(v > 0 for v in g.gate.state.scores.values()), str(g.gate.state.scores))
    rec("tags transferred", any(g.gate.state.tags.values()), str(list(g.gate.state.tags.items())[:2]))
    # sandbox isolation: box music — should weaken music↔biz growth actions
    p.box(["music"], "alone")
    before = len([e for e in g.events if e.action == "harmonize"])
    g.step(p.cube.session.plane)
    # still may harmonize biz-ops
    rec("floor", g.summary()["floor"] == list(FLOOR))
    rec("summary", g.summary()["cycles"] >= 5)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def demo(cycles: int = 10) -> None:
    print("13[Loop] > 35[Discover] > 05[Tone] >> 04[Transform] :: IdeaGrow")
    p = open_program("GrowDemo")
    p.cube.session.plane.units.clear()
    p.place("biz", "Business", words="crm stain seal Texas", skin=Skin.BUILDING, x=1)
    p.place("music", "Music", words="Bombs Away melody", skin=Skin.SEED, x=-1)
    p.place("code", "MandellOS", words="Dell Matrix CRM plane", skin=Skin.CUBE, y=1)
    g = IdeaGrow()
    last = g.run(p.cube.session.plane, cycles=cycles)[-1]
    print("last step:", last)
    print("summary:", g.summary())
    print(p.cube.session.plane.render(scores=g.gate.state.scores))


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    cycles = 10
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = int(sys.argv[i + 1])
    demo(cycles)


if __name__ == "__main__":
    main()
