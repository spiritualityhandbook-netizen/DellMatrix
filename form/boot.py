#!/usr/bin/env python3
"""
Boot foundation: Mandell → Dell Matrix → DuoBeta self-understand.
"""

from __future__ import annotations
import json
import sys

from form.mandell import assert_floor_intact, floor_status, manifest_from_dell, Manifest
from form.dell_matrix import DellMatrix, SnapCandidate
from form.duobeta import DuoBeta


def boot() -> dict:
    assert_floor_intact()
    dm = DellMatrix()
    duo = DuoBeta(matrix=dm)

    # Snap foundational companions
    dm.snap(
        SnapCandidate(
            name="DuoBeta",
            kind="growth",
            manifest=manifest_from_dell(4, "DuoBeta"),
            payload={"role": "living growth"},
        )
    )
    dm.snap(
        SnapCandidate(
            name="BlankCubePort",
            kind="cube",
            manifest=manifest_from_dell(8, "BlankCube"),
            payload={"blank": True},
        )
    )
    dm.snap(
        SnapCandidate(
            name="MainField",
            kind="main",
            manifest=manifest_from_dell(21, "MainMatrix"),
            payload={"third_space": True, "no_clobber": True},
        )
    )

    duo.evolve("foundation boot")
    return {
        "floor": floor_status(),
        "dell_matrix": dm.status(),
        "duobeta": duo.status(),
    }


def smoke() -> bool:
    print("=== FORM FOUNDATION SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    st = boot()
    rec("floor", st["floor"]["locked"] and st["floor"]["floor"] == ["Alpha", "Delta", "Omega", "Omni"])
    rec("dell matrix self", st["dell_matrix"]["self"] == "DellMatrix")
    rec("ports", st["dell_matrix"]["ports"]["growth"] >= 1 and st["dell_matrix"]["ports"]["cube"] >= 1)
    rec("duobeta gen", st["duobeta"]["generation"] >= 1)
    rec("dell count", st["dell_matrix"]["dell_count"] == 51)

    # reject bad snap
    dm = DellMatrix()
    bad = dm.snap(SnapCandidate(name="x", kind="tool", manifest=None))
    rec("reject tool without manifest", bad.ok is False, bad.reason)

    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


def main():
    if "--smoke" in sys.argv:
        sys.exit(0 if smoke() else 1)
    st = boot()
    print(json.dumps(st, indent=2, default=str))


if __name__ == "__main__":
    main()
