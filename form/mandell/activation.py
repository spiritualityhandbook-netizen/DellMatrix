#!/usr/bin/env python3
"""Mandell language activation: floor, cheat, temp, omni, cells, tokenless."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import hashlib
import json
import os

from .floor import FLOOR, NOVA_MODE, assert_floor_intact
from .registry import DELLS
from .seed import CELLS, MANDELLMOJI, FLOW_OPS, BULLET, define_cell, parse_seed

GREEK = {
    "Alpha": {"scope": "floor", "semantic_root": "source", "floor_status": "floor"},
    "Delta": {"scope": "floor", "semantic_root": "change", "floor_status": "floor"},
    "Omega": {"scope": "floor", "semantic_root": "bound", "floor_status": "floor"},
    "Omni": {"scope": "floor", "semantic_root": "full-field meta-bus", "floor_status": "floor"},
    "Lambda": {"scope": "language", "semantic_root": "logic wavelength", "floor_status": "not_floor"},
    "Sigma": {"scope": "language", "semantic_root": "sum of parts", "floor_status": "not_floor"},
}
TEMP_HORIZON = {"cold": 1, "warm": 2, "hot": 3}
DIRECTIONS = ("forward", "back", "side", "up", "down", "in", "out")
CELL_STORE = os.path.join(os.path.dirname(__file__), "..", "state", "mandell_cells.json")


def greek_operator(name: str) -> Dict[str, Any]:
    row = GREEK.get(name)
    if not row:
        return {"ok": False, "error": "unknown_greek"}
    return {"ok": True, "glyph": name, "name": name, **row}


def temp_horizon(name: str) -> int:
    return TEMP_HORIZON.get((name or "warm").lower(), 2)


def cheat_project(origin: str, direction: str = "forward", temp: str = "hot") -> List[Dict[str, Any]]:
    n = min(3, temp_horizon(temp))
    out = []
    prior = origin or "HEAD"
    for i in range(1, n + 1):
        candidate = f"{prior}|{direction}|iter{i}"
        out.append({
            "origin": origin,
            "direction": direction if direction in DIRECTIONS else "forward",
            "iteration": i,
            "candidate_state": candidate,
            "assumptions": [f"from:{prior}"],
            "uncertainty": round(0.3 * i, 2),
            "label": "PROJECTED_NOT_FACT",
        })
        prior = candidate
    return out


def omni_report() -> Dict[str, Any]:
    assert_floor_intact()
    open_circuits = []
    if not CELLS:
        open_circuits.append("cells_empty_until_defined")
    return {
        "floor": list(FLOOR),
        "nova": NOVA_MODE,
        "grammar": {"flows": list(FLOW_OPS), "bullet": BULLET, "moji": dict(MANDELLMOJI)},
        "dells": {"count": len(DELLS), "min": min(DELLS), "max": max(DELLS)},
        "cells": sorted(CELLS),
        "temperature": dict(TEMP_HORIZON),
        "projection": "transient",
        "persistence": {"cells_file": os.path.abspath(CELL_STORE)},
        "open_circuits": open_circuits,
        "owned_nodes": [],
    }


def semantic_hash(seed_text: str) -> str:
    s = parse_seed(seed_text)
    payload = json.dumps({"atoms": [(a.dell, a.term) for a in s.atoms], "flows": list(s.flows), "ok": s.ok}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def tokenless_report(verbose: str, compressed: str) -> Dict[str, Any]:
    from .seed import compression_report
    rep = compression_report(verbose, compressed)
    rep["source_hash"] = semantic_hash(verbose)
    rep["compressed_hash"] = semantic_hash(compressed)
    rep["semantic_hash_equal"] = rep["source_hash"] == rep["compressed_hash"]
    return rep


def emoji_expand(text: str) -> str:
    out = text or ""
    out = out.replace(MANDELLMOJI["Chain"], ">")
    out = out.replace(MANDELLMOJI["Chainlink"], BULLET)
    return out


def persist_cells(path: Optional[str] = None) -> str:
    target = path or CELL_STORE
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(dict(CELLS), f, indent=2)
    return target


def load_cells(path: Optional[str] = None) -> int:
    target = path or CELL_STORE
    if not os.path.isfile(target):
        return 0
    with open(target, encoding="utf-8") as f:
        data = json.load(f) or {}
    n = 0
    for name, seed in data.items():
        if str(seed).startswith("__cell__:"):
            from .seed import link_cell
            link_cell(str(name), str(seed).split(":", 1)[1])
        else:
            define_cell(str(name), str(seed))
        n += 1
    return n


def explain_dell(n: int) -> Dict[str, Any]:
    d = DELLS.get(n)
    if not d:
        return {"ok": False, "error": "unregistered"}
    from .latinmandell import explain
    latin = explain(d["name"])
    return {"ok": True, "n": n, "name": d["name"], "manor": d["manor"], "latin": latin}


def parse_directive(text: str) -> Dict[str, Any]:
    s = parse_seed(text)
    return {
        "ok": s.ok,
        "error": s.error,
        "objective": s.atoms[0].as_mandel() if s.atoms else "",
        "operations": [a.as_mandel() for a in s.atoms],
        "flows": list(s.flows),
        "context": s.label,
        "human": s.as_english() if s.ok else s.error,
    }


def broad_route(open_circuits: List[str]) -> Dict[str, Any]:
    ranked = []
    for loc in open_circuits:
        value = (1 * 3 * 2 * 2 * 3) / (1 * 1 * 1)
        ranked.append({"locality": loc, "route_value": value})
    ranked.sort(key=lambda r: -r["route_value"])
    return {"chosen": (ranked[0]["locality"] if ranked else "none"), "ranked": ranked, "label": "PROJECTED_NOT_FACT"}
