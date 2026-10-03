#!/usr/bin/env python3
"""CA01-IAC-STATE-CONTAMINATION regression (MPC-011 K).

Direct invocation of iac_i_test used Program() (default "Operator" owner) and
issued "save", atomically overwriting the real default user's
form/state/program_Operator.json. iac_i_test now uses a test-local unique
owner. This test proves a direct run leaves default-user state byte-identical.
"""
from __future__ import annotations

import sys
import os
import json
import hashlib
import subprocess
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form.open import open_program
from form.mandell.executor import execute_seed
from form.persist import _path as _persist_path

CHECKS = []


def check(name, cond):
    CHECKS.append((name, bool(cond)))
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        raise AssertionError(name)


def _sha(fp):
    return hashlib.sha256(open(fp, "rb").read()).hexdigest()


def run_all():
    # 1. seed default-user state with a canary idea
    p = open_program("Operator")
    execute_seed(p, "08[Create] :: kiso_canary")
    p.save()
    fp = _persist_path("Operator")
    h0 = _sha(fp)

    # 2. run iac_i_test the dangerous way: direct module invocation
    r = subprocess.run(
        [sys.executable, "-B", "-m", "form.mandell.iac_i_test"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/..",
        capture_output=True, text=True, timeout=600,
    )
    check("direct iac_i_test run green", r.returncode == 0)

    # 3. default-user state byte-identical
    check("Operator state untouched", _sha(fp) == h0)
    d = json.load(open(fp))
    check("canary idea intact", "kiso_canary" in d["plane"]["units"])

    # 4. the test's save went to a test-local file instead
    strays = [f for f in glob.glob(os.path.join(os.path.dirname(fp), "program_iac1_test_*.json"))]
    check("test saved to test-local owner file", len(strays) >= 1)
    for f in strays:
        try:
            os.remove(f)
        except OSError:
            pass

    print(f"IAC-ISOLATION: {sum(1 for _, c in CHECKS if c)}/{len(CHECKS)} GREEN")


def smoke() -> bool:
    """Regress entry point: run all checks, return True on success."""
    try:
        run_all()
        return True
    except Exception as e:
        print(f"IAC-ISOLATION SMOKE FAILED: {e}")
        return False


if __name__ == "__main__":
    run_all()
