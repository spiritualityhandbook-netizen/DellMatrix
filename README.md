# DellMatrix

**Just talk to it.**

Form is the only front door.  
Floor locked: Alpha · Delta · Omega · Omni

---

## Start (average user)

```bash
python -m form.repl --owner Ace
```

Then type normal English:

```
create an idea called grocery list
grow ideas 2
walk forward
turn left
smile
how do I look
show me the matrix
visual
save
```

`visual` writes an offline HTML file you can open in any browser.

---

## What you can say

| You type | What happens |
|----------|--------------|
| create an idea called X | Places a new idea |
| grow ideas 3 | Grows the matrix |
| walk forward / turn left / sit down | Moves your Avatar |
| smile / calm / focus | Changes face expression |
| how do I look | Shows Avatar status |
| show me the matrix | Prints current state |
| visual | Opens visual workspace |
| enhance on / pulse | Activates growth energy |
| save | Saves your session |

---

## Structure

```
form/           ← THE SYSTEM
├── avatar/     Body + face + kaomoji
├── mandell/    Language + English translator
├── dell_matrix/ Matrix, visual, growth
├── open.py     One program object
└── repl.py     Front door (talk here)

src/            LEGACY — do not use
preform/        Planning docs only
```

---

## Goal

A non-developer can open it, talk in plain English, move an Avatar, place ideas, grow them, and see a visual workspace — without writing code.
