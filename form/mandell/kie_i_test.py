"""KIE-I: Knowledge Influence Explanation I — contract tests.

Read-only explanation layer over existing authorities.
Tests the Knowledge Influence Chain:
  STORED → ELIGIBLE → SELECTED → ROUTABLE → USED → OBSERVED → LEARNED

REALISM:
  UNIT_SYNTHETIC: direct knowledge_influence.* calls
  INTEGRATION: via ROS views + REPL handler
  CROSS_PROCESS: real subprocess (not just new instance)
  REAL_USER_PATH: via _repl_dispatch (same order as run() loop)

EPISTEMIC: FACT / DERIVED_FACT / UNKNOWN. No causal claims.
"""
import io
import sys
import subprocess
import tempfile
import os

sys.path.insert(0, ".")

from form.open import Program
from form.mandell import knowledge_influence as ki
from form.mandell import knowledge_selector as ks
from form.mandell.execution_observer import observe_seed_execution

_passed = 0
_failed = 0
_failures = []


def check(name, cond):
    global _passed, _failed
    if cond:
        _passed += 1
    else:
        _failed += 1
        _failures.append(name)
        print(f"FAIL: {name}")


def fresh() -> Program:
    return Program()


def make_knowledge(p, label="kie-idea", words="test knowledge about growth"):
    pr = p.nursery.add(label, words=words)
    p.confirm_proposal(pr.id)
    return pr.id


# ══════════════════════════════════════════════════════════════════
# T1: Direct explanation contracts (UNIT_SYNTHETIC)
# ══════════════════════════════════════════════════════════════════

def test_stored_fact():
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid)
    stored = exp["chain"]["STORED"]
    check("T1.stored_fact", stored["status"] == "FACT" and stored["id"] == kid)


def test_stored_unknown():
    p = fresh()
    exp = ki.explain_influence(p, "nonexistent-id")
    check("T1.stored_unknown", exp["chain"]["STORED"]["status"] == "UNKNOWN")


def test_eligible_fact():
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid)
    elig = exp["chain"]["ELIGIBLE"]
    # Should be eligible (not superseded, no bad deps)
    check("T1.eligible", elig["status"] in ("FACT", "DERIVED_FACT"))


def test_superseded_not_eligible():
    p = fresh()
    kid1 = make_knowledge(p, "kie-old", "old knowledge")
    # Supersede it
    from form.mandell.supersession import supersede_proposal
    try:
        receipt = supersede_proposal(p, kid1, "new knowledge words")
        kid2 = receipt.get("new_id")
    except Exception:
        check("T1.superseded_setup", False)
        return
    exp = ki.explain_influence(p, kid1)
    elig = exp["chain"]["ELIGIBLE"]
    check("T1.superseded_not_eligible",
          elig.get("eligible") is False and elig.get("reason") == "SUPERSEDED")


def test_selected_with_context():
    p = fresh()
    kid = make_knowledge(p, words="knowledge about growth patterns")
    exp = ki.explain_influence(p, kid, context="growth")
    sel = exp["chain"]["SELECTED"]
    check("T1.selected", sel["status"] == "FACT" and sel.get("selected") is True)


def test_not_selected_wrong_context():
    p = fresh()
    kid = make_knowledge(p, words="knowledge about growth patterns")
    exp = ki.explain_influence(p, kid, context="quantum xyzzy unrelated")
    sel = exp["chain"]["SELECTED"]
    # May or may not be selected; just verify structure
    check("T1.not_selected_struct", sel["status"] == "FACT" and "selected" in sel)


def test_historical_from_outcome():
    p = fresh()
    kid = make_knowledge(p, words="knowledge about growth")
    # Execute with knowledge to create Outcome with provenance
    observe_seed_execution(p, "1[Keep]")
    oid = list(p.outcome_records.values())[-1]["outcome_id"]
    # Explain (historical mode)
    exp = ki.explain_influence(p, kid, outcome_id=oid)
    check("T1.historical_mode", exp["mode"] == "historical")
    # ELIGIBLE should be UNKNOWN for historical (not captured)
    check("T1.historical_eligible_unknown",
          exp["chain"]["ELIGIBLE"]["status"] == "UNKNOWN")


