#!/usr/bin/env python3
"""Failing-first probe (DAF-09 identity follow-up): hand
_kill_process_tree a witnessed set containing an UNRELATED
bystander's bare pid — exactly what a stale witnessed entry
becomes after PID reuse. On unmodified code the bystander is
SIGKILLed (identity race H3). After the fix the bystander,
whose starttime was never witnessed, must survive."""
import subprocess
import sys
import time

sys.path.insert(0, sys.argv[1])
from form import regress as R

root = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                        start_new_session=True)
bystander = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
time.sleep(0.5)
# Simulate: bystander pid sits in the witnessed set with NO valid
# witnessed identity for it (stale/reused entry).
root._witnessed_descendants = [bystander.pid]
if hasattr(R, "_signal_identity"):
    root._witnessed_identities = []  # no identity was ever witnessed for it
R._kill_process_tree(root)
time.sleep(0.3)
alive = bystander.poll() is None
print("BYSTANDER_ALIVE" if alive else "BYSTANDER_KILLED")
if alive:
    bystander.terminate(); bystander.wait(timeout=10)
sys.exit(0 if alive else 1)
