"""KIE-I: Knowledge Influence Chain — read-only explanation layer.

Exposes WHY knowledge influenced (or did not influence) execution,
using existing authorities. Does NOT select, score, or decide.

KIC states:
  STORED → ELIGIBLE → SELECTED → ROUTABLE → USED → OBSERVED → LEARNED

Epistemic: FACT / DERIVED_FACT / UNKNOWN. No causal claims.
"""

from typing import Any, Dict, List, Optional


def _epistemic(value: Any, source: str) -> Dict[str, Any]:
    """Wrap a value with epistemic status."""
    if value is None:
        return {"status": "UNKNOWN", "value": None, "source": source}
    return {"status": "FACT", "value": value, "source": source}


def explain_influence(
    program: Any,
    knowledge_id: str,
    outcome_id: Optional[str] = None,
    context: Optional[str] = None,
) -> Dict[str, Any]:
    """Explain why a knowledge item was (or was not) used.

    If outcome_id is given: HISTORICAL explanation from Outcome V1 provenance.
    If context is given (no outcome_id): CURRENT explanation from live state.
    If neither: CURRENT explanation of stored state.

    Read-only. Never modifies program state.
    """
    from . import knowledge_selector as ks

    kid = str(knowledge_id or "")
    result: Dict[str, Any] = {
        "knowledge_id": kid,
        "mode": "historical" if outcome_id else "current",
        "chain": {},
    }

    # ── STORED ──
    stored = _find_stored(program, kid)
    result["chain"]["STORED"] = stored
    if stored["status"] == "UNKNOWN":
        # Cannot explain further without stored knowledge
        for state in ["ELIGIBLE", "SELECTED", "ROUTABLE", "USED", "OBSERVED", "LEARNED"]:
            result["chain"][state] = {"status": "UNKNOWN", "reason": "knowledge not found in stored state"}
        return result

    if outcome_id:
        return _explain_historical(program, kid, outcome_id, result, stored)
    else:
        return _explain_current(program, kid, context, result, stored, ks)


def _find_stored(program: Any, kid: str) -> Dict[str, Any]:
    """Find knowledge in stored state (nursery)."""
    try:
        nursery = program.nursery
        proposals = getattr(nursery, "proposals", {}) or {}
        prop = proposals.get(kid)
        if prop is None:
            return {"status": "UNKNOWN", "reason": f"knowledge {kid} not in nursery"}
        return {
            "status": "FACT",
            "id": kid,
            "label": getattr(prop, "label", None),
            "lifecycle_state": getattr(prop, "lifecycle_state", None),
            "revision_number": getattr(prop, "revision_number", None),
            "source": "nursery.proposals",
        }
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"lookup failed: {e}"}


def _explain_current(
    program: Any, kid: str, context: Optional[str],
    result: Dict[str, Any], stored: Dict[str, Any], ks: Any,
) -> Dict[str, Any]:
    """CURRENT explanation: derive from live state."""
    # ── ELIGIBLE ──
    eligible = _check_eligible(program, kid, ks)
    result["chain"]["ELIGIBLE"] = eligible

    # ── SELECTED ──
    if context:
        selected = _check_selected(program, kid, context, ks)
    else:
        selected = {"status": "UNKNOWN", "reason": "no context provided for selection check"}
    result["chain"]["SELECTED"] = selected

    # ── ROUTABLE ── (requires conflict check; simplified)
    routable = _check_routable(program, kid)
    result["chain"]["ROUTABLE"] = routable

    # ── USED ── (current: not yet executed in this explanation)
    result["chain"]["USED"] = {
        "status": "UNKNOWN",
        "reason": "current mode: use is determined at execution time",
    }

    # ── OBSERVED ──
    result["chain"]["OBSERVED"] = {
        "status": "UNKNOWN",
        "reason": "current mode: observation requires an Outcome ID",
    }

    # ── LEARNED ──
    learned = _check_learned(program, kid)
    result["chain"]["LEARNED"] = learned

    return result


