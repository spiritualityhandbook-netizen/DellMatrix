#!/usr/bin/env python3
"""DAF-09 instrumented run driver (Course 1 step b, spec:
daf09_mapping_reverify_2026-11-01.md section 4).

The suite file is NOT edited. This driver:
  - imports the real form.regress from the scratch worktree,
  - wraps its functions with JSONL logging hooks (module-object
    patching; internal regress calls resolve globals at call time,
    so wrapped attributes are seen by regress internals and by
    the suite, which receives this same module object through
    sys.modules["form.regress"]),
  - runs a minimal positive fixture BEFORE the suite (Ruling #7),
  - observes marker/pidfile timing from outside the suite,
  - invokes the suite's main() unchanged (exact 22 checks),
  - dumps the suite RESULTS verbatim.

Usage: daf09instr_driver.py <worktree_root> <jsonl_out> <label>
Exit code: suite result (0 = 22/22) AND fixture classification is
reported in the JSONL, never folded into the suite verdict.
"""
import contextvars
import glob
import json
import os
import signal
import subprocess
import sys
import threading
import time

WORKTREE = os.path.abspath(sys.argv[1])
JSONL_OUT = sys.argv[2]
LABEL = sys.argv[3] if len(sys.argv) > 3 else "run"

sys.path.insert(0, WORKTREE)
os.chdir(WORKTREE)

_log_lock = threading.Lock()
_t0 = time.monotonic()


def log(event, **fields):
    rec = {"run": LABEL, "event": event,
           "t_mono": round(time.monotonic() - _t0, 4),
           "t_wall": time.time()}
    rec.update(fields)
    line = json.dumps(rec, default=str)
    with _log_lock:
        with open(JSONL_OUT, "a") as fh:
            fh.write(line + "\n")


# ---------------- environment header (spec hook: env) ----------------
def env_header():
    def ns_inode(path):
        try:
            return os.stat(path).st_ino
        except OSError as e:
            return f"ERR:{type(e).__name__}:{getattr(e, 'errno', None)}"
    hidepid = None
    try:
        with open("/proc/self/mountinfo") as fh:
            for ln in fh:
                parts = ln.split()
                if len(parts) > 4 and parts[4] == "/proc":
                    hidepid = ln.strip()
                    break
    except OSError as e:
        hidepid = f"ERR:{type(e).__name__}"
    try:
        load = os.getloadavg()
    except OSError:
        load = None
    log("env_header",
        uname=os.uname().sysname + " " + os.uname().release,
        machine=os.uname().machine,
        python=sys.version.split()[0],
        cpu_count=os.cpu_count(),
        loadavg=load,
        pidfd_open_available=hasattr(os, "pidfd_open"),
        pid_ns_self=ns_inode("/proc/self/ns/pid"),
        pid_ns_init=ns_inode("/proc/1/ns/pid"),
        proc_mount=hidepid,
        observer_pid=os.getpid(),
        worktree=WORKTREE)


# ---------------- marker observer (spec hook 7) ----------------
_stop_obs = threading.Event()
_seen_files = {}


def marker_observer():
    while not _stop_obs.is_set():
        for path in glob.glob(os.path.join(
                os.environ.get("TMPDIR", "/tmp"), "daf09_out_*", "*")):
            base = os.path.basename(path)
            if base not in ("esc_marker.txt", "esc_child.pid",
                            "marker.txt", "child.pid"):
                continue
            key = path
            try:
                st = os.stat(path)
            except OSError:
                continue
            if key not in _seen_files:
                _seen_files[key] = st.st_mtime
                content = None
                if base.endswith(".pid"):
                    try:
                        with open(path) as fh:
                            content = fh.read().strip()
                    except OSError:
                        content = None
                log("marker_observer_first_seen", file=base,
                    dir=os.path.basename(os.path.dirname(path)),
                    mtime=st.st_mtime, content=content)
        _stop_obs.wait(0.05)


