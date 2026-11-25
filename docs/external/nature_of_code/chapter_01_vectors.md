Chapter 1 — Vectors

Source: https://natureofcode.com/vectors/

Summary:
Euclidean vectors (magnitude + direction) as building block for motion.
position, velocity, acceleration. add / sub / mult / normalize / limit.

Key concepts (usable):
- Vec2 with mag, normalize, limit, heading
- Motion loop: vel.add(acc); pos.add(vel); acc.clear

Implemented in DellMatrix:
- `form/dell_matrix/nature_code.py` → Vec2, Mover base
- Maps to FlowShell direction + grade-as-magnitude

Next: https://natureofcode.com/forces/ (Chapter 2)
