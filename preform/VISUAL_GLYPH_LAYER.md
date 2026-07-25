# Visual Glyph Layer — Mandell (whole system)

Status: **PREFORM**  
Scope: GodWorkSpace **and** Mandell core visual language (not UI-only).

---

## 1. Outside-the-box ASCII / Unicode techniques (investigation)

### A. Structural techniques (still pure text)
| Technique | What it does | Mandell use |
|-----------|--------------|-------------|
| **Box-draw dual lattice** | `┌┬┐ ├┼┤ └┴┘ ─ │` as cube/sphere projection on square screen | Lattice rooms, shell rings |
| **Density gradients** | `.·:┊│║█` from sparse → solid | Fog intensity, Temp C→H |
| **Braille dots** | `⠁⠂⠃⠄…⣿` 2×4 bit grids | Micro-nodes, 8-bit state stamps |
| **Half-blocks** | `▀▄▌▐█` | Split shells, vesica edges |
| **Overstrike illusion** | Stack `=`, `-`, `_` in consecutive lines | Fake depth without graphics |
| **Diagonal flow** | `╱ ╲ ╳` + arrows | RuPat diagonals ↘↙↗↖ |
| **Corner anchors** | `⌜⌝⌞⌟ ⎾⏋⎿⏌` | OpBox corners, Guard frames |
| **Double-stroke** | `═ ║ ╔╗╚╝` | Alpha/Omni “sealed” frames |

### B. Innovative (still terminal-safe)
1. **Pulse columns** — one glyph column changes on each “tick” line (Age/Fade).
2. **Negative-space corridors** — empty cells between box walls = Water/force channels.
3. **Semantic monograms** — fixed 3×3 stamps for Dell IDs (readable at phone zoom).
4. **Orbit rings** — concentric `· ∘ ○ ◎ ●` for growth shells.
5. **Clash stamps** — `🆚` or `⚔️` only at conflict coords (sparse, high meaning).
6. **Layer sandwich** — Line1 structure · Line2 flow arrows · Line3 status markers (3 parallel tracks).
7. **Unicode block as “type”** — Box Drawing vs Arrows vs Geometric mean different Manor classes (notation law candidate).

### C. Phone / offline constraints
- Prefer **monospace-stable** sets (Box Drawing, Geometric Shapes, Arrows).
- Avoid rare plane-1 glyphs that tofu on cheap fonts.
- One emoji max per cell if emoji used (density law).
- GodWorkSpace: CSS `font-family: ui-monospace, monospace` + `white-space: pre`.

---

## 2. Unicode block semantics (for Notation)

| Block / set | Semantic role in Mandell |
|-------------|---------------------------|
| **Box Drawing** (U+2500) | Structure · rooms · lattice edges · sealed frames |
| **Arrows** (U+2190) | Flow · RuPat · direction of execution |
| **Geometric Shapes** | Nodes · centers · Temp beads · shell markers |
| **Misc Symbols** | Status · force · rare emphasis (sparse) |
| **Braille Patterns** | Dense micro-state / bitfields |
| **Block Elements** | Fill · fog · progress bars |
| **Math operators** | Orbit / Verita / formula stamps |
| **Emoji** (optional) | Wake / clash / pulse — never required for core |

**Rule candidate:** Structure glyphs ≠ Flow glyphs ≠ Marker glyphs. Mixing types in one cell needs explicit `:` FlowBy.

---

## 3. Sorted taxonomy (from supplied glyph paste + standard set)

### FLOW (direction / RuPat)
```
→ ← ↑ ↓ ↔ ↕ ↖ ↗ ↘ ↙
⇢ ⇠ ⇡ ⇣ ⇒ ⇐ ⇑ ⇓ ⇔ ⇕
↪ ↠ ↣ ⟶ ⟵ ⟷ » « › ‹
╱ ╲ ╳
```
Use: sequence, diagonal RuPat, major jump (pair with `>` `>>` `>>>`).

### STRUCTURE (boxes / lattice / rooms)
```
─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼
═ ║ ╔ ╗ ╚ ╝ ╠ ╣ ╦ ╩ ╬
╭ ╮ ╯ ╰ ┊ ┋ ┆ ┇
⌜ ⌝ ⌞ ⌟ ⎾ ⏋ ⎿ ⏌
⌂ ⌁ ⌧ ⌫
```
Use: OpBox, cube projection, Guard frame, sealed Alpha frames.

### MARKERS (nodes / status / emphasis)
```
· ∘ ○ ◎ ● □ ■ ▢ ▤ ▥
★ ☆ ✦ ✧ ✴ ✵ ✶ ✷ ✸ ✹ ✺
◆ ◇ ▲ ▼ ▶ ◀ △ ▽
⚓ ⚖ ⚛ ⚑ ⚐ ☀ ☼ ☽ ☾
♠ ♣ ♥ ♦ ⚀⚁⚂⚃⚄⚅
```
Use: center choice, growth stage, Temp bead, rare status (sparse).

### FILL / FOG / DENSITY
```
. · : ┊ │ ║ █ ▓ ▒ ░ ▀ ▄ ▌ ▐
⠁ ⠂ ⠃ ⠄ ⣿ (braille scale)
```
Use: Fog levels, Age/Fade pulse, progress.

### CONTROL / TECH (optional UI chrome)
```
⌘ ⌥ ⌃ ⌤ ⎋ ⏎ ⌫ ⌦
⌚ ⌛ ⌨ ⛽
```
Use: GodWorkSpace chrome only — not core lattice law.

### DECO / ZODIAC / MISC (reference, not default law)
Zodiac, card suits extras, rare alchemical — **REFERENCE_DUMP** unless Architect assigns Manor.

---

## 4. Incorporation map (Mandell whole)

| Layer | How glyphs plug in |
|-------|---------------------|
| **Dual Lattice** | Structure = edges; Flow = RuPat; Markers = nodes/centers |
| **Flower shells** | Orbit rings `·∘○◎●`; negative space = force channels |
| **Temp** | Density gradient or C/W/H marker colors in UI |
| **Fade / Age** | Pulse column + density drop over ticks |
| **GodWorkSpace** | Monospace panels; tabs paint Structure/Flow/Marker legends |
| **Notation (4-N)** | Glyph class is part of Notation audit |
| **True Mandel** | New glyph→Manor only after number confirm |

---

## 5. Next code-facing (Phase 2 later)
- `src/visual/glyph_taxonomy.json` — class lists above
- GodWorkSpace legend panel
- Optional ASCII lattice renderer using Structure+Flow only
