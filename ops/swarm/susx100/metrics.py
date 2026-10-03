"""SUSX100 quantitative system.

Q = (E,F,C,U,R,A,T,P) — diagnostic dimensions. NEVER collapsed into a
universal intelligence number. Metrics are advisory; they cannot grant
authority (see metric_authority_separation).
"""
from __future__ import annotations

EPSILON = 1e-9

SEVERITY_WEIGHTS = {"LOW": 1.0, "MEDIUM": 3.0, "HIGH": 9.0, "CRITICAL": 27.0}


def token_efficiency(decision_relevant_verified_findings: int, tokens_consumed: int) -> float:
    """TE = decision-relevant verified findings / max(1, tokens/1000)."""
    return decision_relevant_verified_findings / max(1.0, tokens_consumed / 1000.0)


def redundancy_ratio(duplicate_evidence_items: int, total_evidence_items: int) -> float:
    """RR = duplicates / max(1, total)."""
    return duplicate_evidence_items / max(1, total_evidence_items)


def contradiction_debt(contradictions: list[dict]) -> float:
    """CD = SUM(severity_weight_i * unresolved_i)."""
    total = 0.0
    for c in contradictions:
        if c.get("status") == "OPEN":
            total += SEVERITY_WEIGHTS.get(c.get("severity", "MEDIUM"), 3.0)
    return total


def candidate_value(impact: float, evidence: float, reachability: float,
                    recovery: float, cost: float, risk: float,
                    duplication: float) -> float:
    """V = (Impact*Evidence*Reachability*Recovery) / max(eps, Cost*Risk*Duplication).
    V is a candidate-ranking aid. V DOES NOT grant authority."""
    num = impact * evidence * reachability * recovery
    den = max(EPSILON, cost * risk * duplication)
    return num / den


def run_vector(evidence_coverage: float, falsification_coverage: float,
               contradiction_resolution: float, uncertainty_integrity: float,
               recovery_coverage: float, authority_coverage: float,
               token_efficiency_v: float, production_capability: float) -> dict:
    """Q = (E,F,C,U,R,A,T,P). Each in [0,1] except T (TE) which is unbounded.
    Returned as a dict; never reduced to a scalar."""
    return {
        "E_evidence_coverage": evidence_coverage,
        "F_falsification_coverage": falsification_coverage,
        "C_contradiction_resolution": contradiction_resolution,
        "U_uncertainty_integrity": uncertainty_integrity,
        "R_recovery_coverage": recovery_coverage,
        "A_authority_coverage": authority_coverage,
        "T_token_efficiency": token_efficiency_v,
        "P_production_capability": production_capability,
    }


def metric_authority_separation() -> dict:
    """The law, as data: no metric value appears in any authorization path.
    authorize_action() in state_machine.py takes only (run, action) and the
    recorded director_decision — metrics are not consulted."""
    return {
        "law": "metrics_cannot_grant_authority",
        "authorization_inputs": ["run.allowed_actions", "run.forbidden_actions",
                                 "director_decision.decision", "director_decision.candidate_head"],
        "metrics_consulted": [],
    }
