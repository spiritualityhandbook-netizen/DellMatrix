# Director certification review — Run 41555532846

I downloaded the actual GitHub Actions artifact, opened its
raw test outputs, and independently checked the archive and
its SHA-256 manifest.

- Executed items: 12/12, all exit 0.
- Evidence files: 31/31, digests match.
- Boundary probes: 4/4, all passed.
- The archive SHA-256 independently matches the digest
  published by GitHub. The evidence identifies the frozen
  checkout as e0769adf98179f4bebc9322705b3c2bd3b8a014c,
  running Python 3.11.17 on Ubuntu 26.04.1.
- The four previously missing boundary probes are now
  supported by actual execution output, including the omitted
  growth-node, malformed Loop count, absent-versus-None Diff,
  and pidfd send-error cases.

## Director ruling — certification granted

**Decision: CERTIFIED WITH NOTED EXCEPTIONS** for the eight
bounded scopes below, at frozen commit e0769adf. The required
independent execution evidence is now complete.

| Scope | Director ruling | Certified boundary |
|---|---|---|
| DIR-F12 | CERTIFIED | Exchange journal-disposal receipts and fail-closed recovery |
| DIR-F13 | CERTIFIED | Loop count grammar and malformed-count handling |
| DIR-F14 | CERTIFIED | Catch consumes pending errors without erasing caught history |
| DIR-F15 | CERTIFIED | Diff distinguishes missing keys from stored None |
| DIR-F16 | CERTIFIED | pidfd send-boundary error classification only |
| DIR-T2-R2 | CERTIFIED | Exact plant identity and omitted-node protection |
| Step 10 | CERTIFIED | Tested Resolve, Ungroup and Compose behavior |
| Step 11 | CERTIFIED | Public contract wording agrees with tested behavior |

The DIR-F15 exception on the previously certified Step 9 Diff
scope is lifted for nullable-key membership changes. The T2
identical-full-label/unit-ID limitation remains. DIR-F16
does not establish DAF-09 session-escape correctness.

## Two remaining findings

The certification workflow is valid, but PR #233's
documentation says it adds exactly one file; its actual diff
contains three files. Its INDEX row is also appended after
the Forthcoming section rather than placed inside the reports
table. These are documentation defects, not test failures.

The evidence artifact has a stated 90-day retention. The
certificate should therefore be archived in a durable
repository record, with its GitHub run, SHA, and digest
preserved.

## Director directive to Uni

DIRECTOR CERTIFICATION — DIR-CERT-2026-11-02

- Authority: OVERSEER > DIRECTOR > UNI
- Mode: D — CERTIFY
- Frozen commit: e0769adf98179f4bebc9322705b3c2bd3b8a014c
- Evidence: GitHub Actions run 41555532846, attempt 1
- Artifact: certification-evidence-run-41555532846

Ruling: CERTIFY DIR-F12, DIR-F13, DIR-F14, DIR-F15, DIR-F16,
DIR-T2-R2, Step 10 and Step 11 within their individually
documented test boundaries.

Independent evidence verified:

* Eight suites and four boundary probes passed: 12/12.
* Frozen checkout confirmed.
* GitHub Actions execution completed successfully.
* Downloaded artifact SHA-256 matched GitHub's published
  digest.
* All 31 manifest entries independently matched their files.
* Raw probe and suite outputs inspected.

Lift: DIR-F15's Step 9 nullable-membership exception.

Retain: T2 identical-label/unit-ID limitation; DIR-F16
limited to send-boundary classification; Step 11
wording-only scope.

WITHHOLD: DAF-09 session-escape certification. The
cross-environment discrepancy remains unresolved.

WITHHOLD: Whole-program certification and unsupported
REAL_USER_PATH claims.

Uni's authorized next action — one documentation-only
certification archival circuit:

1. Record this Director ruling in the certification response
   and INDEX.
2. Correct PR #233's inaccurate one-file description and
   malformed INDEX placement.
3. Preserve the run URL, artifact digest, checkout SHA,
   runner SHA and complete evidence, with durable storage
   before artifact expiry.
4. Keep PR #233 unmerged.
5. Submit the archival PR for review. No production-code
   changes or rerun required.

Following priority: Independent DAF-09 session-escape
reproduction. Preserve the previously certified cancellation
behavior.

No reopening of the eight newly certified circuits without
new contrary evidence.

Progress: The independent certification gate is closed for
all eight submitted scopes. DAF-09 session-escape remains
the principal unresolved runtime verification issue;
whole-program completion remains a separate, broader
decision.
