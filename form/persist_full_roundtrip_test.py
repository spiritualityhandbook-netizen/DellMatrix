#!/usr/bin/env python3
"""Full persist domain roundtrip + checkpoint + Mandell e2e."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile

from form.open import open_program
from form.persist import serialize, save, load, checkpoint
from form.persist_rest import DURABLE_KEYS, durable
from form.mandell.seed import CELLS, define_cell, expand_cell
from form.mandell.latinmandell import customize, clear_customs, root_of
from form.mandell.executor import execute_seed
from form.dell_matrix.plane import Skin
from form.avatar import Expression


def _tmp():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def smoke() -> bool:
    print("=== PERSIST FULL ROUNDTRIP ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("persist_import", True)
    p = open_program("RT")
    p.place("u1", "UnitOne", words="w", detail="d1", goals=["g1"], skin=Skin.CUBE, x=2, y=3)
    p.place("u2", "UnitTwo", words="w2", x=4)
    plane = p.cube.session.plane
    plane.box(["u1", "u2"], "box1")
    p.enhance.turn_on()
    p.sandbox.turn_on()
    p.network_url = "https://example.invalid"
    p.ambient.turn_on()
    p.main.tags["ops"] = 1.5
    p.avatar.step(2)
    p.face.set(Expression.JOY)
    p.lattice.to_sphere()
    p.history = ["h1", "h2"]
    p.ux_mode = "builder"
    p.grid_snap = True
    customize("rtlux", dell=9, sense="roundtrip-light")
    define_cell("L0", "08[Create] :: nested")
    define_cell("L1", "{{L0}}")
    execute_seed(p, "08[Create] :: corei")
    execute_seed(p, "51[Select]")
    execute_seed(p, "55[Set] :: rk=7")
    before = serialize(p)
    rec("serialize_load_domain_parity", set(DURABLE_KEYS) <= set(before.keys()))
    rec("mandell_language_version", (before.get("mandell_language") or {}).get("version") == "4")
    rec("mandell_cells_present", "L1" in ((before.get("mandell_language") or {}).get("cells") or {}))
    path = _tmp()
    save(p, path)
    CELLS.clear()
    clear_customs()
    q = load("RT", path)
    after = serialize(q)
    rec("plane_units_sandboxes", "u1" in after["plane"]["units"] and "box1" in after["plane"]["sandboxes"])
    rec("plane_perspective_zoom", after["plane"].get("perspective") == before["plane"].get("perspective"))
    rec("enhance_sandbox", after.get("enhance_on") is True and after.get("sandbox_on") is True)
    rec("network_internet", after.get("network_url") == "https://example.invalid")
    rec("ambient", bool((after.get("ambient") or {}).get("master_on")))
    rec("resonance", isinstance(after.get("resonance"), dict))
    rec("main_tags", (after.get("main") or {}).get("tags", {}).get("ops") == 1.5)
    rec("main_contribution_pull", isinstance((after.get("main") or {}).get("contributions"), list))
    rec("duo_generation", after.get("duo_generation") == before.get("duo_generation"))
    rec("avatar", after.get("avatar", {}).get("expression") == before.get("avatar", {}).get("expression"))
    rec("nursery", isinstance(after.get("nursery"), dict))
    rec("lattice", after.get("lattice", {}).get("form") == before.get("lattice", {}).get("form") or after.get("lattice", {}).get("size") == before.get("lattice", {}).get("size"))
    rec("companion", isinstance(after.get("companion"), dict))
    rec("inspire", isinstance(after.get("inspire"), dict))
    rec("self_knowledge", isinstance(after.get("self_knowledge"), dict))
    rec("ux", after.get("ux", {}).get("grid_snap") is True)
    rec("forces", isinstance(after.get("forces"), dict))
    rec("bimo", isinstance(after.get("bimo"), dict))
    rec("persona_matrix", getattr(q, "persona_lens", None) == getattr(p, "persona_lens", None))
    rec("history", "h1" in (after.get("history") or []))
    rec("latin_customs", root_of("rtlux") is not None)
    rec("mandell_cells", "L1" in CELLS and expand_cell("L1").ok)
    rec("core_ii", isinstance(after.get("core_ii"), dict))
    rec("roundtrip_semantic_equivalence", durable(after)["owner"] == durable(before)["owner"] and durable(after)["version"] == durable(before)["version"])
    cp = checkpoint(p)
    rec("checkpoint_full_state", os.path.isfile(cp) and "mandell_language" in json.load(open(cp)))
    rec("checkpoint_mandell_language", "L1" in json.load(open(cp)).get("mandell_language", {}).get("cells", {}))
    rec("checkpoint_core_ii", "core_ii" in json.load(open(cp)))
    CELLS.clear()
    clear_customs()
    z = load("RT", path)
    rec("mandell_persistence_roundtrip", "L1" in CELLS and expand_cell("L1").ok and root_of("rtlux") is not None)
    rec("execution_eq", execute_seed(z, "12[Test]").get("ok") is not False)
    os.remove(path)
    restore_contract(rec)
    language_owner_contract(rec)
    persist_entry_contract(rec)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


def _sha(path):
    if not path or not os.path.isfile(path):
        return "ABSENT"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _status(owner, pid):
    pr = open_program(owner).nursery.proposals.get(pid)
    return pr.status if pr else "ABSENT"


def _forged(pid, status, parents):
    return {"id": pid, "label": pid, "words": "", "kind": "new", "parents": list(parents), "affinity": 0.0,
            "reason": "forged", "created": "x", "status": status}


def restore_contract(rec) -> None:
    """DA restore: serialized nursery is never a decision source (no forged confirmed, no reverted rejected,
    no foreign import, no nursery write, cross-owner snapshot leaves the other owner's file untouched);
    rollback keeps committed confirmations; the live persisted Program state restores valid semantics."""
    sfx = os.getpid()
    O, B = f"RstA{sfx}", f"RstB{sfx}"
    tmps = []
    p = open_program(O)
    b = open_program(B)
    try:
        p.place("seed", "Seed", words="origin", skin=Skin.CUBE, x=0)
        keep = p.nursery.add("Keep me", parents=[])
        rj = p.nursery.add("Reject me", parents=[])
        snap = _tmp()
        tmps.append(snap)
        save(p, snap)
        p.reject_proposal(rj.id)
        with open(snap, encoding="utf-8") as f:
            d = json.load(f)
        nur = d.setdefault("nursery", {})
        nur["ghostc"] = _forged("ghostc", "confirmed", ["nonexistent"])
        nur["welcome_foreign_1"] = _forged("welcome_foreign_1", "pending", ["welcome"])
        if keep.id in nur:
            nur[keep.id]["status"] = "confirmed"
        with open(snap, "w", encoding="utf-8") as f:
            json.dump(d, f)
        own = getattr(p.nursery, "path", None)
        h_own = _sha(own)
        q = load(O, snap)
        rec("restore_no_forged_confirmed", "ghostc" not in q.nursery.proposals and _status(O, "ghostc") == "ABSENT")
        rec("restore_no_decision_authority",
            q.nursery.proposals.get(keep.id) is not None and q.nursery.proposals[keep.id].status == "pending"
            and q.nursery.proposals.get(rj.id) is not None and q.nursery.proposals[rj.id].status == "rejected"
            and _status(O, keep.id) == "pending" and _status(O, rj.id) == "rejected")
        rec("restore_no_foreign_import_m1", _status(O, "welcome_foreign_1") == "ABSENT"
            and "welcome_foreign_1" not in q.nursery.proposals)
        rec("restore_writes_no_nursery_file", own is not None and _sha(own) == h_own)
        bx = b.nursery.add("B keeps", parents=[])
        snap_b = _tmp()
        tmps.append(snap_b)
        save(b, snap_b)
        bn = b.nursery.add("B newer", parents=[])
        b.reject_proposal(bx.id)
        b_path = getattr(b.nursery, "path", None)
        h_b = _sha(b_path)
        load(O, snap_b)
        rec("restore_cross_owner_snapshot_leaves_owner_file_rnt5",
            b_path is not None and _sha(b_path) == h_b and _status(B, bn.id) == "pending" and _status(B, bx.id) == "rejected")
        c = q.nursery.add("After checkpoint", parents=["seed"])
        snap2 = _tmp()
        tmps.append(snap2)
        save(q, snap2)
        res = q.confirm_proposal(c.id)
        rolled = load(O, snap2)
        rec("rollback_keeps_committed_confirmation_DA",
            res.get("ok") is True and rolled.nursery.proposals.get(c.id) is not None
            and rolled.nursery.proposals[c.id].status == "confirmed" and c.id not in rolled.cube.session.plane.units)
        snap3 = _tmp()
        tmps.append(snap3)
        save(q, snap3)
        z = load(O, snap3)
        zu = z.cube.session.plane.units.get(c.id)
        rec("restore_live_persisted_program_semantics",
            zu is not None and zu.origin == "confirmed" and list(zu.parents) == ["seed"]
            and z.nursery.proposals.get(c.id) is not None and z.nursery.proposals[c.id].status == "confirmed")
    finally:
        for path in (getattr(p.nursery, "path", None), getattr(b.nursery, "path", None)):
            if path and os.path.basename(path).startswith("nursery_") and os.path.exists(path):
                os.remove(path)
        for path in tmps:
            if os.path.exists(path):
                os.remove(path)


def _lang_file(path):
    """Owner language persisted in a program file: (cells, customs) name sets."""
    from form.mandell.language import parse_language
    with open(path, encoding="utf-8") as f:
        lang = parse_language(json.load(f))
    return set(lang["cells"]), set(lang["customs"])


def _live():
    from form.mandell.latinmandell import export_customs
    return set(CELLS), set(export_customs())


def _make_owner(owner, cell, lux):
    """Persist an owner whose OWN language is {cell}/{lux}, defined while that owner is explicitly bound."""
    from form.mandell.language import bind
    from form.persist import _path
    p = open_program(owner)
    bind(p)
    CELLS.clear()
    clear_customs()
    define_cell(cell, "08[Create] :: " + cell.lower())
    customize(lux, dell=9, sense="owner " + owner)
    save(p)
    return _path(owner)


def language_owner_contract(rec) -> None:
    """RH-I R2/R3 (D2/D3/D5/D6): owner-bound language + validate > prepare > swap load. Attack matrix rows
    1-6 and 9-14 (7, 8, 15 = AUTO, in lineage_authority_test). Each row asserts file AND live language."""
    import subprocess
    import sys
    from form.mandell import language as L
    from form.persist import _path
    from form import persist_rest
    sfx = os.getpid()
    A, B, C, M, N = (f"LgA{sfx}", f"LgB{sfx}", f"LgC{sfx}", f"LgBad{sfx}", f"LgNone{sfx}")
    X = f"LgMiss{sfx}"
    owners = [A, B, C, M, N, X]
    pa_path = _make_owner(A, "CA", "alux")
    pb_path = _make_owner(B, "CB", "blux")
    A_LANG, B_LANG = ({"CA"}, {"alux"}), ({"CB"}, {"blux"})
    try:
        # 1 A > load B: B active, A's language kept by A's Program; re-saving A persists A (not B)
        pa = load(A)
        a_live = _live()
        pb = load(B)
        rec("L01_A_then_load_B_B_active", _live() == B_LANG and L.bound_program() is pb and a_live == A_LANG)
        save(pa)
        rec("L01_A_resave_after_B_keeps_A", _lang_file(pa_path) == A_LANG)
        # 2 B > load A (symmetric)
        pa = load(A)
        save(pb)
        rec("L02_B_then_load_A_no_leak", _live() == A_LANG and _lang_file(pb_path) == B_LANG)
        # 3 A customize > save > B load
        pa = load(A)
        customize("aextra", dell=9, sense="a only")
        save(pa)
        pb = load(B)
        rec("L03_A_custom_save_then_B_load",
            "aextra" in _lang_file(pa_path)[1] and "aextra" not in _live()[1] and "aextra" not in _lang_file(pb_path)[1])
        # 4 B customize > save > A load
        customize("bextra", dell=9, sense="b only")
        save(pb)
        pa = load(A)
        rec("L04_B_custom_save_then_A_load",
            "bextra" in _lang_file(pb_path)[1] and "bextra" not in _live()[1] and "bextra" not in _lang_file(pa_path)[1])
        A_LANG = _live()
        # 5 A > malformed B load: loud, nothing changes (active owner, working copy, bound Program, files)
        with open(pb_path, encoding="utf-8") as f:
            good = json.load(f)
        bad_path = _path(M)
        shapes = {
            "cells_list": lambda d: d["mandell_language"].__setitem__("cells", ["CB"]),
            "language_string": lambda d: d.__setitem__("mandell_language", "garbage"),
            "cell_value_not_string": lambda d: d["mandell_language"]["cells"].__setitem__("CB", 7),
            "customs_list": lambda d: d["mandell_language"].__setitem__("latin_customs", ["blux"]),
            "legacy_customs_list": lambda d: d.__setitem__("latinmandell_customs", ["blux"]),
            "missing_program_plane": lambda d: d.pop("plane"),
            "owner_not_string": lambda d: d.__setitem__("owner", 5),
        }
        for name, spoil in shapes.items():
            d = json.loads(json.dumps(good))
            d["owner"] = M
            spoil(d)
            with open(bad_path, "w", encoding="utf-8") as f:
                json.dump(d, f)
            h = _sha(bad_path)
            try:
                load(M)
                raised = ""
            except (L.LanguageLoadError, persist_rest.ProgramLoadError) as e:
                raised = type(e).__name__
            rec(f"L05_malformed_{name}_loud_unchanged",
                bool(raised) and _live() == A_LANG and L.bound_program() is pa and _sha(bad_path) == h, raised)
        with open(bad_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(good)[:200])
        try:
            load(M)
            raised = False
        except ValueError:
            raised = True
        rec("L05_truncated_json_loud_unchanged", raised and _live() == A_LANG and L.bound_program() is pa)
        # 6 A > missing-language B load: empty cells + legacy customs, never A's; missing file: empty/default
        d = json.loads(json.dumps(good))
        d["owner"] = M
        d.pop("mandell_language")
        d["latinmandell_customs"] = {"legacylux": {"label": "legacylux", "dell": 9, "sense": "legacy"}}
        with open(bad_path, "w", encoding="utf-8") as f:
            json.dump(d, f)
        pm = load(M)
        rec("L06_missing_language_key_empty_cells_legacy_customs",
            _live() == (set(), {"legacylux"}) and L.bound_program() is pm and pa.language is not None
            and set(pa.language["cells"]) == A_LANG[0])
        pa = load(A)
        pn = load(N)
        rec("L06_missing_file_fresh_owner_empty", _live() == (set(), set()) and L.bound_owner() == N
            and not os.path.exists(_path(N)))
        save(pn)
        rec("L06_fresh_owner_saved_empty_not_A", _lang_file(_path(N)) == (set(), set()))
        # 9 two owners in one process: edits go to the bound owner; switching back restores; no cross-write
        pa = load(A)
        pb = load(B)
        customize("bonly", dell=9, sense="b edit")
        save(pa)
        save(pb)
        rec("L09_two_owners_edit_lands_in_bound_owner_only",
            "bonly" in _lang_file(pb_path)[1] and "bonly" not in _lang_file(pa_path)[1] and _lang_file(pa_path) == A_LANG)
        L.bind(pa)
        a_back = _live()
        L.bind(pb)
        rec("L09_switch_B_to_A_restores_A_and_back_keeps_B_edit", a_back == A_LANG and "bonly" in _live()[1])
        pc = open_program(C)
        save(pc)
        rec("L09_unbound_other_owner_save_no_leak", _lang_file(_path(C)) == (set(), set()))
        L.bind(pa)
        save(open_program(A))
        rec("L09_D5_same_owner_open_then_save_replaces_with_owner_language", _lang_file(pa_path) == A_LANG)
        # 10 same owner repeated load
        pa1 = load(A)
        pa2 = load(A)
        rec("L10_same_owner_repeated_load", _live() == A_LANG and L.bound_program() is pa2)
        save(pa1)
        rec("L10_same_owner_stale_instance_save_keeps_owner_language", _lang_file(pa_path) == A_LANG)
        # 11 same-owner roundtrip: save > load > save is a fixed point for language
        with open(pa_path, encoding="utf-8") as f:
            before = json.load(f)
        save(load(A))
        with open(pa_path, encoding="utf-8") as f:
            after = json.load(f)
        rec("L11_same_owner_roundtrip_fixed_point",
            before["mandell_language"]["cells"] == after["mandell_language"]["cells"]
            and before["mandell_language"]["latin_customs"] == after["mandell_language"]["latin_customs"]
            and after["latinmandell_customs"] == after["mandell_language"]["latin_customs"])
        # 12 fresh process: load(A) installs exactly A; open without load binds nothing
        code = ("import json; from form.mandell.seed import CELLS; from form.mandell.latinmandell import export_customs; "
                "from form.mandell import language as L; from form.open import open_program; from form.persist import load; "
                f"open_program({A!r}); o = (sorted(CELLS), L.bound_owner()); load({A!r}); "
                "print(json.dumps([o, sorted(CELLS), sorted(export_customs()), L.bound_owner()]))")
        out = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, cwd=os.getcwd())
        try:
            o, cells, customs, owner_now = json.loads(out.stdout.strip().splitlines()[-1])
        except Exception:
            o, cells, customs, owner_now = None, None, None, None
        rec("L12_fresh_process_load_installs_owner_only",
            o == [[], None] and set(cells or []) == A_LANG[0] and set(customs or []) == A_LANG[1] and owner_now == A,
            out.stderr[-200:])
        code = ("import json; from form.mandell.seed import CELLS, define_cell; from form.mandell import language as L; "
                "from form.persist import load; define_cell('Stray', '08[Create] :: unowned'); "
                f"p = load({X!r}); print(json.dumps([sorted(CELLS), sorted(p.language['cells']), L.bound_owner()]))")
        out = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, cwd=os.getcwd())
        try:
            got = json.loads(out.stdout.strip().splitlines()[-1])
        except Exception:
            got = None
        rec("L12_fresh_process_missing_file_load_never_adopts_unowned_state",
            got == [[], [], X] and not os.path.exists(_path(X)), out.stderr[-200:])
        # 13 load failure during PREPARE (after validation): nothing changes
        pa = load(A)
        orig = persist_rest._restore_lattice

        def boom(*_a, **_k):
            raise RuntimeError("injected prepare failure")

        persist_rest._restore_lattice = boom
        try:
            load(B)
            raised = False
        except RuntimeError:
            raised = True
        finally:
            persist_rest._restore_lattice = orig
        rec("L13_prepare_failure_leaves_owner_language_unchanged", raised and _live() == A_LANG and L.bound_program() is pa)
        # 14 owner mismatch: load(A, B's file) never combines A persistence with B language
        ha = _sha(pa_path)
        q = load(A, pb_path)
        rec("L14_owner_mismatch_resolves_to_file_owner_consistently",
            q.owner == B and os.path.basename(q.nursery.path) == f"nursery_{B}.json" and "CA" not in _live()[0]
            and "CB" in _live()[0] and L.bound_program() is q and set(pa.language["cells"]) == A_LANG[0])
        save(q)
        rec("L14_owner_mismatch_save_never_writes_other_owner", _sha(pa_path) == ha and "CB" in _lang_file(pb_path)[0])
    finally:
        from form.dell_matrix.nursery import owner_nursery_path
        for o in owners:
            for path in (_path(o), owner_nursery_path(o)):
                if os.path.exists(path):
                    os.remove(path)


def persist_entry_contract(rec) -> None:
    """RH-I R5: no form.persist <-> form.persist_rest import cycle; explicit module entry (no traceback)."""
    import subprocess
    import sys

    def run(*args):
        r = subprocess.run([sys.executable, "-B", *args], capture_output=True, text=True, cwd=os.getcwd())
        return r.returncode, r.stdout + r.stderr

    for code in ("import form.persist", "import form.persist_rest", "import form.open, form.persist_rest",
                 "from form.persist_rest import load, save", "from form.persist import load, save, serialize, smoke"):
        rc, out = run("-c", code)
        rec(f"R5_import_ok[{code}]", rc == 0 and "Traceback" not in out, out[-160:])
    rc, out = run("-m", "form.persist")
    rec("R5_entry_no_args_usage_no_work",
        rc == 0 and "usage:" in out and "Traceback" not in out and "PASS" not in out, out[-160:])
    rc, out = run("-m", "form.persist", "--bogus")
    rec("R5_entry_unknown_arg_exit2", rc == 2 and "Traceback" not in out, out[-160:])
    rc, out = run("-m", "form.persist_rest")
    rec("R5_rest_entry_same_contract", rc == 0 and "usage:" in out and "Traceback" not in out, out[-160:])


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
