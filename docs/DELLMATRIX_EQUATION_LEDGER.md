# DELLMATRIX EQUATION LEDGER

**Program:** DELLMATRIX_GDP_001 · **Phase:** 0 — Integrity & Semantic Foundation
**Requirement:** 0.4 Mathematical Authority · **Version:** GDP-V1
**Base:** `gdp-phase0-work` @ `1c90cecf9e5bbbf6bda055f3157ecada299f6840`
**Status:** LEDGER V1 (working authority, not implementation)
**Law:** No two formulas may silently define the same semantic quantity.
Every entry cites its evidence. UNKNOWN is recorded as UNKNOWN.

---

## 0. HOW TO READ THIS LEDGER

Each entry carries:

- **ID** — stable ledger identifier (e.g. `EQ-VER-007`).
- **Formula** — verbatim as implemented (not paraphrased).
- **Location** — exact file:line on the Phase-0 base.
- **Origin** — era and commit where introduced.
- **Variables** — every variable defined with type and domain.
- **Classification** — exactly one of:
  `ACTIVE_VALIDATED` · `ACTIVE_UNVALIDATED` · `DISCONNECTED` ·
  `EXPERIMENTAL` · `HISTORICAL` · `DUPLICATE` · `CONTRADICTORY` ·
  `MATHEMATICALLY_UNJUSTIFIED` · `RECOVERY_CANDIDATE` · `UNKNOWN`
- **Evidence** — the recovery record or code reference supporting the classification.
- **Honesty note** — what the formula does NOT prove or mean.

Classification rule: a formula that *computes correctly* but whose *constants,
weights, or semantic interpretation* are designer-chosen without derivation is
`ACTIVE_UNVALIDATED`, not `MATHEMATICALLY_UNJUSTIFIED`. `MATHEMATICALLY_UNJUSTIFIED`
is reserved for formulas/claims that are mathematically incoherent or whose
stated meaning is contradicted by their own behavior.

---

## 1. VERITA ERA 1 — SMITH CHART LINEAGE (LEGACY)

Origin: commit `476c509` (2026-07-25) "Incorporate Veritasium Smith Chart concept";
registered `65f7938`; frozen by the 2026-08-01 LEGACY freeze of `src/`.
Design record: `docs/SMITH_MAP.md`. External research: `mpc012r-smith-chart-research.md`
(13 sources, 10 families). The Veritasium video itself (`GK2pZ_oVU1o`) is NOT in the repo —
only its incorporation.

### EQ-SMI-001 — Reflection coefficient (complex)
- **Formula:** `Γ = (ZL − Z0) / (ZL + Z0)` via complex division:
  `gamma.r = (num.r*den.r + num.x*den.x)/denMag2`,
  `gamma.x = (num.x*den.r − num.r*den.x)/denMag2`;
  `mag = min(1, |gamma|)`
- **Location:** `src/core/smith_map.js:34-39`
- **Origin:** 2026-07-25, `476c509`
- **Variables:** `ZL = {r, x}` load impedance (Ω, complex); `Z0 = {r:50, x:0}` characteristic impedance (Ω, real by default); `Γ = {r, x}` complex reflection coefficient; `mag ∈ [0,1]` clamped magnitude.
- **Classification:** `HISTORICAL` — mathematically valid in its own domain (transmission-line physics), zero `form/` callers, frozen with `src/`.
- **Evidence:** mpc012r-verita-code-map.md §M1; mpc012r-smith-chart-research.md §2.1 confirms the external equation.
- **Honesty note:** The complex math was never ported to Python. It does not prove anything about DellMatrix ideas.

### EQ-SMI-002 — Match threshold
- **Formula:** `matched ⟺ |Γ| < 0.05`
- **Location:** `src/core/smith_map.js:39`
- **Origin:** 2026-07-25, `476c509`
- **Variables:** `mag` from EQ-SMI-001; `0.05` arbitrary threshold (dimensionless).
- **Classification:** `HISTORICAL` — the 0.05 threshold was a designer-chosen constant of the era-1 experiment; it is not derived.
- **Evidence:** code-map §M1.

### EQ-SMI-003 — Unit-circle projection
- **Formula:** `(u, v) = (Re Γ, Im Γ)`; `inside ⟺ |Γ| ≤ 1`
- **Location:** `src/core/smith_map.js:46-51`
- **Origin:** 2026-07-25, `476c509`
- **Variables:** `(u,v)` unit-disk coordinates; `inside` boolean.
- **Classification:** `HISTORICAL` — valid Möbius-image projection in its domain; never rendered by any recovered consumer (code-map UNKNOWN-1: no evidence `projectAll` output was ever consumed).
- **Evidence:** code-map §M1, §VERITA_VS_PERSPECTIVE.