# ---------------- main ----------------
def main():
    env_header()
    import form.regress as R  # real module; patched in place below

    orig = {
        "_proc_starttime": R._proc_starttime,
        "_descendant_identities": R._descendant_identities,
        "_signal_identity": R._signal_identity,
        "_kill_process_tree": R._kill_process_tree,
        "_communicate_tracked": R._communicate_tracked,
        "run_entry": R.run_entry,
        "_identity_alive": R._identity_alive,
    }
    in_signal = contextvars.ContextVar("in_signal", default=False)

    # --- hook 3: _proc_starttime ---
    def wrap_starttime(pid):
        val = orig["_proc_starttime"](pid)
        log("proc_starttime", pid=pid, value=val,
            in_signal_identity=in_signal.get(),
            none_reason=("unreadable_or_gone" if val is None else None))
        return val

    # --- hook 1: _descendant_identities ---
    def wrap_descendants(root_pid):
        start = time.monotonic()
        skipped = []
        try:
            entries = [n for n in os.listdir("/proc") if n.isdigit()]
            entry_count = len(entries)
            for name in entries:
                try:
                    with open(f"/proc/{name}/stat", "rb") as fh:
                        stat = fh.read()
                    tail = stat[stat.rfind(b")") + 2:].split()
                    int(tail[1]); int(tail[19])
                except (OSError, ValueError, IndexError) as e:
                    skipped.append((int(name), type(e).__name__))
        except OSError:
            entry_count = -1
        out = orig["_descendant_identities"](root_pid)
        dur = time.monotonic() - start
        log("descendant_identities", root_pid=root_pid,
            duration_s=round(dur, 4), proc_entry_count=entry_count,
            returned=[[p, s] for p, s in out],
            none_starttimes=[p for p, s in out if s is None],
            skipped_sample=skipped[:10], skipped_count=len(skipped))
        return out

    # --- hook 4: _signal_identity ---
    def classify(expected, observed):
        if expected is None or observed is None:
            return "MISSING"
        return "MATCH" if observed == expected else "CHANGED"

    def wrap_signal(pid, starttime, sig):
        pre = orig["_proc_starttime"](pid)
        tok = in_signal.set(True)
        start = time.monotonic()
        try:
            outcome = orig["_signal_identity"](pid, starttime, sig)
        finally:
            in_signal.reset(tok)
        post = orig["_proc_starttime"](pid)
        log("signal_identity", pid=pid, expected_starttime=starttime,
            pre_read=pre, pre_class=classify(starttime, pre),
            outcome=outcome, post_read=post,
            pidfd_open_is_driver_proxy=(
                getattr(os, "pidfd_open", None) is logging_pidfd_open),
            duration_s=round(time.monotonic() - start, 4))
        return outcome

    # --- hook 2: _communicate_tracked (entry/exit; per-slice via hook 1) ---
    def wrap_communicate(proc):
        log("communicate_tracked_enter", root_pid=proc.pid,
            timeout_s=R.TIMEOUT_S)
        start = time.monotonic()
        try:
            out = orig["_communicate_tracked"](proc)
            log("communicate_tracked_exit", root_pid=proc.pid,
                outcome="returned",
                duration_s=round(time.monotonic() - start, 4),
                witnessed=[[p, s] for p, s in
                           getattr(proc, "_witnessed_identities", [])])
            return out
        except BaseException as e:
            log("communicate_tracked_exit", root_pid=proc.pid,
                outcome=type(e).__name__,
                duration_s=round(time.monotonic() - start, 4),
                witnessed=[[p, s] for p, s in
                           getattr(proc, "_witnessed_identities", [])])
            raise

    # --- hook 5: _kill_process_tree ---
    def ppid_of(pid):
        try:
            with open(f"/proc/{pid}/stat", "rb") as fh:
                stat = fh.read()
            return int(stat[stat.rfind(b")") + 2:].split()[1])
        except (OSError, ValueError, IndexError):
            return None

    def wrap_kill(proc):
        known = []
        try:
            known = orig["_descendant_identities"](proc.pid)
        except Exception:
            pass
        witnessed = list(getattr(proc, "_witnessed_identities", []))
        union = []
        seen = set()
        for ident in list(known) + witnessed:
            if ident not in seen:
                seen.add(ident)
                union.append(ident)
        log("kill_process_tree_enter", root_pid=proc.pid,
            snapshot=[[p, s] for p, s in known],
            witnessed=[[p, s] for p, s in witnessed],
            union=[[p, s] for p, s in union],
            ppid_at_kill={str(p): ppid_of(p) for p, _ in union})
        start = time.monotonic()
        out = orig["_kill_process_tree"](proc)
        report = getattr(proc, "_kill_report", None) or {}
        alive_after = [[p, s] for p, s in union
                       if orig["_identity_alive"](p, s)]
        log("kill_process_tree_exit", root_pid=proc.pid,
            duration_s=round(time.monotonic() - start, 4),
            report={k: [[p, s] for p, s in v]
                    for k, v in report.items()},
            alive_after=[[p, s] for p, s in alive_after])
        return out

    # --- hook 6: run_entry ---
    def wrap_run_entry(entry, cwd):
        log("run_entry_enter", entry=entry)
        start = time.monotonic()
        try:
            res = orig["run_entry"](entry, cwd)
            log("run_entry_exit", entry=entry, outcome="returned",
                result=list(res),
                duration_s=round(time.monotonic() - start, 4))
            return res
        except BaseException as e:
            log("run_entry_exit", entry=entry,
                outcome=type(e).__name__,
                duration_s=round(time.monotonic() - start, 4))
            raise

    # --- hook 4b: pidfd_open result/errno (original swallows it) ---
    _real_pidfd_open = getattr(os, "pidfd_open", None)

    def _proc_state(pid):
        try:
            with open(f"/proc/{pid}/stat", "rb") as fh:
                stat = fh.read()
            return stat[stat.rfind(b")") + 2:].split()[0].decode()
        except OSError:
            return None

    def logging_pidfd_open(pid, flags=0):
        try:
            fd = _real_pidfd_open(pid, flags)
            log("pidfd_open", pid=pid, result="ok", fd=fd,
                proc_state=_proc_state(pid))
            return fd
        except OSError as e:
            log("pidfd_open", pid=pid, result="error",
                errno=getattr(e, "errno", None), error=str(e),
                proc_state=_proc_state(pid))
            raise

    if _real_pidfd_open is not None:
        os.pidfd_open = logging_pidfd_open

    R._proc_starttime = wrap_starttime
    R._descendant_identities = wrap_descendants
    R._signal_identity = wrap_signal
    R._communicate_tracked = wrap_communicate
    R._kill_process_tree = wrap_kill
    R.run_entry = wrap_run_entry
    sys.modules["form.regress"] = R

    # --- minimal positive fixture (BEFORE the 22 checks) ---
    fixture_ok = True
    fixture_detail = {}
    tmpd = None
    try:
        import tempfile
        tmpd = tempfile.mkdtemp(prefix="daf09instr_fixture_")
        child_pid_path = os.path.join(tmpd, "sleeper.pid")
        root_code = (
            "import subprocess, sys, time\n"
            f"ch = subprocess.Popen([sys.executable, '-c', "
            f"\"import os,time; open({child_pid_path!r},'w').write(str(os.getpid())); time.sleep(30)\"])\n"
            "time.sleep(30)\n")
        root = subprocess.Popen([sys.executable, "-c", root_code],
                                start_new_session=True)
        dl = time.monotonic() + 10
        while not os.path.exists(child_pid_path) and time.monotonic() < dl:
            time.sleep(0.05)
        sleeper_pid = int(open(child_pid_path).read().strip())
        scan = orig["_descendant_identities"](root.pid)
        scan_rec = [s for p, s in scan if p == sleeper_pid]
        direct = orig["_proc_starttime"](sleeper_pid)
        seen_ok = len(scan_rec) == 1
        start_ok = (direct is not None and scan_rec and
                    scan_rec[0] == direct)
        outcome = None
        dead_ok = False
        if seen_ok and start_ok:
            outcome = orig["_signal_identity"](sleeper_pid, direct,
                                              signal.SIGKILL)
            dl = time.monotonic() + 5
            while time.monotonic() < dl:
                if not orig["_identity_alive"](sleeper_pid, direct):
                    dead_ok = True
                    break
                time.sleep(0.05)
        fixture_detail = {
            "root_pid": root.pid, "sleeper_pid": sleeper_pid,
            "i_seen_in_scan": seen_ok, "scan_starttime": scan_rec,
            "ii_starttime_nonNone_and_equal": bool(start_ok),
            "direct_starttime": direct,
            "iii_signal_outcome": outcome,
            "iii_bounded_wait_dead": dead_ok}
        fixture_ok = bool(seen_ok and start_ok and
                          outcome == "signalled" and dead_ok)
        # cleanup: kill root (its sleeper is already dead if iii passed)
        try:
            R._kill_process_tree(root)
        except Exception as e:
            log("fixture_cleanup_error", error=str(e))
    except Exception as e:
        fixture_ok = False
        fixture_detail = {"error": f"{type(e).__name__}: {e}"}
    log("minimal_positive_fixture",
        passed=fixture_ok,
        classification=("SUPPORTED" if fixture_ok else
                        "UNSUPPORTED-FOR-CLEANUP-JUDGEMENT"),
        detail=fixture_detail)

    # --- run the exact suite, unedited ---
    obs = threading.Thread(target=marker_observer, daemon=True)
    obs.start()
    import form.daf09_timeout_tree_test as suite
    suite_ok = suite.main()
    _stop_obs.set()
    log("suite_results", passed_count=sum(
        1 for _, ok_, _ in suite.RESULTS if ok_),
        total=len(suite.RESULTS),
        check_names=[n for n, _, _ in suite.RESULTS],
        results=[[n, bool(o), d] for n, o, d in suite.RESULTS])
    log("driver_done", suite_ok=bool(suite_ok), fixture_ok=fixture_ok)
    return 0 if suite_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
