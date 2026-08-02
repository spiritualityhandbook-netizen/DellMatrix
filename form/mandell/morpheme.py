#!/usr/bin/env python3
"""
Morpheme delimiter protocol + lexicon (Codex + Visual Control forms).

Force structured subword splits. Expand prefix/root/suffix senses.
Does not reprogram host BPE.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import re

PREFIXES: Dict[str, str] = {
    "com": "together · synthesis · unified",
    "con": "with · joint",
    "re": "again · iterative · back",
    "pre": "before · predictive",
    "post": "after",
    "trans": "across · transformative",
    "de": "down · analytical · reverse · intensive",
    "omni": "all · universal · whole",
    "im": "in · isolated",
    "sub": "under · nested",
    "over": "above · across",
    "nova": "new · edge (not Floor)",
    "alpha": "beginning",
    "omega": "end · completion",
    "delta": "change",
    "man": "control · hand · execution",
    "nur": "nurse · feed · adaptive growth",
    "syn": "synchronized",
    "iso": "quarantined · equal",
    "aequi": "balanced",
    "ob": "against · opposed",
    "ad": "toward · directed",
    "fu": "forward vector",
    "nud": "raw · naked",
}

ROOTS: Dict[str, str] = {
    "fac": "construct · make",
    "log": "trace · reason",
    "mit": "send · transmit",
    "spec": "evaluate · look",
    "men": "mind",
    "mend": "validate · repair · honor",
    "tu": "protect",
    "birth": "genesis",
    "dell": "nested unit · operator cell · protected pocket",
    "mand": "command · order · execute",
    "cor": "heart · core",
    "ordo": "order · rank",
    "lux": "light",
    "lumen": "light made visible",
    "pulse": "stroke · beat",
    "voc": "voice",
    "gen": "origin · generate",
    "struct": "structure",
    "plete": "terminate · complete",
}

SUFFIXES: Dict[str, str] = {
    "ce": "attribute / act",
    "er": "actor",
    "re": "loop / again · return frame",
    "ure": "object / result · formalized",
    "dell": "fragment · nested cell · protected pocket",
    "tion": "act or state",
    "ment": "result or means · mind",
    "ing": "active pipeline",
    "ex": "execute immediately",
    "term": "terminate · wipe",
    "mut": "mutate variable",
}

# Flat lookup for quick sense
MORPHEMES: Dict[str, str] = {}
MORPHEMES.update(PREFIXES)
MORPHEMES.update(ROOTS)
MORPHEMES.update(SUFFIXES)
MORPHEMES.update({
    "mandel": "control-nest · Mandell root surface",
    "mandell": "control-nest · Mandell root surface",
    "nurture": "feed growth",
    "commandell": "unified execution protected pocket",
    "omnifacure": "universal object construction",
})


def split_delimited(text: str) -> List[str]:
    t = (text or "").strip()
    if not t:
        return []
    t = re.sub(r"^[\[\{⟨]+", "", t)
    t = re.sub(r"[\]\}⟩]+", "", t)
    parts = re.split(r"[-_/]+", t)
    return [p for p in (x.strip() for x in parts) if p]


def force_mandell_morphemes(word: str) -> str:
    w = (word or "").strip()
    low = w.lower().replace(" ", "")
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
        "omnifacure": "Omni-fac-ure",
        "omni-fac-ure": "Omni-fac-ure",
        "transfacure": "Trans-fac-ure",
        "rebirth": "Re-birth",
        "defacure": "De-fac-ure",
        "refacure": "Re-fac-ure",
        "conlogure": "Con-log-ure",
        "premiture": "Pre-mit-ure",
        "omnispecure": "Omni-spec-ure",
        "translogdell": "Trans-log-dell",
    }
    if low in table:
        return table[low]
    if "-" in w or "_" in w:
        return w
    return w


def sense_of(part: str) -> str:
    p = (part or "").lower()
    if p in PREFIXES:
        return PREFIXES[p]
    if p in ROOTS:
        return ROOTS[p]
    if p in SUFFIXES:
        return SUFFIXES[p]
    return MORPHEMES.get(p, "")


def explain_morphemes(text: str) -> Dict:
    forced = force_mandell_morphemes(text)
    parts = split_delimited(forced if "-" in forced else text)
    if not parts:
        parts = split_delimited(text)
    out = []
    for p in parts:
        s = sense_of(p)
        out.append({
            "morpheme": p,
            "sense": s or "(open)",
            "known": bool(s),
            "kind": (
                "prefix" if p.lower() in PREFIXES else
                "root" if p.lower() in ROOTS else
                "suffix" if p.lower() in SUFFIXES else
                "open"
            ),
        })
    return {
        "input": text,
        "forced": forced,
        "parts": out,
        "note": "Delimiter + lexicon · client-side Mandell surface",
    }


def smoke() -> bool:
    print("=== MORPHEME PROTOCOL SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    rec("force Commandell", force_mandell_morphemes("Commandell") == "Com-man-dell")
    rec("force Omni-fac-ure", "fac" in force_mandell_morphemes("omnifacure").lower())
    rec("split", split_delimited("Com-man-dell") == ["Com", "man", "dell"])
    rec("prefix sense", "unified" in sense_of("com").lower() or "together" in sense_of("com").lower())
    rec("explain", len(explain_morphemes("Omni-fac-ure")["parts"]) >= 2)
    rec("new prefix syn", "syn" in PREFIXES)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
