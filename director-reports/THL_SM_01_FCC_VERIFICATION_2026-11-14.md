# THL-SM-01 — INDEPENDENT FCC VERIFICATION: RETURN

**Circuit:** THL-SM-01 — Tree of Harmonic Life admission preparation
(Director directive, 2026-11-14; authority Ace → Director → Uni).
**Seat:** Uni, DellMatrix research seat (sandbox).
**Pinned repository state:** main `715bfc21f972973c9e894a76e98f94ea6de77803`.
The one product file used, `form/dell_matrix/sacred_geometry.py`, is
byte-identical at that pin and at the cross-check import root
(blob `d30e282688793899f71c1afdab36ddd4af3d1994` both places).
**Stop conditions honored:** no FCC promotion, no semantic invention,
no product implementation, no certification claim. The Tree and THE
CHORD remain derived witnesses throughout. Nothing in the product was
modified; no canonical state, persistence, resonance, or spatial
authority was touched.

## 1. Sources recovered

| Source | Path |
|---|---|
| Original exact-census probe | `hidden_files/tree_of_life_study/probe_tree_exact.py` |
| Original field (Monte Carlo) probe | `hidden_files/tree_of_life_study/probe_tree_fields.py` (seeded, `numpy` 1.26.4 at re-run) |
| Original corners probe | `hidden_files/tree_of_life_study/probe_tree_corners.py` |
| Recorded outputs | same directory: `exact_output.json`, `fields_output.json`, `corners_output.json` (+ `*_clean.json`) |
| Study under verification | `SANDBOX_TREE_OF_LIFE_STUDY_2026-11-13.md` (Parts I–III context: `SANDBOX_FLOWER_SPHERE_FIELD_STUDY_2026-11-13.md`, `SANDBOX_FLOWER_POLYGON_LADDER_STUDY_2026-11-13.md`) |
| New verification code + outputs | `hidden_files/thl_sm_01/` (`thl_verify.py`, `thl_hcp.py`, `thl_reference_model.py`, `verify_output.json`, `hcp_output.json`, `reference_model.json`, `thl_projection_111.svg`, `rerun_*.json`) — also attached to the delivery PR under `director-reports/thl_sm_01_evidence/` |

## 2. Reproduction (original probes, re-run as-is)

Commands: `python3 probe_tree_exact.py`, `python3 probe_tree_fields.py`,
`python3 probe_tree_corners.py` in the study directory.

| Probe | Expected (recorded) | Observed (re-run) | Result |
|---|---|---|---|
| exact | `exact_output.json` | deep-equal, zero diffs | **REPRODUCED EXACTLY** |
| corners | `corners_output.json` | deep-equal (tol 1e-6) | **REPRODUCED EXACTLY** |
| fields (seeded MC) | `fields_output.json` | deep-equal (tol 1e-6) | **REPRODUCED EXACTLY** — sphere multiplicity {4: 10.93%, 5: 11.59%, 6: 51.90%, 7: 24.94%, 8: 0.64%}; mean MC 5.9278 vs analytic 5.9238; exclusive fraction 0.0 over 400,000 in-solid samples |

## 3. Independent verification (new code, different construction)

Independence method: the point set was rebuilt by the **conventional-cell
construction** (cubic cell corners + face centers, cell edge √2) instead
of the original probes' parity filter, and the two constructions were
proven set-equal at R = 1.05, 2.05, 3.05 before any census was taken.
All counting is exact integer arithmetic in scaled coordinates
(centers (i, j, k), i + j + k even; squared distance = s2/2,
s2 = di² + dj² + dk²).

| Claim (study) | Independent result | Verdict |
|---|---|---|
| Euclidean shells: 12/6/24/12/24/8/48/6/36; cumulative 13/19/43/55/79/87/135/141/177 | Identical counts and cumulative, shell by shell | **VERIFIED (exact)** |
| Step shells 12/42/92/162 = 10k² + 2 | BFS on the independently built set: 12/42/92/162. Envelope honesty: shell-4 points lie within Euclidean distance 4.0 < the 4.6 generation radius, so the finite envelope cannot truncate shells ≤ 4 | **VERIFIED (exact)** |
| (111) slice is a Flower layer: cumulative 7/13/19/31/37 | Identical | **VERIFIED (exact)** |
| (100) slice is a square flower | Slice census (s2, count) = (2,4), (4,4), (8,4), (10,8), (16,4) → squared distances 1, 2, 4, 5, 8 with Z² multiplicities — exactly a square-lattice layer census | **VERIFIED (exact)** |
| √14 never occurs as a distance | s2 = 28 is attained by **no integer triple at all** (exhaustive), hence by no FCC difference vector. Stronger: the complete gap list for even s2 ≤ 80 is exactly {28, 60}, and both are precisely the values forbidden by **Legendre's three-square theorem** (28 = 4·7, 60 = 4·15, with 7 ≡ 15 ≡ 7 mod 8); every attained value is three-square-legal. The next excluded distance after √14 is **√30** (s2 = 60), same theorem | **VERIFIED + EXTENDED (theorem)** |
| Sphere-field multiplicity ∈ {4..8}, mean ≈ 5.92 | Analytic mean = (4π/3) / (√2/2) = **5.9238** (volume-per-center from the cell construction: √2/2 exactly). Independent sampling found max multiplicity **8** with a witness point (0.461, 0.703, 0.453); never above 8 | **VERIFIED** |
| Exclusive volume of a sphere in the full Tree = ZERO | **Exact proof, not Monte Carlo.** For any point x in the central unit ball, some nearest-neighbour direction ĉ satisfies x·ĉ ≥ \|x\|/√2 (the 12 NN directions have angular covering radius exactly 45°, attained at the six axis directions — verified by 400,000-direction sampling: min of max-dot 0.7077 against the theoretical 1/√2 = 0.70711, axis directions attaining it exactly). Hence min over neighbours of \|x − c\|² ≤ \|x\|² + 1 − √2\|x\| ≤ 1 on [0, 1], with equality only at x = 0 (the centre itself, at distance exactly 1). No point of the sphere is exclusive. The MC's 0.0 was a theorem all along | **VERIFIED (theorem)** |
| Volume per centre √2/2; packing density π/(3√2) ≈ 0.7405 | Recovered identically from the cell construction | **VERIFIED (exact)** |