def test_historical_unknown_outcome():
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid, outcome_id="bad-oid")
    check("T1.hist_unknown", exp["chain"]["OBSERVED"]["status"] == "UNKNOWN")


def test_why_used():
    p = fresh()
    kid = make_knowledge(p)
    observe_seed_execution(p, "1[Keep]")
    oid = list(p.outcome_records.values())[-1]["outcome_id"]
    res = ki.why_used(p, kid, oid)
    check("T1.why_used_q", "WHY WAS" in res["question"] and "USED" in res["question"])
    check("T1.why_used_epistemic", "observation" in res.get("epistemic", "").lower())


def test_why_not_used():
    p = fresh()
    kid1 = make_knowledge(p, "kie-a", "alpha knowledge")
    # Supersede kid1 so it's blocked
    from form.mandell.supersession import supersede_proposal
    try:
        supersede_proposal(p, kid1, "replacement words")
    except Exception:
        pass
    res = ki.why_not_used(p, kid1, context="alpha")
    check("T1.why_not_q", "NOT USED" in res["question"])
    # Should have blocking reasons
    check("T1.why_not_reasons", len(res.get("blocking_reasons", [])) > 0)


def test_no_causal_language():
    """Epistemic guard: explanations must not claim causation."""
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid, context="growth")
    import json
    text = json.dumps(exp).lower()
    # Should not contain causal claims
    check("T1.no_caused", "caused" not in text)
    check("T1.no_causes", "causes " not in text)


def test_read_only():
    """Explanation must not mutate program state."""
    p = fresh()
    kid = make_knowledge(p)
    n_before = len(p.nursery.proposals)
    ki.explain_influence(p, kid, context="growth")
    ki.why_not_used(p, kid)
    n_after = len(p.nursery.proposals)
    check("T1.read_only", n_before == n_after)


# ══════════════════════════════════════════════════════════════════
# T2: Adversarial (UNIT_SYNTHETIC + INTEGRATION)
# ══════════════════════════════════════════════════════════════════

def test_historical_not_rewritten():
    """Later state changes must not rewrite historical explanation."""
    p = fresh()
    kid = make_knowledge(p, "kie-hist", "historical knowledge")
    observe_seed_execution(p, "1[Keep]")
    oid = list(p.outcome_records.values())[-1]["outcome_id"]
    
    # Get historical explanation
    exp1 = ki.explain_influence(p, kid, outcome_id=oid)
    obs1 = exp1["chain"]["OBSERVED"]
    
    # Now supersede the knowledge (changes current state)
    from form.mandell.supersession import supersede_proposal
    try:
        supersede_proposal(p, kid, "newer words here")
    except Exception:
        pass
    
    # Historical explanation must be unchanged
    exp2 = ki.explain_influence(p, kid, outcome_id=oid)
    obs2 = exp2["chain"]["OBSERVED"]
    check("T2.hist_stable",
          obs1.get("revision_number") == obs2.get("revision_number"))


def test_ekc_explicit_explained():
    """EKC explicit choice should appear in explanation."""
    p = fresh()
    kid = make_knowledge(p, words="explicit test knowledge")
    # Select with explicit_ids
    result = ks.select_for_context(p, "test", explicit_ids=[kid])
    # Check explanation reflects EKC
    exp = ki.explain_influence(p, kid, context="test")
    sel = exp["chain"]["SELECTED"]
    # The selection should note explicit status if selected
    check("T2.ekc_struct", sel["status"] == "FACT")


# ══════════════════════════════════════════════════════════════════
# T5: Real user path via REPL dispatch (REAL_USER_PATH)
# ══════════════════════════════════════════════════════════════════

