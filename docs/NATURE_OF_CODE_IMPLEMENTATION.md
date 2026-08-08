# Nature of Code → DellMatrix (integrated)

**Source:** Daniel Shiffman, *The Nature of Code*  
**Cores:** `form/dell_matrix/nature_code.py`  
**Physics tick:** `form/dell_matrix/nature_physics.py`  
**Canvas:** `form/dell_matrix/assets/pages/nature_code.html`

---

## What is wired into the matrix

| Concept | Where it lives |
|---------|----------------|
| Vec2 / Mover / forces | `nature_code.py` |
| Inverse-square attraction | `attract()` + `NatureBridge.step_nodes` |
| Physics on idea nodes | `nature_physics.program_force_tick_nature(program)` |
| Live positions | Writes `Unit.x` / `Unit.y` on the plane |
| Visual demos | `/pages/nature_code.html` (Walker, Forces, Particles, Agents, CA) |

---

## Use in Program

```python
from form.open import open_program
from form.dell_matrix.nature_physics import program_force_tick_nature

p = open_program("Operator")
p.place("a", "Alpha", x=0, y=0)
p.place("b", "Beta", x=5, y=2)

# One Nature of Code physics frame (gravity wells + friction)
report = program_force_tick_nature(p)
print(report["nature_applied"], report["status"])

# Or via force tick after local open.py wiring:
# report = p.force_tick()  # includes nature when integrated
```

## Live visual

```text
http://127.0.0.1:8765/pages/nature_code.html
```

Keys: 1–6 modes · R reset · pointer = agent/particle target

## Runnable smoke

```bash
python -m form.dell_matrix.nature_code
```

Boolean host · Floor · Nursery intact.
