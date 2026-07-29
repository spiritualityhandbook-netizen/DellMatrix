# 30 — Compose × Lexer bind

Status: TRUE (behavior in `29_COMPOSE_ENTRY.py`)

When command text contains Dell-like tokens (`08`, `14[Bind]`, `>>`, etc.),
ComposeEntry runs Tiny Lexer (02) if present and records token summary on pipeline + status.
