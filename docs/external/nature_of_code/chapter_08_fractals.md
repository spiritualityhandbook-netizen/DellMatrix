Chapter 8 — Fractals (notes)

Source: https://natureofcode.com/fractals/

Summary:
Chapter 8 introduces fractals as geometric shapes and processes that exhibit
self-similarity across scales and often have non-integer (fractal) dimensions.
Key points:
- Fractals appear in nature (coastlines, trees, clouds, blood vessels) and can
  be generated via recursive subdivision, iterated function systems (IFS),
  L-systems, escape-time fractals (Mandelbrot/Julia sets), and random fractal
  terrains.
- Self-similarity: exact (pure recursion) or statistical (natural forms).
- Fractal dimension: measures complexity; common methods include box-counting
  and Hausdorff dimension intuition.
- Generation techniques:
  - Recursive subdivision (e.g., Cantor set, Koch curve, Sierpinski gasket).
  - L-systems for plant-like branching structures.
  - Iterated function systems for affine-transformation-based fractals.
  - Escape-time algorithms for complex dynamics (Mandelbrot set).
- Visualization tips: iterative drawing, escape-time coloring, using recursion
  limits to control detail, and combining randomness for natural variability.

Implementation notes:
- Represent recursive structures with simple functions that draw and call
  themselves with scaled transforms; avoid too-deep recursion on JS engines by
  limiting depth and using iterative approximations for heavy workloads.
- For escape-time fractals, iteratively compute complex iterations and color
  by iteration count; optimize with tiling or WebGL for performance.

Integration ideas:
- Add examples to `form/dell_matrix/assets/examples`: Koch curve, Sierpinski
  triangle, simple L-system tree, and a Mandelbrot viewer (WebGL optional).
- Create paraphrase seeds for `form/mandell/english_brain.py` capturing core
  ideas: "self-similarity", "recursive subdivision produces detail", "fractal
  dimension measures complexity".

Next: Chapter 9 (Noise) — https://natureofcode.com/noise/
