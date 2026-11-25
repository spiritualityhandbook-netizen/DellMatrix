#!/usr/bin/env python3
"""
04_RUNTIME_STUB.py
Code Phase 2 · Artifact 4
Status: TRUE
Offline · Zero dependencies · Stdlib only

Thin evaluator: takes an AST node (or DELL number)
and returns the Manor + basic action from the offline registry.
No side effects. Structure + lookup only.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# ---------------------------------------------------------------------------
# Offline registry loader (reads the JSON we already wrote)
# ---------------------------------------------------------------------------
_REGISTRY_PATH = Path(__file__).parent / "01_REGISTRY_DATA.json"
_REGISTRY: Optional[Dict[str, Any]] = None

def _load_registry() -> Dict[str, Any]:
    global _REGISTRY
    if _REGISTRY is None:
        with open(_REGISTRY_PATH, "r", encoding="utf-8") as f:
            _REGISTRY = json.load(f)
    return _REGISTRY

def get_dell(dell_num: int) -> Optional[Dict[str, Any]]:
    """Return the True registry entry for a Dell number, or None."""
    reg = _load_registry()
    for entry in reg.get("dells", []):
        if entry["dell"] == dell_num:
            return entry
    return None

def get_flow(symbol: str) -> Optional[Dict[str, Any]]:
    """Return the locked flow entry, or None."""
    reg = _load_registry()
    for entry in reg.get("flows", []):
        if entry["symbol"] == symbol:
            return entry
    return None

# ---------------------------------------------------------------------------
# Thin runtime
# ---------------------------------------------------------------------------

def evaluate_node(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a single AST node.
    Returns a result dict with status, kind, value, manor, and optional flow info.
    Never executes side effects — pure lookup + structure.
    """
    kind = node.get("kind")

    if kind == "DELL":
        num = node.get("value")
        entry = get_dell(num) if isinstance(num, int) else None
        result = {
            "status": "ok" if entry else "unknown_dell",
            "kind": "DELL",
            "value": num,
            "name": entry["name"] if entry else None,
            "manor": entry["manor"] if entry else None,
            "raw": node.get("raw"),
        }
        # attach flow if present on the node
        flow_sym = node.get("flow")
        if flow_sym:
            flow_entry = get_flow(flow_sym)
            result["flow"] = {
                "symbol": flow_sym,
                "name": flow_entry["name"] if flow_entry else None,
                "manor": flow_entry["manor"] if flow_entry else None,
            }
        return result

    if kind == "FLOW":
        sym = node.get("value")
        entry = get_flow(sym)
        return {
            "status": "ok" if entry else "unknown_flow",
            "kind": "FLOW",
            "value": sym,
            "name": entry["name"] if entry else None,
            "manor": entry["manor"] if entry else None,
            "raw": node.get("raw"),
        }

    if kind in ("LEIGHT", "LOURE"):
        return {
            "status": "ok",
            "kind": kind,
            "value": kind,
            "manor": "create-path" if kind == "LEIGHT" else "change-path",
            "raw": node.get("raw"),
        }

    if kind == "TEXT":
        return {
            "status": "display",
            "kind": "TEXT",
            "value": node.get("value"),
            "manor": "English / display side",
            "raw": node.get("raw"),
        }

    return {
        "status": "unhandled",
        "kind": kind,
        "value": node.get("value"),
        "raw": node.get("raw"),
    }


def evaluate_ast(ast: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Evaluate every node in an AST. Returns list of result dicts."""
    return [evaluate_node(node) for node in ast]


def evaluate_text(text: str) -> List[Dict[str, Any]]:
    """
    Convenience: text → tokens → AST → evaluated results.
    Requires 02_TINY_LEXER and 03_MINIMAL_PARSER on the path.
    """
    try:
        from tiny_lexer import tokenize
        from minimal_parser import parse
    except ImportError:
        # fallback names if files are run from same directory
        import importlib.util
        def _load(name, path):
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        here = Path(__file__).parent
        tl = _load("tiny_lexer", here / "02_TINY_LEXER.py")
        mp = _load("minimal_parser", here / "03_MINIMAL_PARSER.py")
        tokenize = tl.tokenize
        parse = mp.parse

    tokens = tokenize(text)
    ast = parse(tokens)
    return evaluate_ast(ast)


def demo():
    samples = [
        "50 Manifest > 08 Create",
        "23 Lock >> 12 Test",
        "00 Nova : Alpha",
        "Leight newroot Loure adopt"
    ]
    for s in samples:
        print("INPUT :", s)
        try:
            results = evaluate_text(s)
            for r in results:
                print("  ", r)
        except Exception as e:
            print("  (demo requires sibling modules)", e)
        print()

if __name__ == "__main__":
    print("Thin Runtime Stub ready.")
    print("Core functions: get_dell(), get_flow(), evaluate_node(), evaluate_ast(), evaluate_text()")
