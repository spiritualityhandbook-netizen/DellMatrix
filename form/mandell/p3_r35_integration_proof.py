"""P3 R3.5: resonance/harmony integration proof.

NON-VACUOUS (P3R rewrite, 2026-10-04). Covers the Stream D acceptance
objectives against the merged W1+W2 implementation:

- 3.5.1: selection->growth handoff contract. What crosses the
  selection->growth boundary (core_i_ops grow_using_knowledge_about ->
  Program.grow_ideas -> RingedGrowth.run) is IDs ONLY; growth recomputes
  affinity independently. NEW (W1): growth->Nursery now persists
  harmony + graph_coherence per proposal pair, and
  Program.ranked_proposals CONSUMES them as tie-breakers. The proof
  includes a consumer bypass-must-fail: with ranked_proposals patched
  to affinity-only, tied-affinity proposals MUST order differently
  (else the signals are decorative).
- 3.5.2: faded-state exclusion. Ideas with lifecycle_state=FADED are
  excluded from _affinity (0.0, pair skipped), from pulse (no send, no
  receive, no score entries — including RETAINED scores from before the
  fade, W2), and from harmony_score (exclude_faded wired, no skip
  guard anymore). All-faded input yields empty/zero results, never an
  exception.
- 3.5.3: resonance/affinity effects observable via Outcome/observation.
  Live witness: observe_seed_execution over the grow_using_knowledge_about
  seed records an Outcome V1 with the consumed knowledge provenance,
  and the new proposals carry the consumer-computed affinity/parents/
  reason. Documented limitation: the Outcome record itself does not
  carry per-pair affinity values or gate decisions (those live on the
  nursery proposals and last_nurture, which are not frozen into the
  outcome).
- 3.5.4: public-path witness through the honest existing front door
  (observe_seed_execution over execute_seed, the same front door the
  REPL dispatches Mandell seeds through).
- 3.5.5: Phase-2 graph integration (IMPLEMENTED via W1; the old DEFER
  is superseded). A REAL SemanticGraph with REAL edges is attached to
  a REAL RingedGrowth.run: edged pairs persist graph_coherence 1.0,
  unedged pairs 0.0, graph=None degrades to the defined neutral, and
  the graph is never mutated (read-only). Bypass-must-fail: with the
  graph query patched to [], persisted coherence MUST drop to 0.0.
- Mutation test: disabling the faded filter via monkeypatch makes
  faded ideas leak back into _affinity and pulse, proving the filter
  is what excludes them.
- Fresh-process subprocess phase (cross-process realism).

Portable: derives REPO from __file__. smoke() -> bool, honest exit
status (0 only if ALL non-skipped checks pass). Registered in
form.regress under a P3 R3.5 block.

Test realism (honest labels):
  INTEGRATION   — same OS process, isolated owner (unique OWNER per
                  phase; state dirs verified absent before and removed
                  after).
  CROSS_PROCESS — fresh interpreter subprocess, no shared state.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)

from form.persist import _STATE_DIR, _safe_owner  # noqa: E402

OWNER_BASE = "R35P3"

_results: dict = {}
_skips: list = []


def rec(name: str, ok: bool, detail: str = "") -> None:
    _results[name] = bool(ok)
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" | {detail}" if detail else ""), flush=True)


def skip(name: str, reason: str) -> None:
    _skips.append((name, reason))
    print(f"  [SKIP] {name} | {reason}", flush=True)


def _owner(tag: str) -> str:
    return f"{OWNER_BASE}_{tag}"


def _clean(owner: str) -> None:
    d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}")
    f = os.path.join(_STATE_DIR, f"nursery_{owner}.json")
    import shutil as _sh
    _sh.rmtree(d, ignore_errors=True)
    try:
        os.remove(f)
    except OSError:
        pass
    # Phase-2 graph state for this owner (3.5.5).
    from form.mandell.semantic_graph import graph_path, graph_journal_path
    for p in (graph_path(owner), graph_journal_path(owner)):
        try:
            os.remove(p)
        except OSError:
            pass


def _assert_clean(owner: str) -> bool:
    d = os.path.join(_STATE_DIR, f"ideas_{_safe_owner(owner)}")
    f = os.path.join(_STATE_DIR, f"nursery_{owner}.json")
    return (not os.path.exists(d)) and (not os.path.exists(f))


def _fixture_program(owner: str):
    """Two confirmed, token-overlapping ideas (INTEGRATION realism)."""
    from form.open import open_program
    p = open_program(owner)
    a = p.nursery.add("river flow water current")
    b = p.nursery.add("river bank water shore")
    p.confirm_proposal(a.id)
    p.confirm_proposal(b.id)
    return p, a.id, b.id


# ---------------------------------------------------------------------------
# 3.5.1 handoff contract + growth->nursery->ranking consumption
# ---------------------------------------------------------------------------

def t351_handoff() -> None:
    """IDs-only selection->growth handoff; growth recomputes and persists."""
    from form.mandell.executor import execute_seed
    owner = _owner("H1")
    _clean(owner)
    rec("handoff::clean_start", _assert_clean(owner), "isolated owner state")
    try:
        p, aid, bid = _fixture_program(owner)
        out = execute_seed(p, "37[Nurture] :: grow_using_knowledge_about river water")
        rec("handoff::exec_ok", bool(out.get("ok")), "real grow_using_knowledge_about path")
        ln = p.last_nurture or {}
        routable = ln.get("routable_selected_ids") or []
        consumer_scope = ln.get("consumer_scope_ids")
        rec("handoff::ids_only",
            isinstance(consumer_scope, list) and sorted(consumer_scope) == sorted(routable)
            and all(isinstance(i, str) for i in consumer_scope),
            f"consumer_scope_ids == routable_ids = {sorted(routable)}")
        new_props = [pr for pid, pr in p.nursery.proposals.items()
                     if pid not in (aid, bid)]
        rec("handoff::offspring_exists", len(new_props) >= 1,
            f"{len(new_props)} new proposal(s)")
        gate_re = re.compile(r"^(Solstice|Equinox|Standstill) harm=")
        ok_reasons = all(gate_re.match(pr.reason or "") for pr in new_props)
        rec("handoff::consumer_computed_affinity", ok_reasons,
            "; ".join((pr.reason or "")[:56] for pr in new_props))
        # Selection scores have no field on the proposal and no consumer
        # in the growth modules.
        no_score_field = all(not hasattr(pr, "score") for pr in new_props)
        rec("handoff::no_score_field", no_score_field,
            "Proposal has no selection-score attribute")
        import inspect
        from form.dell_matrix import ringed_growth, nursery
        src = inspect.getsource(ringed_growth) + inspect.getsource(nursery)
        score_reads = [ln2 for ln2 in src.splitlines()
                       if '["score"]' in ln2 or "['score']" in ln2
                       or ".score" in ln2 or "selection_score" in ln2]
        rec("handoff::no_score_consumer", len(score_reads) == 0,
            "no score key/attribute read in ringed_growth.py or nursery.py")
        # NEW (W1, 3.5.1/3.5.5): growth persists harmony + graph_coherence
        # per proposal pair; both in [0,1].
        sig_ok = all(isinstance(pr.harmony, float)
                     and 0.0 <= pr.harmony <= 1.0
                     and isinstance(pr.graph_coherence, float)
                     and 0.0 <= pr.graph_coherence <= 1.0
                     for pr in new_props)
        rec("handoff::signals_persisted", sig_ok,
            "; ".join(f"h={pr.harmony:.3f} g={pr.graph_coherence:.3f}"
                       for pr in new_props))
        rec("handoff::signals_in_reason",
            all("hs=" in (pr.reason or "") and "gcoh=" in (pr.reason or "")
                for pr in new_props))
    finally:
        _clean(owner)


def t351_consumer_bypass() -> None:
    """BYPASS-MUST-FAIL (graph/harmony consumption): Program.ranked_proposals
    consumes harmony/graph_coherence as tie-breakers. With the consumer
    patched to affinity-only, tied-affinity proposals MUST order
    differently. If the orders are identical, the signals are decorative
    and the proof FAILS."""
    from form.open import Program
    owner = _owner("CB")
    _clean(owner)
    try:
        p = Program(owner=owner)
        # Tied affinity, different harmony: inserted lo-first so the
        # bypassed (stable, affinity-only) order differs from the real one.
        p.nursery.add(label="lo harmony", words="w", kind="new",
                      affinity=0.5, seed=1, harmony=0.1, graph_coherence=0.0)
        p.nursery.add(label="hi harmony", words="w", kind="new",
                      affinity=0.5, seed=2, harmony=0.9, graph_coherence=0.0)
        real = [d["id"] for d in p.ranked_proposals()]
        rec("consume::real_harmony_first",
            real[0].startswith("hi_harmony"),
            f"order={[i[:18] for i in real]}")
        orig = Program.ranked_proposals
        Program.ranked_proposals = (  # BYPASS: consumer ignores the signals
            lambda self: sorted(self.list_proposals(),
                                key=lambda d: -float(d.get("affinity", 0) or 0)))
        try:
            bypassed = [d["id"] for d in p.ranked_proposals()]
        finally:
            Program.ranked_proposals = orig
        rec("consume::bypass_differs", bypassed != real,
            f"bypassed={[i[:18] for i in bypassed]} (must differ)")
        rec("consume::restored",
            [d["id"] for d in p.ranked_proposals()] == real)
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 3.5.2 faded exclusion
# ---------------------------------------------------------------------------

def t352_policy_unit() -> None:
    """is_faded / exclude_faded unit semantics."""
    from form.dell_matrix.faded_policy import is_faded, exclude_faded
    from form.dell_matrix.nursery import Proposal
    from form.mandell.idea import LifecycleState

    class O:  # simple carrier
        def __init__(self, **kw): self.__dict__.update(kw)

    rec("faded::enum", is_faded(O(lifecycle_state=LifecycleState.FADED)) is True)
    rec("faded::string", is_faded(O(lifecycle_state="faded")) is True)
    rec("faded::string_noisy", is_faded(O(lifecycle_state=" FADED ")) is True)
    rec("faded::active_str", is_faded(O(lifecycle_state="active")) is False)
    rec("faded::active_enum", is_faded(O(lifecycle_state=LifecycleState.ACTIVE)) is False)
    rec("faded::idea_state", is_faded(O(idea_state=LifecycleState.FADED)) is True)
    rec("faded::no_attr", is_faded(O()) is False)
    rec("faded::none", is_faded(None) is False)
    rec("faded::nursery_proposal",
        is_faded(Proposal(id="x", label="x", words="", kind="new",
                          lifecycle_state="faded")) is True)
    a, f, b = O(tag="a"), O(lifecycle_state="faded", tag="f"), O(tag="b")
    rec("faded::exclude_order", [o.tag for o in exclude_faded([a, f, b])] == ["a", "b"])
    rec("faded::exclude_all", exclude_faded([f]) == [])
    rec("faded::exclude_empty", exclude_faded([]) == [])


def t352_affinity() -> None:
    """_affinity: faded pair -> 0.0, no exception; active pairs unaffected."""
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.ringed_growth import _affinity
    from form.dell_matrix.nursery import Proposal
    from types import SimpleNamespace

    cube = give("R35FA", clean=True)
    cube.place_idea("a", "river flow water current", skin=Skin.SEED, x=0.0)
    cube.place_idea("b", "river bank water shore", skin=Skin.SEED, x=1.0)
    cube.place_idea("f", "river faded old silt", skin=Skin.SEED, x=2.0)
    plane = cube.session.plane
    # Canonical: f is FADED via nursery proposal (not dynamic attributes).
    prog = SimpleNamespace(nursery=SimpleNamespace(proposals={
        "a": Proposal(id="a", label="a", words="river flow water current",
                      kind="new", lifecycle_state="active"),
        "b": Proposal(id="b", label="b", words="river bank water shore",
                      kind="new", lifecycle_state="active"),
        "f": Proposal(id="f", label="f", words="river faded old silt",
                      kind="new", lifecycle_state="faded"),
    }))

    base = _affinity(plane, "a", "b", program=prog)
    rec("affinity::active_pair_live", base["affinity"] > 0.0,
        f"affinity={base['affinity']:.4f}")
    z1 = _affinity(plane, "a", "f", program=prog)
    z2 = _affinity(plane, "f", "a", program=prog)
    expected_keys = {"affinity", "jaccard", "harmonic", "distance",
                     "shared", "goal_boost", "body_boost"}
    rec("affinity::faded_zero_shape",
        set(z1) == expected_keys and set(z2) == expected_keys
        and z1["affinity"] == 0.0 and z2["affinity"] == 0.0
        and all(v == 0.0 for v in z1.values()),
        "same dict shape, all zeroed")
    prog.nursery.proposals["a"].lifecycle_state = "faded"
    z3 = _affinity(plane, "a", "f", program=prog)  # all-faded pair
    rec("affinity::all_faded", z3["affinity"] == 0.0, "no exception")


def t352_pulse() -> None:
    """pulse: faded units neither send nor receive; retained state dropped.

    Uses the canonical lifecycle boundary: (program, unit_id) resolved
    via inspect_revision, not dynamic Unit attributes.
    """
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.resonance import pulse, ResonanceState
    from form.dell_matrix.nursery import Proposal
    from types import SimpleNamespace

    cube = give("R35FP", clean=True)
    cube.place_idea("a", "river flow", skin=Skin.SEED, x=0.0)
    cube.place_idea("b", "river bank", skin=Skin.SEED, x=1.0)
    cube.place_idea("f", "river faded silt", skin=Skin.SEED, x=2.0)
    plane = cube.session.plane
    # Canonical: f is FADED via nursery proposal.
    prog = SimpleNamespace(nursery=SimpleNamespace(proposals={
        "a": Proposal(id="a", label="a", words="river flow",
                      kind="new", lifecycle_state="active"),
        "b": Proposal(id="b", label="b", words="river bank",
                      kind="new", lifecycle_state="active"),
        "f": Proposal(id="f", label="f", words="river faded silt",
                      kind="new", lifecycle_state="faded"),
    }))

    st = pulse(plane, ResonanceState(), program=prog)
    rec("pulse::faded_no_scores", "f" not in st.scores and "f" not in st.tags,
        "faded unit has no score/tag entries")
    rec("pulse::active_scored", st.scores.get("a", 0.0) > 0 and st.scores.get("b", 0.0) > 0)
    # W2: a unit that FADES AFTER an active pulse must lose its retained
    # scores/tags on the next pulse (zero effective influence going
    # forward); the log is preserved (history, not influence).
    log_len = len(st.log)
    prog.nursery.proposals["b"].lifecycle_state = "faded"
    st2 = pulse(plane, st, program=prog)  # reuse: b had retained scores
    rec("pulse::retained_dropped",
        "b" not in st2.scores and "b" not in st2.tags,
        "faded unit's retained scores/tags dropped")
    rec("pulse::log_preserved", len(st2.log) >= log_len,
        "history preserved, exclusion logged")
    # All-faded plane: empty result, never an exception.
    for pid in prog.nursery.proposals:
        prog.nursery.proposals[pid].lifecycle_state = "faded"
    st3 = pulse(plane, ResonanceState(), program=prog)
    rec("pulse::all_faded_empty",
        st3.scores == {} and st3.tags == {},
        "empty scores/tags, no exception")


def t352_harmony() -> None:
    """harmony_score: exclude_faded wired (no skip guard anymore)."""
    from form.dell_matrix.harmony import harmony_score
    from form.mandell.idea import Idea, LifecycleState

    a = Idea(title="river water flow")
    b = Idea(title="stream water flow")
    f = Idea(title="river water flow")
    f._idea_state = LifecycleState.FADED
    solo_pair = harmony_score([a, b])
    rec("harmony::faded_excluded",
        harmony_score([a, b, f]) == solo_pair,
        f"faded dup changes nothing ({solo_pair:.4f})")
    f2 = Idea(title="stream water flow")
    f2._idea_state = LifecycleState.FADED
    rec("harmony::all_faded_zero",
        harmony_score([f]) == 0.0 and harmony_score([f, f2]) == 0.0,
        "all-faded -> 0.0")


# ---------------------------------------------------------------------------
# 3.5.3 observation of resonance effects
# ---------------------------------------------------------------------------

def t353_observation() -> None:
    """Live witness: resonance effects observable via Outcome/observation."""
    from form.mandell.execution_observer import observe_seed_execution
    owner = _owner("O3")
    _clean(owner)
    try:
        p, aid, bid = _fixture_program(owner)
        out = observe_seed_execution(
            p, "37[Nurture] :: grow_using_knowledge_about river water")
        rec("observe::exec_ok", bool(out.get("ok")))
        ore = getattr(p, "last_outcome", None)
        rec("observe::outcome_recorded", isinstance(ore, dict),
            "Outcome V1 captured by the EOC-I adapter")
        if isinstance(ore, dict):
            kids = [k["id"] for k in (ore.get("knowledge") or [])]
            rec("observe::knowledge_provenance",
                aid in kids and bid in kids,
                f"consumed knowledge in outcome: {kids}")
            msgs = ore.get("messages") or []
            rec("observe::messages_carry_effect",
                any("New proposals:" in m for m in msgs),
                "outcome messages report the growth effect")
            rec("observe::routable_echo",
                sorted(ore.get("routable_ids") or []) == sorted([aid, bid]))
        new_props = [pr for pid, pr in p.nursery.proposals.items()
                     if pid not in (aid, bid)]
        ok_aff = all(pr.affinity > 0 and pr.parents and pr.reason for pr in new_props)
        rec("observe::affinity_on_proposals", ok_aff and len(new_props) >= 1,
            "; ".join(f"{pr.id[:20]} aff={pr.affinity:.3f} {pr.reason[:40]}"
                       for pr in new_props))
        # Documented limitation (not a failure): the Outcome record does
        # not carry per-pair affinity values or gate decisions; those live
        # on nursery proposals and last_nurture, which are not frozen into
        # the outcome. No new Outcome subsystem is built (out of scope).
        has_pair_aff = any("affinity" in str(k) for k in (ore.get("knowledge") or []))
        print("    limitation: outcome carries knowledge provenance + effect "
              "summary, not per-pair affinity values "
              f"(pair affinity in outcome knowledge: {has_pair_aff})", flush=True)
        rec("observe::limitation_documented", True)
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 3.5.4 public path
# ---------------------------------------------------------------------------

def t354_public_path() -> None:
    """Public-path witness: the Mandell seed front door (REPL dispatches here)."""
    from form.mandell.execution_observer import observe_seed_execution
    owner = _owner("P4")
    _clean(owner)
    try:
        p, aid, bid = _fixture_program(owner)
        out = observe_seed_execution(
            p, "37[Nurture] :: grow_using_knowledge_about river water")
        rec("public::seed_front_door_ok", bool(out.get("ok")),
            "execute_seed front door == the path REPL dispatches Mandell through")
        rec("public::outcome_observed", getattr(p, "last_outcome", None) is not None)
        rec("public::nurture_receipt", (p.last_nurture or {}).get("action") == "grow_contextual")
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# 3.5.5 graph integration (IMPLEMENTED via W1; old DEFER superseded)
# ---------------------------------------------------------------------------

def t355_graph_integration() -> None:
    """Real Phase-2 graph attached to real growth: read-only consumption."""
    from form.mandell.idea import Idea, Provenance, ProvenanceSource
    from form.mandell.idea_persist import save_idea
    from form.mandell.semantic_graph import (
        RelationshipType, SemanticGraph, graph_path, graph_journal_path)
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    from form.dell_matrix import ringed_growth as rg
    from form.dell_matrix.nursery import Nursery

    owner = _owner("G5")
    _clean(owner)
    try:
        # Real Ideas + real edges via the graph's own write path.
        # Unit IDs ARE the canonical Idea IDs.
        A, B, C = "r35g_a", "r35g_b", "r35g_c"
        for iid, title in ((A, "Alpha routes"), (B, "Beta routes"),
                           (C, "Gamma melody")):
            save_idea(Idea(idea_id=iid, title=title), owner)
        prov = Provenance(source=ProvenanceSource.SYSTEM,
                          activity="p3r35", agent="p3r35")
        graph = SemanticGraph.load(owner)
        graph.add_relationship(RelationshipType.RELATED_TO, A, B, prov, cause="p3r35")
        graph = SemanticGraph.load(owner)  # reload: edges survived the log
        n_edges_before = len(graph.by_type(RelationshipType.RELATED_TO))
        rec("graph::edges_real", n_edges_before == 1)

        cube = give(owner, clean=True)
        cube.place_idea(A, "Alpha routes", words="crm routes delivery",
                        skin=Skin.BUILDING, x=1.0, y=0.0)
        cube.place_idea(B, "Beta routes", words="crm routes pickup",
                        skin=Skin.BUILDING, x=-1.0, y=0.0)
        cube.place_idea(C, "Gamma melody", words="song harmony rhythm",
                        skin=Skin.BUILDING, x=0.0, y=3.0)
        plane = cube.session.plane

        tmp = tempfile.mktemp(prefix="p3r35_g_", suffix=".json")
        try:
            nurs = Nursery(path=tmp)
            out = rg.RingedGrowth(nursery=nurs, seed=11).run(
                plane, cycles=1, graph=graph)
            rec("graph::signal_attached", out.get("graph_signal") == "attached")
            ab = [p for p in nurs.proposals.values() if set(p.parents) == {A, B}]
            rec("graph::ab_proposed", len(ab) >= 1)
            rec("graph::edged_pair_coherence",
                all(p.graph_coherence == 1.0 for p in ab),
                "a-b edged -> 1.0")
            # Unedged pair proposals (if any) read the defined neutral 0.0.
            others = [p for p in nurs.proposals.values()
                      if p.parents and set(p.parents) != {A, B}]
            rec("graph::unedged_neutral",
                all(p.graph_coherence == 0.0 for p in others),
                f"{len(others)} other pair proposal(s)")
            # Read-only: growth never mutates the graph.
            n_edges_after = len(
                SemanticGraph.load(owner).by_type(RelationshipType.RELATED_TO))
            rec("graph::read_only", n_edges_after == n_edges_before,
                "edge count unchanged by growth")

            # BYPASS-MUST-FAIL: with the graph query patched to [], the
            # persisted coherence MUST drop to 0.0. If proposals still
            # carry 1.0, the value is not tracking real graph structure.
            real_q = graph.association_neighbors
            graph.association_neighbors = lambda iid: []  # BYPASS
            try:
                tmp2 = tempfile.mktemp(prefix="p3r35_g2_", suffix=".json")
                try:
                    nurs2 = Nursery(path=tmp2)
                    rg.RingedGrowth(nursery=nurs2, seed=11).run(
                        plane, cycles=1, graph=graph)
                    ab2 = [p for p in nurs2.proposals.values()
                           if set(p.parents) == {A, B}]
                    rec("graph::bypass_drops",
                        len(ab2) >= 1
                        and all(p.graph_coherence == 0.0 for p in ab2),
                        "query bypassed -> coherence 0.0 (was 1.0)")
                finally:
                    try:
                        os.remove(tmp2)
                    except OSError:
                        pass
            finally:
                graph.association_neighbors = real_q

            # graph=None degrades to the defined neutral (backward compatible).
            tmp3 = tempfile.mktemp(prefix="p3r35_g3_", suffix=".json")
            try:
                nurs3 = Nursery(path=tmp3)
                out3 = rg.RingedGrowth(nursery=nurs3, seed=11).run(
                    plane, cycles=1, graph=None)
                rec("graph::none_neutral",
                    all(p.graph_coherence == 0.0
                        for p in nurs3.proposals.values())
                    and out3.get("graph_signal") == "none")
            finally:
                try:
                    os.remove(tmp3)
                except OSError:
                    pass
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
    finally:
        _clean(owner)


# ---------------------------------------------------------------------------
# Mutation test: the faded filter is what excludes
# ---------------------------------------------------------------------------

def t_mutation() -> None:
    """Disable the canonical faded filter -> faded ideas leak back in
    (filter is causal). Uses the canonical lifecycle boundary."""
    from form.dell_matrix import canonical_lifecycle
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.ringed_growth import _affinity
    from form.dell_matrix.resonance import pulse, ResonanceState
    from form.dell_matrix.nursery import Proposal
    from types import SimpleNamespace

    cube = give("R35MU", clean=True)
    cube.place_idea("a", "river flow water current", skin=Skin.SEED, x=0.0)
    cube.place_idea("f", "river faded old silt", skin=Skin.SEED, x=1.0)
    plane = cube.session.plane
    # Canonical: f is FADED via nursery proposal.
    prog = SimpleNamespace(nursery=SimpleNamespace(proposals={
        "a": Proposal(id="a", label="a", words="river flow water current",
                      kind="new", lifecycle_state="active"),
        "f": Proposal(id="f", label="f", words="river faded old silt",
                      kind="new", lifecycle_state="faded"),
    }))

    orig = canonical_lifecycle.is_active
    try:
        canonical_lifecycle.is_active = lambda p, uid: True  # disable filter
        leaked_aff = _affinity(plane, "a", "f", program=prog)["affinity"]
        rec("mutation::affinity_leaks", leaked_aff > 0.0,
            f"filter disabled -> affinity={leaked_aff:.4f} (was 0.0)")
        st = pulse(plane, ResonanceState(), program=prog)
        rec("mutation::pulse_leaks", st.scores.get("f", 0.0) > 0.0,
            f"filter disabled -> faded score={st.scores.get('f', 0.0):.4f}")
    finally:
        canonical_lifecycle.is_active = orig  # restore
    rec("mutation::restored_excludes",
        _affinity(plane, "a", "f", program=prog)["affinity"] == 0.0
        and "f" not in pulse(plane, ResonanceState(), program=prog).scores,
        "filter restored -> exclusion holds again")


# ---------------------------------------------------------------------------
# Fresh-process subprocess phase
# ---------------------------------------------------------------------------

_CHILD = """
import json, sys
sys.path.insert(0, %(REPO)r)
r = {}
from form.mandell.idea import LifecycleState
from form.dell_matrix.faded_policy import is_faded, exclude_faded
from form.dell_matrix.blank_cube import give
from form.dell_matrix.plane import Skin
from form.dell_matrix.ringed_growth import _affinity
from form.dell_matrix.resonance import pulse, ResonanceState

