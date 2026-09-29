#!/usr/bin/env python3
"""Dell 21/22 live-unit identity + lineage. Plane units only."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


def _units(program: Any) -> Dict[str, Any]:
    return program.cube.session.plane.units


def resolve_unit(units: Dict[str, Any], token: str) -> Optional[Any]:
    token = str(token or "").strip()
    if not token:
        return None
    if token in units:
        return units[token]
    low = token.lower()
    hits = [u for u in units.values() if str(getattr(u, "label", "")).lower() == low]
    if len(hits) == 1:
        return hits[0]
    return None


def label_tokens(label: str) -> List[str]:
    skip = {"and", "or", "to", "from", "with", "into", "plus"}
    parts = [t for t in re.split(r"[\s,+/|&]+", str(label or "").strip()) if t]
    return [t for t in parts if t.lower() not in skip]


def resolve_sources(units: Dict[str, Any], label: str) -> List[Any]:
    found: List[Any] = []
    seen = set()
    for tok in label_tokens(label):
        u = resolve_unit(units, tok)
        if u is None:
            continue
        if u.id in seen:
            continue
        seen.add(u.id)
        found.append(u)
    return found


def _child_id(units: Dict[str, Any], base: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", base).strip("_")[:28] or "child"
    if slug not in units:
        return slug
    n = 2
    while f"{slug}_{n}" in units:
        n += 1
    return f"{slug}_{n}"


def merge_live(program: Any, label: str) -> Dict[str, Any]:
    units = _units(program)
    sources = resolve_sources(units, label)
    if len(sources) < 2:
        vals = list(units.values())
        if not sources and len(vals) >= 2:
            sources = vals[-2:]
        else:
            return {"ok": False, "error": "missing_source", "created": []}
    parent_ids = [u.id for u in sources]
    versions = [int(getattr(u, "lineage_version", 1) or 1) for u in sources]
    snap = {u.id: (u.label, u.words, list(getattr(u, "parents", []) or []), int(getattr(u, "lineage_version", 1) or 1)) for u in sources}
    cid = _child_id(units, "merge_" + "_".join(parent_ids))
    child = program.place(
        cid,
        label.strip() or " + ".join(u.label for u in sources),
        words="merge " + " ".join(parent_ids),
        parents=parent_ids,
        origin="merge",
    )
    for pid, before in snap.items():
        u = units[pid]
        if (u.label, u.words, list(u.parents), int(u.lineage_version)) != before:
            return {"ok": False, "error": "parent_mutated", "id": child.id, "parents": parent_ids}
    return {
        "ok": True,
        "id": child.id,
        "parents": list(child.parents),
        "origin": child.origin,
        "lineage_version": int(child.lineage_version),
        "expected_version": max(versions) + 1,
        "created": [child.id],
    }


def split_live(program: Any, label: str) -> Dict[str, Any]:
    units = _units(program)
    sources = resolve_sources(units, label)
    source = sources[0] if sources else None
    if source is None and units:
        source = list(units.values())[-1]
    if source is None:
        return {"ok": False, "error": "missing_source", "created": []}
    before = (source.id, source.label, list(source.parents), int(source.lineage_version))
    base = source.id
    a_id = _child_id(units, f"{base}_a")
    b_id = _child_id(units, f"{base}_b")
    a = program.place(a_id, f"{source.label} A", words=f"split {source.id}", parents=[source.id], origin="split")
    b = program.place(b_id, f"{source.label} B", words=f"split {source.id}", parents=[source.id], origin="split")
    src = units[before[0]]
    if (src.id, src.label, list(src.parents), int(src.lineage_version)) != before:
        return {"ok": False, "error": "source_mutated", "created": [a.id, b.id]}
    return {
        "ok": True,
        "source": source.id,
        "created": [a.id, b.id],
        "origin": "split",
        "lineage_version": int(a.lineage_version),
        "expected_version": int(before[3]) + 1,
    }
