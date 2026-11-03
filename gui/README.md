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

- **Transport bar** — engine status LED, owner switcher.
- **Dell Rack** (left) — all 100 Dells, Core I (00–50) and
  Core II (51–99), searchable by name, number or manor.
  Click one to insert it into the seed editor. A search with
  no matches says so (Esc clears it).
- **Flow Canvas** (center) — your seed drawn as a chain of
  Dell cards, live as you type. The drawing is the engine's
  own parse (`/api/parse` → `form.mandell.seed.parse_seed`):
  real flow operators, arguments and labels, and if a seed
  does not parse, the canvas shows the parser's reason
  instead of a guessed chain. After a run, cards are painted
  from the run's real per-atom receipts (ok / failed /
  skipped with its reason) and a verdict chip summarises the
  chain (OK / PARTIAL / FAILED). Runs that carry no per-atom
  receipts leave the canvas neutral — outcomes are never
  inferred. Click a card to inspect its Dell.
- **Seed Editor** — write Mandell seeds; Ctrl+Enter runs.
- **Examples** — the dropdown over the editor loads one of
  14 shipped example seeds, from a single Create to full
  Create → Nurture → Show arcs. Every shipped example is
  execution-verified by the GUI test suite.
- **Inspector** (right) — the selected Dell's registry entry,
  or the full receipt of your last run.
- **Store** (right) — the program's live key/value store,
  with a type tag per value (string / number / boolean /
  list / object / null) and expand/collapse for long values.
- **Growth** tab — the owner's growth field through the
  canonical lens, grouped by stage in order (seed → sprout
  → stem → branch → leaf → fruit). Plants whose identity the
  lens cannot prove are grouped last under "NO STAGE CLAIM"
  — the Studio never invents a stage.
- **Console** tab — the raw session log.
- **Receipts** (bottom) — every run this session, newest
  first, with honest ok / failed / skipped verdicts.

## Keyboard shortcuts

- **Ctrl+Enter** — run the seed in the editor.
- **/** — jump to the rack search (when you are not already
  typing in a field).
- **Esc** — clear the rack search, the Dell selection and
  focus. Esc never touches your seed text.

## Honesty notes

- A Dell that did not run is shown as **skipped** with the
  engine's own reason (for example, a reserved Dell number) —
  never as if it had executed.
- Empty states say what is empty and what to try next: an
  empty store suggests a first `Set`, an empty growth field
  explains that growth appears as ideas are planted, and if
  the server cannot be reached the transport bar shows the
  connection error instead of a silent blank page.
- Switching owners switches the whole program: each owner
  has their own store, history and growth field, and nothing
  leaks between them.

## Testing

The Studio API has a regression suite that drives the real
server over HTTP — assets, registry fidelity against the
canonical Dell registry, parse refusals, store round-trips,
skipped-Dell honesty, every shipped example, growth-lens
fidelity, owner isolation and error states:

```
python3 -m form.gui_api_test     # standalone, 26 checks
python3 -m form.regress          # includes form.gui_api_test:smoke
```
