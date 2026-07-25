# Full Incorporation from Large Directive Dump

## Truth boundary
Creative / structural mapping only.  
No scientific decipherment claimed for Linear A, Indus, Rongorongo, Voynich, or Wadi el-Hol.

---

## What was incorporated

### Foundation layer
| Piece | Source | File |
|-------|--------|------|
| Dual Lattice | Flower of Life | `dual_lattice.js` |
| 25 Dell Functions | Mandel_OS v12 codex | `dell_functions.js` |
| 4 Flows ↘↙↗↖ | Mandel_OS v12 | `dell_functions.js` |
| Agent Categories | PragLog/EvoLog/AutoLog/DellLog/AgentLog/Ancient_Psalms | `agent_categories.js` |
| Shared Canvas | Mandel Station multi-agent | `shared_canvas.js` |
| 6-Pillar Audit | Standing/Spect/Tonea/Spirea/ManDetail/Omegate | `six_pillar_audit.js` |
| Nature Forces | Water/Growth/Breath/Gravity/Time/Weather/Space | `forces/nature_forces.js` |

### Snap-ins
| Pack | Contains |
|------|----------|
| view-rooms | Growth, Water, Force, Network, Personal, Shared, Ancient Psalms |
| workshops | Matrix, Persona, Perspective, BIMO, Psalms, Mandel |
| personas-pack | Manny, Melody, Aetheris, Mathelody, The_Ancient |
| mandel-station | Omni-Station dispatcher + shared canvas + surface/logic mode |

### Ancient structural operators (not translations)
| Inspiration | Operator |
|-------------|----------|
| Linear A/B ledgers | ledger-shell + sumLedger |
| Rongorongo | retrograde walk ↖ |
| Wadi el-Hol | compression tokens |
| Voynich | 5-Ring (existing) |

---

## Boot

```js
import { bootDellMatrix } from './src/snapins/index.js';

const dm = bootDellMatrix();
console.log(dm.listSnapIns());
console.log(dm.listActive());
```

Default active: view-rooms, personas-pack, mandel-station.  
Workshops registered, snapped out until you need them.
