# Live two-way visual — A+ (Phases A–E)

**Status:** Implemented (opt-in). Snapshot `visual` remains default.

## Capabilities (on main)

| Layer | What |
|-------|------|
| Two-way bridge | Browser ↔ live Program on `127.0.0.1` |
| Matrix SVG | Ideas from x/y · skin silhouettes (2D + iso) · in-view highlight |
| Vision cones | **Drawn on SVG** for User + AI (polygons) |
| Facing arrows | Direction markers on YOU + AI |
| Movement trails | Age-faded path for User + AI |
| User movement | Walk · run · turn · sit/stand · face · WASD + R |
| AI companion | First-class on Program · persist · walk · turn · goto · look · modes |
| AI modes | `manual` · `wander` · `follow` |
| Directional vision | Cone from facing · range ~5.5 · half-angle 55° |
| Patterns | Count · skins · avg score · nearest · persona/lens |
| Proximity | Distance to AI / user |
| Act on seen | Page (inspect) or Confirm — click mode toggle |
| Cmd history | Last commands shown in panel |
| Nursery | Confirm / Reject live · optional ghost markers |
| Lattice | cube · sphere · core · flower · shell rings · FoL centers |
| Edges | enhance · vesica · sandbox on live SVG |
| Camera | Follow YOU · recenter · soft world pan |
| Grid snap | Optional when form is cube/square |
| Workshops | matrix · perspective · mandel |
| Actions registry | Shared with snapshot · mode beginner/builder/depth |
| Auto-refresh | ~1.8s when enabled |

## Keys (focus not in input)

| Key | Action |
|-----|--------|
| W | walk forward |
| Shift+W / R | run |
| J | jog |
| A | turn left |
| D | turn right |
| Shift+A / Shift+D | strafe left / right |
| S | backstep (facing preserved) |
| Q | look |
| E | ai follow |
| C | recenter |
| I / 2 | iso / 2D |

## Commands

```text
you> live

walk forward / run / turn left / turn right / look
zoom <id> / page / unzoom
ai walk / ai turn left / ai look
ai follow / ai wander / ai manual
ai goto 3 4 / ai status
workshop matrix | workshops | workshop leave
mode beginner|builder|depth
lens seed | persona manny | snap on
```

## Files

- `form/dell_matrix/live_visual.py`
- `form/dell_matrix/vision.py`
- `form/dell_matrix/companion.py`
- `form/dell_matrix/actions_registry.py`
- `form/dell_matrix/workshops.py`
- `Program.live_visual()` — `form/open.py`
- REPL — `live` / `visual live`

## Law

Localhost only · Nursery → confirm · Floor locked · snapshot path unchanged · companion saved in persist v7+.
