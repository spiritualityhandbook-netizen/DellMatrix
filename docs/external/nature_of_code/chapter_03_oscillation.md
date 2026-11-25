Chapter 3 — Oscillation (notes)

Source: https://natureofcode.com/oscillation/

Summary:
Chapter 3 introduces oscillation and trigonometry as tools for modeling
back-and-forth motion. Key points:
- Use angles, sine and cosine to produce smooth periodic motion.
- Angular velocity and angular acceleration mirror linear kinematics (position,
  velocity, acceleration) but in rotational space.
- Model pendulums and springs: pendulum uses torque and angular acceleration;
  springs follow Hooke’s law (force proportional to displacement).
- Use `sin()` and `cos()` to map oscillatory values to x/y positions for smooth
  wave patterns and easing.
- Convert between radians/degrees and manage angle wrapping.

Practical seeds for DellMatrix:
- Short paraphrase lines explaining `sin()`/`cos()` use and angular kinematics for
  `form/mandell/english_brain.py`.
- Example code snippets (p5.js) for a simple oscillator and a pendulum demo to
  add under `form/dell_matrix/assets/examples`.

Next: Chapter 4 (Particle Systems) — https://natureofcode.com/particles/
