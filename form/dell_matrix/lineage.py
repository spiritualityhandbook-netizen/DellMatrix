#!/usr/bin/env python3
"""Single lineage authority: parents, origin, version, inspect."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def normalize_parents(parents: Optional[Iterable[Any]]) -> List[str]:
    out: List[str] = []
    seen = set()
    for raw in parents or []:
        pid = str(raw).strip()
        if not pid or pid in seen:
            continue
        seen.add(pid)
        out.append(pid)
    return out


def child_version(parent_versions: Iterable[Any]) -> int:
    vals = []
    for v in parent_versions or []:
        try:
            n = int(v)
        except (TypeError, ValueError):
            n = 1
        if n < 1:
            n = 1
        vals.append(n)
    if not vals:
        return 1
    return max(vals) + 1


def _ancestors(units: Dict[str, Any], start_ids: Iterable[str], stop: Optional[str] = None):
    seen = set()
    stack = list(normalize_parents(start_ids))
    cycle = False
    missing = []
    ordered = []
    while stack:
        pid = stack.pop(0)
        if pid == stop:
            cycle = True
            continue
        if pid in seen:
            continue
        seen.add(pid)
        ordered.append(pid)
        parent = units.get(pid)
        if parent is None:
            missing.append(pid)
            continue
        for gp in normalize_parents(getattr(parent, "parents", None)):
            if gp == stop:
                cycle = True
            elif gp not in seen:
                stack.append(gp)
    return ordered, missing, cycle


def assign_lineage(
    units: Optional[Dict[str, Any]],
    parents: Optional[Iterable[Any]],
    origin: str = "placed",
    lineage_version: Optional[int] = None,
    child_id: Optional[str] = None,
    restore: bool = False,
) -> Dict[str, Any]:
    units = units or {}
    origin = str(origin or "placed").strip() or "placed"
    parents = normalize_parents(parents)
    if child_id and child_id in parents:
        return {"ok": False, "error": "self_parent", "parents": [], "origin": origin, "lineage_version": 1, "missing": []}
    if not restore:
        _, missing, cycle = _ancestors(units, parents, stop=child_id)
        if cycle:
            return {"ok": False, "error": "lineage_cycle", "parents": parents, "origin": origin, "lineage_version": 1, "missing": missing}
        if missing:
            return {"ok": False, "error": "missing_parent", "parents": parents, "origin": origin, "lineage_version": 1, "missing": missing}
    if lineage_version is not None:
        try:
            ver = int(lineage_version)
        except (TypeError, ValueError):
            ver = 0
        if ver < 1:
            return {"ok": False, "error": "malformed_version", "parents": parents, "origin": origin, "lineage_version": 1, "missing": []}
        return {"ok": True, "parents": parents, "origin": origin, "lineage_version": ver, "missing": []}
    if not parents:
        return {"ok": True, "parents": [], "origin": origin, "lineage_version": 1, "missing": []}
    versions = [getattr(units[pid], "lineage_version", 1) for pid in parents if pid in units]
    return {"ok": True, "parents": parents, "origin": origin, "lineage_version": child_version(versions), "missing": []}


def inspect_lineage(plane: Any, unit_id: str) -> Dict[str, Any]:
    units = getattr(plane, "units", None) or {}
    if unit_id not in units:
        return {"ok": False, "error": "missing_unit", "id": unit_id, "missing_parents": []}
    u = units[unit_id]
    children = sorted(i for i, other in units.items() if unit_id in normalize_parents(getattr(other, "parents", None)))
    ancestors, missing, cycle = _ancestors(units, getattr(u, "parents", None), stop=unit_id)
    return {"ok": True, "id": unit_id, "parents": normalize_parents(getattr(u, "parents", None)), "children": children, "ancestors": ancestors, "origin": getattr(u, "origin", "placed") or "placed", "lineage_version": int(getattr(u, "lineage_version", 1) or 1), "cycle": cycle, "missing_parents": missing}
