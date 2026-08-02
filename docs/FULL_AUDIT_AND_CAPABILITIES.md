# DellMatrix / Mandell — Full Audit · Report · Capabilities

Date: 2026-08-01  
Repo: DellMatrix (main)  
Authority companions: START_HERE · AUDIT_AND_NEXT_50 · RESIDUAL_COMPLETE · LIVE_INDEX · CORE_SCOPE · DELL_RUNTIME · MODE_LUPE

---

# Part 1 — Full Audit Report

## 1.1 Verdict

| Axis | Grade | Notes |
|------|-------|-------|
| Core runtime | **Strong** | Program + REPL + persist v7 runnable offline |
| Mandell Origin | **Strong** | Floor locked · seeds · Dells 00–50 dense |
| Controlled growth | **Strong** | RingedGrowth only · Nursery quarantine |
| Session unity | **Strong** | Lattice bound into Program · history · avatar |
| Average-user path | **Good** | START_HERE · accept · English door |
| Perception | **Good** | cube/sphere/core/flower · lattice · chord · shell |
| Polyglot | **Partial** | ES/FR live · more on request |
| Docs hygiene | **Good** | LIVE_INDEX · LEGACY · residual closed |
| Dual-era / side | **Contained** | src/preform LEGACY · trading/llm SIDE |
| Residual queue | **Empty** | RESIDUAL_COMPLETE |

**Overall:** Origin path is **stable for daily offline use**. Worldwide bridge language remains a horizon goal, not a defect in the current program.

## 1.2 Goal alignment

| Origin goal | Status |
|-------------|--------|
| Mandell as Origin | **Met** |
| Practical man ↔ computer | **Met** |
| Controlled growth | **Met** |
| Average-user daily use | **Good / partial→good** |
| Worldwide bridge language | **Not yet** (honest) |

## 1.3 Architecture (live)

```
launch.py / form.repl
        │
        ▼
   Program (form/open.py)     ← single session object
        │
        ├── DellMatrix (snaps / matrix core)
        ├── BlankCube + Plane (live ideas)
        ├── Nursery + RingedGrowth (proposals only)
        ├── HarmonicLattice (H/V/F + perception)
        ├── Avatar + Face
        ├── DuoBeta rings ledger
        ├── Enhance / Ambient / Sandbox gates
        ├── history[] (seed-shaped via note_seed)
        └── persist v7 (save/load)
                │
                ▼
        visual HTML panel (offline)
```

**Laws**

1. Floor locked: Alpha · Delta · Omega · Omni  
2. Growth never auto-writes the live matrix (Nursery only)  
3. RingedGrowth is the sole public growth entrypoint  
4. Mandell seeds are the structured surface; English is the door  
5. Origin acceptance is offline — no network, no llm, no trading required  

## 1.4 What is solid

- Form front door (`open.py` + `repl.py`)
- Floor + Dell registry 00–50 + dense executor behaviors
- Session v7: matrix · avatar · nursery · lattice · history
- place() lands ideas on H/V/F lattice cells
- Perception forms + lattice/chord/shell/lineage commands
- rank / macro / distill / replay English-first handlers
- Offline acceptance path (`form/accept.py`)
- Phrase hit-rate gate ≥ 0.90 + ES/FR polyglot smoke
- Honesty gates in START_HERE
- Lupe / bare-NBD efficiency law (steady X=5)
- CORE_SCOPE + LEGACY + SIDE package READMEs
- Form smoke CI (`.github/workflows/form-smoke.yml`)

## 1.5 What is partial / horizon

- Polyglot beyond ES/FR (by design: on request only)
- Worldwide bridge language claim (explicitly not claimed)
- `preform/` files may still exist on disk (LEGACY stamp closed residual; not authority)
- Some Dells are “usable dense” not research-deep; further polish is on-demand

## 1.6 Risk register

| Risk | Mitigation |
|------|------------|
| Dual-era confusion (src/preform) | LEGACY.md · LIVE_INDEX · START_HERE honesty |
| Side packages pulled into core | CORE_SCOPE · trading/llm README SIDE locks |
| Growth mutating live plane | Nursery quarantine · RingedGrowth law |
| Overclaiming Mandell status | Honesty gates · AUDIT non-goals |
| CI depending on network AI | form-smoke offline env |

## 1.7 Residual status

