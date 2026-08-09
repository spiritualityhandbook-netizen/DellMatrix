# Track B — Free Matrix UI (PRIMARY)

**Operator choice:** B primary · do everything else **except C (trading)**.

## Intent

Chat is only a **window**. The program is a world you (and the companion) walk, look, and act inside.

## Run

```bash
git pull origin main
python -m form.dell_matrix.free_matrix
python -m form.dell_matrix.free_matrix --awake      # + growth heartbeat
python -m form.dell_matrix.free_matrix --smoke
python -m form.dell_matrix.live_host                 # keep UI process alive
```

Browser opens live visual (walk / lattice / nursery / personas / forces / …).

## API

```python
from form.dell_matrix import free_matrix as fm
p = fm.open_world()
fm.walk(p, "forward")
fm.turn(p, "right")
fm.look(p, "up")
fm.see(p)
fm.act(p, "inspect")
fm.companion_step(p)
fm.draw_frame(p)          # Track D seed
fm.start_ui(p)
fm.pulse_awake()          # Track A support
```

## Stack

| Piece | Module |
|-------|--------|
| Program door | `form/open.py` |
| Live UI | `live_visual.py` / `live_host.py` |
| Walk / turn / look | `first_person.py` |
| See | `vision.py` |
| Act on seen | `act_on_seen.py` |
| Companion | `companion.py` |
| Entry | `free_matrix.py` |
| Growth while on | `matrix_awake.py` / `auto_growth.py` |
| Draw seed | `free_matrix.draw_frame` |

## Tracks

| Track | Status |
|-------|--------|
| **B Free matrix UI** | **PRIMARY** — `free_matrix.py` |
| A Always-on agent | Support via `--awake` + `matrix_awake` |
| D Draw organ | Seed `draw_frame` (ASCII + optional glyph) |
| **C Trading** | **SKIPPED** |

## Next densify on B

1. Deeper walk page ↔ first_person parity in browser
2. Companion visible in live_visual state payload always
3. Draw organ → real SVG from lattice (beyond ASCII frame)
4. Single process: live_host + awake loop without two terminals

## Law

All durable work → GitHub `DellMatrix` · `docs/GITHUB_FIRST.md`
