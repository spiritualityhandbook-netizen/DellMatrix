# DAF-09 PIDFD-HARDENING FOLLOW-UP — packet

Circuit: DAF-09 session-escape re-presentation, pidfd-hardening only.
Cancellation is CERTIFIED (Mode D, at f1c0205) and is NOT re-opened.
Base: main 82fe2ad (PR #180 merge). Branch: uni/daf09-pidfd-hardening.
Worktree: ~/workspace/nbd-omega-daf09pidfd.
Source: Director Mode D ruling on the identity follow-up at 3234966 —
his independent suite 18/20 (escape marker + identity positive control
fail; both refusal controls PASS); pidfd_open failure falls back to
numeric kill() after an earlier identity check (mock-confirmed PID-reuse
window); "investigation resolved" claim ruled PREMATURE (owned, §31.3).
Ground: hidden_files/daf09_pidfd_hardening_ground.md (main session).

## Defect (verified in code at 82fe2ad, form/regress.py _signal_identity)

- starttime verified BEFORE the pidfd attempt; if os.pidfd_open raises
  OSError (or does not exist), fd stays None and execution falls through
  to os.kill(pid, sig) guarded only by that earlier check. A PID reused
  between the check and the kill receives a signal meant for a dead
  witnessed process. This is AGENTS.md §31.2's banned silent downgrade
  from a verified primitive to the unverified primitive.
- The identity positive control samples victim.poll() once, immediately
  after _kill_process_tree — an asynchronous assertion without a bounded
  wait (§31.1), the exact race behind the Director's 18/20 discrepancy.
- The escape check gives no diagnostics distinguishing never-witnessed /
  witnessed-not-signalled / signalled-but-wrote / timing (§31.1 report
  requirement).

## SWAT UNANIMITY — recorded BEFORE implementation (4/4)

- Custodian: AGREE. Unavailable cleanup must be retained as evidence
  (kill report on the proc object + explicit marker in the timeout
  verdict), never silently dropped; no state outside regress.py's own
  bookkeeping is touched.
- Interpreter: AGREE. Tri-state outcome (signalled / refused /
  unavailable) preserves the (bool, str) run_entry contract; the
  "TIMEOUT" verdict string for the timeout path stays primary, with
  cleanup_unavailable appended as explicit extra information, not a
  verdict change. Cancellation semantics untouched.
- Sentinel: AGREE. Deleting the kill(2) fallback for witnessed
  identities is the security fix (§31.2); root proc.kill() and the
  session-scoped killpg are NOT historical-witness signalling and stay.
  Legacy bare entries remain never-signalled.
- Mechanic: AGREE. Changes are local to form/regress.py +
  form/daf09_timeout_tree_test.py; bounded-wait positive control (§31.1);
  pidfd-failure controls via monkeypatched os.pidfd_open; defect-
  restoring mutants defined below; no new architecture, no second
  authority.

Unanimity: 4/4. Implementation authorized under Ace's standing rule
(Uni + all four personas unanimous). Certification is NEVER
self-performed: closure = implemented+verified, re-presented to the
Director for re-ruling on session-escape coverage only.

## Plan (per ground sketch, ratified by the SWAT record above)

1. _signal_identity returns tri-state "signalled" / "refused" /
   "unavailable". kill(2) fallback for witnessed identities DELETED.
   pidfd unsupported or pidfd_open failure => "unavailable", process
   NOT signalled. Identity missing/mismatched => "refused".
   ESRCH from pidfd_send_signal (pinned instance already dead) =>
   "refused" (clean no-op, signal delivered to nobody).
2. _kill_process_tree builds proc._kill_report =
   {signalled: [...], refused: [...], unavailable: [...]} of
   (pid, starttime) identities.
3. run_entry timeout path: why = "TIMEOUT" plus
   " cleanup_unavailable=<n>:<pid,...>" when the unavailable set is
   non-empty — explicit in regress output. NOTE: suite checks that
   assert (ok, why) == (False, "TIMEOUT") must be updated to accept
   the TIMEOUT prefix + optional suffix ONLY where pidfd is genuinely
   unavailable; in the normal environment pidfd works, so why stays
   exactly "TIMEOUT" — the suffix appears only when cleanup really
   was unavailable. KeyboardInterrupt path prints one equivalent line.
4. Suite changes (form/daf09_timeout_tree_test.py):
   - Positive control: bounded wait (~5s poll loop) for the witnessed
     process to die instead of a single immediate poll() (§31.1).
   - NEW pidfd-open failure controls: monkeypatch os.pidfd_open to
     raise OSError -> (a) a live witnessed process with MATCHING
     identity is NOT signalled (survives) and appears in the kill
     report's unavailable set; (b) unavailable cleanup is visible via
     the stashed report on a real root through _kill_process_tree.
   - Escape check diagnostics: capture whether (gpid, gstart) is in
     the witnessed set / kill report outcome / marker timing; failure
     detail names which link broke.
   - All 20 existing checks preserved in substance; cancellation
     checks untouched.
5. Mutants: M1 restore the kill() fallback -> pidfd-failure control
   (a) must fail. M2 _signal_identity reports "signalled" without
   sending -> bounded-wait positive control must fail.
6. Closure discipline: suite + mutants -> neighborhoods -> regress x3
   sequential (fwd / --twice / --order rev), logs under
   hidden_files/daf09pidfd_logs/ -> PR -> exact-head CI verified
   COMPLETE in a SEPARATE step -> merge (tree equality) ->
   fresh-clone regress -> ledger + POST_PLAN + register -> Director
   report addendum re-presenting session-escape only.

## Failing-first probe
hidden_files/daf09_pidfd_probe.py — monkeypatches os.pidfd_open to
raise OSError, then calls _signal_identity on a live victim with its
CORRECT starttime. Unmodified code: falls back to os.kill, victim
dies (HAZARD DEMONSTRATED). Fixed code: victim survives, outcome
"unavailable".

## Status
IN FLIGHT.
- PR #180 (step 5b Director report) MERGED at the start of this
  cycle run as 82fe2ad (merge tree ba032ea == candidate tree
  ba032ea; parents 484453f + 5a5f8ef; exact-head CI had been
  verified COMPLETE SUCCESS in the separate 21:50 CDT step —
  package 41264872496, smoke 41264872503 — and re-verified via gh
  in this run before merging). Main = 82fe2ad. Step 5b fully closed
  including report publication.
- Failing-first probe (hidden_files/daf09_pidfd_probe.py) on
  UNMODIFIED code: outcome=True, VICTIM_KILLED_VIA_FALLBACK — the
  bare-kill fallback fires when pidfd_open fails. On fixed code:
  outcome='unavailable', VICTIM_ALIVE_UNAVAILABLE.
- BUILT + COMMITTED: candidate 86df4af on uni/daf09-pidfd-hardening
  (base 82fe2ad). form/regress.py (tri-state _signal_identity, kill
  report, cleanup_unavailable in timeout verdict / interrupt line)
  + form/daf09_timeout_tree_test.py (bounded-wait positive control,
  pidfd-failure controls, escape diagnostics, grandchild pidfile
  carries pid+starttime).
- Suite: 22/22 (20 preserved + 2 new). Probe flips as designed.
- Mutants (real work committed first; reverts via inverse edits,
  diff verified clean): M1 restore kill() fallback -> 20/22,
  failing EXACTLY the two pidfd-failure controls. M2 report
  "signalled" without sending -> 19/22 (positive control bounded
  wait expires; escape checks fail with diagnostics naming the
  broken link: kill_report=signalled identity_now=same
  marker=exists). Suite re-verified 22/22 after reverts.
- REGRESS x3 on 86df4af COMPLETE (logs hidden_files/
  daf09pidfd_logs/): reg1 fwd 211/211 GREEN, reg2 --twice 211/211
  x2 GREEN, reg3 --order rev 211/211 GREEN; daf09 suite 22/22 in
  every leg. Candidate tree bd1eeb4. Worktree clean.
- PUSHED + PR #181 OPEN (head 86df4af, base main 82fe2ad).
- REMAINING: exact-head CI on 86df4af verified COMPLETE in a
  SEPARATE step -> merge (tree equality) -> fresh-clone regress ->
  ledger / POST_PLAN / register -> Director report addendum
  (session-escape only) published to director-reports/ -> then
  step 6.

## Closure completion (2026-10-31, 23:10 CDT cycle run)

CLOSED — IMPLEMENTED-VERIFIED, session-escape re-presented.
- Exact-head CI on 86df4af verified COMPLETE SUCCESS in a
  SEPARATE step (this run, distinct from the 22:50 attempt where
  smoke was still in progress): package 41270691124 SUCCESS
  completed 03:50:09Z; smoke 41270691153 SUCCESS completed
  04:06:18Z; both on head 86df4af; PR MERGEABLE/CLEAN.
- PR #181 MERGED as 87be4de (2026-11-01T04:11:19Z); merge tree
  bd1eeb4 == candidate tree; parents 82fe2ad + 86df4af.
- Fresh-clone regress at merge 87be4de: 211/211 GREEN
  (hidden_files/daf09pidfd_logs/freshclone_regress.log; daf09
  22/22; REGRESS FINAL: GREEN; session EXIT 0). Note: two
  premature background-completion notices during the run
  referenced other sessions' logs (s5b) and were NOT counted;
  closure rests on the log file itself + the genuine session
  completion (elapsed 1036s, EXIT:0, correct tail).
- Ledger row + POST_PLAN note + register entry done
  (DAF-09 pidfd-hardening -> IMPLEMENTED-VERIFIED).
- Director report addendum DIRECTOR_REPORT_DAF09_PIDFD_
  HARDENING.md finalized; publication to director-reports/
  via docs PR follows in this run (its merge waits on its own
  exact-head CI in a separate step).
- NOT certified. Next in Director order: step 6.
