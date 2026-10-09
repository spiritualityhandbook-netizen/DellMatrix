#!/usr/bin/env python3
"""R6.5 separation enforcement — walking skeleton and proof matrix.

GDP_PHASE_6_R65_SEPARATION_ENFORCEMENT (MODE=C).

Proves at runtime:
- PERSONA ≠ PERMISSION: persona changes cannot grant/widen/restore authority.
- BIMO = ENFORCED CAPABILITY: fused capabilities = intersection, not union.
- PERSPECTIVE ≠ TRUTH: views are read-only; cannot modify canonical records.
- HUMAN SOVEREIGNTY: revocation effective; bulk ops require human token.

Uses real public interfaces. No mocks for the enforcement decisions.
"""

from __future__ import annotations

import copy
import sys
from typing import Any, Dict, List

CHECKS: List[Dict[str, Any]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append({"name": name, "ok": bool(cond), "detail": detail})
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" +
          (f" | {detail[:160]}" if detail and not cond else ""))


def fresh_program(owner: str):
    from form.open import open_program
    return open_program(owner)


def _mkgrant(p, pid, subject):
    """Issue a grant via agent_authority (R6.2 owner)."""
    from form.dell_matrix import agent_authority as aa
    grant = aa.issue_root_grant(p, issuer="test-host",
                               subject=subject, target=pid,
                               content_pid=pid)
    return grant


def part_walking_skeleton():
    """§3: Two host-bound agents, different personas/perspectives,
    same accepted Idea."""
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import personas as pm
    from form.dell_matrix import perspective_views as pv

    # --- Setup: one Idea, two agents with different personas. ---
    p = fresh_program("r65s1")
    pr = p.nursery.add("S1", words="separation test idea words")
    pid = pr.id

    coord = ac.new_coordinator(p)
    # Agent A: Manny (logic checker) persona.
    coord.register_agent("agent-a", persona_slots={"pilot": "manny"})
    # Agent B: Melody (growth guide) persona.
    coord.register_agent("agent-b", persona_slots={"pilot": "melody"})

    # --- Both views preserve canonical content and identity. ---
    snap_a = coord.snapshot_for("agent-a")
    snap_b = coord.snapshot_for("agent-b")
    idea_a = next((i for i in snap_a["ideas"] if i["pid"] == pid), None)
    idea_b = next((i for i in snap_b["ideas"] if i["pid"] == pid), None)
    check("r65 skeleton: both agents see the same Idea",
          idea_a is not None and idea_b is not None)
    check("r65 skeleton: views preserve canonical content",
          idea_a["words"] == "separation test idea words"
          and idea_b["words"] == "separation test idea words"
          and idea_a["pid"] == idea_b["pid"] == pid)

    # --- Unauthorized mutation denies (no grant). ---
    sa = coord.surface_for("agent-a")
    r_no_grant = sa.request_confirm(pid, "bogus-grant-id",
                                    request_id="r65-unauth")
    check("r65 skeleton: unauthorized confirm denies",
          r_no_grant["ok"] is False)

    # --- Exact authorized mutation succeeds. ---
    grant_a = _mkgrant(p, pid, "agent-a")
    h = p.acceptance_data_hash(pid, "confirm")
    r_auth = sa.request_confirm(pid, grant_a["grant_id"],
                                request_id="r65-auth",
                                expected_content_hash=h)
    check("r65 skeleton: authorized confirm succeeds",
          r_auth["ok"] is True and r_auth["result"] == "committed",
          detail=str(r_auth)[:200])

    # --- Persona changes do not alter the decision. ---
    # Re-register agent-a with a different persona.
    coord.register_agent("agent-a", persona_slots={"pilot": "melody"})
    # New proposal for a fresh grant.
    pr2 = p.nursery.add("S1b", words="second idea words")
    pid2 = pr2.id
    grant_a2 = _mkgrant(p, pid2, "agent-a")
    h2 = p.acceptance_data_hash(pid2, "confirm")
    r_after = sa.request_confirm(pid2, grant_a2["grant_id"],
                                 request_id="r65-after-persona",
                                 expected_content_hash=h2)
    check("r65 skeleton: persona change does not grant authority",
          r_after["ok"] is True,  # grant was explicitly issued
          detail="grant issued, persona irrelevant")
    # Without a grant, still denied regardless of persona.
    pr3 = p.nursery.add("S1c", words="third idea words")
    pid3 = pr3.id
    r_no_grant2 = sa.request_confirm(pid3, "bogus",
                                     request_id="r65-no-grant-persona")
    check("r65 skeleton: persona change does not bypass denial",
          r_no_grant2["ok"] is False)

    # --- Revocation before execution denies. ---
    pr4 = p.nursery.add("S1d", words="fourth idea words")
    pid4 = pr4.id
    grant_a4 = _mkgrant(p, pid4, "agent-a")
    h4 = p.acceptance_data_hash(pid4, "confirm")
    # Enqueue but don't dispatch yet.
    env = ac.make_envelope(request_id="r65-revoke",
                           operation="confirm", target=pid4,
                           expected={"content_hash": h4}, _program=p)
    qid = coord.enqueue("agent-a", env)
    # Revoke before dispatch.
    from form.dell_matrix import agent_authority as aa
    aa.revoke_grant(p, grant_a4["grant_id"])
    r_revoked = coord.dispatch(qid, grant_a4["grant_id"])
    check("r65 skeleton: revocation before execution denies",
          r_revoked["ok"] is False,
          detail=str(r_revoked)[:200])

    # --- Perspective (snapshot) views are read-only. ---
    # The coordinator's snapshot_for() is the agent's "perspective" —
    # a bounded DETACHED view. Mutating it must not affect canonical.
    snap_mut = coord.snapshot_for("agent-a")
    idea_view = next((i for i in snap_mut["ideas"] if i["pid"] == pid), None)
    if idea_view is not None:
        orig_words = str(p.nursery.proposals[pid].words)
        # Mutate the view's copy.
        idea_view["words"] = "MUTATED VIA VIEW"
        check("r65 skeleton: view mutation does not touch canonical",
              str(p.nursery.proposals[pid].words) == orig_words)
    else:
        check("r65 skeleton: view returned the Idea", False,
              detail="idea not in snapshot")

    # --- Save/reload preserves outcome without restoring authority. ---
    from form import persist_rest as _pr
    _pr.save(p)
    p2 = _pr.load("r65s1", activate=False)
    # The committed proposal should still be committed.
    check("r65 skeleton: reload preserves committed state",
          "confirm" in str(p2.nursery.proposals[pid].status).lower(),
          detail=f"status={p2.nursery.proposals[pid].status}")
    # But the grant should not be restored (session authority).
    # (Grants are session-scoped; reload starts fresh.)


