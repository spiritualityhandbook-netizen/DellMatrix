# DIR-F12 PACKET — journal-deletion receipt (CLOSED 2026-11-01)

Circuit: DIR-F12 (P2, Director Ruling #7 / DIR-REVIEW-2026-11-01).
Base: main 0a1167eb02438c1d7c402d59b609e779dd4ea867 (verified via gh API + fresh clone this run).
Candidate: ce55d5059868285eb2814e3f542c594102d84405, tree 40caa80d4c85aa3854b2c06310ebc83d50a631da, branch uni/dirf12-journal-receipt, worktree ~/workspace/nbd-omega-dirf12.
Status: CLOSED — IMPLEMENTED-VERIFIED. PR #193 MERGED as e9b5d09d17309045c6c83b39c574bb047e5e1a4d (merge tree 40caa80 == candidate tree; parents 0a1167e + ce55d50). NOT certified; no certification claimed.

## Contract (before -> after)
Before: _clear_import_journal returned False on unlink failure; _fail_import reported journal_retained=False after complete compensation, recovery's four exits and the successful-landing path ignored disposal, nursery-add failure re-raised blind.
After: compensation / landing / disposal are separate facts.
- _fail_import: journal_retained = actual disposal outcome; new journal_disposal field (cleared|retained); verified compensation stays complete when true.
- Successful landing: ok=True preserved (no wrongful compensation of a complete import); result carries journal_retained.
- recover_exchange_import: _dispose_import_journal raises ExchangeError(stage=recovery, journal_retained=True, recovery_outcome=<outcome>) when disposal fails after completed/no_target/already_absent/removed; state not exposed; restored unlink permits safe retry (already_absent / completed on next load).
- Nursery-add failure: ExchangeError(stage=journal_clear, journal_retained=True) when disposal fails; original re-raise otherwise.
Single journal owner unchanged (_clear_import_journal); no durable data removed.

## SWAT pre-mortem + unanimity
Recorded BEFORE implementation in hidden_files/dirf12_ground.md (Custodian/Interpreter/Sentinel/Mechanic lenses, Director's-eye attacks 1-5). 4/4 agree, no dissent; DIR-WF-001 amendment honored (unanimity is not a truth gate; the one material counterexample — fail-closed recovery blocks loading a complete import while unlink is broken — was considered and accepted deliberately under the standing recovery law, with W3 proving restored-unlink retry).

## Evidence (executed)
- Failing-first on base 0a1167e runtime: DIRF12 suite 14/20 — exactly the 6 disposal-truth assertions failed (W1 retained report, W1 retry field, W2 surfaced field, W3 load raise, W4 recovery raise, W4 retry field).
- After fix: DIRF12_JOURNAL_RECEIPT 20/20.
- Defect-restoring mutant (disposal always claims success in _clear_import_journal): 16/20, killed (fails W1/W2/W3/W4 disposal assertions); restored, re-verified 20/20.
- Neighborhoods: STEP5B 21/21, STEP5 20/20, AF34 19/19, AF6 13/13, P9 exchange 11/11.
- Regress on candidate: 216/216 x3 GREEN — leg 1 fwd (reg_leg1.log), leg 2 --twice both passes (reg_leg2.log), leg 3 --order rev (reg_leg3.log), each incl. DIRF12 20/20.
- Exact-head CI on ce55d50 verified COMPLETE SUCCESS in a separate step before merge: package run 41312809382 SUCCESS completed 13:46:16Z; smoke run 41312809383 SUCCESS completed 14:00:26Z; head_sha == ce55d50.
- Merge: PR #193 merged 14:22:25Z as e9b5d09; merge tree 40caa80 == candidate tree.
- Fresh-clone regress at merge e9b5d09: 216/216 GREEN (freshclone_regress2.log). Disclosure: the first fresh-clone attempt was SIGTERM'd by a VM replacement at 170/216 entries with zero failures — recorded as NO RESULT and re-run in full, per the chain-durability rule; only the complete re-run is claimed.

## Claim -> assertion map
Every claim above maps to a named check in form/dirf12_journal_receipt_test.py (W1-W4) or the neighborhood suites named. No claim without an executed assertion is made.
