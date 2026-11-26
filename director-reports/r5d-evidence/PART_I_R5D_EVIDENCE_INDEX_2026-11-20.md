# R5-D EVIDENCE INDEX — Part I Carry-Forward (2026-11-20)

**Status: R5-D IMPLEMENTATION HOLD CONTINUES.** This index is a
records artifact. It assembles the existing R5-D evidence chain
in one place for the Part I PR; it contains no product code, no
new evidence claims, and no implication that the hold has moved.

- Register anchor: MWL **#173** (retention/compaction contract)
  and GP-E05. R5-C POLICY is ADOPTED (Director FINAL BINDING
  7026062701; records landing via PR #498, head da42d14).
- Unlock path, in order: **Keeper challenge of prep head
  `13b33fa7972a4ec878d7dcd763131d88c455e03e`** (outstanding,
  expanded scope: lock acquisition order vs `owner_state_lock`;
  note/load/save writer census; `internet_off` early-return
  preservation; preflight-before-every-S7-first-effect;
  per-process lost-update acceptability) → Director bounded
  implementation authorization (at most the S7 subset) → only
  then code, inside the Part I PR.

## The failing-first suite (carried into this PR)

- `form/r5d_history_retention_test_spec.py` — the prep suite,
  content **byte-identical** to the artifact under the Keeper
  challenge (`hidden_files/r5d_prep_clone/form/
  r5d_history_retention_test.py`, verified identical to the
  `r5d_clone` copy). It ships under the `_spec` name in this PR
  ONLY because `form/regress.py`'s `intended_entries()` turns an
  unregistered failing `*_test.py` into a CI-smoke RED (failure
  class proven on PR #503, run 44758805458). **R5-D unlock step
  zero:** rename back to `form/r5d_history_retention_test.py` and
  register in `form/regress.py` LIST in the same commit as the
  authorized implementation.
- Measured on current main af2519b6: **3/22 PASS** — the
  documented prep result (the suite is failing-first by design;
  19 checks encode the R5-C policy contract the held
  implementation must satisfy).

## Evidence chain (goal workspace, `hidden_files/`)

All under `~/workspace/goals/dellmatrix-capability-circuits/
hidden_files/`:

| Artifact | Class |
|---|---|
| `R5D_PREP_2026-11-19.md` | prep record — failing-first package, caller census 111 (= 98 `note_seed` + 13 `note`; door-internal `form/open.py:365` inside the 13) |
| `R5D_CLASSIFICATION_2026-11-19.md`, `r5d_classify.py`, `r5d_classify_emit.py` | per-site classification — of 60 buildable history-write sites only 25 INVENTORY-CLEAN; smallest lawful subset **S7** = radial_drift, internet_on, internet_off, sandbox_on, sandbox_off, enhance_on, enhance_off (save/visual excluded — write files at cap; live_visual excluded — starts an HTTP listener) |
| `r5d_ff_package.md` | failing-first package (posted 7027876063) |
| `r5d_path_proof_package.md`, `r5d_path_proof_receipt_2026-11-19.txt` | path proofs A=24 + B=36 + C-HOLD=50 + DOOR=1 |
| `r5d_executable_package.md`, `r5d_executable_receipt_2026-11-19.txt` | executable package for the bounded subset |
| `r5d_rd_receipt_2026-11-20.txt`, `r5d_rd_run1.txt`, `r5d_rd_run2.txt`, `r5d_rd_clean_run.txt` | refusal-depth battery **R5RD 36/94** — the only legitimate no-note early return in S7 is `internet_off` → `{"ok": True, "on": False}`; the logical cap binds FULL in-memory history, not persisted bytes (`serialize()` persists only `history[-24:]`; ~2,400,152B logical vs 1,920,122B persisted); cross-process admission coordination ABSENT |
| `r5d_per_site_run1.txt`, `r5d_per_site_run2.txt` | per-site runs |
| `r5d_clean_clone_receipt_2026-11-19.txt`, `r5d_clean_verify/`, `r5d_clone/`, `r5d_prep_clone/` | clean-clone verification + prep clones (prep at `7aea4c2`, revision at `13b33fa`) |
| `r5d_publication_package.md` | publication package |

## Policy facts the implementation must satisfy (R5-C, adopted)

- **P1 (Candidate B):** retention bound = 10,000 entries AND
  2 MiB canonical serialized history, first-reached binds.
- **P2:** pre-mutation typed refusal / proven rollback;
  post-mutation throw forbidden.
- **P3 (S2):** report-only aggregate — WARN ≥512 MiB, CRITICAL
  ≥1 GiB; no hard quota.
- **P4:** legacy preserve-first (LEGACY_OVER_BUDGET;
  unchanged-history saves write through; new growth refused; M2
  non-destructive archive default; pruning needs explicit owner
  confirmation).
- **P5:** universal sanitize-at-capture via `sanitize_text`
  (with its stated limitations).
- **P6:** shown/total truthfulness; power-loss durability
  UNKNOWN/unverified.
- Three cut sites on current main: `form/open.py` history cap
  24, `form/persist.py:378` `[-24:]`, `form/persist_rest.py:643`
  `[:120]`+`[-24:]` (plus `macro_seed` `[:200]`).
- Save layer is fail-closed under fault/crash injection at
  INTEGRATION tier; power-loss durability remains UNKNOWN.
