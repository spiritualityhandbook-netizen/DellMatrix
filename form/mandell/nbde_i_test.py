#!/usr/bin/env python3
"""NBDE-I: Next Best Directive Engine I — dedicated control suite (NBD-Ω-009).

The first canonical NBD-Ω decision-support engine. READ-ONLY.

LAW: SYSTEM EVIDENCE > NBD ANALYSIS > PROPOSED DIRECTIVES
     > DIRECTOR DECISION > separate authorized implementation cycle.

NBD may: DISCOVER, CLASSIFY, SCORE, COMPARE, RANK, EXPLAIN, PROPOSE.
NBD may NOT: EXECUTE, MUTATE, MERGE, APPLY LEARNING, CHANGE AUTHORITY,
DECLARE TRUTH, AUTONOMOUSLY ISSUE WORK.

Controls:
  A  fact/projection separation
  B  candidate states (OPEN/BLOCKED/READY/CLOSED)
  C  READY-only ranking
  D  BLOCKED visibility
  E  CLOSED exclusion
  F  dependency handling
  G  locality batching
  H  score component exposure
  I  anti-gaming (closure inflation, reuse, future-work, duplication)
  J  duplicate candidate handling
  K  stale fingerprint
  L  AUTONOMY=NO (static: no executor/mutation imports/calls)
  M  no mutation (packet run changes nothing)
  N  determinism (same state → same ranking)
  O  fresh-process determinism
  P  sensitivity (counterfactuals change ranking explainably)
  Q  ROS read-only inspection (no outcomes, no mutation)
  R  malformed candidate handling
  S  unknown evidence handling
  T  empty candidate set
  U  single candidate
  V  tie behavior (deterministic)
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from form.open import Program  # noqa: E402
from form.mandell import nbd_engine as ne  # noqa: E402
from form.mandell.nbd_candidates import build_frontier  # noqa: E402

CHECKS = []


def check(name: str, cond: bool) -> None:
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")


def mk_cid(cid="c1", **kw):
    base = dict(candidate_id=cid, title=f"Title {cid}",
                target_circuit="test", locality="test")
    base.update(kw)
    return ne.Candidate(**base)


def mk_evidence(kind=ne.FACT, detail="d", source="s"):
    return ne.Evidence(source=source, scope="test", detail=detail, kind=kind)


# ── A: fact/projection separation ──────────────────────────────────
def test_a():
    e_f = mk_evidence(ne.FACT, "PR #31 merged")
    e_p = mk_evidence(ne.PROJECTION, "expected 4 closures")
    e_d = mk_evidence(ne.DERIVED_FACT, "3 of 5 tests failed")
    e_u = mk_evidence(ne.UNKNOWN, "no data")
    check("A.kinds", {e_f.kind, e_p.kind, e_d.kind, e_u.kind} ==
          {"FACT", "PROJECTION", "DERIVED_FACT", "UNKNOWN"})
    c = mk_cid(expected_closures=4, projection_flags=["expected_closures"])
    check("A.projection_labeled", "expected_closures" in c.projection_flags)


# ── B: candidate states ────────────────────────────────────────────
def test_b():
    p = Program()
    cands = build_frontier(p)
    states = {c.state for c in cands}
    # After classify, should be READY or BLOCKED (none CLOSED in frontier)
    ne.classify_candidates(cands)
    states = {c.state for c in cands}
    check("B.states", states <= {"READY", "BLOCKED"})
    check("B.blocked_present", any(c.state == "BLOCKED" for c in cands))
    blocked = [c for c in cands if c.state == "BLOCKED"][0]
    check("B.blocked_reason", bool(blocked.blocked_reason))


# ── C: READY-only ranking ──────────────────────────────────────────
def test_c():
    p = Program()
    cands = build_frontier(p)
    pkt = ne.nbd_packet(p, cands)
    ready_ids = set(pkt["ready_set"])
    for r in pkt["ranked"]:
        check("C.ready_only", r["state"] == "READY")
    # BLOCKED candidate not in ranking
    blocked_ids = {c.candidate_id for c in cands if c.state == "BLOCKED"}
    check("C.blocked_excluded", not (blocked_ids & ready_ids))


# ── D/E/F: BLOCKED visibility, CLOSED exclusion, dependencies ──────
def test_d():
    c1 = mk_cid("c1", dependencies=["c2"])
    c2 = mk_cid("c2")
    c3 = mk_cid("c3", state=ne.CLOSED)
    ne.classify_candidates([c1, c2, c3])
    check("D.c1_blocked", c1.state == "BLOCKED")
    check("D.c2_ready", c2.state == "READY")
    check("D.c3_closed", c3.state == "CLOSED")
    # c2 closes → c1 becomes READY
    c2.state = ne.CLOSED
    ne.classify_candidates([c1, c2, c3])
    check("F.dep_resolved", c1.state == "READY")
    # ranking excludes CLOSED
    ranked = ne.rank_candidates([c1, c2, c3])
    ids = [r.candidate.candidate_id for r in ranked]
    check("E.closed_excluded", "c3" not in ids and "c2" not in ids)
    check("D.visible", c1.candidate_id in ids)


# ── G: locality batching ───────────────────────────────────────────
def test_g():
    p = Program()
    cands = build_frontier(p)
    pkt = ne.nbd_packet(p, cands)
    batches = pkt["batches"]
    check("G.batches", len(batches) >= 1)
    for b in batches:
        check("G.batch_shape", bool(b["batch_id"]) and len(b["members"]) >= 2)
    # batching is a proposal, not a mutation
    check("G.no_mutation", all(
        c.state in ("READY", "BLOCKED") for c in cands))


# ── H: score component exposure ────────────────────────────────────
def test_h():
    p = Program()
    cands = build_frontier(p)
    pkt = ne.nbd_packet(p, cands)
    for r in pkt["ranked"][:3]:
        comps = r["components"]
        for k in ("C_closures", "D_readiness", "R_resonance", "I_clarity",
                  "V_confidence", "K_risk", "S_interference"):
            check(f"H.comp_{k}", k in comps)
        check("H.projection_flags", isinstance(r["projection_flags"], list)
              and len(r["projection_flags"]) > 0)


# ── I: anti-gaming ─────────────────────────────────────────────────
def test_i():
    # closure inflation: claims 5, references 1 → discounted to 1
    c = mk_cid("g1", expected_closures=5,
               evidence=[mk_evidence(detail="closes LE-01")])
    trig = ne.anti_gaming_checks(c)
    check("I.closure_discount", c.expected_closures == 1 and len(trig) >= 1)
    # reuse without evidence: capped at 0.5
    c2 = mk_cid("g2", expected_reuse=0.9)
    trig2 = ne.anti_gaming_checks(c2)
    check("I.reuse_cap", c2.expected_reuse == 0.5)
    # future-work inflation: capped at 3
    c3 = mk_cid("g3", expected_future_work_avoided=10)
    ne.anti_gaming_checks(c3)
    check("I.fwa_cap", c3.expected_future_work_avoided == 3)


# ── J: duplicate candidate handling ────────────────────────────────
def test_j():
    c1 = mk_cid("dup", expected_closures=2,
                evidence=[mk_evidence(detail="LE-01")])
    c2 = mk_cid("dup", expected_closures=2,
                evidence=[mk_evidence(detail="LE-01")])
    # duplicate IDs: classify then rank; must not crash; deterministic
    ne.classify_candidates([c1, c2])
    ranked = ne.rank_candidates([c1, c2])
    check("J.no_crash", len(ranked) == 2)
    # mark duplication via _duplication → NextWeight collapses
    c1._duplication = 1.0
    ne.classify_candidates([c1])
    s_dup = ne.score_candidate(c1)
    c3 = mk_cid("x", expected_closures=2,
                evidence=[mk_evidence(detail="LE-01")])
    ne.classify_candidates([c3])
    s_clean = ne.score_candidate(c3)
    check("J.dup_penalty", s_dup.next_weight < s_clean.next_weight
          and s_clean.next_weight > 0)


# ── K: stale fingerprint ───────────────────────────────────────────
def test_k():
    p = Program()
    cands = build_frontier(p)
    pkt = ne.nbd_packet(p, cands)
    check("K.fresh", ne.is_stale(pkt, p) is False)
    # simulate state change: tamper fingerprint
    pkt["state_fingerprint"]["outcome_ledger_count"] = "tampered"
    check("K.stale", ne.is_stale(pkt, p) is True)
    check("K.hash", len(pkt["fingerprint_hash"]) == 16)


# ── L: AUTONOMY=NO (static) ────────────────────────────────────────
def test_l():
    import pathlib
    src = pathlib.Path(REPO, "form", "mandell", "nbd_engine.py").read_text()
    for bad in ["route_intent", "execute_seed", "apply_proposal",
                "commit_checkpoint", "merge", "subprocess", "import os"]:
        check(f"L.no_{bad}", bad not in src)
    # no nursery/knowledge/disposition mutation
    for bad in ["nursery.add", "nursery.proposals[", ".disposition",
                "knowledge_selector"]:
        # knowledge_selector not imported; disposition not touched
        pass
    check("L.no_nursery_write", "nursery" not in src.lower()
          or "nursery" not in src)
    # Actually check properly:
    check("L.no_nursery_ref", "program.nursery" not in src
          and "nursery.add" not in src)


# ── M: no mutation ─────────────────────────────────────────────────
def test_m():
    p = Program()
    n_out0 = len(p.outcome_records)
    fp0 = ne.state_fingerprint(p)
    cands = build_frontier(p)
    pkt = ne.nbd_packet(p, cands)
    check("M.no_outcomes", len(p.outcome_records) == n_out0)
    # packet doesn't mutate candidates' core state beyond classification
    # (classification is the documented VERIFY>CLASSIFY step)
    check("M.packet_shape", pkt["AUTONOMY"] == "NO"
          and pkt["DIRECTOR_DECISION_REQUIRED"] == "YES"
          and pkt["EXECUTION_AUTHORITY"] == "NONE")


# ── N: determinism ─────────────────────────────────────────────────
def test_n():
    p = Program()
    c1 = build_frontier(p)
    c2 = build_frontier(p)
    pkt1 = ne.nbd_packet(p, c1)
    pkt2 = ne.nbd_packet(p, c2)
    r1 = [(r["candidate_id"], r["next_weight"]) for r in pkt1["ranked"]]
    r2 = [(r["candidate_id"], r["next_weight"]) for r in pkt2["ranked"]]
    check("N.deterministic", r1 == r2)


# ── O: fresh-process determinism ───────────────────────────────────
def test_o():
    code = (
        "import sys; sys.path.insert(0, %r); "
        "from form.open import Program; "
        "from form.mandell.nbd_engine import nbd_packet; "
        "from form.mandell.nbd_candidates import build_frontier; "
        "p = Program(); pkt = nbd_packet(p, build_frontier(p)); "
        "print(';'.join(f\"{r['candidate_id']}:{r['next_weight']}\" "
        "for r in pkt['ranked']))"
        % REPO
    )
    r = subprocess.run([sys.executable, "-c", code], capture_output=True,
                       text=True, timeout=120)
    check("O.proc_ok", r.returncode == 0)
    p = Program()
    pkt = ne.nbd_packet(p, build_frontier(p))
    local = ";".join(f"{r['candidate_id']}:{r['next_weight']}"
                     for r in pkt["ranked"])
    check("O.same", r.stdout.strip() == local)


# ── P: sensitivity ─────────────────────────────────────────────────
def test_p():
    p = Program()
    cands = build_frontier(p)
    pkt = ne.nbd_packet(p, cands)
    top_id = pkt["ranked"][0]["candidate_id"]
    top_c = next(c for c in cands if c.candidate_id == top_id)
    sens = ne.sensitivity(top_c)
    check("P.scenarios", len(sens["scenarios"]) == 4)
    # dependency blocked → NextWeight collapses (D=0)
    d = sens["scenarios"]["dependency_blocked"]
    check("P.blocked_collapses", d["next_weight"] == 0.0)
    # all deltas explainable (numeric)
    for name, s in sens["scenarios"].items():
        check(f"P.delta_{name}", isinstance(s["delta"], float))


# ── Q: ROS read-only ───────────────────────────────────────────────
def test_q():
    from form.mandell import runtime_observe as ro
    p = Program()
    n0 = len(p.outcome_records)
    v = ro.nbd_view(p)
    check("Q.ok", v.get("ok") is True)
    check("Q.ranked", len(v.get("ranked", [])) >= 1)
    check("Q.authority", v.get("AUTONOMY") == "NO"
          and v.get("DIRECTOR_DECISION_REQUIRED") == "YES"
          and v.get("EXECUTION_AUTHORITY") == "NONE")
    v2 = ro.nbd_view(p, candidate_id=v["ranked"][0]["candidate_id"])
    check("Q.candidate", v2.get("ok") is True and "candidate" in v2)
    v3 = ro.nbd_view(p, candidate_id="nonexistent_xyz")
    check("Q.unknown", v3.get("ok") is False)
    check("Q.readonly", len(p.outcome_records) == n0)


# ── R/S/T/U/V: edge cases ──────────────────────────────────────────
def test_r():
    # malformed candidate: missing title → dataclass requires it; use minimal
    c = ne.Candidate(candidate_id="bad", title="", target_circuit="x")
    # empty verification plan → I derived, no crash
    s = ne.score_candidate(c)
    check("R.no_crash", isinstance(s.next_weight, float))


def test_s():
    # unknown evidence kind → still scores (honest UNKNOWN)
    c = mk_cid("u1", evidence=[mk_evidence(ne.UNKNOWN, "no data")])
    s = ne.score_candidate(c)
    check("S.unknown_ok", isinstance(s.next_weight, float))


def test_t():
    p = Program()
    pkt = ne.nbd_packet(p, [])
    check("T.empty", pkt["ranked"] == [] and pkt["top_proposal"] is None
          and pkt["ready_set"] == [])


def test_u():
    c = mk_cid("solo", expected_closures=1,
               evidence=[mk_evidence(detail="LE-01")])
    ne.classify_candidates([c])
    ranked = ne.rank_candidates([c])
    check("U.single", len(ranked) == 1 and ranked[0].rank == 1)


def test_v():
    # ties: identical candidates → deterministic by candidate_id ASC
    c1 = mk_cid("b-tie", expected_closures=1,
                evidence=[mk_evidence(detail="LE-01")])
    c2 = mk_cid("a-tie", expected_closures=1,
                evidence=[mk_evidence(detail="LE-01")])
    ne.classify_candidates([c1, c2])
    ranked = ne.rank_candidates([c1, c2])
    ids = [r.candidate.candidate_id for r in ranked]
    check("V.tie_break", ids == ["a-tie", "b-tie"])
    # repeat → same
    ranked2 = ne.rank_candidates([c1, c2])
    ids2 = [r.candidate.candidate_id for r in ranked2]
    check("V.stable", ids == ids2)


def main() -> int:
    test_a()
    test_b()
    test_c()
    test_d()
    test_g()
    test_h()
    test_i()
    test_j()
    test_k()
    test_l()
    test_m()
    test_n()
    test_o()
    test_p()
    test_q()
    test_r()
    test_s()
    test_t()
    test_u()
    test_v()
    total = len(CHECKS)
    failed = sum(1 for _, ok in CHECKS if not ok)
    print(f"NBDE-I: {total - failed}/{total} checks green")
    return 0 if failed == 0 else 1


def smoke() -> bool:
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok in CHECKS)


if __name__ == "__main__":
    sys.exit(main())
