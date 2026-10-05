# DellMatrix

**An offline idea environment with a structured language for working with thoughts.**

DellMatrix lets you create ideas, grow them into proposals, confirm the ones worth keeping, inspect how they relate, and save everything to disk — all through plain English commands in a terminal, with no network required.

> **Scope honesty:** This README describes what the code at the reviewed production SHA actually does, based on executed walkthroughs. Section 2 lists exactly what is working, partial, in repair, or planned. Nothing here claims more than the evidence supports. Full source/evidence map: [docs/README_EVIDENCE_MAP.md](docs/README_EVIDENCE_MAP.md).

---

## 1. What DellMatrix Is

**Mandell** is a structured language of operators ("Dells"), flow, and math/nature patterns. It is designed to be readable by people and executable by machines — a bridge language for human-computer collaboration.

**DellMatrix** is the host environment that runs Mandell. It provides:

- **An idea workspace** — create ideas, give them words, detail, and goals
- **A nursery** — grow ideas into proposals, review them, confirm or reject
- **A plane** — confirmed ideas become visible "units" you can inspect spatially
- **Persistence** — save your work to disk, reload it later, recover from crashes
- **Learning hooks** — DuoBeta observation and policy-gated learning
- **Visual export** — generate an offline HTML view of your idea space

**Present runtime vs. planned vision:** Today DellMatrix is a working terminal-based idea environment (see §2). The long-term vision includes nested projects, preserved history across sessions, interchangeable perspectives, and richer visual/UX layers — those are labeled PLANNED in §2 and §7, not described as implemented.

---

## 2. Status

