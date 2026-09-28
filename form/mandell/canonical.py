#!/usr/bin/env python3
"""Canonical Mandell graph, lossless directive codec, executor cheat."""
from __future__ import annotations

from typing import Any, Dict, List
import hashlib
import json
import os
import re
import tempfile

from .seed import CELLS, parse_seed, expand_cell

_ATOM = re.compile(r"(\d{1,3})\[([^\]]*)\]")


def graph_hash(graph: Dict[str, Any]) -> str:
    payload = {"nodes": [(n["dell"], n["manifest"], n.get("payload") or "") for n in graph.get("nodes") or []], "edges": [(e.get("from"), e.get("to"), e.get("flow")) for e in graph.get("edges") or []]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def seed_graph(text: str, cell_origin: str = "") -> Dict[str, Any]:
    s = parse_seed(text)
    nodes = []
    edges = []
    if not s.ok:
        return {"ok": False, "error": s.error, "nodes": [], "edges": [], "semantic_hash": ""}
    for i, a in enumerate(s.atoms):
        nodes.append({"id": f"n{i}", "dell": a.dell, "manifest": a.term, "payload": s.label if i == 0 else "", "source_span": [0, len(text)], "cell_origin": cell_origin, "provenance": a.origin})
        if i:
            edges.append({"from": f"n{i-1}", "to": f"n{i}", "flow": s.flows[i-1] if i-1 < len(s.flows) else ">", "position": i-1})
    g = {"ok": True, "nodes": nodes, "edges": edges, "label": s.label, "cells": dict(CELLS)}
    g["semantic_hash"] = graph_hash(g)
    return g


def cell_graph(name: str) -> Dict[str, Any]:
    s = expand_cell(name)
    if not s.ok:
        return {"ok": False, "error": s.error, "nodes": [], "edges": []}
    return seed_graph(s.as_mandel() if s.as_mandel() else s.raw, cell_origin=name)


def parse_directive_v2(text: str) -> Dict[str, Any]:
    raw = text or ""
    if not raw.strip():
        return {"ok": False, "error": "empty_directive", "nodes": [], "comments": []}
    nodes = []
    comments = []
    errors = []
    pos = 0
    for li, line in enumerate(raw.splitlines(keepends=True)):
        start, end = pos, pos + len(line)
        pos = end
        body = line.strip()
        if not body:
            continue
        if body.startswith("/*") or body.startswith("*") or body.startswith("*/"):
            comments.append({"text": body, "span": [start, end], "line": li})
            continue
        if body.startswith("::") and nodes:
            extra = body[2:].strip()
            nodes[-1]["payload"] = ((nodes[-1].get("payload") or "") + ("\n" if nodes[-1].get("payload") else "") + extra).strip()
            nodes[-1]["source_span"][1] = end
            continue
        if body in {">", ">>", ">>>", ":", ":>", "<:", "<:>", "<<[Delta]"}:
            if nodes:
                nodes[-1].setdefault("out_flow", body)
            continue
        matches = list(_ATOM.finditer(body))
        if not matches:
            errors.append({"text": body, "span": [start, end], "line": li})
            continue
        for m in matches:
            tail = body[m.end():].strip()
            payload = tail[2:].strip() if tail.startswith("::") else tail.lstrip("> ").strip()
            nodes.append({"id": f"d{len(nodes)}", "dell": int(m.group(1)), "manifest": m.group(2), "payload": payload, "source_span": [start + m.start(), start + m.end()], "line": li, "cell_origin": "", "provenance": "directive"})
    ok = bool(nodes) and not errors
    g = {"ok": ok, "error": "" if ok else ("unparseable_noncomment" if errors else "no_nodes"), "nodes": nodes, "edges": [{"from": nodes[i]["id"], "to": nodes[i+1]["id"], "flow": ">", "position": i} for i in range(len(nodes)-1)], "comments": comments, "errors": errors, "source": raw}
    g["semantic_hash"] = graph_hash(g)
    g["locks"] = [n for n in nodes if n["dell"] == 23]
    g["guards"] = [n for n in nodes if n["dell"] == 92]
    g["tests"] = [n for n in nodes if n["dell"] == 12]
    g["assertions"] = [n for n in nodes if n["dell"] == 91]
    g["exit"] = [n for n in nodes if n["dell"] == 20]
    g["flows"] = [n.get("out_flow") or ">" for n in nodes[:-1]]
    return g


def compress_graph(g: Dict[str, Any]) -> Dict[str, Any]:
    seen = set()
    nodes = []
    for n in g.get("nodes") or []:
        key = (n["dell"], n["manifest"], n.get("payload") or "")
        if key in seen and n["dell"] in (80, 97, 90):
            continue
        seen.add(key)
        nodes.append(n)
    out = dict(g)
    out["nodes"] = nodes
    out["source_nodes"] = len(g.get("nodes") or [])
    out["compressed_nodes"] = len(nodes)
    out["semantic_hash"] = graph_hash(out)
    out["ratio"] = 0 if not g.get("nodes") else round(len(nodes) / max(1, len(g["nodes"])), 4)
    return out


def expand_graph(g: Dict[str, Any]) -> Dict[str, Any]:
    lines = []
    for n in g.get("nodes") or []:
        line = f"{n['dell']:02d}[{n['manifest']}]"
        if n.get("payload"):
            line += f" :: {n['payload']}"
        lines.append(line)
    return parse_directive_v2("\n".join(lines))


def freeze_program(program: Any) -> Dict[str, Any]:
    from form.persist import serialize
    d = serialize(program)
    d.pop("saved", None)
    return d


def clone_program(program: Any) -> Any:
    from form.persist import save, load
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        save(program, path)
        return load(getattr(program, "owner", "CHEAT"), path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _units_of(program: Any) -> Dict[str, str]:
    plane = program.cube.session.plane
    return {uid: uid for uid in plane.units if uid != "welcome"}


def cheat_project(program: Any, actions: List[str], temp: str = "hot") -> Dict[str, Any]:
    from form.mandell.executor import execute_seed
    horizon = {"cold": 1, "warm": 2, "hot": 3}.get((temp or "hot").lower(), 3)
    origin = freeze_program(program)
    cur = clone_program(program)
    steps = []
    for i, act in enumerate(actions[:horizon], 1):
        before_units = _units_of(cur)
        out = execute_seed(cur, act)
        after_units = _units_of(cur)
        after_store = dict(getattr(cur.core_ii, "store", {}) or {})
        delta = {"units_added": sorted(set(after_units) - set(before_units)), "units_removed": sorted(set(before_units) - set(after_units)), "store_delta": after_store, "selection_delta": list(getattr(cur.core_ii, "selected", []) or []), "trace": list(out.get("chain_ran") or [])}
        steps.append({"iteration": i, "candidate_action": act, "predicted_delta": delta, "candidate_next_state": {"units": after_units, "store": after_store, "ok": out.get("ok"), "error": out.get("error") or ""}, "assumptions": [f"from_iter:{i-1}"], "uncertainty": round(0.25 * i, 2), "label": "PROJECTED_NOT_FACT", "projected_failure": bool(out.get("error"))})
        if out.get("error") and not out.get("ok"):
            break
    return {"ok": True, "steps": steps, "origin": origin, "origin_unchanged": freeze_program(program) == origin, "label": "PROJECTED_NOT_FACT"}


def measured_route(evidence: Dict[str, Any]) -> Dict[str, Any]:
    contracts = list(evidence.get("contracts") or [])
    covered = [c for c in contracts if c.get("tested")]
    ready = [c for c in contracts if c.get("ready")]
    deps = list(evidence.get("edges") or [])
    downstream = list(evidence.get("downstream") or [])
    touched = list(evidence.get("code_localities") or [])
    locked_touch = int(evidence.get("locked_domains_touched") or 0)
    dependents = int(evidence.get("dependents") or 0)
    factors = {"closures": float(len(ready)), "resonance": float(len(deps)), "reuse": float(len(set(evidence.get("shared") or []))), "future_work_avoided": float(len(downstream)), "verification_confidence": (len(covered) / len(contracts)) if contracts else 0.0, "movement": float(max(1, len(set(touched)))), "rework_risk": float(max(1, dependents)), "scope_interference": float(locked_touch + 1)}
    den = factors["movement"] * factors["rework_risk"] * factors["scope_interference"]
    num = factors["closures"] * factors["resonance"] * factors["reuse"] * factors["future_work_avoided"] * factors["verification_confidence"]
    return {"ok": True, "factors": factors, "value": num / den, "trace": factors}


def rank_evidence(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = []
    for row in rows:
        rv = measured_route(row)
        item = dict(row)
        item["route_value"] = rv["value"]
        item["factors"] = rv["factors"]
        scored.append(item)
    scored.sort(key=lambda r: (-r["route_value"], str(r.get("locality") or "")))
    return scored
