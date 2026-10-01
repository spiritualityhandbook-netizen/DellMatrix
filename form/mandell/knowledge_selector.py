#!/usr/bin/env python3
"""DCC-IX: Deterministic contextual knowledge selector.

Selects relevant confirmed knowledge for an operation based on context,
using the same token/Jaccard semantics as RingedGrowth affinity.

This is a SAFE_ADAPTER: reuses existing repository tokenization semantics,
does not invent new ranking algorithms.

Contract:
  Input: program, context (str), operation (str)
  Output: {
    "context": str,
    "eligible_count": int,
    "selected": [{"id": str, "label": str, "score": float, "shared": [str]}],
    "reason": str
  }

Eligibility: confirmed status AND promoted to cube.
Ranking: Jaccard similarity (desc), then ID (asc) for determinism.
No match: empty selected list (consumer runs baseline).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> Set[str]:
    """Tokenize text the same way RingedGrowth does."""
    return {m.group(0).lower() for m in _TOKEN.finditer(text.lower())}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    """Jaccard similarity between token sets."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _unit_tokens(program: Any, uid: str) -> Set[str]:
    """Get tokens for a cube unit (label + detail)."""
    unit = program.cube.session.plane.units.get(uid)
    if not unit:
        return set()
    label = getattr(unit, "label", "") or ""
    detail = getattr(unit, "detail", "") or ""
    words = getattr(unit, "words", "") or ""
    return _tokens(f"{label} {detail} {words}")


class ScopedPlaneView:
    """Read-only view restricting a plane to a subset of unit IDs.

    DCC-XI: lets RingedGrowth consume exactly the selector-approved
    subset without modifying the consumer or mutating the plane.

    Safety:
    - .units exposes ONLY the scoped subset (snapshot dict at construction).
    - All other attribute access delegates to the real plane
      (enhance_scope, spatial methods). Delegated methods only affect
      affinity weighting between scoped pairs; they cannot introduce
      new units into the pair enumeration (the sole enumeration point
      is list(plane.units.keys()) inside RingedGrowth.run).
    - The view is constructed per-call and never persisted; no way to
      widen or leak scope across calls.
    """

    def __init__(self, plane: Any, unit_ids: List[str]):
        self._plane = plane
        # Snapshot: only IDs present on the real plane, in given order.
        self._scoped = {uid: plane.units[uid] for uid in unit_ids if uid in plane.units}
        self._scope_ids = list(self._scoped.keys())

    @property
    def units(self) -> Dict[str, Any]:
        return self._scoped

    @property
    def scope_ids(self) -> List[str]:
        """The exact unit IDs this view exposes."""
        return list(self._scope_ids)

    def __getattr__(self, name: str) -> Any:
        # Delegate enhance_scope and any other plane API to the real plane.
        # Only called when normal lookup fails, so _plane/_scoped are safe.
        return getattr(self.__dict__["_plane"], name)


def select_for_context(
    program: Any,
    context: str,
    operation: str = "grow",
    min_score: float = 0.0,
    max_selected: int = 5,
) -> Dict[str, Any]:
    """Select confirmed knowledge relevant to context.
    
    Deterministic: same state + context → same selection and ordering.
    Tie-break: score desc, then ID asc.
    """
    context = (context or "").strip()
    ctx_tokens = _tokens(context)
    
    # Eligible: confirmed AND in cube
    eligible = []
    for pid, prop in program.nursery.proposals.items():
        if prop.status != "confirmed":
            continue
        if pid not in program.cube.session.plane.units:
            continue
        eligible.append((pid, prop))
    
    eligible_count = len(eligible)
    
    if not ctx_tokens or not eligible:
        return {
            "context": context,
            "operation": operation,
            "eligible_count": eligible_count,
            "selected": [],
            "reason": "no context tokens" if not ctx_tokens else "no eligible knowledge",
        }
    
    # Score each eligible unit
    scored = []
    for pid, prop in eligible:
        unit_tokens = _unit_tokens(program, pid)
        score = _jaccard(ctx_tokens, unit_tokens)
        if score > min_score:
            shared = sorted(ctx_tokens & unit_tokens)
            scored.append({
                "id": pid,
                "label": prop.label,
                "score": round(score, 4),
                "shared": shared,
            })
    
    # Deterministic ordering: score desc, ID asc
    scored.sort(key=lambda x: (-x["score"], x["id"]))
    
    # Limit to max_selected
    selected = scored[:max_selected]
    
    if selected:
        reason = f"jaccard match: {len(selected)} of {eligible_count} eligible"
    else:
        reason = f"no token overlap with {eligible_count} eligible"
    
    return {
        "context": context,
        "operation": operation,
        "eligible_count": eligible_count,
        "selected": selected,
        "reason": reason,
    }
