# Q-S2R.4 — "Harmonic" seven-bearer naming audit: BOUNDED PLAN (records only)

Date: 2026-11-17. Circuit: Q-S2R.4 follow-on from PR #451.
Authority: Director Q-S2R answers on PR #451, comment 6946046074 —
Q-S2R.4 / DC-2: CONFIRM the seven-bearer scope, treating the seven as
distinct mechanisms, not one harmonic authority. Audit naming,
consumers and semantics per bearer; no automatic rename or semantic
merger. Deliver a bounded PLAN/records proposal for independent Uni
and Keeper review before any implementation.
This document is that plan. **It renames nothing, merges nothing,
and changes no code or ledger text.** Any rename, label change, or
ledger edit that the audit later recommends requires its own
Director ruling and its own circuit.

## Problem

Ledger R4-A6 originally recorded "harmonic" as naming three
mechanisms. The SYSTEM-002R verification (Append D, merged via
PR #451) extended the bearer list to seven on first-hand evidence:
four more mechanisms in current code carry the same word while
computing different things. The collision's harm is reader-facing:
a surface, report, or caller that says "harmonic" without saying
which bearer it means invites exactly the false unification R4-A6
exists to prevent — the word is not a concept. The audit this plan
bounds establishes, per bearer, what the mechanism actually does,
who actually consumes it, and what each public surface currently
calls it, so a later disposition (keep + label, qualify, or rename)
can be ruled per bearer on evidence rather than on the word.

## Grounding — all seven bearers re-verified at current main

Executed by Uni 2026-11-17 at main
`a05d27db7473258929cfab8c7aa1ecb3f106bda0` (fresh clone; static
definition + caller search, repo-wide). Every bearer from Append D
still exists at the cited location; no bearer has been renamed,
removed, or semantically merged since the 56b6d9c census.

| ID | Bearer | Location at a05d27db |
|---|---|---|
| H-1 | `HarmonicCube` (JS, 5-ring) | `src/core/harmonic_cube_5ring.js` (class `HarmonicCube`) |
| H-2 | `Form.CUBE` perception family | `form/dell_matrix/perception.py:27` (`Form.CUBE = "cube"`); related cube modes `form/dell_matrix/plane.py:50` (`Perspective.CUBE`), `:57` (`Skin.CUBE`) |
| H-3 | `_harmonic()` (EQ-RES-001) | `form/dell_matrix/ringed_growth.py:197` |
| H-4 | `harmonic_core.py` | `form/dell_matrix/harmonic_core.py` (`KeyLedger` :57, `pulse_status` :37) |
| H-5 | `HarmonicLattice` | `form/dell_matrix/harmonic_lattice.py:80` (class `HarmonicLattice`) |
| H-6 | `harmony_score` | `form/dell_matrix/harmony.py:96` |
| H-7 | `graph_coherence` in `graph_harmony.py` | `form/dell_matrix/graph_harmony.py:126` |

## Per-bearer audit entries (grounding summary; full audit per §Plan)

### H-1 — HarmonicCube (legacy JS)
- **Semantics:** a tiered memory system — five Map tiers
  (shem / gem / rememory / sub / plannedFog) with store/retrieve,
  promotion and fogging statistics. Its own header: "Just a tiered
  memory system with recursive feedback processing." Zero
  sphere/circle mathematics (ledger §8 Harmonic Cube row).
- **Consumers:** legacy JS line only — `src/mandell_kernel.js`
  imports `FiveRingSystem` from the same file's family;
  `src/compat/legacy_map.js` maps the name. No Python consumer.
  Frozen legacy; not on any live Python path.
- **Naming risk:** the compound "Harmonic Cube" collides with H-2's
  cube vocabulary while sharing no geometry with it.

### H-2 — Form.CUBE perception family
- **Semantics:** a perception/plane *mode*, not a quantity:
  `Form.CUBE` is one value of the perception-form enum (paired
  opposite `Form.SPHERE` at `perception.py:37-39`, default form at
  `:46`); `plane.py` carries `Perspective.CUBE` (cube-based grid
  rendering, `plane.py:348`) and `Skin.CUBE`. It names how a plane
  is read/rendered, never a score.
- **Consumers:** wide — `Form.CUBE` / `Skin.CUBE` /
  `Perspective.CUBE` are referenced across `form/` (perception,
  plane, harmonic_lattice, graph_view, sandbox/accept gates, and
  the D1 registry tests). This is the most load-bearing bearer:
  any rename here has the largest blast radius of the seven.
- **Naming risk:** Append D cites this bearer as "`Form.CUBE`
  perception (`perception.py:27`, `plane.py:50`)". The audit must
  first settle whether the bearer is the single enum value or the
  cube-mode family across the three enums (see Q-S2R.4.1) — the
  grounding above shows three distinct enum members share the
  token, in two modules.

### H-3 — `_harmonic()` (EQ-RES-001)
- **Semantics:** a token-set similarity: Jaccard overlap blended
  with a complementary-exclusive "tension" term,
  `(2·jac·(jac+tension)) / (2·jac + tension + eps)`, in [0,1].
  Its docstring self-discloses: "Jaccard-tension combiner (NOT
  musical harmony)… Name is historical; it is a token-set
  similarity, not a harmonic", and records the name is kept for
  caller stability by rule (GDP-001 Phase 3, 3.1.3).
