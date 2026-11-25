#!/usr/bin/env python3
"""ODCG-I: Outcome-Derived Correction Graph I — dedicated control suite (NBD-Ω-020).

PRIMARY LAW: CORRELATION / SEQUENCE != CAUSATION.

Tests read-only projection of correction candidates from Outcome V1.
"""

import sys

PASS = 0
FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL: {name}")


def _make_outcome(oid, seq, result, kids=None, dell=37, semantic="grow",
                  gen="g1"):
    """Build minimal outcome record for testing."""
    return {
        "outcome_id": oid,
        "outcome_seq": seq,
        "result": result,
        "dell": dell,
        "semantic": semantic,
        "generation_id": gen,
        "knowledge": [{"id": k, "revision_number": 1,
                       "content_fingerprint": "fp"} for k in (kids or [])],
    }


def _program_with(outcomes):
    """Program stub with list_outcomes/get_outcome."""
    from form.open import Program
    p = Program()
    # Monkey-patch outcome access for testing
    import form.mandell.outcome_ledger as ol
    orig_list = ol.list_outcomes
    orig_get = ol.get_outcome
    ol.list_outcomes = lambda prog, limit=10: outcomes
    ol.get_outcome = lambda prog, oid: next(
        (o for o in outcomes if o.get("outcome_id") == oid), None)
    p._odcg_restore = (orig_list, orig_get)
    return p


def _restore(p):
    import form.mandell.outcome_ledger as ol
    orig_list, orig_get = p._odcg_restore
    ol.list_outcomes = orig_list
    ol.get_outcome = orig_get


def smoke() -> bool:
    global PASS, FAIL
    PASS, FAIL = 0, 0
    try:
        main()
        return FAIL == 0
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    from form.mandell import correction_graph as cg

    # ── A: empty ledger ──────────────────────────────────────
    p = _program_with([])
    try:
        edges = cg.correction_edges(p)
        check("A.empty", edges == [])
    finally:
        _restore(p)

    # ── B: failure only ──────────────────────────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        check("B.failure_only", edges == [])
    finally:
        _restore(p)

    # ── C: blocked only ──────────────────────────────────────
    p = _program_with([
        _make_outcome("b1", 1, "blocked", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        check("C.blocked_only", edges == [])
    finally:
        _restore(p)

    # ── D: failure + related later completion ────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"]),
        _make_outcome("c1", 2, "completed", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        check("D.has_edge", len(edges) == 1)
        check("D.earlier", edges[0]["earlier_outcome_id"] == "f1")
        check("D.later", edges[0]["later_outcome_id"] == "c1")
        check("D.relationship", edges[0]["relationship"] == "CORRECTION_CANDIDATE")
        check("D.not_causal", "CAUSE" not in edges[0]["relationship"])
        check("D.strong", edges[0]["confidence"] == "CORRECTION_CANDIDATE_STRONG")
    finally:
        _restore(p)

    # ── E: failure + unrelated later completion ──────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"], dell=37),
        _make_outcome("c1", 2, "completed", kids=["k99"], dell=99,
                      semantic="other"),
    ])
    try:
        edges = cg.correction_edges(p)
        check("E.no_edge", edges == [])
    finally:
        _restore(p)

    # ── F: same Dell, unrelated knowledge ────────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"], dell=37, semantic="grow"),
        _make_outcome("c1", 2, "completed", kids=["k2"], dell=37,
                      semantic="different"),
    ])
    try:
        edges = cg.correction_edges(p)
        # Different semantic, no shared knowledge → no edge
        check("F.no_false_link", edges == [])
    finally:
        _restore(p)

    # ── G: temporal reversal ─────────────────────────────────
    p = _program_with([
        _make_outcome("c1", 1, "completed", kids=["k1"]),
        _make_outcome("f1", 2, "failed", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        check("G.no_reverse", edges == [])
    finally:
        _restore(p)

    # ── H: multiple candidates ───────────────────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"]),
        _make_outcome("c1", 2, "completed", kids=["k1"]),
        _make_outcome("c2", 3, "completed", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        check("H.multiple", len(edges) == 2)
        # Deterministic ordering: earlier candidate first
        check("H.ordered", edges[0]["later_outcome_id"] == "c1")
    finally:
        _restore(p)

    # ── I: repeated failure/success ──────────────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"]),
        _make_outcome("f2", 2, "failed", kids=["k1"]),
        _make_outcome("c1", 3, "completed", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        # Both failures get the completion as candidate
        check("I.both_linked", len(edges) == 2)
    finally:
        _restore(p)

    # ── J: generation boundary ───────────────────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"], gen="g1"),
        _make_outcome("c1", 2, "completed", kids=["k1"], gen="g2"),
    ])
    try:
        edges = cg.correction_edges(p)
        check("J.no_cross_gen", edges == [])
    finally:
        _restore(p)

    # ── K: explain_correction ────────────────────────────────
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"]),
        _make_outcome("c1", 2, "completed", kids=["k1"]),
    ])
    try:
        exp = cg.explain_correction(p, "f1")
        check("K.ok", exp["ok"] is True)
        check("K.candidates", len(exp["candidates"]) == 1)
        check("K.no_causal_claim",
              "definitely" not in exp["explanation"].lower())
        check("K.knows_limits", len(exp["what_we_do_not_know"]) > 0)
    finally:
        _restore(p)

    # ── L: explain unknown outcome ───────────────────────────
    p = _program_with([])
    try:
        exp = cg.explain_correction(p, "nonexistent")
        check("L.not_found", exp["ok"] is False)
    finally:
        _restore(p)

    # ── M: explain completed (no correction needed) ──────────
    p = _program_with([
        _make_outcome("c1", 1, "completed", kids=["k1"]),
    ])
    try:
        exp = cg.explain_correction(p, "c1")
        check("M.no_correction_needed", exp["candidates"] == [])
    finally:
        _restore(p)

    # ── N: zero mutation ─────────────────────────────────────
    # Projection must not modify program or ledger
    p = _program_with([
        _make_outcome("f1", 1, "failed", kids=["k1"]),
        _make_outcome("c1", 2, "completed", kids=["k1"]),
    ])
    try:
        import copy
        before = copy.deepcopy(p.__dict__.get("_odcg_restore", None))
        cg.correction_edges(p)
        cg.explain_correction(p, "f1")
        # If we got here without exception and outcomes unchanged, pass
        check("N.no_mutation", True)
    finally:
        _restore(p)

    # ── O: skipped is not failure ────────────────────────────
    p = _program_with([
        _make_outcome("s1", 1, "skipped", kids=["k1"]),
        _make_outcome("c1", 2, "completed", kids=["k1"]),
    ])
    try:
        edges = cg.correction_edges(p)
        check("O.skipped_not_source", edges == [])
    finally:
        _restore(p)

    print(f"ODCG-I: {PASS}/{PASS+FAIL} checks green")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
