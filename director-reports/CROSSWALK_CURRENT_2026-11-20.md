# MWL × EDITION 1 × UNIFIED CENSUS CROSSWALK — CURRENT, 2026-11-20

**Part V (Scoreboard Reconciliation) — plan-stage artifact, PR on branch
`uni/part-5-scoreboard-reconciliation`.** This document brings the
2026-11-15 crosswalk (`MWL_UNIFIED_CROSSWALK_2026-11-15.md`, PR #478)
forward to current main and keeps it there. It is a records/analysis
artifact: it certifies nothing, credits nothing, and changes no status
in any register. Register edits are PROPOSED in
`PART_V_PLAN_2026-11-20.md` and
`CENSUS_CANDIDATE_DISPOSITIONS_2026-11-20.md` only.

**Pins.** Canonical register: `director-reports/master_work_list_items.json`
at main `af2519b6d239ef278397e277210d6da2467c36e5` (185 rows; COMPLETE 40 /
OPEN 84 / PARTIAL 55 / GATED 3 / SANDBOXED 3; active basis 182). Render
verified byte-identical (`master_list.py --check`) at the pin.
Candidate source: `director-reports/GRAND_PLAN_DIRECTOR_EDITION1_2026-11-18/01_SOURCE_CROSSWALK_CANDIDATES.json`
(Edition 1, PR #486; its `source_records` snapshot predates rows
183–185 and the PR #500 settlement — superseded by this document for
current-main purposes). Census source: `THE_GRAND_PLAN_UNIFIED_2026-11-14.md`
Part V (PR #421 head `9e930561afc4eed6a4ef042ba27c122388532d3f`; the
Unified Edition is a records publication, NOT an adoption — see its
2026-11-20 status banner).

**THE STANDING RULE (Ace; Director 7040490093; PR #421 reconciliation).**
The canonical scoreboard is the MWL register on the **182 active basis**,
rendered by `master_list.py` at a pinned main SHA, with STALE/UNVERIFIED
labeling when a rendering's pin is behind main. **The 224 figure is an
internal census only — it is never a scoreboard basis, never a
denominator for progress, and never a target.** Sitting #001 and its
224-basis target were abolished by Ace on 2026-11-15; the live sitting
is #002 (Mon 2026-11-23; ≥42 primary / ≥39 secondary, canonical 182
basis).

**Method.** Mappings are **topical** (same subject / same deliverable,
judged from item texts), never by ID — the registers share the "G-"
prefix for different items (§4 below). No status is imported across any
mapping, in either direction. Every count below was reproduced
mechanically from the register JSON at the pin.

## VERDICT SUMMARY

| Question | Finding |
|---|---|
| MWL rows accounted for | **185 of 185** — 182 carried active, 3 carried sandboxed, 0 unaccounted (§1) |
| Board at pin | **40 / 182 COMPLETE = 22.0%** (COMPLETE 40 / OPEN 84 / PARTIAL 55 / GATED 3 active; 3 SANDBOXED outside the basis) |
| Grand Plan items with an MWL seat | 7 (§3a mapped 6: GP-G03/G08/G09/G10/G11/G21 → #15/#138/#131/#151/#11/#46; + G-31's bounded slice at #34, §3b) — counted once, at the MWL row |
| Historical aliases (Edition 1) | 8 (§2) — proposals until adjudicated; statuses never imported |
| Census candidates with NO MWL seat | **49** — §4 unmapped 22, §7 net 22, §5 steps 5. Each has an individual disposition in `CENSUS_CANDIDATE_DISPOSITIONS_2026-11-20.md` (15 ADMIT-proposed / 10 FOLD / 24 REJECT-census-only) |
| Census arithmetic (for the record) | 185 rows − 4 census-deduped (§3 of dispositions doc) + 49 candidates = 230 all-rows; active basis 182 − 4 + 49 = **227**; the Unified's own published figure was 224 against the older 182-row register. **Census arithmetic is not the scoreboard.** |
| Proven duplicates inside the register | 4 rows census-deduped in Unified §4a (#171/#177/#178/#179) — the register rows still stand; register-side treatment proposed, not applied (§1 annotations) |
| Flagged judgment pairs (§4b) | 4 pairs + 1 overlap cluster + 2 already-deduped — none deducted anywhere; each carries a proposed ruling/flag in the dispositions doc §B |
| Namespace collisions | 12 (MWL G-01..G-12 vs GP-G01..GP-G12) — §4 table; disambiguation rule stated there |
| COMPLETE reconciliation | The 2026-11-15 crosswalk's 35-vs-39 exception (X-1) is CLOSED by the record since: the register reached 39 by authority-credited closures through 2026-11-18, and PR #500 (merged `af2519b6`, 2026-11-20) wrote in #14 COMPLETE + #135 scoped PARTIAL → **40**. Every COMPLETE row's credit trail is in its register text |

---

## 1. FULL MAPPING — EVERY MWL ROW 1..185 AT THE PIN

Reading rules: **CARRIED** = the row is a canonical register row, counted
once in the 182 active basis. **SANDBOXED** = inside the 185 all-rows
count, outside the active basis (Ace's rule). **TOPICAL SEAT** = a Grand
Plan register item's work lives in this row — counted once, here; no
status imported. Annotations for duplicates/pairs are analysis, not
edits.

| MWL # | Item (short title) | Status at pin | Crosswalk disposition |
|---|---|---|---|
| 1 | Loop chained-body repetition repair (PR #348 @ d1ae66d; ALL regression legs TERMINAL GREEN — fw | COMPLETE | CARRIED as MWL-1 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 2 | Loop bounds must be explicit — no silent 8 (PR #360 MERGED d58a3d5; Director SCOPED_CODE_PASS + | COMPLETE | CARRIED as MWL-2 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 3 | Chain parse-refusal must fail closed (PR #345; reconciliation COMPLETE: the one mutation is a P | COMPLETE | CARRIED as MWL-3 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 4 | DD-31 diagnostic capture hardening — failure-only stderr capture in the regress harness (PR #35 | COMPLETE | CARRIED as MWL-4 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 5 | DD31-CI-INTERMITTENT root-cause fix — dd31 suite residue check scoped to its own owner (PR #361 | COMPLETE | CARRIED as MWL-5 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 6 | Sibling whole-directory-assertion inventory (Q-DD31F.2): inventory COMPLETE (267 suites: 1 conf | COMPLETE | CARRIED as MWL-6 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 7 | WORKFLOW role seeds implementation — 31 seeds landed as PENDING proposals, classified, isolated | COMPLETE | CARRIED as MWL-7 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 8 | Governance records publication batch — ALL MERGED: #351 4b1761d, #352 4b04f2f, #353 a7f59c9, #3 | COMPLETE | CARRIED as MWL-8 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 9 | Pulse receipt truth — Dell 25 leaf receipt + Dell 26 disclosure (PR #357 merged fd88d3d; Direct | COMPLETE | CARRIED as MWL-9 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 10 | Predicate infix conditions refuse honestly instead of degrading to truthiness (PR #359 merged 4 | COMPLETE | CARRIED as MWL-10 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 11 | Parallel must mean parallel — concurrency design slice (needs C13 isolation, C3 comparison, C11 | OPEN | TOPICAL SEAT of GP-G11 (Parallel, Dell 62) — counted once, here (§3a). Row #38's audit of Parallel's guarantees is a distinct row, not this seat. |
| 12 | While/Until (64/65) loop conditions: honest refusal surface for unparseable infix conditions (f | OPEN | CARRIED as MWL-12 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 13 | Loop 13 receipted grammar follow-up | OPEN | CARRIED as MWL-13 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 14 | Compose recursion cap follow-up (R17: Compose recursion bound resolves honestly via bound_detai | COMPLETE | CARRIED as MWL-14 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 15 | ForceField gravity wells + evolution levels restore on load (PR #317) | COMPLETE | TOPICAL SEAT of GP-G03 (Gravity Wells) — counted once, here (§3a). Status NOT imported from the GP register. (This row's own register ID is G-04 — the namespace collision in miniature.) |
| 16 | Snapshot retrieval reachability — coverage truth + bounded retrieve_for + cross-process source  | COMPLETE | CARRIED as MWL-16 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 17 | Dock Proposal B — sanitized failure transparency, one fenced-JSON tolerance, session response v | COMPLETE | CARRIED as MWL-17 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 18 | Dell 41 Sanitize copula redaction leak repaired (PR #342; Director scoped certification, Dell 4 | COMPLETE | CARRIED as MWL-18 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 19 | Finalize Studio browser acceptance on integrated revision (= SM-01; certified with noted except | COMPLETE | CARRIED as MWL-19 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 20 | Reconcile merged Core I gate with INDEX/archival status (= SM-05) | COMPLETE | CARRIED as MWL-20 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 21 | Independently reproduce DAF-09 session-escape cleanup (= SM-02; register BLOCKED — Director's i | OPEN | CARRIED as MWL-21 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 22 | Close or precisely retain identical-label/unit-ID ambiguity in Growth lenses (= SM-39, SM-54; l | COMPLETE | Already deduplicated inside the register (SM-39 + SM-54 merged into one row per one-line-one-unit) — no action (§4b item 10). |
| 23 | Repair Dell 37 REPL failure visibility (= SM-16) | COMPLETE | CARRIED as MWL-23 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 24 | Review English Intent.args as a separate end-to-end contract (= SM-11; DD-01 Class E and DD-02  | PARTIAL | CARRIED as MWL-24 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 25 | Dispose remaining per-scope admission/registry certification requests (= SM-04; A1 retained, A2 | PARTIAL | CARRIED as MWL-25 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 26 | Preserve CI-only #233 + long-lived certification artifacts (= SM-03, SM-06; standing preservati | COMPLETE | CARRIED as MWL-26 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 27 | Harden Director–Uni next-best circuit handoff (= SM-07; workflow adopted; standing practice, no | PARTIAL | §4b FLAGGED PAIR with #91 (both carry SM-07) — judgment pair, NOT deducted in any count. Disposition proposed in CENSUS_CANDIDATE_DISPOSITIONS_2026-11-20.md §B (permanent flag; scopes differ). |
| 28 | Stress Seed grammar + error precedence (= SM-58; stress battery landed PR #326, bounded scope c | PARTIAL | CARRIED as MWL-28 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 29 | Reconcile English create + direct REPL handlers with canonical Mandell (= SM-12, SM-13; investi | PARTIAL | CARRIED as MWL-29 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 30 | Deepen reachability for already-supported English actions only (B-2: 37/100 reachable, 63 NO_RO | PARTIAL | CARRIED as MWL-30 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 31 | Audit 17 typed-signature error/coercion contracts (= SM-17, SM-19; per-signature audit landed P | PARTIAL | CARRIED as MWL-31 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 32 | Strengthen Core I single/chain/intercept/live refusal parity (certified with noted boundaries) | COMPLETE | CARRIED as MWL-32 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 33 | Challenge Core II unsupported-role control-head short circuits (certified with noted boundaries | COMPLETE | CARRIED as MWL-33 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 34 | Reconcile legacy flow executor with canonical chain ownership (= SM-15; investigation complete  | GATED | TOPICAL SEAT of G-31's bounded slice (one flow contract, multiple execution paths — the flow_executor divergence) — counted once, here (§3b). This row's wider reconciliation scope remains open beyond the G-31 slice. |
| 35 | Remove/relabel literal Show placeholder output — message-layer R-B repair Director-confirmed bo | PARTIAL | CARRIED as MWL-35 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 36 | Audit message-only Dell descriptions for truthful operations (= SM-23; systematic audit outstan | PARTIAL | CARRIED as MWL-36 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 37 | Preserve first-failure provenance through mixed chain receipts (bounded composition proof lande | PARTIAL | CARRIED as MWL-37 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 38 | Challenge Branch/Parallel/Sequence/Join reported guarantees (= SM-18; bounded recheck landed PR | PARTIAL | Source-ID overlap only (SM-18 also in #39) — deliverables differ; NOT a duplicate (§4b item 9). Also the audit row challenging GP-G11/Parallel's guarantees — distinct from row #11's build seat. |
| 39 | Stress Until/While/ForEach bounds + nested control inheritance (= SM-18; bounded circuit PR #32 | PARTIAL | Source-ID overlap only (SM-18 also in #38) — deliverables differ; NOT a duplicate (§4b item 9). |
| 40 | Reverify Try/Catch error consumption + same-frame reuse | COMPLETE | CARRIED as MWL-40 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 41 | Challenge Commit/Revert exact state + side-effect boundaries | PARTIAL | CARRIED as MWL-41 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 42 | Stress Diff/Set missing-vs-None + baseline handling | COMPLETE | CARRIED as MWL-42 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 43 | Protect Define/Alias/Compose against failed-run persistence (fix landed PR #322 — failed runs p | PARTIAL | CARRIED as MWL-43 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 44 | Stress per-member ManifestSet + typed chainlink transport (= SM-21; member isolation landed PR  | PARTIAL | CARRIED as MWL-44 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 45 | Recheck Guard/Assert failure propagation across control frames (verdict propagation landed PR # | PARTIAL | CARRIED as MWL-45 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 46 | Audit Program/Nursery pair-atomic save + fresh-process load (= SM-35; everyday-save hybrid-pair | GATED | TOPICAL SEAT of GP-G21 (Everyday Save Pair) — counted once, here (§3a); the repair routes through the Q1 C-A circuit; this row is GATED. |
| 47 | Stress checkpoint sealing, rollback, directory-sync failure (= SM-36; DD-04 checkpoint family r | PARTIAL | CARRIED as MWL-47 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 48 | Challenge Exchange journaled import/recovery + receipt disposal (= SM-33, SM-34; includes the G | PARTIAL | CARRIED as MWL-48 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 49 | Check Nursery optimistic concurrency + duplicate confirmation (= SM-31; DD-09 repaired inside,  | PARTIAL | CARRIED as MWL-49 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 50 | Validate semantic-graph journals against derived Program effects (= SM-25; DD-05 graph journal  | PARTIAL | CARRIED as MWL-50 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 51 | Verify supersession crash + acceptance lineage across restart (= SM-30; replacement lineage lan | PARTIAL | CARRIED as MWL-51 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 52 | Test owner namespace collision + foreign-state rejection (DD-12 loud refusal confirmed for prog | PARTIAL | CARRIED as MWL-52 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 53 | Recheck atomic-write orphan-temp + rollback cleanup bounds (crash suite confirmed 67/67, no def | PARTIAL | §4b FLAGGED OVERLAP with #119: this row's remaining scope includes the Q-35.1 orphan-temp cleanup decision that #119 records. Partial overlap (decision vs wider crash-suite scope); no deduction. See dispositions doc §B. |
| 54 | Roundtrip persistent envelopes under corrupt/unknown versions (DD-10 repaired inside, PR #315;  | PARTIAL | CARRIED as MWL-54 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 55 | Plan + verify the Plane-to-Idea bridge / Track D (= SM-27, SM-28) | PARTIAL | Source-ID overlap only (SM-28 also in #57) — deliverables differ; NOT a duplicate (§4b item 9). |
| 56 | Reconcile Idea + semantic-graph node identity through lifecycle (= SM-26) | PARTIAL | Source-ID overlap only (SM-26 also in #57) — deliverables differ; NOT a duplicate (§4b item 9). |
| 57 | Prove nested Idea parent/child + promotion invariants (TD-2 containment BUILT as a candidate pe | PARTIAL | Source-ID overlap only (SM-26 with #56; SM-28 with #55) — deliverables differ; NOT a duplicate (§4b item 9). |
| 58 | Enforce active/faded/superseded participation across all consumers (= SM-29; DD-13 resonance fi | PARTIAL | CARRIED as MWL-58 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 59 | Reconcile GrowthForce label identity with stable Plane unit IDs | COMPLETE | CARRIED as MWL-59 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 60 | Stress knowledge selection, scope, lineage, dependencies (= SM-37) | PARTIAL | CARRIED as MWL-60 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 61 | Trace cause/depend/provenance explanations to real graph evidence (= SM-38; SM-64 theme) | PARTIAL | §4b FLAGGED PAIR with #98 (SM-64 theme overlap) — judgment pair, NOT deducted. See dispositions doc §B. |
| 62 | Test resonance/harmony-to-Nursery proposals at the human gate | PARTIAL | CARRIED as MWL-62 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 63 | Preserve epistemic source/status through views + spatial consumers | PARTIAL | CARRIED as MWL-63 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 64 | Verify dock COMPREHEND/relate_field through policy + Nursery (= SM-44) | COMPLETE | CARRIED as MWL-64 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 65 | Stress stale field-snapshot + agent reconnect boundaries | PARTIAL | CARRIED as MWL-65 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 66 | Exercise agent host-bound idempotency, retries, conflicting envelopes (= SM-45) | PARTIAL | CARRIED as MWL-66 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 67 | Challenge AcceptancePolicy delegation, expiry, revocation chains (= SM-32) | PARTIAL | CARRIED as MWL-67 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 68 | Prove DirectorSession remains recommendations-only (= SM-46) | PARTIAL | CARRIED as MWL-68 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 69 | Reconcile DuoBeta outcome evidence + learning ledger persistence (= SM-41) | PARTIAL | CARRIED as MWL-69 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 70 | Test learned-score saturation + opt-out reversibility (= SM-42) | PARTIAL | CARRIED as MWL-70 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 71 | Harden provider errors, prompt/output validation, protected values (= SM-43) | PARTIAL | CARRIED as MWL-71 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 72 | Keep selfgrow auxiliary ledger isolated from canonical state | PARTIAL | CARRIED as MWL-72 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 73 | Trigger real-browser acceptance for relevant Form runtime changes (= SM-49, SM-50) | COMPLETE | Source-ID overlap only (SM-49 also in #74/#75) — deliverables differ; NOT a duplicate (§4b item 9). |
| 74 | Add browser refusal / PARTIAL / skipped-atom acceptance paths (= SM-49) | COMPLETE | Source-ID overlap only (SM-49 also in #73/#75) — deliverables differ; NOT a duplicate (§4b item 9). |
| 75 | Drive Growth + Console tabs in browser acceptance (= SM-49) | COMPLETE | Source-ID overlap only (SM-49 also in #73/#74) — deliverables differ; NOT a duplicate (§4b item 9). |
| 76 | Regression-test Studio Host/Origin/token + malformed HTTP (= SM-51) | PARTIAL | CARRIED as MWL-76 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 77 | Test Studio state refresh, stale owner state, receipt reconstruction | PARTIAL | CARRIED as MWL-77 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 78 | Prove identical executable semantics across GUI/API/REPL/Python (= SM-52; Director-confirmed CO | COMPLETE | CARRIED as MWL-78 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 79 | Improve Studio keyboard, focus, constrained viewport behavior (= SM-56) | PARTIAL | CARRIED as MWL-79 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 80 | Reconcile offline visual snapshot with canonical state; clear non-live label (= SM-55) | COMPLETE | CARRIED as MWL-80 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 81 | Stress 2D spatial placement, rendering, restore invariants (= SM-40) | PARTIAL | CARRIED as MWL-81 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 82 | Refresh stale in-use docs + README suite-count claims (= SM-62) | COMPLETE | CARRIED as MWL-82 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 83 | Protect Form as source of truth vs frozen JS/preform drift (= SM-63) | PARTIAL | CARRIED as MWL-83 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 84 | Deepen changed-file lint + Python-version compatibility checks (= SM-61) | PARTIAL | CARRIED as MWL-84 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 85 | Harden GitHub workflow permissions + pin third-party actions (Director-approved COMPLETED after | COMPLETE | CARRIED as MWL-85 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 86 | Reconcile regression discovery, suite registration, mutation detection (= SM-57; SM-57 investig | COMPLETE | CARRIED as MWL-86 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 87 | Create repeatable low-memory + large-state performance baselines (= SM-59, SM-60) | PARTIAL | CARRIED as MWL-87 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 88 | Incrementally reduce oversized live-module coupling, no behavior change (register OPEN) | OPEN | CARRIED as MWL-88 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 89 | End-to-end protected-value canaries across outward evidence surfaces (= SM-20; investigation cl | PARTIAL | CARRIED as MWL-89 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 90 | Automate morning-report reconciliation, staleness, next-best recommendations (= SM-09 theme) | PARTIAL | PART V ROW — morning-report reconciliation automation; §4b FLAGGED PAIR with #93 (SM-09): the pair closes together, counted once (see PART_V_PLAN_2026-11-20.md). |
| 91 | Strengthen exact-head / merge-tree / post-merge / fresh-clone gate reconciliation (register als | OPEN | §4b FLAGGED PAIR with #27 (both carry SM-07) — judgment pair, NOT deducted in any count. See dispositions doc §B. |
| 92 | Make workflow resumable: last-good checkpoint + completed-circuit records (partially embodied i | OPEN | CARRIED as MWL-92 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 93 | Standardize morning Director report format (register notes it folded operationally into 72-72's | OPEN | PART V ROW — standard morning report format; §4b FLAGGED PAIR with #90 (SM-09): folded operationally into #90's automation; the pair closes together, counted once. |
| 94 | Connect NBD ranking to real report status, dependencies, improvement candidates; deterministic  | OPEN | PART V ROW — NBD ranking connection. Carries its own internal dedupe ('= SM-48, internal duplicate pair counted once') — no action (§4b item 10). |
| 95 | Strengthen Dell 08 naming, slug collision, skin, legacy-label regression coverage | OPEN | CARRIED as MWL-95 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 96 | Reverify reserved-address refusal / honest unsupported behavior of Bridge and Embed | OPEN | CARRIED as MWL-96 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 97 | Confirm BIMO/persona views remain advisory; cannot bypass host-bound authority (also a Psalm Ma | OPEN | CARRIED as MWL-97 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 98 | Improve traceability from runtime behavior to receipts, outcomes, persisted evidence (end-to-en | OPEN | §4b FLAGGED PAIR with #61 (SM-64) — its own text concedes the theme overlap. Judgment pair, NOT deducted. See dispositions doc §B. |
| 99 | Nursery proposal CARDS (visual, glanceable; confirm / reject / modify) — register DEFERRED, not | OPEN | CARRIED as MWL-99 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 100 | Custom idea shapes in the Nursery (circle, square/box, triangle, custom-drawn outline) — DEFERR | OPEN | CARRIED as MWL-100 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 101 | AI-suggested looks (semantic icons + shape language) as Nursery proposals ONLY — DEFERRED; depe | OPEN | CARRIED as MWL-101 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 102 | Nursery as THE primary decision screen (painting/building feel, fun, organized, never an info d | OPEN | CARRIED as MWL-102 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 103 | SKY perspective (2D; ideas as clouds/shapes; persistent positions; same canonical data as ROOM) | OPEN | CARRIED as MWL-103 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 104 | ROOM perspective (3D; walkable; stackable/openable boxes; never stagnant-looking) — DEFERRED | OPEN | CARRIED as MWL-104 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 105 | Navigation: zoom + tap-to-glide; recursive exploration of ideas within ideas — DEFERRED; depend | OPEN | CARRIED as MWL-105 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 106 | Page set: Plane, Nursery, Dells, Dell Playground, Psalm Matrix — transitions preserve current i | OPEN | CARRIED as MWL-106 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 107 | Navigation placement RESEARCHED online before implementation — DEFERRED; precedes any V-08 buil | OPEN | CARRIED as MWL-107 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 108 | PSALM MATRIX: the AI page — Psalms + personas + status + docking visible there; no second autho | OPEN | TOPICAL SEAT of Unified §5 step 4 (the Psalm Matrix surface) — counted once, here (§3c: step 4 = +0 additions). |
| 109 | AI-talk place: pure English, NOT a chat box — a new interaction concept to invent — DEFERRED | OPEN | CARRIED as MWL-109 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 110 | Human-validation gates: (a) a real AI docked live AND (b) Ace personally working the Matrix, bo | OPEN | CARRIED as MWL-110 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 111 | Reserved neural research: weight-space programming / targeted enhancement of a less powerful AI | OPEN | CARRIED as MWL-111 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 112 | Whole-program certification + REAL_USER_PATH claims — register BLOCKED: certification WITHHELD  | OPEN | Whole-program certification (WITHHELD). The Grand Synchronization REHEARSAL (§5 step 6) is a distinct deliverable that feeds this row's ruling — it is NOT this row; see dispositions doc (SEQ-GRAND-SYNC folds to this row's gate sequence in Part VII). |
| 113 | Symbiosis pairwise compatibility: 100×99 ordered pairs + standalone, classified with evidence;  | PARTIAL | CARRIED as MWL-113 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 114 | Full-registry D1 deepening: per-Dell deep-contract circuits until ALL 100 Dells reach a high st | PARTIAL | CARRIED as MWL-114 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 115 | SUSX100,000 execution run — the standing completion drive itself (Ace GO 2026-11-04; run conclu | PARTIAL | CARRIED as MWL-115 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 116 | DAF-09 catch-up Director report (owed per the 2026-10-31 reporting cadence; Uni-side writing) | OPEN | CARRIED as MWL-116 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 117 | Exchange Phase G (cloud perspectives) — register DECLINED (deferred by adoption, Ace 2026-10-26 | OPEN | CARRIED as MWL-117 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 118 | Q1 family implementation — journaled Exchange import/recovery transactions (C-B) under the adop | GATED | CARRIED as MWL-118 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 119 | Atomic-write sweep wiring decision (Q-35.1): sweep_stale_tmps has no production caller — orphan | OPEN | §4b FLAGGED OVERLAP with #53: this row IS the Q-35.1 decision #53's scope references. Partial overlap; no deduction. See dispositions doc §B. |
| 120 | Historical verify-72-17 reproducer hygiene: give the stale pre-repair probe an explicit/manual  | OPEN | CARRIED as MWL-120 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 121 | C2 bounded candidate: graded-input-to-verdict invariant test on one real canonical path (faded  | OPEN | CARRIED as MWL-121 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 122 | C2 relatedness model — resonance exposes with-whom / how-strong / why over agreed fixtures | OPEN | CARRIED as MWL-122 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 123 | C2 development-coupled growth — growth responds to agreed development evidence; attention the s | OPEN | CARRIED as MWL-123 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 124 | C2 targeted Pulse — Pulse obeys selected targets and exclusions | OPEN | CARRIED as MWL-124 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 125 | C2 decline-coupled Decay | OPEN | CARRIED as MWL-125 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 126 | C2 fusion — Merge carries parent substance and provenance while preserving parents | OPEN | CARRIED as MWL-126 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 127 | C2 partition — Split keeps each resonating cluster intact; zero/one cluster and ties handled ho | OPEN | CARRIED as MWL-127 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 128 | C2 enhancement outcome — Enhance redefined per Ace's ruling (outcome leg of the resonance famil | OPEN | CARRIED as MWL-128 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 129 | C2 temperature design — Temp as a typed intensity control per consumer, not a secret global swi | OPEN | CARRIED as MWL-129 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 130 | Diff becomes the one comparison authority — Rings 1+2 (every declared writer and content slice  | COMPLETE | CARRIED as MWL-130 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 131 | Mirror gains the true compare — pair comparison through the C3 comparator, honest pagination (A | OPEN | TOPICAL SEAT of GP-G09 (True Compare) — counted once, here (§3a). Status not imported. |
| 132 | Trace covers the entire current process — full retrieval beyond 512 entries without silent loss | OPEN | CARRIED as MWL-132 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 133 | Failure doors — Analyze / Revert / Retry per Ace's failure doctrine: Retry targets an identifie | OPEN | CARRIED as MWL-133 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 134 | Rooms are Ace's to close — chosen-room operations cannot overwrite another room's later work; s | OPEN | CARRIED as MWL-134 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 135 | Undo and redo like a real program — 30-step adjustable window, new-write tail invalidation, his | PARTIAL | CARRIED as MWL-135 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 136 | Alpha / history member + close ceremony — old generations freeze/confirm/restore under new code | OPEN | CARRIED as MWL-136 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 137 | Zipper — Compress + Expand as one circuit: Compress preserves a resolvable source link; Expand  | OPEN | CARRIED as MWL-137 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 138 | Inject by reference + Reference dereferencing — Inject adds a reference, not a duplicate; cycle | OPEN | TOPICAL SEAT of GP-G08 (Reference, Dell 81) — counted once, here (§3a). Caveat carried: if G-08's owning lane is a unit distinct from C4.InjectRef, G-08 is unmapped (+1 census) — AMBIGUOUS #5, Director ruling requested in the dispositions doc. |
| 139 | Distill = essence — uses actual words/detail/goals, carries provenance and disclosed omissions, | OPEN | CARRIED as MWL-139 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 140 | Nursery ranking formula — exactly S = 0.40 LINK + 0.25 ACE + 0.20 FRESH + 0.15 NOVEL; top five  | PARTIAL | CARRIED as MWL-140 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 141 | Switchable Plane ranking — Rank measure is switchable per Ace's ruling (§12.35b) | OPEN | CARRIED as MWL-141 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 142 | One search machinery, two faces — Discover + Resolve: stable ordered pages reach every authoriz | OPEN | CARRIED as MWL-142 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 143 | Nursery door policy — auto-passage stays OFF until Ace supplies standards and scope; Cycle neve | OPEN | CARRIED as MWL-143 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 144 | Boxes — standing/named sandboxes: owner put/take, multiple boxes, the standing private box, all | OPEN | CARRIED as MWL-144 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 145 | Freeze — room/item pause: paused items stay visible, retain contents/position, stop aging/growt | OPEN | CARRIED as MWL-145 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 146 | Scope/Group integration — the 53<->82 partnership as one pair; a named Group is never automatic | OPEN | CARRIED as MWL-146 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 147 | Placement — idea/body/both, AUTO/BIND: replacement retains intended position; child placement r | OPEN | CARRIED as MWL-147 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 148 | Schema = the nervous system — read-only baseline distinguishing exists / connected / available  | COMPLETE | CARRIED as MWL-148 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 149 | Profile is the speedometer — named stages with monotonic timing, environment/workload identity, | OPEN | CARRIED as MWL-149 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 150 | Token accounting + shorthand in harmony (§12.87a) — token census executed across Mandellistics; | PARTIAL | CARRIED as MWL-150 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 151 | Universal measurement family + incorporation sweep — Measure / Threshold / Weight-Normalize wit | OPEN | TOPICAL SEAT of GP-G10 (Measure, Dell 71) — counted once, here (§3a); the §1.6 footprint receipt is a named subject of both. |
| 152 | Dock roster repair — BUILT (PR #370 @ 2b95d86): two-tier dock_sessions (live uncapped + compact | COMPLETE | CARRIED as MWL-152 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 153 | Embedding provider binding — EmbedBind reports provider/model/vector-space identity (a vector d | COMPLETE | CARRIED as MWL-153 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 154 | Resident Psalm — visible start/stop, bounded work, proposal-only output; presence grants no aut | OPEN | CARRIED as MWL-154 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 155 | Multi-Psalm / BIMO execution design — persona execution needs actual instance semantics and Ace | OPEN | CARRIED as MWL-155 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 156 | Translate: honest no-intent — unknown text produces no invented Show seed; receipts name determ | OPEN | CARRIED as MWL-156 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 157 | Translate dual-mode / Adapt incorporation — Adapt adoption ruled by Ace (credit Mycroft AI team | OPEN | CARRIED as MWL-157 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 158 | Harmonic stamps — item-attached stamps with provenance in stable order; moving an item never si | OPEN | CARRIED as MWL-158 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 159 | Harmonic lenses — harmony organization/retrieval + derived lens modes; views rearrange DISPLAY  | OPEN | CARRIED as MWL-159 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 160 | The private shelf / little notebook — Macro read back as one seed; Ace's private notebook desig | OPEN | CARRIED as MWL-160 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 161 | Idea editing system — go inside, edit the parts, propose the change: contained-part drafts inde | OPEN | CARRIED as MWL-161 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 162 | Manifest split — Confirm is the yes, Manifest is the walk: confirmed-but-unmanifested is explic | OPEN | CARRIED as MWL-162 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 163 | Universal Move — Move moves anything movable: dispatches by explicit object class to EXISTING e | OPEN | CARRIED as MWL-163 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 164 | Bridge ledger — the ledger of all bridges: reports dock/Exchange facts without taking over thei | OPEN | CARRIED as MWL-164 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 165 | Exchange front door — local Exchange export/import door: preview binds to payload, imports stay | OPEN | CARRIED as MWL-165 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 166 | Room-to-room bridge — preview/transfer between rooms, only after C3 room semantics are settled; | OPEN | CARRIED as MWL-166 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 167 | Simulate: explicit effect inventory — the declared inventory of effects a simulation must accou | OPEN | CARRIED as MWL-167 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 168 | Simulate: isolated executor adapter — the actual supported command executes against an isolated | OPEN | CARRIED as MWL-168 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 169 | Simulate: supported dry-run — a bounded supported subset FIRST; per-atom outcomes and scoped di | OPEN | CARRIED as MWL-169 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 170 | Simulate: parallel preview — per-arm preview shows each arm and its conflicts, never one blende | OPEN | CARRIED as MWL-170 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 171 | Human Surface track (cross-cutting; separately authorized — no UI build started): Nursery cards | OPEN | CENSUS-DEDUPED (§4a): in the Unified census arithmetic this row was deducted as a rollup of Block F rows #99–#111. The REGISTER row stands in the canonical 182. Register-side treatment (rollup flag; re-home its three homeless extras — personal identity page, AGE surfacing, animated face (Dell 05) — AMBIGUOUS #11) is PROPOSED in the Part V plan; Part IV owns the row; no edit in plan stage. |
| 172 | Beyond-72 extension register framework (Director F1/F4): new extension objectives get distinct  | OPEN | CARRIED as MWL-172 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 173 | Coordinated history retention/compaction contract — bounded navigable undo vs durable evidence; | OPEN | CARRIED as MWL-173 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 174 | Guard/Catch wording hygiene — a separate bounded hygiene opportunity (preserved contract; not a | OPEN | CARRIED as MWL-174 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 175 | Q-SNAP.3 launch/signal-hardening proposal — proposal-only product change if still desired; no G | OPEN | CARRIED as MWL-175 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 176 | Literal wave-field instrument — INNOVATE_DEFERRED, parked (§14.9): read-only and nonauthoritati | OPEN | CARRIED as MWL-176 — canonical register row, counted once. No Grand Plan register item maps to it; no duplicate finding. |
| 177 | FRESH aging — RULED by Ace 2026-11-10: proposals age at 3/7/14-day marks and fade at 30 days ON | OPEN | CENSUS-DEDUPED (§4a): the FRESH-aging ruling's implementation rides row #140 (C5.Formula). The REGISTER row stands in the canonical 182. Register-side treatment (attribute of #140) PROPOSED in the Part V plan; no edit in plan stage. |
| 178 | Embed provider — RULED by Ace 2026-11-10: provider-agnostic dock capability (any docked AI serv | OPEN | CENSUS-DEDUPED (§4a): this row's own text states implementation = #153 (C8.EmbedBind, COMPLETE). The REGISTER row stands in the canonical 182. Register-side treatment (attribute of #153) PROPOSED in the Part V plan; no edit in plan stage. |
| 179 | Distill mode — RULED by Ace 2026-11-10: conditional — a docked AI distills when one is docked,  | OPEN | CENSUS-DEDUPED (§4a): the Distill mode ruling; the work it governs is row #139's (C4.Distill, whose text already carries the ruling). The REGISTER row stands in the canonical 182. Register-side treatment (attribute of #139) PROPOSED in the Part V plan; no edit in plan stage. |
| 180 | NVIDIA Inception website — SANDBOXED by Ace 2026-11-10: real-life side mission, NOT DellMatrix  | SANDBOXED | SANDBOXED (Ace 2026-11-10) — inside the 185 all-rows count, OUTSIDE the 182 active basis; Part IV carries it, untouched. |
| 181 | NVIDIA Inception incorporation — SANDBOXED by Ace 2026-11-10: real-life side mission, NOT DellM | SANDBOXED | SANDBOXED (Ace 2026-11-10) — inside the 185 all-rows count, OUTSIDE the 182 active basis; Part IV carries it, untouched. |
| 182 | Live-model demo step 6 — parked by Ace 2026-11-10 until he is at a computer; he will run the ti | SANDBOXED | SANDBOXED (Ace 2026-11-10) — inside the 185 all-rows count, OUTSIDE the 182 active basis; Ace runs it himself; untouched. |
| 183 | LM-2 THE SPLITTER — split_word over the LM table (census-whole -> table-recorded -> guarded gre | COMPLETE | Postdates the Unified edition (2026-11-14) entirely — no census counterpart exists; canonical-register row only. |
| 184 | GS-4 Growth Sandbox Integrity / cross-wall enumeration — CONFIRMED sandbox-integrity defect, pr | COMPLETE | Postdates the Unified edition (2026-11-14) entirely — no census counterpart exists; canonical-register row only. |
| 185 | Sandbox dock-landing + confirm-placement wall blindness — CONFIRMED sandbox-boundary defect fam | OPEN | Postdates the Unified edition (2026-11-14) entirely — no census counterpart exists; canonical-register row only. Its dock-landing build is gated on Part VI Q-U.2 (see map Part I). |
---

## 2. HISTORICAL ALIASES (Edition 1 `historical_aliases` — 8)

Aliases are **proposals until adjudicated** (Edition 1 review contract);
an alias never imports a status. Seven of the eight coincide with the
Unified §3a/§3b topical mappings and are recorded here once:

| Alias | Seat | Basis |
|---|---|---|
| GP-G03 → MWL #15 | §1 row #15 | Unified §3a mapped (gravity wells) |
| GP-G08 → MWL #138 | §1 row #138 | Unified §3a mapped (Reference) — AMBIGUOUS #5 caveat stands |
| GP-G09 → MWL #131 | §1 row #131 | Unified §3a mapped (True Compare) |
| GP-G10 → MWL #151 | §1 row #151 | Unified §3a mapped (Measure) |
| GP-G11 → MWL #11 | §1 row #11 | Unified §3a mapped (Parallel) |
| GP-G21 → MWL #46 | §1 row #46 | Unified §3a mapped (Everyday Save Pair) |
| GP-G31 → MWL #34 | §1 row #34 | Unified §3b mapped (bounded slice only) |
| GP-G30 → FAR-17 | Census-internal | The same item (the nerve's χ) dual-filed in the provisional and FAR registers — counted once, as FAR-17 (Unified §3b). Not an MWL seat. |

## 3. THE 49 CENSUS CANDIDATES — SUMMARY

Full per-item dispositions (admit / fold / reject, each with reasons and
evidence) live in `CENSUS_CANDIDATE_DISPOSITIONS_2026-11-20.md`, which
is this crosswalk's companion and the Director-ruling vehicle. Summary:

| Class | Count | Disposition pattern |
|---|---|---|
| §4 unmapped (GP-G01..G28 minus the 6 mapped) | 22 | 13 ADMIT-proposed · 6 FOLD into SEQ-X11 · 1 FOLD into the SYS-C29 settlement · 2 REJECT-census-only |
| §7 Far Stratum net (FAR-1..FAR-20, READER, GP-G29) | 22 | 22 REJECT as register rows — census-only, carried as design records by Part IV / GP-E28 behind the Far Stratum phase gate |
| §5 sequence steps (SEQ-X11, SEQ-HCN, SEQ-DOCK-LIVE, SEQ-CONSOLE, SEQ-GRAND-SYNC) | 5 | 2 ADMIT-proposed (X11 census, Console) · 3 FOLD into their program homes (Part I sequence; Part VII execution order / #112 gate) |
| **Total** | **49** | **15 ADMIT-proposed · 10 FOLD · 24 REJECT** |

If every ADMIT proposal were ruled in and landed, the register would
stand at 200 rows / **197 active basis**. That figure is a PROJECTION
of proposed rulings, stated for planning only — **the canonical basis
remains 182 unless and until the Director rules and the rows land.**

## 4. NAMESPACE MAP — MWL "G-" vs UNIFIED "GP-G" (12 collisions)

The MWL's source IDs include a register numbered G-01..G-12; the Grand
Plan §4 register is numbered G-01..G-28. **All twelve overlapping
numbers denote entirely different items** (mechanically verified in the
2026-11-15 crosswalk §5, re-verified at this pin):

| # | MWL register item (row · subject) | GP item of the same number |
|---|---|---|
| G-01 | MWL #57 · nested Idea parent/child + promotion invariants (TD-2) | GP-G01 · SPACE |
| G-02 | MWL #30 · deepen reachability for supported English actions (B-2) | GP-G02 · WEATHER |
| G-03 | MWL #48 · Exchange owner-boundary audit leg (Q1) | GP-G03 · GRAVITY WELLS |
| G-04 | MWL #15 · ForceField gravity wells restore (PR #317) | GP-G04 · WATER & GROWTH CONTENTS |
| G-05 | MWL #112 · whole-program certification (WITHHELD) | GP-G05 · FORCES RESTORE |
| G-06 | MWL #113 · symbiosis pairwise compatibility | GP-G06 · RESONANCE LOG CAP |
| G-07 | MWL #114 · full-registry D1 deepening | GP-G07 · ROUTE |
| G-08 | MWL #115 · SUSX100,000 execution run | GP-G08 · REFERENCE (Dell 81) |
| G-09 | MWL #116 · DAF-09 catch-up Director report | GP-G09 · TRUE COMPARE |
| G-10 | MWL #117 · Exchange Phase G | GP-G10 · MEASURE (Dell 71) |
| G-11 | MWL #16 · snapshot retrieval reachability | GP-G11 · PARALLEL (Dell 62) |
| G-12 | MWL #17 · Dock Proposal B | GP-G12 · suggest_preferred() |

The two cross-wired exhibits (why ID-matching is actively wrong):
**GP-G03 is MWL G-04's work** (gravity wells ride row #15, whose own
register ID is G-04 — ID-matching pairs it with row #48 instead);
**GP-G11 is not MWL G-11's work** (Parallel maps to row #11; MWL G-11
is snapshot retrieval, row #16, COMPLETE — ID-matching would "close"
an open build with an unrelated completed audit).

**Disambiguation rule (binding on all Part V documents):** §4 items are
cited **GP-G01..GP-G28**; §7 provisional items keep **G-29/G-30/G-31**
with their FAR alias noted; MWL items are cited **MWL #n** with source
IDs quoted. A bare "G-nn" citation is a defect in any new document.

## 5. MAINTENANCE CONTRACT (how this crosswalk stays current)

1. This crosswalk is refreshed **at every Part landing** that changes
   the register, against the new main pin, by the landing lane for its
   own rows and by Part V for the whole-document re-verification.
2. The Part V automation (row #90, see the plan) diffs the register
   against this crosswalk mechanically: any row whose status, title,
   or IDs changed since the crosswalk pin, and any register row with
   no crosswalk line, is flagged **DRIFT** in the morning report —
   the board can never again lag silently (the 2026-11-20 failure).
3. A crosswalk whose pin is behind main is labeled **STALE** wherever
   it is cited, with the pin named — the same labeling law as the
   board itself.
4. Candidate dispositions change only by Director ruling recorded in
   the dispositions document; a landed ruling moves the candidate's
   line there and, on the admitting Part's landing, this crosswalk
   gains the new row's mapping in §1.
