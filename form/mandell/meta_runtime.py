#!/usr/bin/env python3
"""Executable Mandell meta-runtime: cells, directives, cheat, routes, omni."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import copy
import hashlib
import json
import os

from .seed import CELLS, BULLET, MANDELLMOJI, FLOW_OPS, define_cell, parse_seed, expand_cell as seed_expand_cell
from .registry import DELLS
from .floor import FLOOR, assert_floor_intact

CELL_FILE = os.path.join(os.path.dirname(__file__), "..", "state", "mandell_cell_graph.json")
MOJI_REGISTRY = {
    MANDELLMOJI["Chain"]: {"canonical": ">", "category": "flow", "display_only": True},
    MANDELLMOJI["Chainlink"]: {"canonical": BULLET, "category": "set", "display_only": True},
}


def _hash(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def cell_define(name: str, source: str) -> Dict[str, Any]:
    name = str(name)
    if source.startswith("cell:"):
        CELLS[name] = "__cell__:" + source.split(":", 1)[1]
        return {"ok": True, "name": name, "kind": "ref"}
    s = define_cell(name, source)
    return {"ok": s.ok, "error": s.error, "name": name, "kind": "seed"}


def cell_expand(name: str, seen=None, depth: int = 0) -> Dict[str, Any]:
    s = seed_expand_cell(name)
    if not s.ok:
        return {"ok": False, "error": s.error, "atoms": [], "flows": []}
    return {"ok": True, "name": name, "source": CELLS.get(str(name), ""), "atoms": [(a.dell, a.term) for a in s.atoms], "flows": list(s.flows), "semantic_hash": _hash([(a.dell, a.term) for a in s.atoms] + list(s.flows)), "dependencies": []}


def persist_cell_graph(path: Optional[str] = None) -> str:
    target = path or CELL_FILE
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(dict(CELLS), f, indent=2)
    return target


def load_cell_graph(path: Optional[str] = None) -> int:
    target = path or CELL_FILE
    if not os.path.isfile(target):
        return 0
    with open(target, encoding="utf-8") as f:
        data = json.load(f) or {}
    CELLS.clear()
    CELLS.update({str(k): str(v) for k, v in data.items()})
    return len(CELLS)


def parse_directive(text: str) -> Dict[str, Any]:
    from .language import parse_directive as _parse
    return _parse(text)


def compress_directive(ast: Dict[str, Any]) -> Dict[str, Any]:
    if not ast.get("ok"):
        return {"ok": False, "error": ast.get("error"), "nodes": []}
    nodes = []
    seen = set()
    for n in ast["nodes"]:
        key = (n["dell"], n["manifest"], n["payload"])
        if key in seen and n["dell"] in (80, 97):
            continue
        seen.add(key)
        nodes.append(n)
    return {"ok": True, "nodes": nodes, "locks": ast.get("locks") or [], "guards": ast.get("guards") or [], "tests": ast.get("tests") or [], "exit": ast.get("exit") or [], "semantic_hash": _hash([(n["dell"], n["manifest"], n["payload"]) for n in nodes]), "source_nodes": len(ast["nodes"]), "compressed_nodes": len(nodes)}


def expand_directive(ast: Dict[str, Any]) -> Dict[str, Any]:
    return parse_directive("\n".join(f"{n['dell']:02d}[{n['manifest']}] :: {n['payload']}" if n.get("payload") else f"{n['dell']:02d}[{n['manifest']}]" for n in ast.get("nodes") or []))


def directive_delta(base: Dict[str, Any], nxt: Dict[str, Any]) -> Dict[str, Any]:
    b = {(n["dell"], n["manifest"], n["payload"]) for n in base.get("nodes") or []}
    added = [n for n in nxt.get("nodes") or [] if (n["dell"], n["manifest"], n["payload"]) not in b]
    return {"ok": True, "added": added, "head_hash": base.get("semantic_hash"), "next_hash": nxt.get("semantic_hash")}


def moji_expand(text: str) -> str:
    out = text or ""
    for glyph, row in MOJI_REGISTRY.items():
        out = out.replace(glyph, row["canonical"])
    return out


def moji_render(text: str) -> str:
    s = parse_seed(text)
    if not s.ok:
        return text
    out = s.as_mandel()
    if len(s.atoms) > 1 and all(a.dell == s.atoms[0].dell for a in s.atoms):
        out = out.replace(" > ", f" {MANDELLMOJI['Chain']} ")
    return out


def tokenless(text: str) -> Dict[str, Any]:
    s = parse_seed(text)
    if not s.ok:
        return {"ok": False, "error": s.error}
    if len(s.atoms) > 1 and all(a.dell == s.atoms[0].dell for a in s.atoms) and set(s.flows) <= {">", ""}:
        compressed = f"{s.atoms[0].dell:02d}[{BULLET.join(a.term for a in s.atoms)}]"
    else:
        compressed = s.as_mandel()
    c = parse_seed(compressed)
    proof = {"ok": c.ok, "source": text, "compressed": compressed, "source_atoms": [(a.dell, a.term) for a in s.atoms], "compressed_atoms": [(a.dell, a.term) for a in c.atoms], "source_chars": len(text), "compressed_chars": len(compressed), "semantic_hash_before": _hash([(a.dell, a.term) for a in s.atoms]), "semantic_hash_after": _hash([(a.dell, a.term) for a in c.atoms])}
    proof["ratio"] = 0 if not text else round(len(compressed) / max(1, len(text)), 4)
    proof["equivalent"] = proof["semantic_hash_before"] == proof["semantic_hash_after"]
    return proof


def cheat_from_state(state: Dict[str, Any], actions: List[str], temp: str = "hot") -> Dict[str, Any]:
    from form.open import open_program
    from .canonical import cheat_project
    origin = copy.deepcopy(state)
    program = state if hasattr(state, "core_ii") else open_program("CHEAT_SANDBOX")
    res = cheat_project(program, actions, temp)
    steps = []
    for step in res.get("steps") or []:
        nxt = step.get("candidate_next_state") or {}
        steps.append({"iteration": step["iteration"], "candidate_action": step["candidate_action"], "predicted_delta": step.get("predicted_delta"), "candidate_next_state": {"units": nxt.get("units") or {}, "store": nxt.get("store") or {}}, "assumptions": step.get("assumptions"), "uncertainty": step.get("uncertainty"), "label": "PROJECTED_NOT_FACT"})
        if nxt.get("error") and not nxt.get("ok"):
            return {"ok": False, "error": nxt.get("error"), "steps": steps, "origin": origin}
    return {"ok": True, "steps": steps, "origin": origin, "final_projected": steps[-1]["candidate_next_state"] if steps else origin, "origin_unchanged": origin == state}


def route_value(c: Dict[str, float]) -> Dict[str, Any]:
    need = ("closures", "resonance", "reuse", "future_work_avoided", "verification_confidence", "movement", "rework_risk", "scope_interference")
    for k in need:
        if k not in c:
            return {"ok": False, "error": "invalid_factor"}
        try:
            float(c[k])
        except Exception:
            return {"ok": False, "error": "invalid_factor"}
    den = float(c["movement"]) * float(c["rework_risk"]) * float(c["scope_interference"])
    if den == 0:
        return {"ok": False, "error": "zero_denominator"}
    num = float(c["closures"]) * float(c["resonance"]) * float(c["reuse"]) * float(c["future_work_avoided"]) * float(c["verification_confidence"])
    return {"ok": True, "value": num / den}


def rank_routes(cands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = []
    for c in cands:
        rv = route_value(c)
        row = dict(c)
        if not rv.get("ok"):
            row["error"] = rv.get("error")
            row["route_value"] = None
        else:
            row["route_value"] = rv["value"]
        scored.append(row)
    scored.sort(key=lambda r: (-1e99 if r.get("route_value") is None else -r["route_value"], str(r.get("locality") or "")))
    return scored


def omni_scan(extra_open: Optional[List[str]] = None) -> Dict[str, Any]:
    assert_floor_intact()
    open_c = list(extra_open or [])
    for name in list(CELLS):
        ex = cell_expand(name)
        if ex.get("error") == "cell_cycle":
            open_c.append(f"cell_cycle:{name}")
    if 100 != len(DELLS):
        open_c.append("registry_gap")
    return {"floor": list(FLOOR), "cells": sorted(CELLS), "moji": list(MOJI_REGISTRY), "flows": list(FLOW_OPS), "open_circuits": sorted(set(open_c)), "owned_nodes": []}


def plan_cycle(open_circuits: List[str], resolved: Optional[str] = None) -> Dict[str, Any]:
    from .language import plan_from_evidence, harvest_evidence
    rows = harvest_evidence()
    if open_circuits:
        extra = [{"locality": loc, "authority": "scan", "contracts": [{"id": loc, "tested": True, "ready": True}], "edges": [], "shared": [], "downstream": [], "code_localities": [loc], "dependents": 1, "locked_domains_touched": 0} for loc in open_circuits]
        rows = extra + rows
    return plan_from_evidence(rows, resolved=resolved)
