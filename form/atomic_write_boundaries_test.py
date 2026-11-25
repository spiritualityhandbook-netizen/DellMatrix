#!/usr/bin/env python3
"""72-35 — atomic-write failure boundaries: orphan-temp and
rollback cleanup bounds (dedicated failure-injection suite).

Existing coverage (NOT duplicated):
  - dcc_xvii_test: nursery/program SAVE-level byte preservation
    for the serialize/temp_write/replace hooks (S), os.open /
    os.replace faults at the nursery door (L), sweep dead-vs-live
    (V), cross-process crash_before/after_replace and SIGKILL
    mid-write at the save level, load-failure atomicity (T).
  - checkpoint_generation_stress_test (72-29): fsync OSError ->
    AtomicWriteError + target untouched (D3a, helper level),
    member-copy OSError aborts the commit with the previous
    generation authoritative (D3b), dir_fsync_fail receipt at
    the commit level.
  - sm35_pair_atomic_test: per-file atomicity of the everyday
    save pair (72-28 proof circuit).

This suite pins the bounds those suites do not:
  A. the JSON helper's boundary matrix in isolation (injected
     hooks): error type, predecessor bytes, temp disposition
     per boundary — including that the temp_write hook leaves
     a PARTIAL temp by design (the crash simulation) whose
     content is a strict prefix of the intended blob.
  B. fsync failure cleans its temp (D3a pinned the error type
     and the untouched target; the temp disposition was not
     asserted).
  C. the BYTES helper (generation member copies, recovery
     restores) boundary matrix: non-bytes refusal, hooks,
     byte-exact landing of binary (non-UTF8) content — the
     fingerprint property member copies rely on.
  D. crash lifecycle at the helper level, cross-process:
     crash_before_replace leaves exactly one dead-pid orphan
     and the predecessor canonical; crash_after_replace lands
     the new generation with no temp; a real SIGKILL mid
     slow_write leaves the predecessor canonical and a partial
     orphan that the sweep then removes.
  E. sweep semantics beyond dead/live: foreign files and the
     canonical file are never touched; a temp whose pid field
     does not parse is scanned but NEVER removed; a temp
     naming a live-but-unrelated pid is kept (the safe
     direction: never sweep a possibly-live writer); a missing
     directory reports zeros without raising.
  F. aborted generation commit file accounting: a commit
     aborted mid-seal leaves exactly the already-sealed member
     files as orphans (no manifest, pointer unmoved, previous
     generation authoritative), and the NEXT successful
     commit's generation GC reaps them while retaining the
     current and previous generations.
  G. the wiring bound, pinned as observed fact: NO production
     module calls sweep_stale_tmps (census over form/**/*.py
     excluding tests and the defining module) — orphan temps
     are removed only by an explicit sweep call, never as a
     side effect of a save or a load. If a future circuit
     wires the sweep into production, this check fails and
     must be updated deliberately with that circuit.

Labels: INTEGRATION (helper level, temp dirs) + CROSS_PROCESS
(D) + REAL_PROGRAM (F, the real checkpoint authority).
State hygiene: temp directories for A-E; a uuid-unique owner
in the real state dir for F with exact-pattern cleanup;
cleanup failures are reported, never swallowed.
"""
from __future__ import annotations

import ast
import glob
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []
_CLEANUP_ERRORS = []

from form.dell_matrix import atomic_write as AW  # noqa: E402
from form.dell_matrix.atomic_write import (  # noqa: E402
    AtomicWriteError, atomic_write_bytes, atomic_write_json,
    sweep_stale_tmps)

RUN = uuid.uuid4().hex[:8]


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _tmps(d):
    return sorted(p for p in glob.glob(os.path.join(d, "*.dmtmp.*")))


def _attempt(fn):
    """Run fn; return ('ok', value) or ('atomic', None) or
    ('raw:<type>', None)."""
    try:
        return "ok", fn()
    except AtomicWriteError:
        return "atomic", None
    except Exception as exc:  # noqa: BLE001
        return f"raw:{type(exc).__name__}", None


