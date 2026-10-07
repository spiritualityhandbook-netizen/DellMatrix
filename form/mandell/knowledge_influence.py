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
    explicit_ids: Optional[list] = None,
) -> Dict[str, Any]:
    """Explain why a knowledge item was (or was not) used.

    If outcome_id is given: HISTORICAL explanation from Outcome V1 provenance.
    If context is given (no outcome_id): CURRENT explanation from live state.
    If neither: CURRENT explanation of stored state.
    explicit_ids: EKC explicit user choices to include in the selection check.

    Read-only. Never modifies program state.
    """
    kid = str(knowledge_id or "")
    result: Dict[str, Any] = {
        "knowledge_id": kid,
        "mode": "historical" if outcome_id else "current",
        "chain": {},
    }

    if outcome_id:
        # C1-2: historical mode consults Outcome V1 FIRST.
        # Current nursery absence must not erase historical evidence.
        return _explain_historical(program, kid, outcome_id, result)

    # ── CURRENT mode: STORED first ──
    stored = _find_stored(program, kid)
    result["chain"]["STORED"] = stored
    if stored["status"] == "UNKNOWN":
        # Cannot explain further without stored knowledge
        for state in ["ELIGIBLE", "SELECTED", "ROUTABLE", "USED", "OBSERVED", "LEARNED"]:
            result["chain"][state] = {"status": "UNKNOWN", "reason": "knowledge not found in stored state"}
        return result

    return _explain_current(program, kid, context, result, stored, explicit_ids)


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
    result: Dict[str, Any], stored: Dict[str, Any],
    explicit_ids: Optional[list] = None,
) -> Dict[str, Any]:
    """CURRENT explanation: derive from live state."""
    # ── ELIGIBLE ── (C1-1: positive four-gate evidence)
    eligible = _check_eligible(program, kid)
    result["chain"]["ELIGIBLE"] = eligible

    # ── SELECTED ──
    if context:
        selected = _check_selected(program, kid, context, explicit_ids)
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
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """HISTORICAL explanation: from Outcome V1 provenance (frozen).

    C1-2: Outcome V1 is the historical authority. Current nursery presence
    is NOT required and is reported separately; current absence must not
    erase historical evidence.
    C1-3: LEARNED in the historical chain is UNKNOWN unless historically
    captured. Current DuoBeta state is reported OUTSIDE the chain, clearly
    labeled as current.
    """
    from .outcome_ledger import get_outcome

    rec = get_outcome(program, outcome_id)
    if not rec:
        for state in ["STORED", "ELIGIBLE", "SELECTED", "ROUTABLE", "USED", "OBSERVED", "LEARNED"]:
            result["chain"][state] = {"status": "UNKNOWN", "reason": f"outcome {outcome_id} not found"}
        return result

    # STORED (historical): Outcome V1 knowledge list proves the knowledge
    # existed (was stored) at capture time. Independent of current nursery.
    knowledge = rec.get("knowledge") or []
    kid_in_outcome = None
    for k in knowledge:
        if isinstance(k, dict) and k.get("id") == kid:
            kid_in_outcome = k
            break

    if kid_in_outcome:
        result["chain"]["STORED"] = {
            "status": "FACT",
            "reason": f"present in frozen Outcome V1 knowledge list (stored at capture time)",
            "source": "Outcome V1 (frozen at capture)",
        }
    else:
        result["chain"]["STORED"] = {
            "status": "UNKNOWN",
            "reason": f"knowledge {kid} not in outcome {outcome_id} knowledge list; "
                      f"historical stored-state not otherwise captured",
            "source": "Outcome V1 (frozen at capture)",
        }

    # Current nursery presence: informational only, outside the chain.
    # C1-2: must not gate or erase historical evidence.
    current_prop = _get_proposal(program, kid)
    result["current_stored"] = {
        "present": current_prop is not None,
        "temporal_scope": "CURRENT — informational only; does not affect historical chain",
    }

    # OBSERVED / USED: from frozen Outcome (unchanged, positive evidence).
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
            "used": True,
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
            "used": False,
            "reason": f"not recorded as used in outcome {outcome_id}",
            "source": "Outcome V1 knowledge list",
        }

    # Historical ELIGIBLE/SELECTED/ROUTABLE: UNKNOWN unless captured.
    # We do NOT reconstruct from current state (would be false history).
    # We do NOT fabricate them.
    for state in ["ELIGIBLE", "SELECTED", "ROUTABLE"]:
        result["chain"][state] = {
            "status": "UNKNOWN",
            "reason": f"historical {state.lower()} not captured in Outcome V1; "
                      f"current state must not be presented as historical truth",
        }

    # C1-3: LEARNED temporal semantics.
    # Historical LEARNED is UNKNOWN: Outcome V1 does not capture DuoBeta
    # learning, and learning is a separate explicit lifecycle (DLA-I).
    result["chain"]["LEARNED"] = {
        "status": "UNKNOWN",
        "reason": "historical learned state not captured in Outcome V1; "
                  "DuoBeta learning is a separate explicit lifecycle (DLA-I)",
    }
    # Current learned state: reported OUTSIDE the historical chain,
    # clearly labeled as current.
    current_learned = _check_learned(program, kid)
    current_learned["temporal_scope"] = "CURRENT — not the state at outcome time"
    result["current_learned_state"] = current_learned

    return result


