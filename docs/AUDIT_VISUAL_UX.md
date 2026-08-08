# DellMatrix — Full Visual / Movement / Perception / UX Audit

**Date:** 2026-08-06  
**Scope:** Visual, movement, looking, what is seen, menus, pages, perceptions, workshops — for **all entities**  
**Goal frame:** Upgrade the matrix to be **intuitive, powerful, and user-friendly**  
**Runtime authority:** `form/` only · `src/` + `preform/` = LEGACY frozen  
**Laws:** Floor lock · Nursery → confirm · offline core · snapshot remains default · live is opt-in

---

## 0. Executive verdict

**Updated:** 2026-08-06 · Phases A–E + visual/movement audit pass · `form.smoke_all` **22/22 PASS · SUS: READY**

| Surface | Grade | One-line |
|---------|-------|----------|
| Offline snapshot visual (`visual`) | **A+** | Size-by-score · words glyph · posture marks · cones · Live CTA |
| Live two-way visual (`live`) | **A+** | Iso-facing · shell rings both proj · preferred ★ · entities panel |
| Terminal / REPL render | **A+** | look · entities · zoom/page · AI · mode · workshops |
| Avatar movement (body FSM) | **A+** | Walk/jog/run/backstep/strafe · sit-stands · trail de-dupe |
| Directional vision (what is seen) | **A+** | Cone polygons · persona stars · entity counts on look |
| Lattice perception forms | **A+** | Forms + duals · shell rings (all forms) · FoL centers |
| Plane pages / zoom | **A+** | `zoom` / `page` / `unzoom` · focus gold ring on live |
| Menus / actions | **A+** | Single `actions_registry` · movement + entities |
| Workshops / view-rooms | **A+** | form/ matrix · perspective · mandel workshops live+REPL |
| Entity visual identity (all types) | **A+** | `all_entities()` · auto-spread place · skins · YOU/AI/ghosts |
| Doc alignment (live status) | **A+** | LIVE_VISUAL keys + entity inventory aligned |
| Intuitive / powerful / friendly | **A+ overall** | No idle trail bugs · strafe · iso-correct facing |

**Bottom line:** Full visual/movement/entity audit pass fixed idle trail pollution, iso facing/labels, preferred-star rendering, sit-while-walk, and enhanced entity inventory + movement suite.

### Audit pass fixes (2026-08-06 late)

| Bug / gap | Fix |
|-----------|-----|
| User trail grew on every `/state` poll | Trail only on real position change; removed poll push |
| AI wander speed = refresh rate | Tick throttled (~0.95s) |
| Iso facing arrows used 2D angles | Facing projected through iso map |
| Empty iso label text nodes | Labels always drawn; words skin glyph added |
| Preferred persona star never shown | ★ in vision list + gold dash ring on map |
| Shell rings 2D-only | Iso shell polygons drawn too |
| `step()` while sitting stayed sitting | Movement auto-stands |
| Ideas stacked at (0,0) | Auto-spread spiral placement |
| No entity inventory | `all_entities()` · `entities` cmd · live panel |
| Movement incomplete | `backstep` · `strafe` · `jog` · Shift+A/D |

---

## 1. Stack map (what actually runs)

```
USER DOOR
  launch.py → form/repl.py → form/open.py (Program)
       │
       ├─ visual     → form/dell_matrix/visual.py      (offline HTML snapshot)
       ├─ live       → form/dell_matrix/live_visual.py (127.0.0.1 two-way)
       ├─ render()   → plane ASCII + avatar line
       ├─ avatar     → form/avatar/{body,face,kaomoji}.py
       ├─ lattice    → form/dell_matrix/harmonic_lattice.py + perception.py
       └─ nursery    → proposals list (text + panels)

LEGACY (do not treat as current UX source of truth)
  src/visual/*          dashboard, ascii_bodies, cube_renderer
  src/snapins/workshops.js, view_rooms.js
  preform/ pages, GODWORKSPACE_UI, glyph layer
```

