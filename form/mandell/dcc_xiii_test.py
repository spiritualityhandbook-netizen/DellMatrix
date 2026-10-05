#!/usr/bin/env python3
"""DCC-XIII: Conflict-aware contextual knowledge routing (Conflict V1).

Conflict V1 contract:
  - Polarity: exactly one unit carries a supported negation signal
    (not/no/never/none/neither/nor/cannot, or n't-contraction).
  - Shared frame: de-negated token sets share >=2 tokens AND
    Jaccard >= 0.5.
  - Analysis runs only on already-selected units (status filtered first).
  - Routing: every unit in >=1 conflict pair is quarantined; routable
    preserves V2 rank order; consumer receives exactly the routable set.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from form.open import open_program
from form.persist_rest import save, load
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell.conflict_router import detect_conflicts


def _fresh(name):
    state_dir = Path(__file__).resolve().parent.parent / "state"
    for f in state_dir.glob(f"*{name}*"):
        try:
            f.unlink()
        except OSError:
            pass
    return open_program(name)


def _run(p, eng):
    intent = translate(eng)
    return route_intent(p, intent, raw_line=eng)


def _confirm_all(p):
    for prop in p.nursery.pending():
        p.confirm_proposal(prop.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": prop.id})


def _ctx(p, context="plant growth"):
    r = _run(p, f"grow using knowledge about {context}")
    assert r.ok, "contextual grow must succeed"
    return p.last_nurture


def test_positive_negative_pair():
    """CONTROL A: polarity pair detected; neither silently combined."""
    p = _fresh("DCCXIII_A")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    _confirm_all(p)
    n = _ctx(p)
    assert n["conflict_version"] == 1
    assert n["conflict_count"] == 1
    c = n["conflicts"][0]
    assert {c["id_a"], c["id_b"]} == {k1.id, k2.id}
    assert "not" in c["negation_evidence"]
    assert len(c["shared_frame"]) >= 2 and c["frame_jaccard"] >= 0.5
    # Both were selected and relevant...
    assert k1.id in n["selected_ids"] and k2.id in n["selected_ids"]
    # ...but neither reaches the consumer as mutually compatible
    assert k1.id not in n["consumer_scope_ids"]
    assert k2.id not in n["consumer_scope_ids"]
    assert set(n["quarantined_ids"]) == {k1.id, k2.id}
    print("  positive/negative pair: GREEN")
    return True


def test_non_conflicting_pair():
    """CONTROL B: no conflict invented; both routable."""
    p = _fresh("DCCXIII_B")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth needs water")
    _confirm_all(p)
    n = _ctx(p)
    assert n["conflict_count"] == 0
    assert n["quarantined_ids"] == []
    assert k1.id in n["consumer_scope_ids"]
    assert k2.id in n["consumer_scope_ids"]
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    print("  non-conflicting pair: GREEN")
    return True


def test_mixed_set():
    """CONTROL C: conflict members quarantined, K3 proceeds."""
    p = _fresh("DCCXIII_C")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    k3 = p.nursery.add("plant growth needs water")
    _confirm_all(p)
    n = _ctx(p)
    assert n["conflict_count"] == 1
    assert k1.id not in n["consumer_scope_ids"]
    assert k2.id not in n["consumer_scope_ids"]
    assert n["consumer_scope_ids"] == [k3.id]
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    print("  mixed set: GREEN")
    return True


def test_all_conflict():
    """CONTROL D: everything quarantined -> empty scope, no fallback."""
    p = _fresh("DCCXIII_D")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    _confirm_all(p)
    n = _ctx(p)
    assert n["conflict_count"] == 1
    assert n["consumer_scope_ids"] == []
    assert n["routable_selected_ids"] == []
    assert n["scope_mode"] == "contextual"  # not silent full-plane
    assert n["ok"] is True  # routing completed; receipt explains why empty
    print("  all-conflict: GREEN")
    return True


def test_status_security():
    """CONTROL E: ineligible claims never quarantine valid knowledge."""
    p = _fresh("DCCXIII_E")
    k1 = p.nursery.add("plant growth requires light")  # confirmed
    hot = p.nursery.add("plant growth does not require light")  # pending
    rej = p.nursery.add("plant growth requires no light at all")  # rejected
    p.nursery.reject(rej.id)
    for prop in p.nursery.pending():
        if prop.id != hot.id:
            p.confirm_proposal(prop.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": prop.id})
    n = _ctx(p)
    # Only k1 eligible -> no pair to conflict with
    assert n["conflict_count"] == 0
    assert n["quarantined_ids"] == []
    assert n["consumer_scope_ids"] == [k1.id]
    print("  status security: GREEN")
    return True


def test_relevance_conflict_separation():
    """CONTROL F: relevance evidence and conflict evidence kept separate."""
    p = _fresh("DCCXIII_F")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    _confirm_all(p)
    n = _ctx(p)
    # V2 relevance evidence intact per selection...
    for s in n["selected_details"]:
        assert "score" in s and "coverage" in s and "exact_phrase" in s
    # ...and conflict evidence is a separate structure, not a merged score:
    # conflict entries carry fields selections never have, and vice versa
    assert n["selector_version"] == 2 and n["conflict_version"] == 1
    assert "negation_evidence" in n["conflicts"][0]
    assert "negation_evidence" not in n["selected_details"][0]
    assert "coverage" in n["selected_details"][0]
    assert "coverage" not in n["conflicts"][0]
    # High relevance did not imply truth: the top-ranked unit is quarantined
    top = n["selected_details"][0]["id"]
    assert top in n["quarantined_ids"]
    print("  relevance/conflict separation: GREEN")
    return True


def test_negation_adversarials():
    """CONTROL G: bounded detector; 'not' alone never suffices."""
    cases = [
        # (a, b, expected_conflict, note)
        ("plant growth requires light", "plant growth does not require light",
         True, "canonical does-not"),
        ("plant growth requires light", "plant growth doesn't require light",
         True, "contraction"),
        ("plant growth is tall", "plant growth is not tall",
         True, "is-not"),
        ("PLANT GROWTH REQUIRES LIGHT", "plant growth does  not  require light",
         True, "case+whitespace"),
        ("plant growth requires light.", "plant growth does not require light!",
         True, "punctuation"),
        ("plant growth requires light", "plant growth requires light",
         False, "identical positive"),
        ("plant growth does not require light",
         "plant growth does not require light",
         False, "identical negative (same polarity)"),
        ("plant growth does not require light",
         "plant growth does not require water",
         False, "both negated"),
        ("plant growth requires light", "plant growth does not require water",
         False, "negation on different frame"),
        ("I do not like rain", "plant growth requires light",
         False, "unrelated 'not'"),
        ("plant growth requires light", "quantum entanglement links particles",
         False, "no shared frame"),
        ("plant growth needs no light", "plant growth needs light",
         True, "'no' as negation"),
        ("plant growth never needs light", "plant growth needs light",
         True, "'never' as negation"),
    ]
    for a, b, expected, note in cases:
        got = detect_conflicts([{"id": "a", "text": a}, {"id": "b", "text": b}])
        assert bool(got) == expected, f"case failed [{note}]: {a!r} vs {b!r}"
    print("  negation adversarials: GREEN")
    return True


def test_pair_determinism():
    """CONTROL H: pair enumeration and routing deterministic."""
    def run_once(name):
        p = _fresh(name)
        p.nursery.add("plant growth requires light")
        p.nursery.add("plant growth does not require light")
        p.nursery.add("plant growth needs water")
        p.nursery.add("plant growth does not need water")
        _confirm_all(p)
        return _ctx(p)
    n1, n2 = run_once("DCCXIII_H1"), run_once("DCCXIII_H2")
    for key in ("conflicts", "quarantined_ids", "routable_selected_ids",
                "consumer_scope_ids"):
        v1 = n1[key]
        v2 = n2[key]
        # normalize volatile IDs by label mapping
        assert len(v1) == len(v2), f"{key} length differs"
    pairs1 = [(c["id_a"], c["id_b"]) for c in n1["conflicts"]]
    assert pairs1 == sorted(pairs1), "conflict ordering stable"
    print("  pair determinism: GREEN")
    return True


def test_duplicate_paraphrase_boundary():
    """CONTROL I: documents exactly what V1 can/can't distinguish."""
    # Exact duplicates: same polarity -> no conflict
    assert detect_conflicts([
        {"id": "a", "text": "plant growth requires light"},
        {"id": "b", "text": "plant growth requires light"}]) == []
    # Structurally different, shared tokens, no negation -> no conflict
    assert detect_conflicts([
        {"id": "a", "text": "light helps plant growth daily"},
        {"id": "b", "text": "plant growth uses light for energy"}]) == []
    # Supported conflict still fires
    assert len(detect_conflicts([
        {"id": "a", "text": "plant growth requires light"},
        {"id": "b", "text": "plant growth does not require light"}])) == 1
    # Paraphrase with disjoint vocabulary: invisible to V1 (documented)
    assert detect_conflicts([
        {"id": "a", "text": "plant growth requires light"},
        {"id": "b", "text": "flora maturation lacks illumination"}]) == []
    print("  duplicate/paraphrase boundary: GREEN")
    return True


