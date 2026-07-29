"""
DuoBeta — living growth / self-understanding (Voynich structural).

Not conscious. Understands itself in its way: structure, ports, generation, ledger.
AI can comprehend through Mandell surface (compact structure, less waste).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime, timezone

from form.mandell.floor import FLOOR, assert_floor_intact
from form.dell_matrix.core import DellMatrix


@dataclass
class GrowthEntry:
    gen: int
    detail: str
    ts: str


@dataclass
class DuoBeta:
    matrix: DellMatrix
    generation: int = 0
    ledger: List[GrowthEntry] = field(default_factory=list)
    rings: tuple = ("Seed", "Token", "Body", "Lens", "Evolve")  # structural Voynich rings

    def _ts(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def understand_self(self) -> Dict[str, Any]:
        """Self-understanding for the program — structural, not sentient."""
        assert_floor_intact()
        base = self.matrix.understand()
        return {
            **base,
            "duobeta": True,
            "generation": self.generation,
            "rings": list(self.rings),
            "ledger_len": len(self.ledger),
            "mode": "living growth — combine without clobber",
            "floor": list(FLOOR),
        }

    def evolve(self, detail: str = "tick") -> Dict[str, Any]:
        assert_floor_intact()
        # reject floor-hostile growth
        if "override floor" in detail.lower():
            return {"ok": False, "reason": "Floor hostile"}
        self.generation += 1
        entry = GrowthEntry(gen=self.generation, detail=detail[:120], ts=self._ts())
        self.ledger.append(entry)
        return {"ok": True, "generation": self.generation, "entry": entry.detail}

    def status(self) -> Dict[str, Any]:
        return self.understand_self()
