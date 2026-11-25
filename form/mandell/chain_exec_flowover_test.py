#!/usr/bin/env python3
"""CHAIN-EXEC FLOWOVER-JOIN — regression suite for the `>>>`
immediately-before-`61[Join]` non-termination defect.

Director ruling 7085151190 item 4 (bounded fix, chain_exec.py +
this suite only; NOT folded into PR #506). Classification record:
hidden_files/chain_exec_hang_2026-11-22/CLASSIFICATION.md.

Defect (at base): `_apply_flow` returns "over" for `>>>`
unconditionally; the execute_range skip loop stops AT the Join
without advancing, `continue` re-enters the same (i, flow) pair,
and the Join is never dispatched — deterministic hang with
unbounded memory growth on a lawful seed shape.

Contract pinned here:
  T1/T2  Both lawful hanging triggers terminate; the Join is
         reached and dispatched exactly once through the canonical
         flat dispatch path; the FlowOver flow is consumed exactly
         once (one flow_taken entry, one boundary message, one
         flow_blocked entry — zero re-evaluations of the same atom).
  T3/T4  Controls unchanged: `>>>` before a non-Join tail, and the
         shipped `>>> 70[Count] >> 61[Join]` shape (cac_i
         K.flow.over / g31 expectations).
  T5     A second `>>>` after the Join still consumes exactly
         once per gap (strict monotonic progress across gaps).
  T7     Mixed shape: a `>>>` whose skip advances past an atom
         leaves the NEXT gap's flow application untouched
         (canonical), and when that next flow is itself a `>>>`
         landing directly on the Join it consumes exactly once.
  T6     No unexpected state mutation: the trigger line's Core II
         state equals the canonical `>`-to-Join line's state on a
         twin program, modulo the one documented difference —
         FlowOver records its boundary in flow_blocked, FlowTo
         does not. The Join carries NO skip receipt anywhere
         (no phantom double skip/receipt).

Isolation: every program uses a uuid-unique owner, so no persisted
state for that owner can exist; T0 verifies the fresh baseline
(empty flow lists) before any execution.
"""
from __future__ import annotations

import uuid

CHECKS: list = []


def check(name, cond, detail=""):
    CHECKS.append((name, bool(cond), str(detail or "")))
    if not cond:
        print(f"FAIL {name} :: {detail}")


def fresh_program(tag):
    from form.open import open_program
    return open_program(f"cef_{tag}_{uuid.uuid4().hex[:12]}")


def run(tag, line):
    from form.mandell.executor import execute_seed
    from form.mandell.core_ii_exec import attach
    p = fresh_program(tag)
    out = execute_seed(p, line)
    return p, out, attach(p)


def receipts(out):
    return [(r.get("dell"), bool(r.get("skipped", False)))
            for r in (out.get("atom_results") or [])]


def boundary_msgs(out):
    return sum(1 for m in (out.get("messages") or [])
               if "FlowOver boundary" in str(m))


def control_t0_isolation():
    from form.mandell.core_ii_exec import attach
    p = fresh_program("t0")
    st = attach(p)
    check("T0.fresh-baseline", st.flow_taken == [] and st.flow_blocked == [],
          f"taken={st.flow_taken} blocked={st.flow_blocked}")


def control_t1_trigger_min():
    _, out, st = run("t1", "51[Select] >>> 61[Join]")
    check("T1.terminates-ok", out.get("ok") is True, out.get("ok"))
    check("T1.ran", out.get("chain_ran") == [51, 61], out.get("chain_ran"))
    check("T1.skipped", out.get("chain_skipped") == [], out.get("chain_skipped"))
    check("T1.receipts", receipts(out) == [(51, False), (61, False)],
          receipts(out))
    check("T1.flow-consumed-once",
          list(st.flow_taken) == [">>>:FlowOver"]
          and list(st.flow_blocked) == ["FlowOver"]
          and boundary_msgs(out) == 1,
          f"taken={st.flow_taken} blocked={st.flow_blocked} "
          f"msgs={boundary_msgs(out)}")


def control_t2_trigger_mid():
    _, out, st = run("t2", "51[Select] > 70[Count] >>> 61[Join]")
    check("T2.terminates-ok", out.get("ok") is True, out.get("ok"))
    check("T2.ran", out.get("chain_ran") == [51, 70, 61], out.get("chain_ran"))
    check("T2.skipped", out.get("chain_skipped") == [], out.get("chain_skipped"))
    check("T2.receipts",
          receipts(out) == [(51, False), (70, False), (61, False)],
          receipts(out))
    check("T2.flow-consumed-once",
          list(st.flow_taken).count(">>>:FlowOver") == 1
          and boundary_msgs(out) == 1,
          f"taken={st.flow_taken} msgs={boundary_msgs(out)}")


