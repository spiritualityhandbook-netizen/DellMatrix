#!/usr/bin/env python3
"""
Polyglot bridge foundation — other languages → same Dell layer.

Later goal: any two languages meet in Mandell operators.
Now: small proof maps (ES, simple) → English intent → Mandell seed.
"""

from __future__ import annotations

from typing import Dict, Optional
import re

from .phrases import match_phrase
from .bridge import to_mandell

# surface phrase → English canonical (then phrases/Mandell)
# Keep small and honest — expand as tested.
ES_MAP = [
    (r"^(?:crea|crear|haz)\s+(?:una\s+)?(?:idea\s+)?(?:llamada\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:guarda|guardar|salvar)$", "save"),
    (r"^(?:carga|cargar|restaurar)$", "load"),
    (r"^(?:crece|crecer|evoluciona)(?:\s+(\d+))?$", "grow ideas {x}"),
    (r"^(?:camina|avanzar)$", "walk forward"),
    (r"^(?:sonr[ií]e|sonreir)$", "smile"),
    (r"^(?:ayuda|help)$", "help"),
    (r"^(?:muestra|mostrar|ver)$", "show me"),
    (r"^(?:estado|status)$", "status"),
]

FR_MAP = [
    (r"^(?:cr[eé]e|cr[eé]er)\s+(?:une\s+)?(?:id[eé]e\s+)?(?:appel[eé]e\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:sauvegarde|sauver)$", "save"),
    (r"^(?:charge|charger)$", "load"),
    (r"^(?:marche|avancer)$", "walk forward"),
    (r"^(?:sourire)$", "smile"),
    (r"^(?:aide|help)$", "help"),
    (r"^(?:montre|afficher)$", "show me"),
]

LANG_MAPS = {
    "es": ES_MAP,
    "es": ES_MAP,
    "spanish": ES_MAP,
    "fr": FR_MAP,
    "french": FR_MAP,
}


def normalize_lang(lang: str) -> str:
    return (lang or "en").lower().strip()


def to_english_from(lang: str, text: str) -> Optional[str]:
    """Map a supported language phrase → English canonical."""
    maps = LANG_MAPS.get(normalize_lang(lang))
    if not maps:
        return None
    lower = (text or "").strip().lower()
    for pattern, eng_t in maps:
        m = re.match(pattern, lower, re.I)
        if not m:
            continue
        x = m.group(1).strip() if m.lastindex and m.group(1) else "1"
        return eng_t.replace("{x}", x)
    return None


def bridge_lang(lang: str, text: str) -> Dict[str, str]:
    """lang text → english → mandell."""
    eng = to_english_from(lang, text)
    if not eng:
        return {
            "ok": "false",
            "lang": lang,
            "input": text,
            "english": "",
            "mandel": "",
            "note": "no map yet for this phrase/language",
        }
    phrase = match_phrase(eng)
    mandel = phrase["mandel"] if phrase else to_mandell(eng)
    return {
        "ok": "true",
        "lang": lang,
        "input": text,
        "english": eng,
        "mandel": mandel,
        "note": "via Dell bridge layer",
    }
