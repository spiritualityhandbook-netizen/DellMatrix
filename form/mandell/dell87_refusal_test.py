#!/usr/bin/env python3
"""Dell87 occupied-destination refusal regression (MPC-011 close, §0).

Semantic authority: KEY RENAME. Occupied destination REFUSES BY DEFAULT:
honest failure, zero mutation, no silent destruction. No overwrite flag.

Cases: source exists + destination absent / source absent /
destination occupied / source == destination / empty destination /
rollback behavior.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.mandell.executor import execute_seed
from form.mandell.core_ii_exec import execute_core_ii

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _get(p, key):
    return execute_seed(p, f"56[Get] :: {key}")["messages"][-1]


def run_all():
    p = open_program("D87Refuse")
    execute_seed(p, "55[Set] :: k=1")
    execute_seed(p, "55[Set] :: z=ZZ")

    # 1. destination occupied -> HONEST FAILURE, zero mutation
    snaps_before = len(p.core_ii.snapshots)
    r = execute_seed(p, "87[Replace] :: k>z")
    check("occupied refuses (ok=False)", r["ok"] is False)
    check("occupied error names the key", r.get("error") == "replace_occupied:z")
    check("occupied receipt honest", "refused" in r["messages"][-1] and "occupied" in r["messages"][-1])
    check("occupied: k unchanged", "Get k='1'" in _get(p, "k"))
    check("occupied: z unchanged", "Get z='ZZ'" in _get(p, "z"))
    check("occupied: zero snapshots pushed", len(p.core_ii.snapshots) == snaps_before)

    # 2. source exists + destination absent -> normal rename works
    r = execute_seed(p, "87[Replace] :: k>q")
    check("normal rename succeeds", r["ok"] is True)
    check("normal rename state", "Get q='1'" in _get(p, "q") and "MISSING" in _get(p, "k"))

    # 3. source absent -> honest failure
    r = execute_seed(p, "87[Replace] :: ghost>z")
    check("missing source fails honest", r["ok"] is False and r.get("error") == "replace_missing:ghost")

    # 4. source == destination -> no-op success (no destruction possible)
    r = execute_seed(p, "87[Replace] :: q>q")
    check("self rename ok", r["ok"] is True)
    check("self rename state intact", "Get q='1'" in _get(p, "q"))

    # 5. empty destination -> legacy fallback unchanged (self-rename, no-op)
    r = execute_seed(p, "87[Replace] :: q>")
    check("empty destination ok", r["ok"] is True)
    check("empty destination state intact", "Get q='1'" in _get(p, "q"))

    # 6. rollback: successful rename restores via Dell96
    execute_seed(p, "87[Replace] :: q>w")
    check("pre-revert w exists", "Get w='1'" in _get(p, "w"))
    msgs = []
    execute_core_ii(p, 96, "Revert", "", msgs)
    check("revert restores q", "Get q='1'" in _get(p, "q"))

    print(f"DELL87-REFUSAL: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"DELL87-REFUSAL SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
