#!/usr/bin/env python3
"""Mandell language authority: persist, evidence, plan, parser adapter."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os

from .seed import CELLS
from .canonical import parse_directive_v2, rank_evidence
from .latinmandell import export_customs, import_customs, clear_customs

LANGUAGE_VERSION = "4"
LANGUAGE_KEY = "mandell_language"


def dump_language() -> Dict[str, Any]:
    return {
        "version": LANGUAGE_VERSION,
        "cells": dict(CELLS),
        "latin_customs": export_customs(),
        "language_configuration": {"parser": "parse_directive_v2", "cell_authority": "seed.expand_cell"},
    }


def restore_language(data: Optional[Dict[str, Any]]) -> None:
    blob = (data or {}).get(LANGUAGE_KEY) or data or {}
    if not isinstance(blob, dict):
        return
    cells = blob.get("cells") or {}
    CELLS.clear()
    CELLS.update({str(k): str(v) for k, v in cells.items()})
    if blob.get("latin_customs"):
        clear_customs()
        import_customs(blob.get("latin_customs") or {})


def attach_language(state: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(state)
    out[LANGUAGE_KEY] = dump_language()
    out.pop("cheat_projections", None)
    out.pop("omni_report", None)
    out.pop("route_candidates", None)
    return out


def save_program_language(program: Any, path: str) -> str:
    from form.persist import save
    save(program, path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data = attach_language(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def load_program_language(owner: str, path: str) -> Any:
    from form.persist import load
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    restore_language(data)
    return load(owner, path)


def parse_directive(text: str) -> Dict[str, Any]:
    g = parse_directive_v2(text)
    return {
        "ok": g.get("ok"),
        "error": g.get("error"),
        "nodes": g.get("nodes") or [],
        "locks": g.get("locks") or [],
        "guards": g.get("guards") or [],
        "tests": g.get("tests") or [],
        "assertions": g.get("assertions") or [],
        "exit": g.get("exit") or [],
        "semantic_hash": g.get("semantic_hash"),
        "comments": g.get("comments") or [],
        "errors": g.get("errors") or [],
        "flows": g.get("flows") or [],
    }


def harvest_evidence() -> List[Dict[str, Any]]:
    root = os.path.dirname(__file__)
    rows = [
        {"locality": "cells", "authority": "seed.expand_cell", "contracts": [{"id": "cycle", "tested": True, "ready": True}, {"id": "nested", "tested": True, "ready": True}], "edges": ["seed"], "shared": ["seed"], "downstream": ["directive"], "code_localities": ["seed.py"], "dependents": 2, "locked_domains_touched": 0},
        {"locality": "directive", "authority": "canonical.parse_directive_v2", "contracts": [{"id": "ast", "tested": True, "ready": True}, {"id": "roundtrip", "tested": True, "ready": True}], "edges": ["canonical"], "shared": ["canonical"], "downstream": ["selfhost"], "code_localities": ["canonical.py"], "dependents": 1, "locked_domains_touched": 0},
        {"locality": "cheat", "authority": "canonical.cheat_project", "contracts": [{"id": "executor", "tested": True, "ready": True}], "edges": ["executor"], "shared": ["executor"], "downstream": [], "code_localities": ["canonical.py"], "dependents": 1, "locked_domains_touched": 0},
        {"locality": "docs", "authority": "docs", "contracts": [{"id": "runtime_md", "tested": os.path.isfile(os.path.join(root, "MANDELL_RUNTIME.md")), "ready": False}], "edges": [], "shared": [], "downstream": [], "code_localities": ["MANDELL_RUNTIME.md"], "dependents": 0, "locked_domains_touched": 1},
    ]
    for row in rows:
        row["tests"] = [c["id"] for c in row["contracts"] if c.get("tested")]
        row["feature"] = row["locality"]
    return rows


def plan_from_evidence(rows: Optional[List[Dict[str, Any]]] = None, resolved: Optional[str] = None) -> Dict[str, Any]:
    ev = [dict(r) for r in (rows or harvest_evidence())]
    ev = [r for r in ev if r.get("locality") != resolved]
    ranked = rank_evidence(ev)
    return {"chosen": ranked[0]["locality"] if ranked else "none", "routes": ranked, "label": "PROJECTED_NOT_FACT"}
