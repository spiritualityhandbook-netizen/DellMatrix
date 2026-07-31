# Foundation Status — living map

**Floor:** Alpha · Delta · Omega · Omni (LOCKED)

**Front door:** Form only (`python -m form.repl`)

## Form stack

| Module | Path | Role |
|--------|------|------|
| Mandell Floor | form/mandell/ | Language lock |
| Registry / Manifest | form/mandell/ | Dell 00–50 |
| **Translate** | form/mandell/translate.py | **English → Mandell** |
| DellMatrix host | form/dell_matrix/core.py | Snap + verify |
| Plane | plane.py | Geometric surface |
| Visual | visual.py | Offline interactive HTML |
| IdeaGrow | idea_grow.py | Growth cycles |
| Open / REPL | open.py · repl.py | One program + front door |
| Persist | persist.py | Save / checkpoint |
| SelfGrow | form/duobeta/selfgrow.py | Curriculum growth |

## How to run

```bash
python -m form.repl --owner Ace
```

Inside the REPL:

```
say create an idea called business
say grow ideas 3
say show me the matrix
visual
```

`visual` writes an offline HTML file you can open in any browser.

## Legacy

`src/` is frozen. See `form/LEGACY.md`.
