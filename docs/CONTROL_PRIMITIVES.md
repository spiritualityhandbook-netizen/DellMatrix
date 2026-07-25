# Origin Control Primitives — ESTABLISHED

Source: early directive / ABCC origin form.
Status: **established in runtime**, not “later blocks.”

## Primitives

1. **Tier Memory** — Law (0) / Session (1) / Turn (2)
2. **Persona Contract** — name, voice, directives, abilities, limits (hard)
3. **Pre-Output Chain** — pins → persona limits → hard gates → anti-default
4. **Hard Gates** — truth, zero fluff, fog tool-only, Mandel/English, lattice, completeness, achievability, persona limits, anti-default
5. **Pin Set** — non-negotiable locked phrases/rules
6. **Anti-Default** — block generic autopilot AI voice

## What was rejected from origin hype
- Claims of directly editing transformer Q/K/V weights
- “Nuclear internals mastery” framing

## Files
- `src/core/control_primitives.js`
- `src/snapins/control_plane_pack.js`
- This doc

## Use
```js
const dm = createUnifiedRuntime()
dm.snapIn('control-plane')
dm.control.check({ hasFluff: false, genericAutopilot: false })
```
