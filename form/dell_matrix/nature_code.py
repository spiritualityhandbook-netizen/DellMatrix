#!/usr/bin/env python3
"""
Nature of Code — usable cores for DellMatrix (Ch0–5 fit).

Boolean host intact. No p5.js / canvas runtime claimed.
Maps into Code Evolution decision surfaces where natural.

Sources: natureofcode.com (Shiffman) — concepts only, not full book text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math
import random


# ------------------------------------------------------------------
# Ch1 — Vec2
# ------------------------------------------------------------------

@dataclass
class Vec2:
    x: float = 0.0
    y: float = 0.0

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)

    def add(self, other: "Vec2") -> "Vec2":
        self.x += other.x
        self.y += other.y
        return self

    def sub(self, other: "Vec2") -> "Vec2":
        self.x -= other.x
        self.y -= other.y
        return self

    def mult(self, s: float) -> "Vec2":
        self.x *= s
        self.y *= s
        return self

    def div(self, s: float) -> "Vec2":
        if s == 0:
            return self
        self.x /= s
        self.y /= s
        return self

    def mag(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def mag_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    def normalize(self) -> "Vec2":
        m = self.mag()
        if m > 0:
            self.div(m)
        return self

    def set_mag(self, m: float) -> "Vec2":
        self.normalize()
        return self.mult(m)

    def limit(self, max_mag: float) -> "Vec2":
        if self.mag_sq() > max_mag * max_mag:
            self.set_mag(max_mag)
        return self

    def heading(self) -> float:
        return math.atan2(self.y, self.x)

    @staticmethod
    def add_v(a: "Vec2", b: "Vec2") -> "Vec2":
        return Vec2(a.x + b.x, a.y + b.y)

    @staticmethod
    def sub_v(a: "Vec2", b: "Vec2") -> "Vec2":
        return Vec2(a.x - b.x, a.y - b.y)

    @staticmethod
    def random2d() -> "Vec2":
        a = random.uniform(0, 2 * math.pi)
        return Vec2(math.cos(a), math.sin(a))


# ------------------------------------------------------------------
# Ch0 — Walker / randomness helpers
# ------------------------------------------------------------------

def gaussian(mean: float = 0.0, std: float = 1.0) -> float:
    return random.gauss(mean, std)


def accept_reject() -> float:
    """Monte Carlo accept-reject: returns r in [0,1] with density proportional to r."""
    while True:
        r1 = random.random()
        r2 = random.random()
        if r2 < r1:
            return r1


@dataclass
class Walker:
    pos: Vec2 = field(default_factory=Vec2)

    def step_random(self) -> None:
        choice = random.randint(0, 3)
        if choice == 0:
            self.pos.x += 1
        elif choice == 1:
            self.pos.x -= 1
        elif choice == 2:
            self.pos.y += 1
        else:
            self.pos.y -= 1

    def step_biased(self, right_prob: float = 0.4) -> None:
        r = random.random()
        if r < right_prob:
            self.pos.x += 1
        elif r < right_prob + 0.2:
            self.pos.x -= 1
        elif r < right_prob + 0.4:
            self.pos.y += 1
        else:
            self.pos.y -= 1

    def step_gaussian(self, std: float = 1.0) -> None:
        self.pos.x += gaussian(0, std)
        self.pos.y += gaussian(0, std)


# ------------------------------------------------------------------
# Ch1–2 — Mover + forces
# ------------------------------------------------------------------

@dataclass
class Mover:
    pos: Vec2 = field(default_factory=Vec2)
    vel: Vec2 = field(default_factory=Vec2)
    acc: Vec2 = field(default_factory=Vec2)
    mass: float = 1.0
    max_speed: float = 10.0

    def apply_force(self, force: Vec2) -> None:
        # A = F / M
        f = force.copy().div(self.mass)
        self.acc.add(f)

    def update(self) -> None:
        self.vel.add(self.acc)
        self.vel.limit(self.max_speed)
        self.pos.add(self.vel)
        self.acc.mult(0)  # clear each frame

    def apply_friction(self, c: float = 0.1) -> None:
        if self.vel.mag_sq() == 0:
            return
        friction = self.vel.copy().normalize().mult(-c)
        self.apply_force(friction)


def gravity_force(mass: float, g: float = 0.1) -> Vec2:
    return Vec2(0, g * mass)


def wind_force(strength: float = 0.01) -> Vec2:
    return Vec2(strength, 0)


# ------------------------------------------------------------------
# Ch3 — simple oscillation helper
# ------------------------------------------------------------------

def oscillate(angle: float, amplitude: float = 1.0) -> float:
    """Simple harmonic value in [-amplitude, amplitude]."""
    return amplitude * math.sin(angle)


# ------------------------------------------------------------------
# Ch4 — Particle + Emitter
# ------------------------------------------------------------------

@dataclass
class Particle:
    pos: Vec2 = field(default_factory=Vec2)
    vel: Vec2 = field(default_factory=lambda: Vec2(random.uniform(-1, 1), random.uniform(-2, 0)))
    acc: Vec2 = field(default_factory=Vec2)
    lifespan: float = 255.0
    mass: float = 1.0

    def apply_force(self, force: Vec2) -> None:
        self.acc.add(force.copy().div(self.mass))

    def update(self) -> None:
        self.vel.add(self.acc)
        self.pos.add(self.vel)
        self.acc.mult(0)
        self.lifespan -= 2.0

    def is_dead(self) -> bool:
        return self.lifespan <= 0


@dataclass
class Emitter:
    origin: Vec2 = field(default_factory=Vec2)
    particles: List[Particle] = field(default_factory=list)

    def add_particle(self) -> None:
        p = Particle(pos=self.origin.copy())
        self.particles.append(p)

    def apply_force(self, force: Vec2) -> None:
        for p in self.particles:
            p.apply_force(force)

    def run(self) -> None:
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]


# ------------------------------------------------------------------
# Ch5 — Agent seek / flee
# ------------------------------------------------------------------

@dataclass
class Agent:
    pos: Vec2 = field(default_factory=Vec2)
    vel: Vec2 = field(default_factory=Vec2)
    acc: Vec2 = field(default_factory=Vec2)
    max_speed: float = 4.0
    max_force: float = 0.1

    def apply_force(self, force: Vec2) -> None:
        self.acc.add(force)

    def seek(self, target: Vec2) -> Vec2:
        desired = Vec2.sub_v(target, self.pos)
        desired.set_mag(self.max_speed)
        steer = Vec2.sub_v(desired, self.vel)
        steer.limit(self.max_force)
        return steer

    def flee(self, target: Vec2) -> Vec2:
        desired = Vec2.sub_v(self.pos, target)
        desired.set_mag(self.max_speed)
        steer = Vec2.sub_v(desired, self.vel)
        steer.limit(self.max_force)
        return steer

    def update(self) -> None:
        self.vel.add(self.acc)
        self.vel.limit(self.max_speed)
        self.pos.add(self.vel)
        self.acc.mult(0)


# ------------------------------------------------------------------
# Ch7 — elementary 1D CA step (usable seed)
# ------------------------------------------------------------------

def ca1d_step(cells: List[int], rule: int = 90) -> List[int]:
    """One step of elementary cellular automaton (Wolfram). cells are 0/1."""
    n = len(cells)
    out = [0] * n
    for i in range(n):
        left = cells[(i - 1) % n]
        center = cells[i]
        right = cells[(i + 1) % n]
        idx = (left << 2) | (center << 1) | right
        out[i] = 1 if (rule & (1 << idx)) else 0
    return out


# ------------------------------------------------------------------
# Smoke
# ------------------------------------------------------------------

def smoke() -> bool:
    print("=== NATURE_CODE SMOKE (Ch0–5 usable cores) ===")
    r: List[bool] = []

    def rec(name: str, ok: bool) -> None:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        r.append(ok)

    v = Vec2(3, 4)
    rec("Vec2 mag", abs(v.mag() - 5.0) < 1e-9)
    v.normalize()
    rec("Vec2 normalize", abs(v.mag() - 1.0) < 1e-9)

    w = Walker(pos=Vec2(0, 0))
    w.step_random()
    rec("Walker step", abs(w.pos.x) + abs(w.pos.y) == 1)

    g = gaussian(0, 1)
    rec("gaussian finite", math.isfinite(g))

    ar = accept_reject()
    rec("accept_reject range", 0.0 <= ar <= 1.0)

    m = Mover(mass=2.0)
    m.apply_force(Vec2(2, 0))
    m.update()
    rec("Mover apply_force", m.vel.x > 0)

    osc = oscillate(math.pi / 2, 1.0)
    rec("oscillate peak", abs(osc - 1.0) < 1e-9)

    em = Emitter(origin=Vec2(10, 10))
    em.add_particle()
    em.apply_force(gravity_force(1.0))
    em.run()
    rec("Emitter particle", len(em.particles) == 1)

    ag = Agent(pos=Vec2(0, 0))
    steer = ag.seek(Vec2(10, 0))
    ag.apply_force(steer)
    ag.update()
    rec("Agent seek", ag.vel.x > 0)

    cells = [0] * 11
    cells[5] = 1
    nxt = ca1d_step(cells, rule=90)
    rec("CA1D step", sum(nxt) >= 1)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
