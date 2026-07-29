#!/usr/bin/env python3
"""
DuoBeta self-grow — program evolves itself using Mandell structure.

Inside: Mandel seeds / Dell / Manifest
Outside: English display only

Run:
  python -m form.duobeta.selfgrow
  python -m form.duobeta.selfgrow --cycles 5
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# --- Mandell core (inline-safe if package path differs) ---
try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest, manifest_from_dell
    from form.mandell.registry import DELLS, get_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.duobeta.growth import DuoBeta
except ImportError:
    # path bootstrap
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest, manifest_from_dell
    from form.mandell.registry import DELLS, get_dell
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.duobeta.growth import DuoBeta

_DATA = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_DATA, exist_ok=True)
LEDGER_PATH = os.path.join(_DATA, "selfgrow_ledger.json")
STATE_PATH = os.path.join(_DATA, "selfgrow_state.json")


# Growth curriculum — Mandell seeds the program walks to grow into itself
CURRICULUM: List[Dict[str, Any]] = [
    {
        "seed": "01[Initiate] > 08[Create] >> 14[Bind]",
        "dell": 1,
        "term": "InitiateGrow",
        "manor": "Open growth path into foundation",
        "kind": "growth",
        "english": "Open the self-grow path and bind it to foundation",
    },
    {
        "seed": "11[Architect] : 23[Lock] :: 00[Nova]",
        "dell": 11,
        "term": "ArchitectLock",
        "manor": "Schema growth under Floor lock",
        "kind": "language",
        "english": "Architect confirms growth stays under Floor",
    },
    {
        "seed": "08[Create] >> 50[Manifest]",
        "dell": 50,
        "term": "ManifestPort",
        "manor": "Bring grow-port into form",
        "kind": "tool",
        "english": "Manifest a concrete grow-port on Dell Matrix",
    },
    {
        "seed": "04[Transform] > 13[Loop] >> 10[Keep]",
        "dell": 4,
        "term": "EvoludellLoop",
        "manor": "Recursive transform kept as lineage",
        "kind": "growth",
        "english": "DuoBeta recursive loop kept as living lineage",
    },
    {
        "seed": "12[Test] : 18[Mirror] :: 34[Stamp]",
        "dell": 12,
        "term": "SusMirror",
        "manor": "Self-audit stamp",
        "kind": "pipeline",
        "english": "Self-test and mirror audit with stamp",
    },
    {
        "seed": "07[Link] >> 21[Merge] : 14[Bind]",
        "dell": 7,
        "term": "MainLink",
        "manor": "Link personal cube field to Main third-space",
        "kind": "main",
        "english": "Prepare Main link without clobber",
    },
    {
        "seed": "08[Create] > 09[Show] >> 02[Persona]",
        "dell": 8,
        "term": "BlankCubeForm",
        "manor": "Blank harmonic cube port",
        "kind": "cube",
        "english": "Blank cube port ready to give",
    },
    {
        "seed": "25[Pulse] >> 10[Keep] : 50[Manifest]",
        "dell": 25,
        "term": "PsalmPulse",
        "manor": "Pulse growth into kept Psalm-line",
        "kind": "doc",
        "english": "Growth pulse recorded as kept line",
    },
    {
        "seed": "35[Discover] > 15[Map] >> 39[Schema]",
        "dell": 35,
        "term": "SelfMap",
        "manor": "Program maps its own ports and schema",
        "kind": "growth",
        "english": "Self-discover ports and map schema",
    },
    {
        "seed": "05[Tone] : 18[Mirror] :: 12[Test]",
        "dell": 5,
        "term": "HarmoniCheck",
        "manor": "Harmony check on grown structure",
        "kind": "pipeline",
        "english": "Harmony / coherence check after growth",
    },
]


@dataclass
class WatchLine:
    gen: int
    seed: str
    term: str
    ok: bool
    reason: str
    english: str
    ts: str


@dataclass
class SelfGrow:
    """Program grows itself into itself under Mandell."""

    matrix: DellMatrix = field(default_factory=DellMatrix)
    duo: Optional[DuoBeta] = None
    cursor: int = 0
    watch: List[WatchLine] = field(default_factory=list)

    def __post_init__(self):
        assert_floor_intact()
        if self.duo is None:
            self.duo = DuoBeta(matrix=self.matrix)

    def _ts(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def step(self) -> WatchLine:
        """One growth step — Mandell seed → snap into Dell Matrix → DuoBeta evolve."""
        assert_floor_intact()
        item = CURRICULUM[self.cursor % len(CURRICULUM)]
        self.cursor += 1

        m = Manifest(term=item["term"], manor=item["manor"], dell=int(item["dell"]))
        cand = SnapCandidate(
            name=item["term"],
            kind=item["kind"],
            manifest=m,
            payload={"seed": item["seed"], "english": item["english"]},
        )
        result = self.matrix.snap(cand)
        ev = self.duo.evolve(item["seed"]) if self.duo else {"ok": False}

        ok = bool(result.ok) and bool(ev.get("ok", True))
        reason = result.reason if result.ok else result.reason
        if result.ok and not ev.get("ok", True):
            ok = False
            reason = str(ev.get("reason", "evolve blocked"))

        line = WatchLine(
            gen=self.duo.generation if self.duo else self.cursor,
            seed=item["seed"],
            term=item["term"],
            ok=ok,
            reason=reason,
            english=item["english"],
            ts=self._ts(),
        )
        self.watch.append(line)
        self._persist()
        return line

    def run(self, cycles: int = 5) -> List[WatchLine]:
        lines = []
        for _ in range(max(1, cycles)):
            lines.append(self.step())
        return lines

    def understand(self) -> Dict[str, Any]:
        """Self-understanding after growth."""
        base = self.duo.understand_self() if self.duo else self.matrix.understand()
        return {
            **base,
            "cursor": self.cursor,
            "watch_len": len(self.watch),
            "curriculum_len": len(CURRICULUM),
            "last_seed": self.watch[-1].seed if self.watch else None,
        }

    def _persist(self) -> None:
        data = {
            "floor": list(FLOOR),
            "cursor": self.cursor,
            "generation": self.duo.generation if self.duo else 0,
            "watch": [
                {
                    "gen": w.gen,
                    "seed": w.seed,
                    "term": w.term,
                    "ok": w.ok,
                    "reason": w.reason,
                    "english": w.english,
                    "ts": w.ts,
                }
                for w in self.watch
            ],
            "ports": self.matrix.understand().get("ports", {}),
        }
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        with open(LEDGER_PATH, "w", encoding="utf-8") as f:
            json.dump(data["watch"], f, indent=2)

    def render_watch(self) -> str:
        lines = [
            f"+- SelfGrow WATCH · gen={self.duo.generation if self.duo else 0} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| cursor={self.cursor}/{len(CURRICULUM)}",
        ]
        for w in self.watch[-12:]:
            mark = "✓" if w.ok else "✗"
            lines.append(f"| {mark} g{w.gen} {w.seed}")
            lines.append(f"|    → {w.term} · {w.english}")
        ports = self.matrix.understand().get("ports", {})
        lines.append(f"| ports {ports}")
        lines.append("+" + "-" * 48 + "+")
        return "\n".join(lines)


def main() -> None:
    cycles = 5
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = int(sys.argv[i + 1])

    # Mandel open
    print("01[Initiate] > 08[Create] >> 14[Bind] :: SelfGrow")
    print("English: Turning self-grow on — program evolves into itself under Floor.\n")

    sg = SelfGrow()
    sg.run(cycles=cycles)

    print(sg.render_watch())
    print()
    print("09[Show] :: understand")
    print(json.dumps(sg.understand(), indent=2, default=str))
    print()
    print(f"10[Keep] :: state → {STATE_PATH}")
    print(f"10[Keep] :: ledger → {LEDGER_PATH}")


if __name__ == "__main__":
    main()
