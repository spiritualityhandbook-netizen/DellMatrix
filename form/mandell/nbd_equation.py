#!/usr/bin/env python3
"""NBD equation — levels reflect post L3 Form stack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
import sys

L_STAR = 3
SPINE = (
    "mandell",
    "dell_matrix",
    "duobeta",
    "plane",
    "main",
    "integrate",
    "resonance",
    "enhance",
    "persist",
    "ui",
)


@dataclass
class Cap:
    id: str
    term: str
    spine: str
    L: int
    seq: float

    def rho(self) -> float:
        i = SPINE.index(self.spine) if self.spine in SPINE else len(SPINE)
        return max(0.35, 1.0 - 0.07 * i)

    def lam(self) -> int:
        return max(0, L_STAR - self.L)

    def score(self) -> float:
        return self.rho() * self.lam() * self.seq


# Living levels after NBD chain through interactive HTML + shared main
CAPS: List[Cap] = [
    Cap("floor", "Floor", "mandell", 3, 1.0),
    Cap("registry", "Registry", "mandell", 3, 0.98),
    Cap("snap", "SnapHost", "dell_matrix", 3, 0.94),
    Cap("plane", "Plane", "plane", 3, 0.93),
    Cap("main", "MainThird", "main", 3, 0.92),
    Cap("shared_main", "SharedMain", "main", 2, 0.88),
    Cap("blank", "BlankCube", "plane", 3, 0.88),
    Cap("integrate", "OneProgram", "integrate", 3, 0.97),
    Cap("repl", "REPL", "integrate", 3, 0.96),
    Cap("resonance", "Resonance", "resonance", 3, 0.90),
    Cap("enhance", "EnhanceGate", "enhance", 3, 0.90),
    Cap("persist", "Persist", "persist", 3, 0.91),
    Cap("ui", "Visual", "ui", 3, 0.88),
    Cap("selfgrow", "SelfGrow", "duobeta", 3, 0.85),
    Cap("ambient", "Ambient", "enhance", 0, 0.35),
    Cap("net_main", "NetworkMain", "main", 0, 0.40),
]


def rank() -> List[Cap]:
    return sorted([c for c in CAPS if c.lam() > 0], key=lambda c: -c.score())


def main() -> None:
    print("15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD")
    print("NBD_t = argmax φ·ρ·λ·σ\n")
    ranked = rank()
    if not ranked:
        print("Δ empty at L* for tracked caps — only ambient/network remain (Pre-form).")
        return
    for c in ranked:
        print(f"  {c.score():.3f}  {c.id:16} L{c.L}→{L_STAR}")
    print("\nNBD →", ranked[0].id, ranked[0].term)


if __name__ == "__main__":
    main()
