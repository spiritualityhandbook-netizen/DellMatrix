#!/usr/bin/env python3
"""
SUS invariants — runnable hard checks.

12[Test] : 18[Mirror] :: 34[Stamp] :: Invariants
"""

from __future__ import annotations

from typing import List, Tuple
import re
import sys

try:
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.open import open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.core import REQUIRED_FOR_OPEN
except ImportError:
    import os

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from form.mandell.floor import FLOOR, assert_floor_intact
    from form.open import open_program
    from form.dell_matrix.plane import Skin
    from form.dell_matrix.core import REQUIRED_FOR_OPEN

_SEED = re.compile(r"\d{1,2}\[[A-Za-z_]+\]")


def run_invariants() -> Tuple[int, int, List[Tuple[str, bool, str]]]:
    rows: List[Tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        rows.append((name, bool(ok), detail))

    assert_floor_intact()
    check("floor_locked", list(FLOOR) == ["Alpha", "Delta", "Omega", "Omni"])

    p = open_program("Inv")
    check("enhance_default_off", p.enhance.on is False)
    check("sandbox_default_off", p.sandbox.on is False)
    check("ambient_default_off", p.ambient.master_on is False)

    v = p.matrix.verify()
    check("required_snaps", v.get("ok") is True, str(v.get("missing")))

    p.cube.session.plane.units.clear()
    p.place("a", "Business", words="crm routes", skin=Skin.BUILDING, x=1)
    p.place("b", "Music", words="song routes", skin=Skin.SEED, x=-1)
    check("place_connected", not p.cube.session.plane.units["a"].sandboxed)
    check("scope_linked", "b" in p.cube.session.plane.enhance_scope("a"))

    p.sandbox_on()
    check("sandbox_on", p.sandbox.on and p.cube.session.plane.units["a"].sandboxed)
    check("scope_empty_when_boxed", p.cube.session.plane.enhance_scope("a") == [])

    p.sandbox_off()
    check("sandbox_off", (not p.sandbox.on) and (not p.cube.session.plane.units["a"].sandboxed))
    check("scope_restored", "b" in p.cube.session.plane.enhance_scope("a"))

    out = p.grow_ideas(3)
    check("grow_ideas", all(o.get("ok") for o in out))
    check("scores_moved", any(v > 0 for v in p.scores().values()), str(p.scores()))

    check("dual_seed", bool(_SEED.findall("15[Map] >> 50[Manifest]")))

    # ambient intake empty when off
    amb = p.ambient.intake()
    check("ambient_blocked_off", amb.get("ok") is False)

    passed = sum(1 for _, ok, _ in rows if ok)
    return passed, len(rows), rows


def smoke() -> bool:
    print("=== SUS INVARIANTS ===")
    passed, total, rows = run_invariants()
    for name, ok, detail in rows:
        line = f"[{'PASS' if ok else 'FAIL'}] {name}"
        if detail and not ok:
            line += f" | {detail}"
        print(line)
    print(f"=== {passed}/{total} PASS ===")
    return passed == total


def main() -> None:
    if "--smoke" in sys.argv or True:
        sys.exit(0 if smoke() else 1)


if __name__ == "__main__":
    main()
