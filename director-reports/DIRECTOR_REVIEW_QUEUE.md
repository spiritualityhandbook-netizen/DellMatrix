# DIRECTOR REVIEW QUEUE — standing queue for the hourly review

Ace ruling (2026-11-10): the Director's hourly review clears the
ENTIRE queue, not one item. The review is complete only when every
queued item carries a disposition returned to Uni. Uni keeps this
queue complete and current; an item leaves the queue only when its
disposition is on record. Dual-anchored: this file on main + the
SUSX100,000 state file. Uni updates heads in place as lanes land.

## Awaiting disposition

| Item | Ask | Head | Asked |
|---|---|---|---|
| PR #345 — DD-45 execute_chain refuses failed seeds | SCOPED HOLD (Director delta mail 1a1c72ded8c73827): patch review finds the refusal guard calls _note_unknown(program), potentially mutating the unknown ledger — the "zero state mutates" claim needs scope correction or proof (test asserting Program/Nursery durable state unchanged + diagnostic-note mutation classified). SCOPED CODE REVIEW CONDITIONAL PASS on fail-closed receipt only; MERGE HOLD until reconciled + refreshed local regression | 5fa4d5f | 2026-11-10, comment 6777027932 |
| PR #350 — DD-31 diagnostic capture | Renewed merge ruling at post-rebase head (prior conditional authorization named superseded head 7cdb880 and does not carry). Exact-head CI TERMINAL PASS; disposition package posted (comment 6777942929) | b6b0307cac2467d09e6466065c1b2281f990a2e0 | MERGED e4aad9d (2026-11-10 ~14:38 CST) — all Director conditions verified in the merge step: Keeper CONFIRM ddf0cbd, local full regression GREEN at head (266 suites), capture-file check clean (4 files), SS32 full-body read of mail 1a1c72ded8c73827. Final-check PENDING. DD-31 root mechanism remains OPEN |
| PR #360 — DD-44 loop bounds (Q-DD44.1) | Refreshed disposition at post-rebase head. Keeper scoped CONFIRM on record (main 0815c82, Q-DD44.1 accepted); exact-head CI TERMINAL PASS; Director recheck package posted per MODE D delta list (comment 6777942005) | 0773d1346475760fad0c455ae0ddf8f49a26ad34 | MERGED d58a3d5 (2026-11-10 ~14:25 CST) — all conditions verified in the merge step; post-merge DD-44 suite 16/16 on merged main. Final-check PENDING. Q-DD44.2/.3 remain separate OPEN follow-ups |
| PR #348 — DD-14 / C1.Loop | Refreshed disposition after regression legs 2–3 on the REBASED head. First legs run at 813b2aa: leg 3 (rev) GREEN; leg 2 (--twice) RED isolated to the pre-#361 dd31 suite (proven DD31-CI mechanism, fixed on main by #361; log preserved). Branch rebased onto current main (DD-14 suite 11/11 on the rebased tree); legs 2–3 RERUNNING at the new head | d1ae66d | rebased + legs rerunning 2026-11-10 ~14:10 CST. Director recheck (mail 1a1c713671086995): HOLD remains until rebased regression completes successfully + terminal exact-head CI |

| PR #370 — C8.Roster / DD-37 dock_sessions two-tier retention (live uncapped + compact history archive) | NEW BUILD for review: failing-first 3/15 -> 15/15, mutant killed, dock-family suites green; main-session regression legs running at head; siblings + proposals-50 untouched | 2b95d86 | 2026-11-10 (PR body carries the evidence) |

## Final-check queue (hourly final check, WORKFLOW v1 §4)

Merged 2026-11-10, final-check PENDING: PR #361, #362, #363, #365,
#366, #367 (merged 70a478e; Director scoped certification + Keeper
record-truth CONFIRM on record; Director MODE D delta acknowledged
the merge and ordered merged-main receipts published), #364
(merged 318736014). Records batch remainder: PRs #351–#356 rebased
2026-11-10 (981f5ed / 3e122bc / 7308f9b / 1dfa964 / 7bd483b /
4b886ad), exact-head CI running; each joins this queue on merge.

## Standing decisions owed

- 72-35: orphan-temp cleanup design decision.
- 72-17: Studio __RENDER__ remedy ruling (defect OPEN; R-B repair
  unauthorized pending a bounded proposal).
- Q1 / 72-28: everyday-save repair direction (repair the pair,
  mark not guaranteed, or fold into the C-A circuit).
- 72-16 R-1: design review of the bounded proposal (PR #332,
  proposal only; implementation NOT authorized).
- Q-DD44.2 / Q-DD44.3 (DD-44 follow-ups).
- Q-DD42.2: While/Until (64/65) loop conditions have no refusal
  surface for unparseable infix conditions (fails closed; no
  honest refusal receipt).

## Trailing certifications

- Q-DD42.1: DD-42 second-authority certification trailing.
- DD-18: Keeper second certification trailing (Keeper lane;
  listed here for completeness of the shared record).

## Ace rulings recorded 2026-11-10 (full texts ride the next records PR)

- EPISTEMIC DOCTRINE: Mandell is a checkable chain-of-thought
  visibility layer, NOT a source of truth; truth is the checkable,
  predictable, understandable, reasonable, explainable — mathematics,
  logic, and what can be confirmed. Mandell itself falls under that
  law and can be wrong. UNKNOWN is acceptable and never stops
  progress. Working test: can we use it, calculate it, see or
  experience it, is it present in reality or in nature — then create.
  Time is not a factor of progress; the plan (§14) and real
  capability movement govern.
- BILINGUAL MANDELL: chains shown to Ace carry the English gloss per
  step; ordering per Director refinement: Mandell first, English
  second, evidence and ruling last.
