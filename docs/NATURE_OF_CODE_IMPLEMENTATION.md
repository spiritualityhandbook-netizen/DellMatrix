# Nature of Code → DellMatrix (full per-chapter map)

**Source:** Daniel Shiffman, *The Nature of Code* (Chapters 0–11)  
**Cores:** `form/dell_matrix/nature_code.py`  
**Physics tick:** `form/dell_matrix/nature_physics.py`  
**Symbolic forces:** `form/dell_matrix/forces.py` (ForceField)  
**Growth engine:** `form/dell_matrix/ringed_growth.py`  
**Evolution / decision:** `form/dell_matrix/code_evolution.py` + `decision_shells.py`  
**Canvas:** `form/dell_matrix/assets/pages/nature_code.html`  
**Live host:** `form/dell_matrix/live_visual.py` (routes, commands, movement, vision, iso)

Boolean host · Floor · Nursery remain intact. All physics and growth stay local / offline-first.

---

## Quick status matrix

| Ch | Title | Cores | Live behavior | Commands | Visual | Growth / Forces | Status |
|----|-------|-------|---------------|----------|--------|-----------------|--------|
| 0 | Randomness | Vec2, Walker, gaussian, accept_reject | Random walks on nodes, noise seeds | `nature walk`, `nature gaussian` | Mode 0/1 | Weather (rain seeds), Time | **Wired** |
| 1 | Vectors | Vec2 (add/sub/mult/mag/normalize/limit) | Position + velocity on plane | implicit in every tick | Mode 1 | Space force | **Wired** |
| 2 | Forces | Mover, attract, friction, gravity_force, wind | Idea nodes pulled by gravity wells + friction | `program_force_tick_nature`, force tick | Mode 2 | GravityForce wells | **Wired** |
| 3 | Oscillation | oscillate(angle, amplitude) | Breathing / angular phase on nodes | breath heartbeat | Mode 3 (planned) | BreathForce inhale/exhale | **Partial** |
| 4 | Particle Systems | Particle, Emitter | Lifespan particles from idea origins | `nature emit` | Mode 4 | Water streams as particle-like | **Wired** |
| 5 | Autonomous Agents | Agent (seek / flee) | Nodes seek high-score targets or flee | target in NatureBridge | Mode 5 | Growth affinity seek | **Wired** |
| 6 | Physics Libraries | Pure-force approximation (no Box2D) | Same as Ch2 + mass | force tick | — | Gravity + Space | **Approximated** |
| 7 | Cellular Automata | ca1d_step (Rule 90+) | 1-D CA on ring / lattice lines | `nature ca` | Mode 6 (CA) | RingedGrowth gates | **Wired** |
| 8 | Fractals | (link) recursive / L-system style | Self-similar branching of ideas | grow / ringed | geometry + lattice pages | RingedGrowth Solstice/Equinox, sacred_geometry | **Mapped** |
| 9 | Evolutionary Computing | population / fitness / selection | Code Evolution root + decision shells | `ce develop`, `ce status` | — | code_evolution + RingedGrowth | **Mapped** |
| 10 | Neural Networks | (seed) weighted sum / activation | Decision shells as soft neurons | prefer_open, OpenShell | — | decision_shells | **Planned seeds** |
| 11 | Neuroevolution | genome → network + fitness | Evolve controllers via CE + shells | develop_loop | — | code_evolution + GA operators | **Planned** |

---

## Chapter-by-chapter integration

### Chapter 0 — Randomness
**Core concepts:** uniform random, gaussian, accept-reject, random walks, noise as structured randomness.

**Cores implemented**
- `gaussian(mean, std)`
- `accept_reject()`
- `Walker.step_random()` / `step_biased()`
- `Vec2.random2d()`

**Live behavior**
- Idea nodes can take random or biased steps when no strong force is present.
- Weather “rain” drops new seed ideas (ForceField.weather).
- TimeForce advances the clock; random events can be gated by it.

**Commands / API**
```python
from form.dell_matrix.nature_code import Walker, gaussian
w = Walker(); w.step_biased(0.4)
```
Live: nature walk / gaussian modes on the canvas.

**Visual**
`/pages/nature_code.html` modes 0–1 (random walker trails).

**Growth / Forces**
- WeatherForce condition `rain` → new seeds.
- TimeForce.tick for aging random walks.

**Status:** Fully wired in cores + canvas. Optional: Perlin-style noise later as pure Python.

---

