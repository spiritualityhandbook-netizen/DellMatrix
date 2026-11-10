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
| PR #345 — DD-45 execute_chain refuses failed seeds | Refreshed disposition (flicker closure changes the basis; PR #361 merged c13de21) | 5fa4d5f | 2026-11-10, comment 6777027932 |
| PR #350 — DD-31 diagnostic capture | Renewed merge ruling at post-rebase head (prior conditional authorization named superseded head 7cdb880 and does not carry) | rebase in flight — head lands here | prep running 2026-11-10 |
| PR #360 — DD-44 loop bounds (Q-DD44.1) | Refreshed disposition at post-rebase head | rebase in flight — head lands here | prep running 2026-11-10 |
| PR #348 — DD-14 / C1.Loop | Refreshed disposition after regression legs 2–3 complete (current: review PASS + MERGE HOLD) | 813b2aa | legs running 2026-11-10 |

## Final-check queue (hourly final check, WORKFLOW v1 §4)

Merged 2026-11-10, final-check PENDING: PR #361, #362, #363, #365,
#366. Joining on merge: PR #367 (smoke pending at publication),
PRs #351–#356 and #364 (records batch, runner active).

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
