#!/usr/bin/env python3
"""Foundation acceptance: create → operate → lineage transform → save → load."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile

from form.open import open_program
from form.dell_matrix import nursery as nursery_mod
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
    owner_isolation(rec)
    lost_update_explicit(rec)
    regress_cli_contract(rec)
    regress_guard_contract(rec)
    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


def _npath(p):
    return getattr(p.nursery, "path", None) or nursery_mod.NURSERY_PATH


def _sha(path):
    if not os.path.isfile(path):
        return "ABSENT"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _status(owner, pid):
    pr = open_program(owner).nursery.proposals.get(pid)
    return pr.status if pr else "ABSENT"


def _cleanup(owner_files, tmp_files=()):
    """Remove per-owner nursery files created by this suite (never the legacy ownerless file) and temp files."""
    for path in owner_files:
        if path and os.path.basename(path).startswith("nursery_") and os.path.exists(path):
            os.remove(path)
    for path in tmp_files:
        if path and os.path.exists(path):
            os.remove(path)


def _tmpjson():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    return path


def owner_isolation(rec) -> None:
    """Per-owner nursery: A/B simultaneous pending, save A/load B, confirm A/reject B, restart, no cross-owner
    overwrite/lookup/confirmation, legacy ownerless nursery.json stranded (not read, not written)."""
    sfx = os.getpid()
    A, B, C = f"OwnA{sfx}", f"OwnB{sfx}", f"OwnC{sfx}"
    legacy = nursery_mod.NURSERY_PATH
    legacy_created = False
    if not os.path.exists(legacy):
        with open(legacy, "w", encoding="utf-8") as f:
            json.dump({"legacy_x": {"id": "legacy_x", "label": "Legacy", "words": "", "kind": "new", "parents": [],
                                    "affinity": 0.0, "reason": "", "created": "x", "status": "pending"}}, f)
        legacy_created = True
    legacy_ids = set()
    try:
        with open(legacy, encoding="utf-8") as f:
            legacy_ids = set((json.load(f) or {}).keys())
    except Exception:
        pass
    legacy_h = _sha(legacy)
    pa, pb = open_program(A), open_program(B)
    snap_a, snap_b = _tmpjson(), _tmpjson()
    try:
        pa_path, pb_path = _npath(pa), _npath(pb)
        rec("owner_paths_distinct_per_owner",
            pa_path != pb_path and os.path.basename(pa_path) == f"nursery_{A}.json"
            and os.path.basename(pb_path) == f"nursery_{B}.json", f"{pa_path} {pb_path}")
        a1 = pa.nursery.add("Owner A idea", parents=[])
        b1 = pb.nursery.add("Owner B idea", parents=[])
        rec("owner_simultaneous_pending",
            pa.nursery.proposals[a1.id].status == "pending" and pb.nursery.proposals[b1.id].status == "pending"
            and _status(A, a1.id) == "pending" and _status(B, b1.id) == "pending")
        rec("owner_no_cross_lookup", a1.id not in pb.nursery.proposals and b1.id not in pa.nursery.proposals
            and _status(B, a1.id) == "ABSENT" and _status(A, b1.id) == "ABSENT")
        hb = _sha(pb_path)
        pb.save(snap_b)
        pa.save(snap_a)
        rec("owner_save_A_does_not_destroy_B", _sha(pb_path) == hb and _status(B, b1.id) == "pending")
        qb = load(B, snap_b)
        rec("owner_load_B_does_not_import_A", a1.id not in qb.nursery.proposals and b1.id in qb.nursery.proposals)
        ra = pa.confirm_proposal(a1.id)
        rec("owner_confirm_A_does_not_confirm_B",
            ra.get("ok") is True and _status(A, a1.id) == "confirmed" and _status(B, b1.id) == "pending"
            and _status(B, a1.id) == "ABSENT")
        cross = open_program(B).confirm_proposal(a1.id)
        rec("owner_no_cross_owner_confirmation", cross.get("ok") is False and _status(B, a1.id) == "ABSENT")
        rb = qb.reject_proposal(b1.id)
        rec("owner_reject_B_does_not_affect_A", rb.get("ok") is True and _status(B, b1.id) == "rejected"
            and _status(A, a1.id) == "confirmed")
        fa, fb = open_program(A), load(B, snap_b)
        rec("owner_restart_restore_preserves_separation",
            fa.nursery.proposals.get(a1.id) is not None and fa.nursery.proposals[a1.id].status == "confirmed"
            and b1.id not in fa.nursery.proposals
            and fb.nursery.proposals.get(b1.id) is not None and fb.nursery.proposals[b1.id].status == "rejected"
            and a1.id not in fb.nursery.proposals)
        pc = open_program(C)
        pc.nursery.add("Owner C idea", parents=[])
        rec("legacy_ownerless_nursery_stranded",
            not (legacy_ids & set(pc.nursery.proposals)) and not (legacy_ids & set(fa.nursery.proposals))
            and _sha(legacy) == legacy_h)
    finally:
        _cleanup([_npath(pa), _npath(pb), _npath(open_program(C))], [snap_a, snap_b])
        if legacy_created and os.path.exists(legacy):
            os.remove(legacy)


def lost_update_explicit(rec) -> None:
    """DB: two live same-owner Program instances must fail explicitly on a real lost update (optimistic
    version check of the owner nursery file), never silently overwrite; fresh instances are unaffected."""
    T = f"Twin{os.getpid()}"
    conflict = getattr(nursery_mod, "NurseryConflictError", None)
    t1, t2 = open_program(T), open_program(T)
    path = _npath(t1)
    try:
        x = t1.nursery.add("Twin first", parents=[])
        raised = False
        try:
            t2.nursery.add("Twin second", parents=[])
        except Exception as e:
            raised = conflict is not None and isinstance(e, conflict)
        with open(path, encoding="utf-8") as f:
            ondisk = json.load(f)
        rec("db_lost_update_fails_explicitly", raised)
        rec("db_no_silent_overwrite",
            x.id in ondisk and not any(v.get("label") == "Twin second" for v in ondisk.values())
            and not any(v.label == "Twin second" for v in t2.nursery.proposals.values()))
        t3 = open_program(T)
        bump = t1.nursery.add("Twin bump", parents=[])
        try:
            r3 = t3.confirm_proposal(x.id)
        except Exception as e:
            r3 = {"ok": False, "reason": f"raised:{type(e).__name__}"}
        rec("db_stale_confirm_refused_stays_pending",
            r3.get("ok") is False and r3.get("reason") == "nursery_conflict" and x.id not in t3.cube.session.plane.units
            and t3.nursery.proposals[x.id].status == "pending" and _status(T, x.id) == "pending", str(r3))
        t4 = open_program(T)
        r4 = t4.confirm_proposal(x.id)
        y = t4.nursery.add("Twin later", parents=[])
        rec("db_fresh_instance_not_false_positive",
            r4.get("ok") is True and _status(T, x.id) == "confirmed" and _status(T, y.id) == "pending")
        stale = False
        try:
            t1.reject_proposal(bump.id)
        except Exception as e:
            stale = conflict is not None and isinstance(e, conflict)
        rec("db_stale_reject_refused", stale and _status(T, bump.id) == "pending"
            and t1.nursery.proposals[bump.id].status == "pending")
    finally:
        _cleanup([path])


def regress_cli_contract(rec) -> None:
    """RH-I R1 (D1): strict regress CLI, NULL M1-M7. Every argument is validated before any entry runs."""
    import contextlib
    import io
    import re
    import shutil
    import subprocess
    import sys
    import form.regress as rg
    calls = []
    orig = rg.run
    rg.run = lambda **kw: (calls.append(kw), True)[1]
    try:
        def main(argv):
            del calls[:]
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = rg.main(list(argv))
            return rc, list(calls), out.getvalue() + err.getvalue()

        bad = [["--twcie"], ["bogus"], ["-twice"], ["--TWICE"], [""], ["--order", "rev", "extra"], ["--"],
               ["--tw"], ["--ord", "rev"], ["--twice", "--", "x"]]
        for argv in bad:
            rc, ran, _ = main(argv)
            rec(f"M1_reject_before_run{argv}", rc == 2 and not ran, f"rc={rc} ran={ran}")
        rc, ran, _ = main(["--order=rev"])
        rec("M2_order_eq_rev_runs_reverse", rc == 0 and ran == [{"order": "rev", "twice": False}], f"{rc} {ran}")
        for argv in (["--help"], ["-h"], ["--twice", "--help"]):
            rc, ran, out = main(argv)
            rec(f"M3_help_usage_no_run{argv}", rc == 0 and not ran and "usage:" in out and "GREEN" not in out, f"{rc} {ran}")
        for argv, want in (([], "(order=fwd)"), (["--twice"], "(order=fwd, twice)"),
                           (["--order", "rev", "--twice"], "(order=rev, twice)"), (["--order=rev"], "(order=rev)")):
            rc, ran, out = main(argv)
            m = re.search(r"REGRESS FINAL: GREEN (\(order=(fwd|rev)(, twice)?\))", out)
            rec(f"M4_final_echoes_mode{argv}", rc == 0 and bool(m) and m.group(1) == want, out[-120:])
        for argv in (["--order", "fwd", "--order", "rev"], ["--twice", "--twice"], ["--order=rev", "--order", "rev"]):
            rc, ran, _ = main(argv)
            rec(f"M5_repeat_or_conflict_rejected{argv}", rc == 2 and not ran, f"{rc} {ran}")
        for argv in (["--order"], ["--order", "REV"], ["--order", "--twice"], ["--order="]):
            rc, ran, _ = main(argv)
            rec(f"M6_bad_order_value_rejected{argv}", rc == 2 and not ran, f"{rc} {ran}")
    finally:
        rg.run = orig
    # Fresh interpreter, real parser, run() stubbed (a broken --help must never recurse into the whole list).
    probe = ("import sys, form.regress as rg; rg.run = lambda **kw: print('RUN_CALLED') or True; "
             "sys.exit(rg.main(sys.argv[1:]))")
    for argv, want in ((["--help"], 0), (["--twcie"], 2)):
        r = subprocess.run([sys.executable, "-B", "-c", probe, *argv], capture_output=True, text=True,
                           cwd=os.getcwd(), timeout=120)
        out = r.stdout + r.stderr
        rec(f"M1_M3_fresh_process{argv}", r.returncode == want and "usage:" in out and "RUN_CALLED" not in out
            and "GREEN" not in out and "Traceback" not in out, f"rc={r.returncode}")
    # M7: through the REAL runner, a state-coupled entry is GREEN once and RED under --twice.
    tmp = tempfile.mkdtemp(prefix="dm_m7_")
    try:
        os.makedirs(os.path.join(tmp, "form"))
        open(os.path.join(tmp, "form", "__init__.py"), "w").close()
        with open(os.path.join(tmp, "form", "zz_coupled_probe.py"), "w", encoding="utf-8") as f:
            f.write("import os\n\ndef smoke():\n    first = not os.path.exists('coupled.marker')\n"
                    "    open('coupled.marker', 'w').close()\n    print('%d/1' % int(first))\n    return first\n")
        entries = ["form.zz_coupled_probe"]
        with contextlib.redirect_stdout(io.StringIO()):
            once = rg.run(entries=entries, intended=entries, src=tmp)
            twice = rg.run(entries=entries, intended=entries, src=tmp, twice=True)
        rec("M7_coupled_entry_green_once_red_twice", once is True and twice is False, f"{once} {twice}")
        rec("M7_runner_never_writes_src", not os.path.exists(os.path.join(tmp, "coupled.marker")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def regress_guard_contract(rec) -> None:
    """LLH-I L6: every regression copy is identifiable (COPY_MARKER) and run() refuses a copy as src BEFORE copying
    or running anything, whatever the entries (default or explicit) and whatever the environment. Probes here are
    harmless (a marker-writing module), so a broken guard turns this RED without recursing."""
    import contextlib
    import glob
    import io
    import shutil
    import form.regress as rg
    tmpdir = tempfile.gettempdir()
    leaked_before = set(glob.glob(os.path.join(tmpdir, "dm_regress_*")))
    src = tempfile.mkdtemp(prefix="dm_guard_src_")
    try:
        os.makedirs(os.path.join(src, "form"))
        open(os.path.join(src, "form", "__init__.py"), "w").close()
        ran_flag = src + ".ran"  # absolute path baked into the probe: proves whether any entry executed
        with open(os.path.join(src, "form", "zz_guard_probe.py"), "w", encoding="utf-8") as f:
            f.write(f"def smoke():\n    open({ran_flag!r}, 'w').close()\n    print('1/1')\n    return True\n")
        dst = rg._copy_tree(src)
        try:
            rec("L6_regress_copy_identifiable", os.path.isfile(os.path.join(dst, "src", rg.COPY_MARKER))
                and not os.path.exists(os.path.join(src, rg.COPY_MARKER)))
        finally:
            shutil.rmtree(dst, ignore_errors=True)
        entries = ["form.zz_guard_probe"]
        with contextlib.redirect_stdout(io.StringIO()):
            plain = rg.run(entries=entries, intended=entries, src=src)
        rec("L6_non_copy_src_runs", plain is True and os.path.exists(ran_flag))
        if os.path.exists(ran_flag):
            os.remove(ran_flag)
        open(os.path.join(src, rg.COPY_MARKER), "w").close()  # src now looks like a regression copy
        saved = {k: os.environ.pop(k) for k in list(os.environ) if k.startswith("DM_REGRESS")}
        try:
            for label, kw in (("explicit_entries", {"entries": entries, "intended": entries}),
                              ("explicit_twice", {"entries": entries, "intended": entries, "twice": True})):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    res = rg.run(src=src, **kw)
                rec(f"L6_copy_src_refused_env_independent[{label}]",
                    res is False and not os.path.exists(ran_flag) and "regression copy" in out.getvalue(),
                    out.getvalue()[-120:])
        finally:
            os.environ.update(saved)
        if os.path.isfile(os.path.join(rg.ROOT, rg.COPY_MARKER)):  # this suite is running inside a regression copy
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                res = rg.run(entries=entries, intended=entries)
            rec("L6_nested_run_inside_copy_refused_default_src", res is False and "regression copy" in out.getvalue())
        rec("L6_no_leaked_regress_copies", set(glob.glob(os.path.join(tmpdir, "dm_regress_*"))) <= leaked_before)
    finally:
        shutil.rmtree(src, ignore_errors=True)
        if os.path.exists(src + ".ran"):
            os.remove(src + ".ran")


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
