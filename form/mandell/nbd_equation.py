#!/usr/bin/env python3
"""NBD Equation — reassess after plane vision lock."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import json

FLOOR = ("Alpha", "Delta", "Omega", "Omni")
L_STAR = 3
SPINE = ("mandell", "dell_matrix", "duobeta", "plane", "perspective", "sandbox", "resonance")


@dataclass
class Capability:
    id: str
    term: str
    manor: str
    dell: int
    spine: str
    level_now: int
    level_goal: int = L_STAR
    floor_safe: bool = True
    manifest_complete: bool = True
    seq: float = 0.5

    def phi(self) -> float:
        return 1.0 if (self.floor_safe and self.manifest_complete) else 0.0

    def rho(self) -> float:
        try:
            i = SPINE.index(self.spine)
        except ValueError:
            i = len(SPINE)
        return max(0.35, 1.0 - 0.08 * i)

    def lambda_def(self) -> float:
        return float(max(0, self.level_goal - self.level_now))

    def score(self) -> float:
        return self.phi() * self.rho() * self.lambda_def() * self.seq


def goal_star() -> List[Capability]:
    return [
        Capability("floor", "Floor", "Immutable base", 23, "mandell", 3, seq=1.0),
        Capability("registry", "Registry", "Dell 00–50", 11, "mandell", 3, seq=0.98),
        Capability("manifest", "Manifest", "Term+Manor+Dell", 50, "mandell", 3, seq=0.96),
        Capability("snap", "SnapHost", "Ports + resonate", 14, "dell_matrix", 2, seq=0.94),
        Capability("plane", "Plane", "Geometric plane place units", 15, "plane", 2, seq=0.93),
        Capability("perspective", "Perspective", "table/page/cube/circle/flower/sphere", 9, "perspective", 2, seq=0.91),
        Capability("sandbox", "Sandbox", "Box/void isolation", 23, "sandbox", 2, seq=0.89),
        Capability("skins", "PerceptionSkin", "cube/sphere/seed/building/words", 4, "perspective", 2, seq=0.87),
        Capability("selfgrow", "SelfGrow", "Curriculum loop", 13, "duobeta", 2, seq=0.86),
        Capability("resonance", "ResonanceSeek", "Enhance when connected", 35, "resonance", 1, seq=0.80),
        Capability("vesica", "VesicaMiddle", "Flower left⊗right middle", 18, "resonance", 2, seq=0.78),
        Capability("ui_graph", "GraphUI", "Real visual surface", 9, "plane", 0, seq=0.70),
    ]


def compute_nbd() -> Tuple[Optional[Capability], List[Tuple[str, float]]]:
    G = goal_star()
    d = [c for c in G if c.lambda_def() > 0]
    ranked = sorted(((c.id, c.score(), c) for c in d), key=lambda x: x[1], reverse=True)
    table = [(i, s) for i, s, _ in ranked]
    winner = ranked[0][2] if ranked else None
    return winner, table


def main() -> None:
    w, table = compute_nbd()
    print("15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD")
    print("NBD_t = argmax φ·ρ·λ·σ\n")
    for i, s in table[:10]:
        print(f"  {s:6.3f}  {i}")
    if w:
        print(f"\nNBD → {w.dell:02d}[{w.term}] > 50[Manifest]")
        print(f"English: {w.term} — {w.manor} (L{w.level_now}→{w.level_goal})")


if __name__ == "__main__":
    main()
