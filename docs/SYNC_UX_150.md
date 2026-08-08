# Full program page-by-page step-by-step 150-loop

**Pillars:** Synchronicity · Functionality · Usability  
**Runner:** `python -m form.dell_matrix.sync_ux_150_loop --cycles 150`  
**Result:** **GRADE A+ · 65/65 (100%)** after loop + cleanup  

## Walk order (10 pages × 15 steps = 150)

```
menu → walk → lattice → nursery → program
  → personas → forces → geometry → matrices → console
```

Each page, 15 steps:

| # | Pillar | What happens |
|---|--------|----------------|
| 1 | Sync | Inject **sync strip** (owner · ideas · form · gen · nursery · pillars · position) |
| 2–5 | Sync | Shared `formatSyncLine`, foot sync, state cache bust on cmd, CSS strip |
| 6–10 | Function | Run that page’s primary commands against live Program |
| 11–13 | Usability | Empty-state, keyboard hints, setFoot/setMeta wiring |
| 14 | Function | Route asset load check |
| 15 | Sync | Assert state payload keys after actions |

## Synchronicity

| Mechanism | Role |
|-----------|------|
| `DM.formatSyncLine(s)` | One string for all pages |
| `.sync-strip` + `#sync-text` | Live banner under chrome |
| Footer `setFoot(s)` | owner · ideas · nursery · gen · form · `@ (center)` |
| Cache bust on `sendCmd` ok | Next getState is fresh after mutations |

## Functionality (per page)

| Page | Commands exercised |
|------|-------------------|
| menu | status · look |
| walk | fp forward · turn · look · home |
| lattice | look · home · nearest · cube · sphere |
| nursery | grow · proposals · rank · pulse |
| program | status · audit · evolve · pulse · save · look |
| personas | personas · lens · bimo |
| forces | forces · tick · weather · pulse |
| geometry | geometry · flower · verita · cube · toggle |
| matrices | matrices · entities · status · audit |
| console | status · look · home · radar · lattice |

## Usability

- Keyboard hints on ledes where missing  
- Empty states point to next action  
- Nav hubs (from button/path loop) keep every page reachable  
- Titles on controls · busy toast · live meta  

## Re-run

```bash
python3 -u -m form.dell_matrix.sync_ux_150_loop --cycles 150
python3 -m form.smoke_all
```

## Related loops

| Module | Focus |
|--------|--------|
| `page_enhance_loop` | Menu + page polish |
| `button_path_enhance_loop` | Every button + every path |
| `sync_ux_150_loop` | **This** — sync + function + UX step-by-step |
| `visual_evolve_loop` | Walk world / multi-page A+ checklist |

Authority: `form/dell_matrix/sync_ux_150_loop.py`
