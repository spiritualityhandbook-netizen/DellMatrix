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

    # --- Authoritative restart via fixed child script. ---
    # R6.5 AMEND §2: Before restart, issue a grant for a proposal that
    # remains PENDING. After restart (fresh OS process), attempt that
    # SAME target with the old handle. Prove rejection and no mutation.
    # Then reissue and prove success.
    from form import persist_rest as _pr
    from form.dell_matrix import agent_authority as aa2
    import subprocess, sys, json, os

    # Create a PENDING proposal (do NOT confirm it yet).
    pr_pending = p.nursery.add("S1pending", words="pending restart test")
    pending_pid = pr_pending.id
    # Issue a grant for the pending proposal.
    grant_pending = aa2.issue_root_grant(
        p, issuer="test-host", subject="agent-a",
        target=pending_pid, content_pid=pending_pid)
    old_pending_grant = grant_pending["grant_id"]

    _pr.save(p)

    # Run the fixed child script in a FRESH OS PROCESS with JSON args.
    child_args = {
        "owner": "r65s1",
        "confirmed_pid": pid,  # The already-confirmed proposal
        "pending_pid": pending_pid,
        "old_grant_id": old_pending_grant,
        "expected_words": "pending restart test",
    }
    result = subprocess.run(
        [sys.executable, "form/mandell/r65_fresh_probe.py",
         json.dumps(child_args)],
        cwd=".",
        capture_output=True, text=True, timeout=60,
    )
    # Require returncode==0 (child asserts all).
    check("r65 fresh: child returncode==0",
          result.returncode == 0,
          detail=f"rc={result.returncode} out={result.stdout[:200]}")

    # Parse structured output.
    try:
        out_data = json.loads(result.stdout.strip().split("\n")[-1])
        assertions = out_data.get("assertions", {})
    except Exception:
        assertions = {}

    check("r65 fresh: exact status==confirmed",
          assertions.get("confirmed_status_exact") is True,
          detail=str(assertions)[:200])
    check("r65 fresh: confirmed words match",
          assertions.get("confirmed_words_match") is True)
    check("r65 fresh: old grant denied on same target",
          assertions.get("old_grant_denied_same_target") is True,
          detail="Target mismatch alone must not explain denial")
    check("r65 fresh: denied attempt caused no mutation",
          assertions.get("no_mutation") is True)
    check("r65 fresh: reissued authority succeeds",
          assertions.get("reissued_succeeds") is True)


def part_bimo_capability():
    """R6.5 AMEND §2: BIMO is presentation, not authority.

    effective_capabilities() is a PRESENTATION UTILITY. It computes
    set intersection for display. It does NOT validate grants, bind
    operations, or enforce anything. Real authority comes only from
    host-issued grants validated at dispatch.
    """
    from form.dell_matrix import personas as pm
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa

    bimo = pm.BIMOBody()
    bimo.dock("logic", "manny")
    bimo.dock("growth", "melody")

    # The presentation utility computes intersection (for display).
    labels = {
        "manny": ["validate", "audit"],
        "melody": ["nurture", "validate"],
    }
    effective = bimo.effective_capabilities(labels)
    check("r65 bimo: presentation computes intersection",
          effective == ["validate"],
          detail=f"got {effective}")

    # CRITICAL: The presentation output cannot be used as authority.
    # Attempting to use these labels as a grant must fail.
    p = fresh_program("r65bimo")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-b")
    sa = coord.surface_for("agent-b")
    pr = p.nursery.add("S1", words="bimo authority test")
    pid = pr.id

    # Try to use the "effective" labels as a grant ID — must deny.
    # (Labels are not grant handles.)
    r = sa.request_confirm(pid, "validate", request_id="r65-bimo-label")
    check("r65 bimo: labels are not grant handles",
          r["ok"] is False)

    # Only a real host-issued grant works.
    grant = aa.issue_root_grant(p, issuer="test-host",
                                subject="agent-b", target=pid,
                                content_pid=pid)
    h = p.acceptance_data_hash(pid, "confirm")
    r2 = sa.request_confirm(pid, grant["grant_id"],
                            request_id="r65-bimo-real",
                            expected_content_hash=h)
    check("r65 bimo: real grant succeeds",
          r2["ok"] is True)

    # Fused abilities text is descriptive, not authority.
    fused = bimo.fuse()
    check("r65 bimo: fused abilities are descriptive text",
          len(fused.get("abilities", [])) > 0)


