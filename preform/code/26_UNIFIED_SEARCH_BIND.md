> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 26 — UnifiedEntry search bind

Status: TRUE (in `24_UNIFIED_ENTRY.py`)

- `search_dell(query)` / `search_flow(query)`
- Uses real GWSPanels search when present
- Else searches local registry JSON / embedded core flows
- Hits shown in render under SEARCH section
