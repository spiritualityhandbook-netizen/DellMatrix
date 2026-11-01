# DIRECTOR REPORT ADDENDUM — DAF-09 PIDFD HARDENING (session-escape only)

Evidence submitted for a bounded re-ruling. A report is evidence,
never a certificate. Merged != certified.

## Ruling this answers

Director Mode D (2026-10-31), on the DAF-09 identity follow-up at
3234966: session-escape certification REMAINS WITHHELD. His
independent suite returned 18/20 — the escaping descendant's
post-timeout marker check and the identity positive control failed;
both refusal controls PASSED. Recorded gap: when pidfd_open fails,
_signal_identity fell back to numeric kill() after an earlier
identity check, leaving a PID-reuse window (mock-confirmed; no real
bystander signalled). His directives: record the 18/20; capture
witness identity / reparenting / signal result / marker timing;
make the positive control wait boundedly for termination; remove
the numeric fallback for historical witnesses or provide an equally
strong guarantee and report unavailable cleanup explicitly; add
pidfd-open failure controls; re-present session-escape only.

This addendum re-presents the session-escape coverage only.
Cancellation is CERTIFIED and is not re-opened. The earlier
"investigation resolved" claim stands corrected as premature
(AGENTS.md §31.3); this submission makes no cross-environment
claim — it reports Uni's environment exactly and asks the Director
to re-run in his.

## Frozen candidate

Candidate: 86df4af7d08fc77db81b406492b453461d646a42
Candidate tree: bd1eeb411f933c25ee359099975fcfb950542dc7
Base: main 82fe2addba4aa0ed5d4cba05d30695ea57b9d669 (PR #180 merge)
PR: #181 — merged as 87be4de7fc310baf9e93bbef0d805ec83373c8bc
  (2026-11-01T04:11:19Z)
Merge tree: bd1eeb411f933c25ee359099975fcfb950542dc7 == candidate tree
Merge parents: 82fe2ad + 86df4af

## Defect (verified in code at 82fe2ad, form/regress.py)

- _signal_identity verified starttime BEFORE the pidfd attempt; on
  pidfd_open OSError it fell through to os.kill(pid, sig) guarded
  only by that earlier check — a silent downgrade from the verified
  primitive to the unverified one (AGENTS.md §31.2).
- The identity positive control sampled victim.poll() once,
  immediately — an asynchronous assertion without a bounded wait
  (§31.1), the race class behind the 18/20 discrepancy.
- The escape check carried no diagnostics distinguishing
  never-witnessed / witnessed-not-signalled / signalled-but-wrote /
  timing.

## Failing-first probe

hidden_files/daf09_pidfd_probe.py monkeypatches os.pidfd_open to
raise OSError, then calls _signal_identity on a live victim with
its CORRECT starttime. Unmodified code: VICTIM_KILLED_VIA_FALLBACK.
Fixed code: outcome "unavailable", VICTIM_ALIVE_UNAVAILABLE.

## Fix (SWAT unanimity 4/4 recorded BEFORE implementation)

Packet: DAF09_PIDFD_HARDENING_PACKET.md (Custodian, Interpreter,
Sentinel, Mechanic all AGREE). Files: form/regress.py +
form/daf09_timeout_tree_test.py.

- _signal_identity is tri-state: "signalled" / "refused" /
  "unavailable". The kill(2) fallback for witnessed identities is
  DELETED. pidfd unsupported or pidfd_open failure => "unavailable",
  the process is NOT signalled. Identity missing/mismatched =>
  "refused". ESRCH from pidfd_send_signal => "refused".
- _kill_process_tree records proc._kill_report (also stashed as
  _LAST_KILL_REPORT): {signalled, refused, unavailable} identity
  lists — cleanup failure is retained evidence, never dropped.
- Timeout verdict stays "TIMEOUT", with
  " cleanup_unavailable=<n>:<pid,...>" appended only when the
  unavailable set is non-empty; the KeyboardInterrupt path prints
  one equivalent line.
- Positive control: bounded wait (~5s poll loop) for termination.
- New pidfd-open failure controls: (a) a live witnessed process
  with matching identity is NOT signalled when pidfd_open fails
  and appears in the unavailable set; (b) unavailable cleanup is
  visible via the stashed report on a real root.
- Escape check diagnostics name the broken link (witnessed set
  membership, kill-report outcome, marker timing).
- All 20 prior checks preserved in substance; cancellation checks
  untouched. Root proc.kill() and session-scoped killpg are not
  historical-witness signalling and are unchanged.

## Evidence

- Suite: 22/22 (20 preserved + 2 pidfd-failure controls).
- Mutants (real work committed first; reverts via inverse edits,
  diff verified): M1 restore kill() fallback -> 20/22, failing
  exactly the two pidfd-failure controls. M2 report "signalled"
  without sending -> 19/22 (bounded-wait positive control expires;
  escape checks fail with diagnostics). Both killed; suite
  re-verified 22/22 after reverts.
- Regress x3 on candidate 86df4af (logs hidden_files/
  daf09pidfd_logs/): fwd 211/211, --twice 211/211 x2,
  --order rev 211/211 — all GREEN; daf09 suite 22/22 every leg.
- Exact-head CI verified COMPLETE in a SEPARATE step before merge
  (2026-10-31 23:10 CDT cycle run): package run 41270691124
  SUCCESS completed 2026-11-01T03:50:09Z; smoke run 41270691153
  SUCCESS completed 2026-11-01T04:06:18Z; both on head 86df4af.
- Fresh-clone regress at merge 87be4de: 211/211 GREEN
  (log hidden_files/daf09pidfd_logs/freshclone_regress.log;
  daf09 suite 22/22; REGRESS FINAL: GREEN).

## Limitations

- Linux pidfd path only; where pidfd is unavailable, witnessed
  cleanup is reported unavailable rather than performed unsafely —
  a deliberate fail-closed trade, not a silent gap.
- Uni's environment only. The Director's 18/20 environment was not
  reproduced here; per §31.3 this addendum does not claim the
  cross-environment discrepancy is resolved — it claims the three
  directed mechanisms (no numeric fallback, bounded-wait control,
  pidfd-failure controls + diagnostics) are implemented and proven
  locally, and submits the escape coverage for his re-run.
- No claim of unconditional bystander safety beyond the proven
  controls: stale-identity refusal, bare-PID refusal, and the new
  pidfd-failure non-signalling controls.

## Bounded ruling requested

Re-rule the DAF-09 session-escape coverage only, on candidate
86df4af as merged at 87be4de: whether the pidfd-hardened tree kill
(witnessed identities signalled only via identity-pinned pidfds;
pidfd failure => explicit unavailable cleanup, never a numeric
fallback) satisfies the session-escape contract within the tested
Linux scope. Cancellation is already certified and not re-opened.
