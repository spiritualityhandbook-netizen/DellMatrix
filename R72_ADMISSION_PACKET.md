> HISTORICAL RECORD — preserved as evidence of the state at its writing; it does NOT describe current behavior. The live system is under form/.

# R7.2 ADMISSION PACKET — Perspective Studio (FINISH-BOUNDARIES, CONSOLIDATED)

**Directive:** GDP_R72_FINISH_EXISTING_BOUNDARIES_AND_EXECUTABLE_EVIDENCE (MODE=C)
**Prior directives:** GDP_PHASE_7_R72_SCOPED_PERSPECTIVE_STUDIO (MODE=C);
GDP_PHASE_7_R72_CLOSE_SCOPE_EVIDENCE_AND_FAILURE_CIRCUIT (MODE=C)
**Date:** 2026-10-15
**Status:** CANDIDATE READY FOR DIRECTOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

**Identity note:** The final admission head/tree are delivered in the
external envelope (PR #87 body and the return report), not in this file,
to avoid a self-referential commit hash. This packet's parent candidate
is `e77806b7fa39ef86216249a4fa28ab70579306e4` on base
`25386e8daaa8936ac821b9ee4fd5b2271bf1397e` (main).

## Historical Identities (superseded)

- **First candidate:** HEAD `2f7d4c2543bdda5bb98d40fc4eabfb469e8bdc0c`,
  TREE `6bbf54d75415d94c7355d19f848daa3a28728abc` — Director AMEND #1.
- **First repair candidate:** HEAD `e77806b7fa39ef86216249a4fa28ab70579306e4`,
  TREE `757e57e4a3c0e967cbc526ef8d69a8b37511efff` — 74/74, 113/113 twice
  and reverse, exact-head CI green; Director verified the scope gate,
  scoped prompt, and staged leave/retry, then returned AMEND #2 (four
  remaining closure obligations below). This packet covers the
  finish-boundaries circuit that starts from that candidate.

## Second-AMEND Findings and Dispositions

### Gap 1: Persistence still loses evidence — FIXED
- Loader uses a missing-key sentinel (`_MISSING`): absent key loads as
  legacy empty state; explicit JSON null loads as malformed evidence.
- `serialize_section()` applies the same strict schema as restoration:
  active, foreign-owner, and key/ID-mismatched records are preserved in
  `malformed`, never silently saved as valid or discarded.
- Malformed entries accumulate per key as lists; a new failure never
  overwrites earlier evidence. Carriers survive load → save →
  fresh-process reload (executed proof, including absent-positive,
  null-negative, malformed-carrier, and conflicting-evidence controls).

### Gap 2: Protection is REPL-input-only — FIXED
- `PerspectiveStudio.compose` screens structured input (keys, values,
  escaped JSON) before composition and the detached result before
  release, via the shared `_screen_protected` helper built on the R6.2
  `inference_dock` utilities. Direct API and REPL callers receive the
  same enforcement; protection failure rejects with fixed codes, no
  reflected input or exception text.
- Canonical Idea content is never modified to sanitize a view; output
  containing protected-format material (including from canonical
  labels) is rejected at the studio boundary.
- Zero disclosure verified in complete API results, REPL output, and
  persisted session evidence. Sensitivity: with screening weakened, the
  grant canary actually appears in output (disclosure demonstrated);
  restored, it is rejected.

### Gap 3: Validation can escape its boundary — FIXED
- compose() enforces the collection contract: list container required,
  empty input rejected, eight-spec limit enforced (nine specs reject),
  aggregate bounds checked. Numeric conversion/overflow failures
  (including a huge-integer JSON coordinate) are caught and return
  fixed bounded rejection; invalid containers no longer raise
  TypeError. The REPL remains usable after each rejection.

### Gap 4: Advertised proofs absent — REPLACED WITH EXECUTED PROOFS
- **Rollback:** real authority-bound rollback (`confirm_rollback` with
  issued grant) to a sealed checkpoint containing studio evidence,
  executed after creating a distinguishably different second live
  session; fresh-process reload compares the exact restored records
  (first session present, second absent).
- **Blocked saves:** genuinely recovery-required (`_recovery_required`)
  and stale (`_post_rollback_stale`) instances created via production
  attributes — the guard itself is not mocked. Leave rejects with
  SAVE_FAILED, durable bytes unchanged, session retained.
- **Sensitivity:** demonstrates actual canary disclosure under weakened
  protection (previous INVALID_SPEC acceptance removed).
- **Gate order:** static checks now identify the main dispatch gate
  (the last of three `if _studio is not None:` branches, after the EOF
  and quit handlers) and are backed by behavioral real-REPL routing
  proofs using genuinely pending targets (exact pending status, Plane
  absence, unchanged canonical content, no dispatch).
- **Packet identity:** corrected here — no intermediate identity or
  pending-CI claim remains; the final identity is in the external
  envelope.

## Preserved from the first repair (Director-verified)

- Studio gate ahead of reissue and say-prefix handlers; scoped
  `studio> ` prompt.
- Stage-then-save leave: failure restores prior in-memory records,
  session stays active and usable, retry yields exactly one closed
  record. EOF/quit never claim persistence.
- Bounded recording enforced during recording (50 commands, 10 closed
  sessions); rejected attempts recorded with safe codes; compose
  displays attributed observations; legend validated against displayed
  fields.

## Verification (this candidate)

- **Targeted R7.2 suite:** 90/90
- **`form.regress --twice`:** 113/113 GREEN
- **`form.regress --order rev`:** 113/113 GREEN
- **Exact-head CI:** delivered in the external envelope (PR #87).
- **Scanning:** EVALUATION_UNAVAILABLE (Copilot quota 402) — never PASS.

## Delta-20

All 20 established categories reconciled under their canonical names
and numbering. See R72_DELTA20.md. Remaining uncertainty stated there
(category 20).

## Research Dispositions

- Martin Fowler CQRS: ADAPT (query/write separation, no CQRS machinery)
- pal-mvvm-foundation: ADAPT
- Vortex multiple viewports: ADAPT
- Babylon.js / MDN multiview: ADAPT
- Cosmos DB materialized views: ADAPT (read-only projection)
- Blender View Keeper: REJECT
- Director's notes (central enforcement on every request; sensitive
  input excluded from logs; sentinel for JSON-null absence; OWASP
  logging guidance): implemented through existing utilities.
- Sources without actual links: UNKNOWN (not completed research)

## Limitations

- Scanning: EVALUATION_UNAVAILABLE (quota 402)
- Certification scope: R7.2 studio circuit only
- Cloud perspective: explicitly deferred
- No BIMO Forge, no networking
- Test isolation uses unique owners in the canonical state directory,
  matching the established R6.3 proof pattern; UUID owners alone are
  not claimed as filesystem isolation.
- Workshop identity ("perspective") used for attribution only; the
  Program-level workshop is not activated (matches authorized scope).

---

**END OF R7.2 ADMISSION PACKET (FINISH-BOUNDARIES)**
