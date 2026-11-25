# DAF-09 pidfd-hardening follow-up — ground (prepared 2026-10-31, main session)

Queue: after step 5b closes, before step 6. Source: Director Mode D
ruling on the identity follow-up at 3234966 (session-escape withheld;
his suite 18/20; register entry + INDEX PR #179).

## The gap, in code (form/regress.py at 3234966, lines ~411-446)

_signal_identity(pid, starttime, sig):
- refuses when starttime is None or current starttime differs. Good.
- pidfd path: os.pidfd_open(pid); on OSError fd stays None -> falls
  through to the kill(2) fallback at the bottom, guarded only by the
  starttime check done BEFORE the open attempt. PID reuse between
  that check and os.kill is the window the Director mock-confirmed.
- Same fallback when os.pidfd_open does not exist at all.

## Director's directives (verbatim substance)

1. Record 18/20 (done: register + INDEX).
2. Capture witness identity, reparenting, signal result, marker
   timing; positive control waits boundedly for termination instead
   of relying solely on immediate poll().
3. Remove the unsafe numeric-PID fallback for historical witnesses,
   or an equally strong guarantee; report unavailable cleanup
   explicitly.
4. pidfd-open failure controls; re-present bounded follow-up.
   Cancellation certification stands (do not re-open).

## Design sketch (for the circuit's SWAT record; not yet ratified)

- _signal_identity returns a tri-state outcome: "signalled" /
  "refused" (identity missing/mismatched) / "unavailable" (pidfd
  could not be opened or is unsupported). The kill(2) fallback for
  witnessed identities is DELETED. Root proc.kill() and the
  session-scoped killpg are NOT historical-witness signalling and
  stay unchanged.
- _kill_process_tree builds a report {signalled, refused,
  unavailable} and stashes it as proc._kill_report (diagnostics for
  the suite + any caller). run_entry's timeout path appends
  "cleanup_unavailable=<n>" (+ identities) to its why string when
  the unavailable set is non-empty — explicit in regress output
  without changing the (bool, str) contract. KeyboardInterrupt path
  prints one equivalent line (no return channel).
- Suite (form/daf09_timeout_tree_test.py) changes:
  * Positive control: after _kill_process_tree, wait boundedly
    (poll loop, ~5s deadline) for the witnessed process to die
    (AGENTS.md §31.1) instead of a single immediate poll().
  * New pidfd-open failure controls (§31.2): monkeypatch
    os.pidfd_open to raise OSError -> (a) a live witnessed process
    with MATCHING identity is NOT signalled (survives) and appears
    in the kill report's unavailable set; (b) unavailable cleanup
    is visible in run_entry's timeout verdict for a synthetic
    timed-out entry whose descendant was witnessed (or at minimum
    via the stashed report on a real root Popen through
    _kill_process_tree).
  * Escape check diagnostics: the fixture already writes the
    grandchild's pid+starttime to a pidfile; on the marker check,
    capture and print: whether (gpid, gstart) is in
    proc._witnessed_identities, its _kill_report outcome, marker
    file mtime vs kill time. Failure output must say WHICH link
    broke (never witnessed / witnessed-not-signalled /
    signalled-but-wrote-anyway / timing).
  * All 20 existing checks preserved in substance; count grows by
    the new controls. Cancellation checks untouched.
- Mutants: M1 restore the kill() fallback -> pidfd-failure control
  (a) fails (bystander signalled). M2 restore immediate-poll
  positive control is a test-side mutant; instead M2: make
  _signal_identity report "signalled" without sending -> positive
  control's bounded wait expires -> fails.
- AGENTS.md laws engaged: §31.1 (bounded waits), §31.2 (no silent
  downgrade), §31.3 (his 18/20 is the standing fact; the report
  presents mechanisms + diagnostics, never "resolved" by local
  greens alone).
