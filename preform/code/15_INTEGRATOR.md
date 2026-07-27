# 15 — Integrator (HARDENED)

Status: TRUE

## Hardening
- Loads real `01_REGISTRY_DATA.json` when present
- Loads real `02_TINY_LEXER.tokenize` when present
- Falls back cleanly if either is missing
- `--smoke` runs full path tests (pick/stow/express/move/search/confirm)

## Expanded GodWorkSpace
- Dell search (`search(query)` → registry name/manor/number)
- Pipeline confirm queue (`pipeline_add` / `confirm(n)`)

## Run
```bash
python preform/code/15_INTEGRATOR.py          # demo
python preform/code/15_INTEGRATOR.py --smoke  # smoke test
```
