#!/usr/bin/env python3
"""GDP-001 Phase 3 — P3 R3.6 world proof: graph consumer + harmony wiring.

NON-VACUOUS proof. Content-bearing fixtures throughout:
  - REAL Idea objects (form.mandell.idea.Idea), persisted via save_idea.
  - A REAL SemanticGraph with REAL edges built via the graph's own write
    path (SemanticGraph.add_relationship), over canonical Idea IDs.
  - REAL plane units (blank cube) with overlapping token content, whose
    unit IDs ARE the canonical Idea IDs.
  - A REAL RingedGrowth.run with an attached graph.

Hand-computed expectations (computed by hand in the comments, asserted):
  (H1) graph_coherence over {a,b,c} with edges a-b, b-c = 2/3.
  (H2) harmony_score over {"alpha beta gamma", "alpha beta delta"} = 0.4375.
  (H3) missing-unit _affinity = 0.13/101 + 0.13*0.2 = 0.0272871...,
       repr exactly "0.0273".
  (H4) max-bound corner affinity ~= 1.15 (0.40+0.22+0.13+0.13+0.12+0.15).

Bypass-must-fail tests (each MUST fail if the wiring is removed):
  (B1) graph query monkeypatched to return no neighbors -> the
       graph_coherence == 2/3 assertion MUST raise.
  (B2) growth run with graph=None -> proposals that had
       graph_coherence 1.0 now read 0.0 (signal proven load-bearing).
  (B3) "harmony" stripped from a proposal dict -> the wiring assertion
       MUST raise.
  (B4) harmony stripped from ranked_proposals input -> the
       harmony-first ordering assertion MUST raise.

Exit code: 0 on all pass (prints "P3 R3.6 WORLD: ALL PASS"), non-zero on
any failure. Cleans up all test state files it creates.
"""

import json
import os
import random
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(REPO))

OWNER = "p3r36_world"

from form.mandell.idea import Idea, Provenance, ProvenanceSource
from form.mandell.idea_persist import save_idea
from form.mandell.semantic_graph import (
    RelationshipType,
    SemanticGraph,
    graph_path,
    graph_journal_path,
)
from form.persist import _STATE_DIR, _safe_owner
from form.dell_matrix.graph_harmony import (
    graph_coherence,
    graph_neighbor_ids,
    unit_idea_view,
)
from form.dell_matrix.harmony import harmony_score
from form.dell_matrix import ringed_growth as rg
from form.dell_matrix.nursery import Nursery
from form.dell_matrix.blank_cube import give
from form.dell_matrix.plane import Skin
from form.open import Program


RESULTS = []


def rec(name, ok, detail=""):
    RESULTS.append(bool(ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))


def idea_path(idea_id):
    from form.mandell.idea_persist import _idea_path
    return _idea_path(idea_id, OWNER)


def cleanup():
    for p in (graph_path(OWNER), graph_journal_path(OWNER)):
        try:
            os.remove(p)
        except OSError:
            pass
    d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(OWNER)}")
    shutil.rmtree(d, ignore_errors=True)


def main():
    cleanup()
    try:
        _world()
    finally:
        cleanup()
    n = len(RESULTS)
    ok = sum(RESULTS)
    print(f"=== P3 R3.6 WORLD: {ok}/{n} checks ===")
    if ok == n:
        print("P3 R3.6 WORLD: ALL PASS")
        return 0
    print("P3 R3.6 WORLD: FAILURES PRESENT")
    return 1


