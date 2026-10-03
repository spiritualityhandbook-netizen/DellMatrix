# MATHEMATICAL ADMISSION CONTRACT

**Program:** DELLMATRIX_GDP_001 · **Phase:** 0 — Integrity & Semantic Foundation
**Requirement:** 0.4 Mathematical Authority · **Objective:** 0.4.5
**Version:** GDP-V1
**Companion:** `docs/DELLMATRIX_EQUATION_LEDGER.md` (the ledger this contract feeds)

**Purpose.** From this point forward, no equation, formula, scoring rule, combiner,
threshold, or quantitative claim enters DellMatrix — code, docs, or UI — without
satisfying this contract. This is how the program ends pseudomathematics.

**Authority.** ACE > DIRECTOR > UNI. Admission decisions for new semantic quantities
belong to Director; this contract defines the *evidence* any proposal must carry.
`AUTONOMY = NO` — the contract does not authorize anyone to invent product semantics.

---

## 1. THE EIGHT REQUIRED FIELDS

Every proposed equation must be submitted with all eight fields complete.
A proposal missing any field is returned, not debated.

### 1.1 Defined variables
Every symbol named, with:
- **name** (exact identifier as it appears in code)
- **type** (float, int, set, vector, …)
- **domain** (e.g. `score ∈ [0,1]`; `d ≥ 0`; units where physical: px, s, …)
- **provenance** (where the value comes from: measured, computed by ledger entry EQ-___,
  user-supplied, policy constant)

No symbol may appear in the formula that is not listed here.

### 1.2 Defined domain
The input space on which the equation is claimed valid:
- allowed ranges and their justification
- degenerate inputs (zero distance, empty sets, coincident points) and their handling
- inputs the equation explicitly does NOT cover

### 1.3 Defined outputs
- output range (e.g. `[0,1]`, `ℝ⁺`, a category label)
- units, or the explicit statement "dimensionless"
- what the output is *allowed to drive* (gate, ranking, display) and what it must NOT drive

### 1.4 Defined invariants
Statements that must hold before and after evaluation, stated as checkable assertions:
- bounds (e.g. "output ∈ [0,1] for all valid inputs")
- monotonicity (e.g. "strength decreases monotonically with d on (diff, sum)")
- symmetry (e.g. "f(a,b) = f(b,a)")
- idempotence / fixed points where claimed
- what happens at every boundary of the domain

Invariants must be executable: each one becomes a test (see §2).

### 1.5 Mathematical basis
One of:
- **(a) Derived** — show the derivation from stated assumptions, or
- **(b) Cited** — cite the standard result (textbook, paper, reference implementation)
  with enough precision that a reviewer can verify it, or
- **(c) Heuristic, labeled** — state plainly "this is a designer-chosen heuristic,"
  give the reason for the choice (intuition, precedent, tuning), and state the
  falsification test that would retire it (see §4).

What is never acceptable: a formula presented with the *typography* of derivation
(Greek letters, subscripts, "where…") but the *substance* of (c) undisclosed.
That is pseudomathematics, and this contract exists to refuse it.

### 1.6 Semantic interpretation
- What DellMatrix claims this quantity MEANS (one paragraph, plain language).
- What it explicitly does NOT mean (the anti-readings). Example pattern:
  "Overlap fraction measures shared area of two disks. It does NOT measure truth,
  agreement, importance, or relationship quality."
- Which ledger firewall or name-collision register it respects (for any term that
  already names something else in the repo).

### 1.7 Tests
Per §2 below. No proposal is admitted on derivation alone; no proposal is admitted
on tests alone.

### 1.8 Known limitations
- where the equation is known to be weak, arbitrary, or misleading
- inputs that produce degenerate but "valid" outputs (e.g. all ideas at (0,0))
- the conditions under which the equation should be distrusted or disabled
- the review date or condition that triggers re-examination

---

## 2. TEST REQUIREMENTS

Every admitted equation ships with:

1. **Unit tests** — known-answer cases (hand-computed or cited), including every
   domain boundary and every degenerate input from §1.2.
2. **Invariant tests** — each invariant from §1.4 as an executable assertion,
   run over randomized valid inputs (property-style), not just fixed cases.
3. **Adversarial tests** — inputs designed to break the claimed meaning:
   degenerate geometry, extreme values, and the exact failure modes listed in §1.8.
4. **Honesty tests** — where the equation feeds a display or a gate, a test that the
   displayed/gated value carries its classification label (per §5).

`TEST PASS != CAPABILITY` (GDP-001 §26): tests prove the contract the equation
claims, nothing more.

---

## 3. CLASSIFICATION AT ADMISSION

The proposal states its initial ledger classification from the closed set:

`ACTIVE_VALIDATED` · `ACTIVE_UNVALIDATED` · `DISCONNECTED` · `EXPERIMENTAL` ·
`HISTORICAL` · `DUPLICATE` · `CONTRADICTORY` · `MATHEMATICALLY_UNJUSTIFIED` ·
`RECOVERY_CANDIDATE` · `UNKNOWN`

