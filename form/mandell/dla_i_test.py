"""DLA-I: DuoBeta Learning Activation I — contract tests.

Tests the user-operable learning lifecycle wired in NBD-Ω-023:
  Outcome evidence → propose → inspect → gate → explicit authorize → apply
  → persistent learned state → ASI influence → observable explanation.

REALISM CLASSIFICATION:
  UNIT_SYNTHETIC: direct dl.* calls on fresh Program (contract proof)
  INTEGRATION: dl.* + outcome_ledger + knowledge_selector interaction;
               also _handle_learn_command handler tests (handler + duobeta_learn,
               but not the full run() dispatch loop)
  CROSS_PROCESS: save/load restart between lifecycle stages
  REAL_USER_PATH: full lifecycle through _repl_dispatch (same dispatch order
                  as run() loop: ROS → learn → execution)

Note: _handle_learn_command direct invocation proves handler integration.
True REAL_USER_PATH uses _repl_dispatch which replicates the run() loop's
exact dispatch order.

AUTONOMY=NO: apply requires explicit "confirm"; no auto-apply anywhere.
"""
import io
import os
import sys

sys.path.insert(0, ".")

from form.open import Program
from form.mandell import duobeta_learn as dl
from form.mandell.execution_observer import observe_seed_execution
from form.mandell import knowledge_selector as ks

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "state")

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


# ── Isolation: unique owner per call, emptiness VERIFIED (NBD-Ω-030) ──
_fresh_counter = [0]
_PID = os.getpid()
_CREATED_OWNERS = []


def fresh() -> Program:
    """Isolated Program: unique owner, nursery + learning ledger VERIFIED empty.

    Not "fresh" by name — fresh by verified precondition. Raises (fails loudly)
    if the nursery or learning ledger is not empty.

    Failure class closed (NBD-Ω-030): helper named fresh() + Program() !=
    proven isolated state. Program() (default owner) loads persisted ambient
    state; each call therefore mints a unique owner. Test-owner state files
    are removed at suite end (_teardown_isolated_owners); default/Ace state
    is never touched.
    """
    _fresh_counter[0] += 1
    owner = f"dla-i-isolated-{_PID}-{_fresh_counter[0]}"
    p = Program(owner=owner)
    if len(p.nursery.proposals) != 0:
        raise AssertionError(
            f"isolation violated: owner {owner} nursery has "
            f"{len(p.nursery.proposals)} proposals")
    if dl.learning_ledger(p):
        raise AssertionError(
            f"isolation violated: owner {owner} learning ledger not empty")
    _CREATED_OWNERS.append(owner)
    return p


def _teardown_isolated_owners() -> None:
    """Remove state files created for test owners. Never touches default state."""
    import pathlib
    for owner in _CREATED_OWNERS:
        for f in pathlib.Path(STATE_DIR).glob(f"*{owner}*"):
            try:
                if f.is_file():
                    f.unlink()
            except OSError:
                pass
    _CREATED_OWNERS.clear()


# ══════════════════════════════════════════════════════════════════
# T0: Isolation proof — mechanism-level fixture assertion (NBD-Ω-030)
# ══════════════════════════════════════════════════════════════════

def test_isolation_proof():
    """Prove the fixture's isolation contract before trusting results."""
    p1 = fresh()
    p2 = fresh()
    check("T0.distinct_owners", p1.owner != p2.owner)
    check("T0.p1_nursery_empty", len(p1.nursery.proposals) == 0)
    check("T0.p2_nursery_empty", len(p2.nursery.proposals) == 0)
    check("T0.p1_ledger_empty", dl.learning_ledger(p1) == [])
    check("T0.p2_ledger_empty", dl.learning_ledger(p2) == [])
    # Contamination in one must not leak into the other
    pr = p1.nursery.add("dla-iso-probe", words="isolation probe words")
    check("T0.no_cross_contamination", pr.id not in p2.nursery.proposals)
    # Control: prove the constructor LOADS persisted owner state — the exact
    # mechanism that falsified the old fresh()==Program() assumption.
    # Uses a throwaway owner; its state file is removed afterwards.
    # (Never touches the default/Ace owner state.)
    import pathlib
    from form.dell_matrix.nursery import owner_nursery_path
    cowner = f"dla-i-control-{_PID}"
    cpath = pathlib.Path(owner_nursery_path(cowner))
    if cpath.exists():
        cpath.unlink()
    pa = Program(owner=cowner)
    if len(pa.nursery.proposals) != 0:
        raise AssertionError("control setup: throwaway owner not empty")
    pra = pa.nursery.add("dla-control-k", words="control probe")
    pa.nursery.save()
    pb = Program(owner=cowner)  # must LOAD the saved proposal
    check("T0.constructor_loads_persisted", pra.id in pb.nursery.proposals)
    cpath.unlink(missing_ok=True)