One instrument note, recorded for honesty: an in-plane
nearest-neighbour spot-check inside the verifier sampled points near
the generation envelope, whose in-plane neighbours fall outside the
ball; interior points show exactly 6. The slice censuses above are the
exact evidence and are unaffected.

## 4. FCC vs HCP — the comparison the admission question turns on

HCP was constructed exactly (ABAB stacking of triangular layers,
layer height √(2/3), B-offset (a1 + a2)/3; squared distances kept as
exact rationals in the adapted coordinates) and put through the same
censuses. Headline measurements:

| Measurement | FCC | HCP |
|---|---|---|
| Coordination (nearest neighbours) | 12 | 12 (6 in-plane + 3 above + 3 below) |
| Volume per point / packing density | √2/2 / 0.7405 | √2/2 / 0.7405 — **tie** |
| Step shells 1–4 | **12 / 42 / 92 / 162** (= 10k² + 2) | **12 / 44 / 96 / 170** — the graphs are not isomorphic; the 10k² + 2 law is FCC-only |
| Euclidean shells | 12, 6, 24, 12, 24, … (isotropic) | Diverges at once: extra shell at d² = 8/3 (the two same-column sites two layers away); anisotropic census |
| Flower-plane orientations through a centre | **4** ({111} family) | **1** (basal only; 22 candidate normals tested) |
| Site orbits under translations | 1 (Bravais lattice) | 2 (A and B; no structure translation maps A → B) |
| Indexing | Integer triple (i, j, k), i + j + k even — the HarmonicLattice's own (h, v, f) form | (i, j, m) + layer parity; layer height √(2/3) is irrational in any cubic frame |

### Decision matrix (Director's five criteria)

| Criterion | FCC | HCP | Reading |
|---|---|---|---|
| Mathematical consistency | Valid Barlow packing; Bravais lattice (group structure, one orbit) | Valid Barlow packing; lattice + 2-point basis | **Tie** on validity; FCC simpler in kind |
| Symmetry | Cubic, isotropic shells, one site orbit | Hexagonal, anisotropic shells, two site orbits | **FCC** — and cubic is the symmetry of DellMatrix's own structures |
| 2D Flower compatibility | Flower layer in 4 orientations through every centre; (111) projection reproduces the product's Flower **exactly** (§5) | Flower layer in 1 orientation only | **FCC, decisive** |
| Deterministic indexing | Pure integer triples with a parity rule; every census above is integer arithmetic | Deterministic, but needs a basis flag and an irrational layer height | **FCC, decisive for DellMatrix** |
| DellMatrix's stated requirements | The Tree was *defined* as the Harmonic Cube's completion; FCC **is** the cube's corners + face-centres completion, and THE CHORD's 177 centres are FCC centres | No relationship to the cube; THE CHORD's centre set is not an HCP set | **FCC, decisive** |

**Conclusion of the comparison (evidence, not promotion):** HCP ties
FCC only on packing validity and density — the two criteria that are
indifferent to DellMatrix. On every criterion that references the
system the geometry must serve, FCC is the unique fit. If a canonical
3D construction is admitted, the evidence in this return supports FCC
and does not support HCP. The admission decision itself is **not**
taken here; it belongs to the Director under the Mathematical
Admission Contract, in the GDP Phase 3/4 line per Q-SM1.

## 5. The reference model + reproducible 2D projection (deliverable 5)

`thl_reference_model.py` defines the model exactly:

> **C = { (i, j, k)/√2 : i, j, k ∈ Z, i + j + k even }**, nearest-neighbour
> distance 1, squared distances (di² + dj² + dk²)/2.

