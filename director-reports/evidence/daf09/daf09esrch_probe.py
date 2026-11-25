#!/usr/bin/env python3
"""Failing-first probe: pidfd_open ESRCH-at-open classification.

Spawns a live sleeper, captures its (pid, starttime) identity,
monkeypatches os.pidfd_open to raise a chosen errno, and calls
R._signal_identity directly. Prints the bucket for ESRCH(3) and
EMFILE(24).

Unmodified code: ESRCH -> "unavailable" (DEFECT), EMFILE -> "unavailable".
Fixed code:       ESRCH -> "refused",       EMFILE -> "unavailable".

Usage: python3 daf09esrch_probe.py <worktree_root>
"""
import os
import signal
import subprocess
import sys

root = sys.argv[1]
sys.path.insert(0, root)
import form.regress as R  # noqa: E402


def bucket_for(errno_value):
    victim = subprocess.Popen([sys.executable, "-c",
                               "import time; time.sleep(30)"])
    try:
        ident = (victim.pid, R._proc_starttime(victim.pid))
        real_open = os.pidfd_open

        def boom(pid, flags=0):
            raise OSError(errno_value, os.strerror(errno_value))

        os.pidfd_open = boom
        try:
            return R._signal_identity(ident[0], ident[1], signal.SIGKILL)
        finally:
            os.pidfd_open = real_open
    finally:
        if victim.poll() is None:
            victim.terminate()
        victim.wait(timeout=10)


print("ESRCH(3)  ->", bucket_for(3))
print("EMFILE(24)->", bucket_for(24))
