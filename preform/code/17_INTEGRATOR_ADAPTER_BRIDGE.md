# 17 — Integrator ↔ Adapter Bridge (Code Phase 4.2)

Status: TRUE (documented behavior in 15_INTEGRATOR + 16_IMPORT_ADAPTER)

## Rule
On boot, Integrator may call `load_all()` from Artifact 16.

| LoadReport source | Integrator behavior |
|-------------------|---------------------|
| REAL | Prefer real class/attr when compatible |
| MISS / ERR | Keep embedded stand-in |

## Compatibility gate
Real module is used only if required constructor/attrs exist.
Otherwise stand-in — never crash boot.

## status() fields added
- `module_sources`: map of logical name → real|standin|miss|error
- `adapter_real_count`: number of REAL loads
