# C5 GROUNDING — CURRENT-MAIN DELTA (2026-11-17)

Reconciliation of PR #444's dated grounding report against current main,
per Director EXE comment **6961110373** on PR #444 (2026-11-17):
DISPOSITION — HISTORICAL GROUNDING ACCEPTED AS DATED; CURRENT-STATE
PREMISE SUPERSEDED; NO MERGE AUTHORIZATION AT STALE HEAD
`d116b30a4a5e28a9051935b58cc4b34a0ca8f1be`.

Grounded at main **692e5ca65db3f4feb05a8defbb10ac28bfe54357**
(verified by direct clone, 2026-11-17). Records only. No credit.

---

## 1. WHAT THIS DELTA DOES AND DOES NOT DO

- The dated report `C5_GROUNDING_2026-11-15.md` (PR #444, grounded at
  main `04abc1ea`) is **preserved unedited**. Its claims were accurate
  for their stated snapshot. History is not rewritten.
- This delta records what changed on main after that snapshot, with
  exact merged code references, and classifies each C5 slice against
  current-main evidence only.
- The #444 report's headline current-state claim — "the confirmed
  formula is implemented nowhere" — is **FALSE AS A CURRENT CLAIM**
  (Director 6961110373). It remains true only as a dated 2026-11-15
  statement.
- The #444 §4 failing-first probe (4/4 FAIL at `04abc1ea`) is
  **historical evidence**. It must not be rerun as proof of a current
  defect. It was not rerun for this delta.
- This delta closes **no** unbuilt slice. Unbuilt slices stay open
  under their own gates (§4).

## 2. WHAT LANDED ON MAIN AFTER THE #444 SNAPSHOT

| Step | PR | Merge | Effect on the C5 contract |
|---|---|---|---|
| C5 REPLAN (Ace ruling) | (record on main: `C5_REPLAN_2026-11-15.md`) | — | C5 restructured into C5R.1–C5R.6: elastic holding, total visibility, organization metadata, door operations, advisory organizer; the S formula demoted to the default ordering LENS. This replan, not #444 §3, is the build path that was executed. |
| C5R.2 SEE | #465 | merged 2026-11-17T01:38:37Z | `Nursery.query` / `fetch_many` read-only SEE service: browse + search with totals, stable cursor paging, honest typed refusals. |
| C5R.3 ORGANIZE | #467 | merged | Every proposal carries topic / tags / cluster plus a seed "birth certificate"; Ace relabeling with signed receipts; SEE grouping by topic / tag / cluster. CODE COMPLETE settled 2026-11-17. |
| C5R.4 LENS | #473 | merge `8d5c80280a132d9bae516d6536c12069d4a74c8c` | The S formula implemented as lens-v1 and made the default Nursery ordering; `Program.ranked_proposals()` migrated onto `Nursery.query`; the old Inspire recipe retired as ordering authority. Director SCOPED CODE COMPLETE 6959492051 + Keeper CODE CREDIT CONFIRMED 6959597046 + Uni settlement 6959619312 (CODE +1, scoped). |

## 3. EXACT MERGED CODE REFERENCES (current main 692e5ca6)

All in `form/dell_matrix/nursery.py` unless noted:

- `LENS_VERSION = "lens-v1"`; `LENS_WEIGHTS = {"link": 0.40,
  "ace": 0.25, "fresh": 0.20, "novel": 0.15}` (nursery.py:489–491) —
  the confirmed weight tuple, present in code.
- `LENS_FADE_FUNCTION = "reciprocal-fade-v1"`;
  `LENS_FADE_LADDER = (14.0, 24.0, 48.0, 96.0, 142.0)`;
  `LENS_FADE_DAYS = {"unclassified": 14.0}` — Ace's fade ladder:
  14 days is default AND minimum; an off-ladder value makes the lens
  refuse `LENS_CONFIG_INVALID` (`_lens_config_error`). A cursor binds
  the lens configuration identity (`_lens_config_identity`);
  mid-traversal configuration change refuses `CURSOR_CONFIG_CHANGED`.
