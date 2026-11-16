# DIRECTOR — Live Progress Truth Contract (MWL / PLAN / CODE)

**Date:** 2026-11-16. **Status:** DRAFT / independent Uni + Keeper review required. **Nature:** records + architecture; no product-code implementation or completion credit. **Authority:** Ace — real-time verified status controls the current board; history only documents earlier states.

## Current direct repository evidence

Main SHA read: `36d7679a642c15aebb7539fd138738f15b9ee7b4`.

- Canonical MWL data: `director-reports/master_work_list_items.json`, blob SHA `8da24d34069e24318e5837f1e40bca23cf72c236`. Numbered entries 1–185. Statuses: 39 COMPLETE, 54 PARTIAL, 86 OPEN, 3 GATED, 3 SANDBOXED.
- Generator: `director-reports/master_list.py`, blob SHA `9644599d9a4608977038d3e11041eb2385a5db70`; active denominator = non-SANDBOXED items = 182, headline numerator = COMPLETE = 39.
- Render: `director-reports/MASTER_WORK_LIST.md`, blob SHA `379c319920b6b591184bb26f926571607840146b`; displays **39 / 182 COMPLETE = 21.4%**. This is the **last verified current-main snapshot** at the pinned SHA, not a promise of continuous auto-refresh.
- Distinct belt denominators: `director-reports/DUAL_BELT_TOTALS_LEDGER_2026-11-15.md`: PLAN 242, CODE 198. Those are **not** strict MWL completed counts. Their completed numerators require independently verified belt receipts; do not infer PLAN/CODE completion from MWL 39.

## Why the old 35 was not current

