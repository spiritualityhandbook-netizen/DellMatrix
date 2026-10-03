# GDP-001 Phase 1 — Known Architectural Gaps

## MF-5: Ideas outside checkpoint/rollback envelope

**Status:** RESOLVED in R1/R2 (2026-10-03).

**R1 resolution:** Ideas integrated into the existing Phase-0 checkpoint
authority — no second checkpoint system. `checkpoint_generation.py`
seals an `ideas` owner-snapshot member; `core_i_recovery.rollback()`
restores Ideas from the sealed generation.

**R2 resolution (three-member atomicity):** The Phase-0 journaled
rollback transaction was extended in place from PROGRAM+NURSERY to
PROGRAM+NURSERY+IDEAS (single journal, single recovery, no duplicate
authority). Required invariant holds: a reader observes only OLD
COMPLETE GENERATION or TARGET COMPLETE GENERATION, never a hybrid.
Recovery also completes the observable individual-idea working set
(marker-guarded rehydration), so canonical files and read path agree.

**Legacy semantic (documented, ARGUS A-R2-1):** rolling back to a
pre-R1 generation with no ideas member stages an empty ideas snapshot
and clears stale individual files — coherent "ideas cleared" semantic.

---

## A-6: Test state isolation

**Status:** ACKNOWLEDGED.

**Issue:** Phase-1 tests write to real `form/state/ideas/` without cleanup.

**Mitigation:** Tests use unique UUIDs; no cross-test interference.
Future work should add per-test owner namespacing.
