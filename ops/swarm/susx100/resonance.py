"""SUSX100 resonance law.

Resonance = independently obtained evidence converging through DISTINCT
legitimate methods. Five agents inheriting one assumption do not count as
five independent proofs. Correlated evidence receives reduced weight.
Contradictory high-quality evidence cannot be erased by numerical majority.
"""
from __future__ import annotations


def method_signature(evidence: dict) -> tuple:
    """Identity of the method lineage: (method, root_assumption)."""
    return (evidence.get("method", "unknown"), evidence.get("root_assumption", ""))


def independent_support(claim_id: str, evidence_items: list[dict]) -> dict:
    """Count DISTINCT method lineages supporting a claim. Correlated
    agreement (same method+assumption) counts once."""
    supporting = [e for e in evidence_items
                  if e.get("claim_id") == claim_id and e.get("supports")]
    lineages: dict[tuple, list] = {}
    for e in supporting:
        lineages.setdefault(method_signature(e), []).append(e["agent"])
    return {
        "claim_id": claim_id,
        "independent_methods": len(lineages),
        "total_items": len(supporting),
        "lineages": {f"{m}|{a or 'no-assumption'}": agents
                     for (m, a), agents in lineages.items()},
        # resonance requires >=2 DISTINCT methods, not >=2 agents
        "resonant": len(lineages) >= 2,
    }


def minority_survives(reconciliation: dict) -> bool:
    """A valid reconciliation must retain minority contradictory evidence."""
    contra = reconciliation.get("contradictory_evidence", [])
    return len(contra) > 0 and all(
        e.get("preserved") for e in contra
    )


def merge_blocked_by_contradictions(contradictions: list[dict]) -> dict:
    """D20: critical OPEN contradictions block any merge recommendation.
    Returns the block verdict; never authorizes."""
    critical_open = [c for c in contradictions
                     if c.get("status") == "OPEN" and c.get("severity") == "CRITICAL"]
    return {
        "blocked": len(critical_open) > 0,
        "blocking": [c.get("id") for c in critical_open],
        "note": "advisory only; merge authorization still requires DIRECTOR decision",
    }
