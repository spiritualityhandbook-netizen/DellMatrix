# R7.2 Delta-20 — Perspective Studio (REPAIR CIRCUIT)

**Date:** 2026-10-11 (AMEND repair)
**Circuit:** R7.2 Perspective Studio — Close Scope, Evidence, and Failure Circuit
**Base:** `25386e8` (main, post R7.1 docs)
**Status:** Repair in progress

## Director Findings (all addressed)

1. **Scope bypass**: reissue handled before studio gate → FIXED (gate first)
2. **Protection fail-open**: screening exception suppressed → FIXED (fail-closed)
3. **Incomplete persistence**: no version, malformed not preserved, DURABLE_KEYS missing → FIXED
4. **Failed save left closed session**: close-before-save → FIXED (stage-then-save)
5. **Overstated logging**: unbounded commands, unrecorded rejections, metadata display → FIXED
6. **Weak proofs**: or-True, vacuous checks → REPLACED (74 effective checks)

## Delta-20 Categories (Reconciled Against Executed Evidence)

### 1. Missing concept — Bounded.
The studio is a scoped REPL mode, not a new subsystem. It reuses the
existing REPL loop and R7.1 compose_views. No new runtime concept introduced.
The AMEND repair did not add concepts; it closed the existing scope.

### 2. Contradiction — None.
Preserves R7.1 PERSPECTIVE ≠ TRUTH. The legend explicitly states that
epistemic status means verification, not accepted truth or permission.
Preserves R6.5 PERSONA ≠ PERMISSION: the studio grants nothing.
The scope fix strengthens this: mutations cannot bypass via reissue.

### 3. Semantic drift — Watched.
"Studio" could imply authoring accepted truth. Mitigated: the studio
only composes views (read-only); the help text and legend state this
explicitly. Mutations are rejected, not reinterpreted. The repair adds
a scoped prompt (`studio> `) to reinforce the mode boundary.

### 4. Duplicate authority — None.
No replacement compositor (delegates to compose_views), no permission
system (R6.5 owns), no dispatcher (REPL dispatch unchanged), no save
path (canonical persist_rest.save). PerspectiveStudio is a presentation
adapter only. The repair did not add authorities.

### 5. Wrong abstraction — Bounded.
The studio is a workshop (Phase-7 concept), not a truth or permission
system. Commands are presentation operations (compose, legend) plus
session control (help, leave).

### 6. Wrong layer — None.
Workshop/presentation layer. Does not touch Mandell core, lifecycle,
or persistence internals. Serializer/loader changes are minimal and
follow the strict schema pattern. DURABLE_KEYS now includes the section.

### 7. Persistence failure — Bounded.
Uses canonical persist_rest.save with existing recovery/stale-writer
guards (check_save_allowed). Session evidence is a versioned subsection
of the Program payload with strict validation. Malformed evidence is
preserved through save/reload. Save failure restores prior records and
retains an active session; proven by executed controls. Checkpoint and
rollback preserve the studio evidence contract.

### 8. History/provenance — None.
All studio commands (including rejected attempts) are logged in the
session record with kind, time, and safe result code. Bounds are enforced
during recording (50 commands, 10 sessions); retention is documented,
not claimed as complete.

### 9. Security — Bounded.
Scoped command set; no new privilege. Input-derived data (compose JSON)
is screened for protected material via R6.2 inference_dock utilities
before reflection or recording. Screening covers raw text, decoded
escapes, and structured keys/values. Fail-closed: screening failure
rejects. Fixed bounded failure codes; raw input never reflected.
Grants, authority, and credentials are never persisted. Proven by
executed controls including sensitivity (weakened protection exposes).

### 10. Human-authority — None.
The studio cannot confirm, grant, or override. Mutations attempted in
studio mode are explicitly rejected before normal dispatch. The reissue
bypass is closed: staged reissues cannot execute inside the studio.

### 11. Offline — None.
Local-first preserved. No network dependency. Cloud perspective
explicitly deferred per directive.

### 12. Performance — Bounded.
Composition is O(viewers × modes) via R7.1. Spec parsing is bounded
(8KB JSON, 8 specs). Session records are bounded (50 commands enforced
during recording, 10 sessions retained).

### 13. Public-path theater — Proven.
The walking skeleton and scope proofs use the real REPL
(`python3 -m form.repl`) with piped commands. Composition output is
field-for-field equal to a direct compose_views call. The full user
journey (enter → compose → legend/help → rejected mutation → failed
leave → retry → reload) is executed. No mocks for the routing proofs.

### 14. Mathematical weakness — None.
The layout legend is descriptive (what fields mean), not a proof or
guarantee. No mathematical claims made. Legend keys validated against
displayed fields.

### 15. Visual theater — Watched.
The legend is a machine-inspectable dict (keys asserted by tests).
Compose displays actual attributed observations (report lines with
viewer/mode/status/source), not just metadata. Proven by journey test.

### 16. Historical-recovery — None.
R6.3 rollback untouched. The studio does not interact with the
confirmation lifecycle or rollback machinery. Checkpoint/rollback
preservation of studio evidence is proven.

### 17. Simpler reuse — None.
Reuses R7.1 compose_views directly and R6.2 protection utilities.
The studio module is the minimal adapter; no reimplementation of
composition, viewing, dispatch, or protection.

### 18. Research contradiction — None.
Dispositions: CQRS ADAPT (query/write separation, without CQRS
machinery); pal-mvvm-foundation ADAPT; Vortex ADAPT; Babylon.js/MDN
ADAPT; Cosmos DB materialized views ADAPT; Blender View Keeper REJECT.
Director's repair note: research supports central enforcement on every
request and excluding sensitive input from logs — implemented via the
existing coordinator and protection utilities, no new subsystem.
Sources without actual links marked UNKNOWN per directive.

### 19. Future-phase — Bounded.
Compatible with R7.3 (BIMO Forge) as a peer workshop using the same
scoped-mode pattern. R7.4 (Connected) may add cloud views later;
deferred, not blocked.

### 20. From-scratch — None.
Extends R7.1. One module (perspective_studio.py), REPL command branches,
one persistence subsection. No reimplementation. The AMEND repair
modified existing code; it did not add subsystems.

---

**Remaining uncertainty:**
- Scanning: EVALUATION_UNAVAILABLE (Copilot quota 402).
- The `say ` prefix inside studio is rejected as out-of-scope (not stripped).
  This is intentional per "all inputs pass through the scoped handler."
- Workshop identity ("perspective") is used for attribution only; the
  Program-level workshop is not activated. This matches the authorized scope.

**END OF R7.2 DELTA-20 (REPAIR)**
