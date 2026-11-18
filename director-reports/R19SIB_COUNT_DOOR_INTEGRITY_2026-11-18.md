# R19-SIB — English-door count integrity (all count doors)

**Circuit:** R19-SIB (new, separate from R19; cross-ref GP-E03).
**Authorization:** Director ruling 6987078989 (2026-11-18 :00,
PR #490) under Ace's order to test the English door on all
Dells. Q-A shared semantic contract CONFIRMED (each door keeps
its own bounds/typed errors; Dell 6's 1..5 is NOT imposed on
Dells 13/19). Q-B walk + english_expand hardening INCLUDED,
REPL walk path probed first. Q-C grow/evolve capture
normalization + full-token matching INCLUDED. Q-D FIX-FIRST
build on a separate branch/PR; no merge authorization; Keeper
review + Director exact-head assessment before any credit.

## Defects (failing-first, suite RED on base across all layers)

The audit's battery, extended per layer (probe evidence:
hidden_files/r19_logs/probe_all_doors_2026-11-18.txt; the SIB
suite's first run on unmodified main failed 20+ checks):

1. **english_brain synonym layer (grow verbs):** an unanchored
   re.search extracted the first digit run anywhere in the tail
   — "evolve ideas -3" normalized to "grow ideas 3" (sign
   theft), "evolve ideas 20x" to "grow ideas 20" (suffix
   theft) — and a digit-free tail had its operand DELETED:
   "cultivate ideas banana" -> "grow ideas" (a default grow).
2. **Phrase layer:** the count patterns (grow ×2, walk,
   english_expand) captured with Unicode `\d+`; fullwidth
   counts flowed to _count_value and converted ("grow ２０"
   -> 20).
3. **translate _count_value (3 call sites):** garbage -> the
   caller's default (grow 1, walk 1, expand **50**), executed;
   isdigit-true non-decimal digits (², ①) and oversized digit
   strings CRASHED int() uncaught.
4. **translate fallback grow arm:** any text containing "grow"
   that the strict patterns rejected hard-coded cycles=1 —
   malformed counts became fallback growth.
5. **translate fallback walk arm:** "walk forward <anything>"
   hard-coded steps=1.
6. **_seed_grow (router):** garbage -> 1 via except, 0 -> 1 via
   max(1, ...) — Dell 13's typed refusal and receipt never saw
   the operand.
7. **REPL walk handler (LIVE at the real user path, Q-B probe):**
   `int(args.get("steps", 1))` consumed translate's defaulted
   args directly — pre-repair REPL proof on main: "walk forward
   banana" walked 1 (reported as success), "walk forward ２０"
   walked 20.

## Repair (this PR)

One grammar judges counts everywhere: the leaf's
`_parse_count` (bounded ASCII) + the established count words.

- `english_brain._synonym_rewrite` (grow branch): the tail is
  carried VERBATIM into the rewrite; nothing is extracted,
  nothing is deleted.
- `phrases.py`: the four count patterns use `[0-9]+` — a
  non-ASCII count fails the phrase and reaches a judging door.
- `translate._count_operand` (new): valid -> int; absent ->
  the door's default; malformed -> the RAW string travels.
  Wired into the grow arm (default 1; the "item" no-capture
  sentinel treated as omitted), the walk arm (default 1), and
  english_expand (default 50, omitted only). `_count_value`
  keeps no count-door callers.
- translate fallback grow arm: the trailing operand token is
  judged whole (valid travels; filler/absent -> 1; anything
  else RAW -> Dell 13 refuses).
- translate fallback walk arm: a token after the direction
  word is judged the same way.
- `semantic_router._seed_grow`: mirrors the repaired
  `_seed_cycle` — int travels exactly; strings judged by
  `_parse_count`; anything else travels RAW and Dell 13
  refuses it `invalid_loop_count`. Dell 13's own clamp +
  requested/executed receipt now govern 0 and oversized
  requests (e.g. grow 20 -> requested 20, executed 5).
- `repl.py` walk handler: steps judged by `_parse_count`; a
  malformed count is a typed refusal ("Walk refused: invalid
  count '<x>' — no steps taken.") with NO movement; no
  int() crash path remains.

english_expand's routed door still refuses its correspondence
(pre-existing, unchanged — no route was enabled); its Intent
args are now honest (raw travel instead of a silent 50).

## Evidence

- New suite `form/r19sib_count_door_test.py` (registered in
  form/regress.py): **45/45** — brain preservation, translate
  judgment, routed grow refusals with zero growth, REPL
  subprocess checks (walk 3 walks 3; walk banana / walk ２０
  refuse with no silent step; grow banana -> RESULT ok=False).
- Disclosed re-pins in `translate_intent_args_test.py` (18/18):
  "grow 0" (the old pin asserted the abolished translate-level
  clamp) and "grow abc" (SM11's anti-fabrication pin now
  asserts RAW travel instead of blessing None/default-1). Both
  re-pins cite this ruling in place.
- Neighbors green: translate_word_counts 21/21,
  translate_dead_args 21/21, lm4_tollbooth 26/26,
  core_i_arg_gate 92/92, loop_bounds 27/27, dd14 11/11,
  dirf13_loop_count PASS, flow_executor PASS,
  d1_registry_leaf PASS, phrase_tests PASS,
  repl_seed_error_visibility PASS.

## Scope / non-claims

Count doors only. Label doors and no-operand arms were audited
(PR #490) and are untouched. No route was enabled or changed;
walk/expand routed refusals stand as before. Regression ×3 +
terminal CI at the exact head, Keeper review, and the
Director's final assessment remain ahead; no credit is claimed
by this report.
