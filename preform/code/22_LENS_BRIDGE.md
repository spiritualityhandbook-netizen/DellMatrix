> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 22 — Lens Bridge

Status: TRUE

Wires PersonaLens into a command → examine → pane loop.

```python
b = LensBridge()
b.command("create and bind")
print(b.tick())
print(b.status())
```

Floor stays locked. Lenses are read-only.
