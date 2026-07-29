#!/usr/bin/env python3
"""
DuoBeta self-grow — program evolves itself using Mandell structure.

Inside: Mandel seeds / Dell / Manifest
Outside: English display only

Run:
  python -m form.duobeta.selfgrow
  python -m form.duobeta.selfgrow --cycles 12
  python -m form.duobeta.selfgrow --layer 2
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.duobeta.growth import DuoBeta
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.duobeta.growth import DuoBeta

_DATA = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_DATA, exist_ok=True)
LEDGER_PATH = os.path.join(_DATA, "selfgrow_ledger.json")
STATE_PATH = os.path.join(_DATA, "selfgrow_state.json")

# Layer 1 — foundation into itself
LAYER_1: List[Dict[str, Any]] = [
    {"seed": "01[Initiate] > 08[Create] >> 14[Bind]", "dell": 1, "term": "InitiateGrow", "manor": "Open growth path into foundation", "kind": "growth", "english": "Open self-grow path and bind to foundation"},
    {"seed": "11[Architect] : 23[Lock] :: 00[Nova]", "dell": 11, "term": "ArchitectLock", "manor": "Schema growth under Floor lock", "kind": "language", "english": "Architect confirms growth stays under Floor"},
    {"seed": "08[Create] >> 50[Manifest]", "dell": 50, "term": "ManifestPort", "manor": "Bring grow-port into form", "kind": "tool", "english": "Manifest concrete grow-port on Dell Matrix"},
    {"seed": "04[Transform] > 13[Loop] >> 10[Keep]", "dell": 4, "term": "EvoludellLoop", "manor": "Recursive transform kept as lineage", "kind": "growth", "english": "DuoBeta recursive loop as living lineage"},
    {"seed": "12[Test] : 18[Mirror] :: 34[Stamp]", "dell": 12, "term": "SusMirror", "manor": "Self-audit stamp", "kind": "pipeline", "english": "Self-test mirror audit with stamp"},
    {"seed": "07[Link] >> 21[Merge] : 14[Bind]", "dell": 7, "term": "MainLink", "manor": "Link to Main third-space", "kind": "main", "english": "Main link without clobber"},
    {"seed": "08[Create] > 09[Show] >> 02[Persona]", "dell": 8, "term": "BlankCubeForm", "manor": "Blank harmonic cube port", "kind": "cube", "english": "Blank cube port ready to give"},
    {"seed": "25[Pulse] >> 10[Keep] : 50[Manifest]", "dell": 25, "term": "PsalmPulse", "manor": "Pulse growth into kept line", "kind": "doc", "english": "Growth pulse recorded as kept line"},
    {"seed": "35[Discover] > 15[Map] >> 39[Schema]", "dell": 35, "term": "SelfMap", "manor": "Program maps its own ports", "kind": "growth", "english": "Self-discover ports and map schema"},
    {"seed": "05[Tone] : 18[Mirror] :: 12[Test]", "dell": 5, "term": "HarmoniCheck", "manor": "Harmony check on grown structure", "kind": "pipeline", "english": "Harmony check after growth"},
]

# Layer 2 — cube · table · enhance · resonance (continue)
LAYER_2: List[Dict[str, Any]] = [
    {"seed": "08[Create] >> 15[Map] : 19[Drive]", "dell": 8, "term": "HarmonicCubeHold", "manor": "Holdable harmonic cube form", "kind": "cube", "english": "Cube can be held and inspected"},
    {"seed": "09[Show] > 06[Cycle] >> 14[Bind]", "dell": 9, "term": "TableSurface", "manor": "Table place for cubes", "kind": "tool", "english": "Table surface where cubes set down"},
    {"seed": "18[Mirror] >> 07[Link] : 12[Test]", "dell": 18, "term": "CubeSyncCheck", "manor": "Sync check between cubes on table", "kind": "pipeline", "english": "Cubes check synchronization without rewrite"},
    {"seed": "21[Merge] : 14[Bind] >> 10[Keep]", "dell": 21, "term": "MainThirdField", "manor": "Third space is Main not clobber", "kind": "main", "english": "Sync births Main field; personal cubes stay"},
    {"seed": "24[Unlock] > 36[Inject] : 04[Transform]", "dell": 24, "term": "VoluntaryPull", "manor": "Pull from Main only by choice", "kind": "growth", "english": "Voluntary pull from Main into personal cube"},
    {"seed": "08[Create] >> 50[Manifest] : 10[Keep]", "dell": 8, "term": "BlankCubeGive", "manor": "Givable blank cube", "kind": "cube", "english": "Blank cube handoff pack shape"},
    {"seed": "32[Pause] :: 33[Resume] > 02[Persona]", "dell": 32, "term": "EnhanceGate", "manor": "Enhance mode on/off", "kind": "tool", "english": "Opt-in enhance — off by default"},
    {"seed": "35[Discover] > 47[Embed] >> 14[Bind]", "dell": 35, "term": "ResonanceSeek", "manor": "Seek synchronicity across units", "kind": "growth", "english": "DuoBeta resonance search across snapped units"},
    {"seed": "05[Tone] >> 18[Mirror] : 46[Rank]", "dell": 5, "term": "HarmoniRank", "manor": "Rank harmonic fit", "kind": "pipeline", "english": "Score harmonic relationship between ideas"},
    {"seed": "13[Loop] > 04[Transform] >> 50[Manifest]", "dell": 13, "term": "SelfGrowLoop", "manor": "Curriculum loop continues growth", "kind": "growth", "english": "Self-grow loop locked as living behavior"},
    {"seed": "41[Sanitize] : 12[Test] :: 23[Lock]", "dell": 41, "term": "FloorSanity", "manor": "Strip Floor-hostile growth", "kind": "pipeline", "english": "Sanitize growth against Floor break"},
    {"seed": "25[Pulse] >> 09[Show] : 10[Keep]", "dell": 25, "term": "WatchPulse", "manor": "Show watch lines for human", "kind": "doc", "english": "Human-visible watch of what grew"},
]


def curriculum_for(layer: int) -> List[Dict[str, Any]]:
    if layer <= 1:
        return list(LAYER_1)
    if layer == 2:
        return list(LAYER_1) + list(LAYER_2)
    return list(LAYER_1) + list(LAYER_2)


@dataclass
class WatchLine:
    gen: int
    seed: str
    term: str
    ok: bool
    reason: str
    english: str
    ts: str
    layer: int


@dataclass
class SelfGrow:
    matrix: DellMatrix = field(default_factory=DellMatrix)
    duo: Optional[DuoBeta] = None
    cursor: int = 0
    layer: int = 2
    watch: List[WatchLine] = field(default_factory=list)

    def __post_init__(self):
        assert_floor_intact()
        if self.duo is None:
            self.duo = DuoBeta(matrix=self.matrix)

    def _ts(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _curriculum(self) -> List[Dict[str, Any]]:
        return curriculum_for(self.layer)

    def step(self) -> WatchLine:
        assert_floor_intact()
        cur = self._curriculum()
        item = cur[self.cursor % len(cur)]
        self.cursor += 1
        layer_tag = 1 if self.cursor <= len(LAYER_1) else 2

        m = Manifest(term=item["term"], manor=item["manor"], dell=int(item["dell"]))
        cand = SnapCandidate(
            name=item["term"],
            kind=item["kind"],
            manifest=m,
            payload={"seed": item["seed"], "english": item["english"], "layer": layer_tag},
        )
        result = self.matrix.snap(cand)
        ev = self.duo.evolve(item["seed"]) if self.duo else {"ok": False}

        ok = bool(result.ok) and bool(ev.get("ok", True))
        reason = result.reason
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
            layer=layer_tag,
        )
        self.watch.append(line)
        self._persist()
        return line

    def run(self, cycles: int = 12) -> List[WatchLine]:
        return [self.step() for _ in range(max(1, cycles))]

    def understand(self) -> Dict[str, Any]:
        base = self.duo.understand_self() if self.duo else self.matrix.understand()
        return {
            **base,
            "cursor": self.cursor,
            "layer": self.layer,
            "watch_len": len(self.watch),
            "curriculum_len": len(self._curriculum()),
            "last_seed": self.watch[-1].seed if self.watch else None,
        }

    def _persist(self) -> None:
        data = {
            "floor": list(FLOOR),
            "cursor": self.cursor,
            "layer": self.layer,
            "generation": self.duo.generation if self.duo else 0,
            "watch": [
                {
                    "gen": w.gen,
                    "layer": w.layer,
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
            f"+- SelfGrow WATCH · gen={self.duo.generation if self.duo else 0} · layer={self.layer} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| cursor={self.cursor}/{len(self._curriculum())}",
        ]
        for w in self.watch[-16:]:
            mark = "✓" if w.ok else "✗"
            lines.append(f"| {mark} L{w.layer} g{w.gen} {w.seed}")
            lines.append(f"|    → {w.term} · {w.english}")
        ports = self.matrix.understand().get("ports", {})
        lines.append(f"| ports {ports}")
        lines.append("+" + "-" * 52 + "+")
        return "\n".join(lines)


def main() -> None:
    cycles = 12
    layer = 2
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = int(sys.argv[i + 1])
        if a == "--layer" and i + 1 < len(sys.argv):
            layer = int(sys.argv[i + 1])

    print("01[Initiate] > 13[Loop] >> 04[Transform] :: SelfGrow.Continue")
    print("English: Continue — layer-2 growth into cube/table/enhance/resonance.\n")

    sg = SelfGrow(layer=layer)
    sg.run(cycles=cycles)

    print(sg.render_watch())
    print()
    print("09[Show] :: understand")
    print(json.dumps(sg.understand(), indent=2, default=str))
    print()
    print(f"10[Keep] :: {STATE_PATH}")


if __name__ == "__main__":
    main()
