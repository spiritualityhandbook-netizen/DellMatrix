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
| DIRECTOR_REPORT_STEP2_DAF09.md | Order step 2 | DAF-09 timeout process-tree kill (PR #163, merge e4b13ec) | CERTIFIED WITH NOTED EXCEPTIONS (Mode D, 2026-10-31) — narrowed to executed coverage: Linux ordinary-descendant cleanup, timeout verdict, bystander survival. Session-escape + cancellation NOT certified; addendum checks queued. |
| DIRECTOR_REPORT_STEP3_SECURITY.md | Order step 3 | DAF-02/B5 Sanitize, DAF-03 InternetGate, DAF-10 fetch-log bound (PR #164, merge 76a390d) | PARTIALLY CERTIFIED (Mode D, 2026-10-31) — DAF-03 CERTIFIED WITH NOTED EXCEPTIONS; DAF-10 CERTIFIED; DAF-02 DECLINED as complete and REOPENED (chain-path leak). Step 3b follow-up circuit queued; its report will re-present DAF-02. |
| DIRECTOR_REPORT_STEP4_DAF01_DAF07.md | Order step 4 | DAF-01 lossless operand transport, DAF-07 parser refusal (PR #165, merge a60bb22) | CERTIFIED (Mode D, 2026-10-31) — DAF-01 WITH NOTED EXCEPTIONS (85/87/88 bounded standalone certifications; Dell 55 transport certificate only); DAF-07 CERTIFIED within tested grammar scope. |
| DIRECTOR_REPORT_STEP5_DAF04_DAF05_DAF06.md | Order step 5 | DAF-04/05/06 Exchange boundary + A1 re-presentation (PR #166, merge 4405479) | PARTIALLY CERTIFIED (Mode D, 2026-10-31) — DAF-04 CERTIFIED WITH NOTED EXCEPTIONS; DAF-05 CERTIFIED WITH NOTED EXCEPTIONS; DAF-06 DECLINED as complete (persistence failures still leave durable partial imports) and OPEN; A1 DECLINED pending the DAF-06 durability repair. Step 5b follow-up will re-present DAF-06 and A1. |

Forthcoming, in order: step 3b (Sanitize chain redaction,
re-presents DAF-02), DAF-09 coverage addendum, step 5b
(DAF-06 durability follow-up, re-presents A1), steps 6-11
per-circuit reports, step 13 sweep re-derivation, step 14
consolidated index packet (A2 reconciled closure + remaining
typed-Dell and full-registry re-rulings).