def control_t3_control_tail():
    _, out, st = run("t3", "51[Select] >>> 70[Count]")
    check("T3.ran", out.get("chain_ran") == [51], out.get("chain_ran"))
    check("T3.skipped", out.get("chain_skipped") == [70],
          out.get("chain_skipped"))
    check("T3.receipts", receipts(out) == [(51, False), (70, True)],
          receipts(out))
    check("T3.flow-consumed-once", list(st.flow_taken) == [">>>:FlowOver"],
          st.flow_taken)


def control_t4_control_shipped():
    _, out, st = run("t4", "51[Select] >>> 70[Count] >> 61[Join]")
    check("T4.ran", out.get("chain_ran") == [51, 61], out.get("chain_ran"))
    check("T4.skipped", out.get("chain_skipped") == [70],
          out.get("chain_skipped"))
    check("T4.receipts",
          receipts(out) == [(51, False), (70, True), (61, False)],
          receipts(out))
    check("T4.flow-taken",
          list(st.flow_taken) == [">>>:FlowOver", ">>:FlowThru"],
          st.flow_taken)


def control_t5_double_over():
    _, out, st = run("t5", "51[Select] >>> 61[Join] >>> 70[Count]")
    check("T5.terminates-ok", out.get("ok") is True, out.get("ok"))
    check("T5.ran", out.get("chain_ran") == [51, 61], out.get("chain_ran"))
    check("T5.skipped", out.get("chain_skipped") == [70],
          out.get("chain_skipped"))
    check("T5.receipts",
          receipts(out) == [(51, False), (61, False), (70, True)],
          receipts(out))
    check("T5.each-gap-once",
          list(st.flow_taken) == [">>>:FlowOver", ">>>:FlowOver"]
          and boundary_msgs(out) == 2,
          f"taken={st.flow_taken} msgs={boundary_msgs(out)}")


def control_t7_over_then_over_at_join():
    # First >>> skips 70 (skip advances >= 1: the NEXT gap's flow
    # must still be applied — canonical); that second >>> lands
    # directly on the Join (skip advances 0: consumed once, Join
    # dispatched, no re-application).
    _, out, st = run("t7", "51[Select] >>> 70[Count] >>> 61[Join]")
    check("T7.terminates-ok", out.get("ok") is True, out.get("ok"))
    check("T7.ran", out.get("chain_ran") == [51, 61], out.get("chain_ran"))
    check("T7.skipped", out.get("chain_skipped") == [70],
          out.get("chain_skipped"))
    check("T7.receipts",
          receipts(out) == [(51, False), (70, True), (61, False)],
          receipts(out))
    check("T7.each-gap-once",
          list(st.flow_taken) == [">>>:FlowOver", ">>>:FlowOver"]
          and boundary_msgs(out) == 2,
          f"taken={st.flow_taken} msgs={boundary_msgs(out)}")


# Core II fields compared for the T6 state-parity check. Excluded:
# flow_taken / flow_blocked (the one documented difference, asserted
# separately), diff_baseline / last_diff / traces (session bookkeeping
# written by the mutation-note machinery, not by atom dispatch).
PARITY_FIELDS = ("selected", "store", "groups", "defs", "aliases",
                 "compositions", "staged", "snapshots", "context",
                 "route", "refs", "weights", "last_error")


def control_t6_state_parity():
    _, out_a, st_a = run("t6a", "51[Select] >>> 61[Join]")
    _, out_b, st_b = run("t6b", "51[Select] > 61[Join]")
    check("T6.ran-parity", out_a.get("chain_ran") == out_b.get("chain_ran"),
          f"{out_a.get('chain_ran')} vs {out_b.get('chain_ran')}")
    check("T6.receipt-parity",
          receipts(out_a) == receipts(out_b),
          f"{receipts(out_a)} vs {receipts(out_b)}")
    diffs = [f for f in PARITY_FIELDS
             if getattr(st_a, f) != getattr(st_b, f)]
    check("T6.core-ii-parity", diffs == [], f"diff fields: {diffs}")
    check("T6.documented-difference",
          list(st_a.flow_blocked) == ["FlowOver"]
          and list(st_b.flow_blocked) == [],
          f"a={st_a.flow_blocked} b={st_b.flow_blocked}")


def main():
    control_t0_isolation()
    control_t1_trigger_min()
    control_t2_trigger_mid()
    control_t3_control_tail()
    control_t4_control_shipped()
    control_t5_double_over()
    control_t6_state_parity()
    control_t7_over_then_over_at_join()
    passed = sum(1 for _, ok, _ in CHECKS if ok)
    failed = len(CHECKS) - passed
    print(f"CHAIN_EXEC_FLOWOVER: {passed} passed, {failed} failed")
    print(f"CHAIN_EXEC_FLOWOVER: {passed}/{len(CHECKS)}")
    return 0 if failed == 0 else 1


def smoke():
    """Regress-compatible entry: True when the suite is green."""
    try:
        main()
    except Exception:
        return False
    return all(ok for _, ok, _ in CHECKS)


if __name__ == "__main__":
    raise SystemExit(main())