def completed_oids(p, n=3, dell_seed="1[Keep]"):
    """Generate n completed outcomes via real execution.
    
    1[Keep] → dell=1, result=completed (verified).
    """
    oids = []
    for _ in range(n):
        observe_seed_execution(p, dell_seed)
        oids.append(list(p.outcome_records.values())[-1]["outcome_id"])
    return oids


def failed_oids(p, n=3):
    """Generate n failed outcomes via real execution."""
    oids = []
    for _ in range(n):
        observe_seed_execution(p, "86[Delete]")  # Dell 86 blocked → often failed
        rec = list(p.outcome_records.values())[-1]
        oids.append(rec["outcome_id"])
    return oids


# ══════════════════════════════════════════════════════════════════
# H. FAILURE SEMANTICS — UNIT_SYNTHETIC
# ══════════════════════════════════════════════════════════════════

def test_unknown_outcome_evidence():
    """Propose with nonexistent outcome IDs → gate rejects insufficient_evidence."""
    p = fresh()
    prop = dl.propose(p, "preference", 1, None, ["nope-1", "nope-2", "nope-3"])
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.unknown_outcome", g["accepted"] is False
          and g["reason"] == "insufficient_evidence")


def test_invalid_proposal_gate():
    """Gate with unknown proposal ID → ok=False, unknown_proposal."""
    p = fresh()
    g = dl.gate_proposal(p, 99999)
    check("H.invalid_proposal_gate", g["ok"] is False
          and g["reason"] == "unknown_proposal")


def test_invalid_proposal_apply():
    """Apply with unknown proposal ID → applied=False."""
    p = fresh()
    a = dl.apply_proposal(p, 99999)
    check("H.invalid_proposal_apply", a["applied"] is False
          and a["reason"] == "unknown_proposal")


def test_repl_learn_gate_malformed_no_crash():
    """CND-I: malformed learn gate input must not crash the REPL handler."""
    p = fresh()
    for cmd in ("learn gate", "learn gate abc", "learn gate 12x"):
        handled, out = _repl_learn(p, cmd)
        check(f"CND.malformed_gate_{cmd!r}_handled", handled is True)
        check(f"CND.malformed_gate_{cmd!r}_usage", "usage: learn gate" in out)


def test_repl_learn_apply_malformed_no_crash():
    """CND-I: malformed learn apply input must not crash the REPL handler."""
    p = fresh()
    for cmd in ("learn apply abc confirm", "learn apply 12x confirm"):
        handled, out = _repl_learn(p, cmd)
        check(f"CND.malformed_apply_{cmd!r}_handled", handled is True)
        check(f"CND.malformed_apply_{cmd!r}_usage", "usage: learn apply" in out)


def test_insufficient_evidence():
    """< MIN_EVIDENCE outcomes → gate rejects insufficient_evidence."""
    p = fresh()
    oids = completed_oids(p, n=2)  # only 2, need 3
    prop = dl.propose(p, "preference", 1, None, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.insufficient_evidence", g["accepted"] is False
          and g["reason"] == "insufficient_evidence")


def test_mismatched_result():
    """Preference kind with failed outcomes → gate rejects evidence_mismatch.
    
    REALISM: INTEGRATION (real execution via observe_seed_execution produces
    deterministic failed outcomes; gate semantics proven against real Outcome V1).
    """
    p = fresh()
    oids = failed_oids(p, n=3)
    # Verify precondition: we must have 3 failed outcomes for dell 86.
    # If this fails, the test FAILS (not vacuously passes).
    recs = [p.outcome_records[oid] for oid in oids]
    check("H.mismatched_precondition",
          all(r.get("result") == "failed" and r.get("dell") == 86 for r in recs))
    prop = dl.propose(p, "preference", 86, None, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.mismatched_result", g["accepted"] is False
          and g["reason"] == "evidence_mismatch")


