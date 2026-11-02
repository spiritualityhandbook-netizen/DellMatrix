# DAF-09 ESRCH-AT-OPEN FOLLOW-UP — GROUND + SWAT PRE-MORTEM
# (NBD candidate 1, selected sleep run 2026-11-01 ~21:0x CST;
#  execution begins after PR #209 closes)

## Ground (evidence)
- Packet: ~/workspace/DAF09_INSTRUMENTED_INVESTIGATION_PACKET.md
- run7 JSONL line 96: pidfd_open pid 35111 -> errno 3 (ESRCH),
  proc_state null, pre-read MATCH (starttime 1812456). Outcome
  bucketed "unavailable"; verdict "TIMEOUT cleanup_unavailable=
  1:35111"; suite 21/22 failing ONLY the exact-equality verdict
  check. The instance was already dead (frequently group-killed
  by killpg at the top of _kill_process_tree); cleanup in fact
  succeeded.
- run4: same outcome class (pid 34833, errno not captured by v1
  driver). run6 contrast: same race landing post-open (send /
  recheck) classes "refused", verdict stays exactly "TIMEOUT",
  22/22.
- Code (main 5f1120e, form/regress.py _signal_identity ~L450-453):
      try: fd = os.pidfd_open(pid)
      except OSError: return "unavailable"
  ANY OSError at open -> unavailable, errno ignored.
- Precedent in same function: pidfd_send_signal ESRCH is caught
  by the post-open `except OSError: return "refused"` — "pinned
  instance already dead: nobody signalled". ESRCH at open is the
  same fact one syscall earlier.

## Repair contract (bounded)
- pidfd_open raising OSError with errno == ESRCH -> "refused"
  (instance gone; nobody signalled; NOT a pidfd-availability
  failure). All other errnos (EMFILE, EINVAL, EPERM, ...) stay
  "unavailable". hasattr(os,"pidfd_open") False stays
  "unavailable".
- No other behavior change: no numeric fallback (§31.2), no
  verdict-string change, no timing/sleep changes.
- Suite: exact 22 checks preserved in substance + ONE new
  control (23 total): pidfd_open injected to raise ESRCH for a
  live witnessed identity -> identity lands in "refused", NOT
  "unavailable"; existing EMFILE control (errno 24) still lands
  "unavailable" (already check 8, retained as the contrast).
- This does NOT resolve the Director's 19/22 discrepancy (§31.3);
  it fixes a locally evidenced classification defect only.
  Session-escape stays WITHHELD.

## SWAT Director's-eye pre-mortem (before implementation)
1. "ESRCH could mean the pid was REUSED and the new instance is
   also gone-by-open?" — Either way nobody signalled and the
   witnessed instance is dead; refused is the honest bucket
   (same as send-ESRCH). The identity was verified by the
   pre-read MATCH immediately before open.
2. "Could classifying ESRCH as refused hide a REAL pidfd
   outage?" — Outage errnos are EMFILE/ENFILE/EINVAL/EPERM,
   not ESRCH; ESRCH is per-pid, not per-subsystem. The EMFILE
   control stays in the suite as the outage witness.
3. "Injected ESRCH on a LIVE victim: victim survives the mock —
   does the new control falsely claim death?" — The control
   asserts the BUCKET (refused, not unavailable), not death;
   wording must say exactly that. (Director would probe this.)
4. "errno access: OSError raised by mocks may lack .errno?" —
   Injected OSError(3, ...) sets errno=3; real syscall failure
   via os.pidfd_open sets errno. Guard: getattr(e, "errno",
   None) == errno.ESRCH; None -> unavailable (conservative:
   unknown failure stays unavailable, never refused).
5. Sequel sweep: does anything else consume "unavailable"
   besides the verdict suffix + REGRESS print? run_entry both
   paths (timeout + non-timeout print) read _kill_report
   unavailable — reclassification only REMOVES gone instances
   from that set, which is the contract. _LAST_KILL_REPORT
   consumers: check.
6. Mutant: restore `except OSError: return "unavailable"`
   (ignore errno) -> new control must fail exactly (22/23 or
   the ESRCH checks), EMFILE control must still pass.

## Failing-first plan
Probe script (hidden_files/daf09esrch_probe.py): spawn live
sleeper, capture identity, monkeypatch os.pidfd_open to raise
OSError(3), call R._signal_identity / _kill_process_tree,
print bucket. Unmodified code -> "unavailable" (defect);
fixed -> "refused". EMFILE(24) control -> "unavailable" both.

## Closure gauntlet (standing)
SWAT (above) > failing-first > implement > suite 23/23 >
mutant killed exactly > regress x3 > PR > exact-head CI in a
separate step > merge (merge tree == candidate tree) >
fresh-clone regress > packet > register line > segmented
Director report + INDEX row, held SUBMITTED > state update.
