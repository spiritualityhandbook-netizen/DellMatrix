#!/usr/bin/env python3
"""DCC-VII: Knowledge lifecycle tests.

Verifies the complete lifecycle: add -> pending -> confirm/promote ->
query -> persist -> fresh restore -> query again.

Authority: Nursery (proposals) + Cube plane.units (promoted knowledge).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from form.open import open_program
from form.persist_rest import save, load
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent


def _fresh(name):
    p = open_program(name)
    return p


def _run(p, eng):
    intent = translate(eng)
    result = route_intent(p, intent, raw_line=eng)
    return intent, result


def test_add_pending():
    """Add creates a pending proposal."""
    p = _fresh("DCCVII_Test_Add")
    prop = p.nursery.add("test knowledge item")
    assert prop.status == "pending", f"expected pending, got {prop.status}"
    assert prop.id in p.nursery.proposals
    return True


def test_confirm_promotes():
    """Confirm via canonical path promotes to cube."""
    p = _fresh("DCCVII_Test_Confirm")
    prop = p.nursery.add("promote me")
    result = p.confirm_proposal(prop.id)
    assert result.get("ok"), f"confirm failed: {result}"
    assert p.nursery.proposals[prop.id].status == "confirmed"
    assert prop.id in p.cube.session.plane.units, "not promoted to cube"
    return True


def test_reject_excluded():
    """Rejected proposals are not accepted knowledge."""
    p = _fresh("DCCVII_Test_Reject")
    a = p.nursery.add("idea alpha")
    b = p.nursery.add("idea beta")
    p.confirm_proposal(a.id)
    p.nursery.reject(b.id)

    # Accepted query contains A, excludes B
    confirmed = [pr for pr in p.nursery.proposals.values()
                if pr.status == "confirmed"]
    confirmed_ids = {pr.id for pr in confirmed}
    assert a.id in confirmed_ids, "A should be confirmed"
    assert b.id not in confirmed_ids, "B should NOT be confirmed"

    # B is in cube? No - rejected proposals are NOT promoted
    assert b.id not in p.cube.session.plane.units, "rejected should not be promoted"

    # Pending excludes both
    pending_ids = {pr.id for pr in p.nursery.pending()}
    assert a.id not in pending_ids, "A should not be pending"
    assert b.id not in pending_ids, "B should not be pending"
    return True


def test_list_confirmed():
    """list confirmed queries accepted knowledge."""
    p = _fresh("DCCVII_Test_ListConf")
    prop = p.nursery.add("listable knowledge")
    p.confirm_proposal(prop.id)

    intent, result = _run(p, "list confirmed")
    assert result.ok, f"list confirmed failed"
    assert intent.mandel == "35[Discover] :: list_confirmed"
    disc = p.last_discover
    assert disc["count"] >= 1, "should have at least 1 confirmed"
    assert prop.id in disc["ids"], "confirmed ID should be listed"
    return True


def test_count_confirmed():
    """count confirmed reports confirmed and promoted counts."""
    p = _fresh("DCCVII_Test_CountConf")
    prop = p.nursery.add("countable knowledge")
    p.confirm_proposal(prop.id)

    intent, result = _run(p, "count confirmed")
    assert result.ok
    disc = p.last_discover
    assert disc["confirmed"] >= 1
    assert disc["promoted"] >= 1, "should be promoted to cube"
    return True


def test_find_idea():
    """find idea queries promoted knowledge by text."""
    p = _fresh("DCCVII_Test_Find")
    prop = p.nursery.add("unique searchable knowledge xyz")
    p.confirm_proposal(prop.id)

    intent, result = _run(p, "find idea xyz")
    assert result.ok
    disc = p.last_discover
    assert disc["count"] >= 1, "should find the idea"
    assert any(prop.id == m["id"] for m in disc["matches"])
    return True


def test_persistence_roundtrip():
    """Full lifecycle: add -> confirm -> save -> fresh load -> query."""
    name = "DCCVII_Test_Persist"
    p = _fresh(name)
    prop = p.nursery.add("persistent knowledge")
    pid = prop.id
    p.confirm_proposal(pid)
    save(p)
    del p

    # Fresh process load
    p2 = load(name)
    assert pid in p2.nursery.proposals, "proposal should survive"
    assert p2.nursery.proposals[pid].status == "confirmed"
    assert pid in p2.cube.session.plane.units, "promoted knowledge should survive"

    # Query it again
    intent, result = _run(p2, "find idea persistent")
    assert result.ok
    assert p2.last_discover["count"] >= 1
    return True


def test_duplicate_policy():
    """Duplicate adds are allowed; each gets unique ID."""
    p = _fresh("DCCVII_Test_Dup")
    a = p.nursery.add("duplicate idea")
    b = p.nursery.add("duplicate idea")
    # IDs should be unique (not silently deduplicated)
    assert a.id != b.id, "duplicate ideas should get unique IDs"
    # Both can be confirmed
    p.confirm_proposal(a.id)
    p.confirm_proposal(b.id)
    assert a.id in p.cube.session.plane.units
    assert b.id in p.cube.session.plane.units
    return True


def test_composition():
    """Lifecycle works through English/Mandell composition."""
    p = _fresh("DCCVII_Test_Compose")

    # add idea X -> count nursery
    i1, r1 = _run(p, "add idea composed knowledge")
    assert r1.ok
    i2, r2 = _run(p, "count nursery")
    assert r2.ok

    # confirm -> list confirmed
    pid = p.nursery.pending()[0].id
    i3, r3 = _run(p, f"confirm {pid}")
    assert r3.ok
    i4, r4 = _run(p, "list confirmed")
    assert r4.ok
    assert p.last_discover["count"] >= 1

    # find idea -> trace
    i5, r5 = _run(p, "find idea composed")
    assert r5.ok
    i6, r6 = _run(p, "trace")
    assert r6.ok
    return True


def test_unsupported_id_safe():
    """Confirm with nonexistent ID fails safely."""
    p = _fresh("DCCVII_Test_BadID")
    intent, result = _run(p, "confirm nonexistent_id_12345")
    assert not result.ok, "should fail for nonexistent ID"
    return True


def test_malformed_query_safe():
    """Empty find query doesn't crash."""
    p = _fresh("DCCVII_Test_BadQuery")
    # Direct call with empty query
    from form.mandell import core_i_ops
    # Use translate which should handle it
    intent = translate("find idea ")
    # Should either fail gracefully or fall through
    return True


