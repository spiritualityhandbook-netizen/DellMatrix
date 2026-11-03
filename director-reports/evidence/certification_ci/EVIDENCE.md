# Evidence bundle — certification_ci

Durable in-repository copy of the GitHub Actions evidence
behind **DIR-CERT-2026-11-02** (see
`director-reports/responses/DIRECTOR_RULING_DIR-CERT-2026-11-02.md`),
preserved because the source artifact expires
(2027-02-01T00:49:08Z).

## What this is

Complete raw output of the Director's certification runner,
executed on GitHub-hosted infrastructure under the
CERTIFICATION EXECUTION UNBLOCK directive (2026-11-02), via
the unmerged PR #233 workflow (`.github/workflows/certification.yml`
on branch `uni/certification-ci`).

- Scope: the eight bounded scopes ruled on in
  DIR-CERT-2026-11-02 — DIR-F12, DIR-F13, DIR-F14, DIR-F15,
  DIR-F16, DIR-T2-R2, Step 10, Step 11 — 8 suites + 4
  boundary probes, 12 items.
- Tested revision (frozen, guard-verified twice):
  `e0769adf98179f4bebc9322705b3c2bd3b8a014c`
- Run: https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/41555532846
  (run 41555532846, attempt 1, conclusion success)
- Artifact: `certification-evidence-run-41555532846`
  (id 13193782375, 15,250 bytes)
- **Artifact digest published by GitHub:
  `sha256:ff261be1b45413dd65ea84270d12878b6734e614875573b605e539b496ce8b20`**
  — Uni's independently downloaded archive hashes to the
  same value; the Director likewise verified the match.
- Runner instrument: `director-reports/certification_runner.py`,
  unmodified; its SHA-256 as recorded in the run's own
  environment header:
  `dc988ad38123d75a47a9352ae3c8b6b5af6df83edb351cfec3c594e68a6afcf1`
- Environment: GitHub-hosted ubuntu-latest, image
  ubuntu26 / 20261026.180.1 (Ubuntu 26.04.1 LTS), Python
  3.11.17. Full header: `certification_evidence/environment.txt`
  and `certification_evidence/execution_meta.txt`.

## Contents

- `certification_evidence/` — the runner's output tree
  exactly as produced: `environment.txt`,
  `execution_meta.txt`, `summary.txt`, `MANIFEST.sha256`,
  `suites/` (8 × stdout/stderr), `probes/` (4 × stdout/stderr),
  `probe_sources/` (4 probe sources as executed).
- `certification_meta_post/` — the workflow's post-run
  records: `runner_exit.txt` (0), `manifest_exit.txt` (0),
  `manifest_verify.txt` (the in-CI verification log).

Files not covered by the run's inner MANIFEST.sha256,
SHA-256 (computed at archival):

```
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  certification_meta_post/manifest_exit.txt
37d136ee282ee05965059f787ac27e2acae743a5c6195332de8d011bcedd0bb2  certification_meta_post/manifest_verify.txt
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  certification_meta_post/runner_exit.txt
```

## Verification performed

- Result: **12/12 items exit 0** (suites 20/20, 17/17,
  25/25, 24/24, 31/31, 26/26, 34/34, 31/31; probes 4/4,
  7/7, 2/2, 8/8) — see `certification_evidence/summary.txt`.
- In CI: `sha256sum -c MANIFEST.sha256` exit 0 and a strict
  digest re-check, 31 files, 0 mismatched.
- The Director independently downloaded the artifact,
  matched its SHA-256 against GitHub's published digest,
  and matched all 31 manifest entries against their files.
- Uni re-ran `sha256sum -c` on the downloaded copy before
  archival: all 31 files OK.

## Limits

- This bundle is execution evidence. The certification is
  the Director's ruling recorded in
  `responses/DIRECTOR_RULING_DIR-CERT-2026-11-02.md`, bounded
  per scope there (DIR-F16: send-boundary classification
  only; T2 identical-label/unit-ID limitation retained).
- Nothing here bears on DAF-09 session-escape (WITHHELD) or
  whole-program certification (NOT ISSUED).
