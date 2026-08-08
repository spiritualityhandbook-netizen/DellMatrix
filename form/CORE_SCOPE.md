# Core Form scope

## In core (Mandell Origin path)

Required for the Origin loop and offline acceptance:

- `form/open.py`, `form/repl.py`, `form/persist.py`, `form/accept.py`
- `form/mandell/` (floor, seed, registry, phrases, executor, polyglot, …)
- `form/dell_matrix/` (plane, lattice, growth, nursery, visual, gates,
  forces, personas, view_rooms, workshops, pillars, matrices_hub, ascii_bodies)
- `form/avatar/`
- `form/duobeta/` (generation ledger as used by Program)
- `form/smoke_all.py`, `form/invariants.py`

Ported matrices (from frozen `src/`, reimplemented — not imported):
nature forces · personas · view rooms · workshops ×7 · 6-pillar audit · ascii bodies.
Grow path: `grow ideas` + `evolve` advances DuoBeta + forces + pillars.

Acceptance path:

```
create → grow → confirm → sphere → save → load → visual
```

## Out of core (quarantined side packages)

| Package | Role | Rule |
|---------|------|------|
| `form/trading/` | Sister trading tools | Optional. README SIDE lock. Do not import into open/repl. |
| `form/llm/` | Local model bridge experiments | Optional. README SIDE lock. Offline acceptance must not depend on it. |

**Lock:** Origin path never requires network, brokers, or external models.

## LEGACY (frozen, not side)

See `form/LEGACY.md` — `src/` and `preform/` are frozen historical.
preform residual archive is **closed** via stamp (`docs/RESIDUAL_COMPLETE.md`).

## CI

`.github/workflows/form-smoke.yml` runs core offline checks on push to main.