**Production main:** `1d5b6c7` (2026-10-05, post PR #77/#78 merges).
**Phase-5 candidate:** PR #79 (branch `phase-5-nursery-growth`, NOT MERGED).

All §2 claims below were verified on production main `1d5b6c7` unless
labeled otherwise. Walkthroughs originally executed on `f3c9007`
(2026-10-04) are retained as dated historical evidence where noted.
Phase-5 behaviors (§6.5) are candidate-only until PR #79 merges.

| Area | Status | Evidence |
|------|--------|----------|
| REPL launch (`python launch.py`, `python3 -m form.repl`) | **WORKING / VERIFIED** | Launched, `you>` prompt, EOF exits cleanly |
| Create idea (`create an idea called X`) | **WORKING / VERIFIED** | Idea created with coaching on strength/detail/goals |
| Grow ideas (`grow ideas N`) | **WORKING / VERIFIED** | Proposals generated in nursery |
| Review proposals (`proposals`) | **WORKING / VERIFIED** | Lists pending proposals with IDs |
| Confirm (`confirm <id>`, `confirm all`) | **WORKING / VERIFIED** | Proposal confirmed, Idea placed on plane |
| Inspect (`look`, `page`, `rank`) | **WORKING / VERIFIED** | Affinity-ordered display, lineage shown |
| Shapes (`sphere`, `lattice`) | **WORKING / VERIFIED** | Skin/form change, grid render |
| Save / reload (`save`, `--load`) | **WORKING / VERIFIED** | Files written, state survives restart |
| Visual export (`visual`) | **WORKING / VERIFIED** | Offline HTML file generated (in-browser rendering untested) |
| Tutorial (`tutorial`) | **WORKING / VERIFIED** | Walks the acceptance path |
| Help (`help`, 9 categories) | **WORKING / VERIFIED** | create, knowledge, learn, explain, save, recover, look, dell, system |
| DuoBeta learn (`learn propose/inspect/gate/ledger`) | **WORKING / VERIFIED** | Real policy gating within session |
| Python API (`open_program`, `confirm_proposal`, `persist_rest`, `supersede_proposal`) | **WORKING / VERIFIED** | Direct API calls tested |
| Offline operation | **WORKING / VERIFIED** | No network calls in tested paths; stdlib-only core deps |
| Resonance/harmony scoring | **PARTIAL** | Scoring machinery real (`resonance_rank`, affinity); no direct user command |
| DuoBeta cross-session learning | **PARTIAL** | Works within session; cross-process persistence of staged proposals not observed |
| REPL `supersede` command | **WORKING / VERIFIED** | `supersede idea <id> with <words>` works with genuine confirmed ID; fails gracefully on unknown/non-confirmed ID |
| `lineage` by label | **PARTIAL** | Works by proposal ID; label lookup not implemented (use ID from `proposals`) |
| Confirmation atomicity | **WORKING / VERIFIED** | Intent-journal recovery merged via [PR #77](https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/77) (2026-10-05); crash converges to complete OLD or NEW state |
| Nested projects / perspectives | **PLANNED** | Not implemented |
| Rich visual UX | **PLANNED** | HTML export exists; interactive UI planned |
| Windows/Mac launchers | **UNVERIFIED** | `Launch DellMatrix.bat` / `.command` exist but not executed |
| Spanish/French commands | **UNVERIFIED** | Claimed in old docs; not executed this session |

---

## 3. How It Works

### (a) From English input to executed result

```mermaid
flowchart TD
    A["You type English\nat the you> prompt"] --> B["REPL dispatcher\n(form/repl.py)"]
    B --> C{"Command type?"}
    C -->|"Read-only: help, look,\nproposals, outcomes"| D["Direct handler"]
    C -->|"Learn: learn ..."| E["DuoBeta policy gate"]
    C -->|"Mandell flow: > or :"| F["Mandell executor"]
    C -->|"Other English"| G["translate() → intent"]
    G --> H["_execute_intent"]
    D --> I["Program state"]
    E --> I
    F --> I
    H --> I
    I --> J["Render result\nto terminal"]
    I --> K["Optional: save\nto disk"]

    style A fill:#e1f5e1
    style I fill:#fff3e0
```

**Autonomy note:** Most commands require you to type them, but DellMatrix has autonomous paths with different defaults:
- `auto_growth.py`: The `AutoGrowth` dataclass defaults to `auto=True, internet=True`. When instantiated with defaults, it can automatically propose and confirm ideas based on quality thresholds (`_should_auto_confirm` checks `floor_accept`, `verita_score`, `combined` score, and grade). It calls `p.confirm_proposal()` without per-proposal user input. Callers can set `auto=False` to disable.
- REPL `auto confirm on`: The `Program.auto_confirm_grow` attribute defaults to `False`. When the user types `auto confirm on`, every subsequent `grow` command automatically confirms all nursery proposals.
- Default posture: REPL interaction is human-controlled by default; the `AutoGrowth` class is opt-out (defaults on) when instantiated directly.

### (b) Proposal lifecycle and persistence

```mermaid
flowchart TD
    A["Idea created\n(create ...)"] --> B["Proposal in nursery\n(status: pending)"]
    B --> C{"Review"}
    C -->|"confirm <id>"| D["Proposal confirmed\nIdea placed on plane"]
    C -->|"reject"| E["Proposal rejected"]
    D --> F["save"]
    F --> G["Disk: nursery + program\nJSON files"]
    G --> H["Restart"]
    H --> I["Reload: state restored\nfrom disk files"]

    style D fill:#e1f5e1
    style I fill:#fff3e0
```

The nursery tracks proposal status (`pending` → `confirmed`). The plane holds confirmed Ideas as spatial units. On `save`, both are written to disk. On restart, `load` restores state from the disk files.

**Crash recovery (MERGED via PR #77, 2026-10-05):** If the process crashes mid-confirmation, the intent-journal recovery mechanism converges to either the complete OLD state or the complete NEW state (not necessarily the exact pre-crash state). This is production behavior on main `1d5b6c7`.

---

## 4. Quick Start

**Requirements:** Python 3.10+, no third-party packages for the core loop (see `requirements.txt`). Tested on Linux; Windows/Mac launchers exist but are unverified.

**Docs:** [INSTALL](docs/INSTALL.md) · [START_HERE](docs/START_HERE.md) · [TUTORIAL](docs/TUTORIAL.md)

```bash
# Clone and launch
git clone https://github.com/spiritualityhandbook-netizen/DellMatrix
cd DellMatrix
python launch.py YourName
```

You'll see a banner and a `you>` prompt. Type `tutorial` for a guided walkthrough, or `help` for command categories.

**Offline:** The core loop (create → grow → confirm → inspect → save) makes no network calls. Optional features under `form/llm` may need extras; they are not part of the core loop.

**Generated output:** `save` writes JSON files under `form/state/`. `visual` generates `DellMatrix_UI.html` in the repo root.

---

## 5. Capabilities

| Action | User entrypoint | Observable result | Implementation source | Test |
|--------|----------------|-------------------|----------------------|------|
| Create idea | `create an idea called <name>` | Idea stored; coaching on strength/detail/goals | `form/repl.py`, `form/dell_matrix/` | Walkthrough verified |
| Grow proposals | `grow ideas N` | Proposals in nursery (count varies; observed 1 from `grow ideas 2`) | Dell 13 via `form/grow.py` | Walkthrough verified |
| List proposals | `proposals` | Pending proposals with IDs | `form/dell_matrix/nursery.py` | Walkthrough verified |
| Confirm | `confirm <id>` / `confirm all` | Proposal confirmed; Idea on plane | `form/dell_matrix/confirm_lineage.py` | Walkthrough verified |
| Inspect | `look`, `page`, `rank` | Affinity-ordered idea display | `form/dell_matrix/first_person.py` | Walkthrough verified |
| Lineage | `lineage <proposal-id>` | Ancestry/derivation shown | `form/dell_matrix/lineage.py` | Walkthrough verified (ID only) |
| Shapes | `sphere`, `lattice` | Visual form change + grid | `form/dell_matrix/` spatial | Walkthrough verified |
| Save / reload | `save`, `python3 -m form.repl --load` | JSON files; state survives restart | `form/persist.py`, `form/persist_rest.py` | Walkthrough verified |
| Visual export | `visual` | `DellMatrix_UI.html` generated | REPL `visual` handler | File verified; rendering untested |
| Tutorial | `tutorial` | Guided acceptance path | `form/repl.py` | Walkthrough verified |
| DuoBeta learn | `learn propose/inspect/gate/ledger` | Policy-gated learning within session | `form/duobeta/` | Walkthrough verified |
| Supersede (API) | `supersede_proposal(p, old_id, ...)` | New revision; old marked superseded | `form/mandell/supersession.py` | API and REPL both verified with genuine ID |
| Outcomes | `outcomes` | Honest empty ("No outcomes recorded") or list | `form/repl.py` | Walkthrough verified |

> A module's existence is not proof of usable integration. Every row above was verified by actually running the command or API call. Historical walkthroughs (2026-10-04) ran on SHA `f3c9007`; current production is main `1d5b6c7`.

---

## 6. Walkthroughs

> **Historical evidence (2026-10-04):** Each walkthrough below was executed on SHA `f3c9007` with a temporary owner; state was cleaned up afterward. REPL sessions used piped stdin. These remain valid as historical evidence of the production behavior at that SHA; they were not all re-executed on the Phase-5 candidate (PR #79, unmerged).

### 6.1 Create, store, reload

```
you> create an idea called my first thought
# → Idea created. Coaching: add detail: and goals: for strength.

you> save
# → State written to form/state/

# Restart: python3 -m form.repl --owner <name> --load
# → Idea present after reload. VERIFIED.
```

### 6.2 Propose, review, confirm

```
you> grow ideas 3
# → 3 proposals in nursery.

you> proposals
# → Lists: <id1>, <id2>, <id3> (copy an ID)

you> confirm <id1>
# → Proposal confirmed; Idea placed on plane.

you> look
# → Confirmed Idea visible. VERIFIED.
```

**How to obtain proposal IDs:** Run `proposals` first; the output lists IDs. Pass one to `confirm`. `confirm all` confirms everything pending.

### 6.3 Inspect relationships

```
you> lineage <proposal-id>
# → Shows derivation/ancestry for that proposal. VERIFIED (ID required;
#    label lookup does not work — known gap).

you> rank
# → Ideas ordered by affinity. VERIFIED.
```

### 6.4 Resonance / harmony candidates

The scoring machinery (`resonance_rank`, affinity) is real and drives `rank`/`page` ordering. There is **no direct user command** for resonance queries — this is a PARTIAL feature. The Phase-3 proof files (`form/mandell/p3_r3*_proof.py`) are tests, not user features.

```python
# Python API only (not exposed in REPL) - complete executable example:
from form.dell_matrix.first_person import resonance_rank
nodes = [
    {"id": "idea1", "x": 1.0, "y": 2.0, "f": 0.0},
    {"id": "idea2", "x": 5.0, "y": 5.0, "f": 1.0},
]
ranked = resonance_rank(nodes, center=(0, 0, 0), scores={"idea1": 0.9, "idea2": 0.5})
# → Returns scored candidates ordered by resonance. idea1 ranks higher (closer + higher score).
assert ranked[0]["id"] == "idea1"
```

### 6.5 Supersession and history

Supersession (replacing a confirmed idea with a newer revision) works via both the Python API and the REPL command (with a genuine confirmed proposal ID):

> **Phase-5 candidate:** supersession requires explicit authorization (human opt-in or approval). This example was re-executed on the candidate head.

```python
# VERIFIED working on Phase-5 candidate (Python API) - complete end-to-end:
from form.open import open_program
from form.mandell.supersession import supersede_proposal
p = open_program("Owner")
p.acceptance_policy.grant_opt_in("Owner", scope="supersede")  # Phase-5: explicit authorization
# 1. Create and confirm the predecessor
pr = p.nursery.add('Original Idea', words='initial content')
ctx = p.make_review_context(pr.id, "Owner")
p.confirm_proposal(pr.id, _producer="Owner", _review_context=ctx)
old_id = pr.id
# 2. Supersede it (returns a receipt dict)
receipt = supersede_proposal(p, old_id, words="revised content", _producer="Owner")
assert receipt["ok"] is True
assert receipt["old_id"] == old_id
assert receipt["revision_number"] == 2
new_id = receipt["new_id"]
# → Old marked superseded; new revision active; history preserved.
```

```
you> supersede idea <id> with <words>
# → VERIFIED working with genuine confirmed ID. Fails gracefully on
#   unknown/non-confirmed ID (not a broken command).
```

*Historical note (2026-10-04): An earlier draft labeled the REPL command BROKEN based on a test with an unconfirmed ID. Retesting with a genuine confirmed proposal ID shows it works.*

History: `history` shows recent entries. Crash recovery uses intent journals to distinguish interrupted operations from historical records (under active repair — see §2).

### 6.6 Visual output

```
you> visual
# → Generates DellMatrix_UI.html (offline, no network). VERIFIED file created.
#    In-browser rendering not tested this session.
```

---

## 6.5 Phase-5: Acceptance Authorization and Lifecycle Coherence

Phase 5 hardened the acceptance boundary and lifecycle interpretation.
All claims verified by executed tests (see evidence map).

**Acceptance policy** (`form/dell_matrix/acceptance_policy.py`):
- Session IDs are collision-resistant (uuid4).
- Acceptance data uses canonical JSON + SHA-256 (identity, owner, content,
  parents, goals, revision metadata). No delimiter concatenation.
- Approval issuance is recorded; a matching dict alone is not evidence.
  Forged, stale, cross-session, and revoked approvals are denied.
- Revocation is supported; retry means re-issuance after re-review.
- Commit-boundary revalidation: live permission and data hash checked
  immediately before the protected mutation.
- Supersession binds predecessor version + successor payload. The
  successor's confirmation is derived via a constrained, recorded
  relationship (not a general bypass); revoked parents invalidate
  unfinished children.

**Lifecycle** (`form/dell_matrix/canonical_lifecycle.py`):
- Acceptance, revision, participation, and projection are distinct.
- Revision validated first; faded presence never masks malformed data.
- Malformed records excluded in all contexts with explicit reasons.
- Fade/unfade preserves identity, content, acceptance, and revision links.
- Unfade/pin cannot reactivate superseded truth.

**Learning** (DuoBeta):
- Influence OFF restores baseline in all consumers.
- Learning cannot manufacture evidence, resurrect excluded candidates,
  or change accepted truth.

---

## 7. Vision (Planned)

The long-term vision — **not yet implemented** — includes:

- **Nested ideas and projects** — ideas containing sub-ideas, projects grouping related work
- **Preserved history** — full revision chains visible and navigable across sessions
- **Interchangeable perspectives** — view the same idea space through different lenses (spatial, temporal, affinity-based)
- **Candidate connections** — the system suggests related ideas; you accept or reject each one
- **Human-controlled acceptance** — nothing is confirmed, superseded, or learned without your explicit approval

Diagrams or mock examples of the above are conceptual only. Roadmap phases beyond the current terminal-based environment are PLANNED. The current system (§2, §6) is the honest baseline.

---

## 8. Architecture and Source Guide

| Path | Role |
|------|------|
| `form/` | **Live runtime** (Python). All imports resolve here. This is the only active code. |
| `form/repl.py` | REPL front door: `run()` starts the `you>` loop; `_dispatch_public_line` routes commands |
| `form/open.py` | `Program` class and `open_program()` — the central state object |
| `form/mandell/` | Mandell language: `translate.py`, executor, checkpoint/recovery, supersession |
| `form/dell_matrix/` | Dells, nursery, plane, spatial, lineage, persistence helpers |
| `form/duobeta/` | DuoBeta learning: observation, policy gates, ledger |
| `form/persist.py`, `form/persist_rest.py` | Disk persistence (JSON under `form/state/`) |
| `src/` | **Frozen legacy** (JavaScript). Per `src/README.md`: "Do not extend." Only historical interest. |
| `preform/` | Historical notes/docs. Zero imports from `form/`. |
| `docs/` | Documentation (large; currency varies — prefer this README for current truth) |
| `launch.py` | Root launcher → `form.repl.run()` |

**Registry note:** The canonical operator registry is `form/mandell/registry.py` — the "True Dell registry" with numbered operators (CORE_I 00-50, CORE_II 51-99). English commands route through `form/repl.py::_dispatch_public_line` → `form/mandell/translate.py::translate()` → `_execute_intent`. `form/dell_matrix/actions_registry.py` provides UI action lists (`actions_flat`, `actions_for_mode`) for visual modes, not the language operator definitions. The `help` command lists 9 categories: `create`, `knowledge`, `learn`, `explain`, `save`, `recover`, `look`, `dell`, `system`.

---

## 9. Limitations, Tests, Contributing, Glossary

### Honest limitations
- `lineage` works by proposal ID; label lookup is not implemented.
- Resonance/harmony has scoring but no direct user command.
- DuoBeta learning is session-scoped; cross-session persistence unverified.
- Windows/Mac launchers and Spanish/French commands are unverified.
- Confirmation crash recovery is production behavior (merged via PR #77).
- "User-ready" is not claimed. See §2 for the scoped status table.

### Phase-5 candidate (PR #79, unmerged)
Phase-5 acceptance authorization, lifecycle coherence, and learning bounds (§6.5) are implemented on branch `phase-5-nursery-growth` ([PR #79](https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/79), NOT MERGED, NOT CERTIFIED). The main branch described by this README does **not** include Phase-5 changes.

### Test commands
```bash
python3 -m form.regress --twice        # full suite, forward, twice
python3 -m form.regress --order rev    # full suite, reverse order
```

**Phase-5 candidate tests (not on production main):** The following modules exist only on the unmerged Phase-5 branch ([PR #79](https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/79)). They are not runnable on production `1d5b6c7`:
```bash
# On Phase-5 branch checkout only:
python3 -m form.mandell.wo51_adversarial_test  # acceptance adversarial
python3 -m form.mandell.wo52_coherence_test   # lifecycle coherence
python3 -m form.mandell.d20_reference_test    # Delta-20 reference model
```

### Contributing
Issues and PRs are welcome. Please verify claims against the code before documenting them — see this README's method (§1, evidence map). Do not modify `src/` (frozen).

### Glossary
- **Dell** — a Mandell operator (a structured action like Create, Map, Grow).
- **Mandell** — the bridge language: structured operations readable by people, executable by machines.
- **Nursery** — where ideas grow into proposals awaiting review.
- **Plane** — the spatial surface where confirmed Ideas live as units.
- **Proposal** — a candidate idea in the nursery (`pending` → `confirmed`/`rejected`).
- **Supersession** — replacing a confirmed idea with a newer revision (old marked superseded, history preserved).
- **DuoBeta** — the learning subsystem: observation with policy-gated learning.
- **Checkpoint** — an atomic snapshot of program + nursery state (generation-based).
- **Intent journal** — a crash-recovery record distinguishing interrupted operations from history.