### Chapter 1 — Vectors
**Core concepts:** vector as magnitude + direction; add, subtract, scale, normalize, limit, magnitude.

**Cores implemented**
- Full `Vec2` with copy / add / sub / mult / div / mag / mag_sq / normalize / set_mag / limit / sub_v / random2d.

**Live behavior**
- Every idea node on the plane carries implicit position (x, y) treated as a vector.
- Velocity and acceleration live inside NatureBridge movers.

**Commands / API**
Implicit in every physics step. Direct:
```python
from form.dell_matrix.nature_code import Vec2
v = Vec2(3, 4); assert abs(v.mag() - 5) < 1e-9
```

**Visual**
Vector arrows / trails in nature_code.html mode 1.

**Growth / Forces**
- SpaceForce: distance and nearness use vector distance.
- RingedGrowth `_dist` uses hypot (vector length).

**Status:** Complete foundation for all later chapters.

---

### Chapter 2 — Forces
**Core concepts:** Newton’s 2nd law (F = m·a), force accumulation, gravity, friction, attraction (inverse-square).

**Cores implemented**
- `Mover` (pos, vel, acc, mass, max_speed, apply_force, update, apply_friction)
- `attract(a_pos, a_mass, b_pos, b_mass, G, min_dist)`
- `gravity_force`, `wind_force`
- `NatureBridge.step_nodes` — builds movers from nodes, applies wells + friction, writes new positions

**Live behavior**
```python
from form.open import open_program
from form.dell_matrix.nature_physics import program_force_tick_nature

p = open_program("Operator")
p.place("a", "Alpha", x=0, y=0)
p.place("b", "Beta", x=5, y=2)
report = program_force_tick_nature(p)
# report["nature_applied"] · Unit.x / Unit.y updated on the plane
```
Gravity wells are taken from ForceField.gravity.wells (highest-score ideas become attractors).

**Commands / API**
- `program_force_tick_nature(program)`
- Auto-wire option: call inside every `force_tick` on the live Program.

**Visual**
Mode 2 (forces / movers) on nature_code.html; live matrix shows moving nodes under iso or top-down.

**Growth / Forces**
- GravityForce.set_wells_from_scores → feeds NatureBridge attractors.
- Friction damps runaway motion so growth stays readable.

**Status:** Fully wired and proven. This is the primary “ideas move under real forces” path.

---

### Chapter 3 — Oscillation
**Core concepts:** angles, angular velocity/acceleration, sine/cosine oscillation, springs, pendulums, simple harmonic motion.

**Cores implemented**
- `oscillate(angle, amplitude)` (basic sine)
- BreathForce already models periodic inhale/exhale.

**Live behavior**
- BreathForce.heartbeat() drives a shared rhythm across the matrix.
- Future: attach angular phase to nodes so labels or skins “breathe” (scale/opacity pulse).

**Commands / API**
```python
ff = program.forces  # ForceField
ff.breath.heartbeat(len(nodes))
```

**Visual**
Mode 3 planned on nature_code.html (oscillators). Live: breath phase visible in status.

**Growth / Forces**
- BreathForce is the direct mapping: inhale = gather, exhale = release/share.
- Intensity and evolution_level rise with use.

**Status:** Partial (math + BreathForce). Full angular Mover (angle, aVelocity, aAcceleration) can be added without breaking Boolean host.

---

### Chapter 4 — Particle Systems
**Core concepts:** many independent particles, lifespan, emitters, applying forces to systems.

**Cores implemented**
- `Particle` (pos, vel, acc, lifespan, mass, apply_force, update, is_dead)
- `Emitter` (origin, particles, add_particle, apply_force, run)

**Live behavior**
- Emitters can be attached to high-score nodes; particles carry “idea fragments” that fade.
- WaterForce streams act as higher-level particle analogues (flow → merge → pool).

**Commands / API**
```python
from form.dell_matrix.nature_code import Emitter, Particle
e = Emitter(origin=Vec2(0,0)); e.add_particle(); e.run()
```

**Visual**
Mode 4 on nature_code.html (pointer steers / attracts particles).

**Growth / Forces**
- WaterForce.flow / merge_last_two / settle mirrors particle lifecycle at idea scale.
- Weather “storm” can shake particles loose.

**Status:** Cores + canvas wired. Optional: bind Emitter to live Program nodes.

---

### Chapter 5 — Autonomous Agents
**Core concepts:** steering behaviors (seek, flee, arrive, wander, path following, flocking).

**Cores implemented**
- `Agent` with seek() and flee()
- NatureBridge can inject a seek target so movers become agents.

