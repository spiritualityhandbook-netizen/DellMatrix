#!/usr/bin/env python3
"""
03_MINIMAL_PARSER.py
Code Phase 2 · Artifact 3
Status: TRUE
Offline · Zero dependencies · Stdlib only

Consumes tokens from 02_TINY_LEXER.tokenize()
and produces a simple AST (list of nodes).

No runtime execution. Structure only.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional

# Re-use the tokenizer (same directory)
try:
    from tiny_lexer import tokenize          # when imported as package later
except ImportError:
    # standalone fallback – paste or copy the tokenize function if needed
    def tokenize(text: str) -> List[Dict[str, Any]]:
        raise ImportError("02_TINY_LEXER.py must be importable or its tokenize function available")


Node = Dict[str, Any]

def parse(tokens: List[Dict[str, Any]]) -> List[Node]:
    """
    Minimal offline parser.
    Turns a flat token stream into a list of structured nodes.

    Node shapes:
      {"kind": "DELL",   "value": int,   "flow": Optional[str], "raw": str}
      {"kind": "FLOW",   "value": str,   "raw": str}
      {"kind": "LEIGHT", "value": "LEIGHT", "raw": str}
      {"kind": "LOURE",  "value": "LOURE",  "raw": str}
      {"kind": "TEXT",   "value": str,   "raw": str}
      {"kind": "SEQ",    "children": List[Node]}   # when flows bind multiple Dells
    """
    if not tokens:
        return []

    ast: List[Node] = []
    i = 0
    n = len(tokens)

    while i < n:
        tok = tokens[i]
        ttype = tok["type"]

        if ttype == "DELL":
            node: Node = {
                "kind": "DELL",
                "value": tok["value"],
                "flow": None,
                "raw": tok["raw"]
            }
            # look ahead for a following FLOW that binds this Dell
            if i + 1 < n and tokens[i + 1]["type"] == "FLOW":
                node["flow"] = tokens[i + 1]["value"]
                i += 1  # consume the flow
            ast.append(node)

        elif ttype == "FLOW":
            # standalone flow (rare, but legal)
            ast.append({
                "kind": "FLOW",
                "value": tok["value"],
                "raw": tok["raw"]
            })

        elif ttype == "LEIGHT":
            ast.append({
                "kind": "LEIGHT",
                "value": "LEIGHT",
                "raw": tok["raw"]
            })

        elif ttype == "LOURE":
            ast.append({
                "kind": "LOURE",
                "value": "LOURE",
                "raw": tok["raw"]
            })

        elif ttype == "TEXT":
            # collapse consecutive TEXT
            text_parts = [tok["value"]]
            while i + 1 < n and tokens[i + 1]["type"] == "TEXT":
                i += 1
                text_parts.append(tokens[i]["value"])
            combined = "".join(text_parts).strip()
            if combined:
                ast.append({
                    "kind": "TEXT",
                    "value": combined,
                    "raw": combined
                })

        i += 1

    return ast


def parse_text(text: str) -> List[Node]:
    """Convenience: text → tokens → AST"""
    return parse(tokenize(text))


def demo():
    samples = [
        "50 Manifest > 08 Create : Leight newroot",
        "23 Lock >> 12 Test Loure adopt",
        "Alpha : 00 Nova <: English display here",
        "<<[Delta] 14 Bind :: 09 Show"
    ]
    for s in samples:
        print("INPUT :", s)
        tokens = tokenize(s)
        ast = parse(tokens)
        for node in ast:
            print("  ", node)
        print()

if __name__ == "__main__":
    # For standalone demo we need the tokenizer in the same file or path.
    # In real use, import from 02_TINY_LEXER.
    print("Minimal Parser ready. Import tokenize from 02_TINY_LEXER then call parse() or parse_text().")
