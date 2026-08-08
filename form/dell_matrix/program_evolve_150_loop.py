#!/usr/bin/env python3
"""
Program self-understanding + evolution — 150 enhance loop.

The program learns what it is (capabilities, matrices, snaps, pillars)
and evolves generation-by-generation while closing cold surfaces.

Phases (25 cycles each = 150):
  1 Identity     — floor, status, matrices, audit
  2 Perception   — look, page, lattice, geometry, multilook
  3 Growth       — grow, nursery, forces, pulse
  4 Language     — english, help, lang list
  5 Agents       — personas, bimo, entities, AI, workshops
  6 Evolve lock  — evolve, save, sphere, full reflect + mastery

  python -m form.dell_matrix.program_evolve_150_loop
  python -m form.dell_matrix.program_evolve_150_loop --cycles 150
  python -m form.dell_matrix.program_evolve_150_loop --smoke
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from form.open import open_program
from form.dell_matrix.self_model import (
    CAPABILITIES, SelfKnowledge, know_self, reflect_lines,
    probe_capability, close_gaps, evolve_with_understanding, inventory,
)

PHASES = [
    ("identity", ["floor", "status", "matrices", "audit"]),
    ("perception", ["look", "multilook", "page", "lattice", "geometry"]),
    ("growth", ["grow", "proposals", "rank", "forces", "force_tick", "pulse"]),
    ("language", ["english", "lang", "help"]),
    ("agents", ["personas", "bimo", "entities", "ai", "workshops", "inspire", "home"]),
    ("evolve", ["evolve", "save", "sphere", "audit", "status"]),
]


def _caps_by_ids(ids: List[str]) -> List[Dict[str, Any]]:
    by = {c["id"]: c for c in CAPABILITIES}
    return [by[i] for i in ids if i in by]


def run_loop(cycles: int = 150, owner: str = "Evolve150") -> Dict[str, Any]:
    print("=== PROGRAM SELF-UNDERSTAND + EVOLVE 150 ===")
    p = open_program(owner)
    if not hasattr(p, "self_knowledge") or p.self_knowledge is None:
        p.self_knowledge = SelfKnowledge()

    # seed so growth/page have substance
    p.place("core_self", "CoreSelf", words="I am the program surface", x=0, y=1)
    p.place("grow_self", "GrowSelf", words="I evolve with understanding", x=1, y=2)
    if hasattr(p, "enhance") and not p.enhance.on:
        p.enhance.turn_on()

    base = know_self(p)
    base_avg = (base.get("knowledge") or {}).get("avg_mastery", 0)
    base_pil = ((base.get("inventory") or {}).get("pillars") or {}).get("average", 0)
    base_gen = (base.get("inventory") or {}).get("generation", 0)
    print(
        f"[baseline] gen={base_gen} pillars={base_pil} "
        f"mastery={base_avg} matrices={(base.get('inventory') or {}).get('matrix_count')} "
        f"snaps={(base.get('inventory') or {}).get('snap_count')}"
    )

    per_cycle: List[Dict[str, Any]] = []
    total_probes = 0
    total_hits = 0
    evolves = 0

    # distribute cycles across 6 phases
    n_phases = len(PHASES)
    per_phase = max(1, cycles // n_phases)
    remaining = cycles

    cycle_i = 0
    for phase_name, cap_ids in PHASES:
        n = min(per_phase, remaining) if phase_name != PHASES[-1][0] else remaining
        remaining -= n
        caps = _caps_by_ids(cap_ids)
        if not caps:
            continue
        print(f"\n--- phase {phase_name} ×{n} ---")
        for j in range(n):
            cycle_i += 1
            # rotate capability in phase
            cap = caps[j % len(caps)]
            pr = probe_capability(p, cap)
            total_probes += 1
            total_hits += int(pr.get("ok"))

            # every cycle: evolve with understanding of this surface
            detail = f"150/{phase_name}/{cap['id']}"
            evo = evolve_with_understanding(p, detail=detail)
            evolves += 1

            # every 5th: close remaining cold gaps
            closed = []
            if cycle_i % 5 == 0:
                g = close_gaps(p)
                closed = g.get("closed") or []

            # every 10th: grow ideas so nursery path stays warm
            if cycle_i % 10 == 0:
                try:
                    p.grow_ideas(1)
                except Exception:
                    pass

            sk = p.self_knowledge.to_dict()
            pil = p.audit().get("average") if hasattr(p, "audit") else 0
            row = {
                "cycle": cycle_i,
                "phase": phase_name,
                "cap": cap["id"],
                "probe_ok": pr.get("ok"),
                "mastery_cap": pr.get("mastery"),
                "avg_mastery": sk.get("avg_mastery"),
                "generation": evo.get("generation"),
                "pillars": pil,
                "closed": closed,
            }
            per_cycle.append(row)

            if cycle_i == 1 or cycle_i % 25 == 0 or cycle_i == cycles:
                print(
                    f"  c{cycle_i:03d} [{phase_name}] {cap['id']} "
                    f"ok={pr.get('ok')} mast={sk.get('avg_mastery')} "
                    f"gen={evo.get('generation')} pil={pil}"
                )

    # final reflect
    print("\n--- final reflect ---")
    lines = reflect_lines(p)
    for ln in lines:
        print(ln)

    final = know_self(p)
    inv = final.get("inventory") or {}
    sk = final.get("knowledge") or {}
    cold = final.get("cold_capabilities") or []

    probe_rate = total_hits / max(1, total_probes)
    mastery = sk.get("avg_mastery") or 0
    pil = (inv.get("pillars") or {}).get("average") or 0
    gen = inv.get("generation") or 0

    # pass gates: learned itself + evolved + warm
    passed = (
        probe_rate >= 0.85
        and mastery >= 0.75
        and gen > base_gen
        and evolves >= cycles
        and len(cold) <= 3
        and pil >= 0.65
        and inv.get("matrix_count", 0) >= 15
    )

    print(
        f"\n=== RESULT: probes={probe_rate:.1%} mastery={mastery:.3f} "
        f"gen {base_gen}→{gen} pillars={pil} cold={len(cold)} · "
        f"{'PASS' if passed else 'FAIL'} ==="
    )

    return {
        "ok": passed,
        "probe_rate": probe_rate,
        "mastery": mastery,
        "generation_start": base_gen,
        "generation_end": gen,
        "pillars": pil,
        "cold": cold,
        "evolves": evolves,
        "cycles": cycles,
        "per_cycle": per_cycle,
        "reflect": lines,
        "inventory": inv,
        "knowledge": sk,
        "program": p,
    }


def smoke() -> bool:
    # short path for suite
    out = run_loop(cycles=12, owner="EvolveSmoke")
    return bool(
        out["probe_rate"] >= 0.75
        and out["generation_end"] > out["generation_start"]
        and out["mastery"] >= 0.4
    )


if __name__ == "__main__":
    n = 150
    owner = "Evolve150"
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    for a in sys.argv[1:]:
        if a.isdigit():
            n = int(a)
        if a.startswith("--owner="):
            owner = a.split("=", 1)[1]
    out = run_loop(cycles=n, owner=owner)
    sys.exit(0 if out["ok"] else 1)
