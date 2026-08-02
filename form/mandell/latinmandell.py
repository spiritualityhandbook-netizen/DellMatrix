#!/usr/bin/env python3
"""
LatinMandell — core morphological depth layer.

Purpose:
  Use Latin roots and function to reveal deeper meaning of English
  (and other surface languages), and to customize words → Dell function.

Law:
  LatinMandell is core Origin structure, not optional flavor.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import re

# Surface word (EN-facing) → Latin root + deeper sense + optional default Dell
ROOTS: Dict[str, Dict[str, Any]] = {
    "create": {"la": "creare", "sense": "bring into being · call forth", "dell": 8},
    "make": {"la": "facere", "sense": "do · fashion · cause", "dell": 8},
    "idea": {"la": "idea / forma", "sense": "form held in mind · pattern", "dell": 8},
    "grow": {"la": "crescere", "sense": "increase by living process", "dell": 13},
    "evolve": {"la": "evolvere", "sense": "unroll · unfold what is latent", "dell": 4},
    "transform": {"la": "transformare", "sense": "change form across a boundary", "dell": 4},
    "map": {"la": "mappa / ordinare", "sense": "place in ordered relation", "dell": 15},
    "show": {"la": "monstrare", "sense": "cause to be seen", "dell": 9},
    "see": {"la": "videre", "sense": "perceive with clarity", "dell": 9},
    "keep": {"la": "servare", "sense": "guard · preserve continuity", "dell": 10},
    "save": {"la": "servare", "sense": "hold safe across time", "dell": 10},
    "load": {"la": "onerare / restaurare", "sense": "place burden · restore state", "dell": 28},
    "walk": {"la": "ambulare", "sense": "move by measured steps", "dell": 19},
    "run": {"la": "currere", "sense": "move with urgency", "dell": 19},
    "stop": {"la": "sistere", "sense": "cause motion to stand", "dell": 32},
    "bind": {"la": "ligare / vincire", "sense": "fasten into relation", "dell": 14},
    "link": {"la": "nectere", "sense": "join by connection", "dell": 7},
    "merge": {"la": "mergere / miscere", "sense": "plunge together · mix into one", "dell": 21},
    "split": {"la": "findere / dividere", "sense": "cleave into parts", "dell": 22},
    "lock": {"la": "claudere", "sense": "close against change", "dell": 23},
    "unlock": {"la": "aperire", "sense": "open what was closed", "dell": 24},
    "pulse": {"la": "pulsus", "sense": "stroke outward · beat of life", "dell": 25},
    "decay": {"la": "cadere / corrumpi", "sense": "fall away from force", "dell": 16},
    "mirror": {"la": "speculum", "sense": "show by reflection", "dell": 18},
    "shadow": {"la": "umbra", "sense": "parallel presence without full body", "dell": 17},
    "test": {"la": "probare", "sense": "prove by trial", "dell": 12},
    "logic": {"la": "ratio / logos", "sense": "ordered reason · rule-structure", "dell": 3},
    "person": {"la": "persona", "sense": "mask · role through which being speaks", "dell": 2},
    "origin": {"la": "origo / nova", "sense": "source · rising point", "dell": 0},
    "loop": {"la": "circulus / iterare", "sense": "return path · repeat until", "dell": 13},
    "cycle": {"la": "cyclus / orbis", "sense": "ring of recurrence", "dell": 6},
    "rank": {"la": "ordo / ordinare", "sense": "place by worth or order", "dell": 46},
    "distill": {"la": "destillare", "sense": "drop the essence clear of dross", "dell": 38},
    "compress": {"la": "comprimere", "sense": "press into smaller form", "dell": 29},
    "expand": {"la": "expandere", "sense": "spread outward from center", "dell": 30},
    "inject": {"la": "inicere", "sense": "throw into the midst", "dell": 36},
    "schema": {"la": "schema / forma", "sense": "shape that validates structure", "dell": 39},
    "manifest": {"la": "manifestare", "sense": "make evident in the world", "dell": 50},
    "sphere": {"la": "sphaera", "sense": "all-around whole · rounded totality", "dell": 15},
    "cube": {"la": "cubus", "sense": "stable measure · squared body", "dell": 15},
    "core": {"la": "cor / nucleus", "sense": "heart · innermost kernel", "dell": 15},
    "flower": {"la": "flos", "sense": "unfolding peak of a living form", "dell": 15},
    "lattice": {"la": "reticulum", "sense": "net of ordered relations", "dell": 15},
    "bridge": {"la": "pons", "sense": "path across a divide", "dell": 44},
    "translate": {"la": "transferre", "sense": "carry meaning across tongues", "dell": 45},
    "sanitize": {"la": "purgare", "sense": "cleanse of harm or secret", "dell": 41},
    "fallback": {"la": "recedere ad tutum", "sense": "return to the safe path", "dell": 43},
    "accept": {"la": "acceptare", "sense": "take as valid · receive into form", "dell": 50},
}

# Custom bindings: latin_or_label → {dell, term, sense, surface}
# Filled at runtime / session; can be extended without changing ROOTS.
_CUSTOM: Dict[str, Dict[str, Any]] = {}


def normalize_key(word: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "", (word or "").lower().strip())


def root_of(word: str) -> Optional[Dict[str, Any]]:
    """Deeper meaning of a surface word via LatinMandell."""
    k = normalize_key(word)
    if not k:
        return None
    if k in _CUSTOM:
        c = _CUSTOM[k]
        return {
            "word": word,
            "la": c.get("la") or c.get("label") or k,
            "sense": c.get("sense", "custom function"),
            "dell": c.get("dell"),
            "term": c.get("term", ""),
            "custom": True,
            "surface": c.get("surface", word),
        }
    if k in ROOTS:
        r = ROOTS[k]
        return {
            "word": word,
            "la": r["la"],
            "sense": r["sense"],
            "dell": r.get("dell"),
            "term": "",
            "custom": False,
            "surface": word,
        }
    # light morphology hints for common EN endings
    for suffix, note in (
        ("tion", "act or state of (← Latin -tio)"),
        ("sion", "act or state of (← Latin -sio)"),
        ("ment", "result or means (← Latin -mentum)"),
        ("able", "capable of (← Latin -abilis)"),
        ("ible", "capable of (← Latin -ibilis)"),
        ("ous", "full of (← Latin -osus)"),
        ("ive", "tending to (← Latin -ivus)"),
    ):
        if k.endswith(suffix) and len(k) > len(suffix) + 2:
            stem = k[: -len(suffix)]
            base = root_of(stem)
            return {
                "word": word,
                "la": (base["la"] + f" + -{suffix}") if base else f"(stem {stem}) -{suffix}",
                "sense": (base["sense"] + f" · {note}") if base else note,
                "dell": base.get("dell") if base else None,
                "term": "",
                "custom": False,
                "surface": word,
                "morphology": note,
            }
    return None


def deepen(text: str) -> List[Dict[str, Any]]:
    """Explain deeper LatinMandell senses for words in a phrase."""
    tokens = re.findall(r"[A-Za-z_]{2,}", text or "")
    out: List[Dict[str, Any]] = []
    seen = set()
    for t in tokens:
        k = normalize_key(t)
        if k in seen:
            continue
        seen.add(k)
        r = root_of(t)
        if r:
            out.append(r)
    return out


def customize(
    label: str,
    *,
    dell: Optional[int] = None,
    term: str = "",
    sense: str = "",
    la: str = "",
    surface: str = "",
) -> Dict[str, Any]:
    """
    Bind a custom word/function in LatinMandell.
    label may be Latin or any surface token; becomes a callable meaning node.
    """
    k = normalize_key(label)
    if not k:
        return {"ok": False, "error": "empty label"}
    entry = {
        "label": k,
        "la": la or label,
        "dell": dell,
        "term": term or (label[:24] if not term else term),
        "sense": sense or f"custom LatinMandell function · {label}",
        "surface": surface or label,
    }
    _CUSTOM[k] = entry
    return {"ok": True, "custom": entry}


def list_customs() -> List[Dict[str, Any]]:
    return [dict(v) for v in _CUSTOM.values()]


def clear_customs() -> None:
    _CUSTOM.clear()


def seed_for_root(word: str) -> Optional[str]:
    """If root has a Dell, return a minimal seed suggestion."""
    r = root_of(word)
    if not r or r.get("dell") is None:
        return None
    d = int(r["dell"])
    term = r.get("term") or word.replace(" ", "_")[:24]
    # prefer registry name if available
    try:
        from .registry import get_dell
        info = get_dell(d)
        if info and info.get("name"):
            term = info["name"]
    except Exception:
        pass
    return f"{d:02d}[{term}]"


def explain(word_or_phrase: str) -> Dict[str, Any]:
    """Full LatinMandell explanation payload."""
    text = (word_or_phrase or "").strip()
    if not text:
        return {"ok": False, "error": "empty"}
    parts = deepen(text)
    if len(text.split()) == 1 and not parts:
        r = root_of(text)
        parts = [r] if r else []
    return {
        "ok": True,
        "input": text,
        "roots": parts,
        "suggested_seeds": [s for s in (seed_for_root(p["word"]) for p in parts) if s],
        "note": "LatinMandell deeper meaning · customize() binds new function",
    }


def smoke() -> bool:
    print("=== LATINMANDELL SMOKE ===")
    r = []
    def rec(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(bool(ok))
    rec("root create", root_of("create") is not None and root_of("create")["la"].startswith("crea"))
    rec("deepen phrase", len(deepen("create grow save")) >= 3)
    rec("customize", customize("lumen", dell=9, term="Show", sense="light made visible", la="lumen")["ok"])
    rec("custom root", root_of("lumen") is not None and root_of("lumen").get("custom") is True)
    rec("seed suggest", seed_for_root("create") is not None)
    clear_customs()
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
