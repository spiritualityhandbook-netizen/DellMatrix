# DIRECTOR REPORT — DD31-CI-INTERMITTENT: root cause proven; oracle repair

Circuit: DD31-CI-INTERMITTENT closure (Ace-directed live
session, 2026-11-10; the joint research analysis ordered
under the SS33 two-cycle cap converges here). Cycle count
for the issue: exception-request + diagnostic + hardening
+ joint analysis (E1/E2) + this closure = AT/OVER cap,
closed by root-cause proof, not by another sampling round.
Base: ec67245 (main). Product code changed: NONE.

## Root cause (FACT, proven by construction)

The failing check is the LAST check of
form/dd31_sanitize_copula_test.py, "cleanup leaves no
residue". As written it listed the ENTIRE shared form/state
directory and failed if ANY filename contained the
substring "dd31" — not this suite's own files (owner
"dd31mainZZ"), any file at all. Other suites persist state
files named for uuid owners; a uuid is random hex and
sometimes contains "dd31". In forward regress order this
suite runs after ~240 suites have written thousands of
state files, so an innocent bystander file trips the check
roughly a quarter to a third of passes. Alone, or in
reverse order (suite runs early, directory nearly empty),
it cannot trip. Sanitize itself never failed: all 16 pure
checks are deterministic, and the 5 Program checks depend
only on the suite's own cleaned owner state.

## Live proof (Ace present, 2026-11-10 ~08:36 CST)

On the UNMODIFIED suite, in a scratch copy:
- control (clean state dir): 21/21.
- plant unit_9f2dd31beef4.json (substring inside a hex ID,
  not owner-related): 20/21, FAIL "cleanup leaves no
  residue: ['unit_9f2dd31beef4.json']".
- plant <uuid-with-dd31>_program.json (the exact shape of
  a uuid-owner suite's state file): 20/21, same check,
  same signature.
An owner-named plant (notes_dd31mainZZ_extra.json) was
correctly removed by the suite's own cleanup and did not
trip the check — the defect is the check's SCOPE.

## Fit to the whole evidence ledger

- Always exactly 20/21, never any other count: this is the
  only check whose truth depends on ambient shared state.
- Forward-order reds (3/3 on the DD-42 tree; CI pass 2 and
  both-pass cases): maximal accumulated filenames precede
  the suite. Reverse order green: minimal population.
- CI and local both: both run the suite inside a copied
  tree whose state accumulates across entries.
- E1 (240 predecessors paired in fresh copies, zero hits):
  one predecessor's files almost never contain the
  substring. E2 (prefix ladder, up to 5,839 files, green):
  that population happened to lack a "dd31" uuid name;
  two green samples do not exclude a ~29% rate.
- The Director's own harness finding (run_entry discarded
  stdout) is why the failing check's NAME stayed hidden:
  the suite prints it, the stock runner threw it away.

## Repair (test oracle only)

The residue check now scopes to the suite's owner:
leftovers = files whose name contains the owner this
suite created and cleaned. The check's name and subject
("this suite leaves nothing behind") are unchanged; its
jurisdiction is corrected. AGENTS SS30: a certification
test must construct/assert its own contract, not inherit
ambient machine state.

Controls on the FIXED suite:
- control: 21/21.
- both bystander plants present: 21/21 (was 20/21).
- positive control (cleanup disabled in a scratch mutant
  + the suite's own residue planted): the check FAILS on
  exactly its own file — it still bites its true subject.
Full 3-leg regression at the PR head + exact-head CI are
the population-level outcome evidence and ride the PR.

## Relationship to open items

- PR #350 (privacy-hardened capture): UNCHANGED path. The
  trap remains the standing instrument — it is what would
  have named this check in CI — and its conditional merge
  authorization stands on its own terms. This PR is
  independent: the oracle fix removes the flicker; the
  trap guarantees the NEXT unknown failure is named.
- DD-31 certified scope (Dell 41 copula redaction) is
  untouched: zero product code, zero semantic checks
  changed; only the final housekeeping assertion's scope.

## Questions for the Director / Grok

- Q-DD31F.1: scoped certification of this oracle repair
  as the closure of DD31-CI-INTERMITTENT, on the PR's
  evidence (live proof + controls + full chains + CI).
- Q-DD31F.2: sibling sweep — should Uni audit the other
  suites for whole-directory assertions of the same class
  (SS30), as one bounded inventory, before they flicker?

## Anticipated probes

- "Did you weaken the suite?" The check still fails on
  the suite's own residue (positive control above). What
  it no longer does is convict other suites' files.
- "Is the wild instance proven?" The mechanism is proven
  by construction and fits every recorded datapoint,
  including the order asymmetry no other hypothesis
  explained. The trap in PR #350 remains as the standing
  witness for any future occurrence.
