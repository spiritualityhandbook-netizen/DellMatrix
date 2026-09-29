#!/usr/bin/env python3
"""Plane-valid nursery proposal selection. Does not delete pending."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def proposal_parents(prop: Any) -> List[str]:
    if isinstance(prop, dict):
        raw = prop.get("parents") or []
    else:
        raw = getattr(prop, "parents", None) or []
    out: List[str] = []
    seen = set()
    for item in raw:
        pid = str(item).strip()
        if pid and pid not in seen:
            seen.add(pid)
            out.append(pid)
    return out


def proposal_id(prop: Any) -> str:
    if isinstance(prop, dict):
        return str(prop.get("id") or "")
    return str(getattr(prop, "id", "") or "")


def proposal_valid_for_plane(prop: Any, units: Iterable[str]) -> bool:
    live = set(units)
    return all(pid in live for pid in proposal_parents(prop))


def select_confirmable_proposal(pending: List[Any], units: Iterable[str]) -> Optional[Any]:
    valid = [p for p in pending if proposal_valid_for_plane(p, units)]
    if not valid:
        return None

    def key(p: Any):
        if isinstance(prop if False else p, dict):
            aff = float(p.get("affinity") or 0)
            pid = str(p.get("id") or "")
        else:
            aff = float(getattr(p, "affinity", 0) or 0)
            pid = str(getattr(p, "id", "") or "")
        return (-aff, pid)

    return sorted(valid, key=key)[0]
