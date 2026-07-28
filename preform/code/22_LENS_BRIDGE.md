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
