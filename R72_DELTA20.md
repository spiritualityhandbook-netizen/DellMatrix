# R7.2 Delta-20 — Perspective Studio (FINISH-BOUNDARIES CIRCUIT)

**Date:** 2026-10-15
**Circuit:** GDP_R72_FINISH_EXISTING_BOUNDARIES_AND_EXECUTABLE_EVIDENCE (MODE=C)
**Start:** `e77806b7fa39ef86216249a4fa28ab70579306e4` (PR #87)
**Base:** `25386e8daaa8936ac821b9ee4fd5b2271bf1397e` (main)
**Status:** Candidate ready for Director review (NOT CERTIFIED — DO NOT MERGE)

Category names and numbering are the established Delta-20 set
(as in R64_DELTA20.md). No category renamed or renumbered.

## Finding dispositions (second AMEND)

1. **Persistence still loses evidence** — FIXED. Loader uses the
   `_MISSING` sentinel: absent key is legacy; explicit null is malformed.
   `serialize_section` shares the strict schema with restoration; active,
   foreign-owner, and key/ID-mismatched records are preserved as malformed,
   never silently saved as valid or discarded. Same-key malformed failures
   accumulate as lists; earlier evidence is never overwritten.
2. **Protection is REPL-input-only** — FIXED. `PerspectiveStudio.compose`
   screens structured input before composition and detached output before
   release via the shared `_screen_protected` helper (R6.2 utilities).
   Canonical Idea content is never modified to sanitize a view.
3. **Validation escapes its boundary** — FIXED. compose() enforces the
   container contract (list, non-empty, eight-spec limit, aggregate
   bounds) and catches numeric conversion/overflow failures, returning
   fixed bounded rejection codes. The REPL remains usable afterward.
4. **Advertised proofs absent** — REPLACED. Real authority-bound rollback
   executed to a sealed checkpoint; genuinely recovery-required and stale
   instances created via production attributes (no guard mock);
   protection sensitivity demonstrates actual canary disclosure under
   weakened protection and rejection after restore; gate-order checks
   target the main dispatch gate (last of three studio branches), backed
   by behavioral REPL proofs.

## Delta-20 Categories

### 1. Missing workflow — Bounded.
The studio completes the Phase-7 workshop workflow: enter → compose →
inspect observations → legend/help → rejected mutation → failed leave →
continued use → successful retry → fresh-process reload. The full journey
is executed as one real-REPL proof, not asserted piecemeal.

### 2. Contradictory records — None.
One shared strict schema (`validate_section` / `serialize_section`)
governs both directions of persistence; serializer and loader cannot
disagree about what a valid record is. Malformed evidence is preserved
in both directions under the same rules.

### 3. Semantic drift — Bounded.
"Studio" could imply authoring accepted truth. Mitigated: the studio
only composes views (read-only, PERSPECTIVE ≠ TRUTH preserved); the
scoped `studio> ` prompt and help text state the boundary explicitly.
Mutations are rejected, never reinterpreted.

### 4. Duplicate authority — None.
No new compositor (delegates to R7.1 `compose_views`), no permission
model (R6.5 owns), no dispatcher (REPL dispatch unchanged), no save
path (canonical `persist_rest.save`), no persistence store (existing
Program payload section; no sidecar).

### 5. Identity/permission conflation — None.
PERSONA ≠ PERMISSION preserved. The studio grants nothing; owner binding
is enforced on compose (spec owner must match Program owner) and on
restoration (records bound to the loading Program's owner).

### 6. Unmediated execution layer — None.
While the studio is active, every non-exit input passes the scoped
handler before normal dispatch; the gate precedes reissue and the
say-prefix handler. Proven behaviorally with genuinely pending targets
(exact pending status, Plane absence, unchanged canonical content).

### 7. Persistence inconsistency — Bounded.
Section is versioned (int 1; bool rejected, no coercion) and included in
DURABLE_KEYS. Absent vs explicit null distinguished by sentinel.
Malformed sections, carriers, and multiple same-key failures preserved
through load → save → fresh-process reload. Active records are never
persisted as valid.

### 8. Lost history — None.
Malformed evidence accumulates without overwriting earlier entries;
session retention (10 closed sessions, 50 commands) is explicit in help
text and enforced during recording, not only at serialization.

### 9. False provenance — Bounded.
Compose displays actual attributed observations from `compose_views`
(viewer/mode/status/source report lines), field-for-field equal to a
direct compositor call. No invented counts; disagreement is not merged
into truth.

### 10. Credential/subject escape — Bounded.
Fail-closed protection on every public entrypoint (REPL raw input,
decoded specs, direct compose input, detached compose output). Fixed
bounded failure codes; no reflected input, unknown keys, or exception
text. Protected canaries in keys, values, and escaped JSON show zero
disclosure in responses and persisted evidence. Sensitivity: weakened
screening discloses the canary; restored screening rejects.

### 11. Human-authority bypass — None.
EOF/quit in studio mode never claim persistence; leave persists only via
the canonical save after staging. Stale-writer and recovery-required
guards are reused, never bypassed; genuinely blocked instances reject
leave with durable bytes unchanged and the session retained for retry.

### 12. Offline dependency — None.
No networking, no cloud perspective (explicitly deferred), no external
service introduced.

### 13. Measured performance regression — None observed.
Full canonical regression (--twice and --order rev) green at the same
suite size as the start candidate plus the expanded R7.2 suite.

### 14. Public-path theater — None.
Proofs execute the real REPL (subprocess, piped input), the public
compose() API, canonical save/load, and authority-bound rollback —
not private stand-ins. A new Program in one process is never called
cross-process; fresh-process reload is a separate OS process.

### 15. Vacuous/count/statistical claims — None.
No unconditional verdicts or permissive alternatives remain. Checks that
previously could not distinguish success from the defect (static
gate-order search matching the EOF branch; INVALID_SPEC accepted as
sensitivity proof; already-confirmed mutation targets) were replaced
with checks that fail on the demonstrated defect.

### 16. Misleading display — Bounded.
The prompt shows the scoped mode (`studio> `). Composition output shows
observations, not component metadata. The legend's keys are validated
against the fields actually displayed.

### 17. Recovery/replay failure — Bounded.
Real rollback to a sealed checkpoint containing studio evidence restores
exactly the checkpoint records after distinguishable live evidence was
created; fresh-process reload compares the exact expected records.
Failed leave restores prior in-memory records and retries coherently
(exactly one closed record).

### 18. Unnecessary architecture — None.
Repairs extend existing mechanisms only: the REPL loop, R7.1 compositor,
R6.2 protection utilities, canonical persistence. No second router,
selector, ledger, store, compositor, permission system, or dispatcher.

### 19. Research-to-code mismatch — Bounded.
Central enforcement on every request and exclusion of sensitive input
from logs (Director's research note) are implemented through the
existing coordinator and protection utilities. External dispositions
from the first circuit are retained (CQRS ADAPT, materialized views
ADAPT, Blender View Keeper REJECT); unlinked sources remain UNKNOWN.

### 20. Independent-model disagreement — Bounded.
Director probes and Uni proofs now exercise the same boundaries with
the same expectations (sentinel absence, shared schema, public-path
protection, executed rollback). Remaining uncertainty: code scanning is
EVALUATION_UNAVAILABLE (Copilot quota 402), stated separately and never
as PASS; certification scope is the R7.2 studio circuit only.
