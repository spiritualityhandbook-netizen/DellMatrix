# 10 — ASCII Animation Player (Code Phase 3 Artifact 10)

Status: TRUE

## Purpose
Offline text-frame player that grows from:
- ExpressionField (7)
- Face-State Cycles (8)
- Kaomoji Packs (9)

Implements the Anim model defined on page 09.

## Model
```
Anim = { id, frames: string[], fps, loop, pack?, on_end? }
```

## Hooks
| Dell | Use |
|------|-----|
| 06 Cycle | tick() advances frame |
| 09 Show | show() returns current frame |
| 13 Loop | loop=True |
| 25 Pulse | short non-loop clips (sparkle) |
| 32/33 | pause() / resume() |

## Defaults shipped
idle · sparkle · point · joy · walk

## Next growth
- Reach / inventory on Grid can drive walk anim + position
- GodWorkSpace can host the player as a live pane
