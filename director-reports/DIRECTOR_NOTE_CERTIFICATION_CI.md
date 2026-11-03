# Director Note — Certification Execution (CI) — 2026-11-02

**Submission, not a certificate.** Execution of the
certification runner on GitHub-hosted infrastructure, per
DIRECTOR — CERTIFICATION EXECUTION UNBLOCK (2026-11-02).
Certification remains the Director's act on this evidence.

## Mechanism

- PR #233 (branch `uni/certification-ci`) adds exactly one
  file: `.github/workflows/certification.yml`. **The PR is
  not merged and is not to be merged.**
- The workflow checks out the **frozen base
  `e0769adf98179f4bebc9322705b3c2bd3b8a014c`** (pinned; a
  guard step fails the job if HEAD differs). The branch's own
  files never enter the executed tree.
- `director-reports/certification_runner.py` ran
  **unmodified**, sequentially, in one job.

## Execution record

- Job: https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/41555532846
  (run 41555532846, attempt 1; conclusion: success)
- Checkout SHA (verified twice — workflow guard and the
  runner's own environment header): `e0769adf98179f4bebc9322705b3c2bd3b8a014c`
- Runner: GitHub-hosted `ubuntu-latest`, image
  ubuntu26 / 20261026.180.1, Ubuntu 26.04.1 LTS, kernel
  7.0.0-1017-azure, x86_64
- Python: 3.11.17 (`/opt/hostedtoolcache/Python/3.11.17/x64/bin/python3`)
- Artifact: `certification-evidence-run-41555532846`
  (90-day retention), containing the complete
  `certification_evidence/` tree (environment header,
  execution metadata, per-item raw stdout/stderr, probe
  sources, summary, MANIFEST.sha256) plus the manifest
  verification record.

## Result — all 12 items exit 0

| Item | Kind | Exit | Checks |
|---|---|---|---|
| suite_dirf12 | suite | 0 | 20/20 |
| suite_dirf13 | suite | 0 | 17/17 |
| suite_dirf14 | suite | 0 | 25/25 |
| suite_dirf15 | suite | 0 | 24/24 |
| suite_dirf16 | suite | 0 | 31/31 |
| suite_t2 | suite | 0 | 26/26 |
| suite_step10 | suite | 0 | 34/34 |
| suite_step11 | suite | 0 | 31/31 |
| probe_t2_omitted_node | probe | 0 | 4/4 |
| probe_dirf16_send_boundary | probe | 0 | 7/7 |
| probe_dirf15_absent_vs_none | probe | 0 | 2/2 |
| probe_dirf13_malformed_count | probe | 0 | 8/8 |

## Manifest verification

- In CI: `sha256sum -c MANIFEST.sha256` exit 0; strict digest
  re-check 31 files, 0 mismatched.
- Uni additionally downloaded the artifact and re-ran
  `sha256sum -c` locally: all 31 files OK. (Uni's check is an
  integrity confirmation of the preserved bytes, not a
  substitute for the Director's inspection.)

## Stop condition

MET — complete, downloadable evidence exists for all 12
runner items from a single pinned-base GitHub-hosted
execution.

## Explicit non-claims

- This note declares no certification for any scope.
- DAF-09 session-escape remains WITHHELD; nothing here bears
  on it (suite_dirf16 covers the send-boundary errno classes;
  the Director has excluded session-escape from it).
- Whole-program certification remains the Director's call.
