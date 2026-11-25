"""Writer-boundary authorization tests (Director 2026-10-05 boundary).

Injects revocation/content mutation AFTER Program delegates to the
writer, at the actual writer stages (pre-place, pre-commit). Verifies
memory, durable state, receipt, and restart.

Evidence class: INTEGRATION (real Program, real writer).
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def fresh_program(owner):
    from form.open import open_program
    for pat in [f'form/state/nursery_{owner}.json', f'form/state/program_{owner}.json']:
        pp = os.path.join(REPO, pat)
        if os.path.isfile(pp):
            os.remove(pp)
    # Clear checkpoints
    import glob
    for pat in glob.glob(os.path.join(REPO, 'form', 'state', f'checkpoint_{owner}_*.json')):
        os.remove(pat)
    p = open_program(owner)
    p.acceptance_policy.grant_opt_in(owner, scope="test")
    return p


def make_pending(p, owner, label="WB", use_approval=True):
    pr = p.nursery.add(label, words="original content")
    ctx = p.make_review_context(pr.id, owner) if use_approval else None
    return pr, ctx


def test_pre_place_revocation():
    """Revoke after delegation, before writer pre-place validation."""
    from form.dell_matrix import confirm_lineage as cl
    owner = "WB_PREPLACE"
    p = fresh_program(owner)
    pr, ctx = make_pending(p, owner, use_approval=False)

    orig_assign = cl.assign_lineage
    def injecting_assign(units, parents, **kw):
        # Revoke AFTER Program delegated (we're inside the writer now)
        p.acceptance_policy.revoke_opt_in(owner)
        return orig_assign(units, parents, **kw)
    cl.assign_lineage = injecting_assign
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=ctx)
    finally:
        cl.assign_lineage = orig_assign
    check("pre_place_revocation:denied", r.get("ok") is False)
    check("pre_place_revocation:reason", r.get("reason") == "acceptance_policy_denied",
          str(r.get("reason")))
    check("pre_place_revocation:stage", r.get("stage") == "pre_place", str(r.get("stage")))
    check("pre_place_revocation:still_pending", pr.status == "pending", pr.status)
    # No idea placed
    check("pre_place_revocation:no_unit", pr.id not in p.cube.session.plane.units)


def test_pre_place_content_mutation():
    """Mutate content after delegation; hash mismatch denies."""
    from form.dell_matrix import confirm_lineage as cl
    owner = "WB_MUTATE"
    p = fresh_program(owner)
    pr, ctx = make_pending(p, owner)

    orig_assign = cl.assign_lineage
    def mutating_assign(units, parents, **kw):
        pr.words = "TAMPERED CONTENT"
        return orig_assign(units, parents, **kw)
    cl.assign_lineage = mutating_assign
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=ctx)
    finally:
        cl.assign_lineage = orig_assign
    check("pre_place_mutation:denied", r.get("ok") is False)
    check("pre_place_mutation:stage", r.get("stage") == "pre_place", str(r.get("stage")))
    check("pre_place_mutation:detail", "changed after approval" in str(r.get("detail")),
          str(r.get("detail")))
    check("pre_place_mutation:still_pending", pr.status == "pending")


def test_pre_commit_revocation():
    """Revoke after placement, before durable publish. Compensation runs."""
    owner = "WB_PRECOMMIT"
    p = fresh_program(owner)
    pr, ctx = make_pending(p, owner, use_approval=False)

    orig_place = p.place
    def injecting_place(*a, **kw):
        # Revoke AFTER pre-place validation, BEFORE pre-commit validation
        p.acceptance_policy.revoke_opt_in(owner)
        return orig_place(*a, **kw)
    p.place = injecting_place
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=ctx)
    finally:
        p.place = orig_place
    check("pre_commit_revocation:denied", r.get("ok") is False)
    check("pre_commit_revocation:stage", r.get("stage") == "pre_commit", str(r.get("stage")))
    check("pre_commit_revocation:reverted_pending", pr.status == "pending", pr.status)
    check("pre_commit_revocation:no_unit", pr.id not in p.cube.session.plane.units,
          "placed idea not compensated")
    # Durable state: reload, still pending, no unit
    from form import persist_rest
    persist_rest.save(p)
    p2 = persist_rest.load(owner, activate=False)
    pr2 = p2.nursery.proposals.get(pr.id)
    check("pre_commit_revocation:durable_pending",
          pr2 is not None and pr2.status == "pending",
          getattr(pr2, "status", None))
    check("pre_commit_revocation:durable_no_unit",
          pr.id not in p2.cube.session.plane.units)


def test_pre_commit_approval_revocation():
    """Revoke the approval (not opt-in) after placement; writer denies."""
    owner = "WB_APPREV"
    p = fresh_program(owner)
    pr, ctx = make_pending(p, owner, use_approval=True)
    approval_id = ctx.get("approval_id")

    orig_place = p.place
    def injecting_place(*a, **kw):
        p.acceptance_policy.revoke_approval(approval_id)
        return orig_place(*a, **kw)
    p.place = injecting_place
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=ctx)
    finally:
        p.place = orig_place
    check("approval_revocation:denied", r.get("ok") is False)
    check("approval_revocation:stage", r.get("stage") == "pre_commit", str(r.get("stage")))
    check("approval_revocation:reverted", pr.status == "pending", pr.status)


def test_supersession_derived_boundary():
    """Revoke source opt-in during successor placement; writer denies."""
    from form.mandell.supersession import supersede_proposal
    owner = "WB_SUPER"
    p = fresh_program(owner)
    # Confirm predecessor
    pr = p.nursery.add("Pred", words="v1")
    ctx = p.make_review_context(pr.id, owner)
    r = p.confirm_proposal(pr.id, _producer=owner, _review_context=ctx)
    assert r.get("ok"), f"setup confirm failed: {r}"

    orig_place = p.place
    def injecting_place(*a, **kw):
        # Revoke source opt-in after derived approval created, before
        # successor writer pre-commit validation
        p.acceptance_policy.revoke_opt_in(owner)
        return orig_place(*a, **kw)
    p.place = injecting_place
    try:
        try:
            supersede_proposal(p, pr.id, words="v2", _producer=owner)
            denied = False
        except Exception as e:
            denied = "acceptance_policy_denied" in str(e) or "confirm_failed" in str(e)
    finally:
        p.place = orig_place
    check("supersede_derived:denied", denied, "supersession should fail on revoked auth")
    # Predecessor still confirmed (not superseded)
    check("supersede_derived:pred_intact", pr.status == "confirmed", pr.status)


def test_positive_control():
    """Normal confirm still works through the writer boundary."""
    owner = "WB_POS"
    p = fresh_program(owner)
    pr, ctx = make_pending(p, owner)
    r = p.confirm_proposal(pr.id, _producer=owner, _review_context=ctx)
    check("positive:ok", r.get("ok") is True, str(r))
    check("positive:confirmed", pr.status == "confirmed", pr.status)
    check("positive:unit_placed", pr.id in p.cube.session.plane.units)


def smoke():
    print("=== WRITER-BOUNDARY AUTHORIZATION ===")
    for fn in [test_pre_place_revocation, test_pre_place_content_mutation,
               test_pre_commit_revocation, test_pre_commit_approval_revocation,
               test_supersession_derived_boundary, test_positive_control]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False, f"EXC {type(e).__name__}: {e}\n{traceback.format_exc()[:500]}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
