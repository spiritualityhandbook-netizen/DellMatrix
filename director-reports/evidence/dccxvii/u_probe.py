"""Run ONLY control U (cross-process matrix) of dcc_xvii_test, N times in-process-sequence.

Each iteration resets CHECKS/OWNERS like smoke() does for the U segment and
reports per-scenario results. Exits 1 on the first failing iteration.
"""
import sys

sys.path.insert(0, sys.argv[1])  # repo root
N = int(sys.argv[2]) if len(sys.argv) > 2 else 30

from form.mandell import dcc_xvii_test as t

for i in range(1, N + 1):
    t.CHECKS = []
    for owner in list(t.OWNERS):
        t.wipe_owner(owner)
    t.OWNERS.clear()
    t.clean_tmps()
    try:
        t.control_u_cross_process_matrix()
    finally:
        for owner in list(t.OWNERS):
            t.wipe_owner(owner)
        t.OWNERS.clear()
        t.clean_tmps()
    failed = [n for n, ok in t.CHECKS if not ok]
    print(f"U-PROBE iter {i}: {'FAIL ' + str(failed) if failed else 'ok'}", flush=True)
    if failed:
        sys.exit(1)
print("U-PROBE: all ok")
