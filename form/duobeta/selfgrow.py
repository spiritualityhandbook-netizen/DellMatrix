#!/usr/bin/env python3
"""
SelfGrow L3 — program evolves using Mandell seeds against live foundation.

13[Loop] > 04[Transform] >> 50[Manifest] :: SelfGrow

Layer 3 curriculum reflects what Form actually has:
  plane · main · blank · open · graph · resonance · enhance · persist · snap L3

Run:
  python -m form.duobeta.selfgrow --cycles 12
  python -m form.duobeta.selfgrow --smoke
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
    from form.open import open_program
except ImportError:
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.mandell.manifest import Manifest
    from form.dell_matrix.core import DellMatrix
    from form.dell_matrix.snap import SnapCandidate
    from form.duobeta.growth import DuoBeta
    from form.open import open_program

_DATA = os.path.join(os.path.dirname(__file__), "..", "state")
os.makedirs(_DATA, exist_ok=True)
LEDGER_PATH = os.path.join(_DATA, "selfgrow_ledger.json")
STATE_PATH = os.path.join(_DATA, "selfgrow_state.json")

# L3 curriculum — seeds that name real Form capabilities
LAYER_3: List[Dict[str, Any]] = [
    {"seed": "01[Initiate] > 15[Map] >> 09[Show]", "dell": 1, "term": "OpenSurface", "manor": "One program open surface", "kind": "tool", "english": "Open is the one program surface"},
    {"seed": "08[Create] >> 15[Map] : 09[Show]", "dell": 15, "term": "PlaneL3", "manor": "Geometric plane L3", "kind": "tool", "english": "Plane page/zoom/neighbors live"},
    {"seed": "21[Merge] : 14[Bind] >> 10[Keep]", "dell": 21, "term": "MainL3", "manor": "Main third field L3", "kind": "main", "english": "Main top_tags pulls weight stack"},
    {"seed": "08[Create] >> 50[Manifest] : 10[Keep]", "dell": 8, "term": "BlankL3", "manor": "Givable blank pack L3", "kind": "cube", "english": "Blank pack export/import"},
    {"seed": "09[Show] > 15[Map] >> 47[Embed]", "dell": 9, "term": "GraphView", "manor": "UI contract graph", "kind": "tool", "english": "Nodes edges bindable view"},
    {"seed": "35[Discover] > 05[Tone] >> 14[Bind]", "dell": 35, "term": "ResonanceAct", "manor": "Active enhance pulse", "kind": "growth", "english": "Pulse moves scores and tags"},
    {"seed": "32[Pause] :: 33[Resume] > 25[Pulse]", "dell": 32, "term": "EnhanceGate", "manor": "Opt-in enhance", "kind": "tool", "english": "Enhance default off"},
    {"seed": "10[Keep] > 27[Checkpoint] >> 28[Rollback]", "dell": 10, "term": "PersistV2", "manor": "Save load state", "kind": "tool", "english": "Persist scores pulls plane"},
    {"seed": "01[Initiate] > 13[Loop] >> 09[Show]", "dell": 13, "term": "REPL3", "manor": "Interactive session L3", "kind": "tool", "english": "REPL operate the matrix"},
    {"seed": "14[Bind] : 12[Test] >> 35[Discover]", "dell": 14, "term": "SnapL3", "manor": "Snap verify health", "kind": "registry", "english": "Required snaps verified"},
    {"seed": "15[Map] : 18[Mirror] >> 46[Rank]", "dell": 46, "term": "NBDEquation", "manor": "Next best directive formula", "kind": "growth", "english": "NBD ranks gap to goal"},
    {"seed": "12[Test] : 18[Mirror] :: 34[Stamp]", "dell": 12, "term": "SusStamp", "manor": "Self test stamp", "kind": "pipeline", "english": "Smoke stamps health"},
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
    live_has: bool  # whether open_program already has related snap


@dataclass
class SelfGrow:
    matrix: DellMatrix = field(default_factory=DellMatrix)
    duo: Optional[DuoBeta] = None
    cursor: int = 0
    level: int = 3
    watch: List[WatchLine] = field(default_factory=list)
    live_names: set = field(default_factory=set)

    def __post_init__(self):
        assert_floor_intact()
        if self.duo is None:
            self.duo = DuoBeta(matrix=self.matrix)
        # probe live program snaps
        try:
            prog = open_program("SelfGrowProbe")
            self.live_names = prog.matrix.snap_names()
            # adopt live matrix as growth host so snaps accumulate on real host shape
            self.matrix = prog.matrix
            self.duo = DuoBeta(matrix=self.matrix)
        except Exception:
            self.live_names = set()

    def _ts(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def step(self) -> WatchLine:
        assert_floor_intact()
        item = LAYER_3[self.cursor % len(LAYER_3)]
        self.cursor += 1

        m = Manifest(term=item["term"], manor=item["manor"], dell=int(item["dell"]))
        cand = SnapCandidate(
            name=item["term"],
            kind=item["kind"],
            manifest=m,
            payload={"seed": item["seed"], "english": item["english"], "layer": 3},
        )
        result = self.matrix.snap(cand)
        ev = self.duo.evolve(item["seed"]) if self.duo else {"ok": False}

        ok = bool(result.ok) and bool(ev.get("ok", True))
        reason = result.reason
        if result.ok and not ev.get("ok", True):
            ok = False
            reason = str(ev.get("reason", "evolve blocked"))

        live_has = item["term"] in self.live_names or any(
            item["term"].replace("L3", "").replace("V2", "") in n for n in self.live_names
        )

        line = WatchLine(
            gen=self.duo.generation if self.duo else self.cursor,
            seed=item["seed"],
            term=item["term"],
            ok=ok,
            reason=reason,
            english=item["english"],
            ts=self._ts(),
            live_has=live_has,
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
            "selfgrow_level": self.level,
            "cursor": self.cursor,
            "curriculum_len": len(LAYER_3),
            "watch_len": len(self.watch),
            "live_snap_names": sorted(self.live_names),
            "last_seed": self.watch[-1].seed if self.watch else None,
        }

    def _persist(self) -> None:
        data = {
            "floor": list(FLOOR),
            "level": self.level,
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
                    "live_has": w.live_has,
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
            f"+- SelfGrow L{self.level} WATCH · gen={self.duo.generation if self.duo else 0} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED)",
            f"| cursor={self.cursor}/{len(LAYER_3)}",
        ]
        for w in self.watch[-16:]:
            mark = "✓" if w.ok else "✗"
            live = "LIVE" if w.live_has else "seed"
            lines.append(f"| {mark} g{w.gen} [{live}] {w.seed}")
            lines.append(f"|    → {w.term} · {w.english}")
        lines.append(f"| ports {self.matrix.understand().get('ports', {})}")
        lines.append("+" + "-" * 52 + "+")
        return "\n".join(lines)


def smoke() -> bool:
    print("=== SELFGROW L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    sg = SelfGrow()
    lines = sg.run(cycles=len(LAYER_3))
    rec("all ok", all(w.ok for w in lines))
    rec("level 3", sg.level == 3)
    rec("gen", sg.duo.generation >= len(LAYER_3))
    rec("ledger", os.path.isfile(LEDGER_PATH))
    rec("understand", sg.understand().get("selfgrow_level") == 3)
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main() -> None:
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    cycles = 12
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = int(sys.argv[i + 1])

    print("15[Map] : 18[Mirror] >> 46[Rank] > 50[Manifest] :: NBD")
    print("13[Loop] > 04[Transform] >> 50[Manifest] :: SelfGrow L3")
    print("English: Growth curriculum aligned to live Form stack.\n")

    sg = SelfGrow()
    sg.run(cycles=cycles)
    print(sg.render_watch())
    print()
    print(json.dumps(sg.understand(), indent=2, default=str))


if __name__ == "__main__":
    main()