### EQ-SMI-004 — Node impedance mapping
- **Formula:** `r = max(1, 50 / (1 + 0.35·contacts))`; `x = 8·shell + 5·max(0, 3−height)`
- **Location:** `src/core/smith_map.js:62-70`
- **Origin:** 2026-07-25, `476c509`
- **Variables:** `contacts` (int ≥ 0, legacy lattice node contact count); `shell` (int ≥ 0, hex shell index); `height` (float, growth stage); `r, x` pseudo-impedance components (Ω-like, creative mapping).
- **Classification:** `HISTORICAL` — constants `0.35`, `8`, `5`, `3`, `50` are unjustified by any derivation; the era's own header declares it "structural, not RF hardware claims."
- **Evidence:** code-map §M1 (verbatim logic); docs/SMITH_MAP.md.

### EQ-SMI-005 — Stub correction
- **Formula:** `cancelX = −x_load`; series capacitance if `x > 0` else series inductance
- **Location:** `src/core/smith_map.js:87-88`
- **Origin:** 2026-07-25, `476c509`
- **Classification:** `HISTORICAL` — an analogy to RF stub matching; no DellMatrix operation ever consumed a stub suggestion.
- **Evidence:** code-map §M1.

### EQ-SMI-006 — Standing-wave residue record
- **Formula:** if not matched → `{kind:'standing-wave', reflectionMag, flowQuality, at}` left via `foundation.stigmergic.leaveResidue('sw-<a>-<b>', residue, 'wave')`
- **Location:** `src/core/smith_map.js:106-112`
- **Origin:** 2026-07-25, `476c509`
- **Classification:** `HISTORICAL` — the *record* mechanism is coherent code; its meaning ("standing wave") is an era-1 metaphor that died with the legacy freeze.
- **Evidence:** code-map §M1.

---

## 2. VERITA ERA 2 — STRUCTURAL TRUTH CHECKS (ACTIVE)

Origin: commit `cefc216` (2026-08-08) "Verita single-idea integrity + pair coherence; residue field".
The era-1 complex math was deliberately NOT ported. Live callers:
`form/dell_matrix/brain.py`, `auto_growth.py` (MIN_VERITA gate), `flash_path.py`,
`matrix_awake.py`, `free_matrix_150_audit.py`. English-reachable (`verita`, `vesica edges`).

### EQ-VER-001 — Vesica strength (verita.py)
- **Formula:** `ssum = r1+r2`; `diff = |r1−r2|`; `d ≥ ssum → 0.0`; `d ≤ diff → 1.0`; else `strength = 1 − (d − diff)/(ssum − diff)`
- **Location:** `form/dell_matrix/verita.py:31-44`
- **Origin:** 2026-08-08, `cefc216`
- **Variables:** `r1, r2` circle radii (float > 0); `d` center distance (float ≥ 0); `strength ∈ [0,1]` linear overlap fraction.
- **Classification:** `DUPLICATE` of EQ-GEO-001 (same formula, fewer return fields). Canonical authority: `form/dell_matrix/sacred_geometry.py:145` (EQ-GEO-001).
- **Evidence:** code-map §M2; formula textually identical to sacred_geometry strength core.
- **Honesty note:** This is an overlap *fraction* peaking at containment (`d → diff`), NOT at the classic lens shape (equal circles at `d = R` score exactly 0.5). The name "strength" must not be read as "meeting quality."
- **Action:** R4-A1 (ledger §7) — reconcile to one authority; source change required.

### EQ-VER-002 — Solo integrity score
- **Formula:** `score = 0.25·clarity + 0.20·density + 0.25·agreement + 0.15·goal_load + 0.15·structure`; grades: `≥0.55` strong (accept), `≥0.35` viable (accept), `≥0.18` weak (reject→residue), else fog (reject)
- **Location:** `form/dell_matrix/verita.py:47-116`
- **Origin:** 2026-08-08, `cefc216`
- **Variables:** five axes each ∈ [0,1]: clarity (length band 3..72 + anti-fog list), density (token count/6), agreement (label∩body overlap), goal_load (goals or directional words), structure (alphanumeric substance). All weights and thresholds dimensionless.
- **Classification:** `ACTIVE_UNVALIDATED` — live on the auto-growth gate path; every weight (`0.25/0.20/0.25/0.15/0.15`) and threshold (`0.55/0.35/0.18`) is a designer-chosen policy constant with no derivation and no validation test in the repo.
- **Evidence:** code-map §M2 (verbatim); no test file validates the weights (only in-module `smoke()` with 6 assertions).
- **Honesty note:** This is a policy heuristic, not a measurement. It must not be presented as a calibrated truth detector.

### EQ-VER-003 — Pair coherence score
- **Formula:** `score = 0.60·jaccard + 0.40·vesica_strength`; penalty: if `jaccard < 0.08 ∧ geo < 0.85` then `score ×= 0.5`; `accept ⟺ score ≥ 0.18 ∧ (jaccard ≥ 0.08 ∨ contained)`
- **Location:** `form/dell_matrix/verita.py:154-180`
- **Origin:** 2026-08-08, `cefc216`
- **Variables:** `jaccard = |ta∩tb|/|ta∪tb|` token-set Jaccard ∈ [0,1]; `vesica_strength` from EQ-VER-001; `min_jaccard = 0.08` default.
- **Classification:** `ACTIVE_UNVALIDATED` — live on brain/auto-growth paths; the `0.60/0.40` blend, the `0.5` penalty, and the `0.18/0.08/0.85` gates are un-derived policy constants.
- **Evidence:** code-map §M2.
- **Honesty note:** Despite the word "verita," this is a separate quantity from EQ-GEO-002 (sacred verita) and from era-1 match — see the Verita firewall (§6).

