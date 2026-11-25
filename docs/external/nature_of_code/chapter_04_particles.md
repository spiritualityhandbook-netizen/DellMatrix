Chapter 4 — Particle Systems

Source: https://natureofcode.com/particles/

Summary:
Particle with lifespan; Emitter manages birth/update/death; systems of systems;
inheritance; forces and repellers on particles.

Key concepts (usable):
- Particle (pos, vel, acc, lifespan, is_dead)
- Emitter (origin, add_particle, run, apply_force)
- Cull dead each frame

Implemented in DellMatrix:
- `form/dell_matrix/nature_code.py` → Particle, Emitter
- Maps to multiple shells + GrowthResidue aggregation

Next: https://natureofcode.com/autonomous-agents/ (Chapter 5)
