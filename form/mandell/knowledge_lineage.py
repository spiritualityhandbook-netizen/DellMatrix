#!/usr/bin/env python3
"""DCC-XIV: Knowledge evidence lineage + provenance-aware routing (Lineage V1).

Lineage V1 exposes the PERSISTED ancestry structure of knowledge units. It
is built exclusively on the repository's existing lineage authority
(form/dell_matrix/lineage.py): parents, origin, lineage_version are set at
creation/confirmation, validated by assign_lineage, and survive save/load.

Lineage V1 contract:
  - origin_kind: "direct" (no parents) or "derived" (has parents).
    "direct" does NOT mean verified; there is no external source
    verification in this architecture.
  - parent_ids: normalized (deduped, stable first-seen order).
  - root_ids: sorted IDs of transitive ancestors with no parents; a
    direct unit is its own root.
  - depth: derivation generations = unit lineage_version
    (1 for direct; 1 + max(parent depths) for derived).
  - status: "ok" | "cycle" | "missing_parents" | "unknown_unit".
    Malformed lineage is marked, never silently fabricated.

PROVENANCE IS NOT TRUTH. Multiple roots do not make a claim true; a
shared root does not make a claim false. Lineage is descriptive metadata
only — it never boosts relevance rank and never resolves conflicts.

Cycle safety: creation validates via assign_lineage (self_parent,
lineage_cycle, missing_parent rejected). Reads use the cycle-guarded
_ancestors traversal. Legacy restore skips validation, so reads mark
cycle/missing explicitly.
"""
from __future__ import annotations

from typing import Any, Dict, List

from form.dell_matrix.lineage import (
    inspect_lineage,
    normalize_parents,
)

LINEAGE_VERSION = 1


def _units_of(program: Any) -> Dict[str, Any]:
    return getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None).units or {}


def lineage_record(program: Any, uid: str) -> Dict[str, Any]:
    """Deterministic lineage record for one unit.

    Fields: unit_id, origin_kind, origin, parent_ids, root_ids, depth,
    status, cycle, missing_parents. Reconstructible from persisted state.
    """
    units = _units_of(program)
    u = units.get(uid)
    if u is None:
        return {
            "unit_id": uid, "origin_kind": "unknown", "origin": "unknown",
            "parent_ids": [], "root_ids": [], "depth": 0,
            "status": "unknown_unit", "cycle": False, "missing_parents": [],
        }
    parents = normalize_parents(getattr(u, "parents", None))
    insp = inspect_lineage(getattr(getattr(getattr(program, "cube", None), "session", None), "plane", None), uid)

    # Roots: transitive ancestors with no parents; a direct unit roots itself.
    roots = set()
    if not parents:
        roots.add(uid)
    else:
        for anc in insp.get("ancestors", []):
            au = units.get(anc)
            if au is not None and not normalize_parents(getattr(au, "parents", None)):
                roots.add(anc)
    root_ids = sorted(roots)

    try:
        depth = int(getattr(u, "lineage_version", 1) or 1)
    except (TypeError, ValueError):
        depth = 1
    if depth < 1:
        depth = 1

    missing = list(insp.get("missing_parents", []) or [])
    cycle = bool(insp.get("cycle", False))
    if cycle:
        status = "cycle"
    elif missing:
        status = "missing_parents"
    else:
        status = "ok"

    return {
        "unit_id": uid,
        "origin_kind": "direct" if not parents else "derived",
        "origin": getattr(u, "origin", "placed") or "placed",
        "parent_ids": parents,
        "root_ids": root_ids,
        "depth": depth,
        "status": status,
        "cycle": cycle,
        "missing_parents": sorted(missing),
    }


def selected_lineage(program: Any, unit_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Lineage records for each selected unit (deterministic key order)."""
    return {uid: lineage_record(program, uid) for uid in unit_ids}


def lineage_groups(program: Any, unit_ids: List[str]) -> Dict[str, List[str]]:
    """Group selected units by shared lineage root.

    Returns {root_id: sorted(member_ids)}. A unit with multiple roots
    appears under each. Neutral terminology: lineage groups / independent
    roots — never "independent sources" as a truth claim.
    """
    groups: Dict[str, List[str]] = {}
    for uid in unit_ids:
        rec = lineage_record(program, uid)
        for root in rec["root_ids"]:
            groups.setdefault(root, []).append(uid)
    return {root: sorted(members) for root, members in sorted(groups.items())}


def selected_root_ids(program: Any, unit_ids: List[str]) -> List[str]:
    """Sorted union of lineage roots across the selected units."""
    roots = set()
    for uid in unit_ids:
        roots.update(lineage_record(program, uid)["root_ids"])
    return sorted(roots)
