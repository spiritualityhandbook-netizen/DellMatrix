#!/usr/bin/env python3
"""Deterministic Core II control predicates and frames. No eval. No threads."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

DEFAULT_BOUND = 8  # legacy constant; NOT a loop default (DD-44)
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


def bound_detail(st: Any) -> Dict[str, Any]:
    """DD-44: resolve the stored loop bound HONESTLY.

    Returns {status, value, error, domain, raw} where status is
    "specified" (a number the user stated, or the word max =
    the stated maximum), "unspecified" (no Limit was ever
    stated — the loop must ASK, never silently pick a number),
    or "invalid" (a stored value that is not a lawful bound).
    This replaces bound_of, whose contract returned 8 for
    empty, "max", AND invalid input alike — the silent-8
    defect. No accessor may hand back an unstated default."""
    from .predicate import MAX_BOUND, validate_bound
    raw = str(getattr(st, "limit", "") or "").strip()
    if not raw:
        return {"status": "unspecified", "value": None,
                "error": "", "domain": "loop", "raw": raw}
    if raw.lower() == "max":
        return {"status": "specified", "value": MAX_BOUND,
                "error": "", "domain": "loop", "raw": raw}
    ok, n, _err = validate_bound(raw)
    if ok:
        return {"status": "specified", "value": n,
                "error": "", "domain": "loop", "raw": raw}
    return {"status": "invalid", "value": None,
            "error": "invalid_limit", "domain": "loop", "raw": raw}


def bound_display(st: Any) -> str:
    """The bound as receipts may show it: the stated number,
    or the honest word for its absence — never a phantom 8."""
    d = bound_detail(st)
    return str(d["value"]) if d["status"] == "specified" else d["status"]


def eval_condition_detail(st: Any, program: Any, expr: str) -> Dict[str, Any]:
    """DD-42: the full verdict record behind eval_condition.

    The literal layer maps to matched True/False with no
    error. Everything else is eval_predicate's dict, whose
    "error" (e.g. condition_unparseable) the verdict surfaces
    (Assert/Guard/Branch) must surface as a refusal instead
    of stamping a verdict on a bool that hid it."""
    raw = (expr or "").strip()
    e = raw.lower()
    if e in ("", "pass", "true", "allow", "ok", "yes"):
        return {"predicate": "literal", "matched": True, "error": ""}
    if e in ("fail", "false", "block", "deny", "no"):
        return {"predicate": "literal", "matched": False, "error": ""}
    from .predicate import eval_predicate
    return eval_predicate(st, program, raw)


def eval_condition(st: Any, program: Any, expr: str) -> bool:
    return bool(eval_condition_detail(st, program, expr).get("matched"))


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
