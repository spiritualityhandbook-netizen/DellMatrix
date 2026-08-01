# Core Form scope

## In core (Mandell Origin path)

Required for the Origin loop and offline acceptance:

- `form/open.py`, `form/repl.py`, `form/persist.py`, `form/accept.py`
- `form/mandell/` (floor, seed, registry, phrases, executor, polyglot, …)
- `form/dell_matrix/` (plane, lattice, growth, nursery, visual, gates)
- `form/avatar/`
- `form/duobeta/` (generation ledger as used by Program)
- `form/smoke_all.py`, `form/invariants.py`

Acceptance path:

```
create → grow → confirm → sphere → save → load → visual
```

## Out of core (quarantined side packages)

| Package | Role | Rule |
|---------|------|------|
| `form/trading/` | Sister trading tools | Optional. Not required for Origin. |
| `form/llm/` | Local model bridge experiments | Optional. Offline acceptance must not depend on it. |

These may live in the repo. They must not be described as part of the core Form runtime in START_HERE, AUDIT, or LIVE_INDEX.

## LEGACY (frozen, not side)

See `form/LEGACY.md` — `src/` and `preform/` are frozen historical, not optional features.
