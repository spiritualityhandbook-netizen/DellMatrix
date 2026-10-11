# R7.1 ADMISSION PACKET — Read-Only Perspective Composition (FINISHED)

**Directive:** GDP_R71_FINISH_REQUIRED_PERSISTED_VIEW_COMPARISON (MODE=C)
**Date:** 2026-10-10
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

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
- **Head:** `d1769d2829018316d0e7c908550e4a456c050a3f`
- **Tree:** `8c0aac4c436e67bc4559c6d5b74dee78d290bbb4`
- **Base:** `efd68bf5ef702dcb5a59aa246ed4397c0c0a133c`
- **Note:** Intermediate identities (26ec9229, db62e2b, c93e864, ad6fafc)
  superseded; frozen head below is authoritative.

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
