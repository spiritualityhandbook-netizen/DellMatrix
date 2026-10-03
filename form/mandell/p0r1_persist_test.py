#!/usr/bin/env python3
"""GDP-001 Phase 0, Requirement 1: PERSISTENCE INTEGRITY (P0R1).

Executable coverage for the five R1 objectives:

  0.1.1  Dell28 rollback/autosave generation-corruption repair
         (copy-on-rollback + re-point; sealed member never written).
  0.1.2  save / load / checkpoint / rollback across fresh OS processes.
  0.1.3  Generation immutability / sealing invariants as executable assertions.
  0.1.4  Interruption / failure / corruption honesty (kill -9, crash
         injection, corrupt/missing members, lost-update refusal).
  0.1.5  Executable guarantees behind docs/PERSISTENCE_CONTRACT.md.

Isolation: every case uses a unique owner (per-owner state files) and the
regress harness runs each suite in a private temp copy of the tree with a
fresh form/state. State files created here are removed at the end.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from form.persist import _STATE_DIR, _path  # noqa: E402
from form.dell_matrix.nursery import (  # noqa: E402
    Nursery,
    NurseryConflictError,
    NurseryLoadError,
    owner_nursery_path,
)
from form.mandell import checkpoint_generation as CG  # noqa: E402
from form.mandell.core_i_recovery import rollback  # noqa: E402
from form.open import open_program  # noqa: E402
from form.mandell.language import bind  # noqa: E402
from form import persist_rest  # noqa: E402


def _owner() -> str:
    return "P0R1_" + uuid.uuid4().hex[:8]


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _member_path(owner: str, receipt: dict, kind: str) -> str:
    return os.path.join(_STATE_DIR, receipt["members"][kind]["file"])


def _fresh_program(owner: str):
    p = open_program(owner)
    bind(p)
    return p


def _run_driver(name: str, code: str, *args: str, timeout: int = 180):
    """Run a driver script in a FRESH OS process rooted at this tree."""
    d = tempfile.mkdtemp(prefix="p0r1drv_")
    script = os.path.join(d, name + ".py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        return subprocess.run(
            [sys.executable, "-B", script, *args],
            cwd=ROOT, capture_output=True, text=True, timeout=timeout,
        )
    finally:
        shutil.rmtree(d, ignore_errors=True)


_DRIVER_PREAMBLE = "import os, sys\nsys.path.insert(0, os.getcwd())\n"


# ---------------------------------------------------------------------------
# 0.1.1 -- rollback corruption repair
# ---------------------------------------------------------------------------

def t_r1_rollback_repoints_to_live(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    first = p.nursery.add("r1 idea", words="w")
    rc = CG.commit_checkpoint(p)
    member_file = rc["members"]["nursery"]["file"]
    p2 = rollback(o)
    live = owner_nursery_path(o)
    ok = os.path.abspath(p2.nursery.path or "") == os.path.abspath(live)
    ok = ok and os.path.basename(p2.nursery.path or "") != member_file
    ok = ok and ".g_" not in os.path.basename(p2.nursery.path or "")
    ok = ok and first.id in p2.nursery.proposals  # rolled-back content intact
    rec("r1_rollback_repoints_to_live", ok,
        f"nursery.path={p2.nursery.path} live={live}")


def t_r1_postrollback_mutation_keeps_member_byte_identical(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    first = p.nursery.add("r1 idea", words="w")
    rc = CG.commit_checkpoint(p)
    gid = rc["generation_id"]
    mpath = _member_path(o, rc, "nursery")
    manifest_sha = rc["members"]["nursery"]["sha256"]
    p2 = rollback(o)
    # Two different mutation paths, both autosave.
    p2.nursery.add("r1 second", words="w2")
    p2.nursery.confirm(first.id)
    ok = _sha256(mpath) == manifest_sha
    # The committed generation still loads, byte-valid.
    p3, rc3 = CG.load_checkpoint(o, activate=False)
    ok = ok and rc3["generation_id"] == gid
    ok = ok and set(p3.nursery.proposals) == {first.id}  # sealed content only
    # ... while the LIVE working file advanced honestly.
    live_props = Nursery.load(owner_nursery_path(o)).proposals
    ok = ok and first.id in live_props and len(live_props) == 2
    ok = ok and live_props[first.id].status == "confirmed"
    rec("r1_postrollback_mutation_keeps_member_byte_identical", ok,
        f"member sha match={_sha256(mpath) == manifest_sha}")


def t_r1_rollback_then_commit_chain_coherent(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("chain idea", words="w")
    rc1 = CG.commit_checkpoint(p)
    p2 = rollback(o)
    rc2 = CG.commit_checkpoint(p2)
    ok = rc2["generation_id"] != rc1["generation_id"]
    ok = ok and rc2["previous_generation_id"] == rc1["generation_id"]
    q, rcq = CG.load_checkpoint(o, activate=False)
    ok = ok and rcq["generation_id"] == rc2["generation_id"]
    # Both retained members still match their manifests.
    for rcx in (rc1, rc2):
        man = CG._read_manifest(o, rcx["generation_id"])
        for kind in ("nursery", "program"):
            mp = os.path.join(_STATE_DIR, man["members"][kind]["file"])
            if os.path.isfile(mp):
                ok = ok and _sha256(mp) == man["members"][kind]["sha256"]
    rec("r1_rollback_then_commit_chain_coherent", ok, "")


# ---------------------------------------------------------------------------
# 0.1.2 -- cross-process proof
# ---------------------------------------------------------------------------

_P1 = _DRIVER_PREAMBLE + """
o = sys.argv[1]
from form.open import open_program
from form.mandell.language import bind
from form.mandell import checkpoint_generation as CG
from form import persist_rest
p = open_program(o); bind(p)
p.place("xunit", "XUnit", words="cross process")
p.nursery.add("xproc idea", words="xp")
persist_rest.save(p)
rc = CG.commit_checkpoint(p)
print("P1_OK", rc["generation_id"], rc["members"]["nursery"]["sha256"], flush=True)
"""

_P2 = _DRIVER_PREAMBLE + """
o = sys.argv[1]
import os
from form.mandell.core_i_recovery import rollback
from form.mandell import checkpoint_generation as CG
from form import persist_rest
from form.dell_matrix.nursery import owner_nursery_path
p2 = rollback(o)
live = owner_nursery_path(o)
assert os.path.abspath(p2.nursery.path) == os.path.abspath(live), "sealed alias survived!"
p2.nursery.add("xproc second", words="xp2")
persist_rest.save(p2)
rc2 = CG.commit_checkpoint(p2)
print("P2_OK", rc2["generation_id"], rc2["previous_generation_id"], flush=True)
"""

_P3 = _DRIVER_PREAMBLE + """
o = sys.argv[1]
from form.mandell import checkpoint_generation as CG
from form import persist_rest
p3, rc3 = CG.load_checkpoint(o, activate=False)
q = persist_rest.load(o)
units = sorted(p3.cube.session.plane.units)
props = sorted(p3.nursery.proposals)
lunits = sorted(q.cube.session.plane.units)
print("P3_OK", rc3["generation_id"], len(units), len(props), len(lunits), flush=True)
print("P3_UNITS", ",".join(units), flush=True)
print("P3_PROPS", ",".join(props), flush=True)
print("P3_LUNITS", ",".join(lunits), flush=True)
"""


def t_r2_xproc_save_checkpoint_rollback_mutate_save_load(rec) -> None:
    o = _owner()
    t0 = time.perf_counter()
    c1 = _run_driver("p1", _P1, o)
    t_save_commit = time.perf_counter() - t0
    ok = c1.returncode == 0 and "P1_OK" in c1.stdout
    g1 = sha1 = None
    if ok:
        _, g1, sha1 = c1.stdout.strip().split()[-3:]
    else:
        rec("r2_xproc_full_cycle", False, f"P1 failed rc={c1.returncode}: {c1.stderr[-400:]}")
        return
    t0 = time.perf_counter()
    c2 = _run_driver("p2", _P2, o)
    t_rollback = time.perf_counter() - t0
    ok = c2.returncode == 0 and "P2_OK" in c2.stdout
    g2 = None
    if ok:
        g2 = c2.stdout.strip().split()[-2]
        ok = c2.stdout.strip().split()[-1] == g1  # previous link correct
    else:
        rec("r2_xproc_full_cycle", False, f"P2 failed rc={c2.returncode}: {c2.stderr[-400:]}")
        return
    # The sealed G1 member survived P2's mutation byte-identical.
    m1 = os.path.join(_STATE_DIR, f"nursery_{CG._owner_ns(o)}.g_{g1}.json")
    # (member filename recorded in manifest; resolve robustly)
    man1 = CG._read_manifest(o, g1)
    m1 = os.path.join(_STATE_DIR, man1["members"]["nursery"]["file"])
    ok = ok and _sha256(m1) == sha1
    t0 = time.perf_counter()
    c3 = _run_driver("p3", _P3, o)
    t_load = time.perf_counter() - t0
    if c3.returncode == 0 and "P3_OK" in c3.stdout:
        lines = {ln.split(" ", 1)[0]: ln.split(" ", 1)[1].strip()
                 for ln in c3.stdout.strip().splitlines() if " " in ln}
        p3ok = lines.get("P3_OK", "").split()
        ok = ok and p3ok[0] == g2  # latest committed is P2's generation
        ok = ok and p3ok[1:] == ["2", "2", "2"]  # units / sealed proposals / live units
        ok = ok and "xunit" in lines.get("P3_UNITS", "").split(",")
        ok = ok and "xunit" in lines.get("P3_LUNITS", "").split(",")
        ok = ok and len(lines.get("P3_PROPS", "").split(",")) == 2
    else:
        ok = False
    rec("r2_xproc_full_cycle", ok,
        f"P1 save+commit {t_save_commit:.2f}s | P2 rollback+mutate {t_rollback:.2f}s | P3 load {t_load:.2f}s"
        + ("" if ok else f" | c3 rc={c3.returncode}: {c3.stderr[-400:]}"))


_PMISS = _DRIVER_PREAMBLE + """
o = sys.argv[1]
from form.mandell.core_i_recovery import rollback
try:
    rollback(o, None)
    print("MISS_FAIL no error", flush=True)
