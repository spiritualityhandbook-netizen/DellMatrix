# Phase 3 Preform — ASCII Animation

Status: **PREFORM**

## Goal
Intuitive, efficient, offline motion in terminal and GodWorkSpace using **text frames only**.

## Model
```
Anim = {
  id, fps, frames: string[],
  loop: bool,
  pack?: expression category,
  on_end?: Dell chain
}
```

- **Frame** = one multiline or single-line ASCII/kaomoji string
- **Play** = Cycle 06 + Show 09 redraw (clear line / overwrite)
- **Avatar walk** = cycle of facing glyphs + position update on grid
- **Sparkle / pulse** = short non-loop clips on success

## Efficiency
- Max frames default 8–16 for UI chrome
- Prefer 1-line animations for mobile
- Store packs as JSON arrays (gzip cold OK)
- No GIF/network required

## Hooks to Mandell
| Dell | Use |
|------|-----|
| 06 Cycle | Advance frame |
| 09 Show | Paint frame |
| 13 Loop | Repeat until Alpha/Pause |
| 25 Pulse | Trigger sparkle clip |
| 32/33 Pause/Resume | Freeze/unfreeze anim |
| 05 Tone | Choose expression pack |

## Code placement
- Data packs: Code P3
- Minimal blink/spinner: can appear end of Code P2 as demo
- Full Avatar walk cycle: Code P3 with entity FSM

## Freedom
Users add packs in personal matrix; main matrix can pull shared packs.
