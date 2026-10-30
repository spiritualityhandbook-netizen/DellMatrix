> HISTORICAL RECORD — preserved as evidence of the state at its writing; it does NOT describe current behavior. The live system is under form/.

# R7.3 ADMISSION PACKET — General Workshop Contract

**Circuit:** R7.3 General Workshop Contract (Phase 7)
**Date:** 2026-10-16
**Status:** CANDIDATE READY FOR REVIEW (NOT CERTIFIED — DO NOT MERGE)

**Identity note:** The final admission head/tree are delivered in the
external envelope (the PR body and the return report), not in this
file, to avoid a self-referential commit hash. Base:
`8338c297e1614e16afe74035a7c560e5fcb517d7` (main; R7.2 merged).

## Objective (GDP Phase 7 draft, reconciled numbering)

The ledger draft's "one workshop contract" objectives (7.1.1–7.1.3,
7.1.5): a formal enter → scoped command set + scoped view → leave
contract; the button-menus rebuilt as real scoped environments;
workshop semantics tested (commands differ inside); public-path
proofs. Objective 7.1.4 (disclosure onboarding / teach rhythm) is a
separate concern and is NOT in this circuit's scope.

## Before / after

**Before:** `workshop <id>` set a flag and printed a menu. Dispatch
was unaffected — any command ran inside any workshop; no session
evidence existed; the persisted active flag was the whole mechanism.

**After:** `workshop <id>` opens a scoped session in the REPL:
- Scoped prompt `workshop:<id>> `.
- Scope derived at runtime from the workshop's own registry entry
  (command stems) — the displayed menu and the enforced set are one
  source.
- In-scope lines route through the SAME public dispatcher (fresh
  interaction id); the workshop grants nothing new.
- Out-of-scope lines — including mutations, say-prefixed lines, and
  staged reissues — are rejected at a gate positioned ahead of those
  handlers, exactly like the R7.2 studio gate.
- One scoped environment at a time (studio included).
- Input screened fail-closed before scope/dispatch/recording; only
  stems and fixed codes are recorded.
- `leave` stages the closed record, clears the active flag, and saves
  canonically; on failure everything is restored and the session is
  retained for retry. EOF/quit state plainly that nothing was saved.
- Evidence persists as a `workshop_sessions` section under the strict
  shared schema (sentinel absence vs null, closed-only, owner- and
  workshop-bound, malformed preserved and accumulated).

## Files

- `form/dell_matrix/workshop_session.py` (new): session record, scope
  derivation, strict section validate/serialize.
- `form/repl.py`: workshop gate + handler, entry interception, scoped
  prompt, EOF/quit honesty.
- `form/persist.py` / `form/persist_rest.py`: section serialize/restore.
- `form/mandell/r73_workshop_test.py` (new, 71 checks) + registration
  in `form/regress.py`.
- `README.md`: §7.6. `R73_DELTA20.md`: category reconciliation.

## Verification (this candidate)

- **Targeted R7.3 suite:** 71/71 — scope routing, all seven workshops,
  inside/outside differential, leave/EOF/quit honesty, genuine blocked
  save + retry, bounds, real-grant protection (output and persisted
  bytes), strict schema, one-environment rule, studio non-regression.
- **`form.regress --twice`:** 114/114 GREEN
- **`form.regress --order rev`:** 114/114 GREEN
- **Exact-head CI:** delivered in the external envelope (PR).
- **Scanning:** EVALUATION_UNAVAILABLE (Copilot quota 402) — never PASS.

Process note: the first regression run was RED on this module — the
harness requires a `smoke()` entry the module initially lacked. Fixed,
re-verified standalone and in both regression orders. The RED is
evidence the suite can fail; it is recorded here, not hidden.

## Limitations

- Circuit identity "R7.3" is Uni's reconciled numbering (the draft's
  R7.1 slot was taken by the executed composition circuit); a reviewer
  may renumber.
- Draft 7.1.4 (onboarding/teach rhythm) untouched.
- BIMO Forge semantics and Connected World remain unauthorized and
  untouched; the bimo/persona workshops are scoped menu environments
  only, with no new persona/authority behavior.
- The studio does not migrate onto the general contract in this
  circuit; coexistence is governed by the one-environment rule.
- No independent review has run yet (Delta-20 category 20: UNKNOWN).

---

**END OF R7.3 ADMISSION PACKET**
