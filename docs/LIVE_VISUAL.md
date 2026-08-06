# Live two-way visual — DEV

**Status:** Implemented (opt-in). Snapshot `visual` remains default.

## Capabilities (code, not talk)

| Layer | What |
|-------|------|
| Two-way bridge | Browser ↔ live Program on `127.0.0.1` |
| Matrix SVG | Ideas drawn from x/y · skin colors |
| User movement | Avatar body pos/facing · walk · turn · face · sit/stand |
| AI companion | Independent pos/facing · walk · turn · goto · status |
| Directional vision | Look cone from facing · range 5 · half-angle ~55° |
| Patterns | Seen count · skin mix · avg score · nearest |
| AI vision + doing | What AI sees · what AI is doing / last action |
| Act on seen | Confirm / Note buttons on every seen idea |
| Nursery | Confirm / Reject live |
| Lattice forms | cube · sphere · core · flower |
| Auto-refresh | Optional 2s poll |

## Commands

```text
you> live
you> visual live

# movement
walk forward
turn left / turn right
face north
ai walk
ai walk 2
ai turn left
ai face N
ai goto 3 4
ai status

# vision
look
ai look
```

## Files

- `form/dell_matrix/live_visual.py` — server, vision, AI, UI
- `Program.live_visual()` in `form/open.py`
- REPL: `live` / `visual live` in `form/repl.py`

## Law

- Localhost only (offline core)
- Growth still Nursery → confirm only
- Floor locked
- No silent live-plane writes
- Snapshot path unchanged

## Use

```bash
python launch.py
# at prompt:
live
# open printed URL (default http://127.0.0.1:8765/)
```
