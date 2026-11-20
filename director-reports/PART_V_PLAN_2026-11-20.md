# PART V PLAN — THE SCOREBOARD RECONCILIATION (EVIDENCE FOR PART 0)

**Program:** DellMatrix Eight-Part Program (AGENTS.md §46; Ace ruling
2026-11-20 — whole program in parallel, 8 PRs, no small standalone
PRs). **Part:** V of 0–VII. **Stage:** PLAN, the first stage of
plan → confirm → code → confirm. **Branch:**
`uni/part-5-scoreboard-reconciliation`. **Base:** main
`af2519b6d239ef278397e277210d6da2467c36e5`. **Source map:**
`EIGHT_PART_EXECUTION_MAP_2026-11-20.md`, Part V section + its (g)
BUILD-READY PACKAGE, followed exactly; scope enlarged per the GO-BIG
amendment (Ace, 2026-11-20 08:54 CST) — see §11.

**This plan-stage PR contains NO production code and NO register
edits.** It contains the detailed plan (this document) plus the two
analysis artifacts the package assigned to Part V, built NOW at full
depth instead of at code stage (§11):
`CROSSWALK_CURRENT_2026-11-20.md` and
`CENSUS_CANDIDATE_DISPOSITIONS_2026-11-20.md`.

---

## 1. Scope, and the standing rule

Part V keeps the two universes — the canonical MWL register and the
Grand Plan census — reconciled forever, so the board can never
silently lag the work again. That lag is the exact failure Ace caught
on 2026-11-20 (settled work invisible on the board; closed by PR #500
the same morning). Most reconciliation already landed (#478 the
crosswalk, #479 the scoreboard sync, #500 the settlement mechanism).
What remains — this Part's whole scope — is the **automation and
format layer** that keeps the reconciliation true without a human
settlement drive, plus the **final disposition of every census
candidate** so nothing floats unowned.

**The standing rule, stated plainly (Ace; Director 7040490093;
PR #421 reconciliation): the canonical scoreboard is the MWL register
on the 182 active basis (185 rows, 3 SANDBOXED outside the basis),
rendered by `master_list.py` at a pinned main SHA with STALE/UNVERIFIED
labeling when a pin is behind main. The 224 figure is an internal
census only — never a scoreboard basis, never a denominator, never a
target. Sitting #001 (224-basis) was abolished by Ace on 2026-11-15;
the live sitting is #002, Mon 2026-11-23, ≥42 primary / ≥39 secondary
on the canonical 182 basis.**

## 2. Assigned rows (verbatim at the base pin)

| MWL # | Register title (verbatim, truncated) | IDs | Status |
|---|---|---|---|
| 90 | "Automate morning-report reconciliation, staleness, next-best recommendations (= SM-09 theme)" | 72-72 / SM-09 (theme) | PARTIAL |
| 93 | "Standardize morning Director report format (register notes it folded operationally into 72-72's automation question; carried separately per the register's unique-entries table)" | SM-09 | OPEN |
| 94 | "Connect NBD ranking to real report status, dependencies, improvement candidates; deterministic stale-candidate detection (= SM-48, internal duplicate pair counted once)" | SM-10 | OPEN |

No Edition 1 circuit is assigned to Part V; Edition 1's
`01_SOURCE_CROSSWALK_CANDIDATES.json` is this Part's primary input.

## 3. What is already done (not re-built)

- The canonical rule itself, and its instruments: register +
  `master_list.py` (`load_and_validate`, `summarize`, `render`,
  `census`; CLI `--data/--out/--line/--check/--census`) at a pin,
  with `--check` byte-identical render verification.
- The #421 reconciliation (224 relabeled internal census everywhere
  it appears; status banner on the Unified Edition record).
- The #500 settlement mechanism (register write riding inside a
  circuit's closing package — the standing commitment this Part's
  automation exists to make self-enforcing).
