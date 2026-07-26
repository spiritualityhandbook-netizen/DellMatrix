# Phase 3 Preform — Poetry / Scansion → Mandell (PART 1)

Status: **PREFORM**  
Source: Scansion + Iamb notes (Architect “Incorporating poetry into Mandell”).

Not literary homework. **Rhythm as structure** for seeds, Flow, Temp, and glyphs.

---

## 1. Core mapping (calculation)

| Poetry concept | Mandell map |
|----------------|-------------|
| **Syllable** | Smallest spoken token in a seed line |
| **Stress / ictus** | Strong position — maps to emphasis in Flow or Temp Hot bead |
| **Unstressed / nonictus** | Weak position — default Cold/carrier |
| **Foot** | Mini-cell: fixed weak/strong pattern (like a tiny Mandellacell) |
| **Meter** | Repeated foot pattern across a line (Cycle 06) |
| **Scansion** | **18 Mirror** + **12 Test** on a line: mark strong/weak; check against claimed meter |
| **Rhythm vs meter** | Rhythm = actual performance stress; Meter = ideal lattice of positions — same dual as dual-lattice (lived vs address) |

---

## 2. Notation candidates (Visual Glyph Layer)

Prefer typeable, offline-safe:

| Level | Symbols | Use |
|-------|---------|-----|
| 2-level | `/` strong · `x` or `×` weak | Default scansion line under a seed |
| 3-level | `/` · `\` demoted stress · `x` | When one stress is weaker than neighbor |
| 4-level | `1 2 3 4` or `. · : │` density | Fine grain; optional, don’t require for core |

**Example under a seed line:**
```
08[Create]>>09[Show]
x  /   x    /     x   /
```
Scansion is **annotation**, not required syntax for every seed.

---

## 3. Feet as pattern library (optional variants later)

| Foot | Pattern | Rough feel |
|------|---------|------------|
| Iamb | x / | rise (da-DUM) |
| Trochee | / x | fall (DUM-da) |
| Spondee | / / | double hit |
| Pyrrhic | x x | double light |
| Anapest | x x / | double rise |
| Dactyl | / x x | fall then light |

**Mandell use:** teach seed “music”; optional **05 Tone** coupling; not new Dells until Architect assigns.

---

## 4. Line measures (teaching only)

Dimeter → heptameter = count of feet per line.  
Useful for **06 Cycle** examples and GodWorkSpace “rhythm trainer” panel later — not OS law.

---

## 5. What to build in code phases (later)

| Feature | Phase hint |
|---------|------------|
| Optional scansion row under seed in GodWorkSpace | Code UI |
| Stress mark tokens in lexer (ignore if absent) | Code Phase lexer |
| `12[Test]` meter check helper | Runtime optional |
| RhymePattern Dellaman (already noted elsewhere) | Soft law: sound can reinforce Bind |

---

## 6. Explicit rejects
- Scansion systems as mandatory for every Mandell cell
- Classical long/short as physical lattice axes
- Musical-note scansion as required runtime
- Wikipedia bibliography as True registry content

---

## 7. One-line law for PART 1
**Seeds may carry rhythm; scansion makes strong/weak positions visible; meter is the ideal grid, rhythm is the lived stress — dual-lattice in language form.**
