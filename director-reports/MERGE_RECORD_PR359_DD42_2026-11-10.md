# MERGE RECORD — PR #359 / DD-42 (C1.Predicate): infix conditions refuse honestly

- Requirement: plan SS12.47a / SS14.4 C1.Predicate (DD-42, cycle 1
  of 2) — conditions written infix ("level gt 99") silently fell
  through eval_predicate's prefix scan and were judged as one
  literal token, so contradictory conditions both matched True.
- Candidate: PR #359 head dd52a3a28414b24d842633b603669e3ff620cc31
  (base b27f674). MERGED 2026-11-10T15:06:39Z as
  47673cc5c65180aabdb13d2895da6f5cde94d965. ACTUAL merge actor:
  the Uni main session (its own gh merge call), verified from
  the PR's mergedAt/mergeCommit record.
- Uni evidence: suite form/dd42_predicate_infix_test.py
  failing-first 15/25 -> 28/28 after two in-circuit corrections
  (Compare shorthand-truncation control; English-door "if"
  strip); engine mutant killed 17/25; local chain fwd 264/265 +
  twice 264/265 (sole red dd31, classified DD31-CI-INTERMITTENT)
  + rev 265/265 GREEN; exact-head CI terminal ALL PASS.
  Post-merge fresh-clone verification on 47673cc: dd42 28/28,
  guard_assert 16/16, proof cards 6/6, dd31 21/21.
- Authority review: Director 06:44 verification HOLD ->
  complete evidence package published on the PR (comment
  6768499002) -> Director scoped code-review PASS (mail
  1a1c5d8df1e5ccb6, 2026-11-10 08:24 CST) conditioned on both
  authorities' dispositions + evidence reconciliation; Grok
  scoped CONFIRM (record commit ec67245 on main). Conditions
  factually satisfied before merge; SS32 receipt recorded in
  the SUSX state file immediately before the merge call.
- Failures and resolutions: first local chain 263/265 — two
  reds diagnosed and corrected in-circuit (no rerun-hoping);
  the record stands in the DD-42 Director report on main.
- Confirmation authority: Director conditional PASS (above) +
  Grok CONFIRM + Ace standing merge authorization (2026-11-05);
  merged under the hard gate from the main session. The
  Director's hourly final check is the trailing verification;
  merged does not mean certified — Q-DD42.1 scoped
  certification remains the authorities' to issue.
- Limitations: Q-DD42.2 OPEN — While/Until loop conditions
  consume the boolean only; an infix loop condition now
  evaluates False (fail-closed) but has no refusal surface.
  No infix parsing was added anywhere. Chain continuation
  policy untouched (Q-DD18.2 baseline).
- Scoreboard: defect dial 12 FIXED / 3 GATED (DD-42 fixed).
  Strict completed objectives unchanged at 19/72 (DD-42 is a
  SS14 defect circuit, not one of the 72).
