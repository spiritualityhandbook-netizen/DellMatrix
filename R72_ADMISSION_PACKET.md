# R7.2 ADMISSION PACKET — Perspective Studio (AMEND REPAIR, CONSOLIDATED)

**Directive:** GDP_PHASE_7_R72_CLOSE_SCOPE_EVIDENCE_AND_FAILURE_CIRCUIT (MODE=C)
**Prior directive:** GDP_PHASE_7_R72_SCOPED_PERSPECTIVE_STUDIO (MODE=C)
**Date:** 2026-10-11
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## Historical Identities (superseded)

- **First candidate:** HEAD `2f7d4c2543bdda5bb98d40fc4eabfb469e8bdc0c`,
  TREE `6bbf54d75415d94c7355d19f848daa3a28728abc`
  (PR #87, exact-head CI green, 31/31 proofs, 113/113 regression)
- **Director ruling:** AMEND — six findings (scope bypass, protection
  fail-open, incomplete persistence, failed-save incoherence, overstated
  logging, weak proofs). Identity and CI verified; gaps in scope,
  evidence, and failure behavior.
- **This packet** covers the repair circuit. The final admission identity
  is below; the first candidate is historical.

## What Was Repaired

### Finding 1: Studio command boundary bypassable
**Repair:** Moved the active-studio gate ahead of every non-exit special
handler in `run()` (reissue, say-prefix). Added scoped `studio> ` prompt.
**Files:** `form/repl.py`

### Finding 2: Protection fails open
**Repair:** Fail-closed screening of raw input, decoded escapes, and
structured keys/values via R6.2 `inference_dock` utilities. Screening
failure rejects. Fixed bounded failure codes; raw input never reflected
in responses or session evidence.
**Files:** `form/repl.py`, `form/dell_matrix/perspective_studio.py`

### Finding 3: Persisted evidence incomplete
**Repair:** One shared strict schema (`validate_section`) for
serialization and restoration. Validates section version (int 1, bool
rejected), session key/ID agreement, Program owner binding, closed-record
requirement, command field types and bounds. Distinguishes absent legacy
from explicit null/malformed. Malformed evidence preserved through
save/reload in the section payload. `studio_sessions` added to
DURABLE_KEYS. Broad exception suppression removed from restoration.
**Files:** `form/dell_matrix/perspective_studio.py`, `form/persist.py`,
`form/persist_rest.py`

### Finding 4: Failed save leaves a closed active session
**Repair:** `prepare_leave()` builds the closed record without mutating
the studio. Handler stages the record, saves via canonical
`persist_rest.save`, and discards the studio only on success. On failure,
prior in-memory records are restored; the studio remains active and
usable; retry is coherent (exactly one closed record, no duplication).
Stale-writer and recovery-required guards are reused, not bypassed.
**Files:** `form/repl.py`, `form/dell_matrix/perspective_studio.py`

### Finding 5: Logging and presentation overstate functionality
**Repair:** Bounds enforced during recording (50 commands, in-memory).
Rejected attempts recorded with safe codes. Help text documents
retention explicitly. Compose displays actual attributed observations
(report lines with viewer/mode/status/source) from `compose_views`.
Legend keys validated against displayed fields.
**Files:** `form/repl.py`, `form/dell_matrix/perspective_studio.py`

### Finding 6: Several proofs ineffective
**Repair:** Full suite rewrite. Removed unconditional verdicts and
permissive alternatives. All 74 checks are effective: routing proofs use
the real REPL with staged mutations; protection proofs use real grant
canaries with zero-disclosure assertions; persistence proofs use strict
schema cases; leave/retry proofs inject real save failures; detachment
proofs mutate nested observations. Sensitivity controls prove the tests
detect the defects they target.

## Executed Controls (74/74)

**Scope routing:**
- Real REPL: staged `create` via `reissue 1`, enter studio,
  `reissue confirm` → rejected, no "Reissuing now", no duplicate idea.
- Real REPL: `say leave` in studio → rejected (prefix not stripped).
- Static: studio gate precedes reissue and say-prefix in `run()`.

**Protection:**
- Real grant canary in compose JSON → `PROTECTED_MATERIAL`, zero
  disclosure in output and persisted evidence.
- `\uXXXX`-escaped canary → rejected, zero disclosure.
- Canary in spec keys → rejected.
- Screening failure (broken `protected_values`) → rejects, no composition.
- Sensitivity: weakened `contains_protected_decoded` → canary reaches
  composition; restored → rejects.

**Persistence:**
- Bool version → malformed; version 2 → malformed; key/ID mismatch →
  malformed; owner mismatch → malformed; unclosed record → malformed.
- Absent section → legacy empty; explicit null → malformed.
- Malformed evidence preserved through save/reload.
- `studio_sessions` in DURABLE_KEYS.
- Checkpoint contains studio evidence; rollback contract preserved.

**Leave/retry:**
- Injected save failure → `SAVE_FAILED`, studio active, session not
  closed, prior records restored, durable bytes unchanged.
- Studio usable after failure (compose works).
- Retry → exactly one coherent closed record, no duplicate leave.
- Recovery-required guard rejection → no bypass, studio retained.

**Evidence bounds:**
- 60 commands → 50 retained, oldest discarded (in-memory).
- Rejected attempts recorded with `OUT_OF_SCOPE` (not raw text).
- Legend keys match displayed fields.

**Full journey (real REPL):**
enter → compose (attributed observations) → legend → help →
rejected mutation → leave → fresh-process reload with complete
evidence comparison.

**Detachment:**
Nested observation mutation does not affect next compose or canonical
content. Field-for-field fidelity vs direct `compose_views`.

**Sibling sweep:**
Studio gate is the first non-exit branch; no other REPL-level scoped
mode exists; reissue and say-prefix are after the gate.

## Sensitivity Results

| Control | Weakened | Restored |
|---------|----------|----------|
| Protection | Canary reaches composition | Rejects with PROTECTED_MATERIAL |
| Scope routing | (Not weakened; static order proven) | Reissue rejected in studio |
| Save failure | (Injected failure) | Prior records restored, retry coherent |
| Persistence | (Malformed injected) | Preserved as evidence, valid kept |

All weakenings were restored after the sensitivity check. Production
code was not left in a weakened state.

## Raw Failure Evidence (pre-repair)

The Director's probes confirmed:
- `reissue confirm` in studio → "Reissuing now..." (dispatched).
  Reproduced pre-repair; fixed post-repair (rejected as out-of-scope).
- Screening exception → composition reached. Reproduced via broken
  `protected_values`; fixed post-repair (fail-closed rejection).
- Save failure → session already closed. Reproduced via injected
  failure; fixed post-repair (stage-then-save, restore on failure).

## Verification

- **Targeted:** 74/74
- **`--twice`:** 113/113 GREEN
- **`--order rev`:** 113/113 GREEN
- **Exact-head CI:** [pending]
- **Scanning:** EVALUATION_UNAVAILABLE (Copilot quota 402)

## Delta-20

All 20 categories reconciled against executed evidence. See
R72_DELTA20.md. No category renamed or renumbered. Remaining
uncertainty stated.

## Research Dispositions

- Martin Fowler CQRS: ADAPT (query/write separation, no CQRS machinery)
- pal-mvvm-foundation: ADAPT
- Vortex multiple viewports: ADAPT
- Babylon.js / MDN multiview: ADAPT
- Cosmos DB materialized views: ADAPT (read-only projection)
- Blender View Keeper: REJECT
- Director's repair note: central enforcement on every request and
  excluding sensitive input from logs — implemented via existing
  coordinator and R6.2 protection utilities, no new subsystem.
- Sources without actual links: UNKNOWN (not completed research)

## Limitations

- Scanning: EVALUATION_UNAVAILABLE (quota 402)
- Certification scope: R7.2 studio circuit only
- Cloud perspective: explicitly deferred
- No BIMO Forge, no networking
- Workshop identity ("perspective") used for attribution only; the
  Program-level workshop is not activated (matches authorized scope).

## Final Admission Identity

- **Branch:** `gdp-phase7-r72-studio`
- **Head:** `9aeb4194502aa41bd6d86e831ce7350f96fe016b`
- **Tree:** `19a0e50d8012b209d2de573310acec9cc2e356db`
- **Base:** `25386e8daaa8936ac821b9ee4fd5b2271bf1397e` (main)
- **PR:** #87 (to be updated)

---

**END OF R7.2 ADMISSION PACKET (REPAIR)**
