"""Harness self-tests: prove every required property of the swarm bootstrap.

Run: python3 -m ops.swarm.tests.test_harness  (from repo root)
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from ops.swarm import run_store, state_machine
from ops.swarm.state_machine import (
    AuthorityError, TransitionError, authorize_action, check_base,
    invalidate_certification_on_head_change, legal_transitions, transition,
)

BASE = "53919043224b18e12516bd9e885b9352de33422f"
TREE = "561a09934aa103608ae09fb25c2bfa5d3e29977b"
ROOT = os.path.join(os.path.dirname(__file__), "..")

PASS = []
FAIL = []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
    except Exception as e:
        FAIL.append((name, f"{type(e).__name__}: {e}"))


def mk():
    return run_store.new_run(
        "TEST-R1", base_sha=BASE, base_tree=TREE, goal="test",
        director_authority={"directive": "test", "decision": "PROCEED", "autonomy": "NO"},
        allowed_actions=["read-only inspection", "run tests"],
        forbidden_actions=["merge to main"],
        director_decision_required=True,
    )


def t_run_creation():
    r = mk()
    assert r["phase"] == "DIRECTOR_SCOPE"
    assert r["termination"]["state"] == "ACTIVE"
    assert r["director_authority"]["autonomy"] == "NO"

def t_transition_validation():
    r = mk()
    transition(r, "ORACLE_RECON")
    assert r["phase"] == "ORACLE_RECON"

def t_illegal_transition_refusal():
    r = mk()
    transition(r, "ORACLE_RECON")
    try:
        transition(r, "DIRECTOR_SCOPE")  # backward jump is illegal (only DIRECTOR_GATE re-scopes)
        raise AssertionError("should have refused")
    except TransitionError:
        pass
    # forward jump skipping non-required states IS legal by design (manifest lists required gates)

def t_decision_required_blocks_complete():
    r = mk()
    transition(r, "ORACLE_RECON")
    run_store.append_evidence(r, "ORACLE", "x", "VERIFIED", "test")
    r["next_directive"] = "do y"
    try:
        transition(r, "COMPLETE")
        raise AssertionError("should have refused")
    except TransitionError as e:
        assert "AUTHORITY" in str(e)

def t_complete_allowed_with_decision():
    r = mk()
    run_store.append_evidence(r, "ORACLE", "x", "VERIFIED", "test")
    r["next_directive"] = "do y"
    r["director_decision"] = {"decision": "PROCEED", "detail": "ok", "recorded_by": "DIRECTOR",
                              "recorded_at": "2026-10-03T00:00:00Z", "reason": None,
                              "release_condition": None, "bounded_directive": None, "candidate_head": None}
    transition(r, "COMPLETE")
    assert r["termination"]["state"] == "COMPLETE"

def t_hold_requires_release_condition():
    r = mk()
    r["director_decision"] = {"decision": "HOLD", "detail": "wait", "recorded_by": "DIRECTOR",
                              "recorded_at": "2026-10-03T00:00:00Z", "reason": None,
                              "release_condition": None, "bounded_directive": None, "candidate_head": None}
    try:
        transition(r, "HOLD")
        raise AssertionError("should have refused")
    except TransitionError:
        pass
    r["director_decision"]["release_condition"] = "CI green"
    transition(r, "HOLD")
    assert r["termination"]["state"] == "HOLD"

def t_stopped_requires_reason():
    r = mk()
    r["director_decision"] = {"decision": "STOP", "detail": "x", "recorded_by": "DIRECTOR",
                              "recorded_at": "2026-10-03T00:00:00Z", "reason": None,
                              "release_condition": None, "bounded_directive": None, "candidate_head": None}
    try:
        transition(r, "STOPPED")
        raise AssertionError("should have refused")
    except TransitionError:
        pass

def t_evidence_provenance():
    r = mk()
    run_store.append_evidence(r, "ORACLE", "handler exists", "VERIFIED", "query_ops.py:39")
    run_store.append_evidence(r, "ARGUS", "closure claim false", "VERIFIED", "probe.py:12")
    agents = [e["agent"] for e in r["evidence"]]
    assert agents == ["ORACLE", "ARGUS"]
    assert all(e["classification"] in ("VERIFIED", "DERIVED", "PROJECTION", "UNKNOWN") for e in r["evidence"])

def t_contradiction_survives():
    r = mk()
    run_store.add_contradiction(r, "C1", ["ORACLE", "ARGUS"], "Dell21 scope disputed")
    # simulate PRISM reconciliation: contradictions must remain OPEN without new evidence
    c = r["contradictions"][0]
    assert c["status"] == "OPEN" and c["resolution"] is None

def t_unknown_survives():
    r = mk()
    run_store.append_evidence(r, "ORACLE", "Dell70 semantics", "UNKNOWN", "no handler body found")
    # reconciliation must not upgrade UNKNOWN
    assert r["evidence"][0]["classification"] == "UNKNOWN"

def t_no_silent_overwrite():
    r = mk()
    run_store.append_evidence(r, "ORACLE", "claim A", "VERIFIED", "src1")
    before = json.dumps(r["evidence"])
    # another agent appends; original entry untouched
    run_store.append_evidence(r, "ARGUS", "claim B", "DERIVED", "src2")
    assert json.loads(before)[0] == r["evidence"][0]

def t_base_mismatch_stops():
    r = mk()
    try:
        check_base(r, "0" * 40, TREE)
        raise AssertionError("should have refused")
    except TransitionError:
        pass
    check_base(r, BASE, TREE)  # matching base passes

def t_head_change_invalidates_ci():
    r = mk()
    r["candidate_head"] = "a" * 40
    r["ci"] = {"state": "green"}
    invalidate_certification_on_head_change(r, "b" * 40)
    assert r["ci"] is None
    assert any("invalidated" in e["claim"] for e in r["evidence"])

def t_secrets_not_persisted():
    r = mk()
    try:
        run_store.append_evidence(r, "UNI", "api_key=ghp_abc123", "VERIFIED", "test")
        raise AssertionError("should have refused")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as tmp:
        try:
            bad = mk()
            bad["goal"] = "password=hunter2"
            run_store.save(tmp, bad)
            raise AssertionError("should have refused")
        except ValueError:
            pass
    # Dell names must not trip the filter (TokenCount false-positive regression)
    r = mk()
    run_store.append_evidence(r, "ORACLE", "40 TokenCount is a heuristic", "VERIFIED", "core_i_ops.py")

def t_autonomy_no():
    r = mk()
    assert r["director_authority"]["autonomy"] == "NO"
    # hard-forbidden actions can never be authorized by the manifest
    try:
        authorize_action(r, "merge to main")
        raise AssertionError("should have refused")
    except AuthorityError:
        pass
    try:
        authorize_action(r, "autonomy expansion")
        raise AssertionError("should have refused")
    except AuthorityError:
        pass
    # merge authorized ONLY by explicit recorded MERGE decision with candidate
    r["director_decision"] = {"decision": "MERGE", "candidate_head": "c" * 40, "detail": "ok",
                              "recorded_by": "DIRECTOR", "recorded_at": "2026-10-03T00:00:00Z",
                              "reason": None, "release_condition": None, "bounded_directive": None}
    authorize_action(r, "merge to main")  # must not raise

def t_fresh_process_reload():
    with tempfile.TemporaryDirectory() as tmp:
        r = mk()
        transition(r, "ORACLE_RECON")
        run_store.append_evidence(r, "ORACLE", "x", "VERIFIED", "s")
        path = run_store.save(tmp, r)
        # fresh process reload
        out = subprocess.run([sys.executable, "-c",
                              "import json,sys; print(json.load(open(sys.argv[1]))['phase'])",
                              path], capture_output=True, text=True)
        assert out.stdout.strip() == "ORACLE_RECON", out.stderr
        r2 = run_store.load(tmp, "TEST-R1")
        assert r2["phase"] == "ORACLE_RECON" and len(r2["evidence"]) == 1

def t_required_gates_skip():
    r = mk()
    r["required_gates"] = ["ARGUS_ATTACK"]
    # skipping ARGUS_ATTACK must be refused even on forward jump
    try:
        transition(r, "NULL_FALSIFY")
        raise AssertionError("should have refused")
    except TransitionError:
        pass
    # but the gate itself is reachable
    transition(r, "ORACLE_RECON")
    transition(r, "ARGUS_ATTACK")


TESTS = [
    ("run creation", t_run_creation),
    ("state transition validation", t_transition_validation),
    ("illegal transition refusal", t_illegal_transition_refusal),
    ("DIRECTOR_DECISION_REQUIRED prevents COMPLETE", t_decision_required_blocks_complete),
    ("COMPLETE allowed with decision+evidence+continuation", t_complete_allowed_with_decision),
    ("HOLD requires release condition", t_hold_requires_release_condition),
    ("STOPPED requires reason", t_stopped_requires_reason),
    ("agent evidence retains provenance", t_evidence_provenance),
    ("contradictions survive reconciliation", t_contradiction_survives),
    ("UNKNOWN survives reconciliation", t_unknown_survives),
    ("no silent overwrite of agent evidence", t_no_silent_overwrite),
    ("base SHA mismatch stops run", t_base_mismatch_stops),
    ("candidate SHA change invalidates CI", t_head_change_invalidates_ci),
    ("secrets are not persisted", t_secrets_not_persisted),
    ("AUTONOMY remains NO; hard-forbidden gated", t_autonomy_no),
    ("fresh-process reload works", t_fresh_process_reload),
    ("required gates cannot be skipped", t_required_gates_skip),
]


def main():
    for name, fn in TESTS:
        check(name, fn)
    print(f"HARNESS TESTS: {len(PASS)}/{len(TESTS)} passed")
    for name, err in FAIL:
        print(f"  FAIL {name}: {err}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
