> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 27 — UnifiedEntry pipeline bind

Status: TRUE (in `24_UNIFIED_ENTRY.py`)

- `pipeline_add(label)` → numbered item
- `pipeline_confirm(n)` → mark confirmed
- `pipeline_pending()` → open items
- Successful commands auto-add a pipeline line
- Render section `[±] PIPELINE`