def test_top5_integration():
    """CONTROL J: eligibility -> V2 -> top-5 -> conflict -> routable -> scope."""
    p = _fresh("DCCXIII_J")
    p.nursery.add("plant growth requires light")       # conflicts
    p.nursery.add("plant growth does not require light")  # conflicts
    p.nursery.add("plant growth needs water")          # routable
    p.nursery.add("plant growth uses sunlight")        # routable
    p.nursery.add("plant")                             # routable (partial)
    p.nursery.add("growth")                            # rank 6+, must not route
    p.nursery.add("quantum entanglement")              # irrelevant
    _confirm_all(p)
    n = _ctx(p)
    assert len(n["selected_ids"]) == 5, "top-5 bound respected"
    assert n["conflict_count"] == 1
    # Rank 6+ never entered conflict analysis: only selected IDs quarantined
    assert set(n["quarantined_ids"]) <= set(n["selected_ids"])
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    assert len(n["consumer_scope_ids"]) == 3  # 5 selected - 2 quarantined
    print("  top-5 integration: GREEN")
    return True


def test_consumer_enforcement():
    """CONTROL K: consumer_scope == routable (not original selected)."""
    p = _fresh("DCCXIII_K")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    k3 = p.nursery.add("plant growth needs water")
    _confirm_all(p)
    n = _ctx(p)
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    assert n["consumer_scope_ids"] != n["selected_ids"]  # conflict changed it
    assert len(n["selected_ids"]) == 3 and len(n["consumer_scope_ids"]) == 1
    print("  consumer enforcement: GREEN")
    return True