**Empty.** See `docs/RESIDUAL_COMPLETE.md`.

---

# Part 2 — Program Explanation (what it is)

## 2.1 One sentence

**Mandell** is a structured bridge language (operators + flow).  
**DellMatrix** is the offline host program that runs Mandell so a person can create, grow, confirm, perceive, save, and show ideas without needing an AI service.

## 2.2 Why it exists

- Give humans and machines a shared operator surface (Dells 00–50)
- Keep growth **controlled** (proposals in Nursery, not silent live mutation)
- Keep the core **offline** and local
- Make English the friendly door and Mandell the precise spine
- Separate Origin (language + matrix) from side experiments (trading, llm)

## 2.3 Session model

One `Program` instance owns:

| Piece | Role |
|-------|------|
| Plane / Cube | Live ideas you have confirmed |
| Nursery | Proposed ideas from growth (pending) |
| Lattice | Spatial / harmonic placement (H/V/F) |
| Perception | How you *see* the lattice (cube/sphere/core/flower) |
| Avatar | Body posture + face expression in-session |
| History | Seed-shaped action log for macro/replay |
| DuoBeta rings | Generation ledger (structural rings) |
| Gates | Enhance / sandbox / ambient controls |

Save/load (v7) carries matrix + avatar + nursery + lattice + history together.

## 2.4 Growth law (critical)

```
grow  →  proposals only (Nursery)
confirm  →  proposal becomes live on the plane + lattice
reject  →  proposal dropped
```

Nothing “evolves the live world” without an explicit confirm.

## 2.5 Language law

| Layer | Example |
|-------|---------|
| English door | `create an idea called business` |
| Mandell seed | `08[Create] > 15[Map] :: business` |
| Polyglot door | `es crea una idea llamada prueba` |

English and ES/FR map into the same Dell executor path.

---

# Part 3 — Capabilities Page by Page (step by step)

## Page 0 — Launch

**How**

```bash
python launch.py
# or
python -m form.repl
```

Windows: `Launch DellMatrix.bat`  
Mac: `Launch DellMatrix.command`

**What you get:** interactive REPL bound to one Program session.

---

## Page 1 — Create (first idea)

**English**

```
create an idea called business
```

**Mandell**

```
08[Create] > 15[Map] :: business
```

**What happens**
1. Idea unit placed on the live plane
2. Cell written on HarmonicLattice (H/V/F)
3. History notes `08[Create] :: business`

**Capability:** instantiate structured content under Floor law.

---

## Page 2 — Grow (controlled)

```
grow ideas 2
```

or

```
13[Loop] :: 2
06[Cycle] :: 2
```

**What happens**
1. RingedGrowth runs N cycles
2. New/evolved **proposals** land in Nursery only
3. Live plane is unchanged until confirm

**Capability:** controlled expansion without silent mutation.

---

## Page 3 — Nursery (proposals)

```
proposals
rank
```

**What happens**
- `proposals` lists pending cards
- `rank` sorts by affinity (Dell 46)

**Confirm / reject**

```
confirm <id>
confirm all
reject <id>
reject all
```

**Capability:** human gate between proposal and live reality.

---

## Page 4 — Perceive (forms)

```
cube
sphere
core
flower
lattice
chord 0 0
shell 0
```

**What happens**
- Perception form switches (visual metaphor for structure)
- `lattice` shows ASCII + status
- `chord` shows neighborhood
- `shell` shows cells on a radial shell

**Capability:** multiple views of the same underlying lattice.

---

## Page 5 — Avatar (body + face)

```
walk
run
stop
turn left
turn right
sit down
stand up
smile
```

**Mandell examples**

```
19[Drive] :: walk
04[Transform] :: left
05[Tone] :: joy
```

**Capability:** same session can hold idea-structure and an embodied cursor/persona.

---

## Page 6 — History tools (macro / replay / distill)

```
macro 5
replay 3
distill business crm workflow
```

| Command | Dell | Effect |
|---------|------|--------|
| macro | 48 | Pack last N history entries into a macro seed |
| replay | 48/path | Re-exec seed-shaped history |
| distill | 38 | Compress words into a short idea |

**Capability:** session becomes replayable and compressible, not only interactive.

---

## Page 7 — Gates (enhance / sandbox / temp)

```
enhance on
pulse
enhance off
sandbox on
sandbox off
```

**Mandell**