and emits the 177 centres to R = 3 (`reference_model.json`). The (111)
layer is projected with the orthonormal basis e1 = (1, −1, 0)/√2,
e2 = (1, 1, −2)/√6. Cross-check against the product
(`sacred_geometry.flower_centers(rings=2)`, byte-identical file at the
pin): both sets have 19 centres; their **pairwise-distance multisets
are equal**, and an explicit hexagonal symmetry maps the projected set
onto the product's Flower (fit found at symmetry index 0 — the
projection basis lands on the product's own orientation). The 2D
Flower in the live product **is** the (111) shadow of this 3D model.
Projection artifact: `thl_projection_111.svg` (37 centres to d ≤ 2.6,
unit circles drawn on the 19 Flower centres) — regenerated by the
script, byte-reproducible from the definition above.

## 6. Facts / boundary-dependent / design choices (directive item 4)

**Mathematical facts** (intrinsic to the infinite arrangement):
coordination 12; density π/(3√2); the attainable-distance set and its
exclusions (s2 = 28, 60, … — three-square theorem); step-shell counts
as invariants of the infinite neighbour graph (shells 1–4 as computed,
envelope-proven); multiplicity support {4..8} and its density-theorem
mean 5.9238; exclusive volume exactly zero (proof in §3); slice lattice
types (triangular (111), square (100)); FCC's four Flower orientations;
HCP's step shells 12/44/96/170 and single Flower orientation.

**Finite-boundary-dependent** (exact, but only as stated): the ball
censuses (cumulative 13…177) describe the ball of radius ≈ 3.05 about
one centre; the slice census rows describe layer ∩ ball; all Monte
Carlo fractions are seeded estimates (reproduced exactly, still
estimates — their analytic counterparts are the facts above).

**Design choices** (not mathematics): adopting FCC as *the* completion
(evidence-backed by §4, still a choice until admitted); the
nearest-neighbour distance = 1 normalisation; calling the
centre-ball census "the Tree"; THE CHORD as the harmony reading of the
centre set; every question of what the geometry *means* for ideas
(radius, semantics) — untouched by this circuit, per orders.

## 7. Separately scoped preparations (directive item 7)

Prepared as drafts, **not applied** — they enter through their own
circuits: `THL_SM_01_DRAFT_LEDGER_NOTES_AND_R4A7_2026-11-14.md`
(delivered with this return) contains (a) the Q-SM2 evidence-only
annotation texts for EXT-GEO-002, EXT-GEO-004, EXT-GEO-005 with
classifications retained and the exclusive-volume correction included,
and (b) the Q-SM3 / R4-A7 correction drafts: the `DUAL_LATTICE.md`
"recursive" supersession note and the `sacred_geometry.py:143`
comment correction, both drafted as supersession-preserving edits
(original wording preserved, note appended — nothing silently
rewritten).

## Anticipated probes

1. *"Is this certification of the sandbox numbers?"* No. It is
   independent reproduction + independent re-derivation, reported with
   its methods. Certification is the authorities' act.
2. *"Does the exclusive-volume proof depend on the FCC choice?"* The
   proof uses the 12 NN directions of the FCC centre; an HCP centre
   has a different neighbour-direction set (anticuboctahedron) — the
   same covering argument would need its own check there. The claim
   verified is the Tree (FCC) claim, as scoped.
3. *"Why is √30 in this return when the study named only √14?"* The
   exclusion structure is a theorem, not a list of anecdotes: the
   verifier enumerated the full gap set to s2 ≤ 80 and both gaps fall
   under the same theorem. Reporting only √14 would understate the
   verified fact.
4. *"Did anything in the product change?"* No. One product file was
   read (imported) for the §5 cross-check; nothing was written.

## Questions for the Director

- **Q-THL1.** With reproduction, independent verification, and the
  FCC-vs-HCP matrix now on record, is U-1's remaining step solely the
  admission ruling itself, or is a further evidence class required
  (e.g., a Keeper-side independent rerun of `thl_verify.py`)?
- **Q-THL2.** Should the HCP comparison be preserved as a permanent
  appendix to any future admission record, so the road not taken stays
  auditable?
- **Q-THL3.** May the reference model (`thl_reference_model.py` +
  outputs) be proposed as a GDP Phase 3/4 test fixture — data, not
  mechanism — when that line opens?

## Unresolved questions carried forward

U-1 (admission decision — now evidence-complete, awaiting the ruling),
U-2 (negative-space product semantics), U-3 (irregular-field overlap
metric, R4-A3/R4-A5), U-4 / Q-F1 (idea radius), U-5 (higher-order
overlap semantics in product), U-6 (live positions at (0,0)). This
circuit closes none of them by itself; it removes "the 3D construction
is unverified" from the list of things standing in U-1's way.

*End of THL-SM-01 return. Evidence: `hidden_files/thl_sm_01/` and the
delivery PR's `director-reports/thl_sm_01_evidence/`.*
