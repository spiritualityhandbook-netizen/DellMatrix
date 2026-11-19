# R25 / GP-E04 — Dell 57/73 overlong shorthand false-verdict

**Circuit:** R25 (Grand Plan GP-E04).
**Authorization:** Director §42 GP-E04 / R25 source-bound execution
directive 7005888828 (2026-11-19, PR #486) — CONTRACT CONFIRMED /
BOUNDED FIX-FIRST EXECUTION CLEARED for Uni alone, at main
b3b46b94. Build base for this PR: main
9f8642abfe36a36552ca6b2064505ed601bbab43 (Keeper watermark
advance on top of b3b46b94; no code change between the two).

## Defect (failing-first, public entry path)

Verified live pre-fix at `execute_seed` (PUBLIC_ENTRY_PATH) on
9f8642ab — probe log `hidden_files/r25_logs/probe_prefix_red.log`:

- `57[Compare] :: N 5 dropped` -> ok=True, matched=True
- `57[Compare] :: N 5 extra` -> ok=True, matched=True
- `73[Threshold] :: N 5 extra` -> ok=True, matched=True
- `73[Threshold] :: N 5 dropped` -> ok=True, matched=True

Mechanism: `form/mandell/query_ops.py` Dell 57 rewrote any
non-explicit lab to `"eq:" + first-two-tokens`; Dell 73 mapped
`len(parts)>=2` to `gte:` of the first two. Surplus tokens were
silently dropped and a verdict was reported on the prefix. The
legacy pin `rewrite_drops_tokens_beyond_two`
(`d1_dell57_compare_test.py`) and the DD-42 pin
`compare.truncation_contract_preserved` enshrined the loss.

## Repair (this PR)

`query_ops.py` only (plus pin/doc sync and the new suite):

- Dell 57 shorthand: exactly-two operands keep the eq rewrite;
  more than two refuse `ok=False`,
  `error="condition_extra_operand"` (cell predicate
  `extra_operand`, matched=False). Unbalanced quoting in
  shorthand refuses `condition_unparseable`. The DD-42 infix
  refusal (operator in second place) is checked first and is
  unchanged. Explicit predicate labs (`eq:` etc.) pass to the
  governed parser untouched.
- Dell 73 shorthand: same rule for the gte rewrite, including
  the `threshold:` alias form this Dell itself rewrites.
  One-operand (`gte:count N`) and bare (`gte:count 0`)
  documented forms preserved.
- A refusal writes only the typed refusal cell — store,
  selection and weights are snapshot-proven unchanged.
- Defective pins replaced in the same circuit (not deleted):
  `rewrite_drops_tokens_beyond_two` ->
  `rewrite_refuses_tokens_beyond_two`; DD-42
  `compare.truncation_contract_preserved` ->
  `compare.extra_operand_refused_r25`. Dell 57 deep-note /
  proof-card / signature failure text synced.

## Shared consumers (Assert 91 / Guard 92 / Branch 60)

They judge through `eval_condition_detail` -> `eval_predicate`,
not the 57/73 rewrite. A shorthand surplus (`N 5 extra`,
multi-token, no predicate prefix) already refuses there under
the DD-42 engine rule (`condition_unparseable`, no verdict
stamp, no taken arm, chain body skipped) — proven pre-fix by
the probe and pinned post-fix by the R25 suite. No consumer
change was needed and none was made.

## Proof (focused, this PR's branch)

- `form/r25_extra_operand_test.py` (new, registered in
  `regress.py`): **31/31** — surplus refusals at 57/73 (+alias),
  state-unchanged snapshots, two-operand + explicit eq/gte/
  contains controls, missing-key soft, mixed-type
  type_mismatch, malformed comma/quote, DD-42 infix,
  Assert/Guard/Branch no-verdict pins.
- `d1_dell57_compare_test`: **17/17** (incl. REPL
  REAL_USER_PATH checks).
- `dd42_predicate_infix_test`: **28/28**.
- Neighbors: query_reasoning 40/40, d1 51/54/56/58/67/68/69
  all full, r73_workshop 76/76, regress_coverage 5/5.

## Limitations / not yet done

- Full isolated-state regression (forward / twice / reverse)
  is a main-session background-chain act under the standing
  law; it is still owed before merge, together with terminal
  CI at the exact head, Keeper CODE review, and Director
  final exact-head assessment. No merge is requested by this
  report.
- Scoped observation for a Director ruling, NOT repaired
  here (the directive bounds this circuit to the 57/73
  shorthand rewrite and forbids broadening the governed
  parser by naive token count): `eval_predicate` itself
  reads only the first two operand tokens of an explicit
  binary expression, so an explicit surplus (e.g.
  `eq: N 5 extra` reaching the engine directly, or via
  Assert/Guard/Branch) is still silently truncated at the
  engine layer. The 57/73 explicit path inherits this.
  Whether GP-E04 extends to the engine is the Director's
  call; Uni recommends a separate bounded ruling rather
  than silent expansion of this PR.
- No MWL row closes and no CODE credit is claimed until
  merged-main verification. Board unchanged 39/182.
