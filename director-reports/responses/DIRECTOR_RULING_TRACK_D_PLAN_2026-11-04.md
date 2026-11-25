# DIRECTOR RULING — Track D Plane-to-Idea Bridge Plan (PR #261)

Director morning review, 2026-11-04 · Mode D — retrospective verification and certification
Reviewed head: `7f8d1af` · Planning baseline: `2740c22`
Independent evidence integrity: 6/6 SHA-256 matches · Submitted integration probe: 16/16 passed

## Disposition

**PLANNING ACCEPTED WITH AMENDMENTS.**

The architectural direction is accepted: existing Plane units should connect
to canonical Ideas, while SemanticGraph remains the sole authority for
containment.

## The nine decisions

| Question | Director decision |
|---|---|
| TD1 — Binding strategy | Approve S1: additive Unit→Idea pointer and fresh canonical UUID |
| TD2 — Mint timing | Approve lazy binding on explicit authorized bridge actions |
| TD3 — Shell content | Approve title and provenance only; no duplicated Plane content |
| TD4 — Lifecycle | Preserve historical edges; ordinary mutations refuse inactive, malformed or unreadable Ideas |
| TD5 — Missing binding | Refuse and report missing or corrupt targets; no automatic rebind |
| TD6 — Exchange | Exclude containment transfer from v1 |
| TD7 — Sandbox | Refuse containment across sandbox isolation boundaries |
| TD8 — First interface | REPL first; Studio after its Growth payload correction |
| TD9 — Bulk binding | Declined for v1; no automatic mass migration |

## Required amendments

The implementation must address three material boundaries before it can be
considered complete.

1. **A valid pointer requires a valid Idea.** `idea_exists()` checks whether
   a file exists; it does not establish that the stored Idea is readable or
   structurally valid. Use validated loading, and fail closed on corruption.
2. **Failed saves must not leave false in-memory success.** If an Idea is
   minted but the Program save fails, the Unit must not be reported as
   durably bound. The implementation needs rollback or an explicit
   recoverable pending state.
3. **Competing instances must not silently overwrite bindings.** Multiple
   Program instances for the same owner need a tested conflict/refusal rule
   or an enforceable single-writer boundary.

Additional requirements: represent the real invoking subject in provenance,
prevalidate predictable containment failures, and disclose any partial
binding left after a later graph failure. Do not claim cross-file atomicity
that has not been established.

## Authorization

**TD-1 binding foundation is approved as a bounded implementation circuit.**
TD-2 through TD-5 are not yet implementation-certified or authorized by this
ruling.

PR #261 has an older base and needs reconciliation with current main before
its documentation can merge. Re-run applicable CI at the final revised head.

## Provenance

The Director attempted to publish this ruling as a GitHub PR review; the
GitHub integration returned 403 — Resource not accessible by integration. No
repository review or ruling file was created by the Director. This file is
Uni's archival transcription of the ruling as delivered through Ace on
2026-11-04.
