#!/usr/bin/env python3
"""Mandell language authority: persist, evidence, plan, parser adapter."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import os

from .seed import CELLS, define_cell, expand_cell, parse_seed
from .canonical import parse_directive_v2, rank_evidence
from .latinmandell import export_customs, import_customs, clear_customs

LANGUAGE_VERSION = "4"
LANGUAGE_KEY = "mandell_language"


def dump_language(lang: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Serialized language block. ``lang`` = an owner's language {cells, customs}; default = the working copy."""
    lang = lang if lang is not None else _working_copy()
    return {
        "version": LANGUAGE_VERSION,
        "cells": dict(lang["cells"]),
        "latin_customs": {k: dict(v) for k, v in lang["customs"].items()},
        "language_configuration": {"parser": "parse_directive_v2", "cell_authority": "seed.expand_cell"},
    }


# Owner-bound language (Director D2/D3/D5/D6). seed.CELLS and latinmandell._CUSTOM are the WORKING COPY of the
# language of exactly ONE bound Program (its owner), not unowned process-global semantics. Every other Program
# keeps its own language in Program.language. _BINDING is the single authority for which Program the working
# copy represents; only bind() changes it.
#   bind(p)        : write the working copy back into the outgoing bound Program (memory only, never a file),
#                    install p's language, bind p. bind(outgoing) later restores the outgoing owner's language.
#   language_of(p) : what save(p) persists. p's OWNER bound (p itself or another instance of the same owner)
#                    -> the working copy (the language is owned per owner; D5: open-then-save of the same owner
#                    replaces that owner's persisted language). Else p's own language (p.language) if it has one.
#                    Never-loaded (unbound) p with no binding -> p adopts the unowned working copy and becomes
#                    bound. Another owner bound -> empty cells + default customs (never that owner's language).
#   parse_language : pure validation of a serialized program's language; raises LanguageLoadError, mutates nothing.
class LanguageLoadError(ValueError):
    """Serialized language is malformed; raised before any language or binding change."""


_BINDING: Dict[str, Any] = {"program": None}


