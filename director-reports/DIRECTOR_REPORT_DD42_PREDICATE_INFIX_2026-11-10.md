# DIRECTOR REPORT — DD-42 / C1.Predicate: infix conditions refuse honestly

Circuit: SS14.4 C1.Predicate (DD-42), cycle 1 of 2 (SS33 cap).
Base: fd88d3d6b47c181c322d6f52a0facc6733af058b (main after
PR #357). Defect grounded in the tour record SS12.47a
(verified live at 7399ee5) and re-verified at the base.

## Defect (mechanism, code-verified at base)

eval_predicate (form/mandell/predicate.py) scans PREDICATES
for a PREFIX match. On no match it resolved the WHOLE
expression as one literal token and judged its truthiness:
"level gt 99" -> matched=True at level=5, and "level lt 3"
also True. Every surface sharing the engine inherited the
lie, each in its own shape:

- Assert (91): stamped PASS on a numerically false claim.
- Guard (92): stamped ALLOW.
- Branch (60, leaf + chain): always took the true arm and
  executed its body.
- Compare (57): its eq: rewrite silently re-answered
  "eq:level gt" — wrong-reason type_mismatch on numeric
  stores, a silently wrong answer on string stores.
- Threshold (73, sibling rewrite): built "gte:level gt" and
  reported ok=True with the mismatch buried in last_result.
- control_runtime.eval_condition discarded the predicate
  dict's error field, returning a bare bool — so no surface
  consuming it could have surfaced a refusal.

## Repair (condition path only; no grammar expansion)

1. predicate.py fallback: a multi-token expression matching
   no predicate prefix returns predicate="unparseable",
   matched=False, error="condition_unparseable". A bare key
   ALONE (one token) keeps the designed truthiness semantics,
   including literal-token resolution (an unknown bare token
   is a literal value; store:<key> is the missing-ref form).
2. control_runtime.eval_condition_detail returns the full
   verdict record (literal layer mapped, error preserved);
   eval_condition keeps its exact bool contract via it.
3. Assert/Guard (spectrum_ops): on a predicate error the
   atom refuses with that error and stamps NO verdict (the
   prior stamp is left untouched; open Try frames record the
   refusal via the existing _fail_open_tx path).
4. Branch leaf (core_ii_exec): refuses; no st.branch taken
   path, no ControlFrame. Chain Branch (chain_exec): when
   the head atom refused with condition_unparseable, the
   wholesale head-refusal pattern (as the D1 gate) applies —
   no arm executes; body occurrences receipt honest skips.
5. Compare (57): a label carrying a comparison operator in
   second position (the infix signature) refuses in place
   with condition_unparseable before any rewrite. Threshold
   (73): the same guard on its gte shorthand (sibling, SS15).
6. English door (operator_bridge.english_to_intent): the
   generic label builder strips leading English function
   words; "if" joined that strip list, so "branch if ready"
   emits the condition "ready" instead of leaking the
   door's own syntax word into the Mandell condition.

## Evidence

- Suite form/dd42_predicate_infix_test.py (25 checks,
  registered; uuid owners; sentinel-stamp discipline for the
  no-verdict checks because last_guard DEFAULTS to ALLOW):
  FAILING-FIRST 15/25 — the 10 failures are exactly the
  defect checks, each lie visible in the record (engine
  infix x4 matched=True; Compare eq-mangled; Threshold
  ok=True; Assert PASS; Guard ALLOW; Branch leaf taken=True;
  chain Branch executed its arm). All 15 designed-behavior
  controls passed pre-fix.
- After repair: 25/25. Defect-restoring mutant (engine
  fall-through restored, committed work protected first):
  17/25 — killed; the 8 failures are the engine-dependent
  checks; the Compare/Threshold surface guards are
  independent code and keep refusing, as designed.
  Inverse-edit restored; 25/25 re-verified.
- Neighbors (direct runs): guard_assert_propagation 16/16,
  dd18 10/10, dd31 21/21, d1_proof_cards 6/6,
  d1_dell57_compare 17/17, cac_i 177/177.
- FIRST full chain on the repair's first form: RED 263/265
  with exactly two reds, both diagnosed and dispositioned
  inside this circuit (no rerun-hoping):
  (a) d1_dell57_compare rewrite_drops_tokens_beyond_two —
  an existing suite PINS the shorthand truncation of tokens
  beyond two ("N 5 dropped" -> eq:N 5). The first-form
  Compare/Threshold guards refused all >2-token labels,
  breaking that pinned contract. Correction: the guards
  refuse ONLY the operator-in-second-position signature;
  truncation without an operator stands (the DD-42 suite
  now pins it as a preserved control).
  (b) cac_i H.en.branch — the English door's
  "branch if ready" built the condition label "if ready",
  which only ever worked through the defect's truthy
  fall-through. Correction at the translation layer (item
  6): the label is the condition itself ("ready", a bare
  key). An English infix ("branch if level gt 99") now
  refuses honestly at the engine; teaching the door to
  translate English infix into Mandell prefix is NOT in
  this circuit's scope.
- Suite after corrections: 28/28 (three checks added: the
  truncation control and two English-door checks).
- Full regression at the frozen head: cited in the PR
  (fwd + --twice, main-session chain, SIG-reset launcher,
  run on the corrected tree).

## Scope

COVERED: the condition path — engine fallback, eval_condition
consumers Assert/Guard/Branch (leaf + chain), the Compare
and Threshold label rewrites, and the English door's
condition-label construction for Branch.
NOT COVERED: While/Until (64/65) loop conditions consume
eval_condition's bool; post-repair an infix loop condition
evaluates False (the loop does not run — the fail-closed
direction) instead of True, but no refusal surface was added
there; flagged for the authorities as a boundary, not
changed silently. Genuine infix PARSING (accepting
level gt 99 as gt:level 99) was not attempted: the plan's
fix family allows refuse-honestly, and refusal cannot
misjudge. Chain continuation policy untouched (Q-DD18.2
baseline preserved).

## Questions for the Director / Grok

- Q-DD42.1: scoped certification of the repair as bounded
  above.
- Q-DD42.2: While/Until boundary — add refusal surfaces
  there in a follow-up circuit, or accept the fail-closed
  bool behavior as the standing contract?

## Anticipated probes

- "Does any designed multi-token form break?" The suite pins
  the prefix battery, named predicates, bare-key truthiness
  (store + literal), the empty condition, and both shorthands.
  Match/Any/All/None (58/67/68/69) use pred_fn patterns, not
  eval_predicate conditions — untouched.
- "Why not parse infix?" Refusal is the smaller honest
  contract; a parser is a grammar change with its own
  ambiguity surface (reserved tokens shadowing store keys).
  If the authorities prefer parsing, it is a separate
  proposal with its own suite.
