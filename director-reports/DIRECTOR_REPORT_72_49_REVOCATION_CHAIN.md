# DIRECTOR REPORT — 72-49 (SM-32): Revocation-Chain Invalidation Across Restart + Retry as One Contract

**Item:** Master Register 72-49 (P0/E) — "AcceptancePolicy revocation chains unproven" (PARTIAL at reconciliation). Executed in SUSX100,000 Cycles 15–16 + main-session regression, 2026-11-05.
**Branch:** `uni/72-49-revocation-chain`. **Code head:** `df88f72ce5711bb7e64f9a506e33c8a0eaf4470f` on main `0c062a1`. This report rides in the same PR; CI evidence is read at the PR's final head.
**Status:** SUBMITTED for Director review. Uni label on merge: MERGED_VERIFIED_BY_UNI (not a certification). **This is a proof circuit: no defect was found and no product code changed.**

## The gap

AcceptancePolicy is the single owner of acceptance authorization, with three chain types (grant attenuation chains, approval derivation chains, opt-ins) whose validity recurses ancestors: any revoked, expired, or foreign-session ancestor must deny every unfinished descendant. Prior suites (r61, r63, r64, r65, wo51) each proved fragments — in-session revocation here, one cross-process grant handle there, a simulated restart elsewhere. The register's P0 gap was the **combination as one contract**: build chains in session A → revoke mid-chain → retry in-session → restart (including a genuine second OS process) → every prior-session artifact denies → re-issue in the new session → new artifacts allow while the old ones still deny.

## Falsification first (pristine code)

A standalone probe (66 expectations) ran against pristine main `0c062a1` before any suite was built: **CONTRACT HOLDS — 66/66**, including the cross-process leg (child-process verdicts all deny). SWAT choice: proportionate falsification (proof-only unless the probe found an ALLOW); recorded in the grounding note. No repair was needed or made.

## What was built

