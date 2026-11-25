# Evidence bundle — d1_typed_52_53

Durable in-repository copy of the Uni-produced evidence behind
circuit **D1-TYPED-52-53** (typed signatures for Dell 52 Filter
and Dell 53 Scope; PR #250), published per step 4 of the
Director's ruling of 2026-11-03 (see
`director-reports/responses/DIRECTOR_RULING_D1_TYPED_52_53_2026-11-03.md`).

## What this is

The complete 18-file evidence set recorded in the circuit's
SHA-256 manifest: the SWAT pre-mortem (`SWAT.md`), the
completion envelope (`ENVELOPE.md`), the failing-first probe
and its red/green logs (`probe_red.py`, `red_probe.log`,
`green_probe.log`), literal REPL transcripts (`repl_red.log`,
`repl_green.log`), the new suite's red/green logs
(`suite_red.log`, `suite_green1.log`), sibling-suite results
(`siblings.log`), the three defect-restoring mutant logs
(`mutant1.log`, `mutant2.log`, `mutant3.log`), the three
sequential regression runs (`regress_fwd.log`,
`regress_twice.log`, `regress_rev.log`), the fresh-clone
regression (`freshclone_regress.log`), and the exact-head CI
record (`ci_final.log`).

- Manifest: `MANIFEST.sha256` in this directory; its own
  SHA-256 is
  `a543971989c9cb31ec2b7c5ed71618c848a4870af511d887bd6b48a8413d3f`.
- Every file in this copy was verified against the manifest
  after copying (`sha256sum -c`: 18/18 OK).

## Provenance boundary (read this first)

These are **Uni-produced** logs, published after the fact for
the durable record. The Director's certification of
D1-TYPED-52-53 (**CERTIFIED WITH NOTED EXCEPTION**) rested on
his independent check of the PR #250 patch and the
GitHub-hosted CI results at the exact head — **not** on
independent inspection of these logs. That distinction is the
ruling's noted evidence exception and must remain on the
record: this bundle is preserved evidence, not
Director-inspected evidence.
