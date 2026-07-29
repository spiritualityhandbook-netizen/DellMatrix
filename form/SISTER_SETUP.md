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
python -m form.smoke_all
python -m form.repl --owner Sister --load
```

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
- Optional later: `push_main` only shares tags, does not wipe her cube

## Optional: same Wi‑Fi Main later

Only after she’s comfortable:

```bash
# on one machine
python -m form.dell_matrix.network_main --serve --port 8765
```

```text
matrix> network http://THAT_IP:8765
matrix> net_push
```
