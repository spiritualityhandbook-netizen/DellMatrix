# GDP-001 Phase 1 — Known Architectural Gaps

## MF-5: Ideas outside checkpoint/rollback envelope

**Status:** KNOWN GAP, deferred.

**Issue:** Phase-0 checkpoints seal only `nursery` and `program` members.
Idea files in `form/state/ideas/` are not snapshotted or restored by
`rollback()`. A rollback after Idea mutation leaves program/nursery at
the checkpoint but Ideas at their mutated state — a hybrid.

**Why deferred:** Integrating Ideas into the Phase-0 checkpoint system
requires modifying `checkpoint_generation.py` (`_MEMBER_KINDS`), which is
Phase-0 sealed machinery. Doing so risks weakening Phase-0 contracts.

**Mitigation:** Idea saves are atomic (via `atomic_write_json`). History
is append-only and immutable. The hybrid risk is documented, not hidden.

**Future:** Phase 2+ should extend the checkpoint envelope to include
Ideas, or define an Idea-specific generation system.

---

## A-6: Test state isolation

**Status:** ACKNOWLEDGED.

**Issue:** Phase-1 tests write to real `form/state/ideas/` without cleanup.

**Mitigation:** Tests use unique UUIDs; no cross-test interference.
Future work should add per-test owner namespacing.
