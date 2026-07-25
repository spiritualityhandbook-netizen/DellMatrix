# Ancient Psalms — Truth Boundary & Operators

## Truth Boundary (Locked)

DellMatrix does **not** claim scientific decipherment of:

- Linear A (undeciphered)
- Indus Valley Script (undeciphered)
- Rongorongo (undeciphered)
- Voynich Manuscript (undeciphered)
- Wadi el-Hol (proto-alphabetic, partially understood)

Linear B is historically deciphered as Mycenaean Greek; we use only its **structural** patterns (syllabic grid, inventory format).

What we do: extract **structural operators** and bind them into the Dual Lattice as lawful system behavior.

---

## Category

- **ID:** `Ancient_Psalms`
- **Presence:** 🏺 📜 🗿
- **Type:** Cube Room (Perspective lens)
- **Persona:** The_Ancient 🪨

---

## Operators Bound

| Source inspiration | Operator in DellMatrix |
|--------------------|-------------------------|
| Linear A / B ledgers | `ledger-shell` + `sumLedger()` (KU-RO style total) |
| Rongorongo reverse boustrophedon | `setTraversalMode('retrograde')` + `walkFrom()` |
| Wadi el-Hol acrophonic | `_compressToken()` on every node |
| Indus seal clusters | High vesica density on shared shell |
| Voynich 5-Ring | Already mapped in Harmonic / 5-Ring system |

---

## How to use

```js
import { createDualLattice } from '../src/core/dual_lattice.js';
import { createPerspectiveMatrix } from '../src/core/perspective_matrix.js';

const lattice = createDualLattice();
const view = createPerspectiveMatrix(lattice);

view.setLens('ancient_psalms');
view.setPersona('The_Ancient');

const a = lattice.addLedgerItem({ label: 'grain', amount: 12 });
const b = lattice.addLedgerItem({ label: 'oil', amount: 3 });
const sum = lattice.sumLedger([a.id, b.id]);

lattice.setTraversalMode('retrograde');
const path = lattice.walkFrom(a.id, 4);

console.log(view.render());
console.log(view.toPhoneGrid(7));
```

---

## Files touched

- `src/core/dual_lattice.js` — retrograde, ledger, tokens
- `src/core/perspective_matrix.js` — ancient_psalms lens + phone grid fields
- `src/core/persona_guidance.js` — The_Ancient
- `docs/ANCIENT_PSALMS.md` — this boundary document