- **Consumers:** exactly one production caller —
  `ringed_growth.py:349` inside `_affinity` (weight into the
  growth affinity pipeline); plus the invariants test
  (`equation_ledger_invariants_test.py:23,89-98`, EQ-RES-001
  bounds) and the P3 R3.1 affinity proof.
- **Naming risk:** low surface exposure (private name, one caller,
  honest docstring) but it is the bearer the ledger's EQ-RES-001
  entry names "Harmonic bridge combiner" — the ledger label, not
  the code, is the exposed surface.

### H-4 — `harmonic_core.py`
- **Semantics:** pulse-ratio constants (Subkey 4 : Core 1 :
  Relay 0.25), a lattice size policy (12 | 14), the `KeyLedger`
  permanent-key bookkeeping with radial soft-forget of cell
  payloads. Its header self-discloses: "It is not a harmonic
  engine and computes nothing musical; the 'harmonic' name is
  historical."
- **Consumers:** live production — `form/open.py` (Program holds
  `keys: KeyLedger`, :128/:276; imports :25-26), `schema_board.py`
  (`pulse_status`), `persist` path via lattice sizes; registry
  rows in `organ_atlas.py:99-101`. Proof surface:
  `p4_lattice_collision_proof.py`, `p3_wiring_test.py:212`.
- **Naming risk:** module name promises an engine the header
  disclaims; consumers import concrete symbols (`KeyLedger`,
  `pulse_status`), so the collision is at module-discovery level,
  not call-site level.

### H-5 — `HarmonicLattice`
- **Semantics:** the H/V/F spatial lattice Program actually runs
  on: cells with lossless derived membership, shared perception
  forms (cube/core, square/circle, cube/sphere, Flower of Life as
  perception modes over one coordinate set). The "harmonic" part
  is real but narrow: musical-interval constants (`NOTES`,
  `FIFTH = 7`, `MAJOR_THIRD = 4`) participate in the coordinate
  vocabulary.
- **Consumers:** central — `form/open.py` (Program.lattice,
  :127/:274), `form/persist.py` / `persist_rest.py` (serialization
  authority), registry rows (`organ_atlas.py:28`,
  `matrix_body.py:29`, `matrices_hub.py:18`). Proofs:
  `p4_lattice_collision_proof.py`, D1 registry tests.
- **Naming risk:** highest legitimacy of the seven (the name
  describes its coordinate vocabulary) and the highest rename
  cost; the audit question is labeling, not renaming.

### H-6 — `harmony_score`
- **Semantics:** set-level coherence of an idea set, penalized by
  redundancy: `harmony = C · (1 − R)`, R from mean pairwise
  Jaccard raised to `_DUP_EXPONENT = 3.0` (`harmony.py:96`).
  Module docstring explicitly separates it from resonance `pulse`,
  `harmonize_pair`, `_affinity`, and verita pair coherence —
  separation proven in `p3_r32_harmony_proof.py`.
- **Consumers:** canonical growth path — `ringed_growth.py:32`
  imports it as "canonical harmony authority", called at `:651`
  per proposal pair; persisted on Nursery proposals; proof
  `p3_r32_harmony_proof.py` (37/37 at a05d27db, this circuit).
- **Naming risk:** the word here is "harmony", not "harmonic" —
  the audit must record whether the R4-A6 scope covers the
  harmony/harmonic word family or the token "harmonic" only
  (see Q-S2R.4.2). Its docstring already performs the firewall
  duty R4-A6 asks for.

### H-7 — `graph_coherence` (`graph_harmony.py`)
- **Semantics:** graph-level coherence: the fraction of association
  evidence the canonical SemanticGraph records for a set of idea
  IDs, read-only through `association_neighbors`; defined neutral
  0.0 when the graph records no association — explicitly never
  presented as proof of disconnectedness.
