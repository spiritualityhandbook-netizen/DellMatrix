# MERGE RECORD — PR #357 / DD-18 C1.PulseReceipt

- Requirement: SS14.4 circuit C1.PulseReceipt (DD-18) — Pulse
  (Dell 25) and Temp-hot (Dell 26) receipts must report the
  EnhanceGate's actual verdict; a refused pulse may never be
  reported as sent.
- Candidate head: 3dc14194d2fd98fcbf09f78b562f3aab65c670f2
- Base: 6b471504ff46b96cdb3aef650e72ea5581c34c0e (main)
- MERGED: 2026-11-10T11:05:51Z as merge commit
  fd88d3d6b47c181c322d6f52a0facc6733af058b.
- Uni evidence: failing-first 5/10 -> 10/10
  (form/dd18_pulse_receipt_test.py); defect-restoring mutant
  killed 6/10, inverse-edit reverted; local regression at the
  frozen head GREEN both passes (fwd 264/264; --twice 264/264
  x2); exact-head CI terminal ALL PASS (smoke, build 3.10,
  build 3.11, browser-acceptance).
- Failures and resolutions: the first full chain caught
  d1_proof_cards_test 4/6 — two artifacts encoded the defect
  (EXPECTED_BARE_FAILURES lacked Dell 25's honest refusal;
  the committed DELL_PROOF_CARDS.md render predated the
  card-25 text). Both corrected inside the PR (expectation +
  docstring, distribution 79/21 -> 78/22; renderer
  re-render); proof cards 6/6 at the frozen head; chain
  re-run in full.
- Director review: scoped code PASS + CONDITIONAL MERGE
  AUTHORIZATION (Gmail 1a1c50b41a0de295, 2026-11-10 04:40:11
  CST) — explicitly NOT certification; Q-DD18.2 (chain policy
  on a refused Pulse) remains a separate decision.
- SS32 receipt: recorded in the SUSX state file at merge
  time (Director triage: no mail newer than the ruling;
  Grok lane: no mail, no HOLD on #357 in the record).
- Confirmation authority for the merge: the Director's
  conditional authorization with all conditions verified +
  Ace's standing merge authorization; executed from the main
  session under the hard gate.
- Post-merge verification (fresh clone at fd88d3d):
  DD18_PULSE_RECEIPT 10/10; D1_PROOF_CARDS 6/6;
  DD31_SANITIZE_COPULA 21/21.
- Limitations: Studio client-side pulse label not covered;
  gate semantics unchanged (receipt layer only); DD-44
  bounds untouched.
- Certifications outstanding (trailing list, never awaited):
  Grok certification (first); Director scoped certification
  Q-DD18.1.
- Scoreboard: strict completed UNCHANGED 19/72 (per the
  Director's ruling); defect dial: DD-18 FIXED — 11 fixed /
  3 gated. C1.PulseReceipt is CLOSED as a circuit.
