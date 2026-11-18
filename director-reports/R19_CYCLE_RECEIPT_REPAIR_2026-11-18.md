# R19 — Cycle Count Truthfulness Repair (2026-11-18)

**Circuit:** R19 (Limits Census row 19; Limits Verification Wave 4
classification: value faithful, visibility DEFECT-CONFIRMED).
**Authority:** Director ruling 2026-11-18 (R19 binding contract,
published on GitHub): Dell 06 Cycle, including its flow-program
route, uses the same ruled 1..5 execution bound as the other
Cycle/Loop paths; the unruled flow ceiling of 99 is removed; the
receipt must explicitly show requested / executed / remaining
without implying the full request succeeded; invalid counts refuse
without executing growth; automatic continuation beyond five is
NOT authorized.
**Base:** main `3a8b1412e026cfdc646bf66793749212ddb672d8`.

## Defect (reproduced on base by the R19 census probe, 11/11)

1. `form/mandell/executor_leaf.py` Cycle arm clamped the parsed
   count and printed ONLY the clamped value (`Cycle x5` for a
   request of 20); the request was lost. `note_seed` likewise
   recorded only the clamped value (unchanged by this repair: it
   records the seed as executed; the receipt is the disclosure
   surface — flagged here for the record).
2. `form/mandell/semantic_router.py` `_seed_cycle` clamped inside
   seed construction, so no downstream receipt could name the loss.
   The Loop seed builder (`_seed_grow`) applies no upper clamp —
   the in-codebase precedent this repair follows.
3. `form/mandell/translate.py` cycle arm clamped inside Intent
   construction the same way (`cycle 20` -> count 5).
4. `form/mandell/flow_executor.py` `_args_from_label` applied an
   UNRULED 99 ceiling: flow step record (count 20) and execution
   (clamped to 5 downstream) disagreed, undisclosed.

## Repair (this PR)

- **executor_leaf Cycle arm:** keep `requested`, clamp only the
  executed count, append a truthful count line mirroring the Loop
  B2 pattern — `Cycle: requested 20, executed 5, remaining 15.
  (clamped to 1..5)`; `requested 0, executed 1. (clamped to 1..5)`
  for under-range; unadorned `requested 3, executed 3.` in range.
  The `Cycle x{executed}:` growth line is unchanged.
- **Malformed counts (ruling point 3):** a genuinely omitted count
  keeps the default of 1, but an explicitly malformed count
  (non-ASCII, oversized, negative, garbage, trailing tokens) is a
  typed refusal at the leaf — `ok=False`,
  `error="invalid_cycle_count"`, no growth — at Loop B2 parity.
  Router and flow adapters carry a malformed count RAW to the leaf
  instead of silently defaulting it. This supersedes the DIR-F13
  Cycle default for explicit labels: the two DIR-F13 checks that
  pinned malformed -> default-x1 (superscript, oversized) are
  RE-PINNED to the refusal with disclosure in
  `form/dirf13_loop_count_test.py`; DIR-F13's crash-safety contract
  (int() never sees an unvalidated string) is preserved.
- **semantic_router._seed_cycle / translate cycle arm:** early
  upper clamp AND floor removed; the requested count travels in
  the Intent/seed exactly as supplied (0 and negatives included —
  the leaf disposes); the leaf is the single clamp + report +
  refusal authority.
- **flow_executor._args_from_label:** the 99 ceiling removed; the
  count is read under the ONE shared grammar (`_parse_count`):
  valid counts travel as-is, malformed labels travel raw to the
  leaf refusal, omitted labels default.
- **chain_exec.py:480:** verified consistent (Loop-body repetition
  re-derives from the effective label and clamps identically); no
  change.

## Evidence

- Failing-first suite `form/r19_cycle_receipt_test.py` (registered
  in `form/regress.py`): 39 checks — seed Cycle at 0/1/5/6/20/100,
  in-range exactness, omitted-count default, the malformed matrix
  (garbage / negative / superscript / fullwidth / oversized /
  trailing tokens -> typed refusal, no growth, no history trace),
  Loop receipt guard, router seeds (incl. 0, -3, raw malformed
  travel + leaf refusal), translate Intent + end-to-end (incl.
  cycle 0), flow args (20 / 99 / 150 / omitted / malformed) +
  reconciliation end-to-end, chains containing a Cycle atom and a
  Loop atom at 20. RED on base (clamps hid the request at every
  face; flow capped at 99), GREEN 39/39 after the repair. Seed
  legs are PUBLIC_ENTRY_PATH (real Program via execute_seed);
  router / translate / flow-args legs are INTEGRATION.
- Named regressions GREEN after the repair: loop_bounds_test,
  dirf13_loop_count_test (with the two disclosed re-pins),
  dd14_loop_body_test, core_i_arg_gate_test,
  translate_word_counts_test, d1_registry_leaf_test,
  flow_executor_test.
