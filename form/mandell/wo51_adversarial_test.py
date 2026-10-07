"""WO-5.1 adversarial acceptance tests (Director 2026-10-05 whole-circuit).

Proves the acceptance policy rejects:
- forged approval dicts (matching fields, no issuance)
- stale approvals (proposal changed after review)
- cross-session approvals (different session_id)
- revoked approvals
- changed parents/goals after review
- unissued approval_id references

And accepts:
- valid manual confirmation via issued approval
- idempotent supersession (already-superseded returns existing)

Evidence class: INTEGRATION (real Program, real policy, isolated owner).
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

from form.open import open_program

OWNER = "WO51_ADV"
CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean():
    for pat in [f'form/state/nursery_{OWNER}.json', f'form/state/program_{OWNER}.json']:
        p = os.path.join(REPO, pat)
        if os.path.isfile(p):
            os.remove(p)


def test_forged_dict():
    """A hand-crafted dict matching all fields but no issuance -> denied."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("Forged", words="forged content")
    forged = {
        "approval_id": "appr_forged12345678",
        "reviewer": "test",
        "approved_pid": pr.id,
        "operation": "confirm",
        "session_id": p.acceptance_policy.session_id,
        "proposal_version": p.acceptance_data_hash(pr.id),
    }
    r = p.confirm_proposal(pr.id, _producer="test", _review_context=forged)
    check("forged_dict_denied", r.get("ok") is False and r.get("reason") == "acceptance_policy_denied", str(r.get("detail")))


def test_stale_content():
    """Proposal changed after review -> denied (stale)."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("Stale", words="original words")
    ctx = p.make_review_context(pr.id, "test")
    # Mutate after review
    pr.words = "changed words"
    r = p.confirm_proposal(pr.id, _producer="test", _review_context=ctx)
    check("stale_content_denied", r.get("ok") is False, str(r.get("reason")))


def test_stale_parents():
    """Parents changed after review -> denied."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("StaleParents", words="w", parents=[])
    ctx = p.make_review_context(pr.id, "test")
    pr.parents = ["someone_else"]
    r = p.confirm_proposal(pr.id, _producer="test", _review_context=ctx)
    check("stale_parents_denied", r.get("ok") is False, str(r.get("reason")))


def test_cross_session():
    """Approval issued in another policy session -> denied."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("CrossSession", words="w")
    ctx = p.make_review_context(pr.id, "test")
    # Simulate new session (restart): new policy, same persisted proposal
    p.acceptance_policy.reset_session()
    r = p.confirm_proposal(pr.id, _producer="test", _review_context=ctx)
    check("cross_session_denied", r.get("ok") is False, str(r.get("reason")))


def test_revoked():
    """Revoked approval -> denied."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("Revoked", words="w")
    issued = p.acceptance_policy.issue_approval(
        operation="confirm", target=pr.id, reviewer="test",
        data=p._acceptance_data_for(pr.id))
    p.acceptance_policy.revoke_approval(issued["approval_id"])
    r = p.confirm_proposal(pr.id, _producer="test", _review_context=issued["context"])
    check("revoked_denied", r.get("ok") is False, str(r.get("reason")))


def test_valid_manual():
    """Issued approval, unchanged -> allowed."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("Valid", words="w")
    ctx = p.make_review_context(pr.id, "test")
    r = p.confirm_proposal(pr.id, _producer="test", _review_context=ctx)
    check("valid_manual_allowed", r.get("ok") is True, str(r))


def test_revoked_opt_in():
    """Opt-in granted then revoked -> denied."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("OptRevoke", words="w")
    p.acceptance_policy.grant_opt_in("temp", scope="test")
    p.acceptance_policy.revoke_opt_in("temp")
    r = p.confirm_proposal(pr.id, _producer="temp")
    check("revoked_optin_denied", r.get("ok") is False, str(r.get("reason")))


