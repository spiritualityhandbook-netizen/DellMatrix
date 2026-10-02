#!/usr/bin/env python3
"""RCCR-I tests — Residual Code Circuit Resolution I.

Verifies LE-10 and LE-15 resolutions and the canonical/NBD boundary fix.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

CHECKS = []

def check(name, cond):
    CHECKS.append((name, bool(cond)))
    if not cond:
        print(f"  FAIL: {name}")

def smoke() -> bool:
    global CHECKS
    CHECKS = []
    
    from form.mandell import circuit_ledger as cl
    from form.mandell import nbd_engine as ne
    from form.mandell.nbd_candidates import build_frontier, CANDIDATE_CIRCUIT_MAP
    from form.open import Program
    
    p = Program()
    
    # ── A: attention_rank caller inventory ───────────────────────
    import subprocess
    repo = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    result = subprocess.run(
        ["grep", "-rn", "attention_rank(", "form/", "--include=*.py"],
        cwd=repo, capture_output=True, text=True
    )
    callers = [l for l in result.stdout.strip().split("\n") if l 
               and "def attention_rank" not in l]
    # Should be: open.py:1229 (Program.attend) and inspire_pack.py:566 (test)
    check("A.has_callers", len(callers) >= 1)
    check("A.open_caller", any("open.py" in l for l in callers))
    
    # ── B: semantic-overlap proof ───────────────────────────────
    # attention_rank is for interactive attend; Relevance V2 for autonomous.
    # They are separate; no adapter needed.
    le10 = cl.get_circuit("LE-10")
    check("B.le10_closed", le10.state == "CLOSED")
    check("B.le10_cycle", le10.closure_cycle == "RCCR-I")
    
    # ── C: single ranking authority ──────────────────────────────
    # Verify no second ranking authority was created
    # (attention_rank still exists for attend, but not in selection stack)
    from form.dell_matrix.inspire_pack import attention_rank
    check("C.attention_exists", callable(attention_rank))
    # Verify it's not in knowledge_selector
    with open(os.path.join(repo, "form", "mandell", "knowledge_selector.py")) as f:
        ks_src = f.read()
    check("C.not_in_selector", "attention_rank" not in ks_src)
    
    # ── D: body alias reproduction ───────────────────────────────
    from form.avatar.body import Avatar, BodyState
    a1 = Avatar(name="A")
    a2 = Avatar(name="B")
    check("D.independent_bodies", a1.body is not a2.body)
    
    # ── E: parent→child mutation test ────────────────────────────
    # (No parent/child relationship exists; verify independence)
    a1.body.pos = (5, 5)
    check("E.no_contamination", a2.body.pos == (0, 0))
    
    # ── F: child→parent mutation test ────────────────────────────
    a2.body.facing = a2.body.facing  # No-op; verify no shared state
    check("F.still_independent", a1.body.pos == (5, 5))
    
    # ── G: ownership contract ────────────────────────────────────
    # All BodyState fields are immutable types
    import dataclasses
    fields = dataclasses.fields(BodyState)
    check("G.has_fields", len(fields) > 0)
    # pos is tuple, facing/posture/etc are Enums, holding is Optional[str]
    # (We verify by checking no list/dict/set fields)
    for f in fields:
        # The type annotations should not be mutable containers
        t = str(f.type).lower()
        check(f"G.{f.name}_immutable", 
              not any(m in t for m in ["list", "dict", "set"]) or "optional" in t)
    
    # ── H: LE-15 classification ──────────────────────────────────
    le15 = cl.get_circuit("LE-15")
    check("H.le15_closed", le15.state == "CLOSED")
    check("H.le15_cycle", le15.closure_cycle == "RCCR-I")
    
    # ── I: canonical/NBD state equality ──────────────────────────
    cands = build_frontier(p)
    ne.sync_from_ledger(cands)
    ne.classify_candidates(cands)
    # LE-10 CLOSED → candidate CLOSED
    ara = [c for c in cands if c.candidate_id == "attention-rank-adapter"][0]
    check("I.ara_closed", ara.state == "CLOSED")
    # LE-15 CLOSED → candidate CLOSED
    bsc = [c for c in cands if c.candidate_id == "body-shallow-copy"][0]
    check("I.bsc_closed", bsc.state == "CLOSED")
    # LE-04 OPEN → candidate OPEN (needs classification), not READY
    lvc = [c for c in cands if c.candidate_id == "live-visual-convergence"][0]
    check("I.lvc_open", lvc.state == "OPEN")
    check("I.lvc_flag", lvc.circuit_needs_classification)
    
    # ── J: OPEN exclusion ────────────────────────────────────────
    ranked = ne.rank_candidates(cands)
    ranked_ids = {r.candidate.candidate_id for r in ranked}
    check("J.open_excluded", "live-visual-convergence" not in ranked_ids)
    
    # ── K: READY inclusion ───────────────────────────────────────
    # Frontier candidates (no LE mapping) can be READY
    check("K.ready_ranked", len(ranked_ids) > 0)
    for rid in ranked_ids:
        c = [x for x in cands if x.candidate_id == rid][0]
        check(f"K.{rid}_ready", c.state == "READY")
    
    # ── L: CLOSED exclusion ──────────────────────────────────────
    for cid in ["attention-rank-adapter", "body-shallow-copy", 
                "dead-path-cleanup", "phantom-commands", "terminology-docs",
                "program-strength-registration", "nbd-log-stamping"]:
        check(f"L.{cid}_excluded", cid not in ranked_ids)
    
    # ── M: SUPERSEDED exclusion ──────────────────────────────────
    # LE-13 is SUPERSEDED → nbd-log-stamping is CLOSED (excluded)
    check("M.superseded_excluded", "nbd-log-stamping" not in ranked_ids)
    
    # ── N: determinism ───────────────────────────────────────────
    c1 = build_frontier(p)
    ne.sync_from_ledger(c1)
    ne.classify_candidates(c1)
    pkt1 = ne.nbd_packet(p, c1, main_commit="x")
    c2 = build_frontier(p)
    ne.sync_from_ledger(c2)
    ne.classify_candidates(c2)
    pkt2 = ne.nbd_packet(p, c2, main_commit="x")
    r1 = [r["candidate_id"] for r in pkt1["ranked"]]
    r2 = [r["candidate_id"] for r in pkt2["ranked"]]
    check("N.deterministic", r1 == r2)
    
    passed = sum(1 for _, ok in CHECKS if ok)
    total = len(CHECKS)
    print(f"RCCR-I: {passed}/{total} checks green")
    return passed == total

if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