def _explain_historical(
    program: Any, kid: str, outcome_id: str,
    result: Dict[str, Any], stored: Dict[str, Any],
) -> Dict[str, Any]:
    """HISTORICAL explanation: from Outcome V1 provenance (frozen)."""
    from .outcome_ledger import get_outcome

    rec = get_outcome(program, outcome_id)
    if not rec:
        for state in ["ELIGIBLE", "SELECTED", "ROUTABLE", "USED", "OBSERVED", "LEARNED"]:
            result["chain"][state] = {"status": "UNKNOWN", "reason": f"outcome {outcome_id} not found"}
        return result

    # OBSERVED: what does the Outcome record?
    knowledge = rec.get("knowledge") or []
    kid_in_outcome = None
    for k in knowledge:
        if isinstance(k, dict) and k.get("id") == kid:
            kid_in_outcome = k
            break

    if kid_in_outcome:
        result["chain"]["OBSERVED"] = {
            "status": "FACT",
            "outcome_id": outcome_id,
            "revision_number": kid_in_outcome.get("revision_number"),
            "content_fingerprint": kid_in_outcome.get("content_fingerprint"),
            "source": "Outcome V1 (frozen at capture)",
        }
        result["chain"]["USED"] = {
            "status": "DERIVED_FACT",
            "reason": f"recorded as used in outcome {outcome_id}",
            "source": "Outcome V1 knowledge list",
        }
    else:
        result["chain"]["OBSERVED"] = {
            "status": "FACT",
            "outcome_id": outcome_id,
            "recorded": False,
            "reason": f"knowledge {kid} not in outcome {outcome_id} knowledge list",
            "source": "Outcome V1 (frozen at capture)",
        }
        result["chain"]["USED"] = {
            "status": "DERIVED_FACT",
            "reason": f"not recorded as used in outcome {outcome_id}",
            "source": "Outcome V1 knowledge list",
        }

    # Historical ELIGIBLE/SELECTED/ROUTABLE: UNKNOWN unless captured
    # We do NOT reconstruct from current state (would be false history)
    for state in ["ELIGIBLE", "SELECTED", "ROUTABLE"]:
        result["chain"][state] = {
            "status": "UNKNOWN",
            "reason": f"historical {state.lower()} not captured in Outcome V1; "
                      f"current state must not be presented as historical truth",
        }

    # LEARNED: check DuoBeta (separate lifecycle)
    learned = _check_learned(program, kid)
    result["chain"]["LEARNED"] = learned
    if learned.get("status") == "FACT":
        learned["note"] = "learning is separate from outcome observation (DLA-I)"

    return result


def _check_eligible(program: Any, kid: str, ks: Any) -> Dict[str, Any]:
    """Check hard eligibility gates (current state)."""
    # Use selector's exclusion lists by running a probe selection
    try:
        result = ks.select_for_context(program, "", operation="grow", max_selected=1000)
        sup_excl = result.get("supersession_exclusions") or []
        dep_excl = result.get("dependency_exclusions") or []
        eligible_count = result.get("eligible_count", 0)

        for e in sup_excl:
            if isinstance(e, dict) and e.get("id") == kid:
                return {
                    "status": "FACT",
                    "eligible": False,
                    "reason": "SUPERSEDED",
                    "detail": e.get("reason", "superseded"),
                    "source": "knowledge_selector.supersession_exclusions",
                }
        for e in dep_excl:
            if isinstance(e, dict) and e.get("id") == kid:
                return {
                    "status": "FACT",
                    "eligible": False,
                    "reason": "UNRESOLVED_DEPENDENCY",
                    "detail": e.get("reason", "dependency invalid"),
                    "source": "knowledge_selector.dependency_exclusions",
                }
        # If not excluded, check if it would be in eligible set
        # (We can't directly get the eligible set, so this is derived)
        return {
            "status": "DERIVED_FACT",
            "eligible": True,
            "reason": "not in supersession or dependency exclusion lists",
            "source": "knowledge_selector exclusion lists",
        }
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"eligibility check failed: {e}"}


