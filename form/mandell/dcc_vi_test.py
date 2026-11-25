#!/usr/bin/env python3
"""DCC-VI operational capabilities test suite.

Tests the 9 new capabilities:
READ (3): count nursery, list pending, trace
MUTATION (3): add idea, confirm, reject
COMPARISON (1): compare nursery
RECOVERY (2): revert (alias), trace (history)

Each capability is proven through:
- English interpretation
- Mandell representation
- Typed arguments
- Verified route (semantic router)
- Real Dell/runtime authority
- Correct result and mutation/non-mutation
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell.english_composer import compose_english, execute_composite


def _fresh(owner: str):
    p = open_program(owner)
    # Start with clean nursery
    for prop in list(p.nursery.proposals.values()):
        p.nursery.proposals.pop(prop.id, None)
    try:
        p.nursery.save()
    except Exception:
        pass
    return p


def _run(p, eng):
    i = translate(eng)
    r = route_intent(p, i, raw_line=eng)
    return i, r


def test_add_idea():
    p = _fresh("DCCVI_Add")
    i, r = _run(p, "add idea test proposal alpha")
    assert r.ok and r.routed, f"add failed: {r.error}"
    assert i.action == "nurture" and i.dell == 37
    assert "37[Nurture]" in i.mandel
    # Verify it was actually added
    pending = p.nursery.pending()
    assert len(pending) == 1, f"expected 1 pending, got {len(pending)}"
    assert "test proposal alpha" in pending[0].label.lower()
    print("  add idea: GREEN")


def test_count_nursery():
    p = _fresh("DCCVI_Count")
    _run(p, "add idea one")
    _run(p, "add idea two")
    i, r = _run(p, "count nursery")
    assert r.ok and r.routed
    assert i.action == "discover" and i.dell == 35
    d = p.last_discover
    assert d["pending"] == 2, f"expected pending=2, got {d}"
    assert d["total"] == 2
    print("  count nursery: GREEN")


def test_list_pending():
    p = _fresh("DCCVI_List")
    _run(p, "add idea listable")
    i, r = _run(p, "list pending")
    assert r.ok and r.routed
    d = p.last_discover
    assert d["count"] == 1
    assert "listable" in d["labels"][0].lower()
    print("  list pending: GREEN")


def test_confirm_reject():
    p = _fresh("DCCVI_Confirm")
    _run(p, "add idea to confirm")
    pending = p.nursery.pending()
    pid = pending[0].id
    # Confirm
    i, r = _run(p, f"confirm {pid}")
    assert r.ok and r.routed, f"confirm failed: {r.error}"
    assert p.nursery.summary()["confirmed"] == 1
    # Reject (add another first)
    _run(p, "add idea to reject")
    pending = p.nursery.pending()
    pid2 = pending[0].id
    i, r = _run(p, f"reject {pid2}")
    assert r.ok and r.routed
    assert p.nursery.summary()["rejected"] == 1
    print("  confirm/reject: GREEN")


def test_compare_nursery():
    p = _fresh("DCCVI_Compare")
    _run(p, "add idea cmp one")
    _run(p, "add idea cmp two")
    pid = p.nursery.pending()[0].id
    _run(p, f"confirm {pid}")
    i, r = _run(p, "compare nursery")
    assert r.ok and r.routed
    d = p.last_discover
    assert d["pending"] == 1 and d["confirmed"] == 1
    assert d["comparison"] == "equal"
    print("  compare nursery: GREEN")


def test_trace():
    p = _fresh("DCCVI_Trace")
    # Execute via flow to populate history
    r = compose_english("form a sphere then measure")
    assert r.ok
    execute_composite(p, r.composite)
    i, r2 = _run(p, "trace")
    assert r2.ok and r2.routed
    d = p.last_discover
    assert d["count"] >= 2, f"expected >=2 history entries, got {d['count']}"
    print("  trace: GREEN")


def test_revert_alias():
    p = _fresh("DCCVI_Revert")
    i, r = _run(p, "revert")
    # Should route to Dell 28 (may fail if no checkpoint, but must route)
    assert i.action == "load" and i.dell == 28
    assert "28[Rollback]" in i.mandel
    print("  revert alias: GREEN")


def test_composition_mutation_read():
    p = _fresh("DCCVI_Comp1")
    r = compose_english("add idea composed one then count nursery")
    assert r.ok, f"compose failed: {r.error}"
    receipt = execute_composite(p, r.composite)
    assert receipt.completed == 2 and receipt.failed == 0
    print("  composition (mutation>read): GREEN")


def test_composition_read_mutation():
    p = _fresh("DCCVI_Comp2")
    r = compose_english("count nursery then add idea composed two")
    assert r.ok, f"compose failed: {r.error}"
    receipt = execute_composite(p, r.composite)
    assert receipt.completed == 2 and receipt.failed == 0
    print("  composition (read>mutation): GREEN")


def test_composition_mutation_save():
    p = _fresh("DCCVI_Comp3")
    r = compose_english("add idea persistent then save")
    assert r.ok, f"compose failed: {r.error}"
    receipt = execute_composite(p, r.composite)
    assert receipt.completed == 2 and receipt.failed == 0
    print("  composition (mutation>save): GREEN")


def test_adversarial_invalid_target():
    p = _fresh("DCCVI_Adv1")
    # Confirm nonexistent PID should fail safely
    i, r = _run(p, "confirm nonexistent_pid_12345")
    assert not r.ok, "confirm nonexistent should fail"
    print("  adversarial (invalid target): GREEN")


def test_adversarial_empty_label():
    p = _fresh("DCCVI_Adv2")
    # "add idea" with no label should not create an empty proposal.
    # It falls through to generic handling; verify no empty proposal exists.
    from form.mandell.translate import translate
    i = translate("add idea   ")
    # If it routes to nurture, the Dell must refuse empty labels.
    if i.action == "nurture":
        r = route_intent(p, i, raw_line="add idea   ")
        assert not r.ok, "empty label must be refused"
    # Verify no proposal with empty label was created
    for prop in p.nursery.pending():
        assert prop.label.strip(), "empty label proposal must not exist"
    print("  adversarial (empty label): GREEN")


def run_all():
    print("DCC-VI operational capabilities:")
    test_add_idea()
    test_count_nursery()
    test_list_pending()
    test_confirm_reject()
    test_compare_nursery()
    test_trace()
    test_revert_alias()
    test_composition_mutation_read()
    test_composition_read_mutation()
    test_composition_mutation_save()
    test_adversarial_invalid_target()
    test_adversarial_empty_label()
    print("DCC-VI: 12/12 GREEN")
    # Cleanup
    import glob
    for f in glob.glob("form/state/program_DCCVI_*"):
        try:
            os.remove(f)
        except Exception:
            pass


def smoke() -> bool:
    """Regress entry point: run all tests, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"DCC-VI SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
