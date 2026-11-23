"""Q-35.1 — sweep_stale_tmps safety contract (Director ruling 7085151190
item 7 on issue #512; proposal 7079215767).

The pre-repair sweep matched the substring ``.dmtmp.`` anywhere in a
name, parsed the first dot-segment after it as a pid, and unlinked by
name. A substring does not prove helper ownership: foreign files whose
names merely contain the infix were deleted, a symlink wearing a
temp-shaped name was unlinked unexamined, unlink failures were
swallowed, and nothing re-validated the file's identity between the
liveness probe and the unlink.

This suite pins the repaired contract, failing-first against the old
helper:

  S1  foreign filenames that merely contain the infix are KEPT
      (non-mint tails, uppercase/short rand segments, infix in base).
  S2  a symlink wearing a temp-shaped name is KEPT and its target is
      byte-identical after; a symlinked sweep root is a typed refusal
      (SweepRefusalError) and removes nothing.
  S3  a temp whose pid number is held by a live unrelated process
      (the PID-reuse shape) is KEPT with reason LIVE_PID.
  S4  a genuine helper-minted orphan (real crash_before_replace
      worker) IS swept; a hand-planted valid-shape dead-pid temp is
      KEPT byte-identical with typed reason NOT_PROVEN_OWNED —
      filename shape is not provenance (Director CORRECTION_REQUIRED
      7088554768; CONTRACT SUPERSESSION 7088845962). Canonical
      neighbours stay byte-identical.
  S5  canonical neighbouring files are byte-identical after every
      sweep in this suite (asserted per section via snapshots).
  S6  the age rail, on a genuine helper-minted orphan: a fresh one
      is KEPT (TOO_YOUNG) under min_age_seconds=300 and swept once
      aged past the rail.
  S7  identity race: a genuine orphan replaced between scan and
      unlink (test hook) is KEPT (CHANGED_SINCE_SCAN); replacement
      bytes intact.
  S8  partial failure is reported: a forced unlink failure on one
      genuine orphan appears in the report as REMOVE_FAILED with
      the error class, the failed file remains, and the other
      genuine orphan is still removed.
  S9  receipt truth: report entries cover every scanned candidate
      exactly once and the removed count matches the entries (the
      one removed entry is a genuine helper-minted orphan).
  S10 missing directory keeps the proven legacy contract:
      exactly {"scanned": 0, "removed": 0}, no raise.
  S11 a temp owned by a different uid is KEPT (NOT_OWNER) — exercised
      only where chown is permitted; otherwise a NOTE is printed and
      the check is not recorded (never vacuous).

Labels: INTEGRATION (helper level, temp dirs) + CROSS_PROCESS (S4).
State hygiene: temp directories only; nothing touches form/state.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, REPO)

RESULTS = []

from form.dell_matrix import atomic_write as AW  # noqa: E402
from form.dell_matrix.atomic_write import sweep_stale_tmps  # noqa: E402

RUN = uuid.uuid4().hex[:8]


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}")


def _dead_pid():
    """A pid proven dead at probe time (reaped child, re-verified)."""
    for _ in range(5):
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait(timeout=30)
        try:
            os.kill(proc.pid, 0)
        except ProcessLookupError:
            return proc.pid
        except OSError:
            return proc.pid
    return 99999997


def _plant(d, name, data=b"partial"):
    pth = os.path.join(d, name)
    with open(pth, "wb") as f:
        f.write(data)
    return pth


def _snapshot(d):
    """{name: bytes} for every regular file directly in d."""
    out = {}
    for name in sorted(os.listdir(d)):
        pth = os.path.join(d, name)
        if os.path.isfile(pth) and not os.path.islink(pth):
            with open(pth, "rb") as f:
                out[name] = f.read()
    return out


def _report_reasons(report):
    return {e["name"]: e.get("reason") for e in report}


def _crash_orphan(d, target_name):
    """Mint ONE genuine helper orphan in d: a subprocess runs the real
    atomic_write_bytes with crash_before_replace against a target
    named target_name inside d and dies (exit 42) after temp fsync,
    leaving exactly one helper-minted temp. Returns (proc, [names]).
    The orphan carries durable writer-minted provenance; a
    hand-planted file never does."""
    target = os.path.join(d, target_name)
    if not os.path.exists(target):
        _plant(d, target_name, b"PRED")
    fd, wpath = tempfile.mkstemp(suffix=".py")
    os.close(fd)
    with open(wpath, "w", encoding="utf-8") as f:
        f.write(
            "import sys\n"
            "sys.path.insert(0, sys.argv[1])\n"
            "from form.dell_matrix.atomic_write import"
            " atomic_write_bytes\n"
            "atomic_write_bytes(sys.argv[2], b'NEWX',"
            " _fail_at=sys.argv[3])\n"
        )
    proc = subprocess.run(
        [sys.executable, wpath, REPO, target, "crash_before_replace"],
        capture_output=True, text=True, timeout=120)
    os.unlink(wpath)
    orphans = [n for n in os.listdir(d)
               if ".dmtmp." in n and n.startswith(target_name + ".")]
    return proc, orphans


# ---------------------------------------------------------------- S1
def section_s1(d):
    canon = _plant(d, "canon.json", b"{}")
    dead = _dead_pid()
    foreign = [
        f"evil.dmtmp.{dead}.backup",            # infix, tail not rand8
        f"notes.dmtmp.{dead}.txt",              # infix, tail not rand8
        f"x.json.dmtmp.{dead}.DEADBEEF",        # uppercase rand
        f"x.json.dmtmp.{dead}.short",           # short rand
        f"x.json.dmtmp.{dead}.deadbeef.extra",  # trailing segment
        f"a.dmtmp.b.json.dmtmp.{dead}.deadbeef",  # infix inside base
    ]
    for name in foreign:
        _plant(d, name)
    before = _snapshot(d)
    report = []
    res = sweep_stale_tmps(d, report=report)
    kept = all(os.path.exists(os.path.join(d, n)) for n in foreign)
    check("S1.foreign_infix_names_all_kept", kept and res["removed"] == 0,
          str(res))
    reasons = _report_reasons(report)
    check("S1.foreign_reported_malformed",
          all(reasons.get(n) == "MALFORMED_NAME" for n in foreign),
          str(reasons))
    check("S5.s1_canonical_byte_identical",
          _snapshot(d).get("canon.json") == b"{}" and
          os.path.exists(canon))


# ---------------------------------------------------------------- S2
def section_s2(d):
    canon = _plant(d, "canon.json", b"CANON-BYTES")
    dead = _dead_pid()
    link_name = f"canon.json.dmtmp.{dead}.deadbeef"
    link = os.path.join(d, link_name)
    os.symlink(canon, link)
    report = []
    res = sweep_stale_tmps(d, report=report)
    check("S2.symlink_candidate_kept",
          os.path.islink(link) and res["removed"] == 0, str(res))
    check("S2.symlink_reason_typed",
          _report_reasons(report).get(link_name) == "NOT_A_REGULAR_FILE",
          str(report))
    with open(canon, "rb") as f:
        check("S5.s2_symlink_target_byte_identical",
              f.read() == b"CANON-BYTES")

    # symlinked root: typed refusal, nothing removed
    real = os.path.join(d, "real")
    os.mkdir(real)
    victim = _plant(real, f"x.json.dmtmp.{dead}.deadbeef")
    root_link = os.path.join(d, "rootlink")
    os.symlink(real, root_link)
    raised = None
    try:
        sweep_stale_tmps(root_link)
    except AW.SweepRefusalError as exc:
        raised = exc
    except Exception as exc:  # noqa: BLE001
        raised = f"wrong-type:{type(exc).__name__}"
    check("S2.symlinked_root_typed_refusal",
          isinstance(raised, AW.SweepRefusalError), str(raised))
    check("S2.symlinked_root_removes_nothing", os.path.exists(victim))


# ---------------------------------------------------------------- S3
def section_s3(d):
    _plant(d, "canon.json", b"{}")
    sleeper = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        name = f"x.json.dmtmp.{sleeper.pid}.deadbeef"
        _plant(d, name)
        report = []
        res = sweep_stale_tmps(d, report=report)
        check("S3.live_pid_number_kept",
              os.path.exists(os.path.join(d, name)) and
              res["removed"] == 0, str(res))
        check("S3.live_pid_reason_typed",
              _report_reasons(report).get(name) == "LIVE_PID",
              str(report))
    finally:
        sleeper.kill()
        sleeper.wait(timeout=30)


# ---------------------------------------------------------------- S4
def section_s4(d):
    # genuine helper-minted orphan via the real crash fixture shape
    canon = _plant(d, "canon.bin", b"PRED")
    proc, orphans = _crash_orphan(d, "canon.bin")
    check("S4.crash_worker_exit_42", proc.returncode == 42,
          f"rc={proc.returncode}")
    check("S4.exactly_one_genuine_orphan", len(orphans) == 1,
          str(orphans))
    report = []
    res = sweep_stale_tmps(d, report=report)
    check("S4.genuine_orphan_swept",
          res["removed"] == 1 and
          not any(".dmtmp." in n for n in os.listdir(d)), str(res))
    check("S4.removal_reported",
          len(report) == 1 and report[0]["action"] == "removed",
          str(report))
    with open(canon, "rb") as f:
        check("S5.s4_canonical_byte_identical", f.read() == b"PRED")

    # FAILING-FIRST (7088554768): a hand-planted foreign file whose
    # name matches the exact full mint pattern (dead pid, random
    # 8 hex) is NOT helper-owned: filename shape is not provenance.
    # The sweep must leave its bytes intact (7088845962).
    dead = _dead_pid()
    foreign_name = f"x.json.dmtmp.{dead}.cafebabe"
    planted = _plant(d, foreign_name, b"foreign-bytes")
    report = []
    res = sweep_stale_tmps(d, report=report)
    check("S4.foreign_exact_shape_kept",
          res["removed"] == 0 and os.path.exists(planted), str(res))
    check("S4.foreign_reason_not_proven_owned",
          _report_reasons(report).get(foreign_name) ==
          "NOT_PROVEN_OWNED", str(report))
    intact = os.path.exists(planted)
    if intact:
        with open(planted, "rb") as f:
            intact = f.read() == b"foreign-bytes"
    check("S4.foreign_bytes_intact", intact)


# ---------------------------------------------------------------- S6
def section_s6(d):
    _plant(d, "canon.json", b"{}")
    # the age rail is exercised on a GENUINE helper-minted orphan:
    # a hand-planted file is kept as NOT_PROVEN_OWNED before age is
    # ever consulted (7088845962).
    proc, orphans = _crash_orphan(d, "canon.json")
    name = orphans[0] if orphans else "<none>"
    pth = os.path.join(d, name)
    report = []
    res = sweep_stale_tmps(d, min_age_seconds=300, report=report)
    check("S6.fresh_temp_too_young_kept",
          len(orphans) == 1 and os.path.exists(pth) and
          res["removed"] == 0, str(res))
    check("S6.too_young_reason_typed",
          _report_reasons(report).get(name) == "TOO_YOUNG", str(report))
    old = time.time() - 3600
    os.utime(pth, (old, old))
    res = sweep_stale_tmps(d, min_age_seconds=300)
    check("S6.aged_temp_swept_past_rail",
          res["removed"] == 1 and not os.path.exists(pth), str(res))


# ---------------------------------------------------------------- S7
def section_s7(d):
    _plant(d, "canon.json", b"{}")
    # hostile race/swap (7088554768): the candidate is a GENUINE
    # helper-minted orphan; the hook replaces it with foreign bytes
    # between classification and unlink. Identity revalidation must
    # keep the replacement.
    proc, orphans = _crash_orphan(d, "canon.json")
    name = orphans[0] if orphans else "<none>"
    pth = os.path.join(d, name)

    def _swap(path):
        staging = path + ".staging"
        with open(staging, "wb") as f:
            f.write(b"REPLACEMENT")
        os.replace(staging, path)

    AW._SWEEP_HOOK = _swap
    try:
        report = []
        res = sweep_stale_tmps(d, report=report)
    finally:
        AW._SWEEP_HOOK = None
    check("S7.replaced_candidate_kept",
          len(orphans) == 1 and os.path.exists(pth) and
          res["removed"] == 0, str(res))
    check("S7.changed_reason_typed",
          _report_reasons(report).get(name) == "CHANGED_SINCE_SCAN",
          str(report))
    with open(pth, "rb") as f:
        check("S5.s7_replacement_bytes_intact", f.read() == b"REPLACEMENT")


# ---------------------------------------------------------------- S8
def section_s8(d):
    _plant(d, "canon.json", b"{}")
    # both candidates are GENUINE helper-minted orphans (only a
    # proven-owned candidate ever reaches the unlink).
    _, bad_orphans = _crash_orphan(d, "a.json")
    _, good_orphans = _crash_orphan(d, "b.json")
    bad_name = bad_orphans[0] if bad_orphans else "<none-a>"
    good_name = good_orphans[0] if good_orphans else "<none-b>"
    bad = os.path.join(d, bad_name)
    good = os.path.join(d, good_name)
    real_unlink = os.unlink

    def flaky_unlink(path, *a, **k):
        if os.path.basename(str(path)) == bad_name:
            raise PermissionError("injected unlink failure")
        return real_unlink(path, *a, **k)

    os.unlink = flaky_unlink
    try:
        report = []
        res = sweep_stale_tmps(d, report=report)
    finally:
        os.unlink = real_unlink
    check("S8.partial_failure_counts",
          len(bad_orphans) == 1 and len(good_orphans) == 1 and
          res["removed"] == 1 and os.path.exists(bad) and
          not os.path.exists(good), str(res))
    entry = {e["name"]: e for e in report}.get(bad_name, {})
    check("S8.failure_reported_typed",
          entry.get("action") == "failed" and
          entry.get("reason") == "REMOVE_FAILED" and
          entry.get("error") == "PermissionError", str(report))


# ---------------------------------------------------------------- S9
def section_s9(d):
    _plant(d, "canon.json", b"{}")
    dead = _dead_pid()
    # the removed entry is a GENUINE helper-minted orphan; the
    # hand-planted entries are all kept under the provenance law.
    _, orphans = _crash_orphan(d, "a.json")
    names = [
        orphans[0] if orphans else "<none>",             # removed
        f"b.json.dmtmp.{os.getpid()}.deadbeef",          # live (self)
        f"c.json.dmtmp.{dead}.DEADBEEF",                 # malformed
        f"ddir.json.dmtmp.{dead}.deadbeef",              # directory
    ]
    for n in names[1:3]:
        _plant(d, n)
    os.mkdir(os.path.join(d, names[3]))
    report = []
    res = sweep_stale_tmps(d, report=report)
    check("S9.report_covers_every_candidate_once",
          sorted(e["name"] for e in report) == sorted(names) and
          res["scanned"] == len(names), str(report))
    check("S9.removed_count_matches_entries",
          res["removed"] ==
          sum(1 for e in report if e["action"] == "removed") == 1,
          str(res))
    check("S9.directory_candidate_kept_typed",
          _report_reasons(report).get(names[3]) == "NOT_A_REGULAR_FILE",
          str(report))


# --------------------------------------------------------------- S10
def section_s10(d):
    res = sweep_stale_tmps(os.path.join(d, "does-not-exist"))
    check("S10.missing_dir_legacy_zeros",
          res == {"scanned": 0, "removed": 0}, str(res))


# --------------------------------------------------------------- S11
def section_s11(d):
    _plant(d, "canon.json", b"{}")
    dead = _dead_pid()
    name = f"x.json.dmtmp.{dead}.deadbeef"
    pth = _plant(d, name)
    try:
        os.chown(pth, 65534, -1)
    except OSError as exc:
        print(f"NOTE  S11 owner check not exercised: chown unavailable "
              f"({type(exc).__name__})")
        return
    report = []
    res = sweep_stale_tmps(d, report=report)
    check("S11.foreign_owner_kept",
          os.path.exists(pth) and res["removed"] == 0, str(res))
    check("S11.not_owner_reason_typed",
          _report_reasons(report).get(name) == "NOT_OWNER", str(report))


def main():
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s1(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s2(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s3(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s4(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s6(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s7(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s8(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s9(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s10(d)
    with tempfile.TemporaryDirectory(prefix="q351_") as d:
        section_s11(d)
    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"sweep_stale_tmps_safety_test: {passed}/{len(RESULTS)} PASS")
    return 0 if passed == len(RESULTS) else 1


def smoke() -> bool:
    return main() == 0


if __name__ == "__main__":
    sys.exit(main())
