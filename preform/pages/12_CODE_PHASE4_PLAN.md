# Page 12 — Code Phase 4 Planning

Status: ACTIVE

## Active cells

| Cell | Artifact | Status |
|------|----------|--------|
| 4.1 Real-module import layer | `code/16_IMPORT_ADAPTER.py` | **TRUE** |
| 4.2 Integrator consumes LoadReport | `resolve_components()` + bridge doc | **TRUE** |
| 4.3 TokenBudget on Show/seed paths | — | **NEXT** |
| 4B GWS expand/collapse + flow search | — | queued |
| 4C Persona runtime lens | — | queued |

## 4.2 behavior
`resolve_components(report)` returns real classes when `source=="real"`, else `None`.
Integrator / callers keep stand-ins when value is `None`.
Boot must never crash on missing modules.

## Entry rules
- Functionality first
- Offline purity
- Register growth on this page + Psalm