| Layer | File(s) | Role |
|-------|---------|------|
| Snapshot panel | `form/dell_matrix/visual.py` (~427 lines) | Offline HTML · ACTIONS menu · SVG nodes · nursery · avatar text |
| Live panel | `form/dell_matrix/live_visual.py` (~715 lines) | HTTP bridge · state · cmd · iso/2D · vision · AI |
| Terminal flow | `form/dell_matrix/visual_terminal.py` | OpBox / Rule90 seed show (optional) |
| Graph contract | `form/dell_matrix/graph_view.py` | Nodes/edges for SVG |
| Plane / pages | `form/dell_matrix/plane.py` | Units, skins, perspective, zoom page detail |
| Perception | `form/dell_matrix/perception.py` | Form metrics + flower centers |
| Decision look | `form/dell_matrix/decision_shells.py` | FlowShell look/move (language layer, not avatar) |
| Avatar | `form/avatar/*` | Body · face · kaomoji |
| REPL menus | `form/repl.py` HELP_SHORT / HELP_MORE | Text command map |
| LEGACY workshops | `src/snapins/workshops.js` | Matrix/persona/perspective/BIMO/psalms/mandel |
| LEGACY rooms | `src/snapins/view_rooms.js` | Growth/water/force/network/personal/shared/psalms |

---

## 2. Entities inventory — how each looks / moves / is seen

### 2.1 Idea units (live plane)

| Aspect | Current | Gap |
|--------|---------|-----|
| Data | `Unit`: id, label, words, detail, goals, skin, x/y, sandboxed | No facing, no posture, no “eye” |
| Skins | cube · sphere · seed · flower · building · words · circle · core | Good taxonomy |
| Snapshot SVG | Rect vs circle by skin; 8 colors; score text; click → detail | No size-by-score; no detail/goals on shape; avatar absent |
| Live SVG 2D | Same rect/circle; white stroke if in user vision | Click fills confirm-id (not inspect) |
| Live SVG Iso | **All ideas as boxes** (painter’s order); z = shell + score | Skin identity mostly lost in iso |
| Seen by vision | In cone if within range 5.5 and ±55° of facing | Words truncated 60 chars; max 12 listed |
| Act on seen | Live: Confirm button per seen node | No “inspect / zoom page / note” first-class |

### 2.2 Nursery proposals (not live until confirm)

| Aspect | Current | Gap |
|--------|---------|-----|
| Snapshot | Ranked list right column · copy `confirm <id>` | Not on SVG |
| Live | Confirm / Reject buttons | No spatial ghost placement preview |
| Visual metaphor | Text affinity | Should feel “quarantine / unborn” (ghost, dashed, nursery zone) |

### 2.3 User avatar

| Aspect | Current | Gap |
|--------|---------|-----|
| Body | 8-way facing, pos, posture, locomotion, reach, holding | Strong FSM |
| Face | Expression enum + kaomoji packs | Terminal/HTML string only |
| Snapshot | **Text only** in side card — **not on matrix SVG** | Major UX hole |
| Live | Circle marker YOU + facing line + trail | No stick figure / posture / expression glyph |
| Movement | walk / turn / sit / stand / jump / bend · live WASD | No run/jog hotkeys; no strafe |
| Look | `look` refreshes vision payload | Does not “cast” a visible cone on canvas |

### 2.4 AI companion

| Aspect | Current | Gap |
|--------|---------|-----|
| State | Module-global `_AI` in `live_visual.py` | Not on Program; not in save/load v7 |
| Modes | manual · wander · follow | Good |
| Live visual | Pink marker + trail + facing | Same as user: minimal body |
| Snapshot | **Absent** | — |
| Persist | **Not saved** | Session-only ephemeral |

### 2.5 Personas (Manny, Melody, Aetheris, Mathelody, The_Ancient)

| Aspect | Current | Gap |
|--------|---------|-----|
| Registry | `AGENTS.md` · personas-pack LEGACY | Not entities on plane |
| Visual | LEGACY `persona_roster.js` | Zero presence in `form/` visual/live |
| Looking | N/A | Future: persona lens = filter “what is seen” |

### 2.6 Lattice cells / shells / chords

| Aspect | Current | Gap |
|--------|---------|-----|
| Data | H/V/F cells, shell metric by form | Strong |
| REPL | `lattice` · `chord` · `shell` · form toggles | Text-only |
| Visual | Form label in meta; no shell rings drawn | Rings / FoL centers not painted on SVG |

### 2.7 Graph edges (enhance / vesica / sandbox)

| Aspect | Current | Gap |
|--------|---------|-----|
| Snapshot | Lines with color + dash for sandbox | Live panel does not draw edges |

### 2.8 Decision / FlowShell “look”

| Aspect | Current | Gap |
|--------|---------|-----|
| API | `look()` / `move()` / `multi_look()` in decision_shells | Not wired to avatar vision or UI |
| Role | Abstract language/direction shells | Name collision with avatar `look` |

---

## 3. Visual systems deep dive

### 3.1 Snapshot (`visual` → `write_visual`)

**Layout:** 3 columns — Actions | Matrix SVG | Avatar + Nursery  

**Menus (ACTIONS groups):**

