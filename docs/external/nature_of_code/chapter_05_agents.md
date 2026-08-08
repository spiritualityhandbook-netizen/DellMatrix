Chapter 5 — Autonomous Agents

Source: https://natureofcode.com/autonomous-agents/

Summary:
Steering behaviors: seek, flee, arrive, wander, flow field, path following,
flocking (separation, alignment, cohesion). Steering = desired − velocity,
limited by max_force.

Key concepts (usable now):
- Agent.seek(target) / Agent.flee(target)
- max_speed, max_force

Deferred (next growth):
- arrive, wander, flow field, path following, full flocking
- Spatial subdivision (bin-lattice / quadtree)

Implemented in DellMatrix:
- `form/dell_matrix/nature_code.py` → Agent.seek, Agent.flee
- Maps to look() / move() + prefer_open decision surfaces

Next: physics libraries / CA / fractals / evolution chapters