- The 2026-11-15 crosswalk (#478) — superseded for current-main
  purposes by this PR's refreshed crosswalk (register has since
  grown rows 183–185 and the #500 settlement moved #14/#135).

## 4. Build design — row #90: morning-report reconciliation automation

**Deliverable.** A deterministic reconciliation pass that runs with
the morning report and answers, from pinned sources only: *is the
board current, what drifted, and what is the next best work?*

**Where it lives (per package).** Automation hooks in
`director-reports/master_list.py` (Part V owns this file; Part 0 uses
it read-only) plus the goal-workspace morning tooling
(`~/workspace/goals/dellmatrix-capability-circuits/hidden_files/oci.py`
and the watch/cycle report path) for the report-side emission. No
`form/` code is touched by this Part — see §7 (no campaign).

**Inputs (all pinned, all named in the output).**
1. `master_work_list_items.json` at a stated main SHA + the
   `MASTER_WORK_LIST.md` render (`--check` receipt).
2. Live main HEAD at run time (for the STALE comparison).
3. `CROSSWALK_CURRENT_2026-11-20.md` (and its successors) — the
   drift baseline.
4. The authority surfaces the morning report already reads:
   KEEPER_WATERMARK, open-PR heads + check states, the Director's
   latest report files.

**Functions (code stage, in build order).**
- **F1 — Pin & render proof.** Load the register at the pin,
  re-render, byte-compare (`--check`); emit the board line
  (COMPLETE/total at the pin) with the pin SHA attached.
- **F2 — Staleness detection.** Compare pin vs live main: if main has
  advanced past the pin, every figure is emitted with a **STALE**
  label and the delta (commits, register-touching files) is listed.
  A report may never present a behind-main figure as current — the
  labeling law, mechanized.
- **F3 — Drift diff vs the crosswalk.** For each register row: status,
  title, or IDs changed since the crosswalk pin → **DRIFT** line
  naming the row and the field. Any register row with no crosswalk
  line, and any crosswalk line with no register row, is a DRIFT
  error, not a footnote. This is the anti-lag mechanism: drift
  becomes a same-morning alarm instead of a quarterly discovery.
- **F4 — Gate & hold digest.** Open PRs with their exact heads,
  terminal check states, and outstanding authority acts (the same
  facts the watch folds), rendered in the §5 format — the automation
  assembles, humans still judge.
- **F5 — Next-best recommendations.** A deterministic ranking over
  open register rows (the §6 engine, shared with row #94): inputs are
  real row status, block, dependency facts, and staleness of the
  row's own evidence. Output: the top recommendations with the
  *reason string* for each (never a bare score), so a recommendation
  can be argued with.

**Failure behavior.** Any input unreadable, any pin unverifiable, or
`--check` failing → the pass reports **UNVERIFIED** for the affected
section and never substitutes a stale or guessed figure (the
prove-absence discipline: unverified is a stated result, not a
silent pass).

## 5. Build design — row #93: the standard morning Director report format

#93's register text already records the fold: the format is
implemented **as the output format of the #90 automation**; the pair
closes together, counted once (dispositions doc §B2). The standard
format, fixed by this plan:

1. **Board line** — `COMPLETE / 182` + % at the named pin, STALE
   label when applicable, one-line delta since the previous report.
2. **Gate table** — every open PR: head (short SHA), checks terminal
   state, authority acts outstanding, next owner.
3. **Holds table** — every standing HOLD with its issuing authority,
   date, and exact release condition.
4. **Drift section** — F3 output (empty is a stated result: "no
   drift").
5. **Next-best** — F5 output with reason strings.
6. **Sitting line** — distance to the live sitting target on the
   canonical basis (until Sitting #002 closes: ≥42 / ≥39 of 182).

The format is a template in the automation, not a style guide: a
morning report that cannot fill a section prints the section with
its UNVERIFIED/empty state rather than omitting it.

## 6. Build design — row #94: NBD ranking ↔ real status connection

**Problem (register title, verbatim intent).** The NBD ranking
(`director-reports/NBD_MASTER_OBJECTIVE_REGISTER.md` +
`NBD_OBJECTIVE_RECONCILIATION.md`, both Part V-exclusive files) must
rank from **real report status, dependencies, and improvement
candidates**, with **deterministic stale-candidate detection** — not
from a snapshot that silently ages (the NBD register's own baseline
is main `7e593e0a`, 2026-11-04: a live exhibit of the failure).

**Design.**
- **Status feed.** Ranking inputs are read from the register at the
  same pin as the morning pass (F1's pin — one pin per report, never
  two). A candidate whose register row changed status since the
  ranking's input pin is a **stale candidate**.
- **Deterministic stale rule.** Staleness is a pure function of
  (candidate, input pin, current pin): if the row's status/title/IDs
  differ between pins, the candidate is flagged STALE with the field
  that changed; a stale candidate is **excluded from the ranking and
  listed**, never silently re-ranked on new data. Same inputs →
  same ranking, byte-stable output (ties broken by MWL number).
- **Dependencies.** Read from the register's block/ID structure plus
  Edition 1's `08_DEPENDENCY_DAG.json` where a row maps to a circuit;
  a candidate whose dependency is OPEN/GATED is ranked with that
  fact in its reason string, not hidden by its score.
- **Improvement candidates.** PARTIAL rows are the improvement pool,
  ranked by evidence recency (their F3 drift/staleness facts) — the
  ranking recommends *finishing* before *starting* wherever the
  facts support it, and says so in the reason string.
- **NBD file updates (code stage).** A dated addendum to
  `NBD_OBJECTIVE_RECONCILIATION.md` recording the connection design
  as built, and the `NBD_MASTER_OBJECTIVE_REGISTER.md` baseline line
  refreshed to the Part V landing pin with the old baseline preserved
  as history (never silently rewritten).

## 7. Test plan (code stage)

- **Render determinism:** `master_list.py --check` byte-identical at
  the landing pin (existing instrument, re-run as this Part's gate).
- **Staleness fixtures:** planted stale pin (register advanced one
  row) → F2 must label STALE and name the delta; planted crosswalk
  drift (one row's status flipped in a fixture register) → F3 must
  flag exactly that row; clean fixture → "no drift" stated.
- **Ranking determinism:** fixed input set → two runs byte-identical;
  a planted status change between pins → exactly the affected
  candidate flagged STALE and excluded, all others unmoved.
- **Format completeness:** a fixture report with an unreadable input
  renders the section as UNVERIFIED, never omitted.
- **Campaign:** none. Part V changes no `form/` code (package:
  campaign ×3 only if `form/` changes — it does not). CI (Python
  package + Form smoke) at the exact head is the code-stage gate,
  plus the focused tests above.

## 8. Proposed register flips (PROPOSED — written only at code-stage landing, on confirm)

| Row | From | To | Basis |
|---|---|---|---|
| 90 | PARTIAL | COMPLETE | F1–F5 built + fixture tests green + the automation's first production morning run emitted in the §5 format |
| 93 | OPEN | COMPLETE | The §5 format is the automation's output format — **paired closure with #90, counted once** (register's own fold note; dispositions §B2) |
| 94 | OPEN | COMPLETE (or PARTIAL if the dependency feed lands without the improvement-pool ranking) | §6 connection built + determinism tests green; the PARTIAL fallback is named now so the landing never has to improvise it |

No other register rows are edited by Part V. Candidate admissions, if
ruled, are written by the **admitting Part's** landing (own-rows-only
collision law), not by Part V.

## 9. Sitting #002 evidence pack

Prepared by the #90 automation's first production run, snapshot as of
**Mon 2026-11-23**: the board at the snapshot pin (canonical 182
basis), the `--check` receipt, the per-row delta since this plan's
pin (`af2519b6`), and the authority credit citation for every row
that flipped in the interval. The pack **reports** the board against
the sitting targets (≥42 primary / ≥39 secondary); it does not
promise them — at this plan's pin the board stands at 40, and the
pack's honesty about that is its purpose. Filed as a records
artifact under `director-reports/` at code stage (or by the morning
lane on the day, using the automation, if the code stage has not
landed by 2026-11-23 — the pack must not be held hostage to the
Part's own landing order).

## 10. Dependencies and gates

- **NEEDS_DIRECTOR (rolling, none blocking this PR):** rulings on the
  15 ADMIT proposals; rulings/permanent flags on dispositions §B1,
  §B3, §B4 and the §B7 attribute-folds (incl. the #171 re-homing,
  AMBIGUOUS #11); adjudication of the GP-G08 alias caveat
  (AMBIGUOUS #5). Full texts in the dispositions document §C.
- **PLAN-CONFIRM (this PR's ask):** Director + Keeper, in the
  one-bundle presentation of all eight Parts.
- **Code stage:** on PLAN-CONFIRM — build §4–§6, tests §7, then
  CODE/RECORDS-CONFIRM at the exact head; merge under §32 in the
  program landing order (Part V lands second: 0 → V → III → II → I →
  VI → IV → VII).
- **Consumes, never blocks:** every other Part's register writes at
  integration — Part V's automation *detects* drift in theirs; their
  landings refresh the crosswalk per its §5 maintenance contract.

## 11. GO-BIG accounting — what was "later" and is built NOW

The package scoped the crosswalk and the candidate dispositions as
code-stage file creations. Under the GO-BIG amendment they are built
**in this plan-stage PR, at full depth**: the crosswalk covers all
185 rows at the current pin with per-row dispositions, the alias and
namespace tables, and the maintenance contract; the dispositions
document decides all 49 candidates individually with reasons and
evidence, plus the §4b pairs and §4a register-side proposals. What
genuinely remains for later, and why it cannot be built now: the
**automation code** (the plan → confirm → code gate is itself the
authorization for code; building it in the plan PR would collapse
the workflow's confirm stage), the **register flips** (they record
built work; the work is not built yet), and the **candidate
admissions** (Director rulings by law). Nothing else is deferred.

## 12. Limitations

- The crosswalk's topical mappings rest on the Unified Edition's own
  §3 analysis, re-verified at the pin for seats and counts; where
  the Unified itself flags ambiguity (AMBIGUOUS #5, #11), this plan
  carries the flag rather than resolving it — resolution is the
  Director's.
- Candidate dispositions for the six census-executed GP-G items
  assume SEQ-X11's admission; if the Director declines that row, the
  six folds revert to census-only with their execution unhoused —
  the dispositions document states this dependency on its face.
- The #94 design reads Edition 1's dependency DAG where rows map to
  circuits; rows with no circuit mapping rank on register facts
  alone, and the reason string says so.