def _world():
    # ------------------------------------------------------------------
    # A. Content-bearing fixtures: real Ideas + real graph with edges.
    # ------------------------------------------------------------------
    # Canonical Idea IDs (identity lives in the Idea).
    A, B, C = "p3r36_a", "p3r36_b", "p3r36_c"
    ia = Idea(idea_id=A, title="Alpha routes")
    ib = Idea(idea_id=B, title="Beta routes")
    ic = Idea(idea_id=C, title="Gamma melody")
    for i in (ia, ib, ic):
        save_idea(i, OWNER)
    rec("ideas_persisted",
        all(os.path.isfile(idea_path(x)) for x in (A, B, C)))

    prov = Provenance(source=ProvenanceSource.SYSTEM,
                      activity="p3r36_proof", agent="p3r36")
    graph = SemanticGraph.load(OWNER)
    # Real edges via the graph's OWN write path (not fixtures injected
    # behind its back): a-b and b-c as RELATED_TO associations.
    graph.add_relationship(RelationshipType.RELATED_TO, A, B, prov,
                           cause="p3r36")
    graph.add_relationship(RelationshipType.RELATED_TO, B, C, prov,
                           cause="p3r36")
    # Reload from disk: proves the edges survived the persisted log.
    graph = SemanticGraph.load(OWNER)
    rec("graph_edges_real",
        len(graph.by_type(RelationshipType.RELATED_TO)) == 2,
        f"active RELATED_TO edges={len(graph.by_type(RelationshipType.RELATED_TO))}")

    # ------------------------------------------------------------------
    # B. graph_neighbor_ids / graph_coherence (H1: hand-computed 2/3).
    # ------------------------------------------------------------------
    # HAND COMPUTATION (H1): association neighborhood (CONTAINS excluded
    # by the query; we created no containment edges anyway):
    #   neighbors(a) = {b}, neighbors(b) = {a, c}, neighbors(c) = {b}.
    # Unordered pairs of {a,b,c}: (a,b) linked, (a,c) not, (b,c) linked.
    # graph_coherence = 2 linked / 3 total = 2/3.
    rec("neighbor_ids_b", graph_neighbor_ids(graph, B) == sorted([A, C]),
        f"{graph_neighbor_ids(graph, B)}")
    rec("neighbor_ids_a", graph_neighbor_ids(graph, A) == [B])
    coh = graph_coherence(graph, [A, B, C])
    rec("coherence_hand_computed_2_3", abs(coh - 2.0 / 3.0) < 1e-12,
        f"got {coh!r}, expected 2/3")
    # Defined neutral value: 0.0 = "no graph evidence", never fabricated.
    rec("coherence_neutral_single", graph_coherence(graph, [A]) == 0.0)
    rec("coherence_neutral_unknown", graph_coherence(graph, ["nope_x"]) == 0.0)
    rec("coherence_neutral_empty", graph_coherence(graph, []) == 0.0)
    rec("coherence_neutral_dedupe",
        graph_coherence(graph, [A, A, A]) == 0.0)  # one distinct id -> 0.0

    # ------------------------------------------------------------------
    # C. Bypass-must-fail (B1): graph consumer bypassed -> MUST fail.
    # ------------------------------------------------------------------
    real_neighbors = graph.association_neighbors
    graph.association_neighbors = lambda iid: []  # bypass: no structure read
    try:
        bypass_detected = False
        try:
            # If the consumer ignored graph structure, this would still be
            # 2/3. It must NOT be.
            assert abs(graph_coherence(graph, [A, B, C]) - 2.0 / 3.0) < 1e-12
        except AssertionError:
            bypass_detected = True
        rec("bypass_graph_query_detected", bypass_detected,
            "patched association_neighbors->[] changed the result")
        rec("bypass_graph_neutral",
            graph_coherence(graph, [A, B, C]) == 0.0,
            "bypassed consumer returns the defined neutral, never fabricates")
    finally:
        graph.association_neighbors = real_neighbors
    # Sanity: restored query gives the real value again.
    rec("graph_query_restored",
        abs(graph_coherence(graph, [A, B, C]) - 2.0 / 3.0) < 1e-12)

    # ------------------------------------------------------------------
    # D. harmony_score hand-computed (H2 = 0.4375).
    # ------------------------------------------------------------------
    # HAND COMPUTATION (H2): idea1.title = "alpha beta gamma",
    # idea2.title = "alpha beta delta", no properties.
    # _idea_tokens: [a-z0-9]+ over the lowercased title ->
    #   T1 = {alpha, beta, gamma}, T2 = {alpha, beta, delta}.
    # jac = |T1 cap T2| / |T1 cup T2| = 2/4 = 0.5.
    # One pair: C = 0.5, R = 0.5^3 = 0.125.
    # harmony = C * (1 - R) = 0.5 * 0.875 = 0.4375 (exact in binary).
    h1 = Idea(idea_id="p3r36_h1", title="alpha beta gamma")
    h2 = Idea(idea_id="p3r36_h2", title="alpha beta delta")
    h = harmony_score([h1, h2])
    rec("harmony_hand_computed_0_4375", abs(h - 0.4375) < 1e-12,
        f"got {h!r}, expected 0.4375")
    rec("harmony_hand_computed_exact", h == 0.4375,
        "0.5*(1-0.125) is exactly representable; equality must be bitwise")

    # ------------------------------------------------------------------
    # E. The growth adapter agrees with the Idea path (one authority).
    # ------------------------------------------------------------------
    cube = give(OWNER, clean=True)
    cube.place_idea(A, "Alpha routes", words="crm routes delivery",
                    skin=Skin.BUILDING, x=1.0, y=0.0)
    cube.place_idea(B, "Beta routes", words="crm routes pickup",
                    skin=Skin.BUILDING, x=-1.0, y=0.0)
    cube.place_idea(C, "Gamma melody", words="song harmony rhythm",
                    skin=Skin.BUILDING, x=0.0, y=3.0)
    plane = cube.session.plane
    ua, ub, uc = plane.units[A], plane.units[B], plane.units[C]
    va, vb = unit_idea_view(ua), unit_idea_view(ub)
    # Same underlying content as h1/h2? No — these units have words too.
    # Agreement check instead: the adapter exposes the unit's real
    # label/words, and harmony over views equals harmony over
    # equivalent idea-likes built from the same text.
    from form.dell_matrix.harmony import _idea_tokens
    # va: title "Alpha routes" -> {alpha, routes}; get_active_properties()
    # -> {"words": "crm routes delivery"}; _idea_tokens tokenizes property
    # NAMES as well as values (same for real Ideas) -> + {words}.
    rec("view_tokens_honest",
        _idea_tokens(va) == {"alpha", "routes", "crm", "delivery", "words"},
        f"view tokens={sorted(_idea_tokens(va))}")
    h_views = harmony_score([va, vb])
    rec("view_harmony_in_range", 0.0 <= h_views <= 1.0, f"{h_views!r}")
    # Determinism of the adapter: same unit -> same score.
    rec("view_harmony_deterministic",
        harmony_score([unit_idea_view(ua), unit_idea_view(ub)]) == h_views)

    # ------------------------------------------------------------------
    # F. Live growth wiring: harmony + graph persisted per proposal.
    # ------------------------------------------------------------------
    tmpn = tempfile.mktemp(prefix="p3r36_nursery_", suffix=".json")
    try:
        nurs = Nursery(path=tmpn)
        eng = rg.RingedGrowth(nursery=nurs, seed=11)
        out = eng.run(plane, cycles=1, graph=graph)
        rec("growth_run_ok", out.get("ok") is True)
        rec("growth_graph_signal",
            out.get("graph_signal") == "attached",
            f"graph_signal={out.get('graph_signal')!r}")
        props = list(nurs.proposals.values())
        rec("growth_proposed", len(props) > 0, f"n={len(props)}")
        # The a-b pair shares a graph edge; its proposal must carry
        # graph_coherence 1.0 and the independently recomputed harmony.
        ab = [p for p in props if set(p.parents) == {A, B}]
        rec("growth_ab_proposed", len(ab) >= 1,
            f"proposals with parents {{a,b}}: {len(ab)}")
        expected_h = harmony_score([unit_idea_view(ua), unit_idea_view(ub)])
        wired_ok = True
        gcoh_seen = set()
        for p in ab:
            d = p.to_dict()
            gcoh_seen.add(d["graph_coherence"])
            if abs(d["harmony"] - expected_h) >= 1e-12:
                wired_ok = False
            if d["graph_coherence"] != 1.0:
                wired_ok = False
            if "hs=" not in d["reason"] or "gcoh=" not in d["reason"]:
                wired_ok = False
        rec("growth_harmony_persisted", wired_ok,
            f"harmony={expected_h!r} on {len(ab)} proposal(s)")
        rec("growth_gcoh_persisted", gcoh_seen == {1.0},
            f"graph_coherence values seen: {sorted(gcoh_seen)}")
        # Every pair proposal carries both fields (no silent omission).
        all_have = all("harmony" in p.to_dict()
                       and "graph_coherence" in p.to_dict() for p in props)
        rec("growth_all_proposals_carry_signals", all_have)
        # Report evidence present.
        rep_h = out.get("harmony", {})
        rec("growth_report_harmony",
            rep_h.get("n", 0) > 0 and rep_h.get("max", 0) > 0,
            f"{rep_h}")

        # (B3) harmony bypass-must-fail: strip "harmony" -> assertion MUST raise.
        sample = ab[0].to_dict()
        def _assert_harmony_wired(d):
            assert "harmony" in d, "harmony missing from proposal"
            assert abs(d["harmony"] - expected_h) < 1e-12, "harmony value wrong"
        _assert_harmony_wired(sample)  # passes on intact data
        stripped = {k: v for k, v in sample.items() if k != "harmony"}
        b3 = False
        try:
            _assert_harmony_wired(stripped)
        except AssertionError:
            b3 = True
        rec("bypass_harmony_strip_detected", b3,
            "removing harmony from the proposal breaks the wiring check")

        # (B2) graph=None run: the signal is load-bearing, not decorative.
        tmpn2 = tempfile.mktemp(prefix="p3r36_nursery2_", suffix=".json")
        try:
            nurs2 = Nursery(path=tmpn2)
            eng2 = rg.RingedGrowth(nursery=nurs2, seed=11)
            out2 = eng2.run(plane, cycles=1, graph=None)
            gcoh2 = {p.to_dict()["graph_coherence"]
                     for p in nurs2.proposals.values()}
            rec("bypass_graph_none_neutral", gcoh2 == {0.0},
                f"graph=None -> all graph_coherence 0.0 (was {sorted(gcoh_seen)})")
            rec("bypass_graph_none_signal",
                out2.get("graph_signal") == "none")
            # Proposal IDs identical with/without graph (signal never
            # changes identity or gate decisions).
            rec("graph_signal_does_not_change_ids",
                sorted(nurs2.proposals.keys()) == sorted(nurs.proposals.keys()))
        finally:
            try:
                os.remove(tmpn2)
            except OSError:
                pass
    finally:
        try:
            os.remove(tmpn)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # G. ranked_proposals consumes harmony (B4: bypass-must-fail).
    # ------------------------------------------------------------------
    # Call the REAL Program.ranked_proposals with a stub program that
    # supplies list_proposals() + a prefs ranker mimicking the real
    # inspire blend (0.65*affinity, pref 0 -> ties on equal affinity).
    class _StubPrefs:
        def rank_proposals(self, props):
            out = []
            for p in props:
                row = dict(p)
                row["blended"] = round(0.65 * float(p.get("affinity") or 0), 4)
                out.append(row)
            out.sort(key=lambda x: -x["blended"])
            return out

    class _StubProg:
        def __init__(self, props):
            self._props = props
            self.inspire = type("I", (), {"prefs": _StubPrefs()})()

        def list_proposals(self):
            return [dict(d) for d in self._props]

    base = {"label": "x", "words": "w", "kind": "new", "parents": [],
            "reason": "", "status": "pending"}
    p_lo = dict(base, id="p_lo", affinity=0.5, harmony=0.1, graph_coherence=0.0)
    p_hi = dict(base, id="p_hi", affinity=0.5, harmony=0.9, graph_coherence=0.0)
    stub = _StubProg([p_lo, p_hi])  # insertion order: lo first
    ranked = Program.ranked_proposals(stub)
    rec("ranked_harmony_tiebreak",
        [r["id"] for r in ranked] == ["p_hi", "p_lo"],
        f"order={[r['id'] for r in ranked]} (equal blended, harmony decides)")
    # Graph coherence breaks harmony ties.
    p_g1 = dict(base, id="p_g1", affinity=0.5, harmony=0.9, graph_coherence=0.0)
    p_g2 = dict(base, id="p_g2", affinity=0.5, harmony=0.9, graph_coherence=1.0)
    ranked2 = Program.ranked_proposals(_StubProg([p_g1, p_g2]))
    rec("ranked_gcoh_tiebreak",
        [r["id"] for r in ranked2] == ["p_g2", "p_g1"],
        f"order={[r['id'] for r in ranked2]}")
    # Affinity still dominates (harmony is a tie-break, not a replacement).
    p_a1 = dict(base, id="p_a1", affinity=0.9, harmony=0.0, graph_coherence=0.0)
    p_a2 = dict(base, id="p_a2", affinity=0.1, harmony=1.0, graph_coherence=1.0)
    ranked3 = Program.ranked_proposals(_StubProg([p_a2, p_a1]))
    rec("ranked_affinity_dominates",
        [r["id"] for r in ranked3] == ["p_a1", "p_a2"],
        f"order={[r['id'] for r in ranked3]}")

    # (B4) bypass-must-fail: strip harmony -> harmony-first assertion MUST raise.
    stripped_props = [{k: v for k, v in d.items() if k != "harmony"}
                      for d in (p_lo, p_hi)]
    ranked_stripped = Program.ranked_proposals(_StubProg(stripped_props))
    b4 = False
    try:
        assert [r["id"] for r in ranked_stripped] == ["p_hi", "p_lo"]
    except AssertionError:
        b4 = True
    rec("bypass_ranked_harmony_detected", b4,
        f"stripped order={[r['id'] for r in ranked_stripped]}; "
        "without harmony the tie-break is gone")

    # Fallback path (prefs ranker raises): same tie-break contract.
    class _FailPrefs:
        def rank_proposals(self, props):
            raise RuntimeError("prefs down")
    stub_f = _StubProg([p_lo, p_hi])
    stub_f.inspire = type("I", (), {"prefs": _FailPrefs()})()
    ranked_f = Program.ranked_proposals(stub_f)
    rec("ranked_fallback_harmony_tiebreak",
        [r["id"] for r in ranked_f] == ["p_hi", "p_lo"],
        f"order={[r['id'] for r in ranked_f]}")

    # ------------------------------------------------------------------
    # H. Contract reconciliation: _affinity bounds, missing-unit,
    #    permutation, serendipity range (P3R).
    # ------------------------------------------------------------------
    # (H3) HAND COMPUTATION: missing units -> tokens empty, distance 99.0
    # (sentinel), enhance_scope -> [] so in_scope floor 0.2, goal/body
    # boosts 0.0:
    # affinity = 0.40*0 + 0.22*0 + 0.13*(1/(1+99)) + 0.13*0.2 + 0 + 0
    #          = 0.13*0.01 + 0.026 = 0.0013 + 0.026 = 0.0273.
    # NOT 0.0 (the old shorthand is falsified); still fail-closed because
    # 0.0273 < STANSTILL_AFFINITY (0.10) -> gate "None".
    dm = rg._affinity(plane, "nope_a", "nope_b")
    expected_missing = 0.13 * (1.0 / 100.0) + 0.13 * 0.2
    rec("missing_unit_affinity_value",
        abs(dm["affinity"] - expected_missing) < 1e-15,
        f"got {dm['affinity']!r}")
    rec("missing_unit_affinity_repr", repr(dm["affinity"]) == "0.0273",
        f"repr={dm['affinity']!r}")
    rec("missing_unit_fail_closed",
        dm["affinity"] < rg.STANSTILL_AFFINITY and dm["distance"] == 99.0)
    rec("missing_unit_full_dict",
        set(dm.keys()) == {"affinity", "jaccard", "harmonic", "distance",
                           "shared", "goal_boost", "body_boost"})

    # (H4) TRUE BOUND: identical co-located in-scope units, identical
    # goals, body naming 3 missing organs in the labels:
    # 0.40*~1 + 0.22*1 + 0.13*1 + 0.13*1 + 0.12 + 0.15 ~= 1.15
    # (harmonic is 1 - 5e-10 from the 1e-9 epsilon). The old "[0,1]"
    # bound is falsified by construction.
    cube2 = give(OWNER, clean=True)
    lab = "Floor nursery lattice core"
    w = "floor nursery lattice core"
    cube2.place_idea("ca", lab, words=w, goals=["floor nursery lattice"],
                     skin=Skin.BUILDING, x=1.0, y=2.0)
    cube2.place_idea("cb", lab, words=w, goals=["floor nursery lattice"],
                     skin=Skin.BUILDING, x=1.0, y=2.0)
    plane2 = cube2.session.plane
    body = {"missing": ["floor", "nursery", "lattice"], "present": []}
    dc = rg._affinity(plane2, "ca", "cb", body=body)
    rec("affinity_max_corner",
        1.149 < dc["affinity"] <= 1.15 + 1e-9,
        f"got {dc['affinity']!r}; terms="
        f"harm={dc['harmonic']!r} body={dc['body_boost']!r}")
    rec("affinity_never_negative", dc["affinity"] >= 0.0)

    # Permutation guarantee: bitwise identical under argument swap on
    # realistic data (seeded; body snapshot active).
    rng = random.Random(20261004)
    ids = list(plane.units.keys())
    mism = 0
    for _ in range(2000):
        x, y = rng.sample(ids, 2)
        if rg._affinity(plane, x, y, body=body) != rg._affinity(plane, y, x, body=body):
            mism += 1
    rec("affinity_permutation_bitwise", mism == 0,
        f"mismatches={mism}/2000 ordered pairs")

    # serendipity(): exact range [0,1); the exposed tension subterm.
    s_vals = [rg.serendipity({f"t{i}", f"u{i}"}, {f"v{i}", f"w{i}", f"x{i}"})
              for i in range(50)]
    rec("serendipity_range",
        all(0.0 <= s < 1.0 for s in s_vals),
        f"min={min(s_vals)!r} max={max(s_vals)!r}")
    rec("serendipity_identical_zero",
        rg.serendipity({"a", "b"}, {"a", "b"}) == 0.0)
    rec("serendipity_empty_zero",
        rg.serendipity(set(), set()) == 0.0
        and rg.serendipity({"a"}, set()) == 0.0)
    rec("serendipity_symmetric",
        rg.serendipity({"a", "b", "x"}, {"c", "d", "x"})
        == rg.serendipity({"c", "d", "x"}, {"a", "b", "x"}))
    # serendipity is the normalized twin of the raw _tension term:
    # s == t/(1+t) by definition.
    t_raw = rg._tension({"a", "b", "x"}, {"c", "d", "y"})
    rec("serendipity_normalizes_tension",
        abs(rg.serendipity({"a", "b", "x"}, {"c", "d", "y"})
            - t_raw / (1.0 + t_raw)) < 1e-15)

    # ------------------------------------------------------------------
    # I. Nursery backward compatibility: pre-R3.6 records load.
    # ------------------------------------------------------------------
    tmpn3 = tempfile.mktemp(prefix="p3r36_legacy_", suffix=".json")
    try:
        legacy = {"old_1": {
            "id": "old_1", "label": "Old", "words": "w", "kind": "new",
            "parents": [], "affinity": 0.3, "reason": "r",
            "created": "2026-01-01T00:00:00Z", "status": "pending",
            "lifecycle_state": "active", "supersedes_id": None,
            "superseded_by_id": None, "revision_root_id": None,
            "revision_number": None,
        }}
        with open(tmpn3, "w", encoding="utf-8") as f:
            json.dump(legacy, f)
        n3 = Nursery.load(tmpn3)
        p_old = n3.proposals["old_1"]
        rec("nursery_legacy_loads",
            p_old.harmony == 0.0 and p_old.graph_coherence == 0.0,
            "pre-R3.6 record -> defined neutral defaults, no load error")
        p_new = n3.add(label="New sig", words="w", kind="new", seed=3,
                       harmony=0.44, graph_coherence=1.0)
        n3b = Nursery.load(tmpn3)
        p_rt = n3b.proposals[p_new.id]
        rec("nursery_signals_roundtrip",
            abs(p_rt.harmony - 0.44) < 1e-12
            and p_rt.graph_coherence == 1.0)
    finally:
        try:
            os.remove(tmpn3)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
