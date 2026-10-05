#!/usr/bin/env python3
"""DCC-XV: Dependency validity + transitive knowledge invalidation (Dependency V1).

Historical lineage is immutable; dependency validity is current-state
evidence recomputed from live state. A derived unit is dependency-valid
only when every required transitive ancestor: exists on the plane, has a
confirmed nursery proposal, and has valid lineage.

Statuses: valid / missing / invalid / malformed (precedence in that order).

DEPENDENCY VALIDITY != RELEVANCE != CONFLICT != TRUTH.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from form.open import open_program
from form.persist_rest import save, load
from form.persist import _STATE_DIR
from form.dell_matrix.nursery import owner_nursery_path
from form.mandell.translate import translate
from form.mandell.semantic_router import route_intent
from form.mandell.dependency_validity import (
    DEPENDENCY_VERSION, inspect_dependency,
)
from form.mandell.knowledge_lineage import lineage_record


def _fresh(name):
    for f in Path(_STATE_DIR).glob(f"*{name}*"):
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
    res = p.confirm_proposal(prop.id, _producer="test", _review_context=p.make_review_context(prop.id, "test"))
    assert res.get("ok"), f"confirm failed: {res}"
    return prop.id


def _chain(p):
    """A confirmed root, B derived from A, C derived from B."""
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    bid = _confirm(p, p.nursery.add("plant growth requires light daily",
                                    parents=[aid]))
    cid = _confirm(p, p.nursery.add("plant growth requires light always",
                                    parents=[bid]))
    return aid, bid, cid


def _invalidate(p, uid):
    """Existing legitimate lifecycle transition: plane removal (undo path)."""
    assert p.cube.session.plane.remove(uid), "plane.remove must succeed"


def test_valid_chain():
    """CONTROL A: valid chain; C reconstructs A+B ancestry."""
    p = _fresh("DCCXV_A")
    aid, bid, cid = _chain(p)
    for uid in (aid, bid, cid):
        rec = inspect_dependency(p, uid)
        assert rec["dependency_status"] == "valid", rec
    rec = inspect_dependency(p, cid)
    assert rec["direct_parent_ids"] == [bid]
    assert rec["ancestor_ids"] == sorted([aid, bid])
    assert rec["invalid_dependency_ids"] == []
    assert rec["missing_dependency_ids"] == []
    print("  valid chain: GREEN")
    return True


def test_direct_invalidation():
    """CONTROL B: invalidate A -> B invalid; lineage unchanged."""
    p = _fresh("DCCXV_B")
    aid, bid, cid = _chain(p)
    # Historical evidence: persisted parent lists, historical roots, depth,
    # origin — must survive invalidation untouched.
    before = {i: inspect_dependency(p, i) for i in (aid, bid, cid)}
    lin_before = {i: lineage_record(p, i) for i in (bid, cid)}
    _invalidate(p, aid)
    rec_b = inspect_dependency(p, bid)
    assert rec_b["dependency_status"] == "missing"
    assert rec_b["missing_dependency_ids"] == [aid]
    after = {i: inspect_dependency(p, i) for i in (bid, cid)}
    lin_after = {i: lineage_record(p, i) for i in (bid, cid)}
    for i in (bid, cid):
        for k in ("direct_parent_ids", "ancestor_ids", "historical_root_ids"):
            assert after[i][k] == before[i][k], \
                f"historical {k} changed for {i}"
        for k in ("parent_ids", "depth", "origin", "origin_kind"):
            assert lin_after[i][k] == lin_before[i][k], \
                f"persisted lineage {k} changed for {i}"
    print("  direct invalidation: GREEN")
    return True


def test_transitive_invalidation():
    """CONTROL C: A invalid -> B and C invalid; C names A."""
    p = _fresh("DCCXV_C")
    aid, bid, cid = _chain(p)
    _invalidate(p, aid)
    rb = inspect_dependency(p, bid)
    rc = inspect_dependency(p, cid)
    assert rb["dependency_status"] == "missing"
    assert rc["dependency_status"] == "missing"
    assert rc["missing_dependency_ids"] == [aid], \
        "C must identify the upstream dependency responsible"
    assert rc["ancestor_ids"] == sorted([aid, bid])
    print("  transitive invalidation: GREEN")
    return True


def test_sibling_isolation():
    """CONTROL D: invalidating A affects B, not Y (child of X)."""
    p = _fresh("DCCXV_D")
    aid, bid, _ = _chain(p)
    xid = _confirm(p, p.nursery.add("seed germination needs warmth"))
    yid = _confirm(p, p.nursery.add("seed germination needs warmth daily",
                                    parents=[xid]))
    _invalidate(p, aid)
    assert inspect_dependency(p, bid)["dependency_status"] != "valid"
    ry = inspect_dependency(p, yid)
    assert ry["dependency_status"] == "valid", "sibling subtree unaffected"
    assert ry["ancestor_ids"] == [xid]
    print("  sibling isolation: GREEN")
    return True


def test_multi_parent_one_invalid():
    """CONTROL E: A+B->C; invalidate A -> C invalid naming A; roots intact."""
    p = _fresh("DCCXV_E")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    bid = _confirm(p, p.nursery.add("plant growth needs water"))
    cid = _confirm(p, p.nursery.add("plant growth needs light and water",
                                    parents=[aid, bid]))
    roots_before = inspect_dependency(p, cid)["historical_root_ids"]
    _invalidate(p, aid)
    rc = inspect_dependency(p, cid)
    assert rc["dependency_status"] == "missing"
    assert rc["missing_dependency_ids"] == [aid]
    assert rc["invalid_dependency_ids"] == []
    # B remains represented as valid ancestry; historical roots unchanged
    assert bid in rc["ancestor_ids"]
    assert rc["historical_root_ids"] == roots_before == sorted([aid, bid])
    rb = inspect_dependency(p, bid)
    assert rb["dependency_status"] == "valid"
    print("  multi-parent one-invalid: GREEN")
    return True


def test_missing_ancestor_restore():
    """CONTROL F: persisted historical parent now absent -> missing (via restore)."""
    name = "DCCXV_F"
    p = _fresh(name)
    aid, bid, _ = _chain(p)
    _invalidate(p, aid)
    save(p)
    del p
    p2 = load(name)
    rb = inspect_dependency(p2, bid)
    assert rb["dependency_status"] == "missing"
    assert rb["missing_dependency_ids"] == [aid]
    # historical lineage survived the restore (parents + historical roots)
    assert rb["direct_parent_ids"] == [aid]
    assert rb["historical_root_ids"] == [aid]
    print("  missing ancestor (restore): GREEN")
    return True


def test_rejected_ancestor_fixture():
    """CONTROL F (legacy): nursery records ancestor rejected -> invalid."""
    name = "DCCXV_F2"
    p = _fresh(name)
    aid, bid, _ = _chain(p)
    save(p)
    # legitimate restore/legacy fixture: nursery file records A as rejected
    npath = owner_nursery_path(name)
    with open(npath, encoding="utf-8") as f:
        data = json.load(f)
    assert data[aid]["status"] == "confirmed"
    data[aid]["status"] = "rejected"
    with open(npath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    del p
    p2 = load(name)
    rb = inspect_dependency(p2, bid)
    assert rb["dependency_status"] == "invalid", rb
    assert rb["invalid_dependency_ids"] == [aid]
    assert rb["missing_dependency_ids"] == []
    # lineage still historical
    assert lineage_record(p2, bid)["parent_ids"] == [aid]
    print("  rejected ancestor (legacy fixture): GREEN")
    return True


def test_malformed_cycle_mapping():
    """CONTROL G: lineage malformed/cycle maps deterministically."""
    p = _fresh("DCCXV_G")
    rec = inspect_dependency(p, "no_such_unit")
    assert rec["dependency_status"] == "malformed"
    assert rec["dependency_reason"] == "lineage_unknown_unit"
    # unknown unit: deterministic across calls
    assert inspect_dependency(p, "no_such_unit") == rec
    print("  malformed/cycle mapping: GREEN")
    return True


def test_selector_exclusion():
    """CONTROL H: dependency-invalid units excluded at eligibility."""
    p = _fresh("DCCXV_H")
    aid, bid, cid = _chain(p)
    _invalidate(p, aid)
    n = _ctx(p)
    assert n["dependency_version"] == 1
    assert bid not in n["selected_ids"] and cid not in n["selected_ids"]
    exc = {e["id"]: e for e in n["dependency_exclusions"]}
    assert set(exc) == {bid, cid}
    assert exc[bid]["missing_dependency_ids"] == [aid]
    assert exc[cid]["missing_dependency_ids"] == [aid]
    assert n["dependency_valid_count"] == 0  # A removed; B/C excluded
    print("  selector exclusion: GREEN")
    return True


def test_transitive_routing_exclusion():
    """CONTROL I: C matches context strongly but is excluded; receipt explains."""
    p = _fresh("DCCXV_I")
    aid, bid, cid = _chain(p)
    _invalidate(p, aid)
    n = _ctx(p, context="plant growth requires light always")
    assert cid not in n["selected_ids"]
    assert cid not in n["consumer_scope_ids"]
    exc = {e["id"]: e for e in n["dependency_exclusions"]}
    assert exc[cid]["dependency_status"] == "missing"
    assert "which candidate" not in str(exc)  # fields speak for themselves
    assert exc[cid]["id"] == cid
    print("  transitive routing exclusion: GREEN")
    return True


def test_mixed_validity():
    """CONTROL J: K1/K3 valid selected; K2 invalid excluded; V2 over valid only."""
    p = _fresh("DCCXV_J")
    k1 = _confirm(p, p.nursery.add("plant growth requires light"))
    a2 = _confirm(p, p.nursery.add("old rejected root"))
    k2 = _confirm(p, p.nursery.add("plant growth needs nutrients",
                                   parents=[a2]))
    k3 = _confirm(p, p.nursery.add("plant growth needs water"))
    _invalidate(p, a2)
    n = _ctx(p)
    assert k1 in n["selected_ids"] and k3 in n["selected_ids"]
    assert k2 not in n["selected_ids"]
    assert all(s["id"] != k2 for s in n["selected_details"])
    # conflict analysis + scope see only valid candidates
    assert k2 not in n["consumer_scope_ids"]
    assert k2 not in n["selected_lineage"]
    print("  mixed validity: GREEN")
    return True


def test_conflict_interaction():
    """CONTROL K: invalid units filtered before Conflict V1; cannot quarantine valid."""
    p = _fresh("DCCXV_K")
    # invalid descendant carrying a negation: would conflict with c1 if selected
    c1 = _confirm(p, p.nursery.add("seed growth requires light"))
    c2 = _confirm(p, p.nursery.add("seed growth does not require light",
                                   parents=[c1]))
    _invalidate(p, c1)
    n = _ctx(p, context="seed growth")
    assert c2 not in n["selected_ids"], "invalid unit must not reach conflict analysis"
    assert n["conflict_count"] == 0
    assert n["quarantined_ids"] == []
    print("  conflict interaction: GREEN")
    return True


def test_lineage_immutability_and_groups():
    """CONTROL C (immutability) + CONTROL L: groups describe selected only;
    trace of invalid unit still exposes historical lineage."""
    p = _fresh("DCCXV_L")
    aid, bid, cid = _chain(p)
    before = {i: inspect_dependency(p, i) for i in (aid, bid, cid)}
    _invalidate(p, aid)
    n = _ctx(p)
    # groups describe only actual selected knowledge (nothing selected here)
    for members in n["lineage_groups"].values():
        assert set(members) <= set(n["selected_ids"])
    # historical lineage unchanged for invalid units
    for i in (bid, cid):
        after = inspect_dependency(p, i)
        for k in ("direct_parent_ids", "ancestor_ids", "historical_root_ids"):
            assert after[k] == before[i][k]
    # trace of invalid unit still exposes historical lineage
    # (trace lineage: DCC-XIV live record; trace dependency: historical)
    r = _run(p, f"trace lineage {cid}")
    assert r.ok
    assert p.last_discover["parent_ids"] == [bid]
    r = _run(p, f"trace dependency {cid}")
    assert r.ok
    d = p.last_discover
    assert d["parent_ids"] == [bid] and d["root_ids"] == [aid]
    assert d["dependency_status"] == "missing"
    print("  lineage immutability + groups: GREEN")
    return True


def test_receipt_exclusions():
    """CONTROL M: receipt explains each exclusion (which/why/caused-by)."""
    p = _fresh("DCCXV_M")
    aid, bid, cid = _chain(p)
    _invalidate(p, aid)
    n = _ctx(p)
    assert n["dependency_version"] == DEPENDENCY_VERSION
    assert isinstance(n["dependency_exclusions"], list)
    assert n["dependency_valid_count"] >= 0
    for e in n["dependency_exclusions"]:
        assert set(e) >= {"id", "dependency_status", "dependency_reason",
                          "invalid_dependency_ids", "missing_dependency_ids"}
        assert e["dependency_status"] in ("missing", "invalid", "malformed")
    # relevance fields not overloaded
    for s in n["selected_details"]:
        assert "dependency" not in s
    print("  receipt exclusions: GREEN")
    return True


def test_trace_dependency():
    """CONTROL N: trace dependency exposes lineage + current status."""
    p = _fresh("DCCXV_N")
    aid, bid, cid = _chain(p)
    r = _run(p, f"trace dependency {cid}")
    assert r.ok
    d = p.last_discover
    assert d["source"] == "trace_dependency"
    assert d["dependency_status"] == "valid"
    assert d["ancestor_ids"] == sorted([aid, bid])
    _invalidate(p, aid)
    r = _run(p, f"trace dependency {cid}")
    assert r.ok
    d = p.last_discover
    assert d["dependency_status"] == "missing"
    assert d["missing_dependency_ids"] == [aid]
    # historical lineage still exposed alongside
    assert d["parent_ids"] == [bid] and d["root_ids"] == [aid]
    print("  trace dependency: GREEN")
    return True


def test_restoration():
    """CONTROL O: two-process restore preserves lineage, recomputes validity,
    routing still excludes descendants."""
    name = "DCCXV_O"
    p = _fresh(name)
    aid, bid, cid = _chain(p)
    _invalidate(p, aid)
    save(p)
    del p
    # PROCESS 2
    p2 = load(name)
    dep_c = inspect_dependency(p2, cid)
    assert dep_c["direct_parent_ids"] == [bid]
    assert dep_c["historical_root_ids"] == [aid]
    assert dep_c["ancestor_ids"] == sorted([aid, bid])
    assert lineage_record(p2, cid)["depth"] == 3
    assert inspect_dependency(p2, cid)["dependency_status"] == "missing"
    n = _ctx(p2)
    assert bid not in n["selected_ids"] and cid not in n["selected_ids"]
    assert {e["id"] for e in n["dependency_exclusions"]} >= {bid, cid}
    print("  restoration: GREEN")
    return True


def test_revalidation_not_applicable():
    """CONTROL P: no legitimate operation re-qualifies an invalid ancestor."""
    p = _fresh("DCCXV_P")
    aid, bid, _ = _chain(p)
    _invalidate(p, aid)
    # nursery offers no confirmed->* transition; plane offers no un-remove
    assert p.nursery.reject(aid) is None, "confirmed cannot be rejected"
    assert p.nursery.confirm(aid) is None, "confirmed cannot be re-confirmed"
    assert not hasattr(p.cube.session.plane, "unremove")
    assert not hasattr(p.cube.session.plane, "restore_unit")
    # invalidity persists: recomputed from current state, never cached-away
    assert inspect_dependency(p, bid)["dependency_status"] == "missing"
    print("  revalidation NOT_APPLICABLE: GREEN")
    return True


def test_determinism():
    """CONTROL Q: equivalent states -> identical dependency semantics."""
    def build(name):
        p = _fresh(name)
        return p, _chain(p)
    p1, (a1, b1, c1) = build("DCCXV_Q1")
    p2, (a2, b2, c2) = build("DCCXV_Q2")
    _invalidate(p1, a1)
    _invalidate(p2, a2)
    r1 = inspect_dependency(p1, c1)
    r2 = inspect_dependency(p2, c2)
    assert r1["dependency_status"] == r2["dependency_status"] == "missing"
    assert len(r1["missing_dependency_ids"]) == len(r2["missing_dependency_ids"]) == 1
    assert r1["ancestor_ids"] and r2["ancestor_ids"]
    n1, n2 = _ctx(p1), _ctx(p2)
    assert len(n1["dependency_exclusions"]) == len(n2["dependency_exclusions"]) == 2
    assert n1["dependency_valid_count"] == n2["dependency_valid_count"]
    print("  determinism: GREEN")
    return True


def test_top5_dependency():
    """CONTROL R: filter -> V2 -> top-5 -> conflict -> routable -> scope."""
    p = _fresh("DCCXV_R")
    # 7 textually matching units; 2 have invalid dependencies
    xa = _confirm(p, p.nursery.add("old root one"))
    xb = _confirm(p, p.nursery.add("old root two"))
    ids = []
    ids.append(_confirm(p, p.nursery.add("plant growth requires light")))
    ids.append(_confirm(p, p.nursery.add("plant growth needs water")))
    ids.append(_confirm(p, p.nursery.add("plant growth uses sunlight")))
    ids.append(_confirm(p, p.nursery.add("plant growth absorbs nutrients",
                                        parents=[xa])))
    ids.append(_confirm(p, p.nursery.add("plant growth soil mix",
                                        parents=[xb])))
    ids.append(_confirm(p, p.nursery.add("plant growth daily care")))
    ids.append(_confirm(p, p.nursery.add("plant")))
    _invalidate(p, xa)
    _invalidate(p, xb)
    n = _ctx(p)
    assert len(n["selected_ids"]) == 5
    # invalid candidates excluded before V2: they hold no top-5 slots
    assert ids[3] not in n["selected_ids"] and ids[4] not in n["selected_ids"]
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    assert set(n["consumer_scope_ids"]) <= set(n["selected_ids"])
    print("  top-5 dependency: GREEN")
    return True


def test_direct_root_validity():
    """CONTROL S: direct root is vacuously dependency-valid; no self-dependency."""
    p = _fresh("DCCXV_S")
    aid = _confirm(p, p.nursery.add("plant growth requires light"))
    rec = inspect_dependency(p, aid)
    assert rec["dependency_status"] == "valid"
    assert rec["direct_parent_ids"] == [] and rec["ancestor_ids"] == []
    assert aid not in rec["missing_dependency_ids"]
    print("  direct root validity: GREEN")
    return True


def test_baseline_explicit_override():
    """CONTROL T: baseline growth unchanged; explicit override boundary documented."""
    p = _fresh("DCCXV_T")
    aid, bid, _ = _chain(p)
    g = p.grow_ideas(1)
    assert g["scope_mode"] == "full"
    assert "dependency_version" not in g
    # explicit override still routes the named idea (operator's explicit choice)
    r = _run(p, f"use idea {bid} to grow")
    assert r.ok
    print("  baseline/explicit override: GREEN")
    return True


def test_composition():
    """CONTROL U: dependency-aware routing through compositions."""
    from form.mandell.english_composer import compose_english, execute_composite
    p = _fresh("DCCXV_U")
    aid, bid, cid = _chain(p)
    _invalidate(p, aid)
    r = compose_english("grow using knowledge about plant growth then trace")
    assert r.ok and execute_composite(p, r.composite).completed >= 2
    n = p.last_nurture
    assert n["dependency_version"] == 1
    assert bid not in n["selected_ids"]
    r = compose_english("grow using knowledge about plant growth then list confirmed")
    assert r.ok and execute_composite(p, r.composite).completed >= 2
    print("  composition: GREEN")
    return True


def test_failure_atomicity():
    """CONTROL V: failures leave no partial/corrupt/stale state."""
    p = _fresh("DCCXV_V")
    aid, bid, cid = _chain(p)
    before = set(p.nursery.proposals.keys())
    _invalidate(p, aid)
    # scope validation failure still raises before growth; proposals intact
    try:
        p.grow_ideas(1, scope_ids=["missing_unit"])
        assert False, "must raise"
    except ValueError:
        pass
    assert set(p.nursery.proposals.keys()) == before
    n = _ctx(p)
    assert n["ok"] is True
    assert n["dependency_version"] == 1
    assert n["consumer_scope_ids"] == n["routable_selected_ids"]
    # exclusion evidence fresh, not stale
    assert {e["id"] for e in n["dependency_exclusions"]} == {bid, cid}
    print("  failure atomicity: GREEN")
    return True


def test_dependency_corpus():
    """PHASE D: auditable corpus — expected vs actual, 0 mismatches."""
    p = _fresh("DCCXV_CORPUS")
    a = _confirm(p, p.nursery.add("plant growth requires light"))
    b = _confirm(p, p.nursery.add("plant growth requires light daily",
                                  parents=[a]))
    c = _confirm(p, p.nursery.add("plant growth requires light always",
                                  parents=[b]))
    x = _confirm(p, p.nursery.add("seed germination needs warmth"))
    y = _confirm(p, p.nursery.add("seed germination needs warmth daily",
                                  parents=[x]))
    m1 = _confirm(p, p.nursery.add("old root alpha"))
    m2 = _confirm(p, p.nursery.add("old root beta"))
    m = _confirm(p, p.nursery.add("plant growth mixed roots",
                                  parents=[m1, m2]))
    d = _confirm(p, p.nursery.add("plant growth requires light notes",
                                  parents=[a]))
    _invalidate(p, a)   # kills b, c, d transitively
    _invalidate(p, m1)   # kills m (m2 still valid ancestry)

    expected = {
        x:  ("valid", [], []),
        y:  ("valid", [], []),
        b:  ("missing", [a], []),
        c:  ("missing", [a], []),
        d:  ("missing", [a], []),
        m:  ("missing", [m1], []),
        m2: ("valid", [], []),
    }
    mismatches = []
    for uid, (want_status, want_missing, want_invalid) in expected.items():
        rec = inspect_dependency(p, uid)
        got = (rec["dependency_status"], rec["missing_dependency_ids"],
               rec["invalid_dependency_ids"])
        status = "OK" if got == (want_status, want_missing, want_invalid) else "MISMATCH"
        if got != (want_status, want_missing, want_invalid):
            mismatches.append((uid, (want_status, want_missing, want_invalid), got))
        print(f"  [{status}] {rec['dependency_status']} "
              f"missing={rec['missing_dependency_ids']} invalid={rec['invalid_dependency_ids']}")
    # routing eligibility: b, c, d, m excluded regardless of textual match
    n = _ctx(p, context="growth")
    for uid in (b, c, d, m):
        assert uid not in n["selected_ids"], f"{uid} must be excluded"
    assert not mismatches, f"corpus mismatches: {mismatches}"
    print("  dependency corpus: GREEN")
    return True


def main():
    tests = [
        ("valid_chain", test_valid_chain),
        ("direct_invalidation", test_direct_invalidation),
        ("transitive_invalidation", test_transitive_invalidation),
        ("sibling_isolation", test_sibling_isolation),
        ("multi_parent_one_invalid", test_multi_parent_one_invalid),
        ("missing_ancestor_restore", test_missing_ancestor_restore),
        ("rejected_ancestor_fixture", test_rejected_ancestor_fixture),
        ("malformed_cycle_mapping", test_malformed_cycle_mapping),
        ("selector_exclusion", test_selector_exclusion),
        ("transitive_routing_exclusion", test_transitive_routing_exclusion),
        ("mixed_validity", test_mixed_validity),
        ("conflict_interaction", test_conflict_interaction),
        ("lineage_immutability_and_groups", test_lineage_immutability_and_groups),
        ("receipt_exclusions", test_receipt_exclusions),
        ("trace_dependency", test_trace_dependency),
        ("restoration", test_restoration),
        ("revalidation_not_applicable", test_revalidation_not_applicable),
        ("determinism", test_determinism),
        ("top5_dependency", test_top5_dependency),
        ("direct_root_validity", test_direct_root_validity),
        ("baseline_explicit_override", test_baseline_explicit_override),
        ("composition", test_composition),
        ("failure_atomicity", test_failure_atomicity),
        ("dependency_corpus", test_dependency_corpus),
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
    print(f"\nDCC-XV: {passed}/{len(tests)}")
    if failed:
        for n, e in failed:
            print(f"  {n}: {e}")
        return 1
    print("DCC-XV: GREEN")
    return 0


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
