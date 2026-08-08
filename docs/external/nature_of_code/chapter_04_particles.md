Chapter 4 — Particle Systems (notes)

Source: https://natureofcode.com/particles/

Summary:
Chapter 4 explains particle systems: collections of many small particles whose
individual behaviors combine to form complex phenomena like fire, smoke, and
waterfalls. Key points:
- Architecture: particle class (data + behavior), particle system (spawner,
  updater, renderer).
- Lifecycle: birth, update (apply forces, velocity, position), death (lifespan),
  and recycling.
- Efficiency: reuse dead particles (object pooling) to avoid allocation overhead.
- Visual variety: randomize initial properties (velocity, color, size) and apply
  behaviors (gravity, drag, noise) for richer effects.
- Group-level controls: emit rate, force fields, boundaries, collision handling.

Integration ideas:
- Add a small interactive particle demo under `form/dell_matrix/assets/examples`.
- Paraphrase seeds: lifecycle, pooling, and force-application sentences for
  `form/mandell/english_brain.py`.

Next: Chapter 5 (Autonomous Agents) — https://natureofcode.com/agents/
