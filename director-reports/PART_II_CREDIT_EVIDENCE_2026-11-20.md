# PART II — CREDIT EVIDENCE PACKAGES: FIVE BACKLOG CIRCUITS (+1 TRAILING)

**Date:** 2026-11-20 · **Lane:** Part II — The Dell Plan (Eight-Part
Program, AGENTS.md §46) · **Branch:** `uni/part-2-dell-plan` ·
**Base:** main `af2519b6d239ef278397e277210d6da2467c36e5`

**Provenance.** Director triage 7040622309 (2026-11-20) independently
checked the seven merged backlog circuits for successful merge-commit
CI and routed them to the Keeper for scoped credit / identity
decisions, with no duplicate points. Five of the seven are assigned
to Part II: #401, #416, #429, #439, #457. (The remaining two —
#413 and #417 — are assigned to other Parts and are NOT covered
here.) This document is the complete Uni evidence package for the
five, assembled so the Keeper's grouped decision needs nothing else.

**Verification method (all five, 2026-11-20, first-hand):**
(1) PR state/merge SHAs read from GitHub (`gh pr view`);
(2) merged-main ancestry proven in a fresh clone of main
`af2519b6` — `git merge-base --is-ancestor <mergeSHA> main` = YES
for every package below; (3) merge-commit CI read from the GitHub
check-runs API at each merge SHA — for every package: build (3.10)
SUCCESS, build (3.11) SUCCESS, smoke SUCCESS.

---

## Package 1 — PR #401: C7.Profile (DD-39) — Dell 49 the speedometer

- **Title:** C7.Profile (DD-39): Dell 49 becomes the speedometer —
  benchmark-only timing surface
- **Merged:** 2026-11-14T12:43:18Z · **Head:** `00868f11085f95d48dbf2a5c229dde21f7ee8c0b`
  · **Merge SHA:** `587bec4b37f1fc6ae52148ab5b8b4d5cae722e98`
- **Merged-main proof:** merge SHA is an ancestor of current main
  (verified 2026-11-20). **Merge-commit CI:** all SUCCESS (above).
- **What shipped:** Dell 49 Profile as a benchmark speedometer.
  Live-verified 2026-11-20 at current main (PUBLIC_ENTRY_PATH):
  `49[Profile]` prints kind BENCHMARK, workload identity
  ("12 ideas"), named stages (place, pulse, growth, save, load)
  with per-stage timings, and environment identity
  (python version + platform). Pinned in
  `form/c7_measure_family_test.py` (pin.profile_benchmark_labeled).
- **Register identity:** DIRECT — MWL row **#149** (DD-39 /
  C7.Profile), current status **OPEN**. The shipped scope is the
  benchmark speedometer; the row's full contract (real-observation
  mode distinct from deliberate benchmarks, overhead disclosure)
  is completed by GP-E12 inside Part II.
- **Exact ask:** Keeper scoped CODE CREDIT decision for #401
  against row #149 — proposed register treatment on credit:
  #149 OPEN → PARTIAL on this settlement (benchmark scope
  credited), flipping to COMPLETE only when GP-E12 closes the
  row's remainder inside the Part II PR. If the Keeper judges the
  benchmark scope to BE the row's contract, COMPLETE is his call
  to make on this evidence — Uni proposes PARTIAL as the honest
  scope.

## Package 2 — PR #416: LM-4 THE TOLL BOOTH

- **Title:** LM-4 THE TOLL BOOTH: forced LatinMandell first pass on
  the English entry path
- **Merged:** 2026-11-14T04:39:34Z · **Head:** `183f78185e0ab7461642a590e219c5597024e347`
  · **Merge SHA:** `b546faf8d9765c025011ee7835de3c921d42f47e`
- **Merged-main proof:** ancestor of current main (verified).
  **Merge-commit CI:** all SUCCESS.
- **What shipped:** every English Intent carries the LatinMandell
  decomposition receipt (the forced first READ). Live-verified
  2026-11-20 at current main: `Intent.lm` is attached on
  translate() output (pinned in `form/c9_translate_honesty_test.py`,
  pin.receipt_names_engine); the Intent dataclass documents the
  receipt as computed once by the translate() wrapper, None exactly
  when no decomposition exists (never fabricated).
- **Register identity:** NONE FOUND — no register row names LM-4,
  the toll booth, or LatinMandell (searched all 185 rows by title,
  2026-11-20). Row #183 is LM-2 THE SPLITTER, a different LM item,
  already COMPLETE; it is NOT this circuit's row.
- **Exact ask:** Keeper scoped CODE CREDIT + IDENTITY decision —
  either (a) confirm no-row code credit for #416 (the R19 / R25 /
  #497 precedent: real credited code, no board point, no row
  invented), or (b) name the register row this circuit belongs to.
  Uni recommends (a) on this evidence.

## Package 3 — PR #439: A4 — LM-4 resource guard

- **Title:** A4 — LM-4 resource guard: prompt bound enforced before
  full decomposition cost is paid
- **Merged:** 2026-11-16T05:05:48Z · **Head:** `903957cf7ff0291f83a1355cefbcaeca9c2b9d81`
  · **Merge SHA:** `7ed41b1f5919b6f2f016626cf91d2b8fdc7848fe`