- **Consumers:** `ringed_growth.py:35` import, called at `:659`
  per proposal pair when a graph is attached, persisted as the
  proposal's `graph_coherence`; proofs `p3_r36_graph_harmony_proof.py`
  (48/48 at a05d27db, this circuit) and `p3_r35_integration_proof.py`.
- **Naming risk:** the *function* is honestly named
  (`graph_coherence`); the collision lives in the *module* name
  `graph_harmony` and in prose that shortens it to "harmony".

## The bounded audit plan

**Deliverable:** one records-only audit report (a successor to
this plan) with, per bearer H-1..H-7, a completed audit card and a
disposition *proposal*. The audit itself changes no code, no
ledger text, and no name.

**Phase A — Inventory freeze (per bearer).** Definition site,
every in-tree consumer (static import / call / registry row /
prose mention, classified), and every public surface that prints
the bearer's name (REPL output, status renders, ledger entries,
organ atlas / schema board rows). Evidence standard: file:line at
a named main SHA, search scope stated (static + dynamic-import
scan), UNKNOWN where a search cannot be completed — absence is
recorded as NO_CALLER_FOUND only on a completed exhaustive search
(the Q-S2R.2 participation-schema standard, PR #470).

**Phase B — Semantics statement (per bearer).** One paragraph per
bearer: inputs, outputs, what quantity (if any) it computes, and
what it is *not* — checked against a behavioral probe or an
existing green proof where one exists (H-3: invariants test;
H-6: P3 R3.2 proof; H-7: P3 R3.6 proof; H-5: P4 lattice proof).
No new mathematics is admitted or validated by this phase.

**Phase C — Labeling-duty assessment (per bearer).** Does each
public surface that reports the bearer already say *which* bearer
it reports (the R4-A2 verita-firewall duty, applied by analogy)?
Recorded per surface as OBEYS / DOES-NOT-OBEY / NO-SURFACE, with
the H-3/H-4/H-6 self-disclosing docstrings assessed as code-level
labeling only — a docstring does not discharge a user-facing
surface.

**Phase D — Disposition proposals (per bearer, for ruling).**
Exactly one proposal per bearer, chosen from: (i) KEEP name +
add/extend surface labeling; (ii) QUALIFY in docs/ledger prose
only; (iii) RENAME CANDIDATE — with blast radius (consumer count
from Phase A), the stability rules that bear on it (e.g. H-3's
name-kept-by-rule record), and a falsifier (what evidence would
make the proposal wrong). No proposal is executed by the audit;
each disposition is a separate Director ruling and, where code is
touched, a separate CODE circuit.

**Bounds.** In scope: the seven bearers above, their consumers,
and surfaces that name them. Out of scope: any rename or code
change; any semantic merger or averaging (firewall F5 / R4-A5);
the verita bearer family (R4-A2 / Q-S2R.2 own it); new bearers
discovered mid-audit — they are recorded as a scope question for
the Director, never silently added. Stop condition: the audit
report is complete when all seven cards carry Phase A–C evidence
and a Phase D proposal, or a named blocker (owner + exact missing
input) is recorded for a specific card.

## Questions carried

- **Q-S2R.4.1 (Director):** is H-2 one bearer (the `Form.CUBE`
  enum value as cited in Append D) or the cube-mode family across
  `Form` / `Perspective` / `Skin`? The plan audits the family and
  flags the distinction on the H-2 card either way.
- **Q-S2R.4.2 (Director):** does the R4-A6 scope cover the
  harmony/harmonic word family (bringing H-6/H-7 in as word-family
  bearers, as Append D already lists them) — the plan assumes
  Append D's seven as given and asks only whether the *labeling
  standard* should be stated for the family or the token.
- **Q-S2R.4.3 (Director/Keeper):** for the frozen legacy bearer
  H-1, is registry/docs labeling (legacy_map + ledger §8) a
  sufficient disposition path, given no live Python consumer?
- **Q-S2R.4.4 (Keeper):** Keeper check of this plan's grounding
  table and bounds before the audit executes — the same
  check-before-adoption pattern as Q-S2R.2.

## Test receipts (Uni, this circuit, at a05d27db)

- `form.equation_ledger_invariants_test` — ALL PASS 14/14
  (includes EQ-RES-001 `_harmonic` bounds, H-3).
- `form.mandell.p3_r32_harmony_proof` — 37/37 PASS (H-6 separation).
- `form.mandell.p3_r36_graph_harmony_proof` — 48/48 PASS (H-7).

## Scope / credits

Records only. No code changed, no ledger text changed, no name
changed by this PR. No PLAN/CODE credit claimed — the plan is
submitted for Keeper check and Director ruling; the audit it
bounds is a separate circuit once ruled.
