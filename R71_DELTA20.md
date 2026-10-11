# R7.1 Delta-20 — Read-Only Perspective Composition (MERGED/CLOSED)

**Date:** 2026-10-10/11
**Circuit:** R7.1 (first Phase-7 implementation circuit)
**Base:** `efd68bf` (R6.5 production)
**Merge:** PR #85 → `cf4d67e` (parents efd68bf + 7164cde8; tree 21f9a9c matches certified)
**Status:** MERGED / CLOSED — all proof corrections complete (52/52)

## Proof Corrections

1. **Populated observations:** Exact Idea IDs in each mode's structure.
2. **Exact aggregation:** Preconditions; exact statuses; no permissive.
3. **Detachment sensitivity:** Retained nested; shallow fails; restored.
4. **Exact restart:** Uses persist_rest.load(owner, activate=False).
   Compares the ENTIRE normalized compose_views result (every field, no
   hand-built projection, no default=str). One fixed child script takes owner,
   specs, and expected as JSON args. Valid run requires exit zero and exact
   equality. Negative control submits a skin-mutated expectation (counts,
   statuses, viewer order intact) to the same child and requires an explicit
   COMPARISON_MISMATCH.
5. **State:** Content-level comparison.
6. **Siblings:** Both outcomes; report failure bounded.

## Delta-20

1. Missing concept — None.
2. Contradiction — None. Preserves PERSPECTIVE ≠ TRUTH.
3. Semantic drift — None. Additive.
4. Duplicate authority — None.
5. Wrong abstraction — None.
6. Wrong layer — None.
7. Persistence failure — None.
8. History/provenance — None.
9. Security — None. Bounded failures.
10. Human-authority — None.
11. Offline — None.
12. Performance — Bounded.
13. Public-path theater — None. Correct loader used.
14. Mathematical weakness — None.
15. Visual theater — None.
16. Historical-recovery — None.
17. Simpler reuse — None.
18. Research contradiction — None.
19. Future-phase — Bounded.
20. From-scratch — None.

---

**END OF R7.1 DELTA-20 (FINISHED)**
