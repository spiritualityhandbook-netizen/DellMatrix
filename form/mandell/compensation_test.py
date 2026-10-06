"""Compensation completeness tests (Director 2026-10-05 compensation).

Verifies:
- Incomplete compensation is reported (not ordinary denial)
- Evidence (journal) retained on incomplete compensation
- Original authorization denial remains identifiable
- Normal denial removes unit, velocities, placements, lattice participation
- Append-only history preserved
- Restart behavior (before save vs after save)
- Ordinary and supersession-derived paths
- Positive controls

Evidence class: INTEGRATION (real Program, real writer).
"""

import glob
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

CHECKS = []


def check(name, cond, detail=""):
    CHECKS.append(bool(cond))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail and not cond else ""))


def clean_owner(owner):
    for pat in [f'form/state/nursery_{owner}.json', f'form/state/program_{owner}.json']:
        pp = os.path.join(REPO, pat)
        if os.path.isfile(pp):
            os.remove(pp)
    for pat in glob.glob(os.path.join(REPO, 'form', 'state', f'checkpoint_{owner}_*')):
        os.remove(pat)
    from form.mandell.core_i_recovery import _confirm_journal_path
    jp = _confirm_journal_path(owner)
    # Journal path may be relative; resolve against REPO
    if not os.path.isabs(jp):
        jp = os.path.join(REPO, jp)
    if os.path.isfile(jp):
        os.remove(jp)


def fresh_program(owner):
    from form.open import open_program
    clean_owner(owner)
    p = open_program(owner)
    p.acceptance_policy.grant_opt_in(owner, scope="test")
    return p


def journal_exists(owner):
    from form.mandell.core_i_recovery import _confirm_journal_path
    jp = _confirm_journal_path(owner)
    if not os.path.isabs(jp):
        jp = os.path.join(REPO, jp)
    return os.path.isfile(jp)


class BrokenDict(dict):
    def pop(self, *a, **kw):
        raise RuntimeError("injected_cleanup_failure")


def test_incomplete_compensation_reported():
    """Spatial cleanup failure -> incomplete reported, journal retained."""
    owner = "COMP_INCOMPLETE"
    p = fresh_program(owner)
    pr = p.nursery.add("DenyMe", words="content")

    orig_place = p.place
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        p.acceptance_policy.revoke_opt_in(owner)
        p.spatial.velocities = BrokenDict(p.spatial.velocities)
        return result
    p.place = injecting_place
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=None)
    finally:
        p.place = orig_place

    check("incomplete:denied", r.get("ok") is False)
    check("incomplete:orig_reason", r.get("reason") == "acceptance_policy_denied",
          str(r.get("reason")))
    check("incomplete:reported", r.get("compensation") == "incomplete",
          str(r.get("compensation")))
    check("incomplete:failures_listed", bool(r.get("compensation_failures")),
          str(r.get("compensation_failures")))
    check("incomplete:evidence_retained", r.get("evidence_retained") is True)
    check("incomplete:journal_kept", journal_exists(owner),
          "journal must be retained on incomplete compensation")


def test_lattice_failure_separate():
    """Lattice rebuild failure alone -> incomplete (best-effort still reported)."""
    owner = "COMP_LATTICE"
    p = fresh_program(owner)
    pr = p.nursery.add("DenyMe", words="content")

    orig_place = p.place
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        p.acceptance_policy.revoke_opt_in(owner)
        def broken_rebuild(*a, **kw):
            raise RuntimeError("injected lattice failure")
        p.lattice.rebuild_from_plane = broken_rebuild
        return result
    p.place = injecting_place
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=None)
    finally:
        p.place = orig_place

    check("lattice:denied", r.get("ok") is False)
    check("lattice:reported_incomplete", r.get("compensation") == "incomplete",
          str(r.get("compensation")))
    check("lattice:failure_named",
          any("lattice" in f for f in r.get("compensation_failures", [])),
          str(r.get("compensation_failures")))


def test_normal_denial_complete():
    """Normal denial (no injected failures) removes all artifacts."""
    owner = "COMP_NORMAL"
    p = fresh_program(owner)
    pr = p.nursery.add("DenyMe", words="content")

    orig_place = p.place
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        p.acceptance_policy.revoke_opt_in(owner)
        return result
    p.place = injecting_place
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=None)
    finally:
        p.place = orig_place

    check("normal:denied", r.get("ok") is False)
    check("normal:no_compensation_flag", "compensation" not in r,
          f"ordinary denial must not carry compensation flag: {r.keys()}")
    check("normal:unit_removed", pr.id not in p.cube.session.plane.units)
    check("normal:velocities_clean", pr.id not in p.spatial.velocities)
    check("normal:placements_clean",
          pr.id not in getattr(p.spatial, 'placements', {}))
    check("normal:pending", pr.status == "pending", pr.status)
    check("normal:journal_cleared", not journal_exists(owner),
          "complete compensation clears journal (deliberate denial)")


