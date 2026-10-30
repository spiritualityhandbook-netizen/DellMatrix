> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 23 — GWS Lens Panel

Status: TRUE

Embeds PersonaLens notes into a GodWorkSpace-style panel.

```python
ui = GWSWithLens()
ui.command("create and bind")
print(ui.render())
ui.collapse_lens()
```

Floor locked. Expand/collapse on `lens` panel.