### EQ-VER-004 — Floor license combination
- **Formula:** `combined_score = 0.50·local_score + 0.50·floor_alignment_score`; local reject is final; local accept requires at least partial Floor alignment
- **Location:** `form/dell_matrix/floor_spirit.py:209-246`
- **Origin:** 2026-08-08 integration wave (`61610b3`, `854d0db` era)
- **Variables:** `local_score ∈ [0,1]` (Verita judgment); `floor_alignment_score ∈ [0,1]` (`whole_alignment` over Alpha·Delta·Omega·Omni).
- **Classification:** `ACTIVE_UNVALIDATED` — live gate on brain and auto-growth; the 50/50 blend is policy, not derivation.
- **Evidence:** code-map §M4 (verbatim logic).
---

## 3. FLOWER / SPHERE GEOMETRY (ACTIVE)

Origin: Python port `22da7ec` (2026-08-08) of the 2026-07-25 dual-lattice work (`23ba729`);
touched by FCND-I `da6e154` (2026-10-02). Live consumers: `graph_view.py:129`
(`verita_between_nodes` → `ViewEdge(kind="vesica")`), REPL commands
(`flower`, `vesica`, `verita`), `plane.py` `Perspective.FLOWER`, live SVG rendering.
Blocking reality (MPC-012 Agent C): all real user ideas sit at `(0,0)`, so
`verita_between_nodes` on live content computes overlap of stacked positions —
the geometric relationship layer is currently vacuous on real content.
Evidence: mpc012r-flower-sphere-recovery.md §PLANE_LATTICE_LINK.

### EQ-GEO-001 — Overlap strength core (canonical)
- **Formula:** `sum_r = ar+br`; `diff_r = |ar−br|`; `d ≥ sum_r → 0.0`; `d ≤ diff_r → 1.0`;
  else `strength = 1.0 − (dist − diff_r) / (sum_r − diff_r)`
- **Location:** `form/dell_matrix/sacred_geometry.py:145`
- **Origin:** 2026-08-08 port of `src/core/dual_lattice.js:50-67` (`computeVesica`)
- **Variables:** `ar, br` circle radii (float > 0); `dist` center distance (float ≥ 0); `strength ∈ [0,1]` linear overlap fraction.
- **Classification:** `ACTIVE_UNVALIDATED` — the geometry is correct but the semantic
  reading ("strength of meeting") is unvalidated; the linear form is one arbitrary
  choice among many (lens-area fraction, Jaccard-of-disks).
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.2 (verified: equal unit circles at `d=1` → strength 0.5).
- **Honesty note:** strength peaks at containment, not at the classic lens. The in-code comment
  at `sacred_geometry.py:143` ("strength peaks when dist ≈ radius (equal circles)") is
  **contradicted by the formula itself** — recorded separately as EQ-GEO-013.

### EQ-GEO-002 — Sacred verita (coherence-of-meet heuristic)
- **Formula:** `ideal = (ar+br)/2`; `verita = strength × (1.0 − min(1.0, |dist − ideal|/ideal) × 0.5)`;
  coincident → 1.0; contained → 0.85; clamped to [0,1]
- **Location:** `form/dell_matrix/sacred_geometry.py:146-149` (+ special cases 118-142)
- **Origin:** 2026-08-08 port lineage; constants undocumented
- **Variables:** `strength` from EQ-GEO-001; `ideal` the "ideal" center distance; `0.5` max discount factor; `0.85/1.0` special-case constants.
- **Classification:** `MATHEMATICALLY_UNJUSTIFIED` — no derivation from any standard;
  the classic vesica (equal circles, `d=R`) scores verita = 0.5 while containment
  scores 0.85; the penalty peaks nowhere meaningful.
- **Evidence:** flower-sphere-recovery.md §MATHEMATICALLY_UNJUSTIFIED_COMPONENTS (explicitly flagged).
- **Honesty note:** `docs/SACRED_GEOMETRY.md:24-25` already renames this "coherence-of-meet"
  with the note "coherence ≠ truth" — the anti-pseudomath discipline is partially applied
  in-tree. Do not present this number as a truth measure.
- **Action:** R4-A3 (replace with a defined metric; Phase 3 candidate).

### EQ-GEO-003 — Lens geometry (chord formula)
- **Formula:** `a = (ar² − br² + d²) / (2d)`; `h = √(ar² − a²)`; `lens_width = 2h`;
  midpoint `m = a + (d̂)·((ar² − br² + d²)/(2d))`
- **Location:** `form/dell_matrix/sacred_geometry.py:150-158`
- **Origin:** standard circle–circle intersection; 2026-08-08 port
- **Variables:** `a` plane offset from circle A center along the center line; `h` half-chord length; `lens_width = 2h`.
- **Classification:** `ACTIVE_VALIDATED` — standard mathematics; empirically verified in recovery
  (equal unit circles at `d=1` → `2h = √3 ≈ 1.7321` ✓).
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.2 (√3 verified).