```
25[Pulse]
26[Temp] :: hot
23[Lock]
24[Unlock]
16[Decay] :: 0.8
```

**Capability:** intensity and isolation controls without leaving Origin path.

---

## Page 8 — Inspect / safety / schema

```
status
```

**Mandell**

```
11[Architect]
12[Test]
18[Mirror]
31[Simulate]
39[Schema]
40[TokenCount]
41[Sanitize] :: password=demo
43[Fallback]
49[Profile]
03[Logic]
```

**Capability:** inspect structure, dry-run, validate shape, redact secrets, show safe path.

---

## Page 9 — Persist (save / load / checkpoint)

```
save
load
```

**Mandell**

```
10[Keep]
27[Checkpoint]
28[Rollback]
```

**v7 payload includes:** plane ideas · nursery · lattice + perception · avatar · history

**Capability:** full session continuity offline.

---

## Page 10 — Visual panel

```
visual
```

or

```
09[Show] :: visual
47[Embed]
```

**What happens**
Writes offline HTML panel (`DellMatrix_UI.html` path reported by the command) with form skin, ranked nursery, avatar, scores.

**Capability:** eyes-on structure without a server.

---

## Page 11 — Bridge language

```
mandell create an idea called test
english 08[Create] > 15[Map] :: test
es crea una idea llamada prueba
fr sphère
lang list
```

**Capability:** multi-door entry into the same Dell layer (EN + ES + FR now).

---

## Page 12 — Acceptance path (proof the core is alive)

Offline, no AI:

```
create → grow → confirm → sphere → save → load → visual
```

If this loop completes, Origin is considered alive.

Automated helper: `form/accept.py` (and CI form-smoke).

---

## Page 13 — Full Dell operator map (00–50)

See `form/mandell/DELL_RUNTIME.md` for the complete dense table.

Highlights by family:

| Family | Dells | Use |
|--------|-------|-----|
| Origin / id | 00–05 | start, persona, logic, transform, tone |
| Make / show / keep | 06–15 | cycle, create, show, map, loop |
| Parallel / compare | 16–22 | decay, shadow, mirror, split |
| Control | 23–34 | lock, pulse, temp, checkpoint, resume, stamp |
| Shape / measure | 35–41 | discover, inject, stream, distill, schema, tokens, sanitize |
| Recover / bridge | 42–45 | retry, fallback, bridge, translate |
| Rank / pack / real | 46–50 | rank, embed, macro, profile, manifest |

---

## Page 14 — What is NOT core

| Path | Status |
|------|--------|
| `form/trading/` | SIDE — sister tools |
| `form/llm/` | SIDE — local model experiments |
| `src/` | LEGACY dual-era JS |
| `preform/` | LEGACY historical |

Origin must not require these for acceptance.

---

## Page 15 — Operating modes (meta)

**Lupe / NBD law** (`form/MODE_LUPE.md`)

- Bare `NBD` computes optimal batch size via efficiency function, then executes that many next-best directives
- Steady default **X = 5**
- Every Lupe step must touch real repo surfaces and push

This is process law for development of the system, not a user-facing idea command.

---

# Part 4 — Step-by-step first session (recommended)

1. Launch: `python launch.py`
2. `create an idea called business`
3. `grow ideas 2`
4. `proposals` then `rank`
5. `confirm all` (or confirm chosen ids)
6. `sphere` then `lattice`
7. `walk` · `smile` (optional avatar)
8. `macro 5`
9. `save`
10. `visual`
11. Quit / relaunch · `load` · confirm lattice and ideas returned

That is the full Origin heartbeat.

---

# Part 5 — Honesty (required reading)

- Voynich references are **structural / inspirational**, not a decode claim
- Orbit / reality-loop language is **metaphor** for controlled growth
- Mandell is a **practical bridge under construction**, not a finished worldwide standard
- Growth never auto-writes the live matrix
- Side packages and LEGACY paths are not the Origin narrative

---

# Part 6 — Audit conclusion

DellMatrix Form is a coherent offline Mandell host:

- unified session object
- controlled growth
- dense Dell runtime
- English + ES/FR doors
- persist v7
- visual offline panel
- residual hygiene closed

**Ready for daily Origin use.**  
**Not claiming worldwide bridge completion.**

Next work should come from **named surfaces** or **reported friction**, not from an open residual queue.
