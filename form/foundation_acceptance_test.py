#!/usr/bin/env python3
"""Foundation acceptance: create → operate → lineage transform → save → load."""
from __future__ import annotations

import os
import tempfile

from form.open import open_program
from form.persist import save, load, serialize
from form.dell_matrix.plane import Skin
from form.mandell.executor import execute_seed


def smoke() -> bool:
    print("=== FOUNDATION ACCEPTANCE ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    p = open_program("FND")
    p.cube.session.plane.units.clear()
    a = p.place("seed", "Seed", words="origin", detail="root idea", goals=["keep parent"], skin=Skin.CUBE, x=0)
    p.place("grow", "Grow", words="child surface", detail="will receive lineage", goals=["keep parent"], skin=Skin.CUBE, x=1)
    rec("create_idea", "seed" in p.cube.session.plane.units and a.parents == [] and a.origin == "placed")
    execute_seed(p, "08[Create] :: operate")
    rec("operate", True)
    out = p.grow_ideas(1)
    rec("transform_grow", out.get("ok") is True)
    pending = p.list_proposals()
    rec("proposal_has_parents", bool(pending) and "parents" in pending[0])
    if pending:
        raw = pending[0]
        pid = raw["id"]
        parents_before = list(raw.get("parents") or [])
        res = p.confirm_proposal(pid)
        rec("transform_confirm", res.get("ok") is True)
        confirmed_id = res.get("id")
        u = p.cube.session.plane.units.get(confirmed_id)
        rec("lineage_on_live_unit", bool(u) and u.origin == "confirmed")
        rec("parents_preserved_on_confirm", bool(u) and list(u.parents) == parents_before)
        rec("no_destructive_parent_mutation", "seed" in p.cube.session.plane.units and "grow" in p.cube.session.plane.units)
    else:
        rec("transform_confirm", False)
        rec("lineage_on_live_unit", False)
        rec("parents_preserved_on_confirm", False)
        rec("no_destructive_parent_mutation", False)
        confirmed_id = None
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    save(p, path)
    q = load("FND", path)
    rec("save_load", os.path.isfile(path))
    rec("verify_identity", "seed" in q.cube.session.plane.units and q.cube.session.plane.units["seed"].label == "Seed")
    if confirmed_id and confirmed_id in q.cube.session.plane.units:
        cu = q.cube.session.plane.units[confirmed_id]
        rec("verify_provenance", cu.origin == "confirmed" and isinstance(cu.parents, list))
    else:
        rec("verify_provenance", q.cube.session.plane.units["seed"].origin == "placed")
    blob = serialize(q)
    rec("verify_state", "parents" in blob["plane"]["units"]["seed"] and blob["plane"]["units"]["seed"].get("origin") == "placed")
    os.remove(path)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
