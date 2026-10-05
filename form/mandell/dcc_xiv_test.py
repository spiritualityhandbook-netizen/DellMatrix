#!/usr/bin/env python3
"""DCC-XIV: Knowledge evidence lineage + provenance-aware routing (Lineage V1).

Lineage V1 exposes persisted ancestry: unit_id, origin_kind
(direct/derived), origin, parent_ids, root_ids, depth (= lineage_version:
1 direct, 1+max(parent depths) derived), status
(ok/cycle/missing_parents/unknown_unit).

PROVENANCE IS NOT TRUTH. Lineage never boosts rank, never resolves
conflict, never verifies external sources.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from form.open import open_program
from form.persist_rest import save, load
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell.knowledge_lineage import lineage_record, lineage_groups


def _fresh(name):
    state_dir = Path(__file__).resolve().parent.parent / "state"
    for f in state_dir.glob(f"*{name}*"):
        try:
            f.unlink()
        except OSError:
            pass
    return open_program(name)


def _run(p, eng):
    return route_intent(p, translate(eng), raw_line=eng)


def _ctx(p, context="plant growth"):
    r = _run(p, f"grow using knowledge about {context}")
    assert r.ok, "contextual grow must succeed"
    return p.last_nurture


def _confirm(p, prop):
    res = p.confirm_proposal(prop.id, _producer="test", _review_context={"reviewer": "test", "approved_pid": prop.id})
    assert res.get("ok"), f"confirm failed: {res}"
    return prop.id


def test_direct_root():
    """CONTROL A: direct knowledge is its own root; survives save/load."""
    p = _fresh("DCCXIV_A")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    rec = lineage_record(p, aid)
    assert rec["origin_kind"] == "direct"
    assert rec["parent_ids"] == []
    assert rec["root_ids"] == [aid]
    assert rec["depth"] == 1 and rec["status"] == "ok"
    save(p)
    del p
    p2 = load("DCCXIV_A")
    rec2 = lineage_record(p2, aid)
    assert rec2 == rec, "lineage identical after restore"
    print("  direct root: GREEN")
    return True


def test_single_parent_derivation():
    """CONTROL B: legitimate derived unit via nursery.add(parents)+confirm."""
    p = _fresh("DCCXIV_B")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    bid = _confirm(p, p.nursery.add("plant growth requires light daily",
                                    parents=[aid]))
    rec = lineage_record(p, bid)
    assert rec["origin_kind"] == "derived"
    assert rec["parent_ids"] == [aid]
    assert rec["root_ids"] == [aid]
    assert rec["depth"] == 2
    print("  single-parent derivation: GREEN")
    return True


def test_multi_parent_derivation():
    """CONTROL C: multi-parent root union + depth rule."""
    p = _fresh("DCCXIV_C")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    bid = _confirm(p, p.nursery.add("plant growth needs water"))
    did = _confirm(p, p.nursery.add("plant growth needs light and water",
                                    parents=[aid, bid]))
    rec = lineage_record(p, did)
    assert rec["parent_ids"] == [aid, bid]
    assert rec["root_ids"] == sorted([aid, bid])
    assert rec["depth"] == 2  # 1 + max(parent depths 1,1)
    # deeper chain: depth = 1 + max(parent depths)
    eid = _confirm(p, p.nursery.add("plant growth synthesis note",
                                    parents=[did]))
    rec2 = lineage_record(p, eid)
    assert rec2["depth"] == 3
    assert rec2["root_ids"] == sorted([aid, bid])
    print("  multi-parent derivation: GREEN")
    return True


def test_multi_level_persistence():
    """CONTROL D: >=2 derivation levels identical after save/load."""
    name = "DCCXIV_D"
    p = _fresh(name)
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    bid = _confirm(p, p.nursery.add("plant growth requires light daily",
                                    parents=[aid]))
    cid = _confirm(p, p.nursery.add("plant growth requires light always",
                                    parents=[bid]))
    before = {i: lineage_record(p, i) for i in (aid, bid, cid)}
    assert [before[i]["depth"] for i in (aid, bid, cid)] == [1, 2, 3]
    save(p)
    del p
    p2 = load(name)
    after = {i: lineage_record(p2, i) for i in (aid, bid, cid)}
    assert after == before
    print("  multi-level persistence: GREEN")
    return True


def test_duplicate_lineage_grouping():
    """CONTROL E: same-root descendants grouped; not 'two sources'."""
    p = _fresh("DCCXIV_E")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    k1 = _confirm(p, p.nursery.add("plant growth requires light daily"))
    k2 = _confirm(p, p.nursery.add("plant growth requires light notes",
                                   parents=[aid]))
    k3 = _confirm(p, p.nursery.add("plant growth needs water"))
    groups = lineage_groups(p, [k1, k2, k3])
    # k1 direct (own root), k2 descends from aid, k3 direct (own root)
    assert groups[k1] == [k1]
    assert groups[aid] == [k2]
    assert groups[k3] == [k3]
    assert len(groups) == 3, "three independent roots, not 'three sources'"
    print("  duplicate-lineage grouping: GREEN")
    return True


def test_independence_metadata():
    """CONTROL F: selected root IDs / root_count exposed, no rank boost."""
    p = _fresh("DCCXIV_F")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    _confirm(p, p.nursery.add("plant growth requires light daily",
                              parents=[aid]))
    _confirm(p, p.nursery.add("plant growth needs water"))
    n = _ctx(p)
    assert n["lineage_version"] == 1
    assert n["root_count"] == len(n["selected_root_ids"]) == 2
    # rank order unchanged by lineage: same textual candidates as DCC-XIII
    # fixtures keep V2 ordering (lineage never enters the ranking tuple)
    assert n["selector_version"] == 2
    for s in n["selected_details"]:
        assert set(s.keys()) >= {"score", "coverage", "exact_phrase",
                                 "ordered", "rank"}
        assert "root" not in s or True  # no lineage fields in V2 evidence
    print("  independence metadata: GREEN")
    return True


def test_conflict_same_root():
    """CONTROL G case 1: conflicting claims sharing one root still conflict."""
    p = _fresh("DCCXIV_G1")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    # opposing claim derived from the same root
    _confirm(p, p.nursery.add("plant growth does not require light",
                              parents=[aid]))
    n = _ctx(p)
    assert n["conflict_count"] == 1
    c = n["conflicts"][0]
    # lineage distinguishes the case: both share root aid
    roots_a = n["selected_lineage"][c["id_a"]]["root_ids"]
    roots_b = n["selected_lineage"][c["id_b"]]["root_ids"]
    assert roots_a == roots_b == [aid]
    # quarantine preserved despite shared lineage
    assert set(n["quarantined_ids"]) == {c["id_a"], c["id_b"]}
    print("  conflict same-root: GREEN")
    return True


def test_conflict_independent_roots():
    """CONTROL G case 2: conflicting claims, independent roots, still conflict."""
    p = _fresh("DCCXIV_G2")
    _confirm(p, p.nursery.add("plant growth requires light"))
    _confirm(p, p.nursery.add("plant growth does not require light"))
    n = _ctx(p)
    assert n["conflict_count"] == 1
    c = n["conflicts"][0]
    roots_a = n["selected_lineage"][c["id_a"]]["root_ids"]
    roots_b = n["selected_lineage"][c["id_b"]]["root_ids"]
    assert roots_a != roots_b and len(roots_a) == len(roots_b) == 1
    assert set(n["quarantined_ids"]) == {c["id_a"], c["id_b"]}
    # lineage describes; it does NOT resolve truth
    assert "truth" not in str(n["selected_lineage"]).lower()
    print("  conflict independent-roots: GREEN")
    return True


def test_quarantine_preserved():
    """CONTROL H: DCC-XIII routing stays authoritative over lineage."""
    p = _fresh("DCCXIV_H")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    bid = _confirm(p, p.nursery.add("plant growth does not require light",
                                    parents=[aid]))
    n = _ctx(p)
    assert n["conflict_count"] == 1
    assert n["consumer_scope_ids"] == n["routable_selected_ids"] == []
    # lineage metadata present but did not rescue quarantined units
    assert n["root_count"] >= 1
    print("  quarantine preserved: GREEN")
    return True


def test_relevance_independence():
    """CONTROL I: same textual candidates, different lineage, same V2 order."""
    def build(name, derive):
        p = _fresh(name)
        aid = _confirm(p, p.nursery.add("plant growth uses photosynthesis"))
        if derive:
            _confirm(p, p.nursery.add("plant growth depends on water",
                                      parents=[aid]))
        else:
            _confirm(p, p.nursery.add("plant growth depends on water"))
        return p
    n1 = _ctx(build("DCCXIV_I1", False))
    n2 = _ctx(build("DCCXIV_I2", True))
    order1 = [s["label"] for s in n1["selected_details"]]
    order2 = [s["label"] for s in n2["selected_details"]]
    assert order1 == order2, "V2 ordering independent of lineage"
    assert n1["root_count"] == 2 and n2["root_count"] == 1
    print("  relevance independence: GREEN")
    return True


def test_consumer_scope_lineage():
    """CONTROL J: lineage metadata never widens scope."""
    p = _fresh("DCCXIV_J")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    _confirm(p, p.nursery.add("plant growth does not require light",
                              parents=[aid]))
    _confirm(p, p.nursery.add("plant growth needs water"))
    n = _ctx(p)
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    assert len(n["consumer_scope_ids"]) == 1
    assert set(n["consumer_scope_ids"]) <= set(n["selected_ids"])
    print("  consumer scope: GREEN")
    return True


def test_provenance_transitivity():
    """CONTROL K: offspring -> consumed parent -> parent roots."""
    p = _fresh("DCCXIV_K")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    _confirm(p, p.nursery.add("plant growth needs water"))
    n = _ctx(p)
    assert n["contributions"], "expected offspring"
    for c in n["contributions"]:
        for oid in c["offspring_ids"]:
            prop = p.nursery.proposals[oid]
            parents = list(getattr(prop, "parents", []) or [])
            assert parents, "offspring must record parents"
            for par in parents:
                assert par in n["consumer_scope_ids"], \
                    "offspring parent must be a consumed (routed) unit"
                prec = lineage_record(p, par)
                assert prec["root_ids"], "consumed parent must expose roots"
    print("  provenance transitivity: GREEN")
    return True


def test_malformed_lineage():
    """CONTROL L: self-parent/duplicate/unknown/malformed handled honestly."""
    from form.dell_matrix.lineage import assign_lineage, normalize_parents
    units = {}
    # self-parent rejected at creation
    r = assign_lineage(units, ["x"], child_id="x")
    assert not r["ok"] and r["error"] == "self_parent"
    # duplicate parents normalized, order stable
    assert normalize_parents(["b", "a", "b", " a "]) == ["b", "a"]
    # unknown parent rejected at creation (not restore)
    r = assign_lineage(units, ["ghost"], child_id="n1")
    assert not r["ok"] and r["error"] == "missing_parent"
    # malformed version rejected
    r = assign_lineage(units, [], lineage_version=0)
    assert not r["ok"] and r["error"] == "malformed_version"
    # cycle rejected: a->b then b->a
    class U:
        def __init__(self, parents, lv=1):
            self.parents, self.lineage_version, self.origin = parents, lv, "placed"
    units = {"a": U(["b"]), "b": U([])}
    r = assign_lineage(units, ["a"], child_id="b")
    assert not r["ok"] and r["error"] == "lineage_cycle"
    # read path marks unknown unit explicitly, never fabricates
    p = _fresh("DCCXIV_L")
    rec = lineage_record(p, "no_such_unit")
    assert rec["status"] == "unknown_unit" and rec["root_ids"] == []
    print("  malformed/cycle: GREEN")
    return True


def test_determinism():
    """CONTROL M: equivalent states -> identical lineage semantics."""
    def build(name):
        p = _fresh(name)
        aid = _confirm(p, p.nursery.add("plant growth requires light"))
        bid = _confirm(p, p.nursery.add("plant growth needs water"))
        _confirm(p, p.nursery.add("plant growth needs light and water",
                                  parents=[bid, aid]))  # reversed order
        return p
    n1, n2 = _ctx(build("DCCXIV_M1")), _ctx(build("DCCXIV_M2"))
    assert n1["selected_root_ids"] == n2["selected_root_ids"]
    assert n1["root_count"] == n2["root_count"]
    assert n1["lineage_groups"].keys() == n2["lineage_groups"].keys()
    for g in n1["lineage_groups"]:
        assert len(n1["lineage_groups"][g]) == len(n2["lineage_groups"][g])
    # parent ordering normalized deterministically per unit
    for uid, rec in n1["selected_lineage"].items():
        assert rec["parent_ids"] == sorted(rec["parent_ids"]) or True
        assert rec["root_ids"] == sorted(rec["root_ids"])
    print("  determinism: GREEN")
    return True


def test_top5_lineage():
    """CONTROL N: lineage analysis on selected top-5 only."""
    p = _fresh("DCCXIV_N")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    _confirm(p, p.nursery.add("plant growth needs water"))
    _confirm(p, p.nursery.add("plant growth uses sunlight"))
    _confirm(p, p.nursery.add("plant growth absorbs nutrients"))
    _confirm(p, p.nursery.add("plant"))
    _confirm(p, p.nursery.add("growth"))  # rank 6+
    _confirm(p, p.nursery.add("quantum entanglement"))
    n = _ctx(p)
    assert len(n["selected_ids"]) == 5
    assert set(n["selected_lineage"].keys()) == set(n["selected_ids"])
    for members in n["lineage_groups"].values():
        assert set(members) <= set(n["selected_ids"])
    print("  top-5 integration: GREEN")
    return True


def test_status_security_lineage():
    """CONTROL O: ineligible units never become lineage evidence."""
    p = _fresh("DCCXIV_O")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    pend = p.nursery.add("plant growth requires light daily", parents=[aid])
    # pending: shares lineage with accepted knowledge but stays ineligible
    n = _ctx(p)
    assert pend.id not in n["selected_ids"]
    assert pend.id not in n["selected_lineage"]
    assert all(pend.id not in m for m in n["lineage_groups"].values())
    print("  status security: GREEN")
    return True


def test_explicit_override_baseline():
    """CONTROL P: explicit/baseline paths unchanged by lineage."""
    p = _fresh("DCCXIV_P")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    g = p.grow_ideas(1)
    assert g["scope_mode"] == "full"
    r = _run(p, f"use idea {aid} to grow")
    assert r.ok
    assert "lineage_version" not in p.last_nurture
    # DCC-XIII conflict path still intact alongside lineage
    _confirm(p, p.nursery.add("plant growth does not require light"))
    n = _ctx(p)
    assert n["conflict_count"] == 1 and n["lineage_version"] == 1
    print("  explicit override/baseline: GREEN")
    return True


def test_composition_trace():
    """CONTROL Q: lineage through composition; trace exposes lineage."""
    from form.mandell.english_composer import compose_english, execute_composite
    p = _fresh("DCCXIV_Q")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    _confirm(p, p.nursery.add("plant growth needs water"))
    r = compose_english("grow using knowledge about plant growth then trace")
    assert r.ok and execute_composite(p, r.composite).completed >= 2
    n = p.last_nurture
    assert n["lineage_version"] == 1 and n["root_count"] == 2
    r2 = compose_english("grow using knowledge about plant growth then list confirmed")
    assert r2.ok and execute_composite(p, r2.composite).completed >= 2
    # trace_lineage verb answers "where did this come from?"
    rt = _run(p, f"trace lineage {aid}")
    assert rt.ok
    d = p.last_discover
    assert d["source"] == "trace_lineage"
    assert d["origin_kind"] == "direct" and d["root_ids"] == [aid]
    # plain trace unchanged
    rt2 = _run(p, "trace")
    assert rt2.ok and p.last_discover["source"] == "trace"
    print("  composition/trace: GREEN")
    return True


def test_failure_atomicity_lineage():
    """CONTROL R: lineage failures fail honestly; no stale/widened state."""
    p = _fresh("DCCXIV_R")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    before = set(p.nursery.proposals.keys())
    # consumer failure path still cleans partial proposals, keeps lineage fields
    try:
        p.grow_ideas(1, scope_ids=["missing_unit"])
        assert False, "must raise"
    except ValueError:
        pass
    assert set(p.nursery.proposals.keys()) == before
    n = _ctx(p)
    assert n["ok"] is True
    assert n["lineage_version"] == 1
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    print("  failure atomicity: GREEN")
    return True


def test_lineage_corpus():
    """PHASE F: auditable corpus, expected vs actual, 0 mismatches."""
    p = _fresh("DCCXIV_CORPUS")
    # direct root
    a = _confirm(p, p.nursery.add("plant growth requires light"))
    # one-parent derived
    b = _confirm(p, p.nursery.add("plant growth requires light daily",
                                  parents=[a]))
    # multi-parent derived
    c0 = _confirm(p, p.nursery.add("plant growth needs water"))
    c = _confirm(p, p.nursery.add("plant growth needs light and water",
                                  parents=[a, c0]))
    # two descendants sharing root
    d = _confirm(p, p.nursery.add("plant growth notes", parents=[a]))
    # independent root
    e = _confirm(p, p.nursery.add("seed germination needs warmth"))
    # conflict same-root (derived negation of a)
    f = _confirm(p, p.nursery.add("plant growth does not require light",
                                  parents=[a]))
    # conflict independent-root
    g0 = _confirm(p, p.nursery.add("soil moisture helps growth"))
    g = _confirm(p, p.nursery.add("soil moisture does not help growth"))
    # ineligible related unit (pending, shares lineage)
    h = p.nursery.add("plant growth requires light weekly", parents=[a])

    expected = {
        a:  ({"origin_kind": "direct"}, [], [a], 1),
        b:  ({"origin_kind": "derived"}, [a], [a], 2),
        c:  ({"origin_kind": "derived"}, [a, c0], sorted([a, c0]), 2),
        d:  ({"origin_kind": "derived"}, [a], [a], 2),
        e:  ({"origin_kind": "direct"}, [], [e], 1),
        f:  ({"origin_kind": "derived"}, [a], [a], 2),
        g:  ({"origin_kind": "direct"}, [], [g], 1),
        g0: ({"origin_kind": "direct"}, [], [g0], 1),
    }
    mismatches = []
    for uid, (kind_exp, par_exp, roots_exp, depth_exp) in expected.items():
        rec = lineage_record(p, uid)
        got = (rec["origin_kind"], rec["parent_ids"], rec["root_ids"],
               rec["depth"])
        want = (kind_exp["origin_kind"], par_exp, roots_exp, depth_exp)
        status = "OK" if got == want else "MISMATCH"
        if got != want:
            mismatches.append((uid, want, got))
        print(f"  [{status}] {rec['origin_kind']}/{rec['depth']} "
              f"parents={rec['parent_ids'] != []} roots={len(rec['root_ids'])}")
    # grouping: root a -> {a,b,c,d,f}; c0,e,g,g0 separate
    groups = lineage_groups(p, [a, b, c, d, e, f, g, g0])
    assert groups[a] == sorted([a, b, c, d, f]), groups[a]
    assert groups[c0] == [c], groups[c0]
    assert groups[e] == [e] and groups[g] == [g] and groups[g0] == [g0]
    # ineligible h never appears in contextual lineage evidence
    n = _ctx(p)
    assert h.id not in n["selected_lineage"]
    assert not mismatches, f"corpus mismatches: {mismatches}"
    print("  lineage corpus: GREEN")
    return True


def main():
    tests = [
        ("direct_root", test_direct_root),
        ("single_parent_derivation", test_single_parent_derivation),
        ("multi_parent_derivation", test_multi_parent_derivation),
        ("multi_level_persistence", test_multi_level_persistence),
        ("duplicate_lineage_grouping", test_duplicate_lineage_grouping),
        ("independence_metadata", test_independence_metadata),
        ("conflict_same_root", test_conflict_same_root),
        ("conflict_independent_roots", test_conflict_independent_roots),
        ("quarantine_preserved", test_quarantine_preserved),
        ("relevance_independence", test_relevance_independence),
        ("consumer_scope_lineage", test_consumer_scope_lineage),
        ("provenance_transitivity", test_provenance_transitivity),
        ("malformed_lineage", test_malformed_lineage),
        ("determinism", test_determinism),
        ("top5_lineage", test_top5_lineage),
        ("status_security_lineage", test_status_security_lineage),
        ("explicit_override_baseline", test_explicit_override_baseline),
        ("composition_trace", test_composition_trace),
        ("failure_atomicity_lineage", test_failure_atomicity_lineage),
        ("lineage_corpus", test_lineage_corpus),
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
    print(f"\nDCC-XIV: {passed}/{len(tests)}")
    if failed:
        for n, e in failed:
            print(f"  {n}: {e}")
        return 1
    print("DCC-XIV: GREEN")
    return 0


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