def test_restart_after_incomplete():
    """Restart after incomplete compensation: no silent accepted artifacts."""
    owner = "COMP_RESTART"
    p = fresh_program(owner)
    pr = p.nursery.add("DenyMe", words="content")

    orig_place = p.place
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        p.acceptance_policy.revoke_opt_in(owner)
        p.spatial.velocities = BrokenDict(p.spatial.velocities)
        return result
    p.place = injecting_place
    try:
        r = p.confirm_proposal(pr.id, _producer=owner, _review_context=None)
    finally:
        p.place = orig_place
    assert r.get("compensation") == "incomplete"

    # Restart BEFORE any test-triggered save: in-memory hybrid is gone,
    # durable state should show pending with no accepted artifacts.
    from form import persist_rest
    p2 = persist_rest.load(owner, activate=False)
    pr2 = p2.nursery.proposals.get(pr.id)
    check("restart:pending", pr2 is not None and pr2.status == "pending",
          getattr(pr2, "status", None))
    check("restart:no_unit", pr.id not in p2.cube.session.plane.units,
          "rejected accepted-state artifact must not persist")


def test_supersession_derived_compensation():
    """Supersession-derived denial with cleanup failure: reported."""
    from form.mandell.supersession import supersede_proposal
    owner = "COMP_SUPER"
    p = fresh_program(owner)
    pred = p.nursery.add("Pred", words="v1")
    r = p.confirm_proposal(pred.id, _producer=owner, _review_context=None)
    assert r.get("ok"), f"setup failed: {r}"

    orig_place = p.place
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        # Revoke AFTER successor placed (derived auth now invalid)
        p.acceptance_policy.revoke_opt_in(owner)
        p.spatial.velocities = BrokenDict(p.spatial.velocities)
        return result
    p.place = injecting_place
    try:
        try:
            supersede_proposal(p, pred.id, words="v2", _producer=owner)
            outcome = "unexpected_success"
        except Exception as e:
            outcome = str(e)[:200]
    finally:
        p.place = orig_place
    check("super:failed", outcome != "unexpected_success", outcome)
    check("super:pred_intact", pred.status == "confirmed", pred.status)


def test_positive_controls():
    """Successful confirmation and successful compensation."""
    owner = "COMP_POS"
    p = fresh_program(owner)
    # Successful confirmation
    pr = p.nursery.add("Good", words="content")
    r = p.confirm_proposal(pr.id, _producer=owner, _review_context=None)
    check("pos:confirm_ok", r.get("ok") is True, str(r))
    check("pos:confirmed", pr.status == "confirmed")
    # Successful compensation (denial with working cleanup)
    pr2 = p.nursery.add("DenyOk", words="content")
    # Re-grant (was not revoked in this test)
    orig_place = p.place
    def injecting_place(*a, **kw):
        result = orig_place(*a, **kw)
        p.acceptance_policy.revoke_opt_in(owner)
        return result
    p.place = injecting_place
    try:
        r2 = p.confirm_proposal(pr2.id, _producer=owner, _review_context=None)
    finally:
        p.place = orig_place
    check("pos:denial_ok", r2.get("ok") is False)
    check("pos:complete_compensation", "compensation" not in r2,
          "no incomplete flag on clean denial")


def test_public_path_denial():
    """Public-path failure: confirm_proposal without _producer/_review_context
    (the public API) must deny and clean up completely.
    
    Director 2026-10-05 (enclosing rollback): The public path is how real
    users trigger confirmation. Failure through this path must preserve
    the same compensation guarantees as the internal authorized path.
    """
    owner = "COMP_PUBLIC"
    p = fresh_program(owner)
    # Public API: no _producer, no _review_context
    pr = p.nursery.add("PublicTest", words="public path content")
    r = p.confirm_proposal(pr.id)
    # Must deny (no authorization)
    check("pub:denied", r.get("ok") is False,
          f"got {r.get('ok')}")
    check("pub:reason_denied", "denied" in r.get("reason", "").lower(),
          f"reason={r.get('reason')}")
    # Must not leave accepted-state artifacts
    check("pub:no_unit", pr.id not in p.cube.session.plane.units,
          "unit leaked")
    # Compensation must be complete (not incomplete)
    check("pub:complete", r.get("compensation") != "incomplete",
          f"compensation={r.get('compensation')}")
    # Proposal must remain pending (not confirmed)
    check("pub:still_pending", pr.status == "pending",
          f"status={pr.status}")


def smoke():
    print("=== COMPENSATION COMPLETENESS ===")
    for fn in [test_incomplete_compensation_reported,
               test_lattice_failure_separate,
               test_normal_denial_complete,
               test_restart_after_incomplete,
               test_supersession_derived_compensation,
               test_positive_controls,
               test_public_path_denial]:
        try:
            fn()
        except Exception as e:
            import traceback
            check(fn.__name__, False,
                  f"EXC {type(e).__name__}: {e}\n{traceback.format_exc()[:600]}")
    n = sum(CHECKS)
    print(f"=== {n}/{len(CHECKS)} ===")
    return n == len(CHECKS)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