def test_unknown_producer():
    """Default unknown producer, no context -> denied."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("Unknown", words="w")
    r = p.confirm_proposal(pr.id)
    check("unknown_denied", r.get("ok") is False, str(r.get("reason")))


def test_supersede_changed_successor():
    """Supersede approval bound to different successor words -> denied."""
    clean()
    from form.mandell import supersession as S
    p = open_program(OWNER)
    pr = p.nursery.add("SupBase", words="v1")
    ctx = p.make_review_context(pr.id, "test")
    assert p.confirm_proposal(pr.id, _producer="test", _review_context=ctx).get("ok")
    # Issue supersede approval for words="v2", then try words="v3"
    sctx = p.make_supersede_context(pr.id, "test", "v2 words", "V2")
    try:
        S.supersede_proposal(p, pr.id, "v3 words", label="V2",
                             _producer="test", _review_context=sctx)
        check("supersede_changed_successor_denied", False, "unexpectedly allowed")
    except Exception as e:
        check("supersede_changed_successor_denied",
              "acceptance_policy_denied" in str(e), str(e)[:80])


def test_idempotent_supersede():
    """Superseding an already-superseded unit returns existing (no dup)."""
    clean()
    from form.mandell import supersession as S
    p = open_program(OWNER)
    pr = p.nursery.add("IdemBase", words="v1")
    ctx = p.make_review_context(pr.id, "test")
    assert p.confirm_proposal(pr.id, _producer="test", _review_context=ctx).get("ok")
    p.acceptance_policy.grant_opt_in("test", scope="test")
    r1 = S.supersede_proposal(p, pr.id, "v2", _producer="test")
    assert r1.get("ok"), r1
    r2 = S.supersede_proposal(p, pr.id, "v2-again", _producer="test")
    # Deterministic refusal: no duplicate successor, existing relationship
    # returned. ok=False with reason already_superseded is BY DESIGN.
    check("idempotent_supersede",
          r2.get("ok") is False
          and r2.get("reason") == "already_superseded"
          and r2.get("superseded_by_id") == r1.get("new_id"),
          str(r2))




def test_derive_unrelated_target():
    """Approval for A cannot derive approval for unrelated B."""
    clean()
    from form.dell_matrix.acceptance_policy import ApprovalError
    p = open_program(OWNER)
    a = p.nursery.add("DeriveA", words="a words")
    b = p.nursery.add("DeriveB", words="b words")
    # Issue a plain confirm approval for A
    issued = p.acceptance_policy.issue_approval(
        operation="confirm", target=a.id, reviewer="test",
        data=p._acceptance_data_for(a.id))
    try:
        p.acceptance_policy.derive_approval(
            source_approval_id=issued["approval_id"],
            source_opt_in=None,
            operation="confirm", target=b.id, reviewer="test",
            data=p._acceptance_data_for(b.id),
            relationship={"type": "supersede_successor", "predecessor_id": a.id})
        check("derive_unrelated_denied", False, "unexpectedly allowed")
    except ApprovalError as e:
        check("derive_unrelated_denied", True, str(e)[:60])
    except Exception as e:
        check("derive_unrelated_denied", False, f"wrong exc {type(e).__name__}")


def test_derive_wrong_source_operation():
    """A confirm approval cannot source a supersede derivation."""
    clean()
    from form.dell_matrix.acceptance_policy import ApprovalError
    p = open_program(OWNER)
    a = p.nursery.add("DeriveC", words="c words")
    issued = p.acceptance_policy.issue_approval(
        operation="confirm", target=a.id, reviewer="test",
        data=p._acceptance_data_for(a.id))
    try:
        p.acceptance_policy.derive_approval(
            source_approval_id=issued["approval_id"],
            source_opt_in=None,
            operation="confirm", target="some_other",
            reviewer="test", data=p._acceptance_data_for(a.id),
            relationship={"type": "supersede_successor", "predecessor_id": a.id})
        check("derive_wrong_op_denied", False, "unexpectedly allowed")
    except ApprovalError:
        check("derive_wrong_op_denied", True)
    except Exception as e:
        check("derive_wrong_op_denied", False, f"wrong exc {type(e).__name__}")


def test_derive_changed_successor_data():
    """Derived content must match the approved successor payload."""
    clean()
    from form.dell_matrix.acceptance_policy import ApprovalError
    from form.mandell import supersession as S
    p = open_program(OWNER)
    pr = p.nursery.add("DeriveD", words="v1")
    ctx = p.make_review_context(pr.id, "test")
    assert p.confirm_proposal(pr.id, _producer="test", _review_context=ctx).get("ok")
    # Issue supersede approval for specific successor words
    sctx = p.make_supersede_context(pr.id, "test", "approved words", "V2")
    src_id = sctx["approval_id"]
    # Try to derive for content with DIFFERENT words
    fake_data = p._acceptance_data_for(pr.id)
    fake_data["content"] = {"label": "V2", "words": "different words", "detail": ""}
    try:
        p.acceptance_policy.derive_approval(
            source_approval_id=src_id, source_opt_in=None,
            operation="confirm", target="fake_succ",
            reviewer="test", data=fake_data,
            relationship={"type": "supersede_successor", "predecessor_id": pr.id})
        check("derive_changed_data_denied", False, "unexpectedly allowed")
    except ApprovalError:
        check("derive_changed_data_denied", True)
    except Exception as e:
        check("derive_changed_data_denied", False, f"wrong exc {type(e).__name__}")


def test_parent_revocation_invalidates_child():
    """Revoking the parent approval invalidates the derived child."""
    clean()
    from form.mandell import supersession as S
    p = open_program(OWNER)
    pr = p.nursery.add("DeriveE", words="v1")
    ctx = p.make_review_context(pr.id, "test")
    assert p.confirm_proposal(pr.id, _producer="test", _review_context=ctx).get("ok")
    sctx = p.make_supersede_context(pr.id, "test", "v2 words", "V2")
    src_id = sctx["approval_id"]
    # Manually derive (simulating what _supersede_impl does).
    # Content must match the approved successor payload (label="V2").
    succ = p.nursery.add("V2", words="v2 words")
    derived = p.acceptance_policy.derive_approval(
        source_approval_id=src_id, source_opt_in=None,
        operation="confirm", target=succ.id, reviewer="test",
        data=p._acceptance_data_for(succ.id),
        relationship={"type": "supersede_successor", "predecessor_id": pr.id})
    # Child valid before revocation
    r1 = p.confirm_proposal(succ.id, _producer="test",
                            _review_context=derived["context"])
    check("child_valid_before_revoke", r1.get("ok") is True, str(r1.get("reason")))
    # Revoke parent; a NEW derived child must now fail
    p.acceptance_policy.revoke_approval(src_id)
    succ2 = p.nursery.add("V2", words="v2 words")
    try:
        derived2 = p.acceptance_policy.derive_approval(
            source_approval_id=src_id, source_opt_in=None,
            operation="confirm", target=succ2.id, reviewer="test",
            data=p._acceptance_data_for(succ2.id),
            relationship={"type": "supersede_successor", "predecessor_id": pr.id})
        check("revoked_parent_blocks_derive", False, "unexpectedly allowed")
    except Exception:
        check("revoked_parent_blocks_derive", True)


def test_optin_revocation_invalidates_child():
    """Revoking the source opt-in invalidates a derived child at execution."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("DeriveF", words="v1")
    p.acceptance_policy.grant_opt_in("testprod", scope="test")
    # Derive from opt-in
    succ = p.nursery.add("DeriveF2", words="v2 words")
    derived = p.acceptance_policy.derive_approval(
        source_approval_id=None, source_opt_in="testprod",
        operation="confirm", target=succ.id, reviewer="test",
        data=p._acceptance_data_for(succ.id),
        relationship={"type": "supersede_successor", "predecessor_id": pr.id})
    # Revoke the opt-in before child execution
    p.acceptance_policy.revoke_opt_in("testprod")
    r = p.confirm_proposal(succ.id, _producer="testprod",
                           _review_context=derived["context"])
    check("revoked_optin_blocks_child", r.get("ok") is False,
          str(r.get("reason")))


