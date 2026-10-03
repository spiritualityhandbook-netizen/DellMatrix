# GDP-001 Phase 0 — DELTA-20 Reconsideration Audit

**Branch:** gdp-phase0-work (post-integration + NULL MUST_FIX repairs) · **Date:** 2026-10-03
**Method:** 20 substantive reconsideration passes over the integrated Phase-0 result.
Only substantive findings recorded; "no material finding" is legitimate when supported.

## 1. Missing concept — NO MATERIAL FINDING
Scanned for Phase-0-sized concepts the 25 objectives missed. Candidates considered:
persisted-state schema migration/versioning; backup/restore as user capability.
Migration is genuinely needed but belongs to Phase 1 (Unit revision store will
need it) — recorded as future-phase, not a Phase-0 gap. Backup/restore is an
ops/workshop concern (Phase 7). Nothing blocks Phase 0's "trustworthy foundation" bar.

## 2. Contradiction — 1 FINDING (documented, Director ruling requested)
Chain-skip (`ok=True, skipped=True`) vs single-seed-refuse (`ok=False`) for
reserved dells: both report the same fact (reserved/not-active, zero mutation);
control-flow treatment differs by composition context. Documented in
LANGUAGE_COMPLETION_MATRIX.md; unification is a product-semantic decision for
Director at the phase gate. Not a silent contradiction — it is a recorded open decision.

## 3. Semantic drift — NO MATERIAL FINDING
Phase-0 behavior changes were all intended honesty fixes (operator_bridge
arg-drop, reserved-dell refusal, perspective rewire). Full regress 82/82 guards
against unintended drift. No operation changed meaning silently.

## 4. Duplicate authority — NO MATERIAL FINDING (deferrals verified)
NULL audit verified the three deferred families (vesica, resonance, _harmonic/
verita) are documented in the equation ledger §7 with Phase-3 actions, not
forgotten. No new duplicates introduced (C1–C4 cosmetic, deferred to future).

## 5. Wrong abstraction — NO MATERIAL FINDING
`Nursery.repoint_to_live` (named method > inline rebind, carries contract),
`execution_standing()` (read-only index, test-pinned), epistemic_status
vocabulary (confined to perspective files). Each judged KEEP-WITH-JUSTIFICATION
by NULL; concur.

## 6. Wrong layer — NO MATERIAL FINDING
Reserved-dell refusal placement (leaf vs front door): behaviorally equivalent
(all leaf paths go through the front door); NOT_A_DEFECT. Receipt threading in
the router is the correct layer (the router holds requested/resolved/authority;
derivation would be fabrication).

## 7. Persistence failure — 1 NOTE (documented, not a defect)
R1's two deferred rollback-timing semantics (eager copy-on-rollback inside
core_i_recovery; eager live-program-file restore on rollback) remain Director
decisions. The deferred-copy window is documented in PERSISTENCE_CONTRACT.md §3.
The corruption bug (0.1.1) is fixed and proven; the deferred items change WHEN
convergence happens, not WHETHER sealed state is safe.

## 8. History/provenance consequence — NO MATERIAL FINDING
Receipt standardization ADDS provenance (requested/resolved/authority/affected).
The Dell28 fix never mutates sealed members, so generation provenance is
untouched. No historical record was rewritten.

## 9. Security consequence — POSITIVE
The reserved-dell refusal closes an idea-smuggling path (`place_idea` side
effect on the public raw-seed path). NurseryConflictError is honest.
No new attack surface (new code paths are refusal paths; new docs are docs).
/cmd hardening and Dell87 refusal from the PR #69 base remain green in the
integrated regress.

## 10. Human-authority consequence — NO MATERIAL FINDING
Nothing in Phase 0 expands machine autonomy. Receipts DESCRIBE authority;
they do not confer it (R3). BIMO/confirmation paths untouched.

## 11. Offline consequence — NO MATERIAL FINDING
All Phase-0 mechanisms are local-first; zero network added. 44/47 refusals
preserve offline honesty.

## 12. Performance consequence — NO MATERIAL FINDING
Baseline recorded (P0_PERFORMANCE_BASELINE.md). No Phase-0 perf regression
(regress ~115s, consistent with pre-Phase-0). R1's per-mutation whole-file
nursery autosave noted as a Phase-5 perf item.

## 13. Public-path theater — NO MATERIAL FINDING (verified)
Investigated a suspicious `| ideas=1` REPL banner against a 3-idea session:
the banner is a startup snapshot, accurate when printed (fresh owner had 1
idea at startup); the save receipt and file state both correctly show 3.
Not theater — verified, not assumed.

## 14. Mathematical weakness — HONEST (no new finding)
R4's ledger is explicit: 3 MATHEMATICALLY_UNJUSTIFIED, 2 CONTRADICTORY,
headline "zero live equations carry a full in-repo derivation." The admission
contract (P1–P8, H1–H4) requires derivations going forward, closing the loop.

## 15. Visual theater — NO MATERIAL FINDING
free_matrix fallback now propagates honesty instead of synthesizing counts
(R5). Lattice single-cell pileup remains a documented Phase-4 item.

## 16. Historical-recovery conflict — NO MATERIAL FINDING
Phase 0 does not conflict with MPC-012-R recovery. The Verita firewall
(F1–F5) prevents mathematical soup; lineage preserved.

## 17. Simpler reuse opportunity — DEFERRED (NULL C1–C4)
Four cosmetic reductions (framing filter ×3, partial ×3, receipt-naming
fallback, 21/22 delegation ×2) deferred to SAFE_FUTURE_PHASE. Behavior is
correct; the reductions are hygiene, not defects.

## 18. Research contradiction — NO MATERIAL FINDING
Phase 0's architectural choices were mechanism-level, decided by code evidence
(reproduce-then-fix). No external-research claims were made; nothing to contradict.

## 19. Future-phase incompatibility — NO MATERIAL FINDING
Receipt fields are optional/backward-compatible (extensible). epistemic_status
vocabulary is ready for Phase 7. R1's deferred-copy window is documented for
Phase 1's revision store. No incompatibility found.

## 20. From-scratch challenge — 1 OPEN QUESTION (for Director)
If rebuilding persistence from scratch: the sealed/live split with non-aliased
ownership IS the clean design; R1's fix converges to it. The one genuine
from-scratch question is whether rollback should EAGERLY restore the live
program file (R1's deferred semantic decision). Phase 0 chose deferred
convergence (documented); Director may rule otherwise at the gate.

## Summary
20 passes: 15 no material finding · 2 documented findings (contradiction-2
open Director decision; persistence-7 deferred semantic) · 1 positive
(security-9) · 1 honest-no-change (math-14) · 1 deferred hygiene set (17).
No manufactured defects. No MUST_FIX_BEFORE_GATE findings from Delta-20.
