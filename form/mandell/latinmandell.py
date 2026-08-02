#!/usr/bin/env python3
"""
LatinMandell — core morphological depth layer (new-age LatinMandell).

Not classical Latin scholarship. A practical Origin layer that:
  · uses classic Latin roots when useful / intuitive / practical
  · otherwise uses morphology (prefix-root-suffix) to comprehend
  · separates morpheme tokens with '-' for meaning (Com-man-dell)
  · maps surface words → sense → Dell
  · allows customize() bindings that persist with the session

Law: LatinMandell is core Origin structure, not optional flavor.
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
    "confirm": {"la": "confirmare", "sense": "make firm · establish as live", "dell": 50},
    "reject": {"la": "reicere", "sense": "cast back · refuse entry", "dell": 24},
    "tutorial": {"la": "tutor / via", "sense": "guided path of learning", "dell": 1},
    "visual": {"la": "visualis", "sense": "of sight · rendered form", "dell": 9},
    "nursery": {"la": "seminarium", "sense": "place where seedlings are held", "dell": 23},
}

# Custom bindings — session + persist v7
_CUSTOM: Dict[str, Dict[str, Any]] = {}


def normalize_key(word: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "", (word or "").lower().strip())


def export_customs() -> Dict[str, Dict[str, Any]]:
    """Snapshot for persist v7."""
    return {k: dict(v) for k, v in _CUSTOM.items()}


def import_customs(data: Optional[Dict[str, Any]]) -> int:
    """Restore customs from persist. Returns count loaded."""
    if not data or not isinstance(data, dict):
        return 0
    n = 0
    for k, v in data.items():
        if not isinstance(v, dict):
            continue
        key = normalize_key(str(k))
        if not key:
            continue
        _CUSTOM[key] = {
            "label": key,
            "la": v.get("la") or key,
            "dell": v.get("dell"),
            "term": v.get("term") or "",
            "sense": v.get("sense") or "custom LatinMandell function",
            "surface": v.get("surface") or key,
        }
        n += 1
    return n


def root_of(word: str) -> Optional[Dict[str, Any]]:
    """Deeper meaning of a surface word via LatinMandell."""
    raw = (word or "").strip()
    k = normalize_key(raw)
    if not k:
        return None

    # Hyphen / underscore morphology first when delimiters present
    if "-" in raw or "_" in raw:
        morph = _morph_depth(raw)
        if morph:
            return morph

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

    # Try forced Mandell morpheme split (Commandell → Com-man-dell)
    try:
        from .morpheme import force_mandell_morphemes, explain_morphemes
        forced = force_mandell_morphemes(raw)
        if "-" in forced and forced.lower() != raw.lower():
            return _morph_depth(forced)
    except Exception:
        pass

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


def _morph_depth(text: str) -> Optional[Dict[str, Any]]:
    """Hyphen-separated morpheme tokens → combined sense (new-age LatinMandell)."""
    try:
        from .morpheme import explain_morphemes, force_mandell_morphemes
    except Exception:
        return None
    forced = force_mandell_morphemes(text)
    payload = explain_morphemes(forced if "-" in forced else text)
    parts = payload.get("parts") or []
    if not parts:
        return None
    senses = [p["sense"] for p in parts if p.get("sense") and p["sense"] != "(open)"]
    labels = [p["morpheme"] for p in parts]
    kind_mix = "-".join(labels)
    combined = " · ".join(senses) if senses else "open morphology"
    # Prefer dell from any known full-word root of the joined form
    joined = normalize_key("".join(labels))
    dell = None
    if joined in ROOTS:
        dell = ROOTS[joined].get("dell")
    if joined in _CUSTOM:
        dell = _CUSTOM[joined].get("dell")
    return {
        "word": text,
        "la": kind_mix,
        "sense": combined,
        "dell": dell,
        "term": "",
        "custom": joined in _CUSTOM,
        "surface": text,
        "morphology": "hyphen-token LatinMandell",
        "parts": parts,
        "forced": forced,
    }


def deepen(text: str) -> List[Dict[str, Any]]:
    """Explain deeper LatinMandell senses for words / hyphen-tokens in a phrase."""
    text = text or ""
    # Keep hyphen compounds as single tokens
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}", text)
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
    Survives save/load when persist imports customs.
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
    term = r.get("term") or word.replace(" ", "_").replace("-", "_")[:24]
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
    if len(re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,}", text)) == 1 and not parts:
        r = root_of(text)
        parts = [r] if r else []
    return {
        "ok": True,
        "input": text,
        "roots": parts,
        "suggested_seeds": [s for s in (seed_for_root(p["word"]) for p in parts) if s],
        "note": "LatinMandell · classic roots when useful · '-' morpheme tokens · customize() binds",
    }


def format_explain(word_or_phrase: str) -> str:
    """Human-readable block for REPL."""
    rep = explain(word_or_phrase)
    if not rep.get("ok"):
        return rep.get("error") or "empty"
    lines = [f"LatinMandell · {rep['input']}"]
    for r in rep.get("roots") or []:
        dell = r.get("dell")
        dell_s = f"  dell={int(dell):02d}" if dell is not None else ""
        custom = "  [custom]" if r.get("custom") else ""
        lines.append(f"  {r.get('word')}")
        lines.append(f"    la: {r.get('la')}")
        lines.append(f"    sense: {r.get('sense')}{dell_s}{custom}")
        if r.get("parts"):
            for p in r["parts"]:
                lines.append(
                    f"      - {p.get('morpheme')} ({p.get('kind')}): {p.get('sense')}"
                )
    seeds = rep.get("suggested_seeds") or []
    if seeds:
        lines.append("  seeds: " + " · ".join(seeds))
    if not rep.get("roots"):
        lines.append("  (no root yet — try customize, or hyphen form like Com-man-dell)")
    return "\n".join(lines)


def smoke() -> bool:
    print("=== LATINMANDELL SMOKE ===")
    r = []
    def rec(name, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(bool(ok))
    clear_customs()
    rec("root create", root_of("create") is not None and root_of("create")["la"].startswith("crea"))
    rec("deepen phrase", len(deepen("create grow save")) >= 3)
    rec("customize", customize("lumen", dell=9, term="Show", sense="light made visible", la="lumen")["ok"])
    rec("custom root", root_of("lumen") is not None and root_of("lumen").get("custom") is True)
    rec("seed suggest", seed_for_root("create") is not None)
    rec("hyphen morph", root_of("Com-man-dell") is not None)
    snap = export_customs()
    clear_customs()
    rec("export had lumen", "lumen" in snap)
    n = import_customs(snap)
    rec("import customs", n >= 1 and root_of("lumen") is not None)
    clear_customs()
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
