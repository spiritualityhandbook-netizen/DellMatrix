# DellMatrix

**Form is the only front door.**

This is a Mandell language + Dell Matrix system.
Floor is locked: **Alpha · Delta · Omega · Omni**

---

## Quick Start (the only way)

```bash
# Interactive session
python -m form.repl --owner Ace

# One-shot open + status
python -m form.boot --owner Ace

# Generate visual workspace (HTML you can open)
python -m form.open --owner Ace
# then in the REPL type: visual
```

### Most useful commands inside the REPL

```
place idea1 "My first idea" words here
grow ideas 3
enhance on
pulse
visual
say grow the business idea and show me
show
save
help
```

`say` accepts normal English and maps it into Mandell structure.

---

## Architecture (current)

```
form/                  ← THE SYSTEM (Python)
├── mandell/           Language floor + registry + translate
├── dell_matrix/       Matrix host, plane, visual, growth
├── duobeta/           Growth / self-understand
├── open.py            One program object
├── repl.py            Interactive front door
├── boot.py            Status entry
└── persist.py         Save / load

preform/               Planning + living Psalm pages (not runtime)
src/                   LEGACY (old JS). Do not use for new work.
```

---

## Rules

- Floor is locked. Nova is cheat-only.
- True registry writes require Architect confirm.
- Structure stays Mandell. English is display only.
- `src/` is legacy. All new work goes into `form/`.

---

## Status

Form foundation is live.  
English → Mandell path is active via `say`.  
Visual workspace generates offline interactive HTML.
