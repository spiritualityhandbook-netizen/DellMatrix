# form/ Matrices — Ported from src/ (LEGACY)

**Date:** 2026-08-06  
**Rule:** `src/` stays frozen. Useful systems are **reimplemented** in `form/`, not imported.

## What landed in form/

| LEGACY (src/) | form/ module | Commands |
|---------------|--------------|----------|
| `snapins/personas_pack.js` | `dell_matrix/personas.py` | `personas` · `persona manny\|…` · `guide` |
| `snapins/view_rooms.js` | `dell_matrix/view_rooms.py` | `rooms` · `view growth\|water\|…` |
| `snapins/workshops.js` | `dell_matrix/workshops.py` | 7 workshops including persona/bimo/psalms/forces |
| `forces/nature_forces.js` | `dell_matrix/forces.py` | `forces` · `force tick` · `weather …` · `evolve` |
| `core/six_pillar_audit.js` | `dell_matrix/pillars.py` | `audit` |
| `visual/ascii_bodies.js` | `dell_matrix/ascii_bodies.py` | `body stick\|block\|shadow\|robot` · shown in `look`/`render` |
| snap-in inventory | `dell_matrix/matrices_hub.py` | `matrices` · `evolve` |

## Grow & evolve

```text
you> grow ideas 2          # nursery + plant stages + water streams
you> evolve                # DuoBeta gen++ · force tick · 6-pillar re-score
you> force tick            # pulse active nature forces only
you> audit                 # Standing/Spect/Tonea/Spirea/ManDetail/Omegate
you> matrices              # full inventory of live form/ matrices
```

`Program.evolve()` = generation ledger + force field + pillar audit.  
`grow ideas` also advances GrowthForce plant stages and water streams.

## Still LEGACY (not ported — reference only)

Heavy JS-only surfaces left as design seeds if ever needed:

- `omega_lexer` / oracle protocol full protocol stack  
- `format_router` adapters  
- `psalm_genesis` / sanctuary UI  
- `stigmergic` / full DualLattice class (form already has harmonic lattice + FoL)  
- `smith_map` / DNA profile / neural patterns as full engines  

Port only when a user path needs them; prefer thin form/ reimplementation.

## Smoke

```bash
python3 -m form.smoke_all
# 29/29 including personas · view_rooms · forces · pillars · workshops · matrices_hub · ascii_bodies
```