**Live behavior**
- High-score ideas become seek targets; low-affinity or conflicting ideas can be fled.
- Vision cones (live_visual) already show what the agent “sees” in a direction.

**Commands / API**
```python
# inside NatureBridge.step_nodes when target is supplied
ag = Agent(...); force = ag.seek(Vec2(tx, ty))
```

**Visual**
Mode 5 (agents) + live directional vision cones + trails.

**Growth / Forces**
- RingedGrowth affinity + goal_boost act as the “desired velocity” for idea pairing.
- GrowthForce stages (seed → fruit) give agents long-term goals.

**Status:** Seek/flee wired. Flocking / path-follow can be layered later.

---

### Chapter 6 — Physics Libraries
**Core concepts:** rigid-body physics, constraints, collisions (typically Box2D / Matter.js).

**Cores implemented**
- Pure-Python approximation via Mover + attract + friction (no external library to stay offline/Boolean-host clean).

**Live behavior**
- Same as Chapter 2. Mass from score, inverse-square attraction, damping.
- Collisions can be soft (overlap repulsion) if added later.

**Commands / API**
Identical to `program_force_tick_nature`.

**Visual**
Same force mode; future soft-body or constraint lines optional.

**Growth / Forces**
- GravityForce + SpaceForce already provide the mass/distance field.

**Status:** Approximated intentionally (no native C++ dependency). Sufficient for idea-plane motion.

---

### Chapter 7 — Cellular Automata
**Core concepts:** discrete grid, neighborhood rules, emergent patterns (1-D elementary CA, 2-D Game of Life, etc.).

**Cores implemented**
- `ca1d_step(cells, rule=90)` (elementary 1-D, Rule 90 default).

**Live behavior**
- 1-D rings or lattice lines can evolve under CA rules.
- RingedGrowth “gates” (Solstice / Equinox / Standstill / None) act as discrete state transitions driven by affinity thresholds.

**Commands / API**
```python
from form.dell_matrix.nature_code import ca1d_step
next_gen = ca1d_step([0,1,0,1,1,0,0,1], rule=90)
```
Live: nature ca mode.

**Visual**
Mode 6 (CA) on nature_code.html.

**Growth / Forces**
- RingedGrowth is the higher-order CA: affinity → gate → new/evolved proposal in Nursery.

**Status:** 1-D core + mapping to growth gates wired. 2-D Life-style grid can be added on a lattice page.

---

### Chapter 8 — Fractals
**Core concepts:** self-similarity, recursion, L-systems, IFS, escape-time (Mandelbrot), fractal dimension.

**Cores / mapping**
- No dedicated fractal class yet; mapped onto existing geometry and growth:
  - `ringed_growth.py` — recursive pairing of ideas produces self-similar branching.
  - `sacred_geometry.py` — geometric primitives that can be subdivided.
  - Dual Lattice / HarmonicLattice already support recursive structure.

**Live behavior**
- Ideas branch via Solstice (new combined idea) and Equinox/Standstill (evolution of an existing idea).
- Depth is controlled by Nursery quarantine + fog filters (Aetheris clear).

**Commands / API**
```python
program.grow_ideas(cycles)  # RingedGrowth under the hood
```

**Visual**
geometry.html, lattice.html, and future recursive SVG / L-system renderer.

**Growth / Forces**
- RingedGrowth is the fractal engine for ideas.
- GrowthForce stages mirror recursive plant growth (seed → fruit).

**Status:** Conceptually mapped and operational via RingedGrowth. Explicit Koch / L-system / Mandelbrot viewers can be added as pure visual demos without touching the Boolean core.

---

### Chapter 9 — Evolutionary Computing (Genetic Algorithms)
**Core concepts:** population, genome, fitness function, selection, crossover, mutation, generational replacement.

**Cores / mapping**
- `code_evolution.py` — root development loop, completion checklist, grow_from_root, develop_loop.
- Decision shells (OpenShell, prefer_open, FlowShell) act as soft fitness surfaces.
- RingedGrowth supplies variation (new / evolved proposals) and selection (affinity + goal_boost).

**Live behavior**
- Code Evolution root is placed on the plane; develop_loop runs cycles of grow → force_tick → pulse → checklist until complete or budget exhausted.
- Proposals live in Nursery until confirmed (selection).

**Commands / API**
```python
from form.dell_matrix.code_evolution import develop_loop, format_status, exhaust_shells
out = develop_loop(program, cycles=8, internet=False)
print(format_status(program))
```
Live commands: `ce develop`, `ce status`.

