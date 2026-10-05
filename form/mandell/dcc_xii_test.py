#!/usr/bin/env python3
"""DCC-XII: Contextual relevance quality + explainable ranking (V2).

Relevance V2 scoring contract:
  jaccard      = |ctx ∩ unit| / |ctx ∪ unit|   (kept as "score")
  coverage     = |ctx ∩ unit| / |ctx|
  exact_phrase = 1 if normalized context is substring of unit text
  ordered      = 1 if context tokens are an ordered subsequence
Ranking: (-exact_phrase, -ordered, -coverage, -jaccard, id) ascending.
Eligibility: confirmed AND on-plane (unchanged).
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
        p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))


def _v1_order(evidence):
    """The documented V1 contract: jaccard desc, id asc (for differential)."""
    return sorted(evidence, key=lambda s: (-s["score"], s["id"]))


def test_exact_relevance():
    """CONTROL A: complete-context candidate ranks above partial."""
    p = _fresh("DCCXII_A")
    p.nursery.add("plant growth uses photosynthesis")
    p.nursery.add("plant")
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    assert sel["selector_version"] == 2
    assert sel["selected"][0]["label"] == "plant growth uses photosynthesis"
    assert sel["selected"][0]["exact_phrase"] == 1
    assert sel["selected"][1]["label"] == "plant"
    print("  exact relevance: GREEN")
    return True


def test_order_phrase_signal():
    """CONTROL B: 'plant growth X' outranks 'growth plant X' via documented signal."""
    p = _fresh("DCCXII_B")
    p.nursery.add("growth plant reversed")
    p.nursery.add("plant growth forward")
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    first, second = sel["selected"][0], sel["selected"][1]
    assert first["label"] == "plant growth forward"
    assert first["exact_phrase"] == 1 and first["ordered"] == 1
    assert second["exact_phrase"] == 0 and second["ordered"] == 0
    # Same jaccard — the difference comes ONLY from the documented signals
    assert first["score"] == second["score"]
    print("  order/phrase signal: GREEN")
    return True


def test_partial_overlap():
    """CONTROL C: ranking reflects declared coverage contract."""
    p = _fresh("DCCXII_C")
    p.nursery.add("plant growth water sunlight")   # full coverage
    p.nursery.add("plant soil")                     # half coverage
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    assert sel["selected"][0]["coverage"] == 1.0
    assert sel["selected"][1]["coverage"] == 0.5
    covs = [s["coverage"] for s in sel["selected"]]
    assert covs == sorted(covs, reverse=True)
    print("  partial overlap: GREEN")
    return True


def test_no_match():
    """CONTROL D: no evidence -> empty selection, no fallback."""
    p = _fresh("DCCXII_D")
    p.nursery.add("quantum entanglement")
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    assert sel["selected"] == []
    assert "no token overlap" in sel["reason"]
    r = _run(p, "grow using knowledge about plant growth")
    assert r.ok
    n = p.last_nurture
    assert n["consumer_scope_ids"] == []
    assert n["scope_mode"] == "contextual"
    print("  no-match: GREEN")
    return True


def test_status_security():
    """CONTROL E: status beats relevance — pending/rejected never rank."""
    p = _fresh("DCCXII_E")
    p.nursery.add("plant growth uses photosynthesis")  # confirmed (weaker text)
    hot = p.nursery.add("plant growth plant growth")  # stays pending (stronger text)
    rej = p.nursery.add("plant growth growth plant")  # rejected (stronger text)
    p.nursery.reject(rej.id)  # reject while pending
    for prop in p.nursery.pending():
        if prop.id != hot.id:
            p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))
    sel = select_for_context(p, "plant growth", operation="grow")
    ids = [s["id"] for s in sel["selected"]]
    assert hot.id not in ids and rej.id not in ids
    assert len(ids) == 1
    print("  status security: GREEN")
    return True


def test_normalization_adversarial():
    """CONTROL F: normalization behavior is explicit and deterministic."""
    p = _fresh("DCCXII_F")
    p.nursery.add("Plant, GROWTH!")        # punctuation + case
    p.nursery.add("plant   growth")        # whitespace
    p.nursery.add("plant plant growth")    # repeated words (deduped)
    p.nursery.add("plant growth and then some much longer trailing text here")
    _confirm_all(p)
    sel = select_for_context(p, "  PLANT growth ", operation="grow")
    assert sel["normalized_context"] == "plant growth"
    by_label = {s["label"]: s for s in sel["selected"]}
    # Case/punct/whitespace normalize to the same evidence
    assert by_label["Plant, GROWTH!"]["exact_phrase"] == 1
    assert by_label["plant   growth"]["exact_phrase"] == 1
    assert by_label["plant plant growth"]["exact_phrase"] == 1
    # Dedup: repeated words don't inflate coverage beyond 1.0
    assert by_label["plant plant growth"]["coverage"] == 1.0
    # Superset text: exact phrase still found, coverage full
    sup = by_label["plant growth and then some much longer trailing text here"]
    assert sup["exact_phrase"] == 1 and sup["coverage"] == 1.0
    # One-token context
    sel1 = select_for_context(p, "plant", operation="grow")
    assert all(s["coverage"] == 1.0 for s in sel1["selected"])
    # Empty context -> no tokens -> empty
    sel0 = select_for_context(p, "", operation="grow")
    assert sel0["selected"] == []
    print("  normalization adversarial: GREEN")
    return True


def test_generic_token_collision():
    """CONTROL G: stronger evidence outranks weak single-token collision."""
    p = _fresh("DCCXII_G")
    p.nursery.add("the plant sat alone")              # weak: 1 generic-ish token
    p.nursery.add("plant growth uses photosynthesis")  # strong: full context
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    assert sel["selected"][0]["label"] == "plant growth uses photosynthesis"
    # Described structurally: weaker textual evidence, not "unrelated"
    weak = [s for s in sel["selected"] if s["label"] == "the plant sat alone"][0]
    assert weak["coverage"] == 0.5 < 1.0
    print("  generic token collision: GREEN")
    return True


def test_determinism():
    """CONTROL H: identical evidence across independent fixtures."""
    def snap(name):
        p = _fresh(name)
        p.nursery.add("plant growth uses photosynthesis")
        p.nursery.add("growth plant reversed")
        p.nursery.add("plant")
        _confirm_all(p)
        sel = select_for_context(p, "plant growth", operation="grow")
        return sel
    s1, s2 = snap("DCCXII_H1"), snap("DCCXII_H2")
    assert s1["eligible_count"] == s2["eligible_count"]
    assert s1["normalized_context"] == s2["normalized_context"]
    e1 = [(s["label"], s["score"], s["coverage"], s["exact_phrase"],
           s["ordered"], s["rank"]) for s in s1["selected"]]
    e2 = [(s["label"], s["score"], s["coverage"], s["exact_phrase"],
           s["ordered"], s["rank"]) for s in s2["selected"]]
    assert e1 == e2, "identical candidate evidence and ranking"
    print("  determinism: GREEN")
    return True


def test_explainability():
    """CONTROL I: receipt exposes enough to reconstruct ranking."""
    p = _fresh("DCCXII_I")
    p.nursery.add("plant growth uses photosynthesis")
    p.nursery.add("plant")
    _confirm_all(p)
    r = _run(p, "grow using knowledge about plant growth")
    assert r.ok
    n = p.last_nurture
    assert n["selector_version"] == 2
    assert "relevance v2" in n["ordering_rule"]
    for s in n["selected_details"]:
        for field in ("id", "score", "shared", "coverage",
                      "exact_phrase", "ordered", "rank"):
            assert field in s, f"missing explainability field {field}"
    # Reconstruct ranking from evidence
    det = n["selected_details"]
    keys = [(-s["exact_phrase"], -s["ordered"], -s["coverage"],
             -s["score"], s["id"]) for s in det]
    assert keys == sorted(keys), "ranking reconstructible from evidence"
    print("  explainability: GREEN")
    return True


def test_scoped_integration():
    """CONTROL J: V2 selection == consumer scope (DCC-XI invariant)."""
    p = _fresh("DCCXII_J")
    p.nursery.add("plant growth uses photosynthesis")
    p.nursery.add("growth plant reversed")
    p.nursery.add("quantum entanglement")
    _confirm_all(p)
    r = _run(p, "grow using knowledge about plant growth")
    assert r.ok
    n = p.last_nurture
    assert n["selected_ids"] == n["consumer_scope_ids"]
    assert n["scope_mode"] == "contextual"
    # V2 reordering cannot widen scope: scope is exactly the selection
    assert len(n["consumer_scope_ids"]) == 2
    print("  scoped integration: GREEN")
    return True


def test_top5_quality():
    """CONTROL K: >5 candidates -> top 5 by V2 rank, explained boundary."""
    p = _fresh("DCCXII_K")
    p.nursery.add("plant growth uses photosynthesis")  # rank 1
    p.nursery.add("plant growth needs water")         # rank 2-ish
    p.nursery.add("plant growth")                     # exact, short
    p.nursery.add("growth plant")                     # reordered
    p.nursery.add("plant")                            # partial
    p.nursery.add("growth")                           # partial
    p.nursery.add("plant biology")                    # partial
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    assert len(sel["selected"]) == 5
    ranks = [s["rank"] for s in sel["selected"]]
    assert ranks == [1, 2, 3, 4, 5]
    r = _run(p, "grow using knowledge about plant growth")
    assert r.ok
    n = p.last_nurture
    assert len(n["consumer_scope_ids"]) == 5
    assert n["selected_ids"] == n["consumer_scope_ids"]
    print("  top-5 quality: GREEN")
    return True


def test_persistence():
    """CONTROL L: save/terminate/load -> identical V2 ranking evidence."""
    name = "DCCXII_L"
    p = _fresh(name)
    p.nursery.add("plant growth uses photosynthesis")
    p.nursery.add("growth plant reversed")
    p.nursery.add("plant")
    _confirm_all(p)
    save(p)
    del p
    p2 = load(name)
    r = _run(p2, "grow using knowledge about plant growth")
    assert r.ok
    n = p2.last_nurture
    ev = [(s["label"], s["score"], s["coverage"], s["exact_phrase"],
           s["ordered"], s["rank"]) for s in n["selected_details"]]
    assert ev[0][0] == "plant growth uses photosynthesis"
    assert [e[5] for e in ev] == sorted(e[5] for e in ev)
    assert n["selected_ids"] == n["consumer_scope_ids"]
    print("  persistence: GREEN")
    return True


def test_composition():
    """CONTROL M: V2 contextual selection through composition."""
    from form.mandell.english_composer import compose_english, execute_composite
    p = _fresh("DCCXII_M")
    p.nursery.add("plant growth uses photosynthesis")
    p.nursery.add("plant")
    _confirm_all(p)
    r = compose_english("grow using knowledge about plant growth then trace")
    assert r.ok
    assert execute_composite(p, r.composite).completed >= 2
    r2 = compose_english("grow using knowledge about plant growth then list confirmed")
    assert r2.ok
    assert execute_composite(p, r2.composite).completed >= 2
    print("  composition: GREEN")
    return True


def test_legacy_compatibility():
    """CONTROL N: ordinary/explicit/DCC-IX/X/XI behavior unchanged."""
    p = _fresh("DCCXII_N")
    k1 = p.nursery.add("plant growth uses photosynthesis")
    k2 = p.nursery.add("plant growth depends on water")
    k3 = p.nursery.add("quantum entanglement links particles")
    _confirm_all(p)
    # Ordinary growth: full-plane
    assert p.grow_ideas(1)["scope_mode"] == "full"
    # Explicit use: unchanged action
    r = _run(p, f"use idea {k1.id} to grow")
    assert r.ok and p.last_nurture.get("action") == "use"
    # DCC-IX syntax: contextual command works
    r = _run(p, "grow using knowledge about plant growth")
    assert r.ok
    n = p.last_nurture
    # DCC-X multi-selection + DCC-XI scope enforcement
    assert len(n["selected_ids"]) >= 2
    assert n["selected_ids"] == n["consumer_scope_ids"]
    assert k3.id not in n["consumer_scope_ids"]
    print("  legacy compatibility: GREEN")
    return True


def test_causal_ranking_change():
    """CONTROL O: V1 ties at jaccard 0.5; V2 distinguishes with evidence."""
    p = _fresh("DCCXII_O")
    p.nursery.add("plant growth uses photosynthesis")
    p.nursery.add("growth plant reversed order")
    p.nursery.add("plant")
    _confirm_all(p)
    sel = select_for_context(p, "plant growth", operation="grow")
    ev = sel["selected"]
    # Old evidence: all three tied at jaccard 0.5
    assert all(s["score"] == 0.5 for s in ev), "V1 would tie"
    v1 = _v1_order(ev)
    # V2 evidence produces a strict, explained ranking
    assert ev[0]["exact_phrase"] == 1 and ev[0]["ordered"] == 1
    assert ev[1]["exact_phrase"] == 0 and ev[1]["ordered"] == 0
    assert ev[2]["coverage"] == 0.5
    labels_v2 = [s["label"] for s in ev]
    assert labels_v2 == ["plant growth uses photosynthesis",
                         "growth plant reversed order", "plant"]
    # V1 order would have been ID-tiebreak (arbitrary w.r.t. relevance)
    print(f"  V1 tie order: {[s['label'][:12] for s in v1]}")
    print(f"  V2 rank order: {[s['label'][:12] for s in ev]}")
    print("  causal ranking change: GREEN")
    return True


def test_failure_atomicity():
    """CONTROL P: failures never widen selection/scope or mislead."""
    p = _fresh("DCCXII_P")
    p.nursery.add("plant growth uses photosynthesis")
    _confirm_all(p)
    before = set(p.nursery.proposals.keys())
    # Consumer-boundary failure: invalid scope
    try:
        p.grow_ideas(1, scope_ids=["missing_unit"])
        assert False, "must raise"
    except ValueError:
        pass
    assert set(p.nursery.proposals.keys()) == before
    # Scoring with empty context: no selection, no crash, empty scope
    sel = select_for_context(p, "", operation="grow")
    assert sel["selected"] == []
    print("  failure atomicity: GREEN")
    return True


def test_differential_corpus():
    """PHASE C: V1 vs V2 differential corpus — differences explainable."""
    corpus = [
        # (context, candidates, expectation notes)
        ("plant growth",
         ["plant growth uses photosynthesis", "growth plant", "plant",
          "quantum entanglement"],
         "V2 must promote exact-phrase above reordered; V1 ties them"),
        ("water cycle",
         ["water cycle evaporation", "cycle water", "water",
          "unrelated topic here"],
         "same pattern on a second context"),
        ("ancient stone",
         ["ancient stone tablet", "stone ancient", "ancient"],
         "phrase/order/coverage ladder"),
    ]
    diffs = 0
    for ctx, cands, note in corpus:
        p = _fresh(f"DCCXII_CORP_{abs(hash(ctx)) % 9999}")
        for c in cands:
            p.nursery.add(c)
        _confirm_all(p)
        sel = select_for_context(p, ctx, operation="grow")
        ev = sel["selected"]
        v1 = [s["label"] for s in _v1_order(ev)]
        v2 = [s["label"] for s in ev]
        status = "SAME" if v1 == v2 else "DIFF"
        if v1 != v2:
            diffs += 1
            # Every difference must be explained by V2 components
            for s in ev:
                assert "exact_phrase" in s and "ordered" in s and "coverage" in s
        print(f"  corpus '{ctx}': {status} — {note}")
        print(f"    V1: {[l[:20] for l in v1]}")
        print(f"    V2: {[l[:20] for l in v2]}")
    assert diffs >= 1, "corpus must expose at least one intentional difference"
    print("  differential corpus: GREEN")
    return True


def main():
    tests = [
        ("exact_relevance", test_exact_relevance),
        ("order_phrase_signal", test_order_phrase_signal),
        ("partial_overlap", test_partial_overlap),
        ("no_match", test_no_match),
        ("status_security", test_status_security),
        ("normalization_adversarial", test_normalization_adversarial),
        ("generic_token_collision", test_generic_token_collision),
        ("determinism", test_determinism),
        ("explainability", test_explainability),
        ("scoped_integration", test_scoped_integration),
        ("top5_quality", test_top5_quality),
        ("persistence", test_persistence),
        ("composition", test_composition),
        ("legacy_compatibility", test_legacy_compatibility),
        ("causal_ranking_change", test_causal_ranking_change),
        ("failure_atomicity", test_failure_atomicity),
        ("differential_corpus", test_differential_corpus),
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
    print(f"\nDCC-XII: {passed}/{len(tests)}")
    if failed:
        for n, e in failed:
            print(f"  {n}: {e}")
        return 1
    print("DCC-XII: GREEN")
    return 0


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
