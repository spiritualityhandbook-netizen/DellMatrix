#!/usr/bin/env python3
"""ASI-I: Adaptive Selection Integration — dedicated control suite (NBD-Ω-008).

Closes the production learning loop: accepted DuoBeta learning connects to
the EXISTING canonical knowledge selection authority as a bounded advisory
signal.

LAW: Learning reorders eligible candidates. It never resurrects ineligible
ones. AUTONOMY = NO.

Controls:
  A  cold-start parity (no learning → exactly baseline)
  B  positive production adaptation (B moves up via real 37 path)
  C  negative bounded adaptation (moves down, never removed)
  D  superseded dominance (hard law wins)
  E  dependency dominance (hard law wins)
  F  relevance dominance (hard law wins)
  G  conflict dominance (hard law wins)
  H  disposition dominance (hard law wins)
  I  explicit intent (N/A — no such mechanism; verified)
  J  single-candidate no-op
  K  rejected-learning no-op
  L  insufficient-evidence no-op
  M  deterministic repeated run
  N  save/load persistence
  O  fresh-process persistence
  P  checkpoint (Generation V1) persistence
  Q  feedback loop (Selection0→Outcome0→learn→Selection1→Outcome1)
  R  no double counting (duplicate rejected)
  S  ROS inspection (read-only observability)
  T  AUTONOMY=NO (static)
  U  no selector duplication (static)
"""
from __future__ import annotations

import os
import subprocess
import sys
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from form.open import Program  # noqa: E402
from form.mandell import duobeta_learn as dl  # noqa: E402
from form.mandell.knowledge_selector import select_for_context  # noqa: E402


def _score_eq(actual, expected_raw, tol=1e-9):
    """AEC-I: compare learned score against saturated expected value."""
    return abs(actual - dl.saturate_learned_score(expected_raw)) < tol
from form.mandell.translate import translate  # noqa: E402
from form.mandell.semantic_router import route_intent  # noqa: E402
from form.mandell.execution_observer import observe_seed_execution  # noqa: E402

CHECKS = []
STATE_DIR = os.path.join(REPO, "form", "state")


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")


# ── Isolation: unique owner per call, emptiness VERIFIED (NBD-Ω-030) ──
# Failure class closed: helper named fresh() + Program() != proven isolated
# state. Program() (default owner) loads persisted ambient state. An explicit
# owner is honored (tests N/O/P); otherwise each call mints a unique owner.
# Nursery and learning ledger are VERIFIED empty — fails loudly otherwise.
# Test-owner state files are removed at suite end (_teardown_isolated_owners);
# default/Ace state is never touched.
_fresh_counter = [0]
_PID = os.getpid()
_CREATED_OWNERS = []


def fresh(owner: str | None = None) -> Program:
    """Isolated Program: unique (or given) owner, emptiness VERIFIED.

    Not "fresh" by name — fresh by verified precondition. Raises (fails loudly)
    if the nursery or learning ledger is not empty.
    """
    _fresh_counter[0] += 1
    if not owner:
        owner = f"asi-i-isolated-{_PID}-{_fresh_counter[0]}"
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


# ── T0: Isolation proof — mechanism-level fixture assertion (NBD-Ω-030) ──
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
    pr = p1.nursery.add("asi-iso-probe", words="isolation probe words")
    check("T0.no_cross_contamination", pr.id not in p2.nursery.proposals)
    # Control: prove the constructor LOADS persisted owner state — the exact
    # mechanism that falsified the old fresh()==Program() assumption.
    # Uses a throwaway owner; its state file is removed afterwards.
    import pathlib
    from form.dell_matrix.nursery import owner_nursery_path
    cowner = f"asi-i-control-{_PID}"
    cpath = pathlib.Path(owner_nursery_path(cowner))
    if cpath.exists():
        cpath.unlink()
    pa = Program(owner=cowner)
    if len(pa.nursery.proposals) != 0:
        raise AssertionError("control setup: throwaway owner not empty")
    pra = pa.nursery.add("asi-control-k", words="control probe")
    pa.nursery.save()
    pb = Program(owner=cowner)  # must LOAD the saved proposal
    check("T0.constructor_loads_persisted", pra.id in pb.nursery.proposals)
    cpath.unlink(missing_ok=True)


