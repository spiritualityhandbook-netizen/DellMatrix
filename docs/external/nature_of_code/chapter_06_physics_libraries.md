Chapter 6 — Physics Libraries (notes)

Source: https://natureofcode.com/physics-libraries/

Summary:
Chapter 6 surveys physics libraries and when to use them versus hand-rolled
simulations. Key points:
- Libraries (e.g., Matter.js, Toxiclibs.js) provide robust collision, constraint,
  and rigid-body simulations; they speed up development for complex interactions.
- Learning fundamentals first helps you understand and customize library
  behavior; libraries can obscure algorithmic details.
- Use libraries when precision and complex interactions are required; keep
  lightweight hand-rolled code for pedagogical or artistic control.
- Example integration ideas: provide optional adapters/wrappers to switch
  between p5.js native sim and Matter.js in examples under
  `form/dell_matrix/assets/examples`.

Integration seeds:
- Paraphrase sentences explaining tradeoffs between custom code and libraries
  for `form/mandell/english_brain.py`.
- Small adapter scaffold to toggle physics backends (pseudocode) for examples.

Next: Chapter 7 (Cellular Automata / Complex Systems) — https://natureofcode.com/cellular-automata/