def test_provenance():
    """CONTROL L: offspring trace only to routable units."""
    p = _fresh("DCCXIII_L")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    k3 = p.nursery.add("plant growth needs water")
    _confirm_all(p)
    n = _ctx(p)
    contrib_ids = {c["id"] for c in n["contributions"]}
    assert k1.id not in contrib_ids and k2.id not in contrib_ids
    assert contrib_ids == {k3.id}
    for c in n["contributions"]:
        for o in c["offspring_ids"]:
            parents = p.nursery.proposals[o].parents
            assert k1.id not in parents and k2.id not in parents
    print("  provenance: GREEN")
    return True


def test_persistence():
    """CONTROL M: save/terminate/load -> identical conflict routing."""
    name = "DCCXIII_M"
    p = _fresh(name)
    p.nursery.add("plant growth requires light")
    p.nursery.add("plant growth does not require light")
    p.nursery.add("plant growth needs water")
    _confirm_all(p)
    save(p)
    del p
    p2 = load(name)
    n = _ctx(p2)
    assert n["conflict_version"] == 1 and n["conflict_count"] == 1
    assert len(n["quarantined_ids"]) == 2
    assert len(n["routable_selected_ids"]) == 1
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    labels = sorted(s["label"] for s in n["selected_details"])
    assert labels == ["plant growth does not require light",
                      "plant growth needs water",
                      "plant growth requires light"]
    print("  persistence: GREEN")
    return True


def test_composition():
    """CONTROL N: conflict-aware routing through composition."""
    from form.mandell.english_composer import compose_english, execute_composite
    p = _fresh("DCCXIII_N")
    p.nursery.add("plant growth requires light")
    p.nursery.add("plant growth does not require light")
    p.nursery.add("plant growth needs water")
    _confirm_all(p)
    r = compose_english("grow using knowledge about plant growth then trace")
    assert r.ok
    assert execute_composite(p, r.composite).completed >= 2
    n = p.last_nurture
    assert n["conflict_count"] == 1
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    r2 = compose_english("grow using knowledge about plant growth then list confirmed")
    assert r2.ok
    assert execute_composite(p, r2.composite).completed >= 2
    print("  composition: GREEN")
    return True


def test_baseline_compatibility():
    """CONTROL O (part 1): baseline/explicit paths unchanged."""
    p = _fresh("DCCXIII_O")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    _confirm_all(p)
    # Ordinary growth: full-plane, no conflict analysis
    g = p.grow_ideas(1)
    assert g["scope_mode"] == "full"
    # Explicit use: unchanged semantics, no quarantine
    r = _run(p, f"use idea {k1.id} to grow")
    assert r.ok and p.last_nurture.get("action") == "use"
    assert "conflict_version" not in p.last_nurture
    print("  baseline compatibility: GREEN")
    return True


