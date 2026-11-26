# PART IV — CODE STAGE, SECTION 1: C9 DUALMODE (ROW #157, DD-36)

Date: 2026-11-21 · Lane: PR #505 (`uni/part-4-far-stratum`) · Actor: Uni

## Authority

- Ace ruling 2026-11-20, item 10: "Row #157 Adapt: NOW — DualMode
  build authorized." (DD-36's 2026-11-09 "not yet" is lifted.)
- Design of record: ACE_FUTURE_DEVELOPMENT_PLAN SS12.34a/b + the C9
  circuit block (slices C9.NoIntent DD-35 + C9.DualMode DD-36).
- Placement: #157 rides Part IV per Ace's rulings and the Eight-Part
  lane assignment for the #155/#157 builds; stated openly in the
  code-stage claim on PR #505 (comment 7065144407). This is a
  Translate (Dell 45) build under Ace's direct order, not a Far
  V/FAR runtime build (the Director's Part IV plan-confirm fence on
  Far runtime is untouched).

## What was built

- `form/mandell/adapt_intent.py` (new): a deterministic intent
  determination engine in the Adapt architecture — vocabulary
  phrases (token n-grams, longest-first) + regex entities -> intent
  candidates gated on ALL required entities, with a deterministic
  confidence (0.55 required + 0.25 optional + 0.20 tagged-token
  coverage) and deterministic ranking. DellMatrix vocabulary =
  the pattern router's families, restricted to the subset the
  canonical cascade verifiably constructs (probed at build head:
  PlaceVerb is {place, plant}, not put/set; destructive verbs are
  never registered).
- `form/mandell/translate.py`: `Intent.engine` receipt field
  (default None; canonical `translate()` never sets it);
  `_safety_blocked()` extracted so the canonical body and the dual
  door share one MPC-001/002 guard; `adapt_determine()` (Translate
  as the dock's tool, SS12.34b item 3 — determination only, never
  calls translate); `translate_dual(english, docked=False)` — the
  dual-mode door with engine receipts (layers: adapt / router /
  dock / guard / none).
- DD-35 at the dual door: unparseable text returns an explicit
  `no_intent` (dell None, mandel "") — no invented Show seed. In
  docked mode, unknown text is residue: receipt marks it
  proposal-only for the docked AI; nothing is invented.
- `form/c9_dualmode_test.py` (new, registered in `form/regress.py`):
  23 checks — engine determination/entities/confidence determinism,
  no-translate-import structure, credit presence, undocked adapt /
  router / guard / no-intent paths, docked + residue paths, the tool
  face, and a canonical-untouched pin.

## Engine decision (the circuit's call, SS12.34a)

ADAPT-the-approach, in-tree — not the pip library. Grounds: the
runtime is stdlib-only by record (requirements.txt: no external
packages in form/) with an offline-first posture; a downloaded
library artifact also failed this environment's execution-risk
check on 2026-11-21 and was not extracted, installed, or read.
If Ace or the Director want the literal library vendored instead,
that is a separate, explicitly approved step.

## Credit (Ace, SS12.34b item 2 — in code AND documentation)

The deterministic layer implements the architecture of the **Adapt
Intent Parser, by the Mycroft AI team (team led by Sean
Fitzgerald), Apache-2.0** — github.com/MycroftAI/adapt. Credit also
stands in `form/mandell/adapt_intent.py` (ADAPT_CREDIT).

## Evidence

- Failing-first: suite written before the implementation; RED run
  = ImportError (module absent), log preserved in the goal
  workspace (`hidden_files/c9_build_2026-11-21/`).
- GREEN: `form.c9_dualmode_test` 23/23. Spot regressions:
  translate_intent_args 18/18, translate_dead_args 21/21,
  translate_word_counts 21/21, english_composer 33/33,
  phrase_tests PASS, polyglot_tests PASS, adapt_intent smoke PASS.
- Mutant control: no_intent mutated to carry an invented Show seed
  -> suite FAILS at c9_dual_no_intent_prose; inverse-edit revert ->
  23/23. Baseline before changes: the three translate suites green
  at the rebased head.
- Branch hygiene: plan-stage commits rebased onto current main
  (b83a53e) with zero conflicts before building.

## Limitations / what remains for C9 and Part IV

- Canonical `translate()` behavior is deliberately unchanged —
  including its unknown -> "09[Show] :: unknown" form; DD-35's
  honest no-intent lives at the dual door. REPL/bridge adoption of
  `translate_dual` is a later step (not claimed here).
- Docked mode's top layer is represented by the canonical cascade
  in-process; a live docked model invoking `adapt_determine` as a
  tool is FI-017 territory (runtime home Part I GP-E23/C8), not
  built here.
- Row #157 is NOT flipped: credit settles only via the normal
  post-merge path (merged-main proof + both authorities). Row #155
  PERSONAMATRIX is the next section in this lane. No V/FAR row moves.

## Correction addendum (2026-11-21) — docked receipt truth

Director §42 code challenge 7066274038 (CORRECTION REQUIRED) found a
receipt-integrity defect in the original build above: under
`docked=True`, `translate_dual` called only the canonical local
router yet wrote `layer: "dock"` on the engine receipt, falsely
attributing the result to a dock that was never invoked (the live
dock integration is FI-017, not built). The §"What was built"
receipt list above ("adapt / router / dock / guard / none") records
that original labeling and is superseded by this addendum.

Repair (this PR, corrected head): `mode="docked"` remains the
REQUESTED mode, but the receipt now names the layer that ACTUALLY
determined the result — "guard" when the safety guard binds,
"router" when the canonical cascade constructs the command, "none"
when nothing determines an intent — and explicitly carries
`dock_invoked: False` / `dock_status: "not_invoked"`. Residue stays
proposal-only; canonical `translate()` is unchanged. Failing-first:
3 new checks (router-recognized / unknown residue / guarded
conditional destructive, all under `docked=True`) RED at the
original head, GREEN after repair; suite 26/26 (one pre-existing
assertion, `c9_dual_docked_grow`, updated — it had encoded the
false "dock" label).
