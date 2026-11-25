# DIR-F14 — REPEATED CATCH RE-REPORTS A CONSUMED ERROR — packet

Circuit: Director repair wave (Ruling #7), DIR-F14 (P2, OPEN).
Finding: Try; Delete absent; Catch; Catch reports
"Catch delete_missing:absent" TWICE — caught_error is archival
evidence, but frame.error retains the consumed error and the
next Catch treats it as pending.
Base: main c00c325 (PR #197 merge; DIR-F13 publication closed).
Branch: uni/dirf14-catch-consumed.
Worktree: ~/workspace/nbd-omega-dirf14.
Ground: hidden_files/dirf14_ground.md.

## Contract (DIRECTOR_FINDINGS_REGISTER.md, DIR-F14)
- Explicitly distinguish pending from consumed error.
- A second Catch with no new failure reports no error and
  preserves caught history.
- A new post-Catch failure becomes a new pending root cause
  (Director Q1: ACCEPT) and must not erase prior caught
  evidence.
- Nested isolation, failed-Commit evidence and commit
  eligibility must remain correct.
- Test repeated Catch, new failure after Catch, and nested
  frames through direct and chain paths. (Q2: bounded wording
  scope accepted; cross-surface wording is step 11.)

## Defect site (verified by code read this run, c00c325)
form/mandell/spectrum_ops.py, apply_spectrum n == 94 (Catch):
Catch archives the error into caught_error but copies it back
into frame["error"], so the pending slot is never emptied.
A second Catch satisfies the same predicate and re-reports
the consumed error as if newly caught. No other consumer
reads frame["error"] (grep this run: only spectrum_ops —
the note hook, Catch, and status-based Commit eligibility).
note_atom_failure (the ONE canonical hook, B15) already
implements the post-Catch branch correctly: a failure noted
while status == "caught" becomes a new root cause and never
touches caught_error.

## SWAT Director's-eye pre-mortem (BEFORE implementation)
Attacks the Director is expected to try, and the evidence
this circuit must carry for each:
- P1 Repeated Catch x3, not just x2: every later Catch must
  report no error; history must not grow on empty Catches.
- P2 Catch a failure, fail the SAME key again, Catch: this
  is a NEW failure with an identical error string. It must
  be reported — any repair that suppresses notes identical
  to caught_error would swallow a genuine new root cause
  (register W2 uses a different key; the same-key case is
  the sharper probe and is asserted explicitly, W2b).
- P3 Two DIFFERENT failures caught in sequence: the second
  Catch must not erase the first caught evidence. The
  single caught_error slot alone cannot prove this; the
  repair adds an append-only caught_history list on the
  frame (caught_error remains the latest, preserving the
  step-8 contract exactly).
- P4 Failed-Commit evidence: Commit on a failed frame adds
  commit_illegal to extra_errors; Catch afterwards consumes
  ONLY the root cause — extra_errors stays as evidence and
  never becomes pending or caught.
- P5 Nested frames: inner Catch x2 never touches the outer
  frame's pending slot; outer Catch with no outer failure
  reports no error.
- P6 Late duplicate note (ground interplay 2): the same
  atom outcome reaches the hook from Core II tail and chain
  layer synchronously, while status == "failed", where the
  existing dedupe applies. A note arriving AFTER a Catch is,
  by execution order, a new failure signal — DECISION: no
  identity suppression in the hook (see P2); the behavior
  is asserted at hook level (W3) so it is never accidental.
- P7 Catch with no frame still refuses catch_illegal;
  no-error Catch consumes nothing and creates no
  caught_error/caught_history fields (step-8 regression).
- P8 Revert after Catch and Commit eligibility from
  "caught" remain exactly as step 8 certified (statuses
  unchanged by this repair; only the pending slot clears).

## Design (SWAT unanimity 4/4 recorded BEFORE implementation)
Custodian: pending slot clears on consumption; caught
evidence is append-only history, never erased — agree.
Interpreter: frame["error"] IS the pending slot and
caught_error/caught_history ARE the consumed archive;
the split is explicit in state, not inferred — agree.
Sentinel: no suppression of identical post-Catch failures
(a swallowed real failure is worse than a re-report) —
agree. Mechanic: minimal change inside the one Catch
authority + one additive frame field; no second authority,
no hook change — agree. UNANIMITY 4/4.

Repair (n == 94 only): on consumption,
frame["caught_error"] = captured (latest, as before);
frame.setdefault("caught_history", []).append(captured);
frame["error"] = "" (pending emptied); status = "caught"
(unchanged). Second Catch then takes the existing
"Catch (no error)" branch and consumes nothing.

## Failing-first
Suite form/dirf14_catch_consumed_test.py written BEFORE the
fix; run on unfixed c00c325 code — results recorded in the
closure addendum below.

## Closure addendum
CLOSED 2026-11-01 IMPLEMENTED-VERIFIED (claims
reconciled to executed assertions only).
Candidate acddd37 (fix 0474322 + one pre-existing
witness amendment acddd37: d1_registry_spectrum's
Catch witnesses updated to the repaired contract —
round 1 leg1 RED on exactly that witness, amended,
round 2 all green), tree 463de56, base c00c325.
Failing-first on unfixed code: 14/25 (the Director's
double-report reproduced). Suite DIRF14_CATCH_CONSUMED
25/25 on the candidate. Mutants killed: M1 (pending
slot not cleared) 18/25, M2 (no caught_history)
17/25; both reverted and suite re-verified 25/25.
Regress 218/218 x3 on acddd37 (fwd / --twice both
passes / --order rev; leg3 re-run foreground after
two earlier attempts died with NO RESULT, logs in
hidden_files/dirf14_logs/). Exact-head CI verified
COMPLETE SUCCESS in a SEPARATE step before merge
(package 41336014718 SUCCESS 2026-11-01T18:20:00Z;
smoke 41336014751 SUCCESS completed 18:36:13Z; head
acddd37). PR #198 MERGED as 19388d2 (merge tree
463de56 == candidate tree; parents c00c325 +
acddd37). Fresh-clone regress at merge 19388d2:
218/218 GREEN (dirf14_logs/freshclone_regress.log).
NOT certified; Director report
DIRECTOR_REPORT_DIRF14.md re-presents DIR-F14 for
re-ruling.
