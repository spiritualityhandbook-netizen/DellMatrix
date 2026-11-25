#!/usr/bin/env python3
"""Q4 — Reserved/unexecutable atoms and skip paths: typed args
attached to an atom that never executes.

Receipt shapes recorded verbatim: reserved single-atom (leaf
refusal), reserved in chain (Director Decision 1 skip receipt),
FlowThru-blocked, FlowOver-skipped, While zero-iteration body.
Central question: does validation run for a skipped atom, and
does the argument appear anywhere in the receipt?
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_lib import cleanup, fresh, setup_plane, snap, state_listing, verdict

from form.mandell.executor import execute_seed

results = []


def run(tag, fn):
    before = state_listing()
    owner = "ArgHonQ4" + tag
    try:
        fn(owner)
    finally:
        removed = cleanup(owner, before)
        print(f"  (cleanup {owner}: {len(removed)} entries removed)")


def r1(owner):
    p = fresh(owner)
    typed = execute_seed(p, '151[Harmonic](bogus="x")')
    p2 = fresh(owner + "B")
    bare = execute_seed(p2, "151[Harmonic]")
    print(f"single 151 typed -> ok={typed.get('ok')} error={typed.get('error')!r}")
    print(f"single 151 bare  -> ok={bare.get('ok')} error={bare.get('error')!r}")
    results.append(verdict("Q4-reserved-single",
                           not typed.get("ok") and not bare.get("ok")
                           and typed.get("error") == bare.get("error"),
                           "single-atom reserved Dell routes to the LEAF, "
                           "which refuses it as not-executable; args are "
                           "never inspected — identical with and without"))


def r2(owner):
    p = fresh(owner)
    r = execute_seed(p, '55[Set] :: k=v >> 151[Harmonic](bogus="x")')
    ar = r.get("atom_results") or []
    print(f"chain Set >> 151(bogus) -> ok={r.get('ok')} "
          f"partial={r.get('partial')} any_skipped={r.get('any_skipped')}")
    for rec in ar:
        print(f"  receipt: {rec}")
    rec = ar[1] if len(ar) > 1 else {}
    results.append(verdict("Q4-reserved-chain",
                           len(ar) == 2 and rec.get("ok") is False
                           and rec.get("skipped") is True
                           and rec.get("error") == "reserved/not-active"
                           and "bogus" not in str(rec)
                           and snap(p)["store"] == {"k": "v"},
                           "in a chain the reserved atom gets the Decision-1 "
                           "skip receipt (ok=False, skipped=True, explicit "
                           "reason); the typed arg appears NOWHERE in it"))


def r3(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '53[Scope](name="ghost") >> 82[Group](name="greens")')
    ar = r.get("atom_results") or []
    print(f"Scope(ghost) >> Group(name=greens) -> ok={r.get('ok')}")
    for rec in ar:
        print(f"  receipt: {rec}")
    rec = ar[1] if len(ar) > 1 else {}
    results.append(verdict("Q4-flowthru-block",
                           len(ar) == 2 and rec.get("ok") is False
                           and rec.get("skipped") is True
                           and rec.get("error") == "flow_thru_block"
                           and snap(p)["groups"] == {},
                           "FlowThru-blocked atom: skip receipt names the "
                           "flow, not the args; the Group never ran "
                           "(no 'greens', no default 'group')"))


def r4(owner):
    p = fresh(owner)
    r = execute_seed(p, '53[Scope](name="ghost") >> 55[Set](key="k", value="v")')
    ar = r.get("atom_results") or []
    rec = ar[1] if len(ar) > 1 else {}
    print(f"Scope(ghost) >> Set(key=k,value=v) -> receipts={ar} "
          f"store={snap(p)['store']}")
    results.append(verdict("Q4-skipped-not-validated",
                           rec.get("skipped") is True
                           and rec.get("error") == "flow_thru_block"
                           and snap(p)["store"] == {},
                           "even a REGISTERED Dell's args are not validated "
                           "when the atom is flow-blocked: the skip happens "
                           "in execute_range before _run_atom, so no "
                           "validation receipt exists for skipped atoms"))


def r5(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '55[Set] :: a=1 >>> 82[Group](name="greens") >> 61[Join]')
    ar = r.get("atom_results") or []
    print("FlowOver chain receipts:")
    for rec in ar:
        print(f"  receipt: {rec}")
    rec82 = [x for x in ar if x.get("dell") == 82]
    results.append(verdict("Q4-flowover-skip",
                           len(rec82) == 1 and rec82[0].get("skipped") is True
                           and "FlowOver" in str(rec82[0].get("reason"))
                           and snap(p)["groups"] == {},
                           "FlowOver-skipped atom: occurrence receipt with "
                           "the FlowOver reason; args absent; Group never ran"))


def r6(owner):
    p = fresh(owner)
    setup_plane(p)
    execute_seed(p, "51[Select]")
    r = execute_seed(p, '65[While] :: false > 82[Group](name="greens") > 61[Join]')
    ar = r.get("atom_results") or []
    print("While-false chain receipts:")
    for rec in ar:
        print(f"  receipt: {rec}")
    rec82 = [x for x in ar if x.get("dell") == 82]
    results.append(verdict("Q4-while-zero",
                           len(rec82) == 1 and rec82[0].get("skipped") is True
                           and "zero iterations" in str(rec82[0].get("reason"))
                           and snap(p)["groups"] == {},
                           "zero-iteration body atom: skip receipt with the "
                           "zero-iteration reason; args absent; never ran"))


for tag, fn in [("R1", r1), ("R2", r2), ("R3", r3), ("R4", r4),
                ("R5", r5), ("R6", r6)]:
    run(tag, fn)

print(f"\nQ4 SUMMARY: {sum(results)}/{len(results)} expectations confirmed")
sys.exit(0 if all(results) else 1)
