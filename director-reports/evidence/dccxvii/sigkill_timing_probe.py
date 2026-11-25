"""Instrumented replication of dcc_xvii U.sigkill_mid_write parent choreography.

Mirrors _run_u_scenario's sigkill branch exactly (poll for temp every 50ms,
sleep 0.5, SIGKILL), but records monotonic timestamps + temp growth so the
race margin is measured, not guessed. Runs N iterations, prints one line each.
"""
import glob as _g
import json
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, sys.argv[1])  # repo root
N = int(sys.argv[2]) if len(sys.argv) > 2 else 15

from form.mandell import dcc_xvii_test as t
from form.dell_matrix.nursery import owner_nursery_path

scen = "sigkill_mid_write"
owner = f"DCCXVII_U_{scen}"

for it in range(1, N + 1):
    t.wipe_owner(owner)
    if owner not in t.OWNERS:
        t.OWNERS.append(owner)
    tmp = tempfile.mkdtemp(prefix="dccxvii_sig_")
    res = os.path.join(tmp, "res.json")
    out = os.path.join(tmp, "out.json")

    def fill(script: str) -> str:
        return (script.replace("__REPO__", repr(str(t.REPO))).replace("__OWNER__", repr(owner))
                .replace("__SCEN__", repr(scen)).replace("__RES__", repr(res)).replace("__OUT__", repr(out)))

    pa = os.path.join(tmp, "a.py")
    pb = os.path.join(tmp, "b.py")
    open(pa, "w").write(fill(t._SCRIPT_A))
    open(pb, "w").write(fill(t._SCRIPT_B))

    npath_s = owner_nursery_path(owner)
    t0 = time.monotonic()
    proc = subprocess.Popen([sys.executable, pa], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = time.time() + 60
    t_seen = None
    size_at_kill = None
    while time.time() < deadline:
        if _g.glob(npath_s + ".dmtmp.*"):
            t_seen = time.monotonic()
            break
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    t_sleep_start = time.monotonic()
    time.sleep(0.5)
    t_sleep_end = time.monotonic()
    alive_at_kill = proc.poll() is None
    if alive_at_kill:
        tmps = _g.glob(npath_s + ".dmtmp.*")
        size_at_kill = os.path.getsize(tmps[0]) if tmps else None
        proc.kill()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=15)
    t_dead = time.monotonic()
    rc_a = proc.returncode
    rb = subprocess.run([sys.executable, pb], capture_output=True, text=True, timeout=180)
    checks = {}
    if rb.returncode == 0:
        checks = dict(json.load(open(out))["checks"])
    canon_size = os.path.getsize(npath_s) if os.path.exists(npath_s) else -1
    print(f"iter {it}: temp_seen_at={None if t_seen is None else round(t_seen - t0, 3)} "
          f"sleep05_actual={round(t_sleep_end - t_sleep_start, 3)} alive_at_kill={alive_at_kill} "
          f"temp_size_at_kill={size_at_kill} rc_a={rc_a} dead_at={round(t_dead - t0, 3)} "
          f"canon_size={canon_size} b_rc={rb.returncode} checks={checks}", flush=True)
    t.wipe_owner(owner)
    t.clean_tmps()
print("SIGKILL-TIMING-PROBE done")
