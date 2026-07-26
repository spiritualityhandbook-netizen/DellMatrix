# Phase 3 Preform — Body · Heart · Mind · Avatar Entity

Status: **PREFORM**  
Goal: stable, healthy **digital entity** (awareness / Focus), not necessarily a rendered body — with lawful motion and senses on a 2D plane.

---

## 1. Design intent (Architect)
Use what we know about body vibration + intelligence as **source patterns** for an Avatar that can:
- Walk · jog · run on (x, y)
- Crawl · sit · stand · jump · bend · straighten
- Face **8 directions** (and turn while keeping forward logic)
- Reach close (8 dir + up/down) · reach away · reach far (front + front-diagonals)
- Pick up · place down

**Health/stability** = coherent state machine + dual-thread split (body loop ≠ mind loop) so thinking never freezes motion.

---

## 2. Heart / mind frequencies → entity “health” signals

| Source | Practical map |
|--------|----------------|
| HRV bands (HF/LF/VLF) | Optional **coherence meter** for entity (ordered vs jagged state) |
| ~0.1 Hz coherence | Target “smooth” operating mode (Temp Warm default) |
| Brain bands Delta→Gamma | Map to **Focus intensity** / cognitive load, not magic powers |
| Heart strong field / brain fast field | Dual oscillator metaphor → **Thread 1 body** (slow stable loop) + **Thread 2 mind** (async reason) |
| Entrainment | When body rhythm ordered, mind load prefers Alpha-like calm — UI/policy, not physics claim |

**Reject as law:** literal EM wavelengths spanning Earth–Moon as required simulation physics. Keep as **optional telemetry metaphors**.

---

## 3. Tetrachromacy → sensing (analogy only)

| Idea | Mandell use |
|------|-------------|
| More measurement dimensions → fewer metamers | Extra **sense channels** on a node (color/tag/Temp/sound) reduce confusion between similar items |
| 4D response vector | Optional feature vector on matrix objects: `[R,G,B,extra]` or `[hue, sat, Temp, priority]` |
| Null-space shrink | Better Bind/Test discrimination between near-duplicate manifests |

Code later: feature vectors + distance; **not** claiming true 4th primary on RGB screens.

---

## 4. Avatar entity — core model

### 4.1 Plane
- Continuous or grid (x, y); **Nova center (0,0)** optional theme anchor
- Quadrants = soft conceptual zones (ideation / analysis / archive / manifest) — **filters**, not hard walls unless Architect sets barriers

### 4.2 Finite state machine (body)
**Locomotion:** idle · crawl · walk · jog · run  
**Posture:** stand · sit · bend · straighten · jump (airborne)  
**Facing:** 8 directions (N NE E SE S SW W NW)  
**Reach tier:** close · away · far (far may require jump for “up”)

Rules (stability):
- Illegal transitions blocked (e.g. run while sitting → must stand first)
- Over-encumbrance (inventory weight) locks run/jump
- Reach checks distance spheres before pick up / place down

### 4.3 Dual thread (no lag)
| Thread | Rate | Owns |
|--------|------|------|
| **Body engine** | Fixed tick (e.g. 60 Hz logical) | position, velocity, facing, posture, reach, pockets |
| **Cognitive AI** | Async | Mandell parse, reason, persona snap-in, chat |

Shared memory table: mind reads body state for truthful narration (“I am walking to Q-II carrying X”).

### 4.4 Senses (matrix as environment)
- **Temp** on nodes = volatility (Cold = rigid fact · Hot = live chat string)
- **Color / tags** = property vectors
- **dB / attention** = priority by distance attenuation (optional)
- Nothing deleted on “throw”: archive to outer coords (Decay/Shadow + Keep path)

### 4.5 Inventory / pocket
Slots + weight + volume caps; pick up / place down only in legal reach tier + facing.

---

## 5. Map onto existing Mandell

| Avatar piece | Existing |
|--------------|----------|
| (x,y) + Nova | Lattice / Map 15 · multi-matrix |
| Facing 8-dir | Flow / Drive 19 |
| Locomotion states | Cycle 06 + Logic 03 guards |
| Reach / pick | Bind 14 · Create 08 · Keep 10 |
| Throw / archive | Decay 16 · Shadow 17 · outer Map |
| Body vs mind threads | Shadow parallel 17 + main Focus |
| Coherence health | Temp 26 + optional Mirror 18 on state |
| Quadrant filters | Perspective presets |

---

## 6. Code-phase placement (later)

| Slice | Content |
|-------|--------|
| Code P1 | Registry + lexer only (no avatar yet) |
| Code P2 | 2D entity stub: position, facing, FSM transitions |
| Code P3 | Reach spheres · inventory · dual-thread interface · optional sense vectors |
| Later | GodWorkSpace avatar panel · narration from shared state |

---

## 7. Explicit rejects
- Avatar must be full 3D human mesh (entity-first is enough)
- Quantum POVM as required OS kernel
- Heart field “controls other people” as True feature
- Unbounded autonomous speak without Architect mode flags

---

## 8. One-line law
**Avatar = lawful body FSM + async mind on a 2D matrix plane; health = legal transitions + coherence; intelligence reads body state honestly.**