### EQ-GEO-004 — Overlap classification taxonomy
- **Formula:** `d < 1e-12` → `coincident`; `d ≥ r1+r2` → `separate`; `d ≤ |r1−r2|` → `contained`; else → `vesica`
- **Location:** `form/dell_matrix/sacred_geometry.py:117-142`
- **Classification:** `ACTIVE_VALIDATED` — standard two-circle taxonomy.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.2.

### EQ-GEO-005 — Flower-of-Life center generation
- **Formula:** hexagonal (triangular) lattice: for ring `r`, 6 corners at angles
  0°,60°…300° on radius `r·R`, plus `r−1` interpolated points per edge; dedup at 1e-5.
  Counts: rings=0 → 1; rings=1 → 7 (Seed of Life); rings=2 → 19 (Flower of Life);
  `fruit_of_life_centers` → 13
- **Location:** `form/dell_matrix/sacred_geometry.py:23-53`
- **Classification:** `ACTIVE_VALIDATED` — correct hexagonal numbers 1/7/19; empirically verified.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.1.
- **Honesty note:** FoL rings are a finite construction with no recursive scaling law — they are
  NOT fractal (see EQ-GEO-014).

### EQ-GEO-006 — Idea-node score→radius mapping
- **Formula:** `radius = 1.2 × (0.6 + 0.4 × min(2, score))`; gates `max_dist = 3.5`, `min_verita = 0.2`;
  "near" falloff for separate pairs: `0.35 × (1 − d/max_dist)`
- **Location:** `form/dell_matrix/sacred_geometry.py` (`verita_between_nodes`)
- **Variables:** `score` idea score (float); `1.2/0.6/0.4/2/3.5/0.2/0.35` all undocumented constants.
- **Classification:** `MATHEMATICALLY_UNJUSTIFIED` — every constant is arbitrary; the mapping
  from "idea score" to "circle radius" has no stated basis.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.3 (explicitly flagged).

### EQ-GEO-007 — Rule 90 generator
- **Formula:** `next[i] = left XOR right`
- **Location:** `form/dell_matrix/sacred_geometry.py` (fractals section)
- **Classification:** `ACTIVE_VALIDATED` — genuine Sierpinski generator.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.5.

### EQ-GEO-008 — Complex orbit (`z ← z² + c`)
- **Formula:** standard complex quadratic iteration with escape radius
- **Location:** `form/dell_matrix/sacred_geometry.py` (fractals section)
- **Classification:** `ACTIVE_VALIDATED` — standard; interpretive use documented in-module.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.5.

### EQ-GEO-009 — Sierpinski recursive midpoint subdivision
- **Formula:** recursive midpoint subdivision (`sierpinski_points`)
- **Location:** `form/dell_matrix/sacred_geometry.py` (fractals section)
- **Classification:** `ACTIVE_VALIDATED` — genuine recursive self-similarity.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.5.

### EQ-GEO-010 — Phi-shell scaling (drawing)
- **Formula:** `r ×= φ / 1.4` per shell ("tempered growth for visibility")
- **Location:** `form/dell_matrix/sacred_geometry.py:415`
- **Classification:** `MATHEMATICALLY_UNJUSTIFIED` *as fractal* — decorative geometric scaling for
  drawing; there is no recursive self-similar structure. The code comment is honest
  ("for visibility"); any claim of fractality would be false.
- **Evidence:** flower-sphere-recovery.md §FRACTAL_LINK.

### EQ-GEO-011 — Hex shell offsets / axial-to-cube (JS, legacy)
- **Formula:** `hexShellOffsets(shell)` 6-direction walk; `axialToCube(q,r) = {i:q, j:−q−r, k:r}`
- **Location:** `src/core/dual_lattice.js:69-90`
- **Classification:** `HISTORICAL` — correct hex-grid math; dead with the 2026-08-01 freeze.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.4.

### EQ-GEO-012 — Unit-square projection (JS, legacy)
- **Formula:** `projectToSquare`: `nx = x / maxR` normalization → unit square → grid cell
- **Location:** `src/core/dual_lattice.js:294`
- **Classification:** `HISTORICAL` — bounded projection, mathematically valid; dead code.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.4.

### EQ-GEO-013 — "Strength peaks at the classic vesica" (code comment)
- **Formula/claim:** `sacred_geometry.py:143` comment: "classic vesica — strength peaks when dist ≈ radius (equal circles)"
- **Classification:** `CONTRADICTORY` — the formula at line 145 gives strength = 0.5 at `dist = R`
  (equal circles) and 1.0 at containment. The comment asserts the opposite of the
  formula's behavior.
- **Evidence:** direct code reading; flower-sphere-recovery.md notes "The metric peaks at
  containment, not at the iconic lens shape."
- **Action:** R4-A7 — correct or remove the comment at the reconciliation step.

