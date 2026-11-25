#!/usr/bin/env python3
"""Nature of Code cores for DellMatrix. Boolean host intact.

Ch0 Randomness · Ch1 Vectors · Ch2 Forces · Ch3 Oscillation ·
Ch4 Particles · Ch5 Agents · Ch7 CA1D · bridge for live lattice.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math, random

@dataclass
class Vec2:
    x: float = 0.0
    y: float = 0.0
    def copy(self):
        return Vec2(self.x, self.y)
    def add(self, other):
        self.x += other.x; self.y += other.y; return self
    def sub(self, other):
        self.x -= other.x; self.y -= other.y; return self
    def mult(self, s):
        self.x *= s; self.y *= s; return self
    def div(self, s):
        if s: self.x /= s; self.y /= s
        return self
    def mag(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    def mag_sq(self):
        return self.x*self.x + self.y*self.y
    def normalize(self):
        m = self.mag()
        if m > 0: self.div(m)
        return self
    def set_mag(self, m):
        return self.normalize().mult(m)
    def limit(self, max_mag):
        if self.mag_sq() > max_mag*max_mag: self.set_mag(max_mag)
        return self
    def heading(self):
        return math.atan2(self.y, self.x)
    def rotate(self, angle):
        c, s = math.cos(angle), math.sin(angle)
        x, y = self.x, self.y
        self.x = x * c - y * s
        self.y = x * s + y * c
        return self
    @staticmethod
    def sub_v(a, b):
        return Vec2(a.x - b.x, a.y - b.y)
    @staticmethod
    def from_angle(angle, mag=1.0):
        return Vec2(math.cos(angle) * mag, math.sin(angle) * mag)
    @staticmethod
    def random2d():
        a = random.uniform(0, 2*math.pi)
        return Vec2(math.cos(a), math.sin(a))

def gaussian(mean=0.0, std=1.0):
    return random.gauss(mean, std)

def accept_reject():
    while True:
        r1, r2 = random.random(), random.random()
        if r2 < r1: return r1

@dataclass
class Walker:
    pos: Vec2 = field(default_factory=Vec2)
    def step_random(self):
        c = random.randint(0, 3)
        if c == 0: self.pos.x += 1
        elif c == 1: self.pos.x -= 1
        elif c == 2: self.pos.y += 1
        else: self.pos.y -= 1
    def step_biased(self, right_prob=0.4):
        r = random.random()
        if r < right_prob: self.pos.x += 1
        elif r < right_prob+0.2: self.pos.x -= 1
        elif r < right_prob+0.4: self.pos.y += 1
        else: self.pos.y -= 1

@dataclass
class Mover:
    pos: Vec2 = field(default_factory=Vec2)
    vel: Vec2 = field(default_factory=Vec2)
    acc: Vec2 = field(default_factory=Vec2)
    mass: float = 1.0
    max_speed: float = 10.0
    def apply_force(self, force):
        self.acc.add(force.copy().div(self.mass))
    def update(self):
        self.vel.add(self.acc); self.vel.limit(self.max_speed); self.pos.add(self.vel); self.acc.mult(0)
    def apply_friction(self, c=0.1):
        if self.vel.mag_sq() == 0: return
        self.apply_force(self.vel.copy().normalize().mult(-c))

@dataclass
class AngularMover:
    """Ch3 Oscillation — angle, aVelocity, aAcceleration + polar radius."""
    pos: Vec2 = field(default_factory=Vec2)
    angle: float = 0.0
    a_vel: float = 0.0
    a_acc: float = 0.0
    radius: float = 1.0
    origin: Vec2 = field(default_factory=Vec2)
    damping: float = 0.995

    def apply_torque(self, torque: float):
        self.a_acc += torque

    def update(self):
        self.a_vel += self.a_acc
        self.a_vel *= self.damping
        self.angle += self.a_vel
        self.a_acc = 0.0
        self.pos = Vec2(
            self.origin.x + math.cos(self.angle) * self.radius,
            self.origin.y + math.sin(self.angle) * self.radius,
        )

    def oscillate_step(self, amplitude: float = 1.0, frequency: float = 0.08):
        """Simple harmonic drive toward amplitude * sin(angle)."""
        target = amplitude * math.sin(self.angle)
        # treat as spring-ish torque toward target angle rate
        self.apply_torque((target - self.a_vel) * frequency)
        self.update()
        return self.pos.copy()

def gravity_force(mass, g=0.1):
    return Vec2(0, g*mass)

def wind_force(strength=0.01):
    return Vec2(strength, 0)

def oscillate(angle, amplitude=1.0):
    return amplitude * math.sin(angle)

def spring_force(pos: Vec2, anchor: Vec2, rest_len: float = 1.0, k: float = 0.1) -> Vec2:
    force = Vec2.sub_v(pos, anchor)
    stretch = force.mag() - rest_len
    force.normalize().mult(-k * stretch)
    return force

@dataclass
class Particle:
    pos: Vec2 = field(default_factory=Vec2)
    vel: Vec2 = field(default_factory=lambda: Vec2(random.uniform(-1,1), random.uniform(-2,0)))
    acc: Vec2 = field(default_factory=Vec2)
    lifespan: float = 255.0
    mass: float = 1.0
    def apply_force(self, force):
        self.acc.add(force.copy().div(self.mass))
    def update(self):
        self.vel.add(self.acc); self.pos.add(self.vel); self.acc.mult(0); self.lifespan -= 2.0
    def is_dead(self):
        return self.lifespan <= 0

@dataclass
class Emitter:
    origin: Vec2 = field(default_factory=Vec2)
    particles: List[Particle] = field(default_factory=list)
    def add_particle(self):
        self.particles.append(Particle(pos=self.origin.copy()))
    def apply_force(self, force):
        for p in self.particles: p.apply_force(force)
    def run(self):
        for p in self.particles: p.update()
        self.particles = [p for p in self.particles if not p.is_dead()]

@dataclass
class Agent:
    pos: Vec2 = field(default_factory=Vec2)
    vel: Vec2 = field(default_factory=Vec2)
    acc: Vec2 = field(default_factory=Vec2)
    max_speed: float = 4.0
    max_force: float = 0.1
    def apply_force(self, force):
        self.acc.add(force)
    def seek(self, target):
        desired = Vec2.sub_v(target, self.pos).set_mag(self.max_speed)
        return Vec2.sub_v(desired, self.vel).limit(self.max_force)
    def flee(self, target):
        desired = Vec2.sub_v(self.pos, target).set_mag(self.max_speed)
        return Vec2.sub_v(desired, self.vel).limit(self.max_force)
    def update(self):
        self.vel.add(self.acc); self.vel.limit(self.max_speed); self.pos.add(self.vel); self.acc.mult(0)

def ca1d_step(cells, rule=90):
    n = len(cells); out = [0]*n
    for i in range(n):
        left, center, right = cells[(i-1)%n], cells[i], cells[(i+1)%n]
        idx = (left<<2)|(center<<1)|right
        out[i] = 1 if (rule & (1<<idx)) else 0
    return out

def attract(a_pos, a_mass, b_pos, b_mass, G=0.4, min_dist=2.0):
    force = Vec2.sub_v(b_pos, a_pos)
    d = max(min_dist, force.mag())
    force.set_mag((G*a_mass*b_mass)/(d*d))
    return force

@dataclass
class NatureBridge:
    G: float = 0.35
    friction: float = 0.04
    max_speed: float = 0.85
    movers: Dict[str, Mover] = field(default_factory=dict)
    angular: Dict[str, AngularMover] = field(default_factory=dict)
    osc_amplitude: float = 0.15
    osc_frequency: float = 0.06
    breath_phase: str = "inhale"  # inhale | exhale — drives oscillation sign

    def ensure_mover(self, node_id, x, y, mass=1.0):
        m = self.movers.get(node_id)
        if m is None:
            m = Mover(pos=Vec2(float(x), float(y)), mass=max(0.2, float(mass)), max_speed=self.max_speed)
            self.movers[node_id] = m
        else:
            if abs(m.pos.x - x) + abs(m.pos.y - y) > 8:
                m.pos = Vec2(float(x), float(y))
            m.mass = max(0.2, float(mass))
        return m

    def ensure_angular(self, node_id, x, y, radius=0.8):
        a = self.angular.get(node_id)
        if a is None:
            a = AngularMover(
                origin=Vec2(float(x), float(y)),
                radius=radius,
                angle=random.uniform(0, 2 * math.pi),
            )
            self.angular[node_id] = a
        else:
            # soft-follow origin if node drifted far
            if abs(a.origin.x - x) + abs(a.origin.y - y) > 6:
                a.origin = Vec2(float(x), float(y))
        return a

    def set_breath_phase(self, phase: str):
        p = (phase or "inhale").lower()
        self.breath_phase = "exhale" if p.startswith("ex") else "inhale"

    def step_nodes(self, nodes, wells=None, target=None, use_oscillation=True):
        if not nodes: return []
        for n in nodes:
            nid = str(n.get('id') or '')
            if not nid: continue
            mass = float(n.get('mass') or n.get('score') or 1.0) + 0.5
            self.ensure_mover(nid, float(n.get('x') or 0), float(n.get('y') or 0), mass)
            if use_oscillation:
                self.ensure_angular(nid, float(n.get('x') or 0), float(n.get('y') or 0))
        attractors = []
        if wells:
            for w in wells:
                attractors.append((Vec2(float(w.get('x') or 0), float(w.get('y') or 0)), float(w.get('mass') or 2.0)))
        else:
            ranked = sorted(nodes, key=lambda n: -float(n.get('score') or 0))[:3]
            for n in ranked:
                attractors.append((Vec2(float(n.get('x') or 0), float(n.get('y') or 0)), float(n.get('score') or 1)+1.5))
        # breath modulates oscillation amplitude sign
        amp = self.osc_amplitude if self.breath_phase == "inhale" else -self.osc_amplitude * 0.6
        updates = []
        for n in nodes:
            nid = str(n.get('id') or '')
            m = self.movers.get(nid)
            if m is None: continue
            for apos, amass in attractors:
                m.apply_force(attract(m.pos, m.mass, apos, amass, G=self.G))
            if target is not None:
                ag = Agent(pos=m.pos.copy(), vel=m.vel.copy(), max_speed=self.max_speed, max_force=0.12)
                m.apply_force(ag.seek(Vec2(target[0], target[1])))
            # Ch3: mild oscillatory force from AngularMover
            if use_oscillation:
                ang = self.angular.get(nid)
                if ang is not None:
                    ang.oscillate_step(amplitude=amp, frequency=self.osc_frequency)
                    # pull mover slightly toward angular pos (orbit wobble)
                    pull = Vec2.sub_v(ang.pos, m.pos).mult(0.08)
                    m.apply_force(pull)
            m.apply_friction(self.friction); m.update()
            updates.append({
                'id': nid,
                'x': round(m.pos.x, 4),
                'y': round(m.pos.y, 4),
                'vx': round(m.vel.x, 4),
                'vy': round(m.vel.y, 4),
                'mass': m.mass,
                'angle': round(self.angular[nid].angle, 4) if nid in self.angular else 0.0,
            })
        return updates

    def status(self):
        return {
            'movers': len(self.movers),
            'angular': len(self.angular),
            'G': self.G,
            'friction': self.friction,
            'max_speed': self.max_speed,
            'osc_amplitude': self.osc_amplitude,
            'breath_phase': self.breath_phase,
            'note': 'Nature of Code physics bridge · Ch3 oscillation · Boolean host intact',
        }

_BRIDGE = NatureBridge()

def nature_step(nodes, wells=None):
    return _BRIDGE.step_nodes(nodes, wells=wells)

def nature_status():
    return _BRIDGE.status()

def smoke():
    print('=== NATURE_CODE SMOKE ===')
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)
    v = Vec2(3,4); rec('mag', abs(v.mag()-5)<1e-9)
    m = Mover(mass=2); m.apply_force(Vec2(2,0)); m.update(); rec('mover', m.vel.x>0)
    am = AngularMover(radius=1.0); am.oscillate_step(0.5, 0.1); rec('angular', abs(am.pos.x) + abs(am.pos.y) > 0)
    ups = NatureBridge().step_nodes([{'id':'a','x':0,'y':0,'score':1},{'id':'b','x':5,'y':0,'score':2}])
    rec('bridge', len(ups)==2)
    rec('angle_field', 'angle' in (ups[0] if ups else {}))
    print(f'=== {sum(r)}/{len(r)} ==='); return all(r)

if __name__ == '__main__':
    import sys; sys.exit(0 if smoke() else 1)
