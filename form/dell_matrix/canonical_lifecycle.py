#!/usr/bin/env python3
"""P3 Canonical Lifecycle Boundary (GDP_PHASE_3_CANONICAL_LIFECYCLE_CLOSEOUT).

Single owner-aware boundary resolving canonical Idea lifecycle for
harmony IDs, affinity/growth eligibility, and pulse influence.

Canonical owner: form.mandell.idea.LifecycleState
Canonical resolver: form.mandell.supersession.inspect_revision

DESIGN:
- Lifecycle is resolved via (program, unit_id) through inspect_revision,
  NOT via dynamically injected Unit attributes.
- The boundary is owner-aware: it requires the program (owner) that holds
  the canonical proposal records.
- Unreadable canonical state (UNKNOWN, malformed, missing) FAILS CLOSED:
  it does NOT silently become ACTIVE. Such units are excluded from
  resonance/affinity/harmony computation.

This replaces the attribute-injection approach (getattr(unit,
"lifecycle_state", None)) which was fragile and treated legacy Units
as implicitly ACTIVE.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, TypeVar

from form.mandell.idea import LifecycleState

_T = TypeVar("_T")

# States that permit participation in resonance/affinity/harmony.
# FADED, SUPERSEDED, DELETED, ARCHIVED, REJECTED are excluded.
# UNKNOWN/malformed/unreadable are excluded (fail-closed).
_ACTIVE_STATES = frozenset({
    LifecycleState.ACTIVE.value,
    LifecycleState.PROPOSED.value,
    LifecycleState.ACCEPTED.value,
    LifecycleState.RESTORED.value,
})


def _normalize_state(state: Any) -> Optional[str]:
    """Normalize a lifecycle state to its canonical string value."""
    if state is None:
        return None
    if isinstance(state, LifecycleState):
        return state.value
    try:
        return str(state).strip().lower()
    except Exception:
        return None


def resolve_lifecycle(program: Any, unit_id: str) -> str:
    """Resolve canonical lifecycle state for (program, unit_id).

    Uses form.mandell.supersession.inspect_revision — the canonical
    resolver. Never reads dynamic Unit attributes.

    Returns the canonical state string (e.g. "active", "faded",
    "unknown").

    LEGACY COMPATIBILITY (explicit, not silent): Units with NO canonical
    record at all (legacy units predating the proposal system) are treated
    as "active" by explicit compatibility policy. This is documented here,
    not a silent default.

    FAIL-CLOSED: Units WITH a record that is unreadable, malformed, or
    explicitly UNKNOWN are treated as "unknown" (excluded, not active).
    Unreadable canonical state never silently becomes ACTIVE.
    """
    try:
        from form.mandell.supersession import inspect_revision
        rec = inspect_revision(program, unit_id)
        # Distinguish "no record" (legacy) from "unreadable record"
        # inspect_revision returns malformed_reason="unknown_unit" for
        # units with no proposal record at all.
        malformed = rec.get("malformed_reason")
        state = _normalize_state(rec.get("lifecycle_state"))
        if malformed == "unknown_unit":
            # Legacy unit: no canonical record. Explicit compatibility:
            # treat as active (documented policy, not silent default).
            return "active"
        # Has a record: use its state, or "unknown" if unreadable.
        return state or "unknown"
    except Exception:
        # Unreadable canonical state -> unknown (fail-closed, not active)
        return "unknown"


def is_active(program: Any, unit_id: str) -> bool:
    """True iff canonical lifecycle for (program, unit_id) permits participation.

    Unreadable/unknown/malformed states return False (fail-closed).
    """
    return resolve_lifecycle(program, unit_id) in _ACTIVE_STATES


def is_faded(program: Any, unit_id: str) -> bool:
    """True iff canonical lifecycle for (program, unit_id) is FADED."""
    return resolve_lifecycle(program, unit_id) == LifecycleState.FADED.value


def filter_active(program: Any, unit_ids: Iterable[str]) -> List[str]:
    """Return unit IDs with active canonical lifecycle, in original order.

    Units with unreadable/unknown lifecycle are excluded (fail-closed).
    """
    return [uid for uid in (unit_ids or []) if is_active(program, uid)]


def lifecycle_of_idea(idea: Any) -> str:
    """Resolve lifecycle for an Idea-like object (not a Unit ID).

    For Idea objects that carry their own canonical state (idea_state
    or lifecycle_state attributes on the Idea itself, not injected),
    read it directly. For objects carrying no state, return "unknown"
    (fail-closed, not active).

    This is for Idea objects only. For plane Units, use
    resolve_lifecycle(program, unit_id) with the owner program.
    """
    if idea is None:
        return "unknown"
    for attr in ("idea_state", "lifecycle_state"):
        try:
            st = getattr(idea, attr, None)
        except Exception:
            st = None
        if st is not None:
            normalized = _normalize_state(st)
            if normalized:
                return normalized
    return "unknown"


def is_idea_active(idea: Any) -> bool:
    """True iff an Idea-like object's own lifecycle permits participation."""
    return lifecycle_of_idea(idea) in _ACTIVE_STATES


def exclude_inactive_ideas(ideas: Iterable[_T]) -> List[_T]:
    """Return Ideas with active lifecycle, in original order.

    Fail-closed: Ideas with unreadable/unknown lifecycle are excluded.
    """
    return [i for i in (ideas or []) if is_idea_active(i)]
