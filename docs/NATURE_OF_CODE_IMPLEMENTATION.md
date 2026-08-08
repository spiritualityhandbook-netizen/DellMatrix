# Nature of Code → DellMatrix Implementation Map

**Source:** Daniel Shiffman, *The Nature of Code* (https://natureofcode.com/)  
**Repo notes:** `docs/external/nature_of_code/`  
**Runnable cores:** `form/dell_matrix/nature_code.py`  
**Law:** Only concepts that fit and are usable. Boolean host intact. PROJECTED_NOT_FACT on full p5.js / visual runtime.

---

## Fit rule

| Criterion | Action |
|-----------|--------|
| Pure algorithm, no canvas required | Implement in Python |
| Maps to existing decision shells / FlowShell | Bind or reuse |
| Needs full graphics / physics library | Document only + PROJECTED |
| Strengthens continuous fuel / multi-directional flow | Prefer |

---

## Chapter → Implementation

### Ch0 Randomness — **IMPLEMENTED**
- Walker (random step, biased step)
- Gaussian sample
- Accept-reject sample
- Maps to: ProbabilisticShell, FlowShell movement noise

### Ch1 Vectors — **IMPLEMENTED**
- Vec2 (add, sub, mult, mag, normalize, limit)
- Position / velocity / acceleration loop
- Maps to: FlowShell direction + grade as magnitude

### Ch2 Forces — **IMPLEMENTED (core)**
- apply_force → acceleration
- Simple gravity / wind as force vectors
- Friction sketch (oppose velocity)
- Full n-body / drag coefficients → documented, not full sim

### Ch3 Oscillation — **PARTIAL**
- Angular step / simple harmonic grade oscillation helper
- Full spring/pendulum visual → PROJECTED

### Ch4 Particle Systems — **IMPLEMENTED (core)**
- Particle (lifespan, update, is_dead)
- Emitter (add, run, cull dead)
- Maps to: multiple shells as a system; GrowthResidue aggregation

### Ch5 Autonomous Agents — **IMPLEMENTED (core)**
- seek / flee steering
- Agent with max_speed / max_force
- Maps to: look() / move() + prefer_open decision surface
- Full flocking / flow-field / path-following → next growth (documented)

### Ch6 Physics Libraries — **DOC ONLY**
- External engines (Box2D-style) → PROJECTED_NOT_FACT in host

### Ch7 Cellular Automata — **DOC + seed**
- 1D elementary CA step (usable)
- Full 2D Game of Life grid → optional next

### Ch8 Fractals — **DOC + seed**
- Recursive depth / branch factor as GrowthResidue pattern
- Full L-system / Mandelbrot visual → PROJECTED

### Ch9 Evolutionary Computing — **DOC + seed**
- Fitness → selection weight (maps to grade / ResourceShell)
- Full GA population → next growth

### Ch10–11 Neural / Neuroevolution — **DOC ONLY**
- Graded decision already exists (OpenShell)
- Full net + NEAT-style → PROJECTED_NOT_FACT

---

## Runnable entry

```bash
python -m form.dell_matrix.nature_code
```

## Relation to Code Evolution

- Randomness / probability → ProbabilisticShell
- Direction + magnitude → FlowShell / look / move
- Forces on grade → continuous fuel, not forced Boolean cut
- Particles / agents → multiple open surfaces + aggregate_looks
- Evolution → GrowthResidue permanent fuel (never closed)

**True · Dense · Placed · Runnable · Labeled · Finishable**
