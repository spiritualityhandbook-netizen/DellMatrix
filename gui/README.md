# DellMatrix Studio

The creative-tool GUI for DellMatrix — a dark studio interface
in the FL Studio / Photoshop tradition, built for the way
DellMatrix actually works: a rack of 100 Dells, a visual flow
canvas, a seed editor, an inspector, a live store browser,
and a receipts timeline for everything you run.

## Launch

From the repository root:

```
python3 -m gui.server --owner Ace --port 8765
```

Then open http://127.0.0.1:8765 in a browser.

- `--owner` — whose program to open (default `Operator`).
  You can switch owners inside the Studio (top-right).
- `--port` — default 8765. `--host` — default 127.0.0.1
  (local only).

No dependencies beyond Python's standard library and the
repository itself.

## How it works

The Studio is a front-end, not a second engine. The server
(`gui/server.py`) reaches the program only through its public
paths — `open_program`, `execute_seed`, the canonical Dell
registry, and the growth lens — so what you see and run in the
Studio is exactly what the REPL would do. Sovereign steps
(Commit, Lock, the learning gate) stay yours: the Studio runs
a seed when you press RUN, and never on its own.

## Layout

- **Transport bar** — engine status, owner switcher.
- **Dell Rack** (left) — all 100 Dells, Core I and Core II,
  searchable. Click one to insert it into the seed editor.
- **Flow Canvas** (center) — your seed drawn as a chain of
  Dell cards, live as you type.
- **Seed Editor** — write Mandell seeds; Ctrl+Enter runs.
- **Inspector** (right) — the selected Dell's registry entry,
  or the full receipt of your last run.
- **Store** (right) — the program's live key/value store.
- **Growth** tab — the owner's growth field through the
  canonical lens (plants and their stages).
- **Console** tab — the raw session log.
- **Receipts** (bottom) — every run this session, newest
  first, with honest ok / failed / skipped verdicts.
