# DIRECTOR PLAN — Review Queue Truth and No-Silent-Stall Reconciliation

**Date:** 2026-11-16 · **Status:** PLAN DRAFT / independent Uni + Keeper review required · **Authority:** Ace §42 full-capacity and GitHub-first rulings · **Owner of production/code/merge:** Uni. **Author:** Director. **Checker:** Keeper.

**Verified source revision:** merged-main `d1e9c81423d70204865813ad81c914bef69c3c61`; `director-reports/DIRECTOR_REVIEW_QUEUE.md` blob `39a9531f4430bf2d922f00ee5c7e53df294debb2` (133 lines by `wc -l`), `director-reports/INDEX.md` blob `c46a5e3f60ea8286f0602e282b4f3d3152d48592` (279 lines by `wc -l`). The queue has 36 entries in the **Awaiting disposition** table, followed by cadence and workflow record tables. Existing rows include repeated Q-S2.2 material, already-disposed historical #400 and GS-4 questions, and literal `this PR head` instead of a resolvable PR/SHA. The repository's PR and comment record is available, yet outdated queue representations lead to false no-ripe sweeps.

## Objective / nonnegotiable law

One authoritative GitHub review queue, exact item identity, no forgotten ready work, no phantom progress. Keep all open questions and original evidence recoverable. A cycle is a **whole-queue sweep**, not one chosen item. Neither Director nor Keeper can report `nothing ripe` merely because no *new* comment has arrived: an unchanged head with an already-published but unreviewed final checkpoint remains reviewable.

This is **queue and publication hygiene**, NOT a new authority to stamp, merge, modify code, create data stores, waive regression gates or change PLAN/CODE completion.

## 1. Canonical record contract

Each genuinely active item must have the following explicitly typed fields (as columns or linked structured records in the same repository authority):

- `item_id`: stable canonical Grand Plan / Q- / circuit identifier; `title` (human-readable, not a bare number);
- `pr_number`, `head_sha`, `source_receipt_urls`, `last_verified_main_sha`;
- `Director_last_disposition` (enum + URL + scope + timestamp), `Keeper_last_stamp` (enum + URL + head + timestamp);
- `next_missing_gate` (a *specific* unmet condition), `owner`, `review_state` (AWAITING, EVIDENCE_READY, UNDER_REVIEW, HOLD, DISPOSED, SUPERSEDED, PR_ID_UNKNOWN, HEAD_UNKNOWN);
- `updated_at`, `last_examined_at`, and `change_reason` (evidence, head, question, gate, or authority change).

Use PR IDs and exact HEADs from GitHub itself; never infer a HEAD from its title, trust a stale comment that says "at current head", or convert an unknown into PASS. Named placeholders are acceptable **only as explicit typed errors** with owner and next retrieval action. Distinguish an item whose PR is already merged from one whose associated Plan/CODE objective remains open.

For multi-PR objects, one canonical item record may reference several PRs; keep the separate gate/head for each. For one PR carrying multiple genuinely independent questions, retain them separately but share the PR identity. Deduplication is based on canonical work-object **and question scope**, not substring/title equality.

## 2. Migration with exact no-loss accounting

Uni creates a records-only reconciliation of current QUEUE and INDEX. Before editing, export a 1:1 row receipt from source blob to destination status:

`old_source_sha | old_section | old_row_ordinal | canonical_item_id | disposition | active_row_id_or_archive_ref | evidence_urls | reason`.

Retain every distinct pending decision. Move obsolete/closed rows to a **dated history section or archive record linked from QUEUE/INDEX**; do not delete their evidence or imply they have been reopened. Correct stale pointers and duplicate Q-S2.2/GS-4/#400 references by proof against original PRs and the Director/Acting-Keeper rulings. All unresolved asks retain their original owner. If an old row cannot be resolved reliably, keep it in a named **UNRESOLVED_IDENTITY** bucket with its full original text, not as silently dropped work.

The one authoritative queue may use a linked archival file, but not another independently writable live queue. INDEX is navigational, not a rival decision database. Keep original historical versions in Git history.

## 3. No-silent-stall sweep

Each Director :00/:30 and Keeper :15/:45 reads all open queue items, checks current PR HEAD and current published receipts, and classifies three separately:

1. **Ripe:** all evidence published for a scoped decision; a missing answer/stamp MUST be acted upon in this sweep.
2. **Blocked with named gap:** exact missing proof, unreviewed head or role-owned action.
3. **No change:** genuinely unchanged and already correctly disposed at the current head; silence is fine.

Reevaluate **pending unchanged heads**, not only PRs updated after the last watermark. A new head invalidates prior head-bound stamps without deleting the historical stamp. Independent reviewer may review/stamp without waiting for a Director code/merge HOLD to lift; only the merge itself needs that lift. The merge remains serial under Uni with exact-head CI, current §32 freshness and merged-main proof.

A whole-queue report records total active, ripe acted-on, blocked named, unchanged already-disposed, identity-unresolved and trailing. If any item is ripe and no action occurs, record the seat/capacity reason as a defect, not a false `nothing ripe`.

## 4. Failing-first and acceptance suite

Proposed unit: `director-reports/QUEUE_RECONCILIATION_EVIDENCE_2026-11-16.md`; optional read-only validation script owned by Uni only if needed, as a separate authorized hygiene code circuit. **This plan alone authorizes no code.**

- **Q-1 Enumeration:** all 36 active original entries accounted for individually; every source row maps to exactly one active target or archived/unknown receipt; zero silent losses; INDEX links resolve.
- **Q-2 Identity:** every truly active row identifies its exact PR + SHA; unknown ones produce named identity errors and assigned owner, never a fabricated value.
- **Q-3 Duplicate:** repeated Q-S2.2 and historical #400/GS-4 rows classify by object/scope and merge or archive only with links; no open question silently combined into a closed one.
- **Q-4 Stale head:** simulated HEAD change forces REVIEW_REQUIRED; previous exact-head CI/keeper stamp stays in audit but not current gate.
- **Q-5 Unchanged ready head:** an already-published terminal package not stamped by Keeper remains EVIDENCE_READY after any watermark update; a scan with no new comments cannot return `nothing ripe`.
- **Q-6 Director HOLD vs Keeper review:** HOLD blocks merge, but not independent evidence inspection/stamping; tested with #447/#448 interlock scenario.
- **Q-7 No false credit:** records-only queue migration increments neither CODE completion nor strict MWL COMPLETE; PLAN-stage credit is object-bound and independently ruled.
- **Q-8 Regression and merge:** exact-head records-only CI, independent keeper review, §32, Uni-only merge, merged-main file/readback plus zero lost main-side queue updates. Preserve #233/#294/#308 fences and standing #421 stale-edition HOLD.

## 5. Decision/output

**Director disposition:** proposed one bounded QUEUE/INDEX reconciliation plan. Keeper independently challenges semantics and conservation; Uni reconciles the row map against the actual GitHub PR records. This is not complete merely because the draft is published. Once independently accepted, Uni may stage the records-only PR, subject to normal gates. Do not wait for this housekeeping PR to advance unrelated already-ready work.

**Result sought:** every authority sweep advances every ripe item within its capacity, and an unresolved item can never vanish behind a watermark, a duplicated title, a stale head, or an ambiguous placeholder.
