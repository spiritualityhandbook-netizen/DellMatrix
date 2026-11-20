# SETTLEMENT 2026-11-20 — settled work written into the register

Authority: Ace reconciliation order, 2026-11-20 (in-chat, verified channel):
"Reconcile every hold that can be but if the hold is still valid then keep
it." Performed by Uni as a records act under §32 review; this file is the
per-item provenance record for the register changes in this PR.

## Rows settled (verified per-row before changing)

1. **MWL 135 — DD-54 / C3.Undo (Q-LC.1 undo/redo) — PARTIAL, scoped
   settlement only.** Session-local undo/redo repair merged as PR #481
   (merge commit d17c6b48, 2026-11-18); CODE credit settled 2026-11-18,
   scoped SESSION-LOCAL (Keeper 6975649030). Per Director 7040476004
   (2026-11-20), the broad row is NOT complete: room/multi-actor undo
   and Core II snapshot-stack unification remain UNRESOLVED (deferred
   per Director §6.4 #6967292333). Row set PARTIAL with the settled
   scope and the retained remainder both stated in the row title. (An
   earlier version of this settlement flipped the row to COMPLETE;
   that overstated the scope and was corrected the same day.)
2. **MWL 14 — Q-DD44.3 (Compose recursion cap follow-up; R17).** The
   item is Compose's `_compose_bound` per
   DIRECTOR_REPORT_DD44_BOUNDS_EXPLICIT_2026-11-10 (Q-DD44.3). R17 made
   the bound resolve honestly via `bound_detail` (no phantom 8), merged
   as PR #485 (merge commit 9d7a65b6, 2026-11-18). CODE credit settled
   2026-11-18 (Gemini fallback Keeper CONFIRM, comment 6985521624). The
   row was left OPEN in error after settlement; now COMPLETE.

## Settled items with NO MWL row (no board point created)

3. **R26 — DuoBeta ledger detail stored whole at all cut sites**
   (PR #483, merged c93e358b, 2026-11-18; CODE credit settled
   2026-11-18). Verified 2026-11-20: no row in
   master_work_list_items.json carries this item (nearest rows 72-51 /
   SM-41 and 72-54 are different scopes and were NOT touched). Like
   R19 / R19-SIB / PR #497 before it, R26's credit lives on the CODE
   belt only. No row invented.
4. **R25 — GP-E04 condition shorthand** (PR #496, merged c13428cb,
   2026-11-19). GP-E04 is a Grand Plan Edition 1 execution circuit, not
   an MWL row; no board point created. Its CODE CREDIT HOLD is released
   by Ace's Overseer ruling of 2026-11-20 (posted on PR #496, comment
   7040200362): the single merged-main smoke failure (run 44534366396,
   c7profile 35/36, raw log lost to a re-run before capture) is recorded
   as a NOTED ANOMALY — never reproduced in 11 attempts — noted, not
   blocking. If it ever reproduces, the ruling is revisited and the
   failure is captured in full before any re-run.

## Provenance reconciliation (no status change)

5. **FI-017 — Gemini in-program Docked Operator role.** Intake: Ace,
   2026-11-16 13:22 CST; confirmed in Ace's own words 2026-11-17
   ("freedom with a nursery gate"). Register row of record: goal
   workspace files/SYSTEM_DECISION_REGISTER.md line 127. Repo-side
   mentions in GRAND_PLAN_DIRECTOR_EDITION1_2026-11-18 files agree with
   that provenance. Per Director 7027799816, FI-017 is NOT automatically
   a new COMPLETE entry; no MWL row is created by this settlement.

## Board effect

COMPLETE 39 -> 40 of 182 (21.4% -> 22.0%): MWL 14 flips to COMPLETE;
MWL 135 moves OPEN -> PARTIAL (scoped settlement, remainder retained).
OPEN 86 -> 84, PARTIAL 54 -> 55. All other counts unchanged. Render
regenerated with master_list.py from this directory; --check
byte-diff clean at this PR's head.
