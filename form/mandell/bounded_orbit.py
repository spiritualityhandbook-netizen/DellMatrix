#!/usr/bin/env python3
"""
Bounded Orbit — coherence recursion for interpretive analysis.

C_{n+1} = C_n² + Δ

Used as a *tracking metaphor / numeric helper* for iterative refinement
under Mandell rules — not a claim of physical or cryptographic proof.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def step(c: float, delta: float) -> float:
    """One orbit step: C' = C² + Δ."""
    return float(c) * float(c) + float(delta)


def orbit(
    c0: float = 0.0,
    delta: float = 0.25,
    steps: int = 8,
    *,
    clamp: Optional[float] = 1.0,
) -> List[float]:
    """
    Iterate Bounded Orbit.
    If clamp is set, values are pulled toward [-clamp, clamp] after each step
    (soft bound — prevents pure explosion in tracking use).
    """
    c = float(c0)
    out = [c]
    for _ in range(max(0, int(steps))):
        c = step(c, delta)
        if clamp is not None:
            lim = abs(float(clamp))
            if c > lim:
                c = lim
            elif c < -lim:
                c = -lim
        out.append(c)
    return out


def coherence_report(
    c0: float = 0.3,
    delta: float = 0.2,
    steps: int = 5,
) -> Dict[str, Any]:
    series = orbit(c0, delta, steps, clamp=1.0)
    return {
        "equation": "C_{n+1} = C_n^2 + Δ",
        "c0": c0,
        "delta": delta,
        "steps": steps,
        "series": series,
        "final": series[-1] if series else c0,
        "note": "Interpretive coherence tracker · not scientific Voynich proof",
    }


def smoke() -> bool:
    print("=== BOUNDED ORBIT SMOKE ===")
    s = orbit(0.2, 0.15, 4, clamp=1.0)
    ok = len(s) == 5 and all(abs(x) <= 1.0 + 1e-9 for x in s)
    print("[PASS]" if ok else "[FAIL]", "orbit clamp", s)
    r = coherence_report()
    print("[PASS]" if "equation" in r else "[FAIL]", "report")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
