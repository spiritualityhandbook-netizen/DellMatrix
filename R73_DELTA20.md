# R7.3 Delta-20 — General Workshop Contract

**Date:** 2026-10-16
**Circuit:** R7.3 General Workshop Contract (Phase 7, draft objectives
7.1.1–7.1.3, 7.1.5; 7.1.4 disclosure onboarding NOT in scope)
**Base:** `8338c297e1614e16afe74035a7c560e5fcb517d7` (main, R7.2 merged)
**Status:** Candidate ready for review (NOT CERTIFIED — DO NOT MERGE)

Category names and numbering are the established Delta-20 set
(as in R64_DELTA20.md). No category renamed or renumbered.

## Delta-20 Categories

### 1. Missing workflow — Bounded.
Before: entering a workshop changed nothing; there was no scoped
workflow. Now: `workshop <id>` → scoped session (prompt, scoped
commands, recorded evidence) → `leave` persists and exits. All seven
registry workshops execute the workflow (71-check suite, part 2).

### 2. Contradictory records — Bounded.
The persisted `active_workshop` flag and session evidence could
disagree: leave clears the flag BEFORE the canonical save (restored on
failure), so durable state never claims an active workshop alongside a
closed record. Verified in suite (reload checks) and manual smoke.

### 3. Semantic drift — Bounded.
"Workshop" previously meant a printed menu. It now means the registry
definition PLUS the scoped contract, and the scope set is derived from
that same registry entry at runtime — the menu the user sees and the
gate that enforces are one source, so they cannot drift apart.

### 4. Duplicate authority — Avoided.
No second workshop registry, dispatcher, or persistence store. Scope
derives from `workshops.py`; dispatch is `_dispatch_public_line`;
persistence is a new section in the canonical save/load; screening
reuses the R6.2 utilities through the existing REPL helper. The studio
(R7.2) remains a separate specialized environment by design, with a
one-scoped-environment-at-a-time rule rather than a merged gate.

### 5. Identity/permission conflation — Bounded.
The workshop grants nothing: in-scope lines route through the same
dispatcher with a fresh interaction id; no authority is minted,
inherited, or widened by being inside a workshop. Session records bind
to the Program owner under the strict schema (foreign-owner records
are malformed evidence, never restored).

### 6. Unmediated execution layer — Closed for this surface.
Every line typed while a workshop session is open passes the gate
before dispatch — including say-prefixed lines and staged reissues,
which the gate's position (ahead of those handlers) makes unreachable
inside. Proven behaviorally (suite part 1).

### 7. Persistence inconsistency — Bounded.
`workshop_sessions` follows the identical strict-schema pattern as
`studio_sessions`: sentinel absence vs explicit null, version strict,
key/ID agreement, closed-only, malformed preserved and accumulated,
serializer shares the schema. Same contract, second instance — the
pattern is now the established section law.

### 8. Lost history — Bounded, honestly.
Evidence is a retained window (50 commands/session, 10 sessions),
enforced during recording. Rejected and protected attempts are
recorded with safe codes. Beyond the window is unavailable and is
documented as such, not claimed as complete history.

### 9. False provenance — Bounded.
Records contain only stems, fixed result codes, timestamps, owner, and
workshop id — each produced by the gate at the moment of the line.
Nothing is reconstructed after the fact; a dispatched stem claims
routing, not command success.

### 10. Credential/subject escape — Bounded.
Input is screened (fail-closed) before scope decision, dispatch, or
recording; only stems and codes are recorded, never raw lines. The
real-grant proof shows the handle absent from REPL output AND from
persisted bytes.

### 11. Human-authority bypass — Not introduced.
The contract changes command scoping, not authority. Mutations inside
run only if the same dispatcher would run them outside; confirm/grant
class commands are out of scope in every workshop's registry menu and
are rejected at the gate.

### 12. Offline dependency — None.
Pure local REPL/persistence work; no network, no external service.

### 13. Measured performance regression — Not observed.
Full regression module time is dominated by the existing suite; the
R7.3 module adds ~6s locally. No production hot path changed except
one gate check per interactive line.

### 14. Public-path theater — Avoided.
The contract is enforced in the real REPL main loop (the literal user
path), and the majority of proofs run through real REPL subprocesses,
not private handler calls. The one in-process proof (blocked save)
uses the production attribute and the real guard, following the R7.2
precedent.

### 15. Vacuous/count/statistical claims — Guarded.
Every check asserts an observable: prompt strings, dispatcher output,
unit counts in durable state (inside/outside differential), persisted
record contents, byte-level absence of the grant handle. The harness
contract failure found during this circuit (missing `smoke()` entry)
was a real RED, fixed and re-verified — evidence the suite can fail.

### 16. Misleading display — Bounded.
The scoped prompt names the active workshop; help inside lists exactly
the commands the gate will accept (same registry source); EOF/quit
state plainly that the session was NOT saved.

### 17. Recovery/replay failure — Bounded.
Stage-then-save leave mirrors the studio: failure restores prior
records AND the active flag, retains the session, and retry produces
exactly one closed record (proven with a genuinely recovery-required
instance, guard not mocked).

### 18. Unnecessary architecture — Avoided.
One new module (session evidence + section schema, mirroring the
established studio pattern), one gate + handler in the REPL, one
section in each persistence direction. No new registry, router,
selector, or store.

### 19. Research-to-code mismatch — Not applicable.
No external research claims are made for this circuit; the design
follows the GDP draft objectives and the in-repo R7.2 precedent.

### 20. Independent-model disagreement — UNKNOWN.
No independent review has run on this circuit yet. The R7.2 candidate
was strengthened by two external AMEND rounds; this candidate has had
only Uni's own adversarial suite. Reviewer findings may reopen any
category above; this map records Uni's dispositions, not a ruling.
