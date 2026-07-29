"""True Dell registry — numbered operators + manors."""

from __future__ import annotations
from typing import Dict, Any, Optional

# Primaries 00–26 locked · Extensions 27–50 formalized
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

NAMED = {
    "Bindell": 14,
    "Formadell": 8,
    "Evoludell": 4,
    "Harmonidell": 5,
    "Mirrordell": 18,
}


def get_dell(n: int) -> Optional[Dict[str, Any]]:
    d = DELLS.get(n)
    if not d:
        return None
    return {"dell": n, **d}


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
    return None
