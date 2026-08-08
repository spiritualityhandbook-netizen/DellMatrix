Chapter 2 — Forces

Source: https://natureofcode.com/forces/

Summary:
Newton F=MA, force accumulation, friction, drag, gravitational attraction,
n-body. applyForce adds to acceleration; clear acc each frame.

Key concepts (usable):
- apply_force(force) → acc += force/mass
- gravity_force, wind_force, apply_friction
- Full inverse-square n-body → documented, optional later

Implemented in DellMatrix:
- `form/dell_matrix/nature_code.py` → Mover.apply_force, gravity_force, wind_force, apply_friction

Next: https://natureofcode.com/oscillation/ (Chapter 3)
