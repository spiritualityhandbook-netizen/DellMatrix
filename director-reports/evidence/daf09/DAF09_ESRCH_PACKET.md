# DAF-09 ESRCH-AT-OPEN FOLLOW-UP — PACKET (sleep-mode NBD candidate 1)

Date: 2026-11-01 (sleep mode). Base: main 48c10f2 (PR #209 merge).
Candidate: a15e099 (branch uni/daf09-esrch-at-open), tree 7c862d7.
PR #210 MERGED as 4ba052c (merge tree 7c862d7 == candidate
tree; parents 48c10f2 + a15e099). Status: IMPLEMENTED-
VERIFIED. NOT certified. Session-escape remains
WITHHELD; the Director's cross-environment discrepancy remains
UNRESOLVED (AGENTS.md §31.3) — this circuit fixes a locally
evidenced classification defect only and claims nothing about
his 19/22.

## Defect (evidence)
Instrumented investigation (DAF09_INSTRUMENTED_INVESTIGATION_
PACKET.md): run7 pidfd_open on pid 35111 raised errno 3 (ESRCH)
with the starttime pre-read MATCH — the witnessed instance had
already died (frequently group-killed at the top of
_kill_process_tree). _signal_identity bucketed ANY pidfd_open
OSError as "unavailable", so run_entry appended
cleanup_unavailable=1:35111 to the verdict: "TIMEOUT
cleanup_unavailable=..." — failing only the exact-equality
TIMEOUT verdict checks (21/22 in run4 and run7) although the
descendants were dead and cleanup had in fact succeeded. Run6
showed the same race landing post-open (send/recheck) classing
"refused" with the verdict intact: the bucket for an
already-dead witnessed instance was timing-dependent.

## Repair contract
- pidfd_open OSError with errno == ESRCH -> "refused" (the
  already-dead class; the same fact pidfd_send_signal ESRCH
  reports one syscall later, already classed "refused").
- All other errnos stay "unavailable"; an OSError without an
  errno stays "unavailable" (unknown failure never upgrades to
  refused). hasattr(os, "pidfd_open") False stays "unavailable".
- No numeric fallback introduced (§31.2); no verdict strings,
  timing, or sleeps changed. One site: form/regress.py
  _signal_identity (+ errno import + docstring precision).

## SWAT Director's-eye pre-mortem (before implementation)
Recorded in hidden_files/daf09esrch_ground.md: ESRCH is per-pid,
not a subsystem outage (outage errnos EMFILE/ENFILE/EINVAL stay
unavailable, witnessed by the retained EMFILE control); the new
control asserts the BUCKET, not death; sequel sweep found the
only "unavailable" consumers are run_entry's verdict suffix /
REGRESS print and _LAST_KILL_REPORT diagnostics.

## Evidence
- Failing-first probe (hidden_files/daf09esrch_probe.py) on
  base 48c10f2: ESRCH(3) -> unavailable (defect), EMFILE(24) ->
  unavailable. On fixed code: ESRCH -> refused, EMFILE ->
  unavailable.
- Suite form.daf09_timeout_tree_test: 22 -> 23 checks (exact 22
  preserved in substance + ESRCH-at-open control). Fixed code:
  23/23. Mutant (ESRCH branch disabled, applied AFTER the real
  commit, reverted by inverse edit, diff verified clean):
  22/23 — exactly the new control fails; EMFILE control passes.
  Suite re-verified 23/23 after revert.
- Regress x3 on candidate a15e099: 220/220 GREEN x3
  (logs hidden_files/daf09esrch_logs/).
- Exact-head CI: verified COMPLETE SUCCESS in a separate step
  before merge (package 41383414668; smoke 41383414678; both
  head a15e099).
- Fresh-clone regress at merge 4ba052c: 220/220 GREEN.

## Anticipated probes
- "Does refused hide real unavailability?" No: ESRCH is the
  kernel saying THIS pid has no process; availability failures
  are different errnos and still surface as unavailable +
  cleanup_unavailable verdict suffixes.
- " PID reused and the reuser also died before open?" Still
  refused, still honest: the witnessed instance is dead and
  nobody was signalled; refused never claims a kill happened.
- "Why not re-read starttime instead?" ESRCH from pidfd_open is
  itself the authoritative gone signal for the pinned pid; a
  re-read adds a second race window, not certainty.

## Questions for the Director
Q1. Does the ESRCH-at-open classification match your reading of
    the run7 evidence, or should gone-at-open remain visible
    somewhere in the verdict (e.g. a separate gone count)?
Q2. Should the instrumented driver be re-run under saturation
    on the fixed code as a post-check (expecting verdict-exact
    22/22-equivalent runs), or is the suite control sufficient?
