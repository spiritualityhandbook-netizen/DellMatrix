"""
Dell Matrix — foundation snap host (L3).

14[Bind] : 12[Test] >> 35[Discover] :: SnapHost

Everything snaps here through Mandell relationship (Manifest / Floor).
L3: health verify, required snap names, full inventory.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from form.mandell.floor import floor_status, assert_floor_intact, FLOOR
from form.mandell.registry import DELLS
from form.mandell.manifest import Manifest, manifest_from_dell
from .snap import SnapCandidate, SnapResult, resonate

FOUNDATION_PORTS = (
    "language",
    "registry",
    "growth",
    "cube",
    "main",
    "persona",
    "tool",
    "doc",
    "pipeline",
    "other",
)

# Names the full program expects after open() (L3 health)
REQUIRED_FOR_OPEN: Tuple[str, ...] = (
    "Mandell",
    "TrueRegistry",
    "PlaneSurface",
    "MainField",
    "BlankCube",
    "GraphView",
    "EnhanceGate",
    "Persist",
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
        self.snapped[port] = [e for e in self.snapped[port] if e["name"] != candidate.name]
        self.snapped[port].append(entry)
        self.log.append(f"SNAP {candidate.name} → {port}")
        return result

    def list_port(self, port: str) -> List[Dict[str, Any]]:
        return list(self.snapped.get(port, []))

    def all_snaps(self) -> List[Dict[str, Any]]:
        """Flat inventory of every snapped entry."""
        out: List[Dict[str, Any]] = []
        for port, entries in self.snapped.items():
            for e in entries:
                row = dict(e)
                row["port"] = port
                out.append(row)
        return out

    def snap_names(self) -> Set[str]:
        return {e["name"] for e in self.all_snaps() if e.get("name")}

    def has_snap(self, name: str) -> bool:
        return name in self.snap_names()

    def verify(self, required: Optional[Tuple[str, ...]] = None) -> Dict[str, Any]:
        """
        L3 health check.
        Floor intact, registry size, required names present.
        """
        assert_floor_intact()
        req = required if required is not None else REQUIRED_FOR_OPEN
        names = self.snap_names()
        missing = [n for n in req if n not in names]
        ok = (
            list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"]
            and len(DELLS) == 51
            and len(missing) == 0
        )
        report = {
            "ok": ok,
            "floor": list(FLOOR),
            "dell_count": len(DELLS),
            "snap_count": len(names),
            "missing": missing,
            "present": sorted(names),
        }
        self.log.append(f"VERIFY ok={ok} missing={missing}")
        return report

    def understand(self) -> Dict[str, Any]:
        health = self.verify(required=())  # soft: no required names for bare matrix
        return {
            "self": "DellMatrix",
            "role": "foundation snap host",
            "level": 3,
            "requires": "Mandell language",
            "floor": floor_status(),
            "ports": {p: len(self.snapped.get(p, [])) for p in FOUNDATION_PORTS},
            "dell_count": len(DELLS),
            "snap_names": sorted(self.snap_names()),
            "log_tail": self.log[-10:],
            "health_soft": health,
        }

    def status(self) -> Dict[str, Any]:
        return self.understand()
