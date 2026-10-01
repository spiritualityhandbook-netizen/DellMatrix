#!/usr/bin/env python3
"""DCC-XV: Dependency validity + transitive knowledge invalidation (Dependency V1).

DCC-XIV records historical ancestry. Dependency V1 answers a separate,
current-state question: do a unit's required ancestors still satisfy the
bounded routing contract?

HISTORICAL LINEAGE (immutable):
    where knowledge came from. Parent lists are persisted on both the
    plane unit and the nursery proposal; the proposal record survives plane
    removal, so historical ancestry (parents, historical roots, depth,
    origin) never changes when validity changes.

CURRENT DEPENDENCY VALIDITY (recomputed from live state):
    whether every required transitive ancestor still qualifies.

Ancestor qualification (architecture-derived; mirrors accepted knowledge):
    - exists on the plane (present where required)
    - nursery proposal status == "confirmed" (accepted knowledge model)
    - revision lifecycle_state == "active" (DCC-XVI: a superseded ancestor
      no longer qualifies; descendants keep their historical parents and
      are NOT silently retargeted to the successor revision)
    - lineage constructible (status ok or missing_parents; a cycle or
      unknown lineage disqualifies the ancestor itself)

A "missing_parents" lineage status is a dependency-state signal, not an
ancestor disqualifier: the absent ancestors are named in
missing_dependency_ids rather than rewriting history.

Dependency V1 statuses:
    valid     — every required transitive ancestor qualifies
                (direct units: vacuously valid; no self-dependency)
    missing   — at least one required ancestor is absent from the plane
    invalid   — at least one required ancestor is present but unqualified
                (not confirmed, superseded revision, or lineage
                unconstructible). Reason "superseded_dependency:<ids>"
                when every disqualifying ancestor is a superseded revision;
                otherwise "unqualified_ancestors:<ids>".
    malformed — the unit's own lineage cannot be constructed
                (unknown unit / cycle)

Precedence: malformed > missing > invalid > valid.

DEPENDENCY VALIDITY != RELEVANCE != CONFLICT != TRUTH. Dependency never
boosts rank, never resolves conflict, never verifies external claims.

Invalidation is one-way in the current lifecycle: confirmed proposals are
terminal (no public reject/demote), and plane removal (e.g. undo) has no
public restore. Revalidation is NOT_APPLICABLE; validity is always
recomputed from current state, never cached.
"""
from __future__ import annotations

from typing import Any, Dict, List

from form.dell_matrix.lineage import normalize_parents
from form.mandell.knowledge_lineage import lineage_record

DEPENDENCY_VERSION = 1


def _plane_units(program: Any) -> Dict[str, Any]:
    plane = getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None)
    return getattr(plane, "units", None) or {}


def _proposals(program: Any) -> Dict[str, Any]:
    return getattr(getattr(program, "nursery", None), "proposals", None) or {}


def _proposal_status(program: Any, uid: str) -> str:
    prop = _proposals(program).get(uid)
    return getattr(prop, "status", "") or ""


def historical_parents(program: Any, uid: str) -> List[str]:
    """Persisted parent list for a unit, alive or removed.

    The plane unit carries parents while present; the nursery proposal
    persists after plane removal (the legitimate invalidation path), so
    historical ancestry survives. Returns [] when no record exists.
    """
    unit = _plane_units(program).get(uid)
    if unit is not None:
        return normalize_parents(getattr(unit, "parents", None))
    prop = _proposals(program).get(uid)
    if prop is not None:
        return normalize_parents(getattr(prop, "parents", None))
    return []


def historical_ancestors(program: Any, uid: str) -> List[str]:
    """Full transitive historical ancestor set (sorted), cycle-guarded.

    Walks persisted parent lists (unit, else nursery proposal), so removed
    ancestors and their own ancestry remain visible as historical evidence.
    """
    seen: List[str] = []
    seen_set = set()
    stack = list(historical_parents(program, uid))
    while stack:
        aid = stack.pop(0)
        if aid in seen_set:
            continue
        seen_set.add(aid)
        seen.append(aid)
        for gp in historical_parents(program, aid):
            if gp not in seen_set:
                stack.append(gp)
    return sorted(seen_set)