| Group | Items |
|-------|--------|
| Start | Tutorial, Help |
| Ideas | Create, Grow, Proposals, Rank, Show matrix |
| Nursery | Confirm, Reject, Confirm all, Reject all |
| Lattice | Cube, Sphere, Core, Flower, Lattice |
| Avatar | Walk, Turn L/R, Sit, Stand, Smile, How do I look |
| System | Enhance ON/OFF, Pulse, Save, Status |

**Strengths**
- Clear grouping and hints  
- Empty state with create prompt  
- Offline, no network  
- Node select → detail panel  
- Smoke tests exist  

**Friction**
1. **Copy-paste loop** — buttons never execute (by design); newcomers feel the panel is “broken”  
2. **No live agents on SVG** — matrix is ideas-only  
3. **No Live entry** in ACTIONS (must type `live` in REPL)  
4. **No Look / vision** group  
5. **No workshop / page / zoom**  
6. Meta still says “Live matrix” for a **snapshot** (wording lies)

### 3.2 Live (`live` → localhost:8765)

**Layout:** Actions + WASD + AI | Matrix (iso/2D) + dual vision lists | Nursery + positions  

**Strengths**
- True two-way: `/state` + `/cmd`  
- User + AI + trails + facing  
- Vision pattern (count, skins, nearest, proximity)  
- Act on seen (confirm)  
- Iso z from radial shell + score  
- Auto-refresh ~1.8s  
- Nursery confirm/reject live  

**Gaps / bugs vs docs**

| Claim (`docs/LIVE_VISUAL.md`) | Reality |
|------------------------------|---------|
| Vision cones drawn on SVG | **Cone computed**, nodes highlighted, **no cone polygon drawn** |
| Facing arrows | Yes (line from marker) |
| Movement trails | Yes |
| Keys E = ai follow | **E not bound** in live HTML (only W/A/D/Q + I/2) |
| Patterns | Yes in side lists |

**Other live gaps**
- Dead code stub `drawIsoBox` unused  
- AI state global, multi-session unsafe  
- Edge graph not drawn  
- Iso collapses skin variety to boxes  
- Confirm on node click is aggressive (no inspect mode)  
- No posture/expression on markers  
- No lattice shell rings / flower centers  
- Mobile layout stacks poorly (acceptable for v1)

### 3.3 Terminal

| Surface | Quality |
|---------|---------|
| `Program.render()` | Good session box |
| `Plane.render()` zoom page | Excellent detail page when zoom set — **no REPL command** |
| `visual_terminal` OpBoxes | Fun optional; not in help |
| Lattice `render_ascii` | Exists |
| LEGACY ascii_bodies / dashboard | Richer bodies — **not imported** |

---

## 4. Movement audit

### 4.1 What works

```
Body: face · step · turn L/R · posture sit/stand/bend/jump
Loco: idle · walk · jog · run (API; jog/run barely exposed in REPL)
Live: W walk · A/D turn · Q look
AI: walk · turn · face · goto · follow · wander · manual
```

### 4.2 What is weak for “intuitive + powerful”

| Issue | Detail |
|-------|--------|
| No spatial feedback in snapshot | Walk changes numbers; map doesn’t show YOU |
| No collision / bounds | Infinite plane; easy to walk off “view” |
| Camera not following user | Live map is fixed world scale; far walk shrinks to edge |
| Run not in menus | Locomotion RUN exists; no button / key |
| Diagonal walk | Facing allows NE etc.; step uses facing delta; no “strafe” |
| AI not first-class entity | Cannot save companion; cannot multi-AI |
| Movement ≠ lattice cells | Avatar pos is free int grid; ideas float floats — slight dual space |

### 4.3 Looking vs moving (law)

- **Avatar look:** observation, no move — good  
- **FlowShell look:** abstract decision layer — parallel, unconnected  
- **Lattice perception:** changes metric reading of same coords — orthogonal and correct  
- **Plane perspective:** table/page/cube/… — third lens, weakly exposed  

Three “looking” systems exist; users only discover one (`look` + form names).

---

## 5. Perception / “what is seen”

### 5.1 Directional vision (live)

```
range ≈ 5.5
half-angle 55°
outputs: nodes[], in_view_ids, pattern, sees_other, proximity
```

**Good:** distance sort, skin histogram, nearest, other agent visibility  
**Missing:** occlusion, height/z in cone test (z ignored for inclusion), memory of last-seen, “focus target”, multi-ring attention

### 5.2 Lattice forms (shared law — keep)

