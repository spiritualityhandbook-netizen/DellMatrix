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

    bash director-reports/evidence/72-49-revocation-chain/verify_72_49.sh

Prerequisites: bash, git, python3 (>=3.10), sha256sum, network
access to github.com. The script clones the repository FRESH
into a temp dir (no local state is used) and checks, in order:
(1) `sha256sum -c MANIFEST.sha256` in a checkout of the PR #297
branch head; (2) the targeted suite at the explicit executed
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
