# Tutorial — DellMatrix (average user)

Offline. About 2 minutes.

---

## Start the program

See [`INSTALL.md`](INSTALL.md) if you have not opened it yet.

```bash
python launch.py
```

At the `you>` prompt type:

```
tutorial
```

(or `start`) — the program will walk you through the acceptance path.

---

## Manual path (same steps)

| Step | Type this | What you should see |
|------|-----------|---------------------|
| 1 | `create an idea called test` | Created idea: "test" |
| 2 | `grow ideas 2` | Ringed growth · Nursery pending |
| 3 | `proposals` | List of pending proposals |
| 4 | `confirm all` | Confirmed N proposal(s) |
| 5 | `sphere` | Form → sphere |
| 6 | `save` | Session saved · file path |
| 7 | `load` | Session loaded · render |
| 8 | `visual` | Path to HTML — open in browser offline |

That is the full acceptance path:

```
create → grow → confirm → sphere → save → load → visual
```

---

## Top commands

```
help          short list
help more     full list
status        where you are
lattice       structure view
rank          sort nursery
lang list     EN · LA · ES · FR
```

---

## Tips

- Growth never writes the live matrix until you **confirm**.
- `visual` is offline HTML — open the printed path in any browser.
- No internet, no API keys, no AI required for this path.
