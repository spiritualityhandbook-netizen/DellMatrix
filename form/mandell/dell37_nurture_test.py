#!/usr/bin/env python3
"""Dell37 Nurture-authority regression (MPC-011 E).

Proves Dell37 routes to the Nurture (nursery-lifecycle) authority on every
production route, and that the removed Stream leaf branch is not reachable:

- single-atom raw Mandell seed -> Nurture (nursery add/confirm)
- multi-atom chain containing a 37 atom -> Nurture
- _leaf=True re-entry -> Nurture
- 37[Stream] label -> Nurture (term is inert decoration)
- registry names Dell37 "Nurture"
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.mandell.executor import execute_seed
from form.mandell import registry as registry_mod

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _stream_in(messages):
    return any("Stream last" in m for m in messages)


def run_all():
    owner = "D37NurtureReg"
    p = open_program(owner)

    # 1. registry authority
    name = registry_mod.get_dell(37)["name"] if hasattr(registry_mod, "get_dell") else None
    if name is None:
        import form.mandell.registry as R
        name = dict(R.DELLS if hasattr(R, "DELLS") else R.REGISTRY).get(37, {}).get("name")
    check("registry names Dell37 Nurture", name == "Nurture")

    # 2. single-atom raw Mandell -> Nurture (default nursery add, NOT Stream)
    r = execute_seed(p, "37[Stream] :: d37reg1")
    check("single-atom 37 routes to Nurture, not Stream",
          not _stream_in(r["messages"]) and r.get("ok") is True)

    # 3. multi-atom chain -> Nurture (single trailing label; >> is the flow op)
    r = execute_seed(p, "08[Create] >> 37[Nurture] :: d37reg3")
    check("multi-atom 37 routes to Nurture, not Stream",
          r.get("ok") is True and not _stream_in(r["messages"]))

    # 4. _leaf=True re-entry -> Nurture
    r = execute_seed(p, "37[Stream] :: d37reg4", _leaf=True)
    check("_leaf re-entry routes to Nurture, not Stream",
          not _stream_in(r["messages"]))

    # 5. confirm path is the Nurture authority (honest failure, no Stream)
    r = execute_seed(p, "37[Nurture] :: confirm NOPE_d37")
    check("37 confirm path is Nurture authority",
          r.get("ok") is False and not _stream_in(r["messages"]))

    # 6. nursery state actually mutated by the default add
    ids = [pid for pid, prop in p.nursery.proposals.items()
           if "d37reg" in (prop.label or "")]
    check("Nurture default-add mutated nursery", len(ids) >= 3)

    print(f"D37-NURTURE: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"D37-NURTURE SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
