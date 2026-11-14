# FL-G31-02 — STANDALONE FLOW AUTHORITY TRACE (SANDBOX, READ-ONLY)

Directive: Director FLOW DIFFERENTIAL REVIEW (MODE B),
FL-G31-02. NO REPAIRS. No implementation, PR, or merge.
Pinned baseline: main 1c5129e397d797e83e664b1cbd9e0c97e451f049
(main advanced past the matrix's 8dd4c529 pin; all evidence
below was gathered at 1c5129e). Method: full-repo caller
grep (form/, src/, gui/, ops/), dispatch-path reading, and
behavioral invariant probes in a disposable clone. The
Director's SCOPED PASS on the differential matrix and his
reframing are accepted into this record: G-31 is NOT a
public-path flow failure; it is a standalone-module
consistency and contract-clarity issue.

## 1. WHAT S3 IS — REACHABILITY TRACE

S3 = form/mandell/flow_executor.py (parse_program :187,
execute_program :220, FLOW_CLASSIFICATION :32, parse-time
refusal raise :174).

PRODUCTION CALLERS (non-test):
- form/repl.py:3441-3483 — the REPL dispatch. Since P10, a
  line that parse_seed accepts as a multi-atom seed goes
  FIRST to the canonical chain path (observe_seed_execution
  -> chain_exec semantics). The comment at :3441 records why:
  before P10 the DCC-IV branch claimed every line containing
  ">" or ":" first, so ">" and ">>" chains ran with
  flow_executor semantics (whose Assert ignores the seed
  label payload) while the other seven fell through to
  chain_exec — "the same seed text meant different things by
  dispatcher." After the seed branch, the DCC-IV branch
  (:3466) still calls parse_program/execute_program for
  lines containing ">" or ":" that are NOT valid multi-atom
  seeds but parse as flow programs with >1 node; ValueError
  falls through silently. S3 remains reachable from the
  public REPL for that residual class.
