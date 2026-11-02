# DIRECTOR REPORT — DIR-F16: pidfd send-boundary error classification

**Status: SUBMITTED for Director ruling. Nothing certified by
submission. Merged != certified.**

## Ruling requested / scope identity / exceptions FIRST

- **Scope:** form/regress.py `_signal_identity` send boundary +
  form/daf09_timeout_tree_test.py check-10 series. One circuit,
  one mechanism. NOTHING else in DAF-09 is re-presented.
- **Ruling requested:** certify (or decline) the bounded claim:
  *pidfd_send_signal errors are classified by errno — ESRCH =
  "refused" (instance proven gone; signal delivered to nobody);
  any other send OSError (EPERM, ENOSYS, EINVAL, errno-less) =
  "unavailable" (cleanup attempted and failed; surfaced through
  the kill report and the timeout verdict as
  cleanup_unavailable).*
- **Exceptions / non-claims:** DAF-09 session-escape remains
  WITHHELD and is not part of this scope. The cross-environment
  discrepancy remains UNRESOLVED. The cancellation certificate
  is untouched. This report does not ask the Director to lift
  any earlier exception.
- **Evidence accessibility (R1 Priority 2, applied here):** raw
  evidence for THIS circuit is published in-repo at
  `director-reports/evidence/dirf16/` (probe source, probe
  outputs pre/post fix, suite output, mutant output), with
  SHA-256 digests in the table below — retrievable from the
  repository itself, not from Uni's workspace.

## The defect (as found by the Director; verified in source)

At main 5ce5074, `_signal_identity`'s send path was a blanket
`except OSError: return "refused"`. The open path had been
errno-split by the ESRCH-at-open repair; the send path had not.
A send failure therefore asserted an identity fact (instance
gone / mismatched) that the error does not establish, and —
because run_entry surfaces `cleanup_unavailable` only from the
kill report's "unavailable" bucket — a genuinely failed cleanup
was hidden from the exact TIMEOUT verdict.

## Failed-before / passed-after (deterministic injections)

Probe: witnessed live sleeper, `_pidfd_send_signal` injected.
Pre-fix (5ce5074): EPERM -> "refused" with the process ALIVE;
ENOSYS -> "refused"; ESRCH -> "refused". PROBE FAIL.
Post-fix: EPERM -> "unavailable"; ENOSYS -> "unavailable";
ESRCH -> "refused"; nothing signalled under any injection.
PROBE PASS. Outputs: evidence files E1/E2 below.

## Fix

Send `except OSError` split by errno, mirroring the open path;
tri-state docstring updated (refused = identity missing/changed
or ESRCH at open-or-send; unavailable = open or send failure
that does not prove the instance gone). No numeric fallback
introduced or restored. Fix commit b9789bb (PR #217), merged
as dd80a0e; merge tree identical to the candidate tree.

## Tests

- Suite form/daf09_timeout_tree_test.py: 23 preserved checks
  untouched; check-10 series adds 8 assertions (31 total):
  send-EPERM/ENOSYS outcomes + victim survival, send-ESRCH
  control, consumer bucket through _kill_process_tree, consumer
  survival. Standalone: 31/31 x5 consecutive.
- Mutant (blanket-except restored, send path only): 28/31 —
  failures exactly the 3 classification assertions. Reverted by
  inverse edit; tree verified identical to the fix commit.
- CORRECTION (2026-11-02, post-submission): an earlier version
  of this report disclosed an "anomaly" — a first combined
  probe+suite invocation supposedly exiting 1 with unknown
  failing checks. That disclosure was WRONG: it rested on a
  truncated interim readout of a still-running command. The
  invocation's authoritative terminal output has since been
  delivered and shows probe PASS and suite 31/31, exit 0.
  No failing run occurred. The anomaly claim is retracted in
  full; the suite record is: first combined run 31/31, five
  standalone runs 31/31, regression legs and fresh-clone below.
- Full regression on b9789bb: 221/221 PASS x3 (forward /
  --twice / --order rev). Exact-head CI on b9789bb: COMPLETE
  SUCCESS (Python package + Form smoke). Fresh-clone regress
  at merge dd80a0e: 221/221 GREEN; probe re-run in the fresh
  clone: PASS.

## Evidence files (director-reports/evidence/dirf16/)

| ID | File | SHA-256 (first 16) | What it shows |
|----|------|--------------------|----------------|
| E1 | probe_prefix_output.txt | cba5907618915eec | failing-first at 5ce5074 |
| E2 | probe_postfix_output.txt | 0aa44f2ed2b73220 | passed-after at merge dd80a0e (fresh clone) |
| E3 | dirf16_probe.py | cd456b192b80891a | the injection probe source (repo root resolved from its own path; run from the repo root) |
| E4 | suite_postfix_output.txt | 96d6edd255c0330a | suite 31/31 at merge dd80a0e (fresh clone) |
| E5 | suite_mutant_output.txt | 76d8a1b38c186935 | mutant 28/31, exact failures |

Environment limits: Linux x86-64 VM, Python 3.12, /proc +
pidfd available; injections are monkeypatched Python-level
OSError raises at the module seam (R._pidfd_send_signal), not
kernel faults — they prove classification logic, not syscall
behavior under real EPERM conditions.

## Anticipated probes

- "Does an errno-less send OSError class unavailable?" Yes —
  only `errno == ESRCH` classes refused; None falls through to
  unavailable (Custodian attack, pre-mortem).
- "Did any preserved check change?" No — the diff to the suite
  is append-only (header contract + check-10 block); the 23
  checks' assertions are byte-untouched.
- "Does the verdict now fail-closed on send failure?" Yes —
  the identity lands in the kill report's unavailable set, and
  run_entry appends cleanup_unavailable to the TIMEOUT verdict,
  the same path the open-failure control (check 8) exercises.
- "Is the live ESRCH race re-proven?" No. The send-ESRCH class
  rests on the deterministic injected control, same posture as
  NBD-1's open-ESRCH landing.

## Questions for the Director

- Q1: Does the send-boundary classification, as evidenced,
  satisfy DIR-F16's required action, or is a kernel-level
  EPERM reproduction (e.g. cross-uid pidfd) required for the
  bounded certificate?
- Q2: Is the in-repo evidence bundle shape
  (director-reports/evidence/<circuit>/ + digest table)
  acceptable as the Priority-2 pattern for the Step 13 /
  F12–F15 evidence publications that follow?
