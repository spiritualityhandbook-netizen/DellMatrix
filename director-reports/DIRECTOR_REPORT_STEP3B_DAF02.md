# DIRECTOR REPORT — Step 3b: DAF-02 chain follow-up (Sanitize)
Evidence submitted for re-ruling. This report is NOT a certificate.
Register: maximally practical, evidence-first.

## Finding re-presented
DAF-02 (P1) — REOPENED by Director Mode D (2026-10-31): step 3's
standalone repair certified for DAF-03/DAF-10, but DAF-02 was
DECLINED as complete. Director's independently executed
counterexample at a60bb22:
  41[Sanitize] > 54[Query](predicate="password=<canary>")
returned ok=True with the marker in the TOAM typed args, the
Query scope line, the returned result, and the saved program
JSON history[1]; the initial chain echo was redacted, later atom
messages and history were not (source: chain_exec.py).
Requested ruling: DAF-02 complete in the bounded scope below,
on the frozen candidate identified in the closure addendum.

## Fix (bounded)
Carry the chain's redaction requirement through atom traces,
returned evidence, and history BEFORE persistence, using the
existing shared redactor (form/mandell/redaction.py) — no second
redaction semantics, no operand changes:
- chain messages list sanitizes every appended trace string
  (TOAM lines, Query scope line, leaf sub-messages, controls);
- a transient program flag (_chain_sanitize_redact, set only
  for the Sanitize chain's execution window, cleared in finally)
  makes CoreII mark() write sanitized traces/history labels and
  Program.note_seed sanitize every history writer's label;
- returned evidence (atom_results, core_ii snap) and the
  completed chain's last_result/last_frame/last_control/frames
  are sanitized; per-atom, only last_result descriptor fields
  (predicate/error) are sanitized mid-chain.
Execution semantics preserved: operands execute unchanged —
Query count/value/matched equal a non-Sanitize control chain's;
non-Sanitize chains and ordinary text are byte-unchanged; the
flag does not stick to later executions (all suite-witnessed).

## Evidence
- Failing-first probe on base 4405479 (step3b_probe.py):
  marker present in result/messages/TOAM/Query line/traces/
  last_result/history[1]/saved JSON; post-fix: all absent.
- Suite form/step3b_sanitize_chain_test.py: 23/23 (counterexample
  surfaces incl. saved JSON, redacted-form survival, semantics
  equality, controls, sibling Match 58, leaf note_seed sibling
  Logic 03, legacy-label form, reversed chain, flag clearing,
  cleanup residue). Registered in form/regress.py.
- Mutants (defect-restoring): M1 plain messages list -> FAIL
  (killed); M2 note_seed guard off -> FAIL on leaf check
  (killed; check added after M2 first survived — recorded);
  M3 mark() sanitization off -> FAIL (killed).
- Neighborhoods: step3 23/23, step4 27/27, step5 20/20,
  af1 13/13, af2 23/23, daf09 7/7.
- Regress x3, exact-head CI, merge tree equality, fresh-clone:
  CLOSURE ADDENDUM (packet STEP3B_SANITIZE_CHAIN_PACKET.md).

## Limitations
Redaction semantics are the canonical step-3 patterns
(secret-key values, 12+ digit runs) — unchanged. Live execution
state (store/selected) keeps real operands by design; it is not
persisted into the saved program JSON (key-walk verified: the
only pre-fix marker key was /history[1]). Third-party scanning
remains EVALUATION_UNAVAILABLE, never PASS.

## Closure addendum (2026-10-31) — frozen candidate + results
- Frozen candidate: dbbdd06139fb98e446fa76cb044f7b9419e16cb8,
  tree 6e666ecf49063bea7d5890af4b22a876515be3d0. Lineage:
  fix commits 366ecaf + 6a8bab1 on base 4405479; main
  a010508 (PR #167, director-reports docs only) merged into
  the branch to form the frozen candidate — the runtime
  delta is exactly the 6a8bab1 content.
- Before/after counterexample: on 4405479 the Director's
  chain (41[Sanitize] > 54[Query], predicate carrying the
  canary) leaked the marker into result, messages, TOAM
  line, Query scope line, traces, last_result, history[1]
  and the saved program JSON. On the candidate every one of
  those surfaces is marker-free; the redacted TOAM and Query
  lines survive in redacted form; Query count/value/matched
  equal the non-Sanitize control chain's; a non-Sanitize
  chain with the same predicate is byte-unchanged.
- Suite: STEP3B_SANITIZE_CHAIN 23/23. Mutants M1/M2/M3
  killed (M2 after the leaf note_seed check was added).
  Neighborhoods: step3 23/23, step4 27/27, step5 20/20,
  af1 13/13, af2 23/23, daf09 7/7.
- Regress x3 on the frozen candidate: 209/209 GREEN in each
  leg (fwd / --twice / --order rev).
- Exact-head CI verified COMPLETE in a separate step
  before merge: Python package run 41220210332 SUCCESS
  (completed 2026-10-31T16:33:32Z); Form smoke run
  41220210456 SUCCESS (completed 2026-10-31T16:46:57Z).
- Merge: PR #168, merge commit
  1ab1afeacbcef7f519c7138c6c617c1e0365e732 (parents
  a010508 + dbbdd06); merge tree 6e666ec == candidate tree.
- Fresh-clone regress at the merge: 209/209 GREEN.
- Limitations: as stated above the addendum (canonical
  step-3 redaction patterns only; live execution state
  keeps real operands by design and is not persisted;
  third-party scanning EVALUATION_UNAVAILABLE, never PASS).
- Ruling requested: DAF-02 CERTIFIED as complete in this
  bounded scope (chain redaction carry-through: atom
  traces, returned evidence, and history before
  persistence; execution operands unchanged). This report
  is evidence submitted, not a certificate.
