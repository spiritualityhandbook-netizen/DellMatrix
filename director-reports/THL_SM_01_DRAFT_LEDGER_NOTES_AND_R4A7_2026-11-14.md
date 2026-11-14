# THL-SM-01 — SEPARATELY SCOPED PREPARATIONS (DRAFTS — NOT APPLIED)

**Prepared under:** Director directive THL-SM-01, item 7 (2026-11-14),
and rulings Q-SM2 / Q-SM3.
**Status of everything in this file: DRAFT TEXT ONLY.** Nothing here has
been applied to `docs/DELLMATRIX_EQUATION_LEDGER.md`,
`docs/DUAL_LATTICE.md`, or `form/dell_matrix/sacred_geometry.py`. Each
item enters through its own authorized circuit. Wording is offered for
the Director's disposition; Uni asserts no ledger authority.

---

## Part A — Q-SM2 evidence-only ledger annotations

Approved in principle by the Director (Q-SM2): attach sandbox probe
references and bounded findings to EXT-GEO-002, EXT-GEO-004,
EXT-GEO-005; **retain existing classifications**; include the
exclusive-volume correction. Draft annotation texts:

### A-1 — for EXT-GEO-002 (Čech complex / Nerve Theorem), append:

> **Evidence note (sandbox, THL-SM-01, 2026-11-14; classification
> unchanged — RECOVERY_CANDIDATE):** the sandbox Flower study measured
> the nerve phenomenon this candidate method formalises. In the Flower
> ball cover, higher-order intersections persist — overlap multiplicity
> reaches order 4 in the studied pattern (sharing cascade: pairwise
> 39.10% / 31.25% of the sampled field) — so the nerve is *thick*, not
> a pairwise graph. Probes: `hidden_files/flower_sphere_study/`
> (`probe_flower_sphere.py`, `probe_membership_patterns.py`, outputs
> alongside); study: `SANDBOX_FLOWER_SPHERE_FIELD_STUDY_2026-11-13.md`.
> Bounded: regular Flower pattern, finite pattern radius; no product
> semantics attached.

### A-2 — for EXT-GEO-004 (Power diagram / Laguerre), append:

> **Evidence note (sandbox, THL-SM-01, 2026-11-14; classification
> unchanged — RECOVERY_CANDIDATE):** the sandbox Tree study computed
> exclusive-vs-shared volume decompositions for the regular FCC
> arrangement by direct probe — the decomposition this candidate
> method computes in general. Sphere field on FCC centres (unit
> spheres, NN distance 1): multiplicity support {4..8}, mean 5.9238
> (analytic, = sphere volume / volume-per-centre √2/2); bipyramid
> fields n = 3..10 tabulated in the study. **Correction carried with
> this note:** the full-Tree exclusive sphere volume is **zero** for
> the studied arrangement — independently proven in THL-SM-01
> (nearest-neighbour covering argument), superseding the one-layer
> "private caps" reading in the earlier Flower study, which was a
> single-layer artefact. Probes: `hidden_files/tree_of_life_study/`,
> `hidden_files/thl_sm_01/`; studies:
> `SANDBOX_TREE_OF_LIFE_STUDY_2026-11-13.md`,
> `SANDBOX_THL_SM_01_FCC_VERIFICATION_2026-11-14.md`. Bounded:
> regular arrangements only; irregular fields are this candidate's
> open work, per the entry's own caution.

### A-3 — for EXT-GEO-005 (Sphere-packing void facts), append:

> **Evidence note (sandbox, THL-SM-01, 2026-11-14; classification
> unchanged — LEAD_ONLY):** the lead's regular-arrangement facts were
> exercised directly. The FCC completion of the Flower (centres
> (i, j, k)/√2, i + j + k even) was censused exactly: Euclidean shells
> 12/6/24/12/24/8/48/6/36 (cumulative to 177 at R ≈ 3.05); step shells
> 12/42/92/162 = 10k² + 2; attainable squared distances exclude
> s2 = 28 and s2 = 60 (Legendre three-square exclusions — hence no
> √14 or √30 distances); the arrangement's voids are the tetrahedral
> and octahedral holes of this entry. HCP control: identical density
> (0.7405) but step shells 12/44/96/170 and a single Flower-plane
> orientation — the regular-arrangement facts are
> arrangement-specific, exactly as this entry's caution states.
> Probes and verification: `hidden_files/thl_sm_01/` (`thl_verify.py`,
> `thl_hcp.py`, `thl_reference_model.py`); return:
> `SANDBOX_THL_SM_01_FCC_VERIFICATION_2026-11-14.md`.

---

## Part B — Q-SM3 / R4-A7 documentation corrections

Director's ruling: fold into the next authorized documentation
circuit; correct the misleading claims; **preserve historical wording
with supersession notes where required; do not silently rewrite the
original evidence.** Drafts accordingly — both are *additions /
supersession notes*, not silent rewrites.

### B-1 — `docs/DUAL_LATTICE.md`, Origin item 1

Current text: "2D circles → equal units, shared centers, recursive".
The word "recursive" is classified CONTRADICTORY by ledger EQ-GEO-014
(`flower_centers` is a finite construction with no recursive scaling
law). The document already carries a HISTORICAL RECORD banner.
**Draft:** leave the original line untouched; append to the Origin
section:

> *Supersession note (R4-A7): item 1's word "recursive" is not
> supported by the construction it describes — `flower_centers`
> generates finite rings (1 / 7 / 19 centres) with no recursive
> scaling law (equation ledger EQ-GEO-014). The historical wording
> is preserved as evidence of intent; the mechanism claim is
> superseded by the ledger's classification.*

### B-2 — `form/dell_matrix/sacred_geometry.py`, the vesica comment

Ledger EQ-GEO-013 cites this comment at line 143; **at the current
pin (main `715bfc21`) the comment sits at line 157** — the ledger's
line reference has drifted and the applying circuit should re-anchor
it. Current text (line 157):

```python
    # classic vesica — strength peaks when dist ≈ radius (equal circles)
```

The formula it annotates (EQ-GEO-001) gives strength 0.5 at
dist = radius for equal circles and 1.0 at containment — the comment
asserts the opposite of the code. This is a *code comment*, not
historical evidence, so direct correction (not a supersession note)
is the honest form. **Draft replacement:**

```python
    # partial overlap — strength is the linear overlap fraction
    # (ledger EQ-GEO-001): 0.5 at dist == radius for equal circles,
    # rising to 1.0 at containment; it does not peak here.
```

Behaviour change: none (comment only). The applying circuit should
run the module's smoke + `geometry_status` consumers as its regression
evidence, and record the re-anchored line number back into EQ-GEO-013.

---

*End of drafts. Application of any item above requires its own
authorized circuit; this file is the preparation, not the act.*