def test_forbidden_kind():
    """Kind not in ALLOWED_KINDS → gate rejects forbidden_kind."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "mind_control", 37, None, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.forbidden_kind", g["accepted"] is False
          and g["reason"] == "forbidden_kind")


def test_invalid_dell_zero():
    """Dell 0 → gate rejects out_of_scope."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 0, None, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.invalid_dell_zero", g["accepted"] is False
          and g["reason"] == "out_of_scope")


def test_invalid_dell_100():
    """Dell 100 → gate rejects out_of_scope."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 100, None, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.invalid_dell_100", g["accepted"] is False
          and g["reason"] == "out_of_scope")


def test_invalid_knowledge_provenance():
    """knowledge_id not in evidence → gate rejects evidence_mismatch."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, "fake-knowledge-id", oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.invalid_knowledge", g["accepted"] is False
          and g["reason"] == "evidence_mismatch")


def test_duplicate_application():
    """Apply same proposal twice → second apply fails (not_accepted)."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    pid = prop["proposal_id"]
    g = dl.gate_proposal(p, pid)
    check("H.dup_gate", g["accepted"] is True)
    a1 = dl.apply_proposal(p, pid)
    check("H.dup_first_apply", a1["applied"] is True)
    a2 = dl.apply_proposal(p, pid)
    check("H.dup_second_apply", a2["applied"] is False
          and "not_accepted" in a2["reason"])


def test_duplicate_proposal_rejected():
    """Second proposal for same (kind,dell,kid) after APPLY → gate rejects duplicate."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop1 = dl.propose(p, "preference", 1, None, oids)
    dl.gate_proposal(p, prop1["proposal_id"])
    dl.apply_proposal(p, prop1["proposal_id"])
    # Second proposal for same target
    prop2 = dl.propose(p, "preference", 1, None, oids)
    g2 = dl.gate_proposal(p, prop2["proposal_id"])
    check("H.duplicate_proposal", g2["accepted"] is False
          and g2["reason"] == "duplicate")


def test_rejected_gate_persists():
    """REJECTED status persists with reason (not silently dropped)."""
    p = fresh()
    prop = dl.propose(p, "preference", 1, None, ["bad-1"])
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("H.rejected", g["accepted"] is False)
    stored = dl.get_proposal(p, prop["proposal_id"])
    check("H.rejected_persists", stored["status"] == "REJECTED"
          and stored["reason"] == g["reason"])


def test_apply_without_accepted_gate():
    """Apply on PROPOSED (not gated) → fails not_accepted."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    a = dl.apply_proposal(p, prop["proposal_id"])
    check("H.apply_without_gate", a["applied"] is False
          and "not_accepted" in a["reason"])


def test_apply_rejected_proposal():
    """Apply on REJECTED → fails not_accepted."""
    p = fresh()
    prop = dl.propose(p, "preference", 1, None, ["bad-1"])
    dl.gate_proposal(p, prop["proposal_id"])  # rejects
    a = dl.apply_proposal(p, prop["proposal_id"])
    check("H.apply_rejected", a["applied"] is False
          and "not_accepted" in a["reason"])


# ══════════════════════════════════════════════════════════════════
# D. USER CONTROL — REPL handler (INTEGRATION)
#
# These test _handle_learn_command directly (handler + duobeta_learn).
# Classified INTEGRATION, not REAL_USER_PATH (see K.* for dispatch-level proof).
# ══════════════════════════════════════════════════════════════════

def _repl_learn(p, cmd):
    """Run a learn command through the REPL handler, capture output."""
    from form import repl as repl_mod
    buf = io.StringIO()
    old_say = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        handled = repl_mod._handle_learn_command(p, cmd)
    finally:
        repl_mod._say = old_say
    return handled, buf.getvalue()


def test_repl_propose():
    """learn propose stages a proposal."""
    p = fresh()
    oids = completed_oids(p, n=3)
    handled, out = _repl_learn(p, f"learn propose preference 1 from {' '.join(oids)}")
    check("D.repl_propose_handled", handled is True)
    check("D.repl_propose_staged", "PROPOSED" in out and "not yet gated" in out)


def test_repl_propose_usage():
    """learn propose with bad syntax → usage message."""
    p = fresh()
    handled, out = _repl_learn(p, "learn propose preference")
    check("D.repl_propose_usage", handled is True and "usage:" in out)


def test_repl_inspect():
    """learn inspect shows proposal details."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    handled, out = _repl_learn(p, f"learn inspect {prop['proposal_id']}")
    check("D.repl_inspect", handled is True
          and str(prop["proposal_id"]) in out and "PROPOSED" in out)