class O:
    def __init__(self, **kw): self.__dict__.update(kw)

r["policy_enum"] = is_faded(O(lifecycle_state=LifecycleState.FADED)) is True
r["policy_str"] = is_faded(O(lifecycle_state="faded")) is True
r["policy_neg"] = is_faded(O()) is False

from form.dell_matrix.nursery import Proposal
from types import SimpleNamespace
cube = give("R35CH", clean=True)
cube.place_idea("a", "river flow water", skin=Skin.SEED, x=0.0)
cube.place_idea("b", "river bank shore", skin=Skin.SEED, x=1.0)
cube.place_idea("f", "river faded silt", skin=Skin.SEED, x=2.0)
plane = cube.session.plane
# Canonical: f is FADED via nursery proposal.
prog = SimpleNamespace(nursery=SimpleNamespace(proposals={
    "a": Proposal(id="a", label="a", words="river flow water",
                  kind="new", lifecycle_state="active"),
    "b": Proposal(id="b", label="b", words="river bank shore",
                  kind="new", lifecycle_state="active"),
    "f": Proposal(id="f", label="f", words="river faded silt",
                  kind="new", lifecycle_state="faded"),
}))
r["affinity_zero"] = (_affinity(plane, "a", "f", program=prog)["affinity"] == 0.0)
st = pulse(plane, ResonanceState(), program=prog)
r["pulse_excludes"] = ("f" not in st.scores and st.scores.get("a", 0.0) > 0
                       and st.scores.get("b", 0.0) > 0)
