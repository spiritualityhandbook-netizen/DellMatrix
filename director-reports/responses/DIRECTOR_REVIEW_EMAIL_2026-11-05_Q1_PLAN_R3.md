# Director Review Email — 2026-11-05 05:44 CST (Q1 Amendment B review)

Source: Gmail id 1a1ab862b9532954, from Acetoocold
<acetoocold24@gmail.com>, received 2026-11-05 05:44 CST.
Subject: "[DellMatrix Director Review] Q1 2bf7d9a4
TARGETED_CORRECTION_REQUIRED". Archived verbatim by Uni
during SUSX100,000 Cycle 24.

> DIRECTOR → UNI | Q1 AMENDMENT B REVIEW | 2026-11-05
>
> PR: https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/294
>
> Plan: https://github.com/spiritualityhandbook-netizen/DellMatrix/blob/2bf7d9a4405e36bb20bd6a302ddf10b74876f1e6/director-reports/DIRECTOR_Q1_REPAIR_PLAN.md
>
> Exact PR head: 2bf7d9a4405e36bb20bd6a302ddf10b74876f1e6
>
> VERDICT: TARGETED_CORRECTION_REQUIRED — PLAN ONLY; HOLD IMPLEMENTATION AND MERGE.
>
> VERIFIED: bounded PR diff is documentation/evidence, not product-code repair. GitHub exact-head smoke, build 3.10 and build 3.11 all terminal SUCCESS (3/3). Amendment B now explicitly withdraws the unjustified no-journal pair-coherence claim, proposes lock-light validation, specifies adversarial two-process probes P5-A/B/C, and anchors journal disposal to a trusted under-lock snapshot with pid=None cases. These are design specifications, not executed repairs.
>
> FINDING: P5-C-i assumes a canonical program save followed by Nursery.save is one lock-held pair transaction. Source form/persist_rest.py save() holds owner_state_lock only during _write_program_file; form/dell_matrix/nursery.py save() performs a separate direct write without that lock. Therefore the proposed P5-R validation can observe the intermediate program-new/nursery-old pair after the first save's lock releases and wrongly classify it as coherent. A fingerprint check establishes stability at one instant, not transaction-level coherence when the writers have no common transaction. This contradicts the B2 P5-C-i PASS rationale and the P5-R proof's in-scope-writer assumption. The unlocked Nursery.save case also cannot be guaranteed detected if its write completed before the initial fingerprints; equality of fingerprints at validation cannot prove semantic pair coherence.
>
> UNI NEXT ACTION: amend the writer taxonomy and P5-R guarantee; either serialize the complete logical program+nursery operation under one shared transaction/intent, or explicitly exclude such two-step updates and narrow the load contract to per-file consistency. Add a deterministic two-process counterexample that pauses AFTER persist_rest.save releases its lock and BEFORE Nursery.save, then loads and asserts the actual result; separately test an unlocked Nursery.save completed before fingerprint capture. Do not call these cases protected by the shared lock. Retain P3 journal identity/no_target requirements. Re-present one frozen plan head with the precise proposed contract; no implementation or merge authorization.
>
> No independent adversarial probe was executed in this review. CI is not certification.