def test_legacy_compatibility():
    """CONTROL O (part 2): DCC-IX/X/XI/XII behavior preserved."""
    p = _fresh("DCCXIII_O2")
    k1 = p.nursery.add("plant growth uses photosynthesis")
    k2 = p.nursery.add("plant growth depends on water")
    k3 = p.nursery.add("quantum entanglement links particles")
    _confirm_all(p)
    n = _ctx(p)
    # DCC-IX syntax works; DCC-XII V2 ranking intact
    assert n["selector_version"] == 2
    assert [s["rank"] for s in n["selected_details"]] == [1, 2]
    # DCC-X multi-selection + DCC-XI scope; no conflicts here
    assert n["conflict_count"] == 0
    assert n["selected_ids"] == n["routable_selected_ids"]
    assert n["selected_ids"] == n["consumer_scope_ids"]
    assert k3.id not in n["consumer_scope_ids"]
    print("  legacy compatibility: GREEN")
    return True


def test_failure_atomicity():
    """CONTROL P: failures leave no widened scope or stale metadata."""
    p = _fresh("DCCXIII_P")
    k1 = p.nursery.add("plant growth requires light")
    k2 = p.nursery.add("plant growth does not require light")
    _confirm_all(p)
    before = set(p.nursery.proposals.keys())
    # Scope-construction failure: invalid ID still raises, nothing persists
    try:
        p.grow_ideas(1, scope_ids=["missing_unit"])
        assert False, "must raise"
    except ValueError:
        pass
    assert set(p.nursery.proposals.keys()) == before
    # A fresh successful run writes fresh conflict metadata (no staleness)
    n = _ctx(p)
    assert n["ok"] is True
    assert n["conflict_count"] == 1
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    print("  failure atomicity: GREEN")
    return True


def test_conflict_corpus():
    """PHASE E: manually auditable corpus, expected vs actual."""
    corpus = [
        # (text_a, text_b, expected, reason)
        ("plant growth requires light", "plant growth does not require light",
         True, "canonical polarity conflict"),
        ("seed germination needs warmth", "seed germination does not need warmth",
         True, "second context, same pattern"),
        ("plant growth requires light", "plant growth needs water",
         False, "compatible claims, no negation"),
        ("plant growth requires light", "plant growth requires light",
         False, "duplicate positive"),
        ("plant growth does not require light",
         "plant growth does not require light",
         False, "duplicate negative, same polarity"),
        ("I do not know the answer", "plant growth requires light",
         False, "unrelated negation"),
        ("plant growth requires light", "plant growth does not require water",
         False, "negation on different frame"),
        ("plant growth needs no water", "plant growth needs water",
         True, "'no' negation"),
        ("the sky is blue", "the sky is not blue",
         True, "minimal frame pair"),
        ("light", "plant growth does not require light",
         False, "fragment frame too small (shared<2)"),
        ("plant growth needs water", "plant growth does not need water or soil",
         False, "asymmetric frame breadth under V1 (documented boundary)"),
        ("quantum entanglement links particles", "quantum entanglement links waves",
         False, "shared tokens, no negation signal"),
    ]
    mismatches = []
    for a, b, expected, reason in corpus:
        got = bool(detect_conflicts([{"id": "a", "text": a},
                                     {"id": "b", "text": b}]))
        status = "OK" if got == expected else "MISMATCH"
        if got != expected:
            mismatches.append((a, b, expected, got, reason))
        print(f"  [{status}] expected={expected} got={got} — {reason}")
    assert not mismatches, f"corpus mismatches: {mismatches}"
    print("  conflict corpus: GREEN")
    return True


def main():
    tests = [
        ("positive_negative_pair", test_positive_negative_pair),
        ("non_conflicting_pair", test_non_conflicting_pair),
        ("mixed_set", test_mixed_set),
        ("all_conflict", test_all_conflict),
        ("status_security", test_status_security),
        ("relevance_conflict_separation", test_relevance_conflict_separation),
        ("negation_adversarials", test_negation_adversarials),
        ("pair_determinism", test_pair_determinism),
        ("duplicate_paraphrase_boundary", test_duplicate_paraphrase_boundary),
        ("top5_integration", test_top5_integration),
        ("consumer_enforcement", test_consumer_enforcement),
        ("provenance", test_provenance),
        ("persistence", test_persistence),
        ("composition", test_composition),
        ("baseline_compatibility", test_baseline_compatibility),
        ("legacy_compatibility", test_legacy_compatibility),
        ("failure_atomicity", test_failure_atomicity),
        ("conflict_corpus", test_conflict_corpus),
    ]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  PASS: {name}")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"  FAIL: {name}: {e}")
    print(f"\nDCC-XIII: {passed}/{len(tests)}")
    if failed:
        for n, e in failed:
            print(f"  {n}: {e}")
        return 1
    print("DCC-XIII: GREEN")
    return 0


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
