# DellMatrix

**Just talk to it.**

---

## How to start (easiest)

### Windows
Double-click:

```
Launch DellMatrix.bat
```

### Mac
Double-click:

```
Launch DellMatrix.command
```
(If it asks for permission the first time, right-click → Open)

### Any system
```bash
python launch.py
```
or
```bash
python -m form.repl --owner Ace
```

---

## What to type

Just use normal English:

```
create an idea called grocery list
grow ideas 2
walk forward
turn left
sit down
smile
how do I look
show me
visual
save
```

The system replies in plain English, for example:

```
  Created idea: "grocery list"
  You walked forward 1 step(s). Now at (1, 0), facing N.
  (^_^)  You look joy.
```

---

## What it does

- Understands normal English
- Moves an Avatar (walk, turn, sit, expressions)
- Lets you create and grow ideas in a matrix
- Can show a visual workspace (offline HTML)
- Works offline

---

## Structure

```
form/           ← the actual program
launch.py       ← simple starter
Launch *.bat / *.command  ← double-click starters
src/            ← old system (ignore)
preform/        ← planning docs only
```
