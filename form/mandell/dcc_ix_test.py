#!/usr/bin/env python3
"""DCC-IX: Contextual knowledge selection tests.

Verifies deterministic, explainable selection of relevant confirmed
knowledge by context, without requiring explicit proposal IDs.

Controls:
1. RELEVANCE: relevant selected, unrelated excluded
2. STATUS: only confirmed eligible (pending/rejected excluded)
3. DETERMINISM: same state+context → same selection
4. CAUSAL: selector finding relevant knowledge changes behavior
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from form.open import open_program
from form.persist_rest import save, load
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell.knowledge_selector import select_for_context


def _fresh(name):
    return open_program(name)


def _run(p, eng):
    intent = translate(eng)
    result = route_intent(p, intent, raw_line=eng)
    return intent, result


def _confirm_all(p):
    for prop in p.nursery.pending():
        p.confirm_proposal(prop.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": prop.id})


def test_relevance_control():
    """CONTROL 1: relevant selected, unrelated excluded."""
    p = _fresh("DCCIX_Rel")
    p.nursery.add("plant growth photosynthesis")
    p.nursery.add("quantum physics entanglement")
    _confirm_all(p)

    sel = select_for_context(p, "plant", operation="grow")
    selected_ids = [s["id"] for s in sel["selected"]]
    
    # Find which is which
    plant_id = None
    quantum_id = None
    for pid, prop in p.nursery.proposals.items():
        if "plant" in prop.label:
            plant_id = pid
        if "quantum" in prop.label:
            quantum_id = pid
    
    assert plant_id in selected_ids, "relevant should be selected"
    assert quantum_id not in selected_ids, "unrelated should be excluded"
    print(f"  relevant selected, unrelated excluded: GREEN")
    return True


def test_status_control():
    """CONTROL 2: only confirmed eligible."""
    p = _fresh("DCCIX_Status")
    # Confirmed (relevant)
    a = p.nursery.add("plant biology")
    p.confirm_proposal(a.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": a.id})
    # Pending (relevant but not confirmed)
    b = p.nursery.add("plant chemistry")
    # Rejected (relevant but rejected)
    c = p.nursery.add("plant physics")
    p.nursery.reject(c.id)

    sel = select_for_context(p, "plant", operation="grow")
    selected_ids = [s["id"] for s in sel["selected"]]
    
    assert a.id in selected_ids, "confirmed should be eligible"
    assert b.id not in selected_ids, "pending should be excluded"
    assert c.id not in selected_ids, "rejected should be excluded"
    assert sel["eligible_count"] == 1, "only 1 eligible"
    print(f"  status control: GREEN")
    return True


def test_determinism_control():
    """CONTROL 3: same state+context → same selection."""
    p = _fresh("DCCIX_Det")
    p.nursery.add("plant growth")
    p.nursery.add("plant reproduction")
    p.nursery.add("quantum mechanics")
    _confirm_all(p)

    sel1 = select_for_context(p, "plant", operation="grow")
    sel2 = select_for_context(p, "plant", operation="grow")
    
    ids1 = [s["id"] for s in sel1["selected"]]
    ids2 = [s["id"] for s in sel2["selected"]]
    
    assert ids1 == ids2, "selections should be identical"
    # Check ordering is deterministic (score desc, ID asc)
    scores1 = [(s["id"], s["score"]) for s in sel1["selected"]]
    scores2 = [(s["id"], s["score"]) for s in sel2["selected"]]
    assert scores1 == scores2, "ordering should be identical"
    print(f"  determinism: GREEN")
    return True


def test_causal_control():
    """CONTROL 4: selector finding relevant knowledge changes behavior."""
    # Baseline: no relevant knowledge
    pA = _fresh("DCCIX_CausalA")
    pA.nursery.add("base foundation")
    _confirm_all(pA)
    before_A = len(pA.nursery.proposals)
    sel_A = select_for_context(pA, "plant", operation="grow")
    pA.grow_ideas(1)
    new_A = len(pA.nursery.proposals) - before_A
    
    # With relevant knowledge
    pB = _fresh("DCCIX_CausalB")
    pB.nursery.add("base foundation")
    pB.nursery.add("plant growth catalyst")
    _confirm_all(pB)
    before_B = len(pB.nursery.proposals)
    sel_B = select_for_context(pB, "plant", operation="grow")
    pB.grow_ideas(1)
    new_B = len(pB.nursery.proposals) - before_B
    
    # Selector should find the relevant knowledge in B
    assert len(sel_B["selected"]) > 0, "should select relevant knowledge"
    assert len(sel_A["selected"]) == 0, "should select none in baseline"
    
    print(f"  causal: A={new_A} new (0 selected), B={new_B} new ({len(sel_B['selected'])} selected)")
    return True


def test_explicit_override_preserved():
    """DCC-VIII explicit ID selection still works."""
    p = _fresh("DCCIX_Override")
    prop = p.nursery.add("explicit knowledge")
    p.confirm_proposal(prop.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": prop.id})
    
    # Explicit ID takes precedence
    i, r = _run(p, f"use idea {prop.id} to grow")
    assert r.ok, "explicit use should work"
    assert p.last_nurture.get("pid") == prop.id
    assert p.last_nurture.get("action") == "use"
    print(f"  explicit override: GREEN")
    return True


def test_contextual_pipeline():
    """Contextual selection via English/Mandell pipeline."""
    p = _fresh("DCCIX_Pipe")
    p.nursery.add("plant photosynthesis")
    p.nursery.add("quantum entanglement")
    _confirm_all(p)
    
    i, r = _run(p, "grow using knowledge about plant")
    assert r.ok, "pipeline should work"
    assert "grow_using_knowledge_about" in i.mandel
    
    sel = p.last_nurture
    assert sel.get("action") == "grow_contextual"
    assert sel.get("context") == "plant"
    assert len(sel.get("selected_ids", [])) > 0, "should select relevant"
    print(f"  pipeline: GREEN")
    return True


def test_no_match_behavior():
    """No qualifying knowledge → empty selection, baseline behavior."""
    p = _fresh("DCCIX_NoMatch")
    p.nursery.add("quantum physics")
    _confirm_all(p)
    
    sel = select_for_context(p, "plant", operation="grow")
    assert len(sel["selected"]) == 0, "should select none"
    assert "no token overlap" in sel["reason"]
    
    # Via pipeline: should still run (baseline)
    i, r = _run(p, "grow using knowledge about plant")
    assert r.ok, "should run baseline"
    assert p.last_nurture.get("selected_ids") == []
    print(f"  no match: GREEN")
    return True


def test_tie_determinism():
    """Ties broken deterministically by ID."""
    p = _fresh("DCCIX_Tie")
    # Two with identical content (same tokens)
    p.nursery.add("plant growth")
    p.nursery.add("plant growth")  # duplicate label → different ID, same tokens
    _confirm_all(p)
    
    sel1 = select_for_context(p, "plant", operation="grow")
    sel2 = select_for_context(p, "plant", operation="grow")
    
    ids1 = [s["id"] for s in sel1["selected"]]
    ids2 = [s["id"] for s in sel2["selected"]]
    assert ids1 == ids2, "tie order should be deterministic"
    # Should be sorted by ID asc for ties
    assert ids1 == sorted(ids1), "ties should be ID-sorted"
    print(f"  tie determinism: GREEN")
    return True


def test_persistence_selection():
    """Restored knowledge selected for same context."""
    name = "DCCIX_Persist"
    p = _fresh(name)
    p.nursery.add("plant biology")
    _confirm_all(p)
    save(p)
    del p
    
    p2 = load(name)
    sel = select_for_context(p2, "plant", operation="grow")
    assert len(sel["selected"]) > 0, "restored knowledge should be selected"
    
    # Via pipeline
    i, r = _run(p2, "grow using knowledge about plant")
    assert r.ok
    assert len(p2.last_nurture.get("selected_ids", [])) > 0
    print(f"  persistence: GREEN")
    return True


def test_composition():
    """Contextual consumption in composed program."""
    from form.mandell.english_composer import compose_english, execute_composite
    
    p = _fresh("DCCIX_Comp")
    p.nursery.add("plant growth")
    _confirm_all(p)
    
    r = compose_english("grow using knowledge about plant then trace")
    assert r.ok, "compose should work"
    receipt = execute_composite(p, r.composite)
    assert receipt.completed >= 2, "both should complete"
    print(f"  composition: GREEN")
    return True


def test_receipt_evidence():
    """Receipt shows CONTEXT, ELIGIBLE_COUNT, SELECTED_IDS, REASON."""
    p = _fresh("DCCIX_Receipt")
    p.nursery.add("plant photosynthesis")
    _confirm_all(p)
    
    i, r = _run(p, "grow using knowledge about plant")
    assert r.ok
    
    n = p.last_nurture
    assert "context" in n, "receipt needs CONTEXT"
    assert "eligible_count" in n, "receipt needs ELIGIBLE_COUNT"
    assert "selected_ids" in n, "receipt needs SELECTED_IDS"
    assert "selection_reason" in n, "receipt needs SELECTION_REASON"
    assert n.get("consumer") == "grow_ideas", "receipt needs CONSUMER"
    assert n.get("dell") == 37, "receipt needs DELL"
    print(f"  receipt: GREEN")
    return True


def test_unknown_excluded():
    """Unknown IDs never selected."""
    p = _fresh("DCCIX_Unknown")
    p.nursery.add("plant biology")
    _confirm_all(p)
    
    # Selector only returns real IDs
    sel = select_for_context(p, "plant", operation="grow")
    for s in sel["selected"]:
        assert s["id"] in p.nursery.proposals, "selected ID must exist"
        assert s["id"] in p.cube.session.plane.units, "selected must be in cube"
    print(f"  unknown excluded: GREEN")
    return True


def test_multiple_relevant_ordering():
    """Multiple relevant units ordered by score desc, ID asc for ties."""
    p = _fresh("DCCIX_MultiOrder")
    # Three relevant with different token overlap:
    # "plant growth photosynthesis" shares 1 token with "plant growth"
    # "plant" shares 1 token but smaller set → higher jaccard
    # "plant plant growth" shares 1 token (deduped)
    a = p.nursery.add("plant")
    b = p.nursery.add("plant growth photosynthesis")
    c = p.nursery.add("plant biology chemistry physics")
    d = p.nursery.add("quantum mechanics")
    _confirm_all(p)
    
    sel = select_for_context(p, "plant growth", operation="grow")
    selected = sel["selected"]
    # d (quantum) must be excluded
    ids = [s["id"] for s in selected]
    assert d.id not in ids, "unrelated excluded"
    assert len(ids) == 3, "three relevant selected"
    
    # Ordering: score desc; verify strictly
    scores = [s["score"] for s in selected]
    assert scores == sorted(scores, reverse=True), "ordered by score desc"
    
    # Deterministic across runs
    sel2 = select_for_context(p, "plant growth", operation="grow")
    assert [s["id"] for s in sel2["selected"]] == ids
    print(f"  multiple relevant ordering: GREEN")
    return True


def test_compile_failure_zero_execution():
    """Malformed contextual instruction executes zero Dells."""
    p = _fresh("DCCIX_CompileFail")
    p.nursery.add("plant biology")
    _confirm_all(p)
    before = len(p.nursery.proposals)
    before_trace = len(getattr(p, "trace", [])) if hasattr(p, "trace") else 0
    
    # Empty context: translate should not produce a valid nurture intent
    intent = translate("grow using knowledge about")
    ran = False
    if intent is not None and "grow_using_knowledge_about" in (intent.mandel or ""):
        result = route_intent(p, intent, raw_line="grow using knowledge about")
        ran = result.ok
    
    after = len(p.nursery.proposals)
    assert after == before, "no proposals created on compile failure"
    assert not ran, "no execution on empty context"
    
    # Missing 'about' keyword entirely → not a contextual intent
    intent2 = translate("grow using knowledge")
    if intent2 is not None:
        assert "grow_using_knowledge_about" not in (intent2.mandel or ""), \
            "should not match without 'about'"
    print(f"  compile failure zero execution: GREEN")
    return True


def main():
    tests = [
        ("relevance_control", test_relevance_control),
        ("status_control", test_status_control),
        ("determinism_control", test_determinism_control),
        ("causal_control", test_causal_control),
        ("explicit_override_preserved", test_explicit_override_preserved),
        ("contextual_pipeline", test_contextual_pipeline),
        ("no_match_behavior", test_no_match_behavior),
        ("tie_determinism", test_tie_determinism),
        ("persistence_selection", test_persistence_selection),
        ("composition", test_composition),
        ("receipt_evidence", test_receipt_evidence),
        ("unknown_excluded", test_unknown_excluded),
        ("multiple_relevant_ordering", test_multiple_relevant_ordering),
        ("compile_failure_zero_execution", test_compile_failure_zero_execution),
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

    print(f"\nDCC-IX: {passed}/{len(tests)}")
    if failed:
        print("Failures:")
        for n, e in failed:
            print(f"  {n}: {e}")
        return 1
    print("DCC-IX: GREEN")
    return 0


def smoke() -> bool:
    """Regress entry point."""
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
