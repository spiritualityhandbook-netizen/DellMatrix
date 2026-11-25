# GS-4 POST-MERGE RECEIPTS — PR #405 @41e1556, merged-main evidence chain

Director MODE D request (mail 1a1d12096c97ad97, 2026-11-12 ~13:00 CST).
Every gate of the conditional authorization (mail 1a1d0b65f0927bbc) is
evidenced below from terminal records. No gate was waived; nothing is
described as certified beyond the authorities' own scoped rulings.

## Candidate and merge identity

- Candidate head: 41e1556dcb6aae7a690c76aed8b6dbe327b1b94f (unchanged
  through the transaction; verified in the merge step).
- Merge: PR #405 MERGED 2026-11-12T18:35:12Z by the main Uni session
  (merge actor: Uni, main session, under the Director's conditional
  authorization + Ace's standing authorization).
- Merge commit: c0742cedbdbc9bf7f4f2950815606f572f7625f8
- Merge tree: b1474f4dabf62d627c1515d7b3d53a05a0845dec
- PR #404 merged as #405's ancestry in the same act (never standalone),
  per the standing Director ruling.

## Gate 1 — exact-head CI, terminal (candidate 41e1556)

- Form smoke run 43262338026: SUCCESS (20m23s).
- Python package runs (3.10 / 3.11) incl. run 43262338085: SUCCESS.
- Studio Browser Acceptance run 43262338055: SUCCESS.
- PR state at merge: MERGEABLE / CLEAN.

## Gate 2 — full regression campaign at candidate 41e1556 (main session)

Logs: hidden_files/gs4_campaign/campaign_{fwd,twice,rev}.log (durable
goal storage; SIGINT/SIGQUIT-reset runner; clone at candidate head).

- fwd:   REGRESS 278/278 -> GREEN; REGRESS FINAL: GREEN (order=fwd);
         LEG fwd EXIT 0. Terminal 2026-11-12 11:28:58 CST.
- twice: REGRESS pass2 278/278 -> GREEN; REGRESS FINAL: GREEN
         (order=fwd, twice); LEG twice EXIT 0. Terminal 2026-11-12
         12:14:35 CST.
- rev:   REGRESS 278/278 -> GREEN; REGRESS FINAL: GREEN (order=rev);
         LEG rev EXIT 0. Terminal 2026-11-12 12:23:33 CST.

Failed/aborted attempts and resolution (full disclosure):
- The first twice leg was KILLED mid-run by a VM replacement at
  ~11:32 CST (log frozen at 89 lines; driver died with the machine).
  Classified NO RESULT (partial output is never a result). Relaunched
  as run_campaign_legs.py (twice + rev) from the main session; both
  legs then ran to terminal GREEN (above). The fwd leg's terminal
  GREEN from the first launch stands (its log completed before the
  replacement).
- One independent live-behavior probe attempted during merged-main
  verification used a wrong import path (form.dell_matrix.primitives
  does not exist) and failed at import; it produced NO behavioral
  claim and was not retried under a guessed API — merged-main
  behavior is evidenced by the 19/19 suite run below, whose fixtures
  exercise the same grow path.

## Gate 3 — Keeper final confirmation naming the head

- Keeper FINAL CODE CONFIRMATION, PR #405 comment 6830347970
  (2026-11-12 11:04 CST): explicitly names
  41e1556dcb6aae7a690c76aed8b6dbe327b1b94f; scoped to the wall-mate
  enumeration filter; U1/U2/U3 expressly not covered.

## Gate 4 — SS32 freshness + unchanged-head transaction (same step)

- In the merge step itself (2026-11-12 ~12:34 CST), Gmail triage
  showed NO Director or Keeper mail newer than watermark
  1a1d0b65f0927bbc (the conditional authorization). No unread HOLD /
  CORRECTION_REQUIRED / INSUFFICIENT_EVIDENCE existed for #405.
- Head re-verified 41e1556 in the same step; merge executed
  immediately after; merge result read back from GitHub (state
  MERGED, mergeCommit c0742ce) before any completion claim.

## Merged-main verification (fresh clone @c0742ce)

- form/gs4_sandbox_test.py on merged main: 19/19 checks PASS
  (includes A1/A1b/A2/A3 wall contract, B-series unboxed identity,
  C-series scope composition, D-series fail-closed scope errors,
  E-series mixed-box strangers, F1-F5 malformed fail-closed).
- form/regress.py LIST on merged main: 278 entries.
- Register on merged main: 184 rows; row 184 present, status OPEN
  (verbatim as authored pre-merge; credit was NOT self-applied).

## Limitations (unchanged, not repaired, not counted as repaired)

- U1 post-growth mutation surfaces (duo.evolve / nature forces /
  opt-in auto-confirm after run() returns): UNPROVEN.
- U2 docked-session synthesis semantics: UNPROVEN.
- U3 multi-cycle compounding: UNPROVEN (all probes cycles=1).
- Boundary F-d (sandboxed=False with stale sandbox_id treated as
  unboxed per Plane precedent): separate consistency-audit item,
  not certified harmless in all consumers.

## Credit request (restated, for the authorities' ruling)

On this merged-main evidence: MWL 184 -> COMPLETE (scoped:
enumeration-level wall containment for default growth — both
reproduced manifestations plus the malformed fail-closed correction)
and the corresponding defect-dial movement. Uni claims neither.
The register/scoreboard update rides the reconciliation PR carrying
this receipts file, and applies ONLY the credit the authorities rule.
