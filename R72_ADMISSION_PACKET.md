# R7.2 ADMISSION PACKET — Perspective Studio (FINISHED)

**Directive:** GDP_PHASE_7_R72_SCOPED_PERSPECTIVE_STUDIO (MODE=C)
**Date:** 2026-10-11
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

## What Was Built

Perspective Studio: a scoped REPL workshop for composing perspective
views and inspecting their meaning. Read-only: the studio delegates to
R7.1 `compose_views`; it cannot confirm, grant, or mutate.

**Files:**
- `form/dell_matrix/perspective_studio.py` (new): PerspectiveStudio adapter,
  spec validation, session records, inspectable legend
- `form/repl.py`: studio mode branching in `run()`; `_handle_studio_line`;
  explicit EOF/quit behavior
- `form/persist.py`: `studio_sessions` in serialize payload
- `form/persist_rest.py`: shape-validated restore with malformed-evidence
  preservation and 10-session retention
- `form/mandell/r72_studio_test.py` (new): 31 proofs, registered
- `form/regress.py`: suite registered
- `R72_DELTA20.md` (new): all 20 categories reconciled
- `README.md`: §7.5 walkthrough with exact syntax

## Proof (31/31)

Walking skeleton via the real REPL (`python3 -m form.repl`):
- Entry, caller-supplied JSON composition, legend, leave, fresh-process reload
- Field-for-field fidelity: studio compose == direct compose_views

Executed negative controls:
- Mutation rejection (`confirm` in studio → out-of-scope, idea unchanged)
- Malformed JSON/specs (10 cases, all rejected with explicit errors)
- Owner mismatch (spec owner ≠ Program owner → OWNER_MISMATCH)
- Save failure (session retained, studio stays active for retry)
- Output detachment (mutating result does not affect program)
- Malformed persistence (section preserved as evidence, fail-closed)
- Protected logging (input screened via inference_dock utilities)

## Verification

- Targeted: 31/31
- `--twice`: 113/113 GREEN
- `--order rev`: 113/113 GREEN
- Exact-head CI: [pending]

## Delta-20

All 20 categories reconciled against executed evidence. See R72_DELTA20.md.
No category replaced; provenance/security/recovery use established numbering.

## Research Dispositions

- Martin Fowler CQRS: ADAPT (query/write separation, no CQRS machinery)
- pal-mvvm-foundation: ADAPT
- Vortex multiple viewports: ADAPT
- Babylon.js / MDN multiview: ADAPT
- Cosmos DB materialized views: ADAPT (read-only projection)
- Blender View Keeper: REJECT
- Sources without actual links: UNKNOWN (not completed research)

## Limitations

- Scanning: EVALUATION_UNAVAILABLE (Copilot quota 402)
- Certification scope: R7.2 studio circuit only
- Cloud perspective: explicitly deferred
- No BIMO Forge, no networking

## Exact Identity

- **Branch:** `gdp-phase7-r72-studio`
- **Head:** [frozen below]
- **Tree:** [frozen below]
- **Base:** `25386e8daaa8936ac821b9ee4fd5b2271bf1397e` (main)

---

**END OF R7.2 ADMISSION PACKET**
