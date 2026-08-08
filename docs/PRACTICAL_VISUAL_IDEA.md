# Practical Visual Idea — First-Person Infinite Matrix

**Date:** 2026-08-07  
**Status:** A+ Matrix Walk rebuild · evolve loop 150/150 @ 100%  
**Runtime:** `first_person.py` + `live_visual.py` + `assets/fp_world.html`  
**Bridge:** Pure Mandell addresses every centerpoint  
**UI file:** `form/dell_matrix/assets/fp_world.html` 

---

## 1. Full audit snapshot (DEV Operator)

| Area | Verdict | Notes |
|------|---------|--------|
| Cube-to-cube step | **OK** | Integer (H,V,F); W/S/A/D/R/F work |
| Infinite space | **OK** | No world bounds; empty cells still enterable |
| Occupancy (DEV) | **Dense** | 160 ideas on unique cells; 7×7 origin full |
| Face visibility | **OK** | Front · left · right · top · bottom (no back until turn) |
| Grid / edges | **OK** | CSS lattice lines + wire shell |
| Dual lattice | **OK** | cube ↔ sphere form changes cell grammar + look |
| Mandell bridge | **Partial → fixed** | Each cell: `15[Map] :: CubeCell@(h,v,f)` on step |
| English → Mandell FP | **Partial → fixed** | `fp forward`, `enter next cube`, turns, up/down phrases |
| Resonance pages | **OK** | Forces + score + distance rank what appears |
| Fun / cool / intuitive | **Iterate** | Structure clear; polish motion + empty-cell craft |

### Gaps to keep evolving

1. **Step animation** — brief lunge / fade when entering next cube  
2. **Empty-cell craft** — void cubes should still feel like real rooms (dim lattice, shell number)  
3. **Data density in far void** — auto soft-ghost of high-resonance ideas on distant faces  
4. **Mandell always visible** — HUD + each face address (in progress)  
5. **Sphere mode depth** — stronger non-cube silhouette without losing face readability  

---

## 2. Core metaphor (what you are building)

```
        ∞ cube / sphere lattice = the matrix of information
                    │
                    ▼
        You stand at a CENTERPOINT inside one cell
                    │
         ┌──────────┼──────────┐
         │          │          │
      enter      turn       look
      next cell   90°        pages
         │          │          │
         ▼          ▼          ▼
   new center   new front   resonance-
   Mandell addr  face set    ranked data
```

- **Not** Minecraft from outside.  
- **Not** a top-down cone map.  
- **Yes** infinite addressable cells; Mandell is the shared language for place and move.

---

## 3. Practical visual design (target experience)

### 3.1 Room

| Element | Spec |
|---------|------|
| Volume | Inward-facing cube (or soft sphere dual) |
| Faces shown | Front, left, right, top, bottom |
| Hidden | Back (until you turn) |
| Structure | Grid lines · edge wire · shell number |
| You | Center ring marker “you are the centerpoint” |
| Empty face | Dim lattice + `void cube` + Mandell `15[Map] :: Cell@(h,v,f)` |
| Occupied face | Skin color · title · short detail · resonance · Mandell |

### 3.2 Motion

| Input | Meaning | Mandell |
|-------|---------|---------|
| W / enter next cube | Enter front cell | `19[Drive] :: step → 15[Map] :: Cell@…` |
| S | Enter back cell | same pattern |
| A / D | Turn 90° | `04[Transform] :: turn` |
| R / F | Up / down cell | F-axis Drive |
| Click face | Enter that neighbor | Drive to coord |

### 3.3 Information

| Channel | Role |
|---------|------|
| **Here pages** | What is bound to *this* center (detail + goals) |
| **Looking ahead** | Resonance-ranked data in look half-space |
| **Forces** | Which nature forces currently reach this cell |
| **Mandell HUD** | Always show address of current cell |

### 3.4 Dual lattice

- **Cube form:** orthogonal 6-neighbor cells (Minecraft blocks).  
- **Sphere form:** same centers; radial + ring reading (softer face geometry).  
- Toggle is a perception change, not a second world.

---

## 4. Mandell as communication bridge

Every centerpoint has a pure Mandell name:

```text
15[Map] :: CubeCell@(3,-1,0)
15[Map] :: SphereCell@(0,2,1)
19[Drive] :: step → 15[Map] :: CubeCell@(0,1,0)
09[Show] :: look@N/level
```

English is optional surface. Live steps already emit Mandell on the reply line.

---

## 5. Implementation map (now)

| Piece | File |
|-------|------|
| Cell walk + resonance + faces | `form/dell_matrix/first_person.py` |
| Live 3D room UI | `form/dell_matrix/live_visual.py` `_LIVE_HTML` |
| Program API | `fp_move` · `fp_turn` · `fp_look` · `fp_goto` · `first_person` |
| Mandell phrases | `form/mandell/phrases.py` fp_* |
| DEV data | `form/state/program_Operator.json` |

---

## 6. Next polish loop (practical order)

1. **Motion juice** — 200ms cell transition (scale/opacity).  
2. **Void craft** — shell rings painted on empty faces.  
3. **Ghost neighbors** — faint labels for high-resonance ideas 2+ cells ahead.  
4. **Mandell whisper** — small green address always on compass + face footer.  
5. **Tutorial strip** — first visit: “You are inside a cell. W enters the face you see.”  

---

## 7. Success criteria

A new operator can:

1. Open `live` and immediately see a **cube interior** (faces + lines).  
2. Press **W** and **enter another cube** with a new Mandell address.  
3. Turn and understand that **behind was not drawn** until they face it.  
4. See **data pages** when a cell holds ideas; void when empty — both still real cells.  
5. Switch **cube/sphere** and feel dual lattice without losing place.  
6. Trust that **Mandell** names where they are and where they step.

---

## 8. Law

Floor locked · Nursery still for growth · live localhost only · Voynich/geometry remain structural honesty.

---

## 9. Rebuild log (A+ Matrix Walk)

### What changed
- **New UI** from scratch: perspective room (floor/ceiling vanishing grids, left/right walls, far wall = next cube)
- **No broken CSS cube shadow** — readable first-person corridor cell
- **Animated step/turn** classes on world
- **Minimap** local lattice + you + facing
- **Capability dock**: grow, nursery, pulse, evolve, forces, personas, BIMO, verita, voynich, geometry, audit, matrices, save
- **Page reader modal** for full idea detail/goals
- **Mandell** on footer + faces
- **YOU** center marker + crosshair
- **Cube / sphere / flower** form themes

### Evolution loop
```bash
python -m form.dell_matrix.visual_evolve_loop --cycles 150
# GRADE A+ · final=100% · all checks PASS
```

### Open
```text
http://127.0.0.1:8765/
# hard refresh: Ctrl+Shift+R
```
