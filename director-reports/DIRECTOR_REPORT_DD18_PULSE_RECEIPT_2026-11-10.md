# DIRECTOR REPORT — C1.PulseReceipt / DD-18: Pulse receipt honesty

Circuit: SS14 C1.PulseReceipt (DD-18), cycle 1 of 2 under the
two-cycle cap. Base: main 14fcb3c. Authority: SS14 working plan +
fix-first (defect proven failing-first). Status: repair delivered;
certification is the Director's / Grok's to give.

## Defect (grounded at 7780dff and 14fcb3c, reproduced)
form/mandell/executor_leaf.py, Dell 25 branch: program.pulse()'s
return was DISCARDED and "Pulse sent." appended unconditionally;
execute_seed's fall-through reported ok=True. The EnhanceGate was
always honest ({ok: False, reason: "enhance OFF"} / budget refusal);
the lie was introduced at the leaf. Sibling in the same class:
form/repl.py's pulse action (_say("Pulse sent.") unconditional).
An existing suite encoded the lie: d1_registry_leaf3_test asserted
["Pulse sent."] WITH enhance OFF and unchanged scores.

## Repair (minimal, at the receipt layer only)
- executor_leaf Dell 25: the receipt reports the gate outcome —
  "Pulse sent." only on ok=True; on refusal the leaf returns
  ok=False with "Pulse NOT sent (<reason>)." and
  error="Pulse refused: <reason>" (the function's existing refusal
  return shape). Chain consumers read this exact result
  (chain_exec.py:165), so chain atom receipts inherit the honesty.
- executor_leaf Dell 26 (Temp hot): enhance ON is real, the pulse
  may still refuse — message now discloses it:
  "Temp → hot (enhance ON; pulse refused: <reason>)".
- repl.py pulse action: same pattern on the REAL_USER_PATH surface.
- d1_registry_leaf3_test: the encoded expectation corrected to the
  honest receipt (state assertions unchanged). dell_cards 25 note
  updated to match behavior.
No gate semantics changed; no targeting/visibility work (that
belongs to the resonance design session, per the tour record).

## Evidence
- New suite form/dd18_pulse_receipt_test.py (registered in
  regress.py LIST): FAILING-FIRST 5/10 (all five honesty checks
  red; state + controls green) -> 10/10 after repair.
- Mutant (restore unconditional claim): 6/10 — killed; reverted
  by inverse edit; back to 10/10.
- Neighbors: full d1 registry family 7/7 GREEN (incl. corrected
  leaf3 44/44), resonance_lifecycle_gate 11/11, dd31 21/21.
- Full regression, first chain: fwd and --twice both RED on ONE
  suite — d1_proof_cards_test 4/6 (dd31 GREEN everywhere in that
  chain; dd18 10/10). Diagnosis: two artifacts encoded the old
  behavior — EXPECTED_BARE_FAILURES lacked Dell 25 (bare Pulse
  now honestly fails 'Pulse refused: enhance OFF', joining the
  Step-6 bare-Decay precedent; distribution 79/21 -> 78/22) and
  the committed DELL_PROOF_CARDS.md render predated the card-25
  text. Both corrected (expectation + docstring + re-render via
  the project's own renderer); proof cards 6/6, dd18 still 10/10.
  The chain was then re-run in full for clean both-passes
  evidence at the final head, cited in the PR.
Non-claims: REPL branch verified by identical-pattern code path +
regression greens, not by a dedicated REPL-drive suite; DD-18's
wider tour items (aim/weighting/visibility) are NOT addressed.

## Questions for the Director (and Grok, confirm lane)
Q-DD18.1: scoped certification of the receipt contract as above?
Q-DD18.2: should a refused Pulse inside a chain also STOP the
chain (policy), or continue with the atom marked not-ok (current
inherited behavior, DD-19 receipts)? Uni's reading: continue +
honest atom receipt; chain policy is a separate decision.
