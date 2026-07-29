#!/usr/bin/env python3
"""Snap L3 smoke."""

from form.dell_matrix.core import DellMatrix, REQUIRED_FOR_OPEN
from form.dell_matrix.snap import SnapCandidate
from form.mandell.manifest import manifest_from_dell
from form.open import open_program


def smoke() -> bool:
    print("=== SNAP L3 SMOKE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r)+1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail else ""))
        r.append(bool(ok))

    bare = DellMatrix()
    rec("bare has Mandell", bare.has_snap("Mandell"))
    rec("bare missing open set", len(bare.verify()["missing"]) > 0)

    p = open_program("SnapL3")
    v = p.matrix.verify()
    rec("open verify ok", v["ok"] is True, str(v.get("missing")))
    rec("all required", all(p.matrix.has_snap(n) for n in REQUIRED_FOR_OPEN))
    rec("all_snaps non-empty", len(p.matrix.all_snaps()) >= 8)
    rec("understand level 3", p.matrix.understand().get("level") == 3)

    bad = p.matrix.snap(SnapCandidate(name="NoManifestTool", kind="tool", manifest=None))
    rec("reject tool without manifest", bad.ok is False)

    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    import sys

    sys.exit(0 if smoke() else 1)
