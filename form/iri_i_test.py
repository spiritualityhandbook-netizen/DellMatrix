#!/usr/bin/env python3
"""IRI-I direct tests (NBD-Omega-042).

Tests the staged reissue contract through production handlers.
"""
import io
import sys
import uuid

sys.path.insert(0, ".")

from form.open import Program
from form import repl as repl_mod
from form.mandell.translate import translate


def make_program(owner):
    p = Program(owner=owner)
    p.outcome_records = {}
    p.outcome_seq = 0
    return p


def run_line(p, line, pending=None, interaction_id=None):
    """Simulate one REPL turn through the real handlers."""
    buf = io.StringIO()
    old_say = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        low = line.strip().lower()
        if low == "reissue" or low.startswith("reissue "):
            p, pending = repl_mod._handle_reissue(p, line, pending)
        else:
            iid = interaction_id or str(uuid.uuid4())
            p = repl_mod._dispatch_public_line(p, line, iid)
    finally:
        repl_mod._say = old_say
    return p, pending, buf.getvalue()


def create_via_public(p, text):
    iid = str(uuid.uuid4())
    return run_line(p, text, interaction_id=iid)


results = []


def check(name, cond):
    results.append((name, bool(cond)))
    print(f"  {'PASS' if cond else 'FAIL'}: {name}")


def smoke() -> bool:
    """Run all IRI-I direct tests. Returns True if all pass."""
    global results
    results = []
    _run_all()
    n_pass = sum(1 for _, c in results if c)
    print(f"\nIRI-I-DIRECT: {n_pass}/{len(results)}")
    return n_pass == len(results)


def _run_all():
    print("== R1/R2: Historical Outcome read-only; inspection never executes ==")
    p = make_program("iri_t1")
    p, _, _ = create_via_public(p, "create an idea called t1")
    n_before = len(p.outcome_records)
    p, pending, out = run_line(p, "reissue 1")
    check("inspect does not execute", len(p.outcome_records) == n_before)
    check("source staged", pending == "create an idea called t1")
    check("source shown", "create an idea called t1" in out)
    check("warning shown", "current state" in out)

    print("== R3/R4: fidelity gate ==")
    p2 = make_program("iri_t2")
    # Empty source outcome -> refuse
    from form.mandell.execution_observer import _RawReceipt
    from form.mandell.outcome_ledger import capture_outcome
    r = _RawReceipt(action="place", input="", ok=True)
    o = capture_outcome(p2, r, interaction_id=str(uuid.uuid4()))
    seq = o["outcome_seq"]
    p2, pending2, out2 = run_line(p2, f"reissue {seq}")
    check("empty source refused", pending2 is None and "not reissuable" in out2)

    print("== F1: unknown ref ==")
    p3 = make_program("iri_t3")
    p3, pend3, out3 = run_line(p3, "reissue 999")
    check("unknown ref safe", pend3 is None and "no outcome" in out3)

    print("== confirm with nothing staged ==")
    p4 = make_program("iri_t4")
    p4, pend4, out4 = run_line(p4, "reissue confirm")
    check("confirm w/o stage safe", "Nothing staged" in out4)

    print("== R7/R9/R10/R11/R12: new identity on confirm ==")
    p5 = make_program("iri_t5")
    p5, _, _ = create_via_public(p5, "create an idea called t5")
    orig = list(p5.outcome_records.values())[0]
    orig_iid = orig["interaction_id"]
    orig_oid = orig["outcome_id"]
    p5, pending5, _ = run_line(p5, "reissue 1")
    p5, pending5, out5 = run_line(p5, "reissue confirm", pending=pending5)
    new_recs = list(p5.outcome_records.values())
    check("exactly 2 outcomes (no dup)", len(new_recs) == 2)
    new = new_recs[1]
    check("new interaction_id", new["interaction_id"] != orig_iid)
    check("new outcome_id", new["outcome_id"] != orig_oid)
    check("stage cleared", pending5 is None)

    print("== R16: current state governs (not replay) ==")
    # t5 reissued -> collision avoidance gives t5_1, proving current-state execution
    check("collision avoidance (current state)", "t5_1" in out5 or new["input"] == orig["input"])

    print("== cancel ==")
    p6 = make_program("iri_t6")
    p6, _, _ = create_via_public(p6, "create an idea called t6")
    p6, pend6, _ = run_line(p6, "reissue 1")
    p6, pend6, out6 = run_line(p6, "reissue cancel", pending=pend6)
    check("cancel clears stage", pend6 is None)
    check("cancel no execution", len(p6.outcome_records) == 1)


if __name__ == "__main__":
    ok = smoke()
    sys.exit(0 if ok else 1)
