# Lattice Architecture — Preform

Status: **PREFORM** (from bare-bones matrix + game-structure pastes)

## Floor reminder
Alpha · Delta · Omega · Omni on floor · Nova = Cheat only

---

## 1. Size calculation (practical)

| Size | Pros | Cons |
|------|------|------|
| **15³** | Familiar from older Harmonic Cube talk | Does not divide cleanly by 2 → messy fractal subdivision |
| **12³** | Musical 12-tone friendly, highly composite | Still not pure power-of-2 for octrees |
| **16³ (recommended baseline cell)** | Power of 2 · clean octree split 16→8→4→2→1 · computer-friendly | Slightly less “12-note native” |
| **32³** | Same fractal cleanliness, larger zones | Heavier memory if dense |

**Preform default for coding:** prefer **16×16×16 cell** as zone size when implementing dual lattice / snap-in blocks. Keep 12/15 as **harmonic overlay** options, not mandatory grid edge counts.

---

## 2. Dual lattice + snap (kept)

- **Sphere / Flower** = resonance / contact / growth shells (visual + relation)
- **Cube** = address / room / perspective preset
- **Snap-in:** 2D lattice latches on shared H or V line → cross-product opens 3D volume (Dynamic Mesh Latching concept)
- Negative space between contacts = force / Water channels (already in Flower directives)

---

## 3. ECS mapping (candidate for Phase 2)

| Game ECS | Mandell map |
|----------|-------------|
| Entity | Node / blank address in lattice |
| Component | Manor bags (data only) |
| System | Operators that scan components (Bind, Test, Decay, Pulse…) |
| Game loop | Optional runtime teaching: Input → Update → Render (not True law) |

Useful for code modularity; does not replace Dell numbers.

---

## 4. Harmonic overlay (optional, not floor)

- Tonnetz-style axes (fifths / thirds) = **view filter**, not required storage physics
- Same lattice can switch: Harmonic view · Conceptual view · Top-down flatten
- Chord = multi-node select by relation, not mandatory file path

Park as Perspective Matrix technique until Architect confirms coding priority.

---

## 5. Folders / memory truth

RAM is flat. Folders / entities / OpBoxes are **human and Mandell address overlays**. Aligns with lattice coordinates + UI projection.

---

## 6. Rejected as program law

- Universe-is-game-loop / Planck tick as mandatory metaphysics
- Mega Man / AGILOX lore as architecture
- Harmonic matrix as only allowed storage model
- 15³ as “absolute ideal” without power-of-2 note
