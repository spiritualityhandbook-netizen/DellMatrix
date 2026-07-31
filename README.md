# DellMatrix

**Just talk to it.**

Voynich-inspired Ringed Growth · Nursery quarantine · Avatar · offline visual UI

---

## Start

**Windows:** double-click `Launch DellMatrix.bat`  
**Mac:** double-click `Launch DellMatrix.command`  
**Any:** `python launch.py`

---

## Everyday flow

```
create an idea called business
create an idea called music
grow ideas 2
proposals
confirm <id>
visual
save
```

After `visual`, open:

```
DellMatrix_UI.html
```

in the project folder (any browser, works offline).

---

## What the system does

| Feature | Behavior |
|---------|----------|
| English in | Normal phrases → actions |
| Ringed growth | Seed→Token→Body→Lens→Evolve (Voynich-inspired) |
| Nursery | New/evolved ideas quarantined until you confirm |
| Avatar | Walk, turn, sit, expressions |
| Visual UI | Buttons for all main options + matrix graph |
| Offline | Core + UI work without internet |

Nothing enters the live matrix until you `confirm`. Reject discards. Live ideas are never deleted by growth.

---

## Structure

```
form/                 ← the program
  avatar/             body + face
  mandell/            language + English translator
  dell_matrix/        matrix, nursery, ringed growth, visual
  duobeta/            generation + rings ledger
  open.py · repl.py   front door
Launch DellMatrix.*   double-click starters
launch.py
DellMatrix_UI.html    easy visual (written when you run visual)
src/                  legacy (ignore)
preform/              planning docs
```

Floor locked: Alpha · Delta · Omega · Omni
