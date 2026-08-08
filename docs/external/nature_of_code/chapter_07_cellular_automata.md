Chapter 7 — Cellular Automata (notes)

Source: https://natureofcode.com/cellular-automata/

Summary:
Chapter 7 introduces cellular automata (CA) as grids of simple cells whose
local rules produce emergent global behavior. Key points:
- A cell has a discrete state (often 0 or 1) and updates synchronously based on
  neighbor states according to rules (e.g., Conway’s Game of Life, Wolfram's
  elementary CA rules).
- CA examples: 1D elementary automata, 2D Game of Life, reaction-diffusion
  systems; boundaries and wrapping behavior affect patterns.
- Emergence: simple local rules can create complex, persistent, or chaotic
  patterns; CA are useful for texture generation, simulations, and procedural
  content.
- Implementation tips: represent grid as 2D array, compute new grid from old
  to avoid in-place mutation, visualize using pixels or small rectangles.

Integration ideas:
- Add Game of Life / elementary CA demo under `form/dell_matrix/assets/examples`.
- Paraphrase seeds: concise statements about local rules → global patterns for
  `form/mandell/english_brain.py`.

Next: Chapter 8 (Fractals) — https://natureofcode.com/fractals/
