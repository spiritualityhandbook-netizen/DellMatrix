# 72-49 (SM-32) — Evidence bundle index

Supplement submitted 2026-11-05 (SUSX100,000 Cycle 19) in answer to
the Director's review of PR #296 (email 2026-11-05 04:14 CST,
Gmail id 1a1ab33b0360b3b9, archived at
`director-reports/responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49.md`):
verdict INSUFFICIENT_EVIDENCE FOR INDEPENDENT CONFIRMATION — the
claimed executions were not retrievable from the PR. This bundle
makes every claimed execution retrievable. MANIFEST.sha256 covers
every file in this directory (verify: `sha256sum -c MANIFEST.sha256`
from this directory).

## Commit identity (the head distinction the review asked for)

- **Code head df88f72** (`df88f72ce5711bb7e64f9a506e33c8a0eaf4470f`):
  the head at which the probe, targeted suite, mutants, regress x3
  and the first fresh-clone run were executed.
- **Final PR head 423ab50** (`423ab500ece6fcb6292f6fb979587e998c1f91d6`):
  df88f72 + ONE docs-only commit (the Director report + INDEX row).
  No code or test file differs between df88f72 and 423ab50.
  GitHub exact-head CI at 423ab50 (browser-acceptance, build 3.10,
  build 3.11, smoke) was all SUCCESS — the Director verified this
  in the review itself.
- **Merged main ed4ac00** (`ed4ac00fba08b81a7194dfd9d76618d07c74ec21`):
  PR #296 merge. `form/dell_matrix/acceptance_policy.py` is
  byte-identical from base 0c062a1 through ed4ac00; the only form/
  change in the whole circuit is the ADDED test file
  `form/sm32_revocation_chain_test.py` (227 lines).
- Post-merge fresh-clone receipt at ed4ac00 is included
  (`fresh_clone_main_ed4ac00.log`), so the final merged head is
  itself covered by a fresh-clone targeted run, not only df88f72.

## Executions (command, exit code, transcript)

| Claim | Command | Exit | Transcript |
|---|---|---|---|
| Probe on pristine base 0c062a1: contract holds 66/66 | `python3 mr49_probe.py` (script in this bundle) | 0 | `probe_pristine.log` |
| Grounding / contract matrix | — (working paper) | — | `mr49_ground.md` |
| Targeted suite at df88f72: 60/60 GREEN | `python3 -m form.sm32_revocation_chain_test` | 0 | `suite_run1_tail.log` (tail; full text identical in shape to fresh-clone logs) |
| Fresh clone at df88f72: 60/60 GREEN | clone of the branch worktree, checkout df88f72, same suite command | 0 | `fresh_clone.log` (tail-only capture — disclosed; superseded by the full receipt below) |
| Fresh clone at merged main ed4ac00: 60/60 GREEN | `git clone https://github.com/spiritualityhandbook-netizen/DellMatrix`, checkout ed4ac00, `python3 -m form.sm32_revocation_chain_test` | 0 | `fresh_clone_main_ed4ac00.log` (full, with clone source + head printed in the log header) |
| Regress leg 1 (fwd) at df88f72: 237/237 GREEN | `python3 -m form.regress` | 0 | `regress/main_leg1.log`, chain record `regress/main_chain.log` |
| Regress leg 2 (--twice) at df88f72: 237/237 GREEN | `python3 -m form.regress --twice` | 0 | `regress/main_leg2.log` |
| Regress leg 3 (--order rev) at df88f72: 237/237 GREEN | `python3 -m form.regress --order rev` | 0 | `regress/main_leg3.log` |

## Mutants (diffs + failure signatures)

Original mutant edits were reverted by inverse edit in Cycle 15
(diff 0 lines after each revert); the original kill logs are
`mutant_m{1,2,3}.log`. Because the original diffs were not saved,
the diffs in this bundle are **reconstructions generated
2026-11-05 from the df88f72 source** (semantically the recorded
mutants: M1 `_grant_chain_valid` forced True; M2
`_source_chain_valid` forced True; M3 the revoked-approval test
dropped from `check()` step 1), and each reconstruction was
re-executed against the suite in Cycle 19 — all three killed at
the EXACT original failure signatures:

