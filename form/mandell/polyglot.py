#!/usr/bin/env python3
"""
Polyglot bridge — other languages → same Dell layer.

Later goal: any two languages meet in Mandell operators.
Now: expanded ES/FR maps → English intent → Mandell seed.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import re

from .phrases import match_phrase
from .bridge import to_mandell

ES_MAP = [
    (r"^(?:crea|crear|haz)\s+(?:una\s+)?(?:idea\s+)?(?:llamada\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:guarda|guardar|salvar)$", "save"),
    (r"^(?:carga|cargar|restaurar)$", "load"),
    (r"^(?:crece|crecer|evoluciona)(?:\s+(\d+))?$", "grow ideas {x}"),
    (r"^(?:camina|avanzar)(?:\s+(\d+))?$", "walk forward {x}"),
    (r"^(?:corre)$", "run"),
    (r"^(?:para|detener)$", "stop"),
    (r"^(?:gira\s+izquierda|vuelta\s+izquierda)$", "turn left"),
    (r"^(?:gira\s+derecha|vuelta\s+derecha)$", "turn right"),
    (r"^(?:sientate|sentarse)$", "sit down"),
    (r"^(?:levantate|levantarse)$", "stand up"),
    (r"^(?:sonr[ií]e|sonreir)$", "smile"),
    (r"^(?:ayuda|help)$", "help"),
    (r"^(?:muestra|mostrar|ver)$", "show me"),
    (r"^(?:estado|status)$", "status"),
    (r"^(?:visual|panel)$", "visual"),
    (r"^(?:propuestas|vivero)$", "proposals"),
    (r"^(?:confirma\s+todo)$", "confirm all"),
    (r"^(?:rechaza\s+todo)$", "reject all"),
    (r"^(?:esfera)$", "sphere"),
    (r"^(?:cubo)$", "cube"),
    (r"^(?:nucleo|n[uú]cleo)$", "core"),
    (r"^(?:flor)$", "flower"),
    (r"^(?:ret[ií]cula|lattice)$", "lattice"),
    (r"^(?:clasifica|rank|ordenar)$", "rank"),
    (r"^(?:macro)(?:\s+(\d+))?$", "macro {x}"),
    (r"^(?:repite|replay)(?:\s+(\d+))?$", "replay {x}"),
    (r"^(?:destila|resumir)\s+(.+)$", "distill {x}"),
    (r"^(?:aceptaci[oó]n|acceptance)$", "acceptance"),
]

FR_MAP = [
    (r"^(?:cr[eé]e|cr[eé]er)\s+(?:une\s+)?(?:id[eé]e\s+)?(?:appel[eé]e\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:sauvegarde|sauver)$", "save"),
    (r"^(?:charge|charger)$", "load"),
    (r"^(?:grandis|évoluer)(?:\s+(\d+))?$", "grow ideas {x}"),
    (r"^(?:marche|avancer)(?:\s+(\d+))?$", "walk forward {x}"),
    (r"^(?:cours|courir)$", "run"),
    (r"^(?:arr[eê]te|stop)$", "stop"),
    (r"^(?:tourne\s+[aà]\s+gauche)$", "turn left"),
    (r"^(?:tourne\s+[aà]\s+droite)$", "turn right"),
    (r"^(?:assieds[- ]toi|s'asseoir)$", "sit down"),
    (r"^(?:l[eè]ve[- ]toi|se lever)$", "stand up"),
    (r"^(?:sourire)$", "smile"),
    (r"^(?:aide|help)$", "help"),
    (r"^(?:montre|afficher)$", "show me"),
    (r"^(?:statut|status)$", "status"),
    (r"^(?:visuel|panel)$", "visual"),
    (r"^(?:propositions|p[eé]pini[eè]re)$", "proposals"),
    (r"^(?:confirme\s+tout)$", "confirm all"),
    (r"^(?:rejette\s+tout)$", "reject all"),
    (r"^(?:sph[eè]re)$", "sphere"),
    (r"^(?:cube)$", "cube"),
    (r"^(?:noyau|core)$", "core"),
    (r"^(?:fleur)$", "flower"),
    (r"^(?:treillis|lattice)$", "lattice"),
    (r"^(?:classe|rank|ordonner)$", "rank"),
    (r"^(?:macro)(?:\s+(\d+))?$", "macro {x}"),
    (r"^(?:rejoue|replay)(?:\s+(\d+))?$", "replay {x}"),
    (r"^(?:distille|r[eé]sume)\s+(.+)$", "distill {x}"),
    (r"^(?:acceptation|acceptance)$", "acceptance"),
]

LANG_MAPS = {
    "es": ES_MAP,
    "spanish": ES_MAP,
    "fr": FR_MAP,
    "french": FR_MAP,
}


def normalize_lang(lang: str) -> str:
    return (lang or "en").lower().strip()


def list_langs() -> List[str]:
    return sorted({k for k in LANG_MAPS if len(k) <= 7})


def to_english_from(lang: str, text: str) -> Optional[str]:
    maps = LANG_MAPS.get(normalize_lang(lang))
    if not maps:
        return None
    lower = (text or "").strip().lower()
    for pattern, eng_t in maps:
        m = re.match(pattern, lower, re.I)
        if not m:
            continue
        x = m.group(1).strip() if m.lastindex and m.group(1) else "1"
        return eng_t.replace("{x}", x).replace("  ", " ").strip()
    return None


def bridge_lang(lang: str, text: str) -> Dict[str, str]:
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
