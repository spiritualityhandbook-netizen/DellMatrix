# 26 — UnifiedEntry search bind

Status: TRUE (in `24_UNIFIED_ENTRY.py`)

- `search_dell(query)` / `search_flow(query)`
- Uses real GWSPanels search when present
- Else searches local registry JSON / embedded core flows
- Hits shown in render under SEARCH section
