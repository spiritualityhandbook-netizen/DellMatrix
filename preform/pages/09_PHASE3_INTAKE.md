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

## Language Components (folded)

| Component | Mandell home |
|-----------|--------------|
| Phonology | Glyph layer · optional scansion · spoken seed rhythm |
| Morphology | **Leight / Loure** · morpheme engine |
| Syntax | **Flow ops** · brackets · Dell + manor order · parser |
| Semantics | **Manor** definitions · Primaries · Bind edges |
| Pragmatics | **Temp** · Persona · Architect confirm · context Horizon |

**One-line law:** Mandell already carries form (flow/morph), content (manor), and use (Temp/pragmatics); linguistics labels help audit gaps, not replace Primaries.

## Memory · Context Budget · Work Graph (folded practical)

| Kind | Map |
|------|-----|
| Work memory (what ran, failed, corrections) | Checkpoint 27 · Stamp 34 · Shadow 17 · delta log |
| Preference / taste | Optional personal matrix only |
| Traceable source links | Bind 14 · Map 15 · Keep 10 |
| Context budget / chunking | TokenCount 40 · Distill 38 · Split/Merge |
| Work context graph | Lightweight nodes (seed · file · correction) + Bind edges |

**Law:** Main matrix prefers work/coherence memory. Personal matrix may store vibe. Never answer only from summary when raw exists.

## Root files now historical

Folded into this page or page 10:
- PHASE3_EXPRESSION_KAOMOJI.md
- PHASE3_BODY_HEART_MIND_AVATAR.md
- PHASE3_ASCII_ANIMATION.md
- PHASE3_LANGUAGE_COMPONENTS.md
- PHASE3_MEMORY_RAG_PATTERNS.md
- PHASE3_BRIEFING_EXTRACT.md (useful non-decipherment bits only)

They remain for reference only.
