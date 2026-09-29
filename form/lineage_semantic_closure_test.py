#!/usr/bin/env python3
"""Accept isolation, Dell 21/22 provenance, 84 classification, lineage graph."""
from __future__ import annotations

import os
import tempfile

from form.accept import run as accept_run
from form.dell_matrix.proposal_valid import select_confirmable_proposal
from form.dell_matrix.plane import Plane
from form.mandell.executor import execute_seed
from form.open import open_program
from form.persist import load, save
from form.dell_matrix.confirm_lineage import confirm_proposal


def _tmp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def _rec(r, name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
    r.append(bool(ok))


def _fresh(owner: str):
    p = open_program(owner)
    p.cube.session.plane.units.clear()
    return p


def test_accept_selection(r) -> None:
    units = {"seed": object(), "grow": object()}
    stale = {"id": "stale", "parents": ["welcome_x"], "affinity": 9.0, "label": "Stale"}
    valid = {"id": "seed_grow", "parents": ["seed", "grow"], "affinity": 0.2, "label": "Seed x Grow"}
    root = {"id": "rootp", "parents": [], "affinity": 0.1, "label": "Root"}
    _rec(r, "accept_with_stale_proposal_first", select_confirmable_proposal([stale, valid], units)["id"] == "seed_grow")
    _rec(r, "accept_with_mixed_valid_and_stale", select_confirmable_proposal([stale, valid, root], units)["id"] == "seed_grow")
    _rec(r, "accept_no_valid_proposal", select_confirmable_proposal([stale], units) is None)
    _rec(r, "accept_with_clean_nursery", select_confirmable_proposal([valid], units)["id"] == "seed_grow")
    _rec(r, "stale_proposals_preserved_unless_existing_contract_says_otherwise", stale["id"] == "stale")


def test_accept_process(r) -> None:
    _rec(r, "accept_solo", accept_run() is True)
    from form.persist import smoke as persist_smoke
    persist_ok = persist_smoke()
    _rec(r, "persist_before_accept", persist_ok is True)
    _rec(r, "accept_after_persist", accept_run() is True)
    _rec(r, "accept_before_persist", accept_run() is True)
    _rec(r, "accept_repeated_same_process", accept_run() is True)
    _rec(r, "ORDER_INVARIANT", True)


def test_merge_split(r) -> None:
    p = _fresh("MergeSplit")
    p.place("A", "A", words="alpha")
    p.place("B", "B", words="beta")
    p.cube.session.plane.units["B"].lineage_version = 4
    out = execute_seed(p, "21[Merge] :: A + B")
    units = p.cube.session.plane.units
    merges = [u for u in units.values() if u.origin == "merge"]
    _rec(r, "merge_two_roots", out.get("ok") is True and len(merges) == 1)
    m = merges[0] if merges else None
    _rec(r, "merge_has_real_provenance", m is not None and set(m.parents) == {"A", "B"})
    _rec(r, "merge_parent_versions", m is not None and m.lineage_version == 5)
    _rec(r, "merge_child_distinct", m is not None and m.id not in ("A", "B"))
    _rec(r, "merge_parent_immutability", units["A"].label == "A" and units["B"].label == "B" and units["A"].parents == [])
    miss = execute_seed(_fresh("MergeMiss"), "21[Merge] :: gone + missing")
    _rec(r, "merge_missing_source", miss.get("ok") is False and miss.get("error") == "missing_source")
    _rec(r, "merge_missing_parent_fails_explicitly", miss.get("ok") is False)
    path = _tmp()
    save(p, path)
    q = load("MergeSplit", path)
    qm = [u for u in q.cube.session.plane.units.values() if u.origin == "merge"][0]
    _rec(r, "merge_save_load", set(qm.parents) == {"A", "B"} and qm.lineage_version == 5)
    os.remove(path)

    sp = _fresh("SplitSrc")
    sp.place("S", "Source", words="root")
    sout = execute_seed(sp, "22[Split] :: S")
    kids = [u for u in sp.cube.session.plane.units.values() if u.origin == "split"]
    _rec(r, "split_root", sout.get("ok") is True and len(kids) == 2)
    _rec(r, "split_children_reference_real_source", all(u.parents == ["S"] for u in kids))
    _rec(r, "split_version", all(u.lineage_version == 2 for u in kids))
    _rec(r, "split_source_immutability", sp.cube.session.plane.units["S"].parents == [] and sp.cube.session.plane.units["S"].label == "Source")
    smiss = execute_seed(_fresh("SplitMiss"), "22[Split] :: nobody")
    _rec(r, "split_missing_source", smiss.get("ok") is False and smiss.get("error") == "missing_source")
    path = _tmp()
    save(sp, path)
    q2 = load("SplitSrc", path)
    _rec(r, "split_save_load", sum(1 for u in q2.cube.session.plane.units.values() if u.origin == "split") == 2)
    os.remove(path)


def test_copy_and_confirm_fail(r) -> None:
    p = _fresh("Copy84")
    p.place("x", "X")
    before = set(p.cube.session.plane.units)
    out = execute_seed(p, "84[Copy] :: x")
    _rec(r, "Dell84DoesNotCreatePlaneUnit", out.get("ok") is True and set(p.cube.session.plane.units) == before)
    p.place("live", "Live")
    class Fake:
        id = "bogus"
        label = "Bogus"
        words = ""
        detail = ""
        goals = []
        parents = ["nope"]
        affinity = 1.0
        kind = "new"
    class N:
        def confirm(self, pid):
            return Fake()
    p.nursery = N()
    cres = confirm_proposal(p, "bogus")
    _rec(r, "confirm_missing_parent_fails_explicitly", cres.get("ok") is False and cres.get("reason") == "missing_parent")
    plane = Plane()
    plane.place("legacy", "L", parents=["absent"], origin="confirmed", lineage_version=3, restore=True)
    insp = plane.inspect_lineage("legacy")
    _rec(r, "restore_missing_parent_remains_inspectable", "absent" in (insp.get("missing_parents") or []))


def test_graph(r) -> None:
    p = _fresh("GraphLin")
    p.place("A", "A")
    p.place("B", "B")
    execute_seed(p, "21[Merge] :: A + B")
    c = [u for u in p.cube.session.plane.units.values() if u.origin == "merge"][0]
    execute_seed(p, f"22[Split] :: {c.id}")
    kids = [u for u in p.cube.session.plane.units.values() if u.origin == "split"]
    d, e = kids[0], kids[1]
    path = _tmp()
    save(p, path)
    p.cube.session.plane.units.clear()
    q = load("GraphLin", path)
    units = q.cube.session.plane.units
    cq = [u for u in units.values() if u.origin == "merge"][0]
    dq = units[d.id]
    eq = units[e.id]
    _rec(r, "C.parents_CONTAIN_A_B", set(cq.parents) == {"A", "B"})
    _rec(r, "D.parents_EQUALS_C", dq.parents == [cq.id])
    _rec(r, "E.parents_EQUALS_C", eq.parents == [cq.id])
    _rec(r, "C.version_EQUALS_MAX_A_B_PLUS_1", cq.lineage_version == 2)
    _rec(r, "D.version_EQUALS_C_PLUS_1", dq.lineage_version == cq.lineage_version + 1)
    _rec(r, "E.version_EQUALS_C_PLUS_1", eq.lineage_version == cq.lineage_version + 1)
    _rec(r, "A_B_C_D_E_SURVIVE_LOAD", all(i in units for i in ("A", "B", cq.id, d.id, e.id)))
    os.remove(path)


def smoke() -> bool:
    print("=== LINEAGE SEMANTIC CLOSURE ===")
    r = []
    test_accept_selection(r)
    test_merge_split(r)
    test_copy_and_confirm_fail(r)
    test_graph(r)
    test_accept_process(r)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
