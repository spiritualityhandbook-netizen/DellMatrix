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
# FADED, DELETED, ARCHIVED, REJECTED, SUPERSEDED are excluded from ordinary
# participation.
# WO-5.3: SUPERSEDED is NOT in ordinary _ACTIVE_STATES. Explicit historical
# use ("use idea {id} to grow") uses the historical context via
# is_participating(..., context="historical"), not broad inclusion.
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
    """Resolve canonical REVISION state for (program, unit_id).

    Returns the revision dimension only: "active" | "superseded" |
    "malformed" | "unknown". Participation (faded presence) is a SEPARATE
    dimension — see is_participating().

    Director 2026-10-05 (whole-circuit): the underlying record is
    VALIDATED FIRST. TPP-I faded presence must not mask malformed revision
    data, and faded presence never makes malformed records eligible.

    Uses form.mandell.supersession.inspect_revision — the canonical
    resolver. Never reads dynamic Unit attributes.

    LEGACY COMPATIBILITY (explicit, not silent): Units with NO canonical
    record at all (legacy units predating the proposal system) are treated
    as "active" by explicit compatibility policy. This is documented here,
    not a silent default.

    FAIL-CLOSED: Units WITH a record that is unreadable, malformed, or
    explicitly UNKNOWN resolve as "malformed"/"unknown" (excluded, not
    active). Unreadable canonical state never silently becomes ACTIVE.
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
        # Has a record: revision state, or malformed/unknown if unreadable.
        if state in ("active", "superseded"):
            return state
        return "malformed" if malformed else "unknown"
    except Exception:
        # Unreadable canonical state -> unknown (fail-closed, not active)
        return "unknown"


def _presence_is_faded(program: Any, unit_id: str) -> bool:
    """TPP-I compatibility adapter: faded presence signal.

    Director 2026-10-05 (whole-circuit): TPP-I is a compatibility ADAPTER,
    not an independent competing decision maker. It supplies the faded
    presence signal; the authoritative participation interpretation lives
    in is_participating(), which validates revision FIRST.

    Never raises; unreadable presence means "not faded".
    """
    try:
        lc = getattr(program, "lifecycle", None)
        if isinstance(lc, dict):
            meta = lc.get(unit_id)
            if isinstance(meta, dict):
                return meta.get("presence") == "faded"
    except Exception:
        pass
    return False


def _revision_valid(program: Any, unit_id: str) -> Optional[str]:
    """Validated revision state, or None if invalid.

    Invalid = malformed/unknown/unreadable. Faded presence never rescues
    an invalid revision.
    """
    state = resolve_lifecycle(program, unit_id)
    if state in ("active", "superseded"):
        return state
    return None


def _is_accepted(program: Any, unit_id: str) -> bool:
    """Acceptance dimension: proposal status is confirmed.

    Director 2026-10-05 (whole-circuit): acceptance, revision,
    participation, and projection are DISTINCT. Pending proposals do not
    ordinarily participate, regardless of revision/presence.

    A missing status (synthetic/legacy doubles) is treated as accepted
    for compatibility; an explicit non-confirmed status excludes.
    """
    try:
        proposals = getattr(getattr(program, "nursery", None), "proposals", {})
        prop = proposals.get(unit_id) if isinstance(proposals, dict) else None
        if prop is None:
            # No proposal record: legacy compat path (resolve_lifecycle
            # treats as active). Acceptance unknown -> do not block here;
            # revision validation remains authoritative.
            return True
        status = getattr(prop, "status", None)
        if status is None:
            return True  # synthetic/legacy double: do not block
        return status == "confirmed"
    except Exception:
        return False


def is_active(program: Any, unit_id: str) -> bool:
    """True iff unit may participate ordinarily.

    Requires: accepted (confirmed) AND valid active revision AND
    non-faded presence. Malformed/unknown revisions return False
    (fail-closed) even when presence claims faded.
    """
    return (_is_accepted(program, unit_id)
            and _revision_valid(program, unit_id) == "active"
            and not _presence_is_faded(program, unit_id))


def is_faded(program: Any, unit_id: str) -> bool:
    """True iff unit carries faded presence on a VALID revision.

    Director 2026-10-05 (whole-circuit): faded presence on a malformed
    or unknown revision is NOT "faded" — it is excluded data. Fading is
    participation, not revision.
    """
    return (_revision_valid(program, unit_id) is not None
            and _presence_is_faded(program, unit_id))


# WO-5.2/WO-5.3: Participation contexts.
# Ordinary participation: eligible accepted/current knowledge only.
# Excludes SUPERSEDED, FADED, and other non-current states.
_ORDINARY_PARTICIPATION_STATES = frozenset({
    LifecycleState.ACTIVE.value,
    LifecycleState.PROPOSED.value,
    LifecycleState.ACCEPTED.value,
    LifecycleState.RESTORED.value,
})

# Historical participation: explicitly requested historical use.
# Includes SUPERSEDED and FADED with clear labels. Does not include
# malformed/unknown/deleted.
_HISTORICAL_PARTICIPATION_STATES = frozenset({
    LifecycleState.ACTIVE.value,
    LifecycleState.PROPOSED.value,
    LifecycleState.ACCEPTED.value,
    LifecycleState.RESTORED.value,
    LifecycleState.SUPERSEDED.value,
    LifecycleState.FADED.value,
})


def is_participating(program: Any, unit_id: str,
                     context: str = "ordinary") -> bool:
    """WO-5.2/WO-5.3: Check participation in a given context.

    Director 2026-10-05 (whole-circuit): ONE authoritative participation
    interpretation. Revision is validated FIRST; faded presence never
    rescues malformed/unknown revisions.

    Args:
        program: The program.
        unit_id: The unit/idea ID.
        context: "ordinary" (default) or "historical".
            - "ordinary": accepted + revision-active + non-faded presence.
              Excludes SUPERSEDED, FADED, pending, malformed.
            - "historical": explicitly requested historical use. Accepted
              records with revision active-or-superseded, including faded
              presence. NEVER malformed/unknown.

    Returns:
        True iff the record may participate in the given context.
    """
    revision = _revision_valid(program, unit_id)
    if revision is None:
        # Malformed/unknown: excluded in EVERY context. Faded presence
        # must not make malformed data eligible for historical use.
        return False
    if not _is_accepted(program, unit_id):
        return False
    faded = _presence_is_faded(program, unit_id)
    if context == "historical":
        return revision in ("active", "superseded")
    # Default: ordinary
    return revision == "active" and not faded


def participation_reason(program: Any, unit_id: str,
                         context: str = "ordinary") -> str:
    """WO-5.2: Human-readable reason for participation decision.

    Exposes why a record is excluded, for transparency.
    """
    revision = _revision_valid(program, unit_id)
    if revision is None:
        return (f"excluded ({context} context): "
                f"revision {resolve_lifecycle(program, unit_id)}; "
                "malformed/unknown records never participate")
    if not _is_accepted(program, unit_id):
        return f"excluded ({context} context): not accepted (pending)"
    faded = _presence_is_faded(program, unit_id)
    if context == "historical":
        if revision in ("active", "superseded"):
            return (f"participating (historical context, revision={revision}, "
                    f"faded={faded})")
        return f"excluded (historical context, revision={revision})"
    if revision == "active" and not faded:
        return "participating (ordinary context)"
    if revision == "superseded":
        return ("excluded (ordinary context): superseded; "
                "use historical context for explicit historical use")
    if faded:
        return ("excluded (ordinary context): faded; "
                "use historical context for explicit historical inspection")
    return f"excluded (ordinary context, revision={revision})"


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
