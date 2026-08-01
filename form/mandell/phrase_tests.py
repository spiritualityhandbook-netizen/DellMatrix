#!/usr/bin/env python3
"""Bidirectional EN ↔ Mandell hit-rate checks for stable phrases."""

from __future__ import annotations

from typing import List, Tuple
import sys

from form.mandell.phrases import match_phrase, PHRASES
from form.mandell.bridge import to_english, to_mandell

# Fixed sample set for hit-rate measurement
SAMPLES: List[str] = [
    "create an idea called business",
    "grow ideas 2",
    "save",
    "load",
    "show me",
    "visual",
    "walk forward",
    "turn left",
    "sit down",
    "stand up",
    "smile",
    "status",
    "help",
    "proposals",
    "confirm all",
    "reject all",
    "sphere",
    "cube",
    "core",
    "flower",
    "lattice",
    "enhance on",
    "pulse",
    "sandbox off",
    "acceptance",
]


def hit_rate() -> Tuple[int, int, List[str]]:
    ok = 0
    misses: List[str] = []
    for s in SAMPLES:
        m = match_phrase(s)
        if m and m.get("mandel"):
            ok += 1
        else:
            misses.append(s)
    return ok, len(SAMPLES), misses


def roundtrip_sample(english: str) -> dict:
    m = match_phrase(english)
    mandel = m["mandel"] if m else to_mandell(english)
    back = to_english(mandel) if mandel else ""
    return {
        "english": english,
        "mandel": mandel,
        "back": back,
        "hit": bool(m),
    }


def smoke() -> bool:
    print("=== PHRASE HIT-RATE SMOKE ===")
    ok, total, misses = hit_rate()
    rate = ok / total if total else 0.0
    print(f"hits: {ok}/{total}  rate={rate:.2%}")
    if misses:
        print("misses:")
        for m in misses[:10]:
            print(f"  - {m}")
    # require strong coverage on the fixed set
    passed = rate >= 0.80
    print("PASS" if passed else "FAIL")
    return passed


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    ok, total, misses = hit_rate()
    print(f"{ok}/{total}")
    for s in SAMPLES[:5]:
        print(roundtrip_sample(s))


if __name__ == "__main__":
    main()
