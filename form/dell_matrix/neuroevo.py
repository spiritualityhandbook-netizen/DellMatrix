#!/usr/bin/env python3
"""
Neuroevolution seed for DellMatrix (Nature of Code Ch11).

Genome = ForceField intensities (water, growth, breath, gravity, time, weather, space).
Fitness = pillars average + growth plant count + nature movers coherence proxy.
No gradient — selection + mutation only. Offline · Floor/Nursery intact.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import random
import copy

FORCE_KEYS = ("water", "growth", "breath", "gravity", "time", "weather", "space")


@dataclass
class Genome:
    intensities: Dict[str, float] = field(default_factory=dict)
    fitness: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"intensities": dict(self.intensities), "fitness": round(self.fitness, 4)}


def _random_genome(rng: random.Random) -> Genome:
    return Genome(intensities={k: round(rng.uniform(0.2, 0.95), 3) for k in FORCE_KEYS})


def _mutate(g: Genome, rng: random.Random, rate: float = 0.25, sigma: float = 0.08) -> Genome:
    child = Genome(intensities=dict(g.intensities))
    for k in FORCE_KEYS:
        if rng.random() < rate:
            child.intensities[k] = max(0.05, min(1.0, child.intensities[k] + rng.gauss(0, sigma)))
            child.intensities[k] = round(child.intensities[k], 3)
    return child


def _crossover(a: Genome, b: Genome, rng: random.Random) -> Genome:
    child = Genome(intensities={})
    for k in FORCE_KEYS:
        child.intensities[k] = a.intensities[k] if rng.random() < 0.5 else b.intensities[k]
    return child


def _apply_genome(program, genome: Genome) -> None:
    ff = getattr(program, "forces", None)
    if not ff:
        return
    for k, val in genome.intensities.items():
        force = ff.get(k) if hasattr(ff, "get") else getattr(ff, k, None)
        if force is not None and hasattr(force, "intensity"):
            force.intensity = float(val)


def _evaluate(program) -> float:
    """Fitness from pillars avg + growth activity + nature status."""
    score = 0.0
    try:
        audit = program.audit() if hasattr(program, "audit") else {}
        avg = float(audit.get("average") or 0)
        score += avg * 10.0  # 0–10-ish
    except Exception:
        pass
    try:
        st = program.forces.status() if hasattr(program, "forces") else {}
        plants = len(st.get("growth_map") or [])
        streams = int(st.get("water_streams") or 0)
        score += min(5.0, plants * 0.4 + streams * 0.2)
    except Exception:
        pass
    try:
        from form.dell_matrix.nature_code import nature_status
        ns = nature_status()
        score += min(2.0, float(ns.get("movers") or 0) * 0.15)
    except Exception:
        pass
    # mild preference for balanced intensities (not all max)
    try:
        vals = [getattr(program.forces.get(k), "intensity", 0.5) for k in FORCE_KEYS if program.forces.get(k)]
        if vals:
            mean = sum(vals) / len(vals)
            var = sum((v - mean) ** 2 for v in vals) / len(vals)
            score += max(0.0, 1.5 - var * 4)  # reward moderate diversity
    except Exception:
        pass
    return round(score, 4)


def neuroevo_run(
    program,
    *,
    generations: int = 5,
    pop_size: int = 8,
    elite: int = 2,
    mutate_rate: float = 0.3,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Evolve ForceField intensities for `generations`.
    Applies best genome to program.forces at the end.
    """
    rng = random.Random(seed)
    generations = max(1, min(30, int(generations)))
    pop_size = max(4, min(24, int(pop_size)))
    elite = max(1, min(elite, pop_size // 2))

    # seed population from current intensities + randoms
    population: List[Genome] = []
    base = Genome(intensities={})
    ff = getattr(program, "forces", None)
    for k in FORCE_KEYS:
        force = ff.get(k) if ff and hasattr(ff, "get") else None
        base.intensities[k] = float(getattr(force, "intensity", 0.5) if force else 0.5)
    population.append(base)
    while len(population) < pop_size:
        population.append(_random_genome(rng))

    history: List[Dict[str, Any]] = []
    best: Optional[Genome] = None

    for gen in range(1, generations + 1):
        # evaluate
        for g in population:
            _apply_genome(program, g)
            # one force tick so growth/nature respond
            try:
                program.force_tick()
            except Exception:
                pass
            g.fitness = _evaluate(program)
        population.sort(key=lambda g: -g.fitness)
        if best is None or population[0].fitness > best.fitness:
            best = Genome(intensities=dict(population[0].intensities), fitness=population[0].fitness)
        history.append({
            "gen": gen,
            "best": population[0].fitness,
            "mean": round(sum(g.fitness for g in population) / len(population), 4),
            "top": population[0].to_dict(),
        })
        # next generation
        next_pop: List[Genome] = [Genome(intensities=dict(g.intensities), fitness=g.fitness) for g in population[:elite]]
        while len(next_pop) < pop_size:
            # tournament
            a = max(rng.sample(population, min(3, len(population))), key=lambda g: g.fitness)
            b = max(rng.sample(population, min(3, len(population))), key=lambda g: g.fitness)
            child = _crossover(a, b, rng)
            child = _mutate(child, rng, rate=mutate_rate)
            next_pop.append(child)
        population = next_pop

    # apply champion
    if best:
        _apply_genome(program, best)
        try:
            program.force_tick()
            program.note_seed(13, "Loop", "neuroevo")
        except Exception:
            pass

    return {
        "ok": True,
        "engine": "neuroevo",
        "generations": generations,
        "pop_size": pop_size,
        "best": best.to_dict() if best else None,
        "history": history,
        "honesty": "PROJECTED_NOT_FACT · fitness is structural proxy not truth",
        "law": "offline · Floor/Nursery intact · intensities only",
    }


def smoke() -> bool:
    print("=== NEUROEVO SMOKE ===")
    from form.open import open_program
    p = open_program("NeuroSmoke")
    p.place("a", "Alpha", x=0, y=0)
    p.place("b", "Beta", x=2, y=1)
    out = neuroevo_run(p, generations=2, pop_size=4, seed=7)
    ok = out.get("ok") and out.get("best") is not None
    print(f"[{'PASS' if ok else 'FAIL'}] gens={out.get('generations')} best={out.get('best')}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