def test_repl_inspect_unknown():
    """learn inspect unknown ID → clear message."""
    p = fresh()
    handled, out = _repl_learn(p, "learn inspect 99999")
    check("D.repl_inspect_unknown", handled is True and "unknown proposal" in out)


def test_repl_gate_accept():
    """learn gate runs gate and reports ACCEPTED."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    handled, out = _repl_learn(p, f"learn gate {prop['proposal_id']}")
    check("D.repl_gate", handled is True and "GATE ACCEPTED" in out)


def test_repl_gate_reject():
    """learn gate reports REJECTED with reason."""
    p = fresh()
    prop = dl.propose(p, "preference", 1, None, ["bad-1"])
    handled, out = _repl_learn(p, f"learn gate {prop['proposal_id']}")
    check("D.repl_gate_reject", handled is True and "GATE REJECTED" in out)


def test_repl_apply_requires_confirm():
    """learn apply WITHOUT confirm → requires explicit authorization, does NOT apply."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    pid = prop["proposal_id"]
    dl.gate_proposal(p, pid)  # ACCEPTED
    handled, out = _repl_learn(p, f"learn apply {pid}")
    check("D.repl_apply_no_confirm_handled", handled is True)
    check("D.repl_apply_no_confirm_msg", "explicit authorization required" in out)
    # Verify NOT applied
    stored = dl.get_proposal(p, pid)
    check("D.repl_apply_no_confirm_noop", stored["status"] == "ACCEPTED")  # not APPLIED


def test_repl_apply_with_confirm():
    """learn apply <pid> confirm → applies."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    pid = prop["proposal_id"]
    dl.gate_proposal(p, pid)
    handled, out = _repl_learn(p, f"learn apply {pid} confirm")
    check("D.repl_apply_confirm", handled is True and "APPLIED" in out)
    stored = dl.get_proposal(p, pid)
    check("D.repl_apply_confirm_state", stored["status"] == "APPLIED")


def test_repl_apply_confirm_rejected():
    """learn apply <pid> confirm on REJECTED → not applied."""
    p = fresh()
    prop = dl.propose(p, "preference", 1, None, ["bad-1"])
    pid = prop["proposal_id"]
    dl.gate_proposal(p, pid)  # REJECTED
    handled, out = _repl_learn(p, f"learn apply {pid} confirm")
    check("D.repl_apply_confirm_rejected", handled is True and "not applied" in out)


def test_repl_ledger():
    """learn ledger shows learned state."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    dl.gate_proposal(p, prop["proposal_id"])
    dl.apply_proposal(p, prop["proposal_id"])
    handled, out = _repl_learn(p, "learn ledger")
    check("D.repl_ledger", handled is True and "APPLIED" in out)


def test_repl_ledger_empty():
    """learn ledger on fresh program → empty message."""
    p = fresh()
    handled, out = _repl_learn(p, "learn ledger")
    check("D.repl_ledger_empty", handled is True and "empty" in out)


def test_repl_unknown_subcommand():
    """learn <unknown> → help message."""
    p = fresh()
    handled, out = _repl_learn(p, "learn frobnicate")
    check("D.repl_unknown", handled is True and "learn propose" in out)


def test_repl_not_learn_command():
    """Non-learn commands return False (not handled)."""
    p = fresh()
    from form import repl as repl_mod
    check("D.repl_passthrough", repl_mod._handle_learn_command(p, "learned") is False)
    check("D.repl_passthrough2", repl_mod._handle_learn_command(p, "health") is False)


# ══════════════════════════════════════════════════════════════════
# K. REAL USER PATH — full lifecycle through actual REPL dispatch
# ══════════════════════════════════════════════════════════════════

def _repl_dispatch(p, commands):
    """Simulate the actual REPL dispatch loop from run().
    
    Feeds commands through the same dispatch logic as the interactive
    run() loop: ROS handler → learn handler → (execution path).
    This is the strongest practical REAL_USER_PATH proof short of
    mocking builtin input() for the full run() function.
    
    Returns captured output.
    """
    from form import repl as repl_mod
    buf = io.StringIO()
    old_say = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        for line in commands:
            line = line.strip()
            if not line:
                continue
            # Exact dispatch order from run(): ROS → learn → execution
            if repl_mod._handle_ros_command(p, line):
                continue
            if repl_mod._handle_learn_command(p, line):
                continue
            # (execution path not needed for learn commands)
    finally:
        repl_mod._say = old_say
    return buf.getvalue()