except FileNotFoundError as exc:
    print("MISS_OK", "rollback_missing" in str(exc), flush=True)
"""


def t_r2_xproc_rollback_missing_honest(rec) -> None:
    o = _owner()  # never committed
    c = _run_driver("pmiss", _PMISS, o)
    rec("r2_xproc_rollback_missing_honest",
        c.returncode == 0 and "MISS_OK True" in c.stdout,
        c.stdout.strip()[-80:] + c.stderr.strip()[-200:])


# ---------------------------------------------------------------------------
# 0.1.3 -- sealing invariants (executable)
# ---------------------------------------------------------------------------

def t_r3_member_immutability_battery(rec) -> None:
    """INVARIANT: no sealed generation member is ever written after sealing.

    Battery: commit -> (rollback, mutate nursery, save, commit) x3.
    After every step, every retained member's bytes must match its manifest.
    """
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("inv idea", words="w")
    committed = [CG.commit_checkpoint(p)["generation_id"]]
    ok = True
    for i in range(3):
        q = rollback(o)
        q.nursery.add(f"inv mutation {i}", words="w")
        persist_rest.save(q)
        committed.append(CG.commit_checkpoint(q)["generation_id"])
        # check every retained generation's members against its manifest
        for gid in committed:
            try:
                man = CG._read_manifest(o, gid)
            except CG.CheckpointError:
                continue  # pruned by retention; only retained ones are checked
            for kind in ("nursery", "program"):
                mp = os.path.join(_STATE_DIR, man["members"][kind]["file"])
                if os.path.isfile(mp) and _sha256(mp) != man["members"][kind]["sha256"]:
                    ok = False
    # current generation loads cleanly
    cur, _ = CG.load_checkpoint(o, activate=False)
    ok = ok and cur is not None
    rec("r3_member_immutability_battery", ok,
        f"generations={len(committed)}")


def t_r3_no_alias_ownership(rec) -> None:
    """INVARIANT: after rollback, committed and working state are not aliased."""
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("alias idea", words="w")
    rc = CG.commit_checkpoint(p)
    member_files = {m["file"] for m in rc["members"].values()}
    q = rollback(o)
    qp = os.path.abspath(q.nursery.path or "")
    ok = os.path.basename(qp) not in member_files
    ok = ok and qp == os.path.abspath(owner_nursery_path(o))
    # And the program member is never referenced for writing either:
    # persist.save targets the live program file.
    ok = ok and os.path.abspath(persist_rest.save(q)) == os.path.abspath(_path(o))
    rec("r3_no_alias_ownership", ok, f"nursery.path={q.nursery.path}")


# ---------------------------------------------------------------------------
# 0.1.4 -- interruption / failure / corruption honesty
# ---------------------------------------------------------------------------

_PKILL = _DRIVER_PREAMBLE + """
o = sys.argv[1]
from form.open import open_program
from form.mandell.language import bind
from form import persist_rest
p = open_program(o); bind(p)
for i in range(6000):
    p.place(f"k{i}", f"Kill{i}", words="x" * 200)