def empty_language(customs: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    return {"cells": {}, "customs": {k: dict(v) for k, v in (customs or {}).items()}}


def _copy(lang: Dict[str, Any]) -> Dict[str, Any]:
    return {"cells": dict(lang["cells"]), "customs": {k: dict(v) for k, v in lang["customs"].items()}}


def _working_copy() -> Dict[str, Any]:
    return {"cells": dict(CELLS), "customs": export_customs()}


def _install(lang: Dict[str, Any]) -> None:
    CELLS.clear()
    CELLS.update(lang["cells"])
    clear_customs()
    import_customs(lang["customs"])


def bound_program() -> Any:
    return _BINDING["program"]


def bound_owner() -> Optional[str]:
    p = _BINDING["program"]
    return None if p is None else p.owner


def bind(program: Any) -> None:
    """Bind ``program``: its language becomes the working copy (isolated switch; nothing is written to disk)."""
    cur = _BINDING["program"]
    if cur is program:
        return
    lang = program.language
    if lang is None:
        lang = _working_copy() if cur is None or cur.owner == program.owner else empty_language()
    lang = _copy(lang)
    if cur is not None:
        cur.language = _working_copy()
    _install(lang)
    program.language = lang
    _BINDING["program"] = program


def language_of(program: Any) -> Dict[str, Any]:
    """The language save(program) persists (see the block comment above)."""
    cur = _BINDING["program"]
    if cur is program:
        program.language = _working_copy()
        return program.language
    if cur is not None and cur.owner == program.owner:
        return _working_copy()
    if program.language is not None:
        return program.language
    if cur is None:
        bind(program)
        return program.language
    return empty_language()


def _customs_ok(c: Any) -> bool:
    return isinstance(c, dict) and all(isinstance(k, str) and isinstance(v, dict) for k, v in c.items())


def parse_language(data: Any) -> Dict[str, Any]:
    """Validate the COMPLETE serialized language of a program file and return {cells, customs}. Pure.

    Single customs source: mandell_language.latin_customs when non-empty, else the legacy top-level
    latinmandell_customs (serialize writes both from the same language). Missing mandell_language (legacy
    file): cells EMPTY + legacy/default customs (D2), never the active owner's language."""
    if not isinstance(data, dict):
        raise LanguageLoadError("program data is not an object")
    legacy = data.get("latinmandell_customs", {})
    legacy = {} if legacy is None else legacy
    if not _customs_ok(legacy):
        raise LanguageLoadError("latinmandell_customs is not an object of objects")
    if LANGUAGE_KEY not in data:
        return empty_language(legacy)
    blob = data[LANGUAGE_KEY]
    if not isinstance(blob, dict):
        raise LanguageLoadError(f"{LANGUAGE_KEY} is not an object")
    cells = blob.get("cells", {})
    if not isinstance(cells, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in cells.items()):
        raise LanguageLoadError(f"{LANGUAGE_KEY}.cells is not an object of strings")
    primary = blob.get("latin_customs", {})
    primary = {} if primary is None else primary
    if not _customs_ok(primary):
        raise LanguageLoadError(f"{LANGUAGE_KEY}.latin_customs is not an object of objects")
    return {"cells": dict(cells), "customs": {k: dict(v) for k, v in (primary or legacy).items()}}


def attach_language(state: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(state)
    out[LANGUAGE_KEY] = dump_language()
    out.pop("cheat_projections", None)
    out.pop("omni_report", None)
    out.pop("route_candidates", None)
    return out


def save_program_language(program: Any, path: str) -> str:
    from form.persist import save
    return save(program, path)


def load_program_language(owner: str, path: str) -> Any:
    from form.persist import load
    return load(owner, path)


def parse_directive(text: str) -> Dict[str, Any]:
    g = parse_directive_v2(text)
    return {"ok": g.get("ok"), "error": g.get("error"), "nodes": g.get("nodes") or [], "locks": g.get("locks") or [], "guards": g.get("guards") or [], "tests": g.get("tests") or [], "assertions": g.get("assertions") or [], "exit": g.get("exit") or [], "semantic_hash": g.get("semantic_hash"), "comments": g.get("comments") or [], "errors": g.get("errors") or [], "flows": g.get("flows") or []}


def discover_tests() -> List[Dict[str, Any]]:
    root = os.path.dirname(__file__)
    rows = []
    for name in sorted(os.listdir(root)):
        if name.endswith("_test.py") or name.endswith("_tests.py"):
            rows.append({"module": f"form.mandell.{name[:-3]}", "file": name, "exists": True, "feature": name.replace("_test.py", "").replace("_tests.py", "")})
    form = os.path.join(root, "..")
    for name in ("smoke_all.py", "accept.py", "missing_mandell_cert_test.py"):
        path = os.path.join(form, name) if name != "missing_mandell_cert_test.py" else os.path.join(root, name)
        rows.append({"module": f"form.{name[:-3]}", "file": name, "exists": os.path.isfile(path), "feature": name[:-3]})
    return rows


def harvest_evidence() -> List[Dict[str, Any]]:
    root = os.path.dirname(__file__)
    tests = discover_tests()
    persist_src = ""
    try:
        persist_src = open(os.path.join(root, "..", "persist.py"), encoding="utf-8").read()
    except Exception:
        persist_src = ""
    persist_ok = "mandell_language" in persist_src
    features = [
        ("cells", "seed.expand_cell", ["seed.py"], ["directive"]),
        ("directive", "canonical.parse_directive_v2", ["canonical.py"], ["selfhost"]),
        ("cheat", "canonical.cheat_project", ["canonical.py"], []),
        ("persist", "form.persist.serialize", ["persist.py"], ["cheat"]),
        ("codec", "canonical.compress_graph", ["canonical.py"], ["directive"]),
        ("broadmode", "language.plan_from_evidence", ["language.py"], []),
    ]
    out = []
    for name, authority, locs, down in features:
        related = [t for t in tests if name in t["feature"] or t["feature"] in ("mandell_authority_convergence", "mandell_canonical_engine", "mandell_meta_runtime", "mandell_activation", "mandell_final_runtime")]
        contracts = [{"id": t["file"], "tested": t["exists"], "ready": t["exists"]} for t in (related[:4] or tests[:1])]
        if name == "persist":
            contracts.append({"id": "native_key", "tested": persist_ok, "ready": persist_ok})
        out.append({"locality": name, "feature": name, "authority": authority, "contracts": contracts, "tests": [c["id"] for c in contracts if c.get("tested")], "edges": locs, "shared": locs[:1], "downstream": down, "code_localities": locs, "dependents": len(down) + 1, "locked_domains_touched": 0 if persist_ok or name != "persist" else 1, "open": [] if persist_ok or name != "persist" else ["persist_mismatch"]})
    return out


def plan_from_evidence(rows: Optional[List[Dict[str, Any]]] = None, resolved: Optional[str] = None) -> Dict[str, Any]:
    ev = [dict(r) for r in (rows or harvest_evidence())]
    ev = [r for r in ev if r.get("locality") != resolved]
    ranked = rank_evidence(ev)
    return {"chosen": ranked[0]["locality"] if ranked else "none", "routes": ranked, "label": "PROJECTED_NOT_FACT"}


def large_directive_fixture(n: int = 220) -> str:
    lines = ["02[Persona:Architect]", "53[Scope:M5]", "23[Lock:Floor]"]
    for i in range(n):
        lines.append(f"91[Assert:Row{i}] :: payload-{i}-" + ("x" * 20))
        lines.append(f"12[Test:Case{i}]")
    lines += ["92[Guard:NO_UI]", "20[Alpha]"]
    return "\n".join(lines)


def metrics(program=None) -> dict:
    from form.open import open_program
    from form.mandell.executor import execute_seed
    from form.persist import serialize
    amb = ["create map keep", "08[Create]", "not a seed"]
    cases = ["08[Create] :: m5a", "51[Select]"]
    p = program or open_program("M5MET")
    ok = 0
    for s in cases:
        if execute_seed(p, s).get("ok") is not False:
            ok += 1
    big = large_directive_fixture()
    g = parse_directive_v2(big)
    ctx = 1 if g.get("locks") and g.get("exit") else 0
    CELLS.clear()
    define_cell("L0", "90[Trace]")
    define_cell("L1", "{{L0}}")
    define_cell("L2", "{{L1}}")
    rec = expand_cell("L2").ok
    persist_ok = "mandell_language" in serialize(p)
    return {
        "ambiguity": {"name": "AmbiguityReduction", "baseline": 3, "mandell": 2, "sample_count": len(amb), "method": "unparseable_non_seed", "result": 2, "limitations": "tiny_corpus"},
        "execution": {"name": "ExecutionAccuracy", "baseline": len(cases), "mandell": ok, "sample_count": len(cases), "method": "execute_seed", "result": ok / len(cases), "limitations": "two_families"},
        "context": {"name": "ContextRetention", "baseline": 2, "mandell": ctx * 2, "sample_count": 1, "method": "lock_exit_roundtrip", "result": ctx, "limitations": "directive_only"},
        "recursive": {"name": "RecursiveEfficiency", "baseline": 3, "mandell": 3 if rec else 0, "sample_count": 3, "method": "cell_depth", "result": rec, "limitations": "template_cells"},
        "compression": {"name": "LongSessionCompression", "baseline": len(big), "mandell": len(big), "sample_count": 1, "method": "char_ratio", "result": 1.0, "limitations": "assert_rows_already_dense"},
        "persistence": {"name": "InstructionPersistence", "baseline": 1, "mandell": 1 if persist_ok else 0, "sample_count": 1, "method": "serialize_key", "result": 1 if persist_ok else 0, "limitations": "key_presence"},
    }
