#!/usr/bin/env python3
"""ODCG-I: Outcome-Derived Correction Graph I (NBD-Ω-020).

Read-only projection of correction candidates from Outcome V1 ledger.

PRIMARY LAW: CORRELATION / SEQUENCE != CAUSATION.

A later successful outcome may be a CORRECTION_CANDIDATE.
It is not automatically "the thing that fixed" the earlier failure.

This module READS Outcome V1 evidence. It does NOT:
- create learning evidence
- change learned scores
- train ASI
- modify NBD scoring
- create autonomous self-correction
- persist anything

The graph is derived on demand from canonical evidence. No new ledger.
No second Outcome authority.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

# ── Confidence classes (NBD epistemics) ─────────────────────────────
# FACT: ledger facts (status, identity, ordering)
# DERIVED_FACT: deterministic shared provenance
# PROJECTION: "this later outcome is a correction candidate"
# UNKNOWN: insufficient evidence

CONFIDENCE_CANDIDATE_STRONG = "CORRECTION_CANDIDATE_STRONG"
CONFIDENCE_CANDIDATE = "CORRECTION_CANDIDATE"
CONFIDENCE_UNKNOWN = "UNKNOWN"

# Relationship class (explicitly non-causal)
RELATIONSHIP = "CORRECTION_CANDIDATE"

# Eligible source statuses (need correction)
SOURCE_STATUSES = frozenset({"failed", "blocked"})

# Eligible candidate status (must be completed)
CANDIDATE_STATUS = "completed"


def _outcome_seq(o: Dict[str, Any]) -> int:
    """Canonical temporal ordering."""
    return int(o.get("outcome_seq", 0) or 0)


def _knowledge_ids(o: Dict[str, Any]) -> Set[str]:
    """Knowledge identities involved in outcome."""
    ids = set()
    for k in o.get("knowledge") or []:
        if isinstance(k, dict) and k.get("id"):
            ids.add(str(k["id"]))
    return ids


def _generation_id(o: Dict[str, Any]) -> Optional[str]:
    """Generation/checkpoint epoch."""
    return o.get("generation_id")


def _shared_knowledge(a: Dict[str, Any], b: Dict[str, Any]) -> Set[str]:
    """Knowledge IDs present in both outcomes."""
    return _knowledge_ids(a) & _knowledge_ids(b)


def _is_eligible_source(o: Dict[str, Any]) -> bool:
    """FAILED or BLOCKED outcomes may need correction."""
    return str(o.get("result", "")) in SOURCE_STATUSES


def _is_eligible_candidate(o: Dict[str, Any]) -> bool:
    """Only COMPLETED outcomes can be correction candidates."""
    return str(o.get("result", "")) == CANDIDATE_STATUS


def _confidence_for(source: Dict[str, Any], candidate: Dict[str, Any],
                    shared_kids: Set[str]) -> str:
    """Determine confidence class from evidence.

    STRONG: shared knowledge IDs (deterministic shared provenance)
    CANDIDATE: same dell + semantic, no shared knowledge
    UNKNOWN: insufficient evidence (should not happen if called correctly)
    """
    if shared_kids:
        return CONFIDENCE_CANDIDATE_STRONG
    # Same dell and semantic provides weaker but valid linkage
    if (source.get("dell") == candidate.get("dell")
            and source.get("dell") is not None
            and source.get("semantic") == candidate.get("semantic")
            and source.get("semantic")):
        return CONFIDENCE_CANDIDATE
    return CONFIDENCE_UNKNOWN


def correction_edges(program: Any) -> List[Dict[str, Any]]:
    """Project correction candidate edges from Outcome V1 ledger.

    Read-only. Pure derivation from canonical evidence.

    Returns list of:
    {
        "earlier_outcome_id": str,      # FACT: from ledger
        "later_outcome_id": str,        # FACT: from ledger
        "relationship": "CORRECTION_CANDIDATE",  # PROJECTION label
        "shared_knowledge_ids": [...], # DERIVED_FACT
        "temporal_evidence": {          # FACT
            "earlier_seq": int,
            "later_seq": int,
        },
        "confidence": "CORRECTION_CANDIDATE_STRONG" | "CORRECTION_CANDIDATE",
        "reason": str,  # human-readable evidence summary
    }

    Ordered by: stronger shared evidence first, then canonical temporal order.
    Deterministic.
    """
    from form.mandell.outcome_ledger import list_outcomes

    outcomes = list_outcomes(program, limit=1000)
    if not outcomes:
        return []

    # Index by seq for temporal ordering
    by_seq = sorted(outcomes, key=_outcome_seq)

    edges = []
    for i, source in enumerate(by_seq):
        if not _is_eligible_source(source):
            continue
        source_seq = _outcome_seq(source)
        source_gen = _generation_id(source)

        for candidate in by_seq[i + 1:]:
            if not _is_eligible_candidate(candidate):
                continue
            cand_seq = _outcome_seq(candidate)
            if cand_seq <= source_seq:
                continue  # Must be strictly later

            # Generation boundary: do not cross generations blindly.
            # Only relate within same generation_id (or both None).
            cand_gen = _generation_id(candidate)
            if source_gen != cand_gen:
                continue

            shared = _shared_knowledge(source, candidate)
            conf = _confidence_for(source, candidate, shared)
            if conf == CONFIDENCE_UNKNOWN:
                continue  # Insufficient evidence; do not project

            edges.append({
                "earlier_outcome_id": source.get("outcome_id"),
                "later_outcome_id": candidate.get("outcome_id"),
                "relationship": RELATIONSHIP,
                "shared_knowledge_ids": sorted(shared),
                "temporal_evidence": {
                    "earlier_seq": source_seq,
                    "later_seq": cand_seq,
                },
                "confidence": conf,
                "reason": _build_reason(source, candidate, shared, conf),
            })

    # Deterministic ordering: stronger evidence first, then temporal
    def _sort_key(e):
        strong = 0 if e["confidence"] == CONFIDENCE_CANDIDATE_STRONG else 1
        return (strong, e["temporal_evidence"]["earlier_seq"],
                e["temporal_evidence"]["later_seq"])

    edges.sort(key=_sort_key)
    return edges


def _build_reason(source: Dict[str, Any], candidate: Dict[str, Any],
                  shared: Set[str], confidence: str) -> str:
    """Human-readable evidence summary."""
    parts = [
        f"Outcome {source.get('outcome_id')} ({source.get('result')})",
        f"seq {source.get('outcome_seq')}",
    ]
    if shared:
        parts.append(f"shares knowledge {sorted(shared)} with")
    else:
        parts.append(f"shares dell {candidate.get('dell')}/"
                     f"{candidate.get('semantic')} with")
    parts.append(
        f"outcome {candidate.get('outcome_id')} (completed) "
        f"seq {candidate.get('outcome_seq')}"
    )
    parts.append(f"[{confidence}; correlation, not proven causation]")
    return " ".join(parts)


def explain_correction(program: Any, outcome_id: str) -> Dict[str, Any]:
    """Explain what (if anything) is a correction candidate for an outcome.

    Returns:
    {
        "ok": bool,
        "outcome_id": str,
        "outcome_result": str,
        "candidates": [...],  # correction edges where this is the earlier
        "explanation": str,   # human-readable
        "what_we_know": [...],
        "what_we_do_not_know": [...],
    }

    Never fabricates. If insufficient evidence, says so.
    """
    from form.mandell.outcome_ledger import get_outcome

    outcome = get_outcome(program, outcome_id)
    if outcome is None:
        return {
            "ok": False,
            "outcome_id": outcome_id,
            "reason": "outcome_not_found",
            "explanation": f"No outcome with ID {outcome_id} found in ledger.",
        }

    result = str(outcome.get("result", ""))
    if result not in SOURCE_STATUSES:
        return {
            "ok": True,
            "outcome_id": outcome_id,
            "outcome_result": result,
            "candidates": [],
            "explanation": (
                f"Outcome {outcome_id} has result '{result}', which does not "
                f"indicate a failure needing correction."
            ),
            "what_we_know": [f"result={result}", f"seq={outcome.get('outcome_seq')}"],
            "what_we_do_not_know": [],
        }

    # Find candidates where this is the earlier outcome
    all_edges = correction_edges(program)
    candidates = [e for e in all_edges
                  if e["earlier_outcome_id"] == outcome_id]

    what_we_know = [
        f"result={result}",
        f"seq={outcome.get('outcome_seq')}",
        f"dell={outcome.get('dell')}",
        f"knowledge_ids={sorted(_knowledge_ids(outcome))}",
    ]
    what_we_do_not_know = [
        "Whether any candidate actually caused the correction "
        "(correlation != causation).",
        "Whether the failure would have resolved without the candidate.",
    ]

    if not candidates:
        explanation = (
            f"Outcome {outcome_id} ({result}) has no later completed outcome "
            f"with sufficient shared evidence to project as a correction candidate."
        )
    else:
        c = candidates[0]
        explanation = (
            f"Outcome {outcome_id} ({result}) has "
            f"{len(candidates)} correction candidate(s). "
            f"Strongest: {c['later_outcome_id']} "
            f"({c['confidence']}). {c['reason']}"
        )

    return {
        "ok": True,
        "outcome_id": outcome_id,
        "outcome_result": result,
        "candidates": candidates,
        "explanation": explanation,
        "what_we_know": what_we_know,
        "what_we_do_not_know": what_we_do_not_know,
    }
