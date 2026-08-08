# Button + Path full coverage enhance loop × 150

**Runner:** `python -m form.dell_matrix.button_path_enhance_loop --cycles 150`  
**Result:** **GRADE A+ · 137/137 checks · 100%**  
**Buttons:** 266 (after nav hubs) · **unique cmds:** 59 · **paths:** 16  

## Coverage

### Routes (all load assets)

`/` `/menu` `/index.html` `/ui` `/walk` `/walk/world` `/lattice` `/nursery` `/program` `/personas` `/forces` `/geometry` `/matrices` `/console` `/css/app.css` `/js/core.js`

### Page → page hrefs

Every content page gets a **full nav hub**: Menu · Walk · Lattice · Nursery · Program · Personas · Forces · Geometry · Matrices · Console.

### Commands exercised (every cycle rotates these)

All static `data-cmd` / `data-fill` / `data-c` / `data-nav` values including:

- System: status · audit · evolve · pulse · save · look · guide  
- Forms: cube · sphere · core · flower · toggle  
- Growth: grow ×1/×2 · proposals · rank · confirm all · reject all  
- Personas/BIMO: full set  
- Forces/weather: clear/rain/storm/fog/calm  
- Geometry: verita · voynich · fractal  
- FP walk: forward/back/turn/up/down · strafe  
- Matrices · entities · home · nearest · radar · workshops  

### Enhancements applied

1. Nav hubs on all pages missing full cross-links  
2. `title=` on buttons from their data-cmd  
3. Core form button on walk world if missing  
4. Menu route completeness check  
5. Console fill completeness  
6. **150 cycles** executing / verifying each command path  

## Re-run

```bash
python3 -u -m form.dell_matrix.button_path_enhance_loop --cycles 150
python3 -m form.smoke_all
```

Authority: `form/dell_matrix/button_path_enhance_loop.py`