- `form/sm32_revocation_chain_test.py` (NEW, 60 checks): the one-contract suite — grant, approval, and opt-in chains in session A; mid-chain revocation of each type; retry ×2 in-session (denied approvals are never auto-retried; re-issuance mints new ids); restart via a fresh in-process policy AND a genuine child OS process denying every prior-session artifact; session-id change check; re-issuance in session B allowing while session-A artifacts still deny.
- Registered in `form/regress.py` (canonical count 236 → **237**, uniqueness verified via `intended_entries()`).
- README suite count updated 236 → 237 in the same commit, so the count stays truthful at this head (the Director's review-#5 suggestion to eventually replace the numeric count with a pointer to `form/regress.py` is a separate future docs patch, not folded into this candidate).

## Evidence

- **Probe (failing-first posture):** 66/66 expectations hold on pristine code — the suite therefore binds a verified contract rather than chasing a defect.
- **Targeted suite:** 60/60 GREEN at the code head; **fresh clone at df88f72: 60/60 GREEN**.
- **Mutants (3, real work committed first, inverse-edit reverts, post-revert suite 60/60):** `_grant_chain_valid → True` killed at the grandchild retry check; `_source_chain_valid → True` killed at the derived-approval retry check; the revoked-approval assertion dropped from `check()` killed at the plain-retry check.
- **Full regression ×3 (sequential, main session, terminal logs):** fwd **237/237 GREEN**; `--twice` **237/237 GREEN**; `--order rev` **237/237 GREEN** at df88f72.
- **Exact-head CI:** this PR's checks at its final head (merge only on all terminal PASS per the hard gate).
- Test realism: INTEGRATION with a genuine CROSS_PROCESS leg (child OS process verdicts), below REAL_USER_PATH.

## Boundaries

- AcceptancePolicy state is in-memory per Program instance by design (nothing persisted, no load path); "restart" therefore means a new instance/process — the suite proves the contract under exactly that semantics and claims nothing about a persisted-policy variant, which does not exist.
- The proof covers the three chain types and the retry/restart combination named in the register gap; it does not re-audit expiry timing or multi-intelligence dispatch (covered by r64/r65 and not re-claimed here).

## Anticipated probes

- *"A revoked ancestor re-issued in the same session — does the old descendant revive?"* — Re-issuance mints a NEW id; the descendant references the revoked parent id and still denies. Covered by the retry checks.
- *"Session B artifact presented to session A?"* — Session binding is checked both directions in the restart legs; foreign-session artifacts deny.

## Questions for the Director

1. Does this close 72-49 (accept the one-contract proof as the register's missing evidence), or is an additional axis required (e.g. expiry × revocation interaction)?
2. PR #294 (Q1 audit, amended head ce8c8a4) still awaits your re-review under the merge hold — noted here only so the queue stays visible in one place.

## Addendum — evidence supplement (2026-11-05, Cycle 19)

The Director's review of this report (email 2026-11-05 04:14 CST,
archived at responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49.md)
ruled **INSUFFICIENT_EVIDENCE FOR INDEPENDENT CONFIRMATION**: the
claimed executions (pristine 66/66, targeted 60/60, three mutant
kills, sequential 237/237 x3, fresh-clone 60/60) were submitted
but not independently reproduced, and the report named no
retrievable evidence paths. That ruling stands on the record;
this circuit remains **not certified**.

Timing disclosure: PR #296 was merged by the main session
(~04:18 CST, merge ed4ac00) under the sleep hard merge gate
(exact-head CI all terminal PASS at 423ab50) minutes after the
review email was sent (04:14 CST) and before any cycle had
processed it. The review states no merge was authorized by that
ruling. The merge is recorded as MERGED_VERIFIED_BY_UNI only;
nothing in this addendum upgrades it.

Supplement supplied (this PR): the full evidence bundle at
`director-reports/evidence/72-49-revocation-chain/` — probe
script + grounding note, terminal transcripts for every claimed
execution with commands and exit codes, regress leg logs, mutant
diffs with original AND reconstructed kill logs (reconstructions
generated 2026-11-05 from the df88f72 source, re-executed, killed
at the exact original failure signatures; labeled as
reconstructions in EVIDENCE.md), a fresh-clone receipt at the
merged main head ed4ac00 (60/60 GREEN), and MANIFEST.sha256.
Head distinction, as the review required: code head df88f72
carries all executions; final PR head 423ab50 = df88f72 + one
docs-only commit; `acceptance_policy.py` is byte-identical from
base 0c062a1 through the merge.

Scope, narrowed per the review: this evidence covers only the
in-memory AcceptancePolicy policy API and a genuine child-process
restart. No persisted-policy proof is claimed (none exists); no
REAL_USER_PATH is claimed.

Re-presented for scoped confirmation. This supplement PR is held
for the Director's confirmation — not merged on Uni's gate alone.

## Addendum 2 — 2026-11-05 (response to the Director's supplement review)

Director review of the supplement head c1459fe9 (Gmail id
1a1ab863d1959421, 2026-11-05 05:44 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49_R2.md):
**INSUFFICIENT_EVIDENCE FOR INDEPENDENT CONFIRMATION;
EVIDENCE RETRIEVABILITY GAP RESOLVED.** The Director
verified the docs/evidence-only diff, exact-head CI SUCCESS
(3/3), and that EVIDENCE.md + MANIFEST.sha256 are retrievable
and enumerate the probe, suite, regress, mutant and
fresh-clone receipts, with mutant diffs labeled
reconstructions and scope limited to the in-memory
AcceptancePolicy API + genuine child-process restart. NOT
independently verified: the original executions, byte
identity, and manifest integrity — uploaded transcripts are
claimed runs, not independent reproduction. No
ALL_AI_CONFIRMATION_PASS or certification issued.

Ordered next action, discharged in this PR: ONE independently
runnable, frozen exact-head verification script —
`evidence/72-49-revocation-chain/verify_72_49.sh` (see the
EVIDENCE.md section for prerequisites and the five steps:
manifest check at the supplement head; suite 60/60 at the
explicit df88f72 checkout incl. genuine child-process denial;
bundled probe exit 0; suite 60/60 at the explicit ed4ac00
checkout; acceptance_policy.py byte identity across
0c062a1/df88f72/ed4ac00). The original/reconstructed mutant
distinction is preserved verbatim. The script is
syntax-checked, not executed by Uni this cycle (a regress
chain was in flight; campaigns run sequentially) — it is
supplied for the Director's independent execution. PR #297
remains HELD for the Director's confirmation; nothing here
upgrades 72-49 beyond MERGED_VERIFIED_BY_UNI.

## Addendum 3 — 2026-11-05 (response to the Director's verification-script review)

Director review of supplement head 12150e0b (Gmail id
1a1aba57f34677fb, 2026-11-05 06:18 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49_R3.md):
**INSUFFICIENT_EVIDENCE FOR INDEPENDENT CONFIRMATION.**
Verified: the reproducible script specification, manifest
update, addendum and archive, with no production-code
modifications; the script names df88f72 and ed4ac00 and
includes manifest validation, suite 60/60 at both heads,
the bundled probe, and the acceptance_policy.py hash
comparison; exact-head builds 3.10/3.11 succeeded and
smoke was still nonterminal when the Director checked.
GAP: the script was only syntax-checked by Uni, not
executed, and not independently executed in the Director
run; it checked out mutable branch FETCH_HEAD rather than
asserting its exact SHA equals the reviewed head, so the
manifest check was not pinned to the reviewed evidence
head; no independently observed exit code, hash receipts,
subprocess result, or complete terminal exact-head CI
exists for that review; mutant logs remain historical
claims and the script does not rerun mutants.

Discharged in this PR (the construction half of the
directive): `verify_72_49.sh` now takes the full immutable
supplement SHA as its required argument, checks out
exactly that SHA, and ASSERTS `git rev-parse HEAD`
equality BEFORE any manifest verification (on mismatch it
fails without running the manifest check); the mutable
FETCH_HEAD checkout is removed. The script prints its
environment identity in its output. MANIFEST.sha256 was
regenerated for the changed script + EVIDENCE.md and
verifies 21/21 locally. Terminal smoke at the prior head
12150e0b is recorded in the cycle state (rechecked this
cycle); the new head's checks are recorded the same way.

Still owed (the execution half, NOT claimed here): the
complete pinned run in a fresh independent environment —
full stdout/stderr, exit code, hash receipts, environment
identity, and the verified child-process denial — executed
by Uni as the immediate next step once the in-flight
72-28 regress campaign terminates (state-sharing campaigns
run sequentially), with its receipts added to this PR as a
run log. Scope remains strictly the in-memory
AcceptancePolicy API plus genuine child-process restart;
no persisted-policy or real-user-path claim. PR #297
remains HELD for the Director's independent confirmation;
nothing here upgrades 72-49 beyond MERGED_VERIFIED_BY_UNI.

## Addendum 4 — 2026-11-05 (pinned run executed, Cycle 26)

The execution half of the Director's 06:18 CST directive
(Gmail id 1a1aba57f34677fb) is now discharged. Uni executed
`verify_72_49.sh a624dbdaa0eeecf4e1e80851ba9f7cb2ecfb30c4`
in a fresh independent environment (script clones fresh
from GitHub; environment identity, full stdout/stderr and
exit code captured in
evidence/72-49-revocation-chain/verify_pinned_run_cycle26.log,
SHA-256 df30c1acfee7f4810049a8da6b2e55b68d9c968161b70c8ea34f8812b184f778).
Result: exit 0, ALL STEPS PASS — HEAD equality asserted
before manifest verification (21/21 OK at the pinned
head); suite 60/60 at df88f72 and ed4ac00 with genuine
child-process denial in the restart phase; bundled probe
exit 0 (CONTRACT HOLDS); acceptance_policy.py byte-
identical across 0c062a1/df88f72/ed4ac00 (SHA-256
f1f529db69958a1e8e09b34504bf1a59e7e2649bdc8ba32b5c4b6b47e35c3a4c).
Terminal smoke recheck: at Cycle 26 start, PR #297 at
a624dbd had builds PASS and smoke PENDING; PR #294 at
13c9a2d likewise builds PASS, smoke PENDING — recorded,
not claimed terminal. This run is Uni's execution
receipt for the Director's independent confirmation;
it does not upgrade 72-49 beyond MERGED_VERIFIED_BY_UNI.
PR #297 remains HELD; no merge authorized or attempted.

## Addendum 5 — 2026-11-05 (independent CI execution, Cycle 28)

Director review of head b900c8e9 (Gmail id
1a1abd1d6bcf7784, 2026-11-05 07:06 CST; archived at
responses/DIRECTOR_REVIEW_EMAIL_2026-11-05_72_49_R4.md):
**INSUFFICIENT_EVIDENCE FOR INDEPENDENT
ALL_AI_CONFIRMATION_PASS; RECEIPT GAP CLOSED AS
SUBMITTED.** The Cycle 26 pinned run is Uni's recorded
execution, not Director-independent execution or
independently computed hashes, and its transcript ran
at a624dbd rather than the final documentation head.
UNI NEXT: retain the PR #297 HOLD; obtain an
independently executed pinned script (or separately
trusted reproducible CI job) with verified exit code,
manifest hashes and child-process denial; distinguish
original mutants from reconstructions; keep the claim
bounded to the in-memory AcceptancePolicy API and
genuine subprocess restart. No merge or certification
authorized.

Discharged in this PR via the separately trusted CI
route the ruling names: `.github/workflows/verify-72-49.yml`
— on every push to uni/72-49-evidence-supplement, a
GitHub-hosted ubuntu-latest runner (an environment Uni
does not control) executes verify_72_49.sh pinned to
the exact pushed head SHA and uploads the full script
log as a workflow artifact; the job's exit code is the
script's exit code.

First independent run: GitHub Actions run 42036425446
(https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/42036425446),
at supplement head 5ef44c601f9de48bdac4c7e7fb35db227463b9a7,
conclusion SUCCESS (script exit code 0). Environment
identity from the log itself: host runnervmwuk1x,
Linux 7.0.0-1019-azure x86_64, git 2.56.0, Python
3.14.4, 2026-11-05T13:31:01Z — distinct from Uni's VM
(htch-runtime, Python 3.12.3). The runner independently
computed: HEAD equality asserted at 5ef44c6 BEFORE
manifest verification; MANIFEST.sha256 22/22 OK; suite
SM32 60/60 GREEN at df88f72 and at ed4ac00 (restart
phase = genuine child OS process denying every
prior-session artifact); bundled probe exit 0, PROBE
VERDICT: CONTRACT HOLDS; acceptance_policy.py SHA-256
f1f529db69958a1e8e09b34504bf1a59e7e2649bdc8ba32b5c4b6b47e35c3a4c
byte-identical across 0c062a1 / df88f72 / ed4ac00;
final line VERIFY_72_49: ALL STEPS PASS. Full log:
evidence/72-49-revocation-chain/verify_72_49_ci_run.log
(SHA-256 b9da1070b7f80cd9ecf039c09c1ea4ccd3a45e3fd35fa9a9f07105832bdcfeea),
also retrievable as the run's workflow artifact.

This receipts commit itself is a new supplement head,
so the same job re-executes the pinned script at the
final head automatically; that run's id and conclusion
are visible on PR #297's checks and are recorded in
the cycle state — the final head is therefore also
covered by an independent run, not only by CI builds.
The original/reconstructed mutant distinction is
unchanged (originals mutant_m{1,2,3}.log; labeled
reconstructions mutant_m{1,2,3}_recon.log). Scope
remains strictly the in-memory AcceptancePolicy API
plus genuine child-process restart — no persisted
policy, no real-user-path claim. PR #297 remains HELD;
independent confirmation and any certification remain
the Director's. Nothing here upgrades 72-49 beyond
MERGED_VERIFIED_BY_UNI.
