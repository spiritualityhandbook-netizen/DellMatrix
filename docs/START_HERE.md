# Start here — DellMatrix (DEV)

**DellMatrix = the developer matrix.**  
Blank matrices share its capabilities, not your personal lore.

```bash
python launch.py              # DEV / Operator
python launch.py Ace          # Dell Matrix Ace (personal)
python launch.py Worldwide    # Worldwide ideas
python launch.py Friend       # blank-style profile
```

## Ideas need substance

```text
create an idea called True Lore detail: deeper meanings of names and lore goals: teach patterns; honest research; loved name tool
```

`detail:` what it is · `goals:` what evolution aims at  
Growth biases toward goals. Nursery still quarantines until confirm.

Edit later: `set detail <id|label> …` · `set goals <id|label> a; b` · `idea <id>` · `undo`

## Acceptance

```text
create → grow → confirm → sphere → save · load · visual
```

Or type `tutorial` · `what next` · `ready`

## What the program needs (built-in)

| Need | Command |
|------|---------|
| Strong ideas | `create … detail: … goals: …` |
| Guidance | `what next` (live NBD) |
| Checklist | `ready` |
| Memory | `history` · `undo` |
| Self | `self` · `self evolve` |
| Strength | `python3 -m form.dell_matrix.program_strength` |

See `docs/PROGRAM_NEEDS.md`

## Tiers

See `form/MATRIX_ARCHITECTURE.md`  
True Lore (future): `form/mandell/TRUE_LORE.md`  
Audit: `docs/AUDIT_MATRIX_TIERS.md`

## LatinMandell

```text
explain create
la cresce 2
morph Commandell
```

## Visual

- **Snapshot (always works offline):** type `visual` → open project-root `DellMatrix_UI.html` in a browser (no server)
- **Live (needs a running process):** keep the host terminal open:
  ```bash
  python3 -m form.dell_matrix.live_host --load
  ```
  then open http://127.0.0.1:8765/  
  A one-shot `live` call dies with its process — that is why HTML often “didn’t work.”
- **Look:** type `look` for directional vision from facing
- **Pages:** `zoom <id|label>` · `page` · `unzoom`
- **Inspire Pack (offline):** `attend` · `multilook` · `slopes` · `prefs` · `glyph` · `script` · `inspire` — see `docs/INSPIRE_PACK.md`
- **End pages (no loose ends):** `page` opens nearest idea end-page with doors; every live route has a surface (`/workshops`, `/inspire`, …); bare incomplete cmds return usage (never mis-create)
- **English brain:** speak naturally — `english expand 150` · `english status` · see `docs/ENGLISH_BRAIN_150.md`
- **Self + evolve:** `self` · `self map` · `self evolve` · `evolve loop 12` · see `docs/PROGRAM_EVOLVE_150.md`
- **Strength:** `python3 -m form.dell_matrix.program_strength` — function + usability gates · `docs/PROGRAM_STRENGTH.md`
- **Function 150:** `python3 -m form.dell_matrix.function_150_loop` — 150-cycle full surface verify (all must pass)

Keys in live: WASD · R run · Q look · E AI follow · C recenter · I/2 iso/2d

LEGACY: `preform/` · `src/` frozen · trading/llm SIDE
