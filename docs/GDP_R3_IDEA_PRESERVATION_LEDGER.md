# GDP R3 Idea Preservation — Process Escape Ledger

## Escape (2026-10-04)

**R2 visibility-based healing destroyed legitimate historical records.**

The `recover_confirmation_hybrid()` function scanned all confirmed proposals
and healed those without Plane Ideas to pending. This was intended to fix
crashed confirmations, but it also destroyed legitimate historical records
(faded, superseded, or otherwise valid) that had no journal.

## Root Cause

Absence from a projection (Plane) was treated as proof that acceptance never
committed. The heuristic could not distinguish:
- "Crashed confirmation" (journal exists, operation interrupted)
- "Legitimate historical record" (no journal, valid history)

## Permanent Executable Guard

**Recovery must use recorded intent (journal), not inferred visibility.**

1. `recover_confirmation_intent()` acts ONLY on the proposal recorded in the
   journal, not by scanning all confirmed proposals.
2. A confirmed proposal WITHOUT a journal is NEVER healed (preserved as-is).
3. Never add production recovery bypasses based on test fixture names
   (e.g., `owner.startswith("DCC_")`). Recovery applies uniformly.
4. When claiming OLD, verify the Program fingerprint matches the recorded
   OLD fingerprint. Do not substitute file shape for transaction coherence.
5. Revision links (`supersedes_id`, `superseded_by_id`) are distinct from
   derivation chain (`chain`). Do not mutate chain for revision ancestry.

**Enforcement:**
- `form/mandell/core_i_recovery.py`: `recover_confirmation_intent()` validates
  owner, operation, version, phase, proposal_id, fingerprints before mutation.
- `form/mandell/r3_permanent_regressions.py`: Case 08 verifies historical
  preservation. Case 09 verifies revision/derivation distinctness.
- No `owner.startswith()` bypasses in `core_i_recovery.py`, `persist_rest.py`,
  or `open.py`.

## Applicability

This guard applies to all future confirmation, supersession, and recovery
work in DellMatrix. Any new recovery mechanism must:
- Record intent BEFORE publication (journal with fingerprints)
- Recover from recorded intent, not inferred state
- Preserve historical records without journals
- Fail closed on malformed/conflicting evidence (preserve journal)

---
**Recorded:** 2026-10-04  
**Authority:** GDP_R3_IDEA_PRESERVATION_ADDENDUM, GDP_R3_COMPLETION_GATE  
**Status:** Permanent project law
