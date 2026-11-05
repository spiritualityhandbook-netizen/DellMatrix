# 72-49 (= SM-32) GROUNDING — Cycle 15 (2026-11-05, cron)

Register gap (NBD_MASTER_OBJECTIVE_REGISTER.md:90): "Challenge
AcceptancePolicy delegation, expiry, revocation chains (P0/E)".
P0 gap: "revocation-chain invalidation across restart + retry
as one contract". Status PARTIAL.

## Mechanism (form/dell_matrix/acceptance_policy.py, 864 lines, at main 0c062a1)

AcceptancePolicy is the SINGLE owner of acceptance authorization.
ALL state is in-memory per instance: _opt_ins, _issued_approvals,
_revoked_approvals, _issued_grants, _revoked_grants, _grant_seq,
_session_id = uuid4 per instance. Docstring contract: "Opt-ins and
issued approvals expire at session end. Restart clears both."
Program.__init__ (form/open.py:212) constructs a fresh
AcceptancePolicy per Program instance -> a Program restart IS a
policy restart. Nothing is persisted; there is no load path.

Three chain types:
1. GRANT chain: issue_grant (root, trusted path) -> attenuate_grant
   (narrowed child, parent_id). Execution: _check_grant ->
   _grant_chain_valid recurses ancestors: every ancestor issued,
   unrevoked, same session, else deny (via revoked_grant_chain).
   revoke_grant(ancestor) denies unfinished descendants.
2. APPROVAL derivation chain: issue_approval -> derive_approval
   (only supersede_successor). Record carries derived_from
   (approval_id or "opt_in:<producer>"). check() ->
   _source_chain_valid: revoked parent approval or revoked source
   opt-in invalidates an unfinished child (explicit deny via
   revoked_source_chain).
3. OPT-IN: grant_opt_in / revoke_opt_in; is_opted_in binds
   session_id. Derived-from-opt-in children re-validate the
   opt-in at execution time.
Retry semantics (docstring): "a denied or stale approval is never
auto-retried. The caller re-reviews and calls issue_approval
again, producing a NEW approval_id."

## Existing coverage (verified by reading the suites at 0c062a1)

- r61_authority_test: in-session ancestor revocation denies
  descendants; reset_session invalidates (F1); CROSS_PROCESS
  restart: ONE grant handle issued in child A denied in child B
  (F2); committed idea survives restart on reload (F3).
- r63_rollback_test: revoked grant / revoked ancestor deny at the
  rollback boundary; fresh policy session does not know the grant.
- r64_multi_intelligence_test 6.4.x: cross-process restart +
  rollback invalidation via dispatch.
- r65_separation_test: authoritative restart via child scripts.
- wo51_adversarial_test: revoked plain approval denies;
  reset_session() simulated restart for a plain approval;
  parent approval revoked -> NEW derivation blocked at derive
  time; source opt-in revoked -> unfinished derived child denied
  at execution; valid derivation positive control.

## The UNPROVEN combination (the 72-49 gap, fixed as a matrix)

No suite binds AS ONE CONTRACT, in one sequence:
(a) full chains of ALL THREE types built and verified ALLOW
    (positive controls) in session A;
(b) MID-CHAIN revocation in A: grant child (middle link),
    source approval, source opt-in, one plain approval;
(c) RETRY x2 in-session: every descendant / unfinished child /
    revoked link denies on BOTH retries; the unrevoked root
    grant and an unrevoked unrelated approval still ALLOW
    (revocation is surgical, not session-wide);
(d) RESTART: a genuine new OS process with a fresh policy
    (and a fresh in-process policy) presented with ALL session-A
    artifacts — revoked AND unrevoked — denies EVERYTHING,
    on retry x2 (nothing from the prior session is honored);
(e) RE-ISSUANCE in the new session: new grant + new approval
    ALLOW, while session-A artifacts STILL deny in the new
    session (no cross-session contamination either way);
(f) an unfinished approval-sourced derived child whose parent
    is revoked BEFORE the child's first execution denies at
    execution (wo51 covers derive-time blocking + the opt-in
    variant of this; the approval-source execution-time case
    in a revoke->restart->retry sequence is unproven).

Committed-history-survives is NOT re-proven here: r61 F3
(cross-process reload) already proves it; cited, not duplicated.

## SWAT choice

Proportionate falsification IF the probe passes on pristine
code (proof-only suite over an existing mechanism, per Cycle 14
selection). Full SWAT + repair circuit if the probe finds an
ALLOW where the contract requires DENY (stateful authority
surface). Choice recorded here per Ace's calibration.

## Plan

1. Failing-first probe (hidden_files/mr49_probe.py): genuine
   child OS processes for the restart leg; coordination-free
   (sequential processes, artifacts via JSON file). Run against
   pristine clone at 0c062a1.
2. If probe green: build form/sm32_revocation_chain_test.py in
   the TD-2 suite style (check() raises, smoke() entry),
   register in form/regress.py LIST (236 -> 237), README count
   bump in the same PR (236 -> 237, both lines; the Director's
   remove-the-number follow-up stays a separate queued patch).
3. Mutants (commit real work first, inverse-edit revert):
   M1 _grant_chain_valid -> True kills (c)-grandchild;
   M2 _source_chain_valid -> True kills (f);
   M3 check() drops revoked-approval test kills (c)-plain.
4. Regress x3 sequential + fresh-clone targeted run, Director
   report + INDEX row, PR, hard merge gate. Q1 (#294) hold and
   the <=2 unreviewed PR limit respected (#294 + this = 2).
