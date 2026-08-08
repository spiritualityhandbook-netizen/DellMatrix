# NBD Log

## 2026-08-08 — Nature of Code auto-wired into every force_tick

| Item | Result |
|------|--------|
| Cores | `form/dell_matrix/nature_code.py` — Vec2, Mover, Agent, NatureBridge |
| Physics | `form/dell_matrix/nature_physics.py` — program_force_tick_nature |
| Auto-wire | `Program.force_tick()` now always calls nature physics after ForceField.tick |
| Canvas | `/pages/nature_code.html` |
| Docs | `docs/NATURE_OF_CODE_IMPLEMENTATION.md` (full Ch0–11 map) |
| Law | Boolean host intact · Floor/Nursery untouched |

```python
# every force_tick now moves idea nodes under gravity wells + friction
report = program.force_tick()
# report["nature"]["nature_applied"] · Unit.x / Unit.y updated
```

```bash
python -m form.dell_matrix.nature_code
# live: /pages/nature_code.html
```