def test_trace_visibility():
    """Lifecycle operations appear in trace (via flow executor)."""
    from form.mandell.english_composer import compose_english, execute_composite

    p = _fresh("DCCVII_Test_Trace")
    # Execute via flow to populate history
    r = compose_english("add idea traceable knowledge then list confirmed")
    assert r.ok, "composition should succeed"
    receipt = execute_composite(p, r.composite)
    assert receipt.completed >= 2, "both ops should complete"

    intent, result = _run(p, "trace")
    assert result.ok
    hist = p.last_discover.get("history", [])
    assert len(hist) >= 2, f"expected >=2 history entries, got {len(hist)}"
    return True


def main():
    tests = [
        ("add_pending", test_add_pending),
        ("confirm_promotes", test_confirm_promotes),
        ("reject_excluded", test_reject_excluded),
        ("list_confirmed", test_list_confirmed),
        ("count_confirmed", test_count_confirmed),
        ("find_idea", test_find_idea),
        ("persistence_roundtrip", test_persistence_roundtrip),
        ("duplicate_policy", test_duplicate_policy),
        ("composition", test_composition),
        ("unsupported_id_safe", test_unsupported_id_safe),
        ("malformed_query_safe", test_malformed_query_safe),
        ("trace_visibility", test_trace_visibility),
    ]
    passed = 0
    failed = []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"  FAIL: {name}: {e}")

    print(f"\nDCC-VII: {passed}/{len(tests)}")
    if failed:
        print("Failures:")
        for n, e in failed:
            print(f"  {n}: {e}")
        return 1
    print("DCC-VII: GREEN")
    return 0


def smoke() -> bool:
    """Regress entry point: run all tests, return True on success."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
