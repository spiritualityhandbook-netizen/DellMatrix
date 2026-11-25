# DAF-09 IDENTITY-SAFE SIGNALLING — follow-up packet

Circuit: Director Mode D bounded follow-up to the DAF-09 addendum.
Base: main f14df47. Worktree: ~/workspace/nbd-omega-daf09id,
branch uni/daf09-identity. Cancellation is CERTIFIED and is NOT
re-opened by this circuit; only the session-escape coverage and the
signalling identity are in scope.

## Director's directive (2026-10-31, at f1c0205)

1. INDEX: cancellation certified within tested scope; session-escape
   withheld. (Done via PR #172.)
2. Investigate the failed marker/dead checks — identities, namespace
   context, timing; distinguish cleanup failure from fixture
   assumptions.
3. Replace bare-PID retention with identity-safe signalling — prefer
   Linux pidfds where supported. Never claim unconditional
   bystander safety from historical PID membership.
4. Identity-reuse negative control; preserve cancellation/bystander
   checks; re-present one bounded follow-up through standing gates.

## Investigation results (executed)

- Uni local: 8/8 suite runs 16/16 at f14df47 (6 idle, 2 under full
  CPU saturation). Director's runs: 15/16, 14/16. Failures do NOT
  reproduce locally; discrepancy is environment-bound.
- Mapping (hidden_files/daf09_identity_mapping_2026-10-31.md):
  H1 zombie misread NOT supported (both dead-probes zombie-aware).
  H2 timing PLAUSIBLE + tight: the escapee is visible to the ppid
  witness walk only during mid's ~1s life; marker slack is 1s
  (write at 3s, timeout at 2s). Fixture assumption identified:
  mid's fixed 1.0s sleep presumes fast fixture startup + dense
  witness scans in ANY environment.
  H3 identity race CONFIRMED in code: witnessed set is bare ints in
  _communicate_tracked, _kill_process_tree, and the suite's own
  cleanup guards.
- Failing-first probe (hidden_files/daf09id_probe_barepid.py) on
  UNMODIFIED code: witnessed set containing an unrelated bystander
  pid => BYSTANDER_KILLED. The defect is demonstrated, not inferred.

## SWAT unanimity — recorded BEFORE implementation (4/4)

- Custodian: identity (pid + /proc starttime) must be captured AT
  WITNESS TIME and carried losslessly to the kill; an entry whose
  identity cannot be verified is REFUSED, and the refusal is the
  honest outcome (no silent bare-PID fallback for witnessed entries).
- Interpreter: the contract change is total — every consumer of the
  witnessed set (runner kill path AND the suite's cleanup guards)
  moves to identities in the same circuit; no bare-PID consumer
  remains behind.
- Sentinel: signalling authority extends only to a verified
  instance. pidfd preferred (kernel-pinned instance; a dead
  instance's fd signals nobody). Starttime re-verification closes
  the capture->open race; fallback path also verifies first and
  refuses on mismatch.
- Mechanic: cost stays bounded — the /proc walk already parses stat;
  starttime is one more field from the same read. pidfd open/send/
  close is O(1) per signalled process. No new unbounded waits.
- UNANIMOUS: proceed with the design below.

## Design

regress.py:
- _proc_starttime(pid): /proc/<pid>/stat field 22 via the existing
  last-')' parse (tail[19]); None when unreadable.
- _descendant_identities(root): one /proc walk -> [(pid, starttime)]
  via ppid links (replaces _descendant_pids in both callers).
- _communicate_tracked: witnesses IDENTITIES (union of (pid,
  starttime)) on proc._witnessed_identities.
- _signal_identity(pid, starttime, sig): refuse when starttime is
  None or current starttime differs; prefer pidfd (os.pidfd_open +
  pidfd_send_signal syscall via ctypes, SYS 424) with a post-open
  identity recheck; on pidfd unavailability, fall back to os.kill
  only after the same verification. Returns delivered-or-not.
- _kill_process_tree: killpg (session-scoped, unchanged) + identity-
  verified signals for snapshot UNION witnessed identities + proc
  kill (unchanged). Legacy bare-int entries without identity are
  NEVER signalled. Post-kill liveness wait is identity-aware
  (starttime match + non-zombie), so a reused pid reads as "not
  ours", never as a survivor.
- Suite (form/daf09_timeout_tree_test.py): section 7 identity
  controls — (a) positive: correct witnessed identity is killed via
  a stub proc; (b) negative: stale identity (live bystander pid +
  non-matching starttime) is REFUSED and the bystander survives;
  (c) negative: legacy bare-pid entry with no identity is refused;
  (d) dead identity is a no-op. Escape fixture grounded: mid waits
  for the grandchild's pidfile (bounded) + 0.5s before exiting, so
  the attachment window no longer presumes fixture startup speed;
  the escape contract is unchanged. Suite cleanup guards become
  identity-checked. Docstring records the follow-up contract.

## Closure gates (standing discipline)

failing-first (probe BYSTANDER_KILLED, recorded) -> build -> suite
(all prior 16 checks preserved + identity controls) -> defect-
restoring mutant (verification removed => negative control fails)
-> neighborhoods -> regress x3 -> packet -> PR -> exact-head CI in
a separate step -> merge (tree equality) -> fresh-clone regress ->
ledger/POST_PLAN/register -> Director report addendum re-presenting
session-escape only -> publish to director-reports/ + INDEX.

## Closure addendum

Candidate ebe3243, tree 7103a4f5d1179161392123b42bf3acb3e78be9a2,
base f14df47. Files: form/regress.py, form/daf09_timeout_tree_test.py
(231 insertions, 42 deletions).
- Failing-first probe (unmodified code): BYSTANDER_KILLED, exit 1.
  Same probe on fixed code: BYSTANDER_ALIVE, exit 0.
- Suite DAF09_TIMEOUT_TREE: 20/20 (16 prior checks preserved —
  cancellation semantics untouched — + 4 identity controls).
- Mutants on scratch copies: M1 (identity verification removed,
  bare kill) 18/20 — fails the identity-reuse AND bare-PID negative
  controls; M2 (legacy bare entries signalled) 19/20 — fails exactly
  the bare-PID negative control. Both killed; candidate untouched.
- flake8 hard select (E9,F63,F7,F82) clean on both files.
- Regress x3 from the main session: leg 1 forward GREEN 210/210,
  leg 2 --twice GREEN, leg 3 --order rev GREEN; daf09 suite 20/20
  in every leg.
- PR #176 merged as 3234966 (2026-10-31T23:25:13Z); merge tree
  7103a4f == candidate tree; parents f14df47 + ebe3243.
- Exact-head CI verified COMPLETE in a separate step before
  merge: package 41251245436 SUCCESS completed 23:08:53Z;
  smoke 41251245385 SUCCESS completed 23:24:57Z.
- Fresh-clone regress at merge 3234966: 210/210 GREEN.
- Register DAF-09 entry updated with the closure. Remaining:
  ledger/POST_PLAN rows, Director report publication to
  director-reports/ + INDEX.
