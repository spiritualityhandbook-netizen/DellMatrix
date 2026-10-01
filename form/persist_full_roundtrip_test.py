#!/usr/bin/env python3
"""Full persist domain roundtrip + checkpoint + Mandell e2e."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile

from form.open import open_program
from form.persist import serialize, save, load, checkpoint, VERSION
from form.persist_rest import DURABLE_KEYS, durable
from form.mandell.language import bind
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
    bind(p)  # Q-022: explicit owner binding before language edits (no adoption)
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
    rec("envelope_version_stamped_current", before.get("version") == VERSION)
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
    version_contract(rec)
    lifecycle_contract(rec)
    for _p in _TMP_PATHS:
        if os.path.exists(_p):
            os.remove(_p)
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


def _fresh(code):
    """Run ``code`` in a fresh interpreter (nothing bound yet); return the JSON printed on its last line."""
    import subprocess
    import sys
    out = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, text=True, cwd=os.getcwd(), timeout=300)
    try:
        return json.loads(out.stdout.strip().splitlines()[-1]), out.stderr[-300:]
    except Exception:
        return None, (out.stdout[-200:] + out.stderr[-300:])


_ANON = ("import json; from form.mandell.seed import CELLS, define_cell; from form.mandell.latinmandell import customize, "
         "export_customs; from form.mandell import language as L; from form.open import open_program; "
         "from form.persist import load, save, serialize, _path; "
         "define_cell('AnonCell', '08[Create] :: anonymous'); customize('anonlux', dell=9, sense='anonymous'); ")


def lifecycle_contract(rec) -> None:
    """LLH-I L1-L5 (Q-022 no adoption, Q-023 reads never bind, Q-024 clone keeps the caller's binding, strong
    _BINDING kept, attach_language gone). Unbound cases run in fresh processes (nothing bound yet)."""
    import gc
    import glob
    import subprocess
    import sys
    import weakref
    from form.mandell import language as L
    from form.mandell.canonical import clone_program, freeze_program, cheat_project
    from form.mandell import core_i_recovery
    from form.mandell.latinmandell import export_customs
    from form.persist import _path, _STATE_DIR
    from form.dell_matrix.nursery import owner_nursery_path
    sfx = os.getpid()
    A, X, F, R, G, Q = (f"LcA{sfx}", f"LcX{sfx}", f"LcF{sfx}", f"LcR{sfx}", f"LcG{sfx}", f"LcQ{sfx}")
    owners = [A, X, F, R, G, Q]
    try:
        # owners A and X with their OWN language (defined while explicitly bound)
        for o, cell, lux in ((A, "CellA", "aluxlc"), (X, "CellX", "xluxlc")):
            p = open_program(o)
            L.bind(p)
            CELLS.clear()
            clear_customs()
            define_cell(cell, "08[Create] :: " + cell)
            customize(lux, dell=9, sense="own " + o)
            save(p)
        # L1 NO_ADOPT: anonymous edits > serialize/save/freeze/checkpoint/bind of never-loaded A: A inherits nothing
        got, err = _fresh(_ANON + "from form.mandell.canonical import freeze_program; "
                          f"p = open_program({F!r}); d = serialize(p); b1 = L.bound_owner(); fz = freeze_program(p); "
                          "b2 = L.bound_owner(); save(p); b3 = L.bound_owner(); "
                          f"f = json.load(open(_path({F!r}))); L.bind(p); "
                          "print(json.dumps([sorted(d['mandell_language']['cells']), "
                          "sorted(d['mandell_language']['latin_customs']), "
                          "sorted(fz['mandell_language']['cells']), sorted(f['mandell_language']['cells']), "
                          "sorted(f['mandell_language']['latin_customs']), sorted(f['latinmandell_customs']), [b1, b2, b3], "
                          "sorted(p.language['cells']), sorted(CELLS), sorted(export_customs()), L.bound_owner()]))")
        rec("LC_NO_ADOPT_serialize_freeze_save_inherit_nothing_and_never_bind",
            got == [[], [], [], [], [], [], [None, None, None], [], [], [], F], f"{got} {err}")
        # LOAD: anonymous edits > load persisted owner > only the persisted language
        got, err = _fresh(_ANON + f"p = load({A!r}); "
                          "print(json.dumps([sorted(CELLS), sorted(export_customs()), L.bound_owner()]))")
        rec("LC_LOAD_pre_bind_anon_then_load_persisted_only", got == [["CellA"], ["aluxlc"], A], f"{got} {err}")
        # MISSING LANGUAGE: anonymous edits > load fresh owner (no file) / legacy file without mandell_language
        with open(_path(A), encoding="utf-8") as f:
            legacy = json.load(f)
        legacy.pop("mandell_language")
        legacy["owner"] = G
        legacy["latinmandell_customs"] = {"legacylc": {"label": "legacylc", "dell": 9, "sense": "legacy"}}
        with open(_path(G), "w", encoding="utf-8") as f:
            json.dump(legacy, f)
        got, err = _fresh(_ANON + f"p = load({Q!r}); a = [sorted(CELLS), sorted(export_customs()), L.bound_owner()]; "
                          f"q = load({G!r}); "
                          "print(json.dumps([a, [sorted(CELLS), sorted(export_customs()), L.bound_owner()]]))")
        rec("LC_MISSING_LANGUAGE_empty_cells_legacy_default_customs",
            got == [[[], [], Q], [[], ["legacylc"], G]] and not os.path.exists(_path(Q)), f"{got} {err}")
        # READ INVARIANCE, unbound: every read op leaves the process UNBOUND
        got, err = _fresh(_ANON + "from form.mandell.canonical import freeze_program, cheat_project, clone_program; "
                          "from form.mandell import core_i_recovery, language as LG; from form.persist import checkpoint; "
                          f"p = open_program({F!r}); seen = {{}}; "
                          "ops = {'serialize': lambda: serialize(p), 'freeze': lambda: freeze_program(p), "
                          "'checkpoint': lambda: checkpoint(p), 'core_i_checkpoint': lambda: core_i_recovery.checkpoint(p), "
                          "'metrics_default': lambda: LG.metrics(), 'metrics_program': lambda: LG.metrics(p), "
                          "'harvest_evidence': lambda: LG.harvest_evidence(), 'bound_owner': lambda: L.bound_owner(), "
                          "'clone': lambda: clone_program(p), "
                          "'cheat_project': lambda: cheat_project(p, ['08[Create] :: z'], 'cold')}\n"
                          "for k, f in ops.items():\n    f(); seen[k] = L.bound_program() is None\n"
                          "print(json.dumps(seen))")
        rec("LC_READ_INVARIANCE_unbound_stays_unbound", bool(got) and all(got.values()) and len(got) == 10, f"{got} {err}")
        # READ INVARIANCE, bound A / bound X: BOUND_BEFORE is BOUND_AFTER (identity) for every read op
        from form.persist import checkpoint as p_checkpoint
        pa = load(A)
        pf = open_program(F)
        for bound_label, target in (("A", pa), ("X", None)):
            if target is None:
                target = load(X)
            before = L.bound_program()
            bad = []
            for name, op in (("serialize", lambda: serialize(pa)), ("serialize_other", lambda: serialize(pf)),
                             ("save_prep_other", lambda: save(pf, _tmp_path())), ("freeze", lambda: freeze_program(pa)),
                             ("freeze_other", lambda: freeze_program(pf)), ("checkpoint", lambda: p_checkpoint(pf)),
                             ("core_i_checkpoint", lambda: core_i_recovery.checkpoint(pf)),
                             ("metrics_default", lambda: L.metrics()), ("metrics_other", lambda: L.metrics(pf)),
                             ("harvest_evidence", lambda: L.harvest_evidence())):
                op()
                if L.bound_program() is not before:
                    bad.append(name)
            rec(f"LC_READ_INVARIANCE_bound_{bound_label}_identity_kept", not bad and before is target, str(bad))
        # CLONE (Q-024): bind A > clone A: A; bind X > clone A: X; unbound > clone: unbound; bind(clone) valid
        pa = load(A)
        c1 = clone_program(pa)
        rec("LC_CLONE_bound_A_stays_A", L.bound_program() is pa and c1 is not pa and c1.owner == A
            and set(c1.language["cells"]) == {"CellA"} and set(c1.language["customs"]) == {"aluxlc"})
        px = load(X)
        c2 = clone_program(pa)
        rec("LC_CLONE_bound_X_stays_X_contents_are_A", L.bound_program() is px and set(c2.language["cells"]) == {"CellA"}
            and set(CELLS) == {"CellX"})
        res = cheat_project(pa, ["08[Create] :: z"], "cold")
        rec("LC_CLONE_cheat_project_keeps_binding", L.bound_program() is px and res.get("origin_unchanged") is True)
        L.bind(c2)
        rec("LC_CLONE_explicit_bind_clone_valid", L.bound_program() is c2 and set(CELLS) == {"CellA"}
            and set(export_customs()) == {"aluxlc"})
        got, err = _fresh("import json; from form.mandell import language as L; from form.persist import load; "
                          "from form.mandell.canonical import clone_program; from form.open import open_program; "
                          f"p = open_program({A!r}); c = clone_program(p); a = L.bound_program() is None; "
                          f"q = load({A!r}, activate=False); c2 = clone_program(q); b = L.bound_program() is None; "
                          "print(json.dumps([a, b, sorted(c2.language['cells'])]))")
        rec("LC_CLONE_unbound_stays_unbound", got == [True, True, ["CellA"]], f"{got} {err}")
        # STRONG REFERENCE (kept, RH-I lifetime semantics): bound owner alive without external refs; released on rebind
        pr = open_program(R)
        L.bind(pr)
        wr = weakref.ref(pr)
        del pr
        gc.collect()
        alive_bound = wr() is not None and L.bound_program() is wr()
        L.bind(load(X))
        gc.collect()
        rec("LC_STRONG_REFERENCE_bound_alive_released_on_rebind", alive_bound and wr() is None)
        # ATTACH (L5): the symbol is gone and nothing in form/ defines or calls it
        needle = "attach_" + "language("  # split so this file is not a hit
        refs = [pth for pth in glob.glob(os.path.join(os.path.dirname(L.__file__), "..", "**", "*.py"), recursive=True)
                if needle in open(pth, encoding="utf-8").read()]
        rec("LC_ATTACH_language_symbol_absent", not hasattr(L, "attach_language") and not refs, str(refs))
        # REPL (L2): fresh > explicit bind > customize > save > restart --load > restored
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        s1 = subprocess.run([sys.executable, "-B", "-m", "form.repl", "--owner", R],
                            input="customize zetallh dell 9 sense llh probe\nsave\nquit\n", capture_output=True,
                            text=True, cwd=os.getcwd(), env=env, timeout=300)
        try:
            with open(_path(R), encoding="utf-8") as f:
                saved = sorted(L.parse_language(json.load(f))["customs"])
        except Exception as e:
            saved = [f"ERR {e}"]
        s2 = subprocess.run([sys.executable, "-B", "-m", "form.repl", "--owner", R, "--load"],
                            input="customs\nquit\n", capture_output=True, text=True, cwd=os.getcwd(), env=env, timeout=300)
        rec("LC_REPL_bind_customize_save_restart_restored",
            s1.returncode == 0 and saved == ["zetallh"] and "zetallh" in s2.stdout and s2.returncode == 0,
            f"rc={s1.returncode}/{s2.returncode} saved={saved} {s1.stderr[-160:]}")
    finally:
        for o in owners:
            for path in [_path(o), owner_nursery_path(o)] + glob.glob(os.path.join(_STATE_DIR, f"program_{o}_cp*.json")):
                if os.path.exists(path):
                    os.remove(path)


def version_contract(rec) -> None:
    """RTPH-I R4 (+R4C narrowing): explicit envelope-version contract.

    Matrix: 7 / missing / 1 / 4 / 5 / 6 → ACCEPT (legacy acceptance is explicit and
    history-proven: v1..v6 were each emitted by serialize(); no migration invented);
    8 / -500 / -1 / 0 / "6" / "7" / 6.0 / 7.0 / null / true / false → REJECT LOUDLY
    before any semantic swap. Version 0 and negatives never existed in repository history.
    Every rejection asserts the hard invariant: no binding change, no CELLS/custom change,
    no Program mutation, no file rewrite.
    """
    from form import persist_rest
    from form.persist_rest import _LEGACY_VERSIONS
    from form.mandell import language as L
    from form.mandell.latinmandell import export_customs
    from form.persist import _path
    from form.dell_matrix.nursery import owner_nursery_path
    sfx = os.getpid()
    A = f"VerA{sfx}"
    p = open_program(A)
    L.bind(p)
    CELLS.clear()
    clear_customs()
    define_cell("VerCell", "08[Create] :: vercell")
    customize("verlux", dell=9, sense="version probe")
    save(p)
    a_path = _path(A)
    with open(a_path, encoding="utf-8") as f:
        good = json.load(f)
    rec("version_writer_stamps_current", good.get("version") == VERSION)

    _MISSING = object()
    probes = [
        ("v7", 7, True),
        ("missing", _MISSING, True),
        ("v1", 1, True),
        ("v4", 4, True),
        ("v5", 5, True),
        ("v6", 6, True),
        ("v8", 8, False),
        ("neg500", -500, False),
        ("neg1", -1, False),
        ("v0", 0, False),
        ("str6", "6", False),
        ("str7", "7", False),
        ("float6", 6.0, False),
        ("float7", 7.0, False),
        ("null", None, False),
        ("true", True, False),
        ("false", False, False),
    ]
    tmps = []
    try:
        for name, ver, accept in probes:
            pa = load(A)  # re-anchor before every probe
            anchor = (set(CELLS), set(export_customs()), L.bound_program(), L.bound_owner())
            d = json.loads(json.dumps(good))
            if ver is _MISSING:
                d.pop("version", None)
            else:
                d["version"] = ver
            probe_path = _tmp()
            tmps.append(probe_path)
            with open(probe_path, "w", encoding="utf-8") as f:
                json.dump(d, f)
            h = _sha(probe_path)
            try:
                q = load(A, probe_path)
                outcome = "accepted"
            except persist_rest.ProgramLoadError as e:
                outcome = "rejected"
                q = None
            if accept:
                rec(f"version_{name}_accepted",
                    outcome == "accepted" and q is not None and "VerCell" in set(q.language["cells"]),
                    outcome)
                if ver is _MISSING or ver in _LEGACY_VERSIONS:
                    save(q, probe_path)
                    with open(probe_path, encoding="utf-8") as f:
                        d2 = json.load(f)
                    rec(f"version_{name}_resave_stamps_current", d2.get("version") == VERSION, str(d2.get("version")))
            else:
                after = (set(CELLS), set(export_customs()), L.bound_program(), L.bound_owner())
                rec(f"version_{name}_rejected_loud_no_mutation",
                    outcome == "rejected" and after == anchor and _sha(probe_path) == h,
                    outcome)
    finally:
        for path in tmps:
            if os.path.exists(path):
                os.remove(path)
        for path in (a_path, owner_nursery_path(A)):
            if path and os.path.exists(path):
                os.remove(path)


def _tmp_path():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    _TMP_PATHS.append(path)
    return path


_TMP_PATHS = []


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