def wipe_owner(owner: str) -> None:
    import pathlib
    for f in pathlib.Path(STATE_DIR).glob(f"*{owner}*"):
        try:
            if f.is_file():
                f.unlink()
        except OSError:
            pass


def confirm(p: Program, label: str, words: str, parents=None) -> str:
    pr = p.nursery.add(label, words=words, parents=parents or [])
    p.confirm_proposal(pr.id)
    return pr.id


def ctx_grow(p: Program, context: str) -> str:
    """Run the REAL production 37 contextual path. Returns outcome_id."""
    route_intent(p, translate(f"grow using knowledge about {context}"),
                 raw_line="x")
    return list(p.outcome_records.values())[-1]["outcome_id"]


def learn_preference(p: Program, kid: str, context: str, n: int = 3):
    """Full honest DBEL-I cycle: n real 37 executions → propose → gate → apply."""
    oids = [ctx_grow(p, context) for _ in range(n)]
    prop = dl.propose(p, "preference", 37, kid, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    a = dl.apply_proposal(p, prop["proposal_id"]) if g["accepted"] else {"applied": False}
    return oids, prop, g, a


def sel_ids(p: Program, context: str):
    s = select_for_context(p, context, operation="grow")
    return [x["id"] for x in s["selected"]], s


# ── A: cold-start parity ────────────────────────────────────────────
def test_a():
    p = fresh()
    aid = confirm(p, "a_cold", "alpha beta gamma delta")
    bid = confirm(p, "b_cold", "alpha zeta")
    ids, s = sel_ids(p, "alpha beta")
    check("A.baseline_order", ids == [aid, bid])
    check("A.parity", s["baseline_selected_ids"] == s["learned_selected_ids"])
    check("A.not_applied", s["learned_preference_applied"] is False)
    check("A.zero_scores", all(v == 0 for v in s["learned_scores"].values()))


# ── B: positive production adaptation ─────────────────────────────
def test_b():
    p = fresh()
    aid = confirm(p, "a_pos", "alpha beta gamma delta")
    bid = confirm(p, "b_pos", "alpha zeta")
    ids0, _ = sel_ids(p, "alpha beta")
    check("B.baseline", ids0 == [aid, bid])

    oids, prop, g, a = learn_preference(p, bid, "alpha beta", 3)
    check("B.gate_accept", g["accepted"] is True)
    check("B.applied", a["applied"] is True)
    # Outcomes were real: completed, dell 37, B in knowledge
    rec0 = list(p.outcome_records.values())[0]
    # (outcome_records is keyed; find by oids)
    for oid in oids:
        r = p.outcome_records.get(oid) or next(
            (v for v in p.outcome_records.values()
             if v.get("outcome_id") == oid), None)
        check("B.outcome_completed", r and r.get("result") == "completed"
              and r.get("dell") == 37)

    ids1, s1 = sel_ids(p, "alpha beta")
    check("B.moved_up", ids1 == [bid, aid])
    check("B.applied_flag", s1["learned_preference_applied"] is True)
    check("B.score", _score_eq(s1["learned_scores"][bid], 3)
          and s1["learned_scores"][aid] == 0.0)
    check("B.baseline_preserved", s1["baseline_selected_ids"] == [aid, bid])

    # Execution after learning → Outcome V1 (production path, not suggest_preferred)
    oid_after = ctx_grow(p, "alpha beta")
    r_after = next((v for v in p.outcome_records.values()
                    if v.get("outcome_id") == oid_after), None)
    check("B.outcome_after", r_after is not None
          and r_after.get("result") == "completed")
    # The production receipt reflects the learned order
    nur = p.last_nurture or {}
    check("B.receipt_order", (nur.get("selected_ids") or [])[:2] == [bid, aid])


# ── C: negative bounded adaptation ─────────────────────────────────
def test_c():
    # C1: honest full-cycle avoidance (mechanism proof, Dell 86)
    p = fresh()
    oids = []
    for _ in range(3):
        observe_seed_execution(p, "86[Delete]")
        oids.append(list(p.outcome_records.values())[-1]["outcome_id"])
    prop = dl.propose(p, "avoidance", 86, None, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    a = dl.apply_proposal(p, prop["proposal_id"]) if g["accepted"] else {}
    check("C.avoidance_cycle", g["accepted"] is True and a.get("applied") is True)
    check("C.negative_score", dl.bounded_learned_score(p, 86, None) < 0)

    # C2: selection integration — D moves down but REMAINS
    p2 = fresh()
    cid = confirm(p2, "c_neg", "alpha beta gamma delta")
    did = confirm(p2, "d_neg", "alpha zeta")
    ids0, _ = sel_ids(p2, "alpha beta")
    check("C.baseline", ids0 == [cid, did])
    # APPLIED avoidance for (37, did): test setup via structured ledger
    # entry (gate already proven by C1/DBEL-I; this tests SELECTION).
    dl._append_learn_entry(
        p2, "LEARN APPLIED avoidance dell=37 (test setup)",
        {"kind": "learn", "proposal_kind": "avoidance", "dell": 37,
         "knowledge_id": did, "status": "APPLIED",
         "evidence": {"outcome_ids": ["t1", "t2", "t3"],
                      "supporting": ["t1", "t2", "t3"]},
         "gate": {"accepted": True}, "reason": "test",
         "proposed_ts": "t", "applied_ts": "t"})
    ids1, s1 = sel_ids(p2, "alpha beta")
    check("C.moved_down", ids1 == [cid, did])
    check("C.still_selected", did in ids1)
    check("C.negative_bounded", _score_eq(s1["learned_scores"][did], -3))
    # C3: D is NOT false/invalid/conflicted/deleted
    check("C.still_confirmed", p2.nursery.proposals[did].status == "confirmed")
    check("C.on_plane", did in p2.cube.session.plane.units)
    check("C.not_quarantined", did not in
          (getattr(p2, "last_nurture", None) or {}).get("quarantined_ids", []))
    # C4: bound holds (clamp)
    check("C.cap", abs(dl.bounded_learned_score(p2, 37, did)) <= dl.ASI_LEARNED_CAP)


# ── D: superseded dominance ────────────────────────────────────────
def test_d():
    p = fresh()
    aid = confirm(p, "a_sup", "alpha beta gamma delta")
    bid = confirm(p, "b_sup", "alpha zeta")
    _, _, g, a = learn_preference(p, bid, "alpha beta", 3)
    check("D.learned", g["accepted"] and a["applied"])
    # Supersede B (preferred but superseded → hard law wins)
    r = route_intent(p, translate(f"supersede idea {bid} with alpha zeta theta"))
    check("D.superseded", r.ok is True)
    ids, s = sel_ids(p, "alpha beta")
    check("D.excluded", bid not in ids)
    check("D.a_selected", aid in ids)
    check("D.evidence", bid in [e.get("id") for e in
                                s.get("supersession_exclusions", [])])


# ── E: dependency dominance ────────────────────────────────────────
def test_e():
    p = fresh()
    aid = confirm(p, "a_dep", "alpha beta gamma")
    bid = confirm(p, "b_dep", "alpha beta", parents=[aid])
    ids0, _ = sel_ids(p, "alpha beta")
    check("E.both_eligible", aid in ids0 and bid in ids0)
    _, _, g, a = learn_preference(p, bid, "alpha beta", 3)
    check("E.learned", g["accepted"] and a["applied"])
    # Invalidate B's dependency (remove parent from plane)
    check("E.removed", p.cube.session.plane.remove(aid) is True)
    ids, s = sel_ids(p, "alpha beta")
    check("E.excluded", bid not in ids)
    check("E.evidence", bid in [e.get("id") for e in
                                s.get("dependency_exclusions", [])])


# ── F: relevance dominance ─────────────────────────────────────────
def test_f():
    p = fresh()
    aid = confirm(p, "a_rel", "alpha beta gamma delta")
    # C is eligible but irrelevant to "alpha beta" (no token overlap)
    cid = confirm(p, "c_rel", "quantum xylophone zebra")
    # Learn preference for C via a context where C IS relevant
    _, _, g, a = learn_preference(p, cid, "quantum xylophone", 3)
    check("F.learned", g["accepted"] and a["applied"])
    check("F.score", _score_eq(dl.bounded_learned_score(p, 37, cid), 3))
    # Select for "alpha beta": C must NOT appear (irrelevant despite +3)
    ids, s = sel_ids(p, "alpha beta")
    check("F.excluded", cid not in ids)
    check("F.a_selected", aid in ids)


# ── G: conflict dominance ──────────────────────────────────────────
def test_g():
    p = fresh()
    aid = confirm(p, "a_con", "plants need bright light")
    bid = confirm(p, "b_con", "rivers need steady rain yearly")
    # Learn preference for B (no conflict yet)
    _, _, g, a = learn_preference(p, bid, "rivers steady rain", 3)
    check("G.learned", g["accepted"] and a["applied"])
    # Create C that polarity-conflicts with B
    cid = confirm(p, "c_con", "rivers do not need steady rain yearly")
    ids, s = sel_ids(p, "rivers steady rain")
    check("G.b_first_learned", ids[0] == bid)  # learned order before filter
    # Production path: conflict detection quarantines despite +3
    ctx_grow(p, "rivers steady rain")
    nur = getattr(p, "last_nurture", None) or {}
    check("G.conflict_found", (nur.get("conflict_count") or 0) >= 1)
    check("G.b_quarantined", bid in (nur.get("quarantined_ids") or []))
    check("G.not_routable", bid not in (nur.get("routable_selected_ids") or []))


# ── H: disposition dominance ───────────────────────────────────────
def test_h():
    from form.mandell.conflict_router import detect_conflicts
    from form.mandell.conflict_disposition import (
        set_disposition, conflict_id_for)
    from form.mandell.knowledge_selector import unit_text
    p = fresh()
    bid = confirm(p, "b_dis", "rivers need steady rain yearly")
    # Learn preference for B (+3)
    _, _, g, a = learn_preference(p, bid, "rivers steady rain", 3)
    check("H.learned", g["accepted"] and a["applied"])
    # Create C that conflicts with B
    cid = confirm(p, "c_dis", "rivers do not need steady rain yearly")
    ids, _ = sel_ids(p, "rivers steady rain")
    items = [{"id": i, "text": unit_text(p, i)} for i in ids]
    conflicts = detect_conflicts(items)
    check("H.conflict", len(conflicts) >= 1)
    c0 = conflicts[0]
    cid_conflict = conflict_id_for(c0["id_a"], c0["id_b"])
    # Explicit operator disposition: prefer C over B
    dr = set_disposition(p, cid_conflict, "prefer", preferred_ids=[cid],
                         operator_reason="test")
    check("H.disposition_set", dr.get("ok") is True)
    ctx_grow(p, "rivers steady rain")
    nur = getattr(p, "last_nurture", None) or {}
    routable = nur.get("routable_selected_ids") or []
    # Disposition wins: C routable, B (preferred by learning) not
    check("H.c_routable", cid in routable)
    check("H.b_not_routable", bid not in routable)


# ── I: explicit intent (N/A — verified absent) ────────────────────
def test_i():
    import pathlib
    # No explicit knowledge-choice / exact-ID selection mechanism exists.
    # The contextual selector is the only production path. We verify this
    # structurally rather than inventing a mechanism for the test.
    found = []
    for f in pathlib.Path(REPO, "form", "mandell").glob("*.py"):
        if f.name.endswith("_test.py"):
            continue
        if "def select_for_context" in f.read_text():
            found.append(f.name)
    check("I.single_selector", found == ["knowledge_selector.py"])
    core_ops = pathlib.Path(REPO, "form", "mandell", "core_i_ops.py").read_text()
    check("I.no_id_grow", "grow_using_knowledge_id" not in core_ops)


# ── J: single-candidate no-op ──────────────────────────────────────
def test_j():
    p = fresh()
    aid = confirm(p, "a_single", "alpha beta gamma")
    _, _, g, a = learn_preference(p, aid, "alpha beta", 3)
    check("J.learned", g["accepted"] and a["applied"])
    ids, s = sel_ids(p, "alpha beta")
    check("J.single", ids == [aid])
    check("J.noop", s["baseline_selected_ids"] == s["learned_selected_ids"])


# ── K/L: rejected / insufficient-evidence no-op ────────────────────
def test_k():
    p = fresh()
    aid = confirm(p, "a_rej", "alpha beta gamma delta")
    bid = confirm(p, "b_rej", "alpha zeta")
    ids0, _ = sel_ids(p, "alpha beta")
    # Only 2 outcomes (< MIN_EVIDENCE=3) → gate rejects
    oids = [ctx_grow(p, "alpha beta") for _ in range(2)]
    prop = dl.propose(p, "preference", 37, bid, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    check("K.rejected", g["accepted"] is False)
    check("K.reason", "insufficient" in (g.get("reason") or ""))
    check("K.status", dl.get_proposal(p, prop["proposal_id"])["status"] == "REJECTED")
    ids1, s1 = sel_ids(p, "alpha beta")
    check("K.noop", ids1 == ids0 == [aid, bid])
    check("K.not_applied", s1["learned_preference_applied"] is False)


# ── M: deterministic repeated run ──────────────────────────────────
def test_m():
    p = fresh()
    aid = confirm(p, "a_det", "alpha beta gamma delta")
    bid = confirm(p, "b_det", "alpha zeta")
    cid = confirm(p, "c_det", "alpha beta")
    learn_preference(p, bid, "alpha beta", 3)
    r1, _ = sel_ids(p, "alpha beta")
    r2, _ = sel_ids(p, "alpha beta")
    r3, _ = sel_ids(p, "alpha beta")
    check("M.repeat", r1 == r2 == r3)
    check("M.learned_order", r1[0] == bid)


# ── N: save/load ───────────────────────────────────────────────────
def test_n():
    owner = f"asi_n_{uuid.uuid4().hex[:8]}"
    p = fresh(owner)
    aid = confirm(p, "a_save", "alpha beta gamma delta")
    bid = confirm(p, "b_save", "alpha zeta")
    learn_preference(p, bid, "alpha beta", 3)
    ids0, _ = sel_ids(p, "alpha beta")
    path = p.save()
    check("N.saved", bool(path))
    p2 = Program.load(owner)
    ids1, s1 = sel_ids(p2, "alpha beta")
    check("N.order", ids1 == ids0 == [bid, aid])
    check("N.scores", _score_eq(s1["learned_scores"][bid], 3))
    wipe_owner(owner)


# ── O: fresh process ───────────────────────────────────────────────
def test_o():
    owner = f"asi_o_{uuid.uuid4().hex[:8]}"
    p = fresh(owner)
    aid = confirm(p, "a_proc", "alpha beta gamma delta")
    bid = confirm(p, "b_proc", "alpha zeta")
    learn_preference(p, bid, "alpha beta", 3)
    ids0, _ = sel_ids(p, "alpha beta")
    p.save()
    code = (
        "import sys; sys.path.insert(0, %r); "
        "from form.open import Program; "
        "from form.mandell.knowledge_selector import select_for_context; "
        "p = Program.load(%r); "
        "s = select_for_context(p, 'alpha beta', operation='grow'); "
        "print(','.join(x['id'] for x in s['selected']))"
        % (REPO, owner)
    )
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=120)
    check("O.proc_ok", r.returncode == 0)
    ids_proc = r.stdout.strip().split(",") if r.stdout.strip() else []
    check("O.order", ids_proc == ids0 == [bid, aid])
    wipe_owner(owner)


# ── P: checkpoint (Generation V1) ──────────────────────────────────
def test_p():
    owner = f"asi_p_{uuid.uuid4().hex[:8]}"
    p = fresh(owner)
    aid = confirm(p, "a_gen", "alpha beta gamma delta")
    bid = confirm(p, "b_gen", "alpha zeta")
    learn_preference(p, bid, "alpha beta", 3)
    ids0, _ = sel_ids(p, "alpha beta")
    # Generation V1 checkpoint via the canonical path
    try:
        from form.mandell.checkpoint_generation import commit_checkpoint
        ck = commit_checkpoint(p, generation_id=f"asi-p-{uuid.uuid4().hex[:8]}")
        check("P.checkpoint", bool(ck and ck.get("committed")))
    except Exception as e:
        check("P.checkpoint", False)
        print(f"  (checkpoint error: {e})")
        wipe_owner(owner)
        return
    p.save()
    p2 = Program.load(owner)
    ids1, _ = sel_ids(p2, "alpha beta")
    check("P.order", ids1 == ids0)
    wipe_owner(owner)


# ── Q/R: feedback loop + no double counting ────────────────────────
def test_q():
    p = fresh()
    aid = confirm(p, "a_fb", "alpha beta gamma delta")
    bid = confirm(p, "b_fb", "alpha zeta")
    ids0, _ = sel_ids(p, "alpha beta")
    check("Q.sel0", ids0 == [aid, bid])

    # Selection0 → Execution0 → Outcome0
    oid0 = ctx_grow(p, "alpha beta")
    n_out0 = len(p.outcome_records)
    check("Q.outcome0", n_out0 >= 1)

    # Outcome0 → DBEL evidence → Proposal → Gate → Apply
    oids = [oid0, ctx_grow(p, "alpha beta"), ctx_grow(p, "alpha beta")]
    prop = dl.propose(p, "preference", 37, bid, oids)
    g = dl.gate_proposal(p, prop["proposal_id"])
    n_before_apply = len(p.outcome_records)
    a = dl.apply_proposal(p, prop["proposal_id"])
    n_after_apply = len(p.outcome_records)
    check("Q.applied", g["accepted"] and a["applied"])
    check("Q.no_recursive_exec", n_after_apply == n_before_apply)

    # Selection1 changes → Execution1 → Outcome1
    ids1, _ = sel_ids(p, "alpha beta")
    check("Q.sel1_changed", ids1 == [bid, aid])
    oid1 = ctx_grow(p, "alpha beta")
    check("Q.outcome1", oid1 not in oids)

    # Outcome1 CAN become later evidence (extractable)…
    ev = dl.extract_evidence(p, oid1)
    check("Q.extractable", ev.get("ok") is True)
    # …but NOT double-counted: same (kind,dell,kid) already APPLIED.
    # Use 3 fresh outcomes so the gate reaches the duplicate check.
    oids2 = [oid1, ctx_grow(p, "alpha beta"), ctx_grow(p, "alpha beta")]
    prop2 = dl.propose(p, "preference", 37, bid, oids2)
    g2 = dl.gate_proposal(p, prop2["proposal_id"])
    check("Q.no_double_count", g2["accepted"] is False
          and g2.get("reason") == "duplicate")
    # No automatic application: ledger has exactly one APPLIED for (37,bid)
    applied = [e for e in dl.learning_ledger(p)
               if e["status"] == "APPLIED" and e["knowledge_id"] == bid]
    check("Q.single_applied", len(applied) == 1)


# ── S: ROS inspection ──────────────────────────────────────────────
def test_s():
    from form.mandell import runtime_observe as ro
    p = fresh()
    aid = confirm(p, "a_ros", "alpha beta gamma delta")
    bid = confirm(p, "b_ros", "alpha zeta")
    learn_preference(p, bid, "alpha beta", 3)
    # Read-only selection learning view (ASI-I ROS extension)
    v = ro.selection_learning_view(p, "alpha beta")
    check("S.view_ok", v.get("ok") is True)
    check("S.applied_flag", v.get("learned_preference_applied") is True)
    check("S.scores", _score_eq(v.get("learned_scores", {}).get(bid), 3))
    check("S.baseline", v.get("baseline_selected_ids") == [aid, bid])
    check("S.learned_order", v.get("learned_selected_ids") == [bid, aid])
    check("S.hard_filters", "supersession_exclusions" in v
          and "dependency_exclusions" in v)
    # Existing ROS-I views still work
    ll = ro.learning_ledger_view(p)
    check("S.ledger", ll.get("count", 0) >= 1)
    lp = ro.learned_preferences_view(p)
    check("S.prefs", lp.get("count", 0) >= 1)
    # Read-only: inspection created no outcomes
    n0 = len(p.outcome_records)
    ro.selection_learning_view(p, "alpha beta")
    ro.learned_preferences_view(p)
    ro.learning_ledger_view(p)
    check("S.readonly", len(p.outcome_records) == n0)


# ── T: AUTONOMY=NO (static) ────────────────────────────────────────
def test_t():
    import pathlib
    import re
    ks = pathlib.Path(REPO, "form", "mandell", "knowledge_selector.py").read_text()
    for bad in ["import os", "import subprocess", "import sys",
                "exec(", "eval("]:
        check(f"T.no_{bad.strip('(')}", bad not in ks)
    # builtin compile() for code (re.compile is fine)
    check("T.no_builtin_compile",
          not re.search(r"(?<!\.)\bcompile\s*\(", ks))
    for fn in ["propose(", "gate_proposal(", "apply_proposal("]:
        # definition/import refs are fine; CALLS are not.
        check(f"T.no_call_{fn.strip('(')}",
              f"dl.{fn}" not in ks and f"= {fn}" not in ks)
    dls = pathlib.Path(REPO, "form", "mandell", "duobeta_learn.py").read_text()
    for bad in ["import os", "import subprocess", "exec(", "eval("]:
        check(f"T.dl_no_{bad.strip('(')}", bad not in dls)
    check("T.dl_no_builtin_compile",
          not re.search(r"(?<!\.)\bcompile\s*\(", dls))


# ── U: no selector duplication (static) ────────────────────────────
def test_u():
    import pathlib
    mandell = pathlib.Path(REPO, "form", "mandell")
    check("U.no_adaptive_selector",
          not (mandell / "adaptive_selector.py").exists())
    check("U.no_learned_selector",
          not (mandell / "learned_selector.py").exists())
    defs = []
    for f in mandell.glob("*.py"):
        if f.name.endswith("_test.py"):
            continue
        txt = f.read_text()
        if "def select_for_context" in txt:
            defs.append(f.name)
    check("U.single_selector", defs == ["knowledge_selector.py"])
    # bounded_learned_score is a scorer, not a selector
    import inspect
    sig = inspect.signature(dl.bounded_learned_score)
    check("U.scorer_not_selector", "knowledge_ids" not in sig.parameters
          and "context" not in sig.parameters)


def main() -> int:
    test_isolation_proof()
    test_a()
    test_b()
    test_c()
    test_d()
    test_e()
    test_f()
    test_g()
    test_h()
    test_i()
    test_j()
    test_k()
    test_m()
    test_n()
    test_o()
    test_p()
    test_q()
    test_s()
    test_t()
    test_u()
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"ASI-I: {total - failed}/{total} checks green")
    return 0 if failed == 0 else 1


def smoke() -> bool:
    try:
        main()
    except Exception:
        return False
    finally:
        _teardown_isolated_owners()
    return all(ok for _, ok in CHECKS)


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        _teardown_isolated_owners()
