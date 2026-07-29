"""
Dell Matrix — foundation snap host.

Holds foundational ports. Everything that works with the system
snaps here because it shares Mandell relationship (Manifest / Floor).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from form.mandell.floor import floor_status, assert_floor_intact
from form.mandell.registry import DELLS
from form.mandell.manifest import Manifest, manifest_from_dell
from .snap import SnapCandidate, SnapResult, resonate


# Foundational ports — what the matrix is built to receive
FOUNDATION_PORTS = (
    "language",   # Mandell itself
    "registry",   # Dell True table
    "growth",     # DuoBeta / Voynich-structural
    "cube",       # personal harmonic cube
    "main",       # main matrix link
    "persona",    # docked AI personas
    "tool",       # tools created with Mandell
    "doc",        # documents / seeds user gives
    "pipeline",   # confirm queues
    "other",
)


@dataclass
class DellMatrix:
    """Core bottom — snap host."""

    snapped: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)

    def __post_init__(self):
        assert_floor_intact()
        for p in FOUNDATION_PORTS:
            self.snapped.setdefault(p, [])
        # Foundation always holds language + registry manifests
        if not self.snapped["language"]:
            m = manifest_from_dell(1, "Mandell")
            self.snapped["language"].append(
                {"name": "Mandell", "manifest": m.to_dict() if m else None}
            )
        if not self.snapped["registry"]:
            self.snapped["registry"].append(
                {"name": "TrueRegistry", "count": len(DELLS)}
            )

    def snap(self, candidate: SnapCandidate) -> SnapResult:
        result = resonate(candidate)
        if not result.ok:
            self.log.append(f"REJECT {candidate.name}: {result.reason}")
            return result
        port = result.port or candidate.kind or "other"
        if port not in self.snapped:
            port = "other"
        entry = {
            "name": candidate.name,
            "kind": candidate.kind,
            "manifest": candidate.manifest.to_dict() if candidate.manifest else None,
            "payload": dict(candidate.payload),
        }
        # replace same name on port
        self.snapped[port] = [e for e in self.snapped[port] if e["name"] != candidate.name]
        self.snapped[port].append(entry)
        self.log.append(f"SNAP {candidate.name} → {port}")
        return result

    def list_port(self, port: str) -> List[Dict[str, Any]]:
        return list(self.snapped.get(port, []))

    def understand(self) -> Dict[str, Any]:
        """Program self-description — not human consciousness."""
        return {
            "self": "DellMatrix",
            "role": "foundation snap host",
            "requires": "Mandell language",
            "floor": floor_status(),
            "ports": {p: len(self.snapped.get(p, [])) for p in FOUNDATION_PORTS},
            "dell_count": len(DELLS),
            "log_tail": self.log[-8:],
        }

    def status(self) -> Dict[str, Any]:
        return self.understand()