- Lens scoring (nursery.py, `_lens_*` block ending at the score
  assembly ~:1320–1341): S = 0.40·LINK + 0.20·FRESH + 0.15·NOVEL.
  **ACE contributes 0 in v1**: the returned breakdown carries
  `"ace": 0.0` with evidence `"ace": "missing"` and
  `"partial": True` on every score — the missing ingredient is
  disclosed on the record, never invented. A separate `ace_proxy`
  (confirmed lineage via the `supersedes` chain, cycle-safe, broken
  references disclosed as `"partial"`) is computed and returned but
  does **not** enter S.
- `Program.ranked_proposals()` (`form/open.py:1549`): signature,
  pending scope, and membership unchanged; the ORDER is now the S
  lens order served by `Nursery.query` (mode `"browse"`,
  status `"pending"`), with the full score breakdown on each
  returned record. The legacy recipe is retired as this method's
  ordering authority; there is no silent fallback — a SEE refusal
  raises. (This answers #444 probe items A1/A2 at the code level;
  merged-main behavioral proof is on the PR #473 record:
  campaign ×3 GREEN, merged-main smoke GREEN.)
- SEE service: `Nursery.query(...)` (nursery.py:1345) — modes
  `"browse"` / `"search"`; topic / tag / cluster filters over the
  EFFECTIVE topic (stored topic, else the explicit `"unclassified"`
  group; stored bytes never rewritten by a view); `group_by`
  summaries over the full matched set before paging (topic/cluster
  groups partition; tag groups may overlap and report BOTH
  `group_membership_total` and `group_distinct_total`);
  `total_searched` / `total_matches` reported on every page;
  cursor continuation binds owner/mode/filters/sort/page-size and
  the lens configuration — an explicitly changed argument refuses
  `CURSOR_FILTER_MISMATCH`, never a silent ignore.
- C5R.3 organization fields: `Proposal.topic` / `Proposal.tags` /
  `Proposal.cluster` (nursery.py:455–457) with admission validators
  (`validate_topic` / `validate_tags` / `validate_cluster`) and
  fail-closed load staging (`_validate_loaded_organization`).
- L11 PlaneRank tripwire: `form/nursery_c5r4_lens_test.py:399–454` —
  a subprocess import-blocker test that exists precisely because the
  PlaneRank-named surface it guards is **not** PlaneRank (see §4).

## 4. C5 SLICE MATRIX — CLASSIFIED ON CURRENT-MAIN EVIDENCE ONLY