- form/mandell/english_composer.py:25 (import), :201-211
  execute_composite -> parse_program + execute_program. The
  English multi-step path (REPL "and then / after that /
  then" branch) composes English into Mandell and executes
  it through S3. The composer emits ONLY " > " joins
  (:170: " > ".join(mandell_parts)) — its generated programs
  sit entirely inside S3's executable set by construction.
- form/mandell/operator_bridge.py:287 — imports ONLY the
  helper _args_from_label from S3 (compose_execute itself
  delegates to chain_exec, :367).
- form/mandell/seed.py:172, :207 — seed.py's AF-2 segment
  rule cites flow_executor's tokenizer as an authority
  ("same authority as flow_executor"). S3's tokenizer is a
  shared parsing authority, independent of execution.

TEST SURFACE (7 files): flow_executor_test.py (DCC-IV
capability), dcc_xx_test.py:494, english_composer_test.py
:30/:139, p0r3_execution_integrity_test.py:137/:229,
ssi_i_test.py:73, af2_delimiter_addressing_test.py
(tokenizer), r2_semantic_honesty_test.py:14/:37 — the last
names S3's refusal behavior as a CONTRACT: "non-executable
operators refused (no silent downgrade)."

No callers in src/, gui/, or ops/. No other production
importer exists at this pin.

CLASSIFICATION: **ACTIVE_INTERNAL** — with a bounded
public reach (the REPL's residual DCC-IV branch) and a
load-bearing internal consumer (English composition). It is
not ACTIVE_PUBLIC for raw seeds (P10 moved those to the
canonical path), not LEGACY_COMPATIBILITY (live consumers
execute real work through it today), not TEST_ONLY, not
UNREACHABLE.

## 2. THE AUTHORITATIVE NINE-OPERATOR CONTRACT

Canonical semantics live in chain_exec (S1) and, identically,
compose_execute (S2). Stated as contract (behavior measured
in the differential matrix + this trace's probes):

- ">" FlowTo: successor runs unconditionally. A failed
  predecessor is recorded; chain ok=False. No state write.
- ">>" FlowThru: THE GATE. Successor runs only if the
  predecessor succeeded; a blocked successor is receipted
  skipped ("FlowThru blocked after fail").
- ">>>" FlowOver: skip forward to 61[Join] or chain end,
  independent of predecessor outcome. Skipped atoms are
  receipted ok=False, skipped=True, reason named (DAF-08).
- ":" FlowBy: bind chain context = next atom's term.
  "::" DeepFlowBy: bind the deep/program-level ref.
  ":>" FlowTowards: set route. "<:" FlowFrom: bind from-ref
  = previous atom's term. "<:>" DynamicFlow: both writes
  (from-ref + route) in one operator. ALL FIVE binding
  operators: the successor RUNS and the binding WRITES even
  when the predecessor failed (chain ok=False preserved).
  This is the contract gap the Director named: behavior
  first documented HERE, by this trace.
- "<<[Delta]" DeltaFlow: append a chain-state snapshot —
  including after failure (the chain's ok=False is the
  snapshot's label). A DeltaFlow snapshot is NOT a committed
  generation and confers no rollback right.
- ROLLBACK SEPARATION: 28[Rollback] targets committed
  checkpoint generations through the rollback authority
  (freeze + grant + confirm_rollback); bare use is denied
  (verified at this pin after a DeltaFlow chain: ok=False,
  denial). DeltaFlow marks; the authority travels.

## 3. MUTATION-DOOR / CHECKPOINT INVARIANTS UNDER FAILURE

Code: chain_exec.py:245-254 — the flow operators' writes
"context/refs/route/DeltaFlow snapshot list likewise pass
through the ONE _note_mutation door with a _ckpt captured
immediately before the write" (DD-51 Ring 1), importing
spectrum_ops._ckpt/_note_mutation at :250-251.
Behavioral probes at pin 1c5129e (disposable clone):
- Bind-after-fail: chain "91[Assert] : 70[Count] :: false"
  -> ok=False, messages carry "FlowBy bind context=Count",
  and the returned Core II state shows context="Count":
  the binding landed, receipted by message, through the
  door. No hidden write: the write IS the operator's
  documented act.
- Pure failure: "91[Assert] :: false" alone -> ok=False,
  Core II context="" — a FAILED ATOM WRITES NOTHING. The
  only post-failure mutations in any row are the flow
  operators' own receipted writes.
- DeltaFlow + rollback at this pin: "DeltaFlow checkpoint
  snapshots=1"; subsequent bare 28[Rollback] ok=False
  (denied; no committed generation). Separation holds.
Verdict: the mutation-door and checkpoint invariants HOLD
under predecessor failure. The risk the Director flagged
(unreceipted or uncheckpointed writes after failure) does
not occur: writes after failure are exactly the binding
operators' writes, each messaged and door-checked.

## 4. RECOMMENDED DISPOSITION: KEEP_ISOLATED

- DELEGATE_TO_CANONICAL rejected: S3 has live consumers
  (english_composer.execute_composite; the REPL residual
  branch) whose programs are inside its executable set, and
  delegation is NOT behavior-neutral even for ">" and ">>":
  S3 routes nodes through CORRESPONDENCE actions via the
  semantic router and its Assert ignores the seed label
  payload (the P10 comment's own words) — swapping engines
  would silently change composed-program semantics for the
  two operators both paths share.
- RETIRE_WITH_COMPATIBILITY rejected: retirement breaks a
  production consumer, a public REPL branch, a tokenizer
  authority cited by seed.py, and a tested honesty contract
  (r2: refusals as a no-silent-downgrade guarantee).
- KEEP_ISOLATED: S3 stays the CORRESPONDENCE-routed
  composition surface for ">" / ">>" programs, refusing the
  other seven explicitly at parse (:174) — refusals that are
  a feature under the honesty contract. The canonical
  nine-operator semantics (section 2) are documented once,
  here; any future admission of further operators into S3
  proceeds only through Q-FL1's equivalence + safety proof
  gate, with section 2 as the contract to prove against.

Evidence limit (stated, per MODE B): caller classification
rests on static trace + the dispatch reading at this pin;
no runtime census of REPL traffic was taken, so the residual
branch's real-world frequency is UNKNOWN — it does not
affect the classification, which needs only reachability.
