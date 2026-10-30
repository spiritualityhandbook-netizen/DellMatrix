> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 25 — UnifiedEntry × Token Show Gate

Status: TRUE (behavior in `24_UNIFIED_ENTRY.py`)

- Loads `18_TOKEN_SHOW_GATE.ShowGate` when present
- `set_seed_strip` / Show-style commands charge budget
- Strict reject or soft trim; never raises
- `status()` exposes budget used / rejects / trims