| Slice (card / MWL) | Classification at 692e5ca6 | Evidence |
|---|---|---|
| **C5.Formula — Lens v1** (MWL 140) | **IMPLEMENTED, partial ACE** | §3 references; PR #473 merged `8d5c8028`; credit settled (Director 6959492051 + Keeper 6959597046). S is the default ordering in SEE and in `ranked_proposals()`; the deciding score and its components are on each returned record. ACE ingredient honestly MISSING in v1 (contributes 0, disclosed, scores partial). |
| **Topic grouping** (C5R.3) | **IMPLEMENTED** | topic/tags/cluster on every proposal; SEE filters + `group_by` summaries with partition/overlap honesty (§3). |
| **Top five per topic** (card acceptance) | **NOT IMPLEMENTED** | No top-five-per-topic rule exists in `form/` at this head (grep: no such mechanism in nursery/open/repl; the only "top-5" hits are knowledge_selector's execution window — a different authority, #444 §2.5). Grouping counts exist; a per-topic top-5 display rule does not. |
| **Global pending cap 200 + tombstoned evictions** (card acceptance) | **NOT IMPLEMENTED** | No pending cap and no Nursery eviction/tombstone mechanism in `form/dell_matrix/nursery.py` at this head. The `page_size=200` in the `ranked_proposals()` traversal is a page size, not a membership cap. (Tombstones exist in `form/mandell/semantic_graph.py` for relationship entries — a different mechanism, not Nursery evictions.) The C5 REPLAN's elastic-holding ruling (no retention cap) also stands against silently importing the old card's cap; the conflict is the authorities' to settle, not this delta's. |
| **C5.PlaneRank** (MWL 141) | **NOT IMPLEMENTED** | No PlaneRank implementation in `form/` at this head. The only PlaneRank-named artifact is the L11 tripwire test (§3), whose own comments state the guarded surface is NOT PlaneRank. `ranked_proposals()` / SEE corpus remains Nursery pending proposals; no switchable Plane ordering, no receipt naming an active Plane measure. |
| **C5.Search** (MWL 142; DD-25 + DD-49 as ONE machinery) | **PARTIAL** | The Nursery face exists: SEE browse/search with totals, coverage counts, stable ordered pages, and honest refusals (§3) — the §14.4 browse-first cut is real. The card's unified machinery is NOT built: no single search authority joining DD-25 Discover and DD-49 Resolve was found in `form/` at this head (grep evidence); Dell 35 Discover remains an inventory surface, and no DD-49 search face exists. Search results remain advisory and never become authority — that stop condition holds by construction (SEE is read-only). |
| **C5.Door** (MWL 143; DD-27) | **NOT IMPLEMENTED (policy OFF by law)** | No door-policy machinery in `form/` at this head (grep: "door" hits are the unrelated edit-door / front-door / end-page surfaces). Auto-passage remains OFF under the standing Cycle AUTO-CONFIRM / DD-27 law; no policy-version receipts exist because no door mechanism exists. |
| **Aging** (MWL 177: 3/7/14-day marks; 30-day fade only under inflow) | **NOT IMPLEMENTED as ruled** | No staged-mark aging and no inflow-conditioned fade/eviction in `form/` at this head. Lens v1 FRESH is a different, separately authorized mechanism (reciprocal fade over `Proposal.created` with Ace's ladder tau, §3) — it does **not** discharge MWL 177, and this delta does not claim it does. |

## 5. DISPOSITION OF THE #444 §3 PROPOSAL

The #444 report's proposed circuit — "build C5.Formula from zero" as
a single formula leg extending `ranked_proposals()` in place — is
**RETIRED AS SUPERSEDED**. The formula was in fact built, but via
the C5 REPLAN path (C5R.2 SEE → C5R.3 ORGANIZE → C5R.4 LENS) under
Ace's 2026-11-15 ruling, with the formula as the SEE service's
default lens rather than an in-place rewrite of the old function
body. Retiring the from-zero proposal closes **only** that proposal;
every slice marked NOT IMPLEMENTED or PARTIAL in §4 remains open.

Residue of the #444 §6 questions, for the record:

- Q-C5.1 (FRESH reading): answered for lens v1 by the C5R.4
  definitions — reciprocal fade on Ace's ladder. MWL 177's staged
  marks remain a separate unbuilt requirement (§4).
- Q-C5.2 (topic): answered by C5R.3 — a stored `topic` field with an
  `"unclassified"` effective-topic projection for legacy records.
- Q-C5.3 (cap eviction order): **OPEN** — the cap itself is unbuilt
  and the REPLAN's elastic-holding ruling must be reconciled with
  the old card first (authority decision).
- Q-C5.5 (ACE signal source): **OPEN** — v1 ships with ACE honestly
  missing; the `ace_proxy` is evidence on the record, not a
  definition. Defining ACE remains an Ace/Director decision.
- Q-C5.4 / Q-C5.7 (tie-breaks, display): answered by the build —
  the old recipe is retired as ordering authority (no silent
  fallback), and the score breakdown rides each returned record.
- Q-C5.8 (sequencing of PlaneRank / Search): partially answered by
  events — SEE browse/search landed first; PlaneRank and the
  unified DD-25/DD-49 machinery remain unbuilt and unsequenced.

## 6. ASK

- **Keeper**: independent exact-head review of this delta's §3 code
  references and §4 classifications.
- **Director**: disposition for PR #444 itself — close as
  superseded-by-this-delta, or keep open as the tracking vehicle
  for the §4 unbuilt slices. No merge authorization is requested
  from the historical report; this delta PR stands on its own
  exact-head CI + Keeper review.
- Records only; no PLAN/CODE credit; fences #233/#294/#308,
  #421 CORRECTION_REQUIRED, and #461 ADOPTION HOLD untouched.

— UNI, execution cycle 2026-11-17 15:13 CST, under Director
directive 6961110373.
