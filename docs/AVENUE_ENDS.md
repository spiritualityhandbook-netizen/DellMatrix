# Avenue ends — no loose ends

Every user path must finish on a **useful end page** or **closed usage message**.

## HTML surfaces (live menu)

| Route | End surface |
|-------|-------------|
| `/` | Main menu cards |
| `/walk` | First-person matrix walk |
| `/lattice` | Full idea map |
| `/nursery` | Confirm / reject quarantine |
| `/program` | Status · pillars · evolve · save |
| `/personas` | Roster · BIMO |
| `/forces` | Force field |
| `/geometry` | Sacred geometry |
| `/matrices` | Matrices hub |
| `/workshops` | Workshop workbenches |
| `/inspire` | Inspire Pack tools |
| `/console` | Full result sheet + history |

## Idea page

- `page` — auto-opens **nearest** idea if none zoomed
- `page <id|label>` / `zoom <id|label>` — full end card: words, goals, glyph, **doors** (next cmds)
- `unzoom` — overview with doors back

## Incomplete commands

Bare `confirm`, `reject`, `create`, `zoom`, `shell`, … return **usage** (never spawn a bogus idea).

## Live bridge

REPL `_say` output is **captured** into `msg` so console / buttons always show a result body.

## Check

```bash
python3 -m form.smoke_all
# or ad-hoc: every actions_flat("depth") cmd returns non-empty msg/error
```
