# Director Reports — Index

Per-circuit certification submissions under the Director's
completion order of 2026-10-31 (section 8). One report per
closed circuit, submitted as it closes (Ace's cadence order,
2026-10-31) so rulings stay incremental. Uni is the only party
that manipulates code; these reports ask the Director to read
and rule. A report is evidence submitted, never a certificate.
Merged != certified.

Status key: SUBMITTED = awaiting ruling. Uni updates this
index when a ruling lands; the register of record is
DIRECTOR_FINDINGS_REGISTER.md (Uni workspace).

| Report | Circuit | Scope requested | Status |
|---|---|---|---|
| DIRECTOR_REPORT_STEP2_DAF09.md | Order step 2 | DAF-09 timeout process-tree kill (PR #163, merge e4b13ec) | CERTIFIED WITH NOTED EXCEPTIONS (Mode D, 2026-10-31) — narrowed to executed coverage: Linux ordinary-descendant cleanup, timeout verdict, bystander survival. Session-escape + cancellation NOT certified at that ruling; see the addendum report below. |
| DIRECTOR_REPORT_STEP3_SECURITY.md | Order step 3 | DAF-02/B5 Sanitize, DAF-03 InternetGate, DAF-10 fetch-log bound (PR #164, merge 76a390d) | PARTIALLY CERTIFIED (Mode D, 2026-10-31) — DAF-03 CERTIFIED WITH NOTED EXCEPTIONS; DAF-10 CERTIFIED; DAF-02 DECLINED as complete and REOPENED (chain-path leak). Step 3b follow-up circuit queued; its report will re-present DAF-02. |
| DIRECTOR_REPORT_STEP4_DAF01_DAF07.md | Order step 4 | DAF-01 lossless operand transport, DAF-07 parser refusal (PR #165, merge a60bb22) | CERTIFIED (Mode D, 2026-10-31) — DAF-01 WITH NOTED EXCEPTIONS (85/87/88 bounded standalone certifications; Dell 55 transport certificate only); DAF-07 CERTIFIED within tested grammar scope. |
| DIRECTOR_REPORT_STEP5_DAF04_DAF05_DAF06.md | Order step 5 | DAF-04/05/06 Exchange boundary + A1 re-presentation (PR #166, merge 4405479) | PARTIALLY CERTIFIED (Mode D, 2026-10-31) — DAF-04 CERTIFIED WITH NOTED EXCEPTIONS; DAF-05 CERTIFIED WITH NOTED EXCEPTIONS; DAF-06 DECLINED as complete (persistence failures still leave durable partial imports) and OPEN; A1 DECLINED pending the DAF-06 durability repair. Step 5b follow-up will re-present DAF-06 and A1. |
| DIRECTOR_REPORT_STEP3B_DAF02.md | Order step 3b (post-step-5 wave a) | DAF-02 re-presentation: Sanitize chain redaction carry-through (PR #168, merge 1ab1afe) | DECLINED AS COMPLETE (Mode D, 2026-10-31, at 1ab1afe) — Query disclosure repaired, but redaction sanitizes executable state in place (last_result + Revert corrupted); DAF-02 remains OPEN; step 3c forthcoming (canonical state unchanged, redact only detached evidence copies). |
| DIRECTOR_REPORT_DAF09_ADDENDUM.md | DAF-09 addendum (post-step-5 wave b) | Widened DAF-09 coverage: session-escaping descendants + cancellation (PR #170, merge f1c0205) | PARTIALLY CERTIFIED (Mode D, 2026-10-31, at f1c0205) — SIGINT CANCELLATION CERTIFIED within the tested Linux scope (cleanup + KeyboardInterrupt propagation passed both independent runs). SESSION-ESCAPE CERTIFICATION WITHHELD: the Director's independent runs returned 15/16 then 14/16 against Uni's 16/16, and the conflicting local results are unresolved. NEW GAP recorded: the tracker retains bare numeric PIDs without process-identity protection (PID-reuse could signal an unrelated process; mock-confirmed, no real bystander signalled). A bounded DAF-09 identity-safe-signalling follow-up is forthcoming (after step 3c, before step 5b); it re-presents the session-escape coverage only — cancellation is already certified and is not re-opened. |

Forthcoming, in order: step 3c (DAF-02 semantic-preservation
follow-up, third DAF-02 presentation), the DAF-09
identity-safe-signalling follow-up (re-presents the
session-escape coverage only), step 5b
(DAF-06 durability follow-up, re-presents A1), steps 6-11
per-circuit reports, step 13 sweep re-derivation, step 14
consolidated index packet (A2 reconciled closure + remaining
typed-Dell and full-registry re-rulings).