def _seed(d, name="canon.json", blob=b'{"v": 1}'):
    p = os.path.join(d, name)
    with open(p, "wb") as f:
        f.write(blob)
    return p


def _read(p):
    with open(p, "rb") as f:
        return f.read()


# ---------------------------------------------------------------- A
def section_a(d):
    p = _seed(d)
    kind, _ = _attempt(lambda: atomic_write_json(
        p, {"v": 2}, _fail_at="serialize"))
    check("A1.serialize_hook.atomic_error", kind == "atomic", kind)
    check("A1.serialize_hook.bytes_preserved", _read(p) == b'{"v": 1}')
    check("A1.serialize_hook.no_temp", _tmps(d) == [], str(_tmps(d)))

    kind, _ = _attempt(lambda: atomic_write_json(p, {"v": {1, 2}}))
    check("A2.unserializable.atomic_error", kind == "atomic", kind)
    check("A2.unserializable.bytes_preserved", _read(p) == b'{"v": 1}')
    check("A2.unserializable.no_temp", _tmps(d) == [])

    kind, _ = _attempt(lambda: atomic_write_json(
        p, {"v": 2, "pad": "x" * 200}, _fail_at="temp_write"))
    left = _tmps(d)
    check("A3.temp_write.atomic_error", kind == "atomic", kind)
    check("A3.temp_write.bytes_preserved", _read(p) == b'{"v": 1}')
    check("A3.temp_write.partial_temp_left", len(left) == 1,
          str(left))
    if left:
        blob = json.dumps({"v": 2, "pad": "x" * 200},
                          indent=2).encode("utf-8")
        part = _read(left[0])
        check("A3.temp_write.temp_is_strict_prefix",
              len(part) < len(blob) and blob.startswith(part),
              f"part={len(part)} blob={len(blob)}")
        os.unlink(left[0])

    kind, _ = _attempt(lambda: atomic_write_json(
        p, {"v": 2}, _fail_at="replace"))
    check("A4.replace_hook.atomic_error", kind == "atomic", kind)
    check("A4.replace_hook.bytes_preserved", _read(p) == b'{"v": 1}')
    check("A4.replace_hook.no_temp", _tmps(d) == [])

    kind, blob = _attempt(lambda: atomic_write_json(p, {"v": 2}))
    expect = json.dumps({"v": 2}, indent=2).encode("utf-8")
    check("A5.happy.returns_exact_blob",
          kind == "ok" and blob == expect, kind)
    check("A5.happy.target_is_blob", _read(p) == expect)
    check("A5.happy.no_temp", _tmps(d) == [])
    check("A5.happy.dir_fsynced_true",
          AW.atomic_write_json._last_dir_fsynced is True)

    kind, _ = _attempt(lambda: atomic_write_json(
        p, {"v": 3}, _fail_at="dir_fsync_fail"))
    check("A6.dir_fsync_fail.save_succeeds", kind == "ok", kind)
    check("A6.dir_fsync_fail.new_bytes_landed",
          _read(p) == json.dumps({"v": 3}, indent=2).encode("utf-8"))
    check("A6.dir_fsync_fail.receipt_false",
          AW.atomic_write_json._last_dir_fsynced is False)


# ---------------------------------------------------------------- B
def section_b(d):
    p = _seed(d)
    orig_fsync = os.fsync
    calls = {"n": 0}

    def bad_fsync(fd):
        calls["n"] += 1
        raise OSError("injected fsync failure")

    os.fsync = bad_fsync
    try:
        kind, _ = _attempt(lambda: atomic_write_json(p, {"v": 2}))
    finally:
        os.fsync = orig_fsync
    check("B1.fsync_fail.atomic_error", kind == "atomic", kind)
    check("B1.fsync_fail.bytes_preserved", _read(p) == b'{"v": 1}')
    check("B1.fsync_fail.temp_cleaned", _tmps(d) == [],
          str(_tmps(d)))


