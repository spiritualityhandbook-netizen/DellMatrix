#!/usr/bin/env python3
"""Polyglot foundation smoke — LA (core) + ES + FR. Gate ≥ 0.90 each."""

from __future__ import annotations

import sys
from form.mandell.polyglot import bridge_lang, foundation_complete, list_langs

LA_SAMPLES = [
    "crea ideam nomine negotium",
    "serva",
    "onera",
    "cresce 2",
    "ambula",
    "curre",
    "siste",
    "flecte sinistrorsum",
    "flecte dextrorsum",
    "sede",
    "surge",
    "ride",
    "adiuva",
    "monstra",
    "status",
    "visuale",
    "sphaera",
    "cubus",
    "nucleus",
    "flos",
    "reticulum",
    "propositiones",
    "ordina",
    "macro",
    "repete",
    "confirma omnia",
    "reice omnia",
    "acceptatio",
    "linguae",
    "pulsus",
    "destilla negotium",
]

ES_SAMPLES = [
    "crea una idea llamada prueba",
    "guarda",
    "cargar",
    "crece 2",
    "camina",
    "corre",
    "para",
    "gira izquierda",
    "esfera",
    "cubo",
    "propuestas",
    "clasifica",
    "macro",
    "confirma todo",
    "aceptación",
    "idiomas",
]

FR_SAMPLES = [
    "crée une idée appelée test",
    "sauvegarde",
    "charger",
    "grandis 2",
    "marche",
    "cours",
    "arrête",
    "sphère",
    "cube",
    "propositions",
    "classe",
    "macro",
    "confirme tout",
    "acceptation",
    "langues",
]

GATE = 0.90


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
    print("=== POLYGLOT LA+ES+FR FOUNDATION SMOKE ===")
    print(f"langs={list_langs()} foundation_complete={foundation_complete()}")
    results = []
    for lang, samples in (("la", LA_SAMPLES), ("es", ES_SAMPLES), ("fr", FR_SAMPLES)):
        ok, total, misses = _rate(lang, samples)
        rate = ok / total if total else 0.0
        print(f"{lang}: {ok}/{total}  rate={rate:.2%}  gate={GATE:.0%}")
        if misses:
            for m in misses[:12]:
                print(f"  miss: {m}")
        results.append(rate >= GATE)
    results.append(foundation_complete())
    passed = all(results)
    print("PASS" if passed else "FAIL")
    return passed


def main() -> None:
    sys.exit(0 if smoke() else 1)


if __name__ == "__main__":
    main()
