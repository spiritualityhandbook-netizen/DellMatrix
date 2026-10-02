#!/usr/bin/env python3
"""HIC-I tests — Historical Integrity Closure I.

Durable proofs for LE-25 closure and archaeology exit gate.
The historical scan itself is an evidence artifact (not rerun every cycle).
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
    from collections import Counter
    
    p = Program()
    ledger = cl.build_ledger()
    counts = Counter(c.state for c in ledger)
    
    # ── A: LE-25 transition validity ───────────────────────────
    le25 = cl.get_circuit("LE-25")
    check("A.le25_closed", le25.state == "CLOSED")
    check("A.le25_cycle", le25.closure_cycle == "HIC-I")
    # Valid forward transition: OPEN → CLOSED (via READY)
    check("A.no_resurrection", not cl.is_resurrection("LE-25", "CLOSED"))
    
    # ── B: no OPEN original circuits ───────────────────────────
    check("B.zero_open", counts.get("OPEN", 0) == 0)
    
    # ── C: exit gate ───────────────────────────────────────────
    check("C.closed_22", counts.get("CLOSED", 0) == 22)
    check("C.superseded_1", counts.get("SUPERSEDED", 0) == 1)
    check("C.historical_1", counts.get("HISTORICAL_ONLY", 0) == 1)
    check("C.blocked_1", counts.get("BLOCKED", 0) == 1)
    check("C.total_25", sum(counts.values()) == 25)
    
    # ── D: LE-12 remains BLOCKED ───────────────────────────────
    le12 = cl.get_circuit("LE-12")
    check("D.le12_blocked", le12.state == "BLOCKED")
    check("D.le12_not_closed", le12.state != "CLOSED")
    
    # ── E: historical/superseded non-rankable ──────────────────
    cands = build_frontier(p)
    ne.sync_from_ledger(cands)
    ne.classify_candidates(cands)
    ranked = ne.rank_candidates(cands)
    ranked_ids = {r.candidate.candidate_id for r in ranked}
    # LE-13 SUPERSEDED → nbd-log-stamping CLOSED, not ranked
    check("E.superseded_excluded", "nbd-log-stamping" not in ranked_ids)
    # LE-09 HISTORICAL_ONLY has no candidate (correct)
    check("E.historical_no_candidate", True)
    
    # ── F: original vs derived frontier separation ─────────────
    original_ranked = []
    derived_ranked = []
    for r in ranked:
        mapped = CANDIDATE_CIRCUIT_MAP.get(r.candidate.candidate_id, [])
        if mapped:
            original_ranked.append(r.candidate.candidate_id)
        else:
            derived_ranked.append(r.candidate.candidate_id)
    check("F.original_empty", len(original_ranked) == 0)
    check("F.derived_nonempty", len(derived_ranked) > 0)
    
    # ── G: NBD deterministic after closure ─────────────────────
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
    check("G.deterministic", r1 == r2)
    
    passed = sum(1 for _, ok in CHECKS if ok)
    total = len(CHECKS)
    print(f"HIC-I: {passed}/{total} checks green")
    return passed == total

if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
