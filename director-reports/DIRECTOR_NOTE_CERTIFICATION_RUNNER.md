# DIRECTOR NOTE — independent certification runner

**Status: SUBMITTED — awaiting Director ruling (not certified).**
Responds to: DIR-2026-11-02-CONSOLIDATED-R1, execution order
item 2. The runner is an execution instrument, not a
certificate: it exists so the certifications deferred in that
review for lack of independent execution can be decided from
outputs the Director produces himself.

## How to run it

In any fresh clone of this repository, from the clone root,
one command (Python 3, standard library only, no network):

    python3 director-reports/certification_runner.py

Optionally `--out DIR` chooses the output directory (default:
`certification_run_<UTC timestamp>` under the current
directory). Items run sequentially — the suites share
form/state and must never run concurrently; per-item timeout
900s. Exit code is 0 only if every suite and probe exits 0;
any failure, timeout, or missing file exits 1.

## What it executes

Targeted suites (subprocesses, `python3 -m <module>`, raw
stdout/stderr/exit captured per item):

| Scope | Suite | R1 condition it answers |
|---|---|---|
| DIR-F12 | form.dirf12_journal_receipt_test (20 checks) | failure-injection/restart execution |
| DIR-F13 | form.dirf13_loop_count_test (17) | malformed-count execution |
| DIR-F14 | form.dirf14_catch_consumed_test (25) | direct/chain execution |
| DIR-F15 | form.step9_diff_test (24) | exception lift pending execution |
| DIR-F16 | form.daf09_timeout_tree_test (31) | runtime execution of the send classes |
| T2 + DIR-T2-R2 | form.mandell.view_rooms_growth_test (26) | identity execution incl. R2 cases |
| Step 10 | form.step10_consistency_test (34) | full behavioral probe |
| Step 11 | form.step11_public_contracts_test (31) | runtime confirmation of the wording scope |

Independent boundary probes (fresh code shipped inside the
runner; the suites are not imported; probe sources are
preserved in every run's output under `probe_sources/`):

- **probe_t2_omitted_node** — the DIR-T2-R2 required
  counterexample: plant A grown to branch; only unplanted
  node B sharing A's 80-char prefix is supplied; B must never
  receive A's stage. Plus a positive control (A resolves to
  its own stage) and the legacy prefix-only rule (ambiguous).
- **probe_dirf16_send_boundary** — a live witnessed sleeper;
  the send boundary is forced to raise EPERM / ENOSYS /
  ESRCH. EPERM and ENOSYS must class "unavailable" with the
  victim unsignalled; ESRCH must class "refused".
- **probe_dirf15_absent_vs_none** — the Director's Diff
  reproducer through the public seed path: a stored None
  (seeded directly into state — disclosed method; no public
  string writer emits None) is deleted and must appear in
  `changed`; a retained None must not.
- **probe_dirf13_malformed_count** — the count grammar
  directly (superscript, Arabic-Indic, oversized, empty
  refused; lawful counts parse) and through the public Loop
  path (superscript count refuses `invalid_loop_count`; the
  program stays usable).

Each run writes an environment header (Python version,
platform, the revision SHA executed at, the runner file's own
SHA-256), per-item raw streams, a summary, and a
MANIFEST.sha256 digesting every output file (C-Q2 standing
format — the digests are the means to verify the bytes; the
manifest itself claims nothing).

## What our run produced (Uni-side simulation — NOT independent execution)

To prove the instrument works end-to-end before asking the
Director to rely on it, Uni ran the exact command in a fresh
clone of the public repository at main `081dd35`, with the
runner file overlaid byte-identical (its SHA-256,
dc988ad38123d75a…, is the committed runner's digest and is
recorded in the run's environment header). Result: runner
exit 0, **12/12 items exit 0**; suite counts DIR-F12 20/20,
DIR-F13 17/17, DIR-F14 25/25, DIR-F15 24/24, DIR-F16 31/31,
Step 10 34/34, Step 11 31/31, T2 26/26; probes 4/4, 7/7, 2/2,
8/8. The run's MANIFEST.sha256 verifies 30/30 via
`sha256sum -c`. Full raw outputs: 
`director-reports/evidence/certification_runner/run/` with
the bundle manifest at
`director-reports/evidence/certification_runner/EVIDENCE.md`.

Honesty controls: the runner was also negative-tested — with
one suite module replaced by a nonexistent module, it reports
that item FAIL and exits 1 (OVERALL: FAIL). A green summary
from this instrument therefore means the items actually ran
and exited 0 in that environment.

## Limits (stated, not hidden)

- The bundled run is Uni-side, on Uni's machine and Python
  (3.12.3, Linux). It demonstrates the instrument; it is not
  the independent execution R1 deferred for, and nothing in
  this note asks that any scope be certified from it.
- The runner executes at whatever revision it sits in; the
  environment header records that SHA so outputs are always
  attributable to an exact tree.
- The runner does not execute the DAF-09 session-escape scope
  (item 4 of the execution order, environment-sensitive by
  definition) and does not touch Step 13 or Step 14 items.

## Questions for the Director

- Q1: Run it and rule per scope from your own outputs — do
  the deferred certifications (Items 1, 3–8 of
  DIR-2026-11-02-CONSOLIDATED-R1) close, and does the F15
  exception lift?
- Q2: Is the probe set the right independent boundary, or are
  there additional counterexamples you want shipped inside
  the runner before you run it?
