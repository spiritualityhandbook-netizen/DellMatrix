#!/usr/bin/env python3
"""Core II durable persist helpers. v7 document stays version 7."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

CORE_II_STATE_VERSION = 1

CORE_II_DURABLE = (
    "scope",
    "selected",
    "store",
    "groups",
    "defs",
    "aliases",
    "compositions",
    "weights",
    "context",
    "route",
    "refs",
    "causes",
    "deps",
    "last_assert",
    "last_guard",
)


def _json_safe(value: Any, depth: int = 0) -> Any:
    if depth > 8:
        return None
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return None
        return value
    if isinstance(value, tuple):
        return [_json_safe(v, depth + 1) for v in value]
    if isinstance(value, list):
        return [_json_safe(v, depth + 1) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v, depth + 1) for k, v in value.items()}
    return str(value)[:240]


def _pair_list(value: Any) -> List[List[str]]:
    out: List[List[str]] = []
    if not isinstance(value, (list, tuple)):
        return out
    for item in value:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            out.append([str(item[0]), str(item[1])])
        elif isinstance(item, str) and ">" in item:
            a, _, b = item.partition(">")
            out.append([a.strip(), b.strip()])
    return out


def serialize_core_ii(program: Any) -> Dict[str, Any]:
    from form.mandell.core_ii_exec import CoreIIState

    st = getattr(program, "core_ii", None)
    if not isinstance(st, CoreIIState):
        return {"version": CORE_II_STATE_VERSION, "present": False}
    return {
        "version": CORE_II_STATE_VERSION,
        "present": True,
        "scope": str(st.scope or "plane"),
        "selected": [str(x) for x in list(st.selected or [])],
        "store": _json_safe({k: v for k, v in dict(st.store or {}).items() if k != "_last_result"}),
        "groups": {str(k): [str(x) for x in list(v or [])] for k, v in dict(st.groups or {}).items()},
        "defs": {str(k): str(v) for k, v in dict(st.defs or {}).items()},
        "aliases": {str(k): str(v) for k, v in dict(st.aliases or {}).items()},
        "compositions": {str(k): str(v) for k, v in dict(st.compositions or {}).items()},
        "weights": {
            str(k): float(v)
            for k, v in dict(st.weights or {}).items()
            if isinstance(v, (int, float)) and v == v
        },
        "context": str(st.context or ""),
        "route": str(st.route or "primary"),
        "refs": {str(k): str(v) for k, v in dict(st.refs or {}).items()},
        "causes": _pair_list(st.causes),
        "deps": _pair_list(st.deps),
        "last_assert": str(st.last_assert or ""),
        "last_guard": str(st.last_guard or "ALLOW"),
    }


def restore_core_ii(program: Any, data: Optional[Dict[str, Any]] = None) -> None:
    from form.mandell.core_ii_exec import CoreIIState, attach

    attach(program)
    raw = None
    if isinstance(data, dict) and "core_ii" in data:
        raw = data.get("core_ii")
    elif isinstance(data, dict) and data.get("version") == CORE_II_STATE_VERSION and "present" in data:
        raw = data
    if not isinstance(raw, dict) or raw.get("present") is False:
        program.core_ii = CoreIIState()
        return
    st = program.core_ii
    try:
        if raw.get("scope") is not None:
            st.scope = str(raw.get("scope") or "plane")
        if isinstance(raw.get("selected"), list):
            st.selected = [str(x) for x in raw["selected"]]
        if isinstance(raw.get("store"), dict):
            st.store = _json_safe(raw["store"])
        if isinstance(raw.get("groups"), dict):
            st.groups = {
                str(k): [str(x) for x in v] if isinstance(v, list) else []
                for k, v in raw["groups"].items()
            }
        if isinstance(raw.get("defs"), dict):
            st.defs = {str(k): str(v) for k, v in raw["defs"].items()}
        if isinstance(raw.get("aliases"), dict):
            st.aliases = {str(k): str(v) for k, v in raw["aliases"].items()}
        if isinstance(raw.get("compositions"), dict):
            st.compositions = {str(k): str(v) for k, v in raw["compositions"].items()}
        if isinstance(raw.get("weights"), dict):
            weights: Dict[str, float] = {}
            for k, v in raw["weights"].items():
                try:
                    weights[str(k)] = float(v)
                except (TypeError, ValueError):
                    continue
            st.weights = weights
        if raw.get("context") is not None:
            st.context = str(raw.get("context") or "")
        if raw.get("route") is not None:
            st.route = str(raw.get("route") or "primary")
        if isinstance(raw.get("refs"), dict):
            st.refs = {str(k): str(v) for k, v in raw["refs"].items()}
        if raw.get("causes") is not None:
            st.causes = [tuple(p) for p in _pair_list(raw.get("causes"))]
        if raw.get("deps") is not None:
            st.deps = [tuple(p) for p in _pair_list(raw.get("deps"))]
        if raw.get("last_assert") is not None:
            st.last_assert = str(raw.get("last_assert") or "")
        if raw.get("last_guard") is not None:
            st.last_guard = str(raw.get("last_guard") or "ALLOW")
    except Exception:
        program.core_ii = CoreIIState()