# ---------------------------------------------------------------- C
def section_c(d):
    p = _seed(d, "member.bin", b"\x00\x01OLD")
    kind, _ = _attempt(lambda: atomic_write_bytes(p, "not-bytes"))
    check("C1.non_bytes.atomic_error", kind == "atomic", kind)
    check("C1.non_bytes.bytes_preserved", _read(p) == b"\x00\x01OLD")

    kind, _ = _attempt(lambda: atomic_write_bytes(
        p, b"\x00\x02NEW", _fail_at="serialize"))
    check("C2.serialize_hook.atomic_error", kind == "atomic", kind)
    check("C2.serialize_hook.bytes_preserved",
          _read(p) == b"\x00\x01OLD")
    check("C2.serialize_hook.no_temp", _tmps(d) == [])

    kind, _ = _attempt(lambda: atomic_write_bytes(
        p, b"\x00\x02NEW" + b"y" * 100, _fail_at="temp_write"))
    left = _tmps(d)
    check("C3.temp_write.atomic_error", kind == "atomic", kind)
    check("C3.temp_write.bytes_preserved", _read(p) == b"\x00\x01OLD")
    check("C3.temp_write.partial_temp_left", len(left) == 1)
    for t in left:
        os.unlink(t)

    orig_replace = os.replace

    def bad_replace(a, b):
        raise OSError("injected replace failure")

    os.replace = bad_replace
    try:
        kind, _ = _attempt(lambda: atomic_write_bytes(p, b"\x00\x02NEW"))
    finally:
        os.replace = orig_replace
    check("C4.replace_fail.atomic_error", kind == "atomic", kind)
    check("C4.replace_fail.bytes_preserved", _read(p) == b"\x00\x01OLD")
    check("C4.replace_fail.temp_cleaned", _tmps(d) == [])

    binary = bytes(range(256)) * 4
    kind, blob = _attempt(lambda: atomic_write_bytes(p, binary))
    check("C5.binary.returns_blob", kind == "ok" and blob == binary,
          kind)
    check("C5.binary.lands_byte_exact", _read(p) == binary)

    kind, _ = _attempt(lambda: atomic_write_bytes(
        p, b"\x03", _fail_at="dir_fsync_fail"))
    check("C6.dir_fsync_fail.receipt_false",
          kind == "ok"
          and AW.atomic_write_bytes._last_dir_fsynced is False,
          kind)


# ---------------------------------------------------------------- D
def _worker(d, mode, blob):
    fd, wpath = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    with open(wpath, "w", encoding="utf-8") as f:
        f.write(
            "import sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from form.dell_matrix.atomic_write import"
            " atomic_write_bytes\n"
            "atomic_write_bytes(sys.argv[2],"
            " sys.argv[3].encode('utf-8'), _fail_at=sys.argv[4])\n"
        )
    target = os.path.join(d, "canon.bin")
    proc = subprocess.run(
        [sys.executable, wpath, REPO, target, blob.decode("ascii"),
         mode],
        capture_output=True, text=True, timeout=120)
    os.unlink(wpath)
    return proc