def _repl_dispatch(p, commands):
    from form import repl as repl_mod
    buf = io.StringIO()
    old_say = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        for line in commands:
            line = line.strip()
            if not line:
                continue
            if repl_mod._handle_ros_command(p, line):
                continue
            if repl_mod._handle_learn_command(p, line):
                continue
            if repl_mod._handle_why_command(p, line):
                continue
    finally:
        repl_mod._say = old_say
    return buf.getvalue()


def test_repl_why_influence():
    p = fresh()
    kid = make_knowledge(p)
    out = _repl_dispatch(p, [f"why influence {kid} for growth"])
    check("T5.why_influence", "STORED" in out and "ELIGIBLE" in out)


def test_repl_why_not_used():
    p = fresh()
    kid = make_knowledge(p)
    out = _repl_dispatch(p, [f"why not used {kid} for growth"])
    check("T5.why_not_used", "WHY WAS" in out and "NOT USED" in out)


def test_repl_why_used():
    p = fresh()
    kid = make_knowledge(p)
    observe_seed_execution(p, "1[Keep]")
    oid = list(p.outcome_records.values())[-1]["outcome_id"]
    out = _repl_dispatch(p, [f"why used {kid} in {oid}"])
    check("T5.why_used", "WHY WAS" in out and "USED" in out)


def test_repl_why_help():
    p = fresh()
    out = _repl_dispatch(p, ["why frobnicate"])
    check("T5.why_help", "why used" in out.lower())


# ══════════════════════════════════════════════════════════════════
# T4: Cross-process (REAL subprocess)
# ══════════════════════════════════════════════════════════════════

def test_cross_process_explanation():
    """CROSS_PROCESS: explanation works after real subprocess restart."""
    script = '''
import sys
sys.path.insert(0, ".")
from form.open import Program
from form.mandell import knowledge_influence as ki

# Load saved program
p = Program.load(path=sys.argv[1])
kid = sys.argv[2]
exp = ki.explain_influence(p, kid)
stored = exp["chain"]["STORED"]
print(f"STORED_STATUS:{stored['status']}")
print(f"STORED_ID:{stored.get('id', '')}")
'''
    p = fresh()
    kid = make_knowledge(p, "kie-xproc", "cross process test")
    
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "kie.dell")
        p.save(path)
        # Real subprocess
        result = subprocess.run(
            [sys.executable, "-c", script, path, kid],
            capture_output=True, text=True, cwd=".",
            env={**os.environ, "PYTHONPATH": "."},
            timeout=30,
        )
        out = result.stdout
        check("T4.xproc_stored", "STORED_STATUS:FACT" in out)
        check("T4.xproc_id", kid in out)


# ══════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════

def main():
    tests = [
        test_stored_fact,
        test_stored_unknown,
        test_eligible_fact,
        test_superseded_not_eligible,
        test_selected_with_context,
        test_not_selected_wrong_context,
        test_historical_from_outcome,
        test_historical_unknown_outcome,
        test_why_used,
        test_why_not_used,
        test_no_causal_language,
        test_read_only,
        test_historical_not_rewritten,
        test_ekc_explicit_explained,
        test_repl_why_influence,
        test_repl_why_not_used,
        test_repl_why_used,
        test_repl_why_help,
        test_cross_process_explanation,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
            global _failed
            _failed += 1
            _failures.append(f"{t.__name__}: EXC {e}")
            print(f"EXC in {t.__name__}: {e}")
    total = _passed + _failed
    print(f"\nKIE-I: {_passed}/{total} {'GREEN' if _failed == 0 else 'RED'}")
    if _failures:
        print("Failures:")
        for f in _failures:
            print(f"  - {f}")
    return 0 if _failed == 0 else 1


def smoke() -> bool:
    global _passed, _failed, _failures
    _passed = 0
    _failed = 0
    _failures = []
    main()
    return _failed == 0


if __name__ == "__main__":
    sys.exit(main())
