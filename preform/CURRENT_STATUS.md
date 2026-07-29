# Current Status — DellMatrix Preform

As of: 2026-07-28

## Phase
| Layer | Status |
|-------|--------|
| Preform docs (pages + Psalm) | Living |
| Code Phase 1–3 | COMPLETE · HARDENED |
| Code Phase 4 | TRUE |
| SUS audit | TRUE (`pages/13_SUS_AUDIT.md`) |
| Blank handoff | TRUE |

## Recommended commands
```bash
# You — living core
python preform/code/29_COMPOSE_ENTRY.py --smoke

# You — pack for someone else
cd preform/seed && python pack_seed.py

# Them — first run
python blank_runner.py
```

## Repo anchors
- Psalm: `preform/00_PSALM_PREFORM.md`
- Capabilities: `preform/CAPABILITIES.md`
- Distribution: `preform/DISTRIBUTION.md`
- Phase status: `preform/pages/07_PHASE_STATUS.md`
- SUS audit: `preform/pages/13_SUS_AUDIT.md`
- Compose runner: `preform/code/29_COMPOSE_ENTRY.py`
- Seed: `preform/seed/`

## Next optional densities (not required to ship)
1. Minimal parser (03) after lexer on compose
2. Prefer Integrator 15 inside compose when loadable
3. Thinks / workmem pane
4. Full GWS expand API on compose render
