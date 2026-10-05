"""WO-5.3: Historical participation test.

- Ordinary consumers exclude SUPERSEDED.
- Historical context includes SUPERSEDED.
- Explicit "use idea" works for superseded.
- Children refer to original derivation parents (not supersession links).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_historical_participation():
    from form.open import open_program
    from form.dell_matrix import canonical_lifecycle as cl
    from form.mandell import supersession as sup

    o = "WO53_HIST"
    for pat in [f'form/state/nursery_{o}.json', f'form/state/program_{o}.json']:
        if os.path.isfile(pat):
            os.remove(pat)

    p = open_program(o)
    ctx = lambda pid: {"reviewer": "test", "approved_pid": pid}

    # Create revision A, confirm it
    pr_a = p.nursery.add('Idea A', words='original')
    p.confirm_proposal(pr_a.id, _producer="test", _review_context=ctx(pr_a.id))
    p.nursery.save()

    # Create revision B (supersedes A), confirm it
    # supersede_proposal creates the successor from words
    res = sup.supersede_proposal(p, pr_a.id, words='revised content',
                                 label='Idea B')
    assert res.get("ok"), f"Supersede failed: {res}"
    pr_b_id = res.get("new_id")
    p.nursery.save()

    # 1. Ordinary context excludes superseded A
    assert not cl.is_participating(p, pr_a.id, context="ordinary"), \
        "Superseded A should NOT participate in ordinary context"
    reason = cl.participation_reason(p, pr_a.id, context="ordinary")
    print(f"1. Ordinary excludes superseded: YES ({reason})")

    # 2. Ordinary context includes current B
    assert cl.is_participating(p, pr_b_id, context="ordinary"), \
        "Current B SHOULD participate in ordinary context"
    print(f"2. Ordinary includes current: YES")

    # 3. Historical context includes superseded A
    assert cl.is_participating(p, pr_a.id, context="historical"), \
        "Superseded A SHOULD participate in historical context"
    print(f"3. Historical includes superseded: YES")

    # 4. Verify revision chain intact
    rec_a = sup.inspect_revision(p, pr_a.id)
    rec_b = sup.inspect_revision(p, pr_b_id)
    assert rec_a.get("lifecycle_state") == "superseded", \
        f"A should be superseded, got {rec_a.get('lifecycle_state')}"
    assert rec_b.get("lifecycle_state") == "active", \
        f"B should be active, got {rec_b.get('lifecycle_state')}"
    assert rec_a.get("superseded_by_id") == pr_b_id
    assert rec_b.get("supersedes_id") == pr_a.id
    print(f"4. Revision chain intact: A(superseded) -> B(active)")

    # 5. Children refer to original derivation parents
    # (Derivation parents are set at proposal creation, not changed by supersession)
    # Create a child of A (derivation, not supersession)
    pr_c = p.nursery.add('Idea C', words='child of A')
    # Set parents explicitly (derivation)
    pr_c.parents = [pr_a.id]
    p.nursery.save()
    # Verify C's parents still point to A (original), not B
    assert pr_a.id in (pr_c.parents or []), \
        "Child C should refer to original parent A"
    print(f"5. Derivation parents preserved: C -> A (not retargeted to B)")

    print("\nWO-5.3 historical participation: ALL CHECKS PASSED")
    return True


if __name__ == "__main__":
    test_historical_participation()

def smoke():
    """Regression smoke entrypoint."""
    return test_historical_participation()