def test_real_user_path_full_lifecycle():
    """REAL_USER_PATH: propose → inspect → gate → apply (confirm) → ledger,
    all through REPL dispatch (same order as run() loop)."""
    p = fresh()
    oids = completed_oids(p, n=3)
    oid_str = " ".join(oids)

    # Stage proposal via dispatch, capture ID from output
    out1 = _repl_dispatch(p, [f"learn propose preference 1 from {oid_str}"])
    assert "PROPOSED" in out1, f"propose failed: {out1}"
    import re
    m = re.search(r"proposal (\d+) staged", out1)
    assert m, f"no proposal ID in: {out1}"
    pid = m.group(1)
    # Proposal actually staged in ledger (not just printed)
    stored = dl.get_proposal(p, pid)
    check("K.propose", stored is not None and stored["status"] == "PROPOSED")

    # Inspect via dispatch
    out2 = _repl_dispatch(p, [f"learn inspect {pid}"])
    check("K.inspect", "PROPOSED" in out2)

    # Gate via dispatch
    out3 = _repl_dispatch(p, [f"learn gate {pid}"])
    check("K.gate", "GATE ACCEPTED" in out3)

    # Apply without confirm → blocked (AUTONOMY=NO)
    out4 = _repl_dispatch(p, [f"learn apply {pid}"])
    check("K.apply_blocked", "explicit authorization required" in out4)
    # Verify state unchanged
    stored = dl.get_proposal(p, pid)
    check("K.apply_blocked_state", stored["status"] == "ACCEPTED")

    # Apply with confirm → applied
    out5 = _repl_dispatch(p, [f"learn apply {pid} confirm"])
    check("K.apply", "APPLIED" in out5)
    stored = dl.get_proposal(p, pid)
    check("K.apply_state", stored["status"] == "APPLIED")

    # Ledger shows it
    out6 = _repl_dispatch(p, ["learn ledger"])
    check("K.ledger", "APPLIED" in out6)

    # ASI consumes it (existing path, unmodified)
    score = dl.bounded_learned_score(p, 1, None)
    check("K.asi_consumes", score > 0)


def test_real_user_path_rejection():
    """REAL_USER_PATH: rejection path through REPL dispatch."""
    p = fresh()
    out1 = _repl_dispatch(p, ["learn propose preference 1 from bad-oid-1 bad-oid-2"])
    import re
    m = re.search(r"proposal (\d+) staged", out1)
    assert m, f"no proposal ID in: {out1}"
    pid = m.group(1)
    check("K.rej_propose", "PROPOSED" in out1)

    out2 = _repl_dispatch(p, [f"learn gate {pid}"])
    check("K.rej_gate", "GATE REJECTED" in out2)

    out3 = _repl_dispatch(p, [f"learn apply {pid} confirm"])
    check("K.rej_apply", "not applied" in out3)


# ══════════════════════════════════════════════════════════════════
# I. PERSISTENCE — CROSS_PROCESS
# ══════════════════════════════════════════════════════════════════

def test_persistence_across_restart():
    """CROSS_PROCESS: APPLIED learning survives save/load."""
    import tempfile, os
    p = fresh()
    p.owner = "dla_test_owner"
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    pid = prop["proposal_id"]
    dl.gate_proposal(p, pid)
    dl.apply_proposal(p, pid)

    # Save
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "dla_test.dell")
        p.save(path)
        # Load into new Program (load returns new instance; path is kwarg)
        p2 = Program.load(path=path)
        stored = dl.get_proposal(p2, pid)
        check("I.persist_applied", stored is not None
              and stored["status"] == "APPLIED")
        # Verify ASI can consume it
        idx = dl.preference_index(p2)
        check("I.persist_index", len(idx) > 0)


def test_persistence_proposed_stage():
    """CROSS_PROCESS: PROPOSED (not yet gated) survives save/load."""
    import tempfile, os
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    pid = prop["proposal_id"]

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "dla_test2.dell")
        p.save(path)
        p2 = Program.load(path=path)
        stored = dl.get_proposal(p2, pid)
        check("I.persist_proposed", stored is not None
              and stored["status"] == "PROPOSED")
        # Can still gate after restart
        g = dl.gate_proposal(p2, pid)
        check("I.persist_gate_after", g["accepted"] is True)