def section_d(d):
    _seed(d, "canon.bin", b"PRED")
    proc = _worker(d, "crash_before_replace", b"NEWX")
    left = _tmps(d)
    check("D1.crash_before.exit_42", proc.returncode == 42,
          f"rc={proc.returncode}")
    check("D1.crash_before.predecessor_canonical",
          _read(os.path.join(d, "canon.bin")) == b"PRED")
    check("D1.crash_before.exactly_one_orphan", len(left) == 1,
          str(left))
    res = sweep_stale_tmps(d)
    check("D1.crash_before.sweep_removes_orphan",
          res["removed"] == 1 and _tmps(d) == [], str(res))

    proc = _worker(d, "crash_after_replace", b"NEWX")
    check("D2.crash_after.exit_42", proc.returncode == 42,
          f"rc={proc.returncode}")
    check("D2.crash_after.new_bytes_canonical",
          _read(os.path.join(d, "canon.bin")) == b"NEWX")
    check("D2.crash_after.no_temp", _tmps(d) == [])

    # D3: real SIGKILL during a slow write of a large blob
    _seed(d, "canon.bin", b"PRED2")
    fd, wpath = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    with open(wpath, "w", encoding="utf-8") as f:
        f.write(
            "import sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from form.dell_matrix.atomic_write import"
            " atomic_write_bytes\n"
            "atomic_write_bytes(sys.argv[2], b'z' * 4000000,"
            " _fail_at='slow_write')\n"
        )
    target = os.path.join(d, "canon.bin")
    proc = subprocess.Popen([sys.executable, wpath, REPO, target],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    orphan = None
    deadline = time.time() + 20
    while time.time() < deadline:
        left = _tmps(d)
        if left and os.path.getsize(left[0]) > 0:
            orphan = left[0]
            break
        time.sleep(0.05)
    proc.send_signal(signal.SIGKILL)
    proc.wait(timeout=30)
    os.unlink(wpath)
    check("D3.sigkill.temp_observed_mid_write", orphan is not None)
    check("D3.sigkill.predecessor_canonical", _read(target) == b"PRED2")
    left = _tmps(d)
    check("D3.sigkill.partial_orphan_remains", len(left) == 1,
          str(left))
    res = sweep_stale_tmps(d)
    check("D3.sigkill.sweep_removes_orphan",
          res["removed"] == 1 and _tmps(d) == [], str(res))


# ---------------------------------------------------------------- E
def section_e(d):
    canon = _seed(d, "keep.json", b"{}")
    dead = os.path.join(d, "x.json.dmtmp.99999997.deadbeef")
    live = os.path.join(
        d, f"x.json.dmtmp.{os.getpid()}.livebeef")
    foreign = os.path.join(d, "unrelated.txt")
    for pth in (dead, live, foreign):
        with open(pth, "wb") as f:
            f.write(b"partial")
    res = sweep_stale_tmps(d)
    check("E1.sweep.removes_dead_pid", not os.path.exists(dead),
          str(res))
    check("E1.sweep.keeps_live_pid", os.path.exists(live))
    check("E1.sweep.keeps_foreign", os.path.exists(foreign))
    check("E1.sweep.keeps_canonical", _read(canon) == b"{}")

    weird = os.path.join(d, "x.json.dmtmp.notapid.beefbeef")
    with open(weird, "wb") as f:
        f.write(b"partial")
    res = sweep_stale_tmps(d)
    check("E2.unparsable.scanned", res["scanned"] >= 1, str(res))
    check("E2.unparsable.never_removed",
          res["removed"] == 0 and os.path.exists(weird), str(res))

    res = sweep_stale_tmps(os.path.join(d, "does-not-exist"))
    check("E3.missing_dir.zeros_no_raise",
          res == {"scanned": 0, "removed": 0}, str(res))

    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        alien = os.path.join(
            d, f"x.json.dmtmp.{sleeper.pid}.alienbee")
        with open(alien, "wb") as f:
            f.write(b"partial")
        res = sweep_stale_tmps(d)
        check("E4.live_unrelated_pid.kept",
              os.path.exists(alien), str(res))
    finally:
        sleeper.kill()
        sleeper.wait(timeout=30)


# ---------------------------------------------------------------- F
def section_f():
    from form.open import open_program
    from form.persist import _STATE_DIR, _safe_owner
    from form.mandell import checkpoint_generation as CG
    from form.mandell.checkpoint_generation import (
        CheckpointCommitError, committed_generation_state)

    owner = f"T7235F{RUN}"
    state = Path(_STATE_DIR)
    ns = CG._owner_ns(owner)

    def member_files(gid):
        return sorted(
            p.name for p in state.glob(f"*_{ns}.g_{gid}.json"))

    def manifest_file(gid):
        return state / f"gen_{ns}_{gid}.json"

    p = open_program(owner)
    p.nursery.add("bounds base", words="bounds alpha")
    g1 = f"t7235{RUN}g1"
    g2 = f"t7235{RUN}g2"
    g3 = f"t7235{RUN}g3"
    CG.commit_checkpoint(p, generation_id=g1)
    state_kind, gen = committed_generation_state(owner)
    check("F1.g1_committed", (state_kind, gen) == ("verified", g1),
          f"{state_kind} {gen}")
    check("F1.g1_members_complete", len(member_files(g1)) == 4,
          str(member_files(g1)))

    p.nursery.add("bounds next", words="bounds beta")
    aborted = False
    try:
        CG.commit_checkpoint(p, generation_id=g2,
                             _fail_at="member_program")
    except CheckpointCommitError:
        aborted = True
    check("F2.abort_raises_commit_error", aborted)
    state_kind, gen = committed_generation_state(owner)
    check("F2.pointer_unmoved", (state_kind, gen) == ("verified", g1),
          f"{state_kind} {gen}")
    orphans = member_files(g2)
    check("F2.orphans_exactly_sealed_prefix",
          orphans == [f"nursery_{ns}.g_{g2}.json"], str(orphans))
    check("F2.no_manifest_for_aborted",
          not manifest_file(g2).exists())

    CG.commit_checkpoint(p, generation_id=g3)
    state_kind, gen = committed_generation_state(owner)
    check("F3.g3_committed", (state_kind, gen) == ("verified", g3),
          f"{state_kind} {gen}")
    check("F3.aborted_orphans_reaped", member_files(g2) == [],
          str(member_files(g2)))
    check("F3.previous_generation_retained",
          len(member_files(g1)) == 4, str(member_files(g1)))

    # exact-pattern cleanup of this owner's state files
    # (the ideas snapshot path is a DIRECTORY for the owner)
    import shutil
    safe = _safe_owner(owner)
    pats = [f"*{ns}*", f"program_{safe}.json", f"nursery_{safe}.json",
            f"ideas_{safe}*", f"*{safe}*"]
    seen = set()
    for pat in pats:
        for pth in state.glob(pat):
            if pth in seen:
                continue
            seen.add(pth)
            try:
                if pth.is_dir():
                    shutil.rmtree(pth)
                else:
                    pth.unlink()
            except OSError as exc:
                _CLEANUP_ERRORS.append(f"{pth}: {exc}")


# ---------------------------------------------------------------- G
def section_g():
    callers = []
    form_dir = Path(REPO) / "form"
    for py in form_dir.rglob("*.py"):
        if "_test.py" in py.name or py.name == "atomic_write.py":
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = (fn.attr if isinstance(fn, ast.Attribute)
                        else fn.id if isinstance(fn, ast.Name) else "")
                if name == "sweep_stale_tmps":
                    callers.append(str(py.relative_to(REPO)))
    check("G1.no_production_sweep_caller", callers == [],
          str(callers))


def main():
    with tempfile.TemporaryDirectory(prefix="awb_a_") as d:
        section_a(d)
    with tempfile.TemporaryDirectory(prefix="awb_b_") as d:
        section_b(d)
    with tempfile.TemporaryDirectory(prefix="awb_c_") as d:
        section_c(d)
    with tempfile.TemporaryDirectory(prefix="awb_d_") as d:
        section_d(d)
    with tempfile.TemporaryDirectory(prefix="awb_e_") as d:
        section_e(d)
    section_f()
    section_g()
    check("cleanup.no_errors", not _CLEANUP_ERRORS,
          str(_CLEANUP_ERRORS))
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"atomic_write_boundaries_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
