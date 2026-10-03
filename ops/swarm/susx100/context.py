"""SUSX100 context economy.

Minimum sufficient specialist context. References to shared evidence are
preferred over copies. These invariants are NEVER compressed away:
UNKNOWN, authority, contradictions, candidate identity, security findings,
recovery state.
"""
from __future__ import annotations

NEVER_DROP = frozenset({
    "authority", "unknowns", "contradictions", "candidate_head",
    "security_findings", "recovery_state",
})


def minimum_context(authority: dict, goal: str, relevant_state: dict,
                    evidence_refs: list[str], relevant_contradictions: list[dict],
                    exact_task: str, forbidden_actions: list[str],
                    output_contract: str, unknowns: list[str] | None = None,
                    candidate_head: str | None = None,
                    security_findings: list | None = None,
                    recovery_state: dict | None = None) -> dict:
    """Build the smallest context that preserves every invariant in NEVER_DROP."""
    ctx = {
        "authority": authority,
        "goal": goal,
        "relevant_current_state": relevant_state,
        "relevant_evidence": evidence_refs,  # references, not copies
        "contradictions": relevant_contradictions,
        "exact_task": exact_task,
        "forbidden_actions": forbidden_actions,
        "output_contract": output_contract,
        "unknowns": unknowns or [],
        "candidate_head": candidate_head,
        "security_findings": security_findings or [],
        "recovery_state": recovery_state or {},
    }
    missing = [k for k in NEVER_DROP if k not in ctx]
    # Invariants must be PRESENT (empty allowed); presence is the guarantee.
    assert not missing, f"context dropped invariants: {missing}"
    return ctx


def check_invariants(ctx: dict) -> list[str]:
    """Return list of violated invariants (empty = all preserved)."""
    return sorted(k for k in NEVER_DROP if k not in ctx)
