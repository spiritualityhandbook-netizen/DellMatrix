# R19 / R19-SIB — CANONICAL MWL IDENTITY RECONCILIATION

**Prepared by:** Uni, 2026-11-18 (late), under the Director's scoped
settlement on PR #493 (comment 7000248746, ":00 credit-desk delta").
**Status:** PREPARED for Keeper independent records review, then
Director section 32 final authorization. This file changes no register
data by itself; the register JSON is intentionally NOT modified by the
accompanying PR (see section 2 for the proof of why).
**Current main at preparation:** `52c2793419572db05291d563f4bcdd7f7aad73bc`.
Canonical register source blob (unchanged):
`8da24d34069e24318e5837f1e40bca23cf72c236` — 185 rows; board
**39/182 COMPLETE = 21.4%** before AND after this reconciliation.

## 1. The two settled CODE credits

| Circuit | Source PR | Merge commit | Keeper postmerge CODE CREDIT verdict | Director postmerge evidence ruling |
|---|---|---|---|---|
| R19 — truthful Cycle requested/executed/remaining receipts; flow 99 removed; malformed count refusal | #489 | `e3ca32d3071650d39c896f40ef4094781884bdc9` | **CODE CREDIT CONFIRMED** — Gemini as fallback Keeper under Ace's 2026-11-18 standing rule, comment 6999995447 (Keeper seat produced no verdict across six slots; fallback exercised and recorded on PR #493, comment 6999998665) | Evidence ACCEPTED, comment 6996839026 |
| R19-SIB — grow / walk / english_expand count-door integrity, full-token handling (Loop contract unchanged reference) | #491 | `389d360fa60dff1d8c8aee6d119a55062f01d8ac` | **CODE CREDIT CONFIRMED** — Gemini as fallback Keeper, comment 6999997968 | Evidence ACCEPTABLE, comment 6996839518 |

Both credits are settled on the **CODE belt** (Director ledger
taxonomy: PLAN 242 / CODE 198 objects). They are distinct code repairs
on distinct surfaces (Cycle door vs the grow/walk/expand doors) sharing
one census parent (Limits Census R19; Grand Plan cross-reference
GP-E03). **Identity fence:** neither credit is a second completion of
the other; no parent objective may receive two COMPLETE marks from
these two repairs.

Director settlement condition (7000248746), recorded verbatim in
effect: the fallback verdicts are accepted as submitted fallback-Keeper
review records for advancing this reconciliation — **not** as automatic
register credit; and if either verdict's independence is contested,
credit is explicitly HELD pending a directly attributable Keeper
review. No contest is on record at preparation time.

## 2. Canonical MWL identity mapping — the proof

The Director's settlement requires the exact canonical MWL row/objective
mapping to be **proven before awarding COMPLETE**. Uni searched the
canonical register (`master_work_list_items.json`, all 185 rows, full
text of title/ids/status/block) for: `R19`, `R19-SIB`, `GP-E03`, `E03`,
`Cycle`, `count-door`, `english_expand`, `census`, `GP-`, `limits`.

**Result: no MWL row carries the R19 or R19-SIB objective.** The R-series
identities live in the Limits Census taxonomy (landed via PR #487) and
in Grand Plan Edition 1's cross-references — not in the canonical MWL
register. The only rows the search surfaced are near-misses whose scopes
provably do not cover these repairs:

- **Row 24** (72-06 / SM-11 / DD-01 / DD-02, PARTIAL) — the English
  Intent.args end-to-end contract, scoped to DD-01 Class E and DD-02
  Class D repairs landed via PRs #309/#310. It does not name Cycle,
  count operands, or the grow/walk/expand doors.
- **Row 29** (72-11 / SM-12 / SM-13, PARTIAL) — English create + direct
  REPL handler reconciliation with canonical Mandell. It does not name
  count-door integrity or Cycle receipts.
- **Row 143** (DD-27 / C5.Door, OPEN) — Nursery door policy; its "Cycle"
  mention is the Nursery proposal cycle, unrelated to the Mandell Cycle
  operator.

Awarding COMPLETE to any of these rows for R19/R19-SIB would be a false
identity. Creating a new MWL row would change the denominator and
constitute adoption of a new register objective — an authority act that
has not been granted (the 49 Edition 1 candidate additions remain
UNADOPTED under G5 ruling 6989088291, and the Director's settlement
authorizes reconciliation, not register expansion).

**Conclusion (per the credit desk's own section 5 rule, PR #493):** no
canonical MWL objective closes under R19 or R19-SIB; the register and
its headline therefore remain **unchanged at 39/182 = 21.4%**. The
merged code is real, credited progress on the CODE belt while the MWL
register stays numerically static — exactly the outcome the desk
anticipated.

## 3. What this PR does

1. Lands this reconciliation record (the proof in section 2, the settled
   credits in section 1).
2. Appends the two verdict links verbatim into the landed G5 status
   bridge (PR #494, `G5_STATUS_BRIDGE_2026-11-18.md` section 3), closing
   the link slots that bridge left open.
3. One additive INDEX row for this file.

It does **not**: modify `master_work_list_items.json` or
`MASTER_WORK_LIST.md`; change any status, figure, or denominator; touch
product code; or settle the separate Q-LC.1 / R26 / R17 register updates
(their own authority trail, a separate records PR).

## 4. Non-coverage

- PR #492 (test-isolation hygiene) remains RECORD COMPLETE / ZERO CODE
  CREDIT (Director final closeout 6996840050); no row action.
- The independence-contest HOLD condition (section 1) survives this
  record: a future contest re-opens the credit question; it does not
  retroactively alter the merged code.
- PR #493 (credit desk) closes as SUPERSEDED BY LANDED RECORD once this
  reconciliation is on main, per the Director's directive.
