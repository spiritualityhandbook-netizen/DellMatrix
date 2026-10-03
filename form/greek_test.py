#!/usr/bin/env python3
"""Greek operators canon test — Alpha, Delta, Omega, Omni, Lambda, Sigma.

Verifies the Mandell floor is publicly reachable via REPL.
"""

import io
import sys

sys.path.insert(0, ".")

from form.open import Program
from form import repl as repl_mod
from form.mandell.activation import greek_operator, GREEK


def run(p, cmd, iid):
    buf = io.StringIO()
    old = repl_mod._say
    repl_mod._say = lambda s: buf.write(str(s) + "\n")
    try:
        result = repl_mod._dispatch_public_line(p, cmd, iid)
        return result, buf.getvalue()
    finally:
        repl_mod._say = old


def main():
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name}")
            failed += 1

    print("=== Greek Operators Canon Test ===\n")

    # 1. GREEK data integrity
    print("1. Floor data:")
    check("Alpha is floor", GREEK["Alpha"]["floor_status"] == "floor")
    check("Delta is floor", GREEK["Delta"]["floor_status"] == "floor")
    check("Omega is floor", GREEK["Omega"]["floor_status"] == "floor")
    check("Omni is floor", GREEK["Omni"]["floor_status"] == "floor")
    check("Lambda is language", GREEK["Lambda"]["floor_status"] == "not_floor")
    check("Sigma is language", GREEK["Sigma"]["floor_status"] == "not_floor")

    # 2. greek_operator function
    print("\n2. Operator function:")
    check("greek_operator(Alpha) ok", greek_operator("Alpha")["ok"])
    check("greek_operator(Unknown) fails", not greek_operator("Unknown")["ok"])

    # 3. REPL reachability
    print("\n3. REPL commands:")
    p = Program(owner="greek_canon_test")
    p.outcome_records = {}
    p.outcome_seq = 0
    p.lifecycle = {}

    p, _ = run(p, "create an idea called canon_test_idea", "t1")
    p, _ = run(p, "pin canon_test_idea", "t2")

    p, out = run(p, "alpha canon_test_idea", "t3")
    check("alpha reachable", "Alpha (source)" in out)
    check("alpha shows label", "canon_test_idea" in out)

    p, out = run(p, "delta canon_test_idea", "t4")
    check("delta reachable", "Delta (change)" in out)

    p, out = run(p, "omega canon_test_idea", "t5")
    check("omega reachable", "Omega (bound)" in out)
    check("omega shows pinned bound", "PINNED" in out)

    p, out = run(p, "omni", "t6")
    check("omni reachable", "Omni (full-field" in out)
    check("omni shows floor", "Alpha · Delta · Omega · Omni" in out)

    p, out = run(p, "lambda canon_test_idea", "t7")
    check("lambda reachable", "Lambda (logic wavelength)" in out)

    p, out = run(p, "sigma", "t8")
    check("sigma reachable", "Sigma (sum" in out)

    # 4. Unknown idea handling
    print("\n4. Error handling:")
    p, out = run(p, "alpha nonexistent_xyz", "t9")
    check("alpha unknown idea", "no idea found" in out)

    p, out = run(p, "alpha", "t10")
    check("alpha usage", "Usage:" in out)

    # 5. Read-only (no mutation)
    print("\n5. Read-only verification:")
    before_units = len(p.cube.session.plane.units)
    before_lc = dict(p.lifecycle)
    p, _ = run(p, "alpha canon_test_idea", "t11")
    p, _ = run(p, "omni", "t12")
    p, _ = run(p, "sigma", "t13")
    check("no units added", len(p.cube.session.plane.units) == before_units)
    check("lifecycle unchanged", p.lifecycle == before_lc)

    print()
    print(f"=== {passed} passed, {failed} failed ===")
    return 0 if failed == 0 else 1


def smoke() -> bool:
    """Regression smoke: run all Greek canon tests, return True if all pass."""
    import contextlib
    import re
    buf = io.StringIO()
    # Suppress test output during regression; just get the result
    with contextlib.redirect_stdout(buf):
        rc = main()
    out = buf.getvalue()
    # Parse "X passed, Y failed" and print in N/M format for regress harness
    m = re.search(r"(\d+) passed, (\d+) failed", out)
    if m:
        passed, failed = int(m.group(1)), int(m.group(2))
        total = passed + failed
        print(f"Greek canon: {passed}/{total}")
    return rc == 0


if __name__ == "__main__":
    sys.exit(main())
