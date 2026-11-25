"""Dual-mode continuity tests (MPC-004 R1 addendum).

Run: python3 -m ops.swarm.tests.test_modes  (from repo root)
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from ops.swarm import run_store, state_machine
from ops.swarm.state_machine import TransitionError
from ops.swarm.tests.test_harness import BASE, TREE, mk


def t_mode_persisted_explicit():
    r = mk()
    assert r["mode"] == "SWARM"
    assert r["mode_history"][0]["to"] == "SWARM"
    r2 = run_store.new_run("M2", base_sha=BASE, base_tree=TREE, goal="t", mode="CORE",
                           director_authority={"directive": "t", "decision": "PROCEED", "autonomy": "NO"})
    assert r2["mode"] == "CORE"
    try:
        run_store.new_run("M3", base_sha=BASE, base_tree=TREE, goal="t", mode="BOGUS",
                          director_authority={"directive": "t", "decision": "PROCEED", "autonomy": "NO"})
        raise AssertionError("should have refused")
    except ValueError:
        pass

def _rich_run():
    r = mk()
    run_store.append_evidence(r, "ORACLE", "handler exists", "VERIFIED", "query_ops.py:39")
    run_store.append_evidence(r, "ARGUS", "claim attacked", "DERIVED", "probe")
    run_store.append_evidence(r, "UNI", "semantics unknown here", "UNKNOWN", "n/a")
    run_store.add_contradiction(r, "C1", ["ORACLE", "ARGUS"], "scope disputed")
    r["candidate_head"] = "a" * 40
    r["ci"] = {"state": "green", "head": "a" * 40}
    r["next_directive"] = "do next"
    r["agent_status"] = {"ORACLE": "DELIVERED", "ARGUS": "RUNNING"}
    return r

def t_swarm_to_core_preserves_everything():
    r = _rich_run()
    before = {k: json.loads(json.dumps(v)) for k, v in r.items() if k not in ("mode", "mode_history", "evidence")}
    ev_before = [e for e in r["evidence"] if e["agent"] != "HARNESS"]
    state_machine.set_mode(r, "CORE", "DIRECTOR")
    assert r["mode"] == "CORE"
    for k, v in before.items():
        assert r[k] == v, f"field {k} changed across mode transition"
    assert ev_before == [e for e in r["evidence"] if e["agent"] != "HARNESS"]
    assert len(r["contradictions"]) == 1 and r["contradictions"][0]["status"] == "OPEN"
    assert r["candidate_head"] == "a" * 40 and r["ci"]["state"] == "green"

def t_core_to_swarm_preserves_everything():
    r = _rich_run()
    state_machine.set_mode(r, "CORE", "DIRECTOR")
    snap = json.dumps({k: v for k, v in r.items() if k not in ("mode", "mode_history")})
    state_machine.set_mode(r, "SWARM", "DIRECTOR")
    assert r["mode"] == "SWARM"
    # mode_history records both transitions
    assert [h["to"] for h in r["mode_history"]] == ["SWARM", "CORE", "SWARM"]
    rest = json.dumps({k: v for k, v in r.items() if k not in ("mode", "mode_history", "evidence")})
    assert json.loads(rest) == {k: v for k, v in json.loads(snap).items() if k != "evidence"}

def t_swarm_interrupted_core_recovery():
    r = _rich_run()
    state_machine.set_mode(r, "CORE", "DIRECTOR")
    state_machine.assume_obligations(r, "DIRECTOR")
    # delivered evidence preserved with original provenance
    assert r["agent_status"]["ORACLE"] == "DELIVERED"
    assert r["agent_status"]["ARGUS"] == "ASSUMED_BY_DIRECTOR"
    oracle_ev = [e for e in r["evidence"] if e["agent"] == "ORACLE"]
    assert len(oracle_ev) == 1 and oracle_ev[0]["claim"] == "handler exists"
    # run can still advance and terminate under CORE laws
    state_machine.transition(r, "ORACLE_RECON")
    assert r["phase"] == "ORACLE_RECON"

def t_fresh_process_reload_both_modes():
    with tempfile.TemporaryDirectory() as tmp:
        for mode in ("SWARM", "CORE"):
            r = run_store.new_run(f"M-{mode}", base_sha=BASE, base_tree=TREE, goal="t", mode=mode,
                                  director_authority={"directive": "t", "decision": "PROCEED", "autonomy": "NO"})
            run_store.append_evidence(r, "ORACLE", "x", "VERIFIED", "s")
            path = run_store.save(tmp, r)
            out = subprocess.run([sys.executable, "-c",
                                  "import json,sys; d=json.load(open(sys.argv[1])); print(d['mode'], len(d['evidence']))",
                                  path], capture_output=True, text=True)
            assert out.stdout.strip() == f"{mode} 1", out.stderr

def t_no_runtime_dependency_on_specialists():
    # form/ (DellMatrix runtime) must not import ops.swarm — specialist
    # availability can never become a runtime dependency.
    import subprocess as sp
    out = sp.run(["grep", "-rn", "ops.swarm\\|ops/swarm", "/tmp/mpc004-base/form/"],
                 capture_output=True, text=True)
    assert out.stdout.strip() == "", f"runtime depends on swarm: {out.stdout[:300]}"

def t_mode_does_not_change_laws():
    for mode in ("SWARM", "CORE"):
        laws = state_machine.production_laws_for_mode(mode)
        assert laws["autonomy"] == "NO"
        assert laws["termination_invariant"] == "STATE+EVIDENCE+AUTHORITY+CONTINUATION"
        assert "merge to main" in laws["hard_forbidden"]
        assert laws["evidence_standards"] == "unchanged"
    # termination invariant identical under CORE
    r = run_store.new_run("MC", base_sha=BASE, base_tree=TREE, goal="t", mode="CORE",
                          director_authority={"directive": "t", "decision": "PROCEED", "autonomy": "NO"})
    run_store.append_evidence(r, "DIRECTOR", "recon done", "VERIFIED", "self-directive")
    r["next_directive"] = "next"
    try:
        state_machine.transition(r, "COMPLETE")
        raise AssertionError("should have refused without director decision")
    except TransitionError:
        pass

def t_mode_change_refused_when_terminal():
    r = mk()
    run_store.append_evidence(r, "ORACLE", "x", "VERIFIED", "s")
    r["next_directive"] = "y"
    r["director_decision"] = {"decision": "STOP", "detail": "x", "recorded_by": "DIRECTOR",
                              "recorded_at": "2026-10-03T00:00:00Z", "reason": "done",
                              "release_condition": None, "bounded_directive": None, "candidate_head": None}
    state_machine.transition(r, "STOPPED")
    try:
        state_machine.set_mode(r, "CORE", "DIRECTOR")
        raise AssertionError("should have refused")
    except TransitionError:
        pass


MODE_TESTS = [
    ("mode persisted explicitly at creation", t_mode_persisted_explicit),
    ("SWARM->CORE preserves everything", t_swarm_to_core_preserves_everything),
    ("CORE->SWARM preserves everything", t_core_to_swarm_preserves_everything),
    ("SWARM interrupted -> CORE recovery", t_swarm_interrupted_core_recovery),
    ("fresh-process reload in both modes", t_fresh_process_reload_both_modes),
    ("no DellMatrix runtime dependency on specialists", t_no_runtime_dependency_on_specialists),
    ("mode does not change production laws", t_mode_does_not_change_laws),
    ("mode change refused when terminal", t_mode_change_refused_when_terminal),
]



def t_adaptive_selects_smallest_sufficient():
    from ops.swarm.state_machine import select_adaptive_team, ADAPTIVE_INPUTS
    low = {k: 0.1 for k in ADAPTIVE_INPUTS}
    s = select_adaptive_team(low)
    assert s["team"] == "CORE"
    assert s["authority_note"].startswith("resource allocation")

def t_adaptive_targeted_default_for_ordinary():
    from ops.swarm.state_machine import select_adaptive_team, ADAPTIVE_INPUTS
    mid = {k: 0.1 for k in ADAPTIVE_INPUTS}
    mid.update(evidence_weakness=0.6, estimated_information_gain=0.8, estimated_specialist_cost=0.2)
    assert select_adaptive_team(mid)["team"] == "TARGETED_SWARM"

def t_adaptive_full_swarm_high_stakes():
    from ops.swarm.state_machine import select_adaptive_team, ADAPTIVE_INPUTS
    for key in ("authority_sensitivity", "semantic_uncertainty", "contradiction_debt", "security_relevance"):
        hi = {k: 0.1 for k in ADAPTIVE_INPUTS}
        hi[key] = 0.9
        assert select_adaptive_team(hi)["team"] == "FULL_SWARM", key

def t_adaptive_requires_all_inputs():
    from ops.swarm.state_machine import select_adaptive_team, TransitionError
    try:
        select_adaptive_team({"blast_radius": 0.1})
        raise AssertionError("must refuse incomplete inputs")
    except TransitionError:
        pass

def t_adaptive_backward_compatible():
    from ops.swarm.state_machine import resolve_team
    assert resolve_team({"mode": "CORE"}) == ("DIRECTOR", "UNI")
    assert "PRISM" in resolve_team({"mode": "SWARM"})
    r = {"mode": "ADAPTIVE", "adaptive_selection": {"personas": ["DIRECTOR", "UNI", "ARGUS"]}}
    assert resolve_team(r) == ("DIRECTOR", "UNI", "ARGUS")


ADAPTIVE_TESTS = [
    ("adaptive selects smallest sufficient team", t_adaptive_selects_smallest_sufficient),
    ("adaptive targeted default for ordinary work", t_adaptive_targeted_default_for_ordinary),
    ("adaptive full swarm for high stakes", t_adaptive_full_swarm_high_stakes),
    ("adaptive requires all inputs", t_adaptive_requires_all_inputs),
    ("adaptive backward compatible", t_adaptive_backward_compatible),
]


if __name__ == "__main__":
    from ops.swarm.tests.test_harness import PASS, FAIL, check
    for _name, _fn in MODE_TESTS + ADAPTIVE_TESTS:
        check(_name, _fn)
    ok = sum(1 for n, _ in MODE_TESTS + ADAPTIVE_TESTS if n in PASS)
    print(f"MODE TESTS: {ok}/{len(MODE_TESTS)+len(ADAPTIVE_TESTS)} passed")
    for n, e in FAIL:
        if n in [x for x, _ in MODE_TESTS + ADAPTIVE_TESTS]:
            print(f"  FAIL {n}: {e}")
    sys.exit(1 if any(n in [x for x, _ in MODE_TESTS] for n, _ in FAIL) else 0)