def test_valid_supersede_derivation():
    """Positive control: valid supersede -> successor confirm works."""
    clean()
    from form.mandell import supersession as S
    p = open_program(OWNER)
    pr = p.nursery.add("DeriveG", words="v1")
    ctx = p.make_review_context(pr.id, "test")
    assert p.confirm_proposal(pr.id, _producer="test", _review_context=ctx).get("ok")
    sctx = p.make_supersede_context(pr.id, "test", "v2 words", "V2")
    res = S.supersede_proposal(p, pr.id, "v2 words", label="V2",
                               _producer="test", _review_context=sctx)
    check("valid_derivation_ok", res.get("ok") is True, str(res.get("reason")))




def test_revoke_between_auth_and_execution():
    """Revocation injected between auth and execution denies; no transition."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("ExecRev", words="w")
    issued = p.make_review_context(pr.id, "test")
    approval_id = issued["approval_id"]
    # Wrap check to revoke after the first (initial) check passes
    policy = p.acceptance_policy
    orig_check = policy.check
    calls = {"n": 0}
    def injecting_check(producer, pid, review_context=None,
                        proposal_version=None, operation="confirm"):
        calls["n"] += 1
        res = orig_check(producer, pid, review_context,
                         proposal_version, operation)
        if calls["n"] == 1 and res.get("allowed"):
            # First check passed; revoke before the live execution check
            policy.revoke_approval(approval_id)
        return res
    policy.check = injecting_check
    try:
        r = p.confirm_proposal(pr.id, _producer="test", _review_context=issued)
    finally:
        policy.check = orig_check
    check("exec_revoke_denied", r.get("ok") is False,
          str(r.get("reason")))
    check("exec_revoke_no_transition",
          p.nursery.proposals[pr.id].status == "pending",
          "proposal must remain pending")
    check("exec_revoke_two_checks", calls["n"] >= 2,
          f"expected live re-validation, got {calls['n']} checks")


def test_mutate_between_auth_and_execution():
    """Content change injected between auth and execution denies."""
    clean()
    p = open_program(OWNER)
    pr = p.nursery.add("ExecMut", words="original")
    issued = p.make_review_context(pr.id, "test")
    policy = p.acceptance_policy
    orig_check = policy.check
    calls = {"n": 0}
    def injecting_check(producer, pid, review_context=None,
                        proposal_version=None, operation="confirm"):
        calls["n"] += 1
        if calls["n"] == 1:
            # Mutate after the first check
            p.nursery.proposals[pid].words = "tampered"
        return orig_check(producer, pid, review_context,
                          proposal_version, operation)
    policy.check = injecting_check
    try:
        r = p.confirm_proposal(pr.id, _producer="test", _review_context=issued)
    finally:
        policy.check = orig_check
    check("exec_mutate_denied", r.get("ok") is False,
          str(r.get("reason")))
    check("exec_mutate_no_transition",
          p.nursery.proposals[pr.id].status == "pending")


def smoke():
    print("=== WO-5.1 ADVERSARIAL ACCEPTANCE ===")
    for fn in [test_forged_dict, test_stale_content, test_stale_parents,
               test_cross_session, test_revoked, test_valid_manual,
               test_revoked_opt_in, test_unknown_producer,
               test_supersede_changed_successor, test_idempotent_supersede,
               test_derive_unrelated_target, test_derive_wrong_source_operation,
               test_derive_changed_successor_data,
               test_parent_revocation_invalidates_child,
               test_optin_revocation_invalidates_child,
               test_valid_supersede_derivation,
               test_revoke_between_auth_and_execution,
               test_mutate_between_auth_and_execution]:
        try:
            fn()
        except Exception as e:
            check(fn.__name__, False, f"EXC {type(e).__name__}: {e}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
