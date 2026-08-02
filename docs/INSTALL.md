# Install — DellMatrix (average user)

Offline. No account. No network required for the core loop.

---

## What you need

- **Python 3.10+** installed and on your PATH  
  Check: open a terminal and run `python --version` or `python3 --version`

If Python is missing:

- Windows: https://www.python.org/downloads/ (check “Add Python to PATH”)
- Mac: usually `python3` is available, or install from python.org / Homebrew
- Linux: `sudo apt install python3` (or your distro equivalent)

---

## Get the project

1. Download or clone this repository onto your computer.
2. Open the project folder (the one that contains `launch.py`).

---

## Start

**Windows** — double-click `Launch DellMatrix.bat`  
**Mac** — double-click `Launch DellMatrix.command` (if blocked: right-click → Open)  
**Any system** — in a terminal, from the project folder:

```bash
python launch.py
# or
python3 launch.py
```

Optional owner name:

```bash
python launch.py YourName
```

---

## First minute

When the program starts you will see a prompt like `you>`.

Type:

```
help
```

Then try:

```
create an idea called test
grow ideas 2
proposals
sphere
save
visual
```

Full walkthrough: [`docs/START_HERE.md`](START_HERE.md)

Acceptance path (offline, no AI):

```
create → grow → confirm → sphere → save → load → visual
```

---

## If it does not start

| Symptom | Fix |
|---------|-----|
| `python` not found | Install Python and ensure PATH; try `python3` |
| Window opens then closes | Run from a terminal so you can read the error |
| Import errors | Run from the project root (folder with `launch.py`) |

Core never needs internet, API keys, or extra packages for the acceptance path.

---

## Not core (ignore for first use)

- `preform/` · `src/` — LEGACY (historical only)
- `form/trading/` · `form/llm/` — SIDE (optional experiments)

Live path is **`form/`** only.
