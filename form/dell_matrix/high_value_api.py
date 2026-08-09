#!/usr/bin/env python3
"""High-value surface helpers bound onto Program without rewriting open.py wholesale."""
from __future__ import annotations

from typing import Any, Dict, Optional


def wire_program_methods(program) -> None:
    """Attach act_on_seen / neuroevo / nature_status callables if missing."""
    if not hasattr(program, "act_on_seen"):
        def _act(action: str = "inspect", index: int = 0, extra: str = ""):
            from form.dell_matrix.act_on_seen import act_on_seen as fn
            return fn(program, action=action, index=index, extra=extra)
        program.act_on_seen = _act  # type: ignore
    if not hasattr(program, "list_seen"):
        def _list():
            from form.dell_matrix.act_on_seen import list_seen as fn
            return fn(program)
        program.list_seen = _list  # type: ignore
    if not hasattr(program, "neuroevo"):
        def _neuro(generations: int = 5, seed: int = 42):
            from form.dell_matrix.neuroevo import neuroevo_run
            return neuroevo_run(program, generations=generations, seed=seed)
        program.neuroevo = _neuro  # type: ignore
    if not hasattr(program, "nature_status"):
        def _ns():
            from form.dell_matrix.nature_code import nature_status
            return nature_status()
        program.nature_status = _ns  # type: ignore


def open_wired(owner: str = "Operator"):
    """open_program + nature english seeds + HV methods."""
    from form.open import open_program
    try:
        from form.mandell.nature_english import register
        register()
    except Exception:
        pass
    p = open_program(owner)
    wire_program_methods(p)
    return p


def smoke() -> bool:
    print("=== HIGH_VALUE_API SMOKE ===")
    p = open_wired("HVSmoke")
    p.place("a", "Alpha", x=0, y=2)
    ok = hasattr(p, "act_on_seen") and hasattr(p, "neuroevo")
    r = p.force_tick()
    ok = ok and isinstance(r.get("nature"), dict)
    print(f"[{'PASS' if ok else 'FAIL'}] wired + force_tick nature")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
