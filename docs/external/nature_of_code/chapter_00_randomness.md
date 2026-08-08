Chapter 0 — Randomness

Source: https://natureofcode.com/random/

Summary:
Random walks, distributions, and Perlin noise. Walker object with position +
step(). Uniform vs nonuniform probability, Gaussian (randomGaussian),
accept-reject sampling, Perlin noise for smooth organic motion.

Key concepts (usable):
- Walker: pos + step_random / step_biased / step_gaussian
- gaussian(mean, std)
- accept_reject() for custom distributions
- Perlin-style smooth noise → later bind; host has no built-in noise (document)

Implemented in DellMatrix:
- `form/dell_matrix/nature_code.py` → Walker, gaussian, accept_reject
- Maps to ProbabilisticShell + FlowShell movement

Next: https://natureofcode.com/vectors/ (Chapter 1: Vectors)
