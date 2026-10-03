"""SUSX100 dynamic spawning.

Permanent personas != permanent worker count. Workers are spawned where
expected marginal information gain justifies cost. High-risk claims may
require independent duplicate verification; routine facts get none.
"""
from __future__ import annotations

from .metrics import EPSILON

# Priority threshold: spawn only when expected marginal gain justifies cost.
SPAWN_THRESHOLD = 1.0
# Risk at or above this requires independent duplicate verification.
HIGH_RISK_THRESHOLD = 0.7


def priority(impact: float, uncertainty: float, dependency: float,
             risk: float, estimated_cost: float) -> float:
    """Priority_j = (Impact*Uncertainty*Dependency*Risk) / max(eps, Cost)."""
    return (impact * uncertainty * dependency * risk) / max(EPSILON, estimated_cost)


def select_workers(candidates: list[dict]) -> list[dict]:
    """Return spawn records for candidates whose priority clears the
    threshold. May legitimately return [] (zero unnecessary workers)."""
    selected = []
    for c in candidates:
        p = priority(c["impact"], c["uncertainty"], c.get("dependency", 1.0),
                     c.get("risk", 0.5), c["estimated_cost"])
        if p >= SPAWN_THRESHOLD:
            selected.append({**c, "priority": p,
                             "reason_spawned": c.get("reason_spawned", "priority>=threshold")})
    return selected


def independent_verification_required(risk: float) -> bool:
    """High-risk claims require a second, independent instance."""
    return risk >= HIGH_RISK_THRESHOLD


def spawn_record(persona: str, instance_id: str, mission: str, dependency: str,
                 reason_spawned: str, estimated_cost: float) -> dict:
    return {
        "persona": persona,
        "instance_id": instance_id,
        "mission": mission,
        "dependency": dependency,
        "reason_spawned": reason_spawned,
        "estimated_cost": estimated_cost,
        "actual_cost": None,
        "information_delta": None,
        "useful_output": None,
    }
