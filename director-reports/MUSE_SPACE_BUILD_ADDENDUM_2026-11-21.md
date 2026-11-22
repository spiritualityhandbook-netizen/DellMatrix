# MUSE SPACE BUILD ADDENDUM — GP-E25 S1–S3 BUILT (2026-11-21)

**Status:** CODE BUILT as a prepared package. Part 0's PR #503 is
merged and closed, so under the Eight-Part rule (no new small PRs)
this build does not open a PR: it sits as one commit on top of main
`b83a53ec105df9a78f4c98abde73e7d5d9c6b914` in the GP-E25 lane clone
for the main session to place. Slice definitions of record:
`MUSE_SPACE_BUILD_RECORD_2026-11-20.md` section 5; design of
record: Edition 1 file `04_MUSE_SPACE_DESIGN.md`.

## What was built

- **S1 — snapshot reducer** (`form/muse_space_snapshot.py`).
  Deterministic, offline, standard-library. Consumes the pinned
  canonical inputs (MWL register JSON; Edition 1 crosswalk
  candidates file 01; Dell 100-address baseline file 05; dependency
  DAG file 08; design file 04; the build record) and emits the
  file-04 read model (`schema_version`, `github_snapshot_time`,
  `source_main_sha`, `source_blob_shas`, `retrieval_coverage`,
  `unresolved_sources`, `nodes`, `typed_edges`, `belts`,
  `contradictions`, `perspectives`, `derived_metrics`) plus a
  sha256 `content_identity` over the canonical serialization.
  Nodes: 185 `mwl:` work objects, 100 core `dell:` addresses +
  reserved `dell:151`, `gp:` candidates, 28 `gp:e*` circuits.
  Edges: crosswalk aliases as PROPOSED `ALIAS_OF`; DAG dependencies
  as INFERRED `DEPENDS_ON` (the DAG record is pinned at an older
  main, named as a STALE contradiction in the Sync Mirror feed).
  PROPOSED/INFERRED edges never enter canonical counts.
- **S2 — static exported view** (`form/muse_space_views.py`).
  The seven views of file 04 section 5 rendered from one snapshot
  into a single self-contained HTML export, labeled `AS_OF` with
  the exact pin; Future View carries the persistent PROJECTION
  watermark; Connection Web discloses drawn/shown/total; all
  source text HTML-escaped; Pending Edits shows local-drafts-only
  with submission disabled (out of scope per the build record).
- **S3 — live revalidation** (`revalidate()` / `offline_status()`
  in the snapshot module). A changed main or changed source blob
  marks the affected source STALE by name; offline status reports
  the pinned snapshot and its age with authority actions disabled.

## Evidence

- Suite `form/muse_space_test.py` (registered in `form/regress.py`
  LIST in the same commit — code-stage step zero): written
  failing-first (RED 0/1, module absent), now **31/31**.
- **S1 acceptance (fresh-clone determinism): PROVEN.** A fresh
  clone at pin `b83a53ec` and the lane clone, both reducing at
  `--pin b83a53ec`, emit byte-identical canonical output
  (sha256 `41a95fb8267f65e678e1142afd02b96307a1dfcd173d619d8ba06
  3e812d5069c`); the suite also passes 31/31 inside the fresh
  clone. (First comparison attempt differed because the lane
  clone's HEAD had advanced to the build commit — a different pin,
  correctly a different snapshot; the proof was re-run at one
  identical pin.)
- Mutant control: alias confidence PROPOSED → VERIFIED made the
  suite fail exactly the intended check (30/31); reverted by
  inverse edit; post-revert 31/31 and a clean tree.
- Spot regression (no full campaign in this lane):
  `form.gate_reconciliation_test` 41/41,
  `form.resumability_checkpoint_test` 10/10; regress LIST ==
  intended entries (310 == 310, none discovered-but-unlisted).

## Limitations / non-coverage (honest)

- **Belts:** the pinned register JSON carries no per-row
  PLAN-readiness or CODE-certification source separate from the
  register status, and `master_list.py` derives no belt split.
  The Two Belts view therefore shows the canonical MWL strict
  count as its own number and marks the PLAN and CODE belts
  `EVIDENCE_UNAVAILABLE` with the reason — file 04 section 5B
  forbids substituting the historical belt totals. Deriving real
  belts needs a canonical belt source (Part V's reconciliation
  lane owns that question).
- **Acceptance:** file 04 section 6's 15-case UI acceptance
  (M-01..M-15, browser act at the built surface's exact head) is
  NOT run by this lane; S2 here is the build record's *static
  exported view*, not the interactive UI. M-01's substance
  (pin/row identities) is covered at reducer level by the suite.
- Inputs not yet consumed as nodes: SYSTEM-001 contracts,
  FI-001..FI-019, UU/DC decision registers, PR/CI evidence — the
  design lists them; this build covers the machine-readable
  canonical files present at the pin and names the boundary here
  rather than fabricating the rest.
- GP-E25 claims no MWL register credit (build record section 6);
  no register rows were touched.

## Remaining for GP-E25

1. Main-session placement of this package (the commit below) into
   a living Part PR or a Director-authorized landing, then
   exact-head CI + the Part 0 campaign slot.
2. The 15-case UI acceptance at the landed head.
3. Belt derivation once Part V's reconciled crosswalk / a
   canonical belt source lands.

## Consumer wiring — UNIMPLEMENTED (2026-11-22)

Director 7075379361 (PR #510) withdrew the seven-day pin freshness
gate and clarified the governing consumer contract: AS_OF/source
pin explicit, STALE marking on revalidation, offline age display
with authority actions disabled. That contract is implemented at
LIBRARY level only (`revalidate()` / `offline_status()` in
`form/muse_space_snapshot.py`) and is now pinned by the suite's
`contract_*` checks, including the negative control that no age
refusal exists. The wiring is **UNIMPLEMENTED** and awaits
placement:

- No production consumer calls `offline_status()` or
  `revalidate()`; their only caller is the suite.
- The S2 export CLI (`form/muse_space_views.py`) accepts no pin
  argument; it always renders at the checkout HEAD.
- No surface displays the offline age or acts on a STALE
  revalidation result.

Until a consumer is placed, the contract holds only where the
suite exercises it; nothing in the shipped tooling refuses,
warns, or labels on pin age, and no action is disabled by
`offline_status()` in any live path.
