#!/usr/bin/env python3
"""CA01-SET-DETAIL-GOALS regression (MPC-011 G).

The public REPL `set detail` / `set goals` parsers split the FULL input line
and used the second token ("detail"/"goals") as the idea ref — a silent
wrong-target mutation when a decoy idea matched. Fixed to strip the command
prefix first, then split into <ref> <text>.

Proven through the canonical public dispatch (_dispatch_public_line — the same
sequence run() uses), plus save/load persistence.
"""
from __future__ import annotations

import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program, Program
from form.repl import _dispatch_public_line
from form.mandell.executor import execute_seed
from form.dell_matrix.needs import idea_info

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _quiet_dispatch(p, line):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        _dispatch_public_line(p, line, "sdt-test")
    return buf.getvalue()


def run_all():
    p = open_program("SDGReg")
    execute_seed(p, "08[Create] :: sdg_alpha")
    execute_seed(p, "08[Create] :: detail")  # decoy: must never absorb edits

    # 1. set detail reaches the INTENDED target through the public dispatch
    _quiet_dispatch(p, "set detail sdg_alpha hello world")
    a = idea_info(p, "sdg_alpha")
    check("set detail targets intended idea", a.get("detail") == "hello world")

    # 2. decoy untouched
    d = idea_info(p, "detail")
    check("decoy idea not mutated", (d.get("detail") or "") == "")

    # 3. set goals reaches the intended target; multiword + semicolons
    _quiet_dispatch(p, "set goals sdg_alpha g1; g2")
    a = idea_info(p, "sdg_alpha")
    check("set goals targets intended idea", list(a.get("goals") or []) == ["g1", "g2"])

    # 4. missing id -> honest miss naming the REF, not "detail"
    out = _quiet_dispatch(p, "set detail sdg_ghost some text")
    check("missing id names the ref", "sdg_ghost" in out and "idea not found" in out)

    # 5. missing text -> usage, no mutation
    out = _quiet_dispatch(p, "set detail sdg_alpha")
    check("missing text yields usage", "usage:" in out)

    # 6. persistence: save -> fresh load -> detail/goals survive
    p.save()
    p2 = Program.load("SDGReg")
    a2 = idea_info(p2, "sdg_alpha")
    check("detail persists across save/load", a2.get("detail") == "hello world")
    check("goals persist across save/load", list(a2.get("goals") or []) == ["g1", "g2"])

    print(f"SET-DETAIL-GOALS: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"SET-DETAIL-GOALS SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