| Form | Distance sense | Skin name |
|------|----------------|-----------|
| cube | max-norm shells | cube |
| sphere | Euclidean 3D | sphere |
| core | radial | seed |
| flower | radial + FoL centers | flower |
| square/circle | plane duals | square/circle |

**Visual gap:** form change rarely changes **drawing grammar** (only meta string + snapshot skin fallback). Power users change metric; casual users don’t *see* cube vs sphere.

### 5.3 Plane perspective / pages

`Perspective`: table · page · cube · circle · flower · sphere  
`zoom_target` → **PAGE / CELL** full detail in `plane.render()`  

**REPL:** no `page`, `zoom`, `open`, or `focus` command found.  
**Visual:** no page mode.  
**Verdict:** page system is half-built data + strong text renderer with no door.

### 5.4 LEGACY view rooms

growth · water · force · network · personal · shared · ancient_psalms  

**Status:** snap-in API only; zero form/ wiring. Valuable design seed for upgrade.

---

## 6. Menus, pages, workshops

### 6.1 Menu surfaces (fragmented)

| Surface | Kind | Executes? |
|---------|------|-----------|
| REPL HELP_SHORT / HELP_MORE | text | yes |
| Snapshot ACTIONS | buttons → copy | no |
| Live data-cmd buttons | subset | yes |
| Live free cmd input | full | yes |
| Tutorial path | guided | yes |
| GodWorkSpace (preform) | spec | frozen |
| Workshops (src) | registry | frozen |

**UX problem:** three different action inventories. Live lacks Create-with-name wizard, full Avatar expressions, polyglot, LatinMandell, page/zoom. Snapshot lacks Live, Look, AI, iso.

### 6.2 Workshops (desired vs actual)

| Workshop (LEGACY) | canEdit | form/ status |
|-------------------|---------|--------------|
| Matrix | center, zoom, shells, sphere/flower | Lattice cmds partial; no workshop UI |
| Persona | directives, abilities, emoji | Not live |
| Perspective | lens rules, filters | Perception exists; no lens editor |
| BIMO | fusion slots | Not live |
| Psalms | content/theme | Not live |
| Mandel | commands/syntax | REPL + registry only |

### 6.3 Pages

| Page concept | Where | UX door |
|--------------|-------|---------|
| Idea cell page (zoom) | `plane.render` when zoom_target | **None in REPL/UI** |
| preform/pages 01–25 | docs only | LEGACY |
| GodWorkSpace panels | spec | LEGACY |
| Selected idea detail | snapshot HTML | Click node (snapshot only) |

---

## 7. Consistency & doc drift

| Issue | Severity |
|-------|----------|
| `docs/START_HERE.md` still: “Live real-time visual is the target — not now” | High — confuses upgrade baseline |
| `docs/USER_READY.md` / older audits: live as Horizon | Medium — partially obsolete |
| `docs/LIVE_VISUAL.md` mostly accurate; cone drawing overstated | Medium |
| Snapshot header “Live matrix” for offline snapshot | Low–Med |
| Dual “look” (avatar vs FlowShell) undocumented for users | Low |
| AI companion outside persist | Medium for “all entities” |

---

## 8. UX principles scorecard (target: intuitive · powerful · friendly)

| Principle | Score | Notes |
|-----------|-------|-------|
| **Discoverability** | 4/10 | Power buried in `help more` / live keys |
| **Feedback** | 5/10 | Live good; snapshot weak; look invisible |
| **Consistency** | 4/10 | Three menus; two visuals; LEGACY lore |
| **Entity clarity** | 4/10 | Skins ok; bodies/personas thin |
| **Spatial intuition** | 6/10 | Iso + trails help; no follow-cam / shells |
| **Safety of growth** | 9/10 | Nursery law excellent |
| **Power depth** | 8/10 | Lattice, duals, vision, AI modes, polyglot |
| **Friendliness** | 6/10 | Tutorial + acceptance strong; then cliff |
| **Accessibility** | 5/10 | Keyboard live ok; contrast ok; no screen-reader labels |
| **Offline integrity** | 9/10 | Snapshot + core loop solid |

---

## 9. Upgrade roadmap (recommended)

Ordered for **intuitive · powerful · friendly** without breaking Floor/Nursery law.

### Phase A — Unify & honesty (fast wins)

1. Fix docs: START_HERE / USER_READY / FULL_AUDIT claim **live opt-in exists**  
2. Snapshot meta: rename “Live matrix” → “Matrix snapshot”  
3. Add **Live** button + URL hint to snapshot ACTIONS  
4. Draw **vision cone** polygons on live SVG (user + AI)  
5. Bind missing keys: `E` follow, `S` optional backstep or look-down; document I/2  