| Mutant | Diff | Original kill | Reconstruction kill (Cycle 19) |
|---|---|---|---|
| M1 | `mutant_m1.diff` | `mutant_m1.log`: FAIL `A-retry1:grant_grandchild` (allowed=True want=False), suite rc=1 | `mutant_m1_recon.log`: FAIL `A-retry1:grant_grandchild`, rc=1 |
| M2 | `mutant_m2.diff` | `mutant_m2.log`: FAIL `A-retry1:derived_appr`, rc=1 | `mutant_m2_recon.log`: FAIL `A-retry1:derived_appr`, rc=1 |
| M3 | `mutant_m3.diff` | `mutant_m3.log`: FAIL `A-retry1:plain2`, rc=1 | `mutant_m3_recon.log`: FAIL `A-retry1:plain2`, rc=1 |

Post-revert suite re-verified 60/60 GREEN in both cycles.

## Scope (as narrowed by the review)

This evidence covers ONLY the in-memory AcceptancePolicy policy
API and a genuine child-process restart. It does NOT claim
persisted-policy proof (no persisted policy exists) and does NOT
claim REAL_USER_PATH. Test realism: INTEGRATION with a genuine
CROSS_PROCESS leg.

## Independent verification script (supplied 2026-11-05, Cycle 24)

Under the Director's supplement review (2026-11-05 05:44 CST,
Gmail id 1a1ab863d1959421, archived at
`director-reports/responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49_R2.md`:
INSUFFICIENT_EVIDENCE FOR INDEPENDENT CONFIRMATION; EVIDENCE
RETRIEVABILITY GAP RESOLVED), the one independently runnable
verification command is:

    bash director-reports/evidence/72-49-revocation-chain/verify_72_49.sh <SUPPLEMENT_SHA>

where <SUPPLEMENT_SHA> is the full immutable PR #297 head
under verification (e.g. from `gh pr view 297 --json
headRefOid`).

PINNED CHECKOUT (Director verification-script review,
2026-11-05 06:18 CST, Gmail id 1a1aba57f34677fb): the script
previously checked out the mutable branch FETCH_HEAD; it
now checks out exactly <SUPPLEMENT_SHA> and ASSERTS
`git rev-parse HEAD` equals it BEFORE any manifest
verification — on mismatch it fails without running the
manifest check. (A file cannot contain its own commit SHA,
so the pin is supplied explicitly and enforced by
assertion.) The script also prints its environment
identity (host, kernel, git/python versions, UTC time) in
its output.

Prerequisites: bash, git, python3 (>=3.10), sha256sum, network
access to github.com. The script clones the repository FRESH
into a temp dir (no local state is used) and checks, in order:
(1) `sha256sum -c MANIFEST.sha256` in the pinned checkout of
the PR #297 head (HEAD equality asserted first); (2) the targeted suite at the explicit executed
code head df88f72ce5711bb7e64f9a506e33c8a0eaf4470f — exit 0 and
"SM32: 60/60 GREEN" (the suite's restart phase presents
session-A artifacts to a genuine child OS process, which must
deny every one — the child-process denial check); (3) the
bundled probe against the df88f72 checkout — exit 0, no FAIL
lines (66/66 expectations incl. the cross-process leg);
(4) the targeted suite at the explicit merged head
ed4ac00fba08b81a7194dfd9d76618d07c74ec21 — same expectations;
(5) SHA-256 byte identity of
form/dell_matrix/acceptance_policy.py across base 0c062a1,
code head df88f72 and merged head ed4ac00. Exit 0 only if
every step passes.

The original/reconstructed mutant distinction is preserved:
mutant_m{1,2,3}.log are the original Cycle 15 kill logs;
mutant_m{1,2,3}_recon.log are the labeled Cycle 19
reconstructions. The script does not apply mutants.

Status of the script itself: syntax-checked (`bash -n`) at
submission; it was NOT executed by Uni in Cycle 24 (a
main-session regress chain was in flight and state-sharing
campaigns run sequentially) — its purpose is the Director's
independent execution, which is exactly what the review
requires. PR #297 remains HELD; no merge or certification
is inferred from supplying it.

PIN UPDATE (Cycle 25, 2026-11-05): the pinned-checkout fix
above discharges the Director's 06:18 CST directive on the
script's construction. The COMPLETE pinned run — fresh
independent environment, full stdout/stderr, exit code,
hash receipts, environment identity, and the verified
child-process denial from the suite's restart phase — is
executed by Uni as the immediate next step once the
in-flight 72-28 regress campaign terminates (sequential
state-sharing law), and its receipts are added to this PR
as a run log; until that run exists, NO execution of the
pinned script is claimed here. Scope remains strictly the
in-memory AcceptancePolicy API plus genuine child-process
restart — no persisted-policy and no real-user-path claim.

