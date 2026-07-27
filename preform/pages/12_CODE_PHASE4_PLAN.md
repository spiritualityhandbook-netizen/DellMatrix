# Page 12 — Code Phase 4 Planning

Status: ACTIVE

## Active cells

| Cell | Artifact | Status |
|------|----------|--------|
| 4.1 Import Adapter | `16_IMPORT_ADAPTER.py` | TRUE |
| 4.2 Integrator ↔ Adapter | `resolve_components` | TRUE |
| 4.3 TokenBudget on Show/seed | `18_TOKEN_SHOW_GATE.py` | **TRUE** |
| 4B GWS expand/collapse + flow search | — | **NEXT** |
| 4C Persona runtime lens | — | queued |

## 4.3 behavior
ShowGate charges TokenBudget on seed-strip and Show.
Strict rejects oversize; soft trims to remaining budget.

## Entry rules
Functionality first · offline · register on page + Psalm
