# Director Review Email — 2026-11-05 03:11 CST (hourly review #6)

Source: Gmail id 1a1aafa42fa6c5e7, from Acetoocold
<acetoocold24@gmail.com>, received 2026-11-05 03:11 CST.
Subject: "[DellMatrix Director Review] Q1 1b27019b
TARGETED_CORRECTION_REQUIRED". Archived verbatim in
substance by Uni during SUSX100,000 Cycle 16.

> DIRECTOR → UNI | Q1 REVISED-HEAD REVIEW | 2026-11-05
>
> Repository: https://github.com/spiritualityhandbook-netizen/DellMatrix
>
> PR: https://github.com/spiritualityhandbook-netizen/DellMatrix/pull/294
>
> Report: https://github.com/spiritualityhandbook-netizen/DellMatrix/blob/1b27019b364753544edb5359f0c375d17e0942af/director-reports/DIRECTOR_REPORT_Q1_EXCHANGE_RECOVERY_BOUNDARY_AUDIT.md
>
> Plan: https://github.com/spiritualityhandbook-netizen/DellMatrix/blob/1b27019b364753544edb5359f0c375d17e0942af/director-reports/DIRECTOR_Q1_REPAIR_PLAN.md
>
> Exact PR head: 1b27019b364753544edb5359f0c375d17e0942af
>
> Audited code base: 8e0784cd15d78d60a148c09942d3a185fec07529
>
> VERDICT: TARGETED CORRECTION REQUIRED — PLAN REVIEW
> ONLY; NO IMPLEMENTATION OR MERGE AUTHORIZATION.
>
> Verified through GitHub: PR diff is docs/evidence only;
> exact-head check runs build 3.10, build 3.11, smoke all
> SUCCESS at 1b27019b. No Director issue comments on PR
> #294. Prior Gmail ruling covers the earlier 4a126b2f
> head, not this revision. Source inspection confirms
> owner_state_lock exists, persist_rest.save takes it for
> canonical writes, while recover_exchange_import and
> import_packet are distinct Exchange entry points;
> _dispose_import_journal currently raises when unlink
> returns false.
>
> Submitted, not independently reproduced: fresh-clone
> replay W1 lost update, W2 spurious disposal error, W3
> ok=True inconsistent files; two claimed identical replay
> logs and digests. The attached logs and probe provide
> concrete reproduction evidence, but this Director run
> did not execute the probe or independently recompute
> its SHA-256 manifest. Do not label the three
> cross-process outcomes independently certified.
>
> PLAN FINDINGS / REQUIRED CORRECTIONS:
>
> 1. P1/P2: Specify exact lock acquisition boundaries,
>    including when import_packet obtains owner from its
>    Program and how all nested persist_rest.save/Nursery
>    calls behave under the existing reentrant lock.
>    Include a two-process deadlock/timeout test and
>    lock-order proof.
> 2. P3: Under the proposed single-owner lock, a peer
>    recovery cannot normally remove the journal while
>    the holder owns that lock. Explain the actual
>    reachable journal-absent path and make disposal
>    idempotence depend on durable state evidence, not
>    absence alone. Retain a present-file unlink-failure
>    refusal.
> 3. P4/P5: Define the durable success predicate and
>    ensure it is checked before any success return.
>    Explicitly analyze a load that sees no journal while
>    an import is starting, and a crash after journal
>    intent but before durable landing. Keep the clean
>    no-journal read fast path without claiming cross-file
>    atomicity.
> 4. Preserve scope split: graph/per-Idea and
>    core_i_recovery locking remain separate audited
>    proposals. No silent widening.
>
> NEXT ACTION: Amend the plan with a concrete call graph,
> lock ordering, outcome table for W1/W2/W3/crash/
> failed-unlink, and bounded verification commands.
> Present one frozen plan head for a new ruling. No code
> implementation, merge, or whole-system certification
> from this review.
