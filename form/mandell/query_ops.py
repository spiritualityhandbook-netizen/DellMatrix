#!/usr/bin/env python3
"""51-59 and 67-79 query/reasoning handlers. Shared predicate engine."""
from __future__ import annotations

from typing import Any, List, Tuple

from .predicate import eval_predicate, result_cell, validate_bound

QUERY_DELLS = {51, 52, 54, 55, 56, 57, 58, 59, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79}


def apply_query(n: int, st: Any, program: Any, lab: str, term: str, messages: List[str], ids_fn, pred_fn, shot_fn) -> Tuple[bool, str]:
    ok, err = True, ""
    if n == 51:
        ids = ids_fn(program)
        st.selected = list(ids) if not lab else [i for i in ids if pred_fn(lab, i)]
        st.last_result = result_cell(value=list(st.selected), matched=bool(st.selected), count=len(st.selected), source="select", predicate=lab or "*", trace="51")
        messages.append(f"Select scope={st.scope} n={len(st.selected)}")
    elif n == 52:
        before = list(st.selected)
        st.selected = [i for i in before if pred_fn(lab, i)] if lab else list(before)
        st.last_result = result_cell(value=list(st.selected), matched=bool(st.selected), count=len(st.selected), source="filter", predicate=lab or "*", trace="52")
        messages.append(f"Filter {len(before)}->{len(st.selected)} cond={lab or '*'}")
    elif n == 54:
        ids = list(st.selected)
        hits = [i for i in ids if pred_fn(lab, i)] if lab else list(ids)
        st.last_result = result_cell(value=hits, matched=hits, count=len(hits), source="query", predicate=lab or "*", confidence=1.0 if hits else 0.0, trace="54")
        messages.append(f"Query scope={st.scope} hits={len(hits)} q={lab or '*'}")
    elif n == 55:
        key, _, val = lab.partition("=")
        key = (key or "value").strip()
        shot_fn()
        st.store[key] = val.strip() if val.strip() else ("" if "=" in lab else "1")
        messages.append(f"Set {key}={st.store[key]}")
    elif n == 56:
        key = lab or (list(st.store)[-1] if st.store else "")
        if key not in st.store:
            st.last_result = result_cell(value=None, matched=False, source="get", predicate=key, error="missing", trace="56")
            messages.append(f"Get {key}=MISSING")
        else:
            val = st.store[key]
            status = "empty" if val == "" else "ok"
            st.last_result = result_cell(value=val, matched=status == "ok", source="get", predicate=key, error=status if status == "empty" else "", trace="56")
            messages.append(f"Get {key}={val!r} status={status}")
    elif n == 57:
        head = lab.lower().split(":")[0].split(" ")[0]
        expr = lab if head in ("eq", "ne", "lt", "lte", "gt", "gte", "contains", "starts", "ends") else ("eq:" + " ".join([p for p in lab.replace(",", " ").split() if p][:2]))
        cmpd = eval_predicate(st, program, expr)
        st.last_result = result_cell(value=cmpd.get("matched"), matched=bool(cmpd.get("matched")), source="compare", predicate=cmpd.get("predicate") or "eq", error=cmpd.get("error") or "", trace="57")
        st.last_result["mode"] = cmpd.get("mode") or ""
        if cmpd.get("error") == "type_mismatch":
            ok, err = False, "type_mismatch"
        messages.append(f"Compare {expr} matched={cmpd.get('matched')} mode={cmpd.get('mode')} err={cmpd.get('error')}")
    elif n == 58:
        pat = lab.lower()
        ids = list(st.selected)
        st.selected = [i for i in ids if pat in str(i).lower()] if pat else list(ids)
        st.last_result = result_cell(value=list(st.selected), matched=list(st.selected), count=len(st.selected), source="match", predicate=pat or "*", trace="58")
        messages.append(f"Match pattern={pat or '*'} hits={len(st.selected)}")
    elif n == 59:
        dest = lab or "primary"
        st.route = dest
        st.last_result = result_cell(value=dest, matched=True, source="route", predicate=dest, trace="59")
        messages.append(f"Route -> {st.route}")
    elif n == 67:
        ids = list(st.selected)
        hit = any(pred_fn(lab, i) for i in ids) if ids else False
        st.last_result = result_cell(value=hit, matched=hit, count=len(ids), source="any", predicate=lab or "*", trace="67")
        messages.append(f"Any {hit} n={len(ids)}")
    elif n == 68:
        ids = list(st.selected)
        hit = all(pred_fn(lab, i) for i in ids) if ids else True
        st.last_result = result_cell(value=hit, matched=hit, count=len(ids), source="all", predicate=lab or "*", trace="68")
        messages.append(f"All {hit} n={len(ids)}")
    elif n == 69:
        ids = list(st.selected)
        hit = not any(pred_fn(lab, i) for i in ids)
        st.last_result = result_cell(value=hit, matched=hit, count=len(ids), source="none", predicate=lab or "*", trace="69")
        messages.append(f"None {hit} n={len(ids)}")
    elif n == 70:
        ids = list(st.selected)
        st.last_result = result_cell(value=len(ids), matched=True, count=len(ids), source="count", predicate="count", trace="70")
        messages.append(f"Count {len(ids)}")
    elif n == 71:
        kind = lab or "count"
        unit = "count"
        if ":" in kind:
            unit, _, kind = kind.partition(":")
            unit, kind = unit.strip() or "count", kind.strip() or "selected"
        val = float(len(st.selected))
        st.last_result = result_cell(value=val, matched=True, count=len(st.selected), source="measure", predicate=kind, trace="71")
        st.last_result["unit"] = unit
        st.last_result["measure_kind"] = kind
        messages.append(f"Measure {kind}={val} unit={unit}")
    elif n == 72:
        vok, bound, verr = validate_bound(lab or "max")
        if not vok:
            ok, err = False, verr
            st.last_result = result_cell(value=None, matched=False, source="limit", error=verr, trace="72")
            messages.append(f"Limit invalid {lab!r}")
        else:
            st.limit = str(bound)
            st.last_result = result_cell(value=bound, matched=True, source="limit", predicate="bound", trace="72")
            messages.append(f"Limit {st.limit}")
    elif n == 73:
        expr = lab if lab else "gte:count 0"
        head = lab.lower().split(":")[0] if lab else ""
        if lab and head not in ("eq", "ne", "lt", "lte", "gt", "gte", "threshold"):
            parts = [p for p in lab.replace(",", " ").replace(":", " ").split() if p]
            expr = f"gte:{parts[0]} {parts[1]}" if len(parts) >= 2 else (f"gte:count {parts[0]}" if parts else expr)
        if expr.lower().startswith("threshold"):
            expr = "gte:" + expr.split(":", 1)[-1]
        cmpd = eval_predicate(st, program, expr)
        hit = bool(cmpd.get("matched"))
        st.last_result = result_cell(value=hit, matched=hit, source="threshold", predicate=cmpd.get("predicate") or "gte", error=cmpd.get("error") or "", trace="73")
        messages.append(f"Threshold {expr} matched={hit}")
    elif n == 74:
        key, _, val = lab.partition("=")
        key = (key or "target").strip()
        try:
            w = float(val) if val else 1.0
        except ValueError:
            w = float("nan")
        if w != w or w in (float("inf"), float("-inf")):
            ok, err = False, "nonfinite_weight"
            st.last_result = result_cell(value=None, matched=False, source="weight", error=err, trace="74")
            messages.append(f"Weight reject {key}={val!r}")
        else:
            st.weights[key] = w
            st.last_result = result_cell(value=w, matched=True, source="weight", predicate=key, trace="74")
            messages.append(f"Weight {key}={w}")
    elif n == 75:
        ssum = sum(st.weights.values())
        if not st.weights or ssum == 0:
            st.last_result = result_cell(value=dict(st.weights), matched=False, count=len(st.weights), source="normalize", error="zero_set", trace="75")
            messages.append("Normalize zero_set")
        else:
            st.weights = {k: v / ssum for k, v in st.weights.items()}
            st.last_result = result_cell(value=dict(st.weights), matched=True, count=len(st.weights), source="normalize", trace="75")
            messages.append(f"Normalize n={len(st.weights)} sum={sum(st.weights.values()):.6f}")
    elif n == 76:
        from .manifest_resolver import resolve_manifest
        try:
            num = int(lab.split()[0]) if lab[:1].isdigit() else n
        except Exception:
            num = n
        res = resolve_manifest(num, term, lab)
        conf = max(0.0, min(1.0, float(getattr(res, "confidence", 0.0) or 0.0)))
        st.last_result = result_cell(value=getattr(res, "resolved", term), matched=True, source="resolve", predicate=str(getattr(res, "requested", term)), confidence=conf, trace="76")
        messages.append(f"Resolve dell={res.dell} req={res.requested}->{res.resolved} conf={conf:.2f} {res.reason}")
    elif n == 77:
        evidence = lab or "evidence"
        prior = dict(st.last_result or {})
        has_ev = bool(evidence) and evidence != "evidence"
        conf = max(0.0, min(1.0, float(prior.get("confidence") or (0.6 if has_ev else 0.0))))
        st.last_result = result_cell(value=evidence, matched=False, source="infer", predicate="projected", confidence=conf, trace="77")
        st.last_result.update({"evidence": evidence if has_ev else prior.get("value") or evidence, "conclusion": evidence, "projected": True, "fact": False})
        messages.append(f"Infer {evidence} PROJECTED_NOT_FACT")
    elif n == 78:
        ok, err = _relation(st, "causes", lab, "cause", "78", messages, "Cause")
    elif n == 79:
        ok, err = _relation(st, "deps", lab, "depend", "79", messages, "Depend")
    return ok, err


def _relation(st, field, lab, source, trace, messages, title) -> Tuple[bool, str]:
    if ">" not in lab:
        st.last_result = result_cell(error="malformed_relation", source=source, trace=trace)
        messages.append(f"{title} malformed")
        return False, "malformed_relation"
    a, _, b = lab.partition(">")
    a, b = a.strip(), b.strip()
    if not a or not b:
        st.last_result = result_cell(error="malformed_relation", source=source, trace=trace)
        messages.append(f"{title} malformed")
        return False, "malformed_relation"
    bag = getattr(st, field)
    if a == b:
        st.last_result = result_cell(error="self_relation", source=source, trace=trace)
        messages.append(f"{title} self rejected")
        return False, "self_relation"
    if (a, b) in [(str(x[0]), str(x[1])) for x in bag]:
        st.last_result = result_cell(value=(a, b), matched=False, source=source, error="duplicate_relation", trace=trace)
        messages.append(f"{title} duplicate {a}->{b}")
        return True, ""
    bag.append((a, b))
    st.last_result = result_cell(value=(a, b), matched=True, source=source, trace=trace)
    messages.append(f"{title} {a}->{b}" if source == "cause" else f"{title} {a} requires {b}")
    return True, ""
