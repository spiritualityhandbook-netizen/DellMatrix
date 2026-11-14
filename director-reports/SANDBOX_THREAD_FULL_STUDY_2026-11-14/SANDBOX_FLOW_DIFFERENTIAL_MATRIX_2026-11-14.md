# FLOW — TWO-EXECUTOR DIFFERENTIAL TEST MATRIX (SANDBOX, READ-ONLY)

The Director's first evidence gate under the FLOW ARCHITECTURE
REVIEW (CONDITIONAL ACCEPT, 2026-11-14): a read-only
differential matrix for all nine flow operators — state
deltas, receipts, failures, rollback behavior — before any
implementation. No product code changed; no merge authorized.

Method: disposable clone at main
8dd4c5295023573b61e0ae89017cf9944c52cfb7. Three surfaces
exist, and the matrix tests all three:
  S1 chain_exec.execute_chain (direct path),
  S2 operator_bridge.compose_execute (the converged public
     composition path; delegates to S1),
  S3 flow_executor.execute_program (the standalone DCC-IV
     module).
Chains: the p10 suite's canonical per-operator seeds
(success) and a uniform failure chain per operator
(91[Assert] <op> 70[Count] :: false). Rollback probe:
28[Rollback] on the same owner after each success chain.
Raw output: hidden_files/flow_matrix/flow_matrix_output.json
+ probe_flow_matrix.py (preserved with this record).
Probe honesty: the first pass contained two INSTRUMENT
artifacts (a wrong StepResult field name; a receipts count
read from a nonexistent key). Both were identified as probe
defects, repaired, and re-run; no finding below rests on
either artifact.

## THE MATRIX (condensed from raw output; messages verbatim)

">" FlowTo — S1: runs both atoms; failure chain: Assert FAIL
recorded, successor STILL RUNS (Count 0), chain ok=False.
S2: identical in every field. S3: executes; receipt
completed=2, per-step ok receipts. ROLLBACK after: denied
(see M-6).
">>" FlowThru — S1: success runs both; failure chain:
"FlowThru blocked after fail" — successor NEVER RUNS;
atom_results carry the block. S2 identical. S3: executes
(completed=2 on the success shape, step receipts ok).
">>>" FlowOver — S1: "FlowOver boundary — skip until Join";
the skipped atom's receipt is ok=False, skipped=True,
reason "skipped by FlowOver (>>> — skip forward to Join)".
Failure chain: skip occurs regardless of the predecessor's
failure. S2 identical. S3: REFUSED AT PARSE — ValueError:
flow '>>>' is REQUIRES_RUNTIME_SUPPORT, not executable.
":" FlowBy — S1: writes the binding ("FlowBy bind
context=Count"), successor runs; failure chain: the binding
is written and the successor runs even after Assert FAIL
(chain ok=False preserved). S2 identical. S3: parse refusal
(DESCRIPTIVE_ONLY).
"::" DeepFlowBy — S1: "DeepFlowBy Count" (deep ref written),
successor runs; failure chain likewise. S2 identical. S3:
parse refusal (DESCRIPTIVE_ONLY).
":>" FlowTowards — S1: "FlowTowards Count" (route written),
successor runs; failure chain likewise. S2 identical. S3:
parse refusal (DESCRIPTIVE_ONLY).
"<:" FlowFrom — S1: "FlowFrom Count" (from-ref written from
the PREVIOUS atom), successor runs; failure chain likewise.
S2 identical. S3: parse refusal (DESCRIPTIVE_ONLY).
"<:>" DynamicFlow — S1: "DynamicFlow Count->Query" (BOTH
writes: from-ref + route), successor runs; failure chain
likewise. S2 identical. S3: parse refusal (UNSAFE/AMBIGUOUS).
"<<[Delta]" DeltaFlow — S1: "DeltaFlow checkpoint
snapshots=1" appended, successor runs; failure chain: the
snapshot is STILL appended (snapshots=1) after Assert FAIL,
with chain ok=False marking the state as failed. S2
identical. S3: parse refusal (REQUIRES_RUNTIME_SUPPORT).
ROLLBACK after every operator (S1): DENIED in all nine
rows — "Rollback denied (rollback_target_invalid): no
committed generation for owner ...". See M-6.

## FINDINGS

M-1 ZERO DIFFERENTIAL between S1 and S2. Across all 18
success/failure runs the messages, verdicts, and atom
receipts are identical — compose delegates, and the public
composition path already speaks the full nine-operator
semantics (consistent with the p10 REAL_USER_PATH suite).
M-2 THE SURVIVING SPLIT IS MODULE-LEVEL, NOT PUBLIC-PATH.
S3 refuses the seven at PARSE time, fail-closed, with the
classification named in the error. No partial execution, no
silent divergence. (This refines the flow study's section 1:
its "composed path" label for S3 was imprecise — the REPL's
composed programs route through S2. The split is real; its
location is the preserved standalone module.)
M-3 ONLY ">>" GATES. Every other operator lets the
successor run after a failed predecessor, and the binding
operators (":", "::", ":>", "<:", "<:>") WRITE their
bindings after failure. Chain-level ok=False is always
preserved, so failure is never hidden — but any composed-
path admission under Q-FL1 must SPECIFY this behavior
(bind-after-failure; run-after-failure) as contract, since
today it is observable behavior in search of a sentence.
M-4 ">>>" SKIPS STRUCTURALLY. Success or failure before it
does not matter; the skipped atom is receipted honestly
(ok=False, skipped=True, reason named) — the DAF-08 rule
observed live.
M-5 DELTAFLOW SNAPSHOTS THE FAILED STATE TOO. A snapshot
taken after failure is a snapshot OF a failed chain state;
the chain's ok=False is its label. Consumers of snapshots
must read the label, not just the count.
M-6 TWO SNAPSHOT KINDS — DO NOT CONFLATE. DeltaFlow's chain
snapshots are NOT committed generations: bare 28[Rollback]
is denied after every operator including <<[Delta],
because Rollback is authority-mediated (its contract:
freeze + grant + confirm_rollback required) and targets
committed checkpoint generations. The study's wording
correction (DeltaFlow = mark; Rollback = travel) is
confirmed by behavior, with the addition that the travel
itself is gated by the rollback authority.
M-7 RECEIPTS. S1/S2 produce per-atom receipts
(atom_results: dell, ok, skipped, reason) plus bilingual
messages; S3 produces per-step receipts (completed/failed/
skipped counts + step ok/skipped/error). Both shapes are
complete for their surface; no row executed without a
receipt trail.

## DIRECTOR CORRECTIONS CARRIED INTO THIS RECORD

(1) Bounded FIFO channels do NOT automatically guarantee
deadlock freedom: the Parallel/Join design (F-N2/F-N3) must
test blocked reads, full buffers, cancellation, and
resource exhaustion before any determinism claim is made.
Determinism of results and freedom from deadlock are
separate properties; the study's F-N3 wording is corrected
accordingly. (2) A projection label is NOT a security-grade
taint system: the hidden-flow audit (F-N4) must trace ACTUAL
dependencies — including branch decisions and observable
timing or termination effects — not read labels.

Status: evidence gate DELIVERED. Q-FL1's conditional
admission now has its differential evidence; equivalence
and safety proofs remain the next gate, per the Director.
No implementation authorized by this matrix.