- Full regression campaign x3 + exact-head CI: see the PR's
  campaign receipt (posted on completion). CAMPAIGN NOTE: leg 1 at
  head fe46c80 returned REGRESS 300/302 with two reds, both
  diagnosed as NON-PRODUCT: (a) this suite was marked RED at rc=0
  with smoke() returning True — the harness (form/regress.py)
  scores a suite by the LAST N/M token in its stdout, and a check
  detail ("20/5") was the last token because the suite printed no
  final tally; the suite now prints `R19_CYCLE_RECEIPT: 39/39`
  last. (b) d1_registry_leaf4_test's symbiosis check failed
  in-campaign but passes standalone on BOTH the R19 tree and a
  main tree, AND on an empty state dir (36/36) — the campaign had
  run against form/state residue accumulated from this worktree's
  earlier standalone test runs; the campaign was relaunched
  against a clean state dir. Neither red reproduces against the
  product code at this head.

## Scope / non-claims

- No bound changed: 1..5 stands exactly as ruled. No automatic
  continuation. Loop arm untouched. `translate("run 20 cycles")`
  routes to Drive (Dell 19) and never reaches Cycle — recorded by
  the census probe, OUT of R19 scope.
- No scoreboard credit is claimed by this report; CODE credit
  settles only under the standing rule (merged-main behavioral
  proof + both authorities' acts).

## CORRECTION ROUND — Director 6986258354 (2026-11-18 :30 delta)

The Director's source finding is CONFIRMED and reproduced
failing-first at the public translate→execute door (probe saved at
`hidden_files/r19_logs/probe_translate_prefix.txt`). Pre-repair,
on a program already holding an idea: `cycle -3` executed 1;
`cycle banana` executed 1; `cycle 20x` executed 20 (prefix
theft); `cycle ²` executed 1; `cycle ２０` executed 20 (Unicode
digit conversion); and an oversized digit operand CRASHED
translate with an uncaught exception (int() digit limit) — worse
than silent execution. The suite had not tested malformed
English inputs; the gap was Uni's.

Repair (`form/mandell/translate.py`, Cycle arm only): the
operand is now consumed as a whole token after the keyword.
Omitted (or the continuation word "times") → default 1. A valid
count (ASCII digits, length checked BEFORE int conversion, or
an established number word) travels as an int, still with no
clamp/floor. ANY other explicit token travels RAW in the
Intent args/seed, and the Dell 6 leaf refuses it typed
(`invalid_cycle_count`, zero growth) — one grammar authority
(the leaf), shared with the router/flow paths. Post-repair probe:
all six malformed cases refuse typed with zero growth; bare
`cycle`, `cycle 3 times`, `cycle three times`, `cycle 20` are
unchanged.

Sibling phrase, as directed: `run cycles -3` is NOT routed to
Dell 06 — the earlier Drive arm claims every `run ...` phrase
(verified identical on main: `run cycles 3`, `run cycles`, and
`run cycles -3` all yield `19[Drive] :: run`). The Cycle arm's
`run\s+cycles?` alternative is shadowed dead grammar. Per the
directive it is NOT reassigned; the established Drive route for
`run 20 cycles` is preserved and pinned in the suite.

Durability label (directive point 3): the requested/executed/
remaining disclosure is **RECEIPT-ONLY**. It is produced in the
execution result at run time; no structured field carries it,
and the persisted program history does not preserve it —
demonstrated in the suite by save + reload after `cycle 20`
(no count disclosure in the reloaded history). `note_seed`
records the seed with the executed count only. No durable
preservation is claimed.

Suite is now 52/52 (13 new checks: the malformed-English
matrix with no-growth, omitted/established forms, Drive-route
preservation + run-cycles pin, receipt-only demonstration).
Named neighbors re-run green: translate_word_counts 21/21,
translate_intent_args 18/18, translate_dead_args 21/21,
lm4_tollbooth 26/26, dirf13 17/17, core_i_arg_gate 92/92,
loop_bounds 27/27, dd14 11/11, flow_executor 28/28,
d1_registry_leaf 22/22.

## ROUTER-HOLE ROUND — all-Dells English-door audit (2026-11-18)

Ace ordered the English door tested on ALL Dells, not only Cycle.
The audit probe (translate -> route_intent battery over every
count-bearing English family; saved at
hidden_files/r19_logs/probe_all_doors_2026-11-18.txt) found a
residual hole INSIDE this circuit's own repair: _seed_cycle
judged the routed count with bare int(), which silently converts
non-ASCII digits — route_intent("cycle ２０") EXECUTED (seed
06[Cycle] :: 20) while the seed door refused the same token.
Signs converted the same way. The R19 suite had exercised the
English door through execute_seed only, so the routed door's
conversion was unobserved — an instrument gap in Uni's own
testing, disclosed.

Repair (this head): _seed_cycle judges the count with the leaf's
own grammar (_parse_count): an int travels exactly; a string
travels only if it is in the grammar; anything else travels RAW
and the leaf refuses it typed. The suite gains six route-level
checks (Face 3c) through the real routed door — cycle ２０,
cycle +3, cycle ², cycle -3, cycle banana refuse with zero
growth; cycle 20 executes — and stands 58/58. The wider audit
(grow/walk/expand families carry the same defect class) is
packaged separately for a Director contract ruling; it does not
expand this circuit's scope.
