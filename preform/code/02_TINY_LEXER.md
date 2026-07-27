# 02 — Tiny Lexer Stub

Status: TRUE · Code Phase 1 Artifact 2

## Decisions (calculated for the program)

| Decision | Choice | Reason |
|----------|--------|--------|
| Language | Python 3 (stdlib only) | Best offline fit for ChromeOS/Linux (penguin), zero deps, future self-host path |
| Form | Pure function `tokenize(text)` | Minimal surface, no class bloat, easy to embed later |
| Matching | Longest-first for flows | Prevents `>` eating `>>>` |
| Scope | Recognition only | Parser / AST belongs to Code Phase 2 |
| Dual boundary | Structure tokens = Mandel · free text = English | Enforces Language Law without extra markers |
| Numbers | Strict 0–50 | Outside range stays TEXT |

## Token Types

- `DELL` — integer 0–50
- `FLOW` — one of the locked symbols
- `LEIGHT` — create-path marker
- `LOURE` — change-path marker
- `TEXT` — everything else (display / English side)

## Usage

```bash
python3 preform/code/02_TINY_LEXER.py
```

Or import:

```python
from preform.code import tiny_lexer   # once package structure exists
tokens = tokenize("50 Manifest > 08 Create")
```

## Next

Code Phase 1 still open for any remaining offline capability hardening.
Code Phase 2 (parser + AST stub) remains closed until this cell is confirmed True by Architect.