def historical_roots(program: Any, uid: str) -> List[str]:
    """Historical root union: ancestors with no persisted parents.

    A direct unit roots itself. Unlike DCC-XIV's live-presence root_ids,
    this never changes when an ancestor is removed — it is the immutable
    ancestry evidence Dependency V1 layers validity on top of.
    """
    parents = historical_parents(program, uid)
    if not parents:
        return [uid]
    return sorted(a for a in historical_ancestors(program, uid)
                  if not historical_parents(program, a))


def inspect_dependency(program: Any, uid: str) -> Dict[str, Any]:
    """Deterministic Dependency V1 inspection for one unit.

    Fields: unit_id, direct_parent_ids, ancestor_ids (sorted),
    historical_root_ids (sorted), invalid_dependency_ids (sorted),
    missing_dependency_ids (sorted), dependency_status, dependency_reason.
    """
    units = _plane_units(program)
    own = lineage_record(program, uid)
    parents = historical_parents(program, uid)

    # Unknown unit or a cycle: dependency evidence cannot be constructed.
    if own["status"] in ("unknown_unit", "cycle"):
        return {
            "unit_id": uid,
            "direct_parent_ids": parents,
            "ancestor_ids": [],
            "historical_root_ids": [],
            "invalid_dependency_ids": [],
            "missing_dependency_ids": [],
            "dependency_status": "malformed",
            "dependency_reason": f"lineage_{own['status']}",
        }

    ancestor_ids = historical_ancestors(program, uid)
    root_ids = historical_roots(program, uid)

    missing: List[str] = []
    invalid: List[str] = []
    superseded: List[str] = []
    for aid in ancestor_ids:
        if aid not in units:
            # Absent from the plane: the root-cause "missing" signal.
            missing.append(aid)
            continue
        if _proposal_status(program, aid) != "confirmed":
            # Present but not accepted knowledge (rejected/pending/unknown).
            invalid.append(aid)
            continue
        # DCC-XVI: a superseded (or malformed-revision) ancestor no longer
        # qualifies as an active dependency. Historical parents are kept;
        # nothing is silently retargeted to the successor revision.
        from form.mandell.supersession import inspect_revision as _inspect_rev
        _rev = _inspect_rev(program, aid)
        if _rev["lifecycle_state"] != "active":
            invalid.append(aid)
            if _rev["lifecycle_state"] == "superseded":
                superseded.append(aid)
            continue
        # Lineage "missing_parents" is a dependency-state signal, not an
        # ancestor disqualifier: the missing ancestors are already named
        # in missing_dependency_ids. Only unconstructible lineage
        # (cycle/unknown) disqualifies the ancestor itself.
        if lineage_record(program, aid)["status"] not in ("ok", "missing_parents"):
            invalid.append(aid)

    missing = sorted(missing)
    invalid = sorted(invalid)
    if missing:
        status, reason = "missing", f"missing_ancestors:{','.join(missing)}"
    elif invalid:
        if superseded and len(superseded) == len(invalid):
            status = "invalid"
            reason = f"superseded_dependency:{','.join(sorted(superseded))}"
        else:
            status, reason = "invalid", f"unqualified_ancestors:{','.join(invalid)}"
    else:
        status, reason = "valid", "all_required_ancestors_qualify"

    return {
        "unit_id": uid,
        "direct_parent_ids": parents,
        "ancestor_ids": ancestor_ids,
        "historical_root_ids": root_ids,
        "invalid_dependency_ids": invalid,
        "missing_dependency_ids": missing,
        "dependency_status": status,
        "dependency_reason": reason,
    }


def is_dependency_valid(program: Any, uid: str) -> bool:
    """True iff the unit is dependency-valid (status == 'valid')."""
    return inspect_dependency(program, uid)["dependency_status"] == "valid"


def dependency_exclusions(
    program: Any, unit_ids: List[str]
) -> List[Dict[str, Any]]:
    """Deterministic exclusion evidence for dependency-invalid candidates.

    Each entry: id, dependency_status, dependency_reason,
    invalid_dependency_ids, missing_dependency_ids. Sorted by id.
    """
    out = []
    for uid in sorted(unit_ids):
        rec = inspect_dependency(program, uid)
        if rec["dependency_status"] != "valid":
            out.append({
                "id": uid,
                "dependency_status": rec["dependency_status"],
                "dependency_reason": rec["dependency_reason"],
                "invalid_dependency_ids": rec["invalid_dependency_ids"],
                "missing_dependency_ids": rec["missing_dependency_ids"],
            })
    return out