- **Merged-main proof:** ancestor of current main (verified).
  **Merge-commit CI:** all SUCCESS.
- **What shipped:** the LM-4 entry path refuses over-bound prompts
  BEFORE paying full LatinMandell decomposition cost — the
  resource-guard half of the LM-4 pair (circuit record:
  `director-reports/A4_RESOURCE_GUARD_CIRCUIT_2026-11-15.md` on
  main).
- **Register identity:** NONE FOUND — same search as Package 2;
  the LM-4 pair has no register row.
- **Exact ask:** Keeper scoped CODE CREDIT + IDENTITY decision for
  the LM-4 pair (#416 + #439 together): no-row credit under the
  R19/R25 precedent, or a named row. Uni recommends no-row credit
  for the pair as one identity.

## Package 4 — PR #429: SYSTEM-002 / SYS-C29 — Nursery store repair

- **Title:** SYSTEM-002 / SYS-C29 — Nursery store silent-truncation
  repair (words preserved through the store)
- **Merged:** 2026-11-15T16:10:49Z · **Head:** `f29a1a2adeca314898c4026d75f16ee6c9eabc15`
  · **Merge SHA:** `97d5cb99f6f74595dda0cdadd525f9835290bcda`
- **Merged-main proof:** ancestor of current main (verified).
  **Merge-commit CI:** all SUCCESS.
- **What shipped:** the Nursery store stopped silently truncating
  stored words — the head of the SYS-C29 silent-cut family that
  the later family repairs (#436, #437, #446) continued. Circuit
  record: `director-reports/SYSTEM_002_SYSC29_CIRCUIT_2026-11-15.md`
  on main.
- **Register identity:** NO DEDICATED ROW — no register row names
  SYS-C29 or SYSTEM-002 (searched 2026-11-20). The work's subject
  matter lives inside the C5 Nursery family's scope (rows
  #140–#143), none of whose titles name the truncation repair.
- **Exact ask:** Keeper scoped CODE CREDIT + IDENTITY decision —
  no-row credit under the R19/R25 precedent, or identity inside
  the C5 cluster named by the Keeper. Uni recommends no-row
  credit; the C5 rows' own remainders are GP-E20's build scope in
  Part II and must not be double-counted with this settlement.

## Package 5 — PR #457: C5R.1 — Nursery lossless holding

- **Title:** C5R.1 HOLD — Nursery lossless holding + honest
  read-path counts (AC-1.1–AC-1.4)
- **Merged:** 2026-11-16T04:07:04Z · **Head:** `bfadca32ec8a655311ccc6f8161235e8cfaaf0a3`
  · **Merge SHA:** `f9def221bf203a5973c624d7f20ac02058e314b9`
- **Merged-main proof:** ancestor of current main (verified).
  **Merge-commit CI:** all SUCCESS.
- **What shipped:** C5R.1 of the C5 Replan — the Nursery holds
  proposals losslessly (no silent eviction/truncation at intake)
  and its read paths report honest counts (build record:
  `director-reports/C5R1_HOLD_BUILD_2026-11-15.md` on main).
  The C5 line continued after it: C5R.2 SEE (#465), C5R.3
  ORGANIZE (#467), C5R.4 LENS (#473) — those are separate
  circuits, not part of this package.
- **Register identity:** NO DEDICATED ROW — no register row names
  C5R.1 (searched 2026-11-20); as with #429, the subject lives
  inside the C5 cluster rows #140–#143 without being named.
- **Exact ask:** Keeper scoped CODE CREDIT + IDENTITY decision —
  no-row credit under the R19/R25 precedent, or a named C5-cluster
  identity. Uni recommends no-row credit, with the same
  no-double-count fence as Package 4.

## Trailing item — PR #496: R25 / GP-E04 credit (not a backlog seven member)

- **Merged:** 2026-11-19T13:31:51Z · **Merge SHA:**
  `c13428cb5807cec9501c1296fd0520f934ff9f4f` (ancestor of current
  main, verified 2026-11-20).
- **Posture:** Ace's single-failure ruling (7040200362) noted the
  one unreproduced merged-main smoke failure as an anomaly;
  Director 7040318415 lifted the credit HOLD under that exception.
  A §45 credit package was already presented (7040793444).
- **Exact ask (renewed inside this bundle):** Keeper scoped
  postmerge CODE CREDIT CONFIRM for R25/GP-E04 at `c13428cb`, or
  name the exact missing evidence. No register row exists for R25
  (Director identity ruling line: GP-E04 has no MWL row); no board
  point is claimed.

---

## Limitations

- Merge-commit CI is cited from the GitHub check-runs API at each
  merge SHA (2026-11-20); it proves the merge commit's own checks,
  not a fresh full campaign on today's main. GP-E20's Part II
  validation re-proves the C5 surface behaviorally at the Part's
  exact head during the code stage.
- Identity recommendations are Uni's proposals. The credit and
  identity decisions themselves are the Keeper's (with the
  Director's final check); nothing in this package self-grants
  credit, and no register edit is made by this document — all
  flips are proposed in the Part II plan and executed only on
  confirm, inside the Part PR.
