# 11 — Reach + Inventory (Code Phase 3 Artifact 11)

Status: TRUE

## Purpose
Body-first reach and inventory that grows from Avatar FSM (6) and Grid (5).

## Reach tiers
| Tier | Distance (Chebyshev) |
|------|----------------------|
| CLOSE | 1 |
| AWAY  | 2 |
| FAR   | 3 |

## Actions
- `can_reach(target)` — distance check
- `look_at(target)` — read cell if in reach (mind-safe)
- `pick(target)` — hand from grid
- `place(target)` — hand to grid
- `stow()` — hand → inventory slot
- `draw(index)` — inventory → hand

## Law
Body first. Mind only reads via `status()` / `read_body()`.
