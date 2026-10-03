"""SUSX100 tests: prove every required 20-delta property.

Run: python3 -m ops.swarm.tests.test_susx100  (from repo root)
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from ops.swarm import run_store, state_machine
from ops.swarm.state_machine import (AuthorityError, TransitionError,
                                     authorize_action, set_mode)
from ops.swarm.susx100 import metrics, spawning, context, sync, resonance, ledger, improvement, directive

PASS, FAIL = [], []


def check(name, fn):
    try:
        fn()
        PASS.append(name)
    except Exception as e:
        FAIL.append((name, f"{type(e).__name__}: {e}"))


BASE = "53919043224b18e12516bd9e885b9352de33422f"
TREE = "561a09934aa103608ae09fb25c2bfa5d3e29977b"
CONTRACTS = os.path.join(os.path.dirname(__file__), "..", "susx100", "contracts")


def t_contracts_have_20_deltas():
    for persona in ("uni", "oracle", "argus", "null", "prism"):
        text = open(os.path.join(CONTRACTS, f"{persona}.md")).read()
        for i in range(1, 21):
            assert f"D{i:02d}" in text, f"{persona} missing D{i:02d}"

def t_spawn_zero_unnecessary():
    cands = [
        {"persona": "ORACLE", "impact": 0.1, "uncertainty": 0.1, "dependency": 1.0,
         "risk": 0.1, "estimated_cost": 10.0, "mission": "trivial fact check"},
    ]
    assert spawning.select_workers(cands) == []

def t_high_risk_independent_verification():
    assert spawning.independent_verification_required(0.9) is True
    assert spawning.independent_verification_required(0.2) is False

def t_evidence_independence_tracked():
    ev = [
        {"claim_id": "C1", "agent": "ORACLE", "supports": True, "method": "code-read", "root_assumption": ""},
        {"claim_id": "C1", "agent": "ARGUS", "supports": True, "method": "live-probe", "root_assumption": ""},
    ]
    r = resonance.independent_support("C1", ev)
    assert r["independent_methods"] == 2 and r["resonant"] is True

def t_correlated_not_independent():
    ev = [{"claim_id": "C1", "agent": f"A{i}", "supports": True,
           "method": "same-assumption", "root_assumption": "X"} for i in range(5)]
    r = resonance.independent_support("C1", ev)
    assert r["independent_methods"] == 1 and r["resonant"] is False

def t_unknown_survives_prism():
    rec = {"contradictory_evidence": [
        {"claim": "Dell52 semantics", "classification": "UNKNOWN", "preserved": True}]}
    assert resonance.minority_survives(rec) is True

def t_minority_contradiction_survives():
    rec = {"contradictory_evidence": [
        {"claim": "minority view", "preserved": True}]}
    assert resonance.minority_survives(rec) is True
    rec2 = {"contradictory_evidence": [{"claim": "erased", "preserved": False}]}
    assert resonance.minority_survives(rec2) is False

def t_critical_contradiction_blocks_merge():
    contra = [{"id": "C-X", "status": "OPEN", "severity": "CRITICAL"}]
    v = resonance.merge_blocked_by_contradictions(contra)
    assert v["blocked"] is True and v["blocking"] == ["C-X"]
    ok = [{"id": "C-Y", "status": "RESOLVED", "severity": "CRITICAL"}]
    assert resonance.merge_blocked_by_contradictions(ok)["blocked"] is False

def t_metrics_cannot_grant_authority():
    v = metrics.candidate_value(9, 9, 9, 9, 0.1, 0.1, 0.1)  # enormous V
    assert v > 1e6
    run = run_store.new_run("TM", base_sha=BASE, base_tree=TREE, goal="t",
                            director_authority={"directive": "t", "decision": "PROCEED", "autonomy": "NO"},
                            allowed_actions=["read"], forbidden_actions=["merge to main"])
    try:
        authorize_action(run, "merge to main")  # V is irrelevant here
        raise AssertionError("metrics must not authorize")
    except AuthorityError:
        pass
    sep = metrics.metric_authority_separation()
    assert sep["metrics_consulted"] == []

def t_q_vector_not_collapsed():
    q = metrics.run_vector(0.9, 0.8, 0.7, 1.0, 0.6, 1.0, 2.5, 0.4)
    assert set(q) == {"E_evidence_coverage", "F_falsification_coverage", "C_contradiction_resolution",
                      "U_uncertainty_integrity", "R_recovery_coverage", "A_authority_coverage",
                      "T_token_efficiency", "P_production_capability"}
    assert not isinstance(q, (int, float))

def t_token_efficiency_and_rr():
    assert metrics.token_efficiency(10, 5000) == 2.0
    assert metrics.redundancy_ratio(0, 0) == 0.0
    assert metrics.contradiction_debt([{"status": "OPEN", "severity": "HIGH"}]) == 9.0

def t_self_improvement_no_self_authorize():
    p = improvement.propose("ORACLE", "evidence methods", {"touches": ["tests"]}, "better probes")
    for stage in ("ARGUS_ATTACK", "NULL_CHALLENGE", "PRISM_RECONCILE", "DIRECTOR_DECISION"):
        improvement.advance(p, stage, by="HARNESS")
    try:
        improvement.advance(p, "APPROVED", by="ORACLE", director_approved=False)
        raise AssertionError("self-authorization must fail")
    except improvement.SelfAuthorizationError:
        pass
    improvement.advance(p, "APPROVED", by="DIRECTOR", director_approved=True)
    assert p["stage"] == "APPROVED"

def t_persona_cannot_touch_hard_authority():
    try:
        improvement.propose("ARGUS", "gates", {"touches": ["autonomy"]}, "weaken")
        raise AssertionError("must refuse")
    except improvement.SelfAuthorizationError:
        pass
    try:
        improvement.amend_own_contract("PRISM", "contracts/prism.md")
        raise AssertionError("must refuse")
    except improvement.SelfAuthorizationError:
        pass

def _full_directive():
    return {f: "x" for f in directive.REQUIRED_FIELDS}

def t_directive_rejects_missing_authority():
    d = _full_directive(); d["authority"] = ""
    try:
        directive.compile(d); raise AssertionError("must reject")
    except directive.DirectiveError as e:
        assert "authority" in str(e)

def t_directive_rejects_missing_falsification():
    d = _full_directive(); d["falsification_targets"] = ""
    try:
        directive.compile(d); raise AssertionError("must reject")
    except directive.DirectiveError as e:
        assert "falsification_targets" in str(e)

def t_directive_rejects_missing_recovery():
    d = _full_directive(); d["recovery_requirements"] = ""
    try:
        directive.compile(d); raise AssertionError("must reject")
    except directive.DirectiveError as e:
        assert "recovery_requirements" in str(e)

def t_directive_rejects_missing_success_stop():
    d = _full_directive(); d["success_condition"] = ""; d["stop_condition"] = ""
    try:
        directive.compile(d); raise AssertionError("must reject")
    except directive.DirectiveError as e:
        assert "success_condition" in str(e) and "stop_condition" in str(e)

def t_directive_accepts_complete():
    assert directive.compile(_full_directive())["_compiled"] == "SUSX100 DIRECTIVE V1"

def t_context_preserves_invariants():
    ctx = context.minimum_context(
        authority={"a": 1}, goal="g", relevant_state={}, evidence_refs=["e1"],
        relevant_contradictions=[], exact_task="t", forbidden_actions=["x"],
        output_contract="o")
    assert context.check_invariants(ctx) == []
    for inv in context.NEVER_DROP:
        assert inv in ctx

def t_core_swarm_preserves_ledger():
    run = run_store.new_run("TC", base_sha=BASE, base_tree=TREE, goal="t", mode="SWARM",
                            director_authority={"directive": "t", "decision": "PROCEED", "autonomy": "NO"})
    led = ledger.new_ledger("ORACLE")
    ledger.record(led, "useful_findings", 3)
    run["performance_ledger"] = {"ORACLE": led}
    run_store.append_evidence(run, "ORACLE", "x", "VERIFIED", "s")
    set_mode(run, "CORE", "DIRECTOR")
    set_mode(run, "SWARM", "DIRECTOR")
    assert run["performance_ledger"]["ORACLE"]["useful_findings"] == 3
    assert len(run["evidence"]) >= 1

def t_fresh_process_reload_susx100():
    with tempfile.TemporaryDirectory() as tmp:
        led = ledger.new_ledger("ARGUS")
        ledger.record(led, "contradictions_found", 2, note="C1")
        path = os.path.join(tmp, "ledger.json")
        json.dump(led, open(path, "w"))
        out = subprocess.run([sys.executable, "-c",
                              "import json,sys; d=json.load(open(sys.argv[1])); "
                              "print(d['contradictions_found'], d['notes'][0])",
                              path], capture_output=True, text=True)
        assert out.stdout.strip() == "2 C1", out.stderr

def t_sync_independence_guard():
    s = sync.Synchronizer()
    assert s.phase == "FAN_OUT"
    for _ in range(3):
        s.advance()
    assert s.phase == "EVIDENCE_INGEST"
    s.ingest("oracle-1", {"claim": "x"})  # not marked independent: recorded as such
    assert s.log[-1]["independent"] is False
    s.mark_independent_done("oracle-2")
    s.ingest("oracle-2", {"claim": "y"})
    assert s.log[-1]["independent"] is True

def t_ledger_diagnose_no_vanity():
    led = ledger.new_ledger("NULL")
    ledger.record(led, "false_positives", 5)
    ledger.record(led, "useful_findings", 2)
    d = ledger.diagnose(led)
    assert any("false positives" in w for w in d["weaknesses"])
    assert "score" not in d and "rating" not in d

def t_spawning_priority_formula():
    p = spawning.priority(impact=8, uncertainty=0.9, dependency=1.0, risk=0.8, estimated_cost=2.0)
    assert abs(p - (8 * 0.9 * 1.0 * 0.8) / 2.0) < 1e-9
    rec = spawning.spawn_record("ORACLE", "o-1", "m", "none", "r", 1.5)
    assert rec["persona"] == "ORACLE" and rec["actual_cost"] is None

def t_no_dell_semantics_changed():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                         capture_output=True, text=True, cwd="/tmp/mpc004-base")
    # worktree may have untracked ops/ only; committed diff must be empty or ops-only
    out2 = subprocess.run(["git", "status", "--porcelain"],
                          capture_output=True, text=True, cwd="/tmp/mpc004-base")
    changed = [l[3:] for l in out2.stdout.splitlines() if l.strip() and not l.startswith("??")]
    assert all(c.startswith("ops/") for c in changed), f"non-ops change: {changed}"
    out3 = subprocess.run(["git", "diff", "--cached", "--name-only"],
                          capture_output=True, text=True, cwd="/tmp/mpc004-base")
    assert all(c.startswith("ops/") or c == "" for c in out3.stdout.splitlines()), "staged non-ops change"


TESTS = [
    ("contracts contain 20-delta obligations", t_contracts_have_20_deltas),
    ("spawning can choose zero workers", t_spawn_zero_unnecessary),
    ("high-risk requires independent verification", t_high_risk_independent_verification),
    ("evidence independence tracked", t_evidence_independence_tracked),
    ("correlated agreement not independent proof", t_correlated_not_independent),
    ("UNKNOWN survives PRISM", t_unknown_survives_prism),
    ("minority contradiction survives PRISM", t_minority_contradiction_survives),
    ("critical contradiction blocks merge recommendation", t_critical_contradiction_blocks_merge),
    ("metrics cannot grant authority", t_metrics_cannot_grant_authority),
    ("Q vector not collapsed to scalar", t_q_vector_not_collapsed),
    ("TE/RR/CD formulas", t_token_efficiency_and_rr),
    ("self-improvement cannot self-authorize", t_self_improvement_no_self_authorize),
    ("persona cannot touch hard authority", t_persona_cannot_touch_hard_authority),
    ("directive rejects missing authority", t_directive_rejects_missing_authority),
    ("directive rejects missing falsification", t_directive_rejects_missing_falsification),
    ("directive rejects missing recovery", t_directive_rejects_missing_recovery),
    ("directive rejects missing success/stop", t_directive_rejects_missing_success_stop),
    ("directive accepts complete", t_directive_accepts_complete),
    ("context preserves invariants", t_context_preserves_invariants),
    ("CORE/SWARM preserves ledger+evidence", t_core_swarm_preserves_ledger),
    ("fresh-process reload susx100", t_fresh_process_reload_susx100),
    ("sync independence guard", t_sync_independence_guard),
    ("ledger diagnose has no vanity score", t_ledger_diagnose_no_vanity),
    ("spawning priority formula", t_spawning_priority_formula),
    ("no Dell semantics changed", t_no_dell_semantics_changed),
]


def main():
    for name, fn in TESTS:
        check(name, fn)
    print(f"SUSX100 TESTS: {len(PASS)}/{len(TESTS)} passed")
    for name, err in FAIL:
        print(f"  FAIL {name}: {err}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
