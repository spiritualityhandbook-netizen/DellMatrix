#!/usr/bin/env python3
"""
31_VOYNICH_DUOBETA.py
Voynich structural 5-ring lattice + DuoBeta-style evolution loop
Status: TRUE
Offline · stdlib only

Voynich = structure (rings), NOT manuscript decipherment.
DuoBeta-style = propose → gate → ledger → apply safe mutation.
Floor never mutates.

Run:
  python preform/code/31_VOYNICH_DUOBETA.py
  python preform/code/31_VOYNICH_DUOBETA.py --smoke
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
import sys

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
FLOOR = ("Alpha", "Delta", "Omega", "Omni")
RING_NAMES = ("Seed", "Token", "Body", "Lens", "Evolve")


@dataclass
class Ring:
    index: int
    name: str
    heat: float = 0.0  # 0..1 emphasis
    note: str = ""

    def status(self) -> Dict[str, Any]:
        return {"index": self.index, "name": self.name, "heat": round(self.heat, 3), "note": self.note}


@dataclass
class EvolutionEntry:
    gen: int
    kind: str
    detail: str
    accepted: bool
    ts: str


@dataclass
class VoynichDuoWorkspace:
    """
    Living workspace core:
    - 5 structural rings (Voynich-as-architecture)
    - DuoBeta-style evolve() loop with ledger
    """
    generation: int = 0
    active_ring: int = 0
    rings: List[Ring] = field(default_factory=list)
    ledger: List[EvolutionEntry] = field(default_factory=list)
    seed: str = "08[Create] >> 14[Bind] :: voynich-struct"
    tokens_note: str = ""
    body_note: str = "pos=(0,0)"
    lens_note: str = "Aetheris clear"
    forbidden_hits: int = 0

    def __post_init__(self):
        if not self.rings:
            self.rings = [Ring(i, RING_NAMES[i]) for i in range(5)]
            self.rings[0].heat = 0.4
            self.rings[0].note = self.seed

    def _ts(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _gate(self, kind: str, detail: str) -> Tuple[bool, str]:
        """Reject anything that smells like Floor break or decipherment."""
        d = (detail or "").lower()
        k = (kind or "").lower()
        if "floor" in d and any(x in d for x in ("remove", "override", "replace", "delete")):
            return False, "rejects Floor mutation"
        if any(w in d for w in ("decipher", "decode voynich", "solved manuscript", "linear a solved")):
            return False, "rejects decipherment claim"
        if "registry manor" in d and "redefine" in d:
            return False, "rejects registry redefine"
        if k in ("network", "http", "online"):
            return False, "rejects network mutation"
        return True, "ok"

    def propose(self, kind: str, detail: str) -> Dict[str, Any]:
        ok, reason = self._gate(kind, detail)
        entry = EvolutionEntry(
            gen=self.generation + (1 if ok else 0),
            kind=kind,
            detail=detail,
            accepted=ok,
            ts=self._ts(),
        )
        if not ok:
            self.forbidden_hits += 1
            self.ledger.append(entry)
            return {"accepted": False, "reason": reason, "entry": entry}

        self.generation += 1
        entry.gen = self.generation
        self.ledger.append(entry)
        self._apply(kind, detail)
        return {"accepted": True, "reason": reason, "generation": self.generation, "entry": entry}

    def _apply(self, kind: str, detail: str) -> None:
        k = kind.lower()
        if k == "heat":
            # detail: "ring=3" or ring name
            idx = self.active_ring
            for i, name in enumerate(RING_NAMES):
                if name.lower() in detail.lower() or f"ring={i}" in detail.replace(" ", ""):
                    idx = i
                    break
            self.active_ring = idx
            for r in self.rings:
                r.heat = max(0.0, r.heat * 0.85)
            self.rings[idx].heat = min(1.0, self.rings[idx].heat + 0.25)
            self.rings[idx].note = detail[:80]
        elif k == "seed":
            self.seed = detail[:120] or self.seed
            self.rings[0].note = self.seed
            self.rings[0].heat = min(1.0, self.rings[0].heat + 0.15)
            self.active_ring = 0
        elif k == "token":
            self.tokens_note = detail[:80]
            self.rings[1].note = self.tokens_note
            self.rings[1].heat = min(1.0, self.rings[1].heat + 0.2)
            self.active_ring = 1
        elif k == "body":
            self.body_note = detail[:80]
            self.rings[2].note = self.body_note
            self.rings[2].heat = min(1.0, self.rings[2].heat + 0.2)
            self.active_ring = 2
        elif k == "lens":
            self.lens_note = detail[:80]
            self.rings[3].note = self.lens_note
            self.rings[3].heat = min(1.0, self.rings[3].heat + 0.2)
            self.active_ring = 3
        elif k in ("evolve", "grow", "duobeta"):
            self.rings[4].note = detail[:80] or f"gen={self.generation}"
            self.rings[4].heat = min(1.0, self.rings[4].heat + 0.3)
            self.active_ring = 4
        else:
            # generic growth mark on Evolve ring
            self.rings[4].note = f"{kind}:{detail[:60]}"
            self.rings[4].heat = min(1.0, self.rings[4].heat + 0.1)
            self.active_ring = 4

    def evolve(self, steps: int = 1) -> List[Dict[str, Any]]:
        """
        DuoBeta-style self-step: each step proposes a safe internal growth.
        Does not touch Floor or registry manors.
        """
        results = []
        for i in range(max(1, steps)):
            # rotate emphasis through rings — crystalline walk
            target = (self.active_ring + 1) % 5
            kind = "heat"
            detail = f"ring={target} crystalline walk gen-pre={self.generation}"
            results.append(self.propose(kind, detail))
            # small evolve stamp
            results.append(
                self.propose("evolve", f"DuoBeta tick {self.generation} ring={RING_NAMES[target]}")
            )
        return results

    def render(self) -> str:
        lines = [
            f"+- VoynichDuo Workspace · gen={self.generation} -+",
            f"| Floor: {' · '.join(FLOOR)} (LOCKED — not a ring)",
            f"| Mode: structural Voynich rings · DuoBeta evolve",
            f"| Active ring: {self.active_ring} ({RING_NAMES[self.active_ring]})",
            "| RINGS",
        ]
        for r in self.rings:
            bar = "█" * int(r.heat * 8) + "·" * (8 - int(r.heat * 8))
            mark = ">" if r.index == self.active_ring else " "
            lines.append(f"| {mark} [{r.index}] {r.name:6} [{bar}] {r.note[:40]}")
        lines.append("| LEDGER (last 5)")
        for e in self.ledger[-5:]:
            flag = "✓" if e.accepted else "✗"
            lines.append(f"|   {flag} g{e.gen} {e.kind}: {e.detail[:42]}")
        lines.append(f"| forbidden_hits={self.forbidden_hits}")
        lines.append("+" + "-" * 44 + "+")
        return "\n".join(lines)

    def status(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "floor": list(FLOOR),
            "active_ring": self.active_ring,
            "active_name": RING_NAMES[self.active_ring],
            "rings": [r.status() for r in self.rings],
            "ledger_len": len(self.ledger),
            "forbidden_hits": self.forbidden_hits,
            "seed": self.seed,
        }

    def export_ledger(self, path: Optional[str] = None) -> str:
        path = path or os.path.join(_CODE_DIR, "31_EVOLUTION_LEDGER.json")
        data = [
            {
                "gen": e.gen,
                "kind": e.kind,
                "detail": e.detail,
                "accepted": e.accepted,
                "ts": e.ts,
            }
            for e in self.ledger
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"floor": list(FLOOR), "generation": self.generation, "entries": data}, f, indent=2)
        return path


def smoke() -> bool:
    print("=== VOYNICH DUOBETA SMOKE ===")
    results: List[bool] = []

    def record(name: str, passed: bool, detail: str = "") -> None:
        print(f"[{len(results)+1}] {name}: {'PASS' if passed else 'FAIL'}" + (f" | {detail}" if detail else ""))
        results.append(bool(passed))

    def run(name, fn):
        try:
            ok, detail = fn()
            record(name, bool(ok), detail)
        except Exception as e:
            record(name, False, f"EXCEPTION {type(e).__name__}: {e}")

    w = VoynichDuoWorkspace()
    run("init rings", lambda: (len(w.rings) == 5, str([r.name for r in w.rings])))
    run("floor locked", lambda: (w.status()["floor"] == list(FLOOR), str(FLOOR)))
    run("evolve steps", lambda: (len(w.evolve(2)) >= 2 and w.generation >= 2, f"gen={w.generation}"))
    run("reject decipherment", lambda: (
        w.propose("evolve", "decode voynich manuscript fully")["accepted"] is False,
        f"forbidden={w.forbidden_hits}",
    ))
    run("reject floor wipe", lambda: (
        w.propose("heat", "remove floor operators override")["accepted"] is False,
        "ok",
    ))
    run("accept seed grow", lambda: (
        w.propose("seed", "08[Create] >> 50[Manifest]")["accepted"] is True,
        w.seed[:40],
    ))
    run("render", lambda: ("VoynichDuo" in w.render() and "LOCKED" in w.render(), "ok"))
    run("ledger", lambda: (len(w.ledger) >= 3, f"n={len(w.ledger)}"))

    print(f"=== RESULT: {sum(1 for x in results if x)}/{len(results)} PASS ===")
    return all(results)


def demo() -> None:
    w = VoynichDuoWorkspace()
    w.evolve(3)
    w.propose("lens", "Aetheris coherence pass")
    print(w.render())
    print("STATUS:", w.status())


if __name__ == "__main__":
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    demo()
