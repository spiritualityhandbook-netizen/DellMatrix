# GDP-001 Phase 4 — External Research Record

**Date:** 2026-10-04 · **Phase:** 4 (Living Spatial Matrix)

## Classification summary

| Idea | Class | DellMatrix analog / decision |
|---|---|---|
| Fruchterman–Reingold bounded displacement + temperature | ADAPT | Per-tick displacement cap; deterministic init; no random coincidence resolution |
| Force-directed layout as truth discovery | REJECT | Coordinates never discover semantic truth; emergent geometry ≠ meaning |
| Dynamic-graph mental-map criteria (decreasing max movement, bounded propagation, reversal penalty) | ADOPT | Stability proof: bounded local consequence of insertion |
| Barycentric placement from admitted neighbors | ADOPT | Deterministic initial placement when graph neighbors exist |
| Deterministic neutral spiral fallback | ADOPT | Sparse/isolate placement; explicitly neutral, never claims meaning |
| Uniform-grid spatial hashing | ADOPT | O(n) neighbor queries for hundreds/low thousands of ideas |
| Quadtree / Barnes–Hut | DEFER | Until measurements justify; current scale does not need it |
| Hard-cutoff short-range separation | ADAPT | Anti-pileup only; not a semantic statement |
| Friction + cooling + dual stop (epsilon / iteration budget) | ADOPT | Damped adjustment; budget exhaustion = honest non-convergence |
| Dependency-aware incremental updates | ADAPT | Active-set filtering; no routine global recomputation |
| Finite-number guards, epsilon clamping | ADOPT | NaN/inf fail-closed; min-distance clamps |

## Key sources

- Fruchterman & Reingold, "Graph Drawing by Force-Directed Placement" — https://reingold.co/force-directed.pdf
- Tamassia (ed.), Handbook of Graph Drawing, force-directed chapter — https://cs.brown.edu/people/rtamassi/gdhandbook/chapters/force-directed.pdf
- Diehl & Görg, "Graph Drawing in Motion" (mental-map preservation) — https://jgaa.info/index.php/jgaa/article/download/paper57/2914
- Jacomy et al., ForceAtlas2 — https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0098679
- react-force-graph / d3-force mechanics — https://github.com/vasturiano/react-force-graph/blob/master/README.md

## Disconfirming evidence (kept)

ForceAtlas2 authors acknowledge: initialization sensitivity, local minima,
nondeterminism, and coordinates that do not directly represent a variable.
Therefore only *constrained mechanics* are reusable; emergent geometry is
never semantic truth. This is why Phase 4 adapts the math but rejects the
layout-as-discovery philosophy.

## DellMatrix-specific synthesis

The novel contribution is not the force math (well-studied) but the
*authority architecture*: one canonical decider (SpatialAuthority), Plane as
identity-keyed store, lattice as derived projection, weather as bounded force
modulator with no semantic write path, Phase-3 lifecycle as participation
gate. The math is admitted per-equation with authority classification;
the architecture is what makes the math safe.
