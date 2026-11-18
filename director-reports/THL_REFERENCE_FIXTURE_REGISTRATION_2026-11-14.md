# REGISTRATION — THL REFERENCE MODEL AS GDP PHASE 3/4 TEST FIXTURE

**Registered under:** Director ruling Q-THL3 (THL-SM-01, 2026-11-14):
*"YES. Approve the reference generator and outputs as proposed GDP
Phase 3/4 test fixtures, not a runtime mechanism."*
**Registered by:** Uni, research seat. **Date:** 2026-11-14.
**Repository pin of the evidence:** main
`715bfc21f972973c9e894a76e98f94ea6de77803`.

## What is registered

| Fixture element | Identity |
|---|---|
| Reference generator | `thl_reference_model.py` (THL-SM-01 evidence: PR #419 `director-reports/thl_sm_01_evidence/`; goal workspace `hidden_files/thl_sm_01/`) |
| Model definition | C = { (i, j, k)/√2 : i, j, k ∈ Z, i + j + k even }; nearest-neighbour distance 1; squared distance (di² + dj² + dk²)/2 |
| Generated output | `reference_model.json` — the 177 centres to R = 3, shell/slice censuses as generated, cross-check results |
| Projection artifact | `thl_projection_111.svg` — the (111) projection, 37 centres to d ≤ 2.6, unit circles on the 19 Flower centres |
| Verification companions | `thl_verify.py` + `verify_output.json` (independent censuses, exclusion proof data, covering-lemma sampling); `thl_hcp.py` + `hcp_output.json` (the control construction) |

## Fixture contract — what "fixture" means here

1. **Data, not mechanism.** The fixture is a frozen, known-good
   geometric dataset against which a future Phase 3/4 implementation
   can be tested. Registering it authorizes **no** runtime code, no
   import from product code, no persistence, no spatial authority.
2. **Regeneration is the integrity check.** The fixture is valid only
   while `thl_reference_model.py`, run against its stated definition,
   reproduces `reference_model.json` exactly. Any drift invalidates
   the fixture, not the model — investigate the generator first
   (verify-the-instrument rule).
3. **Pinned expectations** (the values a future implementation must
   match to claim agreement with the reference model): centres to
   R = 3: **177**; Euclidean shells **12/6/24/12/24/8/48/6/36**;
   step shells **12/42/92/162**; (111) slice cumulative
   **7/13/19/31/37**; (100) slice squared-distance census
   **1, 2, 4, 5, 8** with counts **4, 4, 4, 8, 4**; attainable
   squared distances exclude **s2 = 28, 60**; sphere-field
   multiplicity support **{4..8}**, analytic mean **5.9238**;
   exclusive volume **0** (theorem, THL-SM-01 §3).
4. **Estimates stay estimates.** The Monte Carlo multiplicity
   *percentages* recorded in the study are seeded-sample estimates
   (Director's caution, THL-SM-01 ruling). The fixture's pinned
   values above are the exact/analytic ones; the percentages are
   preserved as study record only and must not be used as pass/fail
   expectations.
5. **Cross-check anchor.** The fixture's (111) projection reproduces
   `form/dell_matrix/sacred_geometry.py`'s `flower_centers(rings=2)`
   exactly (distance multisets equal; explicit symmetry fit). That
   file was byte-identical at the pin (blob
   `d30e282688793899f71c1afdab36ddd4af3d1994`); if it changes, the
   cross-check must be re-run before the fixture is used against a
   changed product.
6. **Admission status is separate.** This registration is effective
   now as a *proposed fixture* for the GDP Phase 3/4 line (per
   Q-THL1/Q-SM1 the geometry's admission gate is the Keeper's
   independent reproduction under THL-SM-02, then the Director's
   ruling). Fixture registration does not wait for admission, and
   does not imply it.

## Where it will live when Phase 3/4 opens

To be copied — by the Phase 3/4 circuit, under its own authorization —
into the repository's test-fixture location chosen by that circuit,
with this registration attached. Until then its canonical homes are
the two evidence locations in the table above.

*End of registration.*
