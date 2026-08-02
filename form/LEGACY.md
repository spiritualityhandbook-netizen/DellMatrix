# LEGACY — Do Not Use for New Work

Unified freeze map for dual-era and pre-Form material.

## Frozen paths

| Path | Era | Rule |
|------|-----|------|
| `src/` | Old JavaScript DellMatrix | **Frozen.** Port into `form/` only if high-S and explicitly requested. |
| `preform/` | Pre-Form research, phases, stubs | **Frozen · residual closed 2026-08-01.** Historical only. Not the execution path. |

## Live path

All new development: **`form/`** (Python).

- Door: `form/open.py` + `form/repl.py`
- Origin: `form/mandell/`
- Matrix: `form/dell_matrix/`

## Side packages (not LEGACY, not core)

See `form/CORE_SCOPE.md`:

- `form/trading/` — optional sister tools
- `form/llm/` — optional local-model experiments

Neither is required for offline acceptance:

`create → grow → confirm → sphere → save → load → visual`

## Rule

Do not extend LEGACY paths.  
Do not import preform into production.  
Do not treat STATUS files under preform as roadmap authority.  
Physical residual of preform is **closed** via hard stamp (NBD Block 1).
