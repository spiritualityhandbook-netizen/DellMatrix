# 16 — Import Adapter (Code Phase 4.1)

Status: TRUE

## Purpose
Thin offline loader for real `preform/code` modules 05–14 (+ 01/02).

## Behavior
- `load_all()` → `LoadReport` with per-file REAL / MISS / ERR
- `report.get(file, attr, default)` — never raises on missing
- Stand-ins remain valid; adapter does not force replacement

## Run
```bash
python preform/code/16_IMPORT_ADAPTER.py
```

## Next
Integrator may optionally consume LoadReport to prefer real classes when `source=="real"`.
