# C3.Diff (DD-51 Rings 1+2) — Grounding, 2026-11-11 (Uni, DISCOVER phase)

Plan authority: ACE_FUTURE_DEVELOPMENT_PLAN.md §12.79 (verified
behavior), §12.79b (assessment), §12.79c (Ace ruling 2026-11-09:
DD-51 — Diff becomes the ONE comparison authority). §14.4 card
C3.Diff = rings 1+2; MWL item 130. STATUS in plan: "design
directive recorded; implementation routes through the Director
as a bounded circuit family (Rings 1+2 first)."

## What Diff is today (verified in code, main 7e0d7fb)

- Dell 89 lives in form/mandell/spectrum_ops.py. Diff compares
  the Core II STORE ONLY: last_diff = {before: store, after:
  store, changed, label, baseline} (spectrum_ops.py:381); with
  no baseline: baseline "missing", available False, error
  "baseline_missing" (:369).
- The baseline is `CoreIIState.diff_baseline` (core_ii_exec.py:29):
  a _ckpt dict captured by spectrum_ops._note_mutation
  immediately before the most recent STORE mutation. Session-only
  (never serialized — not in CORE_II_DURABLE), so a restored
  session honestly reports baseline_missing until the next
  mutation. Last-move only; no archive (§12.79a).
- _note_mutation callers today (non-test): spectrum_ops itself
  (copy/move/delete/replace/patch — the store writers) and
  query_ops.py:44 (imports _note_mutation as _note_diff — one
  non-spectrum caller exists; identify which op in the build
  grounding pass).
- snap() (core_ii_exec.py:57) ALREADY captures the wide frame:
  scope, selected, store, groups, defs, aliases, compositions,
  staged, try_depth, context, route, branch, last_assert,
  last_guard, last_frame, control_steps. The wide PHOTO exists;
  _note_mutation photographs only for store writers, and Diff
  compares only the store slice of it.

## What rings 1+2 require (§12.79c, Ace-ruled)

RING 1 — every writer through the one door: Weight (74),
Normalize (75), Group (82), Ungroup (83), Reference (81),
Context (80), Cause (78), Depend (79), Define/Alias/Compose
join Set (55) and the clerks (84–88) must call the SAME
_note_mutation authority before mutating, so the baseline
photo precedes ANY content change. No second capture authority.

RING 2 — compare every content slice in the photo: store,
weights, groups, refs, causes, deps, defs, aliases,
compositions — in standalone last-move mode AND transaction
mode alike. Working-state slices (selected, scope, context,
route) and verdicts (last_assert, last_guard) compared when
the WHOLE-CHECKPOINT scope is named. Diff is aimed by a SCOPE
WORD (store = today; weights; groups; whole checkpoint; ...).

HONESTY (frozen): last-move only, no archive; no baseline ->
baseline_missing for EVERY scope; a slice she cannot compare
is NAMED unexamined in the receipt, never silently skipped;
last_diff widens to per-slice change-sets under the named scope.
Verify-after-move (§12.79a part 3) is designed in this family.

## Open grounding questions for the build pass

1. Which writers mutate slices today WITHOUT _note_mutation?
   (Trace each of 74/75/78/79/80/81/82/83 + 84–88 clerks to its
   mutation site — the exact ring-1 work list.)
2. Scope-word grammar: how does a seed aim Diff today (label?
   argument form?), and what operand form should name a scope
   without breaking the existing store-Diff seeds in suites?
3. Transaction mode: where is the frame checkpoint captured,
   and does _note_mutation fire inside frames today?
4. weights/refs/causes/deps are NOT in snap() — the photo must
   widen (snap is also the checkpoint serializer's shape —
   check who consumes snap() before widening it; a separate
   photo function may be the authority-preserving shape).
5. Receipt consumers: who reads last_diff (Mirror 18? Studio?)
   — widening its shape must not break them silently.

## Classification

BUILD (not gated): a semantic widening inside one existing
authority (spectrum_ops Diff + _note_mutation), no new store,
no second authority. Sizeable: ring 1 touches many writers —
the circuit should land ring 1 (door) + ring 2 (compare) as
ONE PR per §12.79c (2) "RINGS 1+2 ARE ONE FIX", with failing-
first per writer family. Director routing: this grounding +
a build proposal go into the review queue; the Director may
split the circuit, which is his call to make on the record.
