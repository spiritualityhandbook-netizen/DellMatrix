# ERRATA — DIR-F16 evidence bundle (2026-11-02)

Two header labels in this bundle cite a merge head "dd80a0e":

- probe_postfix_output.txt, line 3 ("revision: merge head
  dd80a0e ...")
- suite_postfix_output.txt, line 2 ("at merge head dd80a0e")

That commit does not exist. Verified against GitHub
(gh pr view 217; git log of main): PR #217 merged as
**6dab0d6** (2026-11-02T12:57:26Z), tree **cc1316c**, which is
identical to the fix candidate's tree (b9789bb). The fresh
clone that produced E2 and E4 was taken from origin/main AFTER
that merge, i.e. at 6dab0d6 — so the outputs themselves are
genuine runs at the true merge head; only the SHA written into
their headers was wrong. The wrong identifiers came from a
non-terminal readout consumed after a backgrounded merge
command; its terminal output carried the true identifiers.

The evidence files are preserved byte-for-byte (their SHA-256
digests in DIRECTOR_REPORT_DIRF16.md remain valid); this
errata, the report, and the INDEX row carry the correction.
