#!/usr/bin/env python3
"""Deterministic Core II control predicates and frames. No eval. No threads."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

DEFAULT_BOUND = 8
MAX_DEPTH = 4
CONTROL_HEADS = {60, 62, 63, 64, 65, 66}


@dataclass
class ControlFrame:
    id: str = "f0"
    kind: str = "sequence"
    condition: str = ""
    body: List[int] = field(default_factory=list)
    status: str = "pending"
    iterations: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""
    policy: str = "all"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "condition": self.condition,
            "status": self.status,
            "iterations": self.iterations,
            "results": list(self.results),
            "error": self.error,
            "policy": self.policy,
            "body": list(self.body),
        }


def bound_of(st: Any) -> int:
    from .predicate import validate_bound
    raw = getattr(st, "limit", "") or ""
    ok, n, _err = validate_bound(raw)
    return n if ok else DEFAULT_BOUND


def _as_num(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _lookup(st: Any, token: str) -> Any:
    if st is None:
        return token
    if token in st.store:
        return st.store[token]
    if token in st.weights:
        return st.weights[token]
    return token


def eval_condition(st: Any, program: Any, expr: str) -> bool:
    raw = (expr or "").strip()
    e = raw.lower()
    if e in ("", "pass", "true", "allow", "ok", "yes"):
        return True
    if e in ("fail", "false", "block", "deny", "no"):
        return False
    from .predicate import PREDICATES, eval_predicate
    if e.split(":")[0].split(" ")[0] in PREDICATES:
        return bool(eval_predicate(st, program, raw).get("matched"))
    if e.startswith("store:") or e.startswith("store_"):
        key = raw.split(":", 1)[1] if e.startswith("store:") else raw.split("_", 1)[1]
        val = st.store.get(key) if st is not None else None
        return bool(val) and str(val).lower() not in ("0", "false", "off", "")
    for op in ("lte", "gte", "eq", "ne", "lt", "gt"):
        prefix = op + ":"
        alt = op + " "
        if e.startswith(prefix) or e.startswith(alt):
            rest = raw[len(op):].lstrip(": ")
            parts = [p for p in rest.replace(":", " ").split() if p]
            if len(parts) < 2:
                return False
            left, right = _lookup(st, parts[0]), _lookup(st, parts[1])
            return _compare(left, right, op)
    if e.startswith("threshold:"):
        rest = raw.split(":", 1)[1]
        key, _, num = rest.partition(":")
        thr = _as_num(num) or 0.0
        val = _as_num(_lookup(st, key.strip())) or 0.0
        return val >= thr
    if e.startswith("any"):
        from .core_ii_exec import _pred
        ids = list(st.selected or []) if st is not None else []
        needle = raw[3:].lstrip(": ").strip()
        return any(_pred(needle, i) for i in ids) if ids else False
    if e.startswith("all"):
        from .core_ii_exec import _pred
        ids = list(st.selected or []) if st is not None else []
        needle = raw[3:].lstrip(": ").strip()
        return all(_pred(needle, i) for i in ids) if ids else True
    if e.startswith("none"):
        from .core_ii_exec import _pred
        ids = list(st.selected or []) if st is not None else []
        needle = raw[4:].lstrip(": ").strip()
        return not any(_pred(needle, i) for i in ids)
    return False


def _compare(left: Any, right: Any, op: str) -> bool:
    ln, rn = _as_num(left), _as_num(right)
    if ln is not None and rn is not None:
        a, b = ln, rn
    else:
        a, b = str(left), str(right)
    if op == "eq":
        return a == b
    if op == "ne":
        return a != b
    if op == "lt":
        return a < b
    if op == "lte":
        return a <= b
    if op == "gt":
        return a > b
    if op == "gte":
        return a >= b
    return False


def find_join(atoms: List[Any], start: int, end: Optional[int] = None) -> int:
    depth = 0
    last = len(atoms) if end is None else end
    for i in range(start, last):
        n = int(getattr(atoms[i], "dell", -1))
        if n in CONTROL_HEADS:
            depth += 1
        elif n == 61:
            if depth == 0:
                return i
            depth -= 1
    return last


def find_else(atoms: List[Any], start: int, end: int) -> tuple:
    depth = 0
    found = None
    count = 0
    for i in range(start, end):
        n = int(getattr(atoms[i], "dell", -1))
        if n in CONTROL_HEADS:
            depth += 1
        elif n == 61:
            depth = max(0, depth - 1)
        elif n == 59 and depth == 0:
            count += 1
            if found is None:
                found = i
    if count > 1:
        return ("multi", found if found is not None else end)
    if found is None:
        return ("none", end)
    return ("one", found)


FLOW_CONTRACT = {
    ">": "FlowTo",
    ">>": "FlowThru",
    ">>>": "FlowOver",
    ":": "FlowBy",
    "::": "DeepFlowBy",
    ":>": "FlowTowards",
    "<:": "FlowFrom",
    "<:>": "DynamicFlow",
    "<<[Delta]": "DeltaFlow",
}
