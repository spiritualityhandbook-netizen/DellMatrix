# GDP-001 Phase 1 — Delta-20 Challenge Report

**Date:** 2026-10-03
**Target:** form/mandell/idea.py @ 03cb962

## 1. Missing concept
**Finding:** Title versioning is asymmetric (rename versions old, current unversioned). **Status:** Documented as P4 latent; acceptable for Phase 1.

## 2. Contradiction
**Finding:** PRISM P1-P3 addressed. No remaining contradictions found.

## 3. Semantic drift
**Finding:** `get_property(name, state)` for non-ACTIVE states returns latest in that state, which is correct. No drift.

## 4. Duplicate authority
**Finding:** Idea vs Unit title duplication (P4). **Status:** Documented; precedence rule: Idea=semantic authority, Unit=spatial representation.

## 5. Wrong abstraction
**Finding:** PropertyVersion as frozen dataclass is correct for event-sourced history. No issue.

## 6. Wrong layer
**Finding:** Idea is in form/mandell (semantic layer) — correct. Not in UI or persistence layer.

## 7. Persistence break
**Finding:** idea_persist.py uses atomic_write_json (Phase-0). Fail-closed on corrupt. No break.

## 8. History break
**Finding:** Immutable versions + supersedes links preserve history. _idea_state_history now serialized. No break.

## 9. Provenance break
**Finding:** Transitions now record provenance (P3 fix). No break.

## 10. Security break
**Finding:** Provenance agent/source are caller-supplied (claimed, not verified). **Status:** Documented as limitation; not a break for Phase 1 (no auth infrastructure yet).

## 11. Human-authority break
**Finding:** No autonomous Idea mutation. All changes require explicit API calls. No break.

## 12. Offline break
**Finding:** No network dependencies. UUID generation is local. No break.

## 13. Performance regression
**Finding:** See performance baseline. No material regression.

## 14. Public-path theater
**Finding:** Public circuit uses real Idea API, not a demo facade. No theater.

## 15. Mathematical weakness
**Finding:** N/A (no mathematical claims in Phase 1).

## 16. Visual theater
**Finding:** No UI/Perspective dependencies. No theater.

## 17. Recovery failure
**Finding:** Fail-closed on corrupt JSON. Missing file raises FileNotFoundError (honest). No silent failure.

## 18. Simpler architecture
**Finding:** NULL audit reviewed. The bitemporal fields (valid_from/valid_to) are justified by supersession semantics. No unnecessary complexity found.

## 19. Research conflict
**Finding:** Research ledger documents 6 sources with rejections. No conflict.

## 20. From-scratch challenge
**Finding:** If rebuilding, would we still need separate Idea vs Unit? **Answer:** Yes — Unit is spatial (x,y,skin), Idea is semantic (history, provenance, lifecycle). The separation is justified.

## Summary
- **Real findings:** P1/P2/P3 (fixed), P4 (documented latent), title asymmetry (documented).
- **No-findings:** 14/20 passes found no material issues.
