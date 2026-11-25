# CI RECEIPT — verify-72-16 exact-head reproduction (PR #307)

- Workflow: `.github/workflows/verify-72-16.yml`
- Run: https://github.com/spiritualityhandbook-netizen/DellMatrix/actions/runs/42138846768
- Conclusion: **success** (all steps PASS)
- Run headSha: adaa6fcfe300ff5441fd1881c17cf36946dd1b41 (PR #307 supplement head)
- Standard checks at the same head: build (3.10) PASS, build (3.11)
  PASS (run 42138846418); Form smoke PASS 15m59s (run 42138846485).

## What the run log proves (read from the log, not the check colour)

- `ASSERT exact-head identity` step: expected ==
  actual == adaa6fcfe300ff5441fd1881c17cf36946dd1b41 →
  `EXACT_HEAD_ASSERTION: PASS`, printed BEFORE any probe ran. The
  checkout used `ref: <PR head sha>` explicitly, so this is the
  head's own code, not the ephemeral merge ref.
- Manifest verification: `sha256sum -c MANIFEST.sha256` — all six
  bundle files OK.
- Authority probe: **16/16 checks passed** (q16_probe.py, tag `ci`).
- Entry-point / operand-preservation probe: **6/6 checks passed**
  (q16_entrypoints_probe.py, tag `ci`), including the live Studio
  server entry (E3) and the pinned flow-API exception (E5).

Archived artifacts from run 42138846768 (artifact
`verify-72-16-evidence`): `q16_probe_ci.log`,
`q16_entrypoints_ci.log` in this directory. These ci/ files are
receipts and are NOT part of MANIFEST.sha256 (the manifest covers
the two probes and their local run logs only).

This receipts commit moves PR #307's head; the verify-72-16 job
re-executes at the new head on push, and that run is the live
exact-head proof for the final head. PR #307 remains HELD for the
Director's evidence review — CI PASS is not merge authorization.
