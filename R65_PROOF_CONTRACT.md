# R6.5 PROOF CONTRACT — Separation Enforcement

**Directive:** GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C)
**Date:** 2026-10-09
**Status:** FROZEN — implementation against this contract.

## Claim 1: PERSONA ≠ PERMISSION

**Statement:** Changing a persona (activating, docking, changing slots)
cannot grant, widen, or restore authority.

**Public path:** `HostCoordinator.register_agent(subject, persona_slots={...})`
→ `AgentIdentity.persona_slots` → `dispatch(queued_id, grant_handle)`.

**Expected state:** The `dispatch` method never reads `persona_slots`
or `bimo_binding`. Authority is determined solely by:
- Host-bound subject (from `register_agent`, not from persona)
- Grant handle validity (via `agent_authority`)
- AcceptancePolicy decision (via R6.1 writer)

**Negative control:** Register agent with `persona_slots={"pilot": "manny"}`,
then change to `{"pilot": "melody"}` (via re-registration or direct
mutation attempt). The authority decision for a queued request must be
identical before and after.

**Sensitivity:** If `dispatch` were modified to consult `persona_slots`,
the negative control would fail (different persona → different decision).

**Non-coverage:** Does not cover persona metadata being used for
non-authority purposes (logging, UI, guidance). Only the permission
decision is in scope.

## Claim 2: BIMO = ENFORCED CAPABILITY

**Statement:** Descriptive BIMO metadata (docked personas, fused
abilities text) cannot substitute for issued authority. Fused
capabilities are the INTERSECTION of constituent grants, never the union.

**Public path:** `personas.BIMO.fuse()` → returns `{"abilities": [...]}` (text)
→ (must NOT be used for decisions).

**Expected state:** The coordinator never calls `BIMO.fuse()` for
permission decisions. If a BIMO fusion is presented as authority, it is
rejected. The effective capability set for a fused BIMO is computed as
the intersection of explicitly granted capabilities.

**Negative control:** Fuse BIMO with personas having abilities
["validate", "audit"] and ["growth", "nurture"]. Attempt to exercise
"validate" without an explicit grant → denied. The fused abilities text
does not confer the capability.

**Sensitivity:** If the coordinator accepted `fuse()["abilities"]` as
authority, the negative control would fail.

**Non-coverage:** Does not cover the UX value of BIMO fusion (guidance,
synthesis). Only the authority decision is in scope.

## Claim 3: PERSPECTIVE ≠ TRUTH

**Statement:** Changing a view (perspective mode, filters) cannot
silently change accepted records, revision identity, lifecycle, or
provenance. Views are read-only; writes through a view raise.

**Public path:** `perspective_views.see_first()/see_whole()` → view dict
→ (attempted write to `program.nursery.proposals` via view data).

**Expected state:** View functions return detached data with
`epistemic_status`. They never return mutable references to canonical
objects. Any attempt to modify the canonical record through view data
either fails (detached copy) or is explicitly rejected.

**Negative control:** Get a view of a proposal. Attempt to modify the
view's `words` field. Verify the canonical proposal is unchanged.
Change view mode from "first" to "whole". Verify the coordinator's
authority decision for the same request is identical.

**Sensitivity:** If views returned mutable canonical references, the
negative control would fail (canonical modified via view).

**Non-coverage:** Does not cover view accuracy (whether the view
correctly represents the canonical state). Only the write barrier and
decision invariance are in scope.

## Claim 4: HUMAN SOVEREIGNTY

**Statement:** Revocation remains effective during queued and derived
execution. Inference and learned preferences may propose or rank;
acceptance still passes the canonical protected writer. Machine-initiated
bulk operations require explicit human authorization.

**Public path:** `agent_authority.revoke()` → `coordinator.dispatch()`
→ R6.1 writer.

**Expected state:** If a grant is revoked after enqueue but before
dispatch, the dispatch denies (R6.4 already enforces this). For
sovereignty: a `sovereignty_token` (explicit human authorization) is
required for operations exceeding a scope threshold (e.g., bulk
confirm of >N proposals).

**Negative control:** Enqueue a request. Revoke the grant. Dispatch →
denied (not committed). Attempt a bulk operation without sovereignty
token → rejected.

**Sensitivity:** If revocation were not checked at dispatch, the
negative control would fail (revoked grant still commits).

**Non-coverage:** Does not define the UX for obtaining human
authorization. Only the enforcement gate is in scope.

## Implementation Plan

1. **Verify** R6.4 coordinator already enforces persona/authority
   separation (it does — `dispatch` never reads `persona_slots`).
2. **Add** `BIMO.effective_capabilities(grants)` computing intersection.
3. **Add** explicit write barrier in perspective views (if not present).
4. **Add** sovereignty gate in coordinator for bulk operations.
5. **Prove** all four claims with the walking skeleton and full matrix.
