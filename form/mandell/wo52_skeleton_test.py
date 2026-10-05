"""WO-5.2 walking skeleton: propose → confirm → fade → exclusion → history → unfade → save/restart.

Tests the canonical participation contract:
- Ordinary consumers exclude faded records.
- Explicit historical inspection includes them.
- Identity/content preserved through fade/unfade.
- Save/restart preserves the same state.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_walking_skeleton():
    from form.open import open_program
    from form import persist_rest
    from form.dell_matrix import canonical_lifecycle as cl
    from form import lifecycle as lc
    import uuid

    o = "WO52_SKELETON"
    for pat in [f'form/state/nursery_{o}.json', f'form/state/program_{o}.json']:
        if os.path.isfile(pat):
            os.remove(pat)

    p = open_program(o)

    # 1. Propose
    pr = p.nursery.add('Skeleton Idea', words='test content for skeleton')
    pid = pr.id
    p.nursery.save()
    print(f"1. Proposed: {pid}")

    # 2. Review/confirm (with review context)
    r = p.confirm_proposal(
        pid,
        _producer="test",
        _review_context={"reviewer": "test", "approved_pid": pid},
    )
    assert r.get("ok"), f"Confirm failed: {r}"
    p.nursery.save()
    persist_rest.save(p)
    print(f"2. Confirmed: {pid}")

    # Get the unit ID (idea ID in plane)
    # The proposal ID becomes the unit ID after confirmation
    unit_id = pid

    # 3. Verify ordinary participation (should participate)
    assert cl.is_participating(p, unit_id, context="ordinary"), \
        "Should participate in ordinary context before fade"
    print(f"3. Ordinary participation: YES")

    # 4. Fade
    iid = str(uuid.uuid4())
    p2, msg = lc.do_fade(p, unit_id, iid)
    print(f"4. Fade: {msg}")
    assert "Faded" in msg or "faded" in msg.lower()

    # 5. Normal query exclusion (ordinary context)
    assert not cl.is_participating(p, unit_id, context="ordinary"), \
        "Faded should NOT participate in ordinary context"
    reason = cl.participation_reason(p, unit_id, context="ordinary")
    print(f"5. Ordinary participation after fade: NO ({reason})")

    # 6. Explicit history inspection (historical context)
    assert cl.is_participating(p, unit_id, context="historical"), \
        "Faded SHOULD participate in historical context"
    print(f"6. Historical participation: YES")

    # 7. Verify identity/content preserved
    # (The unit still exists in plane, just faded)
    assert unit_id in p.cube.session.plane.units, \
        "Faded unit must still exist (identity preserved)"
    print(f"7. Identity preserved: YES")

    # 8. Unfade
    p3, msg2 = lc.do_unfade(p, unit_id, iid)
    print(f"8. Unfade: {msg2}")

    # 9. Ordinary participation restored
    assert cl.is_participating(p, unit_id, context="ordinary"), \
        "Should participate in ordinary context after unfade"
    print(f"9. Ordinary participation after unfade: YES")

    # 10. Save/restart → same identity/content
    persist_rest.save(p)
    from form.persist_rest import load as persist_load
    p_restarted = persist_load(o, activate=False)
    assert cl.is_participating(p_restarted, unit_id, context="ordinary"), \
        "Should participate after restart"
    assert unit_id in p_restarted.cube.session.plane.units, \
        "Unit must exist after restart"
    print(f"10. Save/restart: identity preserved, participating")

    print("\nWO-5.2 walking skeleton: ALL CHECKS PASSED")
    return True


if __name__ == "__main__":
    test_walking_skeleton()