# ══════════════════════════════════════════════════════════════════
# G. ASI/AEC INVARIANCE — INTEGRATION
# ══════════════════════════════════════════════════════════════════

def test_asi_consumes_applied_learning():
    """INTEGRATION: APPLIED learning influences ASI scoring via existing path."""
    p = fresh()
    oids = completed_oids(p, n=3)
    prop = dl.propose(p, "preference", 1, None, oids)
    pid = prop["proposal_id"]
    dl.gate_proposal(p, pid)
    dl.apply_proposal(p, pid)

    # ASI should now see learned evidence for Dell 37
    score = dl.bounded_learned_score(p, 1, None)
    check("G.asi_score", score > 0)


def test_no_asi_semantics_change():
    """INTEGRATION: saturation transform still applied (AEC-I preserved)."""
    p = fresh()
    oids = completed_oids(p, n=10)
    prop = dl.propose(p, "preference", 1, None, oids)
    dl.gate_proposal(p, prop["proposal_id"])
    dl.apply_proposal(p, prop["proposal_id"])
    score = dl.bounded_learned_score(p, 1, None)
    # AEC-I: saturate(raw) = raw*100/(100+|raw|), must be < 100
    check("G.aec_bound", 0 < score < 100)


# ══════════════════════════════════════════════════════════════════
# F. ODCG SEPARATION
# ══════════════════════════════════════════════════════════════════

def test_no_odcg_bridge():
    """ODCG candidates do not automatically become learning evidence."""
    p = fresh()
    # Create a failed outcome then a completed one (ODCG would link them)
    observe_seed_execution(p, "86[Delete]")
    failed_oid = list(p.outcome_records.values())[-1]["outcome_id"]
    oids = completed_oids(p, n=3)
    # Propose using ONLY the completed outcomes — the failed one is not auto-included
    prop = dl.propose(p, "preference", 1, None, oids)
    stored = dl.get_proposal(p, prop["proposal_id"])
    check("F.no_odcg_bridge", failed_oid not in stored["evidence_outcome_ids"])


# ══════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════

def main():
    tests = [
        # T0: isolation proof (fixture contract first)
        test_isolation_proof,
        # H: failure semantics
        test_unknown_outcome_evidence,
        test_invalid_proposal_gate,
        test_invalid_proposal_apply,
        test_repl_learn_gate_malformed_no_crash,
        test_repl_learn_apply_malformed_no_crash,
        test_insufficient_evidence,
        test_mismatched_result,
        test_forbidden_kind,
        test_invalid_dell_zero,
        test_invalid_dell_100,
        test_invalid_knowledge_provenance,
        test_duplicate_application,
        test_duplicate_proposal_rejected,
        test_rejected_gate_persists,
        test_apply_without_accepted_gate,
        test_apply_rejected_proposal,
        # D: user control
        test_repl_propose,
        test_repl_propose_usage,
        test_repl_inspect,
        test_repl_inspect_unknown,
        test_repl_gate_accept,
        test_repl_gate_reject,
        test_repl_apply_requires_confirm,
        test_repl_apply_with_confirm,
        test_repl_apply_confirm_rejected,
        test_repl_ledger,
        test_repl_ledger_empty,
        test_repl_unknown_subcommand,
        test_repl_not_learn_command,
        # K: real user path
        test_real_user_path_full_lifecycle,
        test_real_user_path_rejection,
        # I: persistence
        test_persistence_across_restart,
        test_persistence_proposed_stage,
        # G: ASI/AEC invariance
        test_asi_consumes_applied_learning,
        test_no_asi_semantics_change,
        # F: ODCG separation
        test_no_odcg_bridge,
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
    print(f"\nDLA-I: {_passed}/{total} {'GREEN' if _failed == 0 else 'RED'}")
    if _failures:
        print("Failures:")
        for f in _failures:
            print(f"  - {f}")
    return 0 if _failed == 0 else 1


def smoke() -> bool:
    """Entry point for regress.py (expects smoke() -> bool)."""
    global _passed, _failed, _failures
    _passed = 0
    _failed = 0
    _failures = []
    try:
        main()
    finally:
        _teardown_isolated_owners()
    return _failed == 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        _teardown_isolated_owners()