Rules:
- A new equation may enter as `EXPERIMENTAL` or `ACTIVE_UNVALIDATED`, never directly
  as `ACTIVE_VALIDATED` (validation is earned by tests + review + runtime evidence).
- If an equation already exists for the same semantic quantity, the proposal is
  `DUPLICATE` and must name the canonical entry; second implementations are refused
  (ledger law: no two formulas silently define the same quantity).
- `UNKNOWN` is always an acceptable holding classification. Fabricated certainty is not.

---

## 4. HEURISTIC DISCIPLINE

Heuristics are permitted — DellMatrix runs on judgment in many places — but only
under these rules:

- H1. The heuristic is labeled `HEURISTIC` in code comments, docs, and any UI
  that surfaces its output.
- H2. Every magic constant carries a comment: why this value, what was considered,
  what would change it.
- H3. Every heuristic has a **falsification test**: a stated observation that would
  prove it wrong or useless (e.g. "if the gate rejects >90% of human-accepted ideas
  over 100 trials, the thresholds are recalibrated or the heuristic retired").
- H4. Heuristics on gating paths (accept/reject, growth, authority) are reviewed
  at every phase gate; heuristics on display paths are labeled as estimates.

---

## 5. NO-PSEUDOMATHEMATICS CLAUSE

The following are refused admission, no matter how the proposal is dressed:

- P1. Calling a finite construction "fractal" or "recursive" without a recursive
  scaling law (cf. ledger EQ-GEO-014).
- P2. Calling geometric overlap "truth," "agreement," or "coherence" without the
  coherence≠truth discipline (cf. ledger firewall F3).
- P3. Displaying a computed-but-uncomputed region: any visualization of a quantity
  (voids, channels, fields) that was never computed (cf. ledger §9, no-theater law).
- P4. Reusing a name that already denotes a different mechanism without a firewall
  entry (cf. ledger §10: Verita, Harmonic).
- P5. Constants presented as derived when they are chosen (undisclosed (c)).
- P6. Distance/angle/boundary/center semantics on a geometric display without a
  defined transformation, stated domain, and proven or cited mapping properties
  (the Smith-chart bar: without a proven invertible map, "draw it in a circle"
  is not a principle — ledger EXT-SMI-001).
- P7. Averaging or blending parallel authorities into one number to hide disagreement
  (cf. ledger R4-A5).
- P8. Citing external mathematics as DellMatrix authority without passing this contract.

---

## 6. ADMISSION PROCEDURE

1. Proposal written with the eight fields (§1), proposed classification (§3),
   and tests (§2).
2. Duplicate-authority search: the proposer demonstrates no existing ledger entry
   defines the same semantic quantity (ledger §7 method).
3. Review: at minimum one reviewer other than the author; Director decides on
   new semantic quantities.
4. Ledger entry created (append-only) with classification, evidence, and honesty note.
5. Code merged only through the authorized phase-gate procedure; the ledger entry
   and the code ship together.

Grandfather clause: equations already in the ledger (V1) are NOT required to pass
this contract retroactively — their classifications (`ACTIVE_UNVALIDATED`,
`MATHEMATICALLY_UNJUSTIFIED`, …) already state their standing honestly. Any
*modification* to a ledgered equation re-enters through this contract.

---

## 7. WORKED EXAMPLE (FORMAT REFERENCE)

A proposal for "lens-area fraction" to replace the unjustified sacred-verita
heuristic (ledger R4-A3) would be submitted approximately as:

- **Variables:** `ar, br` radii (float > 0); `d` center distance (float, `|ar−br| < d < ar+br`
  for the vesica case); `A_lens` lens area via the two-segment formula (cited:
  MathWorld Circle-Circle Intersection); `A_union = πar² + πbr² − A_lens`.
- **Domain:** two-circle overlap case only; coincident/contained/separate handled by
  the existing taxonomy (ledger EQ-GEO-004).
- **Outputs:** `f = A_lens / A_union ∈ [0,1]`, dimensionless; allowed to rank edges;
  not allowed to gate truth.
- **Invariants:** `f(a,b) = f(b,a)`; `f → 0` as `d → ar+br`; `f = 1` iff coincident;
  monotone decreasing in `d` for fixed radii.
- **Basis:** (b) cited — standard circle-segment area; derivation in the proposal.
- **Interpretation:** "Fraction of the two disks' combined area that is shared.
  Does NOT measure truth, importance, or agreement."
- **Tests:** hand-computed equal-unit-circle case (`d=1`: `A_lens = 2π/3 − √3/2`);
  property tests for symmetry/monotonicity/bounds; adversarial: near-tangent,
  near-contained.
- **Limitations:** meaningless while all ideas sit at (0,0); radius-from-score mapping
  (ledger EQ-GEO-006) remains unjustified and bounds this metric's honesty.
- **Classification at admission:** `EXPERIMENTAL` (promoted to `ACTIVE_VALIDATED`
  only after tests + review + live-geometry evidence).

---

*Contract V1 — committed on branch `gdp-p0r4`. Violations are defects, not style issues.*
