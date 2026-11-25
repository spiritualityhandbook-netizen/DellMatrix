"""
Snap contract — why something can snap into Dell Matrix.

Snap is allowed only when the candidate resonates with foundation:
- respects Floor
- carries Manifest shape (term + manor + dell) or binds to one
- offline-safe / no Floor mutation
- dual-output aware (structure vs display)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from form.mandell.floor import FLOOR, assert_floor_intact
from form.mandell.manifest import Manifest


@dataclass
class SnapCandidate:
    name: str
    kind: str  # language | tool | persona | cube | doc | growth | other
    manifest: Optional[Manifest] = None
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SnapResult:
    ok: bool
    reason: str
    port: Optional[str] = None


def resonate(candidate: SnapCandidate) -> SnapResult:
    """Relationship test — similar foundational shape → may snap."""
    try:
        assert_floor_intact()
    except RuntimeError as e:
        return SnapResult(False, str(e))

    if not candidate.name:
        return SnapResult(False, "unnamed candidate")

    # Floor-hostile payload rejected
    blob = str(candidate.payload).lower() + " " + candidate.name.lower()
    if "override floor" in blob or "remove floor" in blob:
        return SnapResult(False, "Floor hostile")

    if candidate.manifest is None and candidate.kind not in ("doc", "cube", "other"):
        # tools/personas/growth should bind a Manifest for tight snap
        return SnapResult(False, "missing Manifest binding")

    if candidate.manifest is not None:
        if not (0 <= candidate.manifest.dell <= 50):
            return SnapResult(False, "Dell out of True range")

    return SnapResult(True, "resonance ok", port=candidate.kind)