### Phase B — All entities on stage

6. Snapshot SVG: draw **YOU** (+ optional last AI if present) with facing  
7. Live markers: skin-aware mini glyphs / posture hint / face kaomoji label  
8. Iso: preserve **skin silhouettes** (sphere top vs cube vs seed gem)  
9. Nursery: ghost nodes (dashed, low opacity) optional toggle  
10. Graph edges on live (sandbox dash, vesica, enhance)  
11. First-class **AICompanion** on Program + persist v7 field  

### Phase C — Looking & pages

12. REPL: `zoom <id|label>` · `page` · `unzoom` · `look` prints seen list even offline  
13. Snapshot/live: **Inspect mode** vs Confirm mode for node click  
14. Idea page card: detail, goals, neighbors, skin, shell, words  
15. Draw shell rings / FoL centers when form is core/flower  
16. Form change animates or recolors ground grid grammar  

### Phase D — Menus & workshops (form/ only)

17. Single **action registry** (JSON/py) shared by snapshot, live, help  
18. Workshop panel v0 (live side or tab): Matrix · Perspective · Mandel only first  
19. Persona lens as **filter on what is seen** (not full BIMO yet)  
20. Progressive disclosure: Beginner / Builder / Depth modes  

### Phase E — Movement feel

21. Camera follow user (pan SVG transform)  
22. Soft view bounds + “recenter” button  
23. Run key; sit/stand icons; trail fade by age  
24. Optional grid snap when lattice form = cube  

### Phase F — LEGACY harvest (read-only borrow)

25. Port ideas from `ascii_bodies.js`, `view_rooms.js`, `workshops.js`, glyph taxonomy — **reimplement in form/**, never import frozen tree into acceptance path  

---

## 10. “Definition of done” for the visual upgrade

A session is upgrade-complete when an average operator can:

1. Open `tutorial` then `live` without reading code  
2. **See themselves** on the map, walk, turn, and **see a vision cone**  
3. **See** which ideas are in view vs out of view  
4. Switch cube/sphere/core/flower and **see** the reading change  
5. Open an idea **page** (detail) without leaving the matrix metaphor  
6. Confirm nursery from panel without memorizing ids  
7. Use one coherent menu language across snapshot and live  
8. Optionally work with AI companion that **saves** with the session  
9. Never bypass Nursery or Floor  

---

## 11. File priority for implementers

| Priority | File | Why |
|----------|------|-----|
| P0 | `form/dell_matrix/live_visual.py` | Cone draw, entity craft, keys, edges |
| P0 | `form/dell_matrix/visual.py` | Snapshot agents, Live CTA, wording, shared ACTIONS |
| P1 | `form/repl.py` | zoom/page/look offline; help; live keys doc |
| P1 | `form/open.py` | companion entity; avatar_status richness |
| P1 | `form/persist.py` | save AI + zoom + vision prefs |
| P2 | `form/dell_matrix/plane.py` | page API polish |
| P2 | `form/dell_matrix/perception.py` | helpers for ring/flower draw data |
| P2 | New `form/dell_matrix/actions_registry.py` | single menu source |
| P3 | Docs LIVE_VISUAL, START_HERE, USER_READY | honesty |
| — | `src/*`, `preform/*` | reference only |

---

## 12. Risk & law guardrails

| Risk | Guard |
|------|-------|
| Live becomes required for acceptance | Keep snapshot default; acceptance path unchanged unless product decision |
| AI companion network creep | Stay 127.0.0.1; no remote agents in core |
| Workshop scope explosion | Matrix + Perspective + Mandel first |
| Iso complexity | Keep pure JS, zero deps |
| LEGACY import accident | Core scope lock in `form/CORE_SCOPE.md` |

---

## 13. Summary for operators

**Shipped (A–E):** offline snapshot + opt-in live iso, **drawn vision cones**, shared action registry (beginner/builder/depth), YOU+AI on both maps, skin-aware iso silhouettes, nursery ghosts, graph edges on live, **AICompanion on Program + save/load**, `look` / `zoom` / `page` / `unzoom`, inspect vs confirm click, shell rings + FoL centers, form-themed grid, camera follow + recenter, run/backstep, grid snap, workshops (matrix/perspective/mandel), persona + skin lenses, docs honesty.

**Try:**

```text
python launch.py
tutorial
look
live
# WASD · Q look · E follow · R run · C recenter
workshop matrix
mode depth
zoom <id>
save
```

---

Authority: `form/CORE_SCOPE.md` · `docs/LIVE_VISUAL.md` · `docs/USER_READY.md` · this audit.