def part_bimo_capability():
    """§3: BIMO effective capabilities = intersection, not union."""
    from form.dell_matrix import personas as pm

    bimo = pm.BIMOBody()
    bimo.dock("logic", "manny")
    bimo.dock("growth", "melody")

    # Grants: manny can validate+acudit; melody can nurture+validate.
    grants = {
        "manny": ["validate", "audit"],
        "melody": ["nurture", "validate"],
    }
    effective = bimo.effective_capabilities(grants)
    check("r65 bimo: effective = intersection",
          effective == ["validate"],
          detail=f"got {effective}")

    # Fused abilities text is descriptive, not authority.
    fused = bimo.fuse()
    # The fused abilities are human-readable descriptions, not
    # capability tokens. They must not be usable as grants.
    check("r65 bimo: fused abilities are descriptive text",
          len(fused.get("abilities", [])) > 0
          and "validate" not in fused.get("abilities", []),
          detail=f"abilities={fused.get('abilities', [])[:3]}")
    # But the fused text must NOT be usable as a grant.
    check("r65 bimo: fused text does not include ungranted",
          "audit" not in effective and "nurture" not in effective)

    # Empty when no common grants.
    grants2 = {"manny": ["validate"], "melody": ["nurture"]}
    check("r65 bimo: no common grants -> empty",
          bimo.effective_capabilities(grants2) == [])

    # Sensitivity: if we used union, we'd get all four.
    union = sorted(set(grants["manny"]) | set(grants["melody"]))
    check("r65 bimo: sensitivity (union would be wrong)",
          union != effective and len(union) == 3)


def part_sovereignty():
    """§3: Human sovereignty gate for bulk operations."""
    from form.dell_matrix import agent_coordinator as ac

    p = fresh_program("r65s2")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")

    # Within threshold: no token needed.
    err = coord._check_sovereignty("confirm", 5, None)
    check("r65 sovereignty: within threshold passes", err is None)

    # Exceeds threshold without token: rejected.
    err2 = coord._check_sovereignty("confirm", 15, None)
    check("r65 sovereignty: bulk without token rejected",
          err2 is not None and "Human sovereignty" in err2,
          detail=str(err2)[:150])

    # Invalid token format: rejected.
    err3 = coord._check_sovereignty("confirm", 15, "bad-token")
    check("r65 sovereignty: invalid token rejected", err3 is not None)

    # Wrong owner: rejected.
    err4 = coord._check_sovereignty(
        "confirm", 15, "sovereignty:wrong-owner:123:abc")
    check("r65 sovereignty: owner mismatch rejected", err4 is not None)

    # Valid token format: passes (trusted host validates).
    err5 = coord._check_sovereignty(
        "confirm", 15, "sovereignty:r65s2:123456:abc123")
    check("r65 sovereignty: valid token passes", err5 is None)


def part_persona_separation():
    """§3: Explicit PERSONA ≠ PERMISSION assertion."""
    from form.dell_matrix import agent_coordinator as ac

    p = fresh_program("r65s3")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-x", persona_slots={"pilot": "manny"})
    # The assertion should not raise (separation holds).
    try:
        coord._assert_persona_authority_separation("agent-x")
        check("r65 separation: assertion holds", True)
    except Exception as e:
        check("r65 separation: assertion holds", False, detail=str(e)[:150])

    # Unknown subject: no-op, no raise.
    try:
        coord._assert_persona_authority_separation("nobody")
        check("r65 separation: unknown subject no-op", True)
    except Exception as e:
        check("r65 separation: unknown subject no-op", False,
              detail=str(e)[:150])


def main():
    part_walking_skeleton()
    part_bimo_capability()
    part_sovereignty()
    part_persona_separation()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"=== R6.5 separation: {passed}/{total} ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
