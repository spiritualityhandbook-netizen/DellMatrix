#!/usr/bin/env python3
"""
NBD Equation — dynamic Next Best Directive under Mandell.

Inside (Mandell):
  15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest]

Outside (English):
  Map goal vs state, mirror the gap, rank candidates, manifest the winner.

Profound form (compact):

    NBD_t = argmax_{c ∈ Δ_t}  φ(c) · ρ(c) · λ(c) · σ(c)

  G*   = goal configuration (FOUNDATION end-state)
  G_t  = current configuration at generation t
  Δ_t  = G* ∖ G_t   (capabilities still missing or below target level)
  φ(c) = Floor-safe ∧ Manifest-complete ∈ {0, 1}
  ρ(c) = resonance with spine (Mandell → Dell Matrix → DuoBeta) ∈ [0, 1]
  λ(c) = level deficit = max(0, L* − L_t(c))   L*=3 working, L=1 label, L=2 stub
  σ(c) = sequence priority (language-first order) ∈ [0, 1]

Dual-output seed of the formula itself:
  15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD

Run:
  python -m form.mandell.nbd_equation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import json

FLOOR = ("Alpha", "Delta", "Omega", "Omni")

# Target working level: 1=label/snap, 2=callable stub, 3=real behavior
L_STAR = 3

# Spine resonance weights (Mandell most foundational)
SPINE = ("mandell", "dell_matrix", "duobeta", "cube", "main", "enhance", "resonance")


@dataclass
class Capability:
    id: str
    term: str
    manor: str
    dell: int
    spine: str  # which spine band
    level_now: int  # 0 absent, 1 snapped label, 2 stub, 3 working
    level_goal: int = L_STAR
    floor_safe: bool = True
    manifest_complete: bool = True
    seq: float = 0.5  # sequence priority 0..1 (higher = earlier in true order)

    def phi(self) -> float:
        return 1.0 if (self.floor_safe and self.manifest_complete) else 0.0

    def rho(self) -> float:
        """Resonance with foundation spine — earlier spine bands score higher base."""
        try:
            i = SPINE.index(self.spine)
        except ValueError:
            i = len(SPINE)
        # mandell=1.0 ... later bands slightly lower but still needed
        return max(0.35, 1.0 - 0.08 * i)

    def lambda_def(self) -> float:
        return float(max(0, self.level_goal - self.level_now))

    def sigma(self) -> float:
        return float(self.seq)

    def score(self) -> float:
        """φ · ρ · λ · σ"""
        return self.phi() * self.rho() * self.lambda_def() * self.sigma()


def goal_star() -> List[Capability]:
    """G* — end goal capabilities (FOUNDATION). level_now filled by assess()."""
    # seq: language first → matrix → growth → cube/table/main → enhance/resonance
    return [
        Capability("floor", "Floor", "Immutable base", 23, "mandell", 3, seq=1.00),
        Capability("registry", "Registry", "Dell 00–50 True", 11, "mandell", 3, seq=0.98),
        Capability("manifest", "Manifest", "Term+Manor+Dell", 50, "mandell", 3, seq=0.96),
        Capability("snap", "SnapHost", "Dell Matrix ports + resonate", 14, "dell_matrix", 2, seq=0.94),
        Capability("selfgrow", "SelfGrow", "Curriculum snap loop", 13, "duobeta", 2, seq=0.90),
        Capability("understand", "SelfMap", "Program understands itself structurally", 35, "duobeta", 2, seq=0.88),
        Capability("cube_hold", "HarmonicCubeHold", "Holdable harmonic cube", 8, "cube", 1, seq=0.85),
        Capability("table", "TableSurface", "Table for cubes", 9, "cube", 1, seq=0.83),
        Capability("cube_sync", "CubeSyncCheck", "Sync without rewrite", 18, "cube", 1, seq=0.81),
        Capability("main_third", "MainThirdField", "Third space = Main", 21, "main", 1, seq=0.80),
        Capability("pull", "VoluntaryPull", "Pull from Main by choice", 24, "main", 1, seq=0.78),
        Capability("blank", "BlankCubeGive", "Givable blank cube", 8, "cube", 1, seq=0.76),
        Capability("enhance", "EnhanceGate", "Opt-in enhance on/off", 32, "enhance", 1, seq=0.74),
        Capability("resonance", "ResonanceSeek", "Seek synchronicity", 35, "resonance", 1, seq=0.72),
        Capability("harmoni_rank", "HarmoniRank", "Score harmonic fit", 5, "resonance", 1, seq=0.70),
    ]


def assess(G: List[Capability]) -> List[Capability]:
    """
    G_t assessment for current Form reality (honest levels).
    Update here as real stubs/behaviors land.
    """
    # Honest snapshot after foundation + label growth:
    known = {
        "floor": 3,
        "registry": 3,
        "manifest": 3,
        "snap": 2,        # works as code, not full product UI
        "selfgrow": 2,    # loop works; grows labels
        "understand": 2,
        "cube_hold": 1,
        "table": 1,
        "cube_sync": 1,
        "main_third": 1,
        "pull": 1,
        "blank": 1,
        "enhance": 1,
        "resonance": 1,
        "harmoni_rank": 1,
    }
    out = []
    for c in G:
        c.level_now = known.get(c.id, c.level_now)
        out.append(c)
    return out


def delta(G: List[Capability]) -> List[Capability]:
    """Δ_t = capabilities with level deficit."""
    return [c for c in G if c.lambda_def() > 0]


def compute_nbd(G: Optional[List[Capability]] = None) -> Tuple[Optional[Capability], List[Tuple[str, float]]]:
    """
    NBD_t = argmax_{c ∈ Δ_t} φ(c)·ρ(c)·λ(c)·σ(c)
    """
    G = assess(G or goal_star())
    d = delta(G)
    ranked = sorted(((c.id, c.score(), c) for c in d), key=lambda x: x[1], reverse=True)
    table = [(i, s) for i, s, _ in ranked]
    winner = ranked[0][2] if ranked else None
    return winner, table


def nbd_seed(c: Capability) -> str:
    return f"{c.dell:02d}[{c.term}] > 50[Manifest] :: NBD"


def render() -> str:
    winner, table = compute_nbd()
    lines = [
        "15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD",
        "English: Map goal, mirror gap, rank, manifest next best.",
        "",
        "Equation:",
        "  NBD_t = argmax_{c ∈ Δ_t}  φ(c) · ρ(c) · λ(c) · σ(c)",
        "  φ = Floor-safe ∧ Manifest-complete",
        "  ρ = spine resonance (Mandell→…)",
        "  λ = L* − L_t   (L*=3 working)",
        "  σ = sequence priority (language-first)",
        "",
        f"Floor: {' · '.join(FLOOR)} (LOCKED)",
        "",
        "Ranked Δ (id : score):",
    ]
    for i, s in table[:12]:
        lines.append(f"  {s:6.3f}  {i}")
    if winner:
        lines += [
            "",
            f"NBD → {nbd_seed(winner)}",
            f"English: {winner.term} — {winner.manor}",
            f"  level_now={winner.level_now} → goal={winner.level_goal}  λ={winner.lambda_def()}",
            f"  φ={winner.phi()} ρ={winner.rho():.2f} σ={winner.sigma():.2f}  score={winner.score():.3f}",
        ]
    else:
        lines.append("\nNBD → ∅  (Δ empty — at goal under current assess)")
    return "\n".join(lines)


def main() -> None:
    print(render())
    w, table = compute_nbd()
    print("\n09[Show] :: json")
    print(
        json.dumps(
            {
                "equation": "NBD=argmax φ·ρ·λ·σ",
                "nbd": None
                if not w
                else {
                    "id": w.id,
                    "term": w.term,
                    "manor": w.manor,
                    "dell": w.dell,
                    "seed": nbd_seed(w),
                    "score": w.score(),
                    "level_now": w.level_now,
                    "level_goal": w.level_goal,
                },
                "ranked": table,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
