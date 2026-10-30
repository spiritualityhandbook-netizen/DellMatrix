> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 30 — Compose × Lexer bind

Status: TRUE (behavior in `29_COMPOSE_ENTRY.py`)

When command text contains Dell-like tokens (`08`, `14[Bind]`, `>>`, etc.),
ComposeEntry runs Tiny Lexer (02) if present and records token summary on pipeline + status.
