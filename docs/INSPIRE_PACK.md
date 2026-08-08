# Inspire Pack — offline video-distilled capabilities

Study of public YouTube links → **useful offline patterns only**.  
No external models, no network at runtime, no claim of full transcript capture.

## Sources (public titles)

| # | Video id | Theme → Form feature |
|---|----------|----------------------|
| 1 | `YmLp8qe87A0` | LLM from scratch → `tokenize` / bag embeddings / `attend` |
| 2 | `iyux-TVToRU` | Calculus slowly → score **slopes** (Δscore/Δt after `pulse`) |
| 3 | `eDpTtxFhP2s` | p5play sprites → `SpriteAnimator` walk/idle cycles on `body_art` |
| 4 | `vO6SWG-jxvE` | Multi-scale AI vision → `multilook` near/mid/far + memory |
| 5 | `Qr3VsZYQy4s` | Game with no assets → `glyph` / procedural cards |
| 6 | `ebqKYLKjL6U` | Verse scripting → `script cmd; cmd; …` batch runner |
| 7 | `ppQh4Tc9BmM` | Efficient AI race → cheap-first `route_cost` on scripts |
| 8 | `8B05cy3UuSE` | Copying humans ≠ enough → preference ledger on confirm/reject |
| 9 | `bm1BjOjS7sQ` | DeepSeek moment → same efficiency + pedagogy stubs (offline) |

## Commands

```text
attend [query]           soft attention over live ideas + nursery
multilook                near / mid / far vision layers + memory
slopes                   score calculus after ≥2 pulses
prefs                    preference weights from confirm/reject
glyph [seed|label]       procedural ASCII art card
script look; pulse; status
inspire                  pack status
```

Also on live visual menus (mode **builder**+): group **Inspire**.

## Law

- Floor locked · Nursery confirm · SIDE `llm/` / trading untouched  
- Educational stubs only — not production neural nets  
- Persist: `inspire` key in program JSON (prefs + score samples + sprite)

## Module

`form/dell_matrix/inspire_pack.py` · wired into `Program` (`form/open.py`), REPL, live visual, actions registry, persist.

```bash
python -m form.dell_matrix.inspire_pack
python -m form.smoke_all
```
