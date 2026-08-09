# GitHub First — DellMatrix law

**Repo:** https://github.com/spiritualityhandbook-netizen/DellMatrix  
**Branch:** `main`

## Rule

1. **Every durable change is pushed to this GitHub repo.**
2. Chat / local sandbox runs are **not** the source of truth.
3. If it isn’t on GitHub, it isn’t shipped.
4. Prefer `create_or_update_file` / commits on `main` over ephemeral local-only patches.

## Why

The operator cannot rely on a remote chat computer.  
DellMatrix must live in **GitHub** so it can be cloned, run, and grown anywhere (ChromeOS, Linux, offline hosts).

## Checklist for each session

- [ ] New modules under `form/dell_matrix/` or `form/mandell/` committed
- [ ] Docs under `docs/` updated when behavior changes
- [ ] Smoke paths remain offline-capable unless InternetGate is explicit
- [ ] No “fixed only in chat” logic left unpushed

## Current growth spine (on repo)

| Module | Role |
|--------|------|
| `form/dell_matrix/verita.py` | Solo + pair judgment |
| `form/dell_matrix/floor_spirit.py` | Alpha·Delta·Omega·Omni |
| `form/dell_matrix/delta_pressure.py` | Δ_known / Δ_unknown pressure |
| `form/dell_matrix/organ_atlas.py` | Body organ catalog |
| `form/dell_matrix/brain.py` | Think cycle under Floor |
| `form/dell_matrix/internet_gate.py` | Far-wide search |
| `form/dell_matrix/auto_growth.py` | Auto nursery + continuous grow |
| `form/dell_matrix/matrix_awake.py` | Stay-on heartbeat + text/speak |
| `docs/MATRIX_AWAKE_VISION.md` | Vision |
| `docs/MISSING_ORGANS.md` | Organ densify list |

## Operator note

When densifying missing organs: **pull from this repo**, don’t re-invent in chat.
