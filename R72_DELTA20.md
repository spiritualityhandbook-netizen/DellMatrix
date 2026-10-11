# R7.2 Delta-20 — Perspective Studio (DRAFT)

**Date:** 2026-10-11
**Circuit:** R7.2 Perspective Studio
**Base:** `25386e8` (main, post R7.1 docs)
**Status:** Implementation in progress (31/31 studio proofs)

## Delta-20 Categories (Reconciled Against Executed Evidence)

### 1. Missing concept — Bounded.
The studio is a scoped REPL mode, not a new subsystem. It reuses the
existing REPL loop, the existing workshop identity ("perspective"), and
R7.1 compose_views. No new runtime concept introduced.

### 2. Contradiction — None.
Preserves R7.1 PERSPECTIVE ≠ TRUTH. The legend explicitly states that
epistemic status means verification, not accepted truth or permission.
Preserves R6.5 PERSONA ≠ PERMISSION: the studio grants nothing.

### 3. Semantic drift — Watched.
"Studio" could imply authoring accepted truth. Mitigated: the studio
only composes views (read-only); the help text and legend state this
explicitly. Mutations are rejected, not reinterpreted.

### 4. Duplicate authority — None.
No replacement compositor (delegates to compose_views), no permission
system (R6.5 owns), no dispatcher (REPL dispatch unchanged), no save
path (canonical persist_rest.save). PerspectiveStudio is a presentation
adapter only.

### 5. Wrong abstraction — Bounded.
The studio is a workshop (Phase-7 concept), not a truth or permission
system. Commands are presentation operations (compose, legend) plus
session control (help, leave).

### 6. Wrong layer — None.
Workshop/presentation layer. Does not touch Mandell core, lifecycle,
or persistence internals. Serializer/loader changes are minimal and
follow the outcome_ledger pattern.

### 7. Persistence failure — Bounded.
Uses canonical persist_rest.save with existing recovery/stale-writer
guards (check_save_allowed). Session evidence is a validated subsection
of the Program payload. Save failure retains the session and stays
visible; proven by executed control.

### 8. History/provenance — None.
All studio commands are logged in the session record with kind, time,
and bounded result summary. The workshop identity ("perspective") is
the existing one; no new provenance claim.

### 9. Security — Bounded.
Scoped command set; no new privilege. Input-derived data (compose JSON)
is screened for protected material via inference_dock utilities before
recording. Grants, authority, and credentials are never persisted.
Proven by executed controls.

### 10. Human-authority — None.
The studio cannot confirm, grant, or override. Mutations attempted in
studio mode are explicitly rejected before normal dispatch.

### 11. Offline — None.
Local-first preserved. No network dependency. Cloud perspective
explicitly deferred per directive.

### 12. Performance — Bounded.
Composition is O(viewers × modes) via R7.1. Spec parsing is bounded
(8KB JSON, 8 specs). Session records are bounded (50 commands, 10
sessions retained).

### 13. Public-path theater — Proven.
The walking skeleton uses the real REPL (`python3 -m form.repl`) with
piped commands. Composition output is field-for-field equal to a direct
compose_views call. No mocks, no stubs, no simulated paths.

### 14. Mathematical weakness — None.
The layout legend is descriptive (what fields mean), not a proof or
guarantee. No mathematical claims made.

### 15. Visual theater — Watched.
The legend is a machine-inspectable dict (keys asserted by tests), not
just display text. Proven: `legend` returns the dict; tests assert keys.

### 16. Historical-recovery — None.
R6.3 rollback untouched. The studio does not interact with the
confirmation lifecycle or rollback machinery.

### 17. Simpler reuse — None.
Reuses R7.1 compose_views directly. The studio module is the minimal
adapter; no reimplementation of composition, viewing, or dispatch.

### 18. Research contradiction — None.
Dispositions: CQRS ADAPT (query/write separation, without CQRS
machinery); pal-mvvm-foundation ADAPT; Vortex ADAPT; Babylon.js/MDN
ADAPT; Cosmos DB materialized views ADAPT; Blender View Keeper REJECT.
Sources without actual links marked UNKNOWN per directive.

### 19. Future-phase — Bounded.
Compatible with R7.3 (BIMO Forge) as a peer workshop using the same
scoped-mode pattern. R7.4 (Connected) may add cloud views later;
deferred, not blocked.

### 20. From-scratch — None.
Extends R7.1. One new module (perspective_studio.py), four REPL command
branches, one persistence subsection. No reimplementation.

---

**END OF R7.2 DELTA-20 (DRAFT)**
