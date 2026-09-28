"""True Dell registry — numbered operators + manors.

Namespaces
  CORE_I   00-50  locked action spine
  CORE_II  51-99  instruction architecture (formalized)
  ADDRESS  100-999 reserved until DVS promotion
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from .core_ii import CORE_II

DELLS: Dict[int, Dict[str, str]] = {
    0: {"name": "Nova", "manor": "Origin / fresh start"},
    1: {"name": "Initiate", "manor": "Root command / entry"},
    2: {"name": "Persona", "manor": "Identity / role"},
    3: {"name": "Logic", "manor": "Rules / constraints"},
    4: {"name": "Transform", "manor": "Convert / reshape"},
    5: {"name": "Tone", "manor": "Vibe / style"},
    6: {"name": "Cycle", "manor": "Rhythm / timing"},
    7: {"name": "Link", "manor": "Connect / reference"},
    8: {"name": "Create", "manor": "Instantiate"},
    9: {"name": "Show", "manor": "Render / output"},
    10: {"name": "Keep", "manor": "Pin / persist"},
    11: {"name": "Architect", "manor": "Schema / blueprint"},
    12: {"name": "Test", "manor": "Validate / assert"},
    13: {"name": "Loop", "manor": "Iterate until"},
    14: {"name": "Bind", "manor": "Attach / semantic edge"},
    15: {"name": "Map", "manor": "Coordinate / index"},
    16: {"name": "Decay", "manor": "Discard / expire"},
    17: {"name": "Shadow", "manor": "Background parallel"},
    18: {"name": "Mirror", "manor": "Compare / diff"},
    19: {"name": "Drive", "manor": "Direction / intensity"},
    20: {"name": "Alpha", "manor": "Close / finalize"},
    21: {"name": "Merge", "manor": "Two → one"},
    22: {"name": "Split", "manor": "One → parts"},
    23: {"name": "Lock", "manor": "Freeze immutable"},
    24: {"name": "Unlock", "manor": "Release lock"},
    25: {"name": "Pulse", "manor": "Broadcast outward"},
    26: {"name": "Temp", "manor": "Cold / Warm / Hot planes"},
    27: {"name": "Checkpoint", "manor": "Snapshot state"},
    28: {"name": "Rollback", "manor": "Restore checkpoint"},
    29: {"name": "Compress", "manor": "Shrink payload"},
    30: {"name": "Expand", "manor": "Unfold"},
    31: {"name": "Simulate", "manor": "Dry-run"},
    32: {"name": "Pause", "manor": "Halt"},
    33: {"name": "Resume", "manor": "Continue"},
    34: {"name": "Stamp", "manor": "Time/order mark"},
    35: {"name": "Discover", "manor": "Scan structure"},
    36: {"name": "Inject", "manor": "Load into scope"},
    37: {"name": "Stream", "manor": "Chunked out"},
    38: {"name": "Distill", "manor": "Summarize"},
    39: {"name": "Schema", "manor": "Validate shape"},
    40: {"name": "TokenCount", "manor": "Cost measure"},
    41: {"name": "Sanitize", "manor": "Strip secrets"},
    42: {"name": "Retry", "manor": "Re-attempt"},
    43: {"name": "Fallback", "manor": "Safe path"},
    44: {"name": "Bridge", "manor": "External tool"},
    45: {"name": "Translate", "manor": "EN ↔ Mandell"},
    46: {"name": "Rank", "manor": "Score"},
    47: {"name": "Embed", "manor": "Vectorize"},
    48: {"name": "Macro", "manor": "Shortcut sequence"},
    49: {"name": "Profile", "manor": "Benchmark"},
    50: {"name": "Manifest", "manor": "Make real / bring into form"},
}

for _n, _row in CORE_II.items():
    DELLS[_n] = {"name": _row["name"], "manor": _row["manor"]}

CORE_I_MAX = 50
CORE_II_MAX = 99
ADDRESS_MAX = 999

NAMED = {
    "Bindell": 14,
    "Formadell": 8,
    "Evoludell": 4,
    "Harmonidell": 151,
    "Mirrordell": 18,
}


def namespace_of(n: int) -> str:
    if 0 <= n <= CORE_I_MAX:
        return "CORE_I"
    if CORE_I_MAX < n <= CORE_II_MAX:
        return "CORE_II"
    if CORE_II_MAX < n <= ADDRESS_MAX:
        return "ADDRESS_RESERVED"
    return "OUT_OF_RANGE"


def get_dell(n: int) -> Optional[Dict[str, Any]]:
    d = DELLS.get(n)
    if d:
        return {"dell": n, **d, "namespace": namespace_of(n)}
    if CORE_II_MAX < n <= ADDRESS_MAX:
        try:
            from .address_space import get_reserved
            return get_reserved(n)
        except Exception:
            return None
    return None


def lookup(name_or_num) -> Optional[Dict[str, Any]]:
    if isinstance(name_or_num, int):
        return get_dell(name_or_num)
    s = str(name_or_num).strip()
    if s.isdigit():
        return get_dell(int(s))
    if s in NAMED:
        return get_dell(NAMED[s])
    for n, d in DELLS.items():
        if d["name"].lower() == s.lower():
            return get_dell(n)
    try:
        from .address_space import RESERVED_DOMAIN
        for n, d in RESERVED_DOMAIN.items():
            if d["name"].lower() == s.lower():
                return get_dell(n)
    except Exception:
        pass
    return None


def active_core_count() -> int:
    return sum(1 for n in DELLS if n <= CORE_II_MAX)
