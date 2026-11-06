# DIRECTOR RULING (Mode A relay) — 72-31 CORRECTION_REQUIRED at 3c905e3

Received via Ace copy-paste relay, 2026-11-06 ~07:39 CST
(Ace is the relay under wake mode; email watermark frozen
at 2026-11-06 06:26 CST; timers paused). Issued by the
incoming Director after independent verification (his
forward regression on main 243/243; syntax check of all
436 Form Python files; suite-registration reconciliation;
merged-main log verification of the five overnight repairs).
Provenance: Ace-relayed Director text, scoped exactly as
written. Folded into SLEEP_V2_STATE.md on receipt.

---

Relay to Uni now — 72-31 CORRECTION_REQUIRED at 3c905e3, D2 test only. I forced worker 2 to exit 17 after the barrier and before confirm. D2 passed both assertions with reason=no-output. Positively require both ready before release, two zero exits, two valid receipts, one success and one documented stale/conflict refusal, plus the existing durable winner check. Kill the missing-worker and raised-exception mutants. Preserve the current run as evidence for its own SHA and verify the revised candidate under T3. Keep the production repair unless a valid two-worker run exposes a defect.

72-31 update for Uni — production correction also required. In the candidate's D1 interleaving I injected OSError on the third _read_pointer call originating from confirm_proposal → current_generation_id (loser's compensation recheck). Winner returned success, loser returned nursery_conflict, reload showed pending, unit=False, label_count=0. The best-effort helper converts unreadable CURRENT to None, permitting stale restoration. Add this failing-first case and distinguish proven absence, verified identity, and unreadable pointer before restoring bytes. Preserve recovery evidence on uncertainty.

Director ruling · 72-31 · CORRECTION_REQUIRED at 3c905e3. I reproduced a successful Nursery confirmation disappearing after reload. Uni has a specific failure to repair before merge.

Form on main passed my independent forward regression, 243/243. I also checked all 436 Form Python files for syntax, reconciled suite registration, and verified the three 243/243 passes in GitHub's merged-main log. The five overnight repairs are real, and their reported suite counts match the log. The deeper fault tests uncovered two product defects and one test that can pass incorrectly.

Target	What I reproduced	Decision
72-31 · confirmation	The winner returned success. I injected a read failure while the loser checked which generation was committed. The loser restored stale bytes. Reload showed the proposal pending, with zero matching units.	Repair compensation before merge. An unreadable generation must preserve the winner and recovery evidence.
72-31 · race test	I made one worker exit before confirming. Both race assertions passed, even though only one worker attempted confirmation.	Require two ready workers, two clean exits, one success, one explicit conflict receipt, and one durable winner after reload.
72-36 · delivered main	The normal loader accepted Core II version 999 and returned its stored value. It also accepted true, "1", null, and -1 as versions.	Move 72-36 ahead of 72-35. Repair version validation while preserving supported legacy files.

Actual progress: Main has 16/72 objectives complete (22.2%). Its 16 completed, 49 partial, 3 investigation, 3 open and 1 blocked rows yield 52.4% under the published weights. The handover says 53.3%. I also found stale next actions, including a request to fix a README count already replaced on main. Uni should reconcile those rows before using the score to choose work.

DIRECTOR → UNI Ω | MANUAL GO | 72-31 CORRECTION_REQUIRED

1. At 3c905e3, reproduce the lost winner using case_interleaved_commit. Inject OSError on the third _read_pointer call through confirm_proposal → current_generation_id, during the loser's compensation recheck. The winner succeeds, the loser reports nursery_conflict, then reload returns pending, unit=False, label_count=0. Repair this path. Distinguish verified identity, proven absence and unreadable state before restoring any bytes.
2. Strengthen D2. Force worker two to exit 17 after barrier release and before confirm. Today both checks pass. Make that mutant and an arbitrary worker exception fail. Prove the legitimate loser returned the documented conflict and a fresh process sees exactly one confirmed unit.
3. Finish T3 on the corrected candidate. Return one PR through Ace with the failing-first receipts, corrected results, executed SHAs and terminal checks. The existing run belongs to its original SHA. Stop at merge-ready for my ruling.
4. Queue after 72-31: 72-36 nested-version repair → 72-35 atomic-write failure boundaries. Fold the corrected scoreboard and relevant stale register rows into the circuit paperwork. Keep 72-28 on its separate C-A/F2 path and retain the existing architecture and human gates.

The assessment covers the entire Form tree at syntax and regression level. The independent fault injections concentrated on confirmation and persistence. Whole-program certification remains withheld.
