Appendix: Creature Design (notes)

Source: https://natureofcode.com/appendix-creature/

Summary:
This appendix provides practical guidance for designing creatures visually before
coding them in p5.js. Key points:
- Start with simple shapes and lines, then combine them into bodies, limbs, and
  details.
- Sketch first on paper to explore form, orientation, and design without code
  overhead.
- Use a body plus pairs of fins, wings, arms, or legs, and add features such as
  eyes, mouths, antennae, and tails to clarify direction and behavior.
- Consider the environment and how creature form suggests movement, style, and
  function.
- Keep designs simple, iterate, and treat every drawing as useful data for
  later refinement.

Implementation ideas:
- Build a creature library in `form/dell_matrix/assets/examples` using reusable
  rendering functions and OOP patterns.
- Use `translate()`, `rotate()`, `push()`, and `pop()` in p5.js to position
  features relative to the creature’s origin.
- Let visual form suggest behavior: a long narrow creature may drift, while big
  eyes or wide fins can imply alertness or gliding.

Next: Additional Resources — https://natureofcode.com/resources/
