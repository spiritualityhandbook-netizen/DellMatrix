# DellMatrix Architecture: Foundation + Snap-ins

## The rule

**DellMatrix foundation stays.**  
Everything else **snaps in and out**.

---

## Foundation (never removed)

- Dual Lattice (nodes, vesicas, shells)
- Choose center
- Growth stages
- Negative space
- Slots for nature forces
- Snap-in registry itself

File: `src/core/foundation.js` + `src/core/dual_lattice.js`

---

## Snap-ins (modular)

### View Rooms (`view-rooms`)
Only change how you **look**:
- Growth, Water, Force, Network, Personal, Shared, Ancient Psalms

### Workshops (`workshops`)
Workbenches where you **build/change**:
- Matrix Workshop — Flower / sphere / center / zoom
- Persona Workshop — AIs, directives, abilities, limits
- Perspective Workshop — design the view rooms
- BIMO Workshop — fusion bodies
- Psalms Workshop — psalms / guidance
- Mandel Workshop — the language itself

---

## How to use

```js
import { bootDellMatrix } from './src/snapins/index.js';

const dm = bootDellMatrix();

// See what can snap in
console.log(dm.listSnapIns());

// Snap workshops in when you need them
dm.snapIn('workshops');

// Enter a workshop
const ws = dm.getSnapIn('workshops').api.enterWorkshop(dm, 'persona');
console.log(ws);

// Leave workshop
dm.getSnapIn('workshops').api.leaveWorkshop(dm);

// Snap workshops out when done
dm.snapOut('workshops');
```

---

## Mental model

- Foundation = ground + frame of the house
- View rooms = windows
- Workshops = workbenches you roll in and out