def _get_proposal(program: Any, kid: str) -> Optional[Any]:
    """Fetch the stored proposal, or None."""
    try:
        proposals = getattr(program.nursery, "proposals", {}) or {}
        return proposals.get(kid)
    except Exception:
        return None


def _check_eligible(program: Any, kid: str) -> Dict[str, Any]:
    """Check hard eligibility gates with POSITIVE evidence (C1-1).

    Canonical contract (knowledge_selector.select_for_context, gates in order):
      1. CONFIRMED: prop.status == "confirmed"
      2. ON-PLANE: kid in program.cube.session.plane.units
      3. REVISION-ACTIVE: is_revision_active(program, kid)  [canonical authority]
      4. DEPENDENCY-VALID: is_dependency_valid(program, kid) [canonical authority]

    ELIGIBLE=true only when ALL FOUR are positively established.
    Absence from exclusion lists is NOT sufficient evidence (C1-1 root cause).
    """
    prop = _get_proposal(program, kid)
    if prop is None:
        return {"status": "UNKNOWN", "reason": f"knowledge {kid} not in stored state"}

    # Gate 1: CONFIRMED (positive)
    status = getattr(prop, "status", None)
    if status != "confirmed":
        return {
            "status": "FACT",
            "eligible": False,
            "reason": "NOT_CONFIRMED",
            "detail": f"lifecycle status is '{status}', not 'confirmed'",
            "source": "nursery.proposals[].status",
        }

    # Gate 2: ON-PLANE (positive)
    try:
        units = program.cube.session.plane.units
        on_plane = kid in units
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"plane lookup failed: {e}"}
    if not on_plane:
        return {
            "status": "FACT",
            "eligible": False,
            "reason": "NOT_ON_PLANE",
            "detail": "confirmed but not present in cube plane units",
            "source": "cube.session.plane.units",
        }

    # Gate 3: REVISION-ACTIVE (canonical authority, positive)
    try:
        from .supersession import is_revision_active
        rev_active = is_revision_active(program, kid)
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"revision check failed: {e}"}
    if not rev_active:
        return {
            "status": "FACT",
            "eligible": False,
            "reason": "SUPERSEDED",
            "detail": "not the active revision (superseded or malformed revision)",
            "source": "supersession.is_revision_active",
        }

    # Gate 3b: PARTICIPATION (canonical facade, positive). Ordinary
    # eligibility excludes faded presence. WO-5.2 whole-circuit.
    try:
        from form.dell_matrix import canonical_lifecycle as _cl
        part_active = _cl.is_active(program, kid)
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"participation check failed: {e}"}
    if not part_active:
        return {
            "status": "FACT",
            "eligible": False,
            "reason": "NOT_PARTICIPATING",
            "detail": "excluded by authoritative participation interpretation "
                      "(faded, pending, or otherwise non-participating)",
            "source": "canonical_lifecycle.is_active",
        }

    # Gate 4: DEPENDENCY-VALID (canonical authority, positive)
    try:
        from .dependency_validity import is_dependency_valid
        dep_valid = is_dependency_valid(program, kid)
    except Exception as e:
        return {"status": "UNKNOWN", "reason": f"dependency check failed: {e}"}
    if not dep_valid:
        return {
            "status": "FACT",
            "eligible": False,
            "reason": "UNRESOLVED_DEPENDENCY",
            "detail": "dependency validity gate failed",
            "source": "dependency_validity.is_dependency_valid",
        }

    return {
        "status": "FACT",
        "eligible": True,
        "reason": "confirmed + on-plane + revision-active + dependency-valid "
                  "(all four canonical gates positively established)",
        "source": "nursery + cube plane + supersession + dependency_validity",
    }


def _check_selected(program: Any, kid: str, context: str,
                  explicit_ids: Optional[list] = None) -> Dict[str, Any]:
    """Check selection status for a context (current state).

    POSITIVE evidence: membership in the selector's returned `selected` list.
    explicit_ids: EKC explicit user choices passed to the canonical selector.
    """
    from . import knowledge_selector as ks
    try:
        result = ks.select_for_context(program, context, operation="grow",
                                       explicit_ids=explicit_ids)
        selected = result.get("selected") or []
        for s in selected:
            if isinstance(s, dict) and s.get("id") == kid:
                ech = result.get("explicit_choice") or {}
                explicit = (kid in (ech.get("selected_explicit") or [])
                            or (ech.get("resolutions") or {}).get(kid) == "SELECTED")
                return {
                    "status": "FACT",
                    "selected": True,
                    "reason": ("explicitly chosen by user (EKC)"
                               if explicit else
                               "in canonical selection for this context"),
                    "rank": s.get("rank"),
                    "score": s.get("score"),
                    "provenance": s.get("selection_provenance"),
                    "explicit": explicit,
                    "asi_score": (result.get("learned_scores") or {}).get(kid),
                    "source": "knowledge_selector.select_for_context",
                }
        return {
            "status": "FACT",
            "selected": False,
            "reason": ("not in canonical selection for this context "
                       "(complete returned selection list)"),
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
