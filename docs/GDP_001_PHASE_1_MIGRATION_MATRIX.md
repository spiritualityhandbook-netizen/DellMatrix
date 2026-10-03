# GDP-001 Phase 1 — Migration / Compatibility Matrix

**Date:** 2026-10-03
**Base:** d282d35160386f3df56c68cc1aba21931d1d45a5

## Classification

| Object | Current location | Classification | Rationale |
|--------|-----------------|----------------|-----------|
| Plane Unit | form/dell_matrix/plane.py | LEGACY_COMPATIBLE | De facto idea (IDEA_LAW.md fields = Unit fields). Can be elevated to canonical Idea via manifest schema. |
| Nursery Proposal | form/dell_matrix/nursery.py | LEGACY_COMPATIBLE | Proposed/accepted/rejected states reused for Idea lifecycle. Not an Idea itself. |
| Program.history | form/open.py | NON_IDEA | Interaction log (last-24 inputs), not semantic Idea history. |
| Outcome records | form/mandell/outcome_ledger.py | NON_IDEA | Execution evidence, not Idea state. Provenance source via observation. |
| Knowledge entries | form/mandell/ | NON_IDEA | Influence gating, not Idea identity. |
| IdeaGrow | form/dell_matrix/idea_grow.py | NON_IDEA | Deprecated experimental; not an Idea. |
| Canonical Idea | form/mandell/idea.py (new) | CANONICAL_IDEA | The authoritative evolving Idea object. |

## Migration rules

1. **No destructive migration.** Existing Units, Proposals, and history are not rewritten.
2. **No silent reinterpretation.** A Unit is not automatically an Idea; it becomes one when elevated via the canonical API.
3. **Elevation path:** Unit → Idea via `manifest` schema (future work; Phase 1 establishes the Idea model, Phase 2+ integrates).
4. **Provenance preserved.** All existing history/provenance mechanisms remain authoritative for their domains.

## Compatibility

- Phase-0 persistence contracts: preserved (fail-closed, no hybrids).
- Nursery quarantine law: preserved (proposals don't bypass).
- Lineage single authority: preserved (no second lineage).
- Knowledge influence separation: preserved (STORED ≠ ELIGIBLE ≠ SELECTED).
