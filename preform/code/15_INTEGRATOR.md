> STATUS: NOT IN USE — preform/src are earlier generations of DellMatrix, retained as design history and reference. The production runtime is form/ (verified at commit 11933da, 2026-10-30). This file does not describe current behavior.

# 15 — Integrator (HARDENED + ERROR-HANDLED SMOKE)

Status: TRUE

## Hardening
- Loads real `01_REGISTRY_DATA.json` when present
- Loads real `02_TINY_LEXER.tokenize` when present
- Falls back cleanly if either is missing

## Smoke suite
```bash
python preform/code/15_INTEGRATOR.py --smoke
```

Per-test error handling:
- Each case wrapped in try/except
- Failures report EXCEPTION type + message
- Suite continues after individual failures
- Includes negative path: bad pick target must not raise
- Summary: N/M PASS + failed list

## Expanded GodWorkSpace
- Dell search (`search(query)`)
- Pipeline confirm queue (`pipeline_add` / `confirm(n)`)
