#!/usr/bin/env python3
"""
02_TINY_LEXER.py
Code Phase 1 · Artifact 2
Status: TRUE
Offline · Zero dependencies · Stdlib only

Decisions (calculated for the program):
- Language: Python 3 (best offline fit for ChromeOS/Linux + future self-host)
- Form: pure function, longest-match first
- Scope: recognition only (no parse, no eval) — Code Phase 2 owns parser
- Dual boundary: structure tokens = Mandel side · free text = English display side
"""

from __future__ import annotations
import re
from typing import List, Dict, Any

# Locked from 01_REGISTRY_DATA
FLOWS = [
    ">>>", ">>", ">",
    "::", ":>", "<:", "<:>", ":",
    "<<[Delta]"
]
# Longest first is critical
FLOWS_SORTED = sorted(FLOWS, key=len, reverse=True)

LEIGHT_MARKERS = {"leight", "leight:"}
LOURE_MARKERS  = {"loure", "loure:"}

DELL_RE = re.compile(r"\b(\d{1,2})\b")

def tokenize(text: str) -> List[Dict[str, Any]]:
    """
    Minimal offline token recognizer.
    Returns list of tokens:
      {"type": "DELL"|"FLOW"|"LEIGHT"|"LOURE"|"TEXT", "value": ..., "raw": ...}
    """
    if not text:
        return []

    tokens: List[Dict[str, Any]] = []
    i = 0
    n = len(text)

    while i < n:
        # skip pure whitespace (keep as TEXT only if meaningful later)
        if text[i].isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            # collapse pure whitespace unless it is the entire remaining string
            if j > i:
                tokens.append({"type": "TEXT", "value": text[i:j], "raw": text[i:j]})
                i = j
                continue

        matched = False

        # 1. FLOW (longest match)
        for flow in FLOWS_SORTED:
            if text.startswith(flow, i):
                tokens.append({"type": "FLOW", "value": flow, "raw": flow})
                i += len(flow)
                matched = True
                break
        if matched:
            continue

        # 2. LEIGHT / LOURE (word boundary, case-insensitive)
        rest = text[i:]
        lower = rest.lower()
        for marker in LEIGHT_MARKERS:
            if lower.startswith(marker) and (len(rest) == len(marker) or not rest[len(marker)].isalnum()):
                tokens.append({"type": "LEIGHT", "value": "LEIGHT", "raw": rest[:len(marker)]})
                i += len(marker)
                matched = True
                break
        if matched:
            continue
        for marker in LOURE_MARKERS:
            if lower.startswith(marker) and (len(rest) == len(marker) or not rest[len(marker)].isalnum()):
                tokens.append({"type": "LOURE", "value": "LOURE", "raw": rest[:len(marker)]})
                i += len(marker)
                matched = True
                break
        if matched:
            continue

        # 3. DELL number 0-50
        m = DELL_RE.match(text, i)
        if m:
            num = int(m.group(1))
            if 0 <= num <= 50:
                tokens.append({"type": "DELL", "value": num, "raw": m.group(1)})
                i = m.end()
                matched = True
        if matched:
            continue

        # 4. Everything else is TEXT (English / display side)
        # take until next potential structure token
        j = i + 1
        while j < n:
            # peek for any flow or digit start
            if any(text.startswith(f, j) for f in FLOWS_SORTED):
                break
            if text[j].isdigit():
                break
            # word boundary check for leight/loure is expensive; keep simple
            j += 1
        tokens.append({"type": "TEXT", "value": text[i:j], "raw": text[i:j]})
        i = j

    return tokens


def demo():
    samples = [
        "50 Manifest > 08 Create : Leight newroot",
        "23 Lock >> 12 Test Loure adopt",
        "Alpha : 00 Nova <: English display here",
        "<<[Delta] 14 Bind :: 09 Show"
    ]
    for s in samples:
        print("INPUT :", s)
        for t in tokenize(s):
            print("  ", t)
        print()

if __name__ == "__main__":
    demo()
