> STATUS: IN USE — describes live code in form/ at commit 11933da. Doc verified against code 2026-10-30.

# Foundation Status — living map

**Floor:** Alpha · Delta · Omega · Omni (LOCKED)

**Front door:** Form only (`python -m form.repl`)

## Form stack

| Module | Path | Role |
|--------|------|------|
| Mandell Floor | form/mandell/ | Language lock |
| Registry / Manifest | form/mandell/ | Dell 00–99 (Core I 00–50 + Core II 51–99) |
| **Translate** | form/mandell/translate.py | **English → Mandell** |
| DellMatrix host | form/dell_matrix/core.py | Snap + verify |
| Plane | form/dell_matrix/plane.py | Geometric surface |
| Visual | form/dell_matrix/visual.py | Offline interactive HTML |
| Growth (`grow ideas`) | form/open.py (`Program.grow_ideas`) · form/grow.py | Growth cycles |
| Open / REPL | form/open.py · form/repl.py | One program + front door |
| Persist | form/persist.py | Save / checkpoint |
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