# All-faded: empty, no exception.
for pid in prog.nursery.proposals:
    prog.nursery.proposals[pid].lifecycle_state = "faded"
st2 = pulse(plane, ResonanceState(), program=prog)
r["all_faded_empty"] = (st2.scores == {} and st2.tags == {})
print("RESULT " + json.dumps(r))
"""


def t_cross_process() -> None:
    """CROSS_PROCESS: faded exclusion holds in a fresh interpreter."""
    code = _CHILD % {"REPO": REPO}
    pr = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                        capture_output=True, text=True, timeout=120)
    ok = pr.returncode == 0
    rec("xproc::no_crash", ok, f"returncode={pr.returncode}"
        + (f" stderr={pr.stderr[-200:]}" if not ok else ""))
    found = {}
    if ok:
        for line in pr.stdout.splitlines():
            if line.startswith("RESULT "):
                try:
                    found = json.loads(line[len("RESULT "):])
                except json.JSONDecodeError:
                    pass
    rec("xproc::evidence", bool(found), "child emitted RESULT JSON")
    for k, v in found.items():
        rec(f"xproc::{k}", bool(v))


def smoke() -> bool:
    """Run all R3.5 phases. Returns True iff every non-skipped check passes."""
    print("=== P3 R3.5 INTEGRATION PROOF (non-vacuous) ===", flush=True)
    _results.clear()
    _skips.clear()
    print("-- 3.5.1 handoff contract (INTEGRATION) --", flush=True)
    t351_handoff()
    print("-- 3.5.1 consumer bypass-must-fail (INTEGRATION) --", flush=True)
    t351_consumer_bypass()
    print("-- 3.5.2 faded policy units (INTEGRATION) --", flush=True)
    t352_policy_unit()
    print("-- 3.5.2 _affinity exclusion (INTEGRATION) --", flush=True)
    t352_affinity()
    print("-- 3.5.2 pulse exclusion (INTEGRATION) --", flush=True)
    t352_pulse()
    print("-- 3.5.2 harmony exclusion (INTEGRATION) --", flush=True)
    t352_harmony()
    print("-- 3.5.3 observation witness (INTEGRATION) --", flush=True)
    t353_observation()
    print("-- 3.5.4 public path (INTEGRATION) --", flush=True)
    t354_public_path()
    print("-- 3.5.5 graph integration (INTEGRATION) --", flush=True)
    t355_graph_integration()
    print("-- mutation test (INTEGRATION) --", flush=True)
    t_mutation()
    print("-- fresh-process phase (CROSS_PROCESS) --", flush=True)
    t_cross_process()

    fails = [k for k, v in _results.items() if not v]
    npass = sum(1 for v in _results.values() if v)
    ntotal = len(_results)
    print(f"P3 R3.5: {npass}/{ntotal} PASS, {len(_skips)} SKIP", flush=True)
    for name, reason in _skips:
        print(f"  skipped: {name} — {reason}", flush=True)
    if fails:
        print(f"FAILURES: {fails}", flush=True)
        return False
    if ntotal == 0:
        print("FAIL: empty evidence", flush=True)
        return False
    print("P3 R3.5 WORLD: ALL PASS", flush=True)
    return True


def main() -> None:
    """Entry point with honest exit status."""
    ok = smoke()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
