#!/usr/bin/env python3
"""High-value surface helpers bound onto Program without rewriting open.py wholesale."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


def wire_program_methods(program) -> None:
    """Attach act_on_seen / neuroevo / nature / LA / logistic / fourier / stability."""
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
    if not hasattr(program, "la_transform"):
        def _la(kind: str = "rotate", amount: float = 0.1):
            from form.dell_matrix.linear_algebra import program_transform
            return program_transform(program, kind=kind, amount=amount)
        program.la_transform = _la  # type: ignore
    if not hasattr(program, "logistic_tick"):
        def _log(r: Optional[float] = None):
            from form.dell_matrix.logistic_map import logistic_tick
            return logistic_tick(program, r=r)
        program.logistic_tick = _log  # type: ignore
    if not hasattr(program, "logistic_status"):
        def _ls():
            from form.dell_matrix.logistic_map import logistic_status
            return logistic_status()
        program.logistic_status = _ls  # type: ignore
    if not hasattr(program, "fourier_analyze"):
        def _fa(samples: Sequence[float], top: int = 5):
            from form.dell_matrix.fourier import analyze_samples
            return analyze_samples(samples, top=top)
        program.fourier_analyze = _fa  # type: ignore
    if not hasattr(program, "fourier_demo"):
        def _fd():
            from form.dell_matrix.fourier import program_fourier_demo
            return program_fourier_demo(program)
        program.fourier_demo = _fd  # type: ignore
    if not hasattr(program, "eigen_stability"):
        def _es(kind: str = "rotate", amount: float = 0.1):
            from form.dell_matrix.eigen_stability import analyze_transform_stability
            return analyze_transform_stability(kind, amount)
        program.eigen_stability = _es  # type: ignore


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
    p.place("a", "Alpha", x=1, y=0)
    ok = hasattr(p, "act_on_seen") and hasattr(p, "neuroevo") and hasattr(p, "la_transform")
    ok = ok and hasattr(p, "fourier_analyze") and hasattr(p, "eigen_stability")
    r = p.force_tick()
    ok = ok and isinstance(r.get("nature"), dict)
    tr = p.la_transform("rotate", 0.2)
    ok = ok and tr.get("ok")
    lg = p.logistic_tick(3.5)
    ok = ok and "regime" in lg
    from form.dell_matrix.fourier import make_sine
    fa = p.fourier_analyze(make_sine(32, 2.0), top=2)
    ok = ok and fa.get("ok")
    print(f"[{'PASS' if ok else 'FAIL'}] wired + force_tick + la + logistic + fourier")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