### EQ-GEO-014 — "FoL rings are recursive/fractal" (doc claim)
- **Formula/claim:** `docs/DUAL_LATTICE.md` describes the derivation as "2D circles → equal
  units, shared centers, recursive"
- **Classification:** `CONTRADICTORY` — `flower_centers` is a finite two-ring construction
  with no recursive scaling law (see EQ-GEO-005). The recovery explicitly falsifies
  the "recursive" reading.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.5, §FRACTAL_LINK.
- **Action:** R4-A7 — correct the doc wording when docs are touched under an authorized directive.

### EQ-GEO-015 — Dual-lattice growth stage thresholds (JS, legacy)
- **Formula:** `height += amount`; stage advances when `height ≥ (idx+1) × 1.2` through
  seed→sprout→stem→branch→leaf→fruit
- **Location:** `src/core/dual_lattice.js` (growth section)
- **Classification:** `HISTORICAL` — the `1.2` step is an arbitrary constant; dead with the freeze.
- **Evidence:** flower-sphere-recovery.md §FLOWER_OF_LIFE_EQUATIONS.4.

---

## 4. RESONANCE / HARMONY / GROWTH-AFFINITY (ACTIVE)

The real cross-idea computation is `ringed_growth._affinity()` — the file named
`resonance.py` is disconnected from geometric resonance (see EQ-RES-003).
Future home: GDP Phase 3 (Resonance, Harmony & Information Geometry).

### EQ-RES-001 — Harmonic bridge combiner (`_harmonic`)
- **Formula:** `jac = |a∩b|/|a∪b|`; `bridge = min(|a−b|, |b−a|)`; `tension = bridge / (1 + |a∪b|)`;
  if `jac ≤ 0 ∧ tension ≤ 0 → 0.0`; else `(2·jac·(jac+tension)) / (2·jac + tension + 1e-9)`
- **Location:** `form/dell_matrix/ringed_growth.py:81-91`
- **Origin:** RingedGrowth mechanism (pre-Phase-0)
- **Variables:** `a, b` token sets of the two ideas; `tension ∈ [0,1)` exclusive-token bridge pressure.
- **Classification:** `ACTIVE_UNVALIDATED` — a defined combiner with bounded output, but the
  harmonic-mean-like form and its weights are un-derived; the name "harmonic" has no
  musical/harmonic-series basis and must not be read as one.
- **Evidence:** direct code reading 2026-10-03.
- **Honesty note:** This and EQ-VER-003 (pair verita) are parallel, unmerged overlap-like
  authorities — see D5 in §7.

### EQ-RES-002 — Growth affinity blend (`_affinity`)
- **Formula:** `spatial = 1/(1+dist)`; `in_scope = 1.0 if b ∈ scope(a) else 0.2`;
  `aff = 0.40·harm + 0.22·jac + 0.13·spatial + 0.13·in_scope + gboost + bboost`
- **Location:** `form/dell_matrix/ringed_growth.py:123-142`
- **Variables:** `harm` EQ-RES-001; `jac` EQ-RES-001's Jaccard; `dist` Euclidean plane distance;
  `gboost` goal boost; `bboost` body-goal boost.
- **Classification:** `ACTIVE_UNVALIDATED` — live in growth decisions; weights `0.40/0.22/0.13/0.13`
  and the `0.2` out-of-scope constant are un-derived policy.
- **Evidence:** direct code reading 2026-10-03.

### EQ-RES-003 — `harmonize_pair` accumulation
- **Formula:** `scores[uid] += amount` (default `amount = 0.5`); `tags[mid] += amount`;
  `tags[token] += amount × 0.3` for the other's label/word tokens; log string
  `"vesica {a}⊗{b} → {mid}"`
- **Location:** `form/dell_matrix/resonance.py:115-148` (log string at line 140)
- **Classification:** `ACTIVE_UNVALIDATED` for the accumulation arithmetic;
  `DISCONNECTED` for the "vesica" reference — `harmonize_pair` computes NO geometry;
  "vesica" is a log token only.
- **Evidence:** flower-sphere-recovery.md §RESONANCE_GEOMETRY_LINK ("Terminological only");
  code-map §VERITA_VS_RESONANCE.
- **Action:** R4-A4 — rename the log token or wire real geometry (Phase 3).

---

## 5. GRAVITY / FORCES (ACTIVE, DESCRIPTIVE)

