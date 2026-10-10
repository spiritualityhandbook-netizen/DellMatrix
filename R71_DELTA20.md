# R7.1 Delta-20 — Read-Only Perspective Composition (AMEND)

**Date:** 2026-10-09
**Circuit:** R7.1 (first Phase-7 implementation circuit)
**Base:** `efd68bf` (R6.5 production)
**Status:** AMEND findings addressed

## AMEND Findings (Addressed)

1. **Container validation:** `None`, `False`, `0`, `""`, `{}` now explicitly reject
   (UNSUPPORTED), not silent empty success. Only valid empty list/tuple → empty request.

2. **Failure boundary:** Dispatch, validation, detachment (deepcopy), and report
   construction all inside bounded failure handling. No exception text reflected.
   Copying failures (custom `__deepcopy__`) produce UNAVAILABLE, not crashes.

3. **Real confirmed Ideas:** Fixtures use coordinator + grants to confirm Ideas;
   assert receipts, confirmed status, exact Plane presence.

4. **No unconditional verdicts:** Removed `or True`; swept suite.

5. **Fresh-process restart:** Fixed-script OS process reloads production state,
   recreates identical specs, compares against pre-captured expected.

6. **Exact aggregation:** Asserts specific outcomes, not permissive "any status".

7. **Detachment:** Mutates actual nested observations (vision, report); verifies
   canonical Plane units unchanged.

8. **State:** Captures proposal count, Plane count, statuses, and unit IDs.

## Research Dispositions (Preserved)

- **CQRS view composition** (Fowler): ADAPT — composition is query-side only
- **pal-mvvm-foundation composite**: ADAPT — pure function, fail loudly
- **Vortex viewport mappings**: ADAPT — registry pattern
- **Babylon.js/MDN multiview**: ADAPT — broadcast, don't branch
- **Cosmos DB materialized views**: ADAPT — read-only by construction
- **CAPMAS** (arXiv 2609.06500): ADAPT principles (for 7.1, not R7.1)
- **MCP/A2A**: ADAPT boundary distinction (for 7.1, not R7.1)

Source links in `~/workspace/PHASE_7_R71_WORK_ORDER.md`.

## Delta-20 Categories

### 1. Missing concept
**Finding:** None. Composition uses existing see_* functions; no new concepts.

### 2. Contradiction
**Finding:** None. Composition preserves PERSPECTIVE ≠ TRUTH (R6.5).
Also read-only; cannot modify canonical records.

### 3. Semantic drift
**Finding:** None. No R6.1–R6.5 behavior changed. Additive only.

### 4. Duplicate authority
**Finding:** None. Composition creates no authority. Accepts no grants
(grants rejected, not ignored). Issues no grants.

### 5. Wrong abstraction
**Finding:** None. Composition is a query, not an authority mechanism.

### 6. Wrong layer
**Finding:** None. Composition lives in `perspective_views.py` (view layer).
Not in coordinator, authority, or persistence.

### 7. Persistence failure
**Finding:** None. Composition is pure; no persistence. Detached output
via deepcopy inside failure boundary; no references into canonical state.

### 8. History/provenance consequence
**Finding:** None. No historical records modified. Each component attributed
with viewer, mode, source, epistemic_status.

### 9. Security consequence
**Finding:** None. No new attack surface. No network exposure. No new
agent interfaces. Trusted local query only. Copying failures bounded.

### 10. Human-authority consequence
**Finding:** None. Composition does not grant authority. Human sovereignty
unchanged.

### 11. Offline consequence
**Finding:** None. Local-first preserved. No network dependencies.

### 12. Performance consequence
**Finding:** Bounded. Composition is O(N) in viewers, each view O(M) in nodes.
No hot paths modified.

### 13. Public-path theater
**Finding:** None (verified). Uses real `see_as`, real Viewers, real Program
with confirmed Ideas. No mocks. Registered in `form/regress.py`.

### 14. Mathematical weakness
**Finding:** None. Aggregation semantics explicitly defined. Counts not summed.
Container validation prevents malformed input masquerading as data.

### 15. Visual theater
**Finding:** None. No UI changes. Combined report attributed, not merged truth.

### 16. Historical-recovery conflict
**Finding:** None. R6.3 rollback untouched. Composition has no recovery
paths (pure function).

### 17. Simpler reuse opportunity
**Finding:** None. Reuses existing see_*; no duplication.

### 18. Research contradiction
**Finding:** None. Research supports design. No contradictions.

### 19. Future-phase incompatibility
**Finding:** Bounded. Compatible with 7.1 (oversight views) and 7.3.
No networking assumptions.

### 20. From-scratch challenge
**Finding:** None. Extends existing `perspective_views.py`. Reuses R6.5
proven guarantees.

---

**END OF R7.1 DELTA-20 (AMEND)**