persist_rest.save(p)
print("BASELINE_SAVED", flush=True)
persist_rest.save(p, _fail_at="slow_write")  # SIGKILL lands mid-temp-write
print("SHOULD_NOT_PRINT", flush=True)
"""


def t_r4_kill9_mid_save_keeps_previous_complete(rec) -> None:
    o = _owner()
    d = tempfile.mkdtemp(prefix="p0r1kill_")
    script = os.path.join(d, "pkill.py")
    with open(script, "w", encoding="utf-8") as f:
        f.write(_PKILL)
    target = _path(o)
    try:
        proc = subprocess.Popen([sys.executable, "-B", script, o],
                                cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        # wait for baseline save
        baseline_line = proc.stdout.readline().strip()
        if baseline_line != "BASELINE_SAVED":
            proc.kill()
            rec("r4_kill9_mid_save_keeps_previous_complete", False,
                f"driver never reached baseline: {baseline_line} {proc.stderr.read()[-300:]}")
            return
        sha_before = _sha256(target)
        # wait until the slow temp write is actually in flight, then SIGKILL
        deadline = time.time() + 30
        saw_tmp = False
        while time.time() < deadline:
            try:
                names = os.listdir(_STATE_DIR)
            except OSError:
                names = []
            if any(".dmtmp." in n for n in names):
                saw_tmp = True
                break
            if proc.poll() is not None:
                break
            time.sleep(0.02)
        proc.kill()  # SIGKILL
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        rc = proc.returncode
        ok = rc == -signal.SIGKILL and saw_tmp
        # The canonical file is still the previous COMPLETE generation.
        ok = ok and _sha256(target) == sha_before
        data = json.loads(open(target, encoding="utf-8").read())
        ok = ok and isinstance(data, dict) and data.get("type") == "DellMatrixProgramState"
        q = persist_rest.load(o)
        ok = ok and "k0" in q.cube.session.plane.units
        # A subsequent normal save works (no wedged state).
        persist_rest.save(q)
        ok = ok and "k0" in persist_rest.load(o).cube.session.plane.units
        rec("r4_kill9_mid_save_keeps_previous_complete", ok,
            f"rc={rc} saw_tmp={saw_tmp} sha_stable={_sha256(target) == sha_before}")
    finally:
        shutil.rmtree(d, ignore_errors=True)


_PCRASH = _DRIVER_PREAMBLE + """
o = sys.argv[1]
stage = sys.argv[2]
from form.open import open_program
from form.mandell.language import bind
from form.mandell import checkpoint_generation as CG
from form import persist_rest
p = open_program(o); bind(p)
p.nursery.add("crash idea", words="w")
rc = CG.commit_checkpoint(p)
print("G1", rc["generation_id"], flush=True)
p.place("after_unit", "After", words="after")
if stage == "pointer":
    CG.commit_checkpoint(p, _fail_at="crash_pointer")   # dies before pointer swap
