# 18 — Token Show Gate (Code Phase 4.3)

Status: TRUE

## Purpose
Apply TokenBudget to Dell 09 Show and seed-strip paths.

## API
- `set_seed_strip(text) -> (ok, message)`
- `show(text) -> (ok, payload)`
- modes: `strict` (reject) · `soft` (trim then charge)

## Rules
- Reserve tokens for system chrome
- Never raise on over-budget
- Charge only on successful set/show

## Run
```bash
python preform/code/18_TOKEN_SHOW_GATE.py
```
