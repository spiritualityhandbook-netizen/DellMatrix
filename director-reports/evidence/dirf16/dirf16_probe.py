"""DIR-F16 failing-first probe: send-boundary error classification.

Spawns a live sleeper, witnesses its identity, injects EPERM /
ENOSYS / ESRCH at R._pidfd_send_signal, and records the class
_signal_identity returns. Expected (post-fix): ESRCH -> refused;
EPERM/ENOSYS -> unavailable; sleeper alive after every injection
(nothing was ever signalled). Pre-fix, EPERM/ENOSYS wrongly return
"refused".
"""
import errno
import os
import signal
import subprocess
import sys
import time

# Repo root = three levels up from director-reports/evidence/dirf16/.
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..")))
from form import regress as R  # noqa: E402


def _boom(err):
    def _raise(fd, sig):
        raise OSError(err, os.strerror(err))
    return _raise


def main():
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        start_new_session=True,
    )
    try:
        time.sleep(0.3)
        st = R._proc_starttime(proc.pid)
        assert st is not None, "no starttime for live sleeper"
        real_send = R._pidfd_send_signal
        results = {}
        for name, err in (("EPERM", errno.EPERM),
                          ("ENOSYS", errno.ENOSYS),
                          ("ESRCH", errno.ESRCH)):
            R._pidfd_send_signal = _boom(err)
            try:
                results[name] = R._signal_identity(
                    proc.pid, st, signal.SIGKILL)
            finally:
                R._pidfd_send_signal = real_send
            alive = R._identity_alive(proc.pid, st)
            results[name] = (results[name], f"alive={alive}")
        for name, val in results.items():
            print(f"send-{name}: {val}")
        ok = (results["ESRCH"][0] == "refused"
              and results["EPERM"][0] == "unavailable"
              and results["ENOSYS"][0] == "unavailable"
              and all(v[1] == "alive=True" for v in results.values()))
        print("PROBE:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    finally:
        proc.kill()
        proc.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
