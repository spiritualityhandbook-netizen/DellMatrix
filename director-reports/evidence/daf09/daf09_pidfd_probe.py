#!/usr/bin/env python3
"""Failing-first probe: DAF-09 pidfd hardening.

Monkeypatch os.pidfd_open to raise OSError, then ask _signal_identity
to signal a live victim with its CORRECT (pid, starttime) identity.

Unmodified code: pidfd failure falls through to bare os.kill -> the
victim is signalled through the unverified-at-signal-time path
(HAZARD: a PID reused between the earlier starttime check and the
kill would be hit instead). Prints VICTIM_KILLED_VIA_FALLBACK.

Fixed code: no numeric fallback exists; outcome is "unavailable",
victim survives. Prints VICTIM_ALIVE_UNAVAILABLE.
"""
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "nbd-omega-daf09pidfd")))
# The worktree path above is fragile; fall back to cwd-based import.
try:
    from form import regress as R
except ImportError:
    sys.path.insert(0, os.getcwd())
    from form import regress as R


def main():
    victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        start = R._proc_starttime(victim.pid)
        assert start is not None, "could not read victim starttime"
        real_open = os.pidfd_open

        def boom(pid, flags=0):
            raise OSError(24, "Too many open files (injected)")

        os.pidfd_open = boom
        try:
            outcome = R._signal_identity(victim.pid, start, signal.SIGKILL)
        finally:
            os.pidfd_open = real_open
        # Bounded wait for death (AGENTS.md 31.1), not a single poll.
        deadline = time.monotonic() + 2.0
        while victim.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        alive = victim.poll() is None
        print(f"outcome={outcome!r} victim_alive={alive}")
        if alive and outcome == "unavailable":
            print("VICTIM_ALIVE_UNAVAILABLE")
            return 0
        if not alive:
            print("VICTIM_KILLED_VIA_FALLBACK")
            return 1
        print("UNEXPECTED_OUTCOME")
        return 2
    finally:
        if victim.poll() is None:
            victim.kill()
        victim.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
