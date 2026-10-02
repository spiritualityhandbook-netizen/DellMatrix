"""KIE-I: Knowledge Influence Explanation I — contract tests.

Read-only explanation layer over existing authorities.
Tests the Knowledge Influence Chain:
  STORED → ELIGIBLE → SELECTED → ROUTABLE → USED → OBSERVED → LEARNED

ISOLATION (Amendment A):
  fresh() uses a unique per-test Program owner whose nursery is VERIFIED
  empty before use. Program() (default owner) loads persisted state and
  is NOT isolated. Never call it fresh.

REALISM (honest ladder):
  UNIT_SYNTHETIC: direct knowledge_influence.* calls on isolated state
  INTEGRATION: via _repl_dispatch (private dispatcher, high-fidelity)
  CROSS_PROCESS: real subprocess (separate OS process)
  REAL_USER_PATH: real `python3 -m form.repl` with piped stdin
  (literal public entry: main() -> run() -> input() -> dispatch -> handler)

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

# ── Isolation: unique owner per test, emptiness VERIFIED ──
_fresh_counter = [0]
_PID = os.getpid()


def fresh() -> Program:
    """Isolated Program: unique owner, nursery verified empty.

    Not "fresh" by name — fresh by verified precondition.
    Raises (fails loudly) if the nursery is not empty.
    """
    _fresh_counter[0] += 1
    owner = f"kie-c1-isolated-{_PID}-{_fresh_counter[0]}"
    p = Program(owner=owner)
    n = len(p.nursery.proposals)
    if n != 0:
        raise AssertionError(
            f"isolation violated: owner {owner} nursery has {n} proposals"
        )
    return p


def make_knowledge(p, label="kie-idea", words="test knowledge about growth"):
    pr = p.nursery.add(label, words=words)
    p.confirm_proposal(pr.id)
    return pr.id


def check(name, cond):
    global _passed, _failed
    if cond:
        _passed += 1
    else:
        _failed += 1
        _failures.append(name)
        print(f"FAIL: {name}")


def outcome_with_knowledge(p, kid, context="growth"):
    """Supported path: grow using knowledge -> Outcome V1 with kid frozen.

    Precondition enforced: kid MUST appear in the outcome knowledge list,
    else the test fails loudly (never a false-green fixture).
    """
    observe_seed_execution(p, f"37[Nurture] :: grow_using_knowledge_about {context}")
    rec = list(p.outcome_records.values())[-1]
    kl = [k.get("id") for k in (rec.get("knowledge") or [])]
    if kid not in kl:
        raise AssertionError(
            f"fixture failed: {kid} not in outcome knowledge list {kl}"
        )
    return rec["outcome_id"]


# ══════════════════════════════════════════════════════════════════
# T0: Isolation proof (UNIT_SYNTHETIC)
# ══════════════════════════════════════════════════════════════════

def test_isolation_proof():
    """Amendment A: prove the isolation mechanism before trusting results."""
    p1 = fresh()
    p2 = fresh()
    check("T0.p1_empty", len(p1.nursery.proposals) == 0)
    check("T0.p2_empty", len(p2.nursery.proposals) == 0)
    check("T0.distinct_owners", p1.owner != p2.owner)
    # Contamination in one must not leak into the other
    kid = make_knowledge(p1, "kie-iso-a", "isolation probe")
    check("T0.no_cross_contamination", kid not in p2.nursery.proposals)
    # Control: prove the constructor LOADS persisted owner state — the exact
    # mechanism that falsified the old fresh()==Program() assumption.
    # Uses a throwaway owner; its state file is removed afterwards.
    # (Never touches the default/Ace owner state.)
    import pathlib
    from form.dell_matrix.nursery import owner_nursery_path
    cowner = f"kie-c1-control-{_PID}"
    cpath = pathlib.Path(owner_nursery_path(cowner))
    if cpath.exists():
        cpath.unlink()
    pa = Program(owner=cowner)
    if len(pa.nursery.proposals) != 0:
        raise AssertionError("control setup: throwaway owner not empty")
    pra = pa.nursery.add("kie-control-k", words="control probe")
    pa.nursery.save()
    pb = Program(owner=cowner)  # must LOAD the saved proposal
    check("T0.constructor_loads_persisted", pra.id in pb.nursery.proposals)
    cpath.unlink(missing_ok=True)


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


def test_eligible_positive_evidence():
    """C1-1: ELIGIBLE=true only with positive four-gate evidence."""
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid)
    elig = exp["chain"]["ELIGIBLE"]
    check("T1.eligible_true", elig["status"] == "FACT" and elig.get("eligible") is True)
    check("T1.eligible_reason", "confirmed" in elig.get("reason", "").lower())


def test_pending_not_eligible():
    """C1-1 adversarial: PENDING proposal must NOT be eligible.

    Root-cause case: pending proposals are absent from both exclusion
    lists but are ineligible (not confirmed). This is the exact
    false-positive the old code produced.
    """
    p = fresh()
    pr = p.nursery.add("c1-pending", words="unconfirmed idea")
    # NOTE: deliberately NOT confirmed
    exp = ki.explain_influence(p, pr.id)
    elig = exp["chain"]["ELIGIBLE"]
    check("T1.pending_not_eligible",
          elig["status"] == "FACT"
          and elig.get("eligible") is False
          and elig.get("reason") == "NOT_CONFIRMED")


def test_off_plane_gate_live():
    """C1-1: the on-plane gate is positively verified (defense in depth).

    FINDING (documented, not asserted as a passing negative): a
    CONFIRMED-but-OFF-PLANE state is not constructible through supported
    authority — confirm_proposal always promotes to the cube plane and no
    supported API removes a unit from the plane. The gate's positive path
    is verified here; the negative case is recorded as non-constructible.
    """
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid)
    elig = exp["chain"]["ELIGIBLE"]
    # ELIGIBLE=true requires the on-plane gate to have passed positively.
    check("T1.offplane_gate_live",
          elig["status"] == "FACT" and elig.get("eligible") is True)


def test_superseded_not_eligible():
    """C1-1 adversarial: SUPERSEDED must fail the revision gate."""
    p = fresh()
    kid1 = make_knowledge(p, "kie-old", "old knowledge")
    from form.mandell.supersession import supersede_proposal
    supersede_proposal(p, kid1, "new knowledge words")
    exp = ki.explain_influence(p, kid1)
    elig = exp["chain"]["ELIGIBLE"]
    check("T1.superseded_not_eligible",
          elig["status"] == "FACT"
          and elig.get("eligible") is False
          and elig.get("reason") == "SUPERSEDED")


def test_dependency_blocked_not_eligible():
    """C1-1 adversarial: passes confirmed/on-plane/revision-active,
    fails dependency-valid (parent superseded)."""
    p = fresh()
    pp = p.nursery.add("c1-dep-parent", words="parent knowledge")
    p.confirm_proposal(pp.id)
    pc = p.nursery.add("c1-dep-child", words="child knowledge", parents=[pp.id])
    p.confirm_proposal(pc.id)
    from form.mandell.supersession import supersede_proposal
    supersede_proposal(p, pp.id, "parent replacement words")

    exp = ki.explain_influence(p, pc.id)
    elig = exp["chain"]["ELIGIBLE"]
    check("T1.depblocked_not_eligible",
          elig["status"] == "FACT"
          and elig.get("eligible") is False
          and elig.get("reason") == "UNRESOLVED_DEPENDENCY")


def test_selected_with_context():
    p = fresh()
    kid = make_knowledge(p, words="knowledge about growth patterns")
    exp = ki.explain_influence(p, kid, context="growth")
    sel = exp["chain"]["SELECTED"]
    check("T1.selected", sel["status"] == "FACT" and sel.get("selected") is True)


def test_not_selected_wrong_context():
    """E: assert actual not-selected semantics, not just structure."""
    p = fresh()
    kid = make_knowledge(p, words="knowledge about growth patterns")
    exp = ki.explain_influence(p, kid, context="quantum xyzzy unrelated")
    sel = exp["chain"]["SELECTED"]
    check("T1.not_selected_semantics",
          sel["status"] == "FACT"
          and sel.get("selected") is False
          and "not in canonical selection" in sel.get("reason", ""))


def test_historical_from_outcome():
    p = fresh()
    kid = make_knowledge(p, words="knowledge about growth")
    oid = outcome_with_knowledge(p, kid)
    exp = ki.explain_influence(p, kid, outcome_id=oid)
    check("T1.historical_mode", exp["mode"] == "historical")
    check("T1.historical_eligible_unknown",
          exp["chain"]["ELIGIBLE"]["status"] == "UNKNOWN")
    # The knowledge WAS used in this outcome (fixture precondition proven)
    check("T1.historical_used_true",
          exp["chain"]["USED"].get("used") is True)


def test_historical_unknown_outcome():
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid, outcome_id="bad-oid")
    check("T1.hist_unknown", exp["chain"]["OBSERVED"]["status"] == "UNKNOWN")


def test_why_used():
    p = fresh()
    kid = make_knowledge(p)
    oid = outcome_with_knowledge(p, kid)
    res = ki.why_used(p, kid, oid)
    check("T1.why_used_q", "WHY WAS" in res["question"] and "USED" in res["question"])
    check("T1.why_used_epistemic", "observation" in res.get("epistemic", "").lower())


def test_why_not_used():
    p = fresh()
    kid1 = make_knowledge(p, "kie-a", "alpha knowledge")
    from form.mandell.supersession import supersede_proposal
    supersede_proposal(p, kid1, "replacement words")
    res = ki.why_not_used(p, kid1, context="alpha")
    check("T1.why_not_q", "NOT USED" in res["question"])
    check("T1.why_not_reasons", len(res.get("blocking_reasons", [])) > 0)


def test_no_causal_language():
    """Epistemic guard: explanations must not claim causation."""
    p = fresh()
    kid = make_knowledge(p)
    exp = ki.explain_influence(p, kid, context="growth")
    import json
    text = json.dumps(exp).lower()
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
    kid = make_knowledge(p, "kie-hist", "historical knowledge about growth")
    oid = outcome_with_knowledge(p, kid)

    exp1 = ki.explain_influence(p, kid, outcome_id=oid)
    obs1 = exp1["chain"]["OBSERVED"]

    from form.mandell.supersession import supersede_proposal
    supersede_proposal(p, kid, "newer words here")

    exp2 = ki.explain_influence(p, kid, outcome_id=oid)
    obs2 = exp2["chain"]["OBSERVED"]
    check("T2.hist_stable",
          obs1.get("revision_number") == obs2.get("revision_number"))


def test_historical_without_current_storage():
    """C1-2: current absence must not erase historical evidence.

    Two honest synthetic models of 'knowledge gone from current state'
    (no supported removal API exists; both labeled as synthetic):
    (a) outcome record transplanted to an isolated empty-nursery program
    (b) knowledge deleted from the same program after the outcome
    Both must yield identical historical evidence.
    """
    p = fresh()
    kid = make_knowledge(p, "kie-div", "divergence knowledge about growth")
    oid = outcome_with_knowledge(p, kid)

    # (a) transplant to isolated program with empty nursery
    p2 = fresh()
    assert kid not in p2.nursery.proposals  # verified precondition
    p2.outcome_records[oid] = p.outcome_records[oid]
    exp_a = ki.explain_influence(p2, kid, outcome_id=oid)

    # (b) delete from current nursery in the original program
    del p.nursery.proposals[kid]
    exp_b = ki.explain_influence(p, kid, outcome_id=oid)

    for tag, exp in (("a", exp_a), ("b", exp_b)):
        check(f"T2.div_{tag}_used",
              exp["chain"]["USED"].get("used") is True)
        check(f"T2.div_{tag}_observed",
              exp["chain"]["OBSERVED"]["status"] == "FACT")
        check(f"T2.div_{tag}_eligible_unknown",
              exp["chain"]["ELIGIBLE"]["status"] == "UNKNOWN")
        check(f"T2.div_{tag}_selected_unknown",
              exp["chain"]["SELECTED"]["status"] == "UNKNOWN")
        check(f"T2.div_{tag}_routable_unknown",
              exp["chain"]["ROUTABLE"]["status"] == "UNKNOWN")
    # Current absence is reported separately, not as erasure
    check("T2.div_a_current_absent",
          exp_a["current_stored"]["present"] is False)


def test_learned_temporal_separation():
    """C1-3: current learning must not masquerade as historical learning."""
    from form.mandell import duobeta_learn as dl
    p = fresh()
    kid = make_knowledge(p, "kie-learn", "learning knowledge about growth")
    # MIN_EVIDENCE=3 supporting outcomes required by the learn gate
    oids = [outcome_with_knowledge(p, kid) for _ in range(3)]
    oid = oids[-1]

    # Historical explanation BEFORE any learning
    exp0 = ki.explain_influence(p, kid, outcome_id=oid)
    check("T2.learn_hist_unknown_before",
          exp0["chain"]["LEARNED"]["status"] == "UNKNOWN")

    # Run the authorized learning lifecycle AFTER the outcome
    prop = dl.propose(p, "preference", 37, kid, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    if not g.get("accepted"):
        raise AssertionError(f"learn gate rejected: {g.get('reason')}")
    a = dl.apply_proposal(p, prop["proposal_id"])
    if not a.get("applied"):
        raise AssertionError(f"learn apply failed: {a.get('reason')}")

    # Historical explanation must STILL show UNKNOWN learned...
    exp1 = ki.explain_influence(p, kid, outcome_id=oid)
    check("T2.learn_hist_unknown_after",
          exp1["chain"]["LEARNED"]["status"] == "UNKNOWN")
    # ...while current learned state is reported separately as CURRENT
    cur = exp1.get("current_learned_state", {})
    check("T2.learn_current_labeled",
          cur.get("temporal_scope", "").startswith("CURRENT"))
    check("T2.learn_current_has_counts",
          isinstance(cur.get("detail"), dict))


def test_ekc_explicit_semantics():
    """D: test explicit-choice SEMANTICS, not merely FACT status.

    Explicit choice must select knowledge the context alone would not,
    and explanation must reflect the explicit source. Hard eligibility
    still applies: explicit choice cannot resurrect superseded knowledge.
    """
    p = fresh()
    kid = make_knowledge(p, "kie-ekc", "explicit choice knowledge")
    unrelated = "quantum xyzzy unrelated"

    # Without explicit: not selected for unrelated context
    sel_plain = ks.select_for_context(p, unrelated)
    plain_ids = [s["id"] for s in sel_plain["selected"]]
    check("T2.ekc_plain_not_selected", kid not in plain_ids)

    # With explicit: selected
    sel_exp = ks.select_for_context(p, unrelated, explicit_ids=[kid])
    exp_ids = [s["id"] for s in sel_exp["selected"]]
    check("T2.ekc_explicit_selected", kid in exp_ids)

    # Explanation reflects the explicit source
    exp = ki.explain_influence(p, kid, context=unrelated, explicit_ids=[kid])
    sel = exp["chain"]["SELECTED"]
    check("T2.ekc_explained_explicit",
          sel.get("selected") is True
          and "explicit" in sel.get("reason", "").lower())

    # Hard law: explicit choice cannot bypass supersession
    from form.mandell.supersession import supersede_proposal
    supersede_proposal(p, kid, "replacement words")
    sel_sup = ks.select_for_context(p, unrelated, explicit_ids=[kid])
    check("T2.ekc_no_bypass",
          kid not in [s["id"] for s in sel_sup["selected"]])


# ══════════════════════════════════════════════════════════════════
# T5: REPL dispatch (INTEGRATION — high-fidelity, NOT real-user-path)
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
    oid = outcome_with_knowledge(p, kid)
    out = _repl_dispatch(p, [f"why used {kid} in {oid}"])
    check("T5.why_used", "WHY WAS" in out and "USED" in out)


def test_repl_why_help():
    p = fresh()
    out = _repl_dispatch(p, ["why frobnicate"])
    check("T5.why_help", "why used" in out.lower())


# ══════════════════════════════════════════════════════════════════
# T6: REAL_USER_PATH — literal public entry: python3 -m form.repl
# ══════════════════════════════════════════════════════════════════

def test_real_user_path_repl_stdin():
    """REAL_USER_PATH: real OS process, real main()->run()->input() loop.

    Pipes a literal user command into `python3 -m form.repl` and verifies
    the KIC chain renders. The default-owner REPL loads persisted state;
    the assertion targets routing/rendering, not fixture knowledge.
    """
    cmd = "why influence nonexistent-id-xyz\n"
    result = subprocess.run(
        [sys.executable, "-m", "form.repl"],
        input=cmd, capture_output=True, text=True, cwd=".",
        env={**os.environ, "PYTHONPATH": "."},
        timeout=60,
    )
    out = result.stdout
    check("T6.real_path_exits", result.returncode == 0)
    check("T6.real_path_renders_chain",
          "STORED" in out and "ELIGIBLE" in out and "UNKNOWN" in out)


# ══════════════════════════════════════════════════════════════════
# T4: Cross-process (REAL subprocess, separate OS process)
# ══════════════════════════════════════════════════════════════════

def test_cross_process_explanation():
    """CROSS_PROCESS: explanation works after real subprocess restart."""
    script = '''
import sys
sys.path.insert(0, ".")
from form.open import Program
from form.mandell import knowledge_influence as ki

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
        test_isolation_proof,
        test_stored_fact,
        test_stored_unknown,
        test_eligible_positive_evidence,
        test_pending_not_eligible,
        test_off_plane_gate_live,
        test_superseded_not_eligible,
        test_dependency_blocked_not_eligible,
        test_selected_with_context,
        test_not_selected_wrong_context,
        test_historical_from_outcome,
        test_historical_unknown_outcome,
        test_why_used,
        test_why_not_used,
        test_no_causal_language,
        test_read_only,
        test_historical_not_rewritten,
        test_historical_without_current_storage,
        test_learned_temporal_separation,
        test_ekc_explicit_semantics,
        test_repl_why_influence,
        test_repl_why_not_used,
        test_repl_why_used,
        test_repl_why_help,
        test_real_user_path_repl_stdin,
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
