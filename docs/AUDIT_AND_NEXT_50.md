# DellMatrix / Mandell — Full Audit + Next 50 Directives

Date: 2026-08-01  
Scope: `form/` runtime on GitHub main

---

## 1. Full audit

### 1.1 What is solid

| Area | Status | Notes |
|------|--------|-------|
| **Form as front door** | Strong | `open.py` + `repl.py` + launchers |
| **Floor lock** | Strong | Alpha·Delta·Omega·Omni immutable |
| **Dell registry 00–50** | Strong | Named manors present |
| **English → intent** | Good | Phrases dictionary + fallbacks |
| **Seed parse** | Good | `08[Create] > 15[Map] :: x` |
| **Seed executor** | Partial–Good | Many Dells wired; some thin |
| **Session save/load v6** | Strong | Matrix + avatar + nursery |
| **Nursery quarantine** | Strong | Growth cannot auto-pollute live |
| **Ringed growth** | Good | Gates + FOG cut + lineage |
| **Avatar body/face** | Good | Walk/turn/sit/express |
| **Visual HTML panel** | Good | Buttons + graph + easy path |
| **H/V/F lattice** | New/Good | Tonnetz + sparse cells |
| **Perception duals** | New/Good | cube/sphere, square/circle, core, flower |
| **Patterns teach layer** | Good | loop/grow/lattice/flower/… |
| **Polyglot stub** | Early | ES/FR small maps only |
| **Mandell Origin law** | Strong | Documented priority |

### 1.2 What is weak or fragmented

1. **Two planes not unified** — `plane.py` idea graph vs `harmonic_lattice.py` H/V/F not one object in Program.  
2. **Perception not in REPL/UI** — forms exist in code; user cannot say `sphere mode` yet.  
3. **Lattice not in save/load** — session misses harmonic lattice state.  
4. **Visual ignores lattice/perception** — UI still only idea graph.  
5. **Duplicate growth paths** — `growth_engine.py`, `idea_grow.py`, `ringed_growth.py` overlap.  
6. **Executor gaps** — some Dells only place marker ideas.  
7. **Phrase coverage** — still regex-thin for free speech.  
8. **Polyglot** — tiny; not general.  
9. **Legacy `src/`** — still present; dual-era confusion risk.  
10. **Tests** — smoke functions exist; no single CI-grade suite always green.  
11. **Offline package** — Node not required (good), but no one-click “install deps” story if any added later.  
12. **Docs scatter** — many STATUS/SUS md files; one roadmap should lead.  

### 1.3 Goal alignment (honest)

| Goal | Progress |
|------|----------|
| Mandell as Origin / bridge language | **Foundation yes · worldwide no** |
| Man ↔ computer practical speech | **Usable for core actions** |
| Controlled powerful growth | **Yes (Nursery)** |
| Average-user visual | **Partial (command board, not live app)** |
| H/V/F creativity matrix | **Core math yes · daily UX no** |
| Cube/sphere/flower perception | **Code yes · wired no** |

### 1.4 Risk register

- Overclaim (Voynich decode, universe-as-game-loop) must stay metaphorical.  
- Feature sprawl without unification will slow the average user.  
- Unwired modules feel “done” in docs but invisible in REPL.  

---

## 2. Next 50 best directives

Ordered by leverage toward: **Mandell Origin · practical use · unified matrix · honest growth**.

### A. Unify the runtime (1–10)

1. **Bind HarmonicLattice into Program** as `program.lattice` (single session object).  
2. **Persist lattice + perception** in save/load v7.  
3. **Place ideas onto H/V/F cells** when created (optional auto-map).  
4. **One growth entrypoint** — keep RingedGrowth; deprecate or wrap duplicate grow modules.  
5. **REPL: `cube` / `sphere` / `core` / `flower` / `toggle form`**.  
6. **REPL: `lattice` show ASCII + status**.  
7. **REPL: `chord at H V`** pull neighborhood.  
8. **Visual: draw skin by perception** (circle vs square node shapes).  
9. **Visual: Flower mode overlay** optional layer.  
10. **Smoke_all includes lattice + perception + session v7**.  

### B. Mandell density (11–20)

11. **Executor: full table Dell→action** for every 00–50 with non-thin behavior or explicit “stub”.  
12. **Expand phrase dictionary** to 100 stable intents.  
13. **Always echo Mandell seed** after English actions (already partial — make universal).  
14. **Macro Dell 48** — record last N actions as reusable seed.  
15. **Distill Dell 38** — summarize idea words into shorter seed.  
16. **Rank Dell 46** — score nursery proposals for user.  
17. **Teach all patterns from REPL** already; add `teach all` dump.  
18. **Seed lint** — validate unknown Dell / bad flow before execute.  
19. **Bidirectional tests** EN→Mandell→EN for top 30 phrases.  
20. **Mandell cheat-sheet HTML** page generated offline next to UI.  

### C. Growth & Nursery quality (21–28)

21. **Confirm-all / reject-all** with safety prompt.  
22. **Proposal rank sort** by affinity before list.  
23. **Prevent duplicate proposals** (same label+parents).  
24. **Growth respects lattice shells** (optional: only same shell resonates harder).  
25. **Nursery in visual panel always refreshed on `visual`**.  
26. **Lineage tree print** for a confirmed idea.  
27. **Cap proposals per grow** configurable.  
28. **FOG dictionary expandable** from user “reject reason”.  

### D. Perception & lattice creativity (29–36)

29. **Official size policy**: default 12; fractal zones 16.  
30. **Snap module save/load** as files.  
31. **Latch second lattice from REPL**.  
32. **Core shell listing** `shell 0` `shell 1`.  
33. **Structural overlay command** (harmonic off).  
34. **ima command** = create seed at origin then manifest on lattice.  
35. **Shared-lattice doc** short user page (no mysticism).  
36. **Perception dual on visual button**.  

### E. Average-user product (37–44)

37. **`--load` default for launchers** after first save.  
38. **On `visual`, print only easy path** (already); open browser if possible optional flag.  
39. **Error messages never stack traces** in REPL.  
40. **`help` sections**: Mandell · Matrix · Avatar · Growth · Lattice.  
41. **First-run tutorial script** 10 steps.  
42. **Single `docs/START_HERE.md`** linking Origin + audit.  
43. **Mark legacy `src/` read-only** in README (done-ish; strengthen).  
44. **Remove or archive dead STATUS md noise** into `docs/archive/`.  

### F. Bridge / polyglot / honesty (45–50)

45. **Expand ES/FR maps to top 20 phrases each**.  
46. **`lang es|fr <text>` already**; add `lang list`.  
47. **Honesty gate in docs**: Voynich-inspired, not decoded.  
48. **Honesty gate**: reality-loop is metaphor, not physics claim.  
49. **Measure phrase hit-rate** on a fixed 50-sentence test set.  
50. **Next milestone definition**: “Cold start → create 3 ideas → grow → confirm 1 → sphere mode → save → load → visual” passes offline without AI.  

---

## 3. Recommended immediate sequence (do next)

1. Directive **1–3** (lattice in Program + persist + place)  
2. Directive **5–7** (REPL perception/lattice/chord)  
3. Directive **4** (one growth path)  
4. Directive **50** as acceptance test  

---

## 4. Non-goals (for now)

- Claiming global language adoption  
- Autonomous self-aware evolution  
- Full 4D tesseract UI  
- Replacing natural languages  
