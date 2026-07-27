# Page 09 — Phase 3 Intake (Living Form)

Status: TRUE · Living (folded from root Phase 3 extracts)

## Body · Heart · Mind · Avatar

- Entity lives on (x, y) plane
- 8-directional facing
- Locomotion + posture FSM (walk / jog / run / sit / stand / jump / bend)
- Reach tiers: close / away / far
- Pick up / place down
- Dual thread: body tick is stable · mind is async
- Law: **Body first. Thinks second. Thinks always reads real body state.**

Thinks placement (practical lock):
| Phase | Owns |
|-------|------|
| Code 1 | Language only — thinks **not** here |
| Code 2 | Body FSM + shared state table |
| **Code 3** | **Thinks** (async cognitive thread) bound to body state |

Narration may never invent body facts. Always queries live FSM.

## Expression / Kaomoji Packs

Kaomoji packs map into Tone (05) and Show (09).  
Used for Avatar face-state and ASCII animation frames.  
Pure text · offline · zero image dependency.

### Categories (expression packs)

| Pack | Role |
|------|------|
| Classic | Baseline faces `:-)` `:^)` `^_^` |
| Smiling | Positive / warm Tone |
| Love | Affection / bind-warm |
| Hugging | Embrace / merge-feel |
| Flexing | Strength / Drive |
| Pointing | Direction / Map attention |
| Sparkling | Highlight · Pulse · discovery |
| Worrying | Caution · soft Test signal |
| Disapproving | Soft Logic block |
| Crying | Soft fail / empathy (optional) |
| Table Flipping | Hard reject / humor (gated) |

These are **not new Dells**. They are expression tokens under 05 Tone and 09 Show.

### Sample tokens (copy-safe)

Classic: `:-)` `:^)` `^_^` `(^^)` `;-)`  
Smiling: `(^_^)` `(^∇^)` `(∗‿∗)`  
Love: `(♥ω♥)` `(✿♥‿♥)`  
Pointing: `→_→` `←_←`  
Worrying: `(;_;)` `(⊙_⊙)`  
Disapproving: `ಠ_ಠ`  
Sparkling: `✧` `✦` `★` `☆`

### Rules
- Optional — never required for valid seed
- Avatar face-state field = expression pack + frame index
- Prefer short tokens; long kaomoji = Hot only
- Custom packs allowed in personal matrix
- Harsh packs gated in Surgical mode

## ASCII Animation

Goal: Intuitive, efficient, offline motion in terminal and GodWorkSpace using **text frames only**.

```
Anim = {
  id, fps, frames: string[],
  loop: bool,
  pack?: expression category,
  on_end?: Dell chain
}
```

- Frame = one multiline or single-line ASCII/kaomoji string
- Play = Cycle 06 + Show 09 redraw
- Avatar walk = cycle of facing glyphs + position update on Grid
- Sparkle / pulse = short non-loop clips on success

### Efficiency
- Max frames default 8–16 for UI chrome
- Prefer 1-line animations for mobile
- Store packs as JSON arrays (gzip cold OK)
- No GIF / network required

### Hooks
| Dell | Use |
|------|-----|
| 06 Cycle | Advance frame |
| 09 Show | Paint frame |
| 13 Loop | Repeat until Alpha/Pause |
| 25 Pulse | Trigger sparkle clip |
| 32/33 Pause/Resume | Freeze/unfreeze |
| 05 Tone | Choose expression pack |

## Language Components (summary)

Phonology → glyphs  
Morphology → Leight / Loure  
Syntax → flow / parser  
Semantics → Manor  
Pragmatics → Temp + Manual

## Root files now historical

The following root extracts have been folded into this page or page 10:
- PHASE3_EXPRESSION_KAOMOJI.md
- PHASE3_BODY_HEART_MIND_AVATAR.md
- PHASE3_ASCII_ANIMATION.md

They remain for reference only.
