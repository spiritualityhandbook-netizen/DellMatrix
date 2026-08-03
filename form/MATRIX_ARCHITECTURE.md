# Matrix Architecture — DellMatrix family

**DellMatrix = DEV matrix** (developer matrix).  
Blank matrices mirror DEV **capabilities**, never personal data.  
Visuals: prepare only — live real-time later; snapshot is not the target.

---

## Tiers

| Tier | Name | Role | Growth law |
|------|------|------|------------|
| **DEV** | DellMatrix | Developer source of truth · capabilities | Nursery + confirm |
| **Blank** | Blank matrix | Hand to others · same capabilities as DEV · empty of personal lore | Nursery + confirm |
| **Ace** | Dell Matrix Ace | Personal matrix (owner Ace) | Nursery + confirm |
| **Worldwide** | Worldwide matrix | Ideas for the world · develop here first | Nursery + confirm |
| **Main** | Main matrix | Accepts all matrices · full idea field | **Auto-evolve** (planned) |

### Naming

- “Dell Matrix” / “DEV matrix” = same thing = this repo’s Origin runtime.  
- Blank = capability clone, not a fork of personal sessions.  
- Ace / Worldwide = **profiles** (owner + state files), same `form/` code.  
- Main = special law (auto evolution) — see below.

---

## Capability inheritance

```text
DEV (DellMatrix) ──implements──► form/ runtime
        │
        ├── Blank pack / clean Program(owner=Friend)
        ├── Ace     Program(owner=Ace)     + personal state only
        ├── Worldwide Program(owner=Worldwide) + worldwide ideas only
        └── Main    (future) aggregates + daily auto-evolve
```

When DEV gains a capability (LatinMandell, detail+goals, lattice, …), **every** blank/Ace/Worldwide session that runs current `form/` already has it.  
Personal data (Ace customs, Ace ideas, Worldwide idea list) does **not** flow into Blank or into other people’s packs.

---

## Idea law (all Nursery-tier matrices)

An idea is not a label alone.

| Field | Required | Role |
|-------|----------|------|
| label | yes | Name |
| detail | yes (practical) | What the idea *is* |
| goals | yes (≥1) | What evolution must aim at |
| words | optional | Free notes / tags |

**Growth must bias toward goals** — not random mutation.  
Nursery still quarantines proposals until confirm (DEV / Blank / Ace / Worldwide).

---

## Main matrix law (planned — do not confuse with DEV)

| Rule | Main |
|------|------|
| Ingest | Accepts ideas/signals from connected matrices |
| Nursery | Not required for Main’s own silent evolve |
| Schedule | Once daily (morning) · may run as long as needed |
| Engine | Full matrix capabilities + NBD-style ranking |
| Stop | Only explicit stop |
| Push | Automatic into Main field (no manual “ship to Main”) |

**DEV does not become Main.** Controlled growth stays the default for human-facing matrices.

---

## True Lore Identifier

**Future goal** (Worldwide matrix first): deeper meanings of names, words, phrases, books, ideas, real-life lore — pattern literacy for people.  
May later ship as a loved program *from* Worldwide → DEV if useful.  
See `form/mandell/TRUE_LORE.md`.

---

## Visual

- Current HTML = offline snapshot (not the product vision).  
- Target = **live real-time** visual.  
- Work paused until foundation tiers + idea goals are solid.

---

## Profiles (how to run)

```bash
python launch.py              # DEV default owner Operator
python launch.py Ace          # Dell Matrix Ace (personal)
python launch.py Worldwide    # Worldwide ideas matrix
python launch.py Friend       # blank-style personal for handoff
```

Blank pack export remains: `python -m form.dell_matrix.blank_cube --give Friend --clean`

Authority: this file · `CORE_SCOPE.md` · `docs/AUDIT_MATRIX_TIERS.md`
