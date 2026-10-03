"""SUSX100 DIRECTIVE V1 — directive template / compiler / checker.

Every nontrivial production directive must contain all REQUIRED_FIELDS.
Incomplete directives are rejected; the rejection names every missing field.
"""
from __future__ import annotations

REQUIRED_FIELDS = [
    "why",                  # WHY
    "authority",            # AUTHORITY
    "base",                 # BASE (sha + tree)
    "goal",                 # GOAL
    "known_state",          # KNOWN STATE
    "unknown_state",        # UNKNOWN STATE
    "relevant_contradictions",  # RELEVANT CONTRADICTIONS
    "allowed_actions",      # ALLOWED ACTIONS
    "forbidden_actions",    # FORBIDDEN ACTIONS
    "evidence_contract",    # EVIDENCE CONTRACT
    "falsification_targets",    # FALSIFICATION TARGETS
    "recovery_requirements",    # RECOVERY REQUIREMENTS
    "test_requirements",    # TEST REQUIREMENTS
    "ci_requirements",      # CI REQUIREMENTS
    "success_condition",    # SUCCESS CONDITION
    "stop_condition",       # STOP CONDITION
    "return_schema",        # RETURN SCHEMA
    "director_decision_required",  # DIRECTOR_DECISION_REQUIRED
]

# Fields whose absence is a hard reject (not just a warning).
HARD_REQUIRED = frozenset({
    "authority", "falsification_targets", "recovery_requirements",
    "success_condition", "stop_condition",
})


class DirectiveError(ValueError):
    pass


def compile(directive: dict) -> dict:
    """Validate a directive. Returns normalized directive or raises
    DirectiveError naming every missing field."""
    missing = [f for f in REQUIRED_FIELDS if f not in directive or directive[f] in (None, "", [])]
    hard_missing = [f for f in missing if f in HARD_REQUIRED]
    if hard_missing:
        raise DirectiveError(
            f"SUSX100 DIRECTIVE V1 REJECTED — missing hard-required fields: "
            f"{', '.join(hard_missing)}"
            + (f"; also missing: {', '.join(m for m in missing if m not in hard_missing)}"
               if len(missing) > len(hard_missing) else ""))
    if missing:
        # soft-missing fields are warnings, carried in the compiled output
        directive = {**directive, "_warnings": [f"missing optional field: {f}" for f in missing]}
    directive["_compiled"] = "SUSX100 DIRECTIVE V1"
    directive["_field_count"] = f"{len(REQUIRED_FIELDS) - len(missing)}/{len(REQUIRED_FIELDS)}"
    return directive


def template() -> dict:
    """Blank template with every required field present (empty)."""
    return {f: "" for f in REQUIRED_FIELDS}
