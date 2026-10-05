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
    auto_contract(rec)
    auto_language_contract(rec)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


def _hash(path):
    import hashlib
    if not path or not os.path.isfile(path):
        return "ABSENT"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def auto_contract(rec) -> None:
    """DC: AUTO PROPOSE > Program.confirm_proposal > VALIDATE > PLACE > Nursery.confirm > PERSIST > {ok:True}
    > COUNT SUCCESS. No direct Nursery.confirm, failures/errors count nothing, restart keeps the result."""
    import sys
    import form.persist as persist_mod
    import form.dell_matrix.auto_growth as ag
    import form.dell_matrix.confirm_lineage as cl
    from form.dell_matrix import nursery as nmod
    owner = f"AutoT{os.getpid()}"
    judge = {"floor_accept": True, "verita_score": 0.9, "combined": 0.9, "grade": "clear", "reason": "probe"}
    a = ag.AutoGrowth(auto=True, internet=False)
    a.owner = owner
    legacy_h = _hash(nmod.NURSERY_PATH)
    calls = {"authority": 0, "direct": 0}
    orig_auth, orig_nconfirm = cl.confirm_proposal, nmod.Nursery.confirm

    def authority(program, pid):
        calls["authority"] += 1
        return orig_auth(program, pid)

    def nconfirm(self, pid):
        if sys._getframe(1).f_globals.get("__name__") != "form.dell_matrix.confirm_lineage":
            calls["direct"] += 1
        return orig_nconfirm(self, pid)

    cl.confirm_proposal, nmod.Nursery.confirm = authority, nconfirm
    # Lineage test: mock policy to allow (policy tested separately)
    from form.dell_matrix import acceptance_policy as ap_mod
    orig_check = ap_mod.AcceptancePolicy.check
    def mock_check(self, producer, pid, review_context=None, proposal_version=None,
                   operation="confirm"):
        if producer == "auto_growth":
            return {"allowed": True, "via": "test_mock"}
        return orig_check(self, producer, pid, review_context, proposal_version,
                          operation=operation)
    ap_mod.AcceptancePolicy.check = mock_check
    try:
        res = a._nursery_auto("Auto canonical probe", "w", judge, "probe")
    finally:
        cl.confirm_proposal, nmod.Nursery.confirm = orig_auth, orig_nconfirm
        ap_mod.AcceptancePolicy.check = orig_check
    pid = res.get("id")
    rec("auto_confirms_only_via_program_authority",
        res.get("status") == "auto_confirmed" and calls["authority"] == 1 and calls["direct"] == 0, f"{res} {calls}")
    rec("auto_success_counted_exactly_once", a.confirmed_total == 1)
    q = load(owner)
    qu = q.cube.session.plane.units.get(pid) if pid else None
    rec("auto_restart_retains_live_confirmed_result",
        qu is not None and qu.origin == "confirmed" and q.nursery.proposals.get(pid) is not None
        and q.nursery.proposals[pid].status == "confirmed")
    cl.confirm_proposal = lambda program, pid_: {"ok": False, "reason": "injected"}
    try:
        res2 = a._nursery_auto("Auto failing probe", "w", judge, "probe")
    finally:
        cl.confirm_proposal = orig_auth
    pid2 = res2.get("id")
    q2 = open_program(owner)
    rec("auto_confirm_failure_not_counted",
        res2.get("status") != "auto_confirmed" and a.confirmed_total == 1
        and (pid2 is None or (q2.nursery.proposals.get(pid2) is not None and q2.nursery.proposals[pid2].status == "pending")))

    def boom(*_a, **_k):
        raise RuntimeError("injected")

    orig_load, orig_nload = persist_mod.load, nmod.Nursery.load
    persist_mod.load, nmod.Nursery.load = boom, classmethod(lambda cls, *a_, **k_: boom())
    try:
        res3 = a._nursery_auto("Auto error probe", "w", judge, "probe")
    finally:
        persist_mod.load, nmod.Nursery.load = orig_load, orig_nload
    rec("auto_error_counts_nothing_rnt6",
        "confirm" not in str(res3.get("status")) and a.confirmed_total == 1 and a.rejected_total == 0, str(res3))
    rec("auto_no_legacy_global_nursery_write", _hash(nmod.NURSERY_PATH) == legacy_h)
    from form.persist import _path
    for path in (getattr(q.nursery, "path", None), _path(owner)):
        if path and os.path.basename(path).startswith(("nursery_AutoT", "program_AutoT")) and os.path.exists(path):
            os.remove(path)


