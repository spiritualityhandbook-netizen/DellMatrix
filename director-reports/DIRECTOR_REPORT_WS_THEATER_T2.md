# DIRECTOR REPORT — Workshop/theater T2: view_rooms growth referent

Status: SUBMITTED — held for the Director's return (sleep
mode; nothing certified). Scope: ONE bounded repair in the
view rooms, item T2 of the workshop/theater circuit
(step-1 census: T2 STILL-LIVE, bounded repair candidate
#2, after T6).

## Ruling requested
Accept (or decline) the WIRE-THE-REFERENT disposition:
a view that invented growth stages from node score is
rewired so the stage comes solely from the canonical
growth mechanism (GrowthForce plants), rather than
relabelled (still a second authority) or removed
(the referent exists and is wireable).

## Identity
- PR #214, merged 03b2c30; candidate d5995df; merge
  tree 14c4ce5 == candidate tree; parents 322685d +
  d5995df.
- Code delta: form/dell_matrix/view_rooms.py (growth
  branch rewired, plants= pass-through in
  render_room_ascii), form/dell_matrix/live_visual.py
  and form/open.py (both production callers pass
  forces.growth.plants), new suite
  form/mandell/view_rooms_growth_test.py (9 checks),
  form/regress.py (suite registered; 221 entries).

## Defect and evidence
Traced at base 322685d: the growth room computed every
node's stage as int(score * 2) over the canonical stage
list (seed..fruit), plus a seed/flower skin bump driven
by the same invented index. GrowthForce
(form/dell_matrix/forces.py) is the mechanism that
actually plants node labels and grows them through the
same stage list; node score has no growth meaning. A
high-score unplanted node displayed as late-stage; a
planted node at score 0 displayed as "seed" regardless
of its real plant stage.

## Repair and verification
- filter_nodes_for_room gains plants=: growth stage is
  solely the matching plant's stage (label key,
  truncated to 80 chars exactly as GrowthForce.plant
  stores idea=label[:80]; first plant wins). No match:
  stage=None with stage_source "unplanted" (plant list
  supplied) or "unavailable" (none supplied). Plant
  stages outside the canonical vocabulary are not
  passed through. Score is never consulted for stage.
  The score-driven skin bump is removed in the growth
  branch only; other rooms untouched.
- SWAT Director's-eye pre-mortem before implementation
  (ground: WS_THEATER_T2_PACKET.md in workspace):
  both production callers wired in the same change;
  plants optional (default None) so legacy callers
  keep working and simply make no stage claim.
- Failing-first probe: FAIL on base 322685d, PASS
  after fix (re-verified on candidate at closure).
- Suite view_rooms_growth 9/9 — lens-level checks plus
  a real-Program production-path check through
  Program.view_status (re-verified 9/9 at closure).
  Mutant (score-invention restored post-commit,
  inverse-reverted, diff clean): 5/9 — exactly the 4
  no-stage-claim checks fail.
- Regress 221/221 x3 on candidate d5995df; exact-head
  CI COMPLETE SUCCESS before merge (Python package
  run 41403414701 SUCCESS; Form smoke run 41403414816
  SUCCESS completed 2026-11-02T07:11:37Z; merge at
  07:15:36Z); fresh-clone regress at merge 03b2c30:
  221/221 GREEN.

## Exceptions / limits
- Unplanted nodes now display no growth stage where
  they previously displayed a fabricated one. That is
  the repair, recorded explicitly so it is not read
  as a rendering regression.
- This report covers T2 only. The remaining
  still-live workshop/theater items (T4, T8, T11,
  T12) are recorded in the step-1 census as
  decision-first / campaign-scope and are not
  repaired or certified here.

## Anticipated probes
- "You added a plants parameter nobody passes." —
  Both production callers pass it in the same change;
  the suite proves the production path through a real
  Program, not only the lens function.
- "Plant matching is invented." — plant() stores
  idea=label[:80] and tick/force_growth plant node
  labels; matching by that key is the mechanism's
  own, not a new one.
- "stage=None is a regression." — No plant, no stage:
  the honest state, with stage_source saying why.

## Questions for the Director
Q1. Is WIRE-THE-REFERENT the right disposition when a
    view invents data a canonical mechanism owns —
    should invented displays always be wired to their
    referent where one exists, rather than relabelled
    (T6 pattern) or removed?
Q2. Should the remaining still-live items (T4, T8,
    T11, T12) stay out of the bounded item-by-item
    repair pattern, as the census classified them?
