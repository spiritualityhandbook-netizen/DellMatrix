#!/usr/bin/env python3
"""SAOC-II direct tests (NBD-Omega-044).

Proves the evolve observation gap (E1) and validates the adapter.
"""
import io
import sys
import uuid

sys.path.insert(0, ".")

from form.open import Program
from form import repl as repl_mod


def make_program(owner):
    p = Program(owner=owner)
    p.outcome_records = {}
    p.outcome_seq = 0
    return p


def get_gen(p):
    duo = getattr(p, "duo", None)
    return getattr(duo, "generation", 0) if duo else 0


def run_line(p, line, pending=None):
    buf = io.StringIO()
    old_say = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        low = line.strip().lower()
        if low == "reissue" or low.startswith("reissue "):
            p, pending = repl_mod._handle_reissue(p, line, pending)
        else:
            p = repl_mod._dispatch_public_line(p, line, str(uuid.uuid4()))
    finally:
        repl_mod._say = old_say
    return p, pending, buf.getvalue()


results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}: {name}")


def _run_all():
    print("== 1. E1 gap (pre-adapter logic): evolve mutates, adapter captures ==")
    p = make_program("saoc2_t1")
    g0 = get_gen(p)
    p, _, _ = run_line(p, "evolve")
    g1 = get_gen(p)
    check("mutation occurred", g1 == g0 + 1)
    check("exactly one Outcome", len(p.outcome_records) == 1)

    print("== 2-4. Success observation + cardinality + iid ==")
    rec = list(p.outcome_records.values())[0]
    check("operation=evolve", rec["operation"] == "evolve")
    check("semantic honest", rec["semantic"] == "evolve[program:specialized]")
    check("dell=None (not fabricated)", rec["dell"] is None)
    check("mandell empty (not fabricated)", rec["mandell"] == "")
    check("interaction_id present", bool(rec["interaction_id"]))
    check("input exact", rec["input"] == "evolve")

    print("== 5-9. No dup mutation/Outcome; observer doesn't mutate ==")
    p2 = make_program("saoc2_t2")
    g0 = get_gen(p2)
    p2, _, _ = run_line(p2, "evolve")
    p2, _, _ = run_line(p2, "evolve")
    check("two evolves -> gen+2", get_gen(p2) == g0 + 2)
    check("two evolves -> 2 Outcomes", len(p2.outcome_records) == 2)
    iids = [o["interaction_id"] for o in p2.outcome_records.values()]
    check("distinct iids", len(set(iids)) == 2)

    print("== 10-12. Parity: adapter doesn't change evolution ==")
    # Compare with direct p.evolve() (no adapter path)
    p3 = make_program("saoc2_t3")
    out_direct = p3.evolve("test")
    p4 = make_program("saoc2_t4")
    p4, _, out4 = run_line(p4, "evolve")
    check("generation parity", get_gen(p3) == get_gen(p4))
    # Pillars structure present in both
    check("pillars in direct", "pillars" in out_direct)
    check("Outcome has generation note", "generation" in str(list(p4.outcome_records.values())[0]))

    print("== 15-17. COO/ROS visibility ==")
    from form.mandell.runtime_observe import resolve_outcome_ref
    res = resolve_outcome_ref(p4, "1")
    check("COO resolves", res.get("ok"))
    # Trace via runtime_observe
    from form.mandell.runtime_observe import execution_trace
    tr = execution_trace(p4, res["outcome"]["outcome_id"])
    check("ROS trace works", tr.get("ok", True) or "interaction" in str(tr).lower())

    print("== 18-20. Reissue ==")
    p5 = make_program("saoc2_t5")
    p5, _, _ = run_line(p5, "evolve")
    g1 = get_gen(p5)
    p5, pend, _ = run_line(p5, "reissue 1")
    check("reissue stages (no exec)", pend == "evolve" and len(p5.outcome_records) == 1)
    p5, pend, _ = run_line(p5, "reissue confirm", pending=pend)
    check("reissue executes current", get_gen(p5) == g1 + 1)
    check("reissue new Outcome", len(p5.outcome_records) == 2)
    recs = list(p5.outcome_records.values())
    check("reissue new iid", recs[1]["interaction_id"] != recs[0]["interaction_id"])


def smoke() -> bool:
    global results
    results = []
    _run_all()
    n_pass = sum(1 for _, c in results if c)
    print(f"\nSAOC-II-DIRECT: {n_pass}/{len(results)}")
    return n_pass == len(results)


if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
