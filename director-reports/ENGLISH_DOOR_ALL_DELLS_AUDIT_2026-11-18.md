# ENGLISH-DOOR AUDIT — ALL DELLS (2026-11-18)

**Ordered by:** Ace (2026-11-18: "make sure the English door is
tested on all dells not just cycle, have the director and Gemini
help u"). **Author:** Uni. **Status:** AUDIT COMPLETE, repairs
NOT authorized — packaged for a Director contract ruling, with
Gemini's independent coverage critique solicited in parallel.
**One in-scope exception:** the audit found a residual hole
inside R19's own already-ruled contract; that repair was made
under R19's existing authorization (PR #489, head 48494488).

## Method

Every `Intent` construction site in `form/mandell/translate.py`
(77 sites) was inventoried and grouped: COUNT doors (an explicit
numeric operand), LABEL doors (a name/label operand), and
NO-OPERAND arms. Each count door was probed end-to-end —
`translate(text)` then `route_intent(program, intent, text)`,
plus a translate-alone exception check — with the battery:
valid digit, number word, `-3`, `banana`, `20x`, `²`, `２０`
(fullwidth), a 5000-digit operand, and the omitted form.
Probe output saved at
`hidden_files/r19_logs/probe_all_doors_2026-11-18.txt`.

## Findings

### F1 — Cycle (Dell 6): CLOSED by R19 + router-hole round
Post-repair all doors refuse malformed counts typed with zero
growth. The audit caught one residual: `_seed_cycle` judged the
routed count with bare `int()`, which converts non-ASCII digits
(`route_intent("cycle ２０")` EXECUTED, seed `06[Cycle] :: 20`)
while the seed door refused. Repaired at PR #489 head
`484944886f70de54b03a7d0b459f65cebdc644f9` (the router now uses
the leaf grammar `_parse_count`); suite 58/58 with route-level
checks. Disclosed on #489 as comment 6986968199.

### F2 — Grow family (Dell 13 Loop, phrase-match): DEFECT, LIVE
Phrasings `grow …`, `grow ideas …`, `evolve ideas …` execute at
the real routed door (ok=True, state grows):
- `grow -3`, `grow banana`, `grow 20x`, `grow ²` → silently
  cycles=1 and EXECUTES (SILENT_DEFAULT).
- `grow ２０` → cycles=20 (CONVERTS non-ASCII digits).
- `grow ` + 5000 digits → **translate CRASHES** (uncaught
  ValueError from `int()` digit limit).
- Capture is inconsistent across phrasings: `evolve ideas -3`
  yields cycles=3 and `evolve ideas 20x` yields 20 (prefix
  capture), where `grow 20x` yields 1.
Mechanism: `translate.py` grow arm (~:565) uses
`max(1, _count_value(label, 1))`; `_seed_grow`
(`semantic_router.py`) independently defaults garbage to 1 and
floors with `max(1, …)`. Dell 13's own leaf already refuses
malformed counts typed (`invalid_loop_count`, DIR-F13) — the
malformation is destroyed upstream before the leaf can judge it.

### F3 — Walk family (Dell 19 Drive, phrase-match): DEFECT AT
### TRANSLATE, execution-inert via the routed door today
`translate.py` walk arm (~:582) uses `_count_value(label, 1)`:
-3/banana/20x/² → steps=1 (SILENT_DEFAULT in the Intent);
２０ → steps=20 (CONVERTS); oversized → **translate CRASHES**.
However `route_intent` currently refuses EVERY walk intent
("no verified correspondence for ('walk', Dell 19)"), so nothing
executes via the routed door. CAVEAT (UNKNOWN): the walk arm's
own comment states the REPL walk handler reads steps from
Intent.args — a second door, NOT probed in this pass. Probe owed
before any closure claim.

### F4 — english_expand (Dell 13, phrase-match): DEFECT AT
### TRANSLATE, execution-inert via the routed door today
`translate.py` (~:598) uses `_count_value(label, 50)` — the
default is **50**: a malformed label that reaches the arm puts
cycles=50 in the Intent (SILENT_DEFAULT, fiftyfold); ２０
converts to 20; oversized → **translate CRASHES**. Some
malformed phrasings fall out of the phrase match entirely and
are refused downstream as unknown (honest but incidental).
`route_intent` refuses the english_expand correspondence, so
nothing executes via the routed door today.

### F5 — The shared mechanism
`_count_value` (`translate.py`) is the single defect mechanism
behind F2–F4: it returns the caller's default for any
non-digit non-word token (silent default), converts via
`str.isdigit()` + unbounded `int()` (Unicode conversion +
oversized crash). R19 removed Cycle's dependence on it; three
call sites remain (grow, walk, english_expand).

### F6 — Label doors: inventoried, no count grammar applies
Move/Copy/Delete/Replace/Patch (Dells 85–88), Get/Select/Match
(56/51/58), Create/place, Stamp's mark, Discover's label, and
the Core-II `dell NN` / `NN[Name] :: label` fallback carry
name/label operands by design; their leaves judge existence
and validity. Not probed with the count battery (not
applicable). The `dell NN` address parse is bounded
(`[5-9]\d`, exactly two digits) — no crash surface found.

### F7 — No-operand arms: inventoried
Save/Rollback/Show/Pause/Transform/Tone/Help and similar arms
take no operand; trailing text is inert by grammar design.

## Proposed contract (for the Director's ruling)

Extend R19 ruling point 3 to EVERY count door, verbatim in
effect: an explicitly malformed count is a deterministic typed
refusal before any mutation (no silent default, no prefix
capture, no Unicode conversion, length checked before `int()`);
a genuinely omitted count keeps the door's established default
(grow 1, walk 1, expand 50 — defaults themselves unchanged);
a valid count travels exactly and the executing leaf remains
the single clamp + report + refusal authority; one grammar
(`_parse_count`) judges counts everywhere.

Proposed circuit (working name R19-SIB, English-door count
integrity): failing-first matrix per door (including the REPL
walk-handler probe for F3 and routed-door probes for all),
repairs at the `_count_value` call sites + `_seed_grow`,
regression ×3, exact-head CI, Keeper review, Director final
check — the R19 shape.

## Questions for the Director

Q-A. Contract as proposed, or door-by-door variation?
Q-B. Walk/expand: repair translate now (defense in depth; the
REPL walk door is unprobed) or defer until their routed
correspondence lands?
Q-C. The grow-phrasing capture inconsistency (F2): normalize
capture across phrasings inside the same circuit?
Q-D. Placement: a new R-order item after R19, or an E-series
item inside Grand Plan Edition 1?

## Gemini's lane

An independent coverage critique was solicited from Gemini
(Acting-Keeper-model lane, via the API connector): missed
doors, missed malformed classes, classification disputes, and
count-like operands hiding in the label doors. Her reply is
GEMINI-REPORTED until Uni verifies each claim against the code;
verified additions will ride a follow-up addendum to this audit.
