> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 19 — GWS Panels (Code Phase 4B)

Status: TRUE

## Purpose
Expand/collapse sections + flow-symbol search for GodWorkSpace.

## API
- `expand` / `collapse` / `toggle` / `expand_all` / `collapse_all`
- `search_dell(query)` — number, name, manor
- `search_flow(query)` — symbol, name, manor
- `render(extra)` — respects expanded flags (`[+]` collapsed, `[-]` open)

## Run
```bash
python preform/code/19_GWS_PANELS.py
```
