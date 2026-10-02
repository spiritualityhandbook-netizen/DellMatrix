# Put a blank matrix on her computer

## On your machine (prepare)

```bash
# from DellMatrix repo root
python -m form.give_blank --owner Sister --empty
```

That writes:
- `form/state/program_Sister.json` (blank save)
- pack file under state
- `form/state/START_Sister.txt` (her cheat sheet)

## Copy to her computer

Copy the whole **DellMatrix** folder (or clone the repo), including `form/`.

She needs **Python 3** installed.

## On her computer

```bash
cd path/to/DellMatrix
python -m form.repl --owner Sister --load
```

> **Note (2026-10-02, FCND-I/LE-19):** `form.smoke_all` was removed as a
> disconnected dead path. Smoke coverage is provided by the registered
> regression suite (`form/regress.py`) and CI.

If `--load` has no file yet, just:

```bash
python -m form.repl --owner Sister
```

Then:

```text
matrix> tutorial
matrix> place my1 MyFirstIdea what I care about
matrix> show
matrix> save
```

## Rules to tell her

- **Her name** in `--owner` keeps her files separate from yours
- enhance / sandbox / ambient stay **OFF** until she turns them on
- Her ideas stay on **her** plane

## Optional: same Wi‑Fi Main later

> **Correction (2026-10-02, FCND-I/LE-14):** The `network`, `net_push`,
> and `push_main` commands previously documented here do not exist.
> They have been removed. Do not use them.

Only after she’s comfortable, use whatever current sharing mechanism
the live system provides (see `matrix> help`).
