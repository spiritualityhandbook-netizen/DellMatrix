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


_ABSENT = object()  # sentinel: distinguishes absent key from explicit null


def _presence_state(program: Any, unit_id: str):
    """TPP-I compatibility adapter: (faded, malformed, reason).

    Director 2026-10-05 (close): use membership checks and a sentinel
    before reading values. Distinguishes:
    - absent lifecycle attr / absent key -> legacy absence (not faded)
    - wrong container type (lifecycle not a dict) -> malformed
    - explicit null record (lifecycle[uid] is None) -> malformed
    - wrong record type (not a dict) -> malformed
    - absent presence key -> not faded (legacy default)
    - explicit null presence -> malformed
    - invalid presence value -> malformed

    Never raises.
    """
    try:
        if not hasattr(program, "lifecycle"):
            return (False, False, "absent_legacy")
        lc = program.lifecycle
        if not isinstance(lc, dict):
            return (False, True, "malformed_presence:wrong_container")
        meta = lc.get(unit_id, _ABSENT)
        if meta is _ABSENT:
            return (False, False, "absent_legacy")
        if meta is None:
            return (False, True, "malformed_presence:null_record")
        if not isinstance(meta, dict):
            return (False, True, "malformed_presence:wrong_record_type")
        presence = meta.get("presence", _ABSENT)
        if presence is _ABSENT or presence == "active":
            return (False, False, "")
        if presence is None:
            return (False, True, "malformed_presence:null_value")
        if presence == "faded":
            return (True, False, "")
        return (False, True, f"malformed_presence:invalid_value:{presence!r}")
    except Exception as e:
        return (False, True, f"malformed_presence:unreadable:{type(e).__name__}")


def _presence_is_faded(program: Any, unit_id: str) -> bool:
    """True iff presence is explicitly faded (and well-formed)."""
    faded, malformed, _ = _presence_state(program, unit_id)
    return faded and not malformed


def _revision_valid(program: Any, unit_id: str) -> Optional[str]:
    """Validated revision state, or None if invalid.

    Invalid = malformed/unknown/unreadable. Faded presence never rescues
    an invalid revision.
    """
    state = resolve_lifecycle(program, unit_id)
    if state in ("active", "superseded"):
        return state
    return None


def _acceptance_state(program: Any, unit_id: str):
    """Acceptance dimension: (accepted, malformed, reason).

    Director 2026-10-05 (close): use membership checks and a sentinel.
    Distinguishes:
    - absent nursery/proposals/key -> legacy absence (defer to revision)
    - wrong container type (proposals not a dict) -> malformed
    - explicit null record -> malformed
    - wrong record type (no status attribute) -> malformed
    - explicit null status -> malformed
    - invalid status value -> malformed

    Never raises.
    """
    try:
        nursery = getattr(program, "nursery", None)
        if nursery is None or not hasattr(nursery, "proposals"):
            return (True, False, "absent_legacy")
        proposals = nursery.proposals
        if not isinstance(proposals, dict):
            return (False, True, "malformed_status:wrong_container")
        prop = proposals.get(unit_id, _ABSENT)
        if prop is _ABSENT:
            # No proposal record: legitimate legacy path. Revision
            # validation remains authoritative.
            return (True, False, "absent_legacy")
        if prop is None:
            return (False, True, "malformed_status:null_record")
        if not hasattr(prop, "status"):
            return (False, True, "malformed_status:wrong_record_type")
        status = prop.status
        if status == "confirmed":
            return (True, False, "")
        if status in ("pending", "rejected"):
            return (False, False, f"status_{status}")
        if status is None:
            return (False, True, "malformed_status:null_value")
        return (False, True, f"malformed_status:invalid_value:{status!r}")
    except Exception as e:
        return (False, True, f"malformed_status:unreadable:{type(e).__name__}")


def _is_accepted(program: Any, unit_id: str) -> bool:
    """True iff acceptance dimension permits participation."""
    accepted, malformed, _ = _acceptance_state(program, unit_id)
    return accepted and not malformed


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
    accepted, acc_malformed, _ = _acceptance_state(program, unit_id)
    if acc_malformed or not accepted:
        # Malformed status excludes everywhere; pending/rejected excludes.
        return False
    faded, pres_malformed, _ = _presence_state(program, unit_id)
    if pres_malformed:
        # Malformed presence excludes in EVERY context with explicit reason.
        return False
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
    accepted, acc_malformed, acc_reason = _acceptance_state(program, unit_id)
    if acc_malformed:
        return (f"excluded ({context} context): malformed acceptance "
                f"({acc_reason}); malformed records never participate")
    if not accepted:
        return f"excluded ({context} context): not accepted ({acc_reason})"
    faded, pres_malformed, pres_reason = _presence_state(program, unit_id)
    if pres_malformed:
        return (f"excluded ({context} context): malformed presence "
                f"({pres_reason}); malformed records never participate")
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