**Visual**
Status text + plane nodes for the CE root and decision shells.

**Growth / Forces**
- Direct: code_evolution + RingedGrowth + decision_shells form a complete evolutionary loop for matrix ideas and decision surfaces.

**Status:** Operational for the Code Evolution worldwide root. Classic bit-string GA demo can be added later as a pure Nature page.

---

### Chapter 10 — Neural Networks
**Core concepts:** artificial neuron (weighted sum + activation), layers, feed-forward, error-driven learning / backprop (simplified).

**Cores / mapping**
- Decision shells already provide soft, graded, non-Boolean surfaces (OpenShell.grade, prefer_open).
- `self_model.py` and perception modules can host simple weight vectors.
- Seeds for english_brain / Mandell paraphrases exist in external notes.

**Live behavior**
- Soft decision surfaces replace hard Boolean gates where “maybe / open” is required.
- Future: a tiny feed-forward net whose inputs are node features (score, affinity, distance) and whose output modulates seek force or growth probability.

**Commands / API**
```python
from form.dell_matrix.decision_shells import prefer_open, OpenShell
s = prefer_open(0.68)
```

**Visual**
None dedicated yet; can reuse lattice / program pages to show activation strengths.

**Growth / Forces**
- Decision shells feed into Code Evolution completion and honesty labels (PROJECTED_NOT_FACT).

**Status:** Conceptual seeds + soft surfaces ready. Full multi-layer net is optional and must stay offline / pure-Python.

---

### Chapter 11 — Neuroevolution
**Core concepts:** evolve network weights (and optionally topology) with genetic operators instead of (or in addition to) gradient descent; fitness from agent performance.

**Cores / mapping**
- Combine Chapter 9 (code_evolution + RingedGrowth) with Chapter 10 (decision shells as networks).
- Genome can be a flat list of shell grades / affinity thresholds / force intensities.
- Fitness = completion checklist score, growth rate, or Verita coherence.

**Live behavior**
- develop_loop already iterates generations of growth + evaluation.
- Future: mutate ForceField intensities or NatureBridge G/friction and keep the variants that improve checklist or resonance.

**Commands / API**
Same develop_loop / ce surface; future `neuroevo step` can be added without breaking existing paths.

**Visual**
Status + plane evolution of the CE root.

**Growth / Forces**
- Full loop: variation (RingedGrowth / mutation) → selection (checklist / affinity) → inheritance (confirmed proposals, evolved force levels).

**Status:** Architecture ready via existing CE + shells + forces. Explicit neuroevolution of a small agent controller is the natural next experiment.

---

## How idea nodes move under Nature physics (Ch1–2 core path)

1. Build movers from node `x,y` and mass ≈ score.
2. Attract toward gravity wells (inverse-square via `attract`).
3. Optionally seek a target (Agent.seek).
4. Apply friction.
5. Update velocity & position; write back to `Unit.x` / `Unit.y`.

```python
from form.open import open_program
from form.dell_matrix.nature_physics import program_force_tick_nature

p = open_program("Operator")
# ... place nodes, optionally set program.forces.gravity wells ...
report = program_force_tick_nature(p)
# report["nature_applied"] · positions live on the lattice
```

Optional next wiring: call `program_force_tick_nature` automatically inside every `force_tick` so Nature physics is always on for the live Program.

---

## Visual & smoke

```text
http://127.0.0.1:8765/pages/nature_code.html
Keys: 1–6 switch mode · R reset · pointer steers agents / particles
```

```bash
python -m form.dell_matrix.nature_code
python -m form.dell_matrix.nature_physics   # if smoke added
python -m form.dell_matrix.forces
python -m form.dell_matrix.ringed_growth
python -m form.dell_matrix.code_evolution --smoke
```

---

## Design invariants (never break)

- Boolean host intact.
- Floor + Nursery quarantine for all new proposals.
- Offline / localhost core; no required network for physics or growth.
- Nature of Code physics is an enhancement layer on top of existing Mandell / Dual Lattice / Verita systems, not a replacement.
- Higher chapters (8–11) prefer mapping onto RingedGrowth, ForceField, code_evolution and decision_shells rather than introducing heavy external dependencies.

---

**Last updated:** complete Ch0–11 mapping pushed to main.  
Next optional steps: auto-force-tick Nature physics; explicit angular Mover for Ch3; tiny pure-Python perceptron seed for Ch10; neuroevo experiment on ForceField parameters.