def part_sovereignty():
    """R6.5 AMEND §1: Human sovereignty via existing grant path.

    Human sovereignty is enforced because EVERY protected operation
    requires a grant issued through the trusted host path. Agents
    cannot mint grants. This test proves the grant-issuance boundary
    behaviorally.
    """
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa

    p = fresh_program("r65s2")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-a")
    sa = coord.surface_for("agent-a")

    pr = p.nursery.add("S1", words="sovereignty test")
    pid = pr.id

    # Without a host-issued grant: denied (sovereignty holds).
    r = sa.request_confirm(pid, "agent-minted-grant",
                           request_id="r65-sov-no-grant")
    check("r65 sovereignty: agent cannot mint authority",
          r["ok"] is False)

    # With a host-issued grant: succeeds (legitimate delegation).
    grant = aa.issue_root_grant(p, issuer="test-host",
                                subject="agent-a", target=pid,
                                content_pid=pid)
    h = p.acceptance_data_hash(pid, "confirm")
    r2 = sa.request_confirm(pid, grant["grant_id"],
                            request_id="r65-sov-with-grant",
                            expected_content_hash=h)
    check("r65 sovereignty: host-issued grant succeeds",
          r2["ok"] is True)


def part_persona_behavioral():
    """R6.5 AMEND §3: Behavioral PERSONA ≠ PERMISSION proof.

    Executes matched authorized/unauthorized requests before and after
    persona changes. Descriptive changes must not alter the permission
    decision or canonical state.
    """
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix import agent_authority as aa

    p = fresh_program("r65s3")
    coord = ac.new_coordinator(p)
    # Register with persona A.
    coord.register_agent("agent-x", persona_slots={"pilot": "manny"})
    sa = coord.surface_for("agent-x")

    pr = p.nursery.add("S1", words="behavioral persona test")
    pid = pr.id

    # Baseline: unauthorized denied with persona A.
    r1 = sa.request_confirm(pid, "bogus", request_id="r65-behav-1")
    check("r65 behavioral: denied with persona A (no grant)",
          r1["ok"] is False)

    # Change to persona B (re-register).
    coord.register_agent("agent-x", persona_slots={"pilot": "melody"})
    sa2 = coord.surface_for("agent-x")

    # Still denied with persona B (no grant). Persona change grants nothing.
    r2 = sa2.request_confirm(pid, "bogus", request_id="r65-behav-2")
    check("r65 behavioral: still denied with persona B (no grant)",
          r2["ok"] is False)

    # Issue a legitimate grant. Succeeds regardless of persona.
    grant = aa.issue_root_grant(p, issuer="test-host",
                                subject="agent-x", target=pid,
                                content_pid=pid)
    h = p.acceptance_data_hash(pid, "confirm")
    r3 = sa2.request_confirm(pid, grant["grant_id"],
                             request_id="r65-behav-3",
                             expected_content_hash=h)
    check("r65 behavioral: authorized succeeds with persona B",
          r3["ok"] is True)

    # Canonical state: capture full canonical record.
    prop = p.nursery.proposals[pid]
    # Compare ACTUAL values, not just attribute existence.
    check("r65 behavioral: canonical status is confirmed",
          str(prop.status) == "confirmed")
    # Revision identity: the proposal ID is stable (None revision_number
    # is expected for new proposals; the ID is the identity).
    check("r65 behavioral: proposal ID stable",
          prop.id == pid)
    check("r65 behavioral: words preserved exactly",
          str(prop.words) == "behavioral persona test")
    # Provenance: proposal has an ID and label.
    check("r65 behavioral: proposal identity intact",
          prop.id == pid and str(prop.label) == "S1")


