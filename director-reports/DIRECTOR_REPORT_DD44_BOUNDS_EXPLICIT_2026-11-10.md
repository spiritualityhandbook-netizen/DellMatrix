# DIRECTOR REPORT — DD-44 / C1.Bounds: loop bounds explicit, no silent 8

Circuit: SS14.4 C1.Bounds (DD-44), cycle 1 of 2 (SS33 cap).
Base: b27f6745a48d19abd5727d08ac9350381c05eb2e (main).
Authority: Ace ruling SS12.56 (extended SS12.63a), which
SUPERSEDES the default half of the 72-21 contract (PR #321:
"loop bounds exact including default 8" — bounds-exact
stands, the silent default goes). Contract change routed
through this report + PR per SS12.56.

## Defect (probe-verified at base)

bound_of(st) read st.limit through validate_bound, which
maps "" and "max" to (True, 8); bound_of returned 8 even
when validation FAILED. A While with a true condition and
no Limit ran exactly 8 iterations and ended bound_reached.
The Limit setter shared the silence: a bare Limit stored
'8', and Limit "max" also stored '8' (not the maximum).
Frame stamps and leaf messages displayed the phantom 8 as
if it had been stated.

## Repair (loop-bound domain + its setter; one authority)

1. control_runtime.bound_detail(st) resolves the stored
   limit as specified (a stated number, or the word max =
   MAX_BOUND 64) / unspecified / invalid, with domain and
   raw value. bound_of is DELETED — no accessor may hand
   back an unstated default. bound_display renders the
   stated number or the honest status word for receipts.
2. Chain While/Until (chain_exec): the zero-iteration
   branches run first and need no bound (nothing was going
   to run). A loop that WOULD iterate resolves bound_detail:
   unspecified -> head refusal bound_unspecified (frame
   fails, body occurrences receipt honest skips, chain
   error set, head receipt carries the refusal, and the
   message states the full why: state the count with
   Limit (72); nothing ran). Invalid stored limit ->
   invalid_limit refusal, same shape. Specified -> the
   exact stated count, bound_reached semantics unchanged.
3. Frame stamp (bound) and the core_ii leaf messages show
   the stated number or "unspecified" — never a phantom 8.
4. Dell 72 (query_ops): a bare Limit refuses
   limit_unspecified and stores nothing; "max" stores 64;
   numerics exact; invalid and over-max (>64) still refuse
   invalid_limit — the hard safety ceiling is preserved.

## Contract updates inside existing suites (disclosed)

- loop_bounds_test (72-21): W2's default-8 pin rewritten
  to the DD-44 refusal expectation with the supersession
  cited in place; W3 (condition-clearing exit) now STATES
  its bound (8) — behavior checks unchanged; W4's frame
  bound expectation 8 -> "unspecified" (zero-iteration
  behavior unchanged). Suite: 27/27.
- guard_assert_propagation_test SS I: its While chain now
  states Limit 8; the Guard-propagation subject is
  unchanged. Suite: 16/16.

## Evidence

- Suite form/dd44_bounds_explicit_test.py (16 checks,
  registered): FAILING-FIRST 9/16 — the 7 failures are the
  defect checks with the 8 visible (8 body runs, frame
  bound=8, bare Limit -> '8', max -> '8', invalid stored
  limit ran anyway). All 9 controls passed pre-fix.
- After repair: 16/16. Mutant (bound_detail returns a
  default 8 for unspecified): 12/16 — killed; the setter
  checks are independent code and kept passing, as
  designed. Inverse-edit restored; 16/16 re-verified;
  tree clean against the commit.
- Neighbors (direct): loop_bounds 27/27,
  guard_assert_propagation 16/16, cac_i 177/177,
  dd31 21/21, dirf13_loop_count 17/17.
- Full regression at the frozen head: cited in the PR
  (main-session chain, SIG-reset launcher).

## Audit (SS12.63a deliverable — quantity domains)

- Loop bound (While/Until via st.limit): WIRED (this PR).
- Limit setter (Dell 72): WIRED (this PR).
- Loop 13 count grammar: its own receipted grammar
  (bare = "requested 1, executed 1"; stated counts clamped
  1..5 with the clamp on the receipt). NOT changed —
  pinned as an audit control in the new suite. Q-DD44.2
  asks whether the ask law should extend to it.
- Compose recursion bound (_compose_bound, spectrum_ops):
  reads st.limit through validate_bound, else its own
  COMPOSE_BOUND — a hard-safety recursion cap. AUDIT-ONLY
  here; noted that a stated Limit currently also caps
  Compose depth via that read. Q-DD44.3.
- ForEach 66: its count is the selection size — explicit
  by construction; no default exists. No change.
- Nursery proposal bound (50/session, DD-37) and dock
  session bounds: program constants with receipts, not
  st.limit consumers. Named for completeness; untouched.
Coverage is claimed ONLY for the loop-bound domain and its
setter, per SS12.63a — never for the family wholesale.

## Scope

COVERED: While/Until bound resolution, the frame/leaf
displays, the Dell 72 setter. NOT COVERED: Loop 13's
grammar (Q-DD44.2), Compose's cap (Q-DD44.3), DD-42's
While/Until CONDITION boundary (PR #359, separate
circuit), chain continuation policy (Q-DD18.2 baseline).

## Questions for the Director / Grok

- Q-DD44.1: scoped certification of the repair as bounded.
- Q-DD44.2: does the ask law extend to Loop 13's bare=1
  grammar, or is its receipted "requested 1" explicit
  enough to stand as its own domain contract?
- Q-DD44.3: Compose's _compose_bound — should a stated
  Limit bind Compose depth at all, or is that read an
  accident to remove in its own circuit?

## Addendum (2026-11-10, second commit): migration completed

The first head's exact-head CI Form smoke was TERMINAL RED
261/265 — four suites still pinned the superseded default
contract (the same class DD-18 met in the leaf3 suite; my
pre-PR neighbor set was too narrow, corrected here):
d1_proof_cards, d1_registry_coreii_a (27/30),
d1_registry_coreii_b (42/43), step7_control_verdicts
(25/28). The main-session local chain reproduced the same
four reds; dd44 suite stayed 16/16. NOT the DD-31 flicker.

Repairs, all preserving each suite's behavioral subject:
- coreii_a: bare-While expectation -> bound_unspecified,
  frame fail/0; B8 message pin bound=unspecified; the
  Until symbiosis chain now states Limit 8 first (the
  suite's own pattern, used by its While symbiosis check).
  30/30.
- coreii_b: bare-Limit pin -> limit_unspecified refusal,
  nothing stored. 43/43.
- step7 B8: three bound display pins -> "unspecified";
  the stated-bound B8 case (Limit 3) untouched. 28/28.
- proof_cards: EXPECTED_BARE_FAILURES 65 ->
  bound_unspecified, + 72 limit_unspecified; census
  78/22 -> 77/23; DELL_PROOF_CARDS.md regenerated from
  the repaired render (diff: cards 65 and 72 only). 6/6.

## Anticipated probes

- "Did any lawful loop break?" Every loop chain in the
  regression that iterates now states its bound or never
  needed one (zero-iteration). The two suites that relied
  on the default were updated in the open, above.
- "Is 'ask' a question to the user?" In this slice the ask
  is the structured refusal receipt (error + the full why
  in the message), per the SS14 card's definition of ask
  as a structured missing-input result. Interactive
  prompting belongs to the human surfaces (H track).