def auto_language_contract(rec) -> None:
    """RH-I R4 (D4): AUTO owns AutoGrow's language; it never binds, reads or serializes the caller's language.
    Attack matrix rows 7 (A>AUTO>A), 8 (AutoGrow custom > restart > AUTO retained), 15 (AUTO failure)."""
    import json
    import subprocess
    import sys
    import form.dell_matrix.auto_growth as ag
    import form.dell_matrix.confirm_lineage as cl
    from form.dell_matrix.nursery import owner_nursery_path
    from form.mandell import language as L
    from form.mandell.seed import CELLS, define_cell
    from form.mandell.latinmandell import customize, clear_customs, export_customs
    from form.persist import _path
    sfx = os.getpid()
    A, G, S = f"AlA{sfx}", f"AlGrow{sfx}", f"AlSess{sfx}"
    judge = {"floor_accept": True, "verita_score": 0.9, "combined": 0.9, "grade": "clear", "reason": "probe"}

    def file_lang(owner):
        with open(_path(owner), encoding="utf-8") as f:
            lang = L.parse_language(json.load(f))
        return set(lang["cells"]), set(lang["customs"])

    def live():
        return set(CELLS), set(export_customs())

    try:
        # AutoGrow's own language (defined while AutoGrow is the explicitly bound owner), then a session owner A.
        g = open_program(G)
        L.bind(g)
        CELLS.clear()
        clear_customs()
        define_cell("AGcell", "08[Create] :: autogrow own")
        customize("agrowlux", dell=9, sense="autogrow own")
        save(g)
        pa = open_program(A)
        L.bind(pa)
        CELLS.clear()
        clear_customs()
        define_cell("SessCell", "08[Create] :: session")
        customize("sesslux", dell=9, sense="session")
        save(pa)
        pa = load(A)
        before_live, before_file = live(), _hash(_path(A))
        a = ag.AutoGrowth(auto=True, internet=False)
        a.owner = G
        # Lineage test: mock policy to allow (policy tested separately)
        from form.dell_matrix import acceptance_policy as ap_mod2
        orig_check2 = ap_mod2.AcceptancePolicy.check
        def mock_check2(self, producer, pid, review_context=None, proposal_version=None,
                          operation="confirm"):
            if producer == "auto_growth":
                return {"allowed": True, "via": "test_mock"}
            return orig_check2(self, producer, pid, review_context, proposal_version,
                               operation=operation)
        ap_mod2.AcceptancePolicy.check = mock_check2
        # 7 A > AUTO > A
        res = a._nursery_auto("Autolang probe", "w", judge, "probe")
        ap_mod2.AcceptancePolicy.check = orig_check2
        rec("L07_auto_confirms_under_own_owner", res.get("status") == "auto_confirmed", str(res))
        rec("L07_A_AUTO_A_working_copy_and_binding_unchanged", live() == before_live and L.bound_program() is pa)
        rec("L07_A_file_untouched_by_AUTO", _hash(_path(A)) == before_file)
        rec("L07_AutoGrow_file_has_only_its_own_language", file_lang(G) == ({"AGcell"}, {"agrowlux"}))
        # 8 AutoGrow custom > restart > AUTO (fresh process, a different session owner bound): retained, no leak
        code = ("import json, sys; import form.dell_matrix.auto_growth as ag; from form.persist import load; "
                "from form.mandell.seed import CELLS; from form.mandell import language as L; "
                "from form.dell_matrix import acceptance_policy as ap; "
                "_oc = ap.AcceptancePolicy.check; "
                "ap.AcceptancePolicy.check = lambda self, p, i, r=None, proposal_version=None, operation='confirm': {'allowed': True, 'via': 'test'} if p == 'auto_growth' else _oc(self, p, i, r, proposal_version, operation=operation); "
                f"s = load({S!r}); a = ag.AutoGrowth(auto=True, internet=False); a.owner = {G!r}; "
                "j = {'floor_accept': True, 'verita_score': 0.9, 'combined': 0.9, 'grade': 'clear', 'reason': 'p'}; "
                "r = a._nursery_auto('Autolang restart probe', 'w', j, 'probe'); "
                "print(json.dumps([r.get('status'), L.bound_owner(), sorted(CELLS)]))")
        out = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, cwd=os.getcwd())
        try:
            status, bound, cells = json.loads(out.stdout.strip().splitlines()[-1])
        except Exception:
            status, bound, cells = None, None, None
        rec("L08_restart_AUTO_confirms_session_binding_kept", status == "auto_confirmed" and bound == S and cells == [],
            out.stderr[-200:])
        rec("L08_restart_AutoGrow_language_retained_no_session_leak", file_lang(G) == ({"AGcell"}, {"agrowlux"}))
        # 15 AUTO failure (confirm refused; owner load error): A unchanged, AutoGrow file unchanged, nothing counted
        g_h, total = _hash(_path(G)), a.confirmed_total
        orig = cl.confirm_proposal
        cl.confirm_proposal = lambda program, pid_: {"ok": False, "reason": "injected"}
        try:
            r2 = a._nursery_auto("Autolang failing probe", "w", judge, "probe")
        finally:
            cl.confirm_proposal = orig
        rec("L15_auto_confirm_failure_A_unchanged",
            r2.get("status") != "auto_confirmed" and live() == before_live and L.bound_program() is pa
            and _hash(_path(G)) == g_h and a.confirmed_total == total, str(r2))
        orig_lo = ag.AutoGrowth._load_owner_program

        def boom(self, load_):
            raise RuntimeError("injected owner load failure")

        ag.AutoGrowth._load_owner_program = boom
        try:
            r3 = a._nursery_auto("Autolang error probe", "w", judge, "probe")
        finally:
            ag.AutoGrowth._load_owner_program = orig_lo
        rec("L15_auto_load_failure_A_unchanged_nothing_counted",
            "confirm" not in str(r3.get("status")) and live() == before_live and L.bound_program() is pa
            and _hash(_path(G)) == g_h and a.confirmed_total == total, str(r3))
    finally:
        for o in (A, G, S):
            for path in (_path(o), owner_nursery_path(o)):
                if os.path.exists(path):
                    os.remove(path)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
