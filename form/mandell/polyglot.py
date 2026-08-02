#!/usr/bin/env python3
"""
Polyglot bridge — natural languages → same Dell layer.

Core Mandell linguistic doors:
  EN (primary) · LA (Latin — core Mandell root) · ES · FR

All map: phrase → English intent → Mandell seed → executor.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import re

from .phrases import match_phrase
from .bridge import to_mandell

# Latin — core Mandell root language
LA_MAP = [
    (r"^(?:crea|creare|fac|facere)\s+(?:ideam\s+)?(?:nomine\s+|vocatam\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:serva|servare|conserva|conservare)$", "save"),
    (r"^(?:onera|onerare|restaura|restaurare|recupera)$", "load"),
    (r"^(?:cresce|crescere|auge|augere)(?:\s+(\d+))?$", "grow ideas {x}"),
    (r"^(?:ambula|ambulare|vade)(?:\s+(\d+))?$", "walk forward {x}"),
    (r"^(?:curre|currere)$", "run"),
    (r"^(?:siste|sistere|para|parare|sta)$", "stop"),
    (r"^(?:flecte\s+sinistr(?:a|orsum)|sinistrorsum)$", "turn left"),
    (r"^(?:flecte\s+dextr(?:a|orsum)|dextrorsum)$", "turn right"),
    (r"^(?:sede|sedere)$", "sit down"),
    (r"^(?:surge|surgere|sta\s+rectus)$", "stand up"),
    (r"^(?:sali|salire)$", "jump"),
    (r"^(?:ride|ridere)$", "smile"),
    (r"^(?:quiesce|tranquillus)$", "calm"),
    (r"^(?:attende|focus)$", "focus"),
    (r"^(?:adiuva|adiuvare|auxilium|help)$", "help"),
    (r"^(?:monstra|monstrare|ostende|vide)$", "show me"),
    (r"^(?:status|ubi\s+sum)$", "status"),
    (r"^(?:visuale|visual|tabula)$", "visual"),
    (r"^(?:propositiones|seminarium|pendentes)$", "proposals"),
    (r"^(?:confirma\s+omnia)$", "confirm all"),
    (r"^(?:reice\s+omnia|rejice\s+omnia)$", "reject all"),
    (r"^(?:sphaera)$", "sphere"),
    (r"^(?:cubus)$", "cube"),
    (r"^(?:nucleus|cor)$", "core"),
    (r"^(?:flos)$", "flower"),
    (r"^(?:reticulum|cancelli|lattice)$", "lattice"),
    (r"^(?:alterna|toggle)$", "toggle"),
    (r"^(?:ordina|rank|ordina\s+propositiones)$", "rank"),
    (r"^(?:macro)(?:\s+(\d+))?$", "macro {x}"),
    (r"^(?:repete|repetere|replay)(?:\s+(\d+))?$", "replay {x}"),
    (r"^(?:destilla|destillare|compende)\s+(.+)$", "distill {x}"),
    (r"^(?:acceptatio|acceptance)$", "acceptance"),
    (r"^(?:linguae|lang\s+list)$", "lang list"),
    (r"^(?:pulsus|pulse)$", "pulse"),
    (r"^(?:enhance\s+on|auge\s+on)$", "enhance on"),
    (r"^(?:enhance\s+off|auge\s+off)$", "enhance off"),
    (r"^(?:sandbox\s+on|arca\s+on)$", "sandbox on"),
    (r"^(?:sandbox\s+off|arca\s+off)$", "sandbox off"),
    (r"^(?:concha|shell)(?:\s+(\d+))?$", "shell {x}"),
    (r"^(?:chorda|chord)(?:\s+(-?\d+)\s+(-?\d+))?$", "chord {x}"),
]

ES_MAP = [
    (r"^(?:crea|crear|haz)\s+(?:una\s+)?(?:idea\s+)?(?:llamada\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:guarda|guardar|salvar)(?:\s+sesi[oó]n)?$", "save"),
    (r"^(?:carga|cargar|restaurar)(?:\s+sesi[oó]n)?$", "load"),
    (r"^(?:crece|crecer|evoluciona)(?:\s+(?:ideas?\s+)?(\d+))?$", "grow ideas {x}"),
    (r"^(?:camina|avanzar|anda)(?:\s+(\d+))?$", "walk forward {x}"),
    (r"^(?:corre|correr)$", "run"),
    (r"^(?:para|detener|alto)$", "stop"),
    (r"^(?:gira\s+a?\s*izquierda|vuelta\s+izquierda)$", "turn left"),
    (r"^(?:gira\s+a?\s*derecha|vuelta\s+derecha)$", "turn right"),
    (r"^(?:sientate|si[eé]ntate|sentarse)$", "sit down"),
    (r"^(?:levantate|lev[aá]ntate|levantarse)$", "stand up"),
    (r"^(?:salta|saltar)$", "jump"),
    (r"^(?:sonr[ií]e|sonreir)$", "smile"),
    (r"^(?:calma|relajate)$", "calm"),
    (r"^(?:enfoca|concentra)$", "focus"),
    (r"^(?:ayuda|help)$", "help"),
    (r"^(?:muestra|mostrar|ver|ense[nñ]a)(?:\s+me)?$", "show me"),
    (r"^(?:estado|status|d[oó]nde\s+estoy)$", "status"),
    (r"^(?:visual|panel)$", "visual"),
    (r"^(?:propuestas|vivero|pendientes)$", "proposals"),
    (r"^(?:confirma\s+todo)$", "confirm all"),
    (r"^(?:rechaza\s+todo)$", "reject all"),
    (r"^(?:esfera)$", "sphere"),
    (r"^(?:cubo)$", "cube"),
    (r"^(?:nucleo|n[uú]cleo)$", "core"),
    (r"^(?:flor)$", "flower"),
    (r"^(?:ret[ií]cula|lattice|rejilla)$", "lattice"),
    (r"^(?:alternar|toggle)$", "toggle"),
    (r"^(?:clasifica|rank|ordenar|ordena)$", "rank"),
    (r"^(?:macro)(?:\s+(\d+))?$", "macro {x}"),
    (r"^(?:repite|replay|reproducir)(?:\s+(\d+))?$", "replay {x}"),
    (r"^(?:destila|resumir|resume)\s+(.+)$", "distill {x}"),
    (r"^(?:aceptaci[oó]n|acceptance)$", "acceptance"),
    (r"^(?:idiomas|lenguas|lang\s+list)$", "lang list"),
    (r"^(?:pulso|pulse)$", "pulse"),
    (r"^(?:enhance\s+on|mejora\s+on)$", "enhance on"),
    (r"^(?:enhance\s+off|mejora\s+off)$", "enhance off"),
    (r"^(?:sandbox\s+on|caja\s+on)$", "sandbox on"),
    (r"^(?:sandbox\s+off|caja\s+off)$", "sandbox off"),
    (r"^(?:cascar[oó]n|shell)(?:\s+(\d+))?$", "shell {x}"),
    (r"^(?:acorde|chord)(?:\s+(-?\d+)\s+(-?\d+))?$", "chord {x}"),
]

FR_MAP = [
    (r"^(?:cr[eé]e|cr[eé]er|fais)\s+(?:une\s+)?(?:id[eé]e\s+)?(?:appel[eé]e\s+)?(.+)$", "create an idea called {x}"),
    (r"^(?:sauvegarde|sauver|enregistrer)(?:\s+session)?$", "save"),
    (r"^(?:charge|charger|restaurer)(?:\s+session)?$", "load"),
    (r"^(?:grandis|grandir|évoluer)(?:\s+(?:id[eé]es?\s+)?(\d+))?$", "grow ideas {x}"),
    (r"^(?:marche|avancer)(?:\s+(\d+))?$", "walk forward {x}"),
    (r"^(?:cours|courir)$", "run"),
    (r"^(?:arr[eê]te|stop|halte)$", "stop"),
    (r"^(?:tourne\s+[aà]\s+gauche)$", "turn left"),
    (r"^(?:tourne\s+[aà]\s+droite)$", "turn right"),
    (r"^(?:assieds[- ]toi|s'asseoir)$", "sit down"),
    (r"^(?:l[eè]ve[- ]toi|se lever)$", "stand up"),
    (r"^(?:saute|sauter)$", "jump"),
    (r"^(?:sourire|souris)$", "smile"),
    (r"^(?:calme|détends[- ]toi)$", "calm"),
    (r"^(?:focus|concentre)$", "focus"),
    (r"^(?:aide|help)$", "help"),
    (r"^(?:montre|afficher|voir)(?:\s+moi)?$", "show me"),
    (r"^(?:statut|status|o[uù]\s+suis[- ]je)$", "status"),
    (r"^(?:visuel|panel)$", "visual"),
    (r"^(?:propositions|p[eé]pini[eè]re|en\s+attente)$", "proposals"),
    (r"^(?:confirme\s+tout)$", "confirm all"),
    (r"^(?:rejette\s+tout)$", "reject all"),
    (r"^(?:sph[eè]re)$", "sphere"),
    (r"^(?:cube)$", "cube"),
    (r"^(?:noyau|core)$", "core"),
    (r"^(?:fleur)$", "flower"),
    (r"^(?:treillis|lattice|grille)$", "lattice"),
    (r"^(?:bascule|toggle)$", "toggle"),
    (r"^(?:classe|rank|ordonner|ordonne)$", "rank"),
    (r"^(?:macro)(?:\s+(\d+))?$", "macro {x}"),
    (r"^(?:rejoue|replay|rejouer)(?:\s+(\d+))?$", "replay {x}"),
    (r"^(?:distille|r[eé]sume|r[eé]sumer)\s+(.+)$", "distill {x}"),
    (r"^(?:acceptation|acceptance)$", "acceptance"),
    (r"^(?:langues|lang\s+list)$", "lang list"),
    (r"^(?:impulsion|pulse)$", "pulse"),
    (r"^(?:enhance\s+on|am[eé]liore\s+on)$", "enhance on"),
    (r"^(?:enhance\s+off|am[eé]liore\s+off)$", "enhance off"),
    (r"^(?:sandbox\s+on|bac\s+on)$", "sandbox on"),
    (r"^(?:sandbox\s+off|bac\s+off)$", "sandbox off"),
    (r"^(?:coquille|shell)(?:\s+(\d+))?$", "shell {x}"),
    (r"^(?:accord|chord)(?:\s+(-?\d+)\s+(-?\d+))?$", "chord {x}"),
]

LANG_MAPS = {
    "la": LA_MAP,
    "latin": LA_MAP,
    "es": ES_MAP,
    "spanish": ES_MAP,
    "fr": FR_MAP,
    "french": FR_MAP,
}

# Core foundation: Latin is core Mandell root; ES/FR complete doors
FOUNDATION_LANGS = ("la", "es", "fr")
CORE_LANGS = ("la",)  # linguistic root of Mandell surface


def normalize_lang(lang: str) -> str:
    return (lang or "en").lower().strip()


def list_langs() -> List[str]:
    return sorted({k for k in LANG_MAPS if len(k) <= 7})


def foundation_complete() -> bool:
    return all(code in LANG_MAPS for code in FOUNDATION_LANGS)


def to_english_from(lang: str, text: str) -> Optional[str]:
    maps = LANG_MAPS.get(normalize_lang(lang))
    if not maps:
        return None
    lower = (text or "").strip().lower()
    for pattern, eng_t in maps:
        m = re.match(pattern, lower, re.I)
        if not m:
            continue
        if m.lastindex and m.lastindex >= 2 and m.group(1) and m.group(2):
            x = f"{m.group(1).strip()} {m.group(2).strip()}"
        elif m.lastindex and m.group(1):
            x = m.group(1).strip()
        else:
            x = "1"
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
        "core": "true" if normalize_lang(lang) in ("la", "latin") else "false",
    }
