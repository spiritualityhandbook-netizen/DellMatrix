#!/usr/bin/env python3
"""Shared predicate and value engine. No eval. Used by query and control."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

PREDICATES = (
    "eq", "ne", "lt", "lte", "gt", "gte",
    "contains", "starts", "ends",
    "exists", "empty", "truthy", "falsey",
    "any", "all", "none",
)

MAX_BOUND = 64
DEFAULT_BOUND = 8


def classify_value(value: Any) -> Tuple[str, Any]:
    if isinstance(value, bool):
        return "boolean", value
    if isinstance(value, int) and not isinstance(value, bool):
        return "number", float(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return "literal", str(value)
        return "number", value
    raw = "" if value is None else str(value)
    low = raw.strip().lower()
    if low in ("true", "false"):
        return "boolean", low == "true"
    try:
        if raw.strip() != "":
            num = float(raw.strip())
            if num == num and num not in (float("inf"), float("-inf")):
                return "number", num
    except (TypeError, ValueError):
        pass
    return "literal", raw


def resolve_value(st: Any, program: Any, token: str) -> Dict[str, Any]:
    raw = (token or "").strip()
    low = raw.lower()
    if raw == "":
        return {"kind": "literal", "type": "literal", "value": "", "source": "literal"}
    if low in ("true", "false"):
        return {"kind": "boolean", "type": "boolean", "value": low == "true", "source": "literal"}
    if low in ("count", "count_ref", "selected_count"):
        n = len(getattr(st, "selected", None) or [])
        return {"kind": "count_ref", "type": "number", "value": float(n), "source": "count_ref"}
    if low in ("context", "context_ref"):
        return {"kind": "context_ref", "type": "literal", "value": getattr(st, "context", "") or "", "source": "context_ref"}
    if low in ("selected", "selected_ref"):
        return {"kind": "selected_ref", "type": "literal", "value": list(getattr(st, "selected", None) or []), "source": "selected_ref"}
    if low in ("last_result", "result", "threshold"):
        lr = getattr(st, "last_result", None) or {}
        return {"kind": "last_result", "type": "boolean", "value": bool(lr.get("matched")), "source": "last_result"}
    if low.startswith("store:") or low.startswith("store_"):
        key = raw.split(":", 1)[1] if low.startswith("store:") else raw.split("_", 1)[1]
        store = getattr(st, "store", {}) or {}
        if key not in store:
            return {"kind": "store_ref", "type": "missing", "value": None, "source": "store_ref", "key": key}
        typ, val = classify_value(store[key])
        return {"kind": "store_ref", "type": typ, "value": val, "source": "store_ref", "key": key}
    try:
        num = float(raw)
        if num == num and num not in (float("inf"), float("-inf")):
            return {"kind": "number", "type": "number", "value": num, "source": "literal"}
    except (TypeError, ValueError):
        pass
    store = getattr(st, "store", {}) or {}
    if raw in store:
        typ, val = classify_value(store[raw])
        return {"kind": "store_ref", "type": typ, "value": val, "source": "store_ref", "key": raw}
    weights = getattr(st, "weights", {}) or {}
    if raw in weights:
        return {"kind": "store_ref", "type": "number", "value": float(weights[raw]), "source": "store_ref", "key": raw}
    return {"kind": "literal", "type": "literal", "value": raw, "source": "literal"}


def _cmp_typed(left: Dict[str, Any], right: Dict[str, Any], op: str) -> Dict[str, Any]:
    out = {
        "predicate": op,
        "matched": False,
        "left": left.get("value"),
        "right": right.get("value"),
        "left_type": left.get("type"),
        "right_type": right.get("type"),
        "mode": "",
        "error": "",
    }
    lt, rt = left.get("type"), right.get("type")
    if lt == "missing" or rt == "missing":
        out["error"] = "missing"
        out["mode"] = "missing"
        if op == "exists":
            out["matched"] = False
        return out
    if op in ("lt", "lte", "gt", "gte") and not (lt == "number" and rt == "number"):
        out["error"] = "type_mismatch"
        out["mode"] = "type_mismatch"
        return out
    if op in ("eq", "ne"):
        if lt == rt == "number":
            out["mode"] = "number"
            same = left["value"] == right["value"]
        elif lt == rt == "boolean":
            out["mode"] = "boolean"
            same = bool(left["value"]) is bool(right["value"])
        elif lt == rt:
            out["mode"] = "string" if lt == "literal" else lt
            same = left["value"] == right["value"]
        else:
            out["error"] = "type_mismatch"
            out["mode"] = "type_mismatch"
            return out
        out["matched"] = same if op == "eq" else (not same)
        return out
    if op in ("lt", "lte", "gt", "gte"):
        a, b = float(left["value"]), float(right["value"])
        out["mode"] = "number"
        out["matched"] = {"lt": a < b, "lte": a <= b, "gt": a > b, "gte": a >= b}[op]
        return out
    ls = "" if left.get("value") is None else str(left.get("value"))
    rs = "" if right.get("value") is None else str(right.get("value"))
    out["mode"] = "string"
    if op == "contains":
        out["matched"] = rs.lower() in ls.lower()
    elif op == "starts":
        out["matched"] = ls.lower().startswith(rs.lower())
    elif op == "ends":
        out["matched"] = ls.lower().endswith(rs.lower())
    return out


def eval_predicate(st: Any, program: Any, expr: str) -> Dict[str, Any]:
    raw = (expr or "").strip()
    low = raw.lower()
    result = {
        "predicate": "",
        "matched": False,
        "value": None,
        "count": 0,
        "source": "predicate",
        "confidence": 1.0,
        "trace": raw,
        "error": "",
    }
    if not raw:
        result["predicate"] = "empty"
        result["matched"] = True
        return result
    name = ""
    rest = raw
    for pred in sorted(PREDICATES, key=len, reverse=True):
        if low == pred or low.startswith(pred + ":") or low.startswith(pred + " "):
            name = pred
            rest = raw[len(pred):].lstrip(": ").strip()
            break
    if not name:
        result["predicate"] = "truthy"
        token = resolve_value(st, program, raw)
        result["matched"] = _truthy(token)
        result["value"] = token.get("value")
        return result
    result["predicate"] = name
    parts = [p for p in rest.replace(",", " ").split() if p]
    if name in ("any", "all", "none"):
        ids = list(getattr(st, "selected", None) or [])
        needle = rest.lower()
        def _hit(i):
            u = str(i).lower()
            return True if not needle else needle in u or u.startswith(needle.replace(" ", "_"))
        if name == "any":
            result["matched"] = any(_hit(i) for i in ids) if ids else False
        elif name == "all":
            result["matched"] = all(_hit(i) for i in ids) if ids else True
        else:
            result["matched"] = not any(_hit(i) for i in ids)
        result["value"] = list(ids)
        result["count"] = len(ids)
        return result
    if name in ("exists", "empty", "truthy", "falsey"):
        token = resolve_value(st, program, parts[0] if parts else rest)
        if name == "exists":
            result["matched"] = token.get("type") != "missing"
        elif name == "empty":
            val = token.get("value")
            result["matched"] = val in ("", None, [], {})
        elif name == "truthy":
            result["matched"] = _truthy(token)
        else:
            result["matched"] = not _truthy(token)
        result["value"] = token.get("value")
        result["error"] = "missing" if token.get("type") == "missing" and name != "exists" else ""
        return result
    left_tok = parts[0] if parts else ""
    right_tok = parts[1] if len(parts) > 1 else ""
    left = resolve_value(st, program, left_tok)
    right = resolve_value(st, program, right_tok)
    cmpd = _cmp_typed(left, right, name)
    result.update(cmpd)
    result["value"] = cmpd["matched"]
    return result


def _truthy(token: Dict[str, Any]) -> bool:
    if token.get("type") == "missing":
        return False
    val = token.get("value")
    if token.get("type") == "boolean":
        return bool(val)
    if token.get("type") == "number":
        return float(val) != 0.0
    if isinstance(val, (list, dict)):
        return bool(val)
    text = "" if val is None else str(val).strip().lower()
    return text not in ("", "0", "false", "off", "no")


def validate_bound(raw: Any) -> Tuple[bool, int, str]:
    text = str(raw or "").strip()
    if text == "" or text.lower() == "max":
        return True, DEFAULT_BOUND, ""
    try:
        n = int(text)
    except (TypeError, ValueError):
        try:
            n = int(float(text))
        except (TypeError, ValueError):
            return False, DEFAULT_BOUND, "invalid_limit"
    if n < 0 or n > MAX_BOUND:
        return False, DEFAULT_BOUND, "invalid_limit"
    return True, n, ""


def result_cell(**kwargs: Any) -> Dict[str, Any]:
    cell = {
        "value": None,
        "matched": False,
        "count": 0,
        "source": "",
        "predicate": "",
        "confidence": 1.0,
        "trace": "",
        "error": "",
    }
    cell.update(kwargs)
    conf = cell.get("confidence", 1.0)
    try:
        conf = float(conf)
    except (TypeError, ValueError):
        conf = 0.0
    if conf != conf:
        conf = 0.0
    cell["confidence"] = max(0.0, min(1.0, conf))
    return cell
