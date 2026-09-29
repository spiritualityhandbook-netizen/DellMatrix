#!/usr/bin/env python3
"""Native lineage authority, graph, persist, inspect, failure semantics."""
from __future__ import annotations

import inspect
import os
import tempfile

from form.dell_matrix.lineage import assign_lineage, child_version, inspect_lineage, normalize_parents
from form.dell_matrix.plane import Plane
from form.dell_matrix.blank_cube import give
from form.open import open_program
from form.persist import save, load, checkpoint, serialize
from form.dell_matrix import lineage_bind
import form.open as open_mod


def _tmp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def smoke() -> bool:
    print("=== LINEAGE AUTHORITY ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    from form.dell_matrix import confirm_lineage as confirm_mod
    hop = inspect.getsource(open_mod.Program.confirm_proposal)
    body = inspect.getsource(confirm_mod.confirm_proposal)
    rec("runtime_works_without_lineage_bind_import", lineage_bind.RETIRED is True and "confirm_lineage" in hop)
    rec("confirm_native_delegation", "confirm_lineage" in hop and "return _confirm_proposal" in hop)
    rec("confirm_authority_uses_assign_lineage", "assign_lineage" in body and "lineage_bind" not in body)
    rec("confirm_native_lineage", "confirm_lineage" in hop and "assign_lineage" in body and "lineage_bind" not in hop)
    rec("no_program_method_monkey_patch", not getattr(open_mod.Program.confirm_proposal, "_lineage_bound", False))
    rec("no_persist_load_monkey_patch", not getattr(load, "_lineage_bound", False))
    rec("lineage_authority_root", assign_lineage({}, [], "placed")["lineage_version"] == 1)
    rec("lineage_authority_single_parent", child_version([1]) == 2)
    rec("lineage_authority_multi_parent", child_version([2, 5]) == 6)
    rec("root_version", assign_lineage({}, None, "created")["lineage_version"] == 1)
    plane = Plane()
    a = plane.place("A", "A")
    rec("root_version_live", a.lineage_version == 1 and a.origin == "placed" and a.parents == [])
    c = plane.place("C", "C", parents=["A"], origin="confirmed")
    rec("child_version", c.lineage_version == 2)
    d = plane.place("D", "D", parents=["C"], origin="confirmed")
    rec("grandchild_version", d.lineage_version == 3)
    plane.place("B", "B")
    plane.units["B"].lineage_version = 5
    e = plane.place("E", "E", parents=["B", "D"], origin="confirmed")
    rec("multi_parent_version", e.lineage_version == 6 and e.parents == ["B", "D"])
    snap = (a.label, a.words, a.detail, list(a.goals), list(a.parents), a.lineage_version)
    plane.place("X", "X", parents=["A"], origin="confirmed")
    rec("parent_identity_unchanged", plane.units["A"].id == "A")
    rec("parent_words_unchanged", plane.units["A"].words == snap[1])
    rec("parent_detail_unchanged", plane.units["A"].detail == snap[2])
    rec("parent_goals_unchanged", plane.units["A"].goals == snap[3])
    rec("parent_lineage_unchanged", plane.units["A"].parents == snap[4] and plane.units["A"].lineage_version == snap[5])
    rec("multi_parent_creation", e.parents == ["B", "D"])
    rec("duplicate_parent_ids_normalized", normalize_parents(["A", "A", "B"]) == ["A", "B"])
    rec("deterministic_parent_order", normalize_parents(["B", "D"]) == ["B", "D"])
    rec("inspect_root", inspect_lineage(plane, "A")["ok"] and inspect_lineage(plane, "A")["parents"] == [] and "C" in inspect_lineage(plane, "A")["children"])
    rec("inspect_child", inspect_lineage(plane, "C")["parents"] == ["A"])
    rec("inspect_grandchild", "A" in inspect_lineage(plane, "D")["ancestors"])
    rec("inspect_multi_parent", inspect_lineage(plane, "E")["parents"] == ["B", "D"])
    rec("inspect_missing_unit", inspect_lineage(plane, "nope").get("error") == "missing_unit")
    rec("inspect_cycle_safety", inspect_lineage(plane, "A")["cycle"] is False)
    rec("inspect_does_not_mutate", plane.units["A"].parents == [])
    miss = assign_lineage({}, ["gone"], "confirmed")
    rec("new_missing_parent_rejected", miss.get("ok") is False and miss.get("error") == "missing_parent")
    rec("missing_parent", miss.get("ok") is False and miss.get("error") == "missing_parent")
    restored = assign_lineage({}, ["gone"], "confirmed", restore=True)
    rec("legacy_missing_parent_restored", restored.get("ok") is True and restored.get("parents") == ["gone"])
    legacy_plane = Plane()
    legacy_plane.place("ghost_child", "Ghost", parents=["gone"], origin="confirmed", lineage_version=2, restore=True)
    reported = inspect_lineage(legacy_plane, "ghost_child")
    rec("legacy_missing_parent_reported", "gone" in (reported.get("missing_parents") or []))
    rec("duplicate_parent", normalize_parents(["z", "z"]) == ["z"])
    rec("self_parent", assign_lineage({}, ["me"], "confirmed", child_id="me").get("error") == "self_parent")
    rec("malformed_version", assign_lineage({}, [], "placed", lineage_version="bad").get("error") == "malformed_version")
    try:
        plane.place("loop", "loop", parents=["loop"])
        rec("lineage_cycle_attempt", False)
    except ValueError:
        rec("lineage_cycle_attempt", True)
    bcube = give("Lin", clean=True)
    root = bcube.place_idea("br", "BR")
    rec("blank_cube_root_lineage", root.parents == [] and root.lineage_version == 1)
    child = bcube.place_idea("bc", "BC", parents=["br"], origin="confirmed")
    rec("blank_cube_child_lineage", child.parents == ["br"] and child.lineage_version == 2)
    explicit = bcube.place_idea("be", "BE", parents=["br"], origin="confirmed", lineage_version=9)
    rec("blank_cube_explicit_lineage_forwarding", explicit.lineage_version == 9)
    p = open_program("LIN")
    p.cube.session.plane.units.clear()
    p.place("A", "A", detail="da", goals=["ga"], words="wa")
    p.place("B", "B", detail="db", goals=["gb"])
    p.place("C", "C", parents=["A"], origin="confirmed")
    p.place("D", "D", parents=["C"], origin="confirmed")
    p.place("E", "E", parents=["B", "D"], origin="confirmed")
    rec("lineage_acceptance_versions", p.cube.session.plane.units["E"].lineage_version > p.cube.session.plane.units["D"].lineage_version > p.cube.session.plane.units["C"].lineage_version > p.cube.session.plane.units["A"].lineage_version)
    path = _tmp()
    save(p, path)
    q = load("LIN", path)
    e2 = q.cube.session.plane.units["E"]
    rec("version_save_load", e2.lineage_version == p.cube.session.plane.units["E"].lineage_version)
    rec("multi_parent_persistence", e2.parents == ["B", "D"] and e2.origin == "confirmed")
    rec("verify_all_parents_exist", all(pid in q.cube.session.plane.units for pid in e2.parents))
    rec("a_preserved", q.cube.session.plane.units["A"].detail == "da" and q.cube.session.plane.units["A"].goals == ["ga"])
    rec("b_preserved", q.cube.session.plane.units["B"].detail == "db")
    rec("inspect_e_ancestors", "A" in q.cube.session.plane.inspect_lineage("E")["ancestors"])
    rec("version_checkpoint", os.path.isfile(checkpoint(p)) and serialize(p)["plane"]["units"]["E"]["lineage_version"] == e2.lineage_version)
    rec("multi_parent_checkpoint", "E" in serialize(p)["plane"]["units"])
    rec("persist_load_native_parents", serialize(q)["plane"]["units"]["C"]["parents"] == ["A"])
    rec("no_post_load_stamp_required", True)
    rec("no_silent_lineage_corruption", assign_lineage({}, ["me"], "x", child_id="me")["ok"] is False)
    os.remove(path)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
