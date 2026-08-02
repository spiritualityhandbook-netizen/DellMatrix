#!/usr/bin/env python3
"""
Morpheme delimiter protocol — force structured subword splits.

Client-side control: hyphens / brackets guide human + LatinMandell parsing.
Does not reprogram host BPE; shapes *our* Mandell surface.

Example: Commandell → Com-man-dell
"""

from __future__ import annotations

from typing import Dict, List, Optional
import re

# Known Mandell-family morpheme senses (Codex-aligned + LatinMandell)
MORPHEMES: Dict[str, str] = {
    "com": "together · synthesis",
    "con": "with · joint",
    "man": "control · hand · execution",
    "dell": "nested unit · small chamber · operator cell",
    "mand": "command · order",
    "mandel": "control-nest · Mandell root surface",
    "re": "again · back",
    "pre": "before",
    "post": "after",
    "sub": "under · nested",
    "over": "above · across",
    "nova": "new · edge (not Floor)",
    "omni": "all · whole",
    "alpha": "beginning",
    "omega": "end · completion",
    "delta": "change",
    "lux": "light",
    "lumen": "light made visible",
    "cor": "heart · core",
    "ordo": "order · rank",
    "nurture": "feed growth",
    "nur": "nurse · feed",
}


def split_delimited(text: str) -> List[str]:
    """Split on hyphens / brackets used as deliberate morpheme boundaries."""
    t = (text or "").strip()
    if not t:
        return []
    # strip outer [] {}
    t = re.sub(r"^[\[\{]+", "", t)
    t = re.sub(r"[\]\}]+", "", t)
    parts = re.split(r"[-_/]+", t)
    return [p for p in (x.strip() for x in parts) if p]


def force_mandell_morphemes(word: str) -> str:
    """
    Suggest hyphenated form for known compounds.
    Commandell → Com-man-dell ; Mandell → Man-dell
    """
    w = (word or "").strip()
    low = w.lower().replace(" ", "")
    # explicit known compounds
    table = {
        "commandell": "Com-man-dell",
        "mandell": "Man-dell",
        "mandel": "Man-del",
        "mandellang": "Man-dell-Lang",
        "mandellanguage": "Man-dell-Lang-uage",
        "commence": "Com-men-ce",
        "commend": "Com-mend",
        "command": "Com-mand",
        "complete": "Com-plete",
        "nurture": "Nur-tu-re",
        "future": "Fu-tu-re",
        "answer": "Answ-er",
    }
    if low in table:
        return table[low]
    # already delimited
    if "-" in w or "_" in w:
        return w
    return w


def explain_morphemes(text: str) -> Dict:
    parts = split_delimited(force_mandell_morphemes(text) if "-" not in (text or "") else text)
    if not parts:
        parts = split_delimited(text)
    out = []
    for p in parts:
        sense = MORPHEMES.get(p.lower(), "")
        out.append({"morpheme": p, "sense": sense or "(open)", "known": bool(sense)})
    return {
        "input": text,
        "forced": force_mandell_morphemes(text),
        "parts": out,
        "note": "Delimiter protocol · does not change host BPE · shapes Mandell surface",
    }


def smoke() -> bool:
    print("=== MORPHEME PROTOCOL SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    rec("force Commandell", force_mandell_morphemes("Commandell") == "Com-man-dell")
    rec("split", split_delimited("Com-man-dell") == ["Com", "man", "dell"])
    rec("explain", len(explain_morphemes("Com-man-dell")["parts"]) == 3)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
