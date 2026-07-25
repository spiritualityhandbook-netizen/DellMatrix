# Unification — One Era

## Problem
Two eras lived in one repo:
- New: foundation + dual lattice + snap-ins
- Old: DuoBeta scripts (execute_preform, autonomous_evolution, ...)

## Rule (locked)
**Foundation is truth. Legacy attaches. Legacy does not own boot.**

## Front door
```js
import { createUnifiedRuntime } from './src/unify.js'
// or
import { createUnifiedRuntime } from './src/index.js'

const dm = createUnifiedRuntime()
// dm.lattice, dm.snapIn, dm.oracle, dm.formatRouter, ...
// dm.legacy.load('autonomous_evolution') when needed
```

## Canonical homes
| Concern | Canonical path |
|---------|----------------|
| Living graph | `src/core/dual_lattice.js` |
| Boot | `src/unify.js` / `src/boot.js` |
| Snap-ins | `src/snapins/*` |
| Verita | `src/core/smith_map.js` |
| Forces | `src/forces` + `force_slots.js` |
| Format | `src/core/format_router.js` |
| Legacy tools | `dm.legacy.load(name)` |

## What not to do
- Do not boot from execute_preform as the root forever
- Do not create a second lattice beside dual_lattice
- Do not treat legacy files as equal authority to foundation

## Migration path
1. All new work uses createUnifiedRuntime()
2. Legacy features called only through dm.legacy.load
3. Over time, re-implement needed legacy behavior on foundation and delete dead paths
