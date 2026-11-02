# DIRECTOR REPORT — Workshop/theater T6: can_edit honesty

Status: SUBMITTED — held for the Director's return (sleep mode;
nothing certified). Scope: ONE bounded honesty repair in the
workshops registry, item T6 of the workshop/theater circuit
(step-1 census: 5 items closed, 7 still-live; T6 was bounded
repair candidate #1).

## Ruling requested
Accept (or decline) the RELABEL disposition: a descriptive
registry field whose name claimed an unenforced capability
(can_edit) is renamed to a claim it can support (focus_areas),
values preserved verbatim, rather than enforced (new scope
authority) or removed (content loss, no honesty gain).

## Identity
- PR #212, merged 91780c5; candidate 99ffa3b; merge tree
  501a383 == candidate tree; parents f850fd8 + 99ffa3b.
- Code delta: form/dell_matrix/workshops.py only (key rename
  x7 + descriptive-only header note); suite
  form/mandell/r73_workshop_test.py (part_focus_honesty,
  5 new checks).

## Defect and evidence
Traced at base f850fd8: seven "can_edit" definitions, zero
key-specific readers in form/ (no enforcement, no display),
no persisted schema stores the key, workshops.html and the
REPL print only id/name/description/commands, and the R7.3
scoped gate derives from the "commands" menu via
workshop_session.scope_stems only. Several listed topics
have no corresponding edit operation at all. The field is
carried only as part of whole-dict payloads
(list_workshops / workshops_status).

## Repair and verification
- can_edit -> focus_areas x7, values verbatim; header note
  states the field is descriptive only and the gate derives
  from commands via scope_stems.
- SWAT Director's-eye pre-mortem before implementation
  (ground: WS_THEATER_T6_PACKET.md in workspace): enforce
  rejected (second scope authority, invented edit ops);
  remove rejected (deletes snap-in-carried descriptive
  content, no honesty gain over relabel).
- Failing-first probe: FAIL on base, PASS after fix.
- Suite r73 71/71 -> 76/76. Mutant (one can_edit restored,
  applied after the real commit, inverse-reverted, diff
  verified clean): 72/76 — exactly the 4 focus checks
  touching the mutated entry.
- Regress 220/220 x3 on candidate 99ffa3b; exact-head CI
  COMPLETE SUCCESS verified in a separate step before merge
  (package 41395607728; smoke 41395607717, completed
  2026-11-02T05:59:59Z); fresh-clone regress at merge
  91780c5: 220/220 GREEN.

## Exceptions / limits
- The payload key rename is a deliberate honest break for
  any out-of-repo consumer reading "can_edit"; in-repo
  consumers were all traced, out-of-repo consumers are
  UNKNOWN and recorded as such.
- This report covers T6 only. The other still-live
  workshop/theater items (T2 view_rooms growth referent
  next; T4, T8, T11, T12) are not repaired or certified
  here.

## Anticipated probes
- "Renaming is cosmetic" — focus_areas carries no verb of
  permission or capability; the suite pins that scope stems
  are unchanged and command-derived, so the gate's single
  authority is untouched.
- "Why keep data nobody reads key-specifically?" — it ships
  in public payloads as descriptive registry data, like
  description; the defect was the claim type, not existence.

## Questions for the Director
Q1. Is RELABEL the right disposition for a descriptive field
    whose name overclaims, or should any field with zero
    key-specific readers be removed instead?
Q2. Should the remaining still-live workshop/theater items
    proceed item-by-item in the same bounded pattern, with
    T2 (view_rooms growth referent) next?
