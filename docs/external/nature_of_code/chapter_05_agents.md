Chapter 5 — Autonomous Agents (notes)

Source: https://natureofcode.com/autonomous-agents/

Summary:
Chapter 5 explores autonomous agents—entities that make local decisions to
move/act based on perception. Key points:
- Agents can be modeled as objects with internal decision rules; their "desires"
  are implemented as internal forces or behaviors (seek, flee, wander).
- Steering behaviors: `seek(target)`, `flee(target)`, `arrive(target)`,
  `wander()`, `pursue()`, `evade()`. Combine behaviors by weighting and adding
  resulting force vectors.
- Perception: agents sense nearby objects (neighbors, obstacles) within a
  radius and adjust behavior (e.g., cohesion, separation, alignment for
  flocking).
- Flocking: Reynolds’ rules (separation, alignment, cohesion) produce
  emergent group behavior.
- Implement `applyForce()` and limit forces/velocities to maintain stability.

Integration ideas:
- Paraphrase seeds for `form/mandell/english_brain.py` describing steering and
  flocking rules.
- Add a simple flocking demo under `form/dell_matrix/assets/examples`.

Next: Chapter 6 (Physics libraries / Matter.js & Toxiclibs) — https://natureofcode.com/physics-libraries/