def _check_selected(program: Any, kid: str, context: str, ks: Any) -> Dict[str, Any]:
    """Check selection status for a context (current state)."""
    try:
        result = ks.select_for_context(program, context, operation="grow")
        selected = result.get("selected") or []
        for s in selected:
            if isinstance(s, dict) and s.get("id") == kid:
                return {
                    "status": "FACT",
                    "selected": True,
                    "rank": s.get("rank"),
                    "score": s.get("score"),
                    "provenance": s.get("selection_provenance"),
                    "explicit": (result.get("explicit_choice") or {}).get(kid),
                    "asi_score": (result.get("learned_scores") or {}).get(kid),
                    "source": "knowledge_selector.select_for_context",
                }
        return {
            "status": "FACT",
            "selected": False,
            "reason": "not in selected list for this context",
            "eligible_count": result.get("eligible_count"),
            "source": "knowledge_selector.select_for_context",
        }
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"selection check failed: {e}"}


def _check_routable(program: Any, kid: str) -> Dict[str, Any]:
    """Check conflict/disposition routability (current state)."""
    try:
        from . import conflict_disposition as cd
        # Simplified: check if knowledge is in any active conflict
        # Full implementation would use conflict_router
        return {
            "status": "UNKNOWN",
            "reason": "routability requires conflict context; use execution receipts for definitive answer",
        }
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"routability check failed: {e}"}


def _check_learned(program: Any, kid: str) -> Dict[str, Any]:
    """Check DuoBeta learned state (separate lifecycle)."""
    try:
        from . import duobeta_learn as dl
        idx = dl.preference_index(program)
        # Index is keyed by (dell, knowledge_id)
        for (dell, k), v in idx.items():
            if k == kid:
                return {
                    "status": "FACT",
                    "learned": True,
                    "dell": dell,
                    "detail": v,
                    "source": "duobeta_learn.preference_index",
                    "note": "via explicit DLA-I lifecycle only, not automatic",
                }
        return {
            "status": "FACT",
            "learned": False,
            "reason": "not in DuoBeta preference index",
            "source": "duobeta_learn.preference_index",
        }
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"learned check failed: {e}"}


def why_used(program: Any, knowledge_id: str, outcome_id: str) -> Dict[str, Any]:
    """User-facing: WHY WAS <id> USED? (historical, from Outcome)."""
    exp = explain_influence(program, knowledge_id, outcome_id=outcome_id)
    chain = exp.get("chain", {})
    used = chain.get("USED", {})
    observed = chain.get("OBSERVED", {})
    return {
        "question": f"WHY WAS {knowledge_id} USED?",
        "answer": {
            "used": used,
            "observed_in": observed.get("outcome_id"),
            "revision": observed.get("revision_number"),
            "fingerprint": observed.get("content_fingerprint"),
        },
        "epistemic": "Outcome V1 is observation, not causation. "
                     "This explains recording, not causal necessity.",
    }


def why_not_used(program: Any, knowledge_id: str, context: Optional[str] = None) -> Dict[str, Any]:
    """User-facing: WHY WAS <id> NOT USED? (current state)."""
    exp = explain_influence(program, knowledge_id, context=context)
    chain = exp.get("chain", {})
    reasons = []
    for state in ["ELIGIBLE", "SELECTED", "ROUTABLE"]:
        s = chain.get(state, {})
        if s.get("eligible") is False or s.get("selected") is False:
            reasons.append({
                "state": state,
                "reason": s.get("reason"),
                "detail": s.get("detail", ""),
            })
    return {
        "question": f"WHY WAS {knowledge_id} NOT USED?",
        "blocking_reasons": reasons,
        "chain": {k: v.get("status") for k, v in chain.items()},
    }