PINNED RUN EXECUTED (Cycle 26, 2026-11-05 06:42 CST):
verify_72_49.sh a624dbdaa0eeecf4e1e80851ba9f7cb2ecfb30c4
executed by Uni in a fresh independent clone (the script
clones fresh from GitHub into a temp dir; no local state
used). Full receipts in verify_pinned_run_cycle26.log
(SHA-256 df30c1acfee7f4810049a8da6b2e55b68d9c968161b70c8ea34f8812b184f778):
environment htch-runtime, Linux 7.0.0-39-generic x86_64,
git 2.43.0, Python 3.12.3, 2026-11-05T12:42:58Z. Result:
exit code 0; HEAD equality asserted before manifest
verification; MANIFEST 21/21 OK at the pinned head;
suite SM32 60/60 GREEN at df88f72 and at ed4ac00 (restart
phase = genuine child OS process denying every prior-
session artifact); bundled probe exit 0, PROBE VERDICT:
CONTRACT HOLDS (cross-process leg included);
acceptance_policy.py SHA-256
f1f529db69958a1e8e09b34504bf1a59e7e2649bdc8ba32b5c4b6b47e35c3a4c
byte-identical across 0c062a1 / df88f72 / ed4ac00;
final line VERIFY_72_49: ALL STEPS PASS. Scope remains
strictly the in-memory AcceptancePolicy API plus genuine
child-process restart. This is Uni's execution receipt,
supplied for the Director's independent confirmation;
PR #297 remains HELD, no merge or certification inferred.

INDEPENDENT CI EXECUTION (Cycle 28, 2026-11-05): the
Director's pinned-run review (2026-11-05 07:06 CST, Gmail
id 1a1abd1d6bcf7784, archived at
director-reports/responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49_R4.md)
ruled the Cycle 26 run INSUFFICIENT_EVIDENCE FOR
INDEPENDENT ALL_AI_CONFIRMATION_PASS (receipt gap closed
as submitted) and directed Uni to obtain an independently
executed pinned script OR a separately trusted
reproducible CI job. This PR therefore adds
.github/workflows/verify-72-49.yml: on every push to
uni/72-49-evidence-supplement, a GitHub-hosted
ubuntu-latest runner — an environment Uni does not
control — executes verify_72_49.sh pinned to the exact
pushed head SHA (HEAD equality asserted by the script
before manifest verification) and uploads the full script
log as a workflow artifact; the job's exit code is the
script's exit code. Run receipts (run id, exact head,
conclusion) are recorded in the report's Addendum 5; the
CI log of the run at the pre-receipt head is embedded in
this bundle as verify_72_49_ci_run.log, and the run at
the final head is retrievable from the PR's checks and
the workflow run artifact on GitHub. The
original/reconstructed mutant distinction above is
unchanged (originals mutant_m{1,2,3}.log; labeled
reconstructions mutant_m{1,2,3}_recon.log). Scope
remains strictly the in-memory AcceptancePolicy API plus
genuine child-process restart. PR #297 remains HELD; a
CI PASS is independent execution evidence for the
Director, not a merge or a certification.

CI RUN EXECUTED (Cycle 28, 2026-11-05): GitHub Actions
run 42036425446, at supplement head
5ef44c601f9de48bdac4c7e7fb35db227463b9a7, conclusion
SUCCESS — the job's exit code is the script's, so the
pinned script exited 0 on the GitHub-hosted runner.
Environment from the log: host runnervmwuk1x, Linux
7.0.0-1019-azure x86_64, git 2.56.0, Python 3.14.4,
2026-11-05T13:31:01Z. The runner independently computed
HEAD equality at 5ef44c6 before manifest verification,
MANIFEST 22/22 OK, suite 60/60 at df88f72 and ed4ac00
with child-process denial, probe CONTRACT HOLDS, and
acceptance_policy.py byte identity
(f1f529db69958a1e8e09b34504bf1a59e7e2649bdc8ba32b5c4b6b47e35c3a4c);
final line VERIFY_72_49: ALL STEPS PASS. Full log in
this bundle: verify_72_49_ci_run.log (SHA-256
b9da1070b7f80cd9ecf039c09c1ea4ccd3a45e3fd35fa9a9f07105832bdcfeea);
also the run's workflow artifact on GitHub. The
receipts commit carrying this section is a new head,
and the same job re-executes at that final head; its
run is on PR #297's checks. PR #297 remains HELD.
