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


def smoke():
    print("=== WO-5.1 ADVERSARIAL ACCEPTANCE ===")
    for fn in [test_forged_dict, test_stale_content, test_stale_parents,
               test_cross_session, test_revoked, test_valid_manual,
               test_revoked_opt_in, test_unknown_producer,
               test_supersede_changed_successor, test_idempotent_supersede]:
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
