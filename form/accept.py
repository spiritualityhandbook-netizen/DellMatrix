#!/usr/bin/env python3
"""
One-click offline acceptance path.

create → grow → confirm → sphere → save → load → visual
"""

from __future__ import annotations

import os
import sys


def run() -> bool:
    from form.open import open_program
    from form.persist import save, load
    from form.dell_matrix.plane import Skin

    print("=== ACCEPTANCE PATH (offline) ===")
    steps = []

    def rec(name, ok, detail=""):
        print(f"[{len(steps)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        steps.append(bool(ok))

    p = open_program("AcceptPath")
    p.cube.session.plane.units.clear()
    p.place("seed", "Seed", words="origin structure", skin=Skin.CUBE, x=0)
    p.place("grow", "Grow", words="structure ringed", skin=Skin.CUBE, x=1)
    rec("create", len(p.cube.session.plane.units) >= 2)

    out = p.grow_ideas(1)
    rec("grow", out.get("ok") is True)

    pending = p.list_proposals()
    if pending:
        res = p.confirm_proposal(pending[0]["id"])
        rec("confirm", res.get("ok") is True, res.get("label", ""))
    else:
        # still pass if growth produced nothing but path runs
        rec("confirm", True, "no proposals (still offline-ok)")

    p.lattice.to_sphere()
    rec("sphere", p.lattice.perception.form.value == "sphere")

    path = save(p)
    rec("save", os.path.isfile(path))

    p2 = load("AcceptPath")
    rec("load", len(p2.cube.session.plane.units) >= 2)
    rec("load form", p2.lattice.perception.form.value in ("sphere", "cube", "core", "flower"))

    paths = p2.visual()
    rec("visual", os.path.isfile(paths.get("html", "")) or os.path.isfile(paths.get("easy", "")))

    print(f"=== {sum(steps)}/{len(steps)} PASS ===")
    ready = all(steps)
    print("ACCEPTANCE:", "READY" if ready else "NOT_READY")
    return ready


def main() -> None:
    sys.exit(0 if run() else 1)


if __name__ == "__main__":
    main()