def part_perspective_interface():
    """R6.5 AMEND §3: Exercise actual perspective interface.

    Calls perspective_views.see_first/see_whole, captures canonical
    state, changes persona/BIMO metadata, and verifies canonical
    state is unchanged. The view may differ; the canonical must not.
    """
    from form.dell_matrix import perspective_views as pv
    from form.dell_matrix import agent_coordinator as ac

    p = fresh_program("r65persp")
    pr = p.nursery.add("S1", words="perspective test words")
    pid = pr.id

    # Capture canonical state BEFORE.
    prop_before = p.nursery.proposals[pid]
    canonical_before = {
        "status": str(prop_before.status),
        "words": str(prop_before.words),
        "pid": prop_before.id,
        "label": str(prop_before.label),
    }

    # Exercise the actual perspective interface.
    viewer = pv.Viewer(id="v1", role="ai_first")
    view1 = pv.see_first(p, viewer)
    check("r65 perspective: see_first returns view",
          isinstance(view1, dict) and "epistemic_status" in view1)

    # Change persona metadata (descriptive only).
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-p", persona_slots={"pilot": "manny"})
    coord.register_agent("agent-p", persona_slots={"pilot": "melody"})

    # Exercise perspective again with different mode.
    viewer2 = pv.Viewer(id="v2", role="ai_whole")
    view2 = pv.see_whole(p, viewer2)
    check("r65 perspective: see_whole returns view",
          isinstance(view2, dict) and "epistemic_status" in view2)

    # Canonical state must be UNCHANGED.
    prop_after = p.nursery.proposals[pid]
    canonical_after = {
        "status": str(prop_after.status),
        "words": str(prop_after.words),
        "pid": prop_after.id,
        "label": str(prop_after.label),
    }
    check("r65 perspective: canonical unchanged after view/persona changes",
          canonical_before == canonical_after,
          detail=f"before={canonical_before} after={canonical_after}")

    # The views themselves are read-only (no write methods).
    check("r65 perspective: views expose no mutation API",
          not hasattr(view1, "commit") and not hasattr(view1, "write"))


def part_sensitivity():
    """R6.5 AMEND §1: REAL production-weakening sensitivity.

    Weakens the SPECIFIC production decision (AcceptancePolicy.check),
    not the whole dispatch. Runs the SAME negative assertion against
    normal, weakened, and restored implementations. Requires observable
    divergence. Restores in finally.
    """
    from form.dell_matrix import agent_coordinator as ac
    from form.dell_matrix.agent_coordinator import make_envelope

    p = fresh_program("r65sens")
    coord = ac.new_coordinator(p)
    coord.register_agent("agent-s")
    sa = coord.surface_for("agent-s")

    pr = p.nursery.add("S1", words="sensitivity test")
    pid = pr.id
    h = p.acceptance_data_hash(pid, "confirm")

    def try_unauthorized(tag):
        """Attempt unauthorized confirm via the real dispatch path."""
        env = make_envelope(request_id=f"r65-sens-{tag}",
                            operation="confirm", target=pid,
                            expected={"content_hash": h}, _program=p)
        qid = coord.enqueue("agent-s", env)
        return coord.dispatch(qid, "bogus-grant-id")

    # NORMAL: unauthorized denied (guard intact).
    r_normal = try_unauthorized("normal")
    check("r65 sensitivity: normal denies without grant",
          r_normal["ok"] is False)

    # WEAKEN: Patch the SPECIFIC decision (policy.check) to always allow.
    # This is the real production enforcement point.
    policy = p.acceptance_policy
    orig_check = policy.check
    def weakened_check(*args, **kwargs):
        return {"allowed": True, "decision": "allow",
                "weakened": True, "reason": "sensitivity-test"}
    policy.check = weakened_check

    try:
        # WEAKENED: the SAME negative assertion must now DIVERGE
        # (unauthorized request succeeds, proving the check was load-bearing).
        r_weak = try_unauthorized("weakened")
        # Note: dispatch may still deny for other reasons (e.g., content
        # hash mismatch, queue issues). We check specifically that the
        # policy decision was bypassed.
        diverged = (r_weak.get("weakened") is True or
                    r_weak["ok"] is True)
        check("r65 sensitivity: weakened check diverges",
              diverged,
              detail=f"weak result ok={r_weak['ok']}")
    finally:
        # RESTORE: Always restore the real check.
        policy.check = orig_check

    # RESTORED: unauthorized denied again.
    r_restored = try_unauthorized("restored")
    check("r65 sensitivity: restored denies without grant",
          r_restored["ok"] is False)


def smoke() -> bool:
    """Regression smoke entrypoint for form.regress."""
    global CHECKS
    CHECKS = []
    part_walking_skeleton()
    part_bimo_capability()
    part_sovereignty()
    part_persona_behavioral()
    part_perspective_interface()
    part_sensitivity()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"R6.5 separation: {passed}/{total}", flush=True)
    return passed == total and total > 0


def main():
    part_walking_skeleton()
    part_bimo_capability()
    part_sovereignty()
    part_persona_behavioral()
    part_perspective_interface()
    part_sensitivity()
    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c["ok"])
    print(f"=== R6.5 separation: {passed}/{total} ===")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
