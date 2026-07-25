# Dual Lattice Kernel

## Origin

Derived from the Flower of Life examination:

1. 2D circles → equal units, shared centers, recursive
2. Circles → spheres → contact packing, volumetric voids
3. Negative space → real medium for forces
4. Straight lines / squares → addressable grid for perspective and UI

## Two Lattices, One Matrix

| Lattice | Role | Geometry |
|---------|------|----------|
| **Sphere / Hex** | Living growth, resonance, contact | Continuous positions, vesica connections |
| **Cube / Square** | Perspective, navigation, phone UI | Discrete addresses, clear rooms |

Every node exists on both at once.

## Core Rules Implemented

1. **Equal units** — same radius for all spheres
2. **Any node can become center** — `setCenter(nodeId)` recomputes shells
3. **Resonance = vesica** — shared lens strength, not a thin edge
4. **Negative space** — forces attach here
5. **Radial shells** — growth expands outward from center
6. **Square projection** — phone viewport maps the living lattice onto a grid

## Perspective Matrix

Switching perspective does two things:

- **Center shift** — which node is the origin of view
- **Lens** — how you interpret the same lattice (Growth, Water, Force, Network, Personal, Shared)

Same data. Different look. Instant switch.

## Files

- `src/core/dual_lattice.js` — DualLattice + LatticeNode + vesica math
- `src/core/perspective_matrix.js` — lenses + phone grid projection

## Quick Use

```js
import { createDualLattice } from './core/dual_lattice.js';
import { createPerspectiveMatrix } from './core/perspective_matrix.js';

const lattice = createDualLattice();
const view = createPerspectiveMatrix(lattice);

const a = lattice.addNode({ label: 'First idea' });
const b = lattice.addNode({ label: 'Second idea' });
lattice.grow(a.id, 1.5);

view.setLens('growth');
console.log(view.render());

view.lookFrom(b.id); // b becomes new center
console.log(view.toPhoneGrid(7));
```
