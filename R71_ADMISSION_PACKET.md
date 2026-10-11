# R7.1 ADMISSION PACKET — Read-Only Perspective Composition (MERGED/CLOSED)

**Directive:** GDP_PHASE_7_R71_ADMIT_MERGE_AND_ADVANCE (MODE=D)
**Date:** 2026-10-10/11
**Status:** R7.1 MERGED / CLOSED

**Merge:** PR #85 → `cf4d67e23785b8a9dc3068cc627619b7747256e7`
**Parents:** `efd68bf5ef702dcb5a59aa246ed4397c0c0a133c` + `7164cde8ddad99d44c68543eab907bd9c702359a`
**Tree:** `21f9a9c4bbe67c3ca0c67cfc154e199631140249` (matches certified)

**Production verification (fresh clean clone at cf4d67e):**
- `form.regress --twice`: 112/112 GREEN (R7.1 52/52)
- `form.regress --order rev`: 112/112 GREEN

**Scanning:** EVALUATION_UNAVAILABLE (Copilot quota 402)
**Certification scope:** Read-only composition circuit only; not all Phase 7.

## Restart Proof (Finished)

Uses persist_rest.load(owner, activate=False) — the correct reader.
- Saves populated Program with confirmed Idea
- Child loads via correct reader
- Asserts exact Idea IDs in Nursery AND Plane before composing
- Normalizes the ENTIRE compose_views result via JSON round trip:
  every field preserved, no hand-built projection, no default=str
  (unsupported values fail explicitly instead of being silently stringified)
- One fixed child script takes owner, specs, and expected result as JSON args
- Valid run: exit zero and exact full-result equality
- Negative control: a skin-mutated expectation (counts, statuses, viewer
  order intact) submitted to the same child produces an explicit
  COMPARISON_MISMATCH, not an unrelated failure

The "pre-existing file-naming issue" claim is withdrawn; the correct
loader resolves it. The projection gap (skin/report changes passing the
old selected-field comparison) is closed by full-result equality.

## Exact Identity

- **Branch:** `gdp-phase7-r71-composition`
- **Code head:** `9ff7b87cd7d6d7d686f0722520c5e662b3c8a1b8`
- **Code tree:** `5ad786165e4b151bdc5a8fc267f047ddd03e60f9`
- **Base:** `efd68bf5ef702dcb5a59aa246ed4397c0c0a133c`
- **Note:** Intermediate identities (26ec9229, db62e2b, c93e864, ad6fafc,
  d1769d28, dd10354) superseded. The frozen PR head adds only this packet;
  its exact identity is in the PR body and CI ran on it.

## Proof (52/52)

All Director-required outcomes with populated evidence, including
full-result restart equality and the executed negative control.

## Verification

- Targeted: 52/52
- `--twice`: 112/112 GREEN
- `--order rev`: 112/112 GREEN
- Exact-head CI: [pending]

## Delta-20

All 20 reconciled. See R71_DELTA20.md.

---

**END OF R7.1 ADMISSION PACKET**
