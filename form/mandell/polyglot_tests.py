#!/usr/bin/env python3
"""ES/FR polyglot smoke — top phrases must map. Gate ≥ 0.70 per language."""

from __future__ import annotations

import sys
from form.mandell.polyglot import bridge_lang

ES_SAMPLES = [
    "crea una idea llamada prueba",
    "guarda",
    "cargar",
    "crece 2",
    "camina",
    "ayuda",
    "muestra",
    "estado",
    "esfera",
    "cubo",
    "propuestas",
    "clasifica",
    "macro",
    "confirma todo",
    "aceptación",
]

FR_SAMPLES = [
    "crée une idée appelée test",
    "sauvegarde",
    "charger",
    "marche",
    "aide",
    "montre",
    "sphère",
    "cube",
    "propositions",
    "classe",
    "macro",
    "confirme tout",
    "acceptation",
]


def _rate(lang: str, samples: list) -> tuple:
    ok = 0
    misses = []
    for s in samples:
        rep = bridge_lang(lang, s)
        if rep.get("ok") == "true" and rep.get("english"):
            ok += 1
        else:
            misses.append(s)
    return ok, len(samples), misses


def smoke() -> bool:
    print("=== POLYGLOT ES/FR SMOKE ===")
    results = []
    for lang, samples in (("es", ES_SAMPLES), ("fr", FR_SAMPLES)):
        ok, total, misses = _rate(lang, samples)
        rate = ok / total if total else 0.0
        print(f"{lang}: {ok}/{total}  rate={rate:.2%}")
        if misses:
            for m in misses[:8]:
                print(f"  miss: {m}")
        results.append(rate >= 0.70)
    passed = all(results)
    print("PASS" if passed else "FAIL")
    return passed


def main() -> None:
    sys.exit(0 if smoke() else 1)


if __name__ == "__main__":
    main()