The frozen 2026-11-15 crosswalk (`MWL_UNIFIED_CROSSWALK_2026-11-15.md`, PR #424 @ `be62189b5a3137e6878300e962e9d8718f6576eb`) recorded 35 COMPLETE across 182 *all* historical rows (including 3 sandboxed). The current 182 is an *active* denominator across 185 all rows. Four scoped complete entries account for the difference:

| Row | Frozen crosswalk state | Main state | Source credit / limitations |
|---|---|---|---|
| #130 C3.Diff | PARTIAL | COMPLETE | #384 code merged `76afea8`; #385 record merge `61b036d`, item-specific closeout 6804843585 and Keeper confirmation 6806075604; Rings 1–2 only, Ring 3 excluded |
| #148 C7.Schema | OPEN | COMPLETE | #397 code merged `2e46272`; #400 register merge `074b30f` and receipt 6826936680; read-only DD-29 board only |
| #183 LM-2 | ABSENT | COMPLETE | #395 code merged `c414e71`; #400 register merge `074b30f` and receipt 6826936680; splitter/census/quarantine only |
| #184 GS-4 | ABSENT | COMPLETE | #405 code merged `c0742ce`; #406 receipts `471c8c8`; #407 register merge `e0fc263`, Keeper 6839976718, closeout 6840705011; U1–U3 residuals excluded |

**Ace's older retirement of *unverified* 39 is retained in dated history, not used to override the subsequently substantiated 39.** This packet supports presenting the verified current register as current while never manufacturing additional credit. The old 35 and new 39 are different snapshots, not a dispute to solve by deleting history.

## System contract — current truth, not a frozen screenshot

### Source and recompute

1. Read the canonical MWL JSON and generator **from the same pinned latest-main commit**. Never take the numerator from the report, the denominator from an old crosswalk, or the card state from one branch and the SHA from another.
2. Validate strictly: sequential unique MWL numbers; recognized statuses; no duplicate object identities without a documented crosswalk exception; active = non-SANDBOXED; COMPLETE counted once. Regenerate `MASTER_WORK_LIST.md` and compare byte-for-byte. If mismatched, refuse to display a VERIFIED headline and emit a named discrepancy with the offending SHA.
3. For each progress card, carry: `source=master_work_list_items.json`, `repo_main_sha`, `data_sha`, `verified_at_utc`, `numerator`, `denominator`, `status=VERIFIED|STALE|UNVERIFIED`. All consumers (GitHub reports, Studio, workflow cards, wake/sleep reports) must display the same *pinned* counts or plainly say their snapshot is older. Do not imply 24/7 live-update if the consumer is a committed Markdown file.
4. On viewing or refreshing the board, fetch the current main HEAD then retrieve all sources at **that HEAD** and recompute. If unable to access main or a source, retain last-known value only with `STALE/UNVERIFIED` visibly attached, including the former SHA and time. A later main HEAD invalidates a previous snapshot until compared/recomputed; even if the number stays the same, the freshness claim is head-bound.
5. Event-driven refresh may be added **only** when a verified event channel exists; otherwise the current Director and Keeper checkpoint clocks plus Uni watch can discover changes but cannot guarantee zero lag. Measure observed age in seconds/minutes; enforce a disclosed SLA and alert on a stale source. The word **LIVE** is reserved for an on-access refreshed or continuously confirmed source; static GitHub Markdown is a publication snapshot.

### Historical placement

Archive older scores under a dated `history`/audit section with the precise original source SHA and old denominator interpretation. No historical figure should appear as the headline of today's dashboard, plan board, or workflow output. Never erase historical proof. Ace owns any deliberate rollback in authority, not an automated stale override.

### Parallel belts

Expose three distinct scopes, each with its own data model and source:

- **MWL strict object completion:** current `39/182` at the pinned tested main; 3 sandboxed excluded from the active denominator.
- **PLAN belt:** denominator `242`, completed numerator only from individually closed and source-verified execution-ready PLAN-class receipts; separate from RECORDS merges if law says no product credit. Do not fabricate a numerator.
- **CODE belt:** denominator `198`, completed numerator only from built + merged + proven-main CODE-class receipts. A record-only merge cannot increment it.

## Proposed acceptance tests (not yet executed)

- **A1 Single-revision truth:** At a pinned SHA, JSON count and generator-rendered Markdown match byte-exact; card shows data SHA + main SHA + time. No hardcoded 35/182 or 39/182 in a live-data path.
- **A2 Changed completion:** In a throwaway fixture, flip one verified row from PARTIAL to COMPLETE. All current consumers reflect +1 exactly once, preserve evidence ID and never alter CODE count unless it is actually a proven CODE closure.
- **A3 Added item:** Append one distinct active OPEN row. Denominator increases by one; the historical 182-row appendix stays frozen, labeled historic.
- **A4 Sandboxed:** Add one SANDBOXED row. All-row count rises; active denominator and completed numerator unchanged.
- **A5 Stale/mixed SHA:** Make main advance after one source is read, or read a report produced from a different commit; mark STALE/refetch, never VERIFIED.
- **A6 Unavailable/malformed:** Repository errors, duplicate IDs, renderer mismatch, incomplete belt metadata or missing timestamp produce named refusal/unknown state, not the last historical count as live.
- **A7 Audit preservation:** Old 35 snapshot and every original receipt remain recoverable in dated history. No overwrite or retroactive score claim.
- **A8 Real public path:** Test via the actual Studio/progress endpoint (when wired) and the report generator, not only a helper function. Pin the published result to exact-head CI and a final Keeper/Director check before Uni-only merge.

## Director disposition and scope

This is a **SOURCE-OF-TRUTH DESIGN DRAFT** for Uni + Keeper two-checker review. The verified current-main count is **39 / 182 = 21.4%**. The exact per-belt completed numerators remain subject to their own receipts. PR #421's current conflicting Unified Plan edition is still **CORRECTION_REQUIRED**, not merge-authorized by this new evidence alone; the report must adopt this live-first contract and remove obsolete live headlines while retaining archival history. Any implemented rendering/Studio changes belong to a separately authorized, tested code circuit. Preserve §32, current HOLDs and Uni-only merge.
