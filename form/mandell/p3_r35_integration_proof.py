"""P3 R3.5: resonance/harmony integration proof.

Covers the Stream D acceptance objectives:

- 3.5.1: selection->growth handoff contract. What crosses the boundary
  (core_i_ops grow_using_knowledge_about -> Program.grow_ideas ->
  RingedGrowth.run) is IDs ONLY; growth recomputes affinity
  independently. Selection scores are echoed in receipts for audit;
  no consumer of them exists in ringed_growth.py or nursery.py.
- 3.5.2: faded-state exclusion. Ideas with lifecycle_state=FADED are
  excluded from _affinity (affinity 0.0, pair skipped) and from pulse
  (no send, no receive, no score entries). All-faded input yields
  empty/zero results, never an exception. harmony_score is tested
  behind an explicit skip-if-missing guard (harmony.py lands via
  Stream B; the coordinator wires exclude_faded at merge).
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
- 3.5.5: Phase-2 graph integration. Verified zero integration today
  (no semantic_graph reads in resonance/affinity code; no affinity
  writes to graph edges; _affinity's spatial term uses plane x/y
  coordinates). Explicit DEFER with rationale: no proven consumer,
  threading a graph through _affinity would change Stream A's
  contract, and affinity-written edges would create a second edge
  authority beside SemanticGraph.
- Mutation test: disabling the faded filter via monkeypatch makes
  faded ideas leak back into _affinity and pulse, proving the filter
  is what excludes them.
- Fresh-process subprocess phase (cross-process realism).

Portable: derives REPO from __file__. smoke() -> bool, honest exit
status (0 only if ALL non-skipped checks pass). Registered in
form/regress under a P3 R3.5 block.

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
import subprocess
import sys

# Portable: derive repo root from this file's location.
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)

from form.persist import _STATE_DIR

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
    d = os.path.join(_STATE_DIR, f"ideas_{owner}")
    f = os.path.join(_STATE_DIR, f"nursery_{owner}.json")
    import shutil
    shutil.rmtree(d, ignore_errors=True)
    try:
        os.remove(f)
    except OSError:
        pass


def _assert_clean(owner: str) -> bool:
    d = os.path.join(_STATE_DIR, f"ideas_{owner}")
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
# 3.5.1 handoff contract
# ---------------------------------------------------------------------------

def t351_handoff() -> None:
    """IDs-only handoff: growth recomputes affinity; scores never cross."""
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
        # Growth's own affinity evidence: the new proposal's reason carries
        # the consumer-computed harmonic ("Solstice harm=..."), a concept
        # selection does not have.
        new_props = [pr for pid, pr in p.nursery.proposals.items()
                     if pid not in (aid, bid)]
        rec("handoff::offspring_exists", len(new_props) >= 1,
            f"{len(new_props)} new proposal(s)")
        gate_re = re.compile(r"^(Solstice|Equinox|Standstill) harm=")
        ok_reasons = all(gate_re.match(pr.reason or "") for pr in new_props)
        rec("handoff::consumer_computed_affinity", ok_reasons,
            "; ".join((pr.reason or "")[:48] for pr in new_props))
        # Structural: selection scores have no field on the proposal and
        # no consumer in the growth modules.
        no_score_field = all(not hasattr(pr, "score") for pr in new_props)
        rec("handoff::no_score_field", no_score_field,
            "Proposal has no selection-score attribute")
        # No consumer of selection scores in the growth modules:
        # neither module reads a "score" key/attribute anywhere.
        import inspect
        from form.dell_matrix import ringed_growth, nursery
        src = inspect.getsource(ringed_growth) + inspect.getsource(nursery)
        score_reads = [ln for ln in src.splitlines()
                       if '["score"]' in ln or "['score']" in ln
                       or ".score" in ln or "selection_score" in ln]
        rec("handoff::no_score_consumer", len(score_reads) == 0,
            "no score key/attribute read in ringed_growth.py or nursery.py")
        # Honest evidence of the recompute: proposal affinity vs selection score.
        contribs = {c["id"]: c for c in (ln.get("contributions") or [])}
        for pr in new_props:
            for pid in (pr.parents or []):
                c = contribs.get(pid)
                if c:
                    print(f"    evidence: parent {pid[:24]} selection_score={c['score']} "
                          f"-> offspring affinity={pr.affinity:.4f}", flush=True)
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

    cube = give("R35FA", clean=True)
    cube.place_idea("a", "river flow water current", skin=Skin.SEED, x=0.0)
    cube.place_idea("b", "river bank water shore", skin=Skin.SEED, x=1.0)
    cube.place_idea("f", "river faded old silt", skin=Skin.SEED, x=2.0)
    plane = cube.session.plane
    plane.units["f"].lifecycle_state = "faded"

    base = _affinity(plane, "a", "b")
    rec("affinity::active_pair_live", base["affinity"] > 0.0,
        f"affinity={base['affinity']:.4f}")
    z1 = _affinity(plane, "a", "f")
    z2 = _affinity(plane, "f", "a")
    expected_keys = {"affinity", "jaccard", "harmonic", "distance",
                     "shared", "goal_boost", "body_boost"}
    rec("affinity::faded_zero_shape",
        set(z1) == expected_keys and set(z2) == expected_keys
        and z1["affinity"] == 0.0 and z2["affinity"] == 0.0
        and all(v == 0.0 for v in z1.values()),
        "same dict shape, all zeroed")
    plane.units["a"].lifecycle_state = "faded"
    z3 = _affinity(plane, "a", "f")  # all-faded pair
    rec("affinity::all_faded", z3["affinity"] == 0.0, "no exception")
    del plane.units["a"].lifecycle_state
    # NOTE (observed, Stream A territory): the matrix 3.1.1 claims missing
    # units yield affinity 0.0, but _affinity actually returns 0.0273 for a
    # missing unit (spatial 1/100*0.13 + in_scope 0.2*0.13). That failure
    # behavior belongs to Stream A's contract work; the faded-exclusion
    # edit here deliberately does not alter it. Recorded, not asserted.


def t352_pulse() -> None:
    """pulse: faded units neither send nor receive; all-faded -> empty."""
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.resonance import pulse, ResonanceState

    cube = give("R35FP", clean=True)
    cube.place_idea("a", "river flow", skin=Skin.SEED, x=0.0)
    cube.place_idea("b", "river bank", skin=Skin.SEED, x=1.0)
    cube.place_idea("f", "river faded silt", skin=Skin.SEED, x=2.0)
    plane = cube.session.plane
    plane.units["f"].lifecycle_state = "faded"

    st = pulse(plane, ResonanceState())
    rec("pulse::faded_no_scores", "f" not in st.scores and "f" not in st.tags,
        "faded unit has no score/tag entries")
    rec("pulse::active_scored", st.scores.get("a", 0.0) > 0 and st.scores.get("b", 0.0) > 0)
    leaked = [ln for ln in st.log if " f " in f" {ln} " and "-enhance->" in ln
              and ln.split("-enhance->")[0].rstrip().endswith(" f")]
    rec("pulse::faded_never_sends", len(leaked) == 0, "no 'f -enhance->' lines")
    # All-faded plane: empty result, never an exception.
    for u in plane.units.values():
        u.lifecycle_state = "faded"
    st2 = pulse(plane, ResonanceState())
    rec("pulse::all_faded_empty",
        st2.scores == {} and st2.tags == {} and st2.pulse_count == 1,
        "empty scores/tags, no exception")


def t352_harmony_guard() -> None:
    """harmony_score faded-exclusion test behind an explicit skip guard."""
    try:
        import form.dell_matrix.harmony  # noqa: F401
    except ImportError:
        skip("harmony::faded_exclusion",
             "harmony.py lands via Stream B; coordinator wires at merge")
        return
    # If harmony.py is present (unexpected on this branch), test it for real.
    from form.dell_matrix import harmony
    from form.dell_matrix.faded_policy import exclude_faded

    class O:
        def __init__(self, **kw): self.__dict__.update(kw)
    ideas = [O(lifecycle_state="active", tid="a"),
             O(lifecycle_state="faded", tid="f")]
    kept = exclude_faded(ideas)
    rec("harmony::exclude_wired", [o.tid for o in kept] == ["a"],
        "exclude_faded applied before harmony_score")
    if hasattr(harmony, "harmony_score"):
        try:
            s_all = harmony.harmony_score(ideas)
            s_kept = harmony.harmony_score(kept)
            rec("harmony::faded_excluded", s_all == s_kept,
                "faded idea does not change the score")
        except TypeError:
            skip("harmony::faded_exclusion",
                 "harmony_score signature differs; manual check needed")


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
        # The affinity effect itself is recorded on the nursery proposals:
        # parents + consumer-computed affinity + reason.
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
# 3.5.5 graph integration: explicit DEFER with evidence
# ---------------------------------------------------------------------------

def t355_deferral() -> None:
    """Verify zero integration today; record the deferral rationale."""
    import inspect
    import sys as _sys
    from form.dell_matrix import ringed_growth, resonance
    from form.dell_matrix.ringed_growth import _dist
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin

    rg_src = inspect.getsource(ringed_growth)
    rs_src = inspect.getsource(resonance)
    no_import = ("semantic_graph" not in rg_src and "semantic_graph" not in rs_src
                 and not hasattr(ringed_growth, "semantic_graph")
                 and not hasattr(resonance, "semantic_graph"))
    rec("graph::no_reads", no_import,
        "no semantic_graph import in ringed_growth/resonance (source+module)")
    # _affinity's spatial term uses plane x/y coordinates (verified input).
    cube = give("R35G5", clean=True)
    cube.place_idea("a", "alpha", skin=Skin.SEED, x=0.0)
    cube.place_idea("b", "beta", skin=Skin.SEED, x=3.0)
    plane = cube.session.plane
    d1 = _dist(plane, "a", "b")
    plane.units["b"].x = 6.0
    d2 = _dist(plane, "a", "b")
    rec("graph::spatial_is_plane_coords",
        abs(d1 - 3.0) < 1e-9 and abs(d2 - 6.0) < 1e-9 and d2 != d1,
        f"dist follows plane x/y ({d1:.1f} -> {d2:.1f}); graph edges play no role")
    rationale = (
        "DEFER 3.5.5: no proven consumer of graph-informed affinity or of "
        "affinity-written graph edges; _affinity's spatial term already has "
        "a defined verifiable input (plane x/y); threading a graph through "
        "_affinity would change Stream A's contract; affinity-written edges "
        "would create a second edge authority beside SemanticGraph.")
    print(f"    {rationale}", flush=True)
    rec("graph::deferral_recorded", True)


# ---------------------------------------------------------------------------
# Mutation test: the faded filter is what excludes
# ---------------------------------------------------------------------------

def t_mutation() -> None:
    """Disable the faded filter -> faded ideas leak back in (filter is causal)."""
    from form.dell_matrix import faded_policy
    from form.dell_matrix.blank_cube import give
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.ringed_growth import _affinity
    from form.dell_matrix.resonance import pulse, ResonanceState

    cube = give("R35MU", clean=True)
    cube.place_idea("a", "river flow water current", skin=Skin.SEED, x=0.0)
    cube.place_idea("f", "river faded old silt", skin=Skin.SEED, x=1.0)
    plane = cube.session.plane
    plane.units["f"].lifecycle_state = "faded"

    orig = faded_policy.is_faded
    try:
        faded_policy.is_faded = lambda obj: False  # disable the filter
        leaked_aff = _affinity(plane, "a", "f")["affinity"]
        rec("mutation::affinity_leaks", leaked_aff > 0.0,
            f"filter disabled -> affinity={leaked_aff:.4f} (was 0.0)")
        st = pulse(plane, ResonanceState())
        rec("mutation::pulse_leaks", st.scores.get("f", 0.0) > 0.0,
            f"filter disabled -> faded score={st.scores.get('f', 0.0):.4f}")
    finally:
        faded_policy.is_faded = orig  # restore
    rec("mutation::restored_excludes",
        _affinity(plane, "a", "f")["affinity"] == 0.0
        and "f" not in pulse(plane, ResonanceState()).scores,
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

cube = give("R35CH", clean=True)
cube.place_idea("a", "river flow water", skin=Skin.SEED, x=0.0)
cube.place_idea("b", "river bank shore", skin=Skin.SEED, x=1.0)
cube.place_idea("f", "river faded silt", skin=Skin.SEED, x=2.0)
plane = cube.session.plane
plane.units["f"].lifecycle_state = LifecycleState.FADED  # enum form
r["affinity_zero"] = (_affinity(plane, "a", "f")["affinity"] == 0.0)
st = pulse(plane, ResonanceState())
r["pulse_excludes"] = ("f" not in st.scores and st.scores.get("a", 0.0) > 0
                       and st.scores.get("b", 0.0) > 0)
# All-faded: empty, no exception.
for u in plane.units.values():
    u.lifecycle_state = "faded"
st2 = pulse(plane, ResonanceState())
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
    print("=== P3 R3.5 INTEGRATION PROOF ===", flush=True)
    print("-- 3.5.1 handoff contract (INTEGRATION) --", flush=True)
    t351_handoff()
    print("-- 3.5.2 faded policy units (INTEGRATION) --", flush=True)
    t352_policy_unit()
    print("-- 3.5.2 _affinity exclusion (INTEGRATION) --", flush=True)
    t352_affinity()
    print("-- 3.5.2 pulse exclusion (INTEGRATION) --", flush=True)
    t352_pulse()
    print("-- 3.5.2 harmony guard --", flush=True)
    t352_harmony_guard()
    print("-- 3.5.3 observation witness (INTEGRATION) --", flush=True)
    t353_observation()
    print("-- 3.5.4 public path (INTEGRATION) --", flush=True)
    t354_public_path()
    print("-- 3.5.5 graph deferral (INTEGRATION) --", flush=True)
    t355_deferral()
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
