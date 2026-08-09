# Docs Gap Closer — DellMatrix

**Date:** 2026-08-08  
**Purpose:** Map every major `docs/` idea to code status. Implement remaining high-value items.

---

## High-value implementation (this pass)

| Item | Code | Status |
|------|------|--------|
| Auto-wire Nature physics into every force_tick | `form/open.py` `force_tick` | **DONE** |
| Ch3 Angular oscillation | `nature_code.AngularMover` + NatureBridge | **DONE** |
| Breath → oscillation phase | `nature_physics.program_force_tick_nature` | **DONE** |
| Act-on-seen (vision actions) | `form/dell_matrix/act_on_seen.py` | **DONE** |
| Neuroevo ForceField intensities | `form/dell_matrix/neuroevo.py` | **DONE** |
| Nature paraphrase seeds | english_brain PARAPHRASE + VERB_MAP | **DONE** (this pass) |
| Full Ch0–11 mapping doc | `docs/NATURE_OF_CODE_IMPLEMENTATION.md` | **DONE** |

---

## docs/ inventory → status

### Core architecture (already covered)
- `DUAL_LATTICE.md` → HarmonicLattice + Dual form toggle
- `FOUNDATION_AND_SNAPINS.md` → DellMatrix.snap + SnapCandidate
- `UNIFICATION.md` → Program front door
- `START_HERE.md` / `INSTALL.md` → offline localhost core
- `NATURE_FORCES.md` → `forces.ForceField` (water/growth/breath/gravity/time/weather/space)
- `LIVE_VISUAL.md` / `FIRST_PERSON_MATRIX.md` → live_visual + first_person
- `CODE_EVOLUTION.md` → code_evolution.py develop_loop
- `SACRED_GEOMETRY.md` → sacred_geometry.py
- `ENGLISH_BRAIN.md` → english_brain.py
- `PRACTICAL_VISUAL_IDEA.md` → vision cones + movement + trails

### Audits (reference only — not runtime)
- `AUDIT*.md`, `FULL_PROGRAM_AUDIT_150.md`, `FINAL_AUDIT_REPORT*` → pillars.audit / self_model
- `PROGRAM_STRENGTH.md` / `PROGRAM_NEEDS.md` → needs.py + program_strength

### External Nature of Code notes
- `docs/external/nature_of_code/chapter_00`…`11` → cores in nature_code + mapping doc
- Integration ideas (L-systems draw, GA demo, perceptron) → **partial**: RingedGrowth ≈ fractal branching; neuroevo ≈ Ch11 seed; full L-system canvas still optional

### 150-loops / enhance plans
- `PAGE_ENHANCE_150`, `SYNC_UX_150`, `PROGRAM_EVOLVE_150`, `BUTTON_PATH_ENHANCE_150` → corresponding `*_150_loop.py` modules present under form/dell_matrix

### Archive
- `docs/archive/*` → historical; do not re-implement

---

## Commands (new)

```text
force tick          → ForceField + Nature physics + oscillation
act on seen         → list / inspect / zoom / attend / force / nearest
act inspect 0
act zoom 0
act force 0
neuroevo 5          → evolve force intensities 5 generations
nature status
```

```python
from form.open import open_program
p = open_program("Op")
p.place("a", "Alpha", x=0, y=2)
print(p.force_tick()["nature"]["nature_applied"])

from form.dell_matrix.act_on_seen import act_on_seen, list_seen
print(list_seen(p))
print(act_on_seen(p, "inspect", 0))

from form.dell_matrix.neuroevo import neuroevo_run
print(neuroevo_run(p, generations=3))
```

---

## Still optional (not blocking)

1. Full L-system / Koch canvas page (visual-only)
2. Explicit pure-Python perceptron module (Ch10) beyond OpenShell grades
3. Deeper live_visual UI buttons for act-on-seen (API ready)
4. 2D CA grid beyond ca1d_step

Law: Boolean host · Floor · Nursery · offline core intact.
