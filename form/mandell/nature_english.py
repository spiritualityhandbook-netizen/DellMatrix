#!/usr/bin/env python3
"""Nature of Code → English Brain paraphrase seeds.

Register with register() so everyday English maps to force tick / act-on-seen / neuroevo.
"""
from __future__ import annotations

from typing import List, Tuple
import re

NATURE_VERB_MAP = {
    "oscillate": "force tick",
    "oscillation": "force tick",
    "neuroevo": "neuroevo",
    "neuroevolution": "neuroevo",
    "evolve forces": "neuroevo",
    "act": "act",
    "seen": "act",
}

NATURE_PARAPHRASES: List[Tuple[str, str]] = [
    (r"^(?:force\s+tick|tick\s+forces|nature\s+tick|physics\s+tick|run\s+nature)$", "force tick"),
    (r"^(?:nature\s+status|show\s+nature|nature\s+bridge)$", "nature status"),
    (r"^(?:act\s+on\s+seen|act\s+on\s+what\s+i\s+see|do\s+something\s+with\s+(?:what\s+)?(?:i\s+)?see)$", "act list"),
    (r"^(?:list\s+seen|what\s+can\s+i\s+act\s+on|seen\s+list)$", "act list"),
    (r"^(?:act\s+inspect)(?:\s+(\d+))?$", "act inspect {1}"),
    (r"^(?:act\s+zoom)(?:\s+(\d+))?$", "act zoom {1}"),
    (r"^(?:act\s+force|pull\s+what\s+i\s+see|gravity\s+on\s+seen)(?:\s+(\d+))?$", "act force {1}"),
    (r"^(?:act\s+attend)(?:\s+(\d+))?$", "act attend {1}"),
    (r"^(?:act\s+nearest|go\s+to\s+seen|walk\s+to\s+seen)(?:\s+(\d+))?$", "act nearest {1}"),
    (r"^(?:neuroevo|neuro\s*evo|evolve\s+forces|evolve\s+force\s+field)(?:\s+(\d+))?$", "neuroevo {1}"),
    (r"^(?:oscillate|run\s+oscillation|breath\s+oscillation)$", "force tick"),
]

NATURE_EXPAND = [
    {"canonical": "force tick", "action": "force",
     "variants": ["force tick", "tick forces", "nature tick", "physics tick", "run nature", "please force tick"]},
    {"canonical": "act list", "action": "act",
     "variants": ["act on seen", "list seen", "what can i act on", "act on what i see"]},
    {"canonical": "neuroevo", "action": "neuroevo",
     "variants": ["neuroevo", "evolve forces", "neuro evolution", "evolve force field"]},
]

_REGISTERED = False


def register() -> bool:
    """Idempotent inject into english_brain banks."""
    global _REGISTERED
    if _REGISTERED:
        return True
    try:
        from form.mandell import english_brain as eb
        for k, v in NATURE_VERB_MAP.items():
            eb.VERB_MAP.setdefault(k, v)
        # avoid duplicate patterns
        existing = {p[0] for p in eb.PARAPHRASE_TO_CANONICAL}
        for pat, tmpl in NATURE_PARAPHRASES:
            if pat not in existing:
                eb.PARAPHRASE_TO_CANONICAL.append((pat, tmpl))
        # expand families
        canons = {f["canonical"] for f in eb.EXPAND_FAMILIES}
        for fam in NATURE_EXPAND:
            if fam["canonical"] not in canons:
                eb.EXPAND_FAMILIES.append(fam)
        _REGISTERED = True
        return True
    except Exception:
        return False


def smoke() -> bool:
    print("=== NATURE_ENGLISH SMOKE ===")
    ok = register()
    from form.mandell.english_brain import normalize_english
    n, path = normalize_english("please force tick")
    hit = "force tick" in (n or "")
    print(f"[{'PASS' if ok and hit else 'FAIL'}] normalize={n!r} path={path}")
    return ok and hit


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
