# NBD OBJECTIVE RECONCILIATION — How the Master Register Was Built

**Date:** 2026-11-04 · **Mode:** A — Planning / Reconciliation (Director Addendum, 2026-11-04)
**Companion:** `NBD_MASTER_OBJECTIVE_REGISTER.md` · **Baseline:** main `7e593e0a5b5a47a36111734e35b6464f61b511b6`

## 1. Source coverage (what was actually reconciled)

| # | Source (per the directive's list) | How it was used |
|---|---|---|
| 1 | `director-reports/INDEX.md` + all Director rulings/reports on main | Read directly; INDEX "Latest dispositions" table treated as superseding stale per-row SUBMITTED labels (per the INDEX's own instruction) |
| 2 | SUS Ω-64 inventory + state file + morning report | Full 64-item reconciliation against current main, including post-run closures through PR #288 |
| 3 | The 72-item inventory (2026-11-03, baseline 4df2246) | Transmitted in full with the addendum; stored verbatim at `DELLMATRIX_ORIGINAL_72_INVENTORY_2026-11-03.md`; all 72 items evidence-checked against current main |
| 4 | `ACE_VISION_AND_COMPLETION_QUEUE_SUBMISSION.md` + `SLEEP_MODE_SUSX100000_PROPOSAL.md` (PR #288) | Vision objectives entered as the V series |
| 5 | `ACE_FUTURE_DEVELOPMENT_PLAN.md` (Uni workspace) | Source for V-series wording and Ace's gates |
| 6 | Standing rulings in force (Mode D review 2026-11-04; DIR-CERT-2026-11-02; SUS wake ruling; Track D plan ruling; autonomy charter; symbiosis + full-registry directives) | Entered as the G series and as certification/boundary facts inside 72/SM entries |
| 7 | Current GitHub state | Every status rests on files, suites, merges, or rulings verified at baseline `7e593e0` during this pass |

**Coverage limit (stated, not hidden):** the Ten-Phase Master Plan and the earliest phase documents were covered *through* the INDEX, the rulings, and the two inventories that themselves derive from them — they were not re-read end-to-end as primary texts in this pass. If the Director wants a primary-text census of the phase documents, that is a defined follow-up (estimated: one bounded documentation circuit), and the register's historical-completeness claim extends exactly as far as the table above and no further.

## 2. What changed between the inventories and today

**Of the 72 items written on 2026-11-03, 16 are COMPLETED at current main** — most closed by work the inventory predates or brackets: browser acceptance (72-01), the Core I gate pair (72-02/14), both arg-gate lines (72-15), Dell 37 visibility (72-05), Growth identity (72-04/41), Try/Catch (72-22), Diff/Set (72-24), dock verbs (72-46), the SM-49 browser extensions (72-55/56/57), the visual snapshot label (72-62), regression-registration integrity (72-68), and evidence preservation (72-08). **49 are PARTIAL** — real mechanisms with real evidence whose full acceptance batteries were never exercised as one contract; this is the register's center of gravity. **3 remain INVESTIGATION** (72-11, 72-16, 72-17), **3 are plainly OPEN** (72-64, 72-67, 72-70), and **1 is BLOCKED** (72-03, DAF-09 — Director-environment reproduction).

**Of the 64 SUS items, 56 duplicate a 72 item** (the two inventories were written a day apart against substantially the same program). The SUS run's verified outcomes fold into their 72 twins; 8 SUS items have no twin and stand as unique register entries. One internal duplicate exists inside the SUS inventory itself (SM-10 ≡ SM-48) and is counted once.

**Post-inventory closures the older papers do not show:** SM-54 (PR #276) closed the Growth-truthfulness defect after both inventories were written; the SM-39 persistence closure (PR #277) plus the Director's 2026-11-04 ruling lifted the T2 identical-label limitation inside its scope; TD-1/TD-1-R1/TD-1-R2 and Water were built and certified (PRs #278/#283/#285/#286) — advancing 72-28, 72-30, 72-37 and SM-28/SM-35 to PARTIAL without closing them.

## 3. Stale or false claims found and corrected by this reconciliation

1. **README suite count is stale TODAY:** README claims 230 suites; the canonical `form/regress.py` LIST at baseline contains **235**. SM-62's closure was true at its revision; the drift since is new. → 72-64 reopened as OPEN.
2. **SM-11's original Cycle-5 closure was retracted by the run itself** (PR #264 merged before its smoke finished FAILED; erratum recorded; closure rests on the Cycle-5b repair, PR #265). The register's COMPLETED for 72-06's bounded class cites the repair, never Cycle 5.
3. **The SUS morning report's counts are publication-time** (8 COMPLETE_VERIFIED) and its SM-05/SM-06 rows are stale (both later completed via PRs #272/#274). Final tally (10, then 11 with SM-54) rests on the state file's wake/post-wake records and the INDEX.
4. **INDEX per-row labels lag the dispositions table** for Steps 7/8/5b (rows still read SUBMITTED; the table records the rulings). This reconciliation followed the table per the INDEX's own supersession instruction; the row texts remain a known cosmetic debt (SM-05-class work).
5. **SM-39's original report claimed gravity round-tripped; it did not.** Corrected by dated addendum; the true remainder is register item G-04. No register entry relies on the false claim.
6. **SM-28 / SM-35 PARTIAL ratings are reconciliation judgments**, not recorded dispositions: no source ever assessed those items under their own scopes. They are marked PARTIAL because adjacent certified work (TD-1 line) verifiably advances their territory — the register flags this so the Director can re-rate if he reads the scopes more strictly.
7. **Item-count honesty:** the tasking brief's "10 COMPLETE_VERIFIED" parenthetical listed 9 IDs; the records resolve the tenth as SM-49. The register uses the records.

## 4. Unresolved source gaps

- **No missing source files.** Every file cited by all 72 items and all 64 SUS items was checked and exists on current main.
- **Evidence-thin items** (statuses held at PARTIAL rather than upgraded): 72-43 (one suite, eligibility scope), 72-47/48 (no isolated contract suites), 72-50 (indirect proof only), 72-51/52 (suite existence verified; assertion-level coverage of the acceptance chain NOT verified), 72-61 (responsive behavior unverified either way — grep found no @media rules, which is not proof of absence), 72-67 (permissions-block absence verified in form-smoke.yml and by targeted grep, not by exhaustive read of every workflow line).
- **72-01 acceptance drift:** the inventory demands 16/16; the driver has since grown to 31 assertions under later rulings. The register records the certified 16/16 at its revision and the extensions separately — the figures are not interchangeable.
- **72-03 figures:** "19/22" is the Director's independent result; Uni's local suite is 23/23 post-ESRCH on an expanded check set. These are different measurements; the register keeps the item BLOCKED on the Director's.
- **Primary-text census limit:** see §1 — the phase-document layer is covered indirectly, not exhaustively.

## 5. Dependency conflicts

None found that require Director arbitration today. Recorded dependencies that constrain sequencing: V-07 (recursive navigation) depends on G-01/TD-2 containment data; V-08 depends on V-09 research; G-05 (whole-program certification) depends on 72-03 + 72-07; 72-30's modification leg depends on G-03's audit completing first; vision items are unrouted and therefore cannot conflict with authorized work.

## 6. Proposed dependency-ordered execution queue

**AUTHORIZED — proceed (already ruled):**
1. **G-01 / TD-2** — the active circuit. One frozen candidate, then STOP.
2. **G-02 / B-2** — parallel investigation, per-Dell probes.
3. **G-03 / Q1 audit** — audit only; report precedes any modification proposal.

**NOT AUTHORIZED — proposed order for Director consideration (nothing here starts on this document's say-so):**
4. P0 partials with bounded scopes: 72-49 (AcceptancePolicy revocation chains), 72-28 (Program/Nursery pair-atomic crash proof), 72-64 (README count refresh — trivial docs circuit).
5. Investigation closures with small probes: 72-17 (bare Show probe), 72-16 (flow-executor determination), 72-06 (Intent.args census).
6. Persistence-integrity batch: 72-29, 72-32, 72-35, 72-36, G-04 (gravity/evolution — separate circuit per ruling).
7. Contract-completion batch: 72-13, 72-19/20/21, 72-25, 72-26, 72-27, 72-10.
8. Intelligence/authority batch: 72-40, 72-42, 72-43, 72-44, 72-47, 72-48, 72-50, 72-51, 72-52, 72-54 (72-53 build remains gated by the SM-20 ruling).
9. Studio/parity batch: 72-59, 72-60, 72-61, 72-63, 72-67 (workflow hardening — small, independent), 72-69, 72-72.
10. Standing programs: G-06 (symbiosis), G-07 (full-registry D1), G-09 (DAF-09 catch-up report — Uni-side writing, Director-time reading).
11. Vision circuits (V-01…V-12) — only as routed by the Director.
12. SUSX100,000 (G-08) — only on Ace's GO; its scope, per the filed proposal, is drawn from this register's open items as the Director directs.

## 7. Stop condition

Per the addendum: this register and reconciliation are presented for Director review **before** any implementation priority changes. TD-2, B-2, and the Q1 audit continue under their existing authorizations; nothing else in this document starts work.
