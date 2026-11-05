# DIRECTOR REPORT — 72-49 (SM-32): Revocation-Chain Invalidation Across Restart + Retry as One Contract

**Item:** Master Register 72-49 (P0/E) — "AcceptancePolicy revocation chains unproven" (PARTIAL at reconciliation). Executed in SUSX100,000 Cycles 15–16 + main-session regression, 2026-11-05.
**Branch:** `uni/72-49-revocation-chain`. **Code head:** `df88f72ce5711bb7e64f9a506e33c8a0eaf4470f` on main `0c062a1`. This report rides in the same PR; CI evidence is read at the PR's final head.
**Status:** SUBMITTED for Director review. Uni label on merge: MERGED_VERIFIED_BY_UNI (not a certification). **This is a proof circuit: no defect was found and no product code changed.**

## The gap

AcceptancePolicy is the single owner of acceptance authorization, with three chain types (grant attenuation chains, approval derivation chains, opt-ins) whose validity recurses ancestors: any revoked, expired, or foreign-session ancestor must deny every unfinished descendant. Prior suites (r61, r63, r64, r65, wo51) each proved fragments — in-session revocation here, one cross-process grant handle there, a simulated restart elsewhere. The register's P0 gap was the **combination as one contract**: build chains in session A → revoke mid-chain → retry in-session → restart (including a genuine second OS process) → every prior-session artifact denies → re-issue in the new session → new artifacts allow while the old ones still deny.

## Falsification first (pristine code)

A standalone probe (66 expectations) ran against pristine main `0c062a1` before any suite was built: **CONTRACT HOLDS — 66/66**, including the cross-process leg (child-process verdicts all deny). SWAT choice: proportionate falsification (proof-only unless the probe found an ALLOW); recorded in the grounding note. No repair was needed or made.

## What was built

- `form/sm32_revocation_chain_test.py` (NEW, 60 checks): the one-contract suite — grant, approval, and opt-in chains in session A; mid-chain revocation of each type; retry ×2 in-session (denied approvals are never auto-retried; re-issuance mints new ids); restart via a fresh in-process policy AND a genuine child OS process denying every prior-session artifact; session-id change check; re-issuance in session B allowing while session-A artifacts still deny.
- Registered in `form/regress.py` (canonical count 236 → **237**, uniqueness verified via `intended_entries()`).
- README suite count updated 236 → 237 in the same commit, so the count stays truthful at this head (the Director's review-#5 suggestion to eventually replace the numeric count with a pointer to `form/regress.py` is a separate future docs patch, not folded into this candidate).

## Evidence

- **Probe (failing-first posture):** 66/66 expectations hold on pristine code — the suite therefore binds a verified contract rather than chasing a defect.
- **Targeted suite:** 60/60 GREEN at the code head; **fresh clone at df88f72: 60/60 GREEN**.
- **Mutants (3, real work committed first, inverse-edit reverts, post-revert suite 60/60):** `_grant_chain_valid → True` killed at the grandchild retry check; `_source_chain_valid → True` killed at the derived-approval retry check; the revoked-approval assertion dropped from `check()` killed at the plain-retry check.
- **Full regression ×3 (sequential, main session, terminal logs):** fwd **237/237 GREEN**; `--twice` **237/237 GREEN**; `--order rev` **237/237 GREEN** at df88f72.
- **Exact-head CI:** this PR's checks at its final head (merge only on all terminal PASS per the hard gate).
- Test realism: INTEGRATION with a genuine CROSS_PROCESS leg (child OS process verdicts), below REAL_USER_PATH.

## Boundaries

- AcceptancePolicy state is in-memory per Program instance by design (nothing persisted, no load path); "restart" therefore means a new instance/process — the suite proves the contract under exactly that semantics and claims nothing about a persisted-policy variant, which does not exist.
- The proof covers the three chain types and the retry/restart combination named in the register gap; it does not re-audit expiry timing or multi-intelligence dispatch (covered by r64/r65 and not re-claimed here).

## Anticipated probes

- *"A revoked ancestor re-issued in the same session — does the old descendant revive?"* — Re-issuance mints a NEW id; the descendant references the revoked parent id and still denies. Covered by the retry checks.
- *"Session B artifact presented to session A?"* — Session binding is checked both directions in the restart legs; foreign-session artifacts deny.

## Questions for the Director

1. Does this close 72-49 (accept the one-contract proof as the register's missing evidence), or is an additional axis required (e.g. expiry × revocation interaction)?
2. PR #294 (Q1 audit, amended head ce8c8a4) still awaits your re-review under the merge hold — noted here only so the queue stays visible in one place.