### EQ-GRV-001 — Gravity well assignment
- **Formula:** `wells = top-3 nodes by score`; `mass = score + 1.0`
- **Location:** `form/dell_matrix/forces.py:217-224` (`GravityForce.set_wells_from_scores`)
- **Variables:** `score` idea score (float); `mass` well mass (float ≥ 1.0).
- **Classification:** `ACTIVE_UNVALIDATED` — the assignment runs, but no movement/pull equation
  consumes `mass` in the recovered paths; the class description ("Heavy ideas pull
  others toward them") describes behavior no equation implements.
- **Evidence:** direct code reading 2026-10-03; flower-sphere-recovery.md §GRAVITY_GEOMETRY_LINK
  ("Not established… no code connects gravity, forces, or movement to vesica overlap").
- **Honesty note:** Gravity-as-pull is currently `DISCONNECTED` as a mechanism: described,
  not computed. The generic `ForceMatrix.evolve(amount=0.05)` (`forces.py:48`) is a uniform
  decay, not a gravitational law. Future home: Phase 4 (Living Spatial Matrix).

---

## 6. KNOWN / UNKNOWN / GROWTH

### EQ-KNG-001 — Δ_known / Δ_unknown decision fuel
- **Formula:** none recovered. Prose principles only:
  "Δ_known is permanent fuel — never closed." / "Δ_unknown stays labeled PROJECTED_NOT_FACT."
- **Location:** `form/dell_matrix/decision_shells.py:8-9` (module docstring); referenced at line 322
- **Classification:** `UNKNOWN` — there is no equation to classify; the "known/unknown
  equations" named in the GDP no-loss law have NOT been recovered as mathematics.
  The Overseer's recollection of an occupied/void/boundary ↔ KNOWN/UNKNOWN/POTENTIAL/GROWTH
  mapping is **unconfirmed by repository evidence** (flower-sphere-recovery.md
  §KNOWN_UNKNOWN_GEOMETRY_LINK).
- **Evidence:** flower-sphere-recovery.md §KNOWN_UNKNOWN_GEOMETRY_LINK; direct code reading.
- **Action:** R4-A8 — treat as recovery target, not as authority.

---

## 7. DUPLICATE-AUTHORITY DECISIONS (0.4.4)

No source files were edited (this requirement is ledger-only). Each decision records
the REQUIRED source change as an action item for the coordinator / a future
authorized directive.

| # | Action | Finding | Canonical authority | Required source change (NOT performed) |
|---|---|---|---|---|
| R4-A1 | DEDUP | `vesica_strength` core formula implemented twice live: `sacred_geometry.py:145` (EQ-GEO-001) and `verita.py:31-44` (EQ-VER-001); third copy in legacy `dual_lattice.js:50-67` | `form/dell_matrix/sacred_geometry.py::vesica` (richest: classification + lens geometry + midpoint) | `verita.py::vesica_strength` must delegate to the canonical implementation (or be removed with callers migrated). Legacy JS copy: no action (frozen). |
| R4-A2 | FIREWALL | The name "verita" denotes three different quantities: era-1 match flag (EQ-SMI-002), sacred coherence-of-meet (EQ-GEO-002), pair truth-of-overlap (EQ-VER-003) | Firewall §8 — names are namespaced, mechanisms are not merged | A future cleanup (Director decision; Phase 3 or docs pass) must namespace or rename at least two of the three. Until then, every public surface must say WHICH verita it reports. |
| R4-A3 | REPLACE | EQ-GEO-002 sacred-verita heuristic is `MATHEMATICALLY_UNJUSTIFIED` | To be defined under the Admission Contract (§contract) | Phase 3 candidate: replace with a defined metric (lens-area fraction or Jaccard-of-disks). Until replacement, outputs must carry their classification label. |
| R4-A4 | RENAME-OR-WIRE | `resonance.py:140` logs "vesica" but computes no geometry (EQ-RES-003) | Either the geometric vesica (EQ-GEO-003/004) or an honest label | Rename the log token (e.g. `relation`) or wire real overlap geometry. Phase 3. |
| R4-A5 | RECONCILE-DONT-MERGE | Three parallel overlap-like 0..1 authorities: `_harmonic()` (EQ-RES-001), pair verita (EQ-VER-003), sacred verita (EQ-GEO-002) — shared callers (brain, auto_growth) but no documented relationship | Keep separate; document each as a distinct quantity | Phase 3 must produce the reconciliation: which quantity gates what, with tests. Do NOT average them into one number. |
| R4-A6 | NAME-COLLISION | "Harmonic" names three mechanisms: `harmonic_cube_5ring.js` (5-tier memory, zero math), `Form.CUBE` perception, `_harmonic()` (EQ-RES-001) | Distinct mechanisms; the word is not a concept | Naming audit in a future docs/hygiene pass; no semantic merge. |
| R4-A7 | DOC-CORRECTION | EQ-GEO-013 (comment contradicts formula) and EQ-GEO-014 ("recursive" FoL claim) | The formula (EQ-GEO-001) and the construction (EQ-GEO-005) | Correct the comment at `sacred_geometry.py:143` and the `docs/DUAL_LATTICE.md` wording under the next authorized docs touch. |
| R4-A8 | RECOVER | EQ-KNG-001: no known/unknown equation exists in the repo | UNKNOWN — not authority | Recovery target for Phase 3/4 research; do not invent the equation to fill the slot. |

---

## 8. LINEAGE REGISTER (0.4.3)

| Lineage | Era / commits | Math recovered | Live mechanism | Lineage status |
|---|---|---|---|---|
| **RootPath / RuPat** | preform design docs only | NONE — mentions in `preform/MANUAL_EXTRACT.md:12,18`, `preform/VISUAL_GLYPH_LAYER.md:18,44,58,65,110` (flow diagonals, fog-return path) | No runtime equations found | `UNKNOWN` as mathematics; preserved as design vocabulary. No-loss law applies: do not erase, do not invent. |
| **Harmonic Cube** | `src/core/harmonic_cube_5ring.js` (2026-07-25 era) | NONE — 5-tier memory (shem/gem/rememory/sub/plannedFog), zero sphere/circle math | Memory tiers (legacy) | `UNKNOWN` as mathematics. Name collides with `Form.CUBE` and `_harmonic()` (R4-A6). |
| **Verita** | Era 1: `476c509` (2026-07-25); Era 2: `cefc216` (2026-08-08) | Era 1: EQ-SMI-001..006 (complex Γ math). Era 2: EQ-VER-001..004 (heuristic scoring) | Era 2 live on brain/auto_growth; Era 1 frozen | Two eras, one name, no math ported. Firewall §8. |
| **Flower geometry** | `23ba729` (2026-07-25 JS) → `22da7ec` (2026-08-08 Python) → `da6e154` (2026-10-02) | EQ-GEO-001..014: hex centers valid; lens geometry valid; strength/verita heuristics unjustified; "recursive" claim contradicted | `verita_between_nodes` → graph vesica edges (vacuous at (0,0)) | Valid geometry core; heuristic scoring layer must be replaced (R4-A3). |
| **Gravity** | `form/dell_matrix/forces.py` (pre-Phase-0) | NONE — well assignment only (EQ-GRV-001); no pull law | Described, not computed | `DISCONNECTED` as mechanism. Phase 4 candidate. |
| **Resonance** | `resonance.py` + `ringed_growth.py` (pre-Phase-0) | EQ-RES-001..003 (heuristic combiners + tag accumulation) | Live in growth decisions | Real computation exists (`_affinity`); the named module is disconnected from geometry. Phase 3 home. |
| **Harmony** | `_harmonic()` in `ringed_growth.py:81` | EQ-RES-001 only | Live as affinity subterm | No independent harmony mechanism recovered; the word is a label on a combiner. Phase 3 must define or retire it. |
| **Known/Unknown/Growth** | `decision_shells.py` prose; Overseer recollection | NONE (EQ-KNG-001 = UNKNOWN) | Prose principles guide decisions | Unrecovered as mathematics. Do not assert the geometric mapping. |
| **Nursery / RingedGrowth** | `ringed_growth.py` | EQ-RES-001, EQ-RES-002 (affinity drives growth) | Live | Heuristic but real; Phase 5 home. |
| **DuoBeta** | — | No equations recovered in this requirement's scope | — | Out of scope for R4; noted for ledger completeness. |
| **AbCC / LUPE** | `form/mandell/circuit_ledger.py:166` ("MODE_LUPE stale unrevoked law"); docs mentions | NONE — no definition or equation found | Unknown | `UNKNOWN`. No-loss law: preserved as a name, not as math. |
| **Personas / BIMO** | `form/dell_matrix/personas.py` | No equations in scope | — | Out of scope for R4. |
| **Stonehenge / Voynich** | `form/ancient/stonehenge_seed.py`; Voynich 5-ring metaphor in `sacred_geometry.py` | Circle-`Skin` seed vocabulary; no equations | Tangential | Documented, not mathematical authority. |
| **SUS / SUSX100 / NBD** | Directive architecture | No equations in scope | — | Out of scope for R4. |

---

## 9. EXTERNAL REFERENCE MATHEMATICS (NOT DELLMATRIX AUTHORITY)

Recovered for research discipline; these are NOT DellMatrix equations and must not be
cited as DellMatrix authority without passing the Admission Contract.

- **EXT-SMI-001** — Smith chart core: `z = Z/Z₀`; `Γ = (z−1)/(z+1)`; `z = (1+Γ)/(1−Γ)`;
  constant-r circles center `(r/(1+r), 0)` radius `1/(1+r)`; constant-x arcs center
  `(1, 1/x)` radius `1/|x|`; `VSWR = (1+|Γ|)/(1−|Γ|)`; line propagation
  `Γ(ℓ) = Γ_L·e^(−j2βℓ)`. Source: mpc012r-smith-chart-research.md §2 (13 sources).
- **EXT-GEO-001** — Two-sphere lens volume:
  `V = π(R+r−d)²(d²+2d(R+r)−3(R−r)²)/(12d)`; cap `V_cap = πh²(3R−h)/3`;
  union via inclusion–exclusion. Numerically verified in recovery (1000 random cases).
  Source: flower-sphere-recovery.md §SPHERE_INTERSECTION_EQUATIONS. Status: RECOVERY_CANDIDATE.
- **EXT-GEO-002** — Čech complex / Nerve Theorem (Borsuk 1948): nerve of the ball cover is
  homotopy-equivalent to the union. Status: RECOVERY_CANDIDATE (Phase 3).
  Source: flower-sphere-recovery.md §CECH_COMPLEX_RESEARCH.
- **EXT-GEO-003** — Alpha complex / alpha shapes (Edelsbrunner & Mücke 1994): homotopy-equivalent
  to ball union; filtration over α gives void birth/death. Status: RECOVERY_CANDIDATE (Phase 3/4).
- **EXT-GEO-004** — Power diagram (Laguerre): power distance `Π(x) = |x−p|² − r²`;
  dual of regular triangulation; exact exclusive-vs-shared volume decomposition.
  Status: RECOVERY_CANDIDATE (Phase 3/4).
- **EXT-GEO-005** — Sphere-packing void facts: tetrahedral void radius 0.225R, octahedral 0.414R,
  74% FCC/HCP efficiency. Status: LEAD_ONLY (governs regular arrangements; DellMatrix fields
  are irregular). Source: flower-sphere-recovery.md §SPHERE_PACKING_RESEARCH.

---

## 10. VERITA NAME-COLLISION FIREWALL

The word "Verita" currently denotes THREE different mechanisms. This firewall is binding:

1. **VERITA-SMITH** (era 1, LEGACY): complex reflection coefficient, unit disk, stub, standing waves.
   Ancestry: Veritasium Smith Chart video via commit `476c509`. Math: EQ-SMI-001..006.
   Status: historical experiment/reference. **Do not port the electrical math.**
2. **VERITA-MEET** (sacred geometry, ACTIVE): coherence-of-meet between two circles,
   `sacred_geometry.py::vesica`. Ancestry: Flower-of-Life overlap geometry. Math: EQ-GEO-001..002.
   **Coherence ≠ truth** (in-tree law, `docs/SACRED_GEOMETRY.md:24-25`).
3. **VERITA-JUDGE** (structural truth checks, ACTIVE): solo integrity + pair coherence,
   `verita.py::verita_of_one` / `verita_of_pair`, licensed by Floor Spirit.
   Ancestry: the 2026-08-08 abstraction pivot (`cefc216`) — vocabulary kept, math replaced.
   Math: EQ-VER-001..004.

**Firewall rules:**
- F1. No mechanism may borrow equations, thresholds, or interpretations from another
  Verita without an explicit, reviewed mapping recorded in this ledger.
- F2. Ideas are not impedances: EQ-SMI math must never be applied to idea content.
- F3. Overlap is not truth: EQ-GEO output must never be presented as a truth judgment.
- F4. Every public/REPL surface reporting a "verita" value must identify which of the
  three it reports (action R4-A2).
- F5. The three must not be "unified" into one number (see R4-A5).

---

## 11. CLASSIFICATION SUMMARY

| Classification | Count | IDs |
|---|---|---|
| ACTIVE_VALIDATED | 6 | EQ-GEO-003, 004, 005, 007, 008, 009 |
| ACTIVE_UNVALIDATED | 8 | EQ-VER-002, 003, 004, EQ-GEO-001, EQ-RES-001, 002, EQ-GRV-001, EQ-RES-003 (arith. part) |
| DISCONNECTED | 2 | EQ-RES-003 ("vesica" log ref), EQ-GRV-001 (pull behavior) |
| EXPERIMENTAL | 0 | — |
| HISTORICAL | 9 | EQ-SMI-001, 002, 003, 004, 005, 006, EQ-GEO-011, 012, 015 |
| DUPLICATE | 1 | EQ-VER-001 (→ EQ-GEO-001) |
| CONTRADICTORY | 2 | EQ-GEO-013, EQ-GEO-014 |
| MATHEMATICALLY_UNJUSTIFIED | 3 | EQ-GEO-002, EQ-GEO-006, EQ-GEO-010 (as-fractal-claim) |
| RECOVERY_CANDIDATE | 4 | EXT-GEO-001, 002, 003, 004 |
| UNKNOWN | 3 | EQ-KNG-001, RootPath math, Harmonic-Cube math |

Total ledgered DellMatrix equations: **32** (6 validated, 8 unvalidated-live, 3 unjustified,
2 contradictory, 1 duplicate, 9 historical, 2 disconnected aspects, 3 unknown —
EQ-RES-003 and EQ-GRV-001 each carry two aspects; counts are distinct equations,
aspects listed separately).
External reference entries: 6 (4 EXT-GEO recovery candidates + Smith/sphere-lens
formulae; not DellMatrix authority).

**Ruthless-honesty headline:** of the equations that run live today, ZERO carry a full
mathematical derivation in-repo; 6 are valid standard mathematics (geometry, fractals);
8 are heuristic policy constants on live paths; 3 are mathematically unjustified;
2 in-tree claims contradict their own formulas; 1 live duplicate exists; 10 are
historical; 3 are unknown. This is the baseline Phase 0 must improve.

---

## 12. LEDGER MAINTENANCE

- New equations enter via the Mathematical Admission Contract
  (`docs/MATHEMATICAL_ADMISSION_CONTRACT.md`) — no entry without a classification.
- Reclassification requires evidence cited in this ledger; history is append-only
  (record the old classification, the evidence, and the new one).
- This ledger is append-only within GDP-V1. Completed objectives are never removed.

*Ledger V1 — committed on branch `gdp-p0r4`. Base `1c90cecf9e5bbbf6bda055f3157ecada299f6840`.*
