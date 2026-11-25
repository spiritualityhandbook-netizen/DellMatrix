#!/usr/bin/env python3
"""TEST-ISOLATION HYGIENE — adversarial fixture for the C7.Profile
shared-state oracle defect (circuit authorized by Director comment
6989087312 on PR #489, 2026-11-18).

Defect pinned here: form/c7profile_test.py asserted a GLOBAL
property of the shared form/state directory — its t9/t10 checks
globbed ANY *ProfileBench* / profile_timing artifact in the whole
directory and demanded zero. Disposable bench owners are named
ProfileBench<pid>_<n> (form/dell_matrix/profile_board.py), and a
bench whose process is KILLED (VM restart, SIGKILL) cannot run
its dispose step, so its artifacts stay behind as corpses. One
corpse therefore failed EVERY later c7profile run forever, even
though the board's own disposal is correctly owner-scoped and
the run under test cleaned up after itself perfectly. Observed
in the R19 campaign (PR #489): corpses present -> 34-35/36;
purged -> 36/36.

This suite plants a FOREIGN stale artifact set — a dead pid's
bench owner directory, nursery file, orphaned atomic-write temp
(.dmtmp), and a stale timings-store-shaped file — then runs the
real c7profile suite as a subprocess (the harness's own
invocation shape) and asserts the CORRECT contract:

- the c7profile run passes in full (36/36) despite the corpses;
- the foreign artifacts survive byte-identical (a test must not
  garbage-collect another owner's state, and crash-cleanup /
  recovery semantics belong to the state layer, not an oracle);
- the run leaves NONE of its own benchmark artifacts behind
  (the disposable-hygiene contract itself is NOT loosened).

The fixture removes only its own planted files, by exact path,
when done.
"""
from __future__ import annotations

import glob
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A pid that is not this process and not alive: the corpse owner's
# process is dead by construction (house precedent for dead pids:
# form/atomic_write_boundaries_test.py uses 99999997).
DEAD_PID = 99999983
STALE_OWNER = f"ProfileBench{DEAD_PID}_7"


def _dead_pid_confirmed() -> bool:
    if DEAD_PID == os.getpid():
        return False
    try:
        os.kill(DEAD_PID, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False  # exists but owned by someone else — not dead
    return False


def _plant() -> tuple:
    """Create the foreign stale artifact set.

    Returns (digests, top): digests maps every planted file path
    to its sha256 (the ideas dir maps to "DIR"); top is the set
    of planted TOP-LEVEL paths — the set the state-dir globs can
    see, used for the before/after artifact-set comparisons."""
    os.makedirs(STATE_DIR, exist_ok=True)
    planted = {}
    top = set()

    def _mkfile(path, data: bytes, is_top=False):
        with open(path, "wb") as f:
            f.write(data)
        planted[path] = hashlib.sha256(data).hexdigest()
        if is_top:
            top.add(path)

    ideas_dir = os.path.join(STATE_DIR, f"ideas_{STALE_OWNER}")
    os.makedirs(ideas_dir, exist_ok=True)
    _mkfile(os.path.join(ideas_dir, "units.json"),
            b'{"stale": "interrupted bench workload"}\n')
    planted[ideas_dir] = "DIR"
    top.add(ideas_dir)
    _mkfile(os.path.join(STATE_DIR, f"nursery_{STALE_OWNER}.json"),
            b'{"pending": [], "stale": true}\n', is_top=True)
    _mkfile(os.path.join(
        STATE_DIR, f"nursery_{STALE_OWNER}.json.dmtmp.{DEAD_PID}.deadbeef"),
        b'{"partial": "atomic save interrupted mid-write"}\n', is_top=True)
    _mkfile(os.path.join(
        STATE_DIR, f"profile_timing_{STALE_OWNER}_store.json"),
        b'{"stale": "foreign timings-store-shaped artifact"}\n', is_top=True)
    return planted, top


def _bench_artifacts() -> set:
    out = set()
    for pat in ("*ProfileBench*", "*profile_timing*"):
        out.update(glob.glob(os.path.join(STATE_DIR, pat)))
    return out


def _run_c7profile() -> tuple:
    proc = subprocess.run(
        [sys.executable, "-m", "form.c7profile_test"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=600)
    return proc.returncode, proc.stdout + proc.stderr


def smoke() -> bool:
    print("=== TEST-ISOLATION HYGIENE (C7.Profile oracle) ===")
    r = []

    def rec(name, ok, detail=""):
        print(f"[{'PASS' if ok else 'FAIL'}] {name}"
              + (f" | {detail}" if detail and not ok else ""))
        r.append(bool(ok))

    rec("h0_dead_pid_confirmed", _dead_pid_confirmed(),
        f"pid {DEAD_PID} unexpectedly alive or ours")

    planted, planted_top = _plant()
    try:
        before = _bench_artifacts()
        rec("h1_fixture_planted",
            planted_top <= before,
            f"planted={sorted(planted_top)} present={sorted(before)}")

        # Two consecutive full runs against the same corpse set:
        # the false failure was permanent, so the repair must be
        # permanently immune, not first-run lucky.
        for i in (1, 2):
            rc, out = _run_c7profile()
            tail = [ln for ln in out.splitlines() if "===" in ln]
            rec(f"h2_c7profile_green_with_corpses_run{i}",
                rc == 0 and "=== 36/36 ===" in out,
                f"rc={rc} tally={tail[-1] if tail else 'none'} "
                f"fails={[ln for ln in out.splitlines() if '[FAIL]' in ln]}")
            after = _bench_artifacts()
            rec(f"h3_own_artifacts_cleaned_run{i}",
                after == planted_top,
                f"extra={sorted(after - planted_top)} "
                f"missing={sorted(planted_top - after)}")

        intact = True
        for path, digest in planted.items():
            if digest == "DIR":
                intact = intact and os.path.isdir(path)
            else:
                try:
                    with open(path, "rb") as f:
                        intact = intact and (
                            hashlib.sha256(f.read()).hexdigest() == digest)
                except OSError:
                    intact = False
        rec("h4_foreign_artifacts_untouched", intact,
            "a planted foreign artifact was deleted or modified")
    finally:
        # Remove ONLY the fixture's own planted files, by exact path.
        import shutil
        for path in planted:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            except FileNotFoundError:
                pass

    print(f"TEST_ISOLATION_HYGIENE: {sum(r)}/{len(r)}")
    return all(r)


if __name__ == "__main__":
    sys.exit(0 if smoke() else 1)
