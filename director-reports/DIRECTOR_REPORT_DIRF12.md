# Director Report DIR-F12 — journal-deletion receipt

Requested ruling (first): DIR-F12 bounded — journal disposal reported truthfully at every consumer in form/dell_matrix/exchange.py. Exclusions: no other exchange semantics changed; step 13 re-derivation and whole-program certification are NOT requested here.
Status: SUBMITTED evidence only, not certified. Uni does not self-certify.

- Runtime candidate: ce55d5059868285eb2814e3f542c594102d84405, tree 40caa80d4c85aa3854b2c06310ebc83d50a631da, base main 0a1167eb02438c1d7c402d59b609e779dd4ea867. PR #193 MERGED as e9b5d09d17309045c6c83b39c574bb047e5e1a4d; merge tree 40caa80 == candidate tree; parents 0a1167e + ce55d50.
- Authority: DIR-REVIEW-2026-11-01 / Ruling #7, DIR-F12 (P2) OPEN entry in DIRECTOR_FINDINGS_REGISTER.md.
- Contract: before -> after, canonical owner _clear_import_journal (sole deletion owner, unchanged). Consumers fixed: _fail_import (error details), import_packet success (result field), import_packet nursery-add failure (ExchangeError), recover_exchange_import four exits (fail-closed raise via _dispose_import_journal). Public entry: exchange.import_packet + persist_rest.load recovery. Next consumer: load-boundary recovery / next import's unresolved-journal refusal.
- Claims -> assertions: each claim maps to a named W1-W4 check in form/dirf12_journal_receipt_test.py; see DIRF12_PACKET.md claim map.
- Verification: failing-first 14/20 on base; fixed 20/20; mutant (disposal always claims success) 16/20 killed, restored 20/20; neighborhoods step5b 21/21, step5 20/20, AF34 19/19, AF6 13/13, P9 11/11. Regress 216/216 x3 on the candidate (fwd / --twice both passes / --order rev; logs hidden_files/dirf12_logs/reg_leg1-3.log). Exact-head CI on ce55d50 verified COMPLETE SUCCESS in a separate step before merge (package run 41312809382 SUCCESS completed 13:46:16Z; smoke run 41312809383 SUCCESS completed 14:00:26Z). Merge tree == candidate tree. Fresh-clone regress at merge e9b5d09: 216/216 GREEN (freshclone_regress2.log; the first attempt was SIGTERM'd by a VM replacement at 170/216 with zero failures — NO RESULT, re-run in full; only the complete re-run is claimed).
- Environment: Linux, Python 3, local filesystem; unlink failure injected by a targeted os.remove wrapper failing only the journal path (real journal file on disk). No cross-environment discrepancy in this circuit.
- Limits/open: DIR-F13, DIR-F14 remain open after this circuit; DAF-09 session-escape discrepancy stays UNRESOLVED (separate track).

## Anticipated probes
1. Patch only _fail_import, leave recovery/success lying — all five consumer sites are covered and each has a witness (W1 fail-compensation, W2 landing, W3 completed exit, W4 removed exit; already_absent is exercised by W1/W4 retries, no_target shares the same _dispose helper).
2. Return ok=False for a complete landing with broken unlink — deliberately NOT done: disposal failure does not compensate a durable import; ok=True + journal_retained=True (W2).
3. Recovery returns its outcome string while the file remains — recovery now raises; the return is unreachable on disposal failure (W3/W4).
4. Retry duplicates the import — retry controls in W1/W4 and completed-import integrity in W3 (seed + 2 receipts exact).
5. Mutant — disposal-always-succeeds mutant killed at 16/20.

## Questions for the Director
Q1. Recovery fail-closed on disposal failure (raise, state not exposed) vs. returning the outcome with a retained-journal marker that load ignores — Uni chose fail-closed under the standing recovery law. Does that match the intended receipt semantics? (Unblocks: final wording of the recovery contract; recommended: accept fail-closed.)
Q2. Successful-landing result shape: ok=True + journal_retained field vs. a distinct journal_disposal field mirroring _fail_import details — Uni used journal_retained for symmetry with error details. (Unblocks: public-contract wording at step 11; recommended: keep journal_retained in both shapes.)
