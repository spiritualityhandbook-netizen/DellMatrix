# Q-S2R.4 — "Harmonic" seven-bearer naming audit: EXECUTION REPORT (records only)

Date: 2026-11-17. Circuit: Q-S2R.4 audit execution, bounded by
director-reports/QS2R4_HARMONIC_NAMING_AUDIT_PLAN_2026-11-17.md
(PR #471, merged 0eda0722). Authority: Director Q-S2R answers on
PR #451 (6946046074) + bounded naming-audit execution authorized
(recorded in MEMORY / state queue). Grounding SHA: current main
`7321268e306ad58489b8bd6ad9ff639b0ce0895e` (fresh clone; static
definition + caller search repo-wide, plus dynamic-import scan).
This report renames nothing, merges nothing, and changes no code
or ledger text. Every Phase D item is a PROPOSAL for a separate
Director ruling.

Proof receipts re-run at 7321268e (this circuit):
- `form.equation_ledger_invariants_test` — ALL PASS 14/14 (H-3).
- `form.mandell.p3_r32_harmony_proof` — 37/37 PASS (H-6).
- `form.mandell.p3_r36_graph_harmony_proof` — 48/48 PASS (H-7).

## Scope question raised mid-audit (per plan bounds — NOT added)

**SQ-1:** A SECOND distinct `HarmonicCube` class exists at
`src/core/mandell_toolkit.js:27` — a geometric grid cube
(size/frequency/label; sine/cosine cell values, quasi-crystal
injection), imported by `src/mandell_kernel.js:15`. It is NOT the
H-1 tiered-memory class (`src/core/harmonic_cube_5ring.js:13`).
Two different mechanisms share the exact class name inside the
legacy JS line. Recorded as a scope question for the Director;
the audit did not silently add an eighth bearer.

## H-1 — `HarmonicCube` (JS, 5-ring)
- **A. Inventory:** def `src/core/harmonic_cube_5ring.js:13`;
  instantiated :144 (inside FiveRingSystem); exported :290.
  Consumers: `src/mandell_kernel.js:6,16` imports the family and
  runs `FiveRingSystem` (:66); `src/compat/legacy_map.js` maps the
  name (per plan grounding). No Python consumer found on a
  completed repo-wide search (form/ + src/): NO_PYTHON_CALLER_FOUND.
- **B. Semantics:** five Map tiers (shem/gem/rememory/sub/
  plannedFog) with store/retrieve, promotion, fogging stats.
  Header self-discloses: "Just a tiered memory system with
  recursive feedback processing." No sphere/circle mathematics.
- **C. Labeling duty:** NO-SURFACE on any live path; docs level
  (file header + ledger §8 row) OBEYS — both say what it is.
- **D. Proposal:** (ii) QUALIFY in docs/ledger prose only —
  mark "legacy JS, frozen, tiered memory; not the Form.CUBE
  family (H-2)". Falsifier: any live Python or user-facing
  consumer surfacing would raise this to a labeling-duty fix.
  Carries Q-S2R.4.3.

## H-2 — `Form.CUBE` perception family
- **A. Inventory:** `form/dell_matrix/perception.py:27`
  (`Form.CUBE = "cube"`, paired opposite `Form.SPHERE` :37-39,
  default form :46); `plane.py:50` (`Perspective.CUBE`), `:57`
  (`Skin.CUBE`, default skin :74). Consumers: 58 references
  across 26 files under form/ (perception, plane,
  harmonic_lattice, graph_view, sandbox/accept gates, D1
  registry tests) — largest blast radius of the seven.
  Audited as the FAMILY per the plan; Q-S2R.4.1 distinction
  flagged here as required: three distinct enum members in two
  modules share the token.
- **B. Semantics:** a perception/plane MODE (how a plane is
  read/rendered), never a quantity or score.
- **C. Labeling duty:** OBEYS — the plane render names the mode
  in words: `plane.py:348` prints "cube-based grid" for
  Perspective.CUBE. Surfaces say which mode is active.
- **D. Proposal:** (i) KEEP names; no rename (blast radius
  disproportionate to a mode-token collision). Falsifier:
  evidence of a surface presenting CUBE as a score/quantity.

## H-3 — `_harmonic()` (EQ-RES-001)
- **A. Inventory:** def `form/dell_matrix/ringed_growth.py:197`;
  exactly one production caller, `:349` inside `_affinity`
  (weight 0.40 into _affinity per the admission contract at
  :164-190). Test consumers: invariants test (:10, :89-98) and
  the P3 R3.1 affinity proof.
- **B. Semantics:** token-set similarity — Jaccard overlap
  blended with a complementary-exclusive tension term,
  (2·jac·(jac+tension))/(2·jac+tension+eps), in [0,1].
  Docstring self-discloses: "NOT musical harmony… Name is
  historical; it is a token-set similarity, not a harmonic";
  name kept for caller stability by rule (GDP-001 Phase 3, 3.1.3).
- **C. Labeling duty:** NO-SURFACE in the product (private name,
  value never printed under its own name). The exposed surface
  is the LEDGER label for EQ-RES-001 ("Harmonic bridge
  combiner"), which does not say which bearer it names:
  DOES-NOT-OBEY at ledger level.
- **D. Proposal:** (ii) QUALIFY in ledger prose only — annotate
  EQ-RES-001's label as the ringed_growth token-set similarity,
  not a harmonic engine. Code name KEEP (kept-by-rule).
  Falsifier: a user-facing surface printing `_harmonic` values
  unlabeled would escalate this to (i) with a surface fix.

## H-4 — `harmonic_core.py`
- **A. Inventory:** module `form/dell_matrix/harmonic_core.py`
  (pulse_status :37, KeyLedger :57 per plan grounding; header
  verified at 7321268e). Consumers: `form/open.py:25-26,71-72`
  imports (KeyLedger, normalize_size, pulse_status,
  apply_radial_soft_forget), Program.keys :128/:276;
  `schema_board.py:141-142,333` (pulse_status spec);
  `organ_atlas.py:99-101` registry row; proofs
  `p4_lattice_collision_proof.py:367`,
  `p3_wiring_test.py:212` (dynamic import — the only
  harmonic-family dynamic import in form/).
- **B. Semantics:** pulse-ratio constants (Subkey 4 : Core 1 :
  Relay 0.25), lattice size policy (12 | 14), KeyLedger
  permanent-key bookkeeping with radial soft-forget. Header
  self-discloses: "It is not a harmonic engine and computes
  nothing musical; the 'harmonic' name is historical."
- **C. Labeling duty:** MIXED — organ_atlas source line OBEYS
  ("form harmonic_core · permanent keys soft-forget"); the
  Program status render exposes the value under the bare key
  `"pulse"` (`form/open.py:2222`) without naming the bearer:
  DOES-NOT-OBEY at that surface (a docstring does not discharge
  a user-facing surface, per plan Phase C).
- **D. Proposal:** (i) KEEP module name + extend surface
  labeling (status render key or gloss identifying pulse_status
  as the harmonic_core key/pulse report) — code-side labeling
  is a separate CODE circuit if ruled. Falsifier: evidence the
  status render is never user-facing.

## H-5 — `HarmonicLattice`
- **A. Inventory:** class `form/dell_matrix/harmonic_lattice.py:80`.
  Consumers: `form/open.py:24,70` imports, Program.lattice
  :127/:274; `form/persist.py:18,31`, `form/persist_rest.py:15`
  (serialization authority, rebuild :223/:243); registry rows
  `organ_atlas.py:28-29`, `matrix_body.py:29`,
  `matrices_hub.py:18` ("Harmonic Lattice"); proofs
  `p4_lattice_collision_proof.py`, D1 registry tests
  (`d1_registry_leaf2_test.py:156` matches the status string
  "HarmonicLattice size=").
- **B. Semantics:** the H/V/F spatial lattice Program runs on;
  the "harmonic" content is real but narrow — musical-interval
  constants participate in the coordinate vocabulary
  (`NOTES` :22, `FIFTH = 7` :23, `MAJOR_THIRD = 4` :24, used
  at :101).
- **C. Labeling duty:** OBEYS — registry and status surfaces
  name it "Harmonic Lattice" / "HarmonicLattice", which is
  what it is.
- **D. Proposal:** (i) KEEP name, no change. Highest legitimacy
  and highest rename cost of the seven. Falsifier: none
  identified in this audit.

## H-6 — `harmony_score`
- **A. Inventory:** def `form/dell_matrix/harmony.py:96`.
  Consumers: `ringed_growth.py:32` import ("canonical harmony
  authority"), called :651 per proposal pair; persisted on
  Nursery proposals (`nursery.py:407,611`); proof
  `p3_r32_harmony_proof.py` (37/37 at 7321268e).
- **B. Semantics:** set-level coherence penalized by redundancy,
  harmony = C · (1 − R), R from mean pairwise Jaccard^3.0;
  output float in [0,1]. Module docstring explicitly separates
  it from resonance pulse, harmonize_pair, _affinity, and
  verita pair coherence — separation proven in P3 R3.2.
- **C. Labeling duty:** OBEYS — persisted field is named
  `harmony`, and the C5R.4 lens disclosures (PR #473) label the
  value's provenance on browse surfaces.
- **D. Proposal:** (i) KEEP name. Word-family question
  Q-S2R.4.2 carried: this bearer is "harmony", not "harmonic";
  the audit recommends the labeling standard be stated for the
  word FAMILY, since Append D already lists H-6/H-7.
  Falsifier: a surface shortening another bearer's value to
  "harmony" would breach the firewall this card records.

## H-7 — `graph_coherence` (`graph_harmony.py`)
- **A. Inventory:** def `form/dell_matrix/graph_harmony.py:126`
  (per plan grounding; module verified at 7321268e).
  Consumers: `ringed_growth.py:33-35` import, called :659 per
  proposal pair when a graph is attached; persisted as the
  proposal's `graph_coherence` (`nursery.py:411-417,602,750`);
  proofs `p3_r36_graph_harmony_proof.py` (48/48 at 7321268e)
  and `p3_r35_integration_proof.py`.
- **B. Semantics:** graph-level coherence — fraction of
  association evidence the canonical SemanticGraph records for
  a set of idea IDs, read-only; defined neutral 0.0 when the
  graph records no association, explicitly never proof of
  disconnectedness.
- **C. Labeling duty:** OBEYS at the value level — the function
  and the persisted field are honestly named
  `graph_coherence`. The collision lives only in the MODULE
  name `graph_harmony` and prose that shortens it to "harmony".
- **D. Proposal:** (ii) QUALIFY in docs/ledger prose only —
  refer to the bearer as graph_coherence (module graph_harmony)
  on first mention. Module RENAME noted as a candidate but NOT
  proposed: import blast radius (ringed_growth, nursery,
  proofs) buys nothing the prose qualification does not.
  Falsifier: prose or a surface presenting graph_coherence
  values as "harmony" scores.

## Questions carried (unchanged from the plan)
- Q-S2R.4.1 (Director): H-2 audited as the cube-mode family;
  the plan's flag is discharged on the H-2 card — ruling still
  owed on whether the bearer is the family or the single enum.
- Q-S2R.4.2 (Director): audit recommends the labeling standard
  be stated for the harmony/harmonic word family.
- Q-S2R.4.3 (Director/Keeper): H-1 disposition path (docs
  qualification) proposed on the H-1 card.
- Q-S2R.4.4 (Keeper): plan grounding was checked pre-execution
  per the plan; this report's cards are the execution record
  for independent Keeper/Director review.
- NEW SQ-1 (Director): second distinct `HarmonicCube` class in
  `src/core/mandell_toolkit.js:27` — scope question, not added.

## Scope / credits
Records only. No code changed, no ledger text changed, no name
changed by this audit. No PLAN/CODE credit claimed. The report
is ready to ride a records-only PR from the main session for
Keeper check + Director ruling on the Phase D proposals.
