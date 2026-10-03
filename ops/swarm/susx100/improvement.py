"""SUSX100 controlled self-improvement.

Specialists MAY propose contract/test/spawning/evidence improvements.
Specialists MAY NOT: edit their own authority, expand permissions, weaken
gates, authorize their own evolution, modify AUTONOMY, or merge.

Evolution cycle: EXECUTE > MEASURE > SELF_DIAGNOSE > PROPOSE >
ARGUS_ATTACK > NULL_CHALLENGE > PRISM_RECONCILE > DIRECTOR_DECISION >
UNI_IMPLEMENT > A/B_VERIFY. Director authorization is mandatory; a
proposal can never self-authorize.
"""
from __future__ import annotations

STAGES = ["PROPOSED", "ARGUS_ATTACK", "NULL_CHALLENGE", "PRISM_RECONCILE",
          "DIRECTOR_DECISION", "APPROVED", "IMPLEMENTED", "A/B_VERIFY", "REJECTED"]

# Fields a persona proposal may never touch.
HARD_AUTHORITY = frozenset({
    "autonomy", "allowed_actions", "forbidden_actions", "gates",
    "termination_invariant", "merge_authorization",
})


class ImprovementError(ValueError):
    pass


class SelfAuthorizationError(PermissionError):
    pass


def propose(persona: str, target: str, change: dict, rationale: str) -> dict:
    """Create a proposal. Rejects any change touching hard authority."""
    touched = set(change.get("touches", []))
    if touched & HARD_AUTHORITY:
        raise SelfAuthorizationError(
            f"persona {persona} may not propose changes to hard authority: "
            f"{sorted(touched & HARD_AUTHORITY)}")
    return {"persona": persona, "target": target, "change": change,
            "rationale": rationale, "stage": "PROPOSED", "history": ["PROPOSED"]}


def advance(proposal: dict, to_stage: str, by: str, director_approved: bool = False) -> dict:
    order = STAGES.index(proposal["stage"])
    if STAGES.index(to_stage) != order + 1 and not (
            proposal["stage"] == "DIRECTOR_DECISION" and to_stage in ("APPROVED", "REJECTED")):
        raise ImprovementError(
            f"illegal proposal transition {proposal['stage']} -> {to_stage}")
    if to_stage == "APPROVED":
        if by != "DIRECTOR" or not director_approved:
            raise SelfAuthorizationError(
                "only an explicit DIRECTOR decision approves a proposal; "
                "self-authorization is forbidden")
    proposal["stage"] = to_stage
    proposal["history"].append(to_stage)
    return proposal


def amend_own_contract(persona: str, contract_path: str) -> None:
    """A persona editing its own authority contract: always refused."""
    raise SelfAuthorizationError(
        f"{persona} cannot modify its own authority contract ({contract_path}); "
        "contract changes require a Director-authorized UNI implementation")