else:
    persist_rest.save(p, _fail_at="crash_after_replace")  # dies right after replace
print("SHOULD_NOT_PRINT", flush=True)
"""


def t_r4_crash_before_pointer_swap_previous_authoritative(rec) -> None:
    o = _owner()
    c = _run_driver("pcrash", _PCRASH, o, "pointer")
    g1 = c.stdout.strip().split()[1] if "G1" in c.stdout else None
    ok = c.returncode == 42 and g1 is not None
    # The previous committed generation is still authoritative.
    ok = ok and CG.current_generation_id(o) == g1
    q, rcq = CG.load_checkpoint(o, activate=False)
    ok = ok and rcq["generation_id"] == g1
    rec("r4_crash_before_pointer_swap_previous_authoritative", ok,
        f"rc={c.returncode} current={CG.current_generation_id(o)}")


def t_r4_crash_after_replace_new_generation_honest(rec) -> None:
    o = _owner()
    c = _run_driver("pcrash2", _PCRASH, o, "save")
    ok = c.returncode == 42
    # The new complete generation is honestly loadable (no torn file).
    q = persist_rest.load(o)
    ok = ok and "after_unit" in q.cube.session.plane.units
    rec("r4_crash_after_replace_new_generation_honest", ok, f"rc={c.returncode}")


def t_r4_commit_failure_before_boundary(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("commitfail idea", words="w")
    rc1 = CG.commit_checkpoint(p)
    p.place("doomed_unit", "Doomed", words="d")
    try:
        CG.commit_checkpoint(p, _fail_at="manifest")
        ok = False
    except CG.CheckpointCommitError:
        ok = True
    ok = ok and CG.current_generation_id(o) == rc1["generation_id"]
    q, _ = CG.load_checkpoint(o, activate=False)
    ok = ok and "doomed_unit" not in q.cube.session.plane.units
    rec("r4_commit_failure_before_boundary", ok, "")


def t_r4_corrupt_member_fingerprint_honest(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("corrupt idea", words="w")
    rc = CG.commit_checkpoint(p)
    mpath = _member_path(o, rc, "nursery")
    with open(mpath, "ab") as f:
        f.write(b"X")
    try:
        CG.load_checkpoint(o, activate=False)
        ok = False
    except CG.CheckpointLoadError as exc:
        ok = "fingerprint mismatch" in str(exc)
    rec("r4_corrupt_member_fingerprint_honest", ok, "")


def t_r4_missing_member_honest(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("missing idea", words="w")
    rc = CG.commit_checkpoint(p)
    os.unlink(_member_path(o, rc, "program"))
    try:
        CG.load_checkpoint(o, activate=False)
        ok = False
    except CG.CheckpointLoadError as exc:
        ok = "absent member" in str(exc)
    rec("r4_missing_member_honest", ok, "")


def t_r4_corrupt_manifest_honest(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("manifest idea", words="w")
    rc = CG.commit_checkpoint(p)
    man_path = os.path.join(_STATE_DIR, f"gen_{CG._owner_ns(o)}_{rc['generation_id']}.json")
    with open(man_path, "wb") as f:
        f.write(b"{invalid json")
    try:
        CG.load_checkpoint(o, activate=False)
        ok = False
    except CG.CheckpointLoadError:
        ok = True
    rec("r4_corrupt_manifest_honest", ok, "")


def t_r4_previous_generation_recovery_deterministic(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("rec idea one", words="w")
    rc1 = CG.commit_checkpoint(p)
    p.nursery.add("rec idea two", words="w")
    rc2 = CG.commit_checkpoint(p)
    # Corrupt the CURRENT generation's nursery member.
    with open(_member_path(o, rc2, "nursery"), "ab") as f:
        f.write(b"X")
    q, rcq = CG.load_checkpoint(o, activate=False)
    ok = rcq["generation_id"] == rc1["generation_id"]
    ok = ok and rcq.get("recovered_from") == rc2["generation_id"]
    ok = ok and len(q.nursery.proposals) == 1
    rec("r4_previous_generation_recovery_deterministic", ok,
        f"recovered_from={rcq.get('recovered_from')}")


def t_r4_nursery_lost_update_refused(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("conflict idea", words="w")
    live = owner_nursery_path(o)
    n1 = Nursery.load(live)
    n2 = Nursery.load(live)
    n1.add("n1 idea", words="w")
    try:
        n2.add("n2 idea", words="w")
        ok = False
    except NurseryConflictError:
        ok = True
    rec("r4_nursery_lost_update_refused", ok, "")


def t_r4_corrupt_nursery_file_honest(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    p.nursery.add("honest idea", words="w")
    live = owner_nursery_path(o)
    with open(live, "wb") as f:
        f.write(b'{"truncated": ')
    try:
        n = Nursery.load(live)
        ok = False  # must never silently return an empty nursery
    except NurseryLoadError:
        ok = True
    rec("r4_corrupt_nursery_file_honest", ok, "")


def t_r4_serialize_failure_leaves_target_untouched(rec) -> None:
    from form.dell_matrix.atomic_write import AtomicWriteError
    o = _owner()
    p = _fresh_program(o)
    p.place("ser_unit", "Ser", words="s")
    target = persist_rest.save(p)
    sha_before = _sha256(target)
    try:
        persist_rest.save(p, _fail_at="serialize")
        ok = False
    except AtomicWriteError:
        ok = True
    ok = ok and _sha256(target) == sha_before
    rec("r4_serialize_failure_leaves_target_untouched", ok, "")


# ---------------------------------------------------------------------------
# Performance baseline (Phase-0 §21): recorded, not asserted hard
# ---------------------------------------------------------------------------

def t_perf_baseline(rec) -> None:
    o = _owner()
    p = _fresh_program(o)
    for i in range(200):
        p.place(f"b{i}", f"Bench{i}", words="w" * 40)
        if i % 20 == 0:
            p.nursery.add(f"bench idea {i}", words="w")
    t0 = time.perf_counter(); persist_rest.save(p); t_save = time.perf_counter() - t0
    t0 = time.perf_counter(); persist_rest.load(o); t_load = time.perf_counter() - t0
    t0 = time.perf_counter(); CG.commit_checkpoint(p); t_commit = time.perf_counter() - t0
    t0 = time.perf_counter(); rollback(o); t_rb = time.perf_counter() - t0
    print(f"PERF save={t_save:.3f}s load={t_load:.3f}s commit={t_commit:.3f}s rollback={t_rb:.3f}s")
    rec("perf_baseline_recorded", True, "")


_TESTS = [
    t_r1_rollback_repoints_to_live,
    t_r1_postrollback_mutation_keeps_member_byte_identical,
    t_r1_rollback_then_commit_chain_coherent,
    t_r2_xproc_save_checkpoint_rollback_mutate_save_load,
    t_r2_xproc_rollback_missing_honest,
    t_r3_member_immutability_battery,
    t_r3_no_alias_ownership,
    t_r4_kill9_mid_save_keeps_previous_complete,
    t_r4_crash_before_pointer_swap_previous_authoritative,
    t_r4_crash_after_replace_new_generation_honest,
    t_r4_commit_failure_before_boundary,
    t_r4_corrupt_member_fingerprint_honest,
    t_r4_missing_member_honest,
    t_r4_corrupt_manifest_honest,
    t_r4_previous_generation_recovery_deterministic,
    t_r4_nursery_lost_update_refused,
    t_r4_corrupt_nursery_file_honest,
    t_r4_serialize_failure_leaves_target_untouched,
    t_perf_baseline,
]


def smoke() -> bool:
    print("=== P0R1 PERSISTENCE INTEGRITY ===")
    before = set(os.listdir(_STATE_DIR))
    r = []

    def rec(name, ok, detail=""):
        print(f"[{len(r) + 1}] {name}: {'PASS' if ok else 'FAIL'}" + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    try:
        for t in _TESTS:
            try:
                t(rec)
            except Exception as exc:  # noqa: BLE001 -- honest failure, never silent
                import traceback
                traceback.print_exc()
                rec(t.__name__, False, f"raised {type(exc).__name__}: {exc}")
    finally:
        # Remove only files this suite created.
        for name in set(os.listdir(_STATE_DIR)) - before:
            try:
                os.unlink(os.path.join(_STATE_DIR, name))
            except OSError:
                pass
    print(f"=== RESULT: {sum(r)}/{len(r)} PASS ===")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
