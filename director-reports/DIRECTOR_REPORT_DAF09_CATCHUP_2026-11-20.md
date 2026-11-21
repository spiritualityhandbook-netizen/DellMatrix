# DIRECTOR REPORT — DAF-09 CATCH-UP (G-09 / register row #116)

**From:** Uni. **Date:** 2026-11-20. **Nature:** catch-up report
owed per the 2026-10-31 reporting cadence (register row #116,
G-09). **This report carries no verdict** — it requests none and
gives none. It discharges a reporting debt; it does not move the
DAF-09 evidence state, which is owned by register row #21
(Part III).

## 1. What DAF-09 is

DAF-09 is the session-escape process-cleanup discrepancy: a
cancellation/cleanup path where the observed process-cleanup
behavior in the Director's independent environment did not match
the behavior Uni's local evidence showed. The discrepancy — not
any single run — is the open item.

## 2. The standing evidence state (unchanged by this report)

- The Director's **independent reproduction stands at 19/22**
  (register row #21: "the Director's independent 19/22 stands;
  local greens do not resolve it, section 31.3"). That reading is
  the governing evidence state.
- Uni's local greens on the surrounding suites are on record and,
  per section 31.3, **do not resolve** the discrepancy. They are
  not re-argued here.
- The certification runner explicitly **does not execute the
  DAF-09 session-escape scope** (`DIRECTOR_NOTE_CERTIFICATION_RUNNER.md`),
  so no runner output bears on this item either way.
- Consequence standing since the discrepancy opened:
  **whole-program certification remains WITHHELD.** Nothing in
  this report changes that.

## 3. Uni-side work since 2026-10-31 (labeled as Uni-side)

Uni-side investigation artifacts exist in the goal workspace
records: pidfd hardening probes and ground notes, an identity
mapping and its re-verification (2026-10-31 / 2026-11-01), and
fresh-clone regression legs for the addendum. These are recorded
as Uni-side work product. They narrowed the mechanism space; they
did not produce an independent reproduction, and under section
31.3 they cannot close the item. The background-launch signal-
inheritance defect found during this work (a backgrounded chain
inheriting SIGINT=SIG_IGN, silently disabling cancellation in
descendants) is a real, separately-recorded mechanism lesson; it
explains a class of local non-reproductions and is **not**
presented as a resolution of the Director's 19/22.

## 4. What closes DAF-09

Exactly one thing: the Director's independent reproduction
reaching a terminal disposition (register row #21, Part III) —
either the discrepancy reproduces under agreed conditions and is
diagnosed, or it fails to reproduce under the Director's own
protocol across the agreed run count. Uni's obligations toward
that act are support obligations: provide the frozen sources,
probes, and environment notes on request, and run nothing that
presents local evidence as a substitute.

## 5. Reporting-cadence note

This catch-up was owed from 2026-10-31 and is filed 2026-11-20
inside Part 0's PR, where row #116 is assigned. The lateness is
Uni's. Part VII's execution-order work carries the standing
cadence so the next catch-up is produced by the schedule, not by
archaeology.
