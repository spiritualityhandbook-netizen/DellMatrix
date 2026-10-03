#!/usr/bin/env python3
"""R2 registry reconciliation (GDP-001 Phase 0, Requirement 2, Obj 0.2.1).

Pins the reconciled Dell registry to the real dispatch code so the two
cannot silently drift apart:

- registry.CORE_I_CLOSABLE == core_i_ops.HANDLED. The MPC-012 "dead leaf"
  Dells (27, 28, 34, 35, 40, 44, 47) are NOT dead: the dispatcher checks
  HANDLED before the leaf, even on _leaf=True chain re-entry. Their old
  leaf arms are shadowed in every production path.
- Every Core I Dell (0-50) has a production dispatch path:
  HANDLED -> core_i_ops.apply_core_i; 21/22 -> live_identity;
  all others -> executor_leaf.execute_seed (branch must exist in source).
  Dell 37 (Nurture) has NO leaf branch by design (MPC-011 Stream->Nurture
  correction; production path is core_i_ops).
- Every Core II Dell (51-99) is dispatched by core_ii_exec into exactly
  one family: QUERY_DELLS / inline 53 / control 60-66 / spectrum 80-99.
- Reserved dells report RESERVED_NOT_ACTIVE; unregistered report
  UNREGISTERED (never silently executable).
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.mandell import registry
from form.mandell import core_i_ops
from form.mandell.query_ops import QUERY_DELLS
from form.mandell.control_runtime import CONTROL_HEADS

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _leaf_source() -> str:
    leaf = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "executor_leaf.py")
    with open(leaf, "r", encoding="utf-8") as f:
        return f.read()


def run_all():
    # 1. The reconciled closable set is exactly the dispatcher's HANDLED set.
    check("CORE_I_CLOSABLE == core_i_ops.HANDLED",
          set(registry.CORE_I_CLOSABLE) == set(core_i_ops.HANDLED))
    check("HANDLED covers the MPC-012 seven + Dell 37",
          set(core_i_ops.HANDLED) == {27, 28, 34, 35, 37, 40, 44, 47})

    # 2. Every Core I Dell has a reconciled standing + dispatch.
    src = _leaf_source()
    for n in range(0, 51):
        st = registry.execution_standing(n)
        check(f"d{n:02d} standing active",
              st["standing"] in ("ACTIVE", "ACTIVE_REFUSAL"))
        check(f"d{n:02d} dispatch recorded", st["dispatch"] != "none")
        if n in core_i_ops.HANDLED:
            check(f"d{n:02d} closable -> core_i_ops",
                  st["dispatch"] == "form/mandell/core_i_ops.py::apply_core_i")
        elif n in (21, 22):
            check(f"d{n:02d} -> live_identity",
                  "live_identity" in st["dispatch"])
        else:
            check(f"d{n:02d} leaf branch exists in source",
                  re.search(rf"(if|elif) primary == {n}:", src) is not None)
    # Dell 37: no leaf branch by design (production path is core_i_ops).
    check("d37 has no leaf branch (Nurture via core_i_ops)",
          re.search(r"(if|elif) primary == 37:", src) is None)
    # Honest refusals keep their standing + named error.
    check("d44 standing ACTIVE_REFUSAL",
          registry.execution_standing(44)["standing"] == "ACTIVE_REFUSAL")
    check("d47 standing ACTIVE_REFUSAL",
          registry.execution_standing(47)["standing"] == "ACTIVE_REFUSAL")
    check("refusal errors named",
          registry.HONEST_REFUSALS == {44: "bridge_unavailable",
                                       47: "embed_unavailable"})

    # 3. Every Core II Dell is dispatched into exactly one family.
    for n in range(51, 100):
        st = registry.execution_standing(n)
        check(f"d{n:02d} core-ii standing active", st["standing"] == "ACTIVE")
        check(f"d{n:02d} dispatch via chain_exec", "chain_exec" in st["dispatch"])
        fams = [n in QUERY_DELLS, n == 53,
                n in registry.CORE_II_CONTROL, 80 <= n <= 99]
        check(f"d{n:02d} exactly one core-ii family", sum(fams) == 1)
    check("registry QUERY family == query_ops.QUERY_DELLS",
          set(registry.CORE_II_QUERY_FAMILY) == set(QUERY_DELLS))
    # Control family 60-66: CONTROL_HEADS open blocks; 61 (Join) is the
    # block tail executed by _run_control, not a head.
    check("control family covers CONTROL_HEADS + 61",
          set(registry.CORE_II_CONTROL) == set(CONTROL_HEADS) | {61})

    # 4. Reserved / unregistered honesty.
    st151 = registry.execution_standing(151)
    check("d151 reserved not active",
          st151["standing"] == "RESERVED_NOT_ACTIVE")
    check("d151 dispatch none", st151["dispatch"] == "none")
    check("d999 reserved (Omega)", registry.execution_standing(999)["standing"] == "RESERVED_NOT_ACTIVE")
    check("d100 unregistered", registry.execution_standing(100)["standing"] == "UNREGISTERED")
    check("d1000 out of range unregistered",
          registry.execution_standing(1000)["standing"] == "UNREGISTERED")
    check("lookup unknown name -> None", registry.lookup("NoSuchDell") is None)
    check("get_dell out of range -> None", registry.get_dell(1000) is None)

    print(f"R2-REGISTRY: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"R2-REGISTRY SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
