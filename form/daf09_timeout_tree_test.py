#!/usr/bin/env python3
"""DAF-09: a regress timeout must kill the whole process tree.

Before (probe on b352e39): run_entry returned TIMEOUT at the bound,
but a descendant spawned by the timed-out entry wrote its marker
3s AFTER the timeout — a surviving writer can contaminate the next
suite, so timeout isolation was false. Contract (Director audit
DAF-09; SWAT 4/4 before implementation):
1. Timed-out entry reports (False, "TIMEOUT") at the bound.
2. No descendant survives: its scheduled post-timeout write never
   happens and its PID is dead after the timeout handling.
3. The kill is scoped: an unrelated bystander process spawned
   outside the entry's tree is NOT killed.
4. Positive control: a fast entry still runs GREEN through the
   same Popen path (rc/token/count verdict unchanged).
Addendum (Director Mode D coverage widening, 2026-10-31):
5. Session-escaping descendant: a grandchild that setsid()s AND
   is reparented (its parent exits before the timeout snapshot)
   must still be killed — it was a witnessed member of the tree
   while attached, even though the kill-time ppid walk and the
   process group can no longer see it.
6. Cancellation: SIGINT to a driver running an entry must take
   the KeyboardInterrupt path — tree killed, interrupt
   propagated (not swallowed into a verdict).
Fixtures are synthetic modules written into this (private-copy)
tree and removed afterwards; marker state lives in a temp dir.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time

RESULTS = []

HANG_FIXTURE = "daf09_fixture_hang"
FAST_FIXTURE = "daf09_fixture_fast"
ESCAPE_FIXTURE = "daf09_fixture_escape"
CANCEL_FIXTURE = "daf09_fixture_cancel"


def _pid_alive(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as fh:
            stat = fh.read()
        return stat[stat.rfind(b")") + 2:].split()[0:1] != [b"Z"]
    except OSError:
        return False


def _rec(name, cond, detail=""):
    RESULTS.append((name, bool(cond), str(detail)[:220]))


def _write_fixture(form_dir, name, body):
    path = os.path.join(form_dir, name + ".py")
    with open(path, "w") as fh:
        fh.write(body)
    return path


def main():
    from form import regress as R

    src_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    form_dir = os.path.join(src_root, "form")
    out = tempfile.mkdtemp(prefix="daf09_out_")
    marker = os.path.join(out, "marker.txt")
    pidfile = os.path.join(out, "child.pid")
    hang_body = (
        "import subprocess, sys, time\n"
        "def smoke():\n"
        f"    child = subprocess.Popen([sys.executable, '-c', "
        f"\"import time,os; open({pidfile!r},'w').write(str(os.getpid())); "
        f"time.sleep(3); open({marker!r},'w').write('WROTE_AFTER_TIMEOUT')\"])\n"
        "    time.sleep(30)\n"
        "    print('1/1')\n"
        "    return True\n"
    )
    fast_body = (
        "def smoke():\n"
        "    print('1/1')\n"
        "    return True\n"
    )
    written = []
    bystander = None
    old_timeout = R.TIMEOUT_S
    try:
        written.append(_write_fixture(form_dir, HANG_FIXTURE, hang_body))
        written.append(_write_fixture(form_dir, FAST_FIXTURE, fast_body))

        # Bystander: unrelated sleeper, NOT part of the entry's tree.
        bystander = subprocess.Popen([sys.executable, "-c",
                                      "import time; time.sleep(30)"])

        R.TIMEOUT_S = 2
        t0 = time.monotonic()
        ok, why = R.run_entry(f"form.{HANG_FIXTURE}:smoke", src_root)
        elapsed = time.monotonic() - t0
        _rec("timed-out entry reports TIMEOUT", (ok, why) == (False, "TIMEOUT"),
             f"ok={ok} why={why}")
        _rec("timeout bound respected (no 30s hang)", elapsed < 15,
             f"elapsed={elapsed:.1f}")

        child_pid = None
        if os.path.exists(pidfile):
            child_pid = int(open(pidfile).read().strip())
        _rec("descendant had started (pid recorded)", child_pid is not None)

        # The descendant was scheduled to write 3s after ITS start;
        # wait past that point: a surviving writer would land by now.
        time.sleep(4)
        _rec("no post-timeout marker write", not os.path.exists(marker))
        child_alive = False
        if child_pid is not None:
            child_alive = _pid_alive(child_pid)
        _rec("descendant process is dead", not child_alive, f"pid={child_pid}")

        _rec("bystander outside the tree survives",
             bystander is not None and bystander.poll() is None)

        # --- Addendum check 5: session-escaping descendant ---
        esc_marker = os.path.join(out, "esc_marker.txt")
        esc_pidfile = os.path.join(out, "esc_child.pid")
        grandchild_script = os.path.join(out, "grandchild.py")
        with open(grandchild_script, "w") as fh:
            fh.write(
                "import os, time\n"
                f"open({esc_pidfile!r}, 'w').write(str(os.getpid()))\n"
                "time.sleep(3)\n"
                f"open({esc_marker!r}, 'w').write('ESCAPED_WRITE')\n"
                "time.sleep(30)\n"
            )
        mid_script = os.path.join(out, "mid.py")
        with open(mid_script, "w") as fh:
            fh.write(
                "import subprocess, sys, time\n"
                f"subprocess.Popen([sys.executable, {grandchild_script!r}], "
                "start_new_session=True)\n"
                "time.sleep(1.0)\n"
            )
        escape_body = (
            "import subprocess, sys, time\n"
            "def smoke():\n"
            f"    subprocess.Popen([sys.executable, {mid_script!r}])\n"
            "    time.sleep(30)\n"
            "    print('1/1')\n"
            "    return True\n"
        )
        written.append(_write_fixture(form_dir, ESCAPE_FIXTURE, escape_body))
        ok3, why3 = R.run_entry(f"form.{ESCAPE_FIXTURE}:smoke", src_root)
        _rec("escape entry reports TIMEOUT", (ok3, why3) == (False, "TIMEOUT"),
             f"ok={ok3} why={why3}")
        esc_pid = None
        if os.path.exists(esc_pidfile):
            esc_pid = int(open(esc_pidfile).read().strip())
        _rec("escaping grandchild had started (pid recorded)",
             esc_pid is not None)
        time.sleep(4)
        _rec("no post-timeout write from escaping grandchild",
             not os.path.exists(esc_marker))
        _rec("escaping grandchild is dead",
             esc_pid is not None and not _pid_alive(esc_pid),
             f"pid={esc_pid}")
        if esc_pid is not None and _pid_alive(esc_pid):
            try:
                os.kill(esc_pid, signal.SIGKILL)
            except OSError:
                pass

        # --- Addendum check 6: cancellation (SIGINT to driver) ---
        can_marker = os.path.join(out, "can_marker.txt")
        can_pidfile = os.path.join(out, "can_child.pid")
        cancel_body = (
            "import subprocess, sys, time\n"
            "def smoke():\n"
            f"    child = subprocess.Popen([sys.executable, '-c', "
            f"\"import time,os; open({can_pidfile!r},'w').write(str(os.getpid())); "
            f"time.sleep(3); open({can_marker!r},'w').write('WROTE_AFTER_CANCEL')\"])\n"
            "    time.sleep(60)\n"
            "    print('1/1')\n"
            "    return True\n"
        )
        written.append(_write_fixture(form_dir, CANCEL_FIXTURE, cancel_body))
        driver = os.path.join(out, "cancel_driver.py")
        with open(driver, "w") as fh:
            fh.write(
                "import sys\n"
                f"sys.path.insert(0, {src_root!r})\n"
                "from form import regress as R\n"
                "R.TIMEOUT_S = 60\n"
                "try:\n"
                f"    print(R.run_entry('form.{CANCEL_FIXTURE}:smoke', {src_root!r}), flush=True)\n"
                "    print('DRIVER_COMPLETED', flush=True)\n"
                "except KeyboardInterrupt:\n"
                "    print('DRIVER_INTERRUPTED', flush=True)\n"
            )
        drv = subprocess.Popen([sys.executable, "-B", driver],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True)
        try:
            deadline = time.monotonic() + 15
            while not os.path.exists(can_pidfile) and time.monotonic() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
            _rec("cancel-fixture child had started",
                 os.path.exists(can_pidfile))
            drv.send_signal(signal.SIGINT)
            drv_out, _ = drv.communicate(timeout=20)
        except Exception as e:  # driver cleanup must not hang the suite
            drv.kill()
            drv_out = f"driver error: {e}"
        _rec("cancellation propagates as KeyboardInterrupt",
             "DRIVER_INTERRUPTED" in drv_out, drv_out.strip()[-120:])
        can_pid = None
        if os.path.exists(can_pidfile):
            can_pid = int(open(can_pidfile).read().strip())
        time.sleep(4)
        _rec("no post-cancel marker write", not os.path.exists(can_marker))
        _rec("cancelled entry's child is dead",
             can_pid is not None and not _pid_alive(can_pid),
             f"pid={can_pid}")
        if can_pid is not None and _pid_alive(can_pid):
            try:
                os.kill(can_pid, signal.SIGKILL)
            except OSError:
                pass
        _rec("bystander survives cancellation too",
             bystander is not None and bystander.poll() is None)

        ok2, why2 = R.run_entry(f"form.{FAST_FIXTURE}:smoke", src_root)
        _rec("fast entry still GREEN via same path", ok2 is True,
             f"ok={ok2} why={why2}")
    finally:
        R.TIMEOUT_S = old_timeout
        if bystander is not None and bystander.poll() is None:
            bystander.terminate()
            bystander.wait(timeout=10)
        failed = []
        for path in written:
            try:
                os.remove(path)
            except OSError as e:
                failed.append(f"{path}: {e}")
        if failed:
            raise RuntimeError("fixture cleanup failed: " + "; ".join(failed))

    passed = sum(1 for _, ok_, _ in RESULTS if ok_)
    for name, ok_, detail in RESULTS:
        if not ok_:
            print(f"FAIL {name}: {detail}")
    print(f"DAF09_TIMEOUT_TREE: {passed}/{len(RESULTS)}")
    return passed == len(RESULTS) and len(RESULTS) > 0


def smoke():
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
