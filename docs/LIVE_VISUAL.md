# Live two-way visual — DEV (Lupe20)

**Status:** Implemented (opt-in). Snapshot `visual` remains default.

## Capabilities (on main)

| Layer | What |
|-------|------|
| Two-way bridge | Browser ↔ live Program on `127.0.0.1` |
| Matrix SVG | Ideas from x/y · skin colors · in-view highlight |
| Vision cones | Drawn on SVG for User + AI |
| Facing arrows | Direction markers on YOU + AI |
| Movement trails | Recent path fade for User + AI |
| User movement | Avatar body · walk · turn · face · WASD keys |
| AI companion | Walk · turn · goto · look · status |
| AI modes | `manual` · `wander` · `follow` |
| Directional vision | Cone from facing · range ~5.5 · half-angle 55° |
| Patterns | Count · skins · avg score · nearest |
| Proximity | Distance to AI / user |
| Act on seen | Confirm / Note on every seen idea |
| Cmd history | Last commands shown in panel |
| Nursery | Confirm / Reject live |
| Lattice | cube · sphere · core · flower |
| Auto-refresh | ~1.8s when enabled |

## Keys (focus not in input)

| Key | Action |
|-----|--------|
| W | walk forward |
| A | turn left |
| D | turn right |
| Q | look |
| E | ai look |
| F | ai follow |

## Commands

```text
you> live

walk forward / turn left / turn right / look
ai walk / ai turn left / ai look
ai follow / ai wander / ai manual
ai goto 3 4 / ai status
```

## Files

- `form/dell_matrix/live_visual.py`
- `Program.live_visual()` — `form/open.py`
- REPL — `live` / `visual live`

## Law

Localhost only · Nursery → confirm · Floor locked · snapshot path unchanged.
