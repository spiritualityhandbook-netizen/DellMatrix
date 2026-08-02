#!/usr/bin/env python3
"""
Tri-Harmonic Fusion Equation — LatinMandell link grading.

P (Prefix/Vector) ⇕ R (Root/Core) ⇕ S (Suffix/State) → grade

  ❀ Perfect  — zero semantic vector collision, high synergy
  🌱 Good    — functional, no collision, lower snap
  ⬛ OK      — collision / high entropy redundancy
  🌟 Leight  — unknown affix (new declaration)

High-S intake from Harmonic Formula + Lexer V3 forms.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import re

# Core dictionaries with semantic vectors (expandable)
PREFIXES: Dict[str, Dict[str, Any]] = {
    "omni": {"def": "all/universal", "v": ["scope_max", "inclusive"]},
    "pan": {"def": "all", "v": ["scope_max", "inclusive"]},
    "trans": {"def": "across/change", "v": ["movement", "alteration"]},
    "hyper": {"def": "over/excessive", "v": ["scale_large", "excess"]},
    "hypo": {"def": "under/less", "v": ["scale_small", "beneath"]},
    "auto": {"def": "self", "v": ["reflexive", "internal"]},
    "de": {"def": "down/complete", "v": ["intensive", "finality", "downward"]},
    "re": {"def": "back/again", "v": ["reversal", "loop"]},
    "pre": {"def": "before", "v": ["time_pre", "prior"]},
    "post": {"def": "after", "v": ["time_post", "following"]},
    "com": {"def": "with/together", "v": ["unified", "joint"]},
    "con": {"def": "with/together", "v": ["unified", "joint"]},
    "co": {"def": "with/together", "v": ["unified", "joint"]},
    "multi": {"def": "many", "v": ["plural", "quantity_many"]},
    "mono": {"def": "one", "v": ["singular", "quantity_one"]},
    "uni": {"def": "one", "v": ["singular", "quantity_one"]},
    "bi": {"def": "two", "v": ["dual", "quantity_two"]},
    "tri": {"def": "three", "v": ["quantity_three"]},
    "micro": {"def": "small", "v": ["scale_small", "granular"]},
    "macro": {"def": "large", "v": ["scale_large", "overview"]},
    "mega": {"def": "great", "v": ["scale_max", "power"]},
    "meta": {"def": "beyond/change", "v": ["transcendence", "shift"]},
    "neo": {"def": "new", "v": ["novelty", "origin"]},
    "sub": {"def": "under", "v": ["beneath", "lower"]},
    "super": {"def": "above/beyond", "v": ["above", "superior"]},
    "inter": {"def": "between", "v": ["connection", "bridge"]},
    "intra": {"def": "within", "v": ["interior", "nested"]},
    "anti": {"def": "against", "v": ["opposition"]},
    "contra": {"def": "against", "v": ["opposition"]},
    "dis": {"def": "apart/not", "v": ["separation", "negation"]},
    "non": {"def": "not", "v": ["negation", "absence"]},
    "un": {"def": "not/reverse", "v": ["negation", "reversal"]},
    "mal": {"def": "bad", "v": ["negative", "flaw"]},
    "bene": {"def": "good/well", "v": ["positive", "benefit"]},
    "eu": {"def": "good/well", "v": ["positive", "optimal"]},
    "semi": {"def": "half", "v": ["fraction_half", "partial"]},
    "proto": {"def": "first", "v": ["primary", "origin"]},
    "man": {"def": "control/hand", "v": ["control", "action"]},
    "nova": {"def": "new/edge", "v": ["novelty", "edge"]},
}

ROOTS: Dict[str, Dict[str, Any]] = {
    "fac": {"def": "do/make", "v": ["action", "creation"]},
    "man": {"def": "hand/execute", "v": ["control", "action"]},
    "mand": {"def": "order/command", "v": ["control", "order"]},
    "magn": {"def": "great/large", "v": ["scale_large"]},
    "log": {"def": "word/trace", "v": ["data", "record"]},
    "mut": {"def": "change", "v": ["alteration", "shift"]},
    "form": {"def": "shape", "v": ["structure", "design"]},
    "struct": {"def": "build", "v": ["make", "form"]},
    "spect": {"def": "look/see", "v": ["vision", "eye"]},
    "spec": {"def": "look/see", "v": ["vision", "eye"]},
    "scrib": {"def": "write", "v": ["text", "record"]},
    "script": {"def": "write", "v": ["text", "record"]},
    "duc": {"def": "lead", "v": ["guide", "motion"]},
    "duct": {"def": "lead", "v": ["guide", "motion"]},
    "ject": {"def": "throw", "v": ["projection", "motion"]},
    "puls": {"def": "drive/push", "v": ["force", "motion"]},
    "port": {"def": "carry", "v": ["transfer", "motion"]},
    "chron": {"def": "time", "v": ["time", "cycle"]},
    "graph": {"def": "write/draw", "v": ["record", "visual"]},
    "gram": {"def": "write/record", "v": ["text", "data"]},
    "path": {"def": "feeling/disease", "v": ["feeling", "state"]},
    "phil": {"def": "love", "v": ["bond", "affinity"]},
    "phon": {"def": "sound", "v": ["audio"]},
    "photo": {"def": "light", "v": ["light", "visual"]},
    "therm": {"def": "heat", "v": ["energy", "temperature"]},
    "hydr": {"def": "water", "v": ["element_water"]},
    "geo": {"def": "earth", "v": ["earth", "space"]},
    "bio": {"def": "life", "v": ["biology", "existence"]},
    "morph": {"def": "form/shape", "v": ["structure", "design"]},
    "gen": {"def": "birth/kind", "v": ["creation", "source"]},
    "cred": {"def": "believe", "v": ["trust", "mind"]},
    "fin": {"def": "end/limit", "v": ["stop", "border"]},
    "fix": {"def": "shape", "v": ["structure"]},
    "fract": {"def": "break", "v": ["split", "damage"]},
    "rupt": {"def": "break", "v": ["split", "damage"]},
    "serv": {"def": "keep/guard", "v": ["preserve", "hold"]},
    "ten": {"def": "hold", "v": ["keep", "grasp"]},
    "vert": {"def": "turn", "v": ["spin", "change"]},
    "vers": {"def": "turn", "v": ["spin", "change"]},
    "vid": {"def": "see", "v": ["vision"]},
    "vis": {"def": "see", "v": ["vision"]},
    "voc": {"def": "call/voice", "v": ["speak", "audio"]},
    "dell": {"def": "nested unit/cell", "v": ["container", "protection"]},
    "cor": {"def": "heart/core", "v": ["core", "center"]},
    "centr": {"def": "center", "v": ["core", "focus"]},
    "nova": {"def": "new/edge", "v": ["novelty", "edge"]},
    "xero": {"def": "(open/unknown)", "v": []},
}

SUFFIXES: Dict[str, Dict[str, Any]] = {
    "ure": {"def": "act/process", "v": ["object_state", "process"]},
    "dell": {"def": "pocket/nested", "v": ["container", "protection"]},
    "ell": {"def": "small tool", "v": ["instrument", "utility"]},
    "ity": {"def": "state/quality", "v": ["passive_state", "condition"]},
    "ation": {"def": "action/state", "v": ["active_state", "process"]},
    "tion": {"def": "action/state", "v": ["active_state", "process"]},
    "sion": {"def": "action/state", "v": ["active_state", "process"]},
    "ment": {"def": "result of action", "v": ["outcome"]},
    "ance": {"def": "action/state", "v": ["condition"]},
    "ence": {"def": "condition", "v": ["condition"]},
    "ive": {"def": "tending toward", "v": ["tendency"]},
    "able": {"def": "capable of", "v": ["ability", "passive_state"]},
    "ible": {"def": "capable of", "v": ["ability", "passive_state"]},
    "ic": {"def": "pertaining to", "v": ["relation"]},
    "ical": {"def": "pertaining to", "v": ["relation"]},
    "ous": {"def": "full of", "v": ["abundance"]},
    "ive": {"def": "inclined", "v": ["tendency"]},
    "or": {"def": "person who", "v": ["actor"]},
    "er": {"def": "person who", "v": ["actor"]},
    "ist": {"def": "one who", "v": ["actor"]},
    "ism": {"def": "system/belief", "v": ["ideology"]},
    "ology": {"def": "study of", "v": ["science", "data"]},
    "logy": {"def": "study of", "v": ["science", "data"]},
    "graph": {"def": "writing instrument", "v": ["tool", "record"]},
    "gram": {"def": "record", "v": ["text", "data"]},
    "meter": {"def": "measure", "v": ["tool", "scale"]},
    "metry": {"def": "measuring", "v": ["tool", "scale"]},
    "oid": {"def": "resembling", "v": ["similarity"]},
    "less": {"def": "without", "v": ["absence", "negation"]},
    "ful": {"def": "full of", "v": ["abundance"]},
    "ness": {"def": "state", "v": ["quality"]},
    "ship": {"def": "status", "v": ["state", "relation"]},
    "hood": {"def": "state", "v": ["status"]},
    "ize": {"def": "make/cause", "v": ["creation"]},
    "fy": {"def": "make", "v": ["creation"]},
    "ce": {"def": "act/attribute", "v": ["attribute"]},
    "re": {"def": "loop/again", "v": ["loop"]},
}


def _vecs(entry: Optional[Dict]) -> Set[str]:
    if not entry:
        return set()
    return set(entry.get("v") or [])


def evaluate_harmonic_link(prefix: str, root: str, suffix: str) -> Dict[str, Any]:
    """Tri-Harmonic Fusion grader."""
    p = (prefix or "").lower().strip()
    r = (root or "").lower().strip()
    s = (suffix or "").lower().strip()
    pData = PREFIXES.get(p)
    rData = ROOTS.get(r)
    sData = SUFFIXES.get(s)

    if not pData or not rData or not sData:
        return {
            "grade": "🌟 Leight_Link",
            "entropy": 0.0,
            "status": "NEW_LATINMANDELL_DECLARATION",
            "reason": "Root or affix unknown — awaiting definition",
            "prefix": p, "root": r, "suffix": s,
            "known": {"p": bool(pData), "r": bool(rData), "s": bool(sData)},
        }

    pv, rv, sv = _vecs(pData), _vecs(rData), _vecs(sData)
    overlap_pr = sorted(pv & rv)
    overlap_all = sorted(pv & rv & sv) if sv else []
    collision = bool(overlap_pr)

    if collision:
        return {
            "grade": "⬛ OK_Link",
            "entropy": 0.9,
            "status": "HIGH_ENTROPY_REDUNDANCY",
            "reason": f"Semantic collision on vectors: {overlap_pr}",
            "prefix": p, "root": r, "suffix": s,
            "defs": {"p": pData["def"], "r": rData["def"], "s": sData["def"]},
            "overlap": overlap_pr,
        }

    # Perfect: scope_max or clear action with no overlap
    if "scope_max" in pv or "action" in rv or "creation" in rv:
        return {
            "grade": "❀ Perfect_Link",
            "entropy": 0.1,
            "status": "CRYSTALLINE",
            "reason": "Zero semantic overlap · synergistic snap",
            "prefix": p, "root": r, "suffix": s,
            "defs": {"p": pData["def"], "r": rData["def"], "s": sData["def"]},
        }

    return {
        "grade": "🌱 Good_Link",
        "entropy": 0.4,
        "status": "STABLE_FUNCTIONAL",
        "reason": "Functional · no collision · lower poetic snap",
        "prefix": p, "root": r, "suffix": s,
        "defs": {"p": pData["def"], "r": rData["def"], "s": sData["def"]},
    }


_TRIPLE = re.compile(r"\[([A-Za-z]+)-([A-Za-z]+)-([A-Za-z]+)\]")


def tokenize_manifests(text: str) -> List[Dict[str, Any]]:
    """Extract [P-R-S] LatinMandell manifests and grade each."""
    tokens = []
    for m in _TRIPLE.finditer(text or ""):
        full, p, r, s = m.group(0), m.group(1), m.group(2), m.group(3)
        harm = evaluate_harmonic_link(p, r, s)
        tokens.append({
            "type": "LATINMANDELL_MANIFEST",
            "raw": full,
            "morphemes": {"prefix": p.lower(), "root": r.lower(), "suffix": s.lower()},
            "harmony_grade": harm["grade"],
            "entropy": harm["entropy"],
            "status": harm["status"],
            "diagnostic": harm["reason"],
            "detail": harm,
        })
    return tokens


def smoke() -> bool:
    print("=== HARMONIC LINK SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}")
        r.append(bool(ok))
    t1 = tokenize_manifests("Execute the [Omni-fac-ure] immediately.")
    rec("perfect Omni-fac-ure", t1 and "Perfect" in t1[0]["harmony_grade"])
    t2 = tokenize_manifests("This causes a [Hyper-magn-ity] state.")
    rec("collision Hyper-magn", t2 and ("OK" in t2[0]["harmony_grade"] or t2[0]["entropy"] >= 0.5))
    t3 = tokenize_manifests("Initialize the [Trans-xero-dell] protocol.")
    rec("leight Trans-xero", t3 and "Leight" in t3[0]["harmony_grade"])
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
