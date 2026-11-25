# DIR-F13 — LOOP UNICODE-DIGIT REFUSAL — packet

Circuit: Director repair wave (Ruling #7), DIR-F13 (P2, OPEN).
Finding: 13[Loop] with the superscript-two character as count raises
ValueError instead of an honest refusal (str.isdigit() accepts
characters int() cannot parse).
Base: main da9e0b2. Branch: uni/dirf13-loop-count.
Worktree: ~/workspace/nbd-omega-dirf13.
Ground: hidden_files/dirf13_ground.md.

## Contract (DIRECTOR_FINDINGS_REGISTER.md, DIR-F13)
- Define the accepted count grammar; parse/refuse safely BEFORE
  growth; avoid unbounded conversion for huge counts.
- Test superscript digits, accepted decimal digits, malformed text
  and oversized decimal strings.
- Refusal executes zero cycles and leaves the program usable;
  preserve ordinary clamping (1..5) and count receipts.
- A contract gap in current code, not introduced by the step 6 patch.

## Defect sites (verified by code read this run, da9e0b2)
- form/mandell/executor_leaf.py primary == 13 (Loop), ~L187-200:
  `if raw_label and not raw_label.isdigit(): refuse` then
  `requested = int(raw_label)` — '²'.isdigit() is True but
  int('²') raises ValueError; int('9'*5000) raises ValueError
  (CPython conversion limit) BEFORE the 1..5 clamp runs.
- SIBLINGS, same isdigit->int assumption (AGENTS.md §15 sweep):
  primary == 6 (Cycle) L129 `int(label) if label.isdigit() else 1`;
  primary == 48 (macro) L479-481 per-token `if tok.isdigit():
  n = int(tok)` and L492 `int(label) if label.isdigit() else 5`.
  Both crash identically on '²' tokens. Their existing contract is
  a silent default (1 / 5 / 3), NOT a refusal — the repair makes
  them crash-safe while preserving that default semantics.
- Same-class float sibling: primary == 16 (Decay) L224
  `label.replace(".", "", 1).isdigit()` then `float(label)` —
  float('²') raises ValueError identically. Decay's factor grammar
  is distinct (floats, step-6 B1 certified scope); this circuit
  adds ONLY a crash guard there (unparseable factor keeps the
  default 0.9, exactly as a non-digit label does today) and a
  witness; no Decay verdict/message change.
- Elsewhere isdigit sites (english_brain, phrases, registry,
  query_ops, inspire_pack, *_150_loop mirrors): checked by grep in
  the ground; none is the canonical Loop/Cycle/macro count path.
  The single count-grammar owner is executor_leaf's helper below;
  mirrors are legacy/non-authoritative for counts (authority-first:
  live handlers are in executor_leaf.py). Recorded, not widened.

## Count grammar (DEFINED by this circuit)
A count label is valid iff it is EMPTY (means 1 for Loop/Cycle)
or matches ^[0-9]{1,9}$ — ASCII decimal digits only, at most 9
digits, checked BEFORE any int() conversion.
- Non-ASCII digits (superscripts '²', Arabic-Indic '٣', fullwidth
  '５', circled digits) are REFUSED by Loop (invalid_loop_count)
  and fall back to the default in Cycle/macro — never converted,
  never a crash. Rationale: receipts and the 1..5 bound are stated
  in ASCII; silently accepting Unicode decimal values would make
  the executed count depend on Unicode tables the contract never
  named. The choice is explicit here, per the register.
- Oversized ASCII strings (>9 digits) are REFUSED by Loop before
  conversion (same invalid_loop_count refusal); Cycle/macro fall
  back to default. No int() is ever called on an unbounded string.
- Ordinary counts unchanged: '' -> 1, '3' -> 3, '99' -> clamped 5
  with the requested/executed receipt line intact (B2 witness).

## SWAT DIRECTOR'S-EYE PRE-MORTEM — recorded BEFORE implementation
How the Director would most plausibly break this fix:
- Custodian: he diffs state, not messages — after a refused Loop
  ('²', oversized) he checks nursery pending / proposal counts are
  byte-identical to before (zero growth), and that the program
  still executes a lawful Loop afterwards (usable, not poisoned).
- Interpreter: he tries the OTHER count paths — Cycle (6) and
  macro/replay (48) with '²' tokens, hunting the identical crash
  one Dell over; he tries chain execution of 13[Loop] with '²'
  (does the chain report the atom failed, not ok?) and mixed
  labels ('3²', ' ² ', '٣') through the public seed path.
- Sentinel: he probes refusal identity — the refusal must stay
  invalid_loop_count with zero cycles; a fix that silently runs 1
  cycle (Cycle-style default) for Loop would be a semantic
  downgrade he would flag; non-ASCII acceptance would be an
  unrecorded grammar expansion.
- Mechanic: he feeds '9'*5000 and '9'*100000 watching wall time —
  conversion must never happen (length gate first); he checks the
  requested/executed receipt against the actual nursery delta for
  lawful counts, and re-runs the step-6 suite (B2 contract) to
  catch a clamp regression.
Material counterexamples block the implicated claim only
(DIR-WF-001 P1 amendment); dissent recorded below.

## SWAT REVIEW — recorded BEFORE implementation
- Custodian: AGREE. Fix touches no persistence authority; refusal
  paths assert zero nursery delta and post-refusal usability.
- Interpreter: AGREE with one recorded condition — the ASCII-only
  grammar must be stated in the packet and the suite (it is, above
  and in W2), so the '٣'/'５' behavior is a defined refusal, not
  an accident. Sibling Cycle/macro keep their default semantics;
  only the crash is removed.
- Sentinel: AGREE. Refusal identity preserved; no new grant, gate
  or authority; no silent grammar expansion.
- Mechanic: AGREE. Length gate precedes int(); helper is one
  shared owner for 6/13/48 (no second count parser); mutants
  defined per defect below.
Dissent: none material. Unanimity 4/4 recorded as method, NOT as
a truth gate (DIR-WF-001). Implementation proceeds under Ace's
standing authorization. Certification is NEVER self-performed.

## Design (ratified above)
- executor_leaf.py gains ONE module-level helper:
  _parse_count(text) -> int | None. Returns None unless text is
  non-empty, len <= 9, text.isascii() and all chars in '0123456789'
  (explicit ASCII check, not isdigit/isdecimal). int() is called
  only on a validated string.
- Loop (13): raw_label empty -> requested 1. _parse_count None ->
  the existing B2 refusal verbatim (ok=False,
  error="invalid_loop_count", "no cycles run", zero growth).
  Valid -> requested/executed/clamp/receipts exactly as step 6.
- Cycle (6): n = _parse_count(label.strip()) or 1, then the
  existing 1..5 clamp — identical outcomes for every previously
  lawful label; '²'/oversized now take the default instead of
  raising.
- Macro (48): per-token n = _parse_count(tok) when not None (else
  keep current n); final n = _parse_count(label.strip()) or 5.
  Same default semantics, crash removed.
- Decay (16): factor parse wrapped so an isdigit-passing but
  float-unparseable label keeps factor 0.9 (today's non-digit
  behavior); parseable factors unchanged.

## Suite + mutants
New suite form/dirf13_loop_count_test.py (registered in regress):
W1 '²' refusal (zero growth, usable after); W2 '٣'/'５' defined
refusal; W3 '9'*5000 + '9'*100 oversized refusal before conversion;
W4 ordinary ''/'3'/'99' clamp + receipt (B2 regression); W5
malformed 'abc'/'2.5'/'-3' refusal unchanged; W6 Cycle '²' ->
default 1, no crash, lawful Cycle after; W7 macro token '²' ->
no crash; W8 Decay '²' factor -> no crash, default behavior;
W9 chain-path Loop '²' reports the atom failed (not ok).
Mutants (defect-restoring, must fail the new suite):
M1 restore the bare isdigit gate in Loop -> W1/W3 fail.
M2 remove the length gate (convert any ASCII digit string) ->
W3 oversized check fails (ValueError or conversion attempted).
M3 ASCII check removed (isdecimal accepted) -> W2 fails.

## Closure discipline
Failing-first probe -> build -> suite + mutants -> neighborhoods
(step6_leaf_honesty, d1 leaf suites, regress entries touching
executor_leaf) -> regress x3 sequential (fwd / --twice /
--order rev), logs under hidden_files/dirf13_logs/ -> PR ->
exact-head CI verified COMPLETE in a SEPARATE step -> merge
(tree equality) -> fresh-clone regress -> ledger + POST_PLAN +
register -> Director report with Anticipated probes + Questions
for the Director, published to director-reports/ via docs PR.

## Status
IN FLIGHT — GATE-STOP at exact-head CI verification (separate step).
- Failing-first probe (hidden_files/dirf13_probe.py) on unmodified
  da9e0b2 reproduced EVERY defect via the public path: Loop '²'
  ValueError; Loop '9'*5000 ValueError (conversion limit); Loop '٣'
  silently accepted as 3 (accidental Unicode grammar); Cycle '²',
  Decay '²', Macro '²' all ValueError. On fixed code every line
  flips: Loop refusals invalid_loop_count with delta 0, ordinary
  '3' unchanged, siblings crash-free with defaults preserved.
- Built: executor_leaf.py (_parse_count owner + Loop/Cycle/Macro
  grammar + Decay float guard), regress.py (suite registered;
  216 -> 217 entries). Candidate 2a87021, tree 50965c8.
- Suite DIRF13_LOOP_COUNT 17/17.
- Mutants (killed, reverted from the saved good copy, suite
  re-verified 17/17): M1 bare isdigit gate in Loop 10/17 (exactly
  the superscript/arabic/fullwidth/oversized/malformed/chain
  checks); M2 length gate removed 14/17 (both oversized + Cycle
  oversized); M3 ASCII grammar removed (isdecimal) 13/17
  (arabic/fullwidth accepted + downstream base-delta fallout).
- Neighborhoods green: step6 34/34, step7 28/28, step8 22/22,
  step9 17/17, dirf12 20/20, d1 leaf 22/22 + leaf2 33/33 +
  leaf3 44/44 + leaf4 36/36.
- Regress x3 COMPLETE on 2a87021 (logs hidden_files/dirf13_logs/):
  fwd 217/217 GREEN; --twice 217/217 GREEN x2; --order rev
  217/217 GREEN. Disclosure: leg 2's first attempt was killed by
  a VM replacement at 200/217 with zero failures — NO RESULT,
  re-run in full (surviving leg-1 log + re-run logs are the
  evidence).
- PR #196 OPEN (uni/dirf13-loop-count -> main). Next step
  (separate): verify exact-head CI on 2a87021 COMPLETE SUCCESS
  -> merge (tree equality) -> fresh-clone regress -> ledger +
  POST_PLAN + register -> Director report + publication.


## Closure addendum (2026-11-01)
CLOSED IMPLEMENTED-VERIFIED. Exact-head CI on candidate
2a87021 verified COMPLETE SUCCESS in a SEPARATE step
before merge (package run 41325908103 SUCCESS; smoke
run 41325908212 SUCCESS completed 16:38:07Z; head_sha
== 2a87021). PR #196 MERGED as 81c976a (merge tree
50965c8 == candidate tree; parents da9e0b2 + 2a87021).
Fresh-clone regress at merge 81c976a: 217/217 GREEN
(hidden_files/dirf13_logs/freshclone_regress.log,
fresh clone HEAD verified 81c976a before the run).
Ledger row + POST_PLAN note done; register DIR-F13 ->
IMPLEMENTED-VERIFIED. Director report
DIRECTOR_REPORT_DIRF13.md written; publication to
director-reports/ via docs PR follows under the same
discipline. NOT certified.
